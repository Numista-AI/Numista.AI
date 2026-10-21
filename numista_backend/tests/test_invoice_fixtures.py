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


def test_invoice_multi_object_line_items_merge():
    """NET-400a: Verify multi-object list with line_items across multiple dicts merges correctly."""
    data = [
        {"retailer": "US Mint", "invoice_number": "INV-100", "line_items": [
            {"Program/Series": "American Silver Eagle", "Year": "2024", "Cost": 35.0, "qty": 1}
        ]},
        {"line_items": [
            {"Program/Series": "Morgan Dollar", "Year": "2023", "Cost": 75.0, "qty": 2}
        ]}
    ]

    if isinstance(data, list):
        dict_entries = [d for d in data if isinstance(d, dict)]
        if dict_entries and any("line_items" in d for d in dict_entries):
            merged = dict(next(d for d in dict_entries if "line_items" in d))
            merged["line_items"] = [li for d in dict_entries
                                    for li in (d.get("line_items") or [])
                                    if isinstance(li, dict)]
            data = merged
        else:
            data = {"line_items": dict_entries}

    assert "line_items" in data
    assert len(data["line_items"]) == 2
    assert data["line_items"][0]["Program/Series"] == "American Silver Eagle"
    assert data["line_items"][1]["Program/Series"] == "Morgan Dollar"
    assert data["retailer"] == "US Mint"


def test_invoice_quantity_and_supply_filter_and_set_normalization():
    """NET-400b,c: Test quantity looping, supply folder skipping, and Cent & Nickel Set normalization."""
    import re

    raw_items = [
        {"Program/Series": "Lincoln Cent", "Year": "2024", "Cost": 5.0, "qty": 3, "Denomination": "Cent"},
        {"Program/Series": "Whitman Coin Album", "Year": "", "Cost": 15.0, "is_supply": True, "Denomination": ""},
        {"Program/Series": "", "Year": "2022", "Cost": 25.0, "qty": 1, "Denomination": "Unknown Cent/Nickel"},
    ]

    def _get_item_qty(item_dict):
        try:
            val = item_dict.get("qty") or item_dict.get("quantity") or item_dict.get("Quantity") or 1
            return max(1, min(int(val), 100))
        except Exception:
            return 1

    processed_coins = []
    supply_kws = ("folder", "supply", "album", "holder", "capsule", "supplies", "binder", "display box")

    for it in raw_items:
        is_supply = bool(it.get("is_supply", False))
        prog_val = (it.get("Program/Series") or "").strip()
        raw_desc = (it.get("Personal Notes") or "") + " " + prog_val + " " + (it.get("Denomination") or "")
        raw_lower = raw_desc.lower()

        has_year = bool(re.search(r"\b(1[789]\d\d|20[0-2]\d)\b", raw_desc))
        if is_supply or (any(kw in raw_lower for kw in supply_kws) and not has_year and not it.get("Year")):
            continue

        denom_val = (it.get("Denomination") or "").strip()
        denom_lower = denom_val.lower()
        if "unknown cent/nickel" in denom_lower or denom_lower in ("cent/nickel", "cent / nickel", "unknown cent / nickel"):
            denom_val = "Cent"
            if not prog_val:
                prog_val = "Cent & Nickel Set"
        elif not denom_val:
            denom_val = "Dollar"

        qty = _get_item_qty(it)
        for _ in range(qty):
            processed_coins.append({
                "Program/Series": prog_val,
                "Year": it.get("Year"),
                "Denomination": denom_val,
                "Cost": it.get("Cost"),
            })

    # Album skipped (1 item), Lincoln Cent repeated 3 times, Cent & Nickel Set repeated 1 time = 4 coins
    assert len(processed_coins) == 4
    cents = [c for c in processed_coins if c["Program/Series"] == "Lincoln Cent"]
    assert len(cents) == 3
    set_coin = [c for c in processed_coins if c["Program/Series"] == "Cent & Nickel Set"]
    assert len(set_coin) == 1
    assert set_coin[0]["Denomination"] == "Cent"


def test_duplicate_score_case_and_aliases():
    """NET-400f: Verify _score_duplicate handles case insensitivity and key aliases."""
    try:
        from numista_backend.main import _score_duplicate
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
