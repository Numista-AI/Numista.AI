"""Phase 1 continuation tests: Sold-reader audit, PDF seller photos, and pending transfers list."""

import base64
import io
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from services.item_state import is_sold_item, unsold_docs
from services.transfer_service import (
    _load_seller_photo_bytes_for_pdf,
    initiate_transfer,
    list_pending_transfers,
)


def _sample_jpeg_bytes(color=(200, 160, 40), size=(120, 120)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color=color).save(buf, format="JPEG", quality=85)
    return buf.getvalue()


class _FakeSnap:
    def __init__(self, doc_id: str, data):
        self.id = doc_id
        self._data = dict(data) if data is not None else None
        self.exists = data is not None

    def to_dict(self):
        return dict(self._data) if self._data is not None else None


class _FakeDocRef:
    def __init__(self, store: dict, path: str):
        self._store = store
        self._path = path
        self.id = path.split("/")[-1]

    def get(self):
        return _FakeSnap(self.id, self._store.get(self._path))

    def set(self, data):
        self._store[self._path] = dict(data)

    def update(self, data):
        cur = dict(self._store.get(self._path) or {})
        cur.update(data)
        self._store[self._path] = cur

    def delete(self):
        self._store.pop(self._path, None)

    def collection(self, name: str):
        return _FakeColRef(self._store, f"{self._path}/{name}")


class _FakeQuery:
    def __init__(self, store: dict, prefix: str, filters=None):
        self._store = store
        self._prefix = prefix
        self._filters = list(filters or [])

    def where(self, field: str, op: str, value):
        return _FakeQuery(self._store, self._prefix, self._filters + [(field, op, value)])

    def _matching(self):
        out = []
        depth = self._prefix.count("/") + 1
        for k, v in self._store.items():
            if not k.startswith(self._prefix + "/") or k.count("/") != depth:
                continue
            ok = True
            for field, op, val in self._filters:
                if op == "==" and (v or {}).get(field) != val:
                    ok = False
                    break
            if ok:
                out.append(_FakeSnap(k.split("/")[-1], v))
        return out

    def stream(self):
        return iter(self._matching())

    def count(self):
        n = len(self._matching())
        return SimpleNamespace(get=lambda: [[SimpleNamespace(value=n)]])


class _FakeColRef(_FakeQuery):
    def document(self, doc_id: str):
        return _FakeDocRef(self._store, f"{self._prefix}/{doc_id}")


class _FakeDB:
    def __init__(self):
        self.store = {}

    def collection(self, name: str):
        return _FakeColRef(self.store, name)


class _FakeStorageClient:
    def __init__(self, blobs: dict):
        self._blobs = blobs
        self.requested = []

    def bucket(self, bucket_name: str):
        parent = self

        class _Bucket:
            def blob(self, blob_name: str):
                parent.requested.append((bucket_name, blob_name))
                data = parent._blobs.get((bucket_name, blob_name))
                if data is None:
                    raise FileNotFoundError(f"missing {bucket_name}/{blob_name}")
                return SimpleNamespace(size=len(data), download_as_bytes=lambda: data)

        return _Bucket()


# ── 1. Sold-reader helpers & tier_gatekeeper ──────────────────────────────────

def test_item_state_skips_sold_but_keeps_active_and_pending():
    docs = [
        _FakeSnap("c1", {"Year": "1921", "status": "active"}),
        _FakeSnap("c2", {"Year": "1922", "status": "sold"}),
        _FakeSnap("c3", {"Year": "1923", "transferStatus": "pending"}),
        _FakeSnap("c4", {"Year": "1924", "status": "sold", "transferStatus": "pending"}),
    ]
    assert is_sold_item(docs[1].to_dict()) is True
    assert is_sold_item(docs[2].to_dict()) is False
    kept_ids = [d.id for d in unsold_docs(docs)]
    assert kept_ids == ["c1", "c3"]


def test_tier_gatekeeper_get_coin_count_excludes_sold(monkeypatch):
    import tier_gatekeeper

    fake_db = _FakeDB()
    fake_db.store["users/a@test.com/coins/c1"] = {"Year": "1921"}
    fake_db.store["users/a@test.com/coins/c2"] = {"Year": "1922", "status": "sold"}
    fake_db.store["users/a@test.com/coins/c3"] = {"Year": "1923"}
    monkeypatch.setattr(tier_gatekeeper, "db", fake_db)
    assert tier_gatekeeper.get_coin_count("a@test.com") == 2


# ── 2. Transfer Document seller photos ────────────────────────────────────────

def test_initiate_transfer_include_photos_embeds_only_validated_seller_photos():
    db = _FakeDB()
    bucket = "numista-uploads-studio-9101802118-8c9a8"
    own_blob = "users/seller@test.com/coins/c1/owner_photo_1.jpg"
    other_blob = "users/other@test.com/coins/c1/owner_photo_2.jpg"
    db.store["users/seller@test.com/coins/c1"] = {
        "Year": "1921",
        "Denomination": "$1",
        "Program/Series": "Morgan Dollar",
        "Quantity": 1,
        "owner_photos": [
            {"compressed_url": f"gs://{bucket}/{own_blob}"},
            {"compressed_url": f"gs://{bucket}/{other_blob}"},
            {"compressed_url": "https://evil.example.com/stolen.jpg"},
        ],
    }
    storage = _FakeStorageClient({(bucket, own_blob): _sample_jpeg_bytes()})

    res_with = initiate_transfer(
        db=db,
        user_a_id="seller@test.com",
        item_ids=["c1"],
        version=2,
        include_photos=True,
        storage_client=storage,
    )
    assert res_with["include_photos"] is True
    assert storage.requested == [(bucket, own_blob)]
    pdf_with = base64.b64decode(res_with["document_pdf_b64"])
    assert pdf_with.startswith(b"%PDF-")

    # Without photos: storage is never touched, PDF is smaller.
    db2 = _FakeDB()
    db2.store["users/seller@test.com/coins/c1"] = dict(db.store["users/seller@test.com/coins/c1"])
    db2.store["users/seller@test.com/coins/c1"].pop("transferStatus", None)
    storage2 = _FakeStorageClient({(bucket, own_blob): _sample_jpeg_bytes()})
    res_without = initiate_transfer(
        db=db2,
        user_a_id="seller@test.com",
        item_ids=["c1"],
        version=2,
        include_photos=False,
        storage_client=storage2,
    )
    assert res_without["include_photos"] is False
    assert storage2.requested == []
    pdf_without = base64.b64decode(res_without["document_pdf_b64"])
    assert len(pdf_with) > len(pdf_without)


def test_load_seller_photo_bytes_rejects_external_and_other_owner():
    bucket = "numista-uploads-studio-9101802118-8c9a8"
    storage = _FakeStorageClient({})
    out = _load_seller_photo_bytes_for_pdf(
        {
            "c1": {
                "owner_photos": [
                    {"url": "https://mint.example.com/stock.jpg"},
                    {"url": f"gs://{bucket}/users/other@test.com/coins/c1/a.jpg"},
                ]
            }
        },
        {"seller@test.com"},
        storage_client=storage,
    )
    assert out == {}
    assert storage.requested == []


# ── 3. Pending transfers list (service + route) ───────────────────────────────

def test_list_pending_transfers_filters_and_strips_secrets():
    db = _FakeDB()
    now = datetime.now(timezone.utc)
    db.store["transfers/t_open"] = {
        "transfer_id": "t_open",
        "sender_id": "seller@test.com",
        "status": "pending",
        "version": 2,
        "transfer_type": "sale_ebay",
        "source": "active",
        "created_at": now.isoformat(),
        "expires_at": (now + timedelta(days=30)).isoformat(),
        "items": [{"Year": "1921", "Denomination": "$1", "Program/Series": "Morgan Dollar"}],
        "claim_token_hash": "secret_hash_1",
        "claim_code_hash": "secret_hash_2",
        "claim_lookup_ids": ["secret_hash_1", "secret_hash_2"],
        "sender_address": "123 Private St",
    }
    db.store["transfers/t_expired"] = {
        "transfer_id": "t_expired",
        "sender_id": "seller@test.com",
        "status": "pending",
        "version": 2,
        "created_at": (now - timedelta(days=70)).isoformat(),
        "expires_at": (now - timedelta(days=1)).isoformat(),
        "items": [{"Year": "1964", "Denomination": "50c"}],
    }
    db.store["transfers/t_claimed"] = {
        "transfer_id": "t_claimed",
        "sender_id": "seller@test.com",
        "status": "claimed",
        "items": [],
    }
    db.store["transfers/t_other"] = {
        "transfer_id": "t_other",
        "sender_id": "other@test.com",
        "status": "pending",
        "items": [],
    }

    rows = list_pending_transfers(db, "SELLER@TEST.COM")
    assert [r["transfer_id"] for r in rows] == ["t_open", "t_expired"]
    assert rows[0]["is_expired"] is False
    assert rows[1]["is_expired"] is True
    for forbidden in ("claim_token_hash", "claim_code_hash", "claim_lookup_ids", "claim_pin", "sender_address"):
        assert forbidden not in rows[0]


def test_api_pending_transfers_route_uses_verified_token(monkeypatch):
    import main as backend_main
    from routes.deps import require_registered_user

    fake_db = _FakeDB()
    now = datetime.now(timezone.utc)
    fake_db.store["transfers/t1"] = {
        "transfer_id": "t1",
        "sender_id": "alice@test.com",
        "status": "pending",
        "version": 2,
        "created_at": now.isoformat(),
        "expires_at": (now + timedelta(days=10)).isoformat(),
        "items": [{"Year": "1921", "Denomination": "$1"}],
    }
    monkeypatch.setattr(backend_main, "db", fake_db)
    backend_main.app.dependency_overrides[require_registered_user] = lambda: {
        "email": "alice@test.com",
        "uid": "uid_alice",
    }
    try:
        client = TestClient(backend_main.app)
        resp = client.get("/api/transfer/pending")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert len(body["transfers"]) == 1
        assert body["transfers"][0]["transfer_id"] == "t1"
    finally:
        backend_main.app.dependency_overrides.clear()
