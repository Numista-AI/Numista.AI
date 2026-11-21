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


def test_normalize_product_filters_blank_and_non_string_images():
    raw_item = {
        "item_number": "26XE",
        "title": "Morgan Silver Dollar",
        "price": "$169.00",
        "badge": "New",
        "images": ["  ", None, 123, " https://storage.googleapis.com/a.jpg ", ""],
    }
    normalized = _normalize_product(raw_item)
    assert normalized["image_url"] == "https://storage.googleapis.com/a.jpg"
    assert normalized["image_urls"] == ["https://storage.googleapis.com/a.jpg"]

    raw_empty = {
        "item_number": "26XX",
        "title": "No Image Coin",
        "price": "$50.00",
        "badge": "Coming Soon",
        "images": ["", "   ", None],
    }
    normalized_empty = _normalize_product(raw_empty)
    assert normalized_empty["image_url"] is None
    assert normalized_empty["image_urls"] == []


def test_detect_changes_tracks_image_fields():
    existing = {
        "price": "$169.00",
        "status": "Coming Soon",
        "badge": "Coming Soon",
        "release_date": "Spring 2026",
        "mintage_limit": 50000,
        "image_url": None,
        "image_urls": [],
    }
    incoming = {
        "price": "$169.00",
        "status": "Coming Soon",
        "badge": "Coming Soon",
        "release_date": "Spring 2026",
        "mintage_limit": 50000,
        "image_url": "https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XE_image_1.jpg",
        "image_urls": ["https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XE_image_1.jpg"],
    }
    changes = _detect_changes(existing, incoming)
    assert "image_url" in changes
    assert changes["image_url"][0] is None
    assert "image_urls" in changes


def test_sync_upcoming_releases_without_usmint_gov():
    from services.usmint_releases_scraper import sync_upcoming_releases

    written_docs = {}

    def make_doc_ref(item_number):
        ref = MagicMock()
        existing_snap = MagicMock()
        existing_snap.exists = False
        ref.get.return_value = existing_snap
        ref.set.side_effect = lambda data: written_docs.__setitem__(item_number, data)
        return ref

    mock_db = MagicMock()
    releases_coll = MagicMock()
    releases_coll.document.side_effect = make_doc_ref
    changelog_coll = MagicMock()

    def collection_router(name):
        if name == "usmint_upcoming_releases":
            return releases_coll
        if name == "usmint_release_changelog":
            return changelog_coll
        return MagicMock()

    mock_db.collection.side_effect = collection_router

    with patch("services.usmint_releases_scraper.scrape_product_schedule", return_value=[]):
        report = sync_upcoming_releases(mock_db)

    assert len(report["new"]) == 74
    assert len(report["errors"]) == 0
    assert len(written_docs) == 74

    gcs_prefix = "https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/"
    with_images = [d for d in written_docs.values() if d.get("image_url")]
    assert len(with_images) == 22
    assert all(d["image_url"].startswith(gcs_prefix) for d in with_images)


def test_sync_mint_releases_endpoint_p5_auth_and_capture(monkeypatch):
    import os
    from fastapi.testclient import TestClient

    monkeypatch.setenv("K_SERVICE", "numista-backend-test-env")
    mock_app = MagicMock()
    mock_fs = MagicMock()

    def fake_verify(token, *args, **kwargs):
        if token == "admin-test-token":
            return {"uid": "admin1", "email": "admin@example.com", "admin": True}
        if token == "user-test-token":
            return {"uid": "user1", "email": "user@example.com"}
        raise Exception("invalid token")

    with patch("firebase_admin._apps", {"[DEFAULT]": mock_app, "default": mock_app}), \
         patch("firebase_admin.get_app", return_value=mock_app), \
         patch("firebase_admin.firestore.client", return_value=mock_fs), \
         patch("firebase_admin.auth.verify_id_token", side_effect=fake_verify), \
         patch("firebase_admin.credentials.Certificate", MagicMock()), \
         patch("firebase_admin.initialize_app", MagicMock()), \
         patch("google.cloud.firestore.Client", MagicMock()), \
         patch("google.cloud.storage.Client", MagicMock()), \
         patch("google.genai.Client", MagicMock()), \
         patch("stripe.api_key", "sk_test_dummy"):
        import main as _main_module

        captured_requests = []
        original_app = _main_module.app

        class CaptureMiddleware:
            def __init__(self, app):
                self.app = app

            async def __call__(self, scope, receive, send):
                if scope["type"] == "http" and scope["path"] == "/api/cron/sync-mint-releases":
                    headers = {k.decode("latin1").lower(): v.decode("latin1") for k, v in scope.get("headers", [])}
                    captured_requests.append({
                        "method": scope["method"],
                        "path": scope["path"],
                        "authorization": headers.get("authorization"),
                    })
                await self.app(scope, receive, send)

        client = TestClient(CaptureMiddleware(original_app), raise_server_exceptions=False)

        # 1. Missing Authorization header -> 401
        r_unauth = client.post("/api/cron/sync-mint-releases")
        assert r_unauth.status_code == 401

        # 2. Non-admin token -> 403
        r_non_admin = client.post(
            "/api/cron/sync-mint-releases",
            headers={"Authorization": "Bearer user-test-token"},
        )
        assert r_non_admin.status_code == 403

        # 3. Admin token -> 200, zero live Firestore writes
        fake_report = {"new": ["26XE"], "updated": [], "unchanged": 73, "errors": []}
        with patch("services.usmint_releases_scraper.sync_upcoming_releases", return_value=fake_report) as mock_sync:
            r_admin = client.post(
                "/api/cron/sync-mint-releases",
                headers={"Authorization": "Bearer admin-test-token"},
            )
        assert r_admin.status_code == 200
        assert r_admin.json()["status"] == "completed"
        assert r_admin.json()["report"] == fake_report
        mock_sync.assert_called_once()

        # Verify P5 captured request details
        assert len(captured_requests) == 3
        admin_req = captured_requests[-1]
        assert admin_req["method"] == "POST"
        assert admin_req["path"] == "/api/cron/sync-mint-releases"
        assert admin_req["authorization"] == "Bearer admin-test-token"
