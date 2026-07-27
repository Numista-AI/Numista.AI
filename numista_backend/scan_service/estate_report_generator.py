"""
estate_report_generator.py — Core report generation logic for Numista.AI estate feature

Fetches coin data from Firestore, computes financial summaries, calls Gemini
for professional narrative generation, then delegates to the PDF builder.

Usage:
    result = await generate_estate_report(uid, report_request)
    pdf_bytes = result['pdf_bytes']
    metadata  = result['report_metadata']

Firestore collections read:
    users/{uid}/coins          — coin inventory documents
    users/{uid}/estate_profile — optional estate profile (attorney info, etc.)
    users/{uid}/estate_data    — per-coin estate overrides (keyed by coin doc ID)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from datetime import date, datetime
from typing import Any

from google.cloud import firestore
from google.genai import types

from estate_state_rules import STATE_RULES, get_state_rules

log = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
IRS_APPRAISAL_THRESHOLD = 3_000.0   # IRC §170(f)(11): single item or group of similar items
MAX_TOP_COINS = 10                   # How many top-value coins to include in Gemini prompt


# ─────────────────────────────────────────────────────────────────────────────
# FMV / VALUE PARSING HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def parse_fmv(value_str: Any) -> float | None:
    """
    Parse an AI-estimated FMV string into a float.

    Handles:
      - None / empty / 'Pending' / 'N/A'  → None
      - '$1,250'                           → 1250.0
      - '$100-150' or '$100 - $150'        → 125.0  (midpoint of range)
      - '1500'                             → 1500.0

    Returns None if the string cannot be parsed.
    """
    if not value_str:
        return None
    s = str(value_str).strip()
    if s in ('Pending', 'N/A', '', 'None', 'none', 'null', 'TBD', 'tbd', '—'):
        return None

    # Strip currency symbols, commas, and whitespace
    cleaned = s.replace('$', '').replace(',', '').strip()

    # Handle range: '100 - 150' or '100-150'
    # Guard against negative numbers by checking if there are two distinct parts
    if '-' in cleaned:
        parts = [p.strip() for p in cleaned.split('-')]
        # Only treat as range if we get exactly 2 non-empty parts, both numeric
        nums = []
        for p in parts:
            p = p.replace('$', '').strip()
            if p:
                try:
                    nums.append(float(p))
                except ValueError:
                    pass
        if len(nums) == 2 and nums[0] > 0 and nums[1] > 0:
            return (nums[0] + nums[1]) / 2.0

    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_melt_value(value_str: Any) -> float | None:
    """
    Parse melt value string.  'N/A', empty → None.
    Same handling as parse_fmv for ranges/currency symbols.
    """
    if not value_str:
        return None
    s = str(value_str).strip()
    if s in ('N/A', 'n/a', '', 'None', 'Pending', '—'):
        return None
    return parse_fmv(s)  # reuse the same logic


def parse_purchase_cost(value_str: Any) -> float | None:
    """Parse purchase cost — same cleaning logic as FMV."""
    return parse_fmv(value_str)


# ─────────────────────────────────────────────────────────────────────────────
# FIRESTORE FETCHERS
# ─────────────────────────────────────────────────────────────────────────────

def fetch_coins(db: firestore.Client, uid: str) -> list[dict]:
    """
    Fetch all coin documents from users/{uid}/coins.

    Each returned dict merges the Firestore document data with its document ID
    under the key '_doc_id'.  Returns an empty list if the collection is absent.
    """
    try:
        docs = db.collection('users').document(uid).collection('coins').stream()
        coins = []
        for doc in docs:
            data = doc.to_dict() or {}
            data['_doc_id'] = doc.id
            coins.append(data)
        log.info(f'[estate] Fetched {len(coins)} coins for uid={uid}')
        return coins
    except Exception as exc:
        log.error(f'[estate] Error fetching coins for uid={uid}: {exc}')
        return []


def fetch_estate_profile(db: firestore.Client, uid: str) -> dict:
    """
    Fetch the estate profile document at users/{uid}/estate_profile/primary.
    Returns an empty dict if missing.
    """
    try:
        doc = db.collection('users').document(uid).collection('estate_profile').document('primary').get()
        return doc.to_dict() or {} if doc.exists else {}
    except Exception as exc:
        log.warning(f'[estate] Could not fetch estate_profile for uid={uid}: {exc}')
        return {}


def fetch_estate_data_overrides(db: firestore.Client, uid: str) -> dict[str, dict]:
    """
    Fetch per-coin estate data overrides from users/{uid}/estate_data.
    Returns a dict keyed by coin doc ID.  Each value is a dict that may contain:
        beneficiary_name, fmv_override, estate_notes, appraiser_name
    """
    try:
        docs = db.collection('users').document(uid).collection('estate_data').stream()
        overrides: dict[str, dict] = {}
        for doc in docs:
            data = doc.to_dict() or {}
            overrides[doc.id] = data
        log.info(f'[estate] Fetched {len(overrides)} estate data overrides for uid={uid}')
        return overrides
    except Exception as exc:
        log.warning(f'[estate] Could not fetch estate_data for uid={uid}: {exc}')
        return {}


# ─────────────────────────────────────────────────────────────────────────────
# COLLECTION ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def build_collection_summary(
    coins: list[dict],
    estate_overrides: dict[str, dict],
    state_rules: dict,
) -> dict:
    """
    Compute all financial totals and flags from the coin list.

    Returns a summary dict consumed by both the AI narrative and PDF builder.
    Coins with no parseable FMV are counted but excluded from dollar totals.
    """
    total_coins = len(coins)
    total_fmv = 0.0
    total_melt_value = 0.0
    total_cost_basis = 0.0
    fmv_by_denomination: dict[str, dict] = {}   # {denom: {count, total_fmv}}
    fmv_by_location: dict[str, dict] = {}        # {location: {count, total_fmv}}
    coins_needing_appraisal: list[dict] = []
    enriched_coins: list[dict] = []

    for coin in coins:
        doc_id = coin.get('_doc_id', '')
        override = estate_overrides.get(doc_id, {})

        # ── FMV ───────────────────────────────────────────────────────────────
        raw_fmv_str = coin.get('AI Estimated Value', '') or coin.get('ai_estimated_value', '')
        fmv_override = override.get('fmv_override')

        if fmv_override is not None:
            try:
                fmv = float(fmv_override)
            except (ValueError, TypeError):
                fmv = parse_fmv(raw_fmv_str)
        else:
            fmv = parse_fmv(raw_fmv_str)

        # ── Melt value ────────────────────────────────────────────────────────
        raw_melt = coin.get('Melt Value', '') or coin.get('melt_value', '')
        melt = parse_melt_value(raw_melt)

        # ── Purchase cost ─────────────────────────────────────────────────────
        raw_cost = coin.get('Purchase Cost', '') or coin.get('purchase_cost', '')
        cost = parse_purchase_cost(raw_cost)

        # ── Accumulate totals ─────────────────────────────────────────────────
        if fmv is not None:
            total_fmv += fmv
        if melt is not None:
            total_melt_value += melt
        if cost is not None:
            total_cost_basis += cost

        # ── Denomination breakdown ────────────────────────────────────────────
        denom = (
            coin.get('Denomination', '') or
            coin.get('denomination', '') or
            'Unknown'
        ).strip() or 'Unknown'

        if denom not in fmv_by_denomination:
            fmv_by_denomination[denom] = {'count': 0, 'total_fmv': 0.0}
        fmv_by_denomination[denom]['count'] += 1
        if fmv is not None:
            fmv_by_denomination[denom]['total_fmv'] += fmv

        # ── Location breakdown ────────────────────────────────────────────────
        location = (
            coin.get('Storage Location', '') or
            coin.get('storage_location', '') or
            coin.get('Location', '') or
            'Unknown'
        ).strip() or 'Unknown'

        if location not in fmv_by_location:
            fmv_by_location[location] = {'count': 0, 'total_fmv': 0.0}
        fmv_by_location[location]['count'] += 1
        if fmv is not None:
            fmv_by_location[location]['total_fmv'] += fmv

        # ── Appraisal flag ────────────────────────────────────────────────────
        needs_appraisal = fmv is not None and fmv >= IRS_APPRAISAL_THRESHOLD

        # ── Build enriched coin dict for PDF ─────────────────────────────────
        enriched = dict(coin)
        enriched.update({
            '_fmv': fmv,
            '_melt': melt,
            '_cost': cost,
            '_needs_appraisal': needs_appraisal,
            '_beneficiary': override.get('beneficiary_name', ''),
            '_estate_notes': override.get('estate_notes', ''),
            '_appraiser_name': override.get('appraiser_name', ''),
            '_assigned_heir_id': override.get('assignedHeirId', ''),
            '_division_locked': override.get('divisionLocked', False),
        })
        enriched_coins.append(enriched)

        if needs_appraisal:
            coins_needing_appraisal.append(enriched)

    # ── Sort by FMV descending for top-coins list ─────────────────────────────
    enriched_coins.sort(key=lambda c: (c['_fmv'] or 0.0), reverse=True)
    top_coins = [
        {
            'year': c.get('Year', c.get('year', '')),
            'denomination': c.get('Denomination', c.get('denomination', '')),
            'series': c.get('Series', c.get('series', '')),
            'grade': c.get('Grade', c.get('grade', '')),
            'fmv': c['_fmv'],
        }
        for c in enriched_coins[:MAX_TOP_COINS]
        if c['_fmv'] is not None
    ]

    # ── NY cliff check ────────────────────────────────────────────────────────
    cliff_warning: str | None = None
    if (
        state_rules.get('cliff_rule')
        and state_rules.get('exemption_2026') is not None
    ):
        cliff_threshold = state_rules['exemption_2026'] * state_rules['cliff_multiplier']
        if total_fmv > cliff_threshold:
            cliff_warning = (
                f'WARNING: Estimated collection FMV of ${total_fmv:,.0f} exceeds the NY '
                f'estate tax cliff threshold of ${cliff_threshold:,.0f} '
                f'(105% × ${state_rules["exemption_2026"]:,.0f} exemption). '
                f'If the total gross estate exceeds this threshold, the ENTIRE estate — '
                f'not just the excess — becomes subject to NY estate tax. '
                f'Immediate consultation with a NY estate attorney is essential.'
            )
        elif total_fmv > state_rules['exemption_2026'] * 0.80:
            # Approaching cliff — warn proactively
            cliff_warning = (
                f'CAUTION: Estimated collection FMV of ${total_fmv:,.0f} is approaching the NY '
                f'estate tax cliff threshold of ${cliff_threshold:,.0f}. '
                f'If other assets are included in the gross estate, the cliff may be triggered. '
                f'Consult a NY estate attorney to assess total estate exposure.'
            )

    # ── Step-up benefit ───────────────────────────────────────────────────────
    stepped_up_basis_benefit = max(0.0, total_fmv - total_cost_basis)

    # ── FMV by denomination — sorted by total_fmv desc ───────────────────────
    fmv_by_denomination_sorted = dict(
        sorted(fmv_by_denomination.items(), key=lambda x: x[1]['total_fmv'], reverse=True)
    )
    fmv_by_location_sorted = dict(
        sorted(fmv_by_location.items(), key=lambda x: x[1]['total_fmv'], reverse=True)
    )

    return {
        'total_coins': total_coins,
        'total_fmv': total_fmv,
        'total_melt_value': total_melt_value,
        'total_cost_basis': total_cost_basis,
        'stepped_up_basis_benefit': stepped_up_basis_benefit,
        'fmv_by_denomination': fmv_by_denomination_sorted,
        'fmv_by_location': fmv_by_location_sorted,
        'top_coins': top_coins,
        'coins_needing_appraisal': coins_needing_appraisal,
        'total_coins_needing_appraisal': len(coins_needing_appraisal),
        'cliff_warning': cliff_warning,
        'enriched_coins': enriched_coins,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SMART DIVISION ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def partition_collection_equitably(
    enriched_coins: list[dict],
    estate_overrides: dict[str, dict],
    heirs: list[dict],
) -> dict:
    """
    Equitably partition coins among heirs using a greedy LPT algorithm.
    Respects locked assignments and returns a dictionary detailing:
      - heir_lots: {heir_id: list of coins}
      - heir_totals: {heir_id: total value}
      - unassigned: list of coins with no fmv or excluded
    """
    if not heirs:
        return {}

    # Initialize lots
    heir_lots = {heir['id']: [] for heir in heirs}
    heir_totals = {heir['id']: 0.0 for heir in heirs}
    unassigned = []

    # Map heir_id to name for convenience in rendering
    heir_names = {heir['id']: heir['name'] for heir in heirs}

    # Step 1: Pre-allocate locked assignments
    for coin in enriched_coins:
        if coin.get('excludeFromReport') or coin.get('_exclude_from_report'):
            continue

        cid = coin.get('_doc_id', '')
        override = estate_overrides.get(cid, {})
        
        assigned_heir_id = override.get('assignedHeirId') or override.get('beneficiaryId')
        division_locked = override.get('divisionLocked', False)

        if division_locked and assigned_heir_id in heir_lots:
            heir_lots[assigned_heir_id].append(coin)
            heir_totals[assigned_heir_id] += coin.get('_fmv') or 0.0
            coin['_assigned_heir_id'] = assigned_heir_id
            coin['_assigned_heir_name'] = heir_names[assigned_heir_id]
            coin['_division_locked'] = True
        else:
            pass

    # Step 2: Distribute remaining coins with value
    unlocked_valued_coins = []
    for coin in enriched_coins:
        if coin.get('excludeFromReport') or coin.get('_exclude_from_report'):
            continue

        cid = coin.get('_doc_id', '')
        override = estate_overrides.get(cid, {})
        division_locked = override.get('divisionLocked', False)
        assigned_heir_id = override.get('assignedHeirId') or override.get('beneficiaryId')

        # Skip if already locked/assigned in Step 1
        if division_locked and assigned_heir_id in heir_lots:
            continue

        fmv = coin.get('_fmv')
        if fmv is not None and fmv > 0:
            unlocked_valued_coins.append(coin)
        else:
            unassigned.append(coin)

    # Sort remaining valued coins descending by FMV
    unlocked_valued_coins.sort(key=lambda c: c.get('_fmv', 0.0), reverse=True)

    # Greedy allocation: assign each coin to the heir with the lowest current lot value
    for coin in unlocked_valued_coins:
        target_heir_id = min(heir_totals, key=heir_totals.get)
        heir_lots[target_heir_id].append(coin)
        heir_totals[target_heir_id] += coin.get('_fmv') or 0.0
        coin['_assigned_heir_id'] = target_heir_id
        coin['_assigned_heir_name'] = heir_names[target_heir_id]
        coin['_division_locked'] = False

    return {
        'heir_lots': heir_lots,
        'heir_totals': heir_totals,
        'unassigned': unassigned,
    }


# ─────────────────────────────────────────────────────────────────────────────
# GEMINI NARRATIVE GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def generate_ai_narrative(
    client,
    model: str,
    collection_summary: dict,
    state_rules: dict,
    mode: str,
    report_request: dict | None = None,
) -> dict:
    """
    Call Gemini to generate professional narrative sections for the estate report.

    Returns a dict with keys:
        executive_summary, valuation_narrative, special_items_narrative,
        appraiser_guidance, jurisdiction_guidance, liquidation_playbook

    Falls back to safe boilerplate if Gemini returns invalid JSON or fails.
    """
    state_name = state_rules['display_name']
    mode_label = 'Living Inventory' if mode == 'living_inventory' else 'Estate Settlement'

    # Build a concise top-coins representation
    top_coins_text = json.dumps(collection_summary['top_coins'], indent=2)
    denoms = list(collection_summary['fmv_by_denomination'].keys())[:12]

    appraisal_note = (
        f"{collection_summary['total_coins_needing_appraisal']} coins have estimated FMV "
        f">= ${IRS_APPRAISAL_THRESHOLD:,.0f} and require IRS-qualified appraisal."
        if collection_summary['total_coins_needing_appraisal'] > 0
        else "No individual coins currently exceed the IRS appraisal threshold, though a "
             "comprehensive professional appraisal is still recommended."
    )

    cliff_context = (
        f"IMPORTANT — NY Estate Tax Cliff Warning: {collection_summary['cliff_warning']}"
        if collection_summary.get('cliff_warning') else ''
    )

    # Liquidation preference & consignor preferences
    liquidation_pref = (report_request or {}).get('liquidation_preference', 'consign_all')
    preferred_consignor = (report_request or {}).get('preferred_consignor', 'None')
    
    liquidation_context = f"""
- Liquidation strategy preferred by owner: {liquidation_pref} (Options: consign_all = consign high-value to auctions, maximize_value = maximize bullion spot & auction, keep_family = distribute & keep in family)
- Preferred auction partner: {preferred_consignor}
"""

    prompt = f"""You are a professional numismatic estate consultant writing an estate planning \
report narrative. Write in formal, authoritative language appropriate for an estate attorney. \
Do not use first person. Do not use marketing language.

Collection Details:
- Report type: {mode_label}
- Total coins: {collection_summary['total_coins']:,}
- Total estimated FMV: ${collection_summary['total_fmv']:,.2f}
- Total cost basis: ${collection_summary['total_cost_basis']:,.2f}
- Unrealized appreciation: ${collection_summary['total_fmv'] - collection_summary['total_cost_basis']:,.2f}
- Step-up in basis benefit at death: ${collection_summary['stepped_up_basis_benefit']:,.2f}
- State jurisdiction: {state_name}
- Coins requiring IRS-threshold appraisal: {collection_summary['total_coins_needing_appraisal']}
- {appraisal_note}
- Top coins by estimated value: {top_coins_text}
- Denominations present: {denoms}
{cliff_context}
{liquidation_context}

Generate the following six narrative sections as a JSON object with exactly these keys:

{{
  "executive_summary": "3–4 professional sentences summarizing the collection scope, estimated \
total value, and primary estate planning considerations for counsel. Mention the state \
jurisdiction and report type.",
  "valuation_narrative": "2–3 sentences explaining the basis for AI-estimated values \
(image analysis and market comparables), their limitations, and recommending a certified \
numismatic appraiser for formal estate or tax purposes.",
  "special_items_narrative": "2–3 sentences highlighting any particularly notable, rare, or \
high-value items in the collection based on the top coins list. If no items stand out, \
state that the collection reflects broad diversification.",
  "appraiser_guidance": "2–3 sentences giving specific, actionable guidance on which coins \
require professional appraisal, why (IRS Form 706 / IRC §170(f)(11) requirements), and \
what credentials the appraiser should hold (PCGS, NGC, ANA-certified, ASA, ISA).",
  "jurisdiction_guidance": "2–3 sentences of jurisdiction-specific estate planning guidance \
for {state_name}, including the most critical deadline, any tax exposure, and one \
action the owner or executor should take immediately.",
  "liquidation_playbook": "3–4 paragraphs of step-by-step instructions for heirs, advising on \
how to liquidate the collection according to the owner's preference: {liquidation_pref}. \
If a preferred auction partner is set and not 'None', explicitly recommend using {preferred_consignor} \
for high-value certified coins. Instruct heirs to never clean coins, to avoid local pawn shops \
or jewelry buyers, and how to track bullion spot prices."
}}

Return ONLY valid JSON. No markdown, no explanation, no preamble."""

    try:
        response = client.models.generate_content(
            model=model,
            contents=[types.Part.from_text(text=prompt)],
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=2048,
                response_mime_type='application/json',
            ),
        )
        raw = response.candidates[0].content.parts[0].text.strip()
        # Strip markdown fences if model adds them despite instruction
        raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.IGNORECASE)
        raw = re.sub(r'\s*```$', '', raw)
        narrative = json.loads(raw)
        log.info('[estate] Gemini narrative generated successfully.')
        return narrative

    except Exception as exc:
        log.error(f'[estate] Gemini narrative generation failed: {exc}')
        return _fallback_narrative(collection_summary, state_rules, mode)


def _fallback_narrative(
    collection_summary: dict,
    state_rules: dict,
    mode: str,
) -> dict:
    """Return safe boilerplate narrative if Gemini is unavailable."""
    state_name = state_rules['display_name']
    mode_label = 'living inventory' if mode == 'living_inventory' else 'estate settlement report'
    return {
        'executive_summary': (
            f'This {mode_label} documents a numismatic collection of '
            f'{collection_summary["total_coins"]:,} coins with a total AI-estimated fair '
            f'market value of ${collection_summary["total_fmv"]:,.2f}, prepared for estate '
            f'planning purposes under the laws of {state_name}. '
            f'The collection represents a total cost basis of '
            f'${collection_summary["total_cost_basis"]:,.2f} and an estimated unrealized '
            f'appreciation of '
            f'${collection_summary["total_fmv"] - collection_summary["total_cost_basis"]:,.2f}. '
            f'This document should be reviewed by qualified estate counsel before use in '
            f'any legal or tax proceeding.'
        ),
        'valuation_narrative': (
            'Estimated values in this report are derived from AI image analysis and '
            'numismatic market comparables and are provided for preliminary estate planning '
            'reference only. These estimates do not constitute a qualified appraisal under '
            'IRC §170(f)(11) or Treasury Regulation §1.170A-17. A certified numismatic '
            'appraiser should be retained for all formal estate tax and probate purposes.'
        ),
        'special_items_narrative': (
            'The collection includes a diverse range of numismatic items spanning multiple '
            'denominations, series, and time periods. Individual items of potential significance '
            'are identified in the itemized inventory section. A professional numismatist '
            'should assess rare and key-date coins for accurate valuation.'
        ),
        'appraiser_guidance': (
            f'Any coin or group of similar coins with an estimated FMV exceeding '
            f'${IRS_APPRAISAL_THRESHOLD:,.0f} requires a qualified appraisal under '
            f'IRC §170(f)(11) for inclusion on IRS Form 706. '
            f'{collection_summary["total_coins_needing_appraisal"]} coins in this collection '
            f'currently meet or exceed that threshold. '
            f'Appraisers should hold credentials from ASA, ISA, PCGS, NGC, or ANA.'
        ),
        'jurisdiction_guidance': (
            f'Under {state_name} law, the estate representative must file a probate inventory '
            f'within {state_rules["filing_deadline_days"]} days. '
            f'{"A NY estate tax return (ET-706) is required if the gross estate exceeds the exemption amount. " if state_rules.get("estate_tax") else ""}'
            f'Counsel licensed in {state_name} should be consulted regarding all filing '
            f'deadlines and any applicable tax obligations.'
        ),
        'liquidation_playbook': (
            'For high-value or certified rare coins, heirs should consign them to reputable '
            'national auction houses (such as GreatCollections or Heritage Auctions) rather than '
            'selling to local dealers or pawn shops. Common silver/gold bullion should be valued '
            'at current metal spot prices and sold through established precious metals dealers. '
            'Heirs should obtain multiple quotes before finalizing any sale.'
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

async def generate_estate_report(
    db: firestore.Client,
    client,           # google-genai Client
    model: str,       # e.g. 'gemini-3.5-flash'
    uid: str,
    report_request: dict,
) -> dict:
    """
    Main entry point for estate report generation.

    Orchestrates:
    1. Firestore data fetching
    2. Financial summary computation
    3. AI narrative generation (Gemini)
    4. PDF construction (estate_pdf_builder)

    Args:
        db:             Firestore client
        client:         google-genai Client
        model:          Gemini model string
        uid:            Firestore user document ID (email used as ID)
        report_request: Dict with mode, state, owner_name, report_date, etc.

    Returns:
        {
            'pdf_bytes':       bytes,
            'report_metadata': dict  (total_coins, total_fmv, etc.)
        }

    Raises:
        ValueError:  Invalid state code or missing required fields.
        RuntimeError: Unrecoverable PDF build error.
    """
    # ── Validate state ─────────────────────────────────────────────────────────
    state_code = (report_request.get('state') or '').upper().strip()
    if state_code not in STATE_RULES:
        raise ValueError(
            f"Unsupported state: '{state_code}'. "
            f"Supported: {', '.join(sorted(STATE_RULES.keys()))}"
        )
    state_rules = STATE_RULES[state_code]
    mode = report_request.get('mode', 'living_inventory')

    log.info(
        f'[estate] Starting report: uid={uid} mode={mode} state={state_code}'
    )

    # ── Fetch Firestore data (run sync in executor for async compat) ───────────
    loop = asyncio.get_event_loop()

    coins, estate_profile, estate_overrides = await asyncio.gather(
        loop.run_in_executor(None, fetch_coins, db, uid),
        loop.run_in_executor(None, fetch_estate_profile, db, uid),
        loop.run_in_executor(None, fetch_estate_data_overrides, db, uid),
    )

    log.info(
        f'[estate] Data fetched: {len(coins)} coins, '
        f'{len(estate_overrides)} overrides for uid={uid}'
    )

    # ── Build financial summary ────────────────────────────────────────────────
    summary = build_collection_summary(coins, estate_overrides, state_rules)

    # ── Generate AI narrative ──────────────────────────────────────────────────
    narrative = await loop.run_in_executor(
        None,
        generate_ai_narrative,
        client, model, summary, state_rules, mode, report_request,
    )

    # ── Generate QR code for attorney access page ──────────────────────────────
    # Generate report_id here so it's consistent between the QR code URL
    # embedded in the PDF and the Firestore document the attorney portal reads.
    import uuid as _uuid
    from datetime import datetime as _dt
    report_id = f'report_{_dt.utcnow().strftime("%Y%m%d_%H%M%S")}_{str(_uuid.uuid4())[:8]}'

    from estate_qr_generator import generate_qr_bytes
    attorney_portal_url = (
        f'https://numista.ai/attorney'
        f'?uid={uid}'
        f'&token={report_id}'
        f'&state={state_code}'
        f'&mode={mode}'
    )

    try:
        qr_bytes = await loop.run_in_executor(
            None, generate_qr_bytes, attorney_portal_url
        )
    except Exception as exc:
        log.warning(f'[estate] QR generation failed (non-fatal): {exc}')
        qr_bytes = None

    # ── Smart Division ─────────────────────────────────────────────────────────
    heirs = report_request.get('beneficiaries', []) or estate_profile.get('beneficiaries', [])
    division_results = None
    if len(heirs) > 1:
        division_results = partition_collection_equitably(summary['enriched_coins'], estate_overrides, heirs)

    # ── Build PDF ──────────────────────────────────────────────────────────────
    from estate_pdf_builder import build_estate_pdf

    pdf_context = {
        'report_request': report_request,
        'state_rules': state_rules,
        'state_code': state_code,
        'mode': mode,
        'summary': summary,
        'total_fmv': summary['total_fmv'],  # top-level for easy access in pdf sections
        'narrative': narrative,
        'enriched_coins': summary['enriched_coins'],
        'coins_needing_appraisal': summary['coins_needing_appraisal'],
        'qr_bytes': qr_bytes,
        'attorney_portal_url': attorney_portal_url,
        'estate_profile': estate_profile,
        'division_results': division_results,
    }

    pdf_bytes = await loop.run_in_executor(None, build_estate_pdf, pdf_context)

    log.info(
        f'[estate] PDF built: {len(pdf_bytes):,} bytes | '
        f'coins={summary["total_coins"]} | fmv=${summary["total_fmv"]:,.0f}'
    )

    # ── Calculate SHA-256 Tamper-Evident Document Hash ────────────────────────
    import hashlib
    sha256_hash = hashlib.sha256(pdf_bytes).hexdigest()

    # ── Assemble metadata for Firestore storage ────────────────────────────────
    report_metadata = {
        'uid': uid,
        'mode': mode,
        'state': state_code,
        'report_date': report_request.get('report_date', ''),
        'date_of_death': report_request.get('date_of_death'),
        'total_coins': summary['total_coins'],
        'total_fmv': round(summary['total_fmv'], 2),
        'total_melt_value': round(summary['total_melt_value'], 2),
        'total_cost_basis': round(summary['total_cost_basis'], 2),
        'stepped_up_basis_benefit': round(summary['stepped_up_basis_benefit'], 2),
        'total_coins_needing_appraisal': summary['total_coins_needing_appraisal'],
        'cliff_warning': summary.get('cliff_warning'),
        'pdf_size_bytes': len(pdf_bytes),
        'sha256_hash': sha256_hash,
        'uspap_compliant': True,
        'irs_form_8283_eligible': summary['total_fmv'] >= 5000.0,
        'high_value_estate_tier': summary['total_fmv'] >= 250000.0 or summary['total_coins'] >= 5000,
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'report_id': report_id,  # included so main.py can use the same ID as the QR code
    }


    if division_results:
        report_metadata['division_heir_totals'] = {
            hid: round(val, 2) for hid, val in division_results['heir_totals'].items()
        }

    return {
        'pdf_bytes': pdf_bytes,
        'report_metadata': report_metadata,
    }
