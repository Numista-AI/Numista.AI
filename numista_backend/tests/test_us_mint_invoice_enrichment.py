"""
test_us_mint_invoice_enrichment.py
==================================
Unit and regression tests for US Mint item code catalog lookup,
description truncation expansion, and line-item metadata enrichment.
"""

import pytest
from services.us_mint_catalog_service import (
    lookup_us_mint_item,
    expand_us_mint_truncation,
    enrich_us_mint_item,
    normalize_item_code,
)


def test_normalize_item_code():
    assert normalize_item_code("26XL") == "26XL"
    assert normalize_item_code("26-XL") == "26XL"
    assert normalize_item_code(" 26ea ") == "26EA"
    assert normalize_item_code("26_xm.") == "26XM"
    assert normalize_item_code("") == ""


def test_lookup_26xl_peace_dollar_reverse_proof():
    item = lookup_us_mint_item("26XL")
    assert item is not None
    assert item["year"] == 2026
    assert item["mint_facility"] == "Philadelphia (P)"
    assert item["mint_mark"] == ""
    assert item["strike_type"] == "Reverse Proof"
    assert item["denomination"] == "Peace Dollar"
    assert item["program_series"] == "Morgan and Peace Silver Dollars"
    assert item["metal_content"] == "99.9% Silver"
    assert item["purity"] == 0.999
    assert item["issue_price"] == "$173.00"


def test_lookup_26ea_silver_eagle():
    item = lookup_us_mint_item("26EA")
    assert item is not None
    assert item["year"] == 2026
    assert item["denomination"] == "American Silver Eagle"
    assert item["program_series"] == "American Silver Eagle"
    assert item["metal_content"] == "99.9% Silver"


def test_expand_us_mint_truncation():
    raw = "Peace Silver Dollar 2026 Rever"
    expanded = expand_us_mint_truncation(raw)
    assert "Reverse Proof" in expanded

    raw_unc = "2026 Morgan Dollar Uncirc"
    assert expand_us_mint_truncation(raw_unc) == "2026 Morgan Dollar Uncirculated"


def test_enrich_us_mint_item_26xl_invoice_line():
    raw_item = {
        "item_type": "coin",
        "Year": "2026",
        "Denomination": "Dollar",
        "Program/Series": "USA Invoice Import",
        "Theme/Subject": "Peace Silver Dollar 2026 Rever",
        "Retailer Item No.": "26XL",
        "Cost": "$173.00",
        "Retailer/Website": "United States Mint",
        "Original Description from source": "Peace Silver Dollar 2026 Rever",
    }

    enriched = enrich_us_mint_item(raw_item)
    assert enriched["_catalog_grounded"] is True
    assert enriched["Denomination"] == "Peace Dollar"
    assert enriched["Program/Series"] == "Morgan and Peace Silver Dollars"
    assert enriched["Strike Type"] == "Reverse Proof"
    assert enriched["Condition"] == "Reverse Proof"
    assert enriched["Metal Content"] == "99.9% Silver"
    assert "Philadelphia (P)" in enriched["Personal Notes"]


def test_enrich_us_mint_item_with_code_in_description():
    raw_item = {
        "item_type": "coin",
        "Theme/Subject": "26XL Peace Dollar",
        "Original Description from source": "26XL Peace Silver Dollar 2026 Rever",
        "Cost": "$173.00",
    }

    enriched = enrich_us_mint_item(raw_item)
    assert enriched["_catalog_grounded"] is True
    assert enriched["Retailer Item No."] == "26XL"
    assert enriched["Strike Type"] == "Reverse Proof"
    assert enriched["Denomination"] == "Peace Dollar"
