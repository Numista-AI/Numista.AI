import math
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

import tier_gatekeeper
from main import app  # as tests/test_idor_fixes.py:18
from routes.deps import get_current_user  # as tests/test_idor_fixes.py:19
from tier_gatekeeper import (
    BETA_SIGNUP_CUTOFF_MS,
    TIER_COIN_LIMITS,
    TIER_DAILY_ALLOWANCES,
    AuthFactsUnavailable,
    _bigger,
    auth_beta_facts,
    check_and_enforce_coin_limit,
    check_and_increment_daily_usage,
    get_user_allowance,
    get_user_profile,
    get_user_tier,
    within_limit,
)


@pytest.fixture(autouse=True)
def _isolate():
    tier_gatekeeper._auth_facts_by_uid.cache_clear()
    app.dependency_overrides.clear()
    yield
    tier_gatekeeper._auth_facts_by_uid.cache_clear()
    app.dependency_overrides.clear()


@pytest.fixture
def fake_db():
    """Replaces tier_gatekeeper.db with an explicit fake: users/{id} does NOT exist
    unless a test sets snap.exists = True and snap.to_dict.return_value = <a real dict>."""
    db = MagicMock(name="fake_db")
    snap = MagicMock(name="snap")
    snap.exists = False
    snap.to_dict.return_value = None
    db.collection.return_value.document.return_value.get.return_value = snap
    with patch.object(tier_gatekeeper, "db", db):
        yield db, snap


@pytest.fixture
def no_count():
    # payment_routes.py:147 get_coin_count reads count().get()[0][0].value, which a MagicMock can't supply.
    with patch("routes.payment_routes.get_coin_count", return_value=0) as m:
        yield m


def _rec(created_ms, providers=1):
    rec = MagicMock(name="UserRecord")
    rec.user_metadata.creation_timestamp = created_ms
    rec.provider_data = [MagicMock() for _ in range(providers)]
    return rec


def _tok(uid, email, admin=False, provider="password"):
    return {"uid": uid, "email": email, "admin": admin, "firebase": {"sign_in_provider": provider}}


# ==============================================================================
# U: Tier rule (pure dict profile)
# ==============================================================================

def test_u1_before_cutoff_last_ms():
    assert get_user_tier({"_auth_created_ms": 1797310799999, "_auth_is_anonymous": False}) == "founding_beta"


def test_u2_before_cutoff_last_whole_second():
    assert get_user_tier({"_auth_created_ms": 1797310799000, "_auth_is_anonymous": False}) == "founding_beta"


def test_u3_at_cutoff():
    assert get_user_tier({"_auth_created_ms": 1797310800000, "_auth_is_anonymous": False}) == "free"


def test_u4_after_cutoff():
    assert get_user_tier({"_auth_created_ms": 1797310800001, "_auth_is_anonymous": False}) == "free"


def test_u5_anonymous_excluded():
    assert get_user_tier({"_auth_created_ms": 1700000000000, "_auth_is_anonymous": True}) == "free"


def test_u6_missing_anonymous_flag_fails_closed():
    assert get_user_tier({"_auth_created_ms": 1700000000000}) == "free"


def test_u7_non_int_created_ms_fails_closed():
    assert get_user_tier({"_auth_created_ms": True, "_auth_is_anonymous": False}) == "free"
    assert get_user_tier({"_auth_created_ms": "1", "_auth_is_anonymous": False}) == "free"


def test_u8_firestore_creation_timestamp_ignored():
    assert get_user_tier({"creation_timestamp": 0}) == "free"


def test_u9_beta_tester_flag():
    assert get_user_tier({"beta_tester": True}) == "founding_beta"


def test_u10_lifetime_family_estate():
    assert get_user_tier({"is_lifetime_family_estate": True}) == "family_estate"


# ==============================================================================
# P: Precedence, item by item
# ==============================================================================

_B = {"_auth_created_ms": 1700000000000, "_auth_is_anonymous": False}
_NET827_PATCH = {
    "estate": None,
    "sovereign": None,
    "power_user": None,
    "numismatist": 249,
}


def test_p1_founding_plus_estate_plain():
    p = {**_B, "stripe_tier": "estate"}
    assert get_user_tier(p) == "founding_beta"
    assert get_user_allowance(p) == {"coins": None, "deepdive": 1500, "invoice_scan": 750}


def test_p2_founding_plus_estate_net827():
    p = {**_B, "stripe_tier": "estate"}
    with patch.dict(tier_gatekeeper.TIER_COIN_LIMITS, _NET827_PATCH):
        assert get_user_tier(p) == "estate"
        assert get_user_allowance(p) == {"coins": None, "deepdive": 1500, "invoice_scan": 750}


def test_p3_founding_plus_numismatist():
    p = {**_B, "stripe_tier": "numismatist"}
    assert get_user_tier(p) == "founding_beta"
    a = get_user_allowance(p)
    assert a["coins"] is None
    assert a["deepdive"] == 1500
    assert a["invoice_scan"] == 750
    with patch.dict(tier_gatekeeper.TIER_COIN_LIMITS, _NET827_PATCH):
        assert get_user_tier(p) == "founding_beta"
        a2 = get_user_allowance(p)
        assert a2["coins"] is None
        assert a2["deepdive"] == 1500
        assert a2["invoice_scan"] == 750


def test_p4_founding_plus_sovereign():
    p = {**_B, "stripe_tier": "sovereign"}
    assert get_user_tier(p) == "sovereign"
    assert get_user_allowance(p) == {"coins": None, "deepdive": 5000, "invoice_scan": 2500}


def test_p5_founding_plus_power_user():
    p = {**_B, "stripe_tier": "power_user"}
    assert get_user_tier(p) == "power_user"
    assert get_user_allowance(p) == {"coins": None, "deepdive": None, "invoice_scan": None}


def test_p6_beta_tester_plus_estate_net827():
    p = {"beta_tester": True, "stripe_tier": "estate"}
    with patch.dict(tier_gatekeeper.TIER_COIN_LIMITS, _NET827_PATCH):
        assert get_user_tier(p) == "estate"
        assert get_user_allowance(p) == {"coins": None, "deepdive": 1500, "invoice_scan": 750}


def test_p7_founding_plus_free_pro_dealer():
    for t in ("free", "pro", "dealer"):
        p = {**_B, "stripe_tier": t}
        assert get_user_tier(p) == "founding_beta"
        assert get_user_allowance(p) == {"coins": None, "deepdive": 1500, "invoice_scan": 750}


def test_p8_lifetime_combinations():
    p1 = {"is_lifetime_family_estate": True, "stripe_tier": "sovereign"}
    assert get_user_tier(p1) == "sovereign"
    assert get_user_allowance(p1) == {"coins": None, "deepdive": 5000, "invoice_scan": 2500}

    p2 = {"is_lifetime_family_estate": True, **_B}
    assert get_user_tier(p2) == "founding_beta"
    assert get_user_allowance(p2) == {"coins": None, "deepdive": 1500, "invoice_scan": 750}

    p3 = {"is_lifetime_family_estate": True}
    assert get_user_tier(p3) == "family_estate"
    assert get_user_allowance(p3) == {"coins": 2500, "deepdive": 1500, "invoice_scan": 750}


def test_p9_post_cutoff_plus_estate():
    p = {"_auth_created_ms": 1797310800000, "_auth_is_anonymous": False, "stripe_tier": "estate"}
    assert get_user_tier(p) == "estate"
    assert get_user_allowance(p) == {"coins": 1000, "deepdive": 500, "invoice_scan": 250}
    with patch.dict(tier_gatekeeper.TIER_COIN_LIMITS, _NET827_PATCH):
        assert get_user_tier(p) == "estate"
        assert get_user_allowance(p) == {"coins": None, "deepdive": 500, "invoice_scan": 250}


def test_p10_unknown_paid_string():
    p1 = {**_B, "stripe_tier": "hobbyist"}
    assert get_user_tier(p1) == "founding_beta"
    assert get_user_allowance(p1) == {"coins": None, "deepdive": 1500, "invoice_scan": 750}

    p2 = {"stripe_tier": "hobbyist"}
    assert get_user_tier(p2) == "hobbyist"
    assert get_user_allowance(p2) == {"coins": TIER_COIN_LIMITS["free"], "deepdive": 3, "invoice_scan": 1}


def test_p11_items_compared_separately():
    with patch.dict(tier_gatekeeper.TIER_DAILY_ALLOWANCES, {"dealer": {"deepdive": 2000, "invoice_scan": 10}}):
        p = {**_B, "stripe_tier": "dealer"}
        assert get_user_allowance(p) == {"coins": None, "deepdive": 2000, "invoice_scan": 750}


def test_p12_bigger_helper():
    assert _bigger(None, 5) is None
    assert _bigger(5, None) is None
    assert _bigger(3, 7) == 7
    assert _bigger(None, None) is None


def test_p13_empty_profile():
    assert get_user_tier({}) == "free"
    assert get_user_allowance({}) == {"coins": TIER_COIN_LIMITS["free"], "deepdive": 3, "invoice_scan": 1}


# ==============================================================================
# L: Limits (L1-L7)
# ==============================================================================

def test_l1_free_limit_is_10():
    assert TIER_COIN_LIMITS["free"] == 10


def test_l2_unlimited_coin_limits_are_none():
    assert TIER_COIN_LIMITS["founding_beta"] is None
    assert TIER_COIN_LIMITS["sovereign"] is None
    assert TIER_COIN_LIMITS["power_user"] is None


def test_l3_daily_allowances_and_no_float_inf():
    assert TIER_DAILY_ALLOWANCES["founding_beta"] == {"deepdive": 1500, "invoice_scan": 750}
    assert TIER_DAILY_ALLOWANCES["power_user"] == {"deepdive": None, "invoice_scan": None}
    for v in TIER_COIN_LIMITS.values():
        if isinstance(v, (int, float)):
            assert not math.isinf(v)
    for row in TIER_DAILY_ALLOWANCES.values():
        for v in row.values():
            if isinstance(v, (int, float)):
                assert not math.isinf(v)


def test_l4_within_limit():
    assert within_limit("free", 10) is True
    assert within_limit("free", 11) is False
    assert within_limit("founding_beta", 10**6) is True


def test_l5_check_and_enforce_coin_limit():
    with (
        patch("tier_gatekeeper.get_user_profile", return_value={"beta_tester": True}),
        patch("tier_gatekeeper.get_coin_count", return_value=5000),
    ):
        assert check_and_enforce_coin_limit("u1") is True

    with (
        patch("tier_gatekeeper.get_user_profile", return_value={}),
        patch("tier_gatekeeper.get_coin_count", return_value=11),
        patch("tier_gatekeeper.create_upgrade_checkout_session", return_value=None),
    ):
        with pytest.raises(HTTPException) as exc:
            check_and_enforce_coin_limit("u1")
        assert exc.value.status_code == 403
        assert exc.value.detail["stats"]["limit"] == 10


def test_l6_cutoff_constant_est():
    est = timezone(timedelta(hours=-5))
    assert int(datetime(2026, 12, 15, tzinfo=est).timestamp() * 1000) == BETA_SIGNUP_CUTOFF_MS


def test_l7_daily_usage_none_limit_guard(fake_db):
    with (
        patch.dict(tier_gatekeeper.TIER_DAILY_ALLOWANCES, {"pro": {"deepdive": None, "invoice_scan": None}}),
        patch("tier_gatekeeper.get_user_profile", return_value={"stripe_tier": "pro"}),
    ):
        assert check_and_increment_daily_usage("u1", "deepdive") is True


# ==============================================================================
# F: Auth facts
# ==============================================================================

def test_f1_auth_beta_facts_signed_in():
    with patch("tier_gatekeeper.firebase_auth.get_user", return_value=_rec(1797310799999)):
        assert auth_beta_facts("u1") == {"_auth_created_ms": 1797310799999, "_auth_is_anonymous": False}


def test_f2_auth_beta_facts_no_providers_anonymous():
    with patch("tier_gatekeeper.firebase_auth.get_user", return_value=_rec(1797310799999, providers=0)):
        assert auth_beta_facts("u1")["_auth_is_anonymous"] is True


def test_f3_auth_beta_facts_token_anonymous_override():
    with patch("tier_gatekeeper.firebase_auth.get_user", return_value=_rec(1797310799999, providers=1)):
        assert auth_beta_facts("u1", sign_in_provider="anonymous")["_auth_is_anonymous"] is True


def test_f4_auth_beta_facts_cached():
    with patch("tier_gatekeeper.firebase_auth.get_user", return_value=_rec(1797310799999)) as m:
        auth_beta_facts("u1")
        auth_beta_facts("u1")
        assert m.call_count == 1


def test_f5_auth_beta_facts_failures_not_cached():
    with patch(
        "tier_gatekeeper.firebase_auth.get_user",
        side_effect=[Exception("down"), _rec(1797310799999)],
    ) as m:
        with pytest.raises(AuthFactsUnavailable):
            auth_beta_facts("u1")
        facts = auth_beta_facts("u1")
        assert facts == {"_auth_created_ms": 1797310799999, "_auth_is_anonymous": False}
        assert m.call_count == 2


def test_f6_auth_beta_facts_none_creation_timestamp():
    with patch("tier_gatekeeper.firebase_auth.get_user", return_value=_rec(None)):
        with pytest.raises(AuthFactsUnavailable):
            auth_beta_facts("u1")


def test_f7_auth_beta_facts_email_rejected():
    with patch("tier_gatekeeper.firebase_auth.get_user") as m:
        with pytest.raises(AuthFactsUnavailable):
            auth_beta_facts("a@b.c")
        m.assert_not_called()


# ==============================================================================
# G: Profile loader
# ==============================================================================

def test_g1_forged_auth_keys_stripped(fake_db):
    _, snap = fake_db
    snap.exists = True
    snap.to_dict.return_value = {"_auth_created_ms": 1, "_auth_is_anonymous": False}
    prof = get_user_profile("u1")
    assert "_auth_created_ms" not in prof
    assert "_auth_is_anonymous" not in prof
    assert get_user_tier(prof) == "free"


def test_g2_auth_failure_propagates(fake_db):
    with patch("tier_gatekeeper.firebase_auth.get_user", side_effect=Exception("boom")):
        with pytest.raises(AuthFactsUnavailable):
            get_user_profile("u1", uid_for_auth="u1")


def test_g3_profile_merges_firestore_and_auth_facts(fake_db):
    _, snap = fake_db
    snap.exists = True
    snap.to_dict.return_value = {"stripe_tier": "pro"}
    with patch("tier_gatekeeper.firebase_auth.get_user", return_value=_rec(1700000000000)):
        prof = get_user_profile("u1", uid_for_auth="u1")
    assert type(prof) is dict
    assert prof["stripe_tier"] == "pro"
    assert prof["_auth_created_ms"] == 1700000000000
    assert prof["_auth_is_anonymous"] is False
    assert get_user_tier(prof) == "founding_beta"


# ==============================================================================
# R: Route GET /api/stripe/subscription-status
# ==============================================================================

def test_r1_own_uid(fake_db, no_count):
    app.dependency_overrides[get_current_user] = lambda: _tok("user_A", "user_a@example.com")
    client = TestClient(app, raise_server_exceptions=False)
    with patch("tier_gatekeeper.firebase_auth.get_user", return_value=_rec(1797310799999)) as m:
        resp = client.get("/api/stripe/subscription-status?uid=user_A")
    assert resp.status_code == 200
    body = resp.json()
    assert body["stripe_tier"] == "founding_beta"
    assert body["coin_limit"] is None
    assert body["unlimited"] is True
    assert body["daily_ai_allowance"] == {"deepdive": 1500, "invoice_scan": 750}
    m.assert_called_once_with("user_A")


def test_r2_own_email_uses_token_uid(fake_db, no_count):
    app.dependency_overrides[get_current_user] = lambda: _tok("user_A", "user_a@example.com")
    client = TestClient(app, raise_server_exceptions=False)
    with patch("tier_gatekeeper.firebase_auth.get_user", return_value=_rec(1797310799999)) as m:
        resp = client.get("/api/stripe/subscription-status?uid=USER_A@example.com")
    assert resp.status_code == 200
    assert resp.json()["stripe_tier"] == "founding_beta"
    m.assert_called_once_with("user_A")


def test_r3_admin_email_key_skips_auth(fake_db, no_count):
    app.dependency_overrides[get_current_user] = lambda: _tok("admin_uid", "admin@numista.ai", admin=True)
    client = TestClient(app, raise_server_exceptions=False)
    with patch("tier_gatekeeper.firebase_auth.get_user") as m:
        resp = client.get("/api/stripe/subscription-status?uid=someone@example.com")
    assert resp.status_code == 200
    body = resp.json()
    assert body["stripe_tier"] == "free"
    assert body["coin_limit"] == TIER_COIN_LIMITS["free"]
    assert body["unlimited"] is False
    m.assert_not_called()


def test_r4_guest_token_overrides_provider_data(fake_db, no_count):
    app.dependency_overrides[get_current_user] = lambda: _tok("guest_1", None, provider="anonymous")
    client = TestClient(app, raise_server_exceptions=False)
    with patch("tier_gatekeeper.firebase_auth.get_user", return_value=_rec(1700000000000, providers=1)) as m:
        resp = client.get("/api/stripe/subscription-status?uid=guest_1")
    assert resp.status_code == 200
    body = resp.json()
    assert body["stripe_tier"] == "free"
    assert body["coin_limit"] == TIER_COIN_LIMITS["free"]
    m.assert_called_once_with("guest_1")


def test_r5_negative_control_at_cutoff(fake_db, no_count):
    app.dependency_overrides[get_current_user] = lambda: _tok("user_A", "user_a@example.com")
    client = TestClient(app, raise_server_exceptions=False)
    with patch("tier_gatekeeper.firebase_auth.get_user", return_value=_rec(1797310800000)):
        resp = client.get("/api/stripe/subscription-status?uid=user_A")
    assert resp.status_code == 200
    body = resp.json()
    assert body["stripe_tier"] == "free"
    assert body["coin_limit"] == TIER_COIN_LIMITS["free"]


def test_r6_auth_down_returns_503(fake_db, no_count):
    app.dependency_overrides[get_current_user] = lambda: _tok("user_A", "user_a@example.com")
    client = TestClient(app, raise_server_exceptions=False)
    with patch("tier_gatekeeper.firebase_auth.get_user", side_effect=Exception("down")):
        resp = client.get("/api/stripe/subscription-status?uid=user_A")
    assert resp.status_code == 503
    no_count.assert_not_called()


def test_r7_loader_raises_returns_503(fake_db, no_count):
    app.dependency_overrides[get_current_user] = lambda: _tok("user_A", "user_a@example.com")
    client = TestClient(app, raise_server_exceptions=False)
    with patch("routes.payment_routes.get_user_profile", side_effect=AuthFactsUnavailable("x")):
        resp = client.get("/api/stripe/subscription-status?uid=user_A")
    assert resp.status_code == 503


def test_r8_admin_uid_key(fake_db, no_count):
    app.dependency_overrides[get_current_user] = lambda: _tok("admin_uid", "admin@numista.ai", admin=True)
    client = TestClient(app, raise_server_exceptions=False)
    with patch("tier_gatekeeper.firebase_auth.get_user", return_value=_rec(1797310800001)) as m:
        resp = client.get("/api/stripe/subscription-status?uid=user_B")
    assert resp.status_code == 200
    assert resp.json()["stripe_tier"] == "free"
    m.assert_called_once_with("user_B")


def test_r9_non_admin_other_forbidden(fake_db, no_count):
    app.dependency_overrides[get_current_user] = lambda: _tok("user_A", "user_a@example.com")
    client = TestClient(app, raise_server_exceptions=False)
    with patch("tier_gatekeeper.firebase_auth.get_user") as m:
        resp = client.get("/api/stripe/subscription-status?uid=user_B")
    assert resp.status_code == 403
    m.assert_not_called()


def test_r10_sovereign_json_safe(fake_db, no_count):
    _, snap = fake_db
    snap.exists = True
    snap.to_dict.return_value = {"beta_tester": True, "stripe_tier": "sovereign"}
    app.dependency_overrides[get_current_user] = lambda: _tok("user_A", "user_a@example.com")
    client = TestClient(app, raise_server_exceptions=False)
    with patch("tier_gatekeeper.firebase_auth.get_user", return_value=_rec(1797310800001)):
        resp = client.get("/api/stripe/subscription-status?uid=user_A")
    assert resp.status_code == 200
    body = resp.json()
    assert body["stripe_tier"] == "sovereign"
    assert body["coin_limit"] is None
    assert body["unlimited"] is True
    assert body["daily_ai_allowance"] == {"deepdive": 5000, "invoice_scan": 2500}


def test_r11_power_user_json_safe(fake_db, no_count):
    _, snap = fake_db
    snap.exists = True
    snap.to_dict.return_value = {"stripe_tier": "power_user"}
    app.dependency_overrides[get_current_user] = lambda: _tok("user_A", "user_a@example.com")
    client = TestClient(app, raise_server_exceptions=False)
    with patch("tier_gatekeeper.firebase_auth.get_user", return_value=_rec(1797310800001)):
        resp = client.get("/api/stripe/subscription-status?uid=user_A")
    assert resp.status_code == 200
    body = resp.json()
    assert body["coin_limit"] is None
    assert body["unlimited"] is True
    assert body["daily_ai_allowance"] == {"deepdive": None, "invoice_scan": None}


def test_r12_eric_gold_example(fake_db, no_count):
    _, snap = fake_db
    snap.exists = True
    snap.to_dict.return_value = {"stripe_tier": "estate"}
    app.dependency_overrides[get_current_user] = lambda: _tok("user_A", "user_a@example.com")
    client = TestClient(app, raise_server_exceptions=False)
    with patch("tier_gatekeeper.firebase_auth.get_user", return_value=_rec(1797310799999)):
        resp = client.get("/api/stripe/subscription-status?uid=user_A")
        assert resp.status_code == 200
        body = resp.json()
        assert body["coin_limit"] is None
        assert body["daily_ai_allowance"] == {"deepdive": 1500, "invoice_scan": 750}
        assert body["stripe_tier"] == "founding_beta"

        with patch.dict(tier_gatekeeper.TIER_COIN_LIMITS, _NET827_PATCH):
            resp2 = client.get("/api/stripe/subscription-status?uid=user_A")
        assert resp2.status_code == 200
        body2 = resp2.json()
        assert body2["coin_limit"] is None
        assert body2["daily_ai_allowance"] == {"deepdive": 1500, "invoice_scan": 750}
        assert body2["stripe_tier"] == "estate"


def test_r13_eric_silver_example(fake_db, no_count):
    _, snap = fake_db
    snap.exists = True
    snap.to_dict.return_value = {"stripe_tier": "numismatist"}
    app.dependency_overrides[get_current_user] = lambda: _tok("user_A", "user_a@example.com")
    client = TestClient(app, raise_server_exceptions=False)
    with patch("tier_gatekeeper.firebase_auth.get_user", return_value=_rec(1797310799999)):
        resp = client.get("/api/stripe/subscription-status?uid=user_A")
    assert resp.status_code == 200
    body = resp.json()
    assert body["coin_limit"] is None
    assert body["unlimited"] is True
    assert body["daily_ai_allowance"] == {"deepdive": 1500, "invoice_scan": 750}


def test_l8_power_user_flag_ignored_by_check_and_enforce_coin_limit():
    with patch("tier_gatekeeper.get_user_profile", return_value={"power_user": True}), \
         patch("tier_gatekeeper.get_coin_count", return_value=11):
        with pytest.raises(HTTPException) as exc:
            check_and_enforce_coin_limit("u1")
        assert exc.value.status_code == 403


def test_l9_power_user_flag_ignored_by_check_and_increment_daily_usage():
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    profile = {"power_user": True, "deepdive_count": 3, "last_usage_date": today_str}
    with patch("tier_gatekeeper.get_user_profile", return_value=profile):
        assert check_and_increment_daily_usage("u1", "deepdive") is False
