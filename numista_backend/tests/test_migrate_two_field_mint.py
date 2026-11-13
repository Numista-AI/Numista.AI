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

    def get(self):
        class _S:
            pass

        s = _S()
        s.exists = self.path in self._db.docs
        s.to_dict = lambda: dict(self._db.docs.get(self.path, {}))
        return s


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


# ---------------------------------------------------------------------------
# v2 regression fixtures (BUILD_REVIEW F1, F3, F4)
# ---------------------------------------------------------------------------
from numista_backend.scripts.migrate_two_field_mint import compute_migration_update  # noqa: E402


def test_f1_canada_existing_mint_preserved():
    payload, rule, _ = compute_migration_update(
        {"mint": "Royal Canadian Mint", "Year": "2020", "Country": "Canada"}
    )
    assert payload["mint"] == "Royal Canadian Mint"
    assert rule == 11


def test_f1_us_d_1900_keeps_existing_denver():
    payload, _, _ = compute_migration_update(
        {"mint": "Denver", "Mint Mark": "D", "Year": "1900", "Country": "United States"}
    )
    assert payload["mint"] == "Denver"
    assert payload["mint_mark"] == "D"


def test_f1_us_existing_facility_no_mark_preserved():
    payload, _, _ = compute_migration_update(
        {"mint": "San Francisco", "Mint Mark": "", "Year": "1990", "Strike Type": "Proof"}
    )
    assert payload["mint"] == "San Francisco"


def test_f1_facility_name_in_mark_field_becomes_facility():
    payload, _, _ = compute_migration_update(
        {"Mint Mark": "Denver", "Year": "1990", "Country": "United States"}
    )
    assert payload["mint"] == "Denver"
    assert payload["mint_mark"] == ""


def test_f3_rollback_deletes_legacy_key_it_created(tmp_path):
    db = _FakeDB({"users/u1/coins/c1": {"Year": "1921", "Denomination": "Dollar", "Program/Series": "Morgan Dollars"}})
    res = run_forward(db, execute=True, backup_dir=tmp_path)
    assert "Mint Mark" in db.docs["users/u1/coins/c1"]
    run_rollback(db, res["backup_file"], execute=True, delete_sentinel=DELETE_SENTINEL)
    assert "Mint Mark" not in db.docs["users/u1/coins/c1"]
    assert "mint" not in db.docs["users/u1/coins/c1"]


def test_f3_rollback_skips_docs_edited_after_migration(tmp_path):
    db = _FakeDB({"users/u1/coins/c1": {"Year": "1921", "Mint Mark": "D", "Denomination": "Dollar", "Program/Series": "Morgan Dollars"}})
    res = run_forward(db, execute=True, backup_dir=tmp_path)
    db.docs["users/u1/coins/c1"]["mint"] = "Manually Edited"
    rb = run_rollback(db, res["backup_file"], execute=True, delete_sentinel=DELETE_SENTINEL)
    assert rb["stats"]["skipped_modified_since_migration"] == 1
    assert rb["stats"].get("restored", 0) == 0
    assert db.docs["users/u1/coins/c1"]["mint"] == "Manually Edited"
    forced = run_rollback(db, res["backup_file"], execute=True, delete_sentinel=DELETE_SENTINEL, force=True)
    assert forced["stats"]["restored"] == 1


def test_f4_backup_fsynced_before_each_commit(tmp_path, monkeypatch):
    import numista_backend.scripts.migrate_two_field_mint as mod

    events = []
    monkeypatch.setattr(mod.os, "fsync", lambda fd: events.append("fsync"))
    monkeypatch.setattr(mod, "BATCH_LIMIT", 2)
    docs = {f"users/u/coins/c{i}": {"Year": "1921", "Denomination": "Dollar", "Program/Series": "Morgan Dollars"} for i in range(3)}
    db = _FakeDB(docs)
    orig_batch = db.batch

    def traced_batch():
        b = orig_batch()
        orig_commit = b.commit
        b.commit = lambda: (events.append("commit"), orig_commit())[1]
        return b

    db.batch = traced_batch
    run_forward(db, execute=True, backup_dir=tmp_path)
    assert events == ["fsync", "commit", "fsync", "commit"]
