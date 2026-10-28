"""Catalog schema + transactional collection-add routing gate (Plan.v2 sections 2.3, 3.1, 3.2)."""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from catalog_models import CatalogItem, Specifications  # noqa: E402
from catalog_service import CatalogError, add_catalog_item_in_txn, filter_catalog  # noqa: E402

FIXTURE = os.path.join(os.path.dirname(__file__), "..", "data", "catalog_dev_fixture.json")
with open(FIXTURE, encoding="utf-8") as _f:
    ITEMS = {i["nac_code"]: i for i in json.load(_f)}

MORGAN = "NAC1.CN.US.1D.MORGAN.1881.S.BASE.E"
NOTE = "NAC1.BN.US.SC5.SILV.1899.BEP.BASE.A"
MEDAL = "NAC1.MD.US.PRES.PRES.1923.P.COOL.W"


# ── in-memory Firestore fakes ────────────────────────────────────────────────
class Snap:
    def __init__(self, ref_id, data):
        self.id, self._d = ref_id, data
        self.exists = data is not None

    def to_dict(self):
        return dict(self._d) if self._d is not None else None


class Ref:
    def __init__(self, store, path):
        self.store, self.path = store, path
        self.id = path.rsplit("/", 1)[-1]

    def collection(self, name):
        return Col(self.store, f"{self.path}/{name}")


class Col:
    def __init__(self, store, path):
        self.store, self.path = store, path

    def document(self, doc_id=None):
        doc_id = doc_id or f"auto{len(self.store)}"
        return Ref(self.store, f"{self.path}/{doc_id}")


class FakeDb:
    def __init__(self):
        self.store = {}
        for nac, it in ITEMS.items():
            self.store[f"us_numismatics_catalog/{nac}"] = it

    def collection(self, name):
        return Col(self.store, name)


class FakeTx:
    def __init__(self, db):
        self.db = db
        self.creates = []

    def get(self, ref):
        return Snap(ref.id, self.db.store.get(ref.path))

    def create(self, ref, doc):
        assert ref.path not in self.db.store, "create() must never overwrite"
        self.db.store[ref.path] = doc
        self.creates.append(ref.path)


def count(db):
    def _c(tx, col):
        return sum(1 for p in db.store if p.startswith(f"users/u1/{col}/"))
    return _c


def add(db, nac, limit=250, new=False):
    tx = FakeTx(db)
    return add_catalog_item_in_txn(tx, db, "u1", nac, limit, count(db), new), tx


# ── routing ──────────────────────────────────────────────────────────────────
def test_coin_goes_to_coins_with_slot1_doc_id_and_snapshot():
    db = FakeDb()
    r, _ = add(db, MORGAN)
    assert r["created"] and r["collection"] == "coins"
    assert r["doc_id"] == f"{MORGAN}_SLOT1"            # no {uid}_ prefix
    doc = db.store[f"users/u1/coins/{MORGAN}_SLOT1"]
    assert doc["nac_code"] == MORGAN
    assert doc["catalog_snapshot"]["title_at_acquire"] == "1881-S Morgan Silver Dollar"
    assert doc["catalog_snapshot"]["mintage_official_at_acquire"] == 12760000


def test_banknote_goes_to_currency_never_coins():
    db = FakeDb()
    r, _ = add(db, NOTE)
    assert r["collection"] == "currency"
    assert not [p for p in db.store if p.startswith("users/u1/coins/")]


def test_medal_goes_to_world_items_never_coins():
    db = FakeDb()
    r, _ = add(db, MEDAL)
    assert r["collection"] == "world_items"
    assert not [p for p in db.store if p.startswith("users/u1/coins/")]


def test_idempotent_replay_returns_existing_without_second_create():
    db = FakeDb()
    add(db, MORGAN)
    r, tx = add(db, MORGAN)
    assert r["created"] is False and tx.creates == []
    assert len([p for p in db.store if p.startswith("users/u1/coins/")]) == 1


def test_new_specimen_allocates_next_slot():
    db = FakeDb()
    add(db, MORGAN)
    r, _ = add(db, MORGAN, new=True)
    assert r["created"] and r["doc_id"] == f"{MORGAN}_SLOT2"
    r3, _ = add(db, MORGAN, new=True)
    assert r3["doc_id"] == f"{MORGAN}_SLOT3"


# ── spoofing guard ───────────────────────────────────────────────────────────
def test_invented_code_bad_checksum_400_and_no_write():
    db = FakeDb()
    with pytest.raises(CatalogError) as e:
        add(db, "NAC1.CN.US.1D.MORGAN.1881.S.BASE.F")
    assert e.value.status_code == 400 and e.value.code == "INVALID_NAC1_CHECKSUM"
    assert not [p for p in db.store if p.startswith("users/")]


def test_valid_checksum_but_unreleased_catalog_item_404():
    from catalog_nac1 import build_nac1
    db = FakeDb()
    ghost = build_nac1("NAC1.CN.US.1D.GHOST.1999.P.BASE")
    with pytest.raises(CatalogError) as e:
        add(db, ghost)
    assert e.value.status_code == 404 and e.value.code == "CATALOG_ITEM_NOT_FOUND"
    assert not [p for p in db.store if p.startswith("users/")]


def test_quota_exceeded_403_counts_across_all_collections():
    db = FakeDb()
    add(db, MORGAN, limit=2)
    add(db, NOTE, limit=2)
    with pytest.raises(CatalogError) as e:
        add(db, MEDAL, limit=2)
    assert e.value.status_code == 403 and e.value.code == "QUOTA_EXCEEDED"


def test_replay_at_quota_still_idempotent_not_403():
    db = FakeDb()
    add(db, MORGAN, limit=1)
    r, _ = add(db, MORGAN, limit=1)
    assert r["created"] is False


# ── schema ───────────────────────────────────────────────────────────────────
def test_every_fixture_row_is_a_valid_catalog_item():
    for it in ITEMS.values():
        CatalogItem(**it)


def test_fineness_requires_precious_metal_type():
    with pytest.raises(ValueError):
        Specifications(composition="Silver", fineness=0.9, precious_metal_type="NONE", alignment="COIN")
    Specifications(composition="Silver", fineness=0.9, precious_metal_type="SILVER", alignment="COIN")
    Specifications(composition="Clad", alignment="COIN")


def test_citation_required_and_kind_must_match_nac():
    row = dict(ITEMS[MORGAN])
    with pytest.raises(ValueError):
        CatalogItem(**{**row, "primary_citations": []})
    with pytest.raises(ValueError):
        CatalogItem(**{**row, "kind": "BN"})
    with pytest.raises(ValueError):
        CatalogItem(**{**row, "nac_code": "NAC1.CN.US.1D.MORGAN.1881.S.BASE.F"})


def test_mint_mark_consistency():
    row = dict(ITEMS[MORGAN])
    with pytest.raises(ValueError):
        CatalogItem(**{**row, "mint_mark_on_coin": False})  # mark present but flag false
    with pytest.raises(ValueError):
        CatalogItem(**{**row, "mint_mark": None})


def test_filter_by_state_facet_and_facility():
    items = list(ITEMS.values())
    assert {i["state_or_entity"] for i in filter_catalog(items, era="PRE_FEDERAL")} == {"CONTINENTAL", "CT"}
    assert [i["nac_code"] for i in filter_catalog(items, era="PRE_FEDERAL", state="CT")] == \
        ["NAC1.CN.PF.1C.CT.1787.XX.DRAPED.9"]
    assert [i["facility_code"] for i in filter_catalog(items, facility="DD")] == ["DD"]
    assert all(i["year"] <= 1900 for i in filter_catalog(items, max_year=1900))


# ── HTTP: public read + protected write (dev fixture mode) ───────────────────
def test_public_browse_no_auth_and_write_requires_auth(monkeypatch):
    monkeypatch.setenv("CATALOG_DEV_FIXTURE", "1")
    monkeypatch.delenv("ALLOW_UNAUTHENTICATED", raising=False)  # dev bypass must be off to prove 401
    from fastapi.testclient import TestClient
    from main import app

    client = TestClient(app, raise_server_exceptions=False)
    r = client.get("/api/v1/catalog?kind=CN&facility=S")
    assert r.status_code == 200, r.text
    assert {i["nac_code"] for i in r.json()["items"]} == {MORGAN, "NAC1.CN.PF.1P.USPI.1908.S.BASE.Z"}

    r = client.get(f"/api/v1/catalog/{MORGAN}")
    assert r.status_code == 200 and r.json()["canonical_slug"] == "coins/morgan-dollar/1881-s"
    assert client.get("/api/v1/catalog/NAC1.CN.US.1D.MORGAN.1881.S.BASE.F").status_code == 400
    assert client.get("/api/v1/catalog/resolve?slug=/coins/morgan-dollar/1881-s").status_code == 200

    w = client.post("/api/v1/collection/catalog-add", json={"nac_code": MORGAN})
    assert w.status_code == 401
