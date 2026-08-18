"""
test_set_pricing.py
===================
Unit tests for US Mint Set SKU resolution and catalog valuation.
Tests the real 2002 (S) Proof Set fixture, silver variants, quarter sets, and unvaluable edge cases.
"""

import pytest
from numista_backend.set_pricing import resolve_set_sku, get_set_valuation

def test_2002_clad_proof_set_fixture():
    # Real live 2002 Proof Set document fixture
    doc = {
        "Year": "2002",
        "Denomination": "Set",
        "Mint Mark": "S",
        "Metal Content": "Cupronickel",
        "Program/Series": "United States Mint Proof Set",
        "name": "2002 United States Mint Proof Set"
    }
    sku, err = resolve_set_sku(doc)
    assert err is None
    assert sku == "2002_proof_set_clad_10"
    
    val = get_set_valuation(doc)
    assert val["status"] == "valued"
    assert val["ai_value_status"] == "valued"
    assert val["numeric_median"] == 11.50
    assert val["low"] == 9.00
    assert val["high"] == 14.00
    assert val["estimated_value"] == "$9.00 - $14.00"

def test_2002_silver_proof_set_fixture():
    doc = {
        "Year": "2002",
        "Denomination": "Set",
        "Mint Mark": "S",
        "Metal Content": "Silver",
        "Program/Series": "United States Mint Silver Proof Set",
        "name": "2002 United States Mint Silver Proof Set"
    }
    sku, err = resolve_set_sku(doc)
    assert err is None
    assert sku == "2002_proof_set_silver_10"
    
    val = get_set_valuation(doc)
    assert val["status"] == "valued"
    assert val["numeric_median"] == 75.00
    assert val["low"] == 65.00
    assert val["high"] == 85.00

def test_2002_quarter_proof_set_fixture():
    doc = {
        "Year": "2002",
        "Denomination": "Set",
        "Mint Mark": "S",
        "Metal Content": "Clad",
        "Program/Series": "50 State Quarters Proof Set",
        "name": "2002 50 State Quarters Proof Set"
    }
    sku, err = resolve_set_sku(doc)
    assert err is None
    assert sku == "2002_quarter_proof_set_clad_5"
    
    val = get_set_valuation(doc)
    assert val["status"] == "valued"
    assert val["numeric_median"] == 6.00

def test_missing_metal_returns_unvaluable():
    doc = {
        "Year": "2002",
        "Denomination": "Set",
        "Program/Series": "United States Mint Proof Set",
        "name": "2002 United States Mint Proof Set"
        # Metal Content intentionally omitted
    }
    sku, err = resolve_set_sku(doc)
    assert sku is None
    assert err["status"] == "unvaluable"
    assert err["basis"] == "set_metal_unspecified"
    
    val = get_set_valuation(doc)
    assert val["status"] == "unvaluable"
    assert val["ai_value_status"] == "unvaluable"

def test_uncataloged_custom_set():
    doc = {
        "Year": "1940",
        "Denomination": "Set",
        "Metal Content": "Silver",
        "Program/Series": "Custom Dealer Lucite Proof Set",
        "name": "1940 Custom Proof Set"
    }
    sku, err = resolve_set_sku(doc)
    assert err is None
    assert sku == "1940_proof_set_silver_10"
    
    val = get_set_valuation(doc)
    assert val["status"] == "unvaluable"
    assert "uncataloged_custom_set" in val["basis"]
