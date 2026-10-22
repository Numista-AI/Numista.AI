"""
numista_backend/tests/test_req031_auth.py
----------------------------------------
Unit and integration tests for REQ_031 API Auth Lockdown:
- Fix 1:  /api/v1/rag/query (auth + 50/day cap)
- Fix 2:  /api/checklist/add_coins (auth + body email mismatch guard)
- Fix 3:  /api/review/commit (auth + body email mismatch guard)
- Fix 4:  /api/analyze_binder_scan (auth + body email mismatch guard + 10/day cap)
- Fix 5:  /api/confirm_binder_scan (auth + body email mismatch guard)
- Fix 6:  /api/review/bulk_update (auth + mismatch + updates allowlist)
- Fix 7:  /api/review/delete_items (soft-delete auth + duplicate hard delete removed)
- Fix 8:  scan_routes review/* (auth + body UID mismatch guard) & upload_document (auth + 20/day cap)
- Fix 9:  /api/import_spreadsheet (auth + 5/day cap, optional user_email)
- Fix 10: ai_routes (email document key instead of uid for portfolio stats)
- Fix 11: _authenticate_request helper tests (401 on missing, 403 on mismatch)
- Fix 12: _check_and_increment_rate_cap shared helper tests (429, admin exemption, fail-closed)
"""

import os
import sys
import io
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app, _authenticate_request
from routes.deps import get_current_user, _check_and_increment_rate_cap


# ─── Auth Fixtures & Helpers ──────────────────────────────────────────────────

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
    # Ensure fresh dependency overrides for every test
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


# ─── Fix 1: /api/v1/rag/query ─────────────────────────────────────────────────

def test_rag_query_no_token():
    app.dependency_overrides[get_current_user] = _unauthenticated()
    client = TestClient(app)
    resp = client.post("/api/v1/rag/query", json={"query": "test"})
    assert resp.status_code == 401

def test_rag_query_under_cap():
    app.dependency_overrides[get_current_user] = _user_auth(uid="uid_rag", email="rag@example.com")
    with patch("main._check_and_increment_rate_cap") as mock_cap, \
         patch("main.Path.exists", return_value=False), \
         patch("sys.path"), \
         patch.dict("sys.modules", {"info_bot": MagicMock(query_rag_info_bot=lambda q, c: {"answer": "Grounded answer"})}):
        client = TestClient(app)
        resp = client.post("/api/v1/rag/query", json={"query": "Tell me about Morgan dollars"})
        assert resp.status_code == 200
        mock_cap.assert_called_once_with("uid_rag", "rag_query", 50)

def test_rag_query_at_cap():
    app.dependency_overrides[get_current_user] = _user_auth(uid="uid_rag", email="rag@example.com")
    with patch("main._check_and_increment_rate_cap", side_effect=HTTPException(status_code=429, detail="Daily limit reached")):
        client = TestClient(app)
        resp = client.post("/api/v1/rag/query", json={"query": "test"})
        assert resp.status_code == 429
        assert "Daily limit reached" in resp.json()["detail"]

def test_rag_query_admin_exempt():
    app.dependency_overrides[get_current_user] = _user_auth(uid="uid_admin", email="admin@example.com", is_admin=True)
    with patch("main._check_and_increment_rate_cap") as mock_cap, \
         patch.dict("sys.modules", {"info_bot": MagicMock(query_rag_info_bot=lambda q, c: {"answer": "Admin answer"})}):
        client = TestClient(app)
        resp = client.post("/api/v1/rag/query", json={"query": "test"})
        assert resp.status_code == 200
        mock_cap.assert_not_called()


# ─── Fix 2: /api/checklist/add_coins ──────────────────────────────────────────

def test_checklist_add_coins_no_token():
    app.dependency_overrides[get_current_user] = _unauthenticated()
    client = TestClient(app)
    resp = client.post("/api/checklist/add_coins", json={
        "idempotency_key": "idem-1",
        "program_id": "kennedy_half",
        "program_name": "Kennedy Half",
        "user_email": "alice@example.com",
        "slots": []
    })
    assert resp.status_code == 401

def test_checklist_add_coins_email_mismatch():
    app.dependency_overrides[get_current_user] = _user_auth(email="alice@example.com")
    client = TestClient(app)
    resp = client.post("/api/checklist/add_coins", json={
        "idempotency_key": "idem-1",
        "program_id": "kennedy_half",
        "program_name": "Kennedy Half",
        "user_email": "bob@example.com",
        "slots": []
    })
    assert resp.status_code == 403

def test_checklist_add_coins_happy_path():
    app.dependency_overrides[get_current_user] = _user_auth(email="alice@example.com")
    mock_batch = MagicMock()
    mock_db = MagicMock()
    mock_db.batch.return_value = mock_batch
    mock_idem = MagicMock()
    mock_idem.get.return_value.exists = False
    mock_db.collection.return_value.document.return_value = mock_idem

    with patch("main.db", mock_db):
        client = TestClient(app)
        resp = client.post("/api/checklist/add_coins", json={
            "idempotency_key": "idem-ok",
            "program_id": "kennedy_half",
            "program_name": "Kennedy Half",
            "user_email": "alice@example.com",
            "slots": [{
                "coin_name": "1964 Kennedy",
                "year": "1964",
                "mint_mark": "D",
                "denomination": "50c",
                "variety_id": ""
            }]
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["coins_written"] == 1


# ─── Fix 3: /api/review/commit ────────────────────────────────────────────────

def test_review_commit_no_token():
    app.dependency_overrides[get_current_user] = _unauthenticated()
    client = TestClient(app)
    resp = client.post("/api/review/commit", json={
        "user_email": "alice@example.com",
        "review_ids": ["rev-1"]
    })
    assert resp.status_code == 401

def test_review_commit_email_mismatch():
    app.dependency_overrides[get_current_user] = _user_auth(email="alice@example.com")
    client = TestClient(app)
    resp = client.post("/api/review/commit", json={
        "user_email": "attacker@example.com",
        "review_ids": ["rev-1"]
    })
    assert resp.status_code == 403

def test_review_commit_happy_path():
    app.dependency_overrides[get_current_user] = _user_auth(email="alice@example.com")
    mock_db = MagicMock()
    mock_batch = MagicMock()
    mock_db.batch.return_value = mock_batch
    mock_doc = MagicMock()
    mock_doc.exists = False  # item not found in queue -> 0 committed
    mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = mock_doc

    with patch("main.db", mock_db):
        client = TestClient(app)
        resp = client.post("/api/review/commit", json={
            "user_email": "alice@example.com",
            "review_ids": ["rev-1"]
        })
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"


def test_review_commit_attribute_dupe_committed_with_flag():
    """Verify that an attribute-based duplicate match is committed with possible_duplicate=True and NOT dropped."""
    app.dependency_overrides[get_current_user] = _user_auth(email="alice@example.com")
    mock_db = MagicMock()
    mock_batch = MagicMock()
    mock_db.batch.return_value = mock_batch

    mock_queue_doc = MagicMock()
    mock_queue_doc.exists = True
    mock_queue_doc.to_dict.return_value = {
        "Year": "1881",
        "Mint Mark": "S",
        "Denomination": "Dollar",
        "Program/Series": "Morgan Dollar",
        "Retailer Invoice #": "",
        "Retailer Item No.": "",
    }

    mock_existing_coin = MagicMock()
    mock_existing_coin.id = "existing-coin-1"

    # Set up mock queries on coins collection:
    mock_coins_col = MagicMock()
    # Where query chain returning existing coin
    mock_coins_col.where.return_value.where.return_value.where.return_value.limit.return_value.get.return_value = [mock_existing_coin]

    mock_queue_col = MagicMock()
    mock_queue_col.document.return_value.get.return_value = mock_queue_doc

    def mock_collection(name):
        if name == "coins":
            return mock_coins_col
        elif name == "review_queue":
            return mock_queue_col
        mock_sub = MagicMock()
        mock_sub.document.return_value.collection = mock_collection
        return mock_sub

    mock_user_doc = MagicMock()
    mock_user_doc.collection = mock_collection
    mock_db.collection.return_value.document.return_value = mock_user_doc

    with patch("main.db", mock_db):
        client = TestClient(app)
        resp = client.post("/api/review/commit", json={
            "user_email": "alice@example.com",
            "review_ids": ["rev-attr-dupe"]
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["committed"] == 1
        assert data["skipped"] == 0
        assert data["flagged"] == 1
        # Assert batch.set was called to commit the coin
        assert mock_batch.set.called
        saved_dict = mock_batch.set.call_args[0][1]
        assert saved_dict["possible_duplicate"] is True
def test_review_commit_split_invoice_qty_both_committed():
    """Verify that multiple items with same invoice# and item# in the same review batch are both committed (Qty split rows), even when query matches one in the batch."""
    app.dependency_overrides[get_current_user] = _user_auth(email="alice@example.com")
    mock_db = MagicMock()
    mock_batch = MagicMock()
    mock_db.batch.return_value = mock_batch

    mock_doc1 = MagicMock()
    mock_doc1.exists = True
    mock_doc1.to_dict.return_value = {
        "Year": "2026",
        "Retailer Invoice #": "INV-1234",
        "Retailer Item No.": "26EA",
        "Denomination": "Dollar",
        "Program/Series": "American Silver Eagle",
    }
    mock_doc2 = MagicMock()
    mock_doc2.exists = True
    mock_doc2.to_dict.return_value = {
        "Year": "2026",
        "Retailer Invoice #": "INV-1234",
        "Retailer Item No.": "26EA",
        "Denomination": "Dollar",
        "Program/Series": "American Silver Eagle",
    }

    mock_existing_in_batch = MagicMock()
    mock_existing_in_batch.id = "rev-split-1"  # doc_id IS in review_ids

    mock_coins_col = MagicMock()
    # Invoice query returns a coin whose id is in review_ids -> is_definite_dupe remains False
    mock_coins_col.where.return_value.where.return_value.limit.return_value.get.return_value = [mock_existing_in_batch]
    # Attribute query returns empty
    mock_coins_col.where.return_value.where.return_value.where.return_value.limit.return_value.get.return_value = []

    mock_queue_col = MagicMock()
    mock_queue_col.document.side_effect = lambda doc_id: mock_doc1 if doc_id == "rev-split-1" else mock_doc2

    def mock_collection(name):
        if name == "coins":
            return mock_coins_col
        elif name == "review_queue":
            return mock_queue_col
        mock_sub = MagicMock()
        mock_sub.document.return_value.collection = mock_collection
        return mock_sub

    mock_user_doc = MagicMock()
    mock_user_doc.collection = mock_collection
    mock_db.collection.return_value.document.return_value = mock_user_doc

    with patch("main.db", mock_db):
        client = TestClient(app)
        resp = client.post("/api/review/commit", json={
            "user_email": "alice@example.com",
            "review_ids": ["rev-split-1", "rev-split-2"]
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["committed"] == 2
        assert data["skipped"] == 0
        assert mock_batch.set.call_count == 2


def test_review_commit_reimport_same_invoice_item_skipped():
    """Verify that true re-import of same invoice # + item no skips and reports skipped: 1."""
    app.dependency_overrides[get_current_user] = _user_auth(email="alice@example.com")
    mock_db = MagicMock()
    mock_batch = MagicMock()
    mock_db.batch.return_value = mock_batch

    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "Year": "2026",
        "Retailer Invoice #": "INV-1234",
        "Retailer Item No.": "26EA",
        "Denomination": "Dollar",
        "Program/Series": "American Silver Eagle",
    }

    mock_existing_coin = MagicMock()
    mock_existing_coin.id = "already-in-collection-coin"  # NOT in review_ids

    mock_coins_col = MagicMock()
    # Invoice query returns coin already in collection -> is_definite_dupe becomes True
    mock_coins_col.where.return_value.where.return_value.limit.return_value.get.return_value = [mock_existing_coin]

    mock_queue_col = MagicMock()
    mock_queue_col.document.return_value.get.return_value = mock_doc

    def mock_collection(name):
        if name == "coins":
            return mock_coins_col
        elif name == "review_queue":
            return mock_queue_col
        mock_sub = MagicMock()
        mock_sub.document.return_value.collection = mock_collection
        return mock_sub

    mock_user_doc = MagicMock()
    mock_user_doc.collection = mock_collection
    mock_db.collection.return_value.document.return_value = mock_user_doc

    with patch("main.db", mock_db):
        client = TestClient(app)
        resp = client.post("/api/review/commit", json={
            "user_email": "alice@example.com",
            "review_ids": ["rev-reimport-1"]
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["committed"] == 0
        assert data["skipped"] == 1
        assert data["flagged"] == 0
        assert mock_batch.delete.called
        assert mock_batch.set.call_count == 0




# ─── Fix 4: /api/analyze_binder_scan ──────────────────────────────────────────

def test_analyze_binder_scan_no_token():
    app.dependency_overrides[get_current_user] = _unauthenticated()
    client = TestClient(app)
    resp = client.post(
        "/api/analyze_binder_scan",
        data={"user_email": "alice@example.com"},
        files={"images": ("page1.jpg", b"fake_bytes", "image/jpeg")}
    )
    assert resp.status_code == 401

def test_analyze_binder_scan_email_mismatch():
    app.dependency_overrides[get_current_user] = _user_auth(email="alice@example.com")
    client = TestClient(app)
    resp = client.post(
        "/api/analyze_binder_scan",
        data={"user_email": "bob@example.com"},
        files={"images": ("page1.jpg", b"fake_bytes", "image/jpeg")}
    )
    assert resp.status_code == 403

def test_analyze_binder_scan_at_cap():
    app.dependency_overrides[get_current_user] = _user_auth(email="alice@example.com")
    with patch("main._check_and_increment_rate_cap", side_effect=HTTPException(status_code=429, detail="Daily limit reached")):
        client = TestClient(app)
        resp = client.post(
            "/api/analyze_binder_scan",
            data={"user_email": "alice@example.com"},
            files={"images": ("page1.jpg", b"fake_bytes", "image/jpeg")}
        )
        assert resp.status_code == 429


# ─── Fix 5: /api/confirm_binder_scan ──────────────────────────────────────────

def test_confirm_binder_scan_no_token():
    app.dependency_overrides[get_current_user] = _unauthenticated()
    client = TestClient(app)
    resp = client.post("/api/confirm_binder_scan", json={
        "user_email": "alice@example.com",
        "binder_doc_id": "b-1",
        "scan_uuid": "s-1",
        "book_title": "Quarter Album",
        "storage_location": "Box A",
        "confirmed_coins": []
    })
    assert resp.status_code == 401

def test_confirm_binder_scan_email_mismatch():
    app.dependency_overrides[get_current_user] = _user_auth(email="alice@example.com")
    client = TestClient(app)
    resp = client.post("/api/confirm_binder_scan", json={
        "user_email": "bob@example.com",
        "binder_doc_id": "b-1",
        "scan_uuid": "s-1",
        "book_title": "Quarter Album",
        "storage_location": "Box A",
        "confirmed_coins": []
    })
    assert resp.status_code == 403

def test_confirm_binder_scan_happy_path():
    app.dependency_overrides[get_current_user] = _user_auth(email="alice@example.com")
    mock_db = MagicMock()
    mock_batch = MagicMock()
    mock_db.batch.return_value = mock_batch
    mock_binder_doc = MagicMock()
    mock_binder_doc.exists = False
    mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = mock_binder_doc

    with patch("main.db", mock_db):
        client = TestClient(app)
        resp = client.post("/api/confirm_binder_scan", json={
            "user_email": "alice@example.com",
            "binder_doc_id": "b-1",
            "scan_uuid": "s-1",
            "book_title": "Quarter Album",
            "storage_location": "Box A",
            "confirmed_coins": []
        })
        assert resp.status_code == 200


# ─── Fix 6: /api/review/bulk_update ───────────────────────────────────────────

def test_bulk_update_no_token():
    app.dependency_overrides[get_current_user] = _unauthenticated()
    client = TestClient(app)
    resp = client.post("/api/review/bulk_update", json={
        "user_email": "alice@example.com",
        "review_ids": ["rev-1"],
        "updates": {"condition": "MS-65"}
    })
    assert resp.status_code == 401

def test_bulk_update_email_mismatch():
    app.dependency_overrides[get_current_user] = _user_auth(email="alice@example.com")
    client = TestClient(app)
    resp = client.post("/api/review/bulk_update", json={
        "user_email": "bob@example.com",
        "review_ids": ["rev-1"],
        "updates": {"condition": "MS-65"}
    })
    assert resp.status_code == 403

def test_bulk_update_disallowed_field():
    app.dependency_overrides[get_current_user] = _user_auth(email="alice@example.com")
    client = TestClient(app)
    resp = client.post("/api/review/bulk_update", json={
        "user_email": "alice@example.com",
        "review_ids": ["rev-1"],
        "updates": {"disallowed_field": "injected"}
    })
    assert resp.status_code == 400

def test_bulk_update_allowed_fields_happy_path():
    app.dependency_overrides[get_current_user] = _user_auth(email="alice@example.com")
    mock_db = MagicMock()
    mock_batch = MagicMock()
    mock_db.batch.return_value = mock_batch

    with patch("main.db", mock_db):
        client = TestClient(app)
        resp = client.post("/api/review/bulk_update", json={
            "user_email": "alice@example.com",
            "review_ids": ["rev-1"],
            "updates": {"condition": "MS-65", "storage_location": "Safe", "notes": "Verified", "status": "staged"}
        })
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"


# ─── Fix 7: /api/review/delete_items ──────────────────────────────────────────

def test_delete_items_no_token():
    app.dependency_overrides[get_current_user] = _unauthenticated()
    client = TestClient(app)
    resp = client.post("/api/review/delete_items", json={
        "user_email": "alice@example.com",
        "review_ids": ["rev-1"]
    })
    assert resp.status_code == 401

def test_delete_items_email_mismatch():
    app.dependency_overrides[get_current_user] = _user_auth(email="alice@example.com")
    client = TestClient(app)
    resp = client.post("/api/review/delete_items", json={
        "user_email": "bob@example.com",
        "review_ids": ["rev-1"]
    })
    assert resp.status_code == 403

def test_delete_items_soft_delete_happy_path():
    app.dependency_overrides[get_current_user] = _user_auth(email="alice@example.com")
    mock_db = MagicMock()
    mock_batch = MagicMock()
    mock_db.batch.return_value = mock_batch

    with patch("main.db", mock_db):
        client = TestClient(app)
        resp = client.post("/api/review/delete_items", json={
            "user_email": "alice@example.com",
            "review_ids": ["rev-1"]
        })
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"


# ─── Fix 8: scan_routes review/* & upload_document ────────────────────────────

def test_upload_document_no_token():
    app.dependency_overrides[get_current_user] = _unauthenticated()
    client = TestClient(app)
    resp = client.post(
        "/api/upload_document",
        data={"uid": "uid_alice"},
        files={"file": ("doc.pdf", b"%PDF-1.4 test", "application/pdf")}
    )
    assert resp.status_code == 401

def test_upload_document_at_cap():
    app.dependency_overrides[get_current_user] = _user_auth(uid="uid_alice")
    with patch("routes.scan_routes._check_and_increment_rate_cap", side_effect=HTTPException(status_code=429, detail="Daily limit reached")):
        client = TestClient(app)
        resp = client.post(
            "/api/upload_document",
            data={"uid": "uid_alice"},
            files={"file": ("doc.pdf", b"%PDF-1.4 test", "application/pdf")}
        )
        assert resp.status_code == 429

def test_resume_session_no_token():
    app.dependency_overrides[get_current_user] = _unauthenticated()
    client = TestClient(app)
    resp = client.post("/api/review/resume_session", json={"uid": "uid_alice", "import_session_id": "sess-1"})
    assert resp.status_code == 401

def test_resume_session_uid_mismatch():
    app.dependency_overrides[get_current_user] = _user_auth(uid="uid_alice")
    client = TestClient(app)
    resp = client.post("/api/review/resume_session", json={"uid": "uid_bob", "import_session_id": "sess-1"})
    assert resp.status_code == 403

def test_abort_session_uid_mismatch():
    app.dependency_overrides[get_current_user] = _user_auth(uid="uid_alice")
    client = TestClient(app)
    resp = client.post("/api/review/abort_session", json={"uid": "uid_bob", "import_session_id": "sess-1"})
    assert resp.status_code == 403

def test_commit_session_uid_mismatch():
    app.dependency_overrides[get_current_user] = _user_auth(uid="uid_alice")
    client = TestClient(app)
    resp = client.post("/api/review/commit_session", json={"uid": "uid_bob", "import_session_id": "sess-1"})
    assert resp.status_code == 403

def test_bulk_condition_uid_mismatch():
    app.dependency_overrides[get_current_user] = _user_auth(uid="uid_alice")
    client = TestClient(app)
    resp = client.post("/api/review/bulk_condition", json={"uid": "uid_bob", "import_session_id": "sess-1", "condition": "MS-65"})
    assert resp.status_code == 403


# ─── Fix 9: /api/import_spreadsheet ───────────────────────────────────────────

def test_import_spreadsheet_no_token():
    app.dependency_overrides[get_current_user] = _unauthenticated()
    client = TestClient(app)
    resp = client.post(
        "/api/import_spreadsheet",
        files={"file": ("test.csv", b"Year,Denomination\n1921,Morgan Dollar\n", "text/csv")}
    )
    assert resp.status_code == 401

def test_import_spreadsheet_at_cap():
    app.dependency_overrides[get_current_user] = _user_auth(uid="uid_alice")
    with patch("routes.import_routes._check_and_increment_rate_cap", side_effect=HTTPException(status_code=429, detail="Daily limit reached")):
        client = TestClient(app)
        resp = client.post(
            "/api/import_spreadsheet",
            files={"file": ("test.csv", b"Year,Denomination\n1921,Morgan Dollar\n", "text/csv")}
        )
        assert resp.status_code == 429


# ─── Fix 10: ai_routes uid vs email key ───────────────────────────────────────

def test_ai_routes_portfolio_stats_uses_email_key():
    """Verify that portfolio summary query in /api/ai/chat uses the email doc key, not UID."""
    app.dependency_overrides[get_current_user] = _user_auth(uid="uid_alice_123", email="alice@testnumista.com")
    
    mock_db = MagicMock()
    # Mock document call to observe the key passed to users.document(...)
    mock_user_doc = MagicMock()
    mock_db.collection.return_value.document = MagicMock(return_value=mock_user_doc)
    mock_stats_doc = MagicMock()
    mock_stats_doc.exists = True
    mock_stats_doc.to_dict.return_value = {
        "total_coins": 42,
        "portfolio_value": 12500.0,
        "profit": 1500.0,
        "grade_count": 10
    }
    mock_user_doc.collection.return_value.document.return_value.get.return_value = mock_stats_doc

    with patch("routes.ai_routes.db", mock_db), \
         patch("routes.ai_routes.call_chat_model_with_fallback", return_value="Here is your portfolio answer."):
        client = TestClient(app)
        resp = client.post("/api/ai/chat", json={"query": "How many coins do I have?"})
        assert resp.status_code == 200
        # Check that db.collection('users').document was called with the email, NOT the UID
        document_calls = [c.args[0] for c in mock_db.collection.return_value.document.call_args_list]
        assert "alice@testnumista.com" in document_calls
        assert "uid_alice_123" not in document_calls


# ─── Fix 11: _authenticate_request ───────────────────────────────────────────

def test_authenticate_request_helper():
    # 1. Missing header -> 401
    with pytest.raises(HTTPException) as exc:
        _authenticate_request(None)
    assert exc.value.status_code == 401

    # 2. Invalid header format -> 401
    with pytest.raises(HTTPException) as exc:
        _authenticate_request("Basic 12345")
    assert exc.value.status_code == 401

    # 3. Mismatched email -> 403
    with patch("main.fb_auth.verify_id_token", return_value={"uid": "u1", "email": "alice@example.com"}):
        with pytest.raises(HTTPException) as exc:
            _authenticate_request("Bearer fake_token", body_email="bob@example.com")
        assert exc.value.status_code == 403

    # 4. Matching email -> returns email owner_key
    with patch("main.fb_auth.verify_id_token", return_value={"uid": "u1", "email": "alice@example.com"}):
        owner = _authenticate_request("Bearer fake_token", body_email="alice@example.com")
        assert owner == "alice@example.com"


# ─── Fix 12: _check_and_increment_rate_cap ────────────────────────────────────

def test_check_and_increment_rate_cap_helper():
    mock_db = MagicMock()
    mock_doc = MagicMock()
    mock_snap = MagicMock()
    mock_doc.get.return_value = mock_snap

    with patch("routes.deps.db", mock_db):
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value = mock_doc

        # Under limit -> increments without error
        mock_snap.exists = True
        mock_snap.to_dict.return_value = {"count": 10}
        _check_and_increment_rate_cap("uid1", "test_ep", 50)
        mock_doc.set.assert_called_once()

        # At limit -> raises 429
        mock_snap.to_dict.return_value = {"count": 50}
        with pytest.raises(HTTPException) as exc:
            _check_and_increment_rate_cap("uid1", "test_ep", 50)
        assert exc.value.status_code == 429

        # Admin -> exempt
        mock_doc.reset_mock()
        _check_and_increment_rate_cap("uid1", "test_ep", 50, is_admin=True)
        mock_doc.get.assert_not_called()

        # Fail closed on Firestore exception -> raises 429
        mock_doc.get.side_effect = Exception("Firestore network timeout")
        with pytest.raises(HTTPException) as exc:
            _check_and_increment_rate_cap("uid1", "test_ep", 50)
        assert exc.value.status_code == 429
