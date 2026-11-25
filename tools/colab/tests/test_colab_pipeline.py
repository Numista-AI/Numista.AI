"""Acceptance tests AT-01..AT-10 and reviewer pilot condition checks for tools/colab."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from tools.colab.config import (
    FULL_SCALE_CU_CAP,
    FULL_TIMEOUT_SEC,
    GCP_SECTION_17_CONFIRMATION,
    M2_REVIEW_OWNER,
    M3_PILOT_ANNOTATION_COUNT,
    M4_OCR_HANDCHECK_MIN_SAMPLE,
    MODEL_LICENSES,
    PILOT_CU_CAP,
    PILOT_TIMEOUT_SEC,
)
from tools.colab.guards import (
    GuardViolation,
    build_manifest,
    enforce_pre_run_guards,
    parse_colab_usage,
    static_credential_audit,
    validate_model_license,
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
    real_usage = "Current balance: 1531.77 compute units\nUsage rate: 0.00/hr\nActive assignments: 0\n"
    assert parse_colab_usage(real_usage) == pytest.approx(1531.77)

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
    assert verify_zero_active_sessions("[colab] No active sessions found on server.", expected_session="smoke-l4") is True
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
    assert cfg["license"]["promotion_allowed"] is True

    with pytest.raises(GuardViolation, match="disallowed license"):
        validate_m3_pilot_config(model_name="YOLOv11", annotation_count=M3_PILOT_ANNOTATION_COUNT)

    with pytest.raises(GuardViolation, match="staged annotations"):
        validate_m3_pilot_config(model_name="RT-DETR", annotation_count=M3_PILOT_ANNOTATION_COUNT - 1)


def test_per_model_license_registry() -> None:
    """Condition #3: Enforce per-model SPDX rules and promotion_allowed before any promotion."""
    for name in ("BiRefNet", "SAM2", "DINOv2", "SigLIP", "RT-DETR", "OlmOCR"):
        meta = validate_model_license(name)
        assert meta["commercial_ok"] is True
        assert meta["promotion_allowed"] is True

    with pytest.raises(GuardViolation, match="disallowed license"):
        validate_model_license("YOLOv11", allow_offline_gpl=True)

    for gpl_name in ("Marker", "Surya"):
        assert gpl_name in MODEL_LICENSES
        with pytest.raises(GuardViolation, match="disallowed license"):
            validate_model_license(gpl_name, allow_offline_gpl=False)
        waived = validate_model_license(gpl_name, allow_offline_gpl=True)
        assert waived["promotion_allowed"] is False


def test_at09_m4_numeric_ocr_error_rate() -> None:
    """AT-09 (Condition #2): Hand-check >=10 pages and report numeric CER and WER."""
    assert M4_OCR_HANDCHECK_MIN_SAMPLE == 10
    refs = [
        "1881-S Morgan Dollar mintage 12,760,000",
        "1893-S Morgan Dollar mintage 100,000",
        "1909-S VDB Lincoln Cent mintage 484,000",
        "1916-D Mercury Dime mintage 264,000",
        "1921 Peace Dollar High Relief mintage 1,006,473",
        "1922-D Lincoln Cent mintage 7,160,000",
        "1932-D Washington Quarter mintage 436,800",
        "1938-D Walking Liberty Half Dollar mintage 491,600",
        "1909-S Indian Head Cent mintage 309,000",
        "1895 Proof Morgan Dollar mintage 880",
    ]
    hyps = list(refs)
    perfect = compute_ocr_error_rate(refs, hyps)
    assert perfect["sample_pages_checked"] == 10
    assert perfect["cer"] == 0.0
    assert perfect["wer"] == 0.0

    hyps_noisy = list(hyps)
    hyps_noisy[0] = "1881-S Morgan Dollaz mintage 12,760,000"
    noisy = compute_ocr_error_rate(refs, hyps_noisy)
    assert noisy["cer"] > 0.0
    assert noisy["wer"] > 0.0

    with pytest.raises(GuardViolation, match="hand-checked pages"):
        compute_ocr_error_rate(refs[:9], hyps[:9])


def test_pilots_only_runtime_guard_and_section17_confirmation(tmp_path: Path) -> None:
    """PILOTS ONLY BUILD lock rejects unapproved full-scale run and pins Section 17 check."""
    assert "Section 17" in GCP_SECTION_17_CONFIRMATION
    with pytest.raises(GuardViolation, match="PILOTS ONLY"):
        run_job(
            milestone="M1",
            mode="full",
            job_id="blocked-full",
            output_dir=tmp_path / "full",
            dry_run=True,
        )


@pytest.mark.parametrize("milestone", ["SMOKE", "M1", "M2", "M3", "M4"])
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
    summary_path = out_dir / "summary.md"
    assert summary_path.is_file()
    assert GCP_SECTION_17_CONFIRMATION in summary_path.read_text(encoding="utf-8")

    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    assert manifest_data["gcp_section_17_confirmation"] == GCP_SECTION_17_CONFIRMATION
    assert manifest_data["model"]["promotion_allowed"] is True

    if milestone == "SMOKE":
        smoke_proof = json.loads((out_dir / "gpu_smoke_proof.json").read_text(encoding="utf-8"))
        assert smoke_proof["mode"] == "dry_run"
        assert smoke_proof["gcp_adc_env_absent"] is True
        assert smoke_proof["service_key_files_found"] == 0
    if milestone == "M2":
        assert manifest_data["extra"]["m2_review_owner"] == M2_REVIEW_OWNER
    if milestone == "M4":
        ocr_report = json.loads((out_dir / "ocr_error_report.json").read_text(encoding="utf-8"))
        assert ocr_report["sample_pages_checked"] == 10
        assert isinstance(ocr_report["cer"], float)
        assert isinstance(ocr_report["wer"], float)

    receipt = json.loads((out_dir / "cu_receipt.json").read_text(encoding="utf-8"))
    assert receipt["auto_shutdown_verified"] is True


def test_pack_m1_pilot_inputs_bundle(tmp_path: Path) -> None:
    """Verify M1 input packer enforces minimum image count and builds valid tar + manifest."""
    import tarfile
    from PIL import Image
    from tools.colab.jobs.m1_framing import pack_m1_pilot_inputs

    src_dir = tmp_path / "coins"
    src_dir.mkdir()
    for i in range(3):
        img = Image.new("RGB", (64, 64), (200, 200, 200))
        img.save(src_dir / f"coin_{i}.jpg", format="JPEG")

    out_tar = tmp_path / "m1.tar"
    with pytest.raises(ValueError, match="at least 100 valid images"):
        pack_m1_pilot_inputs(src_dir, out_tar, min_bytes=100, min_count=100)

    provenance = pack_m1_pilot_inputs(src_dir, out_tar, limit=3, min_bytes=100, min_count=3)
    assert len(provenance) == 3
    with tarfile.open(out_tar, "r") as tf:
        names = tf.getnames()
        assert "input_manifest.json" in names
        assert any(n.startswith("images/") for n in names)


def test_pack_m2_pilot_inputs_and_recall(tmp_path: Path) -> None:
    """Verify M2 packer builds valid tar + manifest and evaluates >=90% known-bad recall."""
    import tarfile
    from PIL import Image
    from tools.colab.jobs.m2_embeddings import (
        build_advisory_flags_payload,
        evaluate_known_bad_recall,
        pack_m2_pilot_inputs,
    )

    img_dir = tmp_path / "m2_imgs"
    img_dir.mkdir()
    records = []
    for i in range(4):
        p = img_dir / f"c_{i}.jpg"
        Image.new("RGB", (64, 64), (180, 180, 180)).save(p, format="JPEG")
        records.append({
            "path": f"m2_imgs/c_{i}.jpg",
            "catalog_id": f"CAT-{i}",
            "series_group": "morgan",
            "is_known_bad": i == 3,
            "known_bad_reason": "slabbed" if i == 3 else "",
        })

    manifest_json = tmp_path / "m2_manifest.json"
    manifest_json.write_text(json.dumps(records), encoding="utf-8")
    out_tar = tmp_path / "m2.tar"
    provenance = pack_m2_pilot_inputs(manifest_json, out_tar)
    assert len(provenance) == 4
    with tarfile.open(out_tar, "r") as tf:
        assert "input_manifest.json" in tf.getnames()

    flags = build_advisory_flags_payload([{
        "catalog_id": "CAT-3",
        "candidate_image": "m2_imgs/c_3.jpg",
        "reason": "below_threshold",
        "similarity_score": 0.42,
    }])
    passed = evaluate_known_bad_recall(flags, {"CAT-3"})
    assert passed["recall_pct"] == 100.0
    assert passed["at07_passed"] is True

    failed = evaluate_known_bad_recall(flags, {"CAT-3", "CAT-9"})
    assert failed["recall_pct"] == 50.0
    assert failed["at07_passed"] is False


def test_pack_m4_pilot_inputs_and_handcheck_scoring(tmp_path: Path) -> None:
    """Verify M4 packer builds valid tar and handcheck scorer enforces >=10 filled pages."""
    import tarfile
    from PIL import Image
    from tools.colab.jobs.m4_ocr import pack_m4_pilot_inputs, score_handcheck_file

    docs_dir = tmp_path / "mint_docs"
    docs_dir.mkdir()
    for i in range(2):
        Image.new("RGB", (64, 64), (255, 255, 255)).save(docs_dir / f"page_{i}.png", format="PNG")

    out_tar = tmp_path / "m4.tar"
    provenance = pack_m4_pilot_inputs(docs_dir, out_tar, max_pages=10)
    assert len(provenance) == 2
    with tarfile.open(out_tar, "r") as tf:
        names = tf.getnames()
        assert "input_manifest.json" in names
        assert any(n.startswith("docs/") for n in names)

    hc_path = tmp_path / "handcheck_sample_10pages.json"
    report_path = tmp_path / "ocr_error_report.json"

    rows_9 = [{"page_number": i + 1, "ocr_text": f"Mint {i}", "reference_text": f"Mint {i}"} for i in range(9)]
    hc_path.write_text(json.dumps(rows_9), encoding="utf-8")
    with pytest.raises(GuardViolation, match="hand-checked pages"):
        score_handcheck_file(hc_path, report_path)

    rows_10 = [{"page_number": i + 1, "ocr_text": f"Mint {i}", "reference_text": f"Mint {i}"} for i in range(10)]
    hc_path.write_text(json.dumps(rows_10), encoding="utf-8")
    scored = score_handcheck_file(hc_path, report_path)
    assert scored["status"] == "scored"
    assert scored["sample_pages_checked"] == 10
    assert scored["cer"] == 0.0
    assert report_path.is_file()


def test_generate_synthetic_binder_dataset_and_m3_pack(tmp_path: Path) -> None:
    """Verify M3 synthetic binder-page generator enforces >=150 annotations and writes valid COCO boxes."""
    import io
    import tarfile
    from PIL import Image, ImageDraw
    from tools.colab.jobs.m3_cropper import generate_synthetic_binder_dataset, pack_m3_pilot_inputs

    webp_tar = tmp_path / "coins.tar.gz"
    with tarfile.open(webp_tar, "w:gz") as tf:
        for i in range(4):
            im = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
            draw = ImageDraw.Draw(im)
            draw.ellipse([20, 20, 180, 180], fill=(210, 180, 90, 255))
            buf = io.BytesIO()
            im.save(buf, format="WEBP")
            raw = buf.getvalue()
            ti = tarfile.TarInfo(name=f"webp/coin_{i}.webp")
            ti.size = len(raw)
            tf.addfile(ti, io.BytesIO(raw))

    ds_dir = tmp_path / "m3_ds"
    with pytest.raises(GuardViolation, match="staged annotations"):
        generate_synthetic_binder_dataset(webp_tar, ds_dir, num_images=10, min_annotations=150)

    meta = generate_synthetic_binder_dataset(
        webp_tar,
        ds_dir,
        num_images=6,
        canvas_size=512,
        min_annotations=6,
    )
    assert meta["total_images"] == 6
    assert meta["total_boxes"] >= 24
    val_anns = json.loads((ds_dir / "val_annotations.json").read_text(encoding="utf-8"))
    for rec in val_anns:
        for ann in rec["annotations"]:
            bx, by, bw, bh = ann["bbox"]
            assert 0 <= bx and 0 <= by and bx + bw <= 512 and by + bh <= 512

    out_tar = tmp_path / "m3_inputs.tar"
    prov = pack_m3_pilot_inputs(ds_dir, out_tar, min_annotations=6)
    assert prov[0]["total_images"] == 6
    with tarfile.open(out_tar, "r") as tf:
        names = tf.getnames()
        assert "dataset_meta.json" in names
        assert "train_annotations.json" in names
        assert "val_annotations.json" in names

    # Verify FRASER URL page-pack schema for M4
    from tools.colab.jobs.m4_ocr import pack_m4_pilot_inputs
    fraser_json = tmp_path / "fraser_pack.json"
    fraser_json.write_text(json.dumps({
        "pack_name": "test_fraser",
        "pages": [{
            "seq": 1,
            "pdf_url": "https://fraser.stlouisfed.org/files/docs/publications/books/1974_domesticforeigncoins_usmint.pdf",
            "pdf_page": 34,
            "printed_page": "30",
            "doc_title": "1974 Mint Pamphlet",
            "ground_truth_anchor": "3,403",
        }],
    }), encoding="utf-8")
    m4_url_tar = tmp_path / "m4_urls.tar"
    m4_prov = pack_m4_pilot_inputs(fraser_json, m4_url_tar, max_pages=20)
    assert len(m4_prov) == 1
    assert m4_prov[0]["pdf_page"] == 34
    with tarfile.open(m4_url_tar, "r") as tf:
        assert "input_manifest.json" in tf.getnames()
