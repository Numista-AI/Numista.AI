"""Regression tests for Track #3: Gemini 4 & AI Config Drift (S3-01..S3-05)."""

from __future__ import annotations

import sys
from pathlib import Path
import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import config as backend_config
from config import ingestion_config
from _scripts import check_gemini_model_updates


def test_verify_sa_key_uses_global_location_and_valid_key_name() -> None:
    """S3-01: verify_sa_key.py defaults to location='global' without us-central1 or .json.json typo."""
    text = (BACKEND_ROOT / "_scripts" / "verify_sa_key.py").read_text(encoding="utf-8")
    assert "us-central1" not in text
    assert "serviceAccountKey.json.json" not in text
    assert 'os.environ.get("GCP_REGION", "global")' in text


def test_ingestion_config_derives_from_backend_config() -> None:
    """S3-02: ingestion_config mirrors config/__init__.py and preserves FALLBACK_PRO_MODEL == gemini-4-hydrogen."""
    assert ingestion_config.CLASSIFIER_MODEL == backend_config.GEMINI_FLASH_MODEL
    assert ingestion_config.EXTRACTION_MODEL == backend_config.GEMINI_PRO_MODEL
    assert ingestion_config.FALLBACK_FLASH_MODEL == backend_config.GEMINI_LITE_MODEL
    assert ingestion_config.FALLBACK_PRO_MODEL == backend_config.GEMINI_FLASH_MODEL
    assert ingestion_config.FALLBACK_PRO_MODEL == "gemini-4-hydrogen"


def test_checklist_parser_and_scan_routes_clean_imports() -> None:
    """S3-02: checklist_parser uses CLASSIFIER_MODEL and scan_routes drops unused FALLBACK_VISION_MODEL."""
    parser_text = (BACKEND_ROOT / "services" / "checklist_parser.py").read_text(encoding="utf-8")
    assert '"classifier_model": CLASSIFIER_MODEL' in parser_text
    assert '"classifier_model": "gemini-4-hydrogen"' not in parser_text

    scan_text = (BACKEND_ROOT / "routes" / "scan_routes.py").read_text(encoding="utf-8")
    assert "FALLBACK_VISION_MODEL" not in scan_text


def test_check_gemini_model_updates_fails_closed_on_empty_pdf(monkeypatch, tmp_path: Path) -> None:
    """S3-03: audit_models exits 1 on 0 parsed rows unless allow_unparsed=True, and includes image_pro/embedding."""
    fake_pdf = tmp_path / "empty_schedule.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4\n")
    monkeypatch.setattr(check_gemini_model_updates, "parse_schedule_pdf", lambda _p: {})

    with pytest.raises(SystemExit) as exc:
        check_gemini_model_updates.audit_models(fake_pdf, auto_update=False, allow_unparsed=False)
    assert exc.value.code == 1

    # Should succeed cleanly when allow_unparsed=True
    check_gemini_model_updates.audit_models(fake_pdf, auto_update=False, allow_unparsed=True)

    script_text = (BACKEND_ROOT / "_scripts" / "check_gemini_model_updates.py").read_text(encoding="utf-8")
    assert "GEMINI_IMAGE_PRO_MODEL" in script_text
    assert "GEMINI_EMBEDDING_MODEL" in script_text
    assert "INGESTION_CLASSIFIER_MODEL" in script_text
