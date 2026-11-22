"""
Founder Issues (20 Nov 2026) — Backend Normalization Matrix & Schema Alias Tests.
Covers Section 9.2 official US Mint Terms normalization, metal/series/condition
inference, header aliases, and hard-negative guards (foreign coins, banknotes,
plated/nickel silver).
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.common import normalize_colloquial_header
from services.denomination_normalizer import (
    normalize_denomination,
    normalize_metal_content,
    normalize_condition,
    infer_classic_us_series,
    normalize_coin_fields,
)


@pytest.mark.parametrize(
    "raw_denom,expected",
    [
        # Cent
        ("penny", "Cent"),
        ("1¢", "Cent"),
        ("1₵", "Cent"),
        ("1 ₵", "Cent"),
        ("1¢", "Cent"),
        ("$0.01", "Cent"),
        (".01", "Cent"),
        (".01¢", "Cent"),
        ("Wheat Penny", "Cent"),
        ("wheatie", "Cent"),
        # Five Cents
        ("nickel", "Five Cents"),
        ("nickles", "Five Cents"),
        ("5c", "Five Cents"),
        ("5¢", "Five Cents"),
        ("5₵", "Five Cents"),
        ("$0.05", "Five Cents"),
        (".05", "Five Cents"),
        # Dime
        ("10c", "Dime"),
        ("10¢", "Dime"),
        ("10₵", "Dime"),
        ("$0.10", "Dime"),
        ("ten cents", "Dime"),
        ("Mercury Dime", "Dime"),
        # Quarter Dollar
        ("quarter", "Quarter Dollar"),
        ("25C", "Quarter Dollar"),
        ("25c", "Quarter Dollar"),
        ("25¢", "Quarter Dollar"),
        ("25₵", "Quarter Dollar"),
        (".25¢", "Quarter Dollar"),
        (".25 ₵", "Quarter Dollar"),
        ("0.25 ₵", "Quarter Dollar"),
        ("$0.25", "Quarter Dollar"),
        ("two bits", "Quarter Dollar"),
        # Half Dollar
        ("half", "Half Dollar"),
        ("50c", "Half Dollar"),
        ("50¢", "Half Dollar"),
        ("50₵", "Half Dollar"),
        (".50 ₵", "Half Dollar"),
        ("$0.50", "Half Dollar"),
        ("Fifty cent piece", "Half Dollar"),
        ("50 cent piece", "Half Dollar"),
        ("JFK 50 cent piece", "Half Dollar"),
        ("Kennedy Half", "Half Dollar"),
        # Dollar
        ("dollar coin", "Dollar"),
        ("$1 coin", "Dollar"),
        ("$1", "Dollar"),
        ("buck", "Dollar"),
        ("silver dollar", "Dollar"),
        ("Morgan Dollar", "Dollar"),
        # Historical US
        ("Double Eagle", "Double Eagle"),
        ("Half Eagle", "Half Eagle"),
        ("Quarter Eagle", "Quarter Eagle"),
        ("trime", "Three Cents"),
        ("twenty cents", "Twenty Cents"),
    ],
)
def test_us_mint_terms_denomination_matrix(raw_denom, expected):
    canon, _, _ = normalize_denomination(raw_denom, country="United States", item_type="coin")
    assert canon == expected


@pytest.mark.parametrize(
    "raw_denom,country,item_type",
    [
        ("$1", "United States", "paper_currency"),
        ("$5", "United States", "paper_currency"),
        ("$20", "United States", "coin"),
        ("25c", "Canada", "coin"),
        ("1 Penny", "United Kingdom", "coin"),
        ("10 Cents", "Australia", "coin"),
        ("1 Peso", "Mexico", "coin"),
    ],
)
def test_denomination_hard_negative_guards(raw_denom, country, item_type):
    canon, corrected, _ = normalize_denomination(raw_denom, country=country, item_type=item_type)
    assert canon == raw_denom
    assert corrected is False


def test_founder_quarter_typo_and_silver_enrichment():
    """Exact SS 6a/6b regression: 1958 Quarter with 'Silve', '25C', 'Standard Circulation', 'shiny'."""
    coin = {
        "Year": "1958",
        "Denomination": "25C",
        "Metal Content": "Silve",
        "Program/Series": "Standard Circulation",
        "Condition": "shiny",
        "Country": "United States",
    }
    normalized = normalize_coin_fields(coin)
    assert normalized["Denomination"] == "Quarter Dollar"
    assert normalized["denom_corrected"] is True
    assert normalized["original_denomination"] == "25C"
    assert normalized["Metal Content"] == "90% Silver, 10% Copper"
    assert normalized["Program/Series"] == "Washington Quarters"
    assert normalized["Condition"] == "Uncirculated"


def test_metal_hard_negatives_and_historical_ranges():
    # Hard negatives: base-metal / plated phrases stay untouched
    assert normalize_metal_content("Nickel Silver", year=1958, canonical_denom="Quarter Dollar") == "Nickel Silver"
    assert normalize_metal_content("German Silver", year=1950, canonical_denom="Half Dollar") == "German Silver"
    assert normalize_metal_content("Silver Plated", year=1960, canonical_denom="Dime") == "Silver Plated"
    assert normalize_metal_content("Cupro-Nickel Clad", year=1968, canonical_denom="Quarter Dollar") == "Cupro-Nickel Clad"

    # Historical silver compositions
    assert normalize_metal_content("Silver", year=1968, canonical_denom="Half Dollar") == "40% Silver, 60% Copper"
    assert normalize_metal_content("silver", year=1944, canonical_denom="Five Cents") == "35% Silver, 56% Copper, 9% Manganese"
    assert normalize_metal_content("sliver", year=1985, canonical_denom="Quarter Dollar") == "Silver"
    assert normalize_metal_content("platnium", year=2020, canonical_denom="Dollar") == "Platinum"

    # Non-US or paper currency should not auto-rewrite to US 90% silver
    assert normalize_metal_content("Silver", year=1958, canonical_denom="Quarter Dollar", country="Canada") == "Silver"
    assert normalize_metal_content("Silver", year=1958, canonical_denom="Dollar", item_type="paper_currency") == "Silver"


def test_condition_normalization_preserves_sheldon_grades():
    assert normalize_condition("shiny") == "Uncirculated"
    assert normalize_condition("BU") == "Uncirculated"
    assert normalize_condition("worn") == "Circulated"
    assert normalize_condition("MS-65") == "MS-65"
    assert normalize_condition("PF 69") == "PF 69"
    assert normalize_condition("AU58 Details") == "AU58 Details"


def test_classic_us_series_inference():
    assert infer_classic_us_series(1958, "Quarter Dollar", "Standard Circulation") == "Washington Quarters"
    assert infer_classic_us_series(1925, "Quarter Dollar", "") == "Standing Liberty Quarters"
    assert infer_classic_us_series(1942, "Dime", "General Item") == "Mercury Dimes"
    assert infer_classic_us_series(1964, "Half Dollar", "") == "Kennedy Half Dollars"
    assert infer_classic_us_series(1954, "Half Dollar", "") == "Franklin Half Dollars"
    assert infer_classic_us_series(1921, "Dollar", "") == "Peace Dollars"
    assert infer_classic_us_series(1889, "Dollar", "") == "Morgan Dollars"
    # Existing curated series is preserved
    assert infer_classic_us_series(1958, "Quarter Dollar", "Custom Varieties") == "Custom Varieties"
    # Foreign country is not overwritten
    assert infer_classic_us_series(1958, "Quarter Dollar", "Standard Circulation", country="Canada") == "Standard Circulation"


@pytest.mark.parametrize(
    "raw_header,expected",
    [
        ("date", "Year"),
        ("Date", "Year"),
        ("mintage_year", "Year"),
        ("Mint Year", "Year"),
        ("Coin Date", "Year"),
        ("front", "Obverse"),
        ("Front", "Obverse"),
        ("heads", "Obverse"),
        ("Heads", "Obverse"),
        ("back", "Reverse"),
        ("Back", "Reverse"),
        ("tail", "Reverse"),
        ("tails", "Reverse"),
        ("TAILS", "Reverse"),
    ],
)
def test_colloquial_header_aliases(raw_header, expected):
    assert normalize_colloquial_header(raw_header) == expected
