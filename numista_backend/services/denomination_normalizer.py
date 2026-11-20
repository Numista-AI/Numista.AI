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

    # Clean suffixes like (25C), (50c), etc. and collapse spaces before ¢/₵ ('.25 ₵' -> '.25₵')
    d_clean = re.sub(r"\s*\(\s*\d+\s*[c¢₵\w\s]*\)", "", raw_clean, flags=re.IGNORECASE)
    d_clean = re.sub(r"\s+([¢₵])", r"\1", d_clean).strip()

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


_METAL_WORD_TYPOS: Dict[str, str] = {
    "silve": "Silver",
    "sliver": "Silver",
    "silvr": "Silver",
    "siver": "Silver",
    "silv": "Silver",
    "ag": "Silver",
    "gol": "Gold",
    "gld": "Gold",
    "godl": "Gold",
    "au": "Gold",
    "platnium": "Platinum",
    "platnum": "Platinum",
    "pt": "Platinum",
    "coper": "Copper",
    "coppr": "Copper",
    "cu": "Copper",
    "nickle": "Nickel",
    "cupronickle": "Cupro-Nickel Clad",
    "cupronickel": "Cupro-Nickel Clad",
}

_PROTECTED_BASE_METAL_PHRASES = (
    "nickel silver",
    "german silver",
    "cupro-nickel",
    "cupronickel",
    "silver plated",
    "silver-plated",
    "gold plated",
    "gold-plated",
    "platinum plated",
    "platinum-plated",
)

_SHELDON_GRADE_RE = re.compile(
    r"^(?:PF|PR|MS|AU|XF|EF|VF|F|VG|G|AG|FR|PO)\s*[- ]?\s*\d{1,2}\b",
    re.IGNORECASE,
)


def _is_us_country(country: Optional[str]) -> bool:
    if not country:
        return True
    return country.strip().lower() in {
        "",
        "us",
        "usa",
        "u.s.",
        "u.s.a.",
        "united states",
        "united states of america",
        "united states mint",
    }


def _parse_year_int(raw_year: Optional[Any]) -> Optional[int]:
    if raw_year is None:
        return None
    s = str(raw_year).strip()
    m = re.search(r"\b(1[7-9]\d{2}|20\d{2})\b", s)
    if m:
        return int(m.group(1))
    s_no_dec = re.sub(r"\.0+$", "", s)
    return int(s_no_dec) if s_no_dec.isdigit() else None


def normalize_metal_content(
    raw_metal: Optional[str],
    year: Optional[Any] = None,
    canonical_denom: Optional[str] = None,
    country: Optional[str] = None,
    item_type: Optional[str] = None,
) -> str:
    """Fixes metal typos (`Silve` -> `Silver`) and enriches historical US silver compositions."""
    if item_type and "paper" in str(item_type).lower():
        return str(raw_metal or "").strip()

    trimmed = str(raw_metal or "").strip()
    lower = trimmed.lower()
    for phrase in _PROTECTED_BASE_METAL_PHRASES:
        if phrase in lower:
            return trimmed

    cleaned = trimmed
    if lower == "clad":
        cleaned = "Cupro-Nickel Clad"
    elif lower in _METAL_WORD_TYPOS:
        cleaned = _METAL_WORD_TYPOS[lower]
    elif cleaned:
        cleaned = re.sub(
            r"\b[A-Za-z]+\b",
            lambda m: _METAL_WORD_TYPOS.get(m.group(0).lower(), m.group(0)),
            cleaned,
        )
        if cleaned.lower() in ("silver", "gold", "platinum", "copper", "nickel"):
            cleaned = cleaned.capitalize()

    yr = _parse_year_int(year)
    is_us = _is_us_country(country)
    c_low = cleaned.lower()
    is_bare_or_empty_silver = c_low in ("", "pending", "unknown", "silver")

    if is_us and yr is not None and canonical_denom:
        if yr <= 1964 and canonical_denom in ("Dime", "Quarter Dollar", "Half Dollar") and is_bare_or_empty_silver:
            return "90% Silver, 10% Copper"
        if 1965 <= yr <= 1970 and canonical_denom == "Half Dollar" and c_low == "silver":
            return "40% Silver, 60% Copper"
        if 1942 <= yr <= 1945 and canonical_denom == "Five Cents" and c_low == "silver":
            return "35% Silver, 56% Copper, 9% Manganese"

    return cleaned


def normalize_condition(raw_condition: Optional[str]) -> str:
    """Translates raw condition slang (`shiny` -> `Uncirculated`) while keeping Sheldon grades intact."""
    trimmed = str(raw_condition or "").strip()
    if not trimmed:
        return ""
    if _SHELDON_GRADE_RE.match(trimmed) or "details" in trimmed.lower():
        return trimmed
    low = trimmed.lower()
    if low in ("shiny", "bright", "mint", "bu", "brilliant uncirculated"):
        return "Uncirculated"
    if low in ("worn", "heavily circulated"):
        return "Circulated"
    return trimmed


def infer_classic_us_series(
    year: Optional[Any],
    canonical_denom: Optional[str],
    existing_series: Optional[str],
    country: Optional[str] = None,
) -> str:
    trimmed = str(existing_series or "").strip()
    if not _is_us_country(country):
        return trimmed
    if trimmed.lower() not in ("", "general item", "standard circulation", "none", "n/a", "unknown", "other"):
        return trimmed
    yr = _parse_year_int(year)
    if yr is None or not canonical_denom:
        return trimmed
    if canonical_denom == "Quarter Dollar":
        if 1932 <= yr <= 1998:
            return "Washington Quarters"
        if 1916 <= yr <= 1930:
            return "Standing Liberty Quarters"
    elif canonical_denom == "Dime":
        if yr >= 1946:
            return "Roosevelt Dimes"
        if 1916 <= yr <= 1945:
            return "Mercury Dimes"
    elif canonical_denom == "Half Dollar":
        if yr >= 1964:
            return "Kennedy Half Dollars"
        if 1948 <= yr <= 1963:
            return "Franklin Half Dollars"
        if 1916 <= yr <= 1947:
            return "Walking Liberty Half Dollars"
    elif canonical_denom == "Five Cents":
        if yr >= 1938:
            return "Jefferson Nickels"
        if 1913 <= yr <= 1938:
            return "Buffalo Nickels"
    elif canonical_denom == "Cent":
        if yr >= 2010:
            return "Lincoln Shield Cents"
        if 1959 <= yr <= 2008:
            return "Lincoln Memorial Cents"
        if 1909 <= yr <= 1958:
            return "Lincoln Wheat Cents"
    elif canonical_denom == "Dollar":
        if 1921 <= yr <= 1935:
            return "Peace Dollars"
        if 1878 <= yr <= 1921:
            return "Morgan Dollars"
    return trimmed


def normalize_coin_fields(coin_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Applies canonical US Mint denomination, metal, series, and condition normalization."""
    out = dict(coin_dict)
    country = out.get("Country") or out.get("country")
    item_type = out.get("item_type") or out.get("Item Type")
    if out.get("is_foreign") is True:
        country = country or "Foreign"
    raw_denom = out.get("Denomination") if "Denomination" in out else out.get("denomination")
    year = out.get("Year") if "Year" in out else out.get("year")
    canon_denom, was_corr, orig_denom = normalize_denomination(
        str(raw_denom or ""),
        country=str(country or "") if country is not None else None,
        item_type=str(item_type or "") if item_type is not None else None,
    )
    if canon_denom:
        if "Denomination" in out or "denomination" not in out:
            out["Denomination"] = canon_denom
        if "denomination" in out:
            out["denomination"] = canon_denom
        if was_corr:
            out["denom_corrected"] = True
            out["original_denomination"] = orig_denom

    raw_metal = out.get("Metal Content") if "Metal Content" in out else out.get("metal_content")
    norm_metal = normalize_metal_content(
        str(raw_metal or ""),
        year=year,
        canonical_denom=canon_denom,
        country=str(country or "") if country is not None else None,
        item_type=str(item_type or "") if item_type is not None else None,
    )
    if norm_metal:
        if "Metal Content" in out or "metal_content" not in out:
            out["Metal Content"] = norm_metal
        if "metal_content" in out:
            out["metal_content"] = norm_metal

    raw_series = out.get("Program/Series") if "Program/Series" in out else out.get("program_series")
    norm_series = infer_classic_us_series(
        year=year,
        canonical_denom=canon_denom,
        existing_series=str(raw_series or ""),
        country=str(country or "") if country is not None else None,
    )
    if norm_series:
        if "Program/Series" in out or "program_series" not in out:
            out["Program/Series"] = norm_series
        if "program_series" in out:
            out["program_series"] = norm_series

    raw_cond = out.get("Condition") if "Condition" in out else out.get("condition")
    norm_cond = normalize_condition(str(raw_cond or ""))
    if norm_cond:
        if "Condition" in out or "condition" not in out:
            out["Condition"] = norm_cond
        if "condition" in out:
            out["condition"] = norm_cond

    return out


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


CANONICAL_US_CIRCULATING: List[str] = ["Cent", "Five Cents", "Dime", "Quarter Dollar", "Half Dollar", "Dollar"]


def is_valid_us_denomination(denom: Optional[str]) -> bool:
    """Checks whether a denomination string is in the canonical active US circulating list."""
    if not denom:
        return False
    return denom.strip() in CANONICAL_US_CIRCULATING


def get_canonical_us_denominations() -> List[str]:
    """Returns the ordered list of primary active US circulating denominations."""
    return list(CANONICAL_US_CIRCULATING)
