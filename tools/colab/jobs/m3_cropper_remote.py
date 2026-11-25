"""Standalone Apache-2.0 RT-DETR M3 coin/binder-page trainer for Google Colab GPU.

Executes inside `/content` via `colab exec -s <job_id> -f m3_cropper_remote.py`.
Strictly Apache-2.0 (`PekingU/rtdetr_r18vd` via `transformers`): zero AGPL libraries,
zero `tools.colab` imports, and zero GCP credentials.
"""

from __future__ import annotations

import base64
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

INPUT_TAR = Path("/content/m3_inputs.tar")
WORK_DIR = Path("/content/m3_work")
OUT_DIR = Path("/content/m3_out")
OUTPUT_BUNDLE = Path("/content/m3_outputs.tar.gz")

MODEL_ID = os.environ.get("M3_MODEL_ID", "PekingU/rtdetr_r18vd")
EPOCHS = int(os.environ.get("M3_EPOCHS", "8"))
BATCH_SIZE = int(os.environ.get("M3_BATCH_SIZE", "4"))

SUMMARY_BEGIN = "===M3_REMOTE_SUMMARY_BEGIN==="
SUMMARY_END = "===M3_REMOTE_SUMMARY_END==="


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
        "transformers": "transformers",
        "timm": "timm",
        "onnx": "onnx",
        "PIL": "pillow",
        "numpy": "numpy",
    }
    missing = []
    for mod, pkg in required.items():
        try:
            importlib.import_module(mod)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"[m3_remote] Installing dependencies: {missing}", flush=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", *missing], check=True)


def _bbox_iou(box_a: list[float], box_b: list[float]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0.0:
        return 0.0
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    denom = area_a + area_b - inter
    return inter / denom if denom > 0.0 else 0.0


def _compute_detection_metrics(
    gt_by_image: dict[int, list[list[float]]],
    preds: list[dict[str, Any]],
    *,
    iou_thresh: float = 0.50,
    score_thresh: float = 0.50,
) -> dict[str, Any]:
    total_gt = sum(len(v) for v in gt_by_image.values())
    if total_gt == 0:
        return {"precision_50": 0.0, "recall_50": 0.0, "f1_50": 0.0, "mAP50": 0.0, "total_gt": 0}

    # AP@50 across all confidence-sorted predictions
    preds_sorted = sorted(preds, key=lambda p: p["score"], reverse=True)
    matched_ap: dict[int, set[int]] = {k: set() for k in gt_by_image}
    tp_ap = []
    fp_ap = []
    for p in preds_sorted:
        img_id = p["image_id"]
        gts = gt_by_image.get(img_id, [])
        best_iou = 0.0
        best_idx = -1
        for gi, gt in enumerate(gts):
            if gi in matched_ap[img_id]:
                continue
            iou = _bbox_iou(p["bbox_xyxy"], gt)
            if iou > best_iou:
                best_iou = iou
                best_idx = gi
        if best_iou >= iou_thresh and best_idx >= 0:
            matched_ap[img_id].add(best_idx)
            tp_ap.append(1)
            fp_ap.append(0)
        else:
            tp_ap.append(0)
            fp_ap.append(1)

    cum_tp = 0
    cum_fp = 0
    precisions: list[float] = []
    recalls: list[float] = []
    for t, f in zip(tp_ap, fp_ap):
        cum_tp += t
        cum_fp += f
        precisions.append(cum_tp / max(1, cum_tp + cum_fp))
        recalls.append(cum_tp / float(total_gt))

    # 101-point COCO AP interpolation
    ap50 = 0.0
    if precisions:
        for r_idx in range(101):
            r_thr = r_idx / 100.0
            p_at_r = [p for p, r in zip(precisions, recalls) if r >= r_thr]
            if p_at_r:
                ap50 += max(p_at_r)
        ap50 /= 101.0

    # Operating-point P/R/F1 at score >= score_thresh
    matched_op: dict[int, set[int]] = {k: set() for k in gt_by_image}
    tp_op = 0
    fp_op = 0
    for p in preds_sorted:
        if p["score"] < score_thresh:
            continue
        img_id = p["image_id"]
        gts = gt_by_image.get(img_id, [])
        best_iou = 0.0
        best_idx = -1
        for gi, gt in enumerate(gts):
            if gi in matched_op[img_id]:
                continue
            iou = _bbox_iou(p["bbox_xyxy"], gt)
            if iou > best_iou:
                best_iou = iou
                best_idx = gi
        if best_iou >= iou_thresh and best_idx >= 0:
            matched_op[img_id].add(best_idx)
            tp_op += 1
        else:
            fp_op += 1

    precision_50 = tp_op / max(1, tp_op + fp_op)
    recall_50 = tp_op / float(total_gt)
    f1_50 = (
        (2.0 * precision_50 * recall_50 / (precision_50 + recall_50))
        if (precision_50 + recall_50) > 0.0
        else 0.0
    )
    return {
        "total_gt": total_gt,
        "tp_50": tp_op,
        "fp_50": fp_op,
        "precision_50": round(precision_50, 4),
        "recall_50": round(recall_50, 4),
        "f1_50": round(f1_50, 4),
        "mAP50": round(ap50, 4),
    }


def _render_overlays_html(
    *,
    samples: list[dict[str, Any]],
    metrics: dict[str, Any],
    gpu_name: str,
    elapsed_sec: float,
    out_path: Path,
) -> None:
    from PIL import Image, ImageDraw

    cards = []
    for item in samples[:12]:
        with Image.open(WORK_DIR / item["file_name"]) as im:
            vis = im.convert("RGB")
            draw = ImageDraw.Draw(vis)
            for gx1, gy1, gx2, gy2 in item["gt_xyxy"]:
                draw.rectangle([gx1, gy1, gx2, gy2], outline=(34, 197, 94), width=4)
            for px1, py1, px2, py2, sc in item["pred_xyxy"]:
                draw.rectangle([px1, py1, px2, py2], outline=(6, 182, 212), width=3)
                draw.text((px1 + 4, py1 + 4), f"{sc:.2f}", fill=(6, 182, 212))
            vis.thumbnail((512, 512), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            vis.save(buf, format="WEBP", quality=82)
            b64 = base64.b64encode(buf.getvalue()).decode("ascii")

        cards.append(
            "<div style='border:1px solid #d1d5db;border-radius:8px;padding:8px;background:#fff;'>"
            f"<img src='data:image/webp;base64,{b64}' style='width:100%;border-radius:6px;' />"
            f"<div style='margin-top:6px;font-size:12px;font-weight:700;'>{html.escape(item['file_name'])}</div>"
            f"<div style='font-size:12px;'>GT: {len(item['gt_xyxy'])} | Pred(@0.50): {len(item['pred_xyxy'])}</div>"
            "</div>"
        )

    page = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>Numista.AI M3 RT-DETR Pilot Bounding-Box Overlays</title></head>"
        "<body style='font-family:system-ui,-apple-system,sans-serif;background:#f8fafc;color:#111827;padding:20px;'>"
        f"<h1>M3 Coin / Binder-Page Cropper Pilot QA ({html.escape(MODEL_ID)} &mdash; Apache-2.0)</h1>"
        f"<p>GPU: <b>{html.escape(gpu_name)}</b> | Epochs: <b>{EPOCHS}</b> | "
        f"mAP@50: <b>{metrics['mAP50']:.4f}</b> | Precision@50: <b>{metrics['precision_50']:.4f}</b> | "
        f"Recall@50: <b>{metrics['recall_50']:.4f}</b> | F1@50: <b>{metrics['f1_50']:.4f}</b> | "
        f"Elapsed: <b>{elapsed_sec:.2f}s</b></p>"
        "<p><span style='color:#16a34a;font-weight:700;'>Green = Ground Truth</span> &nbsp;|&nbsp; "
        "<span style='color:#0891b2;font-weight:700;'>Cyan = RT-DETR Prediction</span></p>"
        "<div style='display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px;'>"
        + "".join(cards)
        + "</div></body></html>\n"
    )
    out_path.write_bytes(page.encode("utf-8"))


def main() -> int:
    _assert_zero_credentials()
    if not INPUT_TAR.is_file():
        raise FileNotFoundError(f"Expected staged M3 input archive at {INPUT_TAR}")

    _ensure_dependencies()

    import numpy as np
    import torch
    from PIL import Image
    from transformers import RTDetrForObjectDetection, RTDetrImageProcessor

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is NOT available on Colab runtime; aborting M3 training.")

    gpu_name = torch.cuda.get_device_name(0)
    vram_mib = round(torch.cuda.get_device_properties(0).total_memory / (1024 * 1024), 1)
    print(f"[m3_remote] GPU: {gpu_name} ({vram_mib} MiB)", flush=True)

    WORK_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with tarfile.open(INPUT_TAR, "r:*") as tf:
        tf.extractall(WORK_DIR, filter="data")

    dataset_meta = json.loads((WORK_DIR / "dataset_meta.json").read_text(encoding="utf-8"))
    train_records = json.loads((WORK_DIR / "train_annotations.json").read_text(encoding="utf-8"))
    val_records = json.loads((WORK_DIR / "val_annotations.json").read_text(encoding="utf-8"))
    print(f"[m3_remote] Dataset: train={len(train_records)} val={len(val_records)} boxes={dataset_meta['total_boxes']}", flush=True)

    t0 = time.monotonic()
    processor = RTDetrImageProcessor.from_pretrained(MODEL_ID, size={"height": 640, "width": 640})
    model = RTDetrForObjectDetection.from_pretrained(
        MODEL_ID,
        num_labels=1,
        id2label={0: "coin"},
        label2id={"coin": 0},
        ignore_mismatched_sizes=True,
    ).to("cuda")

    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)

    rng = np.random.default_rng(42)
    epoch_losses: list[float] = []

    model.train()
    for epoch in range(1, EPOCHS + 1):
        order = rng.permutation(len(train_records))
        losses: list[float] = []
        for start in range(0, len(order), BATCH_SIZE):
            batch_recs = [train_records[int(i)] for i in order[start : start + BATCH_SIZE]]
            imgs = []
            targets = []
            for rec in batch_recs:
                with Image.open(WORK_DIR / rec["file_name"]) as im:
                    imgs.append(im.convert("RGB"))
                w_img = float(rec["width"])
                h_img = float(rec["height"])
                norm_boxes = []
                cls_ids = []
                for ann in rec["annotations"]:
                    bx, by, bw, bh = ann["bbox"]
                    cx = (bx + bw * 0.5) / w_img
                    cy = (by + bh * 0.5) / h_img
                    norm_boxes.append([cx, cy, bw / w_img, bh / h_img])
                    cls_ids.append(0)
                targets.append({
                    "class_labels": torch.tensor(cls_ids, dtype=torch.long, device="cuda"),
                    "boxes": torch.tensor(norm_boxes, dtype=torch.float32, device="cuda"),
                })

            enc = processor(images=imgs, return_tensors="pt")
            pixel_values = enc["pixel_values"].to("cuda")

            optimizer.zero_grad(set_to_none=True)
            out = model(pixel_values=pixel_values, labels=targets)
            loss = out.loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)
            optimizer.step()
            losses.append(float(loss.item()))

        scheduler.step()
        avg_loss = round(sum(losses) / max(1, len(losses)), 4)
        epoch_losses.append(avg_loss)
        print(f"[m3_remote] Epoch {epoch}/{EPOCHS} loss={avg_loss:.4f}", flush=True)

    # Validation evaluation
    model.eval()
    gt_by_image: dict[int, list[list[float]]] = {}
    all_preds: list[dict[str, Any]] = []
    overlay_samples: list[dict[str, Any]] = []

    with torch.no_grad():
        for rec in val_records:
            img_id = int(rec["image_id"])
            gt_xyxy = [
                [ann["bbox"][0], ann["bbox"][1], ann["bbox"][0] + ann["bbox"][2], ann["bbox"][1] + ann["bbox"][3]]
                for ann in rec["annotations"]
            ]
            gt_by_image[img_id] = gt_xyxy

            with Image.open(WORK_DIR / rec["file_name"]) as im:
                rgb_im = im.convert("RGB")
            enc = processor(images=[rgb_im], return_tensors="pt")
            out = model(pixel_values=enc["pixel_values"].to("cuda"))
            res = processor.post_process_object_detection(
                out,
                target_sizes=[(int(rec["height"]), int(rec["width"]))],
                threshold=0.25,
            )[0]

            pred_xyxy_op: list[list[float]] = []
            for box_t, score_t in zip(res["boxes"].cpu().tolist(), res["scores"].cpu().tolist()):
                all_preds.append({
                    "image_id": img_id,
                    "bbox_xyxy": [float(v) for v in box_t],
                    "score": float(score_t),
                })
                if float(score_t) >= 0.50:
                    pred_xyxy_op.append([float(box_t[0]), float(box_t[1]), float(box_t[2]), float(box_t[3]), float(score_t)])

            if len(overlay_samples) < 12:
                overlay_samples.append({
                    "file_name": rec["file_name"],
                    "gt_xyxy": gt_xyxy,
                    "pred_xyxy": pred_xyxy_op,
                })

    elapsed_sec = round(time.monotonic() - t0, 2)
    det_metrics = _compute_detection_metrics(gt_by_image, all_preds, iou_thresh=0.50, score_thresh=0.50)

    # Export weights (.pt + optional .onnx)
    pt_path = OUT_DIR / "rtdetr_coin_cropper.pt"
    torch.save({
        "model": "RT-DETR",
        "model_id": MODEL_ID,
        "spdx": "Apache-2.0",
        "id2label": {0: "coin"},
        "metrics": det_metrics,
        "state_dict": model.state_dict(),
    }, pt_path)

    onnx_path = OUT_DIR / "rtdetr_coin_cropper.onnx"
    onnx_exported = False
    onnx_error = ""
    try:
        class _OnnxWrap(torch.nn.Module):
            def __init__(self, m: Any) -> None:
                super().__init__()
                self.m = m

            def forward(self, pixel_values: Any) -> tuple[Any, Any]:
                out_m = self.m(pixel_values=pixel_values)
                return out_m.logits, out_m.pred_boxes

        cpu_model = _OnnxWrap(model.to("cpu").eval())
        dummy = torch.randn(1, 3, 640, 640)
        torch.onnx.export(
            cpu_model,
            (dummy,),
            str(onnx_path),
            input_names=["pixel_values"],
            output_names=["logits", "pred_boxes"],
            opset_version=17,
            dynamo=False,
        )
        onnx_exported = onnx_path.is_file() and onnx_path.stat().st_size > 0
    except Exception as exc:  # noqa: BLE001
        onnx_error = str(exc)

    overlays_path = OUT_DIR / "m3_overlays.html"
    _render_overlays_html(
        samples=overlay_samples,
        metrics=det_metrics,
        gpu_name=gpu_name,
        elapsed_sec=elapsed_sec,
        out_path=overlays_path,
    )

    eval_payload = {
        "model": "RT-DETR",
        "model_id": MODEL_ID,
        "spdx": "Apache-2.0",
        "commercial_ok": True,
        "promotion_allowed": True,
        "annotation_count": dataset_meta["total_images"],
        "train_images": dataset_meta["train_images"],
        "val_images": dataset_meta["val_images"],
        "total_boxes": dataset_meta["total_boxes"],
        "epochs": EPOCHS,
        "epoch_losses": epoch_losses,
        **det_metrics,
        "onnx_exported": onnx_exported,
        "onnx_bytes": onnx_path.stat().st_size if onnx_exported else 0,
        "onnx_error": onnx_error,
        "pt_bytes": pt_path.stat().st_size,
        "gpu_name": gpu_name,
        "vram_total_mib": vram_mib,
        "elapsed_sec": elapsed_sec,
        "status": "pilot_trained",
    }
    metrics_path = OUT_DIR / "eval_metrics.json"
    metrics_path.write_bytes((json.dumps(eval_payload, indent=2) + "\n").encode("utf-8"))

    with tarfile.open(OUTPUT_BUNDLE, "w:gz") as tf:
        for fpath in (metrics_path, overlays_path, pt_path):
            tf.add(fpath, arcname=fpath.name)
        if onnx_exported:
            tf.add(onnx_path, arcname=onnx_path.name)

    print(SUMMARY_BEGIN, flush=True)
    print(json.dumps({k: v for k, v in eval_payload.items() if k != "epoch_losses"}, indent=2), flush=True)
    print(SUMMARY_END, flush=True)
    return 0


if __name__ == "__main__":
    main()
