"""
numista_backend/tests/test_valuation_cap.py
-------------------------------------------
Unit tests for AI valuation rate capping and anonymous user block:
1. Anonymous token -> 403 Forbidden
2. Valid token, 21st call -> 429 Daily limit reached (rate cap enforced)
3. Valid token, first call -> 200 (mocked Gemini client)
"""

import json
from unittest.mock import patch, MagicMock
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from main import app
from routes.deps import get_current_user


@pytest.fixture(autouse=True)
def clean_deps():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def test_estimate_value_text_anonymous_blocked():
    """Anonymous token -> 403 for estimate_value_text."""
    app.dependency_overrides[get_current_user] = lambda: {
        "uid": "anon_guest",
        "firebase": {"sign_in_provider": "anonymous"},
    }
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post(
        "/api/estimate_value_text",
        json={"year": "1921", "denomination": "Morgan Dollar"},
    )
    assert resp.status_code == 403
    assert "Anonymous users cannot use AI valuation" in resp.json()["detail"]


def test_estimate_value_general_anonymous_blocked():
    """Anonymous token -> 403 for estimate_value_general."""
    app.dependency_overrides[get_current_user] = lambda: {
        "uid": "anon_guest",
        "firebase": {"sign_in_provider": "anonymous"},
    }
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post(
        "/api/estimate_value_general",
        json={"item_type": "coin", "name": "1921 Morgan Dollar"},
    )
    assert resp.status_code == 403
    assert "Anonymous users cannot use AI valuation" in resp.json()["detail"]


def test_estimate_value_text_valid_token_first_call_returns_200():
    """Valid token, first call -> 200 with mocked Gemini client."""
    app.dependency_overrides[get_current_user] = lambda: {
        "uid": "user_premium",
        "email": "user@numista.ai",
        "firebase": {"sign_in_provider": "password"},
    }
    client = TestClient(app, raise_server_exceptions=False)

    mock_resp = MagicMock()
    mock_resp.text = json.dumps({
        "estimated_value": "$25 - $35",
        "confidence": "HIGH",
        "basis": "Common date Morgan Dollar in VF/XF condition",
    })

    with patch("main._check_and_increment_rate_cap") as mock_cap, \
         patch("main.genai_client.models.generate_content", return_value=mock_resp):
        resp = client.post(
            "/api/estimate_value_text",
            json={"year": "1921", "denomination": "Dollar", "program_series": "Morgan"},
        )
        assert resp.status_code == 200
        mock_cap.assert_called_once_with("user_premium", "estimate_value", 20, is_admin=False)
        data = resp.json()
        assert data["estimated_value"] == "$25 - $35"
        assert data["confidence"] == "HIGH"


def test_estimate_value_general_valid_token_first_call_returns_200():
    """Valid token, first call -> 200 with mocked Gemini client for estimate_value_general."""
    app.dependency_overrides[get_current_user] = lambda: {
        "uid": "user_premium",
        "email": "user@numista.ai",
        "firebase": {"sign_in_provider": "password"},
    }
    client = TestClient(app, raise_server_exceptions=False)

    mock_resp = MagicMock()
    mock_resp.text = json.dumps({
        "estimated_value": "$100 - $150",
        "confidence": "MEDIUM",
        "basis": "Historic commemorative medal in pristine condition",
    })

    with patch("main._check_and_increment_rate_cap") as mock_cap, \
         patch("main.genai_client.models.generate_content", return_value=mock_resp):
        resp = client.post(
            "/api/estimate_value_general",
            json={"item_type": "medal", "name": "1892 Columbian Exposition Medal"},
        )
        assert resp.status_code == 200
        mock_cap.assert_called_once_with("user_premium", "estimate_value", 20, is_admin=False)
        data = resp.json()
        assert data["estimated_value"] == "$100 - $150"


def test_estimate_value_text_rate_cap_exceeded_returns_429():
    """Valid token, 21st call -> 429 when rate cap is reached."""
    app.dependency_overrides[get_current_user] = lambda: {
        "uid": "user_active",
        "email": "active@numista.ai",
        "firebase": {"sign_in_provider": "password"},
    }
    client = TestClient(app, raise_server_exceptions=False)

    call_count = [0]

    def _mock_rate_cap(uid, endpoint, daily_limit, is_admin=False):
        call_count[0] += 1
        if call_count[0] > 20:
            raise HTTPException(status_code=429, detail="Daily limit reached")

    with patch("main._check_and_increment_rate_cap", side_effect=_mock_rate_cap), \
         patch("main.genai_client.models.generate_content") as mock_gen:
        mock_resp = MagicMock()
        mock_resp.text = json.dumps({
            "estimated_value": "$15 - $25",
            "confidence": "MEDIUM",
            "basis": "Standard circulated coin",
        })
        mock_gen.return_value = mock_resp

        # Simulate 20 calls under limit
        for _ in range(20):
            res = client.post(
                "/api/estimate_value_text",
                json={"year": "1964", "denomination": "Half Dollar"},
            )
            assert res.status_code == 200

        # 21st call triggers 429
        res_21 = client.post(
            "/api/estimate_value_text",
            json={"year": "1964", "denomination": "Half Dollar"},
        )
        assert res_21.status_code == 429
        assert res_21.json()["detail"] == "Daily limit reached"
