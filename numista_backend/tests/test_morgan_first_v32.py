"""
Morgan-First UX v3.2 — AG-0 & Backend Acceptance Tests (AT-01, AT-02, AT-09..AT-12, AT-14, AT-15).
Exercises the real FastAPI app and route handlers (P5a: no skip hooks) and captures
exact request URL, method, and Authorization: Bearer <token> (P5).
"""

import io
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import main  # noqa: E402
from routes import morgan_routes  # noqa: E402


class InMemoryDoc:
    def __init__(self, store: dict, path: str):
        self._store = store
        self._path = path
        self.id = path.split("/")[-1]

    def get(self, transaction=None):
        data = self._store.get(self._path)
        snap = MagicMock()
        snap.exists = data is not None
        snap.id = self.id
        snap.to_dict.return_value = dict(data) if data is not None else None
        return snap

    def set(self, data: dict, merge: bool = False):
        if merge and self._path in self._store:
            merged = dict(self._store[self._path])
            merged.update(data)
            self._store[self._path] = merged
        else:
            self._store[self._path] = dict(data)

    def update(self, data: dict):
        if self._path not in self._store:
            self._store[self._path] = {}
        self._store[self._path].update(data)

    def delete(self):
        self._store.pop(self._path, None)

    def collection(self, name: str):
        return InMemoryCollection(self._store, f"{self._path}/{name}")


class InMemoryCollection:
    def __init__(self, store: dict, prefix: str):
        self._store = store
        self._prefix = prefix
        self._filters = []

    def document(self, doc_id: str = None):
        if not doc_id:
            idx = sum(1 for k in self._store if k.startswith(self._prefix + "/")) + 1
            doc_id = f"auto_{idx}"
        return InMemoryDoc(self._store, f"{self._prefix}/{doc_id}")

    def where(self, field: str, op: str, val):
        clone = InMemoryCollection(self._store, self._prefix)
        clone._filters = list(self._filters) + [(field, op, val)]
        return clone

    def stream(self):
        out = []
        depth = self._prefix.count("/") + 1
        for k, v in list(self._store.items()):
            if k.startswith(self._prefix + "/") and k.count("/") == depth:
                ok = True
                for field, op, val in self._filters:
                    if op == "==" and v.get(field) != val:
                        ok = False
                if ok:
                    snap = MagicMock()
                    snap.id = k.split("/")[-1]
                    snap.to_dict.return_value = dict(v)
                    out.append(snap)
        return out


class InMemoryDB:
    def __init__(self):
        self.store = {}

    def collection(self, name: str):
        return InMemoryCollection(self.store, name)

    def transaction(self):
        tx = MagicMock()

        def _update(ref, data):
            ref.update(data)

        tx.update = _update
        return tx


class RecordedClient:
    """Wraps TestClient to capture exact P5 request details (method, url, Authorization)."""

    def __init__(self, client: TestClient):
        self._client = client
        self.captured = []

    def request(self, method: str, url: str, **kwargs):
        headers = kwargs.get("headers") or {}
        auth = headers.get("Authorization") or headers.get("authorization")
        self.captured.append({"method": method.upper(), "url": url, "authorization": auth})
        return self._client.request(method, url, **kwargs)

    def get(self, url: str, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs):
        return self.request("POST", url, **kwargs)


@pytest.fixture
def env_setup(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("ALLOW_UNAUTHENTICATED", "0")
    mem_db = InMemoryDB()
    tokens = {
        "tok-eric": {"uid": "uid-eric", "email": "eric.seaman@yahoo.com", "firebase": {"sign_in_provider": "password"}},
        "tok-other": {"uid": "uid-other", "email": "collector@example.com", "firebase": {"sign_in_provider": "password"}},
        "tok-demo": {"uid": "uid-demo", "email": "", "firebase": {"sign_in_provider": "anonymous"}},
    }

    def _verify(tok):
        if tok not in tokens:
            raise main.fb_auth.InvalidIdTokenError("bad token")
        return tokens[tok]

    orig_main_db = main.db
    orig_morgan_db = morgan_routes.db
    main.db = mem_db
    morgan_routes.db = mem_db

    with patch("routes.deps.firebase_auth.verify_id_token", side_effect=_verify), \
         patch("main.fb_auth.verify_id_token", side_effect=_verify), \
         patch("routes.morgan_routes._check_and_increment_rate_cap", return_value=None), \
         patch("main._check_and_increment_rate_cap", return_value=None):
        client = RecordedClient(TestClient(main.app))
        yield client, mem_db

    main.db = orig_main_db
    morgan_routes.db = orig_morgan_db


def test_at01_flags_default_off(env_setup):
    client, _ = env_setup
    res = client.get("/api/morgan/home_flags", headers={"Authorization": "Bearer tok-eric"})
    assert res.status_code == 200
    body = res.json()
    assert body["flags"] == {
        "morgan_home_allowlist": False,
        "morgan_home_new_users": False,
        "morgan_home_everyone": False,
    }
    assert body["eligible"] is False
    assert body["show_morgan_home"] is False
    assert client.captured[-1]["authorization"] == "Bearer tok-eric"


def test_at02_existing_users_and_demo_unchanged_when_allowlist_on(env_setup):
    client, mem_db = env_setup
    mem_db.store["app_config/morgan_first_flags"] = {
        "morgan_home_allowlist": True,
        "morgan_home_new_users": False,
        "morgan_home_everyone": False,
    }
    res_other = client.get("/api/morgan/home_flags", headers={"Authorization": "Bearer tok-other"})
    assert res_other.status_code == 200
    assert res_other.json()["eligible"] is False
    assert res_other.json()["show_morgan_home"] is False

    res_demo = client.get("/api/morgan/home_flags", headers={"Authorization": "Bearer tok-demo"})
    assert res_demo.status_code == 200
    assert res_demo.json()["eligible"] is False
    assert res_demo.json()["show_morgan_home"] is False

    res_eric = client.get("/api/morgan/home_flags", headers={"Authorization": "Bearer tok-eric"})
    assert res_eric.status_code == 200
    assert res_eric.json()["eligible"] is True
    assert res_eric.json()["show_morgan_home"] is True


def test_f6_new_users_uses_creation_time_not_auth_time(env_setup):
    client, mem_db = env_setup
    cutoff_s = 1_800_000_000.0
    mem_db.store["app_config/morgan_first_flags"] = {
        "morgan_home_allowlist": False,
        "morgan_home_new_users": True,
        "morgan_home_everyone": False,
        "new_users_cutoff_ts": cutoff_s,
    }

    # Old account signing in AFTER cutoff (auth_time > cutoff, creation_timestamp < cutoff) -> NOT eligible
    old_user = MagicMock()
    old_user.user_metadata = SimpleNamespace(creation_timestamp=(cutoff_s - 86400) * 1000.0)
    # New account created AFTER cutoff -> eligible
    new_user = MagicMock()
    new_user.user_metadata = SimpleNamespace(creation_timestamp=(cutoff_s + 3600) * 1000.0)

    def _get_user(uid):
        return old_user if uid == "uid-other" else new_user

    with patch("routes.morgan_routes.firebase_auth.get_user", side_effect=_get_user):
        res_old = client.get("/api/morgan/home_flags", headers={"Authorization": "Bearer tok-other"})
        assert res_old.status_code == 200
        assert res_old.json()["eligible"] is False

        res_new = client.get("/api/morgan/home_flags", headers={"Authorization": "Bearer tok-eric"})
        assert res_new.status_code == 200
        assert res_new.json()["eligible"] is True


def test_at09_p5_add_confirm_and_idempotency(env_setup):
    client, mem_db = env_setup
    # Propose must NOT write to coins
    prop_res = client.post(
        "/api/morgan/propose",
        headers={"Authorization": "Bearer tok-eric"},
        json={"action": "add_coin", "coin_data": {"Year": "1921", "Denomination": "Dollar", "Mint Mark": "D"}},
    )
    assert prop_res.status_code == 200
    prop_id = prop_res.json()["proposal_id"]
    coin_keys_before = [k for k in mem_db.store if "/coins/" in k]
    assert coin_keys_before == []

    # Unauthenticated confirm rejected
    unauth = client.post("/api/morgan/confirm", json={"proposal_id": prop_id})
    assert unauth.status_code == 401

    # Cross-account confirm rejected
    cross = client.post(
        "/api/morgan/confirm",
        headers={"Authorization": "Bearer tok-other"},
        json={"proposal_id": prop_id},
    )
    assert cross.status_code == 403

    # Confirm once -> writes 1 coin
    conf1 = client.post(
        "/api/morgan/confirm",
        headers={"Authorization": "Bearer tok-eric"},
        json={"proposal_id": prop_id},
    )
    assert conf1.status_code == 200
    assert conf1.json()["status"] == "success"
    coin_keys_after = [k for k in mem_db.store if k.startswith("users/eric.seaman@yahoo.com/coins/")]
    assert len(coin_keys_after) == 1

    # Double tap -> idempotent, still 1 coin
    conf2 = client.post(
        "/api/morgan/confirm",
        headers={"Authorization": "Bearer tok-eric"},
        json={"proposal_id": prop_id},
    )
    assert conf2.status_code == 200
    assert conf2.json().get("idempotent") is True
    assert len([k for k in mem_db.store if k.startswith("users/eric.seaman@yahoo.com/coins/")]) == 1
    assert client.captured[-1]["method"] == "POST"
    assert client.captured[-1]["url"] == "/api/morgan/confirm"
    assert client.captured[-1]["authorization"] == "Bearer tok-eric"


def test_at10_p5_saved_preference(env_setup):
    client, mem_db = env_setup
    mem_db.store["app_config/morgan_first_flags"] = {
        "morgan_home_allowlist": True,
        "morgan_home_new_users": False,
        "morgan_home_everyone": False,
    }
    # Unauth rejected
    assert client.post("/api/morgan/home_preference", json={"preferred_home": "full_site"}).status_code == 401
    # Invalid value rejected
    assert client.post(
        "/api/morgan/home_preference",
        headers={"Authorization": "Bearer tok-eric"},
        json={"preferred_home": "invalid"},
    ).status_code == 400

    # Save full_site
    save_res = client.post(
        "/api/morgan/home_preference",
        headers={"Authorization": "Bearer tok-eric"},
        json={"preferred_home": "full_site"},
    )
    assert save_res.status_code == 200
    assert save_res.json()["preferred_home"] == "full_site"

    # New session read restores full_site
    read_res = client.get("/api/morgan/home_flags", headers={"Authorization": "Bearer tok-eric"})
    assert read_res.status_code == 200
    assert read_res.json()["preferred_home"] == "full_site"
    assert read_res.json()["show_morgan_home"] is False


def test_at11_p5_flags_read_only_to_client(env_setup):
    client, _ = env_setup
    assert client.get("/api/morgan/home_flags").status_code == 401
    # Client cannot flip flags via POST
    assert client.post(
        "/api/morgan/home_flags",
        headers={"Authorization": "Bearer tok-eric"},
        json={"morgan_home_allowlist": True},
    ).status_code in (404, 405)


def test_at12_p5_identify_coin_photo_requires_token_and_rejects_mismatch(env_setup):
    client, _ = env_setup
    files = {"image_a": ("front.jpg", io.BytesIO(b"fakejpeg"), "image/jpeg")}
    data = {"user_email": "eric.seaman@yahoo.com", "save_to_collection": "false"}
    assert client.post("/api/identify_coin_photo", data=data, files=files).status_code == 401

    files2 = {"image_a": ("front.jpg", io.BytesIO(b"fakejpeg"), "image/jpeg")}
    res_cross = client.post(
        "/api/identify_coin_photo",
        headers={"Authorization": "Bearer tok-other"},
        data=data,
        files=files2,
    )
    assert res_cross.status_code == 403


def test_at14_old_morgan_write_tools_closed(env_setup):
    client, mem_db = env_setup
    # 1. No most-recent-coin fallback when coin_id is omitted and 0 recent coins
    upd = main.propose_update_coin("eric.seaman@yahoo.com", "uid-eric", coin_id=None, condition="MS-65")
    assert upd["status"] == "ambiguous"

    # 2. INTERNAL_UNDO with no matching morgan_action_log is rejected 403 (never hard-deletes)
    res_unlogged = client.post(
        "/api/deep_dive",
        headers={"Authorization": "Bearer tok-eric"},
        json={"user_email": "eric.seaman@yahoo.com", "query": "INTERNAL_UNDO:nonexistent_coin"},
    )
    assert res_unlogged.status_code == 403

    # 3. INTERNAL_UNDO with stale (>30 min) log is rejected 403 (session-limited per F7)
    from datetime import datetime, timedelta, timezone
    mem_db.store["users/eric.seaman@yahoo.com/coins/c_old"] = {"Year": "1921", "Denomination": "Dollar"}
    mem_db.store["users/eric.seaman@yahoo.com/morgan_action_log/log_old"] = {
        "who": "uid-eric",
        "action": "add",
        "coin_id": "c_old",
        "confirm_time": datetime.now(timezone.utc) - timedelta(hours=2),
    }
    res_stale = client.post(
        "/api/deep_dive",
        headers={"Authorization": "Bearer tok-eric"},
        json={"user_email": "eric.seaman@yahoo.com", "query": "INTERNAL_UNDO:c_old"},
    )
    assert res_stale.status_code == 403
    assert "users/eric.seaman@yahoo.com/coins/c_old" in mem_db.store

    # 4. INTERNAL_UNDO with valid current-session log moves coin to trash (soft delete)
    mem_db.store["users/eric.seaman@yahoo.com/coins/c1"] = {"Year": "1921", "Denomination": "Dollar"}
    mem_db.store["users/eric.seaman@yahoo.com/morgan_action_log/log1"] = {
        "who": "uid-eric",
        "action": "add",
        "coin_id": "c1",
        "confirm_time": datetime.now(timezone.utc),
    }
    res_undo = client.post(
        "/api/deep_dive",
        headers={"Authorization": "Bearer tok-eric"},
        json={"user_email": "eric.seaman@yahoo.com", "query": "INTERNAL_UNDO:c1"},
    )
    assert res_undo.status_code == 200
    assert "users/eric.seaman@yahoo.com/coins/c1" not in mem_db.store
    assert "users/eric.seaman@yahoo.com/trash/c1" in mem_db.store


@pytest.mark.parametrize(
    "path",
    [
        "/api/checklist/add_coins",
        "/api/review/commit",
        "/api/analyze_binder_scan",
        "/api/confirm_binder_scan",
        "/api/scan/upload_document",
        "/api/scan/review/commit_session",
        "/api/import/upload",
        "/api/import/start",
        "/api/v1/import/commit_batch",
        "/api/v1/rag/query",
        "/api/deep_dive",
        "/api/ai/chat",
        "/api/ai/chat/stream",
        "/api/morgan/propose",
        "/api/morgan/confirm",
    ],
)
def test_at15_req031_write_routes_reject_no_token(env_setup, path):
    client, _ = env_setup
    res = client.post(path, json={"user_email": "eric.seaman@yahoo.com"})
    if path == "/api/ai/chat/stream":
        # Route does not exist in current backend (replaced by /api/ai/chat & /api/deep_dive)
        assert res.status_code in (401, 403, 404), f"Unexpected status on {path}: {res.status_code}"
    else:
        assert res.status_code in (401, 403), f"Expected 401/403 on {path}, got {res.status_code}"
