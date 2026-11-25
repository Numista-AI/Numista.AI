"""M3 — Specialized Coin / Binder-Page / Mintmark Cropper Training.

Enforces Gemini/Muse/SAG conditions:
- Defaults to Apache-2.0 RT-DETR (blocks AGPL-3.0 YOLOv11).
- Pins M3 pilot annotation count (>= 150) before training starts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.colab.config import M3_DEFAULT_MODEL, M3_PILOT_ANNOTATION_COUNT
from tools.colab.guards import GuardViolation, build_manifest, validate_model_license


def validate_m3_pilot_config(
    *,
    model_name: str = M3_DEFAULT_MODEL,
    annotation_count: int,
    min_annotations: int = M3_PILOT_ANNOTATION_COUNT,
) -> dict[str, Any]:
    """Validate model license and minimum pinned annotation count for M3 pilot."""
    license_meta = validate_model_license(model_name, allow_offline_gpl=False)
    if annotation_count < min_annotations:
        raise GuardViolation(
            f"M3 pilot requires at least {min_annotations} staged annotations; got {annotation_count}."
        )
    return {
        "model": model_name,
        "license": license_meta,
        "annotation_count": annotation_count,
        "min_annotations": min_annotations,
    }


def run_pilot_dry_run(output_dir: Path, job_id: str, annotation_count: int = M3_PILOT_ANNOTATION_COUNT) -> Path:
    """Validate M3 pilot config and emit eval stub + manifest for local testing."""
    cfg = validate_m3_pilot_config(model_name=M3_DEFAULT_MODEL, annotation_count=annotation_count)
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics = {
        "model": cfg["model"],
        "spdx": cfg["license"]["spdx"],
        "annotation_count": annotation_count,
        "mAP50": 0.0,
        "status": "dry_run_validated",
    }
    (output_dir / "eval_metrics.json").write_bytes((json.dumps(metrics, indent=2) + "\n").encode("utf-8"))
    return build_manifest(
        job_id=job_id,
        milestone="M3",
        mode="pilot",
        output_dir=output_dir,
        model_name=M3_DEFAULT_MODEL,
        input_provenance=[{"source": "dry-run-annotations", "count": annotation_count}],
        extra_meta={"annotation_count": annotation_count},
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="M3 Coin/Mintmark Cropper Trainer")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--annotation-count", type=int, default=M3_PILOT_ANNOTATION_COUNT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        manifest = run_pilot_dry_run(args.output_dir, args.job_id, args.annotation_count)
        print(f"M3 dry-run manifest written: {manifest}")
        return 0
    raise NotImplementedError("Live GPU execution runs inside Colab via `colab run`.")


if __name__ == "__main__":
    raise SystemExit(main())
