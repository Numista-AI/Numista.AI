"""
numista_backend/tests/test_expiring_photo_links.py
------------------------------------------------
Security & functional tests for Task 7:
- POST /api/v1/photos/signed_url mints 15-minute V4 signed GET URLs for owner
  gs:// and legacy Firebase download URLs.
- Rejects unauthenticated, anonymous, production dev_guest_uid, cross-user,
  non-allowlisted bucket, traversal, and SSRF URLs.
- Enforces 50-URL batch cap and 600/day rate cap (429).
- Handles partial batch failures gracefully and supports Cloud Run IAM
  signBlob fallback.
"""

from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from main import app
from routes.deps import get_current_user
from services.coin_image_service import generate_v4_signed_get_url


@pytest.fixture(autouse=True)
def clean_deps():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def _user_a():
    return {"uid": "uid_a", "email": "user_a@example.com", "admin": False}


def _mock_storage_signing(signed_url: str = "https://storage.googleapis.com/signed-v4-url"):
    mock_storage = MagicMock()
    mock_blob = MagicMock()
    mock_blob.generate_signed_url.return_value = signed_url
    mock_storage.bucket.return_value.blob.return_value = mock_blob
    return mock_storage, mock_blob


def test_1_unauthenticated_anonymous_and_prod_dev_guest_rejected(monkeypatch):
    client = TestClient(app, raise_server_exceptions=False)

    # Unauthenticated in production returns 401
    monkeypatch.setenv("K_SERVICE", "numista-backend")
    resp = client.post(
        "/api/v1/photos/signed_url",
        json={"urls": ["gs://numista-uploads-studio-9101802118-8c9a8/users/user_a@example.com/coins/c1/obv.jpg"]},
    )
    assert resp.status_code == 401

    # Anonymous user
    app.dependency_overrides[get_current_user] = lambda: {
        "uid": "anon_1",
        "firebase": {"sign_in_provider": "anonymous"},
    }
    resp_anon = client.post(
        "/api/v1/photos/signed_url",
        json={"urls": ["gs://numista-uploads-studio-9101802118-8c9a8/users/anon_1/coins/c1/obv.jpg"]},
    )
    assert resp_anon.status_code == 403

    # Production dev_guest_uid
    app.dependency_overrides[get_current_user] = lambda: {"uid": "dev_guest_uid", "email": "dev@example.com"}
    with patch("routes.photo_routes.is_production_env", return_value=True):
        resp_guest = client.post(
            "/api/v1/photos/signed_url",
            json={"urls": ["gs://numista-uploads-studio-9101802118-8c9a8/users/dev@example.com/coins/c1/obv.jpg"]},
        )
    assert resp_guest.status_code == 403


def test_2_owner_gs_url_returns_15_min_v4_signed_url():
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    mock_storage, mock_blob = _mock_storage_signing(
        "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/users/user_a@example.com/coins/c1/obv.jpg?X-Goog-Signature=abc"
    )
    gs_url = "gs://numista-uploads-studio-9101802118-8c9a8/users/user_a@example.com/coins/c1/obv.jpg"

    with patch("routes.photo_routes.storage_client", mock_storage), patch(
        "routes.photo_routes.check_and_increment_rate_cap", return_value=None
    ):
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/api/v1/photos/signed_url", json={"urls": [gs_url]})

    assert resp.status_code == 200
    data = resp.json()
    assert data["expires_in_seconds"] == 900
    assert gs_url in data["signed_urls"]
    assert "X-Goog-Signature=abc" in data["signed_urls"][gs_url]
    assert data["errors"] == {}

    mock_storage.bucket.assert_called_with("numista-uploads-studio-9101802118-8c9a8")
    mock_storage.bucket.return_value.blob.assert_called_with("users/user_a@example.com/coins/c1/obv.jpg")
    mock_blob.generate_signed_url.assert_called_once()
    kwargs = mock_blob.generate_signed_url.call_args.kwargs
    assert kwargs["version"] == "v4"
    assert kwargs["expiration"] == timedelta(minutes=15)
    assert kwargs["method"] == "GET"


def test_3_owner_firebase_download_url_normalizes_and_signs():
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    mock_storage, mock_blob = _mock_storage_signing("https://storage.googleapis.com/signed-fb")
    fb_url = (
        "https://firebasestorage.googleapis.com/v0/b/"
        "studio-9101802118-8c9a8.firebasestorage.app/o/"
        "users%2Fuser_a%40example.com%2Fcoins%2Fc1%2Fobv.jpg"
        "?alt=media&token=permanent-leaked-token"
    )

    with patch("routes.photo_routes.storage_client", mock_storage), patch(
        "routes.photo_routes.check_and_increment_rate_cap", return_value=None
    ):
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/api/v1/photos/signed_url", json={"urls": [fb_url]})

    assert resp.status_code == 200
    data = resp.json()
    assert data["signed_urls"][fb_url] == "https://storage.googleapis.com/signed-fb"
    mock_storage.bucket.assert_called_with("studio-9101802118-8c9a8.firebasestorage.app")
    mock_storage.bucket.return_value.blob.assert_called_with("users/user_a@example.com/coins/c1/obv.jpg")


def test_4_cross_user_url_returns_403():
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    mock_storage, _ = _mock_storage_signing()
    other_url = "gs://numista-uploads-studio-9101802118-8c9a8/users/other@example.com/coins/c1/obv.jpg"

    with patch("routes.photo_routes.storage_client", mock_storage), patch(
        "routes.photo_routes.check_and_increment_rate_cap", return_value=None
    ):
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/api/v1/photos/signed_url", json={"urls": [other_url]})

    assert resp.status_code == 403


@pytest.mark.parametrize(
    "bad_url",
    [
        "gs://evil-bucket/users/user_a@example.com/a.jpg",
        "gs://numista-uploads-studio-9101802118-8c9a8/users/user_a@example.com/../other@example.com/a.jpg",
        "gs://numista-uploads-studio-9101802118-8c9a8/users/user_a@example.com/%2e%2e/other/a.jpg",
        "https://169.254.169.254/latest/meta-data/",
    ],
)
def test_5_invalid_bucket_traversal_and_ssrf_rejected(bad_url):
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    mock_storage, _ = _mock_storage_signing()

    with patch("routes.photo_routes.storage_client", mock_storage), patch(
        "routes.photo_routes.check_and_increment_rate_cap", return_value=None
    ):
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/api/v1/photos/signed_url", json={"urls": [bad_url]})

    assert resp.status_code == 403


def test_6_batch_cap_over_50_rejected():
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    urls = [
        f"gs://numista-uploads-studio-9101802118-8c9a8/users/user_a@example.com/coins/c{i}/obv.jpg"
        for i in range(51)
    ]
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post("/api/v1/photos/signed_url", json={"urls": urls})
    assert resp.status_code in (400, 422)


def test_7_daily_rate_cap_exceeded_returns_429():
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    mock_storage, _ = _mock_storage_signing()
    gs_url = "gs://numista-uploads-studio-9101802118-8c9a8/users/user_a@example.com/coins/c1/obv.jpg"

    def _raise_429(*args, **kwargs):
        raise HTTPException(status_code=429, detail="Daily rate limit exceeded")

    with patch("routes.photo_routes.storage_client", mock_storage), patch(
        "routes.photo_routes.check_and_increment_rate_cap", side_effect=_raise_429
    ):
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/api/v1/photos/signed_url", json={"urls": [gs_url]})

    assert resp.status_code == 429


def test_8_partial_batch_failure_preserves_valid_urls():
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    mock_storage, _ = _mock_storage_signing("https://storage.googleapis.com/signed-valid")
    valid_url = "gs://numista-uploads-studio-9101802118-8c9a8/users/user_a@example.com/coins/c1/obv.jpg"
    bad_url = "gs://numista-uploads-studio-9101802118-8c9a8/users/other@example.com/coins/c1/obv.jpg"

    with patch("routes.photo_routes.storage_client", mock_storage), patch(
        "routes.photo_routes.check_and_increment_rate_cap", return_value=None
    ):
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/api/v1/photos/signed_url", json={"urls": [valid_url, bad_url]})

    assert resp.status_code == 200
    data = resp.json()
    assert data["signed_urls"] == {valid_url: "https://storage.googleapis.com/signed-valid"}
    assert bad_url in data["errors"]


def test_9_iam_signblob_fallback_on_missing_private_key():
    mock_storage = MagicMock()
    mock_blob = MagicMock()
    mock_blob.generate_signed_url.return_value = "https://storage.googleapis.com/iam-signed"
    mock_storage.bucket.return_value.blob.return_value = mock_blob

    fake_creds = MagicMock(spec=["refresh", "service_account_email", "token"])
    fake_creds.service_account_email = "sa@proj.iam.gserviceaccount.com"
    fake_creds.token = "tok_123"
    mock_storage._credentials = fake_creds

    url = generate_v4_signed_get_url(
        mock_storage,
        "numista-uploads-studio-9101802118-8c9a8",
        "users/user_a@example.com/coins/c1/obv.jpg",
        expiry_minutes=15,
    )

    assert url == "https://storage.googleapis.com/iam-signed"
    fake_creds.refresh.assert_called_once()
    kwargs = mock_blob.generate_signed_url.call_args.kwargs
    assert kwargs["service_account_email"] == "sa@proj.iam.gserviceaccount.com"
    assert kwargs["access_token"] == "tok_123"
