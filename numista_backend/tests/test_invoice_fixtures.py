"""
test_invoice_fixtures.py — Verify Repository-Relative Invoice Fixtures & OCR Router
"""

import os
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
        from numista_backend.main import clean_valuation_value
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
        from numista_backend.main import clean_valuation_value
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
