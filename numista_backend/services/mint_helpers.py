"""
Centralized two-field mint helpers (`mint` facility + `mint_mark` on-coin mark).

Implements the canonical normalization rules and dual-key readers defined in
PLAN_TWO_FIELD_MINT_MODEL_v3.0.md (§2.3, §3.2).
"""

from __future__ import annotations

import re
from typing import Any

_DIRTY_PLACEHOLDERS = frozenset({"none", "(none)", "null", "n/a", "nan"})
_PHILLY_TEXT_ALIASES = frozenset({"nmm", "no mint mark", "philadelphia"})
_FACILITY_NAMES = {
    "denver": "Denver",
    "san francisco": "San Francisco",
    "west point": "West Point",
    "new orleans": "New Orleans",
    "carson city": "Carson City",
    "charlotte": "Charlotte",
    "dahlonega": "Dahlonega",
}
_US_COUNTRIES = frozenset({"usa", "us", "united states", ""})
_YEAR_RE = re.compile(r"^(\d{4})")


def _clean_str(val: Any) -> str:
    if val is None:
        return ""
    return str(val).strip()


def _parse_int_year(year: Any) -> int | None:
    s = _clean_str(year)
    if not s:
        return None
    m = _YEAR_RE.match(s)
    if not m:
        return None
    try:
        return int(m.group(1))
    except ValueError:
        return None


def read_mint_mark(doc: dict[str, Any] | None) -> str:
    """
    Dual-key reader for on-coin mint mark.
    Priority: `mint_mark` -> `Mint Mark` -> `mintMark` -> `MintMark`.
    Sanitizes dirty placeholder strings ("none", "(none)", "null", "n/a",
    "nmm", "no mint mark", "philadelphia") to "".
    """
    if not doc:
        return ""
    if "mint_mark" in doc and doc["mint_mark"] is not None:
        raw = str(doc["mint_mark"]).strip()
    else:
        raw = ""
        for key in ("Mint Mark", "mintMark", "MintMark"):
            val = doc.get(key)
            if val is not None and str(val).strip() != "":
                raw = str(val).strip()
                break
    if not raw:
        return ""
    lower = raw.lower()
    if lower in _DIRTY_PLACEHOLDERS or lower in _PHILLY_TEXT_ALIASES:
        return ""
    return raw.upper()


def read_mint_facility(doc: dict[str, Any] | None) -> str:
    """
    Dual-key reader for mint facility.
    Priority: `mint` -> `mint_facility` -> `Mint` -> `Mint Facility`.
    Returns "" if absent or placeholder.
    """
    if not doc:
        return ""
    for key in ("mint", "mint_facility", "Mint", "Mint Facility"):
        val = doc.get(key)
        if val is not None:
            s = str(val).strip()
            if s and s.lower() not in _DIRTY_PLACEHOLDERS:
                return s
    return ""


def is_west_point_nmm(
    year: str = "",
    series: str = "",
    denomination: str = "",
    variety: str = "",
    strike_type: str = "",
    retailer_item_no: str = "",
    country: str = "United States",
) -> bool:
    """Exact programmatic implementation of Table §2.3 Rule 9."""
    is_us = _clean_str(country).lower() in _US_COUNTRIES
    if not is_us:
        return False

    item_no_upper = _clean_str(retailer_item_no).upper()
    if item_no_upper in {"26XE", "26XH"}:
        return True

    year_str = _clean_str(year)
    series_or_denom_lower = f"{_clean_str(series).lower()} {_clean_str(denomination).lower()}"
    strike_lower = _clean_str(strike_type).lower()
    variety_lower = _clean_str(variety).lower()

    return (
        year_str == "2026"
        and ("morgan" in series_or_denom_lower or "peace" in series_or_denom_lower)
        and (
            "enhanced" in strike_lower
            or "enhanced" in variety_lower
            or strike_lower == "eu"
            or variety_lower == "eu"
        )
    )


def resolve_two_field_mint(
    raw_mint_mark: str = "",
    raw_mint: str = "",
    year: str = "",
    series: str = "",
    denomination: str = "",
    country: str = "United States",
    variety: str = "",
    strike_type: str = "",
    metal_content: str = "",
    retailer_item_no: str = "",
    catalog_philly_nmm: bool = False,
) -> tuple[str, str, int]:
    """
    Returns (mint_facility, mint_mark, rule_id) per Table §2.3 (rule_id in 1..11).
    Never invents an on-coin mint mark when none is present.
    """
    country_clean = _clean_str(country)
    is_us = country_clean.lower() in _US_COUNTRIES
    int_year = _parse_int_year(year)

    raw_mm_clean = _clean_str(raw_mint_mark)
    raw_mm_lower = raw_mm_clean.lower()
    raw_mint_clean = _clean_str(raw_mint)
    if raw_mint_clean.lower() in _DIRTY_PLACEHOLDERS:
        raw_mint_clean = ""

    if raw_mm_lower in _DIRTY_PLACEHOLDERS:
        mm = ""
    elif raw_mm_lower in _FACILITY_NAMES:
        # Facility name typed into the mark field (e.g. "Denver"): it is a facility,
        # not an on-coin mark.
        mm = ""
        if not raw_mint_clean:
            raw_mint_clean = _FACILITY_NAMES[raw_mm_lower]
    elif raw_mm_lower in _PHILLY_TEXT_ALIASES:
        mm = ""
        if is_us and not raw_mint_clean:
            raw_mint_clean = "Philadelphia"
    else:
        mm = raw_mm_clean.upper()

    if is_us:
        if mm == "P":
            return ("Philadelphia", "P", 1)
        if mm == "D" and int_year is not None and 1838 <= int_year <= 1861:
            return ("Dahlonega", "D", 2)
        if mm == "D" and (int_year is None or int_year >= 1906):
            return ("Denver", "D", 3)
        if mm == "C" and int_year is not None and 1838 <= int_year <= 1861:
            return ("Charlotte", "C", 4)
        if mm == "S":
            return ("San Francisco", "S", 5)
        if mm == "W":
            return ("West Point", "W", 6)
        if mm == "O":
            return ("New Orleans", "O", 7)
        if mm == "CC":
            return ("Carson City", "CC", 8)

    if mm == "":
        # Rule 9: West Point NMM
        if is_west_point_nmm(
            year=year,
            series=series,
            denomination=denomination,
            variety=variety,
            strike_type=strike_type,
            retailer_item_no=retailer_item_no,
            country=country,
        ):
            return ("West Point", "", 9)

        # Rule 10: Philadelphia NMM
        if is_us:
            series_or_denom_lower = f"{_clean_str(series).lower()} {_clean_str(denomination).lower()}"
            strike_lower = _clean_str(strike_type).lower()
            variety_lower = _clean_str(variety).lower()
            metal_lower = _clean_str(metal_content).lower()
            item_no_upper = _clean_str(retailer_item_no).upper()

            is_war_nickel_ambiguous = (
                int_year is not None
                and 1942 <= int_year <= 1945
                and any(k in series_or_denom_lower for k in ("nickel", "jefferson", "5c", "5 cent"))
                and ("war" in variety_lower or "silver" in metal_lower or int_year >= 1943)
            )
            pre_1980_philly_nmm = (
                int_year is not None and int_year <= 1979 and not is_war_nickel_ambiguous
            )
            strike_or_variety_philly_nmm = (
                any(tok in strike_lower or tok in variety_lower for tok in ("reverse proof", "congratulations"))
                or (
                    strike_lower in {"proof", "pr", "pf"}
                    and (int_year is None or int_year <= 1964 or item_no_upper in {"26XF", "26XL", "26RF"})
                )
            )
            explicit_philly_facility = raw_mint_clean.lower() == "philadelphia"

            if (
                catalog_philly_nmm
                or explicit_philly_facility
                or pre_1980_philly_nmm
                or strike_or_variety_philly_nmm
            ):
                return ("Philadelphia", "", 10)

    # Rule 11: Non-US coin or US coin with insufficient/ambiguous metadata.
    # F1 fix: preserve any facility already on the document (never blank it).
    return (raw_mint_clean, mm, 11)


def build_mint_write_fields(
    raw_mint_mark: str = "",
    raw_mint: str = "",
    **ctx: Any,
) -> dict[str, str]:
    """Transitional dual-write payload for new coin documents (F2).

    Returns ``{"mint", "mint_mark", "Mint Mark"}``. The legacy ``"Mint Mark"`` key
    is kept until Phase 7 prune; remove it from this helper at that point.
    """
    facility, mark, _ = resolve_two_field_mint(
        raw_mint_mark=raw_mint_mark, raw_mint=raw_mint, **ctx
    )
    return {"mint": facility, "mint_mark": mark, "Mint Mark": mark}


def apply_imported_mint_fields(doc: dict[str, Any]) -> dict[str, Any]:
    """Normalize a spreadsheet/CSV import row in place (F2 import mapping).

    A raw ``"Mint"`` column may hold a facility name ("Denver", "Royal Canadian
    Mint") or a mark letter ("D"); route by value so a facility never lands in
    ``Mint Mark``. Writes ``mint`` + ``mint_mark`` and the transitional legacy
    ``Mint Mark`` (remove at Phase 7). Idempotent.
    """
    raw_mint = _clean_str(doc.pop("Mint", ""))
    mark = read_mint_mark(doc)
    facility = read_mint_facility(doc)
    if raw_mint:
        if len(raw_mint) <= 2 and not mark:
            mark = raw_mint.upper()
        elif not facility:
            facility = raw_mint
    new_mint, new_mark, _ = resolve_two_field_mint(
        raw_mint_mark=mark,
        raw_mint=facility,
        year=_clean_str(doc.get("Year") or doc.get("year")),
        series=_clean_str(doc.get("Program/Series") or doc.get("program_series")),
        denomination=_clean_str(doc.get("Denomination") or doc.get("denomination")),
        country=_clean_str(doc.get("Country") or doc.get("country")) or "United States",
        variety=_clean_str(doc.get("Variety") or doc.get("variety")),
        strike_type=_clean_str(doc.get("Strike Type") or doc.get("strike_type")),
        metal_content=_clean_str(doc.get("Metal Content") or doc.get("metal_content")),
        retailer_item_no=_clean_str(doc.get("Retailer Item No.")),
    )
    doc["mint"] = new_mint
    doc["mint_mark"] = new_mark
    doc["Mint Mark"] = new_mark
    return doc

def format_mint_mark_for_display(mint: str, mint_mark: str, compact: bool = False) -> str:
    """
    Display formatter:
    - If mint_mark is non-empty, return mint_mark.
    - If mint_mark is empty and mint == 'Philadelphia':
      - compact=True -> 'NMM'
      - compact=False -> 'No Mint Mark'
    - Otherwise return ''.
    """
    mm = _clean_str(mint_mark).upper()
    if mm:
        return mm
    if _clean_str(mint).lower() == "philadelphia":
        return "NMM" if compact else "No Mint Mark"
    return ""


def format_mint_facility_and_mark(mint: str, mint_mark: str) -> str:
    """Human-readable combined display, e.g. 'Philadelphia (NMM)' or 'Denver (D)'."""
    facility = _clean_str(mint)
    mm = _clean_str(mint_mark).upper()
    if facility and mm:
        return f"{facility} ({mm})"
    if facility.lower() == "philadelphia" and not mm:
        return "Philadelphia (NMM)"
    if facility:
        return facility
    return mm
