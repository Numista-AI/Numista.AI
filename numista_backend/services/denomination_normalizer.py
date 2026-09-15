"""
Numista.AI Denomination Normalizer Service (GI-NOM-01)
Ensures formal US Mint denomination nomenclature in the vault.
Translates colloquial terms (e.g. Penny -> Cent, Quarter -> Quarter Dollar, Nickel -> Five Cents).
Provides banknote guards and foreign coin passthrough.
"""

import os
import re
import json
import logging
from typing import Tuple, Optional, List, Dict, Any

logger = logging.getLogger("denomination_normalizer")

_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "us_denomination_canon.json")

# Fallback dictionaries in case JSON file is missing or corrupted
_FALLBACK_CIRCULATING: Dict[str, List[str]] = {
    "Cent": ["penny", "pennies", "one cent", "1 cent", "1c", "1¢", "lincoln cent", "wheatie", "cent"],
    "Five Cents": ["nickel", "nickels", "nickles", "5 cents", "5c", "5¢", "five cent", "five cents", "jefferson nickel", "buffalo nickel"],
    "Dime": ["10c", "10¢", "ten cents", "10 cents", "roosevelt dime", "mercury dime", "dime"],
    "Quarter Dollar": ["quarter", "quarters", "25c", "25¢", "25 cents", "washington quarter", "state quarter", "quarter dollar"],
    "Half Dollar": ["half", "halves", "50c", "50¢", "50 cents", "jfk half", "kennedy half", "walking liberty half", "franklin half", "half dollar"],
    "Dollar": ["dollar coin", "$1", "buck", "1 dollar", "silver dollar", "morgan dollar", "peace dollar", "eisenhower dollar", "sacagawea dollar", "presidential dollar", "native american dollar", "american innovation dollar", "dollar"]
}

_CANON_DATA: Optional[Dict[str, Any]] = None
_LOOKUP_MAP: Dict[str, str] = {}
_PROGRAM_INFERENCE_MAP: Dict[str, str] = {}


def _load_canon() -> None:
    global _CANON_DATA, _LOOKUP_MAP, _PROGRAM_INFERENCE_MAP
    if _CANON_DATA is not None:
        return

    data = None
    if os.path.exists(_CONFIG_PATH):
        try:
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load {_CONFIG_PATH}: {e}. Using fallback map.")

    lookup: Dict[str, str] = {}
    program_map: Dict[str, str] = {}

    if data:
        _CANON_DATA = data
        for cat in ["us_circulating", "us_historical"]:
            for formal, details in data.get(cat, {}).items():
                lookup[formal.lower()] = formal
                for alias in details.get("colloquial", []):
                    lookup[alias.lower()] = formal

        program_map = {k.lower(): v for k, v in data.get("program_inference", {}).items()}
    else:
        for formal, aliases in _FALLBACK_CIRCULATING.items():
            lookup[formal.lower()] = formal
            for alias in aliases:
                lookup[alias.lower()] = formal

    _LOOKUP_MAP = lookup
    _PROGRAM_INFERENCE_MAP = program_map


def normalize_denomination(
    raw_denom: Optional[str],
    country: Optional[str] = None,
    item_type: Optional[str] = None
) -> Tuple[str, bool, str]:
    """
    Normalizes a raw denomination string to the official US Mint canonical denomination.
    
    Returns:
        Tuple of (canonical_denomination, was_corrected, original_denomination)
    
    Guards:
        1. Banknotes: If item_type == 'paper_currency' or matches banknote pattern (e.g. $1, $5),
           returns raw denomination unchanged (fails open).
        2. Foreign: If country is explicitly non-US, returns raw denomination unchanged.
    """
    _load_canon()

    raw_clean = str(raw_denom or "").strip()
    if not raw_clean:
        return ("", False, "")

    # Guard 1: Paper currency / Banknote check
    if item_type and "paper" in item_type.lower():
        return (raw_clean, False, raw_clean)
    # Currency values above $1 ($2, $5, $10, $20, $50, $100) are banknotes
    if re.match(r"^\$[2-9]\d*(\.\d+)?$", raw_clean) or re.match(r"^\$1\d+(\.\d+)?$", raw_clean):
        return (raw_clean, False, raw_clean)

    # Guard 2: Explicit Foreign country check
    if country:
        c_low = country.strip().lower()
        is_us = c_low in ["united states", "us", "usa", "u.s.", "united states of america", ""]
        if not is_us:
            return (raw_clean, False, raw_clean)

    # Clean suffixes like (25C), (50c), etc.
    d_clean = re.sub(r"\s*\(\s*\d+\s*[c¢\w\s]*\)", "", raw_clean, flags=re.IGNORECASE).strip()

    # Clean doubled words (e.g. "Quarter Dollar Dollar" -> "Quarter Dollar")
    d_lower = d_clean.lower()
    if "quarter dollar dollar" in d_lower:
        d_clean = re.sub(r"(?i)quarter dollar dollar", "Quarter Dollar", d_clean).strip()
        d_lower = d_clean.lower()
    elif "dollar dollar" in d_lower:
        d_clean = re.sub(r"(?i)dollar dollar", "Dollar", d_clean).strip()
        d_lower = d_clean.lower()
    elif "cent cent" in d_lower:
        d_clean = re.sub(r"(?i)cent cent", "Cent", d_clean).strip()
        d_lower = d_clean.lower()

    # Look up in canonical dictionary
    if d_lower in _LOOKUP_MAP:
        canonical = _LOOKUP_MAP[d_lower]
        was_corrected = (canonical != raw_clean)
        return (canonical, was_corrected, raw_clean)

    # Fails open for uncataloged or world denominations
    return (raw_clean, False, raw_clean)


def infer_denomination_from_program(program_str: Optional[str]) -> Optional[str]:
    """
    Infers the coin denomination from a known US Mint Program/Series string.
    Used ONLY when the row's denomination is empty or marked 'Denomination Missing?'.
    """
    _load_canon()
    if not program_str:
        return None

    p_clean = str(program_str).strip().lower()
    for prog_key, canonical_denom in _PROGRAM_INFERENCE_MAP.items():
        if prog_key in p_clean:
            return canonical_denom

    return None


def get_canonical_us_denominations() -> List[str]:
    """Returns the ordered list of primary active US circulating denominations."""
    return ["Cent", "Five Cents", "Dime", "Quarter Dollar", "Half Dollar", "Dollar"]
