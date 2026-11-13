"""Security regression suite for Review #1 (S1-01 through S1-08)."""

import io
import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main as backend_main
from main import app
from routes import deps
from routes.deps import get_current_user
from services.gcs_signing_service import generate_v4_signed_url


@pytest.fixture(autouse=True)
def _clean_overrides(monkeypatch):
    monkeypatch.delenv("ALLOW_UNAUTHENTICATED", raising=False)
    monkeypatch.delenv("CRON_SECRET", raising=False)
    yield
    app.dependency_overrides.clear()


def _alice():
    return {
        "uid": "uid_alice",
        "email": "alice@example.com",
        "admin": False,
        "firebase": {"sign_in_provider": "google.com"},
    }


def _admin():
    return {
        "uid": "uid_admin",
        "email": "admin@example.com",
        "admin": True,
        "firebase": {"sign_in_provider": "google.com"},
    }


def test_1_unauthenticated_phase1_and_cron_endpoints_return_401():
    client = TestClient(app, raise_server_exceptions=False)
    dummy_png = ("obv.png", io.BytesIO(b"fake"), "image/png")

    assert (
        client.post(
            "/api/review/break_up_set",
            json={"user_email": "bob@example.com", "set_doc_id": "s1"},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/review/keep_set_as_is",
            json={"user_email": "bob@example.com", "set_doc_id": "s1"},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/greysheet/resolve",
            json={"user_id": "bob@example.com", "coin_id": "c1"},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/greysheet/refresh",
            json={"user_id": "bob@example.com", "coin_id": "c1"},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/wishlist/create-share",
            json={"user_email": "bob@example.com", "items": []},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/wishlist/deals/check",
            json={"user_email": "bob@example.com", "wishlist_items": []},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/identify-world-item",
            data={"country_hint": "Germany"},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/analyze/grade-coin",
            files={"obverse": dummy_png, "reverse": dummy_png},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/variety/detect",
            json={"base64_image": "AAAA"},
        ).status_code
        == 401
    )
    assert client.get("/support/expire-grants").status_code == 401


def test_2_idor_alice_targeting_bob_returns_403():
    app.dependency_overrides[get_current_user] = _alice
    client = TestClient(app, raise_server_exceptions=False)

    assert (
        client.post(
            "/api/review/break_up_set",
            json={"user_email": "bob@example.com", "set_doc_id": "s1"},
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/review/keep_set_as_is",
            json={"user_email": "bob@example.com", "set_doc_id": "s1"},
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/greysheet/refresh",
            json={"user_id": "bob@example.com", "coin_id": "c1"},
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/greysheet/resolve",
            json={"user_id": "bob@example.com", "coin_id": "c1"},
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/wishlist/create-share",
            json={"user_email": "bob@example.com", "items": []},
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/wishlist/deals/check",
            json={"user_email": "bob@example.com", "wishlist_items": []},
        ).status_code
        == 403
    )
    # Greysheet resolve rejects coin_id without user_id (400)
    assert (
        client.post(
            "/api/greysheet/resolve",
            json={"coin_id": "c1"},
        ).status_code
        == 400
    )


def test_3_admin_impersonation_targeting_bob_succeeds():
    app.dependency_overrides[get_current_user] = _admin
    client = TestClient(app, raise_server_exceptions=False)

    mock_set_snap = MagicMock()
    mock_set_snap.exists = True
    mock_set_snap.to_dict.return_value = {"Theme/Subject": "Test Set"}

    with patch.object(backend_main, "db") as mock_db:
        mock_user_ref = mock_db.collection.return_value.document.return_value
        mock_user_ref.collection.return_value.document.return_value.get.return_value = (
            mock_set_snap
        )

        resp_keep = client.post(
            "/api/review/keep_set_as_is",
            json={"user_email": "bob@example.com", "set_doc_id": "s1"},
        )
        assert resp_keep.status_code == 200
        mock_db.collection.return_value.document.assert_any_call("bob@example.com")

        resp_share = client.post(
            "/api/wishlist/create-share",
            json={"user_email": "bob@example.com", "items": [{"title": "Morgan"}]},
        )
        assert resp_share.status_code == 200
        written = mock_db.collection.return_value.document.return_value.set.call_args[0][0]
        assert written["owner_email"] == "bob@example.com"


def test_4_support_expire_grants_cron_and_admin_gating(monkeypatch):
    client = TestClient(app, raise_server_exceptions=False)

    # Unset CRON_SECRET + empty header -> fail closed (401)
    assert (
        client.get("/support/expire-grants", headers={"X-Cron-Secret": ""}).status_code
        == 401
    )

    # Configured CRON_SECRET: wrong secret -> 401, matching secret -> 200
    monkeypatch.setenv("CRON_SECRET", "super-secret-cron-key")
    assert (
        client.get(
            "/support/expire-grants", headers={"X-Cron-Secret": "wrong-key"}
        ).status_code
        == 401
    )

    mock_db = MagicMock()
    mock_db.collection.return_value.where.return_value.stream.return_value = []
    with patch("routes.support_routes._get_db", return_value=mock_db):
        resp_cron = client.get(
            "/support/expire-grants",
            headers={"X-Cron-Secret": "super-secret-cron-key"},
        )
        assert resp_cron.status_code == 200
        assert resp_cron.json() == {"expired": 0}

        # Non-admin Bearer token -> 403; Admin Bearer token -> 200
        with patch(
            "routes.support_routes.firebase_admin.auth.verify_id_token",
            return_value={"uid": "u1", "admin": False},
        ):
            assert (
                client.get(
                    "/support/expire-grants",
                    headers={"Authorization": "Bearer user_tok"},
                ).status_code
                == 403
            )

        with patch(
            "routes.support_routes.firebase_admin.auth.verify_id_token",
            return_value={"uid": "admin1", "admin": True},
        ):
            resp_admin = client.get(
                "/support/expire-grants",
                headers={"Authorization": "Bearer admin_tok"},
            )
            assert resp_admin.status_code == 200


def test_5_verify_firebase_bearer_token_ignores_query_param_token():
    fake_req_query = MagicMock()
    fake_req_query.headers = {}
    fake_req_query.query_params = {"token": "leaked_query_jwt"}

    with patch.object(
        deps.firebase_auth, "verify_id_token", return_value={"uid": "u1"}
    ) as mock_verify:
        assert deps.verify_firebase_bearer_token(fake_req_query) is None
        mock_verify.assert_not_called()

        fake_req_header = MagicMock()
        fake_req_header.headers = {"Authorization": "Bearer header_jwt"}
        fake_req_header.query_params = {}
        assert deps.verify_firebase_bearer_token(fake_req_header) == {"uid": "u1"}
        mock_verify.assert_called_once_with("header_jwt")


def test_6_shared_put_signed_url_iam_fallback_and_import_basename_sanitization():
    mock_storage = MagicMock()
    mock_blob = MagicMock()
    mock_blob.generate_signed_url.return_value = "https://storage.googleapis.com/put-ok"
    mock_storage.bucket.return_value.blob.return_value = mock_blob
    fake_creds = MagicMock(spec=["refresh", "service_account_email", "token"])
    fake_creds.service_account_email = "sa@proj.iam.gserviceaccount.com"
    fake_creds.token = "tok_put"
    mock_storage._credentials = fake_creds

    url = generate_v4_signed_url(
        mock_storage,
        "test-bucket",
        "uploads/u1/item.jpg",
        expiry_minutes=15,
        method="PUT",
        content_type="image/jpeg",
    )
    assert url == "https://storage.googleapis.com/put-ok"
    fake_creds.refresh.assert_called_once()
    kwargs = mock_blob.generate_signed_url.call_args.kwargs
    assert kwargs["method"] == "PUT"
    assert kwargs["content_type"] == "image/jpeg"
    assert kwargs["service_account_email"] == "sa@proj.iam.gserviceaccount.com"
    assert kwargs["access_token"] == "tok_put"

    # Import route path traversal sanitization
    app.dependency_overrides[get_current_user] = _alice
    client = TestClient(app, raise_server_exceptions=False)
    with patch("routes.import_routes.storage_client", mock_storage):
        resp = client.post(
            "/api/v1/import/get_upload_url",
            json={"filename": "../../etc/passwd", "content_type": "text/csv"},
        )
    assert resp.status_code == 200
    gcs_uri = resp.json()["gcs_uri"]
    assert ".." not in gcs_uri
    assert "/etc/" not in gcs_uri
    assert gcs_uri.endswith("_passwd")
