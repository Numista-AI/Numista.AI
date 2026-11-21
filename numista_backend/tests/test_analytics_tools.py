"""
tests/test_analytics_tools.py
-----------------------------
Unit tests for Phase 1 deterministic Analytics tools and edge cases.
"""

import pytest
from services.analytics_tools import (
    build_vault_snapshot,
    find_duplicates,
    parse_ai_value,
    query_vault_aggregate,
    simulate_spot_prices,
)


def _sample_raw_docs():
    return [
        (
            "c1",
            {
                "country": "USA",
                "year": "1921",
                "mintMark": "P",
                "denomination": "Dollar",
                "programSeries": "Morgan Dollar",
                "metalContent": "90% Silver",
                "quantity": "2",
                "greysheetBid": 38.0,
                "cpgRetail": 52.0,
                "meltValue": 24.0,
                "purchaseCost": 30.0,
                "gradingService": "",
            },
        ),
        (
            "c2",
            {
                "country": "USA",
                "year": "1921",
                "mintMark": "P",
                "denomination": "25C",
                "programSeries": "Standing Liberty",
                "metalContent": "90% Silver",
                "quantity": "1",
                "aiEstimatedValue": "$0.00",  # zero-sentinel must be rejected
                "meltValue": 5.5,
                "purchaseCost": 0.0,
            },
        ),
        (
            "c3",
            {
                "country": "USA",
                "year": "1921",
                "mintMark": "P",
                "denomination": "Quarter Dollar",
                "programSeries": "Standing Liberty",
                "metalContent": "90% Silver",
                "quantity": "1",
                "aiEstimatedValue": "$45.00",
                "meltValue": 5.5,
                "purchaseCost": 20.0,
            },
        ),
        (
            "c_plated",
            {
                "country": "USA",
                "year": "2020",
                "mintMark": "P",
                "denomination": "Dollar",
                "metalContent": "Silver Plated",
                "quantity": "1",
                "aiEstimatedValue": "$10.00",
                "meltValue": 0.0,
            },
        ),
        (
            "set_1",
            {
                "isSet": True,
                "programSeries": "Proof Set",
                "quantity": "1",
                "cpgRetail": 100.0,
            },
        ),
        (
            "child_1",
            {
                "parentSetId": "set_1",
                "year": "2023",
                "denomination": "Half Dollar",
                "metalContent": "90% Silver",
                "quantity": "1",
                "cpgRetail": 60.0,
                "meltValue": 11.0,
            },
        ),
        (
            "sup_1",
            {
                "item_type": "supply",
                "denomination": "Coin Tube",
                "cpgRetail": 15.0,
            },
        ),
    ]


def test_zero_sentinel_rejected_in_parse_ai_value():
    assert parse_ai_value("$0.00") == 0.0
    assert parse_ai_value("0") == 0.0
    assert parse_ai_value("Pending") == 0.0
    assert parse_ai_value("$45.00 - $60.00") == 45.0


def test_supplies_excluded_and_set_double_count_prevented():
    snap = build_vault_snapshot(_sample_raw_docs(), advanced_mode=True)
    ids = {c["id"] for c in snap}
    assert "sup_1" not in ids
    assert "set_1" not in ids  # parent skipped because child_1 exists
    assert "child_1" in ids


def test_plated_metal_guard_prevents_melt_floor():
    snap = build_vault_snapshot(_sample_raw_docs(), advanced_mode=True)
    plated = next(c for c in snap if c["id"] == "c_plated")
    assert plated["fine_ag_oz"] == 0.0
    sim = simulate_spot_prices([plated], gold=3000.0, silver=100.0)
    assert sim["simulated_total"] == 10.0


def test_quantity_multiplier_and_net_liquidation_floor():
    snap = build_vault_snapshot(_sample_raw_docs(), advanced_mode=False)
    c1 = next(c for c in snap if c["id"] == "c1")
    # 2 * 38.0 = 76.0
    assert c1["total_value"] == 76.0
    assert c1["total_net_liq"] == 76.0


def test_canonical_duplicate_grouping_merges_25c_and_quarter_dollar():
    snap = build_vault_snapshot(_sample_raw_docs(), advanced_mode=True)
    dups = find_duplicates(snap, include_sets=False)
    keys = {g["key"] for g in dups["duplicate_groups"]}
    # c2 ("25C") and c3 ("Quarter Dollar") merge into 1921 P quarter dollar
    assert "USA|1921|P|quarter dollar|" in keys
    # c1 has qty=2 -> also a duplicate group
    assert "USA|1921|P|dollar|" in keys


def test_query_vault_aggregate_coverage_excludes_zero_sentinel_and_zero_cost():
    snap = build_vault_snapshot(_sample_raw_docs(), advanced_mode=True)
    agg = query_vault_aggregate(snap)
    # c1(qty 2) + c2(1) + c3(1) + c_plated(1) + child_1(1) = 6 units
    assert agg["coverage"]["total"] == 6
    # c2 has "$0.00" so unpriced -> 5 priced
    assert agg["coverage"]["priced"] == 5
    # c1(2) + c3(1) = 3 with cost > 0
    assert agg["coverage"]["with_cost"] == 3
