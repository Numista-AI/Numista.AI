"""
numista_backend/tests/test_coin_image_privacy.py
----------------------------------------------
Security and privacy tests for Task 6:
- /api/coin_crop owner-only hardening, strict admin bool + audit log,
  prod dev_guest disablement, bucket allowlist + owner-prefix check,
  URL-encoding/traversal rejection, fallback sanitization, generic 500 errors.
- /api/grade_review/queue deterministic assignment upsert & cross-user redaction.
- /api/grade_review/image/{review_id} opaque proxy, EXIF stripping, uniform 404.
"""

import base64
import datetime
import io
import logging
from datetime import timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from main import app
from routes.deps import get_current_user


@pytest.fixture(autouse=True)
def clean_deps():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def _make_jpeg_with_exif(width: int = 200, height: int = 200) -> bytes:
    img = Image.new("RGB", (width, height), color=(180, 140, 90))
    exif = Image.Exif()
    exif[271] = "SecretCameraBrand"  # Make tag
    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif.tobytes())
    return buf.getvalue()


def _mock_storage(img_bytes: bytes, size_override: int | None = None):
    mock_storage = MagicMock()
    mock_blob = MagicMock()
    mock_blob.size = size_override if size_override is not None else len(img_bytes)
    mock_blob.download_as_bytes.return_value = img_bytes
    mock_storage.bucket.return_value.blob.return_value = mock_blob
    return mock_storage


def _user_a():
    return {"uid": "uid_a", "email": "user_a@example.com", "admin": False}


def _user_b():
    return {"uid": "uid_b", "email": "user_b@example.com", "admin": False}


def test_1_owner_coin_crop_uses_token_owner_key():
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    img_bytes = _make_jpeg_with_exif()
    mock_storage = _mock_storage(img_bytes)

    coin_doc = MagicMock()
    coin_doc.exists = True
    coin_doc.to_dict.return_value = {
        "image_url_obverse": "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/users/user_a@example.com/binder_scans/s1/page_00.jpg",
        "slot_bbox": {"x_pct": 0.1, "y_pct": 0.1, "w_pct": 0.4, "h_pct": 0.4},
    }

    with patch("main.db") as mock_db, patch("routes.deps.storage_client", mock_storage):
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = coin_doc
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/api/coin_crop?coin_id=c1&user_email=%20USER_A@EXAMPLE.COM%20")

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["full_page"] is False
    assert "image_url" not in data
    mock_db.collection.return_value.document.assert_called_with("user_a@example.com")


def test_2_non_admin_other_user_returns_403():
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/api/coin_crop?coin_id=c1&user_email=user_b@example.com")
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Forbidden"


def test_3_admin_string_rejected_bool_allowed_and_logged(caplog):
    # String "true" must NOT grant admin access
    app.dependency_overrides[get_current_user] = lambda: {
        "uid": "uid_x",
        "email": "user_a@example.com",
        "admin": "true",
    }
    client = TestClient(app, raise_server_exceptions=False)
    resp_str = client.get("/api/coin_crop?coin_id=c1&user_email=user_b@example.com")
    assert resp_str.status_code == 403

    # Strict bool True succeeds and emits WARNING audit log
    app.dependency_overrides[get_current_user] = lambda: {
        "uid": "admin_uid",
        "email": "admin@numista.ai",
        "admin": True,
    }
    img_bytes = _make_jpeg_with_exif()
    mock_storage = _mock_storage(img_bytes)
    coin_doc = MagicMock()
    coin_doc.exists = True
    coin_doc.to_dict.return_value = {
        "image_url_obverse": "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/users/user_b@example.com/binder_scans/s1/page_00.jpg",
        "slot_bbox": {"x_pct": 0.1, "y_pct": 0.1, "w_pct": 0.4, "h_pct": 0.4},
    }
    with patch("main.db") as mock_db, patch("routes.deps.storage_client", mock_storage), caplog.at_level(logging.WARNING):
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = coin_doc
        resp_bool = client.get("/api/coin_crop?coin_id=c1&user_email=user_b@example.com")

    assert resp_bool.status_code == 200
    assert any("coin_crop admin access" in rec.message for rec in caplog.records)


def test_4_dev_guest_bypass_disabled_in_prod(monkeypatch):
    monkeypatch.setenv("ALLOW_UNAUTHENTICATED", "1")
    monkeypatch.setenv("K_SERVICE", "numista-backend-prod")
    app.dependency_overrides[get_current_user] = lambda: {
        "uid": "dev_guest_uid",
        "email": "dev_guest@numista.ai",
        "admin": False,
    }
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/api/coin_crop?coin_id=c1&user_email=user_b@example.com")
    assert resp.status_code == 403


def test_5_bucket_allowlist_and_uid_plus_email_owner_prefixes():
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    img_bytes = _make_jpeg_with_exif()
    mock_storage = _mock_storage(img_bytes)
    client = TestClient(app, raise_server_exceptions=False)

    # Disallowed bucket -> 403
    bad_bucket_doc = MagicMock()
    bad_bucket_doc.exists = True
    bad_bucket_doc.to_dict.return_value = {
        "image_url_obverse": "https://storage.googleapis.com/evil-bucket/users/user_a@example.com/a.jpg",
    }
    with patch("main.db") as mock_db, patch("routes.deps.storage_client", mock_storage):
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = bad_bucket_doc
        assert client.get("/api/coin_crop?coin_id=c1&user_email=user_a@example.com").status_code == 403

    # Wrong owner prefix -> 403
    other_owner_doc = MagicMock()
    other_owner_doc.exists = True
    other_owner_doc.to_dict.return_value = {
        "image_url_obverse": "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/users/uid_b/a.jpg",
    }
    with patch("main.db") as mock_db, patch("routes.deps.storage_client", mock_storage):
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = other_owner_doc
        assert client.get("/api/coin_crop?coin_id=c1&user_email=user_a@example.com").status_code == 403

    # Both users/{uid_a}/... and users/{email}/... succeed (200)
    for owner_seg in ("uid_a", "user_a@example.com"):
        ok_doc = MagicMock()
        ok_doc.exists = True
        ok_doc.to_dict.return_value = {
            "image_url_obverse": f"https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2F{owner_seg}%2Fcoins%2Fc1%2Fobv.jpg?alt=media",
        }
        with patch("main.db") as mock_db, patch("routes.deps.storage_client", mock_storage):
            mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = ok_doc
            resp = client.get("/api/coin_crop?coin_id=c1&user_email=user_a@example.com")
            assert resp.status_code == 200


@pytest.mark.parametrize(
    "bad_url",
    [
        "https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fuser_a@example.com%2F..%2Fuser_b@example.com%2Fobv.jpg",
        "https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%252Fuser_a@example.com%252Fobv.jpg",
        "https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fuser_a@example.com%c0%af..%c0%afuser_b%2Fobv.jpg",
    ],
)
def test_6_url_encoding_and_traversal_rejected(bad_url):
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    coin_doc = MagicMock()
    coin_doc.exists = True
    coin_doc.to_dict.return_value = {"image_url_obverse": bad_url}
    with patch("main.db") as mock_db:
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = coin_doc
        resp = client.get("/api/coin_crop?coin_id=c1&user_email=user_a@example.com")
    assert resp.status_code == 403


def test_7_fallback_returns_bytes_no_url_no_bucket_no_email():
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    img_bytes = _make_jpeg_with_exif()
    mock_storage = _mock_storage(img_bytes)
    coin_doc = MagicMock()
    coin_doc.exists = True
    coin_doc.to_dict.return_value = {
        "image_url_obverse": "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/users/user_a@example.com/binder_scans/s1/page_00.jpg",
        "slot_bbox": {},
    }
    with patch("main.db") as mock_db, patch("routes.deps.storage_client", mock_storage):
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = coin_doc
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/api/coin_crop?coin_id=c1&user_email=user_a@example.com")

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["full_page"] is True
    assert "image_url" not in data
    assert "crop_b64" in data and len(data["crop_b64"]) > 20
    assert "user_a@example.com" not in resp.text
    assert "numista-uploads-studio-9101802118-8c9a8" not in resp.text


def test_8_forced_exception_returns_generic_500():
    app.dependency_overrides[get_current_user] = lambda: _user_a()
    client = TestClient(app, raise_server_exceptions=False)
    with patch("main.db") as mock_db:
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.side_effect = RuntimeError(
            "secret-internal-bucket-details"
        )
        resp = client.get("/api/coin_crop?coin_id=c1&user_email=user_a@example.com")
    assert resp.status_code == 500
    assert resp.json()["detail"] == "Could not load image."
    assert "secret-internal-bucket-details" not in resp.text


def test_9_reviewer_image_proxy_strips_exif_and_returns_uniform_404():
    app.dependency_overrides[get_current_user] = lambda: _user_b()
    img_bytes = _make_jpeg_with_exif()
    mock_storage = _mock_storage(img_bytes)
    client = TestClient(app, raise_server_exceptions=False)

    valid_snap = MagicMock()
    valid_snap.exists = True
    valid_snap.to_dict.return_value = {
        "reviewer_uid": "uid_b",
        "owner_key": "user_a@example.com",
        "owner_uid": "uid_a",
        "coin_id": "c1",
        "obverse_blob": "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/users/uid_a/obv.jpg",
        "reverse_blob": "",
        "slot_bbox": {},
        "expires_at": datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=1),
    }

    with patch("routes.grade_review_routes.db") as mock_db, patch(
        "routes.grade_review_routes.storage_client", mock_storage
    ), patch("routes.grade_review_routes.check_and_increment_rate_cap"):
        mock_db.collection.return_value.document.return_value.get.return_value = valid_snap
        resp = client.get("/api/grade_review/image/rev123?side=obverse")

    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/jpeg"
    assert resp.headers["cache-control"] == "private, no-store"
    out_img = Image.open(io.BytesIO(resp.content))
    assert len(out_img.getexif()) == 0

    # Wrong user -> 404
    wrong_user_snap = MagicMock()
    wrong_user_snap.exists = True
    wrong_user_snap.to_dict.return_value = {
        **valid_snap.to_dict.return_value,
        "reviewer_uid": "uid_other",
    }
    # Expired -> 404
    expired_snap = MagicMock()
    expired_snap.exists = True
    expired_snap.to_dict.return_value = {
        **valid_snap.to_dict.return_value,
        "expires_at": datetime.datetime.now(timezone.utc) - datetime.timedelta(minutes=5),
    }
    # Unknown -> 404
    missing_snap = MagicMock()
    missing_snap.exists = False

    for snap in (wrong_user_snap, expired_snap, missing_snap):
        with patch("routes.grade_review_routes.db") as mock_db, patch(
            "routes.grade_review_routes.check_and_increment_rate_cap"
        ):
            mock_db.collection.return_value.document.return_value.get.return_value = snap
            r = client.get("/api/grade_review/image/rev123?side=obverse")
            assert r.status_code == 404
            assert r.json()["detail"] == "Not found"


def test_10_queue_deterministic_upsert_and_cross_user_redaction():
    app.dependency_overrides[get_current_user] = lambda: _user_b()
    client = TestClient(app, raise_server_exceptions=False)

    cross_doc = MagicMock()
    cross_doc.id = "secret_coin_99"
    cross_doc.to_dict.return_value = {
        "user_email": "secret_owner@example.com",
        "uid": "uid_secret",
        "Year": "1921",
        "Mint Mark": "P",
        "Denomination": "Dollar",
        "Program/Series": "Morgan",
        "Condition": "MS63",
        "confidence_score": 0.62,
        "image_url_obverse": "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/users/uid_secret/obv.jpg",
        "image_url_reverse": "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/users/uid_secret/rev.jpg",
    }

    written_doc_ids = []

    def make_db():
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_query.limit.return_value.stream.return_value = [cross_doc]
        mock_db.collection.return_value.document.return_value.collection.return_value.where.return_value = mock_query

        def record_assignment(doc_id):
            written_doc_ids.append(doc_id)
            return MagicMock()

        mock_db.collection.return_value.document.side_effect = (
            lambda doc_id: record_assignment(doc_id)
            if doc_id != "user_b@example.com"
            else mock_db.collection.return_value.document.return_value
        )
        return mock_db

    with patch("routes.grade_review_routes.db") as mock_db:
        mock_query = MagicMock()
        mock_query.limit.return_value.stream.return_value = [cross_doc]
        users_doc = MagicMock()
        users_doc.collection.return_value.where.return_value = mock_query

        def col_router(name):
            c = MagicMock()
            if name == "users":
                c.document.return_value = users_doc
            elif name == "grade_review_assignments":
                def assign_doc(rid):
                    written_doc_ids.append(rid)
                    return MagicMock()
                c.document.side_effect = assign_doc
            return c

        mock_db.collection.side_effect = col_router
        r1 = client.get("/api/grade_review/queue")
        r2 = client.get("/api/grade_review/queue")

    assert r1.status_code == 200
    assert r2.status_code == 200
    item1 = r1.json()["results"][0]
    item2 = r2.json()["results"][0]
    assert item1["review_id"] == item2["review_id"]
    assert len(set(written_doc_ids)) == 1
    assert item1["has_reverse"] is True
    for forbidden_key in ("user_email", "coin_id", "image_url_obverse", "image_url_reverse"):
        assert forbidden_key not in item1
    assert "secret_owner@example.com" not in r1.text
    assert "secret_coin_99" not in r1.text


def test_f7_max_image_pixels_bounded():
    from services import coin_image_service

    assert coin_image_service.MAX_IMAGE_PIXELS == 25_000_000
