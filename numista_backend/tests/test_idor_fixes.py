"""
numista_backend/tests/test_idor_fixes.py
----------------------------------------
Unit tests for IDOR and security parameter boundary fixes:
1. GET /api/portfolio/snapshot IDOR enforcement (caller token uid vs query user_id)
2. POST /api/v1/estate/generate-attorney-link valid_days capping (clamped between 1 and 30 days)
3. P4 ownership checks on 20 additional Category-2 routes
"""

import io
import os
import datetime
from datetime import timezone
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

from main import app
from routes.deps import get_current_user


@pytest.fixture(autouse=True)
def clean_deps():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


# ── Helpers ──────────────────────────────────────────────────────────────────

def _user_a():
    return {"uid": "user_A", "email": "user_a@example.com", "admin": False}

def _user_b():
    return {"uid": "user_B", "email": "user_b@example.com", "admin": False}

def _admin_user():
    return {"uid": "admin_uid", "email": "admin@numista.ai", "admin": True}


# ═══════════════════════════════════════════════════════════════════════════════
# 1. GET /api/portfolio/snapshot  (ORIGINAL TESTS)
# ═══════════════════════════════════════════════════════════════════════════════

def test_portfolio_snapshot_token_a_query_a_returns_200():
    """Token A + query user_id=A -> 200."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    with patch("main.db") as mock_db:
        mock_user_doc = MagicMock()
        mock_hist_coll = MagicMock()
        mock_order = MagicMock()
        mock_order.get.return_value = []
        mock_hist_coll.order_by.return_value = mock_order
        mock_user_doc.collection.return_value = mock_hist_coll
        mock_db.collection.return_value.document.return_value = mock_user_doc

        resp = client.get("/api/portfolio/snapshot?user_id=user_A")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)


def test_portfolio_snapshot_token_a_query_b_returns_403():
    """Token A + query user_id=B -> 403."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/api/portfolio/snapshot?user_id=user_B")
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Forbidden"


def test_portfolio_snapshot_no_token_returns_401():
    """No token -> 401."""
    old_k = os.environ.get("K_SERVICE")
    os.environ["K_SERVICE"] = "numista-backend-test-env"
    try:
        client = TestClient(app, raise_server_exceptions=False)
        with patch("routes.deps.verify_firebase_bearer_token", return_value=None):
            resp = client.get("/api/portfolio/snapshot?user_id=user_A")
            assert resp.status_code == 401
    finally:
        if old_k is None:
            os.environ.pop("K_SERVICE", None)
        else:
            os.environ["K_SERVICE"] = old_k


# ═══════════════════════════════════════════════════════════════════════════════
# 2. POST /api/v1/estate/generate-attorney-link (ORIGINAL TESTS)
# ═══════════════════════════════════════════════════════════════════════════════

def test_estate_valid_days_90_capped_to_30():
    """valid_days=90 -> capped to 30."""
    app.dependency_overrides[get_current_user] = lambda: {
        "uid": "owner_123",
        "email": "owner@example.com",
        "admin": False,
    }
    client = TestClient(app, raise_server_exceptions=False)
    with patch("routes.estate_routes.db") as mock_db:
        mock_user_ref = MagicMock()
        mock_user_ref.collection.return_value.get.return_value = []
        mock_db.collection.return_value.document.return_value = mock_user_ref

        now_before = datetime.datetime.now(timezone.utc)
        resp = client.post(
            "/api/v1/estate/generate-attorney-link",
            json={"owner_uid": "owner_123", "valid_days": 90},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "expires_at" in body
        exp_dt = datetime.datetime.fromisoformat(body["expires_at"].replace("Z", "+00:00"))

        max_expected = now_before + datetime.timedelta(days=30, seconds=10)
        min_expected = now_before + datetime.timedelta(days=29, hours=23)
        assert exp_dt <= max_expected
        assert exp_dt >= min_expected


def test_estate_valid_days_0_capped_to_1():
    """valid_days=0 -> capped to 1."""
    app.dependency_overrides[get_current_user] = lambda: {
        "uid": "owner_123",
        "email": "owner@example.com",
        "admin": False,
    }
    client = TestClient(app, raise_server_exceptions=False)
    with patch("routes.estate_routes.db") as mock_db:
        mock_user_ref = MagicMock()
        mock_user_ref.collection.return_value.get.return_value = []
        mock_db.collection.return_value.document.return_value = mock_user_ref

        now_before = datetime.datetime.now(timezone.utc)
        resp = client.post(
            "/api/v1/estate/generate-attorney-link",
            json={"owner_uid": "owner_123", "valid_days": 0},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "expires_at" in body
        exp_dt = datetime.datetime.fromisoformat(body["expires_at"].replace("Z", "+00:00"))

        max_expected = now_before + datetime.timedelta(days=1, seconds=10)
        min_expected = now_before + datetime.timedelta(hours=23)
        assert exp_dt <= max_expected
        assert exp_dt >= min_expected


# ═══════════════════════════════════════════════════════════════════════════════
# 3. POST /api/nicknames/submit — P4 ownership check
# ═══════════════════════════════════════════════════════════════════════════════

def test_nicknames_submit_token_a_email_b_returns_403():
    """Token A submitting as user_b email -> 403."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post(
        "/api/nicknames/submit",
        data={
            "user_email": "user_b@example.com",
            "nickname": "Barber",
            "maps_to": "Barber Quarter",
        },
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Forbidden"


def test_nicknames_submit_token_a_email_a_passes_check():
    """Token A submitting as user_a email -> passes ownership check (may succeed or fail for other reasons)."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    with patch("main.db") as mock_db:
        # Mock Firestore so it doesn't fail on network calls
        mock_coll = MagicMock()
        mock_coll.where.return_value.limit.return_value.get.return_value = []
        mock_coll.document.return_value.get.return_value = MagicMock(exists=False)
        mock_coll.document.return_value.set.return_value = None
        mock_db.collection.return_value = mock_coll

        resp = client.post(
            "/api/nicknames/submit",
            data={
                "user_email": "user_a@example.com",
                "nickname": "Barber",
                "maps_to": "Barber Quarter",
            },
        )
        # Not 403 — ownership check passed
        assert resp.status_code != 403


# ═══════════════════════════════════════════════════════════════════════════════
# 4. POST /api/nicknames/{doc_id}/vote — P4 ownership check
# ═══════════════════════════════════════════════════════════════════════════════

def test_nicknames_vote_token_a_email_b_returns_403():
    """Token A voting as user_b -> 403."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post(
        "/api/nicknames/doc123/vote",
        data={"user_email": "user_b@example.com", "rating": "4"},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Forbidden"


# ═══════════════════════════════════════════════════════════════════════════════
# 5. POST /api/process_invoice — P4 ownership check
# ═══════════════════════════════════════════════════════════════════════════════

def test_process_invoice_token_a_email_b_returns_403():
    """Token A uploading invoice for user_b -> 403."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    dummy_file = io.BytesIO(b"%PDF-1.4 fake content")
    resp = client.post(
        "/api/process_invoice",
        data={"user_email": "user_b@example.com"},
        files={"file": ("invoice.pdf", dummy_file, "application/pdf")},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Forbidden"


# ═══════════════════════════════════════════════════════════════════════════════
# 6. GET /api/coin_crop — P4 ownership check
# ═══════════════════════════════════════════════════════════════════════════════

def test_coin_crop_token_a_email_b_returns_403():
    """Token A requesting crop for user_b -> 403."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/api/coin_crop?coin_id=coin123&user_email=user_b@example.com")
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Forbidden"


# ═══════════════════════════════════════════════════════════════════════════════
# 7. POST /api/analyze_checklist — P4 ownership check
# ═══════════════════════════════════════════════════════════════════════════════

def test_analyze_checklist_token_a_email_b_returns_403():
    """Token A analyzing checklist for user_b -> 403."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    dummy_file = io.BytesIO(b"fake checklist content")
    resp = client.post(
        "/api/analyze_checklist",
        data={"user_email": "user_b@example.com"},
        files={"files": ("checklist.pdf", dummy_file, "application/pdf")},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Forbidden"


# ═══════════════════════════════════════════════════════════════════════════════
# 8. GET /api/binder_scans/{user_email} — P4 ownership check
# ═══════════════════════════════════════════════════════════════════════════════

def test_list_binder_scans_token_a_email_b_returns_403():
    """Token A requesting binder scans for user_b -> 403."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/api/binder_scans/user_b@example.com")
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Forbidden"


def test_list_binder_scans_token_a_email_a_returns_not_403():
    """Token A requesting own binder scans -> passes ownership check."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    with patch("main.db") as mock_db:
        mock_db.collection.return_value.document.return_value.collection.return_value.order_by.return_value.get.return_value = []
        resp = client.get("/api/binder_scans/user_a@example.com")
        assert resp.status_code != 403


# ═══════════════════════════════════════════════════════════════════════════════
# 9. GET /api/binder_scans/{user_email}/{binder_id} — P4 ownership check
# ═══════════════════════════════════════════════════════════════════════════════

def test_get_binder_detail_token_a_email_b_returns_403():
    """Token A requesting binder detail for user_b -> 403."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/api/binder_scans/user_b@example.com/binder_001")
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Forbidden"


# ═══════════════════════════════════════════════════════════════════════════════
# 10. POST /api/import/upload — P4 ownership check
# ═══════════════════════════════════════════════════════════════════════════════

def test_import_upload_token_a_email_b_returns_403():
    """Token A uploading import file for user_b -> 403."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    dummy_file = io.BytesIO(b"fake csv content")
    resp = client.post(
        "/api/import/upload",
        data={"user_email": "user_b@example.com", "session_id": "sess_001"},
        files={"file": ("coins.csv", dummy_file, "text/csv")},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Forbidden"


# ═══════════════════════════════════════════════════════════════════════════════
# 11. GET /api/import/status/{session_id} — P4 ownership check
# ═══════════════════════════════════════════════════════════════════════════════

def test_import_status_token_a_email_b_returns_403():
    """Token A requesting import status for user_b -> 403."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/api/import/status/sess_001?user_email=user_b@example.com")
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Forbidden"


# ═══════════════════════════════════════════════════════════════════════════════
# 12. GET /api/receipts/{user_email} — P4 ownership check via _authenticate_request
# ═══════════════════════════════════════════════════════════════════════════════

def test_list_receipts_token_a_email_b_returns_403():
    """Token A listing receipts for user_b -> 403."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/api/receipts/user_b@example.com")
    assert resp.status_code == 403


def test_list_receipts_token_a_email_a_returns_not_403():
    """Token A listing own receipts -> passes ownership check."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    with patch("main.db") as mock_db:
        mock_col = MagicMock()
        mock_col.order_by.return_value.limit.return_value.stream.return_value = iter([])
        mock_db.collection.return_value.document.return_value.collection.return_value = mock_col
        resp = client.get("/api/receipts/user_a@example.com")
        assert resp.status_code != 403


# ═══════════════════════════════════════════════════════════════════════════════
# 13. DELETE /api/receipts/{user_email}/{receipt_id} — P4 ownership check
# ═══════════════════════════════════════════════════════════════════════════════

def test_delete_receipt_token_a_email_b_returns_403():
    """Token A deleting receipt for user_b -> 403."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.delete("/api/receipts/user_b@example.com/rcpt_001")
    assert resp.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# 14. GET /api/receipts/{user_email}/{receipt_id}/view_url — P4 ownership check
# ═══════════════════════════════════════════════════════════════════════════════

def test_receipt_view_url_token_a_email_b_returns_403():
    """Token A requesting view URL for user_b receipt -> 403."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/api/receipts/user_b@example.com/rcpt_001/view_url")
    assert resp.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# 15. GET /api/receipts/{user_email}/{receipt_id}/stream — P4 ownership check
# ═══════════════════════════════════════════════════════════════════════════════

def test_receipt_stream_token_a_email_b_returns_403():
    """Token A streaming receipt for user_b -> 403."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/api/receipts/user_b@example.com/rcpt_001/stream")
    assert resp.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# 16. GET /api/collection/count — P4 ownership check via _authenticate_request
# ═══════════════════════════════════════════════════════════════════════════════

def test_collection_count_token_a_email_b_returns_403():
    """Token A requesting collection count for user_b -> 403."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/api/collection/count?user_email=user_b@example.com")
    assert resp.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# 17. GET /api/wishlist/deals/{user_email} — P4 ownership check
# ═══════════════════════════════════════════════════════════════════════════════

def test_wishlist_deals_token_a_email_b_returns_403():
    """Token A requesting wishlist deals for user_b -> 403."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/api/wishlist/deals/user_b@example.com")
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Forbidden"


def test_wishlist_deals_admin_can_access_any_user():
    """Admin token can request wishlist deals for any user."""
    app.dependency_overrides[get_current_user] = lambda: _admin_user()
    client = TestClient(app, raise_server_exceptions=False)
    with patch("main.db"):
        with patch("services.deal_spotter_service.DealSpotterService") as mock_svc:
            mock_svc.return_value.match_wishlist_items.return_value = []
            resp = client.get("/api/wishlist/deals/user_b@example.com")
            # Admin bypasses ownership check
            assert resp.status_code != 403


# ═══════════════════════════════════════════════════════════════════════════════
# 18. GET /api/transfer/sold-items/{user_id} — P4 ownership check via _authenticate_request
# ═══════════════════════════════════════════════════════════════════════════════

def test_sold_items_token_a_user_b_returns_403():
    """Token A requesting sold items for user_b -> 403."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/api/transfer/sold-items/user_b@example.com")
    assert resp.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# 19. GET /api/estate/generate-appraisal-url — P4 ownership check
# ═══════════════════════════════════════════════════════════════════════════════

def test_estate_appraisal_url_token_a_email_b_returns_403():
    """Token A generating estate appraisal URL for user_b -> 403."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/api/estate/generate-appraisal-url?user_email=user_b@example.com")
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Forbidden"


def test_estate_appraisal_url_token_a_email_a_not_403():
    """Token A generating estate appraisal URL for own email -> passes ownership check."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    with patch("main.db") as mock_db:
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.set.return_value = None
        with patch("main.pd") as mock_pd:
            mock_pd.Timedelta.return_value = datetime.timedelta(days=7)
            resp = client.get("/api/estate/generate-appraisal-url?user_email=user_a@example.com")
            assert resp.status_code != 403


# ═══════════════════════════════════════════════════════════════════════════════
# 20. GET /api/payment/subscription-status — P4 ownership check
# ═══════════════════════════════════════════════════════════════════════════════

def test_subscription_status_token_a_uid_b_returns_403():
    """Token A requesting subscription status for user_b uid -> 403."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/api/stripe/subscription-status?uid=user_B")
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Forbidden"


def test_subscription_status_token_a_uid_a_not_403():
    """Token A requesting own subscription status -> passes ownership check."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    with patch("routes.payment_routes.get_user_profile", return_value={}):
        with patch("routes.payment_routes.get_user_tier", return_value="free"):
            with patch("routes.payment_routes.get_coin_count", return_value=0):
                resp = client.get("/api/stripe/subscription-status?uid=user_A")
                assert resp.status_code != 403


# ═══════════════════════════════════════════════════════════════════════════════
# 21. GET /api/attorney/snapshot — P4 ownership check
# ═══════════════════════════════════════════════════════════════════════════════

def test_attorney_snapshot_token_a_uid_b_returns_403():
    """Token A requesting attorney snapshot for uid=user_B -> 403."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    with patch("routes.attorney_routes.db") as mock_db:
        # Simulate a valid token doc for user_B
        mock_snap = MagicMock()
        mock_snap.exists = True
        mock_snap.to_dict.return_value = {
            "uid": "user_B",
            "user_email": "user_b@example.com",
            "is_revoked": False,
            "is_one_time": False,
            "redeemed_at": None,
            "expires_at": None,
        }
        mock_db.collection.return_value.document.return_value.get.return_value = mock_snap
        resp = client.get("/api/attorney/snapshot?uid=user_B&token=abc123fake456789abc123fake456789")
        assert resp.status_code == 403


def test_attorney_snapshot_token_a_uid_a_not_403():
    """Token A requesting attorney snapshot for own uid=user_A -> passes ownership check."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    with patch("routes.attorney_routes.db") as mock_db:
        mock_snap = MagicMock()
        mock_snap.exists = True
        mock_snap.to_dict.return_value = {
            "uid": "user_A",
            "user_email": "user_a@example.com",
            "is_revoked": False,
            "is_one_time": False,
            "redeemed_at": None,
            "expires_at": None,
        }
        # mock coins collection
        mock_coins_snap = MagicMock()
        mock_coins_snap.exists = True
        coins_doc = MagicMock()
        coins_doc.to_dict.return_value = {}
        mock_db.collection.return_value.document.return_value.get.return_value = mock_snap
        mock_db.collection.return_value.document.return_value.collection.return_value.stream.return_value = iter([])
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.update.return_value = None
        resp = client.get("/api/attorney/snapshot?uid=user_A&token=abc123fake456789abc123fake456789")
        # Should not be 403 (may be 200 or other non-403)
        assert resp.status_code != 403


# ═══════════════════════════════════════════════════════════════════════════════
# 22. POST /api/identify_group_photo — P4 ownership check via _authenticate_request
# ═══════════════════════════════════════════════════════════════════════════════

def test_identify_group_photo_token_a_email_b_returns_403():
    """Token A identifying group photo for user_b -> 403."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    dummy_image = io.BytesIO(b"\xff\xd8\xff fake jpeg")
    resp = client.post(
        "/api/identify_group_photo",
        data={"user_email": "user_b@example.com"},
        files={"image": ("photo.jpg", dummy_image, "image/jpeg")},
    )
    assert resp.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# 23. POST /api/identify_coin_photo — P4 ownership check via _authenticate_request
# ═══════════════════════════════════════════════════════════════════════════════

def test_identify_coin_photo_token_a_email_b_returns_403():
    """Token A identifying coin photo for user_b -> 403."""
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    dummy_image = io.BytesIO(b"\xff\xd8\xff fake jpeg")
    resp = client.post(
        "/api/identify_coin_photo",
        data={"user_email": "user_b@example.com", "save_to_collection": "false"},
        files={"image_a": ("obverse.jpg", dummy_image, "image/jpeg")},
    )
    assert resp.status_code == 403
