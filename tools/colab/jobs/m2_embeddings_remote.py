"""Standalone DINOv2 + SigLIP M2 visual embedding audit worker for Google Colab GPU.

Executes inside `/content` via `colab exec -s <job_id> -f m2_embeddings_remote.py`.
Must remain 100% self-contained (zero `tools.colab` imports) and hold zero GCP credentials.
ZERO leakage: `is_known_bad` labels are NEVER used during embedding, centroid construction,
or anomaly flagging — only evaluated post-flagging for AT-07 recall scoring.
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
from collections import defaultdict
from pathlib import Path
from typing import Any

INPUT_TAR = Path("/content/m2_inputs.tar")
WORK_DIR = Path("/content/m2_work")
OUT_DIR = Path("/content/m2_out")
OUTPUT_BUNDLE = Path("/content/m2_outputs.tar.gz")

DINOV2_MODEL_ID = os.environ.get("M2_MODEL_ID", "facebook/dinov2-base")
SIGLIP_MODEL_ID = os.environ.get("M2_SIGLIP_MODEL_ID", "google/siglip-base-patch16-384")
REVIEW_OWNER = "TRK-002 SAG/Muse Review Queue"
DEFAULT_SIMILARITY_THRESHOLD = float(os.environ.get("M2_SIMILARITY_THRESHOLD", "0.72"))
MAX_ASPECT_RATIO = float(os.environ.get("M2_MAX_ASPECT_RATIO", "1.30"))

SUMMARY_BEGIN = "===M2_REMOTE_SUMMARY_BEGIN==="
SUMMARY_END = "===M2_REMOTE_SUMMARY_END==="

SIGLIP_PROMPTS: list[str] = [
    "a single isolated round coin photographed straight-on against a plain neutral background",
    "a coin sealed inside a rectangular plastic grading slab holder with text barcode label",
    "a coin photographed against a colorful scenic sunset, landscape, or vivid colorful background",
    "two coins side by side or a multi-image coin comparison diagram with text labels",
    "the obverse heads side of a US coin showing a portrait profile bust and motto IN GOD WE TRUST",
    "the reverse tails side of a US coin showing an eagle, state design, monument, shield, or national park",
]


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
        "PIL": "pillow",
        "numpy": "numpy",
        "sentencepiece": "sentencepiece",
        "google.protobuf": "protobuf",
    }
    missing = []
    for mod, pkg in required.items():
        try:
            importlib.import_module(mod)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"[m2_remote] Installing dependencies: {missing}", flush=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", *missing], check=True)


def _thumb_webp_b64(img_path: Path) -> str:
    from PIL import Image

    with Image.open(img_path) as im:
        thumb = im.convert("RGB")
        thumb.thumbnail((160, 160), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        thumb.save(buf, format="WEBP", quality=80)
        return base64.b64encode(buf.getvalue()).decode("ascii")


def _render_m2_contact_sheet(
    *,
    flags: list[dict[str, Any]],
    total_images: int,
    recall_pct: float | None,
    gpu_name: str,
    elapsed_sec: float,
    out_path: Path,
) -> None:
    cards = []
    for flag in flags:
        kb_badge = (
            "<span style='background:#7c2d12;color:#fff;padding:1px 6px;border-radius:4px;font-size:11px;'>SEEDED BAD</span>"
            if flag["is_known_bad"]
            else "<span style='background:#b45309;color:#fff;padding:1px 6px;border-radius:4px;font-size:11px;'>CANDIDATE FLAG</span>"
        )
        cards.append(
            "<div style='border:1px solid #d1d5db;border-radius:8px;padding:8px;background:#fff;'>"
            f"<div style='display:flex;justify-content:center;align-items:center;background:#f3f4f6;border-radius:6px;padding:6px;'>"
            f"<img src='data:image/webp;base64,{flag['_thumb_b64']}' width='160' height='160' alt='{html.escape(flag['catalog_id'])}' />"
            "</div>"
            f"<div style='margin-top:6px;font-size:12px;font-weight:700;'>{html.escape(flag['catalog_id'])}</div>"
            f"<div style='font-size:11px;color:#4b5563;'>Group: {html.escape(flag['series_group'])}</div>"
            f"<div style='font-size:11px;color:#374151;'>Cosine sim: <b>{flag['similarity_score']:.4f}</b></div>"
            f"<div style='font-size:11px;color:#991b1b;word-break:break-word;'>{html.escape(flag['reason'])}</div>"
            f"<div style='margin-top:4px;display:flex;justify-content:space-between;'>{kb_badge}"
            "<span style='background:#1e3a8a;color:#fff;padding:1px 6px;border-radius:4px;font-size:11px;'>REVIEW ONLY</span>"
            "</div></div>"
        )

    recall_str = f"{recall_pct:.2f}%" if recall_pct is not None else "n/a (no seeded bad controls)"
    page = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>Numista.AI M2 Advisory Audit Contact Sheet</title></head>"
        "<body style='font-family:system-ui,-apple-system,sans-serif;background:#f8fafc;color:#111827;padding:20px;'>"
        f"<h1>M2 Visual Embedding Audit ({len(flags)}/{total_images} Flagged &mdash; Advisory Only)</h1>"
        f"<p>Models: <b>{html.escape(DINOV2_MODEL_ID)} + {html.escape(SIGLIP_MODEL_ID)} (Apache-2.0)</b> | "
        f"GPU: <b>{html.escape(gpu_name)}</b> | Review Owner: <b>{html.escape(REVIEW_OWNER)}</b> | "
        f"Known-Bad Recall: <b>{recall_str}</b> | Elapsed: <b>{elapsed_sec:.2f}s</b></p>"
        "<p><i>Policy notice: Advisory flags never modify or delete catalog records automatically.</i></p>"
        "<div style='display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;'>"
        + ("".join(cards) if cards else "<p>No anomalies flagged.</p>")
        + "</div></body></html>\n"
    )
    out_path.write_bytes(page.encode("utf-8"))


def main() -> int:
    _assert_zero_credentials()
    if not INPUT_TAR.is_file():
        raise FileNotFoundError(f"Expected staged M2 input archive at {INPUT_TAR}")

    _ensure_dependencies()

    import numpy as np
    import torch
    from PIL import Image
    from transformers import AutoImageProcessor, AutoModel, AutoProcessor

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is NOT available on Colab runtime; aborting M2 embedding audit.")

    gpu_name = torch.cuda.get_device_name(0)
    vram_mib = round(torch.cuda.get_device_properties(0).total_memory / (1024 * 1024), 1)
    print(f"[m2_remote] GPU: {gpu_name} ({vram_mib} MiB)", flush=True)

    WORK_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with tarfile.open(INPUT_TAR, "r:*") as tf:
        tf.extractall(WORK_DIR, filter="data")

    input_manifest = json.loads((WORK_DIR / "input_manifest.json").read_text(encoding="utf-8"))
    print(f"[m2_remote] Staged images: {len(input_manifest)}", flush=True)

    t0 = time.monotonic()

    # Pass 1: DINOv2 embeddings (Apache-2.0)
    dino_proc = AutoImageProcessor.from_pretrained(DINOV2_MODEL_ID)
    dino_model = AutoModel.from_pretrained(DINOV2_MODEL_ID, torch_dtype=torch.float16).to("cuda").eval()
    embeddings_list: list[Any] = []
    for idx, entry in enumerate(input_manifest, start=1):
        img_path = WORK_DIR / entry["staged_path"]
        with Image.open(img_path) as raw_img:
            rgb_img = raw_img.convert("RGB")
        inputs = dino_proc(images=rgb_img, return_tensors="pt")
        pixel_values = inputs["pixel_values"].to("cuda", dtype=torch.float16)
        with torch.no_grad():
            outputs = dino_model(pixel_values=pixel_values)
            cls_vec = outputs.last_hidden_state[:, 0, :].float()
            norm_vec = torch.nn.functional.normalize(cls_vec, p=2, dim=-1).cpu().numpy()[0]
        embeddings_list.append(norm_vec)
        if idx % 100 == 0 or idx == len(input_manifest):
            print(f"[m2_remote] DINOv2 embedded {idx}/{len(input_manifest)}", flush=True)

    del dino_model
    torch.cuda.empty_cache()

    # Pass 2: SigLIP zero-shot visual-defect logits (Apache-2.0)
    siglip_proc = AutoProcessor.from_pretrained(SIGLIP_MODEL_ID)
    siglip_model = AutoModel.from_pretrained(SIGLIP_MODEL_ID, torch_dtype=torch.float16).to("cuda").eval()
    defect_labels = ["clean", "slabbed_with_logos", "sunset_non_neutral_bg", "both_sides_or_collage"]
    siglip_logits: list[list[float]] = []

    for idx, entry in enumerate(input_manifest, start=1):
        img_path = WORK_DIR / entry["staged_path"]
        with Image.open(img_path) as raw_img:
            rgb_img = raw_img.convert("RGB")
        inputs = siglip_proc(
            text=SIGLIP_PROMPTS,
            images=rgb_img,
            padding="max_length",
            return_tensors="pt",
        ).to("cuda")
        if "pixel_values" in inputs:
            inputs["pixel_values"] = inputs["pixel_values"].to(dtype=torch.float16)
        with torch.no_grad():
            outputs = siglip_model(**inputs)
            logits_row = outputs.logits_per_image[0].float().cpu().tolist()
        siglip_logits.append([float(v) for v in logits_row])
        if idx % 100 == 0 or idx == len(input_manifest):
            print(f"[m2_remote] SigLIP scored {idx}/{len(input_manifest)}", flush=True)

    del siglip_model
    torch.cuda.empty_cache()

    emb_matrix = np.vstack(embeddings_list).astype(np.float32)

    # Unsupervised series-group index (zero access to `is_known_bad`)
    groups_all_indices: dict[str, list[int]] = defaultdict(list)
    for i, entry in enumerate(input_manifest):
        grp = str(entry.get("series_group") or "default")
        groups_all_indices[grp].append(i)

    global_centroid = np.median(emb_matrix, axis=0)
    global_centroid = global_centroid / max(float(np.linalg.norm(global_centroid)), 1e-8)

    # Trimmed/median centroids for groups with >= 3 images (used for cross-series matching)
    group_centroids: dict[str, Any] = {}
    for grp, idxs in groups_all_indices.items():
        if len(idxs) >= 3:
            c_vec = np.median(emb_matrix[idxs], axis=0)
            group_centroids[grp] = c_vec / max(float(np.linalg.norm(c_vec)), 1e-8)

    sims: list[float] = []
    for i, entry in enumerate(input_manifest):
        grp = str(entry.get("series_group") or "default").strip().lower()
        peers = [j for j in groups_all_indices[grp] if j != i]
        if len(peers) >= 2:
            centroid = np.median(emb_matrix[peers], axis=0)
            centroid = centroid / max(float(np.linalg.norm(centroid)), 1e-8)
        else:
            centroid = global_centroid
        sims.append(float(np.dot(emb_matrix[i], centroid)))

    group_stats: dict[str, tuple[float, float]] = {}
    for grp, idxs in groups_all_indices.items():
        if len(idxs) >= 3:
            arr = np.array([sims[j] for j in idxs], dtype=np.float32)
            group_stats[grp] = (float(np.median(arr)), float(arr.std()))
        else:
            group_stats[grp] = (DEFAULT_SIMILARITY_THRESHOLD, 0.05)

    flagged_items: list[dict[str, Any]] = []
    seeded_total = 0
    seeded_recalled = 0

    for i, entry in enumerate(input_manifest):
        grp = str(entry.get("series_group") or "default").strip().lower()
        sim_score = sims[i]
        med_s, std_s = group_stats[grp]
        adaptive_cutoff = med_s - 1.5 * std_s
        reasons: list[str] = []

        # Signal 1: In-group cosine similarity / z-score outlier
        if sim_score < DEFAULT_SIMILARITY_THRESHOLD:
            reasons.append(f"below_threshold({sim_score:.3f}<{DEFAULT_SIMILARITY_THRESHOLD:.2f})")
        if len(groups_all_indices[grp]) >= 3 and sim_score < adaptive_cutoff and std_s > 0.0:
            reasons.append(f"outlier_z({sim_score:.3f}<{adaptive_cutoff:.3f})")

        # Signal 2: Cross-series/side better-match check
        if grp in group_centroids:
            best_other_grp = ""
            best_other_sim = -1.0
            for other_grp, o_vec in group_centroids.items():
                if other_grp == grp:
                    continue
                osim = float(np.dot(emb_matrix[i], o_vec))
                if osim > best_other_sim:
                    best_other_sim = osim
                    best_other_grp = other_grp
            if best_other_grp and best_other_sim > sim_score + 0.015:
                reasons.append(f"cross_series_mismatch(better_match={best_other_grp}:{best_other_sim:.3f}>{sim_score:.3f})")

        # Signal 3: Geometric aspect ratio check (Rule 3 wide dual-coin / comparison image)
        ow = float(entry.get("orig_width") or 0)
        oh = float(entry.get("orig_height") or 0)
        if ow > 0 and oh > 0:
            aspect = max(ow, oh) / min(ow, oh)
            if aspect > MAX_ASPECT_RATIO:
                reasons.append(f"non_square_aspect({aspect:.2f}>{MAX_ASPECT_RATIO:.2f})")

        # Signal 4: SigLIP zero-shot visual-defect classification (indices 1..3)
        logits_i = siglip_logits[i]
        clean_logit = logits_i[0]
        best_def_idx = int(np.argmax(logits_i[1:4])) + 1
        if logits_i[best_def_idx] > clean_logit - 0.5:
            reasons.append(f"siglip_{defect_labels[best_def_idx]}({logits_i[best_def_idx]:.2f}>=clean:{clean_logit:.2f})")

        # Signal 5: Physical side-consistency check when entry claims `reverse`
        if str(entry.get("side") or "").strip().lower() == "reverse":
            max_obv_sim = max(
                (float(np.dot(emb_matrix[i], o_vec)) for o_grp, o_vec in group_centroids.items() if o_grp.endswith("::obverse")),
                default=0.0,
            )
            obv_logit, rev_logit = logits_i[4], logits_i[5]
            if max_obv_sim >= 0.85 or obv_logit > rev_logit + 0.5:
                reasons.append(f"side_mismatch_obverse_detected(obv_sim={max_obv_sim:.3f},obv={obv_logit:.2f}>rev={rev_logit:.2f})")
            reasons.append(f"siglip_{defect_labels[best_def_idx]}({logits_i[best_def_idx]:.2f}>=clean:{clean_logit:.2f})")

        is_flagged = bool(reasons)
        is_bad = bool(entry.get("is_known_bad", False))
        if is_bad:
            seeded_total += 1
            if is_flagged:
                seeded_recalled += 1

        if is_flagged:
            img_path = WORK_DIR / entry["staged_path"]
            flagged_items.append({
                "catalog_id": str(entry["catalog_id"]),
                "nac_code": str(entry.get("nac_code") or ""),
                "candidate_image": str(entry.get("source_relpath") or entry["staged_path"]),
                "series_group": grp,
                "reason": "; ".join(reasons),
                "similarity_score": round(sim_score, 4),
                "is_known_bad": is_bad,
                "known_bad_reason": str(entry.get("known_bad_reason") or ""),
                "publish_eligible": bool(entry.get("publish_eligible", True)),
                "action": "review_only",
                "auto_applied": False,
                "_thumb_b64": _thumb_webp_b64(img_path),
            })

    elapsed_sec = round(time.monotonic() - t0, 2)
    recall_pct = round((seeded_recalled / seeded_total) * 100.0, 2) if seeded_total > 0 else None
    at07_passed = (recall_pct >= 90.0) if recall_pct is not None else True

    contact_sheet_path = OUT_DIR / "m2_contact_sheet.html"
    _render_m2_contact_sheet(
        flags=flagged_items,
        total_images=len(input_manifest),
        recall_pct=recall_pct,
        gpu_name=gpu_name,
        elapsed_sec=elapsed_sec,
        out_path=contact_sheet_path,
    )

    clean_flags = [{k: v for k, v in it.items() if k != "_thumb_b64"} for it in flagged_items]
    advisory_payload = {
        "advisory_only": True,
        "mutated_catalog": False,
        "review_owner": REVIEW_OWNER,
        "flag_count": len(clean_flags),
        "flags": clean_flags,
    }
    advisory_path = OUT_DIR / "advisory_flags.json"
    advisory_path.write_bytes((json.dumps(advisory_payload, indent=2) + "\n").encode("utf-8"))

    eval_payload = {
        "total_images": len(input_manifest),
        "flagged_count": len(clean_flags),
        "seeded_known_bad_total": seeded_total,
        "seeded_known_bad_recalled": seeded_recalled,
        "known_bad_recall_pct": recall_pct,
        "at07_passed": at07_passed,
        "similarity_threshold": DEFAULT_SIMILARITY_THRESHOLD,
        "model": f"{DINOV2_MODEL_ID} + {SIGLIP_MODEL_ID}",
        "license_spdx": "Apache-2.0",
        "gpu_name": gpu_name,
        "vram_total_mib": vram_mib,
        "elapsed_sec": elapsed_sec,
    }
    eval_path = OUT_DIR / "m2_eval_report.json"
    eval_path.write_bytes((json.dumps(eval_payload, indent=2) + "\n").encode("utf-8"))

    emb_path = OUT_DIR / "embeddings.npz"
    np.savez_compressed(
        emb_path,
        catalog_ids=np.array([str(e["catalog_id"]) for e in input_manifest]),
        embeddings=emb_matrix,
        similarity_scores=np.array(sims, dtype=np.float32),
        siglip_logits=np.array(siglip_logits, dtype=np.float32),
    )

    with tarfile.open(OUTPUT_BUNDLE, "w:gz") as tf:
        for fpath in (advisory_path, eval_path, emb_path, contact_sheet_path):
            tf.add(fpath, arcname=fpath.name)

    print(SUMMARY_BEGIN, flush=True)
    print(json.dumps(eval_payload, indent=2), flush=True)
    print(SUMMARY_END, flush=True)
    return 0


if __name__ == "__main__":
    main()
