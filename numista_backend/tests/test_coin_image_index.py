"""P5 / P5a tests for build_image_index.py and coin_image_schema.json parity."""

import json
from pathlib import Path
import sys

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "_scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import build_image_index as idx


def test_scan_targets_include_previously_missing_folders():
    prefixes = {prefix for (_, prefix, _, _, _) in idx.SCAN_TARGETS}
    assert "reference_library/atb_quarters/" in prefixes
    assert "reference_library/us_mint_official/" in prefixes
    assert "reference_library/2023_series/" in prefixes
    assert "reference_library/2024_series/" in prefixes
    assert "reference_library/2025_series/" in prefixes
    assert "reference_library/2026_series/" in prefixes


def test_ulysses_s_grant_presidential_2011():
    res = idx.parse_filename(
        "reference_library/bulk_programs/2011_ulysses_s_grant_presidential_dollar_obverse.jpg",
        "numista-reference-library",
        "reference_library/bulk_programs/",
        2,
    )
    assert res is not None
    assert res["year"] == "2011"
    assert res["mint"] is None
    assert res["program"] == "presidential-dollars"
    assert res["subject"] == "ulysses-s-grant"
    assert res["side"] == "obverse"
    assert res["composite_key"] == "dollar|presidential-dollars|2011|ulysses-s-grant|obverse"


def test_theodore_roosevelt_no_cross_program_collision():
    dollar_res = idx.parse_filename(
        "reference_library/bulk_programs/2013_theodore_roosevelt_presidential_dollar_obverse.jpg",
        "numista-reference-library",
        "reference_library/bulk_programs/",
        2,
    )
    atb_res = idx.parse_filename(
        "reference_library/atb_quarters/2016-america-the-beautiful-quarters-coin-theodore-roosevelt-uncirculated-reverse.jpg",
        "numista-reference-library",
        "reference_library/atb_quarters/",
        2,
    )
    assert dollar_res is not None
    assert atb_res is not None
    assert dollar_res["composite_key"] == "dollar|presidential-dollars|2013|theodore-roosevelt|obverse"
    assert atb_res["composite_key"] == "quarter|america-the-beautiful|2016|theodore-roosevelt-np|reverse"
    assert dollar_res["composite_key"] != atb_res["composite_key"]


def test_middle_initials_not_parsed_as_mint_marks():
    cases = [
        (
            "reference_library/bulk_programs/2014_D_roosevelt_presidential-dollars_obverse.jpg",
            "2014",
            "franklin-d-roosevelt",
        ),
        (
            "reference_library/bulk_programs/2015_S_truman_presidential-dollars_obverse.jpg",
            "2015",
            "harry-s-truman",
        ),
        (
            "reference_library/bulk_programs/2015_D_eisenhower_presidential-dollars_obverse.jpg",
            "2015",
            "dwight-d-eisenhower",
        ),
        (
            "reference_library/bulk_programs/2015_harry-s-truman_presidential-dollars_obverse.jpg",
            "2015",
            "harry-s-truman",
        ),
    ]
    for blob_name, expected_year, expected_subject in cases:
        res = idx.parse_filename(
            blob_name,
            "numista-reference-library",
            "reference_library/bulk_programs/",
            2,
        )
        assert res is not None, f"Failed to parse {blob_name}"
        assert res["mint"] is None, f"False mint mark on {blob_name}: {res['mint']}"
        assert res["year"] == expected_year
        assert res["subject"] == expected_subject


def test_cleveland_two_terms_and_nixon_2016():
    c1 = idx.parse_filename(
        "reference_library/bulk_programs/2012_grover_cleveland_1st_term_presidential_dollar_obverse.jpg",
        "numista-reference-library",
        "reference_library/bulk_programs/",
        2,
    )
    c2 = idx.parse_filename(
        "reference_library/bulk_programs/2012_grover_cleveland_2nd_term_presidential_dollar_obverse.jpg",
        "numista-reference-library",
        "reference_library/bulk_programs/",
        2,
    )
    nixon = idx.parse_filename(
        "reference_library/bulk_programs/2016_richard_nixon_presidential-dollars_obverse.jpg",
        "numista-reference-library",
        "reference_library/bulk_programs/",
        2,
    )
    assert c1 is not None and c2 is not None and nixon is not None
    assert c1["subject"] == "grover-cleveland-1st"
    assert c2["subject"] == "grover-cleveland-2nd"
    assert c1["composite_key"] != c2["composite_key"]
    assert nixon["subject"] == "richard-nixon"
    assert nixon["composite_key"] == "dollar|presidential-dollars|2016|richard-nixon|obverse"


def test_2026_semiquincentennial_quarters_underscore_year():
    designs = [
        ("2026_quarter_dollar_mayflower_compact_reverse.jpg", "mayflower-compact"),
        ("2026_quarter_dollar_revolutionary_war_reverse.jpg", "revolutionary-war"),
        ("2026_quarter_dollar_declaration_of_independence_reverse.jpg", "declaration-of-independence"),
        ("2026_quarter_dollar_us_constitution_reverse.jpg", "us-constitution"),
        ("2026_quarter_dollar_gettysburg_address_reverse.jpg", "gettysburg-address"),
    ]
    keys = set()
    for fname, expected_subject in designs:
        res = idx.parse_filename(
            f"reference_library/2026_series/{fname}",
            "numista-reference-library",
            "reference_library/2026_series/",
            2,
        )
        assert res is not None, f"Failed on {fname}"
        assert res["year"] == "2026"
        assert res["subject"] == expected_subject
        assert res["side"] == "reverse"
        keys.add(res["composite_key"])
    assert len(keys) == 5


def test_atb_san_antonio_missions_2019():
    res = idx.parse_filename(
        "reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg",
        "numista-reference-library",
        "reference_library/atb_quarters/",
        2,
    )
    assert res is not None
    assert res["composite_key"] == "quarter|america-the-beautiful|2019|san-antonio-missions|reverse"


def test_american_women_quarters_2022_unlabelled_side_defaults_to_reverse():
    honorees = [
        ("2022_american_women_quarters_maya_angelou.jpg", "maya-angelou"),
        ("2022_american_women_quarters_sally_ride.jpg", "sally-ride"),
        ("2022_american_women_quarters_wilma_mankiller.jpg", "wilma-mankiller"),
        ("2022_american_women_quarters_nina_otero_warren.jpg", "nina-otero-warren"),
        ("2022_american_women_quarters_anna_may_wong.jpg", "anna-may-wong"),
    ]
    for fname, expected_subject in honorees:
        res = idx.parse_filename(
            f"reference_library/bulk_programs/{fname}",
            "numista-reference-library",
            "reference_library/bulk_programs/",
            2,
        )
        assert res is not None
        assert res["program"] == "american-women-quarters"
        assert res["subject"] == expected_subject
        assert res["side"] == "reverse", f"Expected reverse default for unlabelled AWQ {fname}"


def test_select_winners_deterministic_tier_ranking():
    tier3 = idx.parse_filename(
        "reference_library/wikimedia_uscoin/2011_ulysses_s_grant_presidential_dollar_obverse.jpg",
        "numista-reference-library",
        "reference_library/wikimedia_uscoin/",
        3,
    )
    tier1 = idx.parse_filename(
        "reference_library/us_mint_official/2011_ulysses_s_grant_presidential_dollar_uncirculated_obverse.jpg",
        "numista-reference-library",
        "reference_library/us_mint_official/",
        1,
    )
    for item, label in [(tier3, "Wikimedia"), (tier1, "US Mint")]:
        item["source_label"] = label
        item["attribution"] = ""

    # Regardless of input order, Tier 1 must win
    winners_a, collisions_a = idx.select_winners([tier3, tier1])
    winners_b, collisions_b = idx.select_winners([tier1, tier3])
    assert collisions_a == 1 and collisions_b == 1
    key = "dollar|presidential-dollars|2011|ulysses-s-grant|obverse"
    assert winners_a[key]["source_tier"] == 1
    assert winners_b[key]["source_tier"] == 1
    assert len(winners_a[key]["alternates"]) == 1


def test_schema_parity_with_dart_coin_image_service():
    schema = json.loads((SCRIPTS_DIR / "coin_image_schema.json").read_text(encoding="utf-8"))
    dart_src = (
        Path(__file__).resolve().parents[2]
        / "numista_mobile"
        / "lib"
        / "services"
        / "coin_image_service.dart"
    ).read_text(encoding="utf-8")
    for slug in set(schema["presidential_subjects"].values()):
        assert f"'{slug}'" in dart_src, f"Missing presidential slug {slug} in Dart"
    for slug in set(schema["atb_park_subjects"].values()):
        assert f"'{slug}'" in dart_src, f"Missing ATB park slug {slug} in Dart"
    for slug in set(schema["women_quarter_subjects"].values()):
        assert f"'{slug}'" in dart_src, f"Missing AWQ slug {slug} in Dart"
    for slug in set(schema["native_american_years"].values()):
        assert f"'{slug}'" in dart_src, f"Missing Native American slug {slug} in Dart"
