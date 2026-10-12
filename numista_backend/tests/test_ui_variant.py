"""
numista_backend/tests/test_ui_variant.py
----------------------------------------
Unit tests for REQ_032B UI variant endpoint gating (Phase A):
- POST /api/admin/set_ui_variant (auth, admin-claim gating, variant validation, Firestore write/delete)
- GET /api/user/ui_variant (auth, default fallback, allowlist Phase A check, degrade behavior)
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app, PHASE_A_ALLOWLIST
from routes.deps import get_current_user, require_admin_user


# ─── Auth Helpers ─────────────────────────────────────────────────────────────

def _user_auth(uid="uid_alice", email="alice@example.com", is_admin=False):
    async def _dependency():
        return {
            "uid": uid,
            "user_id": uid,
            "email": email,
            "admin": is_admin,
            "firebase": {"sign_in_provider": "password"}
        }
    return _dependency

def _unauthenticated():
    async def _dependency():
        raise HTTPException(status_code=401, detail="Authentication token missing or invalid")
    return _dependency


@pytest.fixture(autouse=True)
def cleanup_overrides():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


# ─── Admin Endpoint Tests ─────────────────────────────────────────────────────

def test_admin_set_ui_variant_unauthenticated():
    """Unauthenticated call to /api/admin/set_ui_variant returns 401."""
    app.dependency_overrides[get_current_user] = _unauthenticated()
    client = TestClient(app)
    resp = client.post("/api/admin/set_ui_variant", json={"target_email": "test@example.com", "variant": "alt"})
    assert resp.status_code == 401


def test_admin_set_ui_variant_non_admin_forbidden():
    """Non-admin authenticated user receives 403 on /api/admin/set_ui_variant."""
    app.dependency_overrides[get_current_user] = _user_auth(email="normal@example.com", is_admin=False)
    client = TestClient(app)
    resp = client.post("/api/admin/set_ui_variant", json={"target_email": "target@example.com", "variant": "alt"})
    assert resp.status_code == 403


def test_admin_set_ui_variant_invalid_variant():
    """Admin providing invalid variant (not classic, alt, or null) receives 400."""
    app.dependency_overrides[require_admin_user] = _user_auth(email="admin@numista.ai", is_admin=True)
    client = TestClient(app)
    resp = client.post("/api/admin/set_ui_variant", json={"target_email": "target@example.com", "variant": "beta_invalid"})
    assert resp.status_code == 400
    assert "variant must be 'classic', 'alt', or null" in resp.json()["detail"]


@patch("main.db")
def test_admin_set_ui_variant_set_alt(mock_db):
    """Admin successfully sets variant to 'alt'."""
    app.dependency_overrides[require_admin_user] = _user_auth(email="admin@numista.ai", is_admin=True)
    mock_doc = MagicMock()
    mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value = mock_doc

    client = TestClient(app)
    resp = client.post("/api/admin/set_ui_variant", json={"target_email": "ERIC.SEAMAN@YAHOO.COM", "variant": "alt"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["target"] == "eric.seaman@yahoo.com"
    assert data["variant"] == "alt"

    mock_db.collection.assert_called_with("users")
    mock_db.collection().document.assert_called_with("eric.seaman@yahoo.com")
    mock_db.collection().document().collection.assert_called_with("settings")
    mock_db.collection().document().collection().document.assert_called_with("ui_variant")
    mock_doc.set.assert_called_once()
    set_args = mock_doc.set.call_args[0][0]
    assert set_args["variant"] == "alt"
    assert set_args["set_by"] == "admin"


@patch("main.db")
def test_admin_set_ui_variant_set_classic(mock_db):
    """Admin successfully sets variant to 'classic'."""
    app.dependency_overrides[require_admin_user] = _user_auth(email="admin@numista.ai", is_admin=True)
    mock_doc = MagicMock()
    mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value = mock_doc

    client = TestClient(app)
    resp = client.post("/api/admin/set_ui_variant", json={"target_email": "tester@example.com", "variant": "classic"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["target"] == "tester@example.com"
    assert data["variant"] == "classic"
    mock_doc.set.assert_called_once()


@patch("main.db")
def test_admin_set_ui_variant_reset_null(mock_db):
    """Admin resets variant with null/None -> doc deleted."""
    app.dependency_overrides[require_admin_user] = _user_auth(email="admin@numista.ai", is_admin=True)
    mock_doc = MagicMock()
    mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value = mock_doc

    client = TestClient(app)
    resp = client.post("/api/admin/set_ui_variant", json={"target_email": "tester@example.com", "variant": None})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["target"] == "tester@example.com"
    assert data["variant"] is None
    mock_doc.delete.assert_called_once()


# ─── User Endpoint Tests ──────────────────────────────────────────────────────

def test_get_ui_variant_unauthenticated():
    """Unauthenticated call to /api/user/ui_variant returns 401."""
    app.dependency_overrides[get_current_user] = _unauthenticated()
    client = TestClient(app)
    resp = client.get("/api/user/ui_variant")
    assert resp.status_code == 401


@patch("main.db")
def test_get_ui_variant_default_when_no_doc(mock_db):
    """When no settings/ui_variant doc exists, default 'classic' is returned."""
    app.dependency_overrides[get_current_user] = _user_auth(email="eric.seaman@yahoo.com")
    mock_doc_snap = MagicMock()
    mock_doc_snap.exists = False
    mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = mock_doc_snap

    client = TestClient(app)
    resp = client.get("/api/user/ui_variant")
    assert resp.status_code == 200
    assert resp.json() == {"variant": "classic"}


@patch("main.db")
def test_get_ui_variant_allowlist_user_gets_alt(mock_db):
    """Allowlist user eric.seaman@yahoo.com with doc variant='alt' gets 'alt'."""
    app.dependency_overrides[get_current_user] = _user_auth(email="eric.seaman@yahoo.com")
    mock_doc_snap = MagicMock()
    mock_doc_snap.exists = True
    mock_doc_snap.to_dict.return_value = {"variant": "alt"}
    mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = mock_doc_snap

    client = TestClient(app)
    resp = client.get("/api/user/ui_variant")
    assert resp.status_code == 200
    assert resp.json() == {"variant": "alt"}


@patch("main.db")
def test_get_ui_variant_second_allowlist_user_gets_alt(mock_db):
    """Allowlist user eric@numista.ai with doc variant='alt' gets 'alt'."""
    app.dependency_overrides[get_current_user] = _user_auth(email="ERIC@NUMISTA.AI")
    mock_doc_snap = MagicMock()
    mock_doc_snap.exists = True
    mock_doc_snap.to_dict.return_value = {"variant": "alt"}
    mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = mock_doc_snap

    client = TestClient(app)
    resp = client.get("/api/user/ui_variant")
    assert resp.status_code == 200
    assert resp.json() == {"variant": "alt"}


@patch("main.db")
def test_get_ui_variant_non_allowlist_user_degrades_to_classic(mock_db):
    """User NOT in Phase A allowlist with doc variant='alt' silently degrades to 'classic'."""
    app.dependency_overrides[get_current_user] = _user_auth(email="other_user@example.com")
    mock_doc_snap = MagicMock()
    mock_doc_snap.exists = True
    mock_doc_snap.to_dict.return_value = {"variant": "alt"}
    mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = mock_doc_snap

    client = TestClient(app)
    resp = client.get("/api/user/ui_variant")
    assert resp.status_code == 200
    assert resp.json() == {"variant": "classic"}


@patch("main.db")
def test_get_ui_variant_classic_doc_returns_classic(mock_db):
    """User with doc variant='classic' gets 'classic'."""
    app.dependency_overrides[get_current_user] = _user_auth(email="eric.seaman@yahoo.com")
    mock_doc_snap = MagicMock()
    mock_doc_snap.exists = True
    mock_doc_snap.to_dict.return_value = {"variant": "classic"}
    mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = mock_doc_snap

    client = TestClient(app)
    resp = client.get("/api/user/ui_variant")
    assert resp.status_code == 200
    assert resp.json() == {"variant": "classic"}
