"""Unit tests for `mint_helpers.py` encoding all 15 Canonical Fixtures (F01-F15)."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from numista_backend.services.mint_helpers import (
    format_mint_facility_and_mark,
    format_mint_mark_for_display,
    read_mint_facility,
    read_mint_mark,
    resolve_two_field_mint,
)


def test_canonical_fixtures_f01_through_f14():
    cases = [
        # (id, kwargs, expected_mint, expected_mm, expected_rule, compact, detail)
        ("F01", dict(year="1921", raw_mint_mark="", series="Morgan Dollars", denomination="Dollar"),
         "Philadelphia", "", 10, "NMM", "No Mint Mark"),
        ("F02", dict(year="1921", raw_mint_mark="D", series="Morgan Dollars", denomination="Dollar"),
         "Denver", "D", 3, "D", "D"),
        ("F03", dict(year="1943", raw_mint_mark="P", series="Jefferson Nickels", denomination="5 Cents", metal_content="35% Silver"),
         "Philadelphia", "P", 1, "P", "P"),
        ("F04", dict(year="1943", raw_mint_mark="", series="Jefferson Nickels", denomination="5 Cents", variety="War Nickel", metal_content="35% Silver"),
         "", "", 11, "", ""),
        ("F05", dict(year="1942", raw_mint_mark="", series="Jefferson Nickels", denomination="5 Cents", variety="Type 1", metal_content="Copper-Nickel"),
         "Philadelphia", "", 10, "NMM", "No Mint Mark"),
        ("F06", dict(year="1974", raw_mint_mark="", series="Lincoln Cents", denomination="Cent"),
         "Philadelphia", "", 10, "NMM", "No Mint Mark"),
        ("F07", dict(year="1958", raw_mint_mark="", series="Franklin Half Dollars", denomination="Half Dollar", strike_type="Proof"),
         "Philadelphia", "", 10, "NMM", "No Mint Mark"),
        ("F08", dict(year="1980", raw_mint_mark="P", series="Washington Quarters", denomination="Quarter"),
         "Philadelphia", "P", 1, "P", "P"),
        ("F09", dict(year="1849", raw_mint_mark="D", series="Liberty Head Gold", denomination="$5 Half Eagle"),
         "Dahlonega", "D", 2, "D", "D"),
        ("F10", dict(year="1849", raw_mint_mark="C", series="Liberty Head Gold", denomination="$5 Half Eagle"),
         "Charlotte", "C", 4, "C", "C"),
        ("F11", dict(year="2026", raw_mint_mark="", series="Morgan Dollars", denomination="Dollar", strike_type="Enhanced Uncirculated", variety="Enhanced Uncirculated", retailer_item_no="26XE"),
         "West Point", "", 9, "", ""),
        ("F12", dict(year="2026", raw_mint_mark="", series="Morgan Dollars", denomination="Dollar", strike_type="Reverse Proof", variety="Reverse Proof", retailer_item_no="26XF"),
         "Philadelphia", "", 10, "NMM", "No Mint Mark"),
        ("F13", dict(year="1964", raw_mint_mark="None", series="Roosevelt Dimes", denomination="Dime"),
         "Philadelphia", "", 10, "NMM", "No Mint Mark"),
        ("F14", dict(year="2015", raw_mint_mark="", series="Canadian Maple Leaf", denomination="$5 CAD", country="Canada"),
         "", "", 11, "", ""),
    ]

    for fid, kwargs, exp_mint, exp_mm, exp_rule, exp_compact, exp_detail in cases:
        mint, mm, rule = resolve_two_field_mint(**kwargs)
        assert (mint, mm, rule) == (exp_mint, exp_mm, exp_rule), f"{fid} failed: got {(mint, mm, rule)}"
        assert format_mint_mark_for_display(mint, mm, compact=True) == exp_compact, f"{fid} compact display failed"
        assert format_mint_mark_for_display(mint, mm, compact=False) == exp_detail, f"{fid} detail display failed"


def test_canonical_fixture_f15_legacy_fallback():
    unmigrated = {
        "Year": "1921",
        "Mint Mark": "D",
        "Denomination": "Dollar",
        "Program/Series": "Morgan Dollars",
    }
    assert read_mint_facility(unmigrated) == ""
    assert read_mint_mark(unmigrated) == "D"


def test_dual_key_priority_prefers_snake_case():
    doc = {"mint": "West Point", "mint_mark": "", "Mint Mark": "P"}
    assert read_mint_facility(doc) == "West Point"
    assert read_mint_mark(doc) == ""
    assert format_mint_facility_and_mark("Philadelphia", "") == "Philadelphia (NMM)"
    assert format_mint_facility_and_mark("Denver", "D") == "Denver (D)"
