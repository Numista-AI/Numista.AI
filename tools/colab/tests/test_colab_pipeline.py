"""Acceptance tests AT-01..AT-10 and reviewer pilot condition checks for tools/colab."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from tools.colab.config import (
    FULL_SCALE_CU_CAP,
    FULL_TIMEOUT_SEC,
    M3_PILOT_ANNOTATION_COUNT,
    PILOT_CU_CAP,
    PILOT_TIMEOUT_SEC,
)
from tools.colab.guards import (
    GuardViolation,
    build_manifest,
    enforce_pre_run_guards,
    parse_colab_usage,
    static_credential_audit,
    verify_manifest,
)
from tools.colab.jobs.m1_framing import evaluate_framing_metrics
from tools.colab.jobs.m2_embeddings import build_advisory_flags_payload
from tools.colab.jobs.m3_cropper import validate_m3_pilot_config
from tools.colab.jobs.m4_ocr import compute_ocr_error_rate
from tools.colab.runner import run_job, run_with_timeout, verify_zero_active_sessions


def test_at01_parse_usage_and_balance_floor() -> None:
    """AT-01: Parse `colab usage` output and enforce the 500 CU hard stop floor."""
    assert parse_colab_usage("Available: 1531.77 compute units") == pytest.approx(1531.77)
    assert parse_colab_usage("Remaining balance: 499.99 CUs") == pytest.approx(499.99)

    ok = enforce_pre_run_guards(
        balance_cu=1531.77,
        cumulative_cu=0.0,
        mode="pilot",
        gpu="L4",
        model_name="BiRefNet",
        timeout_sec=PILOT_TIMEOUT_SEC,
    )
    assert ok["gpu"] == "L4"

    with pytest.raises(GuardViolation, match="balance floor"):
        enforce_pre_run_guards(
            balance_cu=499.5,
            cumulative_cu=0.0,
            mode="pilot",
            gpu="L4",
            model_name="BiRefNet",
            timeout_sec=PILOT_TIMEOUT_SEC,
        )


def test_at02_auto_shutdown_verification() -> None:
    """AT-02: Confirm 0 active sessions passes and lingering session fails."""
    assert verify_zero_active_sessions("No active sessions.", expected_session="job-m1-01") is True
    assert verify_zero_active_sessions("other-session running", expected_session="job-m1-01") is True

    with pytest.raises(GuardViolation, match="Auto-shutdown"):
        verify_zero_active_sessions("job-m1-01  L4  RUNNING", expected_session="job-m1-01")


def test_at03_and_at10_zero_credential_static_audit(tmp_path: Path) -> None:
    """AT-03 / AT-10: Zero GCP credentials, Firestore/GCS imports, or forbidden MCP literals in tools/colab."""
    colab_root = Path(__file__).resolve().parents[1]
    assert static_credential_audit(colab_root) == []

    bad_file = tmp_path / "bad_script.py"
    bad_import = ".".join(["google", "cloud", "firestore"])
    bad_key = "".join(["service", "AccountKey"])
    bad_file.write_text(f"import {bad_import}\nKEY = '{bad_key}.json'\n", encoding="utf-8")
    violations = static_credential_audit(tmp_path)
    assert len(violations) == 2


def test_at04_cu_caps_gpu_allowlist_and_wall_clock_timeout() -> None:
    """AT-04 + SAG timeout test: 25/150 CU caps, A100 blocked, and subprocess kill on timeout."""
    with pytest.raises(GuardViolation, match="Pilot CU cap"):
        enforce_pre_run_guards(
            balance_cu=1500.0,
            cumulative_cu=PILOT_CU_CAP,
            mode="pilot",
            gpu="L4",
            model_name="DINOv2",
            timeout_sec=PILOT_TIMEOUT_SEC,
        )

    with pytest.raises(GuardViolation, match="Full CU cap"):
        enforce_pre_run_guards(
            balance_cu=1500.0,
            cumulative_cu=FULL_SCALE_CU_CAP,
            mode="full",
            gpu="T4",
            model_name="DINOv2",
            timeout_sec=FULL_TIMEOUT_SEC,
        )

    with pytest.raises(GuardViolation, match="not permitted"):
        enforce_pre_run_guards(
            balance_cu=1500.0,
            cumulative_cu=0.0,
            mode="pilot",
            gpu="A100",
            model_name="DINOv2",
            timeout_sec=PILOT_TIMEOUT_SEC,
        )

    with pytest.raises(GuardViolation, match="Timeout"):
        enforce_pre_run_guards(
            balance_cu=1500.0,
            cumulative_cu=0.0,
            mode="pilot",
            gpu="L4",
            model_name="DINOv2",
            timeout_sec=PILOT_TIMEOUT_SEC + 1,
        )

    with pytest.raises(TimeoutError, match="exceeded wall-clock timeout"):
        run_with_timeout([sys.executable, "-c", "import time; time.sleep(5)"], timeout_sec=1)


def test_at05_manifest_integrity(tmp_path: Path) -> None:
    """AT-05: Manifest SHA-256 verification passes on intact files and fails on tampering."""
    artifact = tmp_path / "sample.webp"
    artifact.write_bytes(b"RIFF0000WEBP")
    manifest = build_manifest(
        job_id="pilot-m1-test",
        milestone="M1",
        mode="pilot",
        output_dir=tmp_path,
        model_name="BiRefNet",
        input_provenance=[{"source": "smithsonian", "license": "CC0"}],
    )
    assert verify_manifest(manifest) is True

    artifact.write_bytes(b"RIFF0000TAMPERED")
    assert verify_manifest(manifest) is False


def test_at06_m1_numeric_framing_ratio_standard() -> None:
    """AT-06 (Muse #1): Numerically enforce 75% target / 73% minimum framing ratio."""
    passing = evaluate_framing_metrics([
        {"image": "a.webp", "coin_diameter_px": 750, "canvas_size_px": 1000},
        {"image": "b.webp", "coin_diameter_px": 732, "canvas_size_px": 1000},
    ])
    assert passing["passed"] == 2
    assert passing["pass_rate_pct"] == pytest.approx(100.0)

    failing = evaluate_framing_metrics([
        {"image": "too_small.webp", "coin_diameter_px": 680, "canvas_size_px": 1000},
        {"image": "too_large.webp", "coin_diameter_px": 820, "canvas_size_px": 1000},
    ])
    assert failing["passed"] == 0
    assert failing["failed"] == 2


def test_at07_m2_advisory_only_flags() -> None:
    """AT-07 (Muse #4): M2 flags are advisory-only and never mutate catalog data."""
    payload = build_advisory_flags_payload([
        {
            "catalog_id": "US-1881S-MORG",
            "candidate_image": "bad.jpg",
            "reason": "wrong_mintmark",
            "similarity_score": 0.35,
        }
    ])
    assert payload["advisory_only"] is True
    assert payload["mutated_catalog"] is False
    assert payload["review_owner"] == "TRK-002 SAG/Muse Review Queue"
    assert payload["flags"][0]["auto_applied"] is False


def test_at08_m3_license_and_pinned_annotation_count() -> None:
    """AT-08 (Gemini + Muse + SAG #3): RT-DETR Apache-2.0 allowed, YOLOv11 AGPL blocked, >=150 annotations."""
    cfg = validate_m3_pilot_config(model_name="RT-DETR", annotation_count=M3_PILOT_ANNOTATION_COUNT)
    assert cfg["license"]["spdx"] == "Apache-2.0"

    with pytest.raises(GuardViolation, match="disallowed license"):
        validate_m3_pilot_config(model_name="YOLOv11", annotation_count=M3_PILOT_ANNOTATION_COUNT)

    with pytest.raises(GuardViolation, match="staged annotations"):
        validate_m3_pilot_config(model_name="RT-DETR", annotation_count=M3_PILOT_ANNOTATION_COUNT - 1)


def test_at09_m4_numeric_ocr_error_rate() -> None:
    """AT-09 (Muse #2): Hand-check >=5 pages and report numeric CER and WER."""
    refs = [
        "1881-S Morgan Dollar",
        "1893-S Morgan Dollar",
        "1909-S VDB Cent",
        "1916-D Mercury Dime",
        "1921 Peace Dollar",
    ]
    hyps = [
        "1881-S Morgan Dollar",
        "1893-S Morgan Dollar",
        "1909-S VDB Cent",
        "1916-D Mercury Dime",
        "1921 Peace Dollar",
    ]
    perfect = compute_ocr_error_rate(refs, hyps)
    assert perfect["cer"] == 0.0
    assert perfect["wer"] == 0.0

    hyps_noisy = list(hyps)
    hyps_noisy[0] = "1881-S Morgan Dollaz"
    noisy = compute_ocr_error_rate(refs, hyps_noisy)
    assert noisy["cer"] > 0.0
    assert noisy["wer"] > 0.0

    with pytest.raises(GuardViolation, match="hand-checked pages"):
        compute_ocr_error_rate(refs[:4], hyps[:4])


@pytest.mark.parametrize("milestone", ["M1", "M2", "M3", "M4"])
def test_runner_dry_run_all_milestones(tmp_path: Path, milestone: str) -> None:
    """Verify end-to-end dry-run wrapper emits verified manifest, summary.md, and cu_receipt.json."""
    out_dir = tmp_path / milestone
    manifest = run_job(
        milestone=milestone,
        mode="pilot",
        job_id=f"dry-{milestone.lower()}",
        output_dir=out_dir,
        dry_run=True,
    )
    assert verify_manifest(manifest) is True
    assert (out_dir / "cu_receipt.json").is_file()
    assert (out_dir / "summary.md").is_file()
    receipt = json.loads((out_dir / "cu_receipt.json").read_text(encoding="utf-8"))
    assert receipt["auto_shutdown_verified"] is True
