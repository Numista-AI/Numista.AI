"""HTTP-level tests for the extended /api/transfer/* routes (PLAN v1.2 sections 6.2, 7.2, 4.6)."""
import os
import sys

import pytest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient  # noqa: E402

from tests.fakes_firestore import FakeDB, item, seed_item  # noqa: E402

SELLER = "seller@example.com"
BUYER = "buyer@example.org"


@pytest.fixture
def env(monkeypatch):
    import main
    from services import allowance_service

    monkeypatch.setenv("K_SERVICE", "numista-backend-test")
    monkeypatch.delenv("ALLOW_UNAUTHENTICATED", raising=False)
    db = FakeDB()
    monkeypatch.setattr(main, "db", db)
    monkeypatch.setattr(allowance_service, "resolve_coin_limit", lambda **k: 10)
    claims = {}

    def fake_verify(token):
        return claims[token]

    monkeypatch.setattr("routes.deps.firebase_auth.verify_id_token", fake_verify)

    def login(token, email, provider="password"):
        claims[token] = {"email": email, "uid": f"uid-{token}", "firebase": {"sign_in_provider": provider}}
        return {"Authorization": f"Bearer {token}"}

    return TestClient(main.app), db, login


def _init(client, h, **body):
    payload = {"user_id": "ignored@x.com", "item_ids": ["c1"], "transfer_type": "sale_private"}
    payload.update(body)
    return client.post("/api/transfer/initiate", json=payload, headers=h)


def test_initiate_returns_secrets_once_and_no_hashes_or_private_fields(env):
    client, db, login = env
    seed_item(db, SELLER, "c1", Cost="$45.00")
    h = login("s", SELLER)
    r = _init(client, h, sender_address="1 Main St", sender_display="A. Seller")
    assert r.status_code == 200, r.text
    t = r.json()["transfer"]
    assert t["claim_token"] and t["claim_code"] and t["document_pdf_b64"]
    for hidden in ("claim_token_hash", "claim_code_hash", "claim_lookup_ids", "sender_address", "sender_id", "claim_pin"):
        assert hidden not in t, f"{hidden} must not be in the API response"
    assert "seller@example.com" not in r.text


def test_claim_route_by_code_uses_token_identity_and_forwards_ip_and_uid(env, monkeypatch):
    client, db, login = env
    seed_item(db, SELLER, "c1")
    t = _init(client, login("s", SELLER)).json()["transfer"]
    seen = {}
    import services.transfer_service as ts
    real = ts.claim_transfer

    def spy(**kw):
        seen.update(kw)
        return real(**kw)

    monkeypatch.setattr(ts, "claim_transfer", spy)
    r = client.post("/api/transfer/claim", json={"user_id": "attacker@x.com", "claim_code": t["claim_code"]},
                    headers={**login("b", BUYER), "X-Forwarded-For": "6.6.6.6, 7.7.7.7"})
    assert r.status_code == 200, r.text
    assert seen["user_b_id"] == BUYER, "identity comes from the verified token, never the body"
    assert seen["uid"] == "uid-b" and seen["client_ip"] == "7.7.7.7" and seen["sign_in_provider"] == "password"
    assert r.json()["result"]["items_claimed_count"] == 1


def test_claim_route_returns_429_when_limited_and_400_for_a_wrong_code(env):
    client, db, login = env
    h = login("b", BUYER)
    for i in range(10):
        r = client.post("/api/transfer/claim", json={"user_id": "x", "claim_code": f"ABCDE-FGH{i:02d}"}, headers=h)
        assert r.status_code == 400 and "Code not found or expired" in r.text
    r = client.post("/api/transfer/claim", json={"user_id": "x", "claim_code": "ABCDE-FGH99"}, headers=h)
    assert r.status_code == 429


def test_free_recipient_claim_response_reports_the_locked_item(env):
    client, db, login = env
    for i in range(10):
        seed_item(db, BUYER, f"own{i:02d}", created_at=f"2026-02-{i + 1:02d}T00:00:00+00:00")
    seed_item(db, SELLER, "c1")
    t = _init(client, login("s", SELLER)).json()["transfer"]
    r = client.post("/api/transfer/claim", json={"user_id": "x", "claim_token": t["claim_token"]}, headers=login("b", BUYER))
    body = r.json()["result"]
    assert r.status_code == 200 and body["locked"] is True and "nothing is lost" in body["message"].lower()


def test_preview_route_titles_only_and_requires_a_secret(env):
    client, db, login = env
    seed_item(db, SELLER, "c1", Cost="$45.00")
    t = _init(client, login("s", SELLER), sender_display="A. Seller").json()["transfer"]
    h = login("b", BUYER)
    assert client.get("/api/transfer/preview", headers=h).status_code == 400
    r = client.get("/api/transfer/preview", params={"claim_token": t["claim_token"]}, headers=h)
    assert r.status_code == 200
    assert "A. Seller" not in r.text and "45.00" not in r.text and "NUM-" not in r.text
    assert r.json()["preview"]["items"][0]["title"].startswith("1921")


def test_rotate_code_route_is_sender_only(env):
    client, db, login = env
    seed_item(db, SELLER, "c1")
    t = _init(client, login("s", SELLER)).json()["transfer"]
    bad = client.post("/api/transfer/rotate-code", json={"transfer_id": t["transfer_id"]}, headers=login("b", BUYER))
    assert bad.status_code == 400 and "sender" in bad.text.lower()
    ok = client.post("/api/transfer/rotate-code", json={"transfer_id": t["transfer_id"]}, headers=login("s", SELLER))
    assert ok.status_code == 200 and ok.json()["result"]["claim_code"] != t["claim_code"]


def test_anonymous_tokens_are_refused_on_every_new_or_changed_route(env):
    client, db, login = env
    h = login("anon", "anon@x.com", provider="anonymous")
    assert _init(client, h).status_code == 403
    assert client.post("/api/transfer/claim", json={"user_id": "x", "claim_code": "ABCDE-FGH12"}, headers=h).status_code == 403
    assert client.get("/api/transfer/preview", params={"claim_code": "ABCDE-FGH12"}, headers=h).status_code == 403
    assert client.post("/api/transfer/rotate-code", json={"transfer_id": "t"}, headers=h).status_code == 403


def test_no_token_gets_401_on_new_routes(env):
    client, db, login = env
    assert client.get("/api/transfer/preview", params={"claim_code": "ABCDE-FGH12"}).status_code == 401
    assert client.post("/api/transfer/rotate-code", json={"transfer_id": "t"}).status_code == 401
    assert client.post("/api/transfer/claim", json={"user_id": "x", "claim_code": "ABCDE-FGH12"}).status_code == 401


def test_verify_route_is_public_minimal_and_rate_limited(env):
    client, db, login = env
    seed_item(db, SELLER, "c1")
    t = _init(client, login("s", SELLER)).json()["transfer"]
    r = client.get(f"/api/provenance/verify/{t['transfer_id']}", headers={"X-Forwarded-For": "4.4.4.4"})
    assert r.status_code == 200 and set(r.json().keys()) == {"verified", "passport_id", "status"}
    for i in range(30):
        assert client.get(f"/api/provenance/verify/nope{i}", headers={"X-Forwarded-For": "5.5.5.5"}).status_code == 404
    assert client.get("/api/provenance/verify/nope31", headers={"X-Forwarded-For": "5.5.5.5"}).status_code == 429


def test_passport_pdf_v2_is_sender_only(env):
    client, db, login = env
    seed_item(db, SELLER, "c1")
    t = _init(client, login("s", SELLER), recipient_email=BUYER).json()["transfer"]
    mine = client.get(f"/api/transfer/passport-pdf/{t['transfer_id']}", headers=login("s", SELLER))
    assert mine.status_code == 200 and mine.content.startswith(b"%PDF")
    theirs = client.get(f"/api/transfer/passport-pdf/{t['transfer_id']}", headers=login("b", BUYER))
    assert theirs.status_code == 403
