"""NET-827 CORE (webhook / entitlement) tests, plan v1.1.1 §9 (SHA-256 73d55380…c229).
All mocked: no network, Firestore, Stripe or Firebase. tier_gatekeeper.db and
routes.payment_routes.db are one in-memory FakeFirestore (§9.1); tier_gatekeeper._run_txn is
replaced by fake_run_txn (versioned docs, read set, commit-time check, Aborted retry up to 5)."""
import copy
import json
import os
import pathlib
import re
import subprocess
import threading
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
import stripe
from fastapi import HTTPException
from fastapi.testclient import TestClient
from google.api_core import exceptions as gexc
from google.cloud.firestore_v1.transforms import Increment

import tier_gatekeeper
from tier_gatekeeper import (
    TIER_COIN_LIMITS, PURCHASABLE_TIERS,
    PURCHASE_MODE, LIFETIME_PRICE_CENTS, _bigger, _item_limit, count_unique_coins,
    effective_limit, entitlement_ok, get_user_allowance, load_entitlement_profile,
    revoke_paid_tier, to_epoch, RevokeEmailUnresolved, RevokeResult,
)
from main import app                              # as tests/test_idor_fixes.py:18
from routes.deps import get_current_user          # as tests/test_idor_fixes.py:19

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_ATTEMPTS = 5                                   # google-cloud-firestore base_transaction.py:44


# ─── Fakes (§9.1) ────────────────────────────────────────────────────────────

def _apply_merge(dst, src):
    """Firestore set(merge=True): nested maps merged key by key; present None kept;
    Increment applied."""
    for k, v in src.items():
        if isinstance(v, Increment):
            dst[k] = (dst.get(k) or 0) + v.value
        elif isinstance(v, dict) and isinstance(dst.get(k), dict) and v:
            _apply_merge(dst[k], v)
        else:
            dst[k] = copy.deepcopy(v)


class FakeSnap:
    def __init__(self, ref, data):
        self.reference = ref
        self.id = ref.id
        self.exists = data is not None
        self._d = data

    def to_dict(self):
        return copy.deepcopy(self._d) if self._d is not None else None

    def get(self, field):
        return (self._d or {}).get(field)


class FakeRef:
    def __init__(self, db, path):
        self._db = db
        self.path = path
        self.id = path.rsplit("/", 1)[-1]

    def collection(self, name):
        return FakeCollection(self._db, f"{self.path}/{name}")

    def get(self, transaction=None):
        if transaction is not None:
            return transaction._read(self)
        return self._db._plain_get(self)

    def set(self, data, merge=False):
        self._db._check("set", self.path)
        with self._db.lock:
            self._db._apply("set", self.path, data, merge)

    def update(self, data):
        self._db._check("update", self.path)
        with self._db.lock:
            if self.path not in self._db.docs:
                raise gexc.NotFound(self.path)
            self._db._apply("update", self.path, data, True)

    def delete(self):
        self._db._check("delete", self.path)
        with self._db.lock:
            self._db._apply("delete", self.path, None, False)


class FakeQuery:
    def __init__(self, db, coll_path, flt):
        self._db, self._coll, self._flt = db, coll_path, flt

    def stream(self):
        f = self._flt
        assert f.op_string == "==", f.op_string        # FieldFilter public attrs (base_query.py:187+)
        self._db._check("where", self._coll)
        self._db._record("where", f"{self._coll}?{f.field_path}=={f.value}")
        return iter([s for s in self._db._children(self._coll)
                     if (s.to_dict() or {}).get(f.field_path) == f.value])


class FakeCollection:
    def __init__(self, db, path):
        self._db = db
        self.path = path

    def document(self, doc_id):
        return FakeRef(self._db, f"{self.path}/{doc_id}")

    def stream(self):
        self._db._check("stream", self.path)
        self._db._record("stream", self.path)
        return iter(self._db._children(self.path))

    def where(self, field_path=None, op_string=None, value=None, *, filter=None):
        assert filter is not None, "use where(filter=FieldFilter(...))"
        return FakeQuery(self._db, self.path, filter)


class FakeFirestore:
    def __init__(self):
        self.docs = {}
        self.versions = {}
        self.ops = []
        self.fail_on = {}
        self.fail_commit = None          # callable(txn) -> Exception or None
        self.after_read = None           # callable(kind, path, txn_or_None)
        self.aborts = 0
        self.txn_count = 0
        self.lock = threading.RLock()

    # API
    def collection(self, name):
        return FakeCollection(self, name)

    def document(self, path):
        return FakeRef(self, path)

    # internals
    def _check(self, op, path):
        for key in ((op, path), op, path):
            exc = self.fail_on.get(key)
            if exc is not None:
                raise exc

    def _record(self, op, path):
        with self.lock:
            self.ops.append((op, path))

    def _children(self, coll_path):
        with self.lock:
            out = []
            for p in sorted(self.docs):
                if p.startswith(coll_path + "/") and "/" not in p[len(coll_path) + 1:]:
                    out.append(FakeSnap(FakeRef(self, p), copy.deepcopy(self.docs[p])))
            return out

    def _plain_get(self, ref):
        self._check("get", ref.path)
        with self.lock:
            data = copy.deepcopy(self.docs.get(ref.path))
        self._record("get", ref.path)
        if self.after_read:
            self.after_read("plain", ref.path, None)
        return FakeSnap(ref, data)

    def _apply(self, op, path, data, merge):
        if op == "delete":
            self.docs.pop(path, None)
        elif op == "set" and not merge:
            d = {}
            _apply_merge(d, data)
            self.docs[path] = d
        else:
            d = self.docs.setdefault(path, {})
            _apply_merge(d, data)
        self.versions[path] = self.versions.get(path, 0) + 1
        self.ops.append((op, path))

    # test helpers
    def seed(self, path, data):
        with self.lock:
            self.docs[path] = copy.deepcopy(data)
            self.versions[path] = self.versions.get(path, 0) + 1

    def doc(self, path):
        return copy.deepcopy(self.docs.get(path))

    def writes(self, prefix=""):
        return [(op, p) for op, p in self.ops if op in ("set", "update", "delete") and p.startswith(prefix)]

    def seed_coins(self, owner, n, start=0, base_ts=1_700_000_000, prefix="c", folder="users"):
        for i in range(start, start + n):
            self.seed(f"{folder}/{owner}/coins/{prefix}{i:05d}",
                      {"name": f"coin {i}", "created_at": base_ts + i})

    def coin_ids(self, owner, folder="users"):
        return sorted(s.id for s in self._children(f"{folder}/{owner}/coins"))


class FakeTxn:
    def __init__(self, db, attempt):
        self.db = db
        self.attempt = attempt
        self.reads = {}
        self.buffer = []

    def _read(self, ref):
        if self.buffer:
            raise AssertionError(f"read after write in one transaction: {ref.path}")
        self.db._check("get", ref.path)
        with self.db.lock:
            data = copy.deepcopy(self.db.docs.get(ref.path))
            self.reads[ref.path] = self.db.versions.get(ref.path, 0)
        self.db._record("txn_get", ref.path)
        if self.db.after_read:
            self.db.after_read("txn", ref.path, self)
        return FakeSnap(ref, data)

    def get(self, ref):
        return self._read(ref)

    def set(self, ref, data, merge=False):
        self.buffer.append(("set", ref.path, copy.deepcopy(data), merge))

    def update(self, ref, data):
        self.buffer.append(("update", ref.path, copy.deepcopy(data), True))

    def delete(self, ref):
        self.buffer.append(("delete", ref.path, None, False))

    def commit(self):
        db = self.db
        with db.lock:
            if db.fail_commit is not None:
                exc = db.fail_commit(self)
                if exc is not None:
                    if isinstance(exc, gexc.Aborted):
                        db.aborts += 1
                    raise exc
            for path, ver in self.reads.items():
                if db.versions.get(path, 0) != ver:
                    db.aborts += 1
                    raise gexc.Aborted(f"contention on {path}")
            for op, path, data, merge in self.buffer:
                if op == "update" and path not in db.docs:
                    raise gexc.NotFound(path)
                db._apply(op, path, data, merge)


def fake_run_txn(db, fn):
    """Mirrors firestore.transactional (transaction.py:306, :311): re-run on Aborted up to
    MAX_ATTEMPTS, then ValueError. If fn raises, nothing from that attempt is applied."""
    last = None
    for attempt in range(MAX_ATTEMPTS):
        t = FakeTxn(db, attempt)
        with db.lock:
            db.txn_count += 1
        result = fn(t)
        try:
            t.commit()
            return result
        except gexc.Aborted as e:
            last = e
    raise ValueError(f"Failed to commit transaction in {MAX_ATTEMPTS} attempts.") from last


# ─── Auth fakes ──────────────────────────────────────────────────────────────

FOUNDER_MS = 1797310799999
POST_MS = 1797310800001


def _rec(created_ms, providers=1, email=None):
    rec = MagicMock(name="UserRecord")
    rec.user_metadata.creation_timestamp = created_ms
    rec.provider_data = [MagicMock() for _ in range(providers)]
    rec.email = email
    return rec


def FOUNDER(email=None):
    return _rec(FOUNDER_MS, email=email)


def POST(email=None):
    return _rec(POST_MS, email=email)


def GUEST(email=None):
    return _rec(FOUNDER_MS, providers=0, email=email)


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _isolate():
    tier_gatekeeper._auth_facts_by_uid.cache_clear()
    app.dependency_overrides.clear()
    yield
    tier_gatekeeper._auth_facts_by_uid.cache_clear()
    app.dependency_overrides.clear()


@pytest.fixture
def fdb():
    db = FakeFirestore()
    with patch.object(tier_gatekeeper, "db", db), \
         patch("routes.payment_routes.db", db), \
         patch("tier_gatekeeper._run_txn", fake_run_txn):
        yield db


@pytest.fixture
def recs():
    """RECS[uid] = UserRecord or an Exception to raise; unknown uid -> Exception('not found')."""
    table = {}

    def _get(uid):
        r = table.get(uid)
        if r is None:
            raise Exception("not found")
        if isinstance(r, Exception):
            raise r
        return r

    with patch("tier_gatekeeper.firebase_auth.get_user", side_effect=_get) as m:
        table["_mock"] = m
        yield table


NOW = 1_800_000_000.0


def _git_grep_count(pattern, path, fixed=True, extended=False):
    args = ["git", "grep", "-c"]
    if fixed:
        args.append("-F")
    if extended:
        args.append("-E")
    args += ["-e", pattern, "--", path]
    r = subprocess.run(args, cwd=BACKEND, capture_output=True, text=True)
    if r.returncode == 1:
        return 0
    assert r.returncode == 0, r.stderr
    return sum(int(line.rsplit(":", 1)[-1]) for line in r.stdout.splitlines() if line.strip())


# ═════════════════════════════════════════════════════════════════════════════
# C1 — tier_gatekeeper core helpers (§6.2, §6.3, §9.4 C1)
# ═════════════════════════════════════════════════════════════════════════════

def test_T1_single_definitions_c1():
    for pat in ("def revoke_paid_tier", "def load_entitlement_profile",
                "BETA_SIGNUP_CUTOFF_MS =", "def get_user_allowance"):
        assert _git_grep_count(pat, "tier_gatekeeper.py") == 1, pat


def test_T21_revoke_guard_other_subscription(fdb, recs):
    fdb.seed("users/uid_X", {"stripe_tier": "estate", "stripe_customer_id": "cus_1"})
    fdb.seed("entitlements/uid_X", {"stripe_subscription_id": "sub_other", "email": "x@x.com"})
    res = revoke_paid_tier(fdb, "uid_X", None, customer_id="cus_1", revoked_subscription_id="sub_1")
    assert isinstance(res, RevokeResult)
    assert res.guard_skipped is True
    assert "uid_X" not in res.revoked_owner_keys
    assert fdb.doc("users/uid_X")["stripe_tier"] == "estate"


def test_T22_revoke_legacy_sweep(fdb):
    fdb.seed("users/legacy@x.com", {"stripe_tier": "pro", "stripe_customer_id": "cus_L"})
    res = revoke_paid_tier(fdb, None, None, customer_id="cus_L", revoked_subscription_id="sub_L")
    assert res.revoked_owner_keys == ["legacy@x.com"]
    assert res.guard_skipped is False
    d = fdb.doc("users/legacy@x.com")
    assert "stripe_tier" in d and d["stripe_tier"] is None          # present null
    assert d["subscription_status"] == "canceled" and d["grace_period_until"] is None


def test_T23_nothing_to_revoke(fdb):
    res = revoke_paid_tier(fdb, None, None, customer_id="cus_none", revoked_subscription_id="sub_1")
    assert res == RevokeResult([], False)
    assert fdb.writes() == []


def test_T24_revoke_never_creates(fdb, recs):
    fdb.seed("users/uid_P", {"stripe_tier": "pro"})
    res = revoke_paid_tier(fdb, "uid_P", "p@x.com")
    assert res.revoked_owner_keys == ["uid_P"]
    assert fdb.doc("users/p@x.com") is None
    assert ("set", "users/p@x.com") not in fdb.ops


def test_T25_revoke_chunking(fdb):
    for i in range(401):
        fdb.seed(f"users/legacy{i:03d}@x.com", {"stripe_tier": "pro", "stripe_customer_id": "cus_M"})
    before = fdb.txn_count
    res = revoke_paid_tier(fdb, None, None, customer_id="cus_M", revoked_subscription_id="sub_M")
    assert fdb.txn_count - before == 2
    assert len(res.revoked_owner_keys) == 401
    # commit failure on chunk 2 -> chunk 1 stays committed, exception propagates
    db2 = FakeFirestore()
    for i in range(401):
        db2.seed(f"users/legacy{i:03d}@x.com", {"stripe_tier": "pro", "stripe_customer_id": "cus_M"})
    calls = {"n": 0}

    def _fail(t):
        calls["n"] += 1
        return RuntimeError("commit failed") if calls["n"] == 2 else None
    db2.fail_commit = _fail
    with patch("tier_gatekeeper._run_txn", fake_run_txn):
        with pytest.raises(RuntimeError):
            revoke_paid_tier(db2, None, None, customer_id="cus_M", revoked_subscription_id="sub_M")
    nulled = [p for p, d in db2.docs.items() if d.get("stripe_tier") is None]
    assert len(nulled) == 400


def test_T26_email_unresolved(fdb, recs):
    recs["uid_P"] = Exception("auth down")
    fdb.seed("users/uid_P", {"stripe_tier": "pro"})
    fdb.seed("users/swept@x.com", {"stripe_tier": "pro", "stripe_customer_id": "cus_1"})
    with pytest.raises(RevokeEmailUnresolved):
        revoke_paid_tier(fdb, "uid_P", None, customer_id="cus_1", revoked_subscription_id="sub_1")
    assert fdb.doc("users/uid_P")["stripe_tier"] is None
    assert fdb.doc("users/swept@x.com")["stripe_tier"] is None


def test_T34_forged_auth_key(fdb, recs):
    recs["uid_P"] = POST("p@x.com")
    fdb.seed("users/uid_P", {"_auth_created_ms": 0, "_auth_is_anonymous": False})
    profile, ent = load_entitlement_profile(fdb, "uid_P", "p@x.com")
    assert profile["_auth_created_ms"] == POST_MS
    assert effective_limit(profile, ent, NOW) == 10


def test_T36_count_fails_closed(fdb):
    fdb.seed_coins("uid_P", 3)
    fdb.fail_on["stream"] = RuntimeError("firestore down")
    with pytest.raises(RuntimeError):
        count_unique_coins(fdb, "uid_P", "p@x.com")


def test_T37_locked_counts_once(fdb):
    fdb.seed_coins("uid_P", 50, start=0)                 # c00000..c00049
    fdb.seed_coins("p@x.com", 41, start=49)              # c00049..c00089 (c00049 in both)
    fdb.seed_coins("uid_P", 20, start=0, prefix="L", folder="locked_coins")
    assert count_unique_coins(fdb, "uid_P", "p@x.com", include_locked=False) == 90
    assert count_unique_coins(fdb, "uid_P", "p@x.com", include_locked=True) == 110


def test_T40_ladder_estate_at_least_gold():
    assert TIER_COIN_LIMITS["estate"] is None
    assert TIER_COIN_LIMITS["numismatist"] == 249
    assert TIER_COIN_LIMITS["family_estate"] is None
    for item in ("coins", "deepdive", "invoice_scan"):
        assert _bigger(_item_limit("family_estate", item), _item_limit("estate", item)) == \
            _item_limit("family_estate", item), item
    post_gold = {"_auth_created_ms": POST_MS, "_auth_is_anonymous": False, "stripe_tier": "estate"}
    assert effective_limit(post_gold, {}, NOW) is None


def test_T41_beta_tester_unlimited(fdb, recs):
    recs["uid_P"] = POST("p@x.com")
    fdb.seed("users/p@x.com", {"beta_tester": True})
    profile, ent = load_entitlement_profile(fdb, "uid_P", "p@x.com")
    assert effective_limit(profile, ent, NOW) is None
    assert effective_limit(profile, ent, NOW, "deepdive") == 1500
    assert effective_limit(profile, ent, NOW, "invoice_scan") == 750


def test_T42_item_by_item(fdb, recs):
    recs["uid_F"] = FOUNDER("f@x.com")
    fdb.seed("users/uid_F", {"stripe_tier": "dealer"})
    profile, ent = load_entitlement_profile(fdb, "uid_F", "f@x.com")
    assert effective_limit(profile, ent, NOW) is None
    assert effective_limit(profile, ent, NOW, "deepdive") == 1500
    assert effective_limit(profile, ent, NOW, "invoice_scan") == 750


@pytest.mark.parametrize("where", ["uid", "email"])
def test_T55_power_user_flag_ignored(fdb, recs, where):
    """AMEND-A + C1-PU: client-writable `power_user` bool on either doc is ignored;
    post-cutoff Free account gets limit 10."""
    recs["uid_P"] = POST("p@x.com")
    fdb.seed("users/uid_P" if where == "uid" else "users/p@x.com", {"power_user": True})
    fdb.seed_coins("p@x.com", 30)
    profile, ent = load_entitlement_profile(fdb, "uid_P", "p@x.com")
    assert effective_limit(profile, ent, NOW) == 10


def test_T_FREE_1_free_limit_is_10_everywhere():
    import catalog_service
    assert TIER_COIN_LIMITS["free"] == 10 == catalog_service.FREE_TRIAL_ITEM_LIMIT
    root = pathlib.Path(__file__).resolve().parents[1]
    pat = re.compile(r'"free": (5|20)\b|FREE_TRIAL_ITEM_LIMIT = (5|20)\b')
    for py in root.rglob("*.py"):
        parts = set(py.relative_to(root).parts)
        if "_archive" in parts or "tests" in parts:
            continue
        txt = py.read_text(encoding="utf-8", errors="ignore")
        assert not pat.search(txt), f"stale free limit in {py}"


def test_T_GOLD_1_gold_unlimited_silver_249():
    gold = {
        "stripe_tier": "estate",
        "_auth_created_ms": 1_800_000_000_000,
        "_auth_is_anonymous": False,
    }
    assert tier_gatekeeper.get_user_allowance(gold)["coins"] is None
    silver = {
        "stripe_tier": "numismatist",
        "_auth_created_ms": 1_800_000_000_000,
        "_auth_is_anonymous": False,
    }
    assert tier_gatekeeper.get_user_allowance(silver)["coins"] == 249


def test_T_PRICE_0_price_ladder_and_modes():
    assert tier_gatekeeper.PRICE_CENTS == {
        "pro": {"month": 399, "year": 3999},
        "numismatist": {"month": 799, "year": 7999},
        "dealer": {"month": 999, "year": 9900},
        "estate": {"month": 1599, "year": 15000},
    }
    assert set(tier_gatekeeper.PRICE_CENTS) == {
        t for t, m in PURCHASE_MODE.items() if m == "subscription"
    }
    assert tier_gatekeeper.CHRISTMAS2026_START_UTC == 1797310800
    assert tier_gatekeeper.CHRISTMAS2026_END_UTC == 1800075600
    assert tier_gatekeeper.CHRISTMAS2026_COUPON_IDS == {
        "pro": {"month": "CHRISTMAS2026_PRO_MONTH", "year": "CHRISTMAS2026_PRO_YEAR"},
        "numismatist": {"month": "CHRISTMAS2026_NUMISMATIST_MONTH", "year": "CHRISTMAS2026_NUMISMATIST_YEAR"},
        "dealer": {"month": "CHRISTMAS2026_DEALER_MONTH", "year": "CHRISTMAS2026_DEALER_YEAR"},
        "estate": {"month": "CHRISTMAS2026_GOLD_MONTH", "year": "CHRISTMAS2026_GOLD_YEAR"},
    }
    expected_net = {
        ("pro", "month"): 199,
        ("pro", "year"): 1999,
        ("numismatist", "month"): 399,
        ("numismatist", "year"): 3999,
        ("dealer", "month"): 499,
        ("dealer", "year"): 4950,
        ("estate", "month"): 799,
        ("estate", "year"): 7500,
    }
    for (tier, interval), net in expected_net.items():
        assert (
            tier_gatekeeper.PRICE_CENTS[tier][interval]
            - tier_gatekeeper.CHRISTMAS2026_DISCOUNT_CENTS[tier][interval]
        ) == net


def test_T74_purchasable_set_equality():
    assert set(PURCHASE_MODE) == set(PURCHASABLE_TIERS)
    assert PURCHASE_MODE["family_estate"] == "payment"
    for t in ("pro", "numismatist", "dealer", "estate"):
        assert PURCHASE_MODE[t] == "subscription"
    assert LIFETIME_PRICE_CENTS == {"family_estate": 50000}


def test_to_epoch_and_entitlement_ok():
    assert to_epoch(None) is None
    assert to_epoch(1_700_000_000_000) == 1_700_000_000.0
    assert to_epoch("garbage") == 0.0
    assert entitlement_ok(None, 10**9) is True and entitlement_ok(10, 11) is False

# ═════════════════════════════════════════════════════════════════════════════
# C2 — lock / unlock / enforce_entitlement and the webhook rewrite (§5, §9.4 C2)
# ═════════════════════════════════════════════════════════════════════════════

import uuid
from routes import payment_routes
from tier_gatekeeper import enforce_entitlement, lock_overflow_coins, unlock_user_coins, get_user_profile
from routes.subaccount_routes import _get_parent_tier


class _Clock:
    def __init__(self, now):
        self.now = now

    def time(self):
        return self.now


@pytest.fixture
def spies():
    """Every Stripe call the webhook could make is a spy; unexpected calls fail loudly."""
    with patch("routes.payment_routes.stripe.Refund.create") as refund, \
         patch("routes.payment_routes.stripe.Subscription.cancel") as cancel, \
         patch("routes.payment_routes.stripe.Subscription.delete") as delete, \
         patch("routes.payment_routes.stripe.Subscription.modify") as modify, \
         patch("routes.payment_routes.stripe.Subscription.retrieve",
               side_effect=AssertionError("Subscription.retrieve not expected")) as retrieve, \
         patch("routes.payment_routes.stripe.InvoicePayment.list",
               side_effect=AssertionError("InvoicePayment.list not expected")) as ip_list, \
         patch("routes.payment_routes.stripe.Charge.retrieve",
               side_effect=AssertionError("Charge.retrieve not expected")) as charge:
        yield MagicMock(refund=refund, cancel=cancel, delete=delete, modify=modify,
                        retrieve=retrieve, ip_list=ip_list, charge=charge)


def _never_cancel_or_refund(spies):
    spies.refund.assert_not_called()
    spies.cancel.assert_not_called()
    spies.delete.assert_not_called()
    spies.modify.assert_not_called()


def post_event(etype, obj, eid=None, now=NOW, payload=None):
    eid = eid or f"evt_{uuid.uuid4().hex[:16]}"
    body = payload if payload is not None else {"id": eid, "object": "event", "type": etype,
                                                "data": {"object": obj}}
    ev = stripe.Event.construct_from(body, "sk_test_dummy")   # a real StripeObject (no .get)
    with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_dummy"}), \
         patch("routes.payment_routes.stripe.Webhook.construct_event", return_value=ev), \
         patch("routes.payment_routes.time", _Clock(now)):
        client = TestClient(app, raise_server_exceptions=False)
        r = client.post("/api/stripe/webhook", content=b"{}", headers={"stripe-signature": "t=1,v1=dummy"})
    return r, eid


def ev_doc(fdb, eid):
    return fdb.doc(f"stripe_events/{eid}") or {}


def session(uid="uid_P", kind="subscription", tier="estate", mode="subscription", paid="paid",
            sub="sub_1", cus="cus_1", email="p@x.com", pi=None, interval="month",
            amount_subtotal=None, currency="usd", **extra):
    md = {"user_uid": uid, "user_email": email, "target_tier": tier}
    if interval is not None:
        md["interval"] = interval
    if kind is not None:
        md["purchase_kind"] = kind
    if amount_subtotal is None:
        amount_subtotal = tier_gatekeeper.PRICE_CENTS.get((tier or "").lower(), {}).get(interval, 1599)
    obj = {"id": "cs_test_1", "object": "checkout.session", "client_reference_id": uid, "metadata": md,
           "mode": mode, "payment_status": paid, "subscription": sub, "customer": cus,
           "customer_email": email, "payment_intent": pi,
           "amount_subtotal": amount_subtotal, "amount_total": amount_subtotal, "currency": currency}
    obj.update(extra)
    return obj


def lifetime_session(uid="uid_P", pi="pi_L", cus="cus_L", email="p@x.com", amount=50000, currency="usd",
                     mode="payment", paid="paid", tier="family_estate", **extra):
    md = {"user_uid": uid, "user_email": email, "target_tier": tier, "purchase_kind": "lifetime"}
    obj = {"id": "cs_test_L", "object": "checkout.session", "client_reference_id": uid, "metadata": md,
           "mode": mode, "payment_status": paid, "amount_subtotal": amount, "amount_total": amount,
           "currency": currency,
           "payment_intent": pi, "customer": cus, "customer_email": email, "subscription": None}
    obj.update(extra)
    return obj


def invoice(inv="in_1", cus="cus_1", sub="sub_1", pi="pi_1", created=NOW - 100, **extra):
    obj = {"id": inv, "object": "invoice", "customer": cus, "subscription": sub, "payment_intent": pi,
           "created": created, "status": "paid"}
    obj.update(extra)
    return obj


def subscription(sid="sub_1", cus="cus_1", status="active", metadata=None):
    return {"id": sid, "object": "subscription", "customer": cus, "status": status, "metadata": metadata or {}}


def charge(pi="pi_1", cus="cus_1", refunded=True, cid="ch_1"):
    return {"id": cid, "object": "charge", "payment_intent": pi, "customer": cus, "refunded": refunded}


def dispute(pi="pi_1", status="lost", ch="ch_1"):
    return {"id": "dp_1", "object": "dispute", "payment_intent": pi, "status": status, "charge": ch}


def grant_gold(fdb, recs, uid="uid_P", email="p@x.com", rec=None, cus="cus_1", sub="sub_1"):
    recs.setdefault(uid, rec or POST(email))
    r, eid = post_event("checkout.session.completed", session(uid=uid, email=email, cus=cus, sub=sub))
    assert r.status_code == 200, r.text
    assert ev_doc(fdb, eid)["status"] == "done", ev_doc(fdb, eid)
    return eid


def grant_lifetime(fdb, recs, uid="uid_P", email="p@x.com", pi="pi_L", cus="cus_L"):
    recs.setdefault(uid, POST(email))
    r, eid = post_event("checkout.session.completed", lifetime_session(uid=uid, email=email, pi=pi, cus=cus))
    assert r.status_code == 200, r.text
    return eid


def _app_reader(fdb, auth_email):
    """Emulates estate_planning_screen.dart C5 gate on users/{auth email}."""
    data = fdb.doc(f"users/{auth_email}") or {}
    tier = data.get("stripe_tier") or data.get("tier") or "free"
    access = (tier == "family_estate" or data.get("is_lifetime_family_estate") is True
              or auth_email.strip().lower() in {"eric@numista.ai", "grokbot@numista.ai"})
    return tier, access


def test_T1_single_definitions_c2():
    assert _git_grep_count("def enforce_entitlement", "tier_gatekeeper.py") == 1


def test_T2_real_sdk_event_object(fdb, recs, spies):
    fdb.seed("stripe_customers/cus_1", {"uid": "uid_P"})
    fdb.seed("entitlements/uid_P", {"stripe_subscription_id": "sub_1", "email": "p@x.com"})
    fdb.seed("users/uid_P", {"stripe_tier": "estate"})
    recs["uid_P"] = POST("p@x.com")
    r, eid = post_event("invoice.paid", invoice())
    assert r.status_code == 200, r.text
    assert ev_doc(fdb, eid)["status"] == "done"


def test_T3_event_without_id(fdb, spies):
    r, _ = post_event("invoice.paid", {}, payload={"object": "event", "type": "invoice.paid",
                                                   "data": {"object": {}}})
    assert r.status_code == 400
    assert fdb.writes("stripe_events") == []


@pytest.mark.parametrize("snap,expected", [
    (None, "claim"), ({"status": "done"}, "skip_done"),
    ({"status": "processing", "ts": NOW - 10}, "lease_active"),
    ({"status": "processing", "ts": NOW - 61}, "claim"),
    ({"status": "retry"}, "claim"), ({"status": "failed"}, "claim")])
def test_T4_claim(snap, expected):
    assert payment_routes.claim_event(snap, NOW) == expected


def test_T5_legacy_event_doc(fdb, spies):
    fdb.seed("stripe_events/evt_legacy1", {"processed_at": "2026-11-01T00:00:00+00:00", "type": "x"})
    handler = MagicMock()
    with patch.dict(payment_routes._HANDLERS, {"invoice.paid": handler}):
        r, _ = post_event("invoice.paid", invoice(), eid="evt_legacy1")
    assert r.status_code == 200 and r.json()["status"] == "skipped_duplicate"
    handler.assert_not_called()


def test_T6_duplicate(fdb, recs, spies):
    recs["uid_P"] = POST("p@x.com")
    r1, eid = post_event("checkout.session.completed", session())
    r2, _ = post_event("checkout.session.completed", session(), eid=eid)
    assert r1.status_code == 200 and r2.json()["status"] == "skipped_duplicate"
    assert fdb.ops.count(("set", "users/uid_P")) == 1


def test_T7_grant_ok(fdb, recs, spies):
    recs["uid_P"] = POST("p@x.com")
    with patch("routes.payment_routes.enforce_entitlement", wraps=enforce_entitlement) as enf:
        r, eid = post_event("checkout.session.completed", session())
    assert r.status_code == 200
    assert fdb.doc("users/uid_P")["stripe_tier"] == "estate"
    assert fdb.doc("entitlements/uid_P")["stripe_subscription_id"] == "sub_1"
    assert fdb.doc("stripe_customers/cus_1")["uid"] == "uid_P"
    enf.assert_called_once()
    assert enf.call_args.args[1] == "uid_P"
    assert ev_doc(fdb, eid)["status"] == "done"


def test_T8_no_email_fallback(fdb, recs, spies):
    obj = session(uid=None)
    obj["metadata"].pop("user_uid")
    r, eid = post_event("checkout.session.completed", obj)
    d = ev_doc(fdb, eid)
    assert d["status"] == "failed" and d["reason"] == "grant_uid_missing" and d["review_required"] is True
    assert fdb.doc("users/p@x.com") is None


@pytest.mark.parametrize("tier,reason", [(None, "tier_not_purchasable"), ("sovereign", "tier_not_purchasable"),
                                         ("founding_beta", "tier_not_purchasable"),
                                         ("family_estate", "tier_mode_mismatch")])
def test_T9_no_tier_default(fdb, recs, spies, tier, reason):
    recs["uid_P"] = POST("p@x.com")
    obj = session(tier=tier)
    if tier is None:
        obj["metadata"].pop("target_tier")
    r, eid = post_event("checkout.session.completed", obj)
    assert ev_doc(fdb, eid)["reason"] == reason and ev_doc(fdb, eid)["status"] == "failed"
    assert fdb.writes("users") == [] and fdb.writes("entitlements") == []


@pytest.mark.parametrize("kind", [None, "beta"])
def test_T10_purchase_kind(fdb, recs, spies, kind):
    recs["uid_P"] = POST("p@x.com")
    r, eid = post_event("checkout.session.completed", session(kind=kind))
    assert ev_doc(fdb, eid)["reason"] == "purchase_kind_unsupported"
    assert fdb.writes("users") == [] and fdb.writes("entitlements") == []


@pytest.mark.parametrize("paid", ["no_payment_required", "unpaid"])
def test_T11_not_paid(fdb, recs, spies, paid):
    r, eid = post_event("checkout.session.completed", session(paid=paid))
    assert ev_doc(fdb, eid)["reason"] == "not_paid"


def test_T12_guest_backstop(fdb, recs, spies):
    recs["uid_P"] = GUEST("p@x.com")
    r, eid = post_event("checkout.session.completed", session())
    assert ev_doc(fdb, eid)["reason"] == "grant_anonymous_uid"
    assert fdb.writes("users") == [] and fdb.writes("entitlements") == []


def test_T13_auth_outage_at_grant(fdb, recs, spies):
    recs["uid_P"] = Exception("auth down")
    r, eid = post_event("checkout.session.completed", session())
    assert r.status_code == 500
    assert ev_doc(fdb, eid)["status"] == "retry"
    assert fdb.writes("users") == [] and fdb.writes("entitlements") == []


def test_T14_customer_conflict(fdb, recs, spies):
    recs["uid_P"] = POST("p@x.com")
    fdb.seed("stripe_customers/cus_1", {"uid": "other"})
    r, eid = post_event("checkout.session.completed", session())
    assert ev_doc(fdb, eid)["reason"] == "customer_uid_conflict"
    assert fdb.writes("users") == [] and fdb.writes("entitlements") == []


def test_T15_renewal_keeps_tier(fdb, recs, spies):
    recs["uid_P"] = POST("p@x.com")
    fdb.seed("users/uid_P", {"stripe_tier": "estate"})
    fdb.seed("stripe_customers/cus_1", {"uid": "uid_P"})
    fdb.seed("entitlements/uid_P", {"stripe_subscription_id": "sub_1", "email": "p@x.com"})
    r, eid = post_event("invoice.paid", invoice())
    assert ev_doc(fdb, eid)["status"] == "done"
    u = fdb.doc("users/uid_P")
    assert u["stripe_tier"] == "estate" and u["subscription_status"] == "active"
    row = fdb.doc("stripe_payments/pi_1")
    assert row["kind"] == "subscription" and row["tier"] == "estate" and row["granted"] is True


def test_T16_renewal_uid_unknown(fdb, recs, spies):
    r, eid = post_event("invoice.paid", invoice())
    assert ev_doc(fdb, eid)["reason"] == "renewal_uid_unknown"
    assert fdb.writes("users") == []


@pytest.mark.parametrize("shape", ["a", "b", "c", "d"])
def test_T17_ledger_shapes(fdb, recs, spies, shape):
    recs["uid_P"] = POST("p@x.com")
    fdb.seed("users/uid_P", {"stripe_tier": "estate"})
    fdb.seed("stripe_customers/cus_1", {"uid": "uid_P"})
    fdb.seed("entitlements/uid_P", {"stripe_subscription_id": "sub_1", "email": "p@x.com"})
    if shape == "a":
        obj, pi = invoice(pi="pi_1"), "pi_1"
    elif shape == "b":
        obj = invoice(pi=None, payments={"object": "list", "data": [{"payment": {"payment_intent": "pi_2"}}]})
        pi = "pi_2"
    else:
        obj, pi = invoice(pi=None), "pi_3"
        data = [{"payment": {"type": "payment_intent", "payment_intent": "pi_3"}}] if shape == "c" else []
        spies.ip_list.side_effect = None
        spies.ip_list.return_value = stripe.ListObject.construct_from({"object": "list", "data": data}, "sk_test_dummy")
    r, eid = post_event("invoice.paid", obj)
    if shape in ("c", "d"):
        spies.ip_list.assert_called_once_with(invoice="in_1", limit=10)
    d = ev_doc(fdb, eid)
    assert d["status"] == "done"
    if shape == "d":
        assert d["reason"] == "ledger_pi_missing"
        assert fdb.writes("stripe_payments") == []
        return
    row = fdb.doc(f"stripe_payments/{pi}")
    assert {k: row[k] for k in ("uid", "kind", "tier", "subscription_id", "invoice_id", "granted")} == \
        {"uid": "uid_P", "kind": "subscription", "tier": "estate", "subscription_id": "sub_1",
         "invoice_id": "in_1", "granted": True}
    assert "created_at" in row


def test_T18_payment_failed(fdb, recs, spies):
    recs["uid_P"] = POST("p@x.com")
    fdb.seed("stripe_customers/cus_1", {"uid": "uid_P"})
    r, eid = post_event("invoice.payment_failed", invoice())
    u = fdb.doc("users/uid_P")
    assert u["subscription_status"] == "past_due"
    grace = datetime.fromisoformat(u["grace_period_until"]).timestamp()
    assert abs(grace - (NOW + 3 * 86400)) < 5
    r, eid = post_event("invoice.payment_failed", invoice(cus="cus_unknown"))
    assert ev_doc(fdb, eid)["status"] == "failed"


@pytest.mark.parametrize("status", ["active", "past_due", "incomplete", "canceled"])
def test_T19_subscription_updated(fdb, recs, spies, status):
    grant_gold(fdb, recs)
    fdb.seed("users/uid_P", {**fdb.doc("users/uid_P"), "stripe_tier": "pro", "subscription_status": "past_due"})
    before = fdb.doc("users/uid_P")
    r, eid = post_event("customer.subscription.updated", subscription(status=status))
    u = fdb.doc("users/uid_P")
    if status == "active":
        assert u["stripe_tier"] == "pro" and u["subscription_status"] == "active"   # stripe_tier never written
    elif status == "canceled":
        assert u["stripe_tier"] is None and u["subscription_status"] == "canceled"
    else:
        assert u == before and ev_doc(fdb, eid)["status"] == "done"


def test_T20_cancel_founder_gold(fdb, recs, spies):
    recs["uid_F"] = FOUNDER("f@x.com")
    grant_gold(fdb, recs, uid="uid_F", email="f@x.com", cus="cus_F")
    fdb.seed("users/f@x.com", {**fdb.doc("users/f@x.com"), "beta_tester": True, "tier": "legacy"})
    fdb.seed_coins("f@x.com", 5000)
    with patch("routes.payment_routes._relock_hook", wraps=payment_routes._relock_hook) as hook:
        r, eid = post_event("customer.subscription.deleted", subscription(cus="cus_F"))
    assert ev_doc(fdb, eid)["status"] == "done"
    u = fdb.doc("users/uid_F")
    assert "stripe_tier" in u and u["stripe_tier"] is None
    assert fdb.doc("users/f@x.com")["beta_tester"] is True and fdb.doc("users/f@x.com")["tier"] == "legacy"
    hook.assert_called_once_with(fdb, "uid_F", ["uid_F", "f@x.com"], ["cus_F"], NOW)
    assert len(fdb.coin_ids("f@x.com")) == 5000 and fdb.coin_ids("f@x.com", folder="locked_coins") == []
    assert _git_grep_count("lock_overflow_coins(target_id, TIER_COIN_LIMITS", "routes/payment_routes.py") == 0


def test_T21_webhook_guard_done_not_failed(fdb, recs, spies):
    recs["uid_X"] = POST("x@x.com")
    fdb.seed("stripe_customers/cus_1", {"uid": "uid_X"})
    fdb.seed("users/uid_X", {"stripe_tier": "estate", "stripe_customer_id": "cus_1"})
    fdb.seed("entitlements/uid_X", {"stripe_subscription_id": "sub_other", "email": "x@x.com"})
    r, eid = post_event("customer.subscription.deleted", subscription())
    assert ev_doc(fdb, eid)["status"] == "done"
    assert fdb.doc("users/uid_X")["stripe_tier"] == "estate"


def test_T23_webhook_nothing_to_revoke(fdb, recs, spies):
    with patch("routes.payment_routes._relock_hook") as hook:
        r, eid = post_event("customer.subscription.deleted", subscription(cus="cus_none"))
    assert ev_doc(fdb, eid)["reason"] == "nothing_to_revoke"
    hook.assert_not_called()


def test_T25_webhook_chunk_failure_retry(fdb, spies):
    for i in range(401):
        fdb.seed(f"users/legacy{i:03d}@x.com", {"stripe_tier": "pro", "stripe_customer_id": "cus_M"})
    calls = {"n": 0}

    def _fail(t):
        if any(op == "set" and p.startswith("users/") for op, p, _d, _m in t.buffer):
            calls["n"] += 1
            if calls["n"] == 2:
                return RuntimeError("commit failed")
        return None
    fdb.fail_commit = _fail
    r, eid = post_event("customer.subscription.deleted", subscription(cus="cus_M"))
    assert r.status_code == 500 and ev_doc(fdb, eid)["status"] == "retry"
    assert sum(1 for p, d in fdb.docs.items() if p.startswith("users/") and d.get("stripe_tier") is None) == 400


def test_T26_webhook_email_unresolved_retry(fdb, recs, spies):
    recs["uid_P"] = POST(None)                                  # Auth record without email
    fdb.seed("stripe_customers/cus_1", {"uid": "uid_P"})
    fdb.seed("users/uid_P", {"stripe_tier": "pro"})
    fdb.seed("users/swept@x.com", {"stripe_tier": "pro", "stripe_customer_id": "cus_1"})
    r, eid = post_event("customer.subscription.deleted", subscription())
    assert r.status_code == 500 and ev_doc(fdb, eid)["status"] == "retry"
    assert fdb.doc("users/uid_P")["stripe_tier"] is None and fdb.doc("users/swept@x.com")["stripe_tier"] is None


def test_T27_partial_refund(fdb, spies):
    fdb.seed("stripe_payments/pi_1", {"uid": "uid_P", "kind": "subscription", "subscription_id": "sub_1", "granted": True})
    r, eid = post_event("charge.refunded", charge(refunded=False))
    assert ev_doc(fdb, eid)["status"] == "done" and ev_doc(fdb, eid)["reason"] == "partial_refund"
    assert fdb.writes("users") == [] and fdb.writes("stripe_payments") == []


def test_T28_refund_no_ledger(fdb, spies):
    with patch("routes.payment_routes.revoke_paid_tier") as rpt:
        r, eid = post_event("charge.refunded", charge())
    assert ev_doc(fdb, eid)["reason"] == "no_ledger_entry" and ev_doc(fdb, eid)["status"] == "failed"
    rpt.assert_not_called()
    assert not [o for o in fdb.ops if o[0] == "where" and "stripe_customer_id" in o[1]]   # no customer sweep


def test_T29_refund_ledger_subscription(fdb, recs, spies):
    recs["uid_P"] = POST("p@x.com")
    fdb.seed("users/uid_P", {"stripe_tier": "estate", "stripe_customer_id": "cus_1"})
    fdb.seed("stripe_payments/pi_1", {"uid": "uid_P", "kind": "subscription", "subscription_id": "sub_1", "granted": True})
    with patch("routes.payment_routes.revoke_paid_tier", wraps=revoke_paid_tier) as rpt, \
         patch("routes.payment_routes._relock_hook", wraps=payment_routes._relock_hook) as hook:
        r, eid = post_event("charge.refunded", charge())
    assert ev_doc(fdb, eid)["status"] == "done"
    assert rpt.call_args.kwargs == {"customer_id": "cus_1", "revoked_subscription_id": "sub_1"}
    assert hook.call_args.args[3] == ["cus_1"]
    assert fdb.doc("users/uid_P")["stripe_tier"] is None
    assert fdb.doc("stripe_payments/pi_1")["revoked"]["reason"] == "refunded"


def test_T30_disputes(fdb, recs, spies):
    recs["uid_P"] = POST("p@x.com")
    fdb.seed("users/uid_P", {"stripe_tier": "estate", "stripe_customer_id": "cus_1"})
    fdb.seed("stripe_payments/pi_1", {"uid": "uid_P", "kind": "subscription", "subscription_id": "sub_1", "granted": True})
    r, eid = post_event("charge.dispute.created", dispute(status="needs_response"))
    assert fdb.doc("entitlements/uid_P")["dispute_review"] is True
    assert fdb.doc("users/uid_P")["stripe_tier"] == "estate"
    r, eid = post_event("charge.dispute.closed", dispute(status="won"))
    assert fdb.doc("users/uid_P")["stripe_tier"] == "estate"
    spies.charge.side_effect = None
    spies.charge.return_value = stripe.Charge.construct_from({"id": "ch_1", "object": "charge", "customer": "cus_1"},
                                                            "sk_test_dummy")
    with patch("routes.payment_routes._relock_hook", wraps=payment_routes._relock_hook) as hook:
        r, eid = post_event("charge.dispute.closed", dispute(status="lost"))
    assert ev_doc(fdb, eid)["status"] == "done"
    spies.charge.assert_called_once_with("ch_1")
    assert fdb.doc("users/uid_P")["stripe_tier"] is None
    assert hook.call_args.args[3] == ["cus_1"]
    assert fdb.doc("stripe_payments/pi_1")["revoked"]["reason"] == "dispute_lost"


def test_T31_p1_seam_contract(fdb, recs, spies):
    grant_gold(fdb, recs)
    seam = MagicMock(return_value={"accounts_reconciled": [], "review_required": True,
                                   "review_reasons": ["relock_skipped_no_uid"]})
    with patch("routes.payment_routes._relock_hook", seam):
        r, eid = post_event("customer.subscription.deleted", subscription())
    d = ev_doc(fdb, eid)
    assert d["status"] == "done" and d["review_required"] is True
    assert d["review_reasons"] == ["relock_skipped_no_uid"]


def test_T32_founding_not_locked(fdb, recs):
    recs["uid_F"] = FOUNDER("f@x.com")
    fdb.seed_coins("f@x.com", 30)
    res = enforce_entitlement(fdb, "uid_F", "f@x.com", NOW)
    assert res["limit"] is None and res["locked_moved"] == 0
    recs["_mock"].assert_called_with("uid_F")


def test_T33_negative_control_locks_newest(fdb, recs):
    recs["uid_F"] = POST("f@x.com")
    fdb.seed_coins("f@x.com", 30)
    res = enforce_entitlement(fdb, "uid_F", "f@x.com", NOW)
    assert res["limit"] == 10 and res["visible"] == 10 and res["locked"] == 20
    locked = fdb.coin_ids("f@x.com", folder="locked_coins")
    assert locked == [f"c{i:05d}" for i in range(10, 30)]                 # the 20 newest
    assert fdb.coin_ids("f@x.com") == [f"c{i:05d}" for i in range(10)]   # sources deleted
    assert len(fdb.coin_ids("f@x.com")) + len(locked) == 30
    doc = fdb.doc("locked_coins/f@x.com/coins/c00029")
    assert doc["source_path"] == "users/f@x.com/coins/c00029" and doc["data"]["name"] == "coin 29"


def test_T35_email_key_refused(fdb, recs):
    with pytest.raises(ValueError):
        enforce_entitlement(fdb, "a@x.com", None, NOW)
    with pytest.raises(ValueError):
        lock_overflow_coins(fdb, None, "a@x.com", 10, "x", NOW)
    assert fdb.writes() == []


def test_T38_unlock_oldest_first_with_conflict(fdb):
    for i in range(20):
        cid = f"c{i:05d}"
        fdb.seed(f"locked_coins/p@x.com/coins/{cid}",
                 {"coin_id": cid, "source_path": f"users/p@x.com/coins/{cid}", "data": {"n": i},
                  "locked_at": NOW, "lock_reason": "x", "sort_epoch": 1000 + i})
    fdb.seed("users/p@x.com/coins/c00005", {"n": "already back"})
    conflicts = unlock_user_coins(fdb, "uid_P", "p@x.com", None)
    assert conflicts == 1
    assert len(fdb.coin_ids("p@x.com")) == 20
    assert fdb.doc("users/p@x.com/coins/c00005") == {"n": "already back"}
    assert fdb.doc("locked_coins/p@x.com/coins/c00005")["restore_conflict"] is True
    assert fdb.coin_ids("p@x.com", folder="locked_coins") == ["c00005"]
    # oldest first with limited room
    db2 = FakeFirestore()
    for i in range(5):
        db2.seed(f"locked_coins/u2/coins/c{i}", {"coin_id": f"c{i}", "source_path": f"users/u2/coins/c{i}",
                                                 "data": {}, "sort_epoch": 100 - i})
    with patch("tier_gatekeeper._run_txn", fake_run_txn):
        unlock_user_coins(db2, "u2", None, 2)
    assert db2.coin_ids("u2") == ["c3", "c4"]


def test_T39_lock_chunking(fdb):
    fdb.seed_coins("uid_P", 460)
    before = fdb.txn_count
    moved = lock_overflow_coins(fdb, "uid_P", "p@x.com", 10, "x", NOW)
    assert moved == 450 and fdb.txn_count - before == 3
    assert len(fdb.coin_ids("uid_P", folder="locked_coins")) == 450


def test_T49_non_us_never_blocked(fdb, recs, spies):
    recs["uid_P"] = POST("p@x.com")
    r, eid = post_event("checkout.session.completed",
                        session(customer_details={"address": {"country": "CA"}}))
    assert ev_doc(fdb, eid)["status"] == "done"
    assert fdb.doc("users/uid_P")["stripe_tier"] == "estate"
    _never_cancel_or_refund(spies)


def _six_readers(fdb):
    prof = load_entitlement_profile(fdb, "uid_P", "p@x.com", with_auth_facts=False)[0]
    return {
        "uid_doc": fdb.doc("users/uid_P").get("stripe_tier"),
        "email_doc": fdb.doc("users/p@x.com").get("stripe_tier"),
        "app": _app_reader(fdb, "p@x.com")[0],
        "subaccount": _get_parent_tier(fdb, "p@x.com"),
        "sa_uid": get_user_profile("uid_P").get("stripe_tier"),
        "sa_email": get_user_profile("p@x.com").get("stripe_tier"),
        "merged": prof.get("stripe_tier"),
    }


def test_T52_same_doc_all_readers(fdb, recs, spies):
    grant_gold(fdb, recs)
    readers = _six_readers(fdb)
    assert set(readers.values()) == {"estate"}, readers
    assert enforce_entitlement(fdb, "uid_P", "p@x.com", NOW)["limit"] is None
    post_event("customer.subscription.deleted", subscription())
    readers = _six_readers(fdb)
    assert readers["app"] == "free" and readers["subaccount"] == "free"
    assert {readers[k] for k in ("uid_doc", "email_doc", "sa_uid", "sa_email", "merged")} == {None}
    assert enforce_entitlement(fdb, "uid_P", "p@x.com", NOW)["limit"] == 10


def test_T53_mismatch_case(fdb, recs, spies):
    fdb.seed("users/p@x.com", {"stripe_tier": "dealer"})
    fdb.seed("users/uid_P", {"stripe_tier": "pro"})
    r = _six_readers(fdb)
    assert r["merged"] == "pro" and r["app"] == "dealer" and r["subaccount"] == "dealer"   # TIER-KEY-AUDIT case
    grant_gold(fdb, recs)
    assert set(_six_readers(fdb).values()) == {"estate"}
    post_event("customer.subscription.deleted", subscription())
    for p in ("users/uid_P", "users/p@x.com"):
        assert "stripe_tier" in fdb.doc(p) and fdb.doc(p)["stripe_tier"] is None


def test_T54_grant_email_missing(fdb, recs, spies):
    recs["uid_P"] = POST(None)
    r, eid = post_event("checkout.session.completed", session(email=None))
    d = ev_doc(fdb, eid)
    assert d["status"] == "done" and d["review_required"] is True and d["reason"] == "grant_email_missing"
    assert fdb.doc("users/uid_P")["stripe_tier"] == "estate"
    assert [p for p in fdb.docs if p.startswith("users/") and "@" in p] == []


@pytest.mark.parametrize("where", ["uid", "email"])
def test_T55_power_user_enforce(fdb, recs, where):
    """AMEND-A + C1-PU: client-writable `power_user` bool on either doc is ignored;
    enforce_entitlement enforces the post-cutoff Free limit of 10."""
    recs["uid_P"] = POST("p@x.com")
    fdb.seed("users/uid_P" if where == "uid" else "users/p@x.com", {"power_user": True})
    fdb.seed_coins("p@x.com", 30)
    res = enforce_entitlement(fdb, "uid_P", "p@x.com", NOW)
    assert res["limit"] == 10 and res["locked_moved"] == 20


def test_T56_late_update_after_delete(fdb, recs, spies):
    grant_gold(fdb, recs)
    post_event("customer.subscription.deleted", subscription())
    assert fdb.doc("users/uid_P")["stripe_tier"] is None
    assert fdb.doc("entitlements/uid_P")["last_revoke"]["subscription"]["subscription_id"] == "sub_1"
    r, eid = post_event("customer.subscription.updated", subscription(status="active"))
    u = fdb.doc("users/uid_P")
    assert u["stripe_tier"] is None and u["subscription_status"] == "canceled"
    assert ev_doc(fdb, eid)["reason"] == "stale_after_revoke"


def _refunded_state(fdb, recs, spies):
    grant_gold(fdb, recs)
    r, _ = post_event("invoice.paid", invoice(pi="pi_1", created=NOW - 50))
    assert fdb.doc("stripe_payments/pi_1")["granted"] is True
    r, eid = post_event("charge.refunded", charge(pi="pi_1"))
    assert ev_doc(fdb, eid)["status"] == "done"


def test_T57_refund_then_update(fdb, recs, spies):
    _refunded_state(fdb, recs, spies)
    assert fdb.doc("users/uid_P")["stripe_tier"] is None
    assert fdb.doc("stripe_payments/pi_1")["revoked"]["reason"] == "refunded"
    post_event("customer.subscription.updated", subscription(status="active"))
    assert fdb.doc("users/uid_P")["stripe_tier"] is None
    spies.retrieve.side_effect = None
    spies.retrieve.return_value = stripe.Subscription.construct_from(
        {"id": "sub_1", "object": "subscription", "status": "active", "metadata": {"target_tier": "estate"}}, "sk_test_dummy")
    r, eid = post_event("invoice.paid", invoice(pi="pi_1", created=NOW - 50))
    spies.retrieve.assert_called_once_with("sub_1")
    assert fdb.doc("users/uid_P")["stripe_tier"] is None
    assert fdb.doc("users/p@x.com")["stripe_tier"] is None
    assert "reaffirm_refused:iii" in ev_doc(fdb, eid)["review_reasons"]


@pytest.mark.parametrize("variant", ["active", "canceled", "raises"])
def test_T58_new_renewal_restores(fdb, recs, spies, variant):
    _refunded_state(fdb, recs, spies)
    spies.retrieve.side_effect = None
    if variant == "raises":
        spies.retrieve.side_effect = stripe.APIConnectionError("down")
    else:
        spies.retrieve.return_value = stripe.Subscription.construct_from(
            {"id": "sub_1", "object": "subscription", "status": variant, "metadata": {"target_tier": "estate"}},
            "sk_test_dummy")
    r, eid = post_event("invoice.paid", invoice(inv="in_2", pi="pi_2", created=NOW + 10))
    spies.retrieve.assert_called_once_with("sub_1")
    if variant == "active":
        assert fdb.doc("users/uid_P")["stripe_tier"] == "estate"
        assert fdb.doc("users/p@x.com")["stripe_tier"] == "estate"
        assert fdb.doc("stripe_payments/pi_2")["granted"] is True
    elif variant == "canceled":
        assert fdb.doc("users/uid_P")["stripe_tier"] is None
        assert "reaffirm_refused:ii" in ev_doc(fdb, eid)["review_reasons"]
    else:
        assert r.status_code == 500 and ev_doc(fdb, eid)["status"] == "retry"


@pytest.mark.parametrize("etype,status", [("customer.subscription.updated", "canceled"),
                                          ("customer.subscription.deleted", "canceled")])
def test_T59_customer_id_resolution(fdb, recs, spies, etype, status):
    recs["uid_P"] = POST("p@x.com")
    fdb.seed("stripe_customers/cus_1", {"uid": "uid_P"})
    fdb.seed("users/uid_P", {"stripe_tier": "estate"})
    fdb.seed("users/p@x.com", {"stripe_tier": "estate"})
    with patch("routes.payment_routes.revoke_paid_tier", wraps=revoke_paid_tier) as rpt, \
         patch("routes.payment_routes._relock_hook", wraps=payment_routes._relock_hook) as hook:
        r, eid = post_event(etype, {"id": "sub_1", "object": "subscription", "customer": "cus_1",
                                    "status": status, "metadata": {}})
    assert rpt.call_args.args[1] == "uid_P" and rpt.call_args.kwargs["customer_id"] == "cus_1"
    assert fdb.doc("users/uid_P")["stripe_tier"] is None and fdb.doc("users/p@x.com")["stripe_tier"] is None
    assert hook.call_args.args[3] == ["cus_1"]


def test_T60_no_map_no_metadata(fdb, spies):
    fdb.seed("users/legacy@x.com", {"stripe_tier": "pro", "stripe_customer_id": "cus_L"})
    with patch("routes.payment_routes._relock_hook", wraps=payment_routes._relock_hook) as hook:
        r, eid = post_event("customer.subscription.deleted", {"id": "sub_L", "object": "subscription",
                                                              "customer": "cus_L", "metadata": {}})
    assert ev_doc(fdb, eid)["status"] == "done"
    assert hook.call_args.args[1] is None
    assert fdb.doc("users/legacy@x.com")["stripe_tier"] is None
    assert [p for p in fdb.docs if p.startswith("entitlements/")] == []


def test_T61_email_changed(fdb, recs, spies):
    grant_gold(fdb, recs)
    recs["uid_P"] = POST("P2@X.com")
    n_before = fdb.ops.count(("set", "users/p@x.com"))
    r, eid = post_event("invoice.payment_failed", invoice())
    d = ev_doc(fdb, eid)
    assert fdb.doc("users/uid_P")["subscription_status"] == "past_due"
    assert fdb.doc("users/p2@x.com")["subscription_status"] == "past_due"
    assert fdb.ops.count(("set", "users/p@x.com")) == n_before
    assert fdb.doc("entitlements/uid_P")["email"] == "p2@x.com"
    assert "email_changed" in d["review_reasons"]
    post_event("customer.subscription.deleted", subscription())
    assert fdb.doc("users/uid_P")["stripe_tier"] is None and fdb.doc("users/p2@x.com")["stripe_tier"] is None
    # Auth raising -> retry, zero users writes
    recs["uid_P"] = Exception("auth down")
    n_users = len(fdb.writes("users"))
    r, eid = post_event("invoice.payment_failed", invoice())
    assert r.status_code == 500 and ev_doc(fdb, eid)["status"] == "retry"
    assert len(fdb.writes("users")) == n_users
    # Auth record without email -> entitlements.email
    recs["uid_P"] = POST(None)
    n_p2 = fdb.ops.count(("set", "users/p2@x.com"))
    r, eid = post_event("invoice.payment_failed", invoice())
    assert ev_doc(fdb, eid)["status"] == "done"
    assert fdb.ops.count(("set", "users/p2@x.com")) == n_p2 + 1                 # fell back to entitlements.email


def test_T66_lifetime_grant(fdb, recs, spies):
    recs["uid_P"] = POST("p@x.com")
    fdb.seed_coins("p@x.com", 5000)
    eid = grant_lifetime(fdb, recs)
    d = ev_doc(fdb, eid)
    assert d["status"] == "done", d
    for p in ("users/uid_P", "users/p@x.com"):
        u = fdb.doc(p)
        assert u["is_lifetime_family_estate"] is True
        for k in ("stripe_tier", "subscription_status", "stripe_customer_id"):
            assert k not in u, (p, k)
    assert fdb.doc("entitlements/uid_P")["lifetime"]["payment_intent"] == "pi_L"
    assert fdb.doc("stripe_payments/pi_L")["kind"] == "lifetime"
    assert fdb.doc("stripe_customers/cus_L")["uid"] == "uid_P"
    res = enforce_entitlement(fdb, "uid_P", "p@x.com", NOW)
    assert res["limit"] is None and res["locked"] == 0 and len(fdb.coin_ids("p@x.com")) == 5000
    prof, ent = load_entitlement_profile(fdb, "uid_P", "p@x.com")
    assert effective_limit(prof, ent, NOW, "deepdive") == 1500 and effective_limit(prof, ent, NOW, "invoice_scan") == 750
    n = fdb.ops.count(("set", "users/uid_P"))
    r, _ = post_event("checkout.session.completed", lifetime_session(), eid=eid)
    assert r.json()["status"] == "skipped_duplicate" and fdb.ops.count(("set", "users/uid_P")) == n


@pytest.mark.parametrize("kw,reason", [
    ({"mode": "subscription"}, "mode_mismatch"), ({"paid": "unpaid"}, "not_paid"),
    ({"amount": 2900}, "amount_mismatch"), ({"currency": "eur"}, "amount_mismatch"),
    ({"pi": None}, "grant_ids_missing"), ({"tier": "estate"}, "tier_not_purchasable"),
    ({"_guest": True}, "grant_anonymous_uid")])
def test_T67_lifetime_guards(fdb, recs, spies, kw, reason):
    recs["uid_P"] = GUEST("p@x.com") if kw.pop("_guest", False) else POST("p@x.com")
    r, eid = post_event("checkout.session.completed", lifetime_session(**kw))
    d = ev_doc(fdb, eid)
    assert d["status"] == "failed" and d["reason"] == reason and d["review_required"] is True
    assert fdb.writes("users") == []


def test_T68_lifetime_refund_revoke(fdb, recs, spies):
    grant_lifetime(fdb, recs)
    r, eid = post_event("charge.refunded", charge(pi="pi_L", cus="cus_L", refunded=False))
    assert fdb.doc("users/uid_P")["is_lifetime_family_estate"] is True
    with patch("routes.payment_routes.revoke_paid_tier") as rpt, \
         patch("routes.payment_routes._relock_hook", wraps=payment_routes._relock_hook) as hook:
        r, eid = post_event("charge.refunded", charge(pi="pi_L", cus="cus_L"))
    assert ev_doc(fdb, eid)["status"] == "done"
    for p in ("users/uid_P", "users/p@x.com"):
        assert fdb.doc(p)["is_lifetime_family_estate"] is False
    assert fdb.doc("stripe_payments/pi_L")["revoked"]["reason"] == "refunded"
    assert fdb.doc("entitlements/uid_P")["last_revoke"]["lifetime"]["payment_intent"] == "pi_L"
    rpt.assert_not_called()
    assert not [o for o in fdb.ops if o[0] == "where" and "stripe_customer_id" in o[1]]   # no customer sweep
    hook.assert_called_once_with(fdb, "uid_P", ["uid_P", "p@x.com"], [], NOW)
    non_event = lambda: [w for w in fdb.writes() if not w[1].startswith("stripe_events/")]
    n = len(non_event())
    r, eid2 = post_event("charge.refunded", charge(pi="pi_L", cus="cus_L"))      # redelivery, new event id
    assert ev_doc(fdb, eid2)["status"] == "done"
    assert len(non_event()) == n                                               # no second write


def test_T69_lifetime_lost_dispute(fdb, recs, spies):
    grant_lifetime(fdb, recs)
    post_event("charge.dispute.created", dispute(pi="pi_L", status="needs_response", ch="ch_L"))
    assert fdb.doc("entitlements/uid_P")["dispute_review"] is True
    assert fdb.doc("users/uid_P")["is_lifetime_family_estate"] is True
    post_event("charge.dispute.closed", dispute(pi="pi_L", status="won", ch="ch_L"))
    assert fdb.doc("users/uid_P")["is_lifetime_family_estate"] is True
    r, eid = post_event("charge.dispute.closed", dispute(pi="pi_L", status="lost", ch="ch_L"))
    assert ev_doc(fdb, eid)["status"] == "done"
    for p in ("users/uid_P", "users/p@x.com"):
        assert fdb.doc(p)["is_lifetime_family_estate"] is False
    assert fdb.doc("stripe_payments/pi_L")["revoked"]["reason"] == "dispute_lost"
    spies.charge.assert_not_called()


def test_T70_preexisting_flag_kept(fdb, recs, spies, caplog):
    fdb.seed("users/p@x.com", {"is_lifetime_family_estate": True})
    grant_lifetime(fdb, recs)
    with caplog.at_level("INFO"):
        post_event("charge.refunded", charge(pi="pi_L", cus="cus_L"))
    assert fdb.doc("users/p@x.com")["is_lifetime_family_estate"] is True
    assert fdb.doc("users/uid_P")["is_lifetime_family_estate"] is False
    assert "lifetime_flag_kept:preexisting" in caplog.text
    prof = load_entitlement_profile(fdb, "uid_P", "p@x.com", with_auth_facts=False)[0]
    assert prof["is_lifetime_family_estate"] is True


def test_T71_subscription_cancel_keeps_estate(fdb, recs, spies):
    recs["uid_P"] = POST("p@x.com")
    fdb.seed_coins("p@x.com", 5000)
    grant_lifetime(fdb, recs)
    grant_gold(fdb, recs)
    prof, ent = load_entitlement_profile(fdb, "uid_P", "p@x.com")
    assert get_user_allowance(prof) == {"coins": None, "deepdive": 1500, "invoice_scan": 750}
    life_before = fdb.doc("entitlements/uid_P")["lifetime"]
    with patch("routes.payment_routes._relock_hook", wraps=payment_routes._relock_hook) as hook:
        post_event("customer.subscription.deleted", subscription())
    hook.assert_called_once()
    assert fdb.doc("users/uid_P")["stripe_tier"] is None
    for p in ("users/uid_P", "users/p@x.com"):
        assert fdb.doc(p)["is_lifetime_family_estate"] is True
    assert fdb.doc("entitlements/uid_P")["lifetime"] == life_before
    prof, ent = load_entitlement_profile(fdb, "uid_P", "p@x.com")
    assert get_user_allowance(prof) == {"coins": None, "deepdive": 1500, "invoice_scan": 750}
    assert _app_reader(fdb, "p@x.com")[1] is True
    res = enforce_entitlement(fdb, "uid_P", "p@x.com", NOW)
    assert res["limit"] is None and res["locked"] == 0 and len(fdb.coin_ids("p@x.com")) == 5000


def test_T72_no_subscription_event_touches_estate(fdb, recs, spies):
    grant_lifetime(fdb, recs)
    grant_gold(fdb, recs)
    post_event("invoice.paid", invoice(pi="pi_S", created=NOW - 50))
    flag = lambda: (fdb.doc("users/uid_P")["is_lifetime_family_estate"], fdb.doc("users/p@x.com")["is_lifetime_family_estate"])
    life = fdb.doc("entitlements/uid_P")["lifetime"]
    spies.charge.side_effect = None
    spies.charge.return_value = stripe.Charge.construct_from({"id": "ch_1", "object": "charge", "customer": "cus_1"}, "sk_test_dummy")
    spies.retrieve.side_effect = None
    spies.retrieve.return_value = stripe.Subscription.construct_from(
        {"id": "sub_1", "object": "subscription", "status": "active", "metadata": {"target_tier": "estate"}}, "sk_test_dummy")
    events = [("invoice.paid", invoice(pi="pi_S", created=NOW - 40)), ("invoice.payment_failed", invoice()),
              ("customer.subscription.updated", subscription(status="active")),
              ("customer.subscription.updated", subscription(status="past_due")),
              ("customer.subscription.updated", subscription(status="canceled")),
              ("customer.subscription.updated", subscription(status="unpaid")),
              ("customer.subscription.deleted", subscription()),
              ("charge.refunded", charge(pi="pi_S")), ("charge.dispute.closed", dispute(pi="pi_S", status="lost"))]
    for etype, obj in events:
        r, eid = post_event(etype, obj)
        assert r.status_code == 200, (etype, r.text)
        assert flag() == (True, True), etype
        assert fdb.doc("entitlements/uid_P")["lifetime"] == life, etype
    assert _git_grep_count("is_lifetime_family_estate", "routes/payment_routes.py") == 0
    src = open(os.path.join(BACKEND, "tier_gatekeeper.py")).read()
    writer_fns = set()
    for m in re.finditer(r'\{"is_lifetime_family_estate": (True|False)', src):
        fn = re.findall(r"^def (\w+)\(", src[:m.start()], re.M)[-1]
        writer_fns.add(fn)
    assert writer_fns == {"grant_lifetime_purchase", "revoke_lifetime_purchase"}, writer_fns


def test_T73_no_regrant_after_refund(fdb, recs, spies):
    grant_lifetime(fdb, recs)
    post_event("charge.refunded", charge(pi="pi_L", cus="cus_L"))
    r, eid = post_event("checkout.session.completed", lifetime_session())
    assert ev_doc(fdb, eid)["reason"] == "revoked_payment"
    assert fdb.doc("users/uid_P")["is_lifetime_family_estate"] is False


def test_T75_duplicate_lifetime_purchase(fdb, recs, spies):
    grant_lifetime(fdb, recs)
    r, eid = post_event("checkout.session.completed", lifetime_session(pi="pi_L2"))
    d = ev_doc(fdb, eid)
    assert d["review_required"] is True and d["reason"] == "lifetime_duplicate_purchase"
    assert fdb.doc("entitlements/uid_P")["lifetime"]["extra_payment_intents"] == ["pi_L2"]
    assert fdb.doc("users/uid_P")["is_lifetime_family_estate"] is True
    post_event("charge.refunded", charge(pi="pi_L", cus="cus_L"))
    assert fdb.doc("users/uid_P")["is_lifetime_family_estate"] is True          # pi_L2 still live
    _never_cancel_or_refund(spies)


def test_T77_non_us_lifetime(fdb, recs, spies):
    recs["uid_P"] = POST("p@x.com")
    r, eid = post_event("checkout.session.completed",
                        lifetime_session(customer_details={"address": {"country": "CA"}}))
    assert ev_doc(fdb, eid)["status"] == "done"
    assert fdb.doc("users/uid_P")["is_lifetime_family_estate"] is True
    _never_cancel_or_refund(spies)


def test_T85_cancel_lock_line_gone():
    assert _git_grep_count("lock_overflow_coins(target_id", "routes/payment_routes.py") == 0
    assert _git_grep_count('TIER_COIN_LIMITS["free"]', "routes/payment_routes.py") == 0


@pytest.mark.parametrize("case", ["founder_gold", "lifetime_gold", "post_gold"])
def test_T86_cancel_respects_beta_and_lifetime(fdb, recs, spies, case):
    results = []

    def p1_contract(db, handler_uid, keys, swept, now):
        email = next((k for k in keys if "@" in k), None)
        results.append(enforce_entitlement(db, handler_uid, email, now))
        return {"accounts_reconciled": [handler_uid], "review_required": False, "review_reasons": []}

    recs["uid_P"] = FOUNDER("p@x.com") if case == "founder_gold" else POST("p@x.com")
    if case == "lifetime_gold":
        grant_lifetime(fdb, recs)
    grant_gold(fdb, recs)
    fdb.seed_coins("p@x.com", 5000)
    with patch("routes.payment_routes._relock_hook", side_effect=p1_contract):
        r, eid = post_event("customer.subscription.deleted", subscription())
    assert ev_doc(fdb, eid)["status"] == "done"
    res = results[0]
    if case == "post_gold":
        assert res["limit"] == 10 and res["locked_moved"] == 4990
        assert fdb.coin_ids("p@x.com") == [f"c{i:05d}" for i in range(10)]
    else:
        assert res["limit"] is None and res["locked_moved"] == 0
        assert len(fdb.coin_ids("p@x.com")) == 5000
    if case == "lifetime_gold":
        assert fdb.doc("users/p@x.com")["is_lifetime_family_estate"] is True


def test_T21b_mf1_revoke_guard_skips_email_doc_unit(fdb, recs):
    recs["uid_X"] = POST("x@x.com")
    fdb.seed("users/uid_X", {"stripe_tier": "estate", "stripe_customer_id": "cus_1"})
    fdb.seed("users/x@x.com", {"stripe_tier": "estate", "stripe_customer_id": "cus_1"})
    fdb.seed("entitlements/uid_X", {"stripe_subscription_id": "sub_2", "email": "x@x.com"})
    res = revoke_paid_tier(fdb, "uid_X", "x@x.com", customer_id="cus_1", revoked_subscription_id="sub_1")
    assert res.revoked_owner_keys == [] and res.guard_skipped is True
    assert fdb.doc("users/uid_X")["stripe_tier"] == "estate"
    assert fdb.doc("users/x@x.com")["stripe_tier"] == "estate"


def test_T21b_mf1_revoke_guard_skips_email_doc_webhook(fdb, recs, spies):
    recs["uid_X"] = POST("x@x.com")
    fdb.seed("stripe_customers/cus_1", {"uid": "uid_X"})
    fdb.seed("users/uid_X", {"stripe_tier": "estate", "stripe_customer_id": "cus_1"})
    fdb.seed("users/x@x.com", {"stripe_tier": "estate", "stripe_customer_id": "cus_1"})
    fdb.seed("entitlements/uid_X", {"stripe_subscription_id": "sub_2", "email": "x@x.com"})
    r, eid = post_event("customer.subscription.deleted", subscription(sid="sub_1"))
    assert r.status_code == 200
    ev = ev_doc(fdb, eid)
    assert ev["status"] == "done"
    assert "revoke_skip_other_sub" in (ev.get("review_reasons") or [])
    assert fdb.doc("users/uid_X")["stripe_tier"] == "estate"
    assert fdb.doc("users/x@x.com")["stripe_tier"] == "estate"


def test_T_N1_invoice_without_subscription_skips_ledger(fdb, recs, spies):
    recs["uid_P"] = POST("p@x.com")
    fdb.seed("stripe_payments/pi_life", {"uid": "uid_P", "kind": "lifetime", "tier": "family_estate", "granted": True})
    inv = {"id": "in_oneoff", "customer": "cus_1", "subscription": None, "payment_intent": "pi_oneoff"}
    r, eid = post_event("invoice.paid", inv)
    assert r.status_code == 200
    assert ev_doc(fdb, eid)["status"] == "done"
    assert ev_doc(fdb, eid)["reason"] == "invoice_no_subscription"
    assert fdb.doc("stripe_payments/pi_oneoff") is None
    assert fdb.doc("stripe_payments/pi_life")["kind"] == "lifetime"


def test_T_N2_deleted_auth_user_cancel_falls_back_to_entitlements_email(fdb, recs, spies):
    fdb.seed("stripe_customers/cus_1", {"uid": "uid_del"})
    fdb.seed("users/uid_del", {"stripe_tier": "dealer", "stripe_customer_id": "cus_1"})
    fdb.seed("users/del@x.com", {"stripe_tier": "dealer", "stripe_customer_id": "cus_1"})
    fdb.seed("entitlements/uid_del", {"stripe_subscription_id": "sub_1", "email": "del@x.com"})
    with patch("tier_gatekeeper.firebase_auth.get_user",
               side_effect=tier_gatekeeper.firebase_auth.UserNotFoundError("not found")):
        r, eid = post_event("customer.subscription.deleted", subscription())
    assert r.status_code == 200
    assert ev_doc(fdb, eid)["status"] == "done"
    assert fdb.doc("users/uid_del")["stripe_tier"] is None
    assert fdb.doc("users/del@x.com")["stripe_tier"] is None


def test_T_D1a_creates_missing_uid_doc_and_updates_email_doc(fdb, recs, spies):
    recs["uid_P"] = POST("p@x.com")
    fdb.seed("users/p@x.com", {"coins_migrated": True})
    r, eid = post_event("checkout.session.completed", session(tier="numismatist"))
    assert r.status_code == 200
    assert ev_doc(fdb, eid)["status"] == "done"
    assert fdb.doc("users/uid_P")["stripe_tier"] == "numismatist"
    assert fdb.doc("users/p@x.com")["stripe_tier"] == "numismatist"
    assert fdb.doc("stripe_customers/cus_1")["uid"] == "uid_P"
    assert fdb.doc("entitlements/uid_P")["stripe_subscription_id"] == "sub_1"


def test_T_D1b_merge_preserves_existing_uid_fields(fdb, recs, spies):
    recs["uid_P"] = POST("p@x.com")
    fdb.seed("users/uid_P", {"default_sort_field": "year_asc"})
    r, eid = post_event("checkout.session.completed", session(tier="numismatist"))
    assert r.status_code == 200
    u = fdb.doc("users/uid_P")
    assert u["stripe_tier"] == "numismatist"
    assert u["default_sort_field"] == "year_asc"


def test_T_D1c_unknown_uid_fails_without_grant_or_refund(fdb, recs, spies):
    with patch("tier_gatekeeper.firebase_auth.get_user",
               side_effect=tier_gatekeeper.firebase_auth.UserNotFoundError("not found")):
        r, eid = post_event("checkout.session.completed", session(uid="uid_missing", email="m@x.com"))
    assert r.status_code == 200
    ev = ev_doc(fdb, eid)
    assert ev["status"] == "failed" and ev["reason"] == "grant_uid_unknown" and ev["review_required"] is True
    assert fdb.doc("users/uid_missing") is None
    assert fdb.doc("users/m@x.com") is None
    _never_cancel_or_refund(spies)


def test_T_D1d_generic_auth_error_returns_500_retry(fdb, recs, spies):
    with patch("tier_gatekeeper.firebase_auth.get_user", side_effect=RuntimeError("auth down")):
        r, eid = post_event("checkout.session.completed", session())
    assert r.status_code == 500
    assert ev_doc(fdb, eid)["status"] == "retry"


def test_T_D1e_unmapped_renewal_fails_without_email_write(fdb, recs, spies):
    fdb.seed("users/p@x.com", {"stripe_tier": "free"})
    inv = {"id": "in_unmapped", "customer": "cus_unknown", "subscription": "sub_x",
           "customer_email": "p@x.com", "parent": {"subscription_details": {"metadata": {}}}}
    r, eid = post_event("invoice.paid", inv)
    assert r.status_code == 200
    ev = ev_doc(fdb, eid)
    assert ev["status"] == "failed" and ev["reason"] == "renewal_uid_unknown"
    assert fdb.doc("users/p@x.com")["stripe_tier"] == "free"


def test_T_SAG2_cancel_nulls_both_uid_and_email_docs_and_reverts_to_free(fdb, recs, spies):
    recs["uid_P"] = POST("p@x.com")
    fdb.seed("stripe_customers/cus_1", {"uid": "uid_P"})
    fdb.seed("users/p@x.com", {"stripe_tier": "dealer", "stripe_customer_id": "cus_1"})
    fdb.seed("users/uid_P", {"stripe_customer_id": "cus_1"})
    fdb.seed("entitlements/uid_P", {"stripe_subscription_id": "sub_1", "email": "p@x.com"})
    r, eid = post_event("customer.subscription.deleted", subscription())
    assert r.status_code == 200
    assert ev_doc(fdb, eid)["status"] == "done"
    u_uid = fdb.doc("users/uid_P")
    u_em = fdb.doc("users/p@x.com")
    assert "stripe_tier" in u_uid and u_uid["stripe_tier"] is None
    assert "stripe_tier" in u_em and u_em["stripe_tier"] is None
    profile, ent = load_entitlement_profile(fdb, "uid_P", "p@x.com")
    assert effective_limit(profile, ent, NOW) == 10


# ==============================================================================
# C3: Checkout create, price cross-check, Stripe Tax, portal, seller removal
# ==============================================================================

def _co_client(fdb, uid="uid_P", email="p@x.com", provider="password"):
    tok = {"uid": uid, "user_id": uid, "email": email, "firebase": {"sign_in_provider": provider}}
    app.dependency_overrides[get_current_user] = lambda: tok
    return TestClient(app, raise_server_exceptions=False), app


@pytest.mark.parametrize("tier", ["pro", "numismatist", "dealer", "estate"])
@pytest.mark.parametrize("interval", ["month", "year"])
def test_T_CO_1_subscription_checkout_kwargs(fdb, tier, interval):
    client, app = _co_client(fdb)
    try:
        with patch("routes.payment_routes.stripe.api_key", "sk_test_1"), \
             patch("routes.payment_routes.stripe.checkout.Session.create",
                   return_value=MagicMock(url="https://checkout.stripe.com/c", id="cs_1")) as spy:
            r = client.post("/api/stripe/create-checkout-session", json={"tier": tier, "interval": interval})
        assert r.status_code == 200
        kw = spy.call_args.kwargs
        assert kw["mode"] == "subscription"
        assert kw["client_reference_id"] == "uid_P"
        assert kw["customer_email"] == "p@x.com"
        assert kw["allow_promotion_codes"] is False
        assert kw["payment_method_types"] == ["card"]
        assert kw["automatic_tax"] == {"enabled": True}
        assert kw["success_url"] == "https://numista.ai/#/settings?stripe=success"
        assert kw["cancel_url"] == "https://numista.ai/#/settings?stripe=cancel"
        assert "customer" not in kw and "customer_update" not in kw
        assert kw["line_items"][0]["quantity"] == 1
        pd = kw["line_items"][0]["price_data"]
        assert pd["currency"] == "usd"
        assert pd["unit_amount"] == tier_gatekeeper.PRICE_CENTS[tier][interval]
        assert pd["tax_behavior"] == "exclusive"
        assert pd["recurring"] == {"interval": interval}
        exp_md = {"user_uid": "uid_P", "user_email": "p@x.com", "target_tier": tier,
                  "purchase_kind": "subscription", "interval": interval}
        assert kw["metadata"] == exp_md
        assert kw["subscription_data"]["metadata"] == exp_md
    finally:
        app.dependency_overrides.clear()


def test_T_CO_2_estate_year_15000_and_no_2900_in_codebase(fdb):
    client, app = _co_client(fdb)
    try:
        with patch("routes.payment_routes.stripe.api_key", "sk_test_1"), \
             patch("routes.payment_routes.stripe.checkout.Session.create",
                   return_value=MagicMock(url="https://checkout.stripe.com/c", id="cs_1")) as spy:
            r = client.post("/api/stripe/create-checkout-session", json={"tier": "estate", "interval": "year"})
        assert r.status_code == 200
        assert spy.call_args.kwargs["line_items"][0]["price_data"]["unit_amount"] == 15000
    finally:
        app.dependency_overrides.clear()
    root = pathlib.Path(__file__).resolve().parents[1]
    for target in [root / "tier_gatekeeper.py", *(root / "routes").rglob("*.py")]:
        assert "2900" not in target.read_text(encoding="utf-8", errors="ignore"), str(target)


def test_T_CO_3_lifetime_checkout_kwargs(fdb):
    client, app = _co_client(fdb)
    try:
        with patch("routes.payment_routes.stripe.api_key", "sk_test_1"), \
             patch("routes.payment_routes.stripe.checkout.Session.create",
                   return_value=MagicMock(url="https://checkout.stripe.com/c", id="cs_L")) as spy:
            r = client.post("/api/stripe/create-checkout-session", json={"tier": "family_estate"})
        assert r.status_code == 200
        kw = spy.call_args.kwargs
        assert kw["mode"] == "payment"
        assert kw["client_reference_id"] == "uid_P"
        assert kw["customer_email"] == "p@x.com"
        assert kw["customer_creation"] == "always"
        assert kw["allow_promotion_codes"] is False
        assert kw["payment_method_types"] == ["card"]
        assert kw["automatic_tax"] == {"enabled": True}
        assert kw["success_url"] == "https://numista.ai/#/settings?stripe=success"
        assert kw["cancel_url"] == "https://numista.ai/#/settings?stripe=cancel"
        assert kw["line_items"][0]["quantity"] == 1
        pd = kw["line_items"][0]["price_data"]
        assert pd["currency"] == "usd"
        assert pd["unit_amount"] == 50000
        assert pd["tax_behavior"] == "exclusive"
        assert "recurring" not in pd
        exp_md = {
            "user_uid": "uid_P",
            "user_email": "p@x.com",
            "target_tier": "family_estate",
            "purchase_kind": "lifetime",
        }
        assert kw["metadata"] == exp_md
        assert kw["payment_intent_data"]["metadata"] == exp_md
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize("uid,email,provider", [
    ("uid_anon", "a@x.com", "anonymous"),
    ("uid_noemail", "", "password"),
    ("bad@uid", "a@x.com", "password"),
    ("", "a@x.com", "password"),
])
def test_T_CO_3b_lifetime_guest_or_no_email_403(fdb, uid, email, provider):
    client, app = _co_client(fdb, uid=uid, email=email, provider=provider)
    try:
        with patch("routes.payment_routes.stripe.api_key", "sk_test_1"), \
             patch("routes.payment_routes.stripe.checkout.Session.create") as spy:
            r = client.post("/api/stripe/create-checkout-session", json={"tier": "family_estate"})
        assert r.status_code == 403
        assert r.json()["detail"]["error"] == "sign_in_required"
        spy.assert_not_called()
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize("bad_tier", ["sovereign", "power_user", "founding_beta", "gold", ""])
def test_T_CO_4_unsellable_tier_400(fdb, bad_tier):
    client, app = _co_client(fdb)
    try:
        with patch("routes.payment_routes.stripe.api_key", "sk_test_1"), \
             patch("routes.payment_routes.stripe.checkout.Session.create") as spy:
            r = client.post("/api/stripe/create-checkout-session", json={"tier": bad_tier})
        assert r.status_code == 400
        spy.assert_not_called()
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize("uid,email,provider", [
    ("uid_anon", "a@x.com", "anonymous"),
    ("uid_noemail", "", "password"),
    ("bad@uid", "a@x.com", "password"),
    ("", "a@x.com", "password"),
])
def test_T_CO_5_guest_or_no_email_403(fdb, uid, email, provider):
    client, app = _co_client(fdb, uid=uid, email=email, provider=provider)
    try:
        with patch("routes.payment_routes.stripe.api_key", "sk_test_1"), \
             patch("routes.payment_routes.stripe.checkout.Session.create") as spy:
            r = client.post("/api/stripe/create-checkout-session", json={"tier": "pro"})
        assert r.status_code == 403
        assert r.json()["detail"]["error"] == "sign_in_required"
        spy.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_T_CO_6_ignores_body_user_email_and_extras(fdb):
    client, app = _co_client(fdb, uid="uid_tok", email="tok@x.com")
    try:
        with patch("routes.payment_routes.stripe.api_key", "sk_test_1"), \
             patch("routes.payment_routes.stripe.checkout.Session.create",
                   return_value=MagicMock(url="https://checkout.stripe.com/c", id="cs_1")) as spy:
            r = client.post("/api/stripe/create-checkout-session",
                            json={"tier": "pro", "user_email": "evil@x.com", "beta_special": True})
        assert r.status_code == 200
        kw = spy.call_args.kwargs
        assert kw["client_reference_id"] == "uid_tok"
        assert kw["customer_email"] == "tok@x.com"
        assert kw["metadata"]["purchase_kind"] == "subscription"
    finally:
        app.dependency_overrides.clear()


def test_T_CO_7_already_subscribed_409(fdb):
    fdb.seed("entitlements/uid_P", {"stripe_subscription_id": "sub_1"})
    fdb.seed("users/uid_P", {"subscription_status": "active"})
    client, app = _co_client(fdb)
    try:
        with patch("routes.payment_routes.stripe.api_key", "sk_test_1"), \
             patch("routes.payment_routes.stripe.checkout.Session.create") as spy:
            r = client.post("/api/stripe/create-checkout-session", json={"tier": "pro"})
        assert r.status_code == 409
        assert r.json()["detail"]["error"] == "already_subscribed"
        spy.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_T_CO_8_already_lifetime_409(fdb):
    fdb.seed("users/uid_P", {"is_lifetime_family_estate": True})
    client, app = _co_client(fdb)
    try:
        with patch("routes.payment_routes.stripe.api_key", "sk_test_1"), \
             patch("routes.payment_routes.stripe.checkout.Session.create") as spy:
            r = client.post("/api/stripe/create-checkout-session", json={"tier": "family_estate"})
        assert r.status_code == 409
        assert r.json()["detail"]["error"] == "already_lifetime"
        spy.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_T_CO_9_bad_interval_400(fdb):
    client, app = _co_client(fdb)
    try:
        with patch("routes.payment_routes.stripe.api_key", "sk_test_1"), \
             patch("routes.payment_routes.stripe.checkout.Session.create") as spy:
            r = client.post("/api/stripe/create-checkout-session", json={"tier": "pro", "interval": "week"})
        assert r.status_code == 400
        spy.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_T_CO_10_stripe_exception_502(fdb):
    client, app = _co_client(fdb)
    try:
        with patch("routes.payment_routes.stripe.api_key", "sk_test_1"), \
             patch("routes.payment_routes.stripe.checkout.Session.create", side_effect=RuntimeError("boom")):
            r = client.post("/api/stripe/create-checkout-session", json={"tier": "pro"})
        assert r.status_code == 502
    finally:
        app.dependency_overrides.clear()


def test_T_NONUS_1_no_country_restriction_kwargs(fdb):
    client, app = _co_client(fdb)
    try:
        with patch("routes.payment_routes.stripe.api_key", "sk_test_1"), \
             patch("routes.payment_routes.stripe.checkout.Session.create",
                   return_value=MagicMock(url="https://checkout.stripe.com/c", id="cs_1")) as spy:
            r = client.post("/api/stripe/create-checkout-session", json={"tier": "pro"})
        assert r.status_code == 200
        kw = spy.call_args.kwargs
        assert kw["automatic_tax"] == {"enabled": True}
        for forbidden in ("billing_address_collection", "shipping_address_collection", "allowed_countries", "country"):
            assert forbidden not in kw
    finally:
        app.dependency_overrides.clear()


def test_T_NONUS_2_non_us_buyers_granted_never_refunded(fdb, recs, spies):
    recs["uid_P"] = POST("p@x.com")
    r1, eid1 = post_event("checkout.session.completed",
                          session(tier="pro", customer_details={"address": {"country": "DE"}}))
    assert r1.status_code == 200 and ev_doc(fdb, eid1)["status"] == "done"
    assert fdb.doc("users/uid_P")["stripe_tier"] == "pro"
    r2, eid2 = post_event("checkout.session.completed",
                          lifetime_session(customer_details={"address": {"country": "GB"}}))
    assert r2.status_code == 200 and ev_doc(fdb, eid2)["status"] == "done"
    assert fdb.doc("users/uid_P")["is_lifetime_family_estate"] is True
    _never_cancel_or_refund(spies)


def test_T_PRICE_1_subtotal_mismatch_fails_without_grant(fdb, recs, spies):
    recs["uid_P"] = POST("p@x.com")
    r, eid = post_event("checkout.session.completed", session(tier="estate", amount_subtotal=399))
    assert r.status_code == 200
    ev = ev_doc(fdb, eid)
    assert ev["status"] == "failed" and ev["reason"] == "amount_mismatch"
    assert fdb.doc("users/uid_P") is None


def test_T_TAX_1_records_subtotal_tax_total_on_subscription_and_lifetime(fdb, recs, spies):
    recs["uid_P"] = POST("p@x.com")
    r1, eid1 = post_event("checkout.session.completed",
                          session(tier="numismatist", pi="pi_S", amount_subtotal=799,
                                  amount_total=855, total_details={"amount_tax": 56}))
    assert r1.status_code == 200 and ev_doc(fdb, eid1)["status"] == "done"
    p_sub = fdb.doc("stripe_payments/pi_S")
    assert p_sub["amount_subtotal"] == 799 and p_sub["amount_tax"] == 56 and p_sub["amount_total"] == 855 and p_sub["amount_discount"] == 0

    r2, eid2 = post_event("checkout.session.completed",
                          lifetime_session(pi="pi_L2", amount=50000, amount_total=53500,
                                           total_details={"amount_tax": 3500}))
    assert r2.status_code == 200 and ev_doc(fdb, eid2)["status"] == "done"
    life = fdb.doc("entitlements/uid_P")["lifetime"]
    p_life = fdb.doc("stripe_payments/pi_L2")
    for row in (life, p_life):
        assert row["amount_subtotal"] == 50000
        assert row["amount_tax"] == 3500
        assert row["amount_total"] == 53500
        assert row["currency"] == "usd"


def test_T_TAX_2_tax_cannot_mask_wrong_tier(fdb, recs, spies):
    recs["uid_P"] = POST("p@x.com")
    r, eid = post_event("checkout.session.completed",
                        session(tier="estate", amount_subtotal=799, amount_total=1599,
                                total_details={"amount_tax": 800}))
    assert ev_doc(fdb, eid)["status"] == "failed" and ev_doc(fdb, eid)["reason"] == "amount_mismatch"


def test_T_PRICE_2_missing_interval_fails_amount_mismatch(fdb, recs, spies):
    recs["uid_P"] = POST("p@x.com")
    r, eid = post_event("checkout.session.completed", session(tier="pro", interval=None, amount_subtotal=399))
    assert ev_doc(fdb, eid)["status"] == "failed" and ev_doc(fdb, eid)["reason"] == "amount_mismatch"


def test_T_PRICE_3_subscription_updated_price_mismatch_flags_review(fdb, recs, spies):
    grant_gold(fdb, recs)
    sub_obj = subscription(metadata={"target_tier": "estate"})
    sub_obj["items"] = {"data": [{"price": {"unit_amount": 399, "recurring": {"interval": "month"}}}]}
    r, eid = post_event("customer.subscription.updated", sub_obj)
    assert r.status_code == 200
    ev = ev_doc(fdb, eid)
    assert ev["status"] == "done"
    assert "price_tier_mismatch" in (ev.get("review_reasons") or [])
    assert fdb.doc("users/uid_P")["stripe_tier"] == "estate"


def test_T_PORTAL_1_verified_map_opens_portal(fdb):
    fdb.seed("entitlements/uid_P", {"stripe_customer_id": "cus_1"})
    fdb.seed("stripe_customers/cus_1", {"uid": "uid_P"})
    client, app = _co_client(fdb)
    try:
        with patch("routes.payment_routes.stripe.api_key", "sk_test_1"), \
             patch("routes.payment_routes.stripe.billing_portal.Session.create",
                   return_value=MagicMock(url="https://billing.stripe.com/p")) as spy:
            r = client.post("/api/stripe/create-customer-portal")
        assert r.status_code == 200
        assert spy.call_args.kwargs["customer"] == "cus_1"
        assert spy.call_args.kwargs["return_url"] == "https://numista.ai/#/settings"
    finally:
        app.dependency_overrides.clear()


def test_T_PORTAL_2_mismatch_uid_returns_403(fdb):
    fdb.seed("entitlements/uid_P", {"stripe_customer_id": "cus_1"})
    fdb.seed("stripe_customers/cus_1", {"uid": "uid_OTHER"})
    client, app = _co_client(fdb)
    try:
        with patch("routes.payment_routes.stripe.api_key", "sk_test_1"), \
             patch("routes.payment_routes.stripe.billing_portal.Session.create") as spy:
            r = client.post("/api/stripe/create-customer-portal")
        assert r.status_code == 403
        assert r.json()["detail"]["error"] == "billing_account_mismatch"
        spy.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_T_PORTAL_3_no_entitlements_404_no_customer_list_or_create(fdb):
    client, app = _co_client(fdb)
    try:
        with patch("routes.payment_routes.stripe.api_key", "sk_test_1"), \
             patch("routes.payment_routes.stripe.Customer.list") as list_spy, \
             patch("routes.payment_routes.stripe.Customer.create") as create_spy:
            r = client.post("/api/stripe/create-customer-portal")
        assert r.status_code == 404
        list_spy.assert_not_called()
        create_spy.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_T_SELLER_1_second_seller_deleted_and_upgrade_url_none(fdb):
    assert hasattr(tier_gatekeeper, "create_upgrade_checkout_session") is False
    with patch.object(tier_gatekeeper, "load_entitlement_profile", return_value=({"stripe_tier": "free"}, {})), \
         patch.object(tier_gatekeeper, "get_coin_count", return_value=15):
        with pytest.raises(HTTPException) as exc:
            tier_gatekeeper.check_and_enforce_coin_limit("uid_P")
    assert exc.value.status_code == 403
    assert exc.value.detail["upgrade_url"] is None


# ==============================================================================
# C4: Legacy limit helpers (T78-T84, T87-T92)
# ==============================================================================

def test_T78_enforce_coin_limit_uses_auth_facts(fdb, recs):
    recs["uid_P"] = FOUNDER("p@x.com")
    fdb.seed_coins("uid_P", 500)
    with patch.object(tier_gatekeeper, "db", fdb):
        assert tier_gatekeeper.check_and_enforce_coin_limit("uid_P") is True


def test_T79_enforce_coin_limit_post_cutoff_free_blocks_at_11(fdb, recs):
    recs["uid_P"] = POST("p@x.com")
    fdb.seed_coins("uid_P", 11)
    with patch.object(tier_gatekeeper, "db", fdb):
        with pytest.raises(HTTPException) as exc:
            tier_gatekeeper.check_and_enforce_coin_limit("uid_P", email="p@x.com")
    assert exc.value.status_code == 403
    assert exc.value.detail["stats"]["limit"] == 10


def test_T80_enforce_coin_limit_ignores_power_user_bool(fdb, recs):
    recs["uid_P"] = POST("p@x.com")
    fdb.seed("users/uid_P", {"power_user": True})
    fdb.seed_coins("uid_P", 11)
    with patch.object(tier_gatekeeper, "db", fdb):
        with pytest.raises(HTTPException) as exc:
            tier_gatekeeper.check_and_enforce_coin_limit("uid_P", email="p@x.com")
    assert exc.value.status_code == 403


def test_T81_enforce_coin_limit_auth_down_raises_unavailable(fdb):
    with patch.object(tier_gatekeeper, "db", fdb), \
         patch("tier_gatekeeper.firebase_auth.get_user", side_effect=RuntimeError("down")):
        with pytest.raises(tier_gatekeeper.AuthFactsUnavailable):
            tier_gatekeeper.check_and_enforce_coin_limit("uid_P")


def test_T82_daily_usage_post_cutoff_free_allows_3_blocks_4th(fdb, recs):
    recs["uid_P"] = POST("p@x.com")
    with patch.object(tier_gatekeeper, "db", fdb):
        assert tier_gatekeeper.check_and_increment_daily_usage("uid_P", "deepdive") is True
        assert tier_gatekeeper.check_and_increment_daily_usage("uid_P", "deepdive") is True
        assert tier_gatekeeper.check_and_increment_daily_usage("uid_P", "deepdive") is True
        assert tier_gatekeeper.check_and_increment_daily_usage("uid_P", "deepdive") is False


def test_T83_daily_usage_resets_on_new_day(fdb, recs):
    recs["uid_P"] = POST("p@x.com")
    fdb.seed("users/uid_P", {"last_usage_date": "2020-01-01", "deepdive_count": 99})
    with patch.object(tier_gatekeeper, "db", fdb):
        assert tier_gatekeeper.check_and_increment_daily_usage("uid_P", "deepdive") is True
    assert fdb.doc("users/uid_P")["deepdive_count"] == 1


def test_T84_daily_usage_ignores_power_user_bool(fdb, recs):
    recs["uid_P"] = POST("p@x.com")
    fdb.seed("users/uid_P", {"power_user": True, "last_usage_date": "2020-01-01"})
    with patch.object(tier_gatekeeper, "db", fdb):
        for _ in range(3):
            assert tier_gatekeeper.check_and_increment_daily_usage("uid_P", "deepdive") is True
        assert tier_gatekeeper.check_and_increment_daily_usage("uid_P", "deepdive") is False


def test_T87_daily_usage_unverified_family_group_id_ignored(fdb, recs):
    recs["uid_P"] = POST("p@x.com")
    fdb.seed("users/uid_P", {"family_group_id": "fg_fake"})
    fdb.seed("family_groups/fg_fake", {"owner_uid": "uid_OTHER", "members": ["uid_OTHER"]})
    with patch.object(tier_gatekeeper, "db", fdb):
        for _ in range(3):
            assert tier_gatekeeper.check_and_increment_daily_usage("uid_P", "deepdive") is True
        assert tier_gatekeeper.check_and_increment_daily_usage("uid_P", "deepdive") is False
    assert fdb.doc("users/uid_P")["deepdive_count"] == 3


def test_T88_daily_usage_verified_family_member_uses_group_allowance(fdb, recs):
    recs["uid_P"] = POST("p@x.com")
    fdb.seed("users/uid_P", {"family_group_id": "fg_real"})
    fdb.seed("family_groups/fg_real", {"owner_uid": "uid_OWNER", "members": ["uid_P"]})
    with patch.object(tier_gatekeeper, "db", fdb):
        assert tier_gatekeeper.check_and_increment_daily_usage("uid_P", "deepdive") is True
    assert fdb.doc("family_groups/fg_real")["deepdive_count"] == 1


def test_T89_daily_usage_missing_family_group_doc_ignored(fdb, recs):
    recs["uid_P"] = POST("p@x.com")
    fdb.seed("users/uid_P", {"family_group_id": "fg_missing"})
    with patch.object(tier_gatekeeper, "db", fdb):
        assert tier_gatekeeper.check_and_increment_daily_usage("uid_P", "deepdive") is True
    assert fdb.doc("users/uid_P")["deepdive_count"] == 1


def test_T90_daily_usage_founder_gets_1500_limit(fdb, recs):
    recs["uid_P"] = FOUNDER("p@x.com")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    fdb.seed("users/uid_P", {"last_usage_date": today, "deepdive_count": 1499})
    with patch.object(tier_gatekeeper, "db", fdb):
        assert tier_gatekeeper.check_and_increment_daily_usage("uid_P", "deepdive") is True
        assert tier_gatekeeper.check_and_increment_daily_usage("uid_P", "deepdive") is False


def test_T91_daily_usage_runs_inside_run_txn(fdb, recs):
    recs["uid_P"] = POST("p@x.com")
    with patch.object(tier_gatekeeper, "db", fdb), \
         patch.object(tier_gatekeeper, "_run_txn", wraps=tier_gatekeeper._run_txn) as spy:
        assert tier_gatekeeper.check_and_increment_daily_usage("uid_P", "invoice_scan") is True
    assert spy.call_count == 1


def test_T92_daily_usage_auth_down_raises_unavailable(fdb):
    with patch.object(tier_gatekeeper, "db", fdb), \
         patch("tier_gatekeeper.firebase_auth.get_user", side_effect=RuntimeError("down")):
        with pytest.raises(tier_gatekeeper.AuthFactsUnavailable):
            tier_gatekeeper.check_and_increment_daily_usage("uid_P", "deepdive")


def test_T_WH_SIG_1_missing_signature_header_400(fdb):
    with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_real_test"}), \
         patch("routes.payment_routes.stripe.Webhook.construct_event") as spy:
        client = TestClient(app, raise_server_exceptions=False)
        r = client.post("/api/stripe/webhook", content=b'{"id":"evt_1"}')
    assert r.status_code == 400
    spy.assert_not_called()


def test_T_WH_SIG_2_invalid_signature_400_and_passes_raw_args(fdb):
    raw_body = b'{"id":"evt_bad","type":"checkout.session.completed"}'
    sig = "t=123,v1=bad_sig"
    secret = "whsec_real_test"
    with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": secret}), \
         patch("routes.payment_routes.stripe.Webhook.construct_event",
               side_effect=stripe.SignatureVerificationError("bad sig", sig)) as spy:
        client = TestClient(app, raise_server_exceptions=False)
        r = client.post("/api/stripe/webhook", content=raw_body, headers={"stripe-signature": sig})
    assert r.status_code == 400
    spy.assert_called_once_with(raw_body, sig, secret)


# ==============================================================================
# v2.0.7 Delta Tests: CHRISTMAS2026 (T-XMAS-1..7), Guarded TEST100 (T-TEST100-1..4),
# and D1 Named Outbound P5 Exact-Request Tests (T-P5-SESSION-SUB/LIFE/PORTAL)
# ==============================================================================


@pytest.mark.parametrize("tier,interval", [
    ("pro", "month"), ("pro", "year"),
    ("numismatist", "month"), ("numismatist", "year"),
    ("dealer", "month"), ("dealer", "year"),
    ("estate", "month"), ("estate", "year"),
])
def test_T_XMAS_1_all_combos_inside_window(fdb, tier, interval):
    client, app = _co_client(fdb)
    try:
        with patch("routes.payment_routes.stripe.api_key", "placeholder_key"), \
             patch("routes.payment_routes.time.time", return_value=float(tier_gatekeeper.CHRISTMAS2026_START_UTC + 10)), \
             patch("routes.payment_routes.stripe.checkout.Session.create",
                   return_value=MagicMock(url="https://checkout.stripe.com/x", id="cs_x")) as spy:
            r = client.post(
                "/api/stripe/create-checkout-session",
                json={"tier": tier, "interval": interval, "promo_code": " christmas2026 "},
            )
        assert r.status_code == 200
        kw = spy.call_args.kwargs
        assert kw["line_items"][0]["price_data"]["unit_amount"] == tier_gatekeeper.PRICE_CENTS[tier][interval]
        assert kw["discounts"] == [{"coupon": tier_gatekeeper.CHRISTMAS2026_COUPON_IDS[tier][interval]}]
        assert "allow_promotion_codes" not in kw
        assert kw["metadata"]["promo_code"] == "CHRISTMAS2026"
        assert kw["subscription_data"]["metadata"]["promo_code"] == "CHRISTMAS2026"
    finally:
        app.dependency_overrides.clear()


def test_T_XMAS_2_before_window_400(fdb):
    client, app = _co_client(fdb)
    try:
        with patch("routes.payment_routes.stripe.api_key", "placeholder_key"), \
             patch("routes.payment_routes.time.time", return_value=float(tier_gatekeeper.CHRISTMAS2026_START_UTC - 1)), \
             patch("routes.payment_routes.stripe.checkout.Session.create") as spy:
            r = client.post(
                "/api/stripe/create-checkout-session",
                json={"tier": "pro", "interval": "year", "promo_code": "CHRISTMAS2026"},
            )
        assert r.status_code == 400
        assert r.json()["detail"]["error"] == "promo_not_active"
        spy.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_T_XMAS_3_at_or_after_end_400(fdb):
    client, app = _co_client(fdb)
    try:
        with patch("routes.payment_routes.stripe.api_key", "placeholder_key"), \
             patch("routes.payment_routes.time.time", return_value=float(tier_gatekeeper.CHRISTMAS2026_END_UTC)), \
             patch("routes.payment_routes.stripe.checkout.Session.create") as spy:
            r = client.post(
                "/api/stripe/create-checkout-session",
                json={"tier": "pro", "interval": "month", "promo_code": "CHRISTMAS2026"},
            )
        assert r.status_code == 400
        assert r.json()["detail"]["error"] == "promo_not_active"
        spy.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_T_XMAS_4_lifetime_rejected_400(fdb):
    client, app = _co_client(fdb)
    try:
        with patch("routes.payment_routes.stripe.api_key", "placeholder_key"), \
             patch("routes.payment_routes.time.time", return_value=float(tier_gatekeeper.CHRISTMAS2026_START_UTC + 10)), \
             patch("routes.payment_routes.stripe.checkout.Session.create") as spy:
            r = client.post(
                "/api/stripe/create-checkout-session",
                json={"tier": "family_estate", "promo_code": "CHRISTMAS2026"},
            )
        assert r.status_code == 400
        assert r.json()["detail"]["error"] == "promo_not_applicable_to_lifetime"
        spy.assert_not_called()
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize("tier,interval", [
    ("pro", "month"), ("pro", "year"),
    ("numismatist", "month"), ("numismatist", "year"),
    ("dealer", "month"), ("dealer", "year"),
    ("estate", "month"), ("estate", "year"),
])
def test_T_XMAS_5_webhook_all_combos_exact_discount_and_ledger(fdb, recs, spies, tier, interval):
    recs["uid_P"] = POST("p@x.com")
    sub_total = tier_gatekeeper.PRICE_CENTS[tier][interval]
    disc = tier_gatekeeper.CHRISTMAS2026_DISCOUNT_CENTS[tier][interval]
    net = sub_total - disc
    tax = 25
    pi_id = f"pi_{tier}_{interval}"
    ev_obj = session(
        tier=tier,
        interval=interval,
        pi=pi_id,
        amount_subtotal=sub_total,
        amount_total=net + tax,
        total_details={"amount_discount": disc, "amount_tax": tax},
    )
    ev_obj["metadata"]["promo_code"] = "CHRISTMAS2026"
    r, eid = post_event("checkout.session.completed", ev_obj)
    assert r.status_code == 200 and ev_doc(fdb, eid)["status"] == "done"
    row = fdb.doc(f"stripe_payments/{pi_id}")
    assert row["amount_subtotal"] == sub_total
    assert row["amount_discount"] == disc
    assert row["amount_tax"] == tax
    assert row["amount_total"] == net + tax
    assert row["promo_code"] == "CHRISTMAS2026"


def test_T_XMAS_6_webhook_wrong_or_unrequested_discount_fails(fdb, recs, spies):
    recs["uid_P"] = POST("p@x.com")
    ev1 = session(tier="pro", interval="month", pi="pi_bad1", amount_subtotal=399, amount_total=299,
                  total_details={"amount_discount": 100})
    ev1["metadata"]["promo_code"] = "CHRISTMAS2026"
    _, eid1 = post_event("checkout.session.completed", ev1)
    assert ev_doc(fdb, eid1)["status"] == "failed" and ev_doc(fdb, eid1)["reason"] == "discount_mismatch"

    ev2 = session(tier="pro", interval="month", pi="pi_bad2", amount_subtotal=399, amount_total=199,
                  total_details={"amount_discount": 200})
    _, eid2 = post_event("checkout.session.completed", ev2)
    assert ev_doc(fdb, eid2)["status"] == "failed" and ev_doc(fdb, eid2)["reason"] == "discount_mismatch"
    assert fdb.doc("users/uid_P") is None


def test_T_XMAS_7_webhook_lifetime_discount_fails(fdb, recs, spies):
    recs["uid_P"] = POST("p@x.com")
    ev = lifetime_session(pi="pi_Ldisc", amount=50000, amount_total=45000, total_details={"amount_discount": 5000})
    _, eid = post_event("checkout.session.completed", ev)
    assert ev_doc(fdb, eid)["status"] == "failed" and ev_doc(fdb, eid)["reason"] == "discount_mismatch"
    assert fdb.doc("users/uid_P") is None


def test_T_TEST100_1_unset_env_vars_400(fdb, monkeypatch):
    for k in ("STRIPE_TEST_PROMO_CODE", "STRIPE_TEST_COUPON_ID", "STRIPE_TEST_BUYER_EMAILS"):
        monkeypatch.delenv(k, raising=False)
    client, app = _co_client(fdb)
    try:
        with patch("routes.payment_routes.stripe.api_key", "placeholder_key"), \
             patch("routes.payment_routes.stripe.checkout.Session.create") as spy:
            r = client.post("/api/stripe/create-checkout-session", json={"tier": "pro", "promo_code": "MYTEST"})
        assert r.status_code == 400 and r.json()["detail"]["error"] == "promo_invalid"
        spy.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_T_TEST100_2_non_allowlisted_email_400(fdb, monkeypatch):
    monkeypatch.setenv("STRIPE_TEST_PROMO_CODE", "TEST_PROMO_SECRET")
    monkeypatch.setenv("STRIPE_TEST_COUPON_ID", "cpn_test100")
    monkeypatch.setenv("STRIPE_TEST_BUYER_EMAILS", "allowedbuyer@example.com")
    client, app = _co_client(fdb, email="other@example.com")
    try:
        with patch("routes.payment_routes.stripe.api_key", "placeholder_key"), \
             patch("routes.payment_routes.stripe.checkout.Session.create") as spy:
            r = client.post(
                "/api/stripe/create-checkout-session",
                json={"tier": "pro", "promo_code": "TEST_PROMO_SECRET"},
            )
        assert r.status_code == 400 and r.json()["detail"]["error"] == "promo_invalid"
        assert "TEST100" not in r.text
        spy.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_T_TEST100_3_allowlisted_normalized_sub_only_not_lifetime(fdb, monkeypatch):
    # M1 fix: both raw_promo and expected_code are stripped & uppercased before hmac.compare_digest
    monkeypatch.setenv("STRIPE_TEST_PROMO_CODE", "  test_code_100  ")
    monkeypatch.setenv("STRIPE_TEST_COUPON_ID", "cpn_test100")
    monkeypatch.setenv("STRIPE_TEST_BUYER_EMAILS", " Buyer1@Example.com , second@example.com ")
    client, app = _co_client(fdb, email="buyer1@example.com")
    try:
        with patch("routes.payment_routes.stripe.api_key", "placeholder_key"), \
             patch("routes.payment_routes.stripe.checkout.Session.create",
                   return_value=MagicMock(url="https://checkout.stripe.com/t", id="cs_t")) as spy:
            r_sub = client.post(
                "/api/stripe/create-checkout-session",
                json={"tier": "pro", "interval": "month", "promo_code": " test_code_100 "},
            )
        assert r_sub.status_code == 200
        kw = spy.call_args.kwargs
        assert kw["discounts"] == [{"coupon": "cpn_test100"}]
        assert "allow_promotion_codes" not in kw
        assert kw["metadata"]["promo_code"] == "TEST100"

        with patch("routes.payment_routes.stripe.api_key", "placeholder_key"), \
             patch("routes.payment_routes.stripe.checkout.Session.create") as spy_life:
            r_life = client.post(
                "/api/stripe/create-checkout-session",
                json={"tier": "family_estate", "promo_code": "test_code_100"},
            )
        assert r_life.status_code == 400 and r_life.json()["detail"]["error"] == "promo_invalid"
        spy_life.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_T_TEST100_4_webhook_zero_total_requires_configured_coupon_id(fdb, recs, spies, monkeypatch):
    recs["uid_P"] = POST("p@x.com")
    ev = session(
        tier="pro",
        interval="month",
        paid="no_payment_required",
        pi=None,
        amount_subtotal=399,
        amount_total=0,
        total_details={"amount_discount": 399, "amount_tax": 0},
    )
    ev["metadata"]["promo_code"] = "TEST100"

    monkeypatch.delenv("STRIPE_TEST_COUPON_ID", raising=False)
    ev["id"] = "evt_test100_unset"
    _, eid_fail = post_event("checkout.session.completed", dict(ev))
    assert ev_doc(fdb, eid_fail)["status"] == "failed" and ev_doc(fdb, eid_fail)["reason"] == "discount_mismatch"

    monkeypatch.setenv("STRIPE_TEST_COUPON_ID", "cpn_test100")
    ev["id"] = "evt_test100_ok"
    _, eid_ok = post_event("checkout.session.completed", dict(ev))
    assert ev_doc(fdb, eid_ok)["status"] == "done"
    assert fdb.doc("users/uid_P")["stripe_tier"] == "pro"


class _CaptureStripeHttpClient(stripe.HTTPClient):
    """D1 HTTP transport capture: intercepts real Stripe SDK serialization without storing secrets."""

    name = "capture"

    def __init__(self):
        super().__init__()
        self.captured = []

    def request(self, method, url, headers, post_data=None, *, _usage=None):
        self.captured.append({
            "method": method,
            "url": url,
            "header_names": sorted(k.lower() for k in (headers or {}).keys()),
            "post_data": post_data,
        })
        if "/v1/billing_portal/sessions" in url:
            body = {"id": "bps_p5_1", "object": "billing_portal.session", "url": "https://billing.stripe.com/p5"}
        else:
            body = {"id": "cs_p5_1", "object": "checkout.session", "url": "https://checkout.stripe.com/p5"}
        return json.dumps(body), 200, {"Content-Type": "application/json"}

    def request_with_retries(self, method, url, headers, post_data=None, max_network_retries=None, *, _usage=None):
        return self.request(method, url, headers, post_data=post_data, _usage=_usage)


def test_T_P5_SESSION_SUB(fdb):
    from urllib.parse import parse_qs

    capture = _CaptureStripeHttpClient()
    prev_client = stripe.default_http_client
    client, app = _co_client(fdb, uid="uid_P5", email="p5buyer@example.com")
    try:
        stripe.default_http_client = capture
        with patch("routes.payment_routes.stripe.api_key", "unit_test_dummy_key"), \
             patch("routes.payment_routes.time.time", return_value=float(tier_gatekeeper.CHRISTMAS2026_START_UTC + 100)):
            r_reg = client.post(
                "/api/stripe/create-checkout-session",
                json={"tier": "dealer", "interval": "year"},
            )
            r_xmas = client.post(
                "/api/stripe/create-checkout-session",
                json={"tier": "estate", "interval": "month", "promo_code": "CHRISTMAS2026"},
            )
        assert r_reg.status_code == 200
        assert r_xmas.status_code == 200
        assert len(capture.captured) == 2

        reg_req, xmas_req = capture.captured
        assert reg_req["method"].lower() == "post"
        assert reg_req["url"] == "https://api.stripe.com/v1/checkout/sessions"
        assert "authorization" in reg_req["header_names"]
        reg_form = parse_qs(reg_req["post_data"], keep_blank_values=True)
        assert reg_form["mode"] == ["subscription"]
        assert reg_form["customer_email"] == ["p5buyer@example.com"]
        assert reg_form["client_reference_id"] == ["uid_P5"]
        assert reg_form["allow_promotion_codes"] == ["false"]
        assert "discounts[0][coupon]" not in reg_form
        assert reg_form["line_items[0][price_data][unit_amount]"] == ["9900"]
        assert reg_form["line_items[0][price_data][tax_behavior]"] == ["exclusive"]
        assert reg_form["automatic_tax[enabled]"] == ["true"]
        assert reg_form["metadata[target_tier]"] == ["dealer"]
        assert reg_form["metadata[interval]"] == ["year"]
        assert reg_form["success_url"] == ["https://numista.ai/#/settings?stripe=success"]
        assert reg_form["cancel_url"] == ["https://numista.ai/#/settings?stripe=cancel"]

        assert xmas_req["method"].lower() == "post"
        assert xmas_req["url"] == "https://api.stripe.com/v1/checkout/sessions"
        assert "authorization" in xmas_req["header_names"]
        xmas_form = parse_qs(xmas_req["post_data"], keep_blank_values=True)
        assert xmas_form["mode"] == ["subscription"]
        assert xmas_form["line_items[0][price_data][unit_amount]"] == ["1599"]
        assert xmas_form["line_items[0][price_data][tax_behavior]"] == ["exclusive"]
        assert xmas_form["automatic_tax[enabled]"] == ["true"]
        assert xmas_form["discounts[0][coupon]"] == ["CHRISTMAS2026_GOLD_MONTH"]
        assert "allow_promotion_codes" not in xmas_form
        assert xmas_form["metadata[promo_code]"] == ["CHRISTMAS2026"]
        assert xmas_form["subscription_data[metadata][promo_code]"] == ["CHRISTMAS2026"]
    finally:
        stripe.default_http_client = prev_client
        app.dependency_overrides.clear()


def test_T_P5_SESSION_LIFE(fdb):
    from urllib.parse import parse_qs

    capture = _CaptureStripeHttpClient()
    prev_client = stripe.default_http_client
    client, app = _co_client(fdb, uid="uid_P5L", email="life@example.com")
    try:
        stripe.default_http_client = capture
        with patch("routes.payment_routes.stripe.api_key", "unit_test_dummy_key"):
            r = client.post("/api/stripe/create-checkout-session", json={"tier": "family_estate"})
        assert r.status_code == 200
        assert len(capture.captured) == 1
        req = capture.captured[0]
        assert req["method"].lower() == "post"
        assert req["url"] == "https://api.stripe.com/v1/checkout/sessions"
        assert "authorization" in req["header_names"]
        form = parse_qs(req["post_data"], keep_blank_values=True)
        assert form["mode"] == ["payment"]
        assert form["customer_creation"] == ["always"]
        assert form["allow_promotion_codes"] == ["false"]
        assert "discounts[0][coupon]" not in form
        assert form["line_items[0][price_data][unit_amount]"] == ["50000"]
        assert form["line_items[0][price_data][tax_behavior]"] == ["exclusive"]
        assert form["automatic_tax[enabled]"] == ["true"]
        assert form["metadata[purchase_kind]"] == ["lifetime"]
        assert form["payment_intent_data[metadata][target_tier]"] == ["family_estate"]
        assert form["success_url"] == ["https://numista.ai/#/settings?stripe=success"]
        assert form["cancel_url"] == ["https://numista.ai/#/settings?stripe=cancel"]
    finally:
        stripe.default_http_client = prev_client
        app.dependency_overrides.clear()


def test_T_P5_PORTAL(fdb):
    from urllib.parse import parse_qs

    fdb.seed("entitlements/uid_P5", {"stripe_customer_id": "cus_p5_99"})
    fdb.seed("stripe_customers/cus_p5_99", {"uid": "uid_P5"})
    capture = _CaptureStripeHttpClient()
    prev_client = stripe.default_http_client
    client, app = _co_client(fdb, uid="uid_P5", email="p5buyer@example.com")
    try:
        stripe.default_http_client = capture
        with patch("routes.payment_routes.stripe.api_key", "unit_test_dummy_key"):
            r = client.post("/api/stripe/create-customer-portal")
        assert r.status_code == 200
        assert len(capture.captured) == 1
        req = capture.captured[0]
        assert req["method"].lower() == "post"
        assert req["url"] == "https://api.stripe.com/v1/billing_portal/sessions"
        assert "authorization" in req["header_names"]
        form = parse_qs(req["post_data"], keep_blank_values=True)
        assert form["customer"] == ["cus_p5_99"]
        assert form["return_url"] == ["https://numista.ai/#/settings"]
    finally:
        stripe.default_http_client = prev_client
        app.dependency_overrides.clear()


def test_T_FB_1_subscription_status_pre_cutoff_sovereign_is_founding_beta(fdb, recs):
    recs["uid_FB_SOV"] = FOUNDER("founder@example.com")
    fdb.seed("users/uid_FB_SOV", {
        "tier": "sovereign",
        "stripe_tier": "sovereign",
        "is_ai_qc_account": True,
        "beta_tester": False,
    })
    client, app = _co_client(fdb, uid="uid_FB_SOV", email="founder@example.com")
    try:
        r = client.get("/api/stripe/subscription-status?uid=uid_FB_SOV")
        assert r.status_code == 200
        body = r.json()
        assert body["founding_beta"] is True
        assert body["stripe_tier"] == "sovereign"
        assert body["unlimited"] is True
        assert body["estate_access"] is True
        assert body["lifetime_family_estate"] is False
    finally:
        app.dependency_overrides.clear()


def test_T_FB_2_subscription_status_post_cutoff_sovereign_not_founding_beta(fdb, recs):
    recs["uid_POST_SOV"] = POST("post@example.com")
    fdb.seed("users/uid_POST_SOV", {
        "tier": "sovereign",
        "stripe_tier": "sovereign",
        "beta_tester": False,
        "is_lifetime_family_estate": False,
    })
    client, app = _co_client(fdb, uid="uid_POST_SOV", email="post@example.com")
    try:
        r = client.get("/api/stripe/subscription-status?uid=uid_POST_SOV")
        assert r.status_code == 200
        body = r.json()
        assert body["founding_beta"] is False
        assert body["stripe_tier"] == "sovereign"
        assert body["unlimited"] is True
        assert body["lifetime_family_estate"] is False
    finally:
        app.dependency_overrides.clear()


def test_T_FB_3_subscription_status_every_json_return_path_includes_founding_beta(fdb, recs):
    import ast

    # Structural AST check: every JSON dict return in _own_status and api_subscription_status sets "founding_beta".
    src_path = pathlib.Path(BACKEND) / "routes" / "payment_routes.py"
    tree = ast.parse(src_path.read_text(encoding="utf-8"))
    target_fns = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in ("_own_status", "api_subscription_status")
    }
    assert set(target_fns) == {"_own_status", "api_subscription_status"}
    for fn_name, fn_node in target_fns.items():
        for node in ast.walk(fn_node):
            if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict):
                keys = [k.value for k in node.value.keys if isinstance(k, ast.Constant)]
                assert "founding_beta" in keys, f"{fn_name} dict return missing 'founding_beta'"

    # Path (a): _own_status with active Stripe subscription + Stripe customer mapping (founder vs post-cutoff).
    recs["uid_SUB_F"] = FOUNDER("subfounder@example.com")
    fdb.seed("users/uid_SUB_F", {"stripe_tier": "estate", "stripe_customer_id": "cus_sub_f"})
    fdb.seed("entitlements/uid_SUB_F", {
        "stripe_customer_id": "cus_sub_f",
        "stripe_subscription_id": "sub_f_1",
        "stripe_tier": "estate",
        "subscription_status": "active",
        "email": "subfounder@example.com",
    })
    fdb.seed("stripe_customers/cus_sub_f", {"uid": "uid_SUB_F"})
    client, app = _co_client(fdb, uid="uid_SUB_F", email="subfounder@example.com")
    try:
        r_f = client.get("/api/stripe/subscription-status?uid=uid_SUB_F")
        assert r_f.status_code == 200
        assert r_f.json()["founding_beta"] is True
        assert r_f.json()["stripe_tier"] == "estate"
    finally:
        app.dependency_overrides.clear()

    recs["uid_SUB_P"] = POST("subpost@example.com")
    fdb.seed("users/uid_SUB_P", {"stripe_tier": "estate", "stripe_customer_id": "cus_sub_p"})
    fdb.seed("entitlements/uid_SUB_P", {
        "stripe_customer_id": "cus_sub_p",
        "stripe_subscription_id": "sub_p_1",
        "stripe_tier": "estate",
        "subscription_status": "active",
        "email": "subpost@example.com",
    })
    fdb.seed("stripe_customers/cus_sub_p", {"uid": "uid_SUB_P"})
    client, app = _co_client(fdb, uid="uid_SUB_P", email="subpost@example.com")
    try:
        r_p = client.get("/api/stripe/subscription-status?uid=uid_SUB_P")
        assert r_p.status_code == 200
        assert r_p.json()["founding_beta"] is False
        assert r_p.json()["stripe_tier"] == "estate"
    finally:
        app.dependency_overrides.clear()

    # Path (b): api_subscription_status fallback branch (admin reading non-own uid).
    recs["uid_ADM_F"] = FOUNDER("targetf@example.com")
    fdb.seed("users/uid_ADM_F", {"stripe_tier": "pro"})
    recs["uid_ADM_P"] = POST("targetp@example.com")
    fdb.seed("users/uid_ADM_P", {"stripe_tier": "pro"})
    app.dependency_overrides[get_current_user] = lambda: {
        "uid": "uid_admin",
        "user_id": "uid_admin",
        "email": "eric@numista.ai",
        "admin": True,
        "firebase": {"sign_in_provider": "password"},
    }
    try:
        admin_client = TestClient(app, raise_server_exceptions=False)
        r_af = admin_client.get("/api/stripe/subscription-status?uid=uid_ADM_F")
        assert r_af.status_code == 200
        assert r_af.json()["founding_beta"] is True

        r_ap = admin_client.get("/api/stripe/subscription-status?uid=uid_ADM_P")
        assert r_ap.status_code == 200
        assert r_ap.json()["founding_beta"] is False
    finally:
        app.dependency_overrides.clear()
