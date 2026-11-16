"""SIGN-FIX-1: IAM SignBlob must use a cloud-platform-scoped token (no network)."""

from unittest.mock import MagicMock

import pytest

from numista_backend.services import gcs_signing_service as gss

CLOUD_PLATFORM = ["https://www.googleapis.com/auth/cloud-platform"]


@pytest.fixture(autouse=True)
def _reset_signing_creds(monkeypatch):
    monkeypatch.setattr(gss, "_signing_creds", None)
    yield
    gss._signing_creds = None


def _storage(creds):
    storage = MagicMock()
    blob = MagicMock()
    blob.generate_signed_url.return_value = "https://storage.googleapis.com/signed"
    storage.bucket.return_value.blob.return_value = blob
    storage._credentials = creds
    return storage, blob


def _storage_creds_without_sign_bytes():
    creds = MagicMock(spec=["refresh", "service_account_email", "token"])
    creds.service_account_email = "storage-sa@x"
    creds.token = "tok-storage"
    return creds


def _fake_default(monkeypatch, fake_creds):
    calls = []

    def fake_default(*args, **kwargs):
        calls.append(kwargs)
        return fake_creds, "proj"

    monkeypatch.setattr(gss.google.auth, "default", fake_default)
    return calls


def test_t1_uses_cloud_platform_token_not_storage_token(monkeypatch):
    fake = MagicMock()
    fake.token = "tok-cp"
    fake.valid = True
    fake.service_account_email = "sa@x"
    calls = _fake_default(monkeypatch, fake)
    storage_creds = _storage_creds_without_sign_bytes()
    storage, blob = _storage(storage_creds)

    url = gss.generate_v4_signed_url(storage, "b", "o.jpg", method="PUT", content_type="image/jpeg")

    assert url == "https://storage.googleapis.com/signed"
    assert len(calls) == 1
    assert calls[0]["scopes"] == CLOUD_PLATFORM
    kwargs = blob.generate_signed_url.call_args.kwargs
    assert kwargs["access_token"] == "tok-cp"
    assert kwargs["access_token"] != storage_creds.token
    assert kwargs["service_account_email"] == "sa@x"
    assert kwargs["method"] == "PUT"
    assert kwargs["content_type"] == "image/jpeg"
    storage_creds.refresh.assert_not_called()
    fake.refresh.assert_not_called()


def test_t2_default_email_falls_back_to_signer_sa(monkeypatch):
    fake = MagicMock()
    fake.token = "tok-cp"
    fake.valid = True
    fake.service_account_email = "default"
    _fake_default(monkeypatch, fake)
    storage, blob = _storage(_storage_creds_without_sign_bytes())

    gss.generate_v4_signed_url(storage, "b", "o.jpg")

    kwargs = blob.generate_signed_url.call_args.kwargs
    assert kwargs["service_account_email"] == gss.DEFAULT_SIGNER_SA
    assert kwargs["access_token"] == "tok-cp"


def test_t3_local_key_path_unchanged(monkeypatch):
    def boom(*args, **kwargs):
        raise AssertionError("google.auth.default must not be called on the local-key path")

    monkeypatch.setattr(gss.google.auth, "default", boom)
    storage, blob = _storage(MagicMock(sign_bytes=MagicMock()))

    gss.generate_v4_signed_url(storage, "b", "o.jpg")

    kwargs = blob.generate_signed_url.call_args.kwargs
    assert "access_token" not in kwargs
    assert "service_account_email" not in kwargs
    assert kwargs["version"] == "v4"


def test_t4_refresh_only_when_invalid_and_creds_cached(monkeypatch):
    fake = MagicMock()
    fake.token = "tok-cp"
    fake.valid = False
    fake.service_account_email = "sa@x"

    def _refresh(_req):
        fake.valid = True

    fake.refresh.side_effect = _refresh
    calls = _fake_default(monkeypatch, fake)
    storage, blob = _storage(_storage_creds_without_sign_bytes())

    gss.generate_v4_signed_url(storage, "b", "o1.jpg")
    assert fake.refresh.call_count == 1

    gss.generate_v4_signed_url(storage, "b", "o2.jpg")
    assert fake.refresh.call_count == 1
    assert len(calls) == 1
    assert blob.generate_signed_url.call_args.kwargs["access_token"] == "tok-cp"
