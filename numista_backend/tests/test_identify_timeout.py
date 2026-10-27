"""
test_identify_timeout.py
-------------------------
Regression test for P7 V8.18.1: Server-side timeout cap for POST /api/identify_coin_photo.
When Gemini call times out, the endpoint returns 408 with clear message.
"""

import asyncio
import io
import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_identify_coin_photo_returns_408_on_timeout(monkeypatch):
    """When Gemini call times out, endpoint returns 408 with clear message."""
    async def slow_gemini(*args, **kwargs):
        raise asyncio.TimeoutError()

    monkeypatch.setattr(main, "_authenticate_request", lambda auth, email=None, **kw: "tester@numista.ai")

    dummy_image = io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00")
    files = {"image_a": ("obverse.jpg", dummy_image, "image/jpeg")}
    data = {"user_email": "tester@numista.ai", "save_to_collection": "false"}

    with patch("main.call_gemini_identify", side_effect=slow_gemini):
        resp = client.post(
            "/api/identify_coin_photo",
            data=data,
            files=files,
            headers={"Authorization": "Bearer test-token"},
        )
    assert resp.status_code == 408
    assert "timed out" in resp.json()["detail"].lower()


def test_identify_coin_photo_real_wait_for_timeout(monkeypatch):
    """Verify asyncio.wait_for fires with configured timeout."""
    async def hanging_gemini(*args, **kwargs):
        await asyncio.sleep(1.0)
        return {}

    monkeypatch.setattr(main, "GEMINI_IDENTIFY_TIMEOUT", 0.05)
    # Pass 1 now uses GEMINI_IDENTIFY_PASS1_TIMEOUT; patch both to ensure timeout fires
    monkeypatch.setattr(main, "GEMINI_IDENTIFY_PASS1_TIMEOUT", 0.05)
    monkeypatch.setattr(main, "_authenticate_request", lambda auth, email=None, **kw: "tester@numista.ai")

    dummy_image = io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00")
    files = {"image_a": ("obverse.jpg", dummy_image, "image/jpeg")}
    data = {"user_email": "tester@numista.ai", "save_to_collection": "false"}

    with patch("main.call_gemini_identify", side_effect=hanging_gemini):
        resp = client.post(
            "/api/identify_coin_photo",
            data=data,
            files=files,
            headers={"Authorization": "Bearer test-token"},
        )
    assert resp.status_code == 408
    assert "timed out" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Fix 1 (V8.18.2): cert_routes._SCAN_PROJECT_ID must never default to numista-qc
# ---------------------------------------------------------------------------

def test_cert_routes_project_id_never_defaults_to_numista_qc(monkeypatch):
    """With both FIREBASE_PROJECT_ID and GOOGLE_CLOUD_PROJECT unset,
    _SCAN_PROJECT_ID must NOT fall back to 'numista-qc'."""
    monkeypatch.delenv("FIREBASE_PROJECT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    # Re-import or reload to pick up fresh env
    import importlib
    import numista_backend.routes.cert_routes as cr
    importlib.reload(cr)
    assert cr._SCAN_PROJECT_ID != "numista-qc"
    assert cr._SCAN_PROJECT_ID == "studio-9101802118-8c9a8"


# ---------------------------------------------------------------------------
# Fix 2 (V8.18.2): Pass-2 budget skip returns pass-1 result with 200
# ---------------------------------------------------------------------------

def test_identify_coin_photo_pass2_skipped_when_budget_exhausted(monkeypatch):
    """When the whole-request budget is set to 0s, any elapsed time after pass 1
    guarantees _pass2_budget < 3s, so pass 2 is skipped and 200 is returned
    with the pass-1 result."""
    call_count = {"n": 0}

    async def mock_gemini(*args, **kwargs):
        call_count["n"] += 1
        if call_count["n"] == 1:
            # Pass 1 returns immediately with a valid result
            return {
                "year": "1921",
                "denomination": "Dollar",
                "country": "United States",
                "program_series": "Morgan Dollar",
                "mint_mark": "S",
                "grade": "MS-63",
                "metal_content": "90% Silver",
                "grading_service": "None",
                "cert_number": "",
                "confidence": "HIGH",
                "obverse_image": "A",
                "variety_notes": "",
                "theme_subject": "",
                "is_silver": True,
                "is_gold": False,
                "report": "Test coin",
                "personal_notes": "",
            }
        # Pass 2 must never be called when budget is exhausted
        raise AssertionError("Pass 2 should have been skipped due to budget exhaustion")

    # Set budget to 0.0: any elapsed time (even 1ms) makes _pass2_budget < 0 < 3.0
    # so pass 2 is unconditionally skipped. No need to mock time.monotonic.
    monkeypatch.setattr(main, "GEMINI_IDENTIFY_PASS1_TIMEOUT", 20.0)
    monkeypatch.setattr(main, "GEMINI_IDENTIFY_BUDGET", 0.0)
    monkeypatch.setattr(main, "_authenticate_request", lambda auth, email=None, **kw: "tester@numista.ai")

    dummy_image = io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00")
    files = {"image_a": ("obverse.jpg", dummy_image, "image/jpeg")}
    data = {"user_email": "tester@numista.ai", "save_to_collection": "false"}

    with patch("main.call_gemini_identify", side_effect=mock_gemini):
        resp = client.post(
            "/api/identify_coin_photo",
            data=data,
            files=files,
            headers={"Authorization": "Bearer test-token"},
        )

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    # Response wraps coin in body["coin"] when save_to_collection=False
    coin = body.get("coin") or body
    assert coin.get("Year") == "1921", f"Expected Year=1921, got {coin.get('Year')} in {list(coin.keys())[:5]}"
    # Pass 2 must NOT have been called (only 1 gemini call total)
    assert call_count["n"] == 1, f"Pass 2 was called unexpectedly (call_count={call_count['n']})"

