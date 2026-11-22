"""
test_us_mint_catalog_overrides.py
==================================
Regression tests for Phase C US Mint catalog hardening:
- RC-3 deterministic mint override on single-mint SKUs (26SQRP)
- RC-2 deterministic strike & variety override on standard Proof SKUs (26EA)
- Exclusion of multi-mint SKUs (26RJ) and uncataloged coins
- Canonical merged 26GC Reverse Proof Set entry
- Source-level AST duplicate-key guard on US_MINT_PRODUCT_CATALOG
"""

import ast
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.us_mint_catalog_service import (  # noqa: E402
    SINGLE_MINT_DEFINITIVE_SKUS,
    enrich_us_mint_item,
    lookup_us_mint_item,
)


def test_26sqrp_mint_override_replaces_bogus_d(caplog):
    """RC-3: 26SQRP must override LLM-misread 'D' / 'Denver' back to unmarked Philadelphia."""
    assert "26SQRP" in SINGLE_MINT_DEFINITIVE_SKUS
    raw_item = {
        "item_type": "coin",
        "Retailer Item No.": "26SQRP",
        "Mint Mark": "D",
        "mint_mark": "D",
        "mint": "Denver",
        "Quantity": 25,
        "Cost": 61.00,
    }
    with caplog.at_level(logging.WARNING, logger="numista_backend.us_mint_catalog_service"):
        enriched = enrich_us_mint_item(raw_item)

    assert enriched["Mint Mark"] == ""
    assert enriched["mint_mark"] == ""
    assert enriched["mint"] == "Philadelphia"
    assert "CATALOG_OVERRIDE_MINT" in caplog.text


def test_26ea_strike_variety_override_strips_reverse_proof(caplog):
    """RC-2: 26EA standard Proof must override conflicting Strike Type and strip 'Reverse' from Variety."""
    assert "26EA" in SINGLE_MINT_DEFINITIVE_SKUS

    # Case A: empty Strike Type + corrupted Variety ('250 Privy / W-Reverse PROOF')
    raw_item_a = {
        "item_type": "coin",
        "Retailer Item No.": "26EA",
        "Mint Mark": "W",
        "Strike Type": "",
        "Variety": "250 Privy / W-Reverse PROOF",
        "Cost": "$173.00",
    }
    with caplog.at_level(logging.WARNING, logger="numista_backend.us_mint_catalog_service"):
        enriched_a = enrich_us_mint_item(raw_item_a)

    assert enriched_a["Strike Type"] == "Proof"
    assert "reverse" not in enriched_a["Variety"].lower()
    assert enriched_a["Variety"] == "250 Privy / W-Proof"
    assert "CATALOG_OVERRIDE_VARIETY" in caplog.text

    # Case B: conflicting Strike Type ('Reverse Proof') also overridden & logged
    caplog.clear()
    raw_item_b = {
        "item_type": "coin",
        "Retailer Item No.": "26EA",
        "Mint Mark": "W",
        "Strike Type": "Reverse Proof",
        "Variety": "250 Privy / W-Reverse PROOF",
        "Cost": "$173.00",
    }
    with caplog.at_level(logging.WARNING, logger="numista_backend.us_mint_catalog_service"):
        enriched_b = enrich_us_mint_item(raw_item_b)

    assert enriched_b["Strike Type"] == "Proof"
    assert "reverse" not in enriched_b["Variety"].lower()
    assert "CATALOG_OVERRIDE_STRIKE" in caplog.text
    assert "CATALOG_OVERRIDE_VARIETY" in caplog.text


def test_multimint_26rj_not_overridden():
    """Multi-mint sets (26RJ) and non-catalog coins must NOT have mint marks overwritten."""
    assert "26RJ" not in SINGLE_MINT_DEFINITIVE_SKUS

    item_26rj = {
        "item_type": "set",
        "Retailer Item No.": "26RJ",
        "Mint Mark": "P & D",
        "Quantity": 1,
        "Cost": 124.50,
    }
    enriched_26rj = enrich_us_mint_item(item_26rj)
    assert enriched_26rj["Mint Mark"] == "P & D"

    custom_coin = {
        "item_type": "coin",
        "Retailer Item No.": "CUSTOM-999",
        "Mint Mark": "S",
        "Strike Type": "Proof",
        "Quantity": 1,
    }
    enriched_custom = enrich_us_mint_item(custom_coin)
    assert enriched_custom["Mint Mark"] == "S"
    assert enriched_custom["Strike Type"] == "Proof"


def test_26gc_canonical_merged_fields():
    """Merged 26GC catalog entry retains S-mint, Set metadata, no pack multiplier, and 26gc_b.webp."""
    entry = lookup_us_mint_item("26GC")
    assert entry is not None
    assert entry["title"] == "2026 American Innovation $1 Coin Reverse Proof Set"
    assert entry["formal_name"] == "American Innovation $1 Coin 2026 Reverse Proof Set"
    assert entry["is_set"] is True
    assert entry["item_type"] == "set"
    assert entry["denomination"] == "Set"
    assert "pack_quantity" not in entry
    assert entry["mint_mark"] == "S"
    assert entry["mint_facility"] == "San Francisco (S)"
    assert entry["strike_type"] == "Reverse Proof"
    assert entry["image_url_obverse"].endswith("26gc_b.webp")


def test_no_duplicate_keys_in_us_mint_catalog():
    """AST source-level check: fails loudly if US_MINT_PRODUCT_CATALOG defines any key twice."""
    src_path = Path(__file__).resolve().parents[1] / "services" / "us_mint_catalog_service.py"
    tree = ast.parse(src_path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(getattr(t, "id", "") == "US_MINT_PRODUCT_CATALOG" for t in targets):
                assert isinstance(node.value, ast.Dict)
                keys = [ast.literal_eval(k) for k in node.value.keys if k is not None]
                duplicates = [k for idx, k in enumerate(keys) if k in keys[:idx]]
                assert not duplicates, f"Duplicate keys in US_MINT_PRODUCT_CATALOG: {duplicates}"
                return
    raise AssertionError("US_MINT_PRODUCT_CATALOG not found")
