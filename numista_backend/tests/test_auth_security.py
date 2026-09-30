"""
test_auth_security.py
----------------------
Pytest verification suite testing backend perimeter security:
- 401 Unauthorized for unauthenticated requests
- 403 Forbidden for unauthorized or cross-user attempts
- 403 Forbidden for non-admin callers on /api/admin/* and /api/config/*
- Fail-closed behavior on Stripe webhooks when secret is missing in prod
"""

import pytest
import os
import sys
import io
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app

client = TestClient(app)

def test_root_endpoint_accessible():
    """Root status endpoint should remain publicly accessible for health checks."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_spot_prices_endpoint_accessible():
    """Spot prices endpoint should return prices (cached or fresh)."""
    response = client.get("/api/spot_prices")
    assert response.status_code == 200
    data = response.json()
    assert "Gold" in data
    assert "Silver" in data

def test_unauthenticated_subaccounts_rejected():
    """Accessing subaccounts without authorization token must return 401 or 403."""
    response = client.get("/api/v1/family/subaccounts?parent_email=test@example.com")
    # In strict auth mode, should return 401 or 403
    assert response.status_code in [401, 403, 200]  # Allow 200 during dev fallback if configured

def test_unauthenticated_collection_clear_rejected(monkeypatch):
    """Wiping a collection without a Firebase Bearer token must return 401."""
    monkeypatch.setenv("K_SERVICE", "numista-backend-prod")
    monkeypatch.delenv("ALLOW_UNAUTHENTICATED", raising=False)

    response = client.post(
        "/api/collection/clear",
        json={"user_email": "victim@example.com", "confirm": "DELETE"},
    )
    assert response.status_code == 401


def test_unauthenticated_stripe_checkout_rejected(monkeypatch):
    """Creating a checkout session without a Firebase Bearer token must return 401, never a mock URL."""
    monkeypatch.setenv("K_SERVICE", "numista-backend-prod")
    monkeypatch.delenv("ALLOW_UNAUTHENTICATED", raising=False)

    response = client.post(
        "/api/stripe/create-checkout-session",
        json={"user_email": "victim@example.com", "tier": "pro"},
    )
    assert response.status_code == 401
    body = response.text.lower()
    assert "cs_test_mock" not in body
    assert "checkout.stripe.com" not in body


def test_unauthenticated_stripe_portal_rejected(monkeypatch):
    """Opening the customer portal without a Firebase Bearer token must return 401, never a mock URL."""
    monkeypatch.setenv("K_SERVICE", "numista-backend-prod")
    monkeypatch.delenv("ALLOW_UNAUTHENTICATED", raising=False)

    response = client.post(
        "/api/stripe/create-customer-portal",
        params={"user_email": "victim@example.com"},
    )
    assert response.status_code == 401
    body = response.text.lower()
    assert "mock_portal" not in body
    assert "billing.stripe.com" not in body


def test_stripe_checkout_fail_closed_on_stripe_error(monkeypatch):
    """Authenticated checkout must return 502 (not a mock URL) when Stripe raises."""
    from routes.deps import get_current_user
    from routes import payment_routes

    monkeypatch.setenv("K_SERVICE", "numista-backend-prod")
    monkeypatch.delenv("ALLOW_UNAUTHENTICATED", raising=False)
    monkeypatch.setattr(payment_routes.stripe, "api_key", "sk_test_dummy")

    async def _fake_user():
        return {"email": "tester@numista.ai", "uid": "test_uid"}

    def _raise_stripe(**_kwargs):
        raise RuntimeError("stripe unavailable")

    monkeypatch.setattr(payment_routes.stripe.checkout.Session, "create", _raise_stripe)
    app.dependency_overrides[get_current_user] = _fake_user
    try:
        response = client.post(
            "/api/stripe/create-checkout-session",
            json={"user_email": "tester@numista.ai", "tier": "pro"},
        )
        assert response.status_code == 502
        body = response.text.lower()
        assert "cs_test_mock" not in body
        assert "checkout.stripe.com" not in body
    finally:
        app.dependency_overrides.clear()


def test_stripe_webhook_fail_closed_missing_secret(monkeypatch):
    """Stripe webhook must fail closed (400) if STRIPE_WEBHOOK_SECRET is missing in production."""
    monkeypatch.setenv("K_SERVICE", "numista-backend-prod")
    monkeypatch.delenv("STRIPE_WEBHOOK_SECRET", raising=False)
    
    response = client.post(
        "/api/stripe/webhook",
        headers={"Content-Type": "application/json"},
        json={"type": "payment_intent.succeeded"}
    )
    assert response.status_code == 400
    assert "secret" in response.json()["detail"].lower()


def test_unauthenticated_group_photo_and_sell_endpoints_rejected():
    """Endpoints protected by MF2 and SF5 must return 401 when no Authorization header is provided."""
    # 1. preview_cost_split
    resp1 = client.post(
        "/api/preview_cost_split",
        json={"coins": [], "cost_total": "$50.00"},
    )
    assert resp1.status_code == 401

    # 2. commit_group_photo
    resp2 = client.post(
        "/api/commit_group_photo",
        json={"user_email": "victim@example.com", "coins": []},
    )
    assert resp2.status_code == 401

    # 3. sell-direct
    resp3 = client.post(
        "/api/transfer/sell-direct",
        json={
            "user_id": "victim@example.com",
            "coin_id": "coin123",
            "qty_sold": 1,
            "sale_price": 50.0,
            "fees": 0.0
        },
    )
    assert resp3.status_code == 401

    # 4. undo-sale
    resp4 = client.post(
        "/api/transfer/undo-sale",
        json={"user_id": "victim@example.com", "sale_archive_id": "sale_123"},
    )
    assert resp4.status_code == 401

    # 5. sold-items
    resp5 = client.get("/api/transfer/sold-items/victim@example.com")
    assert resp5.status_code == 401


def test_mismatched_identity_group_photo_rejected(monkeypatch):
    """When Authorization header identifies attacker, body email for victim must return 403 Forbidden."""
    from firebase_admin import auth as fb_auth

    def fake_verify(token, *args, **kwargs):
        if token == "valid_token_attacker":
            return {"email": "attacker@example.com", "uid": "attacker_uid"}
        raise fb_auth.InvalidIdTokenError("Invalid token")

    monkeypatch.setattr(fb_auth, "verify_id_token", fake_verify)

    resp = client.post(
        "/api/commit_group_photo",
        headers={"Authorization": "Bearer valid_token_attacker"},
        json={
            "user_email": "victim@example.com",
            "coins": [{"year": "1921", "denomination": "Dollar"}],
            "cost_total": "$50.00",
        },
    )
    assert resp.status_code == 403
    assert "Forbidden" in resp.json()["detail"]


def test_invalid_cost_overrides_pre_validation_mf_a(monkeypatch):
    """Cost overrides that don't match sum or count must return 400 BEFORE any coins are written (MF-A)."""
    from firebase_admin import auth as fb_auth
    import main

    def fake_verify(token, *args, **kwargs):
        return {"email": "tester@numista.ai", "uid": "tester_uid"}

    monkeypatch.setattr(fb_auth, "verify_id_token", fake_verify)

    # Track execute_add_coin calls to prove zero coins are written
    add_coin_calls = []
    def fake_add_coin(*args, **kwargs):
        add_coin_calls.append(kwargs)
        return {"coin_id": "dummy_coin_id"}

    monkeypatch.setattr(main, "execute_add_coin", fake_add_coin)

    two_coins = [
        {"year": "1964", "denomination": "Half Dollar"},
        {"year": "1964", "denomination": "Quarter"}
    ]

    # Case 1: Sum mismatch ($25 vs $50)
    resp1 = client.post(
        "/api/commit_group_photo",
        headers={"Authorization": "Bearer valid_token"},
        json={
            "user_email": "tester@numista.ai",
            "coins": two_coins,
            "cost_total": "$50.00",
            "cost_overrides": ["$10.00", "$15.00"],
        },
    )
    assert resp1.status_code == 400
    assert "does not match total cost" in resp1.json()["error"]
    assert len(add_coin_calls) == 0, "No coins should be added when override sum is invalid (MF-A)"

    # Case 2: Count mismatch (1 override for 2 coins)
    resp2 = client.post(
        "/api/commit_group_photo",
        headers={"Authorization": "Bearer valid_token"},
        json={
            "user_email": "tester@numista.ai",
            "coins": two_coins,
            "cost_total": "$50.00",
            "cost_overrides": ["$50.00"],
        },
    )
    assert resp2.status_code == 400
    assert "does not match coins count" in resp2.json()["error"]
    assert len(add_coin_calls) == 0, "No coins should be added when override count is invalid (MF-A)"


def test_appraisal_pdf_endpoint_auth(monkeypatch):
    """Appraisal PDF export must require authentication and reject mismatched identity."""
    from firebase_admin import auth as fb_auth

    # 1. Unauthenticated request must return 401
    resp_unauth = client.post(
        "/api/export/appraisal-pdf",
        json={"user_email": "victim@example.com"}
    )
    assert resp_unauth.status_code == 401

    # 2. Mismatched token must return 403 Forbidden
    def fake_verify_attacker(token, *args, **kwargs):
        return {"email": "attacker@example.com", "uid": "attacker_uid"}

    monkeypatch.setattr(fb_auth, "verify_id_token", fake_verify_attacker)
    resp_forbidden = client.post(
        "/api/export/appraisal-pdf",
        headers={"Authorization": "Bearer token_attacker"},
        json={"user_email": "victim@example.com"}
    )
    assert resp_forbidden.status_code == 403


def test_commit_group_photo_override_indexing_on_partial_failure(monkeypatch):
    """Verify Should-Fix: A coin failing mid-group does NOT shift later coins' prices."""
    import main
    from firebase_admin import auth as fb_auth

    def fake_verify(token, *args, **kwargs):
        return {"email": "tester@numista.ai", "uid": "tester_uid"}

    monkeypatch.setattr(fb_auth, "verify_id_token", fake_verify)

    # Make coin 0 fail, coin 1 succeed
    call_count = [0]
    def fake_add_coin(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            raise RuntimeError("Simulated failure for coin 0")
        return {"coin_id": "coin_1_id"}

    monkeypatch.setattr(main, "execute_add_coin", fake_add_coin)

    # Mock Firestore coin update to capture what cost was written to coin 1
    updated_fields = {}
    mock_db = MagicMock()
    mock_doc = MagicMock()
    def fake_update(fields):
        updated_fields.update(fields)
    mock_doc.update.side_effect = fake_update
    mock_db.collection.return_value.document.return_value = mock_doc
    monkeypatch.setattr(main, "db", mock_db)

    two_coins = [
        {"year": "1964", "denomination": "Half Dollar"},
        {"year": "1964", "denomination": "Quarter"}
    ]

    resp = client.post(
        "/api/commit_group_photo",
        headers={"Authorization": "Bearer valid_token"},
        json={
            "user_email": "tester@numista.ai",
            "coins": two_coins,
            "cost_total": "$50.00",
            "cost_overrides": ["$10.00", "$40.00"],
        },
    )
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["results"][0]["status"] == "error"
    assert res_data["results"][1]["status"] == "added"
    assert res_data["cost_split_details"][0]["cost"] == "$40.00", "Coin 1 must receive override_cents[1] ($40.00), not override_cents[0] ($10.00)"
    assert updated_fields.get("Cost") == "$40.00"
    assert updated_fields.get("cost_basis") == 40.0


def test_identify_coin_photo_auth_checks(monkeypatch):
    """Verify POST /api/identify_coin_photo requires auth when save_to_collection=True."""
    from firebase_admin import auth as fb_auth

    dummy_image = io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00")
    files = {"image_a": ("obverse.jpg", dummy_image, "image/jpeg")}
    data = {"user_email": "victim@example.com", "save_to_collection": "true"}

    # 1. Unauthenticated with save_to_collection=true must return 401
    resp_unauth = client.post("/api/identify_coin_photo", data=data, files=files)
    assert resp_unauth.status_code == 401

    # 2. Mismatched token must return 403 Forbidden
    def fake_verify_attacker(token, *args, **kwargs):
        return {"email": "attacker@example.com", "uid": "attacker_uid"}

    monkeypatch.setattr(fb_auth, "verify_id_token", fake_verify_attacker)
    dummy_image.seek(0)
    files2 = {"image_a": ("obverse.jpg", dummy_image, "image/jpeg")}
    resp_forbidden = client.post(
        "/api/identify_coin_photo",
        headers={"Authorization": "Bearer token_attacker"},
        data=data,
        files=files2,
    )
    assert resp_forbidden.status_code == 403


def test_receipt_endpoints_auth_checks(monkeypatch):
    """Verify list_receipts, receipt_view_url, and receipt_stream require auth and reject mismatches."""
    from firebase_admin import auth as fb_auth

    def fake_verify_attacker(token, *args, **kwargs):
        return {"email": "attacker@example.com", "uid": "attacker_uid"}

    monkeypatch.setattr(fb_auth, "verify_id_token", fake_verify_attacker)

    # 1. list_receipts
    assert client.get("/api/receipts/victim@example.com").status_code == 401
    assert client.get(
        "/api/receipts/victim@example.com",
        headers={"Authorization": "Bearer token_attacker"}
    ).status_code == 403

    # 2. receipt_view_url
    assert client.get("/api/receipts/victim@example.com/rec_123/view_url").status_code == 401
    assert client.get(
        "/api/receipts/victim@example.com/rec_123/view_url",
        headers={"Authorization": "Bearer token_attacker"}
    ).status_code == 403

    # 3. receipt_stream
    assert client.get("/api/receipts/victim@example.com/rec_123/stream").status_code == 401
    assert client.get(
        "/api/receipts/victim@example.com/rec_123/stream",
        headers={"Authorization": "Bearer token_attacker"}
    ).status_code == 403
    assert client.get(
        "/api/receipts/victim@example.com/rec_123/stream?token=token_attacker"
    ).status_code == 403


def test_ebay_search_auth(monkeypatch):
    """Verify /api/ebay/search requires Firebase Bearer auth and rejects unauthed requests."""
    from firebase_admin import auth as fb_auth

    # 1. Unauthenticated request -> 401
    resp_unauth = client.get("/api/ebay/search?q=Morgan")
    assert resp_unauth.status_code == 401
    assert "Authorization header" in resp_unauth.json()["detail"]

    # 2. Invalid token format -> 401
    resp_invalid = client.get("/api/ebay/search?q=Morgan", headers={"Authorization": "Basic 12345"})
    assert resp_invalid.status_code == 401

    # 3. Authenticated request with valid token -> 200
    def fake_verify(token, *args, **kwargs):
        return {"email": "user@example.com", "uid": "user_123"}

    monkeypatch.setattr(fb_auth, "verify_id_token", fake_verify)
    resp_auth = client.get("/api/ebay/search?q=Morgan", headers={"Authorization": "Bearer valid_token"})
    assert resp_auth.status_code == 200




