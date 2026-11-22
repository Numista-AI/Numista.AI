"""
tests/test_morgan_analytics_golden.py
-------------------------------------
12 Golden-Prompt deterministic verification tests for Morgan Analytics.
"""

from services.analytics_tools import (
    build_vault_snapshot,
    find_duplicates,
    query_vault_aggregate,
    simulate_spot_prices,
)


def _golden_vault():
    raw = [
        ("m1", {"country": "USA", "year": "1881", "mintMark": "S", "denomination": "Dollar", "programSeries": "Morgan Dollar", "metalContent": "90% Silver", "quantity": "2", "cpgRetail": 80.0, "greysheetBid": 65.0, "meltValue": 24.0, "purchaseCost": 50.0, "gradingService": "PCGS", "storageLocation": "Home Safe", "retailer": "APMEX"}),
        ("m2", {"country": "USA", "year": "1921", "mintMark": "P", "denomination": "Dollar", "programSeries": "Morgan Dollar", "metalContent": "90% Silver", "quantity": "1", "cpgRetail": 40.0, "greysheetBid": 32.0, "meltValue": 24.0, "purchaseCost": 28.0, "gradingService": "", "storageLocation": "Bank SDB", "retailer": "JM Bullion"}),
        ("g1", {"country": "USA", "year": "2024", "mintMark": "W", "denomination": "$50", "programSeries": "American Gold Eagle", "metalContent": "1 oz Gold", "quantity": "1", "cpgRetail": 2800.0, "greysheetBid": 2680.0, "meltValue": 2650.0, "purchaseCost": 2400.0, "gradingService": "NGC", "storageLocation": "Bank SDB", "retailer": "APMEX"}),
        ("q1", {"country": "USA", "year": "1932", "mintMark": "P", "denomination": "25C", "programSeries": "Washington Quarter", "metalContent": "90% Silver", "quantity": "1", "cpgRetail": 25.0, "meltValue": 5.5, "purchaseCost": 0.0, "gradingService": "", "storageLocation": "Home Safe", "retailer": "Local"}),
        ("q2", {"country": "USA", "year": "1932", "mintMark": "P", "denomination": "Quarter Dollar", "programSeries": "Washington Quarter", "metalContent": "90% Silver", "quantity": "1", "cpgRetail": 35.0, "meltValue": 5.5, "purchaseCost": 15.0, "gradingService": "", "storageLocation": "Home Safe", "retailer": "Local"}),
    ]
    return build_vault_snapshot(raw, advanced_mode=True)


def test_golden_01_total_vault_value():
    snap = _golden_vault()
    res = query_vault_aggregate(snap)
    assert res["groups"][0]["total_value"] == 3060.0


def test_golden_02_total_cost_basis_excludes_zero_cost():
    snap = _golden_vault()
    res = query_vault_aggregate(snap)
    assert res["groups"][0]["cost_basis"] == 2543.0
    assert res["coverage"]["with_cost"] == 5  # 6 total units, q1 has 0 cost


def test_golden_03_group_by_storage_location():
    snap = _golden_vault()
    res = query_vault_aggregate(snap, group_by="storage_location")
    by_loc = {g["key"]: g for g in res["groups"]}
    assert by_loc["Bank SDB"]["total_value"] == 2840.0
    assert by_loc["Home Safe"]["total_value"] == 220.0


def test_golden_04_filter_by_retailer_apmex():
    snap = _golden_vault()
    res = query_vault_aggregate(snap, filters={"retailer": "APMEX"})
    assert res["groups"][0]["total_value"] == 2960.0
    assert set(res["matching_coin_ids"]) == {"m1", "g1"}


def test_golden_05_filter_raw_coins_only():
    snap = _golden_vault()
    res = query_vault_aggregate(snap, filters={"is_raw": True})
    assert res["groups"][0]["count"] == 3
    assert set(res["matching_coin_ids"]) == {"m2", "q1", "q2"}


def test_golden_06_spot_sim_silver_50_gold_3500():
    snap = _golden_vault()
    res = simulate_spot_prices(snap, gold=3500.0, silver=50.0)
    # g1 bumped from 2800 -> 3500 (+700); m2 bumped from 40 -> 38.67 (no bump);
    # m1 stays 160 (2*0.77344*50 = 77.34 < 160); q1/q2 stay 25/35
    assert res["simulated_total"] == 3760.0
    assert res["delta_dollars"] == 700.0


def test_golden_07_spot_sim_silver_100_bumps_m2_and_m1():
    snap = _golden_vault()
    res = simulate_spot_prices(snap, gold=2650.0, silver=100.0)
    # m1: max(160, 2*0.77344*100=154.688) = 160
    # m2: max(40, 77.344) = 77.344
    # g1: 2800, q1: 25, q2: 35 -> 3097.34
    assert res["simulated_total"] == 3097.34


def test_golden_08_fine_oz_totals():
    snap = _golden_vault()
    res = simulate_spot_prices(snap, gold=2650.0, silver=31.5)
    assert res["fine_oz"]["au"] == 1.0
    # 3*0.77344 + 2*0.18084 = 2.6820
    assert res["fine_oz"]["ag"] == 2.682


def test_golden_09_duplicates_detects_m1_and_quarters():
    snap = _golden_vault()
    dups = find_duplicates(snap)
    assert len(dups["duplicate_groups"]) == 2
    assert dups["total_recoverable_value"] == 110.0  # 80 (m1 extra) + 30 (quarter extra)


def test_golden_10_duplicates_min_unit_value_filter():
    snap = _golden_vault()
    dups = find_duplicates(snap, min_unit_value=50.0)
    assert len(dups["duplicate_groups"]) == 1
    assert dups["duplicate_groups"][0]["coin_ids"] == ["m1"]


def test_golden_11_group_by_grading_service():
    snap = _golden_vault()
    res = query_vault_aggregate(snap, group_by="grading_service")
    by_grade = {g["key"]: g["total_value"] for g in res["groups"]}
    assert by_grade["NGC"] == 2800.0
    assert by_grade["PCGS"] == 160.0
    assert by_grade["Unknown"] == 100.0


def test_golden_12_net_liquidation_total():
    snap = _golden_vault()
    res = query_vault_aggregate(snap)
    # m1: 2*65=130, m2: 32, g1: 2680, q1: 25*(1-0.13)=21.75, q2: 35*(1-0.13)=30.45 -> 2894.20
    assert res["groups"][0]["net_liq"] == 2894.2
