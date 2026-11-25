"""M3 — Specialized Coin / Binder-Page / Mintmark Cropper Training.

Enforces Gemini/Muse/SAG conditions:
- Defaults to Apache-2.0 RT-DETR (blocks AGPL-3.0 YOLOv11).
- Pins M3 pilot annotation count (>= 150) before training starts.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import random
import tarfile
from pathlib import Path
from typing import Any

from tools.colab.config import M3_DEFAULT_MODEL, M3_PILOT_ANNOTATION_COUNT
from tools.colab.guards import GuardViolation, build_manifest, validate_model_license


_BG_PALETTES: tuple[tuple[int, int, int], ...] = (
    (36, 40, 48),     # charcoal velvet
    (28, 44, 72),     # navy display tray
    (232, 224, 206),  # cream 2x2 binder page
    (74, 82, 92),     # neutral slate mat
    (118, 86, 56),    # warm wood desk
)


def _extract_tight_coins(webp_tar_gz: Path) -> tuple[str, list[Any]]:
    from PIL import Image

    archive_sha256 = hashlib.sha256(webp_tar_gz.read_bytes()).hexdigest()
    coins: list[Any] = []
    with tarfile.open(webp_tar_gz, "r:*") as tf:
        for member in sorted(tf.getmembers(), key=lambda m: m.name):
            if not member.isfile() or not member.name.lower().endswith(".webp"):
                continue
            fh = tf.extractfile(member)
            if fh is None:
                continue
            raw = fh.read()
            with Image.open(io.BytesIO(raw)) as im:
                rgba = im.convert("RGBA")
                alpha = rgba.getchannel("A")
                bbox = alpha.point(lambda p: 255 if p >= 128 else 0).getbbox()
                if bbox is None:
                    continue
                coins.append(rgba.crop(bbox).copy())
    if not coins:
        raise ValueError(f"No valid transparent coin WebPs found in {webp_tar_gz}")
    return archive_sha256, coins


def _render_binder_background(canvas_size: int, bg_rgb: tuple[int, int, int], draw_grid: tuple[int, int] | None) -> Any:
    from PIL import Image, ImageDraw

    bg = Image.new("RGB", (canvas_size, canvas_size), bg_rgb)
    if draw_grid is not None:
        cols, rows = draw_grid
        draw = ImageDraw.Draw(bg)
        line_color = tuple(max(0, min(255, c + (32 if sum(bg_rgb) < 380 else -32))) for c in bg_rgb)
        for c in range(1, cols):
            x = int(round(c * canvas_size / cols))
            draw.line([(x, 0), (x, canvas_size)], fill=line_color, width=2)
        for r in range(1, rows):
            y = int(round(r * canvas_size / rows))
            draw.line([(0, y), (canvas_size, y)], fill=line_color, width=2)
    return bg


def generate_synthetic_binder_dataset(
    webp_tar_gz: Path,
    out_dir: Path,
    *,
    num_images: int = 180,
    val_ratio: float = 0.2,
    canvas_size: int = 1024,
    seed: int = 42,
    min_annotations: int = M3_PILOT_ANNOTATION_COUNT,
) -> dict[str, Any]:
    """Generate multi-coin binder/tray composite pages with exact COCO coin bboxes."""
    from PIL import Image

    validate_m3_pilot_config(
        model_name=M3_DEFAULT_MODEL,
        annotation_count=num_images,
        min_annotations=min_annotations,
    )
    if not webp_tar_gz.is_file():
        raise FileNotFoundError(f"M1 framed WebP archive not found: {webp_tar_gz}")

    source_sha256, coins = _extract_tight_coins(webp_tar_gz)
    rng = random.Random(seed)
    layouts: tuple[tuple[int, int], ...] = ((3, 2), (3, 3), (4, 3), (4, 4))

    val_count = max(1, int(round(num_images * val_ratio)))
    train_count = num_images - val_count

    train_dir = out_dir / "train"
    val_dir = out_dir / "val"
    train_dir.mkdir(parents=True, exist_ok=True)
    val_dir.mkdir(parents=True, exist_ok=True)

    train_records: list[dict[str, Any]] = []
    val_records: list[dict[str, Any]] = []
    total_boxes = 0

    for idx in range(num_images):
        is_val = idx >= train_count
        split_name = "val" if is_val else "train"
        rel_name = f"{split_name}/page_{idx + 1:04d}.jpg"
        cols, rows = rng.choice(layouts)
        bg_rgb = rng.choice(_BG_PALETTES)
        grid = (cols, rows) if rng.random() < 0.7 else None
        canvas = _render_binder_background(canvas_size, bg_rgb, grid).convert("RGBA")

        cell_w = canvas_size / cols
        cell_h = canvas_size / rows
        slots = [(c, r) for r in range(rows) for c in range(cols)]
        drop_n = rng.randint(0, min(2, len(slots) - 4))
        if drop_n > 0:
            slots = rng.sample(slots, k=len(slots) - drop_n)

        boxes: list[list[float]] = []
        for col, row in slots:
            coin = rng.choice(coins)
            angle = rng.uniform(-180.0, 180.0)
            rotated = coin.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
            rbbox = rotated.getchannel("A").point(lambda p: 255 if p >= 128 else 0).getbbox()
            if rbbox is None:
                continue
            rotated = rotated.crop(rbbox)

            rw, rh = rotated.size
            max_side = min(cell_w, cell_h) * rng.uniform(0.65, 0.90)
            scale = max_side / float(max(rw, rh))
            nw = max(8, int(round(rw * scale)))
            nh = max(8, int(round(rh * scale)))
            resized = rotated.resize((nw, nh), Image.Resampling.LANCZOS)

            margin_x = max(0, int(cell_w) - nw)
            margin_y = max(0, int(cell_h) - nh)
            px = int(round(col * cell_w)) + rng.randint(0, margin_x)
            py = int(round(row * cell_h)) + rng.randint(0, margin_y)
            px = max(0, min(canvas_size - nw, px))
            py = max(0, min(canvas_size - nh, py))

            # Subtle shadow beneath coin
            shadow_alpha = resized.getchannel("A").point(lambda p: int(p * 0.35))
            shadow = Image.new("RGBA", (nw, nh), (0, 0, 0, 0))
            shadow.putalpha(shadow_alpha)
            sx = min(canvas_size - nw, px + 3)
            sy = min(canvas_size - nh, py + 4)
            canvas.paste(shadow, (sx, sy), shadow)
            canvas.paste(resized, (px, py), resized)

            boxes.append([float(px), float(py), float(nw), float(nh)])

        canvas.convert("RGB").save(out_dir / rel_name, format="JPEG", quality=92)
        total_boxes += len(boxes)
        rec = {
            "image_id": idx + 1,
            "file_name": rel_name,
            "width": canvas_size,
            "height": canvas_size,
            "annotations": [{"bbox": b, "category_id": 0} for b in boxes],
        }
        (val_records if is_val else train_records).append(rec)

    (out_dir / "train_annotations.json").write_bytes((json.dumps(train_records, indent=2) + "\n").encode("utf-8"))
    (out_dir / "val_annotations.json").write_bytes((json.dumps(val_records, indent=2) + "\n").encode("utf-8"))

    meta = {
        "total_images": num_images,
        "train_images": len(train_records),
        "val_images": len(val_records),
        "total_boxes": total_boxes,
        "canvas_size": canvas_size,
        "model": M3_DEFAULT_MODEL,
        "spdx": "Apache-2.0",
        "source_archive": webp_tar_gz.name,
        "source_archive_sha256": source_sha256,
    }
    (out_dir / "dataset_meta.json").write_bytes((json.dumps(meta, indent=2) + "\n").encode("utf-8"))
    return meta


def pack_m3_pilot_inputs(
    dataset_dir: Path,
    out_tar: Path,
    *,
    min_annotations: int = M3_PILOT_ANNOTATION_COUNT,
) -> list[dict[str, Any]]:
    """Validate and pack M3 labeled binder dataset into a tar archive for Colab training."""
    meta_path = dataset_dir / "dataset_meta.json"
    if not meta_path.is_file():
        raise FileNotFoundError(f"Expected dataset_meta.json in {dataset_dir}")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    validate_m3_pilot_config(
        model_name=M3_DEFAULT_MODEL,
        annotation_count=int(meta["total_images"]),
        min_annotations=min_annotations,
    )

    out_tar.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(out_tar, "w") as tf:
        for fname in ("dataset_meta.json", "train_annotations.json", "val_annotations.json"):
            fpath = dataset_dir / fname
            if not fpath.is_file():
                raise FileNotFoundError(f"Missing M3 annotation file: {fpath}")
            tf.add(fpath, arcname=fname)
        for split in ("train", "val"):
            split_dir = dataset_dir / split
            for img_path in sorted(split_dir.glob("*.jpg")):
                tf.add(img_path, arcname=f"{split}/{img_path.name}")

    return [{
        "dataset_dir": dataset_dir.name,
        "total_images": meta["total_images"],
        "total_boxes": meta["total_boxes"],
        "source_archive_sha256": meta["source_archive_sha256"],
    }]


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
