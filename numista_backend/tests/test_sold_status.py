"""PLAN v1.2: Mark Sold, never delete (R3/D4), sold_item transfers (section 4.3), F15 retention."""
import os
import sys

import pytest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from tests.fakes_firestore import FakeDB, item, seed_item  # noqa: E402
from services import allowance_service  # noqa: E402
from services.transfer_service import (  # noqa: E402
    claim_transfer,
    harden_legacy_pins,
    hash_legacy_pin,
    initiate_transfer,
    recall_transfer,
    record_direct_sale,
    undo_sale,
)

U = "seller@example.com"
BUYER = "buyer@example.org"
PRICING = dict(greysheet_bid=123.45, greysheet_ask=130.10, greysheetGsid="99999", cpgRetail=150.0,
               priceLastUpdated="2026-11-25T00:00:00+00:00")


@pytest.fixture
def db():
    d = FakeDB()
    # Any delete of an item doc is a bug under R3: make the fake refuse it.
    d.no_delete_prefixes.append(f"users/{U}/coins/")
    return d


def sell_all(db, item_id="c1", qty=1, **kw):
    return record_direct_sale(db=db, user_id=U, coin_id=item_id, qty_sold=qty, sale_price_usd=100.0,
                              fees_usd=10.0, sales_venue="eBay", **kw)


def test_full_sale_keeps_the_doc_marked_sold_and_never_deletes(db):
    seed_item(db, U, "c1", Cost="$40.00", Quantity=1, **PRICING)
    res = sell_all(db)                      # would raise AssertionError if anything deleted the doc
    doc = item(db, U, "c1")
    assert doc is not None
    assert doc["status"] == "sold" and doc["transferStatus"] == "sold"
    assert doc["sale_archive_id"] == res["sale_archive_id"] and doc["sold_qty"] == 1
    assert res["item_kept_as_sold"] is True
    arch = db.store[f"users/{U}/transferred_coins/{res['sale_archive_id']}"]
    assert arch["status"] == "sold" and arch["realized_profit_cents"] == 5000  # 100 - 10 - 40
    assert res["realized_profit"] == 50.0


def test_f15_archive_row_has_no_licensed_pricing_fields(db):
    seed_item(db, U, "c1", Cost="$40.00", **PRICING)
    res = sell_all(db)
    arch = db.store[f"users/{U}/transferred_coins/{res['sale_archive_id']}"]
    for k in ("greysheet_bid", "greysheet_ask", "greysheetGsid", "cpgRetail", "priceLastUpdated"):
        assert k not in arch, f"{k} copied into a long-lived archive row"
    assert arch["sale_price_usd"] == 100.0  # the user's own sale data is kept


def test_partial_sale_keeps_item_active_without_sold_marker(db):
    seed_item(db, U, "c1", Cost="$10.00", Quantity=3)
    res = sell_all(db, qty=1)
    doc = item(db, U, "c1")
    assert doc["Quantity"] == 2 and "status" not in doc
    assert res["item_kept_as_sold"] is False and res["remaining_qty"] == 2


def test_cannot_sell_twice_or_sell_a_pending_item(db):
    seed_item(db, U, "c1")
    sell_all(db)
    with pytest.raises(ValueError, match="already marked Sold"):
        sell_all(db)
    seed_item(db, U, "c2", transferStatus="pending")
    with pytest.raises(ValueError, match="pending transfer"):
        sell_all(db, item_id="c2")


def test_undo_restores_the_kept_doc_and_voids_the_archive_row(db):
    seed_item(db, U, "c1", Cost="$40.00")
    res = sell_all(db)
    out = undo_sale(db=db, user_id=U, sale_archive_id=res["sale_archive_id"])
    assert out["status"] == "success"
    doc = item(db, U, "c1")
    for gone in ("status", "sold_at", "sold_qty", "sale_archive_id"):
        assert gone not in doc
    assert doc["transferStatus"] == "none" and doc["Quantity"] == 1
    assert db.store[f"users/{U}/transferred_coins/{res['sale_archive_id']}"]["status"] == "voided"


def test_undo_legacy_sale_whose_doc_was_deleted_still_resurrects(db):
    """Sales recorded before this build removed the item; undo must keep working for them."""
    seed_item(db, U, "c1", Cost="$40.00")
    res = sell_all(db)
    db.no_delete_prefixes.clear()
    db.store.pop(f"users/{U}/coins/c1")        # simulate the legacy full-sale delete
    out = undo_sale(db=db, user_id=U, sale_archive_id=res["sale_archive_id"])
    assert out["restored_qty"] == 1
    assert item(db, U, "c1")["transferStatus"] == "none"


def test_undo_refused_while_a_buyer_transfer_is_pending(db):
    seed_item(db, U, "c1")
    res = sell_all(db)
    t = initiate_transfer(db=db, user_a_id=U, item_ids=["c1"], version=2, source="sold_item", transfer_type="sale_ebay")
    with pytest.raises(ValueError, match="Cancel the pending transfer"):
        undo_sale(db=db, user_id=U, sale_archive_id=res["sale_archive_id"])
    recall_transfer(db=db, user_a_id=U, transfer_id=t["transfer_id"])
    assert undo_sale(db=db, user_id=U, sale_archive_id=res["sale_archive_id"])["status"] == "success"


# ---------------------------------------------------------------- Sold + count / lock
def test_sold_items_never_count_and_are_never_locked():
    flags = allowance_service.compute_lock_flags([
        ("a", {"created_at": "2026-01-01T00:00:00+00:00"}),
        ("b", {"created_at": "2026-01-02T00:00:00+00:00"}),
        ("s", {"created_at": "2026-01-03T00:00:00+00:00", "status": "sold", "transferStatus": "sold"}),
        ("c", {"created_at": "2026-01-04T00:00:00+00:00"}),
    ], limit=2)
    assert flags == {"a": False, "b": False, "s": False, "c": True}


def test_g2_doc_matching_several_exclusions_is_judged_once():
    docs = [("d", {"is_demo": True, "is_demo_cleared": True, "status": "sold", "created_at": "2026-01-01T00:00:00+00:00"}),
            ("x", {"created_at": "2026-01-02T00:00:00+00:00"}), ("y", {"created_at": "2026-01-03T00:00:00+00:00"})]
    flags = allowance_service.compute_lock_flags(docs, limit=2)
    assert flags == {"d": False, "x": False, "y": False}, "excluded exactly once: 2 eligible items fit the limit of 2"


def test_g2_sold_item_inside_a_buyer_transfer_stays_excluded(db):
    seed_item(db, U, "c1", created_at="2026-01-01T00:00:00+00:00")
    sell_all(db)
    initiate_transfer(db=db, user_a_id=U, item_ids=["c1"], version=2, source="sold_item", transfer_type="sale_ebay")
    doc = item(db, U, "c1")
    assert doc["status"] == "sold" and doc["transferStatus"] == "pending"
    assert allowance_service.is_eligible_item(doc) is False


def test_lock_is_idempotent_and_unlocks_when_limit_is_lifted():
    d = FakeDB()
    for i in range(12):
        seed_item(d, BUYER, f"k{i:02d}", created_at=f"2026-03-{i + 1:02d}T00:00:00+00:00")
    r1 = allowance_service.apply_free_overflow_lock(d, user_key=BUYER, uid="u", limit_resolver=lambda: 10)
    assert len(r1["locked_ids"]) == 2
    snapshot = {k: dict(v) for k, v in d.store.items()}
    r2 = allowance_service.apply_free_overflow_lock(d, user_key=BUYER, uid="u", limit_resolver=lambda: 10)
    assert d.store == snapshot and r2["locked_ids"] == r1["locked_ids"]
    r3 = allowance_service.apply_free_overflow_lock(d, user_key=BUYER, uid="u", limit_resolver=lambda: None)
    assert r3["locked_ids"] == [] and len(r3["unlocked_ids"]) == 2


# ---------------------------------------------------------------- sold_item transfer (the buyer)
def test_sold_item_claim_leaves_sender_doc_sold_and_sale_row_untouched(db):
    seed_item(db, U, "c1", Cost="$40.00", **PRICING)
    sale = sell_all(db)
    t = initiate_transfer(db=db, user_a_id=U, item_ids=["c1"], version=2, source="sold_item", transfer_type="sale_ebay")
    assert not any(k.startswith(f"users/{U}/transferred_coins/") and k.endswith("/c1") for k in db.store), \
        "no second pending archive row for a sold item"
    sale_row_before = dict(db.store[f"users/{U}/transferred_coins/{sale['sale_archive_id']}"])
    out = claim_transfer(db=db, user_b_id=BUYER, claim_token=t["claim_token"], uid="b")   # no delete may happen
    assert out["items_claimed_count"] == 1
    sender_doc = item(db, U, "c1")
    assert sender_doc["status"] == "sold" and sender_doc["transferStatus"] == "sold"
    assert sender_doc["claimed_by_ref"].startswith("NUM-") and "claimed_at" in sender_doc
    assert db.store[f"users/{U}/transferred_coins/{sale['sale_archive_id']}"] == sale_row_before
    bought = [v for k, v in db.store.items() if k.startswith(f"users/{BUYER}/coins/")][0]
    assert "status" not in bought and "sale_archive_id" not in bought, "Sold state must not travel to the buyer"
    assert bought["transferStatus"] == "active" and "greysheet_bid" not in bought


def test_cancelling_a_sold_item_transfer_returns_it_to_sold_not_active(db):
    seed_item(db, U, "c1")
    sell_all(db)
    t = initiate_transfer(db=db, user_a_id=U, item_ids=["c1"], version=2, source="sold_item")
    recall_transfer(db=db, user_a_id=U, transfer_id=t["transfer_id"])
    doc = item(db, U, "c1")
    assert doc["status"] == "sold" and doc["transferStatus"] == "sold"


def test_sold_item_transfer_requires_a_sold_item_and_regular_transfer_refuses_one(db):
    seed_item(db, U, "c1")
    with pytest.raises(ValueError, match="not marked Sold"):
        initiate_transfer(db=db, user_a_id=U, item_ids=["c1"], version=2, source="sold_item")
    sell_all(db)
    with pytest.raises(ValueError, match="marked Sold"):
        initiate_transfer(db=db, user_a_id=U, item_ids=["c1"], version=2)
    with pytest.raises(ValueError, match="requires a v2"):
        initiate_transfer(db=db, user_a_id=U, item_ids=["c1"], source="sold_item")


# ---------------------------------------------------------------- N4 legacy PIN hardening
def test_harden_legacy_pins_dry_run_changes_nothing_then_apply_hashes(monkeypatch):
    monkeypatch.setenv("TRANSFER_CLAIM_PEPPER", "test-pepper")
    d = FakeDB()
    seed_item(d, U, "c1")
    legacy = initiate_transfer(db=d, user_a_id=U, item_ids=["c1"])
    before = {k: dict(v) for k, v in d.store.items()}
    dry = harden_legacy_pins(d, apply=False)
    assert dry["eligible"] == 1 and dry["hardened"] == 0 and d.store == before
    out = harden_legacy_pins(d, apply=True)
    assert out["hardened"] == 1
    doc = d.store[f"transfers/{legacy['transfer_id']}"]
    assert "claim_pin" not in doc and doc["claim_pin_hash"] and doc["claim_pin_salt"]
    assert legacy["claim_pin"] not in str(d.store)
    assert doc["claim_pin_hash"] == hash_legacy_pin(legacy["claim_pin"], doc["claim_pin_salt"])
    assert harden_legacy_pins(d, apply=True)["eligible"] == 0, "idempotent"
    got = claim_transfer(db=d, user_b_id=BUYER, transfer_id=legacy["transfer_id"], claim_pin=legacy["claim_pin"])
    assert got["status"] == "claimed", "the old PIN still claims through its hash"


def test_hardening_cli_refuses_apply_without_a_deploy_card():
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(backend_dir, "scripts", "harden_legacy_transfer_pins.py"), "--apply"],
                       capture_output=True, text=True)
    assert r.returncode == 2 and "REFUSED" in r.stdout
