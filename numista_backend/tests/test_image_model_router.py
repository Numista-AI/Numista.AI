"""Unit tests for the atomic Nano Banana Pro -> Nano Banana 2 image router."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from config import GEMINI_IMAGE_MODEL, GEMINI_IMAGE_PRO_MODEL  # noqa: E402
from services import image_model_router as router  # noqa: E402


class _FakeSnapshot:
    def __init__(self, exists: bool, data=None):
        self.exists = exists
        self._data = data or {}

    def to_dict(self):
        return dict(self._data)


class _FakeDocRef:
    def __init__(self, store: dict, key: str):
        self._store = store
        self._key = key

    def get(self, transaction=None):
        if self._key in self._store:
            return _FakeSnapshot(True, self._store[self._key])
        return _FakeSnapshot(False)


class _FakeTransaction:
    def __init__(self, store: dict):
        self._store = store
        self._max_attempts = 5
        self._max_read_retries = 5
        self._read_only = False
        self._id = b"fake-tx"

    def _begin(self, retry_id=None):
        pass

    def _rollback(self):
        pass

    def _commit(self):
        return []

    def _clean_up(self):
        pass

    def set(self, doc_ref: _FakeDocRef, data: dict, merge: bool = False):
        existing = self._store.get(doc_ref._key, {}) if merge else {}
        merged = {**existing, **data}
        self._store[doc_ref._key] = merged


class _FakeCollection:
    def __init__(self, store: dict, name: str):
        self._store = store
        self._name = name

    def document(self, doc_id: str):
        return _FakeDocRef(self._store, f"{self._name}/{doc_id}")


class _FakeDB:
    def __init__(self, initial_count: int = 0, month_key: str = "2026-11"):
        self.store = {}
        if initial_count is not None:
            self.store[f"system_metrics/image_gen_quota_{month_key}"] = {
                "pro_count": initial_count
            }

    def collection(self, name: str):
        return _FakeCollection(self.store, name)

    def transaction(self):
        return _FakeTransaction(self.store)


def test_reserves_pro_under_cap():
    db = _FakeDB(initial_count=0, month_key="2026-11")
    model, count, reserved_pro, mkey = router.reserve_image_model(
        db, month_key="2026-11", cap=100
    )
    assert model == GEMINI_IMAGE_PRO_MODEL
    assert count == 1
    assert reserved_pro is True
    assert mkey == "2026-11"
    assert db.store["system_metrics/image_gen_quota_2026-11"]["pro_count"] == 1


def test_reserves_100th_slot_then_overflows_to_flash_image():
    db = _FakeDB(initial_count=99, month_key="2026-11")
    model_100, count_100, reserved_100, _ = router.reserve_image_model(
        db, month_key="2026-11", cap=100
    )
    assert model_100 == GEMINI_IMAGE_PRO_MODEL
    assert count_100 == 100
    assert reserved_100 is True

    model_101, count_101, reserved_101, _ = router.reserve_image_model(
        db, month_key="2026-11", cap=100
    )
    assert model_101 == GEMINI_IMAGE_MODEL
    assert count_101 == 100
    assert reserved_101 is False
    assert db.store["system_metrics/image_gen_quota_2026-11"]["pro_count"] == 100


def test_pro_error_triggers_compensating_decrement_and_flash_fallback():
    db = _FakeDB(initial_count=10, month_key="2026-11")
    calls = []

    def flaky_call(model_id: str):
        calls.append(model_id)
        if model_id == GEMINI_IMAGE_PRO_MODEL:
            raise RuntimeError("503 Pro unavailable")
        return b"png-bytes"

    result, used_model = router.execute_with_image_routing(
        db, flaky_call, month_key="2026-11", cap=100
    )
    assert result == b"png-bytes"
    assert used_model == GEMINI_IMAGE_MODEL
    assert calls == [GEMINI_IMAGE_PRO_MODEL, GEMINI_IMAGE_MODEL]
    # Count incremented 10 -> 11 before call, then decremented 11 -> 10 on failure.
    assert db.store["system_metrics/image_gen_quota_2026-11"]["pro_count"] == 10


def test_none_db_defaults_to_flash_image():
    model, count, reserved_pro, _ = router.reserve_image_model(None, month_key="2026-11")
    assert model == GEMINI_IMAGE_MODEL
    assert count == 0
    assert reserved_pro is False
