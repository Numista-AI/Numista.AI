import csv
import json
import os
import re
import unittest

class TestMissingImagesCSV(unittest.TestCase):
    MASTER_PATH = "output/missing_images_sourcing_master.csv"
    REDACTED_PATH = "output/missing_images_sourcing_redacted.csv"

    EXPECTED_COLUMNS = [
        "priority_tier", "user_account", "collection_type", "doc_id", "canonical_doc_id",
        "is_duplicate_record", "missing_sides", "year", "mint_mark", "denomination",
        "program_series", "theme_subject", "variety_error", "strike_type", "metal_content",
        "condition_grade", "grading_service", "cert_number", "retailer", "retailer_item_no",
        "retailer_invoice_no", "purchase_date", "purchase_cost", "personal_notes",
        "existing_obverse_url", "existing_reverse_url", "naming_key", "sourcing_status",
        "source_attribution", "image_credit", "last_checked_date", "attempt_log",
        "direct_search_query", "is_foreign"
    ]

    EXCLUDED_ACCOUNTS = [
        "ericdcman@gmail.com",
        "eric.d.seaman@outlook.com",
        "beta@numista.ai",
    ]

    def test_file_exists_and_header(self):
        self.assertTrue(os.path.exists(self.MASTER_PATH), "Master CSV must exist")
        with open(self.MASTER_PATH, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            self.assertEqual(len(header), 34, "Must have exactly 34 columns")
            self.assertEqual(header, self.EXPECTED_COLUMNS, "Header must match contract")

    def test_row_validations(self):
        with open(self.MASTER_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertGreater(len(rows), 0, "Should contain deficiency rows")

            tier_order = {
                "P1A_ERRORS_AND_VARIETIES": 1,
                "P1B_RARE_CURRENCY": 2,
                "P1C_HIGH_VALUE_OR_BOTH": 3,
                "P2_OBVERSE_MISSING": 4,
                "P3_REVERSE_MISSING": 5,
            }
            last_order = 0

            for i, r in enumerate(rows):
                # Check excluded accounts
                self.assertNotIn(r["user_account"].lower(), self.EXCLUDED_ACCOUNTS, f"Excluded account in row {i}")
                
                # Check attempt_log JSON validity
                log_data = json.loads(r["attempt_log"])
                self.assertIsInstance(log_data, list, "attempt_log must be JSON array")
                self.assertGreater(len(log_data), 0, "attempt_log must not be empty")

                # Check naming_key regex
                self.assertTrue(re.match(r"^[a-z0-9\-_]+\.png$", r["naming_key"]), f"naming_key invalid: {r['naming_key']}")

                # Check priority tier order
                curr_order = tier_order.get(r["priority_tier"], 99)
                self.assertGreaterEqual(curr_order, last_order, f"Tier ordering violated at row {i}")
                last_order = curr_order

    def test_redaction_consistency(self):
        if os.path.exists(self.REDACTED_PATH):
            with open(self.MASTER_PATH, "r", encoding="utf-8") as fm, open(self.REDACTED_PATH, "r", encoding="utf-8") as fr:
                m_rows = list(csv.DictReader(fm))
                r_rows = list(csv.DictReader(fr))
                self.assertEqual(len(m_rows), len(r_rows), "Row counts must match")

                for m, r in zip(m_rows, r_rows):
                    self.assertEqual(m["doc_id"], r["doc_id"])
                    self.assertEqual(r["purchase_cost"], "[REDACTED]")
                    self.assertEqual(r["retailer_invoice_no"], "[REDACTED]")
                    self.assertEqual(r["personal_notes"], "[REDACTED]")

if __name__ == "__main__":
    unittest.main()
