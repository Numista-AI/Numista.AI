"""Unit tests for GET /api/v1/hardware/installer_url (Lockdown of NumistaAgentSetup.exe)."""

from unittest.mock import MagicMock, patch
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from routes.hardware_routes import router, PRIVATE_INSTALLER_BUCKET, INSTALLER_BLOB_PATH
from routes.deps import get_current_user


def _build_client(user_override=None):
    app = FastAPI()
    app.include_router(router)
    if user_override is not None:
        app.dependency_overrides[get_current_user] = user_override
    return TestClient(app)


def test_unauthenticated_rejected_with_401(monkeypatch):
    monkeypatch.delenv("ALLOW_UNAUTHENTICATED", raising=False)
    client = _build_client()
    resp = client.get("/api/v1/hardware/installer_url")
    assert resp.status_code == 401


def test_anonymous_guest_rejected_with_403():
    client = _build_client(
        lambda: {"uid": "anon_123", "firebase": {"sign_in_provider": "anonymous"}}
    )
    resp = client.get("/api/v1/hardware/installer_url")
    assert resp.status_code == 403
    assert "sign in" in resp.json()["detail"].lower()


def test_authenticated_user_receives_v4_signed_url():
    mock_blob = MagicMock()
    mock_blob.generate_signed_url.return_value = (
        "https://storage.googleapis.com/numista-private-installers/"
        "downloads/NumistaAgentSetup.exe?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Signature=deadbeef"
    )
    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_blob

    with patch("routes.hardware_routes.check_and_increment_rate_cap") as mock_rate, \
         patch("routes.hardware_routes.storage_client") as mock_storage:
        mock_storage._credentials = MagicMock(sign_bytes=MagicMock())
        mock_storage.bucket.return_value = mock_bucket

        client = _build_client(
            lambda: {
                "uid": "user_abc",
                "email": "collector@numista.ai",
                "admin": False,
                "firebase": {"sign_in_provider": "password"},
            }
        )
        resp = client.get("/api/v1/hardware/installer_url")

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "success"
    assert body["filename"] == "NumistaAgentSetup.exe"
    assert body["expires_in_seconds"] == 900
    assert "numista-private-installers/downloads/NumistaAgentSetup.exe" in body["signed_url"]
    mock_rate.assert_called_once_with("user_abc", "hardware_installer_url", daily_limit=10, is_admin=False)
    mock_storage.bucket.assert_called_once_with(PRIVATE_INSTALLER_BUCKET)
    mock_bucket.blob.assert_called_once_with(INSTALLER_BLOB_PATH)


def test_rate_cap_exceeded_returns_429():
    with patch(
        "routes.hardware_routes.check_and_increment_rate_cap",
        side_effect=HTTPException(status_code=429, detail="Daily limit reached"),
    ):
        client = _build_client(
            lambda: {"uid": "user_abc", "email": "collector@numista.ai", "admin": False}
        )
        resp = client.get("/api/v1/hardware/installer_url")
    assert resp.status_code == 429
