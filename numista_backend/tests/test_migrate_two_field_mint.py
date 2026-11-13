"""Unit tests for `migrate_two_field_mint.py` (dry-run, execute backup, and rollback)."""

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from numista_backend.scripts.migrate_two_field_mint import (
    main as migrate_main,
    run_forward,
    run_prune_legacy_key,
    run_rollback,
)

DELETE_SENTINEL = object()


class _FakeRef:
    def __init__(self, db, path: str):
        self._db = db
        self.path = path

    def update(self, payload: dict):
        doc = self._db.docs[self.path]
        for k, v in payload.items():
            if v is DELETE_SENTINEL:
                doc.pop(k, None)
            else:
                doc[k] = v


class _FakeSnap:
    def __init__(self, db, path: str, data: dict):
        self.reference = _FakeRef(db, path)
        self._data = data

    def to_dict(self):
        return dict(self._data)


class _FakeQuery:
    def __init__(self, db, docs: list[tuple[str, dict]]):
        self._db = db
        self._docs = docs

    def limit(self, n: int):
        return _FakeQuery(self._db, self._docs[:n])

    def stream(self):
        return [_FakeSnap(self._db, p, d) for p, d in self._docs]


class _FakeBatch:
    def __init__(self):
        self.ops = []

    def update(self, ref: _FakeRef, payload: dict):
        self.ops.append((ref, payload))

    def commit(self):
        for ref, payload in self.ops:
            ref.update(payload)
        self.ops.clear()


class _FakeDB:
    def __init__(self, docs: dict[str, dict]):
        self.docs = docs

    def collection_group(self, name: str):
        assert name == "coins"
        return _FakeQuery(self, list(self.docs.items()))

    def document(self, path: str):
        return _FakeRef(self, path)

    def batch(self):
        return _FakeBatch()


def test_dry_run_makes_zero_mutations(tmp_path):
    db = _FakeDB({
        "users/a@b.com/coins/c1": {"Year": "1921", "Mint Mark": "", "Denomination": "Dollar", "Program/Series": "Morgan Dollars"},
        "users/a@b.com/coins/c2": {"Year": "2026", "Mint Mark": "", "Denomination": "Dollar", "Program/Series": "Morgan Dollars", "Retailer Item No.": "26XE"},
    })
    res = run_forward(db, execute=False, backup_dir=tmp_path)
    assert res["mode"] == "dry-run"
    assert res["stats"]["would_update"] == 2
    assert "mint" not in db.docs["users/a@b.com/coins/c1"]
    assert "mint" not in db.docs["users/a@b.com/coins/c2"]


def test_execute_and_rollback_restores_exact_state(tmp_path):
    db = _FakeDB({
        "users/u1/coins/c1": {"Year": "1921", "Mint Mark": "", "Denomination": "Dollar", "Program/Series": "Morgan Dollars"},
        "users/u1/coins/c2": {"Year": "1921", "Mint Mark": "D", "Denomination": "Dollar", "Program/Series": "Morgan Dollars"},
    })
    exec_res = run_forward(db, execute=True, backup_dir=tmp_path)
    assert exec_res["mode"] == "execute"
    assert exec_res["stats"]["would_update"] == 2
    assert db.docs["users/u1/coins/c1"]["mint"] == "Philadelphia"
    assert db.docs["users/u1/coins/c1"]["mint_mark"] == ""
    assert db.docs["users/u1/coins/c2"]["mint"] == "Denver"
    assert db.docs["users/u1/coins/c2"]["mint_mark"] == "D"

    backup_file = Path(exec_res["backup_file"])
    assert backup_file.exists()

    # Verify idempotency on second run
    second = run_forward(db, execute=False, backup_dir=tmp_path)
    assert second["stats"].get("already_migrated") == 2
    assert second["stats"].get("would_update", 0) == 0

    # Verify rollback deletes newly added mint & mint_mark
    rb_res = run_rollback(db, backup_file, execute=True, delete_sentinel=DELETE_SENTINEL)
    assert rb_res["stats"]["restored"] == 2
    assert "mint" not in db.docs["users/u1/coins/c1"]
    assert "mint_mark" not in db.docs["users/u1/coins/c1"]
    assert db.docs["users/u1/coins/c2"]["Mint Mark"] == "D"


def test_prune_legacy_key_phase7(tmp_path):
    db = _FakeDB({
        "users/u1/coins/c1": {"Year": "1921", "mint": "Philadelphia", "mint_mark": "", "Mint Mark": ""},
    })
    res = run_prune_legacy_key(db, execute=True, delete_sentinel=DELETE_SENTINEL)
    assert res["stats"]["pruned"] == 1
    assert "Mint Mark" not in db.docs["users/u1/coins/c1"]
    assert db.docs["users/u1/coins/c1"]["mint"] == "Philadelphia"


def test_execute_without_confirm_token_blocks(monkeypatch):
    monkeypatch.setattr("numista_backend.scripts.migrate_two_field_mint._init_firestore", lambda: _FakeDB({}))
    rc = migrate_main(["--execute"])
    assert rc == 2
