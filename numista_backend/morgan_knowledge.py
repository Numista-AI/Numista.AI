"""
morgan_knowledge.py
===================
RAG (Retrieval-Augmented Generation) lookup module for Morgan.

Given a user query, searches the Firestore `coins_reference` collection
for relevant coin entries and returns structured context that is injected
into Morgan's prompt before calling Gemini.

Usage (from main.py):
    from morgan_knowledge import get_coin_context
    context_block = get_coin_context(db, query)
    # inject context_block into the deep_dive prompt
"""

import json
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from google.cloud import firestore

# ─── CONFIG ───────────────────────────────────────────────────────────────────
COLLECTION       = "coins_reference"
MAX_RESULTS      = 5     # max coin entries to inject per query
MIN_SCORE        = 2     # minimum keyword match score to include

# ─── WAVE 2 COMPONENT C + CHAPTER 0 SHARDING: CATALOG-FIRST IN-MEMORY INDEX ───
# Canonical sanitized public catalog loaded in Cloud Run memory first (zero user Firestore reads).
_CATALOG_DEFAULT_MANIFEST_PATHS = (
    os.environ.get("CATALOG_MANIFEST_PATH", ""),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "catalog_manifest_v1.json"),
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "numista_mobile",
        "assets",
        "catalog",
        "catalog_manifest_v1.json",
    ),
)

_CATALOG_DEFAULT_PATHS = (
    os.environ.get("CATALOG_PUBLIC_JSON_PATH", ""),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "catalog_public_v1.json"),
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "numista_mobile",
        "assets",
        "catalog",
        "catalog_public_v1.json",
    ),
)

_CATALOG_INDEX_CACHE: Dict[str, Any] = {
    "loaded": False,
    "path": None,
    "source_mode": None,
    "entries": [],
    "by_nac": {},
    "by_alias": {},
    "varieties_by_parent": {},
}

# Ambiguous colloquial nicknames that span multiple U.S. series/denominations.
AMBIGUOUS_NICKNAMES: Dict[str, List[str]] = {
    "turban head": ["Capped Bust Right $5 Half Eagle (1795-1807)", "Capped Bust Right $10 Eagle (1795-1804)", "Classic / Turban Head $2.50 Quarter Eagle"],
    "draped bust": ["Draped Bust Half Cent & Large Cent", "Draped Bust Half Dime, Dime, Quarter & Half Dollar", "Draped Bust Silver Dollar (1795-1804)", "Capped Bust Right Gold $5 & $10 (colloquially called Draped Bust)"],
    "capped bust": ["Capped Bust Half Dime, Dime, Quarter & Half Dollar", "Capped Bust Right $5 & $10 Gold (1795-1807)", "Capped Bust Left $5 Gold (1807-1834)"],
    "liberty head": ["Liberty Head 'V' Nickel (1883-1913)", "Liberty Head / Barber Dime, Quarter & Half", "Liberty Head Coronet Gold ($2.50, $5, $10, $20)"],
    "indian head": ["Indian Head Cent (1859-1909)", "Indian Head / Buffalo Nickel (1913-1938)", "Indian Head Gold ($2.50, $5, $10)"],
    "mercury": ["Winged Liberty Head 'Mercury' Dime (1916-1945)", "2016 Centennial Gold Mercury Dime"],
    "buffalo": ["Buffalo / Indian Head Nickel (1913-1938)", "American Buffalo $50 Gold Bullion Coin (2006-present)"],
    "standing liberty": ["Standing Liberty Quarter (1916-1930)", "2016 Centennial Gold Standing Liberty Quarter"],
    "morgan": ["Morgan Silver Dollar (1878-1921)", "Modern Morgan Silver Dollar (2021-present)"],
    "peace": ["Peace Silver Dollar (1921-1935)", "Modern Peace Silver Dollar (2021-present)"],
    "stella": ["1879-1880 $4 Flowing Hair Stella Pattern", "1879-1880 $4 Coiled Hair Stella Pattern", "1879 $20 Quintuple Stella Pattern"],
}

_NAC1_INLINE_RE = re.compile(r"\bNAC1\.[A-Z0-9_]+(?:\.[A-Z0-9_]+){7}\b")


def reset_public_catalog_cache() -> None:
    """Reset in-memory public catalog index (used by unit tests)."""
    _CATALOG_INDEX_CACHE.update(
        loaded=False,
        path=None,
        source_mode=None,
        entries=[],
        by_nac={},
        by_alias={},
        varieties_by_parent={},
    )


def _index_catalog_entries(
    entries: List[Dict[str, Any]],
    varieties_rows: Optional[List[Dict[str, Any]]] = None,
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
    by_nac: Dict[str, Dict[str, Any]] = {}
    by_alias: Dict[str, Dict[str, Any]] = {}
    varieties_by_parent: Dict[str, List[Dict[str, Any]]] = {}
    for item in entries:
        if not isinstance(item, dict):
            continue
        nac = str(item.get("nac_code") or "").strip().upper()
        if nac:
            by_nac[nac] = item
        for alias in (item.get("nac_aliases") or []):
            if isinstance(alias, str) and alias.strip():
                by_alias[alias.strip().upper()] = item
    if varieties_rows:
        for vr in varieties_rows:
            if not isinstance(vr, dict):
                continue
            parent = str(vr.get("parent_nac1") or "").strip().upper()
            if parent:
                varieties_by_parent.setdefault(parent, []).append(vr)
    return by_nac, by_alias, varieties_by_parent


def _load_sharded_catalog_from_manifest(manifest_path: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    base_dir = os.path.dirname(os.path.abspath(manifest_path))
    with open(manifest_path, "r", encoding="utf-8") as mf:
        manifest = json.load(mf)
    if not isinstance(manifest, dict) or manifest.get("schema_version") != "catalog_sharded_v1":
        raise ValueError(f"Unsupported catalog manifest schema at {manifest_path}")

    entries: List[Dict[str, Any]] = []
    seen_nacs = set()
    for chunk in (manifest.get("chunks") or []):
        cpath = os.path.join(base_dir, chunk["path"])
        with open(cpath, "r", encoding="utf-8") as cf:
            chunk_rows = json.load(cf)
        if isinstance(chunk_rows, list):
            for item in chunk_rows:
                if not isinstance(item, dict):
                    continue
                nac = str(item.get("nac_code") or "").strip().upper()
                if nac and nac not in seen_nacs:
                    seen_nacs.add(nac)
                    entries.append(item)

    varieties_rows: List[Dict[str, Any]] = []
    var_meta = (manifest.get("child_tables") or {}).get("varieties")
    if isinstance(var_meta, dict) and var_meta.get("path"):
        vpath = os.path.join(base_dir, var_meta["path"])
        if os.path.exists(vpath):
            with open(vpath, "r", encoding="utf-8") as vf:
                raw_v = json.load(vf)
            if isinstance(raw_v, list):
                varieties_rows = [v for v in raw_v if isinstance(v, dict)]

    return entries, varieties_rows


def load_public_catalog_index(
    catalog_path: Optional[str] = None,
    entries_override: Optional[List[Dict[str, Any]]] = None,
    manifest_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Loads sanitized public catalog once into Cloud Run memory (strictly public data).
    Chapter 0: prefers sharded `catalog_manifest_v1.json` + `chunks/*.json` + `children/varieties_v1.json`,
    with transparent fallback to monolithic `catalog_public_v1.json`.
    """
    if entries_override is not None:
        entries = list(entries_override)
        by_nac, by_alias, varieties_by_parent = _index_catalog_entries(entries)
        _CATALOG_INDEX_CACHE.update(
            loaded=True,
            path="<override>",
            source_mode="override",
            entries=entries,
            by_nac=by_nac,
            by_alias=by_alias,
            varieties_by_parent=varieties_by_parent,
        )
        return _CATALOG_INDEX_CACHE

    requested_target = manifest_path or catalog_path
    if _CATALOG_INDEX_CACHE["loaded"] and (
        requested_target is None or _CATALOG_INDEX_CACHE["path"] == requested_target
    ):
        return _CATALOG_INDEX_CACHE

    # 1. Check explicit manifest_path, sibling manifest next to explicit catalog_path, or default manifest paths
    manifest_candidates: List[str] = []
    if manifest_path:
        manifest_candidates.append(manifest_path)
    elif catalog_path:
        sibling = os.path.join(os.path.dirname(os.path.abspath(catalog_path)), "catalog_manifest_v1.json")
        manifest_candidates.append(sibling)
    else:
        manifest_candidates.extend(p for p in _CATALOG_DEFAULT_MANIFEST_PATHS if p)

    chosen_manifest = next((p for p in manifest_candidates if p and os.path.exists(p)), None)
    if chosen_manifest:
        entries, varieties_rows = _load_sharded_catalog_from_manifest(chosen_manifest)
        by_nac, by_alias, varieties_by_parent = _index_catalog_entries(entries, varieties_rows)
        _CATALOG_INDEX_CACHE.update(
            loaded=True,
            path=requested_target or chosen_manifest,
            source_mode="sharded",
            entries=entries,
            by_nac=by_nac,
            by_alias=by_alias,
            varieties_by_parent=varieties_by_parent,
        )
        return _CATALOG_INDEX_CACHE

    # 2. Fallback to legacy monolithic catalog_public_v1.json
    candidates = [catalog_path] if catalog_path else list(_CATALOG_DEFAULT_PATHS)
    chosen = next((p for p in candidates if p and os.path.exists(p)), None)
    if not chosen:
        _CATALOG_INDEX_CACHE.update(
            loaded=True,
            path=None,
            source_mode=None,
            entries=[],
            by_nac={},
            by_alias={},
            varieties_by_parent={},
        )
        return _CATALOG_INDEX_CACHE

    with open(chosen, "r", encoding="utf-8") as f:
        raw = json.load(f)
    entries = raw if isinstance(raw, list) else []
    by_nac, by_alias, varieties_by_parent = _index_catalog_entries(entries)
    _CATALOG_INDEX_CACHE.update(
        loaded=True,
        path=chosen,
        source_mode="monolith",
        entries=entries,
        by_nac=by_nac,
        by_alias=by_alias,
        varieties_by_parent=varieties_by_parent,
    )
    return _CATALOG_INDEX_CACHE


def resolve_catalog_by_nac(nac_code: str, index: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Tier-0 deterministic lookup by canonical `nac_code` or retired `nac_aliases`."""
    if not nac_code or not isinstance(nac_code, str):
        return None
    idx = index or load_public_catalog_index()
    key = nac_code.strip().upper()
    return idx["by_nac"].get(key) or idx["by_alias"].get(key)


def _format_mintage_summary(item: Dict[str, Any]) -> Tuple[str, Optional[str]]:
    m = item.get("mintage")
    if isinstance(m, dict):
        val = m.get("value")
        lbl = (m.get("label") or "").strip()
        src_url = m.get("source_url")
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            val_str = f"{int(val):,}" if float(val).is_integer() else str(val)
            return (f"{val_str} ({lbl})" if lbl else val_str), src_url
        return (lbl if lbl else "Needs source (not yet sourced — do NOT invent a figure)"), src_url
    return "Needs source (not yet sourced — do NOT invent a figure)", None


def _build_catalog_card(item: Dict[str, Any]) -> Dict[str, Any]:
    """Builds a safe public inline Catalog Card payload for Morgan chat UI."""
    mintage_display, mintage_src = _format_mintage_summary(item)
    prim = item.get("primary_image") if isinstance(item.get("primary_image"), dict) else None
    timg = item.get("type_image") if isinstance(item.get("type_image"), dict) else None
    img = prim or timg or {}
    resolved_image_url = img.get("thumb_url") or img.get("url")
    return {
        "nac_code": item.get("nac_code"),
        "name": item.get("name"),
        "type": item.get("type"),
        "year": item.get("year"),
        "denomination": item.get("denomination"),
        "series": item.get("series"),
        "mint_facility": item.get("mint_facility"),
        "mintage_display": mintage_display,
        "mintage_label": mintage_display,
        "mintage_source_url": mintage_src,
        "status_badge": item.get("status_badge"),
        "image_url": resolved_image_url,
        "thumb_url": resolved_image_url,
        "image_credit": img.get("credit") or img.get("source"),
        "ai_generated": bool(img.get("ai_generated") is True),
        "actions": ["view_in_catalog", "add_to_collection", "add_to_wishlist"],
    }


def _format_catalog_entry_for_morgan(item: Dict[str, Any]) -> str:
    mintage_display, mintage_src = _format_mintage_summary(item)
    lines = [
        f"CATALOG ENTRY [{item.get('nac_code')}]: {item.get('name', 'Unknown')}",
        f"  Type/Series:   {item.get('type', '')} | {item.get('series', '')}",
        f"  Year/Denom:    {item.get('year', 'Undated')} | {item.get('denomination', '')}",
        f"  Mint Facility: {item.get('mint_facility', 'Unspecified')}",
        f"  Composition:   {item.get('composition', 'Not yet sourced')}",
        f"  Mintage:       {mintage_display}",
    ]
    if mintage_src:
        lines.append(f"  Mintage Source: {mintage_src}")
    if item.get("search_aliases"):
        lines.append(f"  Also Known As: {', '.join(item['search_aliases'])}")
    if item.get("history"):
        lines.append(f"  History:       {str(item['history'])[:320]}")
    sources = item.get("sources") or []
    if sources:
        src_labels = [str(s.get("label") or s.get("url") or "") for s in sources[:3] if isinstance(s, dict)]
        lines.append(f"  Sources:       {'; '.join(x for x in src_labels if x)}")
    return "\n".join(lines)


def _detect_ambiguous_nickname(query: str) -> Optional[Tuple[str, List[str]]]:
    ql = query.lower().strip()
    has_year = bool(re.search(r"\b(1[789]\d{2}|20[0-2]\d)\b", ql))
    has_denom = bool(
        re.search(r"\b(cent|penny|nickel|dime|quarter|half dollar|dollar|\$1|\$2\.50|\$4|\$5|\$10|\$20|50c|25c|10c|5c|1c)\b", ql)
    )
    if has_year or has_denom:
        return None
    for nick, options in AMBIGUOUS_NICKNAMES.items():
        if nick in ql:
            return nick, options
    return None


def get_catalog_context(
    query: str,
    *,
    nac_code: Optional[str] = None,
    max_results: int = MAX_RESULTS,
    catalog_index: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Wave 2 Component C: Catalog-First Morgan AI lookup (strictly public JSON, zero user Firestore reads).
    Returns:
      {
        "context_block": Optional[str],
        "catalog_cards": List[dict],
        "needs_disambiguation": bool,
        "disambiguation_options": List[str],
        "missing_item_report_prompt": Optional[dict],
        "matched_tier": "tier0_nac" | "tier1_catalog" | "none",
      }
    """
    idx = catalog_index or load_public_catalog_index()
    entries = idx.get("entries") or []

    # Tier 0: Explicit nac_code argument or inline NAC1.* code in query
    explicit_nac = (nac_code or "").strip()
    if not explicit_nac and query:
        m = _NAC1_INLINE_RE.search(query.upper())
        if m:
            explicit_nac = m.group(0)
    if explicit_nac:
        hit = resolve_catalog_by_nac(explicit_nac, index=idx)
        if hit:
            header = (
                "CATALOG OF AMERICAN NUMISMATICS — VERIFIED PRIMARY RECORD (Tier 0 Exact Match):\n"
                "Treat the facts below as authoritative. Never override a verified mintage and NEVER invent a mintage when marked 'Needs source' or 'not yet sourced'.\n"
            )
            return {
                "context_block": f"{header}\n{_format_catalog_entry_for_morgan(hit)}\n",
                "catalog_cards": [_build_catalog_card(hit)],
                "needs_disambiguation": False,
                "disambiguation_options": [],
                "missing_item_report_prompt": None,
                "matched_tier": "tier0_nac",
            }

    q = (query or "").strip()
    if not q or not entries:
        return {
            "context_block": None,
            "catalog_cards": [],
            "needs_disambiguation": False,
            "disambiguation_options": [],
            "missing_item_report_prompt": {"query": q} if q else None,
            "matched_tier": "none",
        }

    ql = q.lower()
    years = re.findall(r"\b(1[789]\d{2}|20[0-2]\d)\b", ql)
    tokens = [t for t in re.findall(r"[a-z0-9\$]+", ql) if t not in STOP_WORDS and len(t) > 1]

    scored: List[Tuple[int, Dict[str, Any]]] = []
    for item in entries:
        name = str(item.get("name") or "").lower()
        series = str(item.get("series") or "").lower()
        denom = str(item.get("denomination") or "").lower()
        year_str = str(item.get("year") or "").lower()
        aliases = " ".join(str(a).lower() for a in (item.get("search_aliases") or []) if isinstance(a, str))
        nac = str(item.get("nac_code") or "").lower()
        hay = f"{name} {series} {denom} {year_str} {aliases} {nac}"

        score = 0
        if ql in name or ql in aliases:
            score += 12
        for y in years:
            if y == year_str:
                score += 8
        matched_tokens = 0
        for tok in tokens:
            if tok in aliases:
                score += 5
                matched_tokens += 1
            elif tok in name or tok in series:
                score += 4
                matched_tokens += 1
            elif tok in hay:
                score += 2
                matched_tokens += 1
        if tokens and matched_tokens == len(tokens):
            score += 6
        if score >= 5:
            scored.append((score, item))

    scored.sort(key=lambda pair: (pair[0], 1 if pair[1].get("primary_image") else 0), reverse=True)
    top = [it for _, it in scored[:max_results]]

    disamb = _detect_ambiguous_nickname(q)
    needs_disamb = disamb is not None and len({str(it.get("series") or "") for it in top}) != 1

    if not top:
        honest_block = (
            "CATALOG OF AMERICAN NUMISMATICS — NO VERIFIED MATCH FOUND:\n"
            f"The user asked about '{q}', which is not currently in our verified Catalog of American Numismatics.\n"
            "MORGAN §1 HONESTY RULE: State plainly that this item is not yet in our verified catalog. "
            "NEVER invent mintage numbers or specifications. Invite the user to tap 'Report Missing Item' so our catalog team can research and verify it from official sources.\n"
        )
        return {
            "context_block": honest_block,
            "catalog_cards": [],
            "needs_disambiguation": bool(disamb),
            "disambiguation_options": disamb[1] if disamb else [],
            "missing_item_report_prompt": {"query": q},
            "matched_tier": "none",
        }

    header = (
        "CATALOG OF AMERICAN NUMISMATICS — VERIFIED PUBLIC RECORDS (Tier 1 Catalog-First):\n"
        "Use ONLY these verified catalog facts for mintages, specifications, and sources. "
        "If a field says 'Needs source' or 'not yet sourced', state honestly that it is not yet sourced — NEVER invent or guess numbers. "
        "Never cite Greysheet wholesale prices or GSIDs.\n"
    )
    if needs_disamb and disamb is not None:
        header += (
            f"DISAMBIGUATION REQUIRED: '{disamb[0]}' refers to multiple U.S. series "
            f"({'; '.join(disamb[1])}). Ask a brief clarifying question naming these options instead of guessing one coin.\n"
        )

    body = "\n\n".join(_format_catalog_entry_for_morgan(it) for it in top)
    return {
        "context_block": f"{header}\n{body}\n",
        "catalog_cards": [_build_catalog_card(it) for it in top],
        "needs_disambiguation": needs_disamb,
        "disambiguation_options": disamb[1] if (needs_disamb and disamb is not None) else [],
        "missing_item_report_prompt": None,
        "matched_tier": "tier1_catalog",
    }


def record_missing_catalog_request(
    db: Any,
    query: str,
    *,
    requester_uid: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Safely queues a missing-item report into internal Firestore `catalog_missing_requests`
    for Morgan review. NEVER auto-scrapes Wikipedia and NEVER auto-publishes to live catalog.
    """
    cleaned = re.sub(r"\s+", " ", (query or "").strip())[:240]
    if not cleaned:
        raise ValueError("Missing-item query must not be empty")
    payload = {
        "query": cleaned,
        "requester_uid": requester_uid,
        "status": "pending_morgan_review",
        "auto_published": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if db is not None:
        db.collection("catalog_missing_requests").document().set(payload)
    return payload

# ─── KEYWORD EXTRACTION ───────────────────────────────────────────────────────

# Common words to ignore when matching
STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "can", "what", "which", "who",
    "how", "when", "where", "why", "my", "your", "his", "her", "their",
    "its", "our", "this", "that", "these", "those", "coin", "coins",
    "about", "tell", "me", "us", "know", "like", "just", "get", "got",
    "need", "want", "please", "thanks", "and", "or", "but", "not",
    "with", "for", "from", "on", "in", "at", "to", "of", "by", "up",
}

# Keyword → series/type hints for better retrieval
SERIES_HINTS = {
    # State quarters
    "state quarter":       "50 State Quarters",
    "state quarters":      "50 State Quarters",
    "50 state":            "50 State Quarters",
    "delaware":            "50 State Quarters",
    "pennsylvania":        "50 State Quarters",
    # Morgan dollar
    "morgan":              "Morgan Silver Dollar",
    "morgan dollar":       "Morgan Silver Dollar",
    # Peace dollar
    "peace dollar":        "Peace Dollar",
    # Lincoln cent
    "lincoln":             "Lincoln Cent",
    "wheat cent":          "Lincoln Wheat Cent",
    "wheat penny":         "Lincoln Wheat Cent",
    "penny":               "Lincoln Cent",
    "cent":                "Lincoln Cent",
    # Buffalo nickel
    "buffalo":             "Buffalo Nickel",
    "buffalo nickel":      "Buffalo Nickel",
    "indian head nickel":  "Buffalo Nickel",
    # Jefferson nickel
    "jefferson":           "Jefferson Nickel",
    # Mercury dime
    "mercury":             "Mercury Dime",
    "mercury dime":        "Mercury Dime",
    # Roosevelt dime
    "roosevelt":           "Roosevelt Dime",
    # Kennedy half
    "kennedy":             "Kennedy Half Dollar",
    "half dollar":         "Kennedy Half Dollar",
    # Walking Liberty
    "walking liberty":     "Walking Liberty Half Dollar",
    # Fugio
    "fugio":               "Early American & Colonial Coppers",
    # Bicentennial
    "bicentennial":        "Bicentennial",
    "1776":                "Bicentennial",
    # Eisenhower
    "ike":                 "Eisenhower Dollar",
    "eisenhower":          "Eisenhower Dollar",
    # American Eagle
    "american eagle":      "American Gold Eagle",
    "silver eagle":        "American Silver Eagle",
    # Commemorative
    "commemorative":       "Commemorative",
    # Error coins
    "error":               "error",
    "doubled die":         "Doubled Die",
    "double die":          "Doubled Die",
    "ddo":                 "Doubled Die Obverse",
    "off center":          "Off-Center",
    "broadstrike":         "Broadstrike",
    "clipped":             "Clipped Planchet",
}


def extract_keywords(query: str) -> list[str]:
    """Extract meaningful keywords from the user's query."""
    q = query.lower()

    # Check for compound hints first
    hints_found = []
    for phrase, series in SERIES_HINTS.items():
        if phrase in q:
            hints_found.append(series.lower())

    # Extract individual tokens
    tokens = re.findall(r'\b[a-z0-9]+\b', q)
    meaningful = [t for t in tokens if t not in STOP_WORDS and len(t) > 2]

    # Extract 4-digit years
    years = re.findall(r'\b(1[0-9]{3}|20[0-2][0-9])\b', query)

    return list(set(meaningful + hints_found + years))


def score_coin(coin: dict, keywords: list[str]) -> int:
    """Score how relevant a coin entry is to the extracted keywords."""
    # Build a single searchable text blob from the coin's fields
    text = " ".join([
        str(coin.get("series", "")),
        str(coin.get("year", "")),
        str(coin.get("denomination", "")),
        str(coin.get("variety", "")),
        str(coin.get("note", "")),
        str(coin.get("composition", "")),
        str(coin.get("design_obverse", "")),
        str(coin.get("design_reverse", "")),
        str(coin.get("design_description", "")),
        str(coin.get("coin_id", "")),
    ]).lower()

    score = 0
    for kw in keywords:
        if kw in text:
            # Year matches are high-value signals
            if re.match(r'^\d{4}$', kw):
                score += 5
            # Series/denomination/variety matches
            elif kw in str(coin.get("series", "")).lower() or kw in str(coin.get("variety", "")).lower():
                score += 4
            else:
                score += 1

    return score


def format_coin_for_context(coin: dict) -> str:
    """Format a single coin entry as a readable context block."""
    lines = [
        f"COIN: {coin.get('series', 'Unknown Series')} — {coin.get('year', '')} {coin.get('variety', '')}",
        f"  Category:      {coin.get('category', '')}",
        f"  Denomination:  {coin.get('denomination', '')}",
        f"  Composition:   {coin.get('composition', '')}",
        f"  Obverse:       {coin.get('design_obverse', '')}",
        f"  Reverse:       {coin.get('design_reverse', '')}",
    ]
    if coin.get("note"):
        lines.append(f"  Note:          {coin.get('note')}")
    if coin.get("design_description"):
        desc = coin["design_description"]
        # Truncate long descriptions
        if len(desc) > 300:
            desc = desc[:297] + "..."
        lines.append(f"  Description:   {desc}")
    if coin.get("mint_marks"):
        lines.append(f"  Mint marks:    {', '.join(coin['mint_marks'])}")
    if coin.get("mintage_notes"):
        lines.append(f"  Mintage:       {coin['mintage_notes']}")
    if coin.get("fun_facts"):
        for fact in coin["fun_facts"][:2]:
            lines.append(f"  ★ {fact}")
    return "\n".join(lines)


# ─── PUBLIC API ───────────────────────────────────────────────────────────────

def _extract_struct(struct_data) -> dict:
    """Convert a protobuf Struct to a plain Python dict, handling both Protobuf Value objects and raw values."""
    out = {}
    if not struct_data:
        return out
    try:
        for key, value in struct_data.items():
            if hasattr(value, "WhichOneof"):
                try:
                    kind = value.WhichOneof("kind")
                    if kind == "string_value":
                        out[key] = value.string_value
                    elif kind == "number_value":
                        out[key] = value.number_value
                    elif kind == "bool_value":
                        out[key] = value.bool_value
                    else:
                        out[key] = str(value)
                except Exception:
                    out[key] = str(value)
            else:
                out[key] = value
    except Exception as e:
        print(f"[morgan_knowledge] Error extracting struct: {e}")
    return out


def get_coin_context_vertex(query: str, max_results: int = MAX_RESULTS) -> Optional[str]:
    """Query the Vertex AI Search engine (Discovery Engine) using configuration in ids.json."""
    try:
        from google.cloud import discoveryengine_v1 as de
        import os
        import json
        
        # Load configuration
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ids_path = os.path.join(current_dir, "vertex_search", "ids.json")
        if not os.path.exists(ids_path):
            print(f"[morgan_knowledge] ids.json not found at: {ids_path}")
            return None
            
        with open(ids_path) as f:
            config = json.load(f)
            
        serving_config = config.get("serving_config")
        if not serving_config:
            print("[morgan_knowledge] serving_config missing from ids.json")
            return None
            
        client = de.SearchServiceClient()
        request = de.SearchRequest(
            serving_config=serving_config,
            query=query,
            page_size=max_results,
            query_expansion_spec=de.SearchRequest.QueryExpansionSpec(
                condition=de.SearchRequest.QueryExpansionSpec.Condition.AUTO,
            ),
            spell_correction_spec=de.SearchRequest.SpellCorrectionSpec(
                mode=de.SearchRequest.SpellCorrectionSpec.Mode.AUTO,
            ),
            content_search_spec=de.SearchRequest.ContentSearchSpec(
                snippet_spec=de.SearchRequest.ContentSearchSpec.SnippetSpec(
                    return_snippet=True,
                    max_snippet_count=1,
                ),
            ),
        )
        
        response = client.search(request=request)
        if not response.results:
            return None
            
        header = (
            "NUMISMATIC REFERENCE DATA (from Vertex AI Search knowledge base):\n"
            "Use the following verified coin information to answer the user's question accurately.\n"
            "If the user's question matches one of these coins, cite these facts.\n"
        )
        
        formatted_entries = []
        for hit in response.results:
            doc = hit.document
            sd = _extract_struct(doc.struct_data)
            
            # Check for unstructured content snippets (e.g. Canon Markdown files)
            derived = _extract_struct(getattr(doc, "derived_struct_data", None))
            snippets = derived.get("snippets", [])
            snippet_text = ""
            if isinstance(snippets, list) and len(snippets) > 0:
                s_obj = snippets[0]
                if isinstance(s_obj, dict):
                    snippet_text = s_obj.get("snippet", "")
            elif isinstance(snippets, str):
                snippet_text = snippets
            
            title = derived.get("title") or sd.get("program_name") or sd.get("coin_name") or "Numista Canon Document"
            
            if not sd.get("program_name") and not sd.get("coin_name") and snippet_text:
                # Unstructured Canon Document Hit
                entry_lines = [
                    f"DOCUMENT: {title}",
                    f"  Excerpt: {snippet_text}",
                ]
            else:
                # Structured Coin Program Hit
                entry_lines = [
                    f"COIN: {sd.get('program_name', 'Unknown Series')} — {sd.get('coin_year', '')} {sd.get('coin_name', '')}",
                    f"  Category:      {sd.get('category', '')}",
                    f"  Denomination:  {sd.get('denomination', '')}",
                    f"  Metal:         {sd.get('metal', '')}",
                    f"  Mint marks:    {sd.get('mint_marks', '')}",
                ]
                
                content_str = sd.get("content", "")
                obverse_match = re.search(r"Obverse:\s*(.*?)(?=\s*\|\s*(?:Reverse:|Base baseline|$))", content_str)
                reverse_match = re.search(r"Reverse:\s*(.*?)(?=\s*\|\s*(?:Base baseline|$))", content_str)
                
                obverse_text = obverse_match.group(1).strip() if obverse_match else ""
                reverse_text = reverse_match.group(1).strip() if reverse_match else ""
                
                if obverse_text:
                    entry_lines.append(f"  Obverse:       {obverse_text}")
                if reverse_text:
                    entry_lines.append(f"  Reverse:       {reverse_text}")
                    
                if sd.get('designer'):
                    entry_lines.append(f"  Designer:      {sd.get('designer')}")
                if sd.get('notes'):
                    entry_lines.append(f"  Description:   {sd.get('notes')}")
                if snippet_text and not obverse_text and not reverse_text:
                    entry_lines.append(f"  Snippet:       {snippet_text}")
                
            formatted_entries.append("\n".join(entry_lines))
            
        return f"{header}\n" + "\n\n".join(formatted_entries) + "\n"
        
    except Exception as e:
        print(f"[morgan_knowledge] Vertex AI Search lookup error: {e}")
        return None


def get_coin_context(
    db: Optional[firestore.Client],
    query: str,
    max_results: int = MAX_RESULTS,
    nac_code: Optional[str] = None,
) -> Optional[str]:
    """
    Catalog-First Morgan RAG lookup (Wave 2 Component C):
      1. Tier 0 / Tier 1: Authoritative in-memory `catalog_public_v1.json` (zero user Firestore reads).
      2. Tier 2: Vertex AI Search (general encyclopedia augmentation) if catalog has no match.
      3. Tier 3: Legacy Firestore `coins_reference` fallback (only when `db` is provided).
    """
    if (not query or not query.strip()) and not nac_code:
        return None

    # 0. Catalog-First lookup (Tier 0 exact nac_code/alias + Tier 1 public catalog search)
    cat_res = get_catalog_context(query, nac_code=nac_code, max_results=max_results)
    if cat_res["matched_tier"] in ("tier0_nac", "tier1_catalog") and cat_res["context_block"]:
        return cat_res["context_block"]

    # 1. Try Vertex AI Search next for general numismatic background
    vertex_context = get_coin_context_vertex(query, max_results)
    if vertex_context:
        print(f"[morgan_knowledge] Successfully retrieved RAG context from Vertex AI Search for: {query!r}")
        if cat_res["context_block"]:
            return f"{cat_res['context_block']}\n{vertex_context}"
        return vertex_context

    if db is None:
        return cat_res["context_block"]

    print(f"[morgan_knowledge] Vertex AI Search unavailable or empty for {query!r}; falling back to Firestore keyword match.")

    # 2. Fallback to Firestore keyword matching
    keywords = extract_keywords(query)
    if not keywords:
        return None

    # ── Query Firestore ────────────────────────────────────────────────────────
    # Strategy: fetch a reasonable sample and score in Python.
    # For collections up to ~2,000 docs this is fast (< 200ms).
    # For larger collections, add Firestore indexes or use Vertex AI Search.
    try:
        docs = db.collection(COLLECTION).stream()
        scored = []
        for doc in docs:
            coin = doc.to_dict()
            score = score_coin(coin, keywords)
            if score >= MIN_SCORE:
                scored.append((score, coin))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        top_coins = [coin for _, coin in scored[:max_results]]

    except Exception as e:
        # Never let a knowledge base failure break Morgan's chat
        print(f"[morgan_knowledge] Warning: Firestore query failed: {e}")
        return None

    if not top_coins:
        return None

    # 3. Add Brain Knowledge Base (Autonomous Learning)
    brain_context = ""
    try:
        # Search the last 50 documents absorbed into the brain
        brain_docs = db.collection('brain_knowledge_base').order_by('absorbed_at', direction=firestore.Query.DESCENDING).limit(50).stream()
        brain_scored = []
        for doc in brain_docs:
            data = doc.to_dict()
            # Simple keyword search in summary and file content
            text = f"{data.get('filename', '')} {data.get('summary', '')}".lower()
            score = 0
            for kw in keywords:
                if kw in text: score += 1
            if score > 0:
                brain_scored.append((score, data))
        
        if brain_scored:
            brain_scored.sort(key=lambda x: x[0], reverse=True)
            top_brain = brain_scored[:3]
            brain_context = "\n\nSUPPLEMENTAL BRAIN KNOWLEDGE (from user-provided docs):\n"
            for _, b in top_brain:
                brain_context += f"- DOC: {b.get('filename')}\n  SUMMARY: {b.get('summary')}\n"
                if b.get('type'): brain_context += f"  TYPE: {b.get('type')}\n"

    except Exception as e:
        print(f"[morgan_knowledge] Brain lookup error: {e}")

    # ── Format context block ───────────────────────────────────────────────────
    header = (
        "NUMISMATIC REFERENCE DATA (from Numista.AI knowledge base):\n"
        "Use the following verified coin information to answer the user's question accurately.\n"
        "If the user's question matches one of these coins, cite these facts.\n"
    )
    
    main_entries = ""
    if top_coins:
        main_entries = "\n\n".join(format_coin_for_context(c) for c in top_coins)

    final_context = f"{header}\n{main_entries}" if main_entries else ""
    if brain_context:
        final_context += brain_context
        
    return final_context if final_context else None


def get_coin_by_id(db: firestore.Client, coin_id: str) -> Optional[dict]:
    """Direct lookup of a specific coin by its coin_id."""
    try:
        doc = db.collection(COLLECTION).document(coin_id).get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        print(f"[morgan_knowledge] Lookup error for {coin_id}: {e}")
        return None


def build_user_collection_snapshot(db: firestore.Client, user_email: str) -> str:
    """
    Builds a compact ~300 token system prompt header summarizing the user's collection.
    Allows Morgan to be 'Coin-Aware' of holdings, total value, top coins, and gaps.
    """
    try:
        user_coins_ref = db.collection('users').document(user_email).collection('portfolio').limit(100).stream()
        coins = [c.to_dict() for c in user_coins_ref]
        if not coins:
            # Fallback to collection 'coins'
            user_coins_ref = db.collection('users').document(user_email).collection('coins').limit(100).stream()
            coins = [c.to_dict() for c in user_coins_ref]

        if not coins:
            return f"USER PORTFOLIO CONTEXT:\n- User '{user_email}' currently has 0 coins logged in portfolio.\n"

        total_count = len(coins)
        total_val = 0.0
        series_counts = {}
        top_items = []

        for c in coins:
            val_str = str(c.get('market_value', c.get('cost_basis', c.get('Price Paid', 0)))).replace('$', '').replace(',', '')
            try:
                val = float(val_str)
            except ValueError:
                val = 0.0
            total_val += val

            ser = c.get('programSeries', c.get('denomination', 'US Coins'))
            series_counts[ser] = series_counts.get(ser, 0) + 1

            yr = c.get('year', c.get('Year', ''))
            mint = c.get('mint_mark', c.get('Mint Mark', ''))
            grade = c.get('condition', c.get('Grade', 'Ungraded'))
            title = f"{yr} {mint} {ser} ({grade})".strip()
            top_items.append((val, title))

        top_items.sort(key=lambda x: x[0], reverse=True)
        top_str = ", ".join(f"{title} [${val:,.2f}]" for val, title in top_items[:5] if val > 0)
        if not top_str and top_items:
            top_str = ", ".join(title for _, title in top_items[:5])

        top_series_str = ", ".join(f"{k} ({v})" for k, v in list(series_counts.items())[:4])

        snapshot = (
            f"📊 USER PORTFOLIO SNAPSHOT (Live Context):\n"
            f"- Owner: {user_email}\n"
            f"- Total Tracked Items: {total_count} coins\n"
            f"- Estimated Collection Value: ${total_val:,.2f}\n"
            f"- Key Series Tracked: {top_series_str if top_series_str else 'General US Coins'}\n"
            f"- Top Holdings: {top_str if top_str else 'N/A'}\n"
            f"Use this personal collection context to answer questions about what the user owns or needs!\n"
        )
        return snapshot

    except Exception as e:
        print(f"[morgan_knowledge] Collection snapshot error: {e}")
        return f"USER PORTFOLIO CONTEXT:\n- Owner: {user_email}\n"

