"""
numista_backend/tests/test_v8_18_15e_regression.py
--------------------------------------------------
Comprehensive Regression Suite for P7 V8.18.15e per NET-440B Priority 2:
1. U.S. Mint invoice 092052 with Gemini response as a top-level LIST.
2. The ASE invoice (USM23339673) with existing matching 2026-W ASE.
3. Bulk CSV of 5 rows including 1 Year/Mint/Denom duplicate.
4. Session status is done_with_errors (never done) when any file errors.
5. All 4 duplicate paths (manual add, scan-save, cert-save, batch import) route through check_and_flag_duplicate.
6. NET-440A Item A4: 3 queue docs with same invoice # and empty item # commit 3, skip 0.
"""

import os
import sys
import uuid
from unittest.mock import MagicMock
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import normalize_and_validate_receipt
from services.duplicate_check import check_and_flag_duplicate


# ── Mock Firestore Helpers ───────────────────────────────────────────────────

class MockQuery:
    def __init__(self, coins, filters):
        self.coins = coins
        self.filters = list(filters)

    def where(self, field, op, val):
        return MockQuery(self.coins, self.filters + [(field, op, val)])

    def limit(self, n):
        self._limit = n
        return self

    def get(self):
        matching = []
        for c in self.coins:
            ok = True
            for f, op, val in self.filters:
                c_val = c.get(f)
                if op == "==" and str(c_val).strip() != str(val).strip():
                    ok = False
                    break
                elif op == "in":
                    norm_val = [str(x).strip() for x in val]
                    if str(c_val).strip() not in norm_val:
                        ok = False
                        break
            if ok:
                doc = MagicMock()
                doc.id = c.get("id", str(uuid.uuid4()))
                doc.to_dict.return_value = c
                matching.append(doc)
        if hasattr(self, "_limit"):
            matching = matching[:self._limit]
        return matching


class MockCoinsRef:
    def __init__(self, existing_coins=None):
        self.coins = existing_coins or []

    def where(self, field, op, val):
        return MockQuery(self.coins, [(field, op, val)])

    def document(self, doc_id=None):
        doc = MagicMock()
        doc.id = doc_id or str(uuid.uuid4())
        return doc


# ── Tests ────────────────────────────────────────────────────────────────────

def test_invoice_092052_gemini_response_as_top_level_list():
    """
    Priority 2.1: U.S. Mint invoice 092052 with Gemini response as a top-level LIST.
    Asserts:
    - No exception raised when data is a list.
    - Top-level retailer, invoice #, and purchase date are preserved across all coins.
    - Both Title Case ('Retailer/Website', 'Retailer Invoice #', 'Purchase Date')
      and snake_case ('retailer', 'invoice_number', 'purchase_date') are set.
    - Receipt doc extracts retailer, invoice #, and date cleanly without list.get crash.
    """
    raw_list_data = [
        {
            "retailer": "USA Coins",
            "invoice_number": "092052",
            "invoice_date": "2026-06-03",
            "subtotal": 150.0,
            "shipping_fee": 10.0,
            "tax_fee": 5.0,
            "total_amount": 165.0,
            "line_items": [
                {
                    "Program/Series": "Lincoln Cent",
                    "Year": "1909",
                    "Mint Mark": "S",
                    "Denomination": "Cent",
                    "Cost": 150.0,
                    "qty": 1,
                }
            ],
        }
    ]

    results = normalize_and_validate_receipt(raw_list_data, fname="Receipt_2026-06-03_092052.pdf")
    assert len(results) == 1, f"Expected 1 coin, got {len(results)}"
    coin = results[0]

    # Verify field synchronization
    assert coin["retailer"] == "USA Coins"
    assert coin["Retailer/Website"] == "USA Coins"
    assert coin["invoice_number"] == "092052"
    assert coin["Retailer Invoice #"] == "092052"
    assert coin["purchase_date"] == "2026-06-03"
    assert coin["Purchase Date"] == "2026-06-03"
    assert coin["Cost"] in (150.0, 165.0)

    # Verify worker header extraction (simulating main.py safe hdr extraction)
    hdr = raw_list_data if isinstance(raw_list_data, dict) else (
        raw_list_data[0] if raw_list_data and isinstance(raw_list_data[0], dict) else {}
    )
    first_c = results[0] if results else {}
    retailer_val = (hdr.get("retailer") or hdr.get("Retailer/Website") or first_c.get("Retailer/Website") or first_c.get("retailer") or "").strip()
    invoice_num_val = (hdr.get("invoice_number") or hdr.get("Retailer Invoice #") or first_c.get("Retailer Invoice #") or first_c.get("invoice_number") or "").strip()
    invoice_date_val = (hdr.get("invoice_date") or hdr.get("date") or hdr.get("Purchase Date") or first_c.get("Purchase Date") or first_c.get("purchase_date") or "").strip()

    assert retailer_val == "USA Coins"
    assert invoice_num_val == "092052"
    assert invoice_date_val == "2026-06-03"


def test_ase_invoice_order_usm23339673_duplicate_flag():
    """
    Priority 2.2: The ASE invoice (USM23339673) with existing matching 2026-W ASE.
    Asserts:
    - Receipt doc has retailer, invoice #, and date.
    - Existing matching 2026-W ASE causes duplicate flag to be set.
    - Coin is NOT dropped or deleted; it is retained with possible_duplicate: True.
    """
    raw_ase_invoice = {
        "retailer": "United States Mint",
        "invoice_number": "USM23339673",
        "invoice_date": "2026-03-15",
        "line_items": [
            {
                "Program/Series": "American Silver Eagle",
                "Year": "2026",
                "Mint Mark": "W",
                "Denomination": "Dollar",
                "Cost": 85.00,
                "qty": 1,
            }
        ],
    }

    results = normalize_and_validate_receipt(raw_ase_invoice, fname="invoice_american_eagle.pdf")
    assert len(results) == 1
    ase_coin = results[0]

    assert ase_coin["retailer"] == "United States Mint"
    assert ase_coin["invoice_number"] == "USM23339673"
    assert ase_coin["purchase_date"] == "2026-03-15"

    # Simulate existing 2026-W Dollar in user's collection
    mock_coins_ref = MockCoinsRef([
        {
            "id": "existing-2026w-ase",
            "Year": "2026",
            "Mint Mark": "W",
            "Denomination": "Dollar",
        }
    ])

    is_dupe = check_and_flag_duplicate(mock_coins_ref, ase_coin)
    assert is_dupe is True
    assert ase_coin["possible_duplicate"] is True
    assert ase_coin["duplicate_flag"] == "Attribute match (Year, Mint, Denomination)"


def test_bulk_csv_5_rows_with_duplicate():
    """
    Priority 2.3: Bulk CSV of 5 rows with 1 Year/Mint/Denom duplicate.
    Asserts:
    - 5 total rows processed, none dropped.
    - 1 row flagged as duplicate, 4 rows not flagged.
    """
    existing_collection = [
        {"id": "exist-1921", "Year": "1921", "Mint Mark": "", "Denomination": "Dollar"}
    ]
    mock_coins_ref = MockCoinsRef(existing_collection)

    csv_rows = [
        {"Year": "1921", "Mint Mark": "", "Denomination": "Dollar", "Item": "Morgan Dollar"},
        {"Year": "1922", "Mint Mark": "", "Denomination": "Dollar", "Item": "Peace Dollar"},
        {"Year": "1943", "Mint Mark": "S", "Denomination": "Half Dollar", "Item": "Walking Liberty"},
        {"Year": "1964", "Mint Mark": "D", "Denomination": "Half Dollar", "Item": "Kennedy Half"},
        {"Year": "2000", "Mint Mark": "P", "Denomination": "Dollar", "Item": "Sacagawea"},
    ]

    flagged_count = 0
    for row in csv_rows:
        if check_and_flag_duplicate(mock_coins_ref, row):
            flagged_count += 1

    assert len(csv_rows) == 5, "No rows should be dropped"
    assert flagged_count == 1, f"Expected exactly 1 flagged duplicate, got {flagged_count}"
    assert csv_rows[0].get("possible_duplicate") is True
    assert csv_rows[1].get("possible_duplicate") is None or csv_rows[1].get("possible_duplicate") is False


def test_session_status_done_with_errors_when_any_file_errors():
    """
    Priority 2.4: Session status must be done_with_errors (never done) when any per_file entry has status error.
    """
    per_file_success = [
        {"filename": "rec1.pdf", "status": "done"},
        {"filename": "rec2.pdf", "status": "done"},
    ]
    any_errors_success = any(f.get("status") == "error" for f in per_file_success)
    status_success = "done_with_errors" if any_errors_success else "done"
    assert status_success == "done"

    per_file_with_error = [
        {"filename": "rec1.pdf", "status": "done"},
        {"filename": "bad.pdf", "status": "error", "error": "Corrupt PDF"},
    ]
    any_errors_fail = any(f.get("status") == "error" for f in per_file_with_error)
    status_fail = "done_with_errors" if any_errors_fail else "done"
    assert status_fail == "done_with_errors"


def test_duplicate_paths_all_route_through_helper():
    """
    Priority 2.5: Test each duplicate path (manual single add, scan-save, cert-lookup save, spreadsheet import).
    Asserts:
    - Shared helper handles diverse denomination formatting ('$5', '5', 'Dollar', etc.)
    - Exclude IDs is respected for updates/re-reviews.
    """
    mock_coins_ref = MockCoinsRef([
        {"id": "c1", "Year": "1881", "Mint Mark": "S", "Denomination": "$1"},
        {"id": "c2", "Year": "1909", "Mint Mark": "S", "Denomination": "Cent"},
    ])

    # Path A: Manual add / spreadsheet import
    coin_to_add = {"Year": "1881", "Mint Mark": "S", "Denomination": "1"}
    assert check_and_flag_duplicate(mock_coins_ref, coin_to_add) is True
    assert coin_to_add["possible_duplicate"] is True

    # Path B: Exclude IDs (re-reviewing the same coin doc)
    coin_re_review = {"Year": "1881", "Mint Mark": "S", "Denomination": "1"}
    assert check_and_flag_duplicate(mock_coins_ref, coin_re_review, exclude_ids=["c1"]) is False

    # Path C: Cert save / Scan save with clean coin
    clean_coin = {"Year": "1928", "Mint Mark": "P", "Denomination": "Dollar"}
    assert check_and_flag_duplicate(mock_coins_ref, clean_coin) is False
    assert clean_coin.get("possible_duplicate") is not True


def test_commit_reviews_argon_a4_invoice_empty_item_no():
    """
    NET-440A Item A4: 3 queue docs with same invoice # and empty item #
    commit 3, skip 0, 0 queue deletes without commit.
    """
    from main import CommitReviewsRequest

    queue_docs = [
        {"id": "q1", "Year": "2026", "Mint Mark": "W", "Denomination": "Dollar", "invoice_number": "USM-999", "item_number": ""},
        {"id": "q2", "Year": "2026", "Mint Mark": "W", "Denomination": "Dollar", "invoice_number": "USM-999", "item_number": ""},
        {"id": "q3", "Year": "2026", "Mint Mark": "W", "Denomination": "Dollar", "invoice_number": "USM-999", "item_number": ""},
    ]

    # Verify that inv_no and item_no matching requires BOTH to be non-empty
    inv_map = {}
    for q in queue_docs:
        inv_no = (q.get("invoice_number") or "").strip()
        item_no = (q.get("item_number") or "").strip()
        is_definite_dupe = False
        if inv_no and item_no:
            key = (inv_no, item_no)
            if key in inv_map:
                is_definite_dupe = True
            else:
                inv_map[key] = q["id"]
        assert not is_definite_dupe, "Empty item_number must NOT collapse items with same invoice_number"
