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
    calculate_mint_pricing,
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


def test_calculate_mint_pricing_contract():
    """Verify deterministic integer cents and unit cost calculations (Lock L1 and G2)."""
    # 26GC Innovation $64.97 / 2 -> $32.49 (3249 cents, ROUND_HALF_UP from 32.485)
    p1 = calculate_mint_pricing(64.97, 2)
    assert p1["line_total"] == 64.97
    assert p1["quantity"] == 2
    assert p1["unit_cost_cents"] == 3249
    assert p1["unit_cost"] == 32.49

    # 26SQRP $61.00 / 25 -> $2.44 (244 cents)
    p2 = calculate_mint_pricing("$61.00", 25)
    assert p2["line_total"] == 61.00
    assert p2["quantity"] == 25
    assert p2["unit_cost_cents"] == 244
    assert p2["unit_cost"] == 2.44

    # 26XE Morgan $169.00 / 2 -> $84.50 (8450 cents)
    p3 = calculate_mint_pricing("169.00", "2")
    assert p3["line_total"] == 169.00
    assert p3["quantity"] == 2
    assert p3["unit_cost_cents"] == 8450
    assert p3["unit_cost"] == 84.50


def test_11_sku_catalog_thumbnails():
    """Verify all 11 required catalog SKUs have valid GCS reference library thumbnails."""
    skus = ["26SQRP", "26XL", "26XM", "26EA", "26XE", "26XH", "26XF", "26RG", "26RJ", "26GC", "2026-AI-IA"]
    for sku in skus:
        item = lookup_us_mint_item(sku)
        assert item is not None, f"Missing catalog entry for SKU {sku}"
        thumb = item.get("thumbnail_url")
        assert thumb is not None and thumb.startswith("https://storage.googleapis.com/numista-reference-library/"), f"Invalid thumbnail for {sku}: {thumb}"
