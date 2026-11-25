"""Standalone BiRefNet M1 coin framing worker for Google Colab L4 GPU.

Executes inside `/content` via `colab exec -s <job_id> -f m1_framing_remote.py`.
Must remain 100% self-contained (zero `tools.colab` imports) and hold zero GCP credentials.
"""

from __future__ import annotations

import base64
import hashlib
import html
import importlib
import io
import json
import os
import subprocess
import sys
import tarfile
import time
from pathlib import Path
from typing import Any

INPUT_TAR = Path("/content/m1_inputs.tar")
WORK_DIR = Path("/content/m1_work")
OUT_DIR = Path("/content/m1_out")
WEBP_DIR = OUT_DIR / "webp"
OUTPUT_BUNDLE = Path("/content/m1_outputs.tar.gz")

CANVAS_SIZE_PX = 1000
TARGET_FRAMING_PCT = 75.0
MIN_FRAMING_PCT = 73.0
MAX_FRAMING_PCT = 77.0
TARGET_DIAMETER_PX = 750.0

SUMMARY_BEGIN = "===M1_REMOTE_SUMMARY_BEGIN==="
SUMMARY_END = "===M1_REMOTE_SUMMARY_END==="


def _assert_zero_credentials() -> None:
    adc_key = "_".join(["GOOGLE", "APPLICATION", "CREDENTIALS"])
    key_prefix = "".join(["service", "AccountKey"])
    if os.environ.get(adc_key):
        raise RuntimeError("Forbidden cloud credential environment variable detected on Colab VM.")
    content_dir = Path("/content")
    if content_dir.exists() and list(content_dir.glob(f"*{key_prefix}*")):
        raise RuntimeError("Forbidden service key file detected in /content on Colab VM.")


def _ensure_dependencies() -> None:
    required = {
        "timm": "timm",
        "einops": "einops",
        "kornia": "kornia",
        "cv2": "opencv-python-headless",
        "PIL": "pillow",
        "transformers": "transformers",
    }
    missing = []
    for mod, pkg in required.items():
        try:
            importlib.import_module(mod)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"[m1_remote] Installing dependencies: {missing}", flush=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", *missing], check=True)


def _keep_largest_component(mask_u8: Any) -> Any:
    import cv2
    import numpy as np

    binary = (mask_u8 >= 128).astype(np.uint8)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    if num_labels <= 1:
        return mask_u8
    areas = stats[1:, cv2.CC_STAT_AREA]
    if areas.size == 0 or int(areas.max()) == 0:
        return mask_u8
    best_label = int(np.argmax(areas)) + 1
    cleaned = np.where(labels == best_label, mask_u8, 0).astype(np.uint8)
    return cleaned


def _frame_single_coin(
    *,
    src_path: Path,
    dest_webp: Path,
    model: Any,
    transform: Any,
    torch_mod: Any,
) -> dict[str, Any]:
    import numpy as np
    from PIL import Image

    with Image.open(src_path) as raw_img:
        rgb_img = raw_img.convert("RGB")
        orig_w, orig_h = rgb_img.size

    inp_tensor = transform(rgb_img).unsqueeze(0).to("cuda")
    with torch_mod.no_grad():
        with torch_mod.autocast("cuda", dtype=torch_mod.float16):
            preds = model(inp_tensor)[-1].sigmoid().cpu()

    pred = preds[0].squeeze().float()
    mask_pil = Image.fromarray((pred.numpy() * 255.0).clip(0, 255).astype(np.uint8)).resize(
        (orig_w, orig_h),
        Image.Resampling.BILINEAR,
    )
    mask_cleaned = _keep_largest_component(np.array(mask_pil, dtype=np.uint8))

    ys, xs = np.where(mask_cleaned >= 128)
    if xs.size == 0 or ys.size == 0:
        raise RuntimeError(f"Empty segmentation mask produced for {src_path.name}")

    x0, x1 = int(xs.min()), int(xs.max()) + 1
    y0, y1 = int(ys.min()), int(ys.max()) + 1

    rgba_full = rgb_img.convert("RGBA")
    rgba_full.putalpha(Image.fromarray(mask_cleaned, mode="L"))
    cropped = rgba_full.crop((x0, y0, x1, y1))

    crop_w, crop_h = cropped.size
    src_diam = float(max(crop_w, crop_h))
    scale = TARGET_DIAMETER_PX / src_diam
    new_w = max(1, int(round(crop_w * scale)))
    new_h = max(1, int(round(crop_h * scale)))
    resized = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (CANVAS_SIZE_PX, CANVAS_SIZE_PX), (0, 0, 0, 0))
    paste_x = (CANVAS_SIZE_PX - new_w) // 2
    paste_y = (CANVAS_SIZE_PX - new_h) // 2
    canvas.paste(resized, (paste_x, paste_y), resized)
    canvas.save(dest_webp, format="WEBP", quality=92, method=4)

    # Independently verify saved WebP alpha bounding box & digest
    webp_bytes = dest_webp.read_bytes()
    out_sha256 = hashlib.sha256(webp_bytes).hexdigest()
    with Image.open(dest_webp) as saved_img:
        alpha_arr = np.array(saved_img.getchannel("A"), dtype=np.uint8)
        rys, rxs = np.where(alpha_arr >= 128)
        if rxs.size == 0 or rys.size == 0:
            measured_diam = 0.0
        else:
            rw = int(rxs.max()) - int(rxs.min()) + 1
            rh = int(rys.max()) - int(rys.min()) + 1
            measured_diam = float(max(rw, rh))

        thumb = saved_img.resize((160, 160), Image.Resampling.LANCZOS)
        thumb_buf = io.BytesIO()
        thumb.save(thumb_buf, format="WEBP", quality=80)
        thumb_b64 = base64.b64encode(thumb_buf.getvalue()).decode("ascii")

    ratio_pct = round((measured_diam / float(CANVAS_SIZE_PX)) * 100.0, 2)
    passed = MIN_FRAMING_PCT <= ratio_pct <= MAX_FRAMING_PCT
    return {
        "image": dest_webp.name,
        "coin_diameter_px": measured_diam,
        "canvas_size_px": CANVAS_SIZE_PX,
        "framing_ratio_pct": ratio_pct,
        "target_pct": TARGET_FRAMING_PCT,
        "min_pct": MIN_FRAMING_PCT,
        "passed": passed,
        "output_bytes": len(webp_bytes),
        "output_sha256": out_sha256,
        "_thumb_b64": thumb_b64,
    }


def _render_contact_sheet(
    *,
    items: list[dict[str, Any]],
    total: int,
    passed: int,
    pass_rate_pct: float,
    gpu_name: str,
    elapsed_sec: float,
    out_path: Path,
) -> None:
    cards = []
    for item in items:
        badge_bg = "#166534" if item["passed"] else "#991b1b"
        status = "PASS" if item["passed"] else "FAIL"
        thumb_uri = f"data:image/webp;base64,{item['_thumb_b64']}"
        cards.append(
            "<div style='border:1px solid #d1d5db;border-radius:8px;padding:8px;background:#fff;'>"
            f"<div style='background:repeating-conic-gradient(#f3f4f6 0% 25%,#e5e7eb 0% 50%) 50%/16px 16px;"
            "border-radius:6px;display:flex;justify-content:center;align-items:center;padding:6px;'>"
            f"<img src='{thumb_uri}' width='160' height='160' alt='{html.escape(item['image'])}' />"
            "</div>"
            f"<div style='margin-top:6px;font-size:12px;font-weight:600;word-break:break-all;'>"
            f"{html.escape(item['image'])}</div>"
            "<div style='margin-top:4px;display:flex;justify-content:space-between;align-items:center;font-size:12px;'>"
            f"<span>{item['framing_ratio_pct']:.2f}% ({int(item['coin_diameter_px'])}px)</span>"
            f"<span style='background:{badge_bg};color:#fff;padding:1px 6px;border-radius:4px;font-weight:700;'>"
            f"{status}</span></div></div>"
        )

    page = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>Numista.AI M1 Framing Pilot QA Contact Sheet</title></head>"
        "<body style='font-family:system-ui,-apple-system,sans-serif;background:#f8fafc;color:#111827;padding:20px;'>"
        f"<h1>M1 Framing Pilot Visual QA ({passed}/{total} PASS &mdash; {pass_rate_pct:.2f}%)</h1>"
        f"<p>Model: <b>ZhengPeng7/BiRefNet (MIT)</b> | GPU: <b>{html.escape(gpu_name)}</b> | "
        f"Target: <b>{TARGET_FRAMING_PCT}%</b> (Allowed: <b>{MIN_FRAMING_PCT}%&ndash;{MAX_FRAMING_PCT}%</b> on {CANVAS_SIZE_PX}x{CANVAS_SIZE_PX}px WebP) | "
        f"Elapsed: <b>{elapsed_sec:.2f}s</b></p>"
        "<div style='display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:12px;'>"
        + "".join(cards)
        + "</div></body></html>\n"
    )
    out_path.write_bytes(page.encode("utf-8"))


def main() -> int:
    _assert_zero_credentials()
    if not INPUT_TAR.is_file():
        raise FileNotFoundError(f"Expected staged input archive at {INPUT_TAR}")

    _ensure_dependencies()

    import torch
    from torchvision import transforms
    from transformers import AutoModelForImageSegmentation

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is NOT available on Colab runtime; aborting M1 framing.")

    gpu_name = torch.cuda.get_device_name(0)
    vram_mib = round(torch.cuda.get_device_properties(0).total_memory / (1024 * 1024), 1)
    print(f"[m1_remote] GPU: {gpu_name} ({vram_mib} MiB)", flush=True)

    WORK_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    WEBP_DIR.mkdir(parents=True, exist_ok=True)

    with tarfile.open(INPUT_TAR, "r:*") as tf:
        tf.extractall(WORK_DIR, filter="data")

    input_manifest = json.loads((WORK_DIR / "input_manifest.json").read_text(encoding="utf-8"))
    print(f"[m1_remote] Staged input images: {len(input_manifest)}", flush=True)

    t0 = time.monotonic()
    print("[m1_remote] Loading ZhengPeng7/BiRefNet (MIT)...", flush=True)
    model = AutoModelForImageSegmentation.from_pretrained(
        "ZhengPeng7/BiRefNet",
        trust_remote_code=True,
    ).to("cuda").eval()

    transform = transforms.Compose([
        transforms.Resize((1024, 1024)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    items_full: list[dict[str, Any]] = []
    for idx, entry in enumerate(input_manifest, start=1):
        src_img = WORK_DIR / entry["staged_path"]
        stem = Path(entry["staged_path"]).stem
        dest_webp = WEBP_DIR / f"{stem}.webp"
        res = _frame_single_coin(
            src_path=src_img,
            dest_webp=dest_webp,
            model=model,
            transform=transform,
            torch_mod=torch,
        )
        res["source_relpath"] = entry["source_relpath"]
        res["original_sha256"] = entry["original_sha256"]
        items_full.append(res)
        if idx % 20 == 0 or idx == len(input_manifest):
            print(f"[m1_remote] Processed {idx}/{len(input_manifest)} ({res['image']}: {res['framing_ratio_pct']}%)", flush=True)

    elapsed_sec = round(time.monotonic() - t0, 2)
    total = len(items_full)
    passed = sum(1 for it in items_full if it["passed"])
    pass_rate_pct = round((passed / total) * 100.0, 2) if total else 0.0
    ratios = [it["framing_ratio_pct"] for it in items_full]

    contact_sheet_path = OUT_DIR / "contact_sheet.html"
    _render_contact_sheet(
        items=items_full,
        total=total,
        passed=passed,
        pass_rate_pct=pass_rate_pct,
        gpu_name=gpu_name,
        elapsed_sec=elapsed_sec,
        out_path=contact_sheet_path,
    )

    clean_items = [{k: v for k, v in it.items() if k != "_thumb_b64"} for it in items_full]
    metrics_payload = {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate_pct": pass_rate_pct,
        "target_pct": TARGET_FRAMING_PCT,
        "min_pct": MIN_FRAMING_PCT,
        "max_pct": MAX_FRAMING_PCT,
        "min_measured_pct": min(ratios) if ratios else 0.0,
        "max_measured_pct": max(ratios) if ratios else 0.0,
        "mean_measured_pct": round(sum(ratios) / len(ratios), 2) if ratios else 0.0,
        "model": "ZhengPeng7/BiRefNet",
        "license_spdx": "MIT",
        "gpu_name": gpu_name,
        "vram_total_mib": vram_mib,
        "elapsed_sec": elapsed_sec,
        "items": clean_items,
    }
    metrics_path = OUT_DIR / "framing_metrics.json"
    metrics_path.write_bytes((json.dumps(metrics_payload, indent=2) + "\n").encode("utf-8"))

    webp_tar = OUT_DIR / "m1_framed_webps.tar.gz"
    with tarfile.open(webp_tar, "w:gz") as tf:
        for wp in sorted(WEBP_DIR.glob("*.webp")):
            tf.add(wp, arcname=f"webp/{wp.name}")

    with tarfile.open(OUTPUT_BUNDLE, "w:gz") as tf:
        tf.add(webp_tar, arcname="m1_framed_webps.tar.gz")
        tf.add(metrics_path, arcname="framing_metrics.json")
        tf.add(contact_sheet_path, arcname="contact_sheet.html")

    summary = {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate_pct": pass_rate_pct,
        "min_measured_pct": metrics_payload["min_measured_pct"],
        "max_measured_pct": metrics_payload["max_measured_pct"],
        "mean_measured_pct": metrics_payload["mean_measured_pct"],
        "gpu_name": gpu_name,
        "elapsed_sec": elapsed_sec,
        "output_bundle_bytes": OUTPUT_BUNDLE.stat().st_size,
    }
    print(SUMMARY_BEGIN, flush=True)
    print(json.dumps(summary, indent=2), flush=True)
    print(SUMMARY_END, flush=True)
    return 0


if __name__ == "__main__":
    main()
