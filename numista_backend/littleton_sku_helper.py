"""
littleton_sku_helper.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hybrid 3-Layer SKU Resolution for Littleton Coin Company Imports
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cloud Run is stateless — local SQLite writes are lost when instances recycle.
This module implements a safe tiered lookup to handle that reality:

    Layer 1 — LOCAL SQLITE (numista.db → littleton_sku_dictionary table)
               Read-only. Pre-seeded at deploy time via seed_littleton_skus.py.
               Fastest possible lookup; zero network latency.

    Layer 2 — FIRESTORE (global_metadata/littleton_sku_dictionary/{sku})
               Shared, persistent across all Cloud Run instances and deploys.
               Any new SKU resolved by Gemini is written here so every future
               instance immediately benefits from the discovery.

    Layer 3 — GEMINI 3.5-FLASH (item type classifier)
               Last resort. Parses the raw description and returns structured
               numismatic fields. Result is written to Firestore (Layer 2) so
               the next lookup for the same SKU hits cache.

Public API
──────────
    resolve_sku(sku, description, conn, db, genai_client, model) → LittletonResolution

    LittletonResolution fields:
        canonical_ref_id   str    — Matches Golden Schema "Personal Reference #" (LCC)
        implied_condition  str    — Standard numismatic grade string
        program_series     str    — Golden Schema "Program/Series"
        year               str    — 4-digit year or ""
        mint_mark          str    — "P", "D", "S", etc., or ""
        denomination       str    — e.g. "Dollar", "Quarter"
        item_type          str    — "coin" | "medal" | "paper_currency" | "supply"
        source             str    — "sqlite" | "firestore" | "gemini"

    ensure_sku_table(conn)   — Idempotent table creation for numista.db
    save_sku_to_firestore(db, sku, resolution) — Persist newly resolved SKU
"""

import json
import re
import sqlite3
from typing import Optional, TypedDict

# ─── TypedDict for structured returns ────────────────────────────────────────

class LittletonResolution(TypedDict):
    canonical_ref_id:  str
    implied_condition: str
    program_series:    str
    year:              str
    mint_mark:         str
    denomination:      str
    item_type:         str
    source:            str   # "sqlite" | "firestore" | "gemini"


# ─── Firestore path constants ─────────────────────────────────────────────────
# Shared collection visible to every Cloud Run instance and every admin script.
# Path:  global_metadata/littleton_sku_dictionary/{sku_doc}
_FS_GLOBAL_META_DOC   = "littleton_sku_dictionary"
_FS_GLOBAL_META_COLL  = "global_metadata"


# ─── LAYER 1: SQLite helpers ──────────────────────────────────────────────────

def ensure_sku_table(conn: sqlite3.Connection) -> None:
    """
    Idempotent CREATE TABLE for the Littleton SKU dictionary.

    This table lives inside numista.db and is pre-populated at deploy time
    by seed_littleton_skus.py. The Cloud Run process opens numista.db as
    READ-ONLY for lookups; never writes to it at runtime.

    Schema
    ──────
    littleton_sku   TEXT PK    — e.g. "CD-9999", "ME-1234"
    description     TEXT       — Raw Littleton product description
    canonical_ref_id TEXT      — Internal Numista.AI reference token
    implied_condition TEXT     — Standard grade string (e.g. "Uncirculated")
    program_series  TEXT       — Golden Schema Program/Series
    year            TEXT       — 4-digit year or ""
    mint_mark       TEXT       — Mint mark code or ""
    denomination    TEXT       — e.g. "Dollar", "Quarter"
    item_type       TEXT       — "coin" | "medal" | "paper_currency" | "supply"
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS littleton_sku_dictionary (
            littleton_sku    TEXT PRIMARY KEY,
            description      TEXT NOT NULL DEFAULT '',
            canonical_ref_id TEXT NOT NULL DEFAULT '',
            implied_condition TEXT NOT NULL DEFAULT 'Uncirculated',
            program_series   TEXT NOT NULL DEFAULT '',
            year             TEXT NOT NULL DEFAULT '',
            mint_mark        TEXT NOT NULL DEFAULT '',
            denomination     TEXT NOT NULL DEFAULT '',
            item_type        TEXT NOT NULL DEFAULT 'coin'
        )
    """)
    conn.commit()


def lookup_sku_sqlite(conn: sqlite3.Connection, sku: str) -> Optional[LittletonResolution]:
    """
    Layer 1: Check the local read-only SQLite seed table.
    Returns a LittletonResolution dict on hit, None on miss.
    All dict access uses .get() to guarantee no KeyError.
    """
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM littleton_sku_dictionary WHERE littleton_sku = ?",
            (sku.strip().upper(),)
        )
        row = cur.fetchone()
        if row is None:
            return None

        row_dict = dict(row)
        return LittletonResolution(
            canonical_ref_id  = row_dict.get("canonical_ref_id", ""),
            implied_condition = row_dict.get("implied_condition", "Uncirculated"),
            program_series    = row_dict.get("program_series", ""),
            year              = row_dict.get("year", ""),
            mint_mark         = row_dict.get("mint_mark", ""),
            denomination      = row_dict.get("denomination", ""),
            item_type         = row_dict.get("item_type", "coin"),
            source            = "sqlite",
        )
    except Exception as exc:
        print(f"[littleton_sku_helper] SQLite lookup error for SKU '{sku}': {exc}")
        return None


# ─── LAYER 2: Firestore shared cache ─────────────────────────────────────────

def lookup_sku_firestore(db, sku: str) -> Optional[LittletonResolution]:
    """
    Layer 2: Check the persistent shared Firestore cache.

    Path:  global_metadata/littleton_sku_dictionary/{sanitized_sku}
    Returns a LittletonResolution dict on hit, None on miss or error.
    """
    try:
        doc_ref = (
            db.collection(_FS_GLOBAL_META_COLL)
              .document(_FS_GLOBAL_META_DOC)
              .collection("skus")
              .document(_sanitize_sku_for_doc_id(sku))
        )
        snap = doc_ref.get()
        if not snap.exists:
            return None

        data = snap.to_dict() or {}
        return LittletonResolution(
            canonical_ref_id  = data.get("canonical_ref_id", ""),
            implied_condition = data.get("implied_condition", "Uncirculated"),
            program_series    = data.get("program_series", ""),
            year              = data.get("year", ""),
            mint_mark         = data.get("mint_mark", ""),
            denomination      = data.get("denomination", ""),
            item_type         = data.get("item_type", "coin"),
            source            = "firestore",
        )
    except Exception as exc:
        print(f"[littleton_sku_helper] Firestore lookup error for SKU '{sku}': {exc}")
        return None


def save_sku_to_firestore(db, sku: str, description: str, resolution: LittletonResolution) -> None:
    """
    Persist a newly Gemini-resolved SKU mapping to the shared Firestore cache.
    This write survives instance recycling and is visible to all Cloud Run pods.

    On error, logs and continues — a failed write is non-fatal; the user's
    coin record is still committed to review_queue regardless.
    """
    try:
        from google.cloud import firestore as _fs
        doc_ref = (
            db.collection(_FS_GLOBAL_META_COLL)
              .document(_FS_GLOBAL_META_DOC)
              .collection("skus")
              .document(_sanitize_sku_for_doc_id(sku))
        )
        doc_ref.set({
            "littleton_sku":    sku.strip().upper(),
            "description":      description,
            "canonical_ref_id": resolution.get("canonical_ref_id", ""),
            "implied_condition": resolution.get("implied_condition", "Uncirculated"),
            "program_series":   resolution.get("program_series", ""),
            "year":             resolution.get("year", ""),
            "mint_mark":        resolution.get("mint_mark", ""),
            "denomination":     resolution.get("denomination", ""),
            "item_type":        resolution.get("item_type", "coin"),
            "resolved_by":      "gemini",
            "created_at":       _fs.SERVER_TIMESTAMP,
        }, merge=True)
        print(f"[littleton_sku_helper] Saved new SKU '{sku}' to Firestore cache.")
    except Exception as exc:
        print(f"[littleton_sku_helper] Firestore write error for SKU '{sku}': {exc}")


# ─── LAYER 3: Gemini 3.5-flash fallback ──────────────────────────────────────

_LITTLETON_CLASSIFY_PROMPT = """\
You are a senior US numismatic cataloger for Numista.AI.
A Littleton Coin Company order line item needs to be classified into the Numista.AI Golden Schema.

Raw Littleton product description:
\"{description}\"

Respond ONLY with a single raw JSON object — no markdown fences, no commentary. Use exactly these keys:

{{
  "canonical_ref_id":  "<a short normalized reference token, e.g. 'LCC-MORGAN-1921-D-AU'>",
  "implied_condition": "<standard numismatic grade, e.g. 'Uncirculated', 'Fine', 'MS-63', 'Proof', 'Circulated'>",
  "program_series":    "<official US series name, e.g. 'Morgan Silver Dollar', 'Lincoln Cent', 'American Eagle Silver Dollar'>",
  "year":              "<4-digit year string, or empty string if unknown/multi-year set>",
  "mint_mark":         "<single uppercase letter: P, D, S, W, CC, O — or empty string>",
  "denomination":      "<denomination name, e.g. 'Dollar', 'Half Dollar', 'Quarter', 'Cent'>",
  "item_type":         "<one of: coin | medal | paper_currency | supply>"
}}

Rules:
- implied_condition must reflect what Littleton typically sells for this product type
  (bulk circulated = 'Circulated'; singles described as BU/Unc = 'Uncirculated', etc.)
- If year is ambiguous (e.g. date range or assorted), use empty string.
- Never return null; use empty string for unknown string fields.
"""


def resolve_via_gemini(
    genai_client,
    model: str,
    description: str,
) -> LittletonResolution:
    """
    Layer 3: Call Gemini 3.5-flash to parse a raw Littleton description.

    Returns a LittletonResolution with source="gemini".
    On any error, returns a safe fallback resolution so the ingestion
    pipeline never stalls on a single unresolvable SKU.
    """
    # Safe fallback in case Gemini fails at any point
    fallback = LittletonResolution(
        canonical_ref_id  = "",
        implied_condition = "Uncirculated",
        program_series    = "",
        year              = "",
        mint_mark         = "",
        denomination      = "",
        item_type         = "coin",
        source            = "gemini",
    )

    try:
        from google.genai import types as genai_types

        filled_prompt = _LITTLETON_CLASSIFY_PROMPT.format(
            description=description.replace('"', '\\"')
        )

        response = genai_client.models.generate_content(
            model=model,
            contents=[genai_types.Part.from_text(text=filled_prompt)],
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0,
                max_output_tokens=512,
            ),
        )

        raw_text = (response.text or "").strip()

        # Strip any accidental markdown fences the model may emit
        if raw_text.startswith("```"):
            raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.MULTILINE)
            raw_text = re.sub(r"\s*```$",          "", raw_text, flags=re.MULTILINE)

        parsed: dict = json.loads(raw_text)

        return LittletonResolution(
            canonical_ref_id  = str(parsed.get("canonical_ref_id",  "") or ""),
            implied_condition = str(parsed.get("implied_condition",  "Uncirculated") or "Uncirculated"),
            program_series    = str(parsed.get("program_series",    "") or ""),
            year              = str(parsed.get("year",              "") or ""),
            mint_mark         = str(parsed.get("mint_mark",         "") or ""),
            denomination      = str(parsed.get("denomination",      "") or ""),
            item_type         = str(parsed.get("item_type",         "coin") or "coin"),
            source            = "gemini",
        )

    except json.JSONDecodeError as exc:
        print(f"[littleton_sku_helper] Gemini JSON parse error: {exc} | raw: {raw_text[:200]}")
        return fallback
    except Exception as exc:
        print(f"[littleton_sku_helper] Gemini resolution error: {exc}")
        return fallback


# ─── Primary public function ──────────────────────────────────────────────────

def resolve_sku(
    sku:          str,
    description:  str,
    conn:         sqlite3.Connection,
    db,
    genai_client,
    model:        str,
) -> LittletonResolution:
    """
    Resolve a Littleton SKU using the 3-layer hybrid pipeline:

        Layer 1 → SQLite static seed (sub-ms, zero network)
        Layer 2 → Firestore shared cache (covers runtime discoveries)
        Layer 3 → Gemini 3.5-flash (new SKU; result written back to Firestore)

    Parameters
    ──────────
    sku          : Raw SKU string from the Littleton order record.
    description  : Full product description string for Gemini fallback.
    conn         : sqlite3.Connection to numista.db (caller manages lifecycle).
    db           : google.cloud.firestore.Client from main.py.
    genai_client : google.genai.Client from main.py.
    model        : Model name constant (e.g. PRIMARY_MODEL = "gemini-3.5-flash").

    Returns
    ───────
    LittletonResolution TypedDict — always populated; never raises.
    """
    normalized_sku = sku.strip().upper()

    # ── Layer 1: SQLite ───────────────────────────────────────────────────────
    result = lookup_sku_sqlite(conn, normalized_sku)
    if result is not None:
        print(f"[littleton_sku_helper] SKU '{normalized_sku}' → cache HIT (sqlite)")
        return result

    # ── Layer 2: Firestore shared cache ───────────────────────────────────────
    result = lookup_sku_firestore(db, normalized_sku)
    if result is not None:
        print(f"[littleton_sku_helper] SKU '{normalized_sku}' → cache HIT (firestore)")
        return result

    # ── Layer 3: Gemini classification + Firestore write-back ─────────────────
    print(f"[littleton_sku_helper] SKU '{normalized_sku}' → MISS; invoking Gemini fallback.")
    result = resolve_via_gemini(genai_client, model, description)

    # Persist to Firestore so every future instance resolves instantly
    save_sku_to_firestore(db, normalized_sku, description, result)

    return result


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _sanitize_sku_for_doc_id(sku: str) -> str:
    """
    Firestore document IDs may not contain forward slashes or other
    reserved characters. Replace any non-alphanumeric chars with underscores.
    """
    sanitized = re.sub(r"[^a-zA-Z0-9\-]", "_", sku.strip().upper())
    return sanitized[:500]  # Firestore doc ID limit is 1500 bytes; 500 is safe
