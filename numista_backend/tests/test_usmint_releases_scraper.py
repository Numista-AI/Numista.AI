import pytest
from unittest.mock import MagicMock, patch
from services.usmint_releases_scraper import (
    parse_price,
    badge_to_status,
    load_local_catalog,
    _normalize_product,
    _detect_changes,
    get_mint_issue_price,
    get_upcoming_products,
    get_all_products,
)

def test_parse_price_valid():
    assert parse_price("$169.00") == 169.0
    assert parse_price("$1,250.50") == 1250.5
    assert parse_price("5740") == 5740.0
    assert parse_price(" $24.95 ") == 24.95

def test_parse_price_invalid_and_empty():
    assert parse_price("TBD") is None
    assert parse_price("N/A") is None
    assert parse_price("PENDING") is None
    assert parse_price("") is None
    assert parse_price(None) is None

def test_badge_to_status():
    assert badge_to_status("New") == "Available"
    assert badge_to_status("NewLimited") == "Available"
    assert badge_to_status("Coming Soon") == "Coming Soon"
    assert badge_to_status("Coming SoonLimited") == "Coming Soon"
    assert badge_to_status("Pre-Order") == "Pre-Order"
    assert badge_to_status("LimitedPre-Order") == "Pre-Order"
    assert badge_to_status("Sold Out") == "Sold Out"
    assert badge_to_status("") == "Available"
    assert badge_to_status(None) == "Available"

def test_load_local_catalog():
    items = load_local_catalog()
    assert isinstance(items, list)
    assert len(items) > 0
    # First item check
    first = items[0]
    assert "item_number" in first
    assert "title" in first
    assert "price" in first

def test_normalize_product():
    raw_item = {
        "item_number": "26XE",
        "title": "Morgan Silver Dollar 2026 Enhanced Uncirculated Coin",
        "price": "$169.00",
        "badge": "NewLimited",
        "url": "https://www.usmint.gov/test.html",
        "images": ["https://storage.googleapis.com/test.jpg"]
    }
    normalized = _normalize_product(raw_item)
    assert normalized["item_number"] == "26XE"
    assert normalized["price"] == "$169.00"
    assert normalized["price_numeric"] == 169.0
    assert normalized["status"] == "Available"
    assert normalized["image_url"] == "https://storage.googleapis.com/test.jpg"
    assert normalized["category"] == "coin"

def test_detect_changes():
    existing = {
        "price": "$169.00",
        "status": "Coming Soon",
        "badge": "Coming Soon",
        "release_date": "Spring 2026",
        "mintage_limit": 50000
    }
    incoming = {
        "price": "$175.00",
        "status": "Available",
        "badge": "New",
        "release_date": "Spring 2026",
        "mintage_limit": 50000
    }
    changes = _detect_changes(existing, incoming)
    assert "price" in changes
    assert changes["price"] == ("$169.00", "$175.00")
    assert "status" in changes
    assert changes["status"] == ("Coming Soon", "Available")
    assert "badge" in changes
    assert "release_date" not in changes
    assert "mintage_limit" not in changes

def test_get_mint_issue_price_exact_item():
    mock_db = MagicMock()
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "title": "Morgan Silver Dollar 2026 Enhanced Uncirculated Coin",
        "price": "$169.00"
    }
    mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

    price = get_mint_issue_price(
        db=mock_db,
        year="2026",
        denomination="Dollar",
        item_number="26XE"
    )
    assert price == 169.0

def test_get_mint_issue_price_fuzzy_search():
    mock_db = MagicMock()
    mock_item_doc = MagicMock()
    mock_item_doc.exists = False
    mock_db.collection.return_value.document.return_value.get.return_value = mock_item_doc

    doc1 = MagicMock()
    doc1.to_dict.return_value = {
        "title": "Morgan Silver Dollar 2026 Reverse Proof Coin",
        "price": "$173.00"
    }
    doc2 = MagicMock()
    doc2.to_dict.return_value = {
        "title": "American Eagle 2026 One Ounce Gold Proof Coin",
        "price": "$5,450.00"
    }
    mock_db.collection.return_value.stream.return_value = [doc1, doc2]

    price = get_mint_issue_price(
        db=mock_db,
        year="2026",
        denomination="Dollar",
        mint_mark="S",
        theme="Morgan"
    )
    assert price == 173.0

def test_get_mint_issue_price_ignores_non_20xx():
    mock_db = MagicMock()
    price = get_mint_issue_price(
        db=mock_db,
        year="1921",
        denomination="Dollar",
        item_number="1921_MORGAN"
    )
    assert price is None
