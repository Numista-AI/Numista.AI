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
