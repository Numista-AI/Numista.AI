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
}

def normalize_colloquial_header(header_name: str) -> str:
    """Maps informal collector spreadsheet headers into canonical Golden Schema column names."""
    cleaned = header_name.strip()
    return GOLDEN_SCHEMA_MAPPING.get(cleaned, cleaned)

def safe_get_str(row: Dict[str, Any], key: str, default: str = "") -> str:
    """Safely extracts string values from data dictionaries preventing KeyError exceptions."""
    val = row.get(key)
    if val is None:
        return default
    return str(val).strip()
