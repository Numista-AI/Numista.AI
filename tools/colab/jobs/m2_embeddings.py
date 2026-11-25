"""M2 — Visual Embedding Wrong-Coin / Slab / Privy Audit (DINOv2 / SigLIP).

Enforces Muse pilot condition #4: M2 flags are strictly advisory-only and
route to the TRK-002 SAG/Muse Review Queue. A flag never mutates any catalog image.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.colab.config import M2_REVIEW_OWNER
from tools.colab.guards import build_manifest


def build_advisory_flags_payload(flags: list[dict[str, Any]]) -> dict[str, Any]:
    """Wrap embedding audit flags with mandatory advisory-only governance fields."""
    normalized: list[dict[str, Any]] = []
    for item in flags:
        normalized.append({
            "catalog_id": str(item["catalog_id"]),
            "candidate_image": str(item["candidate_image"]),
            "reason": str(item["reason"]),
            "similarity_score": round(float(item["similarity_score"]), 4),
            "action": "review_only",
            "auto_applied": False,
        })

    return {
        "advisory_only": True,
        "mutated_catalog": False,
        "review_owner": M2_REVIEW_OWNER,
        "flag_count": len(normalized),
        "flags": normalized,
    }


def run_pilot_dry_run(output_dir: Path, job_id: str) -> Path:
    """Generate deterministic M2 dry-run advisory flags and manifest."""
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = build_advisory_flags_payload([
        {
            "catalog_id": "US-1999-SQ-DE",
            "candidate_image": "wikimedia_slab_mismatch.jpg",
            "reason": "slabbed_or_wrong_state_quarter",
            "similarity_score": 0.41,
        }
    ])
    (output_dir / "advisory_flags.json").write_bytes((json.dumps(payload, indent=2) + "\n").encode("utf-8"))
    return build_manifest(
        job_id=job_id,
        milestone="M2",
        mode="pilot",
        output_dir=output_dir,
        model_name="DINOv2",
        input_provenance=[{"source": "dry-run-fixture", "license": "CC0"}],
        extra_meta={"advisory_only": True, "review_owner": M2_REVIEW_OWNER},
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="M2 Visual Embedding Audit")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        manifest = run_pilot_dry_run(args.output_dir, args.job_id)
        print(f"M2 dry-run manifest written: {manifest}")
        return 0
    raise NotImplementedError("Live GPU execution runs inside Colab via `colab run`.")


if __name__ == "__main__":
    raise SystemExit(main())
