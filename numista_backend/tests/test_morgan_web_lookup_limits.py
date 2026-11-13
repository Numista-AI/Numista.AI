"""
Unit tests for Task #8 (M4): Morgan Web Lookup Limits (50/day global, 3/day per user).
"""

import os
import sys
from unittest.mock import MagicMock, patch
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from routes import deps
from routes import morgan_routes
import main as app_main


def _make_mock_db(user_count: int = 0, global_count: int = 0, raw_store=None):
    store = raw_store if raw_store is not None else {
        "_global": {"count": global_count},
        "uid_alice": {"count": user_count},
    }

    class _MockRef:
        def __init__(self, uid_key):
            self.uid_key = uid_key

        def get(self, transaction=None):
            snap = MagicMock()
            snap.exists = self.uid_key in store
            snap.to_dict.return_value = dict(store.get(self.uid_key, {}))
            return snap

    class _MockTransaction:
        _max_attempts = 1
        _id = b"mock-txn"

        def _begin(self, retry_id=None):
            pass

        def _commit(self):
            return []

        def _rollback(self):
            pass

        def _clean_up(self):
            pass

        def set(self, ref, payload, merge=True):
            prev = dict(store.get(ref.uid_key, {})) if merge else {}
            prev.update(payload)
            store[ref.uid_key] = prev

    def _collection_root(name):
        assert name == "_rate_limits"
        root = MagicMock()

        def _doc(uid_key):
            uid_doc = MagicMock()

            def _subcol(endpoint):
                subcol = MagicMock()
                subcol.document.side_effect = lambda _date: _MockRef(uid_key)
                return subcol

            uid_doc.collection.side_effect = _subcol
            return uid_doc

        root.document.side_effect = _doc
        return root

    mock_db = MagicMock()
    mock_db.collection.side_effect = _collection_root
    mock_db.transaction.side_effect = lambda: _MockTransaction()
    return mock_db, store


# ── 1. Dual-Tier Rate Limiter Logic & Null Safety ────────────────────────────

def test_dual_rate_cap_allows_first_three_and_blocks_fourth_user(monkeypatch):
    mock_db, store = _make_mock_db(user_count=0, global_count=10)
    monkeypatch.setattr(deps, "db", mock_db)
    monkeypatch.setattr(
        deps.firestore,
        "transactional",
        lambda fn: (lambda txn: fn(txn)),
    )

    for expected_user in (1, 2, 3):
        quota = deps.check_and_increment_dual_rate_cap("uid_alice", "morgan_web_lookup")
        assert quota["user_used"] == expected_user
        assert quota["user_remaining"] == 3 - expected_user
        assert quota["global_used"] == 10 + expected_user

    with pytest.raises(HTTPException) as exc_info:
        deps.check_and_increment_dual_rate_cap("uid_alice", "morgan_web_lookup")

    assert exc_info.value.status_code == 429
    assert "3/day" in exc_info.value.detail
    assert store["uid_alice"]["count"] == 3
    assert store["_global"]["count"] == 13


def test_dual_rate_cap_blocks_51st_global_without_burning_user_quota(monkeypatch):
    mock_db, store = _make_mock_db(user_count=0, global_count=50)
    monkeypatch.setattr(deps, "db", mock_db)
    monkeypatch.setattr(
        deps.firestore,
        "transactional",
        lambda fn: (lambda txn: fn(txn)),
    )

    with pytest.raises(HTTPException) as exc_info:
        deps.check_and_increment_dual_rate_cap("uid_alice", "morgan_web_lookup")

    assert exc_info.value.status_code == 429
    assert "50/day" in exc_info.value.detail
    assert store["uid_alice"]["count"] == 0
    assert store["_global"]["count"] == 50


def test_dual_rate_cap_admin_exempts_user_cap_but_enforces_global_cap(monkeypatch):
    mock_db, store = _make_mock_db(user_count=3, global_count=49)
    monkeypatch.setattr(deps, "db", mock_db)
    monkeypatch.setattr(
        deps.firestore,
        "transactional",
        lambda fn: (lambda txn: fn(txn)),
    )

    quota = deps.check_and_increment_dual_rate_cap(
        "uid_alice", "morgan_web_lookup", is_admin=True
    )
    assert quota["global_used"] == 50
    assert store["_global"]["count"] == 50

    with pytest.raises(HTTPException) as exc_info:
        deps.check_and_increment_dual_rate_cap(
            "uid_alice", "morgan_web_lookup", is_admin=True
        )
    assert exc_info.value.status_code == 429
    assert "50/day" in exc_info.value.detail


def test_dual_rate_cap_null_count_safety_and_reserved_global_uid(monkeypatch):
    mock_db, store = _make_mock_db(raw_store={"_global": {"count": None}, "uid_alice": {"count": None}})
    monkeypatch.setattr(deps, "db", mock_db)
    monkeypatch.setattr(
        deps.firestore,
        "transactional",
        lambda fn: (lambda txn: fn(txn)),
    )

    quota = deps.check_and_increment_dual_rate_cap("uid_alice", "morgan_web_lookup")
    assert quota["global_used"] == 1
    assert quota["user_used"] == 1

    with pytest.raises(HTTPException) as exc_info:
        deps.check_and_increment_dual_rate_cap("_global", "morgan_web_lookup")
    assert exc_info.value.status_code == 429


# ── 2. Morgan Routes (/api/morgan/web_lookup & /quota) ───────────────────────

def test_morgan_web_lookup_empty_query_guard_and_kill_switch(monkeypatch):
    mock_db, store = _make_mock_db(user_count=0, global_count=0)
    monkeypatch.setattr(deps, "db", mock_db)
    monkeypatch.setattr(
        deps.firestore,
        "transactional",
        lambda fn: (lambda txn: fn(txn)),
    )
    mock_genai = MagicMock()
    mock_genai.models.generate_content.return_value = MagicMock(text="1909-S VDB mintage is 484,000.")
    monkeypatch.setattr(morgan_routes, "genai_client", mock_genai)

    app_main.app.dependency_overrides[deps.get_current_user] = lambda: {
        "uid": "uid_alice",
        "email": "alice@example.com",
        "admin": False,
    }
    try:
        client = TestClient(app_main.app)

        # Empty/whitespace query -> 400 and 0 writes
        resp_empty = client.post(
            "/api/morgan/web_lookup",
            json={"query": "   "},
            headers={"Authorization": "Bearer fake-token"},
        )
        assert resp_empty.status_code == 400
        assert store["uid_alice"]["count"] == 0
        assert store["_global"]["count"] == 0

        # Kill-switch -> 503 and 0 writes
        monkeypatch.setenv("M4_WEB_LOOKUP_ENABLED", "false")
        resp_disabled = client.post(
            "/api/morgan/web_lookup",
            json={"query": "1909-S VDB mintage"},
            headers={"Authorization": "Bearer fake-token"},
        )
        assert resp_disabled.status_code == 503
        assert store["uid_alice"]["count"] == 0
        assert store["_global"]["count"] == 0

        # Enabled -> 200 and increments once
        monkeypatch.setenv("M4_WEB_LOOKUP_ENABLED", "true")
        resp_ok = client.post(
            "/api/morgan/web_lookup",
            json={"query": "1909-S VDB mintage"},
            headers={"Authorization": "Bearer fake-token"},
        )
        assert resp_ok.status_code == 200
        body = resp_ok.json()
        assert body["status"] == "success"
        assert body["quota"]["user_used"] == 1
        assert body["quota"]["global_used"] == 1

        # Read-only quota endpoint -> 0 additional writes
        resp_quota = client.get(
            "/api/morgan/web_lookup/quota",
            headers={"Authorization": "Bearer fake-token"},
        )
        assert resp_quota.status_code == 200
        q_body = resp_quota.json()
        assert q_body["user_used"] == 1
        assert q_body["user_remaining"] == 2
        assert q_body["global_used"] == 1
        assert q_body["global_remaining"] == 49
    finally:
        app_main.app.dependency_overrides.clear()


# ── 3. /api/deep_dive Zero-Token 429 Short-Circuit & Parallel Guard ──────────

def test_deep_dive_zero_token_429_short_circuit_and_parallel_guard(monkeypatch):
    monkeypatch.setenv("M4_WEB_LOOKUP_ENABLED", "true")
    monkeypatch.setattr(app_main.fb_auth, "verify_id_token", lambda _tok: {
        "uid": "uid_alice",
        "email": "alice@example.com",
        "admin": False,
    })
    monkeypatch.setattr(app_main, "_check_and_increment_rate_cap", lambda *a, **kw: None)

    # Stub Firestore coin stream used by /api/deep_dive prompt builder
    mock_col = MagicMock()
    mock_col.stream.return_value = []
    mock_user_doc = MagicMock()
    mock_user_doc.collection.return_value = mock_col
    mock_users = MagicMock()
    mock_users.document.return_value = mock_user_doc
    monkeypatch.setattr(app_main.db, "collection", lambda _name: mock_users)

    call_one = MagicMock()
    call_one.name = "web_lookup"
    call_one.args = {"query": "1916-D Mercury dime mintage"}
    call_two = MagicMock()
    call_two.name = "web_lookup"
    call_two.args = {"query": "duplicate parallel query"}

    # Case A: 429 on first web_lookup -> zero-token short-circuit (generate_content called ONCE)
    mock_genai = MagicMock()
    mock_genai.models.generate_content.return_value = MagicMock(
        function_calls=[call_one], text=""
    )
    monkeypatch.setattr(app_main, "genai_client", mock_genai)
    monkeypatch.setattr(
        app_main,
        "check_and_increment_dual_rate_cap",
        MagicMock(side_effect=HTTPException(status_code=429, detail="Your daily Morgan web lookup limit reached (3/day). Please try again tomorrow.")),
    )

    client = TestClient(app_main.app)
    resp_429 = client.post(
        "/api/deep_dive",
        json={"user_email": "alice@example.com", "query": "What is the mintage of a 1916-D dime?"},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp_429.status_code == 200
    data = resp_429.json()
    assert data["status"] == "rate_limited"
    assert "3/day" in data["response"]
    assert data["action_payload"]["status"] == "rate_limited"
    assert mock_genai.models.generate_content.call_count == 1

    # Case B: Parallel web_lookup calls in one turn -> quota incremented ONCE
    mock_genai.models.generate_content.reset_mock()
    mock_genai.models.generate_content.side_effect = [
        MagicMock(function_calls=[call_one, call_two], text=""),
        MagicMock(function_calls=[], text="The 1916-D Mercury dime had a mintage of 264,000."),
    ]
    cap_spy = MagicMock(return_value={"user_used": 1, "user_limit": 3, "user_remaining": 2, "global_used": 1, "global_limit": 50, "global_remaining": 49})
    monkeypatch.setattr(app_main, "check_and_increment_dual_rate_cap", cap_spy)
    monkeypatch.setattr(app_main, "execute_morgan_web_lookup", lambda query, coin_context=None: {"status": "success", "query": query, "answer": "264,000"})

    resp_parallel = client.post(
        "/api/deep_dive",
        json={"user_email": "alice@example.com", "query": "Look up 1916-D dime"},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp_parallel.status_code == 200
    assert cap_spy.call_count == 1

    # Case C: Kill-switch omits fn_web_lookup from tools
    monkeypatch.setenv("M4_WEB_LOOKUP_ENABLED", "false")
    mock_genai.models.generate_content.reset_mock()
    mock_genai.models.generate_content.side_effect = [MagicMock(function_calls=[], text="Disabled.")]
    resp_off = client.post(
        "/api/deep_dive",
        json={"user_email": "alice@example.com", "query": "Hello Morgan"},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp_off.status_code == 200
    sent_config = mock_genai.models.generate_content.call_args.kwargs["config"]
    decl_names = [d.name for d in sent_config.tools[0].function_declarations]
    assert "web_lookup" not in decl_names
