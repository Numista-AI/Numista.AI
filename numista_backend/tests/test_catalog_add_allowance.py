"""AMEND-A route tests: POST /api/v1/collection/catalog-add uses server allowance."""
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

import routes.catalog_routes as catalog_routes
import tier_gatekeeper
from catalog_service import add_catalog_item_in_txn
from main import app
from routes.deps import get_current_user
from tests.test_catalog_collection_routing import MORGAN, FakeDb, FakeTx, count


@pytest.fixture(autouse=True)
def _isolate():
    tier_gatekeeper._auth_facts_by_uid.cache_clear()
    app.dependency_overrides.clear()
    yield
    tier_gatekeeper._auth_facts_by_uid.cache_clear()
    app.dependency_overrides.clear()


def _rec(created_ms, providers=1):
    rec = MagicMock(name="UserRecord")
    rec.user_metadata.creation_timestamp = created_ms
    rec.provider_data = [MagicMock() for _ in range(providers)]
    return rec


def _tok(uid, email, admin=False, provider="password"):
    return {"uid": uid, "email": email, "admin": admin, "firebase": {"sign_in_provider": provider}}


def _seed_profile_and_coins(profile_doc, num_coins):
    tg_db = MagicMock(name="tg_fake_db")
    snap = MagicMock(name="snap")
    snap.exists = True
    snap.to_dict.return_value = dict(profile_doc)
    tg_db.collection.return_value.document.return_value.get.return_value = snap

    fdb = FakeDb()
    for i in range(num_coins):
        fdb.store[f"users/u1/coins/seed{i}"] = {}

    route_db = MagicMock(name="route_fake_db")
    route_db.transaction.return_value = FakeTx(fdb)

    def _run_add_stub(tx, uid, nac, lim, spec, idem=None):
        return add_catalog_item_in_txn(
            FakeTx(fdb), fdb, uid, nac, lim, count(fdb), spec, idempotency_key=idem
        )

    return tg_db, fdb, route_db, _run_add_stub


def _post_catalog_add(profile_doc, num_coins, auth_return=None, auth_side_effect=None, provider="password"):
    tg_db, fdb, route_db, _run_add_stub = _seed_profile_and_coins(profile_doc, num_coins)
    app.dependency_overrides[get_current_user] = lambda: _tok("u1", "u1@example.com", provider=provider)
    client = TestClient(app, raise_server_exceptions=False)

    get_user_kwargs = {"side_effect": auth_side_effect} if auth_side_effect else {"return_value": auth_return}
    with patch.object(tier_gatekeeper, "db", tg_db), \
         patch.object(catalog_routes, "db", route_db), \
         patch.object(catalog_routes, "_run_add", side_effect=_run_add_stub) as run_add_mock, \
         patch("tier_gatekeeper.firebase_auth.get_user", **get_user_kwargs) as get_user_mock:
        resp = client.post("/api/v1/collection/catalog-add", json={"nac_code": MORGAN})
    return resp, get_user_mock, run_add_mock


def test_ca1_founding_beta_by_auth_date_unlimited():
    resp, get_user_mock, _ = _post_catalog_add({}, 50, auth_return=_rec(1797310799999))
    assert resp.status_code == 201
    get_user_mock.assert_called_once_with("u1")


def test_ca2_sovereign_unlimited():
    resp, _, _ = _post_catalog_add({"stripe_tier": "sovereign"}, 50, auth_return=_rec(1797310800000))
    assert resp.status_code == 201


def test_ca3_legacy_beta_tester_unlimited():
    resp, _, _ = _post_catalog_add({"beta_tester": True}, 50, auth_return=_rec(1797310800000))
    assert resp.status_code == 201


def test_ca4_free_at_10_returns_403_quota_exceeded():
    resp, _, _ = _post_catalog_add({}, 10, auth_return=_rec(1797310800000))
    assert resp.status_code == 403
    assert resp.json()["detail"] == {"error": "QUOTA_EXCEEDED", "count": 10, "limit": 10}


def test_ca5_free_at_9_returns_201():
    resp, _, _ = _post_catalog_add({}, 9, auth_return=_rec(1797310800000))
    assert resp.status_code == 201


def test_ca6_auth_outage_returns_503_and_skips_add():
    resp, _, run_add_mock = _post_catalog_add({}, 0, auth_side_effect=Exception("down"))
    assert resp.status_code == 503
    run_add_mock.assert_not_called()


def test_ca7_power_user_flag_only_is_not_trusted():
    resp, _, _ = _post_catalog_add({"power_user": True}, 10, auth_return=_rec(1797310800000))
    assert resp.status_code == 403
    assert resp.json()["detail"]["error"] == "QUOTA_EXCEEDED"


def test_ca8_power_user_server_tier_still_honoured():
    resp, _, _ = _post_catalog_add({"stripe_tier": "power_user"}, 50, auth_return=_rec(1797310800000))
    assert resp.status_code == 201


def test_ca9_forged_creation_timestamp_ignored():
    resp, _, _ = _post_catalog_add({"creation_timestamp": 0}, 10, auth_return=_rec(1797310800000))
    assert resp.status_code == 403


def test_ca10_guest_anonymous_provider_never_beta():
    resp, _, _ = _post_catalog_add(
        {}, 10, auth_return=_rec(1700000000000, providers=1), provider="anonymous"
    )
    assert resp.status_code == 403


def test_ca11_stored_auth_fields_popped_and_ignored():
    resp, _, _ = _post_catalog_add(
        {"_auth_created_ms": 1, "_auth_is_anonymous": False},
        10,
        auth_return=_rec(1797310800000),
    )
    assert resp.status_code == 403


def test_ca12_eric_power_user_flag_pre_cutoff_founding_beta_unlimited():
    """
    Order Step 4: Eric's account has power_user==True in Firestore and a pre-cutoff
    Firebase Auth creation time. After dropping trust in power_user, Eric still
    resolves to unlimited via Founding Beta (Firebase Auth creation time).
    """
    resp, _, _ = _post_catalog_add({"power_user": True}, 50, auth_return=_rec(1797310799999))
    assert resp.status_code == 201

    tg_db, _, _, _ = _seed_profile_and_coins({"power_user": True}, 0)
    with patch.object(tier_gatekeeper, "db", tg_db), \
         patch("tier_gatekeeper.firebase_auth.get_user", return_value=_rec(1797310799999)):
        profile = tier_gatekeeper.get_user_profile("u1", uid_for_auth="u1", sign_in_provider="password")
        assert tier_gatekeeper.get_user_tier(profile) == "founding_beta"
        assert tier_gatekeeper.get_user_allowance(profile)["coins"] is None
