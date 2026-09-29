"""
test_scan_service_estate_report.py
----------------------------------
Unit and regression tests for REQ_020:
- CORS OPTIONS preflight response headers (Allow-Origin, Allow-Headers, Allow-Methods, Expose-Headers)
- Bearer Auth requirement on /generate_estate_report (401 on missing/invalid token)
- Token-derived UID (ignores untrusted body UID)
- Request validation (400 on missing required fields / invalid mode)
- Safe fallback for missing or unrecognized state to 'NY'
- Successful PDF generation (200) with correct headers
- Local import verification for collection_inventory in scan_service
"""

import json
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


def test_generate_estate_report_unauthorized(client):
    """Verify 401 when Authorization Bearer token is missing or invalid."""
    # 1. No Authorization header
    resp = client.post(
        "/generate_estate_report",
        headers={"Origin": "https://numista.ai", "Content-Type": "application/json"},
        data=json.dumps({"mode": "living_inventory", "owner_name": "Test", "report_date": "2026-09-29"}),
    )
    assert resp.status_code == 401
    assert "Unauthorized" in resp.get_json().get("error", "")
    assert resp.headers.get("Access-Control-Allow-Origin") == "https://numista.ai"

    # 2. Invalid Bearer token
    with patch.object(scan_main.fb_auth, "verify_id_token", side_effect=Exception("Expired token")):
        resp_invalid = client.post(
            "/generate_estate_report",
            headers={
                "Origin": "https://numista.ai",
                "Content-Type": "application/json",
                "Authorization": "Bearer bad-token",
            },
            data=json.dumps({"mode": "living_inventory", "owner_name": "Test", "report_date": "2026-09-29"}),
        )
        assert resp_invalid.status_code == 401
        assert "Unauthorized" in resp_invalid.get_json().get("error", "")


def test_generate_estate_report_validation_errors(client):
    """Verify 400 when required fields are missing or invalid."""
    with patch.object(scan_main.fb_auth, "verify_id_token", return_value={"email": "tester@numista.ai", "uid": "uid123"}):
        auth_header = {"Authorization": "Bearer valid-token", "Content-Type": "application/json"}

        # Missing required fields
        resp = client.post("/generate_estate_report", headers=auth_header, data=json.dumps({}))
        assert resp.status_code == 400
        assert "Missing required fields" in resp.get_json().get("error", "")

        # Invalid mode
        resp_mode = client.post(
            "/generate_estate_report",
            headers=auth_header,
            data=json.dumps({"mode": "invalid_mode", "owner_name": "Test Owner", "report_date": "2026-09-29"}),
        )
        assert resp_mode.status_code == 400
        assert "Invalid mode" in resp_mode.get_json().get("error", "")

        # Estate settlement mode missing date_of_death
        resp_death = client.post(
            "/generate_estate_report",
            headers=auth_header,
            data=json.dumps({"mode": "estate_settlement", "owner_name": "Test Owner", "report_date": "2026-09-29"}),
        )
        assert resp_death.status_code == 400
        assert "date_of_death is required" in resp_death.get_json().get("error", "")


def test_generate_estate_report_success_and_uid_isolation(client):
    """Verify successful report generation: derives uid from token and defaults missing state to NY."""
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
                # Body attempts to spoof victim uid and omits state
                "uid": "attacker_spoofed_victim@numista.ai",
                "mode": "living_inventory",
                "owner_name": "Verified Collector",
                "report_date": "2026-09-29",
            }),
        )

        assert resp.status_code == 200
        assert resp.headers.get("Content-Type") == "application/pdf"
        assert resp.headers.get("X-Report-Id") == "rep_test_001"
        assert resp.headers.get("Access-Control-Allow-Origin") == "https://numista.ai"
        assert resp.data == fake_pdf

        # CRITICAL SECURITY ASSERTION: UID was derived from token, NOT spoofed body
        assert captured_generator_args["uid"] == "verified_owner@numista.ai"
        # State safely defaulted to 'NY'
        assert captured_generator_args["report_request"]["state"] == "NY"
