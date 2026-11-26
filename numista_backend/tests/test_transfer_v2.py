"""PLAN v1.2 Phase 1: transfer v2 (token/code claim, hashes, limiter, guards, lock on claim, Sold)."""
import json
import os
import sys
from datetime import timedelta

import pytest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from tests.fakes_firestore import FakeDB, item, seed_item  # noqa: E402
from services import allowance_service  # noqa: E402
from services import transfer_service as ts  # noqa: E402
from services.transfer_service import (  # noqa: E402
    ClaimRateLimited,
    claim_transfer,
    initiate_transfer,
    preview_transfer,
    recall_transfer,
    rotate_claim_code,
)

SENDER = "seller@example.com"
BUYER = "buyer@example.org"


@pytest.fixture
def db():
    d = FakeDB()
    seed_item(d, SENDER, "c1", Cost="$45.00", **{"Personal Notes": "bought from Uncle Joe", "Storage Location": "Safe 4"},
              greysheet_bid=123.45, greysheet_ask=130.10, greysheetGsid="99999", cpgRetail=150.0,
              priceLastUpdated="2026-11-25T00:00:00+00:00")
    return d


def make(db, **kw):
    return initiate_transfer(db=db, user_a_id=SENDER, item_ids=["c1"], version=2, **kw)


# ---------------------------------------------------------------- initiate / storage
def test_v2_stores_only_hashes_and_returns_secrets_once(db):
    res = make(db, transfer_type="sale_private")
    token, code = res["claim_token"], res["claim_code"]
    assert len(token) >= 21 and len(code) == 11 and code[5] == "-"
    stored = json.dumps(db.store, default=str)
    assert token not in stored, "raw token must never be stored"
    assert code not in stored and code.replace("-", "") not in stored, "raw code must never be stored"
    doc = db.store[f"transfers/{res['transfer_id']}"]
    assert "claim_pin" not in doc
    assert doc["claim_token_hash"] and doc["claim_code_hash"] and doc["version"] == 2
    assert len(doc["claim_lookup_ids"]) == 2
    for h in doc["claim_lookup_ids"]:
        assert f"transfer_claims/{h}" in db.store
    assert "document_pdf_b64" in res


def test_v2_privacy_defaults_hide_everything_and_strip_licensed_pricing(db):
    res = make(db)
    payload = res["items"][0]
    for gone in ("Cost", "Personal Notes", "Storage Location", "greysheet_bid", "greysheet_ask",
                 "greysheetGsid", "cpgRetail", "priceLastUpdated"):
        assert gone not in payload, f"{gone} leaked into the transfer payload"
    assert payload["Year"] == "1921"


def test_v1_default_behavior_is_unchanged(db):
    res = initiate_transfer(db=db, user_a_id=SENDER, item_ids=["c1"])
    assert res["claim_pin"].isdigit() and len(res["claim_pin"]) == 6
    assert "version" not in res


def test_expiry_choices_and_validation(db):
    assert make(db, expires_days=7)["expires_days"] == 7
    with pytest.raises(ValueError):
        initiate_transfer(db=db, user_a_id=SENDER, item_ids=["c1"], version=2, expires_days=45)
    with pytest.raises(ValueError):
        initiate_transfer(db=db, user_a_id=SENDER, item_ids=["c1"], version=2, transfer_type="barter")


# ---------------------------------------------------------------- guards (F9)
@pytest.mark.parametrize("fields,word", [
    ({"is_demo": True}, "demo"),
    ({"is_demo_cleared": True}, "demo"),
    ({"status": "sold"}, "Sold"),
    ({"locked_pending_upgrade": True}, "locked"),
    ({"ebay_listing": {"status": "published"}}, "eBay listing"),
])
def test_guards_block_transfer(db, fields, word):
    seed_item(db, SENDER, "g1", **fields)
    with pytest.raises(ValueError) as e:
        initiate_transfer(db=db, user_a_id=SENDER, item_ids=["g1"], version=2)
    assert word in str(e.value)
    assert item(db, SENDER, "g1").get("transferStatus") == "none", "a refused item must not be locked"


def test_world_items_are_not_supported(db):
    seed_item(db, SENDER, "w1", subcol="world_items")
    with pytest.raises(ValueError, match="not found"):
        initiate_transfer(db=db, user_a_id=SENDER, item_ids=["w1"], version=2)


# ---------------------------------------------------------------- claim
def test_claim_by_token_happy_path_no_pii(db):
    res = make(db, transfer_type="gift", sender_display="Eric S.")
    out = claim_transfer(db=db, user_b_id=BUYER, claim_token=res["claim_token"], uid="uid-buyer")
    assert out["items_claimed_count"] == 1 and out["status"] == "claimed"
    mine = [v for k, v in db.store.items() if k.startswith(f"users/{BUYER}/coins/")]
    assert len(mine) == 1
    blob = json.dumps(mine[0], default=str)
    assert SENDER not in blob and "seller@" not in blob, "sender e-mail must not reach the recipient"
    ledger = mine[0]["provenanceLedger"][-1]
    assert ledger["from_user"].startswith("NUM-") and ledger["to_user"].startswith("NUM-")
    assert mine[0]["is_demo"] is False and mine[0]["is_demo_cleared"] is False
    assert "Cost" not in mine[0] and "greysheet_bid" not in mine[0]
    arch = db.store[f"users/{SENDER}/transferred_coins/c1"]
    assert arch["transferStatus"] == "transferred" and arch["transfer_status"] == "transferred"
    assert item(db, SENDER, "c1") is None
    assert not any(k.startswith("transfer_claims/") for k in db.store), "lookups die with the claim"


@pytest.mark.parametrize("mangle", [lambda c: c, lambda c: c.lower(), lambda c: c.replace("-", ""),
                                    lambda c: c.replace("0", "O").replace("1", "l")])
def test_claim_by_code_accepts_typing_variants(db, mangle):
    res = make(db)
    out = claim_transfer(db=db, user_b_id=BUYER, claim_code=mangle(res["claim_code"]), uid="u")
    assert out["items_claimed_count"] == 1


def test_one_time_use_double_claim(db):
    res = make(db)
    claim_transfer(db=db, user_b_id=BUYER, claim_token=res["claim_token"], uid="u1")
    with pytest.raises(ValueError, match="Code not found or expired"):
        claim_transfer(db=db, user_b_id="other@example.net", claim_token=res["claim_token"], uid="u2")
    mine = [k for k in db.store if k.startswith(f"users/{BUYER}/coins/")]
    assert len(mine) == 1
    # Even with the lookup gone, the transfer status itself refuses a second claim.
    tid = res["transfer_id"]
    assert db.store[f"transfers/{tid}"]["status"] == "claimed"
    with pytest.raises(ValueError, match="cannot be claimed"):
        claim_transfer(db=db, user_b_id="other@example.net", transfer_id=tid, claim_pin="000000")


def test_expired_transfer_is_refused(db):
    res = make(db)
    tid = res["transfer_id"]
    past = (ts._get_utc_now() - timedelta(days=1)).isoformat()
    db.store[f"transfers/{tid}"]["expires_at"] = past          # transfer expired, lookup still live
    with pytest.raises(ValueError, match="expired"):
        claim_transfer(db=db, user_b_id=BUYER, claim_token=res["claim_token"], uid="u")
    assert not any(k.startswith(f"users/{BUYER}/coins/") for k in db.store)
    for h in db.store[f"transfers/{tid}"]["claim_lookup_ids"]:
        db.store[f"transfer_claims/{h}"]["expires_at"] = past   # lookup expired too
    with pytest.raises(ValueError, match="Code not found or expired"):
        claim_transfer(db=db, user_b_id=BUYER, claim_code=res["claim_code"], uid="u")


def test_cancel_kills_qr_and_code_and_frees_item(db):
    res = make(db)
    recall_transfer(db=db, user_a_id=SENDER, transfer_id=res["transfer_id"])
    assert item(db, SENDER, "c1")["transferStatus"] == "none"
    for secret in ({"claim_token": res["claim_token"]}, {"claim_code": res["claim_code"]}):
        with pytest.raises(ValueError, match="Code not found or expired"):
            claim_transfer(db=db, user_b_id=BUYER, uid="u", **secret)
    done = make(db)
    claim_transfer(db=db, user_b_id=BUYER, claim_token=done["claim_token"], uid="u")
    with pytest.raises(ValueError, match="Cannot recall"):
        recall_transfer(db=db, user_a_id=SENDER, transfer_id=done["transfer_id"])


def test_recipient_email_lock_still_applies_to_token_claims(db):
    res = make(db, recipient_email="only@example.com")
    with pytest.raises(ValueError, match="locked to a different account"):
        claim_transfer(db=db, user_b_id=BUYER, claim_token=res["claim_token"], uid="u")
    out = claim_transfer(db=db, user_b_id="only@example.com", claim_token=res["claim_token"], uid="u2")
    assert out["items_claimed_count"] == 1


def test_v2_transfer_cannot_be_claimed_with_a_guessed_pin(db):
    res = make(db)
    with pytest.raises(ValueError, match="Invalid claim PIN"):
        claim_transfer(db=db, user_b_id=BUYER, transfer_id=res["transfer_id"], claim_pin="123456")


# ---------------------------------------------------------------- brute-force limits (S2)
def test_per_uid_limit_after_ten_failures_and_real_claim_unaffected(db):
    good = make(db)
    for i in range(10):
        with pytest.raises(ValueError, match="Code not found or expired"):
            claim_transfer(db=db, user_b_id="attacker@x.com", claim_code=f"ABCDE-FGH{i:02d}", uid="att", client_ip="9.9.9.9")
    with pytest.raises(ClaimRateLimited):
        claim_transfer(db=db, user_b_id="attacker@x.com", claim_code="ABCDE-FGH99", uid="att", client_ip="9.9.9.9")
    out = claim_transfer(db=db, user_b_id=BUYER, claim_token=good["claim_token"], uid="real", client_ip="1.2.3.4")
    assert out["items_claimed_count"] == 1, "no per-transfer lock: the real recipient is not locked out"


def test_per_ip_limit_across_many_uids(db):
    for i in range(30):
        with pytest.raises(ValueError):
            claim_transfer(db=db, user_b_id=f"u{i}@x.com", claim_token=f"bad-{i}", uid=f"uid{i}", client_ip="8.8.8.8")
    with pytest.raises(ClaimRateLimited):
        claim_transfer(db=db, user_b_id="u31@x.com", claim_token="bad-31", uid="uid31", client_ip="8.8.8.8")


def test_limiter_outage_fails_closed(db):
    res = make(db)
    db.fail_prefixes.append("_rate_limits")
    with pytest.raises(ClaimRateLimited):
        claim_transfer(db=db, user_b_id=BUYER, claim_token=res["claim_token"], uid="u", client_ip="1.1.1.1")
    assert not any(k.startswith(f"users/{BUYER}/coins/") for k in db.store), "outage must block, never open"


def test_limiter_keys_follow_documented_schema(db):
    with pytest.raises(ValueError):
        claim_transfer(db=db, user_b_id="a@b.c", claim_token="nope", uid="uid-1", client_ip="5.5.5.5")
    keys = [k for k in db.store if k.startswith("_rate_limits/")]
    assert len(keys) == 2
    assert all("/claim_attempt/" in k for k in keys)
    assert any(k.startswith("_rate_limits/uid_") for k in keys) and any(k.startswith("_rate_limits/ip_") for k in keys)
    assert "uid-1" not in " ".join(keys) and "5.5.5.5" not in " ".join(keys), "identifiers are hashed"


# ---------------------------------------------------------------- preview / rotate
def test_preview_returns_titles_only(db):
    res = make(db, sender_display="Eric S.", sender_address="1 Main St")
    out = preview_transfer(db=db, user_id=BUYER, claim_token=res["claim_token"], uid="u")
    blob = json.dumps(out)
    assert out["items"][0]["title"].startswith("1921")
    for forbidden in ("Eric", "Main St", "seller", "Cost", "NUM-", "sale_price"):
        assert forbidden not in blob


def test_rotate_invalidates_old_secrets(db):
    res = make(db)
    new = rotate_claim_code(db=db, user_a_id=SENDER, transfer_id=res["transfer_id"])
    with pytest.raises(ValueError, match="Code not found or expired"):
        claim_transfer(db=db, user_b_id=BUYER, claim_token=res["claim_token"], uid="u")
    out = claim_transfer(db=db, user_b_id=BUYER, claim_code=new["claim_code"], uid="u")
    assert out["items_claimed_count"] == 1


def test_rotate_upgrades_a_legacy_pin_transfer(db):
    legacy = initiate_transfer(db=db, user_a_id=SENDER, item_ids=["c1"])
    new = rotate_claim_code(db=db, user_a_id=SENDER, transfer_id=legacy["transfer_id"])
    doc = db.store[f"transfers/{legacy['transfer_id']}"]
    assert "claim_pin" not in doc and doc["version"] == 2 and doc["sender_ref"].startswith("NUM-")
    with pytest.raises(ValueError):
        claim_transfer(db=db, user_b_id=BUYER, transfer_id=legacy["transfer_id"], claim_pin=legacy["claim_pin"])
    assert claim_transfer(db=db, user_b_id=BUYER, claim_token=new["claim_token"], uid="u")["status"] == "claimed"


def test_rotate_is_sender_only(db):
    res = make(db)
    with pytest.raises(ValueError, match="Only the transfer sender"):
        rotate_claim_code(db=db, user_a_id="intruder@x.com", transfer_id=res["transfer_id"])


# ---------------------------------------------------------------- D2: Free recipient over 10
def _fill(db, user, n, **extra):
    for i in range(n):
        seed_item(db, user, f"own{i:02d}", created_at=f"2026-02-{i + 1:02d}T00:00:00+00:00", **extra)


def test_d2_free_with_10_claims_1_gets_11_with_newest_locked(db, monkeypatch):
    monkeypatch.setattr(allowance_service, "resolve_coin_limit", lambda **k: 10)
    _fill(db, BUYER, 10)
    res = make(db)
    out = claim_transfer(db=db, user_b_id=BUYER, claim_token=res["claim_token"], uid="free-user")
    mine = {k.rsplit("/", 1)[1]: v for k, v in db.store.items() if k.startswith(f"users/{BUYER}/coins/")}
    assert len(mine) == 11, "the claim must succeed: nothing refused, nothing lost"
    claimed_id = out["claimed_items"][0]["id"]
    assert mine[claimed_id]["locked_pending_upgrade"] is True
    assert sum(1 for v in mine.values() if v.get("locked_pending_upgrade")) == 1
    assert all(not mine[f"own{i:02d}"].get("locked_pending_upgrade") for i in range(10)), "oldest 10 stay open"
    assert out["locked"] is True and "locked until you upgrade" in out["message"]


def test_d2_demo_and_sold_items_do_not_use_slots(db, monkeypatch):
    monkeypatch.setattr(allowance_service, "resolve_coin_limit", lambda **k: 10)
    _fill(db, BUYER, 9)
    seed_item(db, BUYER, "demo1", is_demo=True)
    seed_item(db, BUYER, "demo2", is_demo=True, is_demo_cleared=True)
    seed_item(db, BUYER, "sold1", status="sold", transferStatus="sold")
    res = make(db)
    out = claim_transfer(db=db, user_b_id=BUYER, claim_token=res["claim_token"], uid="free-user")
    assert out["locked"] is False, "9 real + 1 claimed = 10: within the limit"
    assert not any(v.get("locked_pending_upgrade") for k, v in db.store.items() if k.startswith(f"users/{BUYER}/coins/"))


def test_d2_founding_beta_unlimited_never_locks(db, monkeypatch):
    monkeypatch.setattr(allowance_service, "resolve_coin_limit", lambda **k: None)
    _fill(db, BUYER, 40)
    res = make(db)
    out = claim_transfer(db=db, user_b_id=BUYER, claim_token=res["claim_token"], uid="beta")
    assert out["locked"] is False
    assert not any(v.get("locked_pending_upgrade") for k, v in db.store.items() if k.startswith(f"users/{BUYER}/coins/"))


def test_d2_lock_failure_never_undoes_the_claim(db, monkeypatch):
    def boom(**k):
        raise RuntimeError("entitlement backend down")
    monkeypatch.setattr(allowance_service, "resolve_coin_limit", boom)
    res = make(db)
    out = claim_transfer(db=db, user_b_id=BUYER, claim_token=res["claim_token"], uid="u")
    assert out["status"] == "claimed" and out["locked"] is False
    assert any(k.startswith(f"users/{BUYER}/coins/") for k in db.store)
