"""
set_pricing.py
==============
Authoritative resolution and pricing lookup for US Mint Proof and Mint Sets.
Follows the multi-SKU canonical schema contract: (year, product_type, metal, coin_count).
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

CATALOG_PATH = Path(__file__).parent / "data" / "us_mint_sets_catalog.json"

_CATALOG_CACHE: Optional[Dict[str, Any]] = None

def load_set_catalog() -> Dict[str, Any]:
    global _CATALOG_CACHE
    if _CATALOG_CACHE is None:
        if CATALOG_PATH.exists():
            with open(CATALOG_PATH, "r", encoding="utf-8") as f:
                _CATALOG_CACHE = json.load(f).get("sets", {})
        else:
            _CATALOG_CACHE = {}
    return _CATALOG_CACHE

def resolve_set_sku(doc: Dict[str, Any]) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """
    Parses coin document fields and maps them to a canonical Set SKU key.
    
    Returns:
        (sku_key, error_dict)
        If unvaluable/unparseable, sku_key is None and error_dict contains status & basis reason.
    """
    name = str(doc.get("name") or doc.get("title") or doc.get("Coin Name") or "").strip()
    program = str(doc.get("Program/Series") or doc.get("Program / Series") or doc.get("program_series") or "").strip()
    denom = str(doc.get("Denomination") or doc.get("denomination") or "").strip()
    item_type = str(doc.get("item_type") or "").strip().lower()
    is_set = doc.get("is_set") is True or item_type == "set" or denom.lower() == "set" or "set" in name.lower() or "set" in program.lower()

    if not is_set:
        return None, {"status": "skipped", "reason": "not_a_set"}

    # 1. Year resolution
    raw_year = doc.get("Year") or doc.get("year")
    year = None
    if raw_year:
        try:
            year = int(str(raw_year).strip()[:4])
        except (ValueError, TypeError):
            year = None
    if not year:
        for token in (name + " " + program).split():
            if token.isdigit() and len(token) == 4 and token.startswith(("19", "20")):
                year = int(token)
                break
    if not year:
        return None, {
            "status": "unvaluable",
            "ai_value_status": "unvaluable",
            "ai_estimated_value": "Unvaluable - Year unspecified",
            "basis": "set_year_unspecified"
        }

    # 2. Product type & coin count resolution
    combined_text = f"{name} {program}".lower()
    if "quarter" in combined_text and ("proof" in combined_text or "state" in combined_text):
        product_type = "quarter_proof_set"
        coin_count = 5
    elif "proof" in combined_text:
        product_type = "proof_set"
        coin_count = 10  # Standard proof set (1999-present is 10-coin with 5 quarters)
    elif "mint set" in combined_text or "uncirculated" in combined_text:
        product_type = "mint_set"
        coin_count = 20  # Standard uncirculated P&D mint set
    else:
        product_type = "proof_set"
        coin_count = 10

    # 3. Metal resolution
    metal_text = str(doc.get("Metal Content") or doc.get("metal") or doc.get("Metal") or "").lower()
    combined_all = f"{combined_text} {metal_text}".lower()
    
    if "silver" in combined_all:
        metal = "silver"
    elif any(k in combined_all for k in ["cupronickel", "clad", "copper-nickel", "base metal", "standard"]):
        metal = "clad"
    elif not metal_text:
        return None, {
            "status": "unvaluable",
            "ai_value_status": "unvaluable",
            "ai_estimated_value": "Unvaluable - Metal unspecified",
            "basis": "set_metal_unspecified"
        }
    else:
        return None, {
            "status": "unvaluable",
            "ai_value_status": "unvaluable",
            "ai_estimated_value": "Unvaluable - Unknown metal composition",
            "basis": "set_metal_unrecognized"
        }

    sku_key = f"{year}_{product_type}_{metal}_{coin_count}"
    return sku_key, None

def get_set_valuation(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates a Set document against the catalog and returns the full valuation payload.
    """
    sku_key, error = resolve_set_sku(doc)
    if error:
        return error
    
    catalog = load_set_catalog()
    set_data = catalog.get(sku_key)
    
    if not set_data:
        return {
            "status": "unvaluable",
            "ai_value_status": "unvaluable",
            "ai_estimated_value": "Unvaluable - Uncataloged Set",
            "basis": f"uncataloged_custom_set_{sku_key}"
        }
    
    return {
        "status": "valued",
        "ai_value_status": "valued",
        "sku": sku_key,
        "estimated_value": set_data["display_range"],
        "numeric_median": set_data["median"],
        "low": set_data["low"],
        "high": set_data["high"],
        "basis": set_data["basis"],
        "confidence": set_data.get("confidence", "HIGH"),
        "as_of": set_data.get("as_of", "")
    }
