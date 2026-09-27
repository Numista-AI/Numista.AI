"""
test_us_mint_catalog.py
=======================
Unit tests for Numista.AI US Mint product catalog resolution and truncation expansion (CoS S1).
Tests item 26XE, 26XH, West Point mint facility, 26.73g weight, privy mark variety,
and verifies no double-expansion of Enhanced Uncirculated.
"""

import pytest
from services.us_mint_catalog_service import (
    lookup_us_mint_item,
    expand_us_mint_truncation,
    enrich_us_mint_item,
    US_MINT_PRODUCT_CATALOG,
    US_MINT_TRUNCATION_MAP,
)


def test_26xe_catalog_facts():
    """Verify official US Mint specs for 26XE (Morgan Enhanced Uncirculated)."""
    item = lookup_us_mint_item("26XE")
    assert item is not None
    assert item["year"] == 2026
    assert item["denomination"] == "Dollar"
    assert item["mint_facility"] == "West Point (no mint mark)"
    assert item["mint_mark"] == ""
    assert item["weight_grams"] == 26.73  # 0.859 oz ASW, not 31.103 g
    assert item["variety"] == "Liberty Bell 250 Privy, 1776~2026 Dual Date"
    assert item["strike_type"] == "Enhanced Uncirculated"
    assert item["condition"] == "Enhanced Uncirculated"
    assert item["issue_price"] == "$169.00"
    assert item["mintage_limit"] == 250000


def test_26xh_catalog_facts():
    """Verify official US Mint specs for 26XH (Peace Enhanced Uncirculated twin)."""
    item = lookup_us_mint_item("26XH")
    assert item is not None
    assert item["year"] == 2026
    assert item["denomination"] == "Dollar"
    assert item["mint_facility"] == "West Point (no mint mark)"
    assert item["mint_mark"] == ""
    assert item["weight_grams"] == 26.73
    assert item["variety"] == "Liberty Bell 250 Privy, 1776~2026 Dual Date"
    assert item["strike_type"] == "Enhanced Uncirculated"


def test_truncation_expansion_and_no_double_expansion():
    """Verify 'Enhanced Un...' expands cleanly and does not double-expand."""
    raw = "2026 Morgan Silver Enhanced Un..."
    expanded = expand_us_mint_truncation(raw)
    assert "Enhanced Uncirculated" in expanded
    assert "..." in expanded

    # Expanding again must NOT produce 'Enhanced Uncirculatedcirculated'
    re_expanded = expand_us_mint_truncation(expanded)
    assert re_expanded == expanded
    assert "Enhanced Uncirculated" in re_expanded
    assert "Enhanced Uncirculatedcirculated" not in re_expanded


def test_enrich_us_mint_item_with_26xe():
    """Verify full end-to-end enrichment of an extracted invoice line item for 26XE."""
    extracted = {
        "Retailer Item No.": "26XE",
        "Original Description from source": "2026 Morgan Silver Enhanced Un...",
        "Cost": "$169.00",
        "Quantity": 2,
    }

    enriched = enrich_us_mint_item(extracted)

    assert enriched["Year"] == 2026
    assert enriched["Denomination"] == "Dollar"
    assert enriched["Strike Type"] == "Enhanced Uncirculated"
    assert enriched["Condition"] == "Enhanced Uncirculated"
    assert enriched["Variety"] == "Liberty Bell 250 Privy, 1776~2026 Dual Date"
    assert enriched["weight_grams"] == 26.73
    assert "0.859 oz ASW" in enriched["Metal Content"]
    assert enriched["_catalog_grounded"] is True


def test_26sqrp_catalog_facts():
    """Verify official US Mint specs for 26SQRP (2026 Semiquincentennial Presidential $1 25-coin roll)."""
    item = lookup_us_mint_item("26SQRP")
    assert item is not None
    assert item["year"] == 2026
    assert item["denomination"] == "Dollar"
    assert item["mint_facility"] == "Philadelphia (P)"
    assert item["mint_mark"] == ""
    assert item["issue_price"] == "$61.00"
    assert "Manganese-Brass" in item["metal_content"]
    assert item.get("catalog_url") == "https://catalog.usmint.gov/"


def test_26sqrd_does_not_exist():
    """Verify 26SQRD is removed from catalog because US Mint only offers 26SQRP roll and 26SQBP bag."""
    assert lookup_us_mint_item("26SQRD") is None


def test_enrich_us_mint_item_with_notes_fallback():
    """Verify 26SQRP in Personal Notes enriches and sets Retailer Item No."""
    extracted = {
        "Retailer Item No.": "N/A",
        "Original Description from source": "2026 Presidential $1 Coin",
        "Personal Notes": "26SQRP Semiquincentennial President",
        "Cost": "$61.00",
    }
    enriched = enrich_us_mint_item(extracted)
    assert enriched["Retailer Item No."] == "26SQRP"
    assert enriched["Year"] == 2026
    assert enriched["Denomination"] == "Dollar"
    assert enriched["Mint Mark"] == ""
    assert enriched["_catalog_grounded"] is True


