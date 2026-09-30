"""
test_scan_service_estate_report.py
----------------------------------
Unit and regression tests for REQ_020 & REQ_023E:
- Strict CORS exact matching (allowed origins pass, evil origins rejected)
- Bearer Auth requirement on /generate_estate_report, /scan_checklist, /initialize_estate_upgrade
- Token-derived UID & strict 403 rejection on body/form UID mismatch
- Request validation & strict state validation (400 on missing or unknown state; no silent fallback)
- Successful PDF generation (200) with correct headers
- Local import verification for collection_inventory in scan_service
"""

import json
import io
import pytest
from unittest.mock import MagicMock, patch

import importlib.util
import sys
import os

scan_service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scan_service"))
if scan_service_dir not in sys.path:
    sys.path.insert(0, scan_service_dir)

_scan_main_file = os.path.join(scan_service_dir, "main.py")
_spec = importlib.util.spec_from_file_location("scan_service_main_mod", _scan_main_file)
scan_main = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(scan_main)

flask_app = scan_main.app
ALLOWED_ORIGINS = scan_main.ALLOWED_ORIGINS


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    scan_main.limiter.enabled = False
    with flask_app.test_client() as c:
        yield c
    scan_main.limiter.enabled = True


def test_collection_inventory_import_ok():
    """Verify collection_inventory imports cleanly in scan_service (Docker COPY fix)."""
    from collection_inventory import expand_collection_inventory, count_coins_and_lots, lot_value
    assert callable(expand_collection_inventory)
    assert callable(count_coins_and_lots)
    assert callable(lot_value)


def test_cors_preflight_options(client):
    """Verify OPTIONS preflight returns 200 with proper CORS headers for allowed origins."""
    for origin in ["https://numista.ai", "https://www.numista.ai", "https://numista-vault.web.app", "http://localhost:8080"]:
        resp = client.open(
            "/generate_estate_report",
            method="OPTIONS",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type, Authorization",
            },
        )
        assert resp.status_code == 200
        assert resp.headers.get("Access-Control-Allow-Origin") == origin
        assert resp.headers.get("Access-Control-Allow-Credentials") == "true"
        allow_methods = resp.headers.get("Access-Control-Allow-Methods", "")
        assert "POST" in allow_methods
        assert "OPTIONS" in allow_methods
        allow_headers = resp.headers.get("Access-Control-Allow-Headers", "")
        assert "Authorization" in allow_headers
        assert "Content-Type" in allow_headers
        expose_headers = resp.headers.get("Access-Control-Expose-Headers", "")
        assert "X-Report-Id" in expose_headers


def test_cors_disallowed_origin_rejected(client):
    """Verify that untrusted and lookalike origins are NOT reflected in CORS headers (M2)."""
    evil_origins = [
        "https://evil.example.com",
        "https://evil-numista.attacker.com",
        "http://localhost.attacker.com",
        "https://notnumista.ai",
    ]
    for evil in evil_origins:
        resp = client.open(
            "/generate_estate_report",
            method="OPTIONS",
            headers={
                "Origin": evil,
                "Access-Control-Request-Method": "POST",
            },
        )
        # OPTIONS returns 403 or does not return Allow-Origin matching the evil domain
        assert resp.headers.get("Access-Control-Allow-Origin") != evil


def test_generate_estate_report_unauthorized(client):
    """Verify 401 when Authorization Bearer token is missing or invalid."""
    # 1. No Authorization header
    resp = client.post(
        "/generate_estate_report",
        headers={"Origin": "https://numista.ai", "Content-Type": "application/json"},
        data=json.dumps({"mode": "living_inventory", "owner_name": "Test", "report_date": "2026-09-29", "state": "NY"}),
    )
    assert resp.status_code == 401
    assert "Unauthorized" in resp.get_json().get("error", "")

    # 2. Invalid Bearer token
    with patch.object(scan_main.fb_auth, "verify_id_token", side_effect=Exception("Expired token")):
        resp_invalid = client.post(
            "/generate_estate_report",
            headers={
                "Origin": "https://numista.ai",
                "Content-Type": "application/json",
                "Authorization": "Bearer bad-token",
            },
            data=json.dumps({"mode": "living_inventory", "owner_name": "Test", "report_date": "2026-09-29", "state": "NY"}),
        )
        assert resp_invalid.status_code == 401
        assert "Unauthorized" in resp_invalid.get_json().get("error", "")


def test_generate_estate_report_uid_mismatch_forbidden(client):
    """Verify 403 when body uid differs from authenticated token (M1)."""
    with patch.object(scan_main.fb_auth, "verify_id_token", return_value={"email": "real_owner@numista.ai", "uid": "real_uid"}):
        resp = client.post(
            "/generate_estate_report",
            headers={
                "Origin": "https://numista.ai",
                "Content-Type": "application/json",
                "Authorization": "Bearer valid-token",
            },
            data=json.dumps({
                "uid": "victim_user@numista.ai",
                "mode": "living_inventory",
                "owner_name": "Victim",
                "report_date": "2026-09-30",
                "state": "NY",
            }),
        )
        assert resp.status_code == 403
        assert "Forbidden" in resp.get_json().get("error", "")


def test_generate_estate_report_state_validation(client):
    """Verify strict state validation (S1): missing or unknown state returns 400."""
    with patch.object(scan_main.fb_auth, "verify_id_token", return_value={"email": "tester@numista.ai", "uid": "uid123"}):
        auth_header = {"Authorization": "Bearer valid-token", "Content-Type": "application/json"}

        # 1. Missing state
        resp_missing = client.post(
            "/generate_estate_report",
            headers=auth_header,
            data=json.dumps({"mode": "living_inventory", "owner_name": "Test", "report_date": "2026-09-30"}),
        )
        assert resp_missing.status_code == 400
        assert "state" in resp_missing.get_json().get("error", "")

        # 2. Unknown state code (ZZ)
        resp_unknown = client.post(
            "/generate_estate_report",
            headers=auth_header,
            data=json.dumps({"mode": "living_inventory", "owner_name": "Test", "report_date": "2026-09-30", "state": "ZZ"}),
        )
        assert resp_unknown.status_code == 400
        assert "Unsupported or unrecognized state" in resp_unknown.get_json().get("error", "")


def test_generate_estate_report_validation_400s(client):
    """Verify 400 errors for missing fields, invalid mode, and estate_settlement without date_of_death (REQ-023F)."""
    with patch.object(scan_main.fb_auth, "verify_id_token", return_value={"email": "tester@numista.ai", "uid": "uid123"}):
        auth_header = {"Authorization": "Bearer valid-token", "Content-Type": "application/json"}

        # 1. Missing required fields (e.g. owner_name and report_date missing)
        resp_missing = client.post(
            "/generate_estate_report",
            headers=auth_header,
            data=json.dumps({"mode": "living_inventory", "state": "NY"}),
        )
        assert resp_missing.status_code == 400
        assert "Missing required fields" in resp_missing.get_json().get("error", "")

        # 2. Invalid mode (mode not living_inventory or estate_settlement)
        resp_invalid_mode = client.post(
            "/generate_estate_report",
            headers=auth_header,
            data=json.dumps({
                "mode": "unsupported_mode",
                "state": "NY",
                "owner_name": "Test Collector",
                "report_date": "2026-09-30",
            }),
        )
        assert resp_invalid_mode.status_code == 400
        assert "Invalid mode" in resp_invalid_mode.get_json().get("error", "")

        # 3. Estate settlement mode without date_of_death
        resp_no_dod = client.post(
            "/generate_estate_report",
            headers=auth_header,
            data=json.dumps({
                "mode": "estate_settlement",
                "state": "NY",
                "owner_name": "Late Collector",
                "report_date": "2026-09-30",
            }),
        )
        assert resp_no_dod.status_code == 400
        assert "date_of_death is required" in resp_no_dod.get_json().get("error", "")


def test_initialize_estate_upgrade_security(client):
    """Verify /initialize_estate_upgrade requires Bearer auth and enforces UID matching (M1)."""
    # 1. Unauthenticated -> 401
    resp_unauth = client.post(
        "/initialize_estate_upgrade",
        headers={"Content-Type": "application/json"},
        data=json.dumps({"uid": "target_user@numista.ai"}),
    )
    assert resp_unauth.status_code == 401

    # 2. Cross-user UID mismatch -> 403
    with patch.object(scan_main.fb_auth, "verify_id_token", return_value={"email": "alice@numista.ai", "uid": "alice123"}):
        resp_mismatch = client.post(
            "/initialize_estate_upgrade",
            headers={"Content-Type": "application/json", "Authorization": "Bearer token-alice"},
            data=json.dumps({"uid": "bob@numista.ai"}),
        )
        assert resp_mismatch.status_code == 403


def test_scan_checklist_security(client):
    """Verify /scan_checklist requires Bearer auth and enforces user_id matching (M1)."""
    # 1. Unauthenticated -> 401
    resp_unauth = client.post(
        "/scan_checklist",
        data={"program_id": "prog1", "user_id": "victim@numista.ai", "image": (io.BytesIO(b"fakeimage"), "test.jpg")},
        content_type="multipart/form-data",
    )
    assert resp_unauth.status_code == 401

    # 2. Cross-user user_id mismatch -> 403
    with patch.object(scan_main.fb_auth, "verify_id_token", return_value={"email": "attacker@numista.ai", "uid": "att123"}):
        resp_mismatch = client.post(
            "/scan_checklist",
            headers={"Authorization": "Bearer attacker-token"},
            data={"program_id": "prog1", "user_id": "victim@numista.ai", "image": (io.BytesIO(b"fakeimage"), "test.jpg")},
            content_type="multipart/form-data",
        )
        assert resp_mismatch.status_code == 403


def test_generate_estate_report_success(client):
    """Verify successful report generation with verified token and valid state."""
    fake_token = {"email": "verified_owner@numista.ai", "uid": "auth_uid_999"}
    fake_pdf = b"%PDF-1.4\n...estate report pdf bytes..."
    fake_metadata = {
        "report_id": "rep_test_001",
        "total_coins": 42,
        "total_fmv": 150000.0,
        "mode": "living_inventory",
        "state": "NY",
    }

    mock_db = MagicMock()
    captured_generator_args = {}

    async def fake_generate(**kwargs):
        captured_generator_args.update(kwargs)
        return {
            "pdf_bytes": fake_pdf,
            "report_metadata": fake_metadata,
        }

    with patch.object(scan_main.fb_auth, "verify_id_token", return_value=fake_token), \
         patch.object(scan_main, "db", mock_db), \
         patch("estate_report_generator.generate_estate_report", side_effect=fake_generate):

        resp = client.post(
            "/generate_estate_report",
            headers={
                "Origin": "https://numista.ai",
                "Content-Type": "application/json",
                "Authorization": "Bearer valid-owner-token",
            },
            data=json.dumps({
                "mode": "living_inventory",
                "owner_name": "Verified Collector",
                "report_date": "2026-09-30",
                "state": "NY",
            }),
        )

        assert resp.status_code == 200
        assert resp.headers.get("Content-Type") == "application/pdf"
        assert resp.headers.get("X-Report-Id") == "rep_test_001"
        assert resp.headers.get("Access-Control-Allow-Origin") == "https://numista.ai"
        assert resp.data == fake_pdf
        assert captured_generator_args["uid"] == "verified_owner@numista.ai"
        assert captured_generator_args["report_request"]["state"] == "NY"
