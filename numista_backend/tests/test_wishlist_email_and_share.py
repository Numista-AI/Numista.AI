"""Tests for POST /api/wishlist/send-email, EPN link enforcement, HTML escaping, and share snapshot creation."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main as m  # noqa: E402


@pytest.fixture(autouse=True)
def _clean_overrides(monkeypatch):
    monkeypatch.delenv("ALLOW_UNAUTHENTICATED", raising=False)
    yield
    m.app.dependency_overrides.clear()


def _sample_payload(**overrides):
    base = {
        "user_email": "aunt@example.com",
        "owner_alias": "Aunt Sarah <script>",
        "recipient_email": "eric@example.com",
        "personal_note": "For Christmas <b>please</b>!",
        "items": [
            {
                "title": "50 State Quarters: Delaware (1999) - P Mint",
                "program_id": "50state",
                "program_name": "50 State Quarters",
                "coin_id": "delaware",
                "coin_name": "Delaware",
                "year": "1999",
                "mint_mark": "P",
                "variety_label": "P Mint (Philadelphia)",
                "ebay_query": "1999 P 50 State Quarters Delaware Uncirculated coin",
            }
        ],
    }
    base.update(overrides)
    return base


def test_send_wishlist_email_unauthenticated_returns_401(monkeypatch):
    monkeypatch.setenv("K_SERVICE", "numista-backend-test-env")
    client = TestClient(m.app, raise_server_exceptions=False)
    resp = client.post("/api/wishlist/send-email", json=_sample_payload())
    assert resp.status_code == 401


def test_send_wishlist_email_anonymous_user_returns_403():
    m.app.dependency_overrides[m.get_current_user] = lambda: {
        "uid": "anon_uid_123",
        "firebase": {"sign_in_provider": "anonymous"},
    }
    client = TestClient(m.app, raise_server_exceptions=False)
    resp = client.post(
        "/api/wishlist/send-email",
        headers={"Authorization": "Bearer fake"},
        json=_sample_payload(user_email="anon_uid_123"),
    )
    assert resp.status_code == 403


def test_send_wishlist_email_spoofed_email_returns_403():
    m.app.dependency_overrides[m.require_registered_user] = lambda: {
        "email": "aunt@example.com",
        "uid": "uid_aunt",
        "admin": False,
        "firebase": {"sign_in_provider": "password"},
    }
    client = TestClient(m.app, raise_server_exceptions=False)
    with patch(
        "main._authenticate_request",
        side_effect=m.HTTPException(status_code=403, detail="Forbidden"),
    ):
        resp = client.post(
            "/api/wishlist/send-email",
            headers={"Authorization": "Bearer fake"},
            json=_sample_payload(user_email="victim@example.com"),
        )
    assert resp.status_code == 403


def test_send_wishlist_email_invalid_recipient_returns_422():
    m.app.dependency_overrides[m.require_registered_user] = lambda: {
        "email": "aunt@example.com",
        "uid": "uid_aunt",
        "admin": False,
        "firebase": {"sign_in_provider": "password"},
    }
    client = TestClient(m.app, raise_server_exceptions=False)
    with patch("main._authenticate_request", return_value="aunt@example.com"):
        resp = client.post(
            "/api/wishlist/send-email",
            headers={"Authorization": "Bearer fake"},
            json=_sample_payload(recipient_email="not-an-email"),
        )
    assert resp.status_code == 422


def test_send_wishlist_email_fail_closed_503_without_provider(monkeypatch):
    for var in (
        "RESEND_API_KEY",
        "SENDGRID_API_KEY",
        "SMTP_HOST",
        "SMTP_USER",
        "SMTP_PASSWORD",
    ):
        monkeypatch.delenv(var, raising=False)
    m.app.dependency_overrides[m.require_registered_user] = lambda: {
        "email": "aunt@example.com",
        "uid": "uid_aunt",
        "admin": False,
        "firebase": {"sign_in_provider": "password"},
    }
    client = TestClient(m.app, raise_server_exceptions=False)
    with patch("main._authenticate_request", return_value="aunt@example.com"), patch(
        "main._check_and_increment_rate_cap"
    ), patch.object(m.db, "collection", return_value=MagicMock()):
        resp = client.post(
            "/api/wishlist/send-email",
            headers={"Authorization": "Bearer fake"},
            json=_sample_payload(),
        )
    assert resp.status_code == 503


def test_send_wishlist_email_success_enforces_epn_and_escapes_html():
    m.app.dependency_overrides[m.require_registered_user] = lambda: {
        "email": "aunt@example.com",
        "uid": "uid_aunt",
        "admin": False,
        "firebase": {"sign_in_provider": "password"},
    }
    captured = {}

    async def _fake_send(**kwargs):
        captured.update(kwargs)
        return "resend"

    client = TestClient(m.app)
    with patch("main._authenticate_request", return_value="aunt@example.com"), patch(
        "main._check_and_increment_rate_cap"
    ), patch("main.send_wishlist_email", side_effect=_fake_send), patch.object(
        m.db, "collection", return_value=MagicMock()
    ):
        resp = client.post(
            "/api/wishlist/send-email",
            headers={"Authorization": "Bearer fake"},
            json=_sample_payload(),
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "sent"
    assert body["provider"] == "resend"
    assert body["share_url"].startswith("https://numista.ai/wishlist/wishlist_")
    assert "campid=5339148752" in captured["html_body"]
    assert "mkrid=711-53200-19255-0" in captured["html_body"]
    assert "<script>" not in captured["html_body"]
    assert "&lt;script&gt;" in captured["html_body"]
