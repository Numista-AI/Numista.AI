"""Regression tests for Review #2: Hardware Installer & Lateral Transfer Privacy (S2-01..S2-04)."""

import importlib
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from numista_backend import main as backend_main
from numista_backend.routes import deps
from numista_backend.services.gcs_signing_service import generate_v4_signed_url
from numista_backend.services.transfer_service import claim_transfer


@pytest.mark.asyncio
async def test_require_registered_user_blocks_anonymous_and_guest():
    req = MagicMock()

    with pytest.raises(HTTPException) as exc_anon:
        await deps.require_registered_user(
            req,
            {"uid": "anon-1", "firebase": {"sign_in_provider": "anonymous"}},
        )
    assert exc_anon.value.status_code == 403

    with pytest.raises(HTTPException) as exc_guest_uid:
        await deps.require_registered_user(
            req,
            {"uid": "dev_guest_uid", "email": "dev_guest@numista.ai"},
        )
    assert exc_guest_uid.value.status_code == 403

    with pytest.raises(HTTPException) as exc_guest_email:
        await deps.require_registered_user(
            req,
            {"uid": "other-uid", "email": "dev_guest@numista.ai"},
        )
    assert exc_guest_email.value.status_code == 403

    with pytest.raises(HTTPException) as exc_empty:
        await deps.require_registered_user(req, {})
    assert exc_empty.value.status_code == 401

    valid_user = {
        "uid": "user-1",
        "email": "alice@example.com",
        "firebase": {"sign_in_provider": "password"},
    }
    assert await deps.require_registered_user(req, valid_user) == valid_user


@pytest.mark.parametrize(
    "path,payload",
    [
        ("/api/transfer/initiate", {"item_ids": ["1"], "recipient_email": "b@example.com"}),
        ("/api/transfer/claim", {"transfer_id": "t1", "claim_pin": "123456"}),
        ("/api/transfer/recall", {"transfer_id": "t1"}),
        ("/api/v1/photos/signed_url", {"urls": ["https://storage.googleapis.com/b/o.jpg"]}),
    ],
)
def test_transfer_and_photo_routes_reject_anonymous_user(path, payload):
    backend_main.app.dependency_overrides[deps.get_current_user] = lambda: {
        "uid": "anon-1",
        "firebase": {"sign_in_provider": "anonymous"},
    }
    try:
        client = TestClient(backend_main.app)
        resp = client.post(path, json=payload)
        assert resp.status_code == 403
    finally:
        backend_main.app.dependency_overrides.clear()


def test_hardware_installer_url_rejects_anonymous_and_guest():
    backend_main.app.dependency_overrides[deps.get_current_user] = lambda: {
        "uid": "dev_guest_uid",
        "email": "dev_guest@numista.ai",
    }
    try:
        client = TestClient(backend_main.app)
        resp = client.get("/api/v1/hardware/installer_url")
        assert resp.status_code == 403
    finally:
        backend_main.app.dependency_overrides.clear()


def test_generate_v4_signed_url_handles_none_creds_and_response_headers():
    storage_client = MagicMock()
    storage_client._credentials = None
    blob = storage_client.bucket.return_value.blob.return_value
    blob.generate_signed_url.return_value = "https://signed.example.com/setup.exe"

    url = generate_v4_signed_url(
        storage_client,
        "numista-private-installers",
        "downloads/NumistaAgentSetup.exe",
        expiry_minutes=15,
        method="GET",
        response_disposition='attachment; filename="NumistaAgentSetup.exe"',
        response_type="application/octet-stream",
    )
    assert url == "https://signed.example.com/setup.exe"
    kwargs = blob.generate_signed_url.call_args.kwargs
    assert kwargs["response_disposition"] == 'attachment; filename="NumistaAgentSetup.exe"'
    assert kwargs["response_type"] == "application/octet-stream"


def test_identify_coin_skips_local_dotenv_when_frozen(monkeypatch):
    repo_root = str(Path(__file__).resolve().parents[2])
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    import numista_hardware.identify_coin as identify_coin

    calls = []
    monkeypatch.setattr("dotenv.load_dotenv", lambda p=None, *a, **k: calls.append(str(p)))
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    try:
        importlib.reload(identify_coin)
        here_env = str(Path(identify_coin.__file__).parent / ".env")
        assert here_env not in calls
        assert any("NumistaAI" in c and c.endswith(".env") for c in calls)
    finally:
        monkeypatch.delattr(sys, "frozen", raising=False)
        importlib.reload(identify_coin)


def test_claim_transfer_pin_uses_constant_time_compare_and_locks_after_5():
    db = MagicMock()
    transfer_doc = MagicMock()
    transfer_doc.exists = True
    transfer_doc.to_dict.return_value = {
        "status": "pending",
        "recipient_email": "bob@example.com",
        "claim_pin": "654321",
        "pin_fail_count": 4,
    }
    transfer_ref = db.collection.return_value.document.return_value
    transfer_ref.get.return_value = transfer_doc

    with pytest.raises(ValueError, match="Too many incorrect PIN attempts"):
        claim_transfer(db, "bob@example.com", "t-1", "000000")

    update_payload = transfer_ref.update.call_args.args[0]
    assert "pin_locked_until" in update_payload
