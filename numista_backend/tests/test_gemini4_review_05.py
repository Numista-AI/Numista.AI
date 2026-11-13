"""Regression tests for Review #5: AI Stack Gemini 4 Upgrade Audit (G5-01..G5-03)."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from google.api_core.exceptions import DeadlineExceeded, ServiceUnavailable

from numista_backend.config import GEMINI_IMAGE_MODEL, GEMINI_IMAGE_PRO_MODEL
from numista_backend.config import ingestion_config
from numista_backend.services import image_model_router as router


def test_ingestion_config_fallback_pro_model_is_gemini_4():
    assert ingestion_config.FALLBACK_PRO_MODEL == "gemini-4-hydrogen"
    assert "3.1-pro-preview" not in ingestion_config.FALLBACK_PRO_MODEL


def test_reserve_image_model_fails_open_on_firestore_error():
    db = MagicMock()
    db.transaction.side_effect = ServiceUnavailable("Firestore unavailable")

    selected, count, reserved, mkey = router.reserve_image_model(
        db, month_key="2026-11"
    )
    assert selected == GEMINI_IMAGE_MODEL
    assert count == 0
    assert reserved is False
    assert mkey == "2026-11"


def test_execute_with_image_routing_fails_open_on_reserve_error():
    db = MagicMock()
    db.transaction.side_effect = ServiceUnavailable("Firestore unavailable")
    called_models = []

    def _call_fn(model_id: str) -> str:
        called_models.append(model_id)
        return f"img:{model_id}"

    result, used_model = router.execute_with_image_routing(
        db, _call_fn, month_key="2026-11"
    )
    assert called_models == [GEMINI_IMAGE_MODEL]
    assert used_model == GEMINI_IMAGE_MODEL
    assert result == f"img:{GEMINI_IMAGE_MODEL}"


def test_execute_with_image_routing_handles_nested_pro_and_release_failure(monkeypatch):
    db = MagicMock()
    monkeypatch.setattr(router, "_reserve_pro_slot_tx", lambda tx, ref, cap: (True, 1))
    monkeypatch.setattr(
        router,
        "_release_pro_slot_tx",
        MagicMock(side_effect=DeadlineExceeded("timeout")),
    )

    called_models = []

    def _call_fn(model_id: str) -> str:
        called_models.append(model_id)
        if model_id == GEMINI_IMAGE_PRO_MODEL:
            raise RuntimeError("Pro API error")
        return "ok"

    result, used_model = router.execute_with_image_routing(
        db, _call_fn, month_key="2026-11"
    )
    assert called_models == [GEMINI_IMAGE_PRO_MODEL, GEMINI_IMAGE_MODEL]
    assert result == "ok"
    assert used_model == GEMINI_IMAGE_MODEL


def test_reserve_image_model_does_not_swallow_non_transient_bug(monkeypatch):
    db = MagicMock()
    monkeypatch.setattr(
        router, "_reserve_pro_slot_tx", MagicMock(side_effect=KeyError("bug"))
    )

    with pytest.raises(KeyError):
        router.reserve_image_model(db, month_key="2026-11")


def test_verification_scripts_do_not_hardcode_gemini_35_flash():
    scripts_dir = Path(__file__).resolve().parents[1] / "_scripts"
    for name in ("verify_sa_key.py", "verify_vertex_model.py"):
        text = (scripts_dir / name).read_text(encoding="utf-8")
        assert "gemini-3.5-flash" not in text, f"{name} still references gemini-3.5-flash"
