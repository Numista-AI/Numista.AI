"""Standalone OlmOCR M4 bulk historical Mint pamphlet OCR worker for Google Colab GPU.

Executes inside `/content` via `colab exec -s <job_id> -f m4_ocr_remote.py`.
Must remain 100% self-contained (zero `tools.colab` imports) and hold zero GCP credentials.
Outputs citation-preserved Markdown + 10-page hand-check fixture (`ocr_error_report.json`).
"""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
import tarfile
import time
from pathlib import Path
from typing import Any

INPUT_TAR = Path("/content/m4_inputs.tar")
WORK_DIR = Path("/content/m4_work")
PAGES_DIR = WORK_DIR / "pages"
OUT_DIR = Path("/content/m4_out")
OUTPUT_BUNDLE = Path("/content/m4_outputs.tar.gz")

MODEL_ID = os.environ.get("M4_MODEL_ID", "allenai/olmOCR-7B-0225-preview")
MAX_PAGES = int(os.environ.get("M4_MAX_PAGES", "25"))
MIN_HANDCHECK_PAGES = 10

SUMMARY_BEGIN = "===M4_REMOTE_SUMMARY_BEGIN==="
SUMMARY_END = "===M4_REMOTE_SUMMARY_END==="


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
        "pypdfium2": "pypdfium2",
        "transformers": "transformers",
        "accelerate": "accelerate",
        "PIL": "pillow",
        "qwen_vl_utils": "qwen-vl-utils",
    }
    missing = []
    for mod, pkg in required.items():
        try:
            importlib.import_module(mod)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"[m4_remote] Installing dependencies: {missing}", flush=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", *missing], check=True)


def _levenshtein(seq_a: list[str] | str, seq_b: list[str] | str) -> int:
    len_a, len_b = len(seq_a), len(seq_b)
    if len_a == 0:
        return len_b
    if len_b == 0:
        return len_a
    prev = list(range(len_b + 1))
    for i, tok_a in enumerate(seq_a, start=1):
        curr = [i] + [0] * len_b
        for j, tok_b in enumerate(seq_b, start=1):
            cost = 0 if tok_a == tok_b else 1
            curr[j] = min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost)
        prev = curr
    return prev[-1]


def _compute_error_metrics(refs: list[str], hyps: list[str]) -> dict[str, Any]:
    total_chars = 0
    char_edits = 0
    total_words = 0
    word_edits = 0
    for ref, hyp in zip(refs, hyps):
        ref_norm = " ".join(ref.split())
        hyp_norm = " ".join(hyp.split())
        total_chars += max(len(ref_norm), 1)
        char_edits += _levenshtein(ref_norm, hyp_norm)
        ref_words = ref_norm.split()
        hyp_words = hyp_norm.split()
        total_words += max(len(ref_words), 1)
        word_edits += _levenshtein(ref_words, hyp_words)
    return {
        "status": "scored",
        "sample_pages": len(refs),
        "sample_pages_checked": len(refs),
        "char_edits": char_edits,
        "total_chars": total_chars,
        "cer": round(char_edits / total_chars, 4),
        "word_edits": word_edits,
        "total_words": total_words,
        "wer": round(word_edits / total_words, 4),
    }


def _collect_page_tasks(input_manifest: list[dict[str, Any]]) -> list[dict[str, Any]]:
    import pypdfium2 as pdfium
    from PIL import Image

    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    tasks: list[dict[str, Any]] = []

    for entry in input_manifest:
        if len(tasks) >= MAX_PAGES:
            break
        src_path = WORK_DIR / entry["staged_path"]
        source_doc = str(entry.get("source_doc") or src_path.name)
        ref_map = entry.get("reference_texts") or {}
        req_pages = entry.get("page_numbers")

        if src_path.suffix.lower() == ".pdf":
            pdf = pdfium.PdfDocument(str(src_path))
            page_indices = (
                [int(p) - 1 for p in req_pages if 1 <= int(p) <= len(pdf)]
                if req_pages
                else list(range(len(pdf)))
            )
            for p_idx in page_indices:
                if len(tasks) >= MAX_PAGES:
                    break
                page_num = p_idx + 1
                page = pdf[p_idx]
                bitmap = page.render(scale=150.0 / 72.0)
                pil_img = bitmap.to_pil().convert("RGB")
                out_png = PAGES_DIR / f"doc_{len(tasks) + 1:03d}_p{page_num}.png"
                pil_img.save(out_png, format="PNG")
                tasks.append({
                    "source_doc": source_doc,
                    "page_number": page_num,
                    "page_image": out_png,
                    "reference_text": str(ref_map.get(str(page_num), "")),
                })
        else:
            page_num = int(entry.get("page_number") or 1)
            out_png = PAGES_DIR / f"doc_{len(tasks) + 1:03d}_p{page_num}.png"
            with Image.open(src_path) as raw_img:
                raw_img.convert("RGB").save(out_png, format="PNG")
            tasks.append({
                "source_doc": source_doc,
                "page_number": page_num,
                "page_image": out_png,
                "reference_text": str(ref_map.get(str(page_num), "") or entry.get("reference_text") or ""),
            })
    return tasks


def main() -> int:
    _assert_zero_credentials()
    if not INPUT_TAR.is_file():
        raise FileNotFoundError(f"Expected staged M4 input archive at {INPUT_TAR}")

    _ensure_dependencies()

    import torch
    from PIL import Image
    from transformers import AutoProcessor

    try:
        from transformers import Qwen2VLForConditionalGeneration as VLMClass
    except ImportError:
        from transformers import AutoModelForImageTextToText as VLMClass

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is NOT available on Colab runtime; aborting M4 OCR.")

    gpu_name = torch.cuda.get_device_name(0)
    vram_mib = round(torch.cuda.get_device_properties(0).total_memory / (1024 * 1024), 1)
    print(f"[m4_remote] GPU: {gpu_name} ({vram_mib} MiB)", flush=True)

    WORK_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with tarfile.open(INPUT_TAR, "r:*") as tf:
        tf.extractall(WORK_DIR, filter="data")

    input_manifest = json.loads((WORK_DIR / "input_manifest.json").read_text(encoding="utf-8"))
    page_tasks = _collect_page_tasks(input_manifest)
    if not page_tasks:
        raise RuntimeError("No readable PDF or image pages found in M4 input archive.")
    print(f"[m4_remote] Pages queued for OCR: {len(page_tasks)}", flush=True)

    t0 = time.monotonic()
    print(f"[m4_remote] Loading {MODEL_ID} (Apache-2.0)...", flush=True)
    processor = AutoProcessor.from_pretrained(MODEL_ID)
    model = VLMClass.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16,
        device_map="auto",
    ).eval()

    prompt_text = (
        "Transcribe this historical US Mint / numismatic document page verbatim into clean Markdown. "
        "Preserve all headings, tables, coin denominations, years, mintmarks, and mintage figures exactly."
    )

    page_results: list[dict[str, Any]] = []
    md_sections: list[str] = []

    for idx, task in enumerate(page_tasks, start=1):
        with Image.open(task["page_image"]) as pil_img:
            img_rgb = pil_img.convert("RGB")
            if max(img_rgb.size) > 1288:
                img_rgb.thumbnail((1288, 1288), Image.Resampling.LANCZOS)

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": img_rgb},
                    {"type": "text", "text": prompt_text},
                ],
            }
        ]
        text_prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[text_prompt], images=[img_rgb], padding=True, return_tensors="pt").to("cuda")

        with torch.no_grad():
            output_ids = model.generate(**inputs, max_new_tokens=2048, do_sample=False)

        prompt_len = inputs["input_ids"].shape[1]
        generated_ids = output_ids[:, prompt_len:]
        ocr_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()

        page_results.append({
            "source_doc": task["source_doc"],
            "page_number": task["page_number"],
            "ocr_text": ocr_text,
            "reference_text": task["reference_text"],
        })
        md_sections.append(
            f"<!-- source: {task['source_doc']} -->\n"
            f"<!-- page: {task['page_number']} -->\n"
            f"{ocr_text}\n\n"
        )
        print(f"[m4_remote] OCR complete page {idx}/{len(page_tasks)} ({task['source_doc']} p.{task['page_number']})", flush=True)

    elapsed_sec = round(time.monotonic() - t0, 2)

    ocr_md_path = OUT_DIR / "ocr_output.md"
    ocr_md_path.write_bytes("".join(md_sections).encode("utf-8"))

    pages_json_path = OUT_DIR / "ocr_pages.json"
    pages_json_path.write_bytes((json.dumps(page_results, indent=2) + "\n").encode("utf-8"))

    # Evenly sample up to 10 pages for human/Muse hand-check verification
    n_pages = len(page_results)
    if n_pages <= MIN_HANDCHECK_PAGES:
        sample_indices = list(range(n_pages))
    else:
        step = (n_pages - 1) / float(MIN_HANDCHECK_PAGES - 1)
        sample_indices = sorted({int(round(k * step)) for k in range(MIN_HANDCHECK_PAGES)})
    handcheck_sample = [page_results[idx] for idx in sample_indices]

    handcheck_path = OUT_DIR / "handcheck_sample_10pages.json"
    handcheck_path.write_bytes((json.dumps(handcheck_sample, indent=2) + "\n").encode("utf-8"))

    scored_pairs = [
        (it["reference_text"], it["ocr_text"])
        for it in handcheck_sample
        if it["reference_text"].strip()
    ]
    if len(scored_pairs) >= MIN_HANDCHECK_PAGES:
        error_report = _compute_error_metrics(
            [p[0] for p in scored_pairs],
            [p[1] for p in scored_pairs],
        )
    else:
        error_report = {
            "status": "awaiting_10page_handcheck",
            "sample_pages_checked": len(scored_pairs),
            "required_sample_pages": MIN_HANDCHECK_PAGES,
            "pages_available": n_pages,
            "cer": None,
            "wer": None,
            "note": (
                "Fill `reference_text` for >=10 entries in handcheck_sample_10pages.json and run "
                "`python -m tools.colab.jobs.m4_ocr --score-handcheck <path>` to compute CER/WER."
            ),
        }

    report_path = OUT_DIR / "ocr_error_report.json"
    report_path.write_bytes((json.dumps(error_report, indent=2) + "\n").encode("utf-8"))

    with tarfile.open(OUTPUT_BUNDLE, "w:gz") as tf:
        for fpath in (ocr_md_path, pages_json_path, handcheck_path, report_path):
            tf.add(fpath, arcname=fpath.name)

    summary = {
        "pages_processed": n_pages,
        "handcheck_status": error_report["status"],
        "sample_pages_checked": error_report["sample_pages_checked"],
        "cer": error_report["cer"],
        "wer": error_report["wer"],
        "model": MODEL_ID,
        "license_spdx": "Apache-2.0",
        "gpu_name": gpu_name,
        "elapsed_sec": elapsed_sec,
    }
    print(SUMMARY_BEGIN, flush=True)
    print(json.dumps(summary, indent=2), flush=True)
    print(SUMMARY_END, flush=True)
    return 0


if __name__ == "__main__":
    main()
