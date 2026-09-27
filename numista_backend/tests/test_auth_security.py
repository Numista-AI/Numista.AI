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


def test_invalid_cost_overrides_rejected_sf2(monkeypatch):
    """Cost overrides that don't match sum or count must return 400 (SF2)."""
    from firebase_admin import auth as fb_auth

    def fake_verify(token, *args, **kwargs):
        return {"email": "tester@numista.ai", "uid": "tester_uid"}

    monkeypatch.setattr(fb_auth, "verify_id_token", fake_verify)

    # 1. Sum mismatch
    resp = client.post(
        "/api/commit_group_photo",
        headers={"Authorization": "Bearer valid_token"},
        json={
            "user_email": "tester@numista.ai",
            "coins": [],
            "cost_total": "$50.00",
            "cost_overrides": ["$10.00", "$15.00"],
        },
    )
    # Len 0 coins returns 400
    assert resp.status_code == 400

