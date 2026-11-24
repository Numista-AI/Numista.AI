# ruff: noqa: F811  (pytest fixtures imported from test_net827_core are re-bound as test parameters)
"""NET-827 v2.0.4: Founding Beta accounts get Estate / Lifetime access (Eric t3000u, widget
5:37 PM ET 16 Nov 2026; CoS ruling: reuse AMEND-A's Founding Beta definition), and a
cancellation or refund never downgrades or locks a Founding Beta account (CoS scope A / N5).
Reuses the fakes and fixtures of tests/test_net827_core.py (same pattern as
tests/test_catalog_add_allowance.py:12)."""
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

import tier_gatekeeper
from tier_gatekeeper import (
    BETA_SIGNUP_CUTOFF_MS,
    ESTATE_STAFF_EMAILS,
    _tier_candidates,
    enforce_entitlement,
    estate_access,
    is_founding_beta,
    load_entitlement_profile,
)
from main import app
from routes.deps import get_current_user
from routes import payment_routes
from tests.test_net827_core import (  # noqa: F401  (fixtures are used by name)
    FOUNDER, FOUNDER_MS, GUEST, NOW, POST, POST_MS, _git_grep_count, _isolate, _rec, charge,
    ev_doc, fdb, grant_gold, grant_lifetime, post_event, recs, spies, subscription,
)


def _status(fdb, uid, email, query_uid=None, provider="password", admin=False):
    """GET /api/stripe/subscription-status as the token (uid, email). Returns (response, get_user mock calls)."""
    tok = {"uid": uid, "user_id": uid, "email": email, "admin": admin,
           "firebase": {"sign_in_provider": provider}}
    app.dependency_overrides[get_current_user] = lambda: tok
    client = TestClient(app, raise_server_exceptions=False)
    q = uid if query_uid is None else query_uid
    with patch("routes.payment_routes.get_coin_count", return_value=0):
        return client.get("/api/stripe/subscription-status", params={"uid": q})


def _p1_contract(results):
    """The P1 relock seam contract (as test_T86): relock goes through enforce_entitlement."""
    def hook(db, handler_uid, keys, swept, now):
        email = next((k for k in keys if "@" in k), None)
        results.append(enforce_entitlement(db, handler_uid, email, now))
        return {"accounts_reconciled": [handler_uid], "review_required": False, "review_reasons": []}
    return hook


# ── T-EB-1 / T-EB-2: the one Founding Beta rule ───────────────────────────────

@pytest.mark.parametrize("profile,expected", [
    ({"_auth_created_ms": FOUNDER_MS, "_auth_is_anonymous": False}, True),
    ({"_auth_created_ms": BETA_SIGNUP_CUTOFF_MS - 1, "_auth_is_anonymous": False}, True),
    ({"_auth_created_ms": BETA_SIGNUP_CUTOFF_MS, "_auth_is_anonymous": False}, False),
    ({"_auth_created_ms": POST_MS, "_auth_is_anonymous": False}, False),
    ({"_auth_created_ms": FOUNDER_MS, "_auth_is_anonymous": True}, False),
    ({"_auth_created_ms": True, "_auth_is_anonymous": False}, False),
    ({"_auth_created_ms": str(FOUNDER_MS), "_auth_is_anonymous": False}, False),
    ({}, False),
    ({"beta_tester": True}, True),
    ({"beta_tester": True, "_auth_created_ms": POST_MS, "_auth_is_anonymous": False}, True),
    ({"founding_beta": True, "creation_timestamp": 0, "is_beta": True}, False),
])
def test_T_EB_1_is_founding_beta_matrix(profile, expected):
    assert is_founding_beta(profile) is expected


def test_T_EB_2_refactor_parity_with_tier_candidates():
    grid = [{}, {"beta_tester": True}, {"stripe_tier": "estate"},
            {"_auth_created_ms": FOUNDER_MS, "_auth_is_anonymous": False},
            {"_auth_created_ms": POST_MS, "_auth_is_anonymous": False, "stripe_tier": "pro"},
            {"_auth_created_ms": FOUNDER_MS, "_auth_is_anonymous": True, "is_lifetime_family_estate": True}]
    for p in grid:
        assert ("founding_beta" in _tier_candidates(p)) is is_founding_beta(p), p
    assert _git_grep_count("def is_founding_beta", "tier_gatekeeper.py") == 1
    assert _git_grep_count("created_ms < BETA_SIGNUP_CUTOFF_MS", "tier_gatekeeper.py") == 1


# ── T-EB-3..9: /subscription-status estate_access ─────────────────────────────

def test_T_EB_3_founding_beta_free_account_gets_estate(fdb, recs):
    recs["uid_F"] = FOUNDER("f@x.com")
    r = _status(fdb, "uid_F", "f@x.com")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["estate_access"] is True
    assert body["stripe_tier"] == "founding_beta" and body["unlimited"] is True
    assert body["lifetime_family_estate"] is False
    recs["_mock"].assert_called_once_with("uid_F")      # server's own outbound Auth lookup, exact uid


def test_T_EB_3b_server_set_beta_tester_flag_gets_estate(fdb, recs):
    recs["uid_B"] = POST("b@x.com")
    fdb.seed("users/b@x.com", {"beta_tester": True})    # server-only key (firestore.rules _serverOnlyKeys)
    r = _status(fdb, "uid_B", "b@x.com")
    assert r.status_code == 200 and r.json()["estate_access"] is True


def test_T_EB_4_post_cutoff_free_denied(fdb, recs):
    recs["uid_N"] = POST("n@x.com")
    r = _status(fdb, "uid_N", "n@x.com")
    assert r.status_code == 200
    assert r.json()["estate_access"] is False and r.json()["stripe_tier"] == "free"


@pytest.mark.parametrize("doc,expected", [
    ({"stripe_tier": "estate"}, False),                                      # Gold, no Lifetime
    ({"stripe_tier": "estate", "is_lifetime_family_estate": True}, True),     # Gold + bought Lifetime
    ({"stripe_tier": "family_estate"}, True),
    ({"stripe_tier": "dealer"}, False),
    ({"is_ai_qc_account": True}, True),                                  # D-2: post-cutoff AI-QC
])
def test_T_EB_5_gold_non_beta_post_cutoff_needs_lifetime(fdb, recs, doc, expected):
    recs["uid_G"] = POST("g@x.com")
    fdb.seed("users/uid_G", doc)
    r = _status(fdb, "uid_G", "g@x.com")
    assert r.status_code == 200
    assert r.json()["estate_access"] is expected


def test_T_EB_6_client_set_beta_fields_rejected(fdb, recs):
    recs["uid_X"] = POST("x@x.com")
    forged = {"founding_beta": True, "is_beta": True, "beta": True, "estate_access": True,
              "creation_timestamp": 1600000000000, "_auth_created_ms": 1, "_auth_is_anonymous": False,
              "power_user": True}
    fdb.seed("users/uid_X", dict(forged))
    fdb.seed("users/x@x.com", dict(forged))
    r = _status(fdb, "uid_X", "x@x.com")
    assert r.status_code == 200
    body = r.json()
    assert body["estate_access"] is False and body["stripe_tier"] == "free"
    profile, _ = load_entitlement_profile(fdb, "uid_X", "x@x.com")
    assert profile["_auth_created_ms"] == POST_MS                     # stored copy discarded
    assert estate_access(profile, "x@x.com") is False


def test_T_EB_7a_auth_down_503_no_estate(fdb, recs):
    recs["uid_F"] = RuntimeError("auth down")
    r = _status(fdb, "uid_F", "f@x.com")
    assert r.status_code == 503 and "estate_access" not in r.text


def test_T_EB_7b_firestore_read_error_500_no_estate(fdb, recs):
    recs["uid_F"] = FOUNDER("f@x.com")
    fdb.fail_on[("get", "users/uid_F")] = RuntimeError("firestore down")
    r = _status(fdb, "uid_F", "f@x.com")
    assert r.status_code == 500 and "estate_access" not in r.text


def test_T_EB_7c_anonymous_pre_cutoff_denied(fdb, recs):
    recs["guest_1"] = GUEST()
    r = _status(fdb, "guest_1", None, provider="anonymous")
    assert r.status_code == 200 and r.json()["estate_access"] is False


@pytest.mark.parametrize("email,expected", [
    ("eric@numista.ai", True), ("grokbot@numista.ai", True), (" Eric@Numista.AI ", True),
    ("someone@numista.ai", False), ("xeric@numista.ai", False), ("eric@numista.ai.evil.com", False),
])
def test_T_EB_8_staff_allowlist_on_token_email(fdb, recs, email, expected):
    recs["uid_S"] = POST(email)
    r = _status(fdb, "uid_S", email, query_uid="uid_S")
    assert r.status_code == 200 and r.json()["estate_access"] is expected
    assert ESTATE_STAFF_EMAILS == frozenset({"eric@numista.ai", "grokbot@numista.ai"})


def test_T_EB_8b_admin_staff_email_not_applied_to_other_user(fdb, recs):
    recs["user_B"] = POST("b@x.com")
    r = _status(fdb, "admin_uid", "eric@numista.ai", query_uid="user_B", admin=True)
    assert r.status_code == 200 and r.json()["estate_access"] is False


@pytest.mark.parametrize("query_uid", ["", "   ", "uid_OTHER"])
def test_T_EB_9_empty_or_foreign_uid_refused(fdb, recs, query_uid):
    recs["uid_F"] = FOUNDER("f@x.com")
    r = _status(fdb, "uid_F", "f@x.com", query_uid=query_uid)
    assert r.status_code == 403
    recs["_mock"].assert_not_called()


def test_T_EB_9b_missing_uid_param_422(fdb, recs):
    app.dependency_overrides[get_current_user] = lambda: {"uid": "uid_F", "email": "f@x.com"}
    r = TestClient(app, raise_server_exceptions=False).get("/api/stripe/subscription-status")
    assert r.status_code == 422
    recs["_mock"].assert_not_called()


# ── T-EB-10..14: cancel / refund never downgrade or lock Founding Beta ────────

@pytest.mark.parametrize("hook_mode", ["core_noop", "p1_contract"])
def test_T_EB_10_founder_cancel_no_downgrade_no_lock(fdb, recs, spies, hook_mode):
    recs["uid_F"] = FOUNDER("f@x.com")
    grant_gold(fdb, recs, uid="uid_F", email="f@x.com", cus="cus_F")
    fdb.seed_coins("f@x.com", 5000)
    results = []
    hook = _p1_contract(results) if hook_mode == "p1_contract" else payment_routes._relock_hook
    with patch("routes.payment_routes._relock_hook", side_effect=hook):
        r, eid = post_event("customer.subscription.deleted", subscription(cus="cus_F"))
    assert ev_doc(fdb, eid)["status"] == "done"
    assert fdb.doc("users/uid_F")["stripe_tier"] is None              # paid field cleared (bookkeeping)
    if results:
        assert results[0]["limit"] is None and results[0]["locked_moved"] == 0
    assert len(fdb.coin_ids("f@x.com")) == 5000 and fdb.coin_ids("f@x.com", folder="locked_coins") == []
    profile, ent = load_entitlement_profile(fdb, "uid_F", "f@x.com")
    assert tier_gatekeeper.get_user_tier(profile) == "founding_beta"
    assert tier_gatekeeper.get_user_allowance(profile) == {"coins": None, "deepdive": 1500, "invoice_scan": 750}
    assert estate_access(profile, "f@x.com") is True


@pytest.mark.parametrize("hook_mode", ["core_noop", "p1_contract"])
def test_T_EB_11_founder_subscription_refund_no_downgrade_no_lock(fdb, recs, spies, hook_mode):
    recs["uid_F"] = FOUNDER("f@x.com")
    fdb.seed("users/uid_F", {"stripe_tier": "estate", "stripe_customer_id": "cus_1"})
    fdb.seed("users/f@x.com", {"stripe_tier": "estate", "stripe_customer_id": "cus_1"})
    fdb.seed("stripe_payments/pi_1", {"uid": "uid_F", "kind": "subscription", "subscription_id": "sub_1", "granted": True})
    fdb.seed_coins("f@x.com", 300)
    results = []
    hook = _p1_contract(results) if hook_mode == "p1_contract" else payment_routes._relock_hook
    with patch("routes.payment_routes._relock_hook", side_effect=hook):
        r, eid = post_event("charge.refunded", charge())
    assert ev_doc(fdb, eid)["status"] == "done"
    if results:
        assert results[0]["limit"] is None and results[0]["locked_moved"] == 0
        assert results[0]["visible"] == 300                                # the email-keyed coins were counted
    assert len(fdb.coin_ids("f@x.com")) == 300
    profile, _ = load_entitlement_profile(fdb, "uid_F", "f@x.com")
    assert tier_gatekeeper.get_user_tier(profile) == "founding_beta"
    assert estate_access(profile, "f@x.com") is True


def test_T_EB_12_founder_lifetime_refund_keeps_estate_no_lock(fdb, recs, spies):
    recs["uid_P"] = FOUNDER("p@x.com")
    grant_lifetime(fdb, recs)
    fdb.seed_coins("p@x.com", 400)
    results = []
    with patch("routes.payment_routes._relock_hook", side_effect=_p1_contract(results)):
        post_event("charge.refunded", charge(pi="pi_L", cus="cus_L"))
    assert fdb.doc("users/uid_P")["is_lifetime_family_estate"] is False   # the purchase is undone
    assert results[0]["limit"] is None and results[0]["locked_moved"] == 0
    profile, _ = load_entitlement_profile(fdb, "uid_P", "p@x.com")
    assert estate_access(profile, "p@x.com") is True                      # Founding Beta still grants it


@pytest.mark.parametrize("event", ["cancel", "refund"])
def test_T_EB_13_post_cutoff_control_unchanged(fdb, recs, spies, event):
    recs["uid_P"] = POST("p@x.com")
    if event == "cancel":
        grant_gold(fdb, recs)
    else:
        fdb.seed("users/uid_P", {"stripe_tier": "estate", "stripe_customer_id": "cus_1"})
        fdb.seed("users/p@x.com", {"stripe_tier": "estate", "stripe_customer_id": "cus_1"})
        fdb.seed("stripe_payments/pi_1", {"uid": "uid_P", "kind": "subscription", "subscription_id": "sub_1", "granted": True})
    fdb.seed_coins("p@x.com", 5000)
    results = []
    with patch("routes.payment_routes._relock_hook", side_effect=_p1_contract(results)):
        if event == "cancel":
            post_event("customer.subscription.deleted", subscription())
        else:
            post_event("charge.refunded", charge())
    assert fdb.doc("users/uid_P")["stripe_tier"] is None
    assert results[0]["limit"] == 10 and results[0]["locked_moved"] == 4990
    profile, _ = load_entitlement_profile(fdb, "uid_P", "p@x.com")
    assert estate_access(profile, "p@x.com") is False


def test_T_EB_14_no_lock_guard_is_independent_of_the_tier_table(fdb, recs):
    """Mutation check: even if founding_beta / family_estate were given a coin number, the guard holds."""
    recs["uid_F"] = FOUNDER("f@x.com")
    recs["uid_L"] = POST("l@x.com")
    recs["uid_P"] = POST("p@x.com")
    fdb.seed("users/uid_L", {"is_lifetime_family_estate": True})
    for owner in ("f@x.com", "l@x.com", "p@x.com"):
        fdb.seed_coins(owner, 30)
    with patch.dict(tier_gatekeeper.TIER_COIN_LIMITS, {"founding_beta": 10, "family_estate": 10}):
        f = enforce_entitlement(fdb, "uid_F", "f@x.com", NOW)
        lf = enforce_entitlement(fdb, "uid_L", "l@x.com", NOW)
        p = enforce_entitlement(fdb, "uid_P", "p@x.com", NOW)
    assert f["limit"] is None and f["locked_moved"] == 0
    assert lf["limit"] is None and lf["locked_moved"] == 0
    assert p["limit"] == 10 and p["locked_moved"] == 20                    # non-beta control unchanged


def test_T_EB_15_grep_gates():
    assert _git_grep_count("def estate_access", "tier_gatekeeper.py") == 1
    assert _git_grep_count("ESTATE_STAFF_EMAILS =", "tier_gatekeeper.py") == 1
    assert _git_grep_count('"estate_access": estate_access(profile', "routes/payment_routes.py") == 2
    assert _git_grep_count("is_lifetime_family_estate", "routes/payment_routes.py") == 0   # T72 still holds
    assert _git_grep_count("lock_overflow_coins(target_id", "routes/payment_routes.py") == 0


# ── T-EB-16..18: NET-827 v2.0.7 exclude_from_founding_beta 1 Dec test path ───

@pytest.mark.parametrize("doc_key", ["users/uid_EXCL", "users/excl@x.com"])
def test_T_EB_16_exclude_from_founding_beta_strips_pre_cutoff_status(fdb, recs, doc_key):
    recs["uid_EXCL"] = FOUNDER("excl@x.com")
    fdb.seed(doc_key, {"exclude_from_founding_beta": True})
    assert is_founding_beta({"_auth_created_ms": FOUNDER_MS, "_auth_is_anonymous": False,
                             "exclude_from_founding_beta": True}) is False
    r = _status(fdb, "uid_EXCL", "excl@x.com")
    assert r.status_code == 200
    body = r.json()
    assert body["stripe_tier"] == "free"
    assert body["coin_limit"] == 10
    assert body["unlimited"] is False
    assert body["estate_access"] is False
    assert body["lifetime_family_estate"] is False


def test_T_EB_17_excluded_pre_cutoff_account_cancels_back_to_free_and_relocks(fdb, recs, spies):
    recs["uid_EXCL2"] = FOUNDER("excl2@x.com")
    fdb.seed("users/uid_EXCL2", {"exclude_from_founding_beta": True})
    grant_gold(fdb, recs, uid="uid_EXCL2", email="excl2@x.com", cus="cus_ex2", sub="sub_ex2")
    fdb.seed_coins("excl2@x.com", 25)
    results = []
    with patch("routes.payment_routes._relock_hook", side_effect=_p1_contract(results)):
        post_event("customer.subscription.deleted", subscription(sid="sub_ex2", cus="cus_ex2"))
    assert fdb.doc("users/uid_EXCL2")["stripe_tier"] is None
    assert results[0]["limit"] == 10 and results[0]["locked_moved"] == 15
    profile, _ = load_entitlement_profile(fdb, "uid_EXCL2", "excl2@x.com")
    assert estate_access(profile, "excl2@x.com") is False


def test_T_EB_18_firestore_rules_sync_blocks_client_write_of_exclude_key():
    import pathlib
    import re
    root = pathlib.Path(__file__).resolve().parents[2]
    mob = (root / "numista_mobile" / "firestore.rules").read_text(encoding="utf-8")
    bak = (root / "numista_backend" / "firestore.rules").read_text(encoding="utf-8")
    m_fn = re.search(r"function _serverOnlyKeys\(\)\s*\{.*?\n\s*\}", mob, re.S)
    b_fn = re.search(r"function _serverOnlyKeys\(\)\s*\{.*?\n\s*\}", bak, re.S)
    assert m_fn and b_fn
    assert "'exclude_from_founding_beta'" in m_fn.group(0)
    assert m_fn.group(0) == b_fn.group(0)
