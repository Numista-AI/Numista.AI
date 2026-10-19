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
