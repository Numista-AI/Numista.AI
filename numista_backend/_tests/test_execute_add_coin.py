#!/usr/bin/env python3
"""
test_execute_add_coin.py
========================
Mandatory 3 Integration Test Cases for Coin Ingestion & Greysheet Timeout Contract.

1. Test 1: Successful Catalog Hit + Greysheet Resolution (2019-W San Antonio Missions Quarter).
2. Test 2: Catalog Miss Path (raw theme preserved, valuation_source == 'Unmapped – Manual Review Required').
3. Test 3: Greysheet Timeout / 429 Fallback (local SQLite baseline valuation + valuation_source == 'Local Catalog Baseline').
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Ensure backend directory is on sys.path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from services.mint_nomenclature_service import resolve_coin_catalog_metadata, slugify


class TestExecuteAddCoin(unittest.TestCase):

    def test_slugify_canonical_keys(self):
        """Verify slugify produces exact keys matching coin_image_index."""
        self.assertEqual(slugify("San Antonio Missions National Historical Park"), "san-antonio-missions")
        self.assertEqual(slugify("America the Beautiful Quarters"), "america-the-beautiful")
        self.assertEqual(slugify("War in the Pacific"), "war-in-the-pacific")

    def test_catalog_hit_san_antonio_missions(self):
        """Test 1: Success Path for 2019-W San Antonio Missions Quarter."""
        meta = resolve_coin_catalog_metadata(
            year="2019",
            denomination="Quarter",
            mint_mark="W",
            program_series="America the Beautiful",
            theme_subject="San Antonio Missions",
            variety="W Mint Mark"
        )
        self.assertEqual(meta["program_series"], "America the Beautiful Quarters")
        self.assertEqual(meta["series_slug"], "america-the-beautiful")
        self.assertEqual(meta["theme_subject"], "San Antonio Missions")
        self.assertEqual(meta["subject_slug"], "texas")
        self.assertEqual(meta["country"], "United States")
        self.assertFalse(meta["is_foreign"])
        self.assertTrue(meta["catalog_matched"])

    def test_catalog_miss_path(self):
        """Test 2: Catalog Miss Path preserves raw inputs without synthesizing generic strings."""
        meta = resolve_coin_catalog_metadata(
            year="2035",
            denomination="Future Token",
            program_series="Experimental Cyber Series",
            theme_subject="Quantum Circuit Design"
        )
        self.assertEqual(meta["program_series"], "Experimental Cyber Series")
        self.assertEqual(meta["theme_subject"], "Quantum Circuit Design")
        self.assertEqual(meta["valuation_source"], "Unmapped – Manual Review Required")
        self.assertFalse(meta["catalog_matched"])
        # Ensure no synthesized '2035 Future Token' strings created
        self.assertNotIn("2035 Future Token", meta["theme_subject"])

    @patch("services.greysheet_service.GreysheetService.resolve_coin_with_timeout")
    def test_greysheet_timeout_fallback(self, mock_gs):
        """Test 3: Greysheet Timeout/429 Fallback returns local SQLite catalog baseline."""
        mock_gs.return_value = None  # Simulate 1000ms timeout
        meta = resolve_coin_catalog_metadata(
            year="2019",
            denomination="Quarter",
            theme_subject="San Antonio Missions"
        )
        self.assertTrue(meta["catalog_matched"])
        self.assertEqual(meta["valuation_source"], "Local Catalog Baseline")


if __name__ == "__main__":
    unittest.main()
