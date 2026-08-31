"""
test_attorney_routes.py — ITEM B acceptance criteria tests
===========================================================
Tests POST /api/attorney/issue, GET /api/attorney/snapshot, and
POST /api/attorney/revoke against the route matrix from plan B6/B7.

Coverage:
  [x] B7.3  Bare /attorney → 400 (no uid/token params)
  [x] B7.6  Valid JWT + POST /issue returns token_url exactly once
  [x]       token_url contains raw token (not hash), uid embedded
  [x]       B-ADD-3: token_url never appears in captured log calls
  [x] B7.7  First GET with raw token → 200 + scoped snapshot (coins)
  [x]       Private fields excluded from snapshot (notes, storage_location)
  [x] B7.7  Second GET (one-time token) → 410 "already used"
  [x]       Expired token → 410 "expired"
  [x]       Wrong uid → 403
  [x]       Revoked token → 410 "revoked"
  [x]       Non-existent token → 410

Run: pytest numista_tests/test_attorney_routes.py -v
"""

import datetime
import hashlib
import logging
import secrets
import sys
import types
from datetime import timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# ── Firestore / firebase_admin stubs ─────────────────────────────────────────
# These must be registered BEFORE importing attorney_routes.

_fake_auth = types.SimpleNamespace()

_google_stub   = types.ModuleType("google")
_cloud_stub    = types.ModuleType("google.cloud")
_fs_stub       = types.ModuleType("google.cloud.firestore")
_genai_stub    = types.ModuleType("google.genai")
_genai_t_stub  = types.ModuleType("google.genai.types")

for name, mod in [
    ("google", _google_stub),
    ("google.cloud", _cloud_stub),
    ("google.cloud.firestore", _fs_stub),
    ("google.cloud.storage", types.ModuleType("google.cloud.storage")),
    ("google.genai", _genai_stub),
    ("google.genai.types", _genai_t_stub),
    ("firebase_admin", types.SimpleNamespace(auth=_fake_auth, _apps={"default": True})),
    ("firebase_admin.auth", _fake_auth),
    ("firebase_admin.credentials", MagicMock()),
    ("firebase_admin.firestore", MagicMock()),
]:
    sys.modules.setdefault(name, mod)

# ── Build a mock db that tests can configure per-call ───────────────────────

_mock_db   = MagicMock()
_mock_log  = MagicMock()

# Patch routes.deps so the router imports a controllable db and logger.
_deps_stub = types.SimpleNamespace(db=_mock_db, logger=_mock_log)
sys.modules["routes.deps"] = _deps_stub

import routes.attorney_routes as ar          # noqa: E402  (import after stubs)
import importlib
importlib.reload(ar)                          # pick up the patched deps

# ── App ───────────────────────────────────────────────────────────────────────

_app = FastAPI()
_app.include_router(ar.router)
_client = TestClient(_app, raise_server_exceptions=False)

# ── Constants ─────────────────────────────────────────────────────────────────

OWNER_UID = "Ehdk3F27U2hhYKV8TRGpCiYWeCF2"
OTHER_UID = "OtherUserFirebaseUID12345"
VALID_AUTH = {"Authorization": "Bearer fake-id-token"}

# ── Helpers ───────────────────────────────────────────────────────────────────

def _now():
    return datetime.datetime.now(timezone.utc)


def _make_token_snap(uid, raw_token, *, expired=False, revoked=False, redeemed=False):
    tok_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires  = (_now() - datetime.timedelta(hours=1)) if expired else (_now() + datetime.timedelta(hours=72))
    snap = MagicMock()
    snap.exists = True
    snap.to_dict.return_value = {
        "token_id":   tok_hash,
        "uid":        uid,
        "created_at": _now(),
        "expires_at": expires,
        "is_one_time": True,
        "redeemed_at": _now() if redeemed else None,
        "is_revoked":  revoked,
    }
    return snap


def _missing_snap():
    s = MagicMock()
    s.exists = False
    return s


def _coin_stream(n=3):
    coins = []
    for i in range(n):
        c = MagicMock()
        c.id = f"coin_{i}"
        c.to_dict.return_value = {
            "coin_name":        f"Test Coin {i}",
            "year":             "1921",
            "country":          "USA",
            "is_foreign":       False,
            "purchase_price":   100.0,
            "greysheet_value":  110.0,
            "notes":            "PRIVATE — must not appear in snapshot",
            "storage_location": "Safe — PRIVATE",
        }
        coins.append(c)
    return iter(coins)


def _set_uid(uid: str):
    """Configure the JWT stub to return a specific uid."""
    _fake_auth.verify_id_token = lambda token: {"uid": uid}


def _setup_snapshot_db(uid, raw_token, **kwargs):
    """
    Wire _mock_db for a snapshot call:
      attorney_tokens/{hash}.get() → token snap
      users/{uid}/coins.stream()   → coin stream
    """
    tok_snap = _make_token_snap(uid, raw_token, **kwargs) if not kwargs.get("token_missing") else _missing_snap()
    tok_ref  = MagicMock()
    tok_ref.get.return_value = tok_snap
    tok_ref.update.return_value = None

    coins_col = MagicMock()
    coins_col.stream.return_value = _coin_stream()

    user_ref = MagicMock()
    user_ref.collection.return_value = coins_col

    def _col(name):
        m = MagicMock()
        if name == "attorney_tokens":
            m.document.return_value = tok_ref
        elif name == "users":
            m.document.return_value = user_ref
        return m

    _mock_db.reset_mock()
    _mock_db.collection.side_effect = _col


@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset shared mocks between tests."""
    _mock_db.reset_mock()
    _mock_log.reset_mock()
    _fake_auth.verify_id_token = lambda token: (_ for _ in ()).throw(
        Exception("no uid set — call _set_uid() in test")
    )
    yield


# ── ITEM B7.6 — Issue ────────────────────────────────────────────────────────

class TestIssueToken:

    def test_issue_returns_token_url(self):
        """Valid JWT → token_url contains uid and raw token."""
        _set_uid(OWNER_UID)
        _mock_db.collection.return_value.document.return_value.set.return_value = None

        resp = _client.post("/api/attorney/issue", headers=VALID_AUTH)
        assert resp.status_code == 200, resp.json()
        body = resp.json()
        assert "token_url" in body
        assert OWNER_UID in body["token_url"]
        assert "token=" in body["token_url"]
        assert body["is_one_time"] is True

    def test_issue_no_auth_returns_401(self):
        resp = _client.post("/api/attorney/issue")
        assert resp.status_code == 401

    def test_issue_token_url_not_in_logs(self):
        """B-ADD-3: token_url must never appear in any logger call."""
        _set_uid(OWNER_UID)
        _mock_db.collection.return_value.document.return_value.set.return_value = None

        resp = _client.post("/api/attorney/issue", headers=VALID_AUTH)
        assert resp.status_code == 200
        token_url = resp.json()["token_url"]
        raw_token  = token_url.split("token=")[1]

        all_calls = (
            _mock_log.info.call_args_list
            + _mock_log.warning.call_args_list
            + _mock_log.error.call_args_list
            + getattr(_mock_log, "debug", MagicMock()).call_args_list
        )
        for call in all_calls:
            logged = str(call)
            assert token_url  not in logged, f"token_url leaked into log: {logged}"
            assert raw_token  not in logged, f"raw token leaked into log: {logged}"


# ── ITEM B7.3 / B7.7 — Snapshot ──────────────────────────────────────────────

class TestSnapshotEndpoint:

    def test_snapshot_valid_token_200(self):
        """Valid token → 200, coins returned, private fields excluded."""
        raw = secrets.token_hex(32)
        _setup_snapshot_db(OWNER_UID, raw)

        resp = _client.get(f"/api/attorney/snapshot?uid={OWNER_UID}&token={raw}")
        assert resp.status_code == 200, resp.json()
        body = resp.json()
        assert body["total_coins"] == 3
        for coin in body["coins"]:
            assert "notes" not in coin,            "notes must be excluded"
            assert "storage_location" not in coin, "storage_location must be excluded"

    def test_snapshot_empty_params_400(self):
        """Empty uid + token → 400, no Firestore call."""
        resp = _client.get("/api/attorney/snapshot?uid=&token=")
        assert resp.status_code == 400
        _mock_db.collection.assert_not_called()

    def test_snapshot_nonexistent_token_410(self):
        """Hash not in attorney_tokens → 410."""
        raw = "doesnotexist"
        _setup_snapshot_db(OWNER_UID, raw, token_missing=True)

        resp = _client.get(f"/api/attorney/snapshot?uid={OWNER_UID}&token={raw}")
        assert resp.status_code == 410, resp.json()

    def test_snapshot_expired_token_410(self):
        """Expired token → 410 with 'expired' in message."""
        raw = secrets.token_hex(32)
        _setup_snapshot_db(OWNER_UID, raw, expired=True)

        resp = _client.get(f"/api/attorney/snapshot?uid={OWNER_UID}&token={raw}")
        assert resp.status_code == 410, resp.json()
        assert "expired" in resp.json()["detail"].lower()

    def test_snapshot_wrong_uid_403(self):
        """Token uid != query uid → 403 with account message."""
        raw = secrets.token_hex(32)
        # Token owned by OWNER; request uses OTHER
        _setup_snapshot_db(OWNER_UID, raw)

        resp = _client.get(f"/api/attorney/snapshot?uid={OTHER_UID}&token={raw}")
        assert resp.status_code == 403, resp.json()
        assert "not valid for this account" in resp.json()["detail"]

    def test_snapshot_revoked_token_410(self):
        """Revoked token → 410 with 'revoked' in message."""
        raw = secrets.token_hex(32)
        _setup_snapshot_db(OWNER_UID, raw, revoked=True)

        resp = _client.get(f"/api/attorney/snapshot?uid={OWNER_UID}&token={raw}")
        assert resp.status_code == 410, resp.json()
        assert "revoked" in resp.json()["detail"].lower()

    def test_snapshot_already_redeemed_410(self):
        """One-time token already used → 410 with 'already been used'."""
        raw = secrets.token_hex(32)
        _setup_snapshot_db(OWNER_UID, raw, redeemed=True)

        resp = _client.get(f"/api/attorney/snapshot?uid={OWNER_UID}&token={raw}")
        assert resp.status_code == 410, resp.json()
        assert "already been used" in resp.json()["detail"].lower()


# ── Revoke ────────────────────────────────────────────────────────────────────

class TestRevokeToken:

    def _setup_revoke(self, owner_uid):
        tok_ref = MagicMock()
        snap = MagicMock()
        snap.exists = True
        snap.to_dict.return_value = {"uid": owner_uid, "is_revoked": False}
        tok_ref.get.return_value = snap
        tok_ref.update.return_value = None

        def _col(name):
            m = MagicMock()
            m.document.return_value = tok_ref
            return m

        _mock_db.reset_mock()
        _mock_db.collection.side_effect = _col

    def test_revoke_own_token_200(self):
        """Owner revokes own token → 200."""
        self._setup_revoke(OWNER_UID)
        _set_uid(OWNER_UID)
        tok_hash = hashlib.sha256(b"test").hexdigest()

        resp = _client.post(
            "/api/attorney/revoke",
            json={"token_hash": tok_hash},
            headers=VALID_AUTH,
        )
        assert resp.status_code == 200, resp.json()
        assert resp.json()["status"] == "revoked"

    def test_revoke_other_users_token_403(self):
        """Cannot revoke another user's token → 403."""
        self._setup_revoke(OTHER_UID)   # token owned by OTHER
        _set_uid(OWNER_UID)             # caller is OWNER
        tok_hash = hashlib.sha256(b"test").hexdigest()

        resp = _client.post(
            "/api/attorney/revoke",
            json={"token_hash": tok_hash},
            headers=VALID_AUTH,
        )
        assert resp.status_code == 403, resp.json()
