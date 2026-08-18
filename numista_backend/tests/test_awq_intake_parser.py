import pytest
import re
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from remediate_awq_themes_and_supplies import (
    AWQ_ROSTER,
    match_honoree,
    is_supply_document,
    normalize_text,
)

class TestAwqHonoreeIntake:
    @pytest.mark.parametrize("honoree", AWQ_ROSTER)
    def test_all_20_official_roster_honorees_matched(self, honoree):
        """Verify that line-item descriptions containing any of the 20 official US Mint honorees match cleanly."""
        sample_doc = {
            "Item Description": f"2023-P {honoree} American Women Quarter BU Uncirculated",
            "Program/Series": "American Women Quarters",
            "Denomination": "Quarter",
            "Year": "2023",
        }
        canonical, status = match_honoree(sample_doc)
        assert status == "matched"
        assert canonical == honoree

    @pytest.mark.parametrize(
        "raw_string, expected_canonical",
        [
            ("2024-P Patsy Mink Quarter", "Patsy Takemoto Mink"),
            ("2024-D Rev Dr Pauli Murray Unc", "Rev. Dr. Pauli Murray"),
            ("2024-S Dr Mary Edwards Walker Proof", "Dr. Mary Edwards Walker"),
            ("2022-P Dr Sally Ride Quarter", "Dr. Sally Ride"),
            ("2022-P Sally Ride Quarter BU", "Dr. Sally Ride"),
            ("2023-P Edith Kanaka'ole Quarter", "Edith Kanaka'ole"),
            ("2024-D Zitkala-Sa Quarter", "Zitkala-Sa"),
            ("2025-P Dr. Vera Rubin Quarter", "Dr. Vera Rubin"),
            ("2025-D Vera Rubin Quarter", "Dr. Vera Rubin"),
        ],
    )
    def test_honoree_aliases_and_punctuation(self, raw_string, expected_canonical):
        """Verify that aliases and variations with/without titles and punctuation map to canonical names."""
        sample_doc = {
            "Item Description": raw_string,
            "Program/Series": "American Women Quarters",
            "Denomination": "Quarter",
        }
        canonical, status = match_honoree(sample_doc)
        assert status == "matched"
        assert canonical == expected_canonical

    def test_unmatched_ambiguous_awq_marked_needs_review(self):
        """Verify that AWQ items without an explicit honoree name return needs_review and never guess."""
        sample_doc = {
            "Item Description": "2025-P American Women Quarters",
            "Program/Series": "American Women Quarters",
            "Denomination": "Quarter",
            "Year": "2025",
        }
        canonical, status = match_honoree(sample_doc)
        assert status == "needs_review"
        assert canonical is None

    def test_idempotent_skip_if_already_set(self):
        """Verify that already assigned roster themes are preserved and skipped."""
        sample_doc = {
            "theme_subject": "Maya Angelou",
            "Item Description": "2022-P American Women Quarters",
        }
        canonical, status = match_honoree(sample_doc)
        assert status == "skipped_already_set"
        assert canonical == "Maya Angelou"

class TestConjunctiveSupplyClassifier:
    @pytest.mark.parametrize(
        "title, doc_data",
        [
            ("U.S. Women's Quarter Book", {"Item Description": "U.S. Women's Quarter Book", "Denomination": "", "Year": ""}),
            ("Quarter Album 2022-2025", {"Item Description": "Quarter Album 2022-2025", "Denomination": "", "Year": ""}),
            ("Numismatic Deluxe Coin Binder", {"Item Description": "Numismatic Deluxe Coin Binder", "Denomination": "", "Year": ""}),
            ("Air-Tite Coin Capsule Holder 24mm", {"Item Description": "Air-Tite Coin Capsule Holder 24mm", "Denomination": "", "Year": ""}),
        ],
    )
    def test_supply_items_correctly_classified(self, title, doc_data):
        """Verify that genuine numismatic accessories without coin year/denomination are tagged as supplies."""
        assert is_supply_document(doc_data) is True

    @pytest.mark.parametrize(
        "coin_title, doc_data",
        [
            (
                "1946 Booker T. Washington Commemorative Half Dollar",
                {
                    "Item Description": "1946 Booker T. Washington Commemorative Half Dollar",
                    "Denomination": "Half Dollar",
                    "Year": "1946",
                    "Program/Series": "Commemorative Half Dollars",
                },
            ),
            (
                "1951 Washington-Carver Commemorative Half Dollar",
                {
                    "Item Description": "1951 Washington-Carver Commemorative Half Dollar",
                    "Denomination": "Half Dollar",
                    "Year": "1951",
                },
            ),
            (
                "2022-P Maya Angelou Quarter",
                {
                    "Item Description": "2022-P Maya Angelou Quarter",
                    "Denomination": "Quarter",
                    "Year": "2022",
                    "Program/Series": "American Women Quarters",
                },
            ),
            (
                "1921 Morgan Silver Dollar BU",
                {
                    "Item Description": "1921 Morgan Silver Dollar BU",
                    "Denomination": "Dollar",
                    "Year": "1921",
                },
            ),
        ],
    )
    def test_commemorative_and_regular_coins_never_classified_as_supplies(self, coin_title, doc_data):
        """Verify that real coins with valid denomination and year (like Booker T. Washington) are NEVER classified as supplies."""
        assert is_supply_document(doc_data) is False
