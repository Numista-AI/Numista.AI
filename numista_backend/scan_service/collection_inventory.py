"""
collection_inventory.py — Shared set-expansion and counting helpers

Moved from main.py (Dimes Bug v2.2). Used by:
  - numista_backend/main.py (deep_dive, /api/collection/count)
  - scan_service/estate_report_generator.py (estate PDF)

MUST NOT import main.py or estate_report_generator.py.
"""

from __future__ import annotations

import json
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MAX_INVENTORY_ITEMS = 2000

_INHERIT_BLOCKLIST_YEAR  = {"", "multiple", "various", "n/a"}
_INHERIT_BLOCKLIST_DENOM = {"", "set", "multiple", "various", "n/a"}

_DIME_SYNONYMS = {"dime", "10c", "10-cent", "10 cent", "roosevelt dime"}


# ---------------------------------------------------------------------------
# Field helpers
# ---------------------------------------------------------------------------

def _get_field(d: dict, *keys, default=""):
    """Read first non-empty value from multiple key variants (PascalCase / snake_case)."""
    for k in keys:
        v = d.get(k)
        if v is not None and str(v).strip():
            return str(v).strip()
    return default


def is_dime(denom: str) -> bool:
    """Returns True if the denomination string represents a dime."""
    return denom.strip().lower() in _DIME_SYNONYMS


# ---------------------------------------------------------------------------
# Set-Expansion
# ---------------------------------------------------------------------------

def expand_collection_inventory(docs_iter):
    """Expand Firestore coin documents into a flat inventory list.

    Set documents (item_type == "set" OR set_contents is a non-empty list)
    are projected as one set-parent row plus one row per child in set_contents.

    Returns:
        (inventory_items, stats_dict)

    inventory_items: list of dicts with canonical snake_case keys:
        coin_id, year, denomination, mint_mark, condition, theme_subject,
        program_series, ai_estimated_value, cost, item_type, from_set,
        from_set_name, is_set_parent, fields_incomplete

    stats_dict: { "docs": int, "sets": int, "expanded": int, "total_items": int }

    Synthetic coin_id values contain "__set_coin_" and MUST be rejected
    by any write tool (add/update/undo).  They are prompt-only.
    """
    inventory: list[dict[str, Any]] = []
    doc_count = 0
    set_count = 0
    expanded_count = 0

    for doc in docs_iter:
        d = doc.to_dict()
        doc_count += 1

        item_type_raw = _get_field(d, "item_type", default="coin").lower()

        # Detect set: explicit item_type OR presence of set_contents
        raw_contents = d.get("set_contents")
        if isinstance(raw_contents, str):
            try:
                raw_contents = json.loads(raw_contents)
            except (json.JSONDecodeError, TypeError):
                raw_contents = None

        is_set = (item_type_raw == "set") or (isinstance(raw_contents, list) and len(raw_contents) > 0)

        if is_set:
            set_count += 1
            set_contents = raw_contents if isinstance(raw_contents, list) else []

            set_name = _get_field(d, "Theme/Subject", "theme_subject",
                                  "Original Description from source", default="Unknown Set")

            # Parent set row
            inventory.append({
                "coin_id":            doc.id,
                "year":               _get_field(d, "Year", "year"),
                "denomination":       _get_field(d, "Denomination", "denomination"),
                "mint_mark":          _get_field(d, "Mint Mark", "mint_mark"),
                "condition":          _get_field(d, "Condition", "condition"),
                "theme_subject":      _get_field(d, "Theme/Subject", "theme_subject"),
                "program_series":     _get_field(d, "Program/Series", "program_series"),
                "ai_estimated_value": _get_field(d, "AI Estimated Value", "ai_estimated_value", default="$0.00"),
                "cost":               _get_field(d, "Cost", "cost", "purchase_cost", default="$0.00"),
                "item_type":          "set",
                "from_set":           None,
                "from_set_name":      None,
                "is_set_parent":      True,
                "fields_incomplete":  False,
            })

            parent_year = _get_field(d, "Year", "year")
            parent_cond = _get_field(d, "Condition", "condition")

            for idx, coin in enumerate(set_contents):
                if not isinstance(coin, dict):
                    continue

                child_year  = _get_field(coin, "Year", "year")
                child_denom = _get_field(coin, "Denomination", "denomination")

                # Inherit parent year ONLY if child is blank AND parent is not blocked
                if not child_year and parent_year.lower() not in _INHERIT_BLOCKLIST_YEAR:
                    child_year = parent_year

                # Never inherit blocked denominations
                if child_denom.lower() in _INHERIT_BLOCKLIST_DENOM:
                    child_denom = ""

                incomplete = (not child_year) or (not child_denom)

                # Child item_type from the child itself (default "coin").
                # Paper/medal/supply children stay those types.
                child_item_type = _get_field(coin, "item_type", default="coin").lower()
                if child_item_type in ("set", "multiple", "n/a", ""):
                    child_item_type = "coin"

                inventory.append({
                    "coin_id":            f"{doc.id}__set_coin_{idx}",
                    "year":               child_year,
                    "denomination":       child_denom,
                    "mint_mark":          _get_field(coin, "Mint Mark", "mint_mark"),
                    "condition":          _get_field(coin, "Condition", "condition") or parent_cond,
                    "theme_subject":      _get_field(coin, "Theme/Subject", "theme_subject"),
                    "program_series":     _get_field(coin, "Program/Series", "program_series"),
                    # ── Option B (dual-key — matches Dart contract) ───────
                    "strike_type":        _get_field(coin, "Strike Type", "strike_type"),
                    "Strike Type":        _get_field(coin, "Strike Type", "strike_type"),
                    "metal_content":      _get_field(coin, "Metal Content", "metal_content",
                                                     "Composition", "composition"),
                    "Metal Content":      _get_field(coin, "Metal Content", "metal_content",
                                                     "Composition", "composition"),
                    # ── End Option B ─────────────────────────────────────
                    "ai_estimated_value": _get_field(coin, "AI Estimated Value", "ai_estimated_value", default="$0.00"),
                    "cost":               _get_field(coin, "Cost", "cost", "purchase_cost", default="$0.00"),
                    "item_type":          child_item_type,
                    "from_set":           doc.id,
                    "from_set_name":      set_name,
                    "is_set_parent":      False,
                    "fields_incomplete":  incomplete,
                })
                expanded_count += 1
        else:
            # Regular coin / paper_currency / medal / other
            inventory.append({
                "coin_id":            doc.id,
                "year":               _get_field(d, "Year", "year"),
                "denomination":       _get_field(d, "Denomination", "denomination"),
                "mint_mark":          _get_field(d, "Mint Mark", "mint_mark"),
                "condition":          _get_field(d, "Condition", "condition"),
                "theme_subject":      _get_field(d, "Theme/Subject", "theme_subject"),
                "program_series":     _get_field(d, "Program/Series", "program_series"),
                "ai_estimated_value": _get_field(d, "AI Estimated Value", "ai_estimated_value", default="$0.00"),
                "cost":               _get_field(d, "Cost", "cost", "purchase_cost", default="$0.00"),
                "item_type":          item_type_raw if item_type_raw else "coin",
                "from_set":           None,
                "from_set_name":      None,
                "is_set_parent":      False,
                "fields_incomplete":  False,
            })

    stats = {
        "docs": doc_count,
        "sets": set_count,
        "expanded": expanded_count,
        "total_items": len(inventory),
    }

    return inventory, stats


# ---------------------------------------------------------------------------
# Counting Rules — single source of truth
# ---------------------------------------------------------------------------

def is_set_parent(row: dict) -> bool:
    """True if this row is a set parent (after expansion).

    Reads the is_set_parent flag first (stamped by expand_collection_inventory).
    Falls back to item_type == "set" for rows not produced by the expander.
    None-safe.
    """
    flag = row.get("is_set_parent")
    if flag is not None:
        return bool(flag)
    return (row.get("item_type") or "").lower() == "set"


def is_physical_coin(row: dict) -> bool:
    """True if this row represents a countable physical coin.

    Rules:
    - item_type in {"coin", ""} AND NOT a set parent.
    - Paper/medal/supply/exonumia children are NOT coins.
    - Set parents (item_type="set" or is_set_parent=True) are NOT coins.
    """
    it = (row.get("item_type") or "coin").lower().strip()
    if it not in ("coin", ""):
        return False
    return not is_set_parent(row)


def count_coins_and_lots(inventory: list[dict]) -> dict:
    """Single counting function. Called by all projectors.

    Returns:
        {
            "total_coins": int,  # physical coins (loose + set children)
            "total_lots": int,   # parent docs only (loose = 1 lot, set = 1 lot)
            "set_count": int,    # how many sets
        }
    """
    total_coins = sum(1 for r in inventory if is_physical_coin(r))
    total_lots = sum(1 for r in inventory if r.get("from_set") is None)
    set_count_val = sum(1 for r in inventory if is_set_parent(r))
    return {
        "total_coins": total_coins,
        "total_lots": total_lots,
        "set_count": set_count_val,
    }


# ---------------------------------------------------------------------------
# Lot Value — deterministic value attribution while a set is kept
# ---------------------------------------------------------------------------

def lot_value(parent_val: float, children_vals: list[float]) -> float:
    """Deterministic value for a kept set lot.

    WHILE KEPT:
        lot FMV = parent FMV if parent FMV > 0
                  ELSE sum of child FMVs
                  NEVER parent + children

    Same ladder for CPG, melt, purchase, AI value.
    """
    if parent_val > 0:
        return parent_val
    child_sum = sum(v for v in children_vals if v > 0)
    return child_sum
