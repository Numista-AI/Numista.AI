"""Plan.v2.2 §9 Gate 3: Concurrency, Idempotency & Free-Trial Quota Gate (`pytest numista_tests/test_catalog_add_race.py -v`)."""
import os
import sys

import pytest
from pydantic import ValidationError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "numista_backend")))

from catalog_models import CollectionAddRequest  # noqa: E402
from catalog_service import (  # noqa: E402
    FREE_TRIAL_ITEM_LIMIT,
    CatalogError,
    add_catalog_item_in_txn,
)
from tests.test_catalog_collection_routing import (  # noqa: E402
    FUGIO,
    MEDAL,
    MORGAN,
    NOTE,
    PHL1P,
    SPAN8R,
    FakeDb,
    FakeTx,
    count,
)


def test_two_tab_concurrent_add_and_idempotent_retry():
    """
    Two concurrent browser tabs adding the same nac_code with distinct idempotency keys
    allocate _SLOT1 and _SLOT2 without silent overwrite. Replaying either idempotency key
    returns the original slot with created=False and idempotent_replay=True.
    """
    db = FakeDb()

    tx1 = FakeTx(db)
    r1 = add_catalog_item_in_txn(
        tx1, db, "u1", MORGAN, 250, count(db), new_specimen=False, idempotency_key="tab-1-key"
    )
    assert r1["created"] is True
    assert r1["slot"] == 1
    assert r1["doc_id"] == f"{MORGAN}_SLOT1"

    tx2 = FakeTx(db)
    r2 = add_catalog_item_in_txn(
        tx2, db, "u1", MORGAN, 250, count(db), new_specimen=True, idempotency_key="tab-2-key"
    )
    assert r2["created"] is True
    assert r2["slot"] == 2
    assert r2["doc_id"] == f"{MORGAN}_SLOT2"

    # Replaying tab-1-key or tab-2-key returns original slot without allocating _SLOT3
    tx_retry1 = FakeTx(db)
    replay1 = add_catalog_item_in_txn(
        tx_retry1, db, "u1", MORGAN, 250, count(db), new_specimen=True, idempotency_key="tab-1-key"
    )
    assert replay1["created"] is False
    assert replay1["idempotent_replay"] is True
    assert replay1["doc_id"] == f"{MORGAN}_SLOT1"
    assert tx_retry1.creates == []

    tx_retry2 = FakeTx(db)
    replay2 = add_catalog_item_in_txn(
        tx_retry2, db, "u1", MORGAN, 250, count(db), new_specimen=True, idempotency_key="tab-2-key"
    )
    assert replay2["created"] is False
    assert replay2["idempotent_replay"] is True
    assert replay2["doc_id"] == f"{MORGAN}_SLOT2"
    assert tx_retry2.creates == []


def test_client_supplied_kind_slot_or_tier_rejected():
    """extra='forbid' on CollectionAddRequest rejects any client-supplied kind, slot, or tier."""
    for extra_field in ({"kind": "CN"}, {"slot": 99}, {"tier": "power_user"}, {"collection": "coins"}):
        with pytest.raises(ValidationError):
            CollectionAddRequest(nac_code=MORGAN, **extra_field)


def test_free_trial_5_item_server_enforcement():
    """Founder-confirmed 5-item free trial allows items 1..5 across all collections and blocks item 6 with 403 QUOTA_EXCEEDED."""
    assert FREE_TRIAL_ITEM_LIMIT == 5
    db = FakeDb()
    five_items = [MORGAN, NOTE, MEDAL, FUGIO, PHL1P]
    for nac in five_items:
        tx = FakeTx(db)
        res = add_catalog_item_in_txn(tx, db, "u1", nac, FREE_TRIAL_ITEM_LIMIT, count(db))
        assert res["created"] is True

    tx6 = FakeTx(db)
    with pytest.raises(CatalogError) as exc:
        add_catalog_item_in_txn(tx6, db, "u1", SPAN8R, FREE_TRIAL_ITEM_LIMIT, count(db))
    assert exc.value.status_code == 403
    assert exc.value.code == "QUOTA_EXCEEDED"
    assert exc.value.extra == {"count": 5, "limit": 5}
