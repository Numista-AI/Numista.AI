"""
Common Domain Helpers and Data Normalizers
"""

import re
from typing import Dict, Any

# Golden Schema Column Normalization Mapping
GOLDEN_SCHEMA_MAPPING: Dict[str, str] = {
    "Price Paid": "Cost",
    "Purchase Cost": "Cost",
    "Cost/Price": "Cost",
    "My Notes": "Personal Notes",
    "Notes": "Personal Notes",
    "Personal Notes I": "Personal Notes",
    "Grading Cert #": "Certification Number",
    "Certification #": "Certification Number",
    "Personal Ref #": "Personal Reference #",
    "Ref #": "Personal Reference #",
    # Official US Mint Terms slang headers
    "Date": "Year",
    "date": "Year",
    "mintage_year": "Year",
    "Mint Year": "Year",
    "mint_year": "Year",
    "Coin Date": "Year",
    "coin_date": "Year",
    "front": "Obverse",
    "Front": "Obverse",
    "heads": "Obverse",
    "Heads": "Obverse",
    "back": "Reverse",
    "Back": "Reverse",
    "tail": "Reverse",
    "Tail": "Reverse",
    "tails": "Reverse",
    "Tails": "Reverse",
}

_GOLDEN_SCHEMA_LOWER: Dict[str, str] = {
    k.strip().lower(): v for k, v in GOLDEN_SCHEMA_MAPPING.items()
}

def normalize_colloquial_header(header_name: str) -> str:
    """Maps informal collector spreadsheet headers into canonical Golden Schema column names."""
    cleaned = header_name.strip()
    if cleaned in GOLDEN_SCHEMA_MAPPING:
        return GOLDEN_SCHEMA_MAPPING[cleaned]
    return _GOLDEN_SCHEMA_LOWER.get(cleaned.lower(), cleaned)

def safe_get_str(row: Dict[str, Any], key: str, default: str = "") -> str:
    """Safely extracts string values from data dictionaries preventing KeyError exceptions."""
    val = row.get(key)
    if val is None:
        return default
    return str(val).strip()

_SLANG_CACHE = None

def _load_slang_dictionary():
    global _SLANG_CACHE
    if _SLANG_CACHE is None:
        import json, pathlib
        dict_path = pathlib.Path(__file__).resolve().parent.parent / "data" / "slang_dictionary.json"
        if dict_path.exists():
            with open(dict_path, "r", encoding="utf-8") as f:
                _SLANG_CACHE = json.load(f)
        else:
            _SLANG_CACHE = {}
    return _SLANG_CACHE

def normalize_slang_term(term: str, field_type: str = "auto") -> Dict[str, Any]:
    """
    Normalizes a colloquial term (e.g. 'wheatie', 'walker', 'slick', 'DMPL') into canonical series/grade/mint mark data.
    Case-insensitive and whitespace-tolerant.
    """
    if not term or not isinstance(term, str):
        return {}

    cleaned = term.strip().lower()
    slang_db = _load_slang_dictionary()

    result = {}
    
    # Check denomination/series slang
    denom_map = slang_db.get("denomination_slang", {})
    if cleaned in denom_map:
        result.update(denom_map[cleaned])

    # Check grade slang
    grade_map = slang_db.get("grade_slang", {})
    if cleaned in grade_map:
        result["mapped_grade"] = grade_map[cleaned]

    # Check mint mark slang
    mint_map = slang_db.get("mint_mark_slang", {})
    if cleaned in mint_map:
        result["mapped_mint_mark"] = mint_map[cleaned]

    return result

