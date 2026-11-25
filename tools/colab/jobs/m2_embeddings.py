"""M2 — Visual Embedding Wrong-Coin / Slab / Privy Audit (DINOv2 / SigLIP).

Enforces Muse pilot condition #4: M2 flags are strictly advisory-only and
route to the TRK-002 SAG/Muse Review Queue. A flag never mutates any catalog image.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import tarfile
from pathlib import Path
from typing import Any

from tools.colab.config import M2_REVIEW_OWNER
from tools.colab.guards import build_manifest


_IMAGE_EXTS: tuple[str, ...] = (".jpg", ".jpeg", ".png", ".webp")


def _parse_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() in ("1", "true", "yes", "y")


def pack_m2_pilot_inputs(
    manifest_path: Path,
    out_tar: Path,
    *,
    limit: int = 500,
    max_side_px: int = 518,
) -> list[dict[str, Any]]:
    """Pack curated M2 catalog/candidate images and seeded known-bad flags into a tar bundle."""
    from PIL import Image

    if not manifest_path.is_file():
        raise FileNotFoundError(f"M2 input manifest file not found: {manifest_path}")

    if manifest_path.suffix.lower() == ".csv":
        with manifest_path.open("r", encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
    else:
        loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(loaded, list):
            raise ValueError("M2 JSON manifest must be a list of image records.")
        rows = loaded

    selected = rows[:limit]
    if not selected:
        raise ValueError(f"M2 input manifest is empty: {manifest_path}")

    out_tar.parent.mkdir(parents=True, exist_ok=True)
    staged_entries: list[dict[str, Any]] = []
    provenance: list[dict[str, Any]] = []
    seen_stems: dict[str, int] = {}

    with tarfile.open(out_tar, "w") as tf:
        for row in selected:
            raw_path = Path(str(row["path"]))
            src = raw_path if raw_path.is_absolute() else (manifest_path.parent / raw_path)
            if not src.is_file() or src.suffix.lower() not in _IMAGE_EXTS:
                raise FileNotFoundError(f"Invalid or missing M2 input image: {src}")

            raw_bytes = src.read_bytes()
            orig_sha256 = hashlib.sha256(raw_bytes).hexdigest()
            cat_id = str(row["catalog_id"])
            safe_stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", f"{cat_id}_{src.stem}").strip("._") or "coin"
            count = seen_stems.get(safe_stem.lower(), 0)
            seen_stems[safe_stem.lower()] = count + 1
            if count > 0:
                safe_stem = f"{safe_stem}_{count}"

            buf = io.BytesIO()
            with Image.open(io.BytesIO(raw_bytes)) as img:
                rgb_img = img.convert("RGB")
                if max(rgb_img.size) > max_side_px:
                    rgb_img.thumbnail((max_side_px, max_side_px), Image.Resampling.LANCZOS)
                rgb_img.save(buf, format="JPEG", quality=92)

            staged_rel = f"images/{safe_stem}.jpg"
            staged_bytes = buf.getvalue()
            tinfo = tarfile.TarInfo(name=staged_rel)
            tinfo.size = len(staged_bytes)
            tf.addfile(tinfo, io.BytesIO(staged_bytes))

            staged_entries.append({
                "staged_path": staged_rel,
                "catalog_id": cat_id,
                "series_group": str(row.get("series_group") or "default"),
                "source_relpath": str(row["path"]),
                "original_sha256": orig_sha256,
                "is_known_bad": _parse_bool(row.get("is_known_bad", False)),
                "known_bad_reason": str(row.get("known_bad_reason") or ""),
            })
            provenance.append({
                "catalog_id": cat_id,
                "source_relpath": str(row["path"]),
                "original_sha256": orig_sha256,
            })

        mbytes = (json.dumps(staged_entries, indent=2) + "\n").encode("utf-8")
        minfo = tarfile.TarInfo(name="input_manifest.json")
        minfo.size = len(mbytes)
        tf.addfile(minfo, io.BytesIO(mbytes))

    return provenance


def evaluate_known_bad_recall(
    flags_payload: dict[str, Any],
    known_bad_ids: set[str],
    *,
    min_recall_pct: float = 90.0,
) -> dict[str, Any]:
    """Compute recall on seeded known-bad/slabbed controls against AT-07 (>=90%)."""
    if not known_bad_ids:
        raise ValueError("known_bad_ids must be non-empty for AT-07 recall evaluation.")
    flagged_ids = {str(f["catalog_id"]) for f in flags_payload.get("flags", [])}
    recalled = len(known_bad_ids & flagged_ids)
    recall_pct = round((recalled / len(known_bad_ids)) * 100.0, 2)
    return {
        "seeded_known_bad_total": len(known_bad_ids),
        "seeded_known_bad_recalled": recalled,
        "recall_pct": recall_pct,
        "min_recall_pct": min_recall_pct,
        "at07_passed": recall_pct >= min_recall_pct,
    }


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
