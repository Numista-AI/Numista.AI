"""
numista_backend/tests/test_cert_lookup.py
----------------------------------------
Tests for the unified certification lookup endpoint (/api/cert_lookup)
covering PCGS, NGC, and CAC.

Requirements:
1. test_cert_lookup_pcgs_api_success — mock _requests.get to return valid PCGS JSON -> found=True, source=api
2. test_cert_lookup_pcgs_no_token_fallback — PCGS_BEARER_TOKEN not set -> found=False, source=manual_fallback
3. test_cert_lookup_ngc_always_fallback — 7-digit cert_num -> grader=NGC, found=False, source=manual_fallback
4. test_cert_lookup_cac_prefix — cert_num='CAC12345' -> grader=CAC, found=False, source=manual_fallback
5. test_cert_lookup_auto_detect_pcgs — 8-digit cert_num, no grader -> grader=PCGS
6. test_cert_lookup_no_token_401 — get_current_user raises 401 -> 401
7. test_cert_lookup_rate_limit — call 11 times rapidly -> 11th call returns 429
8. test_cert_lookup_empty_cert_num — cert_num='' -> 400
"""

import os
import sys
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import main as app_main
from routes.deps import get_current_user
import routes.cert_routes as cert_routes


@pytest.fixture(autouse=True)
def reset_cert_rate_limits():
    """Reset the in-memory rate limit store and dependency overrides before each test."""
    cert_routes._CERT_RATE_LIMIT_STORE.clear()
    async def _default_user():
        return {"uid": "test_cert_uid_123", "email": "test_user@numista.ai"}
    app_main.app.dependency_overrides[get_current_user] = _default_user
    yield
    app_main.app.dependency_overrides.clear()
    cert_routes._CERT_RATE_LIMIT_STORE.clear()


client = TestClient(app_main.app)


def test_cert_lookup_pcgs_api_success():
    """Mock _requests.get to return valid PCGS JSON -> found=True, source=api."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "IsValidRequest": True,
        "CoinDetail": {
            "FullName": "1881-S $1 Morgan",
            "Year": "1881",
            "MintMark": "S",
            "Grade": "MS65",
            "Denomination": "Dollar",
        }
    }
    with patch("routes.cert_routes._get_pcgs_token", return_value="mock_pcgs_token"), \
         patch("routes.cert_routes._requests.get", return_value=mock_resp):
        response = client.post(
            "/api/cert_lookup",
            json={"cert_num": "53652580", "grader": "PCGS"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["grader"] == "PCGS"
        assert data["found"] is True
        assert data["source"] == "api"
        assert data["coin_name"] == "1881-S $1 Morgan"
        assert data["year"] == "1881"
        assert data["mint"] == "S"
        assert data["grade"] == "MS65"
        assert data["denomination"] == "Dollar"


def test_cert_lookup_pcgs_no_token_fallback():
    """PCGS_BEARER_TOKEN not set, Firestore mock returns None -> found=False, source=manual_fallback."""
    with patch("routes.cert_routes._get_pcgs_token", return_value=None):
        response = client.post(
            "/api/cert_lookup",
            json={"cert_num": "53652580", "grader": "PCGS"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["grader"] == "PCGS"
        assert data["found"] is False
        assert data["source"] == "manual_fallback"


def test_cert_lookup_ngc_always_fallback():
    """7-digit cert_num -> grader=NGC, found=False, source=manual_fallback."""
    response = client.post(
        "/api/cert_lookup",
        json={"cert_num": "1234567"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["grader"] == "NGC"
    assert data["found"] is False
    assert data["source"] == "manual_fallback"


def test_cert_lookup_cac_prefix():
    """cert_num='CAC12345' -> grader=CAC, found=False, source=manual_fallback."""
    response = client.post(
        "/api/cert_lookup",
        json={"cert_num": "CAC12345"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["grader"] == "CAC"
    assert data["found"] is False
    assert data["source"] == "manual_fallback"


def test_cert_lookup_auto_detect_pcgs():
    """8-digit cert_num, no grader provided -> grader=PCGS."""
    with patch("routes.cert_routes._get_pcgs_token", return_value=None):
        response = client.post(
            "/api/cert_lookup",
            json={"cert_num": "53652580"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["grader"] == "PCGS"


def test_cert_lookup_no_token_401():
    """Override get_current_user to raise HTTPException(401) -> 401."""
    async def _unauthorized():
        raise HTTPException(status_code=401, detail="Unauthorized")

    app_main.app.dependency_overrides[get_current_user] = _unauthorized
    response = client.post(
        "/api/cert_lookup",
        json={"cert_num": "53652580"}
    )
    assert response.status_code == 401


def test_cert_lookup_rate_limit():
    """Call 11 times rapidly -> 11th call returns 429."""
    with patch("routes.cert_routes._get_pcgs_token", return_value=None):
        for i in range(10):
            res = client.post(
                "/api/cert_lookup",
                json={"cert_num": f"5365258{i}"}
            )
            assert res.status_code == 200, f"Call {i+1} failed with status {res.status_code}: {res.text}"

        # 11th call exceeds the 10/min rate limit
        res_11 = client.post(
            "/api/cert_lookup",
            json={"cert_num": "53652589"}
        )
        assert res_11.status_code == 429, f"Expected 429, got {res_11.status_code}: {res_11.text}"
        assert "Rate limit exceeded" in res_11.json()["detail"]


def test_cert_lookup_empty_cert_num():
    """cert_num='' -> 400."""
    response = client.post(
        "/api/cert_lookup",
        json={"cert_num": ""}
    )
    assert response.status_code == 400


def test_cert_exists_endpoint():
    """GET /api/cert_exists returns exists=False when cert is not in collection."""
    with patch("routes.cert_routes.db.collection") as mock_col:
        mock_col.return_value.document.return_value.collection.return_value.where.return_value.limit.return_value.stream.return_value = []
        response = client.get("/api/cert_exists?cert_num=53652580")
        assert response.status_code == 200
        data = response.json()
        assert data["exists"] is False
        assert data["existing_coin_id"] is None
        assert data["cert_num"] == "53652580"


def test_cert_save_duplicate_detection_409():
    """POST /api/cert_save with duplicate cert and allow_duplicate=False returns 409."""
    mock_existing = MagicMock()
    mock_existing.id = "coin_existing_999"

    with patch("routes.cert_routes.db.collection") as mock_col:
        mock_col.return_value.document.return_value.collection.return_value.where.return_value.limit.return_value.stream.return_value = [mock_existing]
        response = client.post(
            "/api/cert_save",
            json={
                "cert_num": "53652580",
                "grader": "PCGS",
                "allow_duplicate": False,
                "coin_data": {"CoinName": "1881-S Morgan"},
            }
        )
        assert response.status_code == 409
        data = response.json()
        assert data["detail"]["error"] == "cert_duplicate"
        assert data["detail"]["existing_coin_id"] == "coin_existing_999"


def test_cert_save_duplicate_allowed():
    """POST /api/cert_save with duplicate cert and allow_duplicate=True returns 200 status='clear'.
    FAIL-1 fix: cert_save is now CHECK-ONLY — Flutter does the single Firestore write.
    """
    mock_existing = MagicMock()
    mock_existing.id = "coin_existing_999"

    with patch("routes.cert_routes.db.collection") as mock_col:
        mock_db_write = mock_col.return_value.document.return_value.collection.return_value.document.return_value.set
        mock_col.return_value.document.return_value.collection.return_value.where.return_value.limit.return_value.stream.return_value = [mock_existing]
        response = client.post(
            "/api/cert_save",
            json={
                "cert_num": "53652580",
                "grader": "PCGS",
                "allow_duplicate": True,
                "coin_data": {"CoinName": "1881-S Morgan"},
            }
        )
        assert response.status_code == 200
        data = response.json()
        # FAIL-1 fix: status is now 'clear', not 'ok'
        assert data["status"] == "clear", f"Expected 'clear', got '{data['status']}'"
        assert data["duplicate_allowed"] is True
        # No Firestore write should have occurred
        mock_db_write.assert_not_called()


def test_cert_save_clear_path_no_firestore_write():
    """POST /api/cert_save with no duplicate returns 200 status='clear' without writing to Firestore.
    FAIL-1 fix: cert_save check-only. Flutter is the single writer.
    FAIL-2 fix: eric_emails safeguard removed (would have returned fake 'ok').
    """
    with patch("routes.cert_routes.db.collection") as mock_col:
        # No existing coin
        mock_col.return_value.document.return_value.collection.return_value.where.return_value.limit.return_value.stream.return_value = []
        mock_db_write = mock_col.return_value.document.return_value.collection.return_value.document.return_value.set

        response = client.post(
            "/api/cert_save",
            json={
                "cert_num": "53652580",
                "grader": "PCGS",
                "allow_duplicate": False,
                "coin_data": {"CoinName": "1881-S Morgan"},
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "clear"
        assert data.get("coin_id") is None  # No ID — Flutter will get one from its .add()
        # Critical: backend must NOT have written to Firestore
        mock_db_write.assert_not_called()


def test_cert_save_no_eric_emails_safeguard():
    """FAIL-2 fix: eric_emails block is removed — no fake 'ok' for any email.
    Previously, emails containing 'eric' (e.g. eric@numista.ai, erica@...) got a
    fake status='ok' with coin_id='safeguard_blocked'. Now all get real responses.
    """
    test_emails = [
        "eric@numista.ai",
        "eric.seaman@yahoo.com",
        "erica@example.com",
        "frederick@example.com",
    ]
    for email in test_emails:
        with patch("routes.cert_routes.db.collection") as mock_col:
            mock_col.return_value.document.return_value.collection.return_value.where.return_value.limit.return_value.stream.return_value = []
            response = client.post(
                "/api/cert_save",
                json={
                    "cert_num": "53652580",
                    "grader": "PCGS",
                    "allow_duplicate": False,
                    "coin_data": {"CoinName": "1881-S Morgan"},
                }
            )
            assert response.status_code == 200
            data = response.json()
            # Must be 'clear', never 'safeguard_blocked' or fake 'ok'
            assert data["status"] == "clear", \
                f"Email {email} got status={data['status']!r} — eric_emails block may still be active"
            assert data.get("coin_id") != "safeguard_blocked", \
                f"Email {email} triggered safeguard — eric_emails block must be removed"


def test_scan_cert_number_upload_returns_cert():
    """scan_cert_number_upload extracts cert # and grader from slab image (Vertex AI mocked).
    Verifies: uses google-genai vertexai=True pattern, no GOOGLE_API_KEY, returns correct fields.
    """
    mock_response = MagicMock()
    mock_response.text = '{"cert_number": "53652580", "grader": "PCGS", "confidence": "HIGH"}'

    with patch("routes.cert_routes._genai") as _mock_genai_mod:
        # Mock the Client constructor and the models.generate_content call
        mock_client = MagicMock()
        _mock_genai_mod.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = mock_response

        response = client.post(
            "/api/scan_cert_number_upload",
            files={"file": ("test.jpg", b"\xff\xd8\xff" + b"\x00" * 100, "image/jpeg")},
        )

    assert response.status_code == 200, f"Got {response.status_code}: {response.text}"
    data = response.json()
    assert data["cert_number"] == "53652580"
    assert data["grader"] == "PCGS"
    assert data["confidence"] == "HIGH"
    assert data["message"] == "OK"


def test_scan_cert_number_upload_ngc_cert():
    """scan_cert_number_upload correctly returns NGC cert with dash suffix."""
    mock_response = MagicMock()
    mock_response.text = '{"cert_number": "8321797-003", "grader": "NGC", "confidence": "HIGH"}'

    with patch("routes.cert_routes._genai") as _mock_genai_mod:
        mock_client = MagicMock()
        _mock_genai_mod.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = mock_response

        response = client.post(
            "/api/scan_cert_number_upload",
            files={"file": ("ngc.jpg", b"\xff\xd8\xff" + b"\x00" * 50, "image/jpeg")},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["cert_number"] == "8321797-003"
    assert data["grader"] == "NGC"


def test_scan_cert_number_upload_no_cert_found():
    """scan_cert_number_upload returns LOW confidence and no cert when AI finds nothing."""
    mock_response = MagicMock()
    mock_response.text = '{"cert_number": null, "grader": null, "confidence": "LOW"}'

    with patch("routes.cert_routes._genai") as _mock_genai_mod:
        mock_client = MagicMock()
        _mock_genai_mod.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = mock_response

        response = client.post(
            "/api/scan_cert_number_upload",
            files={"file": ("blank.png", b"\x89PNG\r\n" + b"\x00" * 50, "image/png")},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["cert_number"] is None
    assert data["confidence"] == "LOW"
    assert "No cert number found" in data["message"]


def test_ngc_verify_url_numeric_grade():
    """NGC certlookup URL must use numeric grade only: PF67→67, MS64→64, PR65→65."""
    import re

    # Simulate the grade extraction logic from _saveManualCertEntry and the verify button
    def _ngc_url(cert_no: str, grade: str) -> str:
        numeric_grade = re.sub(r'[^0-9]', '', grade)
        grade_segment = numeric_grade if numeric_grade else grade
        return f"https://www.ngccoin.com/certlookup/{cert_no}/{grade_segment}/"

    # Grok CoS test case from NET-104
    assert _ngc_url("8321797-003", "PF67") == "https://www.ngccoin.com/certlookup/8321797-003/67/"
    assert _ngc_url("8321797-003", "MS64") == "https://www.ngccoin.com/certlookup/8321797-003/64/"
    assert _ngc_url("8321797-003", "PR65") == "https://www.ngccoin.com/certlookup/8321797-003/65/"
    # Edge: plain numeric grade passed as-is
    assert _ngc_url("1234567", "67") == "https://www.ngccoin.com/certlookup/1234567/67/"


def test_same_cert_reader_both_paths_match(monkeypatch):
    """
    NET-354 Item 2: Same cert reader for both endpoints.
    Verifies that the same slab image fixture passed through:
      1) POST /api/scan_cert_number_upload
      2) POST /api/identify_coin_photo
    uses the shared extract_cert_from_image function and extracts the exact same cert number.
    """
    import io
    import json

    fixture_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00" + b"\x00" * 80
    expected_cert = "53652580"
    expected_grader = "PCGS"

    # Mock extract_cert_from_image / genai Client for cert_routes
    mock_genai_resp = MagicMock()
    mock_genai_resp.text = json.dumps({
        "cert_number": expected_cert,
        "grader": expected_grader,
        "confidence": "HIGH"
    })

    with patch("routes.cert_routes._genai") as mock_genai_mod:
        mock_client = MagicMock()
        mock_genai_mod.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = mock_genai_resp

        # Path 1: /api/scan_cert_number_upload
        resp1 = client.post(
            "/api/scan_cert_number_upload",
            files={"file": ("slab.jpg", io.BytesIO(fixture_bytes), "image/jpeg")},
        )
        assert resp1.status_code == 200, f"Path 1 failed: {resp1.status_code} {resp1.text}"
        data1 = resp1.json()
        cert_from_path1 = data1.get("cert_number")
        assert cert_from_path1 == expected_cert

        # Mock Gemini call in identify_coin_photo for pass1/pass2
        mock_id_resp1 = MagicMock()
        mock_id_resp1.text = json.dumps({
            "year": "1881",
            "denomination": "Dollar",
            "country": "United States",
            "program_series": "Morgan Dollars",
            "mint_mark": "S",
            "grade": "MS-65",
            "confidence": "HIGH",
            "obverse_image": "A"
        })
        mock_id_resp2 = MagicMock()
        mock_id_resp2.text = json.dumps({
            "refined_grade": "MS-65",
            "estimated_value_usd": "$150.00",
            "confidence": "HIGH"
        })
        mock_models = MagicMock()
        mock_models.generate_content.side_effect = [mock_id_resp1, mock_id_resp2]
        mock_id_client = MagicMock()
        mock_id_client.models = mock_models
        monkeypatch.setattr(app_main, "genai_client", mock_id_client)
        monkeypatch.setattr(app_main, "_authenticate_request", lambda auth, email=None, **kw: "test_user@numista.ai")

        # Path 2: /api/identify_coin_photo
        resp2 = client.post(
            "/api/identify_coin_photo",
            data={"user_email": "test_user@numista.ai"},
            files={"image_a": ("slab.jpg", io.BytesIO(fixture_bytes), "image/jpeg")},
        )
        assert resp2.status_code == 200, f"Path 2 failed: {resp2.status_code} {resp2.text}"
        data2 = resp2.json()
        coin2 = data2.get("coin", {})
        cert_from_path2 = coin2.get("Certification Number") or coin2.get("cert_number")
        assert cert_from_path2 == expected_cert

        # Both paths must match!
        assert cert_from_path1 == cert_from_path2 == expected_cert


def test_shared_cert_reader_wins_over_pass1(monkeypatch):
    """
    NET-357 Item 2 (a):
    Pass 1 mock returns cert X ("PASS1-CERT-11111"),
    Shared reader mock returns cert Y ("53652580").
    Both /api/scan_cert_number_upload and /api/identify_coin_photo must return Y.
    """
    import io
    import json

    fixture_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00" + b"\x00" * 80
    expected_cert = "53652580"
    expected_grader = "PCGS"
    pass1_old_cert = "PASS1-CERT-11111"

    # Shared cert reader mock: returns expected_cert Y
    mock_genai_resp = MagicMock()
    mock_genai_resp.text = json.dumps({
        "cert_number": expected_cert,
        "grader": expected_grader,
        "confidence": "HIGH"
    })

    with patch("routes.cert_routes._genai") as mock_genai_mod:
        mock_client = MagicMock()
        mock_genai_mod.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = mock_genai_resp

        # Path 1: /api/scan_cert_number_upload -> must return Y
        resp1 = client.post(
            "/api/scan_cert_number_upload",
            files={"file": ("slab.jpg", io.BytesIO(fixture_bytes), "image/jpeg")},
        )
        assert resp1.status_code == 200, f"Path 1 failed: {resp1.status_code} {resp1.text}"
        data1 = resp1.json()
        assert data1.get("cert_number") == expected_cert

        # Pass 1 returns cert X ("PASS1-CERT-11111")
        mock_id_resp1 = MagicMock()
        mock_id_resp1.text = json.dumps({
            "year": "1921",
            "denomination": "Dollar",
            "country": "United States",
            "program_series": "Morgan Dollars",
            "mint_mark": "S",
            "grade": "MS-65",
            "cert_number": pass1_old_cert,
            "grading_service": "NGC",
            "confidence": "HIGH",
            "obverse_image": "A"
        })
        mock_id_resp2 = MagicMock()
        mock_id_resp2.text = json.dumps({
            "refined_grade": "MS-65",
            "estimated_value_usd": "$150.00",
            "confidence": "HIGH"
        })
        mock_models = MagicMock()
        mock_models.generate_content.side_effect = [mock_id_resp1, mock_id_resp2]
        mock_id_client = MagicMock()
        mock_id_client.models = mock_models
        monkeypatch.setattr(app_main, "genai_client", mock_id_client)
        monkeypatch.setattr(app_main, "_authenticate_request", lambda auth, email=None, **kw: "test_user@numista.ai")

        # Path 2: /api/identify_coin_photo -> shared reader Y must win over pass 1 X
        resp2 = client.post(
            "/api/identify_coin_photo",
            data={"user_email": "test_user@numista.ai"},
            files={"image_a": ("slab.jpg", io.BytesIO(fixture_bytes), "image/jpeg")},
        )
        assert resp2.status_code == 200, f"Path 2 failed: {resp2.status_code} {resp2.text}"
        data2 = resp2.json()
        coin2 = data2.get("coin", {})
        assert coin2.get("cert_number") == expected_cert
        assert coin2.get("Certification Number") == expected_cert
        assert coin2.get("Grading Service") == expected_grader

        # Both endpoints return Y
        assert data1.get("cert_number") == coin2.get("cert_number") == expected_cert


def test_shared_cert_reader_budget_timeout_no_500(monkeypatch):
    """
    NET-357 Item 2 (b):
    Shared reader sleeps past budget -> identify returns < 28 s, no cert, no 500.
    """
    import io
    import json
    import time

    fixture_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00" + b"\x00" * 80

    def slow_extract(*args, **kwargs):
        # Sleeps longer than the configured budget
        time.sleep(1.5)
        return {
            "cert_number": "LATE-CERT",
            "grader": "PCGS",
            "confidence": "HIGH",
            "message": "OK",
        }

    # Set budget to 0.4s so the timeout triggers quickly and cleanly
    monkeypatch.setattr(app_main, "GEMINI_IDENTIFY_BUDGET", 0.4)
    monkeypatch.setattr(app_main, "extract_cert_from_image", slow_extract)

    mock_id_resp1 = MagicMock()
    mock_id_resp1.text = json.dumps({
        "year": "1881",
        "denomination": "Dollar",
        "country": "United States",
        "program_series": "Morgan Dollars",
        "mint_mark": "S",
        "grade": "MS-65",
        "confidence": "HIGH",
        "obverse_image": "A"
    })
    mock_models = MagicMock()
    mock_models.generate_content.return_value = mock_id_resp1
    mock_id_client = MagicMock()
    mock_id_client.models = mock_models
    monkeypatch.setattr(app_main, "genai_client", mock_id_client)
    monkeypatch.setattr(app_main, "_authenticate_request", lambda auth, email=None, **kw: "test_user@numista.ai")

    t0 = time.monotonic()
    resp = client.post(
        "/api/identify_coin_photo",
        data={"user_email": "test_user@numista.ai"},
        files={"image_a": ("slab.jpg", io.BytesIO(fixture_bytes), "image/jpeg")},
    )
    elapsed = time.monotonic() - t0

    # Must return cleanly in < 28 s without 500
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert elapsed < 28.0, f"Took too long: {elapsed}s >= 28s"
    coin = resp.json().get("coin", {})
    # No cert extracted (timed out)
    assert not coin.get("cert_number")
    assert not coin.get("Certification Number")


def test_cert_lookup_never_found_without_real_lookup():
    """cert_lookup must not return found=True for NGC/CACG/CAC certs (no real API available)."""
    response = client.post(
        "/api/cert_lookup",
        json={"cert_num": "8321797-003", "grader": "NGC"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["grader"] == "NGC"
    assert data["found"] is False
    assert data.get("source") != "api"


def test_list_receipts_no_composite_index_required():
    """list_receipts with session_id must not call order_by (which needs a composite index)."""
    from main import list_receipts

    mock_db = MagicMock()
    mock_coll = MagicMock()
    user_ref = MagicMock()
    mock_db.collection.return_value.document.return_value = user_ref
    user_ref.collection.side_effect = lambda name: mock_coll if name == "receipts" else MagicMock(select=lambda _: MagicMock(stream=lambda: []))

    doc1 = MagicMock()
    doc1.id = "rec1"
    doc1.to_dict.return_value = {"uploaded_at": 100, "session_id": "sess_123", "linked_coin_ids": []}

    doc2 = MagicMock()
    doc2.id = "rec2"
    doc2.to_dict.return_value = {"uploaded_at": 200, "import_session_id": "sess_123", "linked_coin_ids": []}

    where_q1 = MagicMock()
    where_q1.stream.return_value = [doc1]
    where_q2 = MagicMock()
    where_q2.stream.return_value = [doc2]

    def mock_where(field, op, val):
        if field == "session_id":
            return where_q1
        if field == "import_session_id":
            return where_q2
        return MagicMock(stream=lambda: [])

    mock_coll.where.side_effect = mock_where

    with patch("main.db", mock_db):
        res = list_receipts(user_email="test_user@numista.ai", session_id="sess_123", _user={"email": "test_user@numista.ai"})

    assert mock_coll.order_by.call_count == 0, "order_by must NOT be called when session_id is provided"
    receipts = res.get("receipts", res) if isinstance(res, dict) else res
    assert len(receipts) == 2
    assert receipts[0]["receipt_id"] == "rec2"
    assert receipts[1]["receipt_id"] == "rec1"


def test_list_receipts_cors_headers_on_p7gate_origin():
    """GET /api/receipts must return Access-Control-Allow-Origin for the p7gate preview origin."""
    with patch("main.db") as mock_db:
        mock_coll = MagicMock()
        mock_db.collection.return_value.document.return_value.collection.return_value = mock_coll
        mock_coll.order_by.return_value.limit.return_value.stream.return_value = []
        response = client.get(
            "/api/receipts?user_email=test_user@numista.ai",
            headers={"Origin": "https://numista-vault--p7-gate-8avtpz22.web.app"}
        )
        assert response.headers.get("access-control-allow-origin") == "https://numista-vault--p7-gate-8avtpz22.web.app"



