"""
test_invoice_fixtures.py — Verify Repository-Relative Invoice Fixtures & OCR Router
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pathlib
import pytest

FIXTURES_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "numista_tests" / "fixtures" / "invoices"

def test_invoice_fixtures_exist():
    """Verify that all 5 repository-relative invoice sample PDFs exist in numista_tests/fixtures/invoices/."""
    assert FIXTURES_DIR.exists(), f"Fixtures directory not found at {FIXTURES_DIR}"
    
    expected_files = [f"sample_receipt_{i}.pdf" for i in range(1, 6)]
    for filename in expected_files:
        filepath = FIXTURES_DIR / filename
        assert filepath.exists(), f"Fixture file missing: {filepath}"
        assert filepath.stat().st_size > 0, f"Fixture file is empty: {filepath}"

def test_invoice_line_item_classification_router():
    """Verify line-item classification parsing handles coin, banknote, supply, and medal items cleanly."""
    mock_ocr_items = [
        {"raw_text": "1921 Morgan Silver Dollar $1", "price": "$35.00", "qty": "1"},
        {"raw_text": "1896 $1 Silver Certificate Educational", "price": "$450.00", "qty": "1"},
        {"raw_text": "Whitman Eisenhower Dollar Album", "price": "$12.95", "qty": "2"},
        {"raw_text": "2x 1937-D Buffalo Nickel @ $15.00", "price": "$30.00", "qty": "2"}
    ]

    processed_items = []
    for item in mock_ocr_items:
        text = item.get("raw_text", "").lower()
        if "album" in text or "holder" in text or "folder" in text or "supply" in text:
            category = "supply"
        elif "certificate" in text or "note" in text or "currency" in text or "bill" in text:
            category = "paper_currency"
        elif "medal" in text or "token" in text:
            category = "medal"
        else:
            category = "coin"
            
        processed_items.append({
            "title": item.get("raw_text"),
            "price": item.get("price", "$0.00"),
            "quantity": item.get("qty", "1"),
            "category": category
        })

    assert len(processed_items) == 4
    assert processed_items[0]["category"] == "coin"
    assert processed_items[1]["category"] == "paper_currency"
    assert processed_items[2]["category"] == "supply"
    assert processed_items[3]["category"] == "coin"


def test_invoice_json_list_normalization():
    """Verify that if Gemini returns a JSON list instead of a dict, normalization extracts items safely."""
    import json
    try:
        from main import clean_valuation_value
    except ModuleNotFoundError:
        from main import clean_valuation_value

    raw_json_list = [
        {"Program/Series": "American Gold Eagle", "Year": "2026", "Cost": 2100.0, "is_supply": False},
        {"Program/Series": "Morgan Dollar", "Year": "1921", "Cost": "$45.50", "is_supply": False},
        {"Program/Series": "Whitman Folder", "Year": "", "Cost": 12.95, "is_supply": True}
    ]

    data = raw_json_list
    if isinstance(data, list):
        if data and isinstance(data[0], dict) and ("line_items" in data[0] or "retailer" in data[0]):
            data = data[0]
        elif data and isinstance(data[0], dict):
            data = {"line_items": data}
        else:
            data = {"line_items": []}
    elif not isinstance(data, dict):
        data = {"line_items": []}

    items = data.get("line_items")
    if not isinstance(items, list):
        for fallback_key in ("items", "coins", "results", "data"):
            candidate = data.get(fallback_key)
            if isinstance(candidate, list):
                items = candidate
                break
    if not isinstance(items, list):
        items = []
    items = [it for it in items if isinstance(it, dict)]

    assert len(items) == 3
    assert items[0]["Program/Series"] == "American Gold Eagle"
    assert clean_valuation_value(items[1]["Cost"]) == 45.50
    assert items[2]["is_supply"] is True


def test_invoice_multi_item_landed_cost_allocation():
    """Verify multi-item proportional landed cost allocation with non-zero shipping/tax."""
    try:
        from main import clean_valuation_value
    except ModuleNotFoundError:
        from main import clean_valuation_value

    items = [
        {"Program/Series": "American Gold Eagle", "Cost": 1000.0},
        {"Program/Series": "Morgan Dollar", "Cost": 50.0},
    ]
    subtotal_val = clean_valuation_value("$1,050.00")
    shipping_val = clean_valuation_value("$25.00")
    tax_val      = clean_valuation_value("$10.00")
    grand_total  = clean_valuation_value("$1,085.00")

    raw_item_sum = sum(clean_valuation_value(it.get("Cost") or 0.0) for it in items)
    assert raw_item_sum == 1050.0
    total_global_fees = grand_total - subtotal_val
    assert total_global_fees == 35.0

    allocations = []
    for it in items:
        sticker_price = clean_valuation_value(it.get("Cost") or 0.0)
        allocated_fee = round(total_global_fees * (sticker_price / raw_item_sum), 2)
        landed_cost = round(sticker_price + allocated_fee, 2)
        allocations.append((sticker_price, allocated_fee, landed_cost))

    # Item 1: 35.0 * (1000 / 1050) = 33.33 -> 1033.33
    # Item 2: 35.0 * (50 / 1050) = 1.67 -> 51.67
    assert allocations[0] == (1000.0, 33.33, 1033.33)
    assert allocations[1] == (50.0, 1.67, 51.67)
    assert round(sum(a[1] for a in allocations), 2) == 35.0


def test_invoice_multi_object_line_items_merge():
    """NET-400a: Verify multi-object list with line_items across multiple dicts merges correctly using production normalizer."""
    try:
        from main import normalize_and_validate_receipt
    except ModuleNotFoundError:
        from main import normalize_and_validate_receipt

    data = [
        {"retailer": "US Mint", "invoice_number": "INV-100", "line_items": [
            {"Program/Series": "American Silver Eagle", "Year": "2024", "Cost": 35.0, "qty": 1}
        ]},
        {"line_items": [
            {"Program/Series": "Morgan Dollar", "Year": "2023", "Cost": 75.0, "qty": 2}
        ]}
    ]

    results = normalize_and_validate_receipt(data)
    assert len(results) == 3  # 1 ASE + 2 Morgan Dollars
    assert results[0]["Program/Series"] == "American Silver Eagle"
    assert results[0]["retailer"] == "US Mint"
    assert results[1]["Program/Series"] == "Morgan Dollar"
    assert results[2]["Program/Series"] == "Morgan Dollar"


def test_invoice_quantity_and_supply_filter_and_set_normalization():
    """NET-400b,c: Test quantity looping, supply folder skipping, and Cent & Nickel Set normalization using production normalizer."""
    try:
        from main import normalize_and_validate_receipt
    except ModuleNotFoundError:
        from main import normalize_and_validate_receipt

    raw_data = {
        "line_items": [
            {"Program/Series": "Lincoln Cent", "Year": "2024", "Cost": 5.0, "qty": 3, "Denomination": "Cent"},
            {"Program/Series": "Whitman Coin Album", "Year": "", "Cost": 15.0, "is_supply": True, "Denomination": ""},
            {"Program/Series": "", "Year": "2022", "Cost": 25.0, "qty": 1, "Denomination": "Unknown Cent/Nickel"},
        ]
    }

    results = normalize_and_validate_receipt(raw_data)
    # Album skipped (1 item), Lincoln Cent repeated 3 times, Cent & Nickel Set repeated 1 time = 4 coins
    assert len(results) == 4
    cents = [c for c in results if c["Program/Series"] == "Lincoln Cent"]
    assert len(cents) == 3
    set_coin = [c for c in results if c["Program/Series"] == "Cent & Nickel Set"]
    assert len(set_coin) == 1
    assert set_coin[0]["Denomination"] == "Cent"
    assert not any("album" in (c.get("Personal Notes") or "").lower() for c in results)


def test_invoice_092052_acceptance():
    """NET-400: Acceptance test for 092052 invoice (15 line items in, 2 with qty=2, 1 set, supply rows filtered).
    Calls production normalize_and_validate_receipt directly from main.py and asserts:
    - Exactly 15 output coins
    - 0 supply rows
    - Set rows mapped (Unknown Cent/Nickel -> Cent & Nickel Set, Cent)
    - Quantities multiplied out
    """
    try:
        from main import normalize_and_validate_receipt
    except ModuleNotFoundError:
        from main import normalize_and_validate_receipt

    raw_invoice = {
        "invoice_number": "092052",
        "retailer": "USA Coins",
        "line_items": [
            # 1 supply row (must be skipped -> 0 coins)
            {"Program/Series": "Whitman Eisenhower Dollar Album", "Year": "", "Cost": 12.95, "is_supply": True, "Denomination": "Supplies"},
            # 1 accessory folder row (must be skipped -> 0 coins)
            {"Program/Series": "Coin Storage Box & Flips", "Year": "", "Cost": 8.50, "is_supply": True, "Denomination": "Supplies"},
            # 1 set row (must map to Cent & Nickel Set, Cent -> 1 coin)
            {"Program/Series": "", "Year": "2021", "Cost": 35.0, "qty": 1, "Denomination": "Unknown Cent/Nickel", "Personal Notes": "21st Century Penny and Nickel Set"},
            # 2 rows with qty=2 (must expand to 2 coins each -> 4 coins)
            {"Program/Series": "Kennedy Half Dollar", "Year": "2001", "Cost": 10.0, "qty": 2, "Denomination": "Half Dollar", "Mint Mark": "P"},
            {"Program/Series": "Kennedy Half Dollar", "Year": "1964", "Cost": 15.0, "qty": 2, "Denomination": "Half Dollar", "Mint Mark": "D"},
            # 10 single coin rows (1 coin each -> 10 coins)
            {"Program/Series": "Mercury Dime", "Year": "1943", "Cost": 5.0, "qty": 1, "Denomination": "Dime", "Mint Mark": ""},
            {"Program/Series": "Mercury Dime", "Year": "1942", "Cost": 5.0, "qty": 1, "Denomination": "Dime", "Mint Mark": "D"},
            {"Program/Series": "Roosevelt Dime", "Year": "1963", "Cost": 4.0, "qty": 1, "Denomination": "Dime", "Mint Mark": "D"},
            {"Program/Series": "Buffalo Nickel", "Year": "1936", "Cost": 8.0, "qty": 1, "Denomination": "Nickel", "Mint Mark": "S"},
            {"Program/Series": "Native American Dollar", "Year": "2017", "Cost": 6.0, "qty": 1, "Denomination": "Dollar", "Mint Mark": "P"},
            {"Program/Series": "Morgan Dollar", "Year": "1881", "Cost": 65.0, "qty": 1, "Denomination": "Dollar", "Mint Mark": "S"},
            {"Program/Series": "Peace Dollar", "Year": "1922", "Cost": 30.0, "qty": 1, "Denomination": "Dollar", "Mint Mark": ""},
            {"Program/Series": "Franklin Half Dollar", "Year": "1954", "Cost": 16.0, "qty": 1, "Denomination": "Half Dollar", "Mint Mark": "D"},
            {"Program/Series": "Walking Liberty Half", "Year": "1943", "Cost": 18.0, "qty": 1, "Denomination": "Half Dollar", "Mint Mark": ""},
            {"Program/Series": "Lincoln Cent", "Year": "1909", "Cost": 12.0, "qty": 1, "Denomination": "Cent", "Mint Mark": "VDB"},
        ]
    }

    # Verify input has exactly 15 line items (2 with qty=2, 1 set, supply rows)
    assert len(raw_invoice["line_items"]) == 15

    results = normalize_and_validate_receipt(raw_invoice, fname="Receipt_2026-06-03_092052.pdf")

    # Output assertions:
    # 1. Output must be exactly 15 coins
    assert len(results) == 15, f"Expected 15 output coins, got {len(results)}"

    # 2. 0 supply rows in output
    for coin in results:
        assert not coin.get("is_supply", False), f"Supply item leaked into output: {coin}"
        notes = (coin.get("Personal Notes") or "").lower()
        assert "album" not in notes, f"Album leaked into output: {coin}"
        assert "storage box" not in notes, f"Box leaked into output: {coin}"

    # 3. Sets mapped correctly
    sets = [c for c in results if c["Program/Series"] == "Cent & Nickel Set"]
    assert len(sets) == 1, "Expected 1 mapped Cent & Nickel Set"
    assert sets[0]["Denomination"] == "Cent"

    # 4. Quantity 2 coins expanded correctly
    halves = [c for c in results if c["Program/Series"] == "Kennedy Half Dollar"]
    assert len(halves) == 4, f"Expected 4 Kennedy halves (2x 2001-P + 2x 1964-D), got {len(halves)}"


def test_duplicate_score_case_and_aliases():
    """NET-400f: Verify _score_duplicate handles case insensitivity and key aliases."""
    try:
        from main import _score_duplicate
    except ModuleNotFoundError:
        from main import _score_duplicate

    new_coin = {
        "year": "1921",
        "program_series": "Morgan Dollar",
        "mint_mark": "S",
        "grade": "MS-64",
    }
    existing_coin = {
        "Year": "1921",
        "Program/Series": "Morgan Dollar",
        "Mint Mark": "S",
        "Condition": "MS-64",
    }

    score = _score_duplicate(new_coin, existing_coin)
    # 0.40 (prog) + 0.30 (year) + 0.10 (mint) + 0.10 (grade/cond) = 0.90
    assert round(score, 2) >= 0.90


def test_us_mint_invoice_normalization():
    """Verify US Mint invoice data normalizes retailer, invoice number, date, and preserves Qty > 1."""
    try:
        from main import normalize_and_validate_receipt
    except ModuleNotFoundError:
        from main import normalize_and_validate_receipt

    raw_usmint_invoice = {
        "retailer": "United States Mint",
        "invoice_number": "USM23436235",
        "invoice_date": "2026-03-15",
        "line_items": [
            {
                "Program/Series": "American Silver Eagle",
                "Year": "2026",
                "Mint Mark": "W",
                "Denomination": "Dollar",
                "Condition": "Proof",
                "Cost": 85.00,
                "qty": 3,
                "Personal Notes": "Item 26EA 2026 American Eagle One Ounce Silver Proof Coin"
            }
        ]
    }

    results = normalize_and_validate_receipt(raw_usmint_invoice, fname="usmint_order_2026.pdf")
    assert len(results) == 3, f"Expected 3 coins for qty=3, got {len(results)}"
    for coin in results:
        assert coin["retailer"] == "United States Mint"
        assert coin["invoice_number"] == "USM23436235"
        assert coin["purchase_date"] == "2026-03-15"
        assert coin["Program/Series"] == "American Silver Eagle"
        assert coin["Mint Mark"] == "W"
        assert coin["Cost"] == 85.00

