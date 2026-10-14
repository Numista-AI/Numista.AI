"""
numista_backend/tests/test_idor_fixes.py
----------------------------------------
Unit tests for IDOR and security parameter boundary fixes:
1. GET /api/portfolio/snapshot IDOR enforcement (caller token uid vs query user_id)
2. POST /api/v1/estate/generate-attorney-link valid_days capping (clamped between 1 and 30 days)
"""

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


def test_portfolio_snapshot_token_a_query_a_returns_200():
    """Token A + query user_id=A -> 200."""
    app.dependency_overrides[get_current_user] = lambda: {
        "uid": "user_A",
        "email": "user_a@example.com",
        "admin": False,
    }
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
        assert len(data) >= 1
        assert data[0]["totalValue"] == 0.0


def test_portfolio_snapshot_token_a_query_b_returns_403():
    """Token A + query user_id=B -> 403."""
    app.dependency_overrides[get_current_user] = lambda: {
        "uid": "user_A",
        "email": "user_a@example.com",
        "admin": False,
    }
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/api/portfolio/snapshot?user_id=user_B")
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Forbidden"


def test_portfolio_snapshot_no_token_returns_401():
    """No token -> 401."""
    # Ensure production mode so default-deny middleware enforces 401
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
