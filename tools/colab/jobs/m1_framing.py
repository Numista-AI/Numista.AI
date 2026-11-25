"""M1 — Museum-Grade Catalog Coin Framing & Cleanup (BiRefNet / SAM2).

Enforces Muse pilot condition #1: numerically measure and validate the
75% target / 73% minimum coin framing ratio on every output and record
pass/fail metrics in framing_metrics.json and contact_sheet.html.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import re
import tarfile
from pathlib import Path
from typing import Any

from tools.colab.config import M1_FRAMING_MAX_PCT, M1_FRAMING_MIN_PCT, M1_FRAMING_TARGET_PCT
from tools.colab.guards import build_manifest


_IMAGE_EXTS: tuple[str, ...] = (".jpg", ".jpeg", ".png", ".webp")


def pack_m1_pilot_inputs(
    source_dir: Path,
    out_tar: Path,
    *,
    limit: int = 120,
    min_bytes: int = 20_000,
    max_side_px: int = 1280,
    min_count: int = 100,
) -> list[dict[str, Any]]:
    """Deterministically pack up to `limit` coin images into a tar bundle for Colab M1."""
    from PIL import Image

    if not source_dir.is_dir():
        raise FileNotFoundError(f"M1 input directory does not exist: {source_dir}")

    candidates = [
        p
        for p in sorted(source_dir.rglob("*"))
        if p.is_file() and p.suffix.lower() in _IMAGE_EXTS and p.stat().st_size >= min_bytes
    ]
    selected = candidates[:limit]
    if len(selected) < min_count:
        raise ValueError(
            f"M1 pilot requires at least {min_count} valid images (>= {min_bytes} B); found {len(selected)} in {source_dir}."
        )

    out_tar.parent.mkdir(parents=True, exist_ok=True)
    manifest_entries: list[dict[str, Any]] = []
    provenance: list[dict[str, Any]] = []
    seen_stems: dict[str, int] = {}

    with tarfile.open(out_tar, "w") as tf:
        for src in selected:
            raw_bytes = src.read_bytes()
            orig_sha256 = hashlib.sha256(raw_bytes).hexdigest()
            relpath = src.relative_to(source_dir).as_posix()

            safe_stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", src.stem).strip("._") or "coin"
            idx_num = seen_stems.get(safe_stem.lower(), 0)
            seen_stems[safe_stem.lower()] = idx_num + 1
            if idx_num > 0:
                safe_stem = f"{safe_stem}_{idx_num}"

            buf = io.BytesIO()
            with Image.open(io.BytesIO(raw_bytes)) as img:
                rgb_or_rgba = img.convert("RGBA" if "A" in img.getbands() else "RGB")
                if max(rgb_or_rgba.size) > max_side_px:
                    rgb_or_rgba.thumbnail((max_side_px, max_side_px), Image.Resampling.LANCZOS)
                ext = ".png" if rgb_or_rgba.mode == "RGBA" else ".jpg"
                if ext == ".png":
                    rgb_or_rgba.save(buf, format="PNG")
                else:
                    rgb_or_rgba.save(buf, format="JPEG", quality=95)

            staged_rel = f"images/{safe_stem}{ext}"
            staged_bytes = buf.getvalue()
            info = tarfile.TarInfo(name=staged_rel)
            info.size = len(staged_bytes)
            tf.addfile(info, io.BytesIO(staged_bytes))

            manifest_entries.append({
                "staged_path": staged_rel,
                "source_relpath": relpath,
                "original_sha256": orig_sha256,
                "source": source_dir.name,
                "license": "US Mint / Eric local archive",
            })
            provenance.append({
                "source_relpath": relpath,
                "original_sha256": orig_sha256,
            })

        manifest_bytes = (json.dumps(manifest_entries, indent=2) + "\n").encode("utf-8")
        minfo = tarfile.TarInfo(name="input_manifest.json")
        minfo.size = len(manifest_bytes)
        tf.addfile(minfo, io.BytesIO(manifest_bytes))

    return provenance


def compute_framing_ratio_pct(coin_diameter_px: float, canvas_size_px: float) -> float:
    """Compute coin diameter as a percentage of square canvas width."""
    if canvas_size_px <= 0 or coin_diameter_px <= 0:
        raise ValueError("Canvas and coin diameter must be positive.")
    return round((coin_diameter_px / canvas_size_px) * 100.0, 2)


def evaluate_framing_metrics(
    measurements: list[dict[str, Any]],
    *,
    min_pct: float = M1_FRAMING_MIN_PCT,
    max_pct: float = M1_FRAMING_MAX_PCT,
) -> dict[str, Any]:
    """Evaluate per-image framing ratios against the 73%-77% (75% target) standard."""
    if not measurements:
        raise ValueError("No framing measurements provided.")

    evaluated: list[dict[str, Any]] = []
    passed = 0
    for item in measurements:
        ratio = compute_framing_ratio_pct(
            float(item["coin_diameter_px"]),
            float(item["canvas_size_px"]),
        )
        ok = min_pct <= ratio <= max_pct
        if ok:
            passed += 1
        evaluated.append({
            "image": str(item["image"]),
            "coin_diameter_px": float(item["coin_diameter_px"]),
            "canvas_size_px": float(item["canvas_size_px"]),
            "framing_ratio_pct": ratio,
            "target_pct": M1_FRAMING_TARGET_PCT,
            "min_pct": min_pct,
            "passed": ok,
        })

    total = len(evaluated)
    pass_rate_pct = round((passed / total) * 100.0, 2)
    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate_pct": pass_rate_pct,
        "target_pct": M1_FRAMING_TARGET_PCT,
        "min_pct": min_pct,
        "max_pct": max_pct,
        "items": evaluated,
    }


def render_contact_sheet_html(report: dict[str, Any], out_path: Path) -> Path:
    """Write a lightweight HTML visual QA contact sheet with numeric framing ratios."""
    rows = []
    for item in report["items"]:
        status = "PASS" if item["passed"] else "FAIL"
        rows.append(
            f"<tr><td>{html.escape(item['image'])}</td>"
            f"<td>{item['framing_ratio_pct']:.2f}%</td>"
            f"<td>{status}</td></tr>"
        )
    body = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>M1 Contact Sheet QA</title></head><body>"
        f"<h1>M1 Framing QA ({report['passed']}/{report['total']} PASS, "
        f"target {report['target_pct']}%, min {report['min_pct']}%)</h1>"
        "<table border='1' cellpadding='6'>"
        "<tr><th>Image</th><th>Framing Ratio</th><th>Status</th></tr>"
        + "".join(rows)
        + "</table></body></html>\n"
    )
    out_path.write_bytes(body.encode("utf-8"))
    return out_path


def run_pilot_dry_run(output_dir: Path, job_id: str) -> Path:
    """Generate deterministic M1 dry-run artifacts for local validation."""
    output_dir.mkdir(parents=True, exist_ok=True)
    sample = [
        {"image": "morgan_1881_s_obv.webp", "coin_diameter_px": 750, "canvas_size_px": 1000},
        {"image": "morgan_1881_s_rev.webp", "coin_diameter_px": 732, "canvas_size_px": 1000},
    ]
    report = evaluate_framing_metrics(sample)
    metrics_path = output_dir / "framing_metrics.json"
    metrics_path.write_bytes((json.dumps(report, indent=2) + "\n").encode("utf-8"))
    render_contact_sheet_html(report, output_dir / "contact_sheet.html")
    return build_manifest(
        job_id=job_id,
        milestone="M1",
        mode="pilot",
        output_dir=output_dir,
        model_name="BiRefNet",
        input_provenance=[{"source": "dry-run-fixture", "license": "CC0"}],
        extra_meta={"framing_pass_rate_pct": report["pass_rate_pct"]},
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="M1 Catalog Coin Framing & Cleanup")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        manifest = run_pilot_dry_run(args.output_dir, args.job_id)
        print(f"M1 dry-run manifest written: {manifest}")
        return 0
    raise NotImplementedError("Live GPU execution runs inside Colab via `colab run`.")


if __name__ == "__main__":
    raise SystemExit(main())
