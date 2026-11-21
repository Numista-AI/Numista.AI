"""P5 wire-level transport & static-guard tests for Gemini 4 Hydrogen migration."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import MagicMock

import httpx
import pytest
from fastapi.testclient import TestClient
from google import genai
from google.auth.credentials import Credentials
from google.genai import types as genai_types

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "numista_backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import config as backend_config  # noqa: E402


class AnonymousTestCredentials(Credentials):
    """Synthetic credentials that never read or print real ADC tokens."""

    def __init__(self, token: str = "synthetic-unit-test-token-do-not-print") -> None:
        super().__init__()
        self.token = token

    def refresh(self, request: Any) -> None:  # pragma: no cover - no-op
        return None


def make_recording_client(
    captured: List[httpx.Request],
    *,
    vertexai: bool = True,
    response_sequence: Optional[List[Tuple[int, Dict[str, Any]]]] = None,
) -> genai.Client:
    seq = list(response_sequence or [])

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        if seq:
            status, body = seq.pop(0)
        else:
            status, body = (
                200,
                {
                    "candidates": [
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": '{"ok": true, "status": "ok"}'}],
                            }
                        }
                    ],
                    "usageMetadata": {
                        "promptTokenCount": 120,
                        "candidatesTokenCount": 30,
                        "thoughtsTokenCount": 15,
                    },
                },
            )
        return httpx.Response(status_code=status, json=body)

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    if vertexai:
        return genai.Client(
            vertexai=True,
            project="studio-9101802118-8c9a8",
            location="global",
            credentials=AnonymousTestCredentials(),
            http_options=genai_types.HttpOptions(httpx_client=http_client),
        )
    return genai.Client(
        api_key="synthetic-api-key-do-not-print",
        http_options=genai_types.HttpOptions(httpx_client=http_client),
    )


def assert_hydrogen_wire_request(
    req: httpx.Request,
    *,
    expected_model: str = "gemini-4-hydrogen",
    vertexai: bool = True,
    expect_thinking: bool = True,
    allowed_levels: Tuple[str, ...] = ("LOW", "MEDIUM", "low", "medium"),
) -> Dict[str, Any]:
    assert req.method == "POST"
    assert req.url.scheme == "https"
    if vertexai:
        assert req.url.host == "aiplatform.googleapis.com"
        assert req.url.path.endswith(
            f"/projects/studio-9101802118-8c9a8/locations/global/publishers/google/models/{expected_model}:generateContent"
        )
        auth = req.headers.get("authorization", "")
        assert auth.startswith("Bearer ") and len(auth) > 10
    else:
        assert req.url.host == "generativelanguage.googleapis.com"
        assert req.url.path.endswith(f"/models/{expected_model}:generateContent")
        api_key = req.headers.get("x-goog-api-key", "")
        assert len(api_key) > 5

    payload = json.loads(req.content.decode("utf-8"))
    gen_cfg = payload.get("generationConfig", {})
    assert "temperature" not in gen_cfg
    assert "topP" not in gen_cfg
    assert "topK" not in gen_cfg
    assert "cachedContent" not in payload
    if expect_thinking:
        thinking = gen_cfg.get("thinkingConfig", {})
        level_val = thinking.get("thinkingLevel") or thinking.get("thinking_level")
        assert level_val in allowed_levels
        assert "thinkingBudget" not in thinking
        assert "thinking_budget" not in thinking
    else:
        assert "thinkingConfig" not in gen_cfg
    return payload


def test_gemini4_thinking_config_helper():
    assert backend_config.is_gemini4_model("gemini-4-hydrogen") is True
    assert backend_config.is_gemini4_model("gemini-4-argon") is True
    assert backend_config.is_gemini4_model("gemini-3.8-flash") is False
    assert backend_config.is_gemini4_model("gemini-3.5-flash-lite") is False
    cfg = backend_config.gemini4_thinking_config("gemini-4-hydrogen", "low")
    assert cfg is not None
    assert str(cfg.thinking_level).lower().endswith("low")
    assert backend_config.gemini4_thinking_config("gemini-3.8-flash", "low") is None


def test_ai_routes_hydrogen_and_lite_fallback(monkeypatch):
    from routes import ai_routes

    captured: List[httpx.Request] = []
    client = make_recording_client(
        captured,
        response_sequence=[
            (503, {"error": {"code": 503, "message": "unavailable"}}),
            (
                200,
                {
                    "candidates": [
                        {"content": {"role": "model", "parts": [{"text": "fallback ok"}]}}
                    ]
                },
            ),
        ],
    )
    monkeypatch.setattr(ai_routes, "genai_client", client)
    text = ai_routes.call_chat_model_with_fallback(
        "You are Morgan.", "What is a 1909-S VDB?"
    )
    assert text == "fallback ok"
    assert len(captured) == 2
    assert_hydrogen_wire_request(captured[0], expected_model="gemini-4-hydrogen", expect_thinking=True)
    assert_hydrogen_wire_request(captured[1], expected_model="gemini-3.5-flash-lite", expect_thinking=False)


def test_emergency_rollback_model_omits_thinking_config():
    captured: List[httpx.Request] = []
    client = make_recording_client(captured)
    rollback_model = "gemini-3.8-flash"
    client.models.generate_content(
        model=rollback_model,
        contents=[genai_types.Part.from_text(text="Ping")],
        config=genai_types.GenerateContentConfig(
            thinking_config=backend_config.gemini4_thinking_config(rollback_model, "low"),
        ),
    )
    assert len(captured) == 1
    assert_hydrogen_wire_request(captured[0], expected_model="gemini-3.8-flash", expect_thinking=False)


def test_morgan_web_lookup_and_deep_dive_guards(monkeypatch):
    import main as app_main
    from routes import morgan_routes

    captured: List[httpx.Request] = []
    client = make_recording_client(captured)
    monkeypatch.setattr(morgan_routes, "genai_client", client)
    monkeypatch.setattr(app_main, "genai_client", client)

    # Blank query -> 400 and 0 outbound requests
    with pytest.raises(Exception) as exc_info:
        morgan_routes.execute_morgan_web_lookup("   ")
    assert getattr(exc_info.value, "status_code", None) == 400
    assert len(captured) == 0

    # Missing auth on /api/deep_dive -> 401 and 0 outbound requests
    tc = TestClient(app_main.app)
    resp = tc.post("/api/deep_dive", json={"user_email": "alice@example.com", "query": "hello"})
    assert resp.status_code == 401
    assert len(captured) == 0


def test_deep_dive_thought_signature_round_trip(monkeypatch):
    import main as app_main

    captured: List[httpx.Request] = []
    client = make_recording_client(
        captured,
        response_sequence=[
            (
                200,
                {
                    "candidates": [
                        {
                            "content": {
                                "role": "model",
                                "parts": [
                                    {"thought": True, "text": "checking mintage"},
                                    {
                                        "functionCall": {
                                            "name": "get_coin_details",
                                            "args": {"coin_name": "1909-S VDB"},
                                        },
                                        "thoughtSignature": "c2lnX3Rlc3RfMTIz",
                                    },
                                ],
                            }
                        }
                    ]
                },
            ),
            (
                200,
                {
                    "candidates": [
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": "1909-S VDB mintage is 484,000."}],
                            }
                        }
                    ]
                },
            ),
        ],
    )
    monkeypatch.setattr(app_main, "genai_client", client)
    monkeypatch.setattr(app_main, "execute_get_coin_details", lambda *a, **kw: {"mintage": 484000})
    monkeypatch.setattr(
        app_main.fb_auth,
        "verify_id_token",
        lambda _tok: {"uid": "uid_test_123", "email": "alice@example.com", "admin": False},
    )
    monkeypatch.setattr(app_main, "_check_and_increment_rate_cap", lambda *a, **kw: None)
    mock_col = MagicMock()
    mock_col.stream.return_value = []
    mock_user_doc = MagicMock()
    mock_user_doc.collection.return_value = mock_col
    mock_users = MagicMock()
    mock_users.document.return_value = mock_user_doc
    monkeypatch.setattr(app_main.db, "collection", lambda _name: mock_users)

    tc = TestClient(app_main.app)
    resp = tc.post(
        "/api/deep_dive",
        json={"user_email": "alice@example.com", "query": "Tell me about 1909-S VDB"},
        headers={"Authorization": "Bearer synthetic-token"},
    )
    assert resp.status_code == 200
    assert len(captured) == 2
    assert_hydrogen_wire_request(captured[0], expected_model="gemini-4-hydrogen")
    turn2_payload = assert_hydrogen_wire_request(captured[1], expected_model="gemini-4-hydrogen")
    assert turn2_payload["contents"][1]["parts"][1]["thoughtSignature"] == "c2lnX3Rlc3RfMTIz"
    assert turn2_payload["contents"][2]["parts"][0]["functionResponse"]["name"] == "get_coin_details"


def test_morgan_copilot_cost_guard_backward_compat():
    from routes import morgan_routes

    # 2-arg backward-compat call must not raise TypeError
    assert morgan_routes._estimate_copilot_cost_usd(1000, 200) == round(
        (1000 * 0.0000015) + (200 * 0.0000075), 6
    )
    # 3-arg call includes thoughts_tokens at output rate
    assert morgan_routes._estimate_copilot_cost_usd(1000, 200, 100) == round(
        (1000 * 0.0000015) + (300 * 0.0000075), 6
    )


def test_cert_and_feedback_routes_wire_requests(monkeypatch):
    from routes import cert_routes

    captured: List[httpx.Request] = []
    client = make_recording_client(captured)
    monkeypatch.setattr(cert_routes, "_scan_client", client, raising=False)
    client.models.generate_content(
        model="gemini-4-hydrogen",
        contents=[
            genai_types.Part.from_text(text="Extract cert"),
            genai_types.Part.from_bytes(data=b"img", mime_type="image/jpeg"),
        ],
        config=genai_types.GenerateContentConfig(
            response_mime_type="application/json",
            max_output_tokens=1024,
            thinking_config=backend_config.gemini4_thinking_config("gemini-4-hydrogen", "low"),
        ),
    )
    assert len(captured) == 1
    assert_hydrogen_wire_request(captured[0], expected_model="gemini-4-hydrogen")


def test_qc_and_hardware_mocked_wire_requests():
    # Mocked P5 transport test only (numista-qc billing is OFF)
    captured: List[httpx.Request] = []
    client = make_recording_client(captured, vertexai=False)
    for model_id in ("gemini-4-hydrogen", "gemini-4-argon"):
        level = "medium" if model_id == "gemini-4-argon" else "low"
        client.models.generate_content(
            model=model_id,
            contents=["Ping"],
            config=genai_types.GenerateContentConfig(
                thinking_config=genai_types.ThinkingConfig(thinking_level=level)
            ),
        )
    assert len(captured) == 2
    assert_hydrogen_wire_request(captured[0], expected_model="gemini-4-hydrogen", vertexai=False)
    assert_hydrogen_wire_request(captured[1], expected_model="gemini-4-argon", vertexai=False)


def test_static_hydrogen_source_guard():
    forbidden = re.compile(
        r"(thinking_budget|thinkingBudget|ThinkingLevel\.minimal|ThinkingLevel\.MINIMAL|"
        r"caches\.create|cached_content|cachedContent|\btop_p\b|\btopP\b|\btop_k\b|\btopK\b|"
        r"\btemperature\s*[:=])"
    )
    checked_files = [
        REPO_ROOT / "numista_backend/main.py",
        REPO_ROOT / "numista_backend/config/__init__.py",
        REPO_ROOT / "numista_backend/routes/ai_routes.py",
        REPO_ROOT / "numista_backend/routes/cert_routes.py",
        REPO_ROOT / "numista_backend/routes/feedback_callable_route.py",
        REPO_ROOT / "numista_backend/routes/morgan_routes.py",
        REPO_ROOT / "numista_backend/services/checklist_parser.py",
        REPO_ROOT / "numista_backend/services/document_classifier_service.py",
        REPO_ROOT / "numista_backend/services/greysheet_service.py",
        REPO_ROOT / "numista_backend/services/variety_detector.py",
        REPO_ROOT / "numista_backend/numista_scraper/grading_advisor.py",
        REPO_ROOT / "numista_backend/scan_service/main.py",
        REPO_ROOT / "numista_backend/scan_service/estate_report_generator.py",
        REPO_ROOT / "numista_backend/brain_processor.py",
        REPO_ROOT / "numista_backend/sync_worker/main.py",
        REPO_ROOT / "numista_backend/littleton_sku_helper.py",
        REPO_ROOT / "numista_backend/generate_definitive_catalog.py",
        REPO_ROOT / "numista_backend/load_definitive_catalog.py",
        REPO_ROOT / "numista_backend/ingest_banknotes.py",
        REPO_ROOT / "numista_backend/_scripts/verify_sa_key.py",
        REPO_ROOT / "numista_backend/_scripts/verify_vertex_model.py",
        REPO_ROOT / "numista_backend/functions/feedbackIntelligence.js",
        REPO_ROOT / "numista_backend/functions/mappingController.js",
        REPO_ROOT / "numista_backend/mappingController.js",
        REPO_ROOT / "numista_backend/integration_service.js",
        REPO_ROOT / "numista_mobile/lib/screens/coin_detail_screen.dart",
        REPO_ROOT / "numista_mobile/lib/services/coin_normalizer_service.dart",
        REPO_ROOT / "numista_ai/info_bot.py",
        REPO_ROOT / "numista_qc/layer_4_self_update/feedback_miner.py",
        REPO_ROOT / "numista_qc/layer_4_self_update/test_synthesizer.py",
        REPO_ROOT / "numista_hardware/coin_engine.py",
        REPO_ROOT / "numista_hardware/identify_coin.py",
        REPO_ROOT / "numista_hardware/test_gemini_response.py",
        REPO_ROOT / "numista_hardware/Original_logic/services/geminiService.ts",
        REPO_ROOT / "numista_hardware/Original_logic/services/ngcService.ts",
    ]
    for path in checked_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        # Ignore comments/docstrings? Check line-by-line excluding pure comment lines
        for lineno, line in enumerate(text.splitlines(), 1):
            stripped = line.lstrip()
            if stripped.startswith("#") or stripped.startswith("//"):
                continue
            m = forbidden.search(line)
            assert m is None, f"Forbidden token {m.group(0)!r} in {path}:{lineno}: {line.strip()}"
