"""
test_identify_group_photo.py
----------------------------
Regression test suite for REQ_010:
- Verifies that POST /api/identify_group_photo succeeds (HTTP 200) when Gemini returns structured coin JSON.
- Verifies that POST /api/identify_group_photo gracefully returns HTTP 500 JSONResponse with CORS headers
  when Gemini or processing raises an exception, preventing unhandled 500s or browser CORS errors.
- Verifies that `JSONResponse` is properly imported in `main.py` without NameError.
"""

import io
import json
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main
from main import app

client = TestClient(app)

def test_jsonresponse_imported():
    """Verify that JSONResponse is imported in main module without NameError."""
    assert hasattr(main, "JSONResponse")
    from fastapi.responses import JSONResponse
    assert main.JSONResponse is JSONResponse


def test_identify_group_photo_success_mocked(monkeypatch):
    """POST a JPEG to /api/identify_group_photo with mocked Gemini returning 1 coin -> 200 OK."""
    # Stub auth check
    monkeypatch.setattr(main, "_authenticate_request", lambda *a, **kw: "tester@numista.ai")

    # Stub GCS upload
    monkeypatch.setattr(main, "_upload_to_gcs", lambda data, path, ct: "https://storage.googleapis.com/test-bucket/test.jpg")

    # Stub Gemini generate_content
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "coins": [{"index": 1, "year": "1964", "denomination": "Half Dollar"}],
        "appears_grouped": True,
        "suggested_group_name": "1964 Set",
        "coin_count": 1,
        "truncated": False,
        "large_group_warning": False
    })
    
    mock_models = MagicMock()
    mock_models.generate_content.return_value = mock_response
    mock_client = MagicMock()
    mock_client.models = mock_models
    monkeypatch.setattr(main, "genai_client", mock_client)

    dummy_image = io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00")
    files = {"image": ("test.jpg", dummy_image, "image/jpeg")}
    data = {"user_email": "tester@numista.ai"}
    
    resp = client.post("/api/identify_group_photo", files=files, data=data, headers={"Authorization": "Bearer mock_token"})
    assert resp.status_code == 200
    res_json = resp.json()
    assert res_json["coin_count"] == 1
    assert len(res_json["coins"]) == 1
    assert res_json["coins"][0]["year"] == "1964"


def test_identify_group_photo_gemini_error_returns_500_json(monkeypatch):
    """When Gemini raises an exception, verify endpoint returns 500 JSON body without crashing."""
    monkeypatch.setattr(main, "_authenticate_request", lambda *a, **kw: "tester@numista.ai")

    # Stub GCS upload
    monkeypatch.setattr(main, "_upload_to_gcs", lambda data, path, ct: "https://storage.googleapis.com/test-bucket/test.jpg")

    # Stub Gemini generate_content to raise
    def _raise_error(*args, **kwargs):
        raise RuntimeError("Simulated Gemini API error")

    mock_models = MagicMock()
    mock_models.generate_content.side_effect = _raise_error
    mock_client = MagicMock()
    mock_client.models = mock_models
    monkeypatch.setattr(main, "genai_client", mock_client)

    dummy_image = io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00")
    files = {"image": ("test.jpg", dummy_image, "image/jpeg")}
    data = {"user_email": "tester@numista.ai"}

    resp = client.post("/api/identify_group_photo", files=files, data=data, headers={"Authorization": "Bearer mock_token"})
    assert resp.status_code == 500
    res_json = resp.json()
    assert "error" in res_json
    assert "Simulated Gemini API error" in res_json["error"]
