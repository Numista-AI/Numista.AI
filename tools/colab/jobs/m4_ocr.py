"""M4 — Bulk Historical Mint Pamphlet & Reference OCR (OlmOCR Apache-2.0 default).

Enforces Muse / CoS pilot condition #2: requires a hand-checked sample of pilot
OCR pages (>= 10) and reports numeric Character Error Rate (CER) and Word Error Rate (WER).
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import tarfile
from pathlib import Path
from typing import Any

from tools.colab.config import M4_DEFAULT_MODEL, M4_OCR_HANDCHECK_MIN_SAMPLE
from tools.colab.guards import GuardViolation, build_manifest


_DOC_EXTS: tuple[str, ...] = (".pdf", ".png", ".jpg", ".jpeg", ".webp")


def pack_m4_pilot_inputs(
    source_path: Path,
    out_tar: Path,
    *,
    max_pages: int = 25,
) -> list[dict[str, Any]]:
    """Pack PDFs/images, list manifests, or FRASER URL page packs into a tar bundle for Colab M4 OCR."""
    entries: list[dict[str, Any]] = []
    if source_path.is_dir():
        files = [
            p for p in sorted(source_path.rglob("*"))
            if p.is_file() and p.suffix.lower() in _DOC_EXTS
        ]
        if not files:
            raise ValueError(f"No PDF or image files found in M4 directory: {source_path}")
        for fpath in files[:max_pages]:
            entries.append({"path": fpath, "source_doc": fpath.relative_to(source_path).as_posix()})
    elif source_path.is_file() and source_path.suffix.lower() == ".json":
        loaded = json.loads(source_path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict) and isinstance(loaded.get("pages"), list):
            # Catalog Manager FRASER URL page-pack schema
            out_tar.parent.mkdir(parents=True, exist_ok=True)
            pages = loaded["pages"][:max_pages]
            staged_entries: list[dict[str, Any]] = []
            provenance: list[dict[str, Any]] = []
            for p in pages:
                staged_entries.append({
                    "seq": p.get("seq"),
                    "pdf_url": str(p["pdf_url"]),
                    "pdf_page": int(p["pdf_page"]),
                    "printed_page": str(p.get("printed_page") or ""),
                    "source_doc": str(p.get("doc_title") or p["pdf_url"]),
                    "target_series": str(p.get("target_series") or ""),
                    "license": str(p.get("license") or ""),
                    "ground_truth_anchor": str(p.get("ground_truth_anchor") or ""),
                    "reference_text": str(p.get("reference_text") or ""),
                })
                provenance.append({
                    "source_doc": str(p.get("doc_title") or p["pdf_url"]),
                    "pdf_url": str(p["pdf_url"]),
                    "pdf_page": int(p["pdf_page"]),
                })
            with tarfile.open(out_tar, "w") as tf:
                mbytes = (json.dumps(staged_entries, indent=2) + "\n").encode("utf-8")
                minfo = tarfile.TarInfo(name="input_manifest.json")
                minfo.size = len(mbytes)
                tf.addfile(minfo, io.BytesIO(mbytes))
            return provenance
        if not isinstance(loaded, list) or not loaded:
            raise ValueError(f"M4 JSON manifest must be a non-empty list or pages dict: {source_path}")
        for item in loaded[:max_pages]:
            raw_p = Path(str(item["path"]))
            fpath = raw_p if raw_p.is_absolute() else (source_path.parent / raw_p)
            entries.append({
                "path": fpath,
                "source_doc": str(item.get("source_doc") or fpath.name),
                "page_numbers": item.get("page_numbers"),
                "reference_texts": item.get("reference_texts") or {},
                "seq": item.get("seq"),
                "page_number": item.get("page_number"),
                "printed_page": str(item.get("printed_page") or ""),
                "target_series": str(item.get("target_series") or ""),
                "ground_truth_anchor": str(item.get("ground_truth_anchor") or ""),
                "pdf_text_layer": str(item.get("pdf_text_layer") or ""),
                "pdf_url": str(item.get("pdf_url") or ""),
                "reference_text": str(item.get("reference_text") or ""),
            })
    elif source_path.is_file() and source_path.suffix.lower() in _DOC_EXTS:
        entries.append({"path": source_path, "source_doc": source_path.name})
    else:
        raise FileNotFoundError(f"Invalid M4 input source path: {source_path}")

    out_tar.parent.mkdir(parents=True, exist_ok=True)
    staged_entries: list[dict[str, Any]] = []
    provenance: list[dict[str, Any]] = []
    seen_names: dict[str, int] = {}

    with tarfile.open(out_tar, "w") as tf:
        for item in entries:
            src: Path = item["path"]
            if not src.is_file():
                raise FileNotFoundError(f"Missing M4 source file: {src}")
            raw_bytes = src.read_bytes()
            orig_sha256 = hashlib.sha256(raw_bytes).hexdigest()

            safe_stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", src.stem).strip("._") or "doc"
            cnt = seen_names.get(safe_stem.lower(), 0)
            seen_names[safe_stem.lower()] = cnt + 1
            if cnt > 0:
                safe_stem = f"{safe_stem}_{cnt}"

            staged_rel = f"docs/{safe_stem}{src.suffix.lower()}"
            tinfo = tarfile.TarInfo(name=staged_rel)
            tinfo.size = len(raw_bytes)
            tf.addfile(tinfo, io.BytesIO(raw_bytes))

            staged_entries.append({
                "staged_path": staged_rel,
                "source_doc": item["source_doc"],
                "original_sha256": orig_sha256,
                "page_numbers": item.get("page_numbers"),
                "reference_texts": item.get("reference_texts") or {},
                "seq": item.get("seq"),
                "page_number": item.get("page_number"),
                "printed_page": item.get("printed_page", ""),
                "target_series": item.get("target_series", ""),
                "ground_truth_anchor": item.get("ground_truth_anchor", ""),
                "pdf_text_layer": item.get("pdf_text_layer", ""),
                "pdf_url": item.get("pdf_url", ""),
                "reference_text": item.get("reference_text", ""),
            })
            provenance.append({
                "source_doc": item["source_doc"],
                "original_sha256": orig_sha256,
            })

        mbytes = (json.dumps(staged_entries, indent=2) + "\n").encode("utf-8")
        minfo = tarfile.TarInfo(name="input_manifest.json")
        minfo.size = len(mbytes)
        tf.addfile(minfo, io.BytesIO(mbytes))

    return provenance


def score_handcheck_file(handcheck_json: Path, out_report_json: Path) -> dict[str, Any]:
    """Compute numeric CER/WER from a >=10-page hand-checked JSON sample and write report."""
    records = json.loads(handcheck_json.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("Hand-check file must contain a JSON list of page records.")

    filled = [
        r for r in records
        if str(r.get("reference_text", "")).strip() and str(r.get("ocr_text", "")).strip()
    ]
    refs = [str(r["reference_text"]) for r in filled]
    hyps = [str(r["ocr_text"]) for r in filled]
    metrics = compute_ocr_error_rate(refs, hyps, min_sample=M4_OCR_HANDCHECK_MIN_SAMPLE)
    metrics["status"] = "scored"
    out_report_json.parent.mkdir(parents=True, exist_ok=True)
    out_report_json.write_bytes((json.dumps(metrics, indent=2) + "\n").encode("utf-8"))
    return metrics


def _levenshtein(seq_a: list[str] | str, seq_b: list[str] | str) -> int:
    """Compute edit distance between two character strings or word lists."""
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


def compute_ocr_error_rate(
    reference_pages: list[str],
    ocr_pages: list[str],
    *,
    min_sample: int = M4_OCR_HANDCHECK_MIN_SAMPLE,
) -> dict[str, Any]:
    """Compute numeric CER and WER across hand-checked OCR sample pages."""
    if len(reference_pages) != len(ocr_pages):
        raise ValueError("reference_pages and ocr_pages must have equal length.")
    if len(reference_pages) < min_sample:
        raise GuardViolation(
            f"M4 pilot requires at least {min_sample} hand-checked pages; got {len(reference_pages)}."
        )

    total_chars = 0
    char_edits = 0
    total_words = 0
    word_edits = 0

    for ref, hyp in zip(reference_pages, ocr_pages):
        ref_norm = " ".join(ref.split())
        hyp_norm = " ".join(hyp.split())
        total_chars += max(len(ref_norm), 1)
        char_edits += _levenshtein(ref_norm, hyp_norm)

        ref_words = ref_norm.split()
        hyp_words = hyp_norm.split()
        total_words += max(len(ref_words), 1)
        word_edits += _levenshtein(ref_words, hyp_words)

    cer = round(char_edits / total_chars, 4)
    wer = round(word_edits / total_words, 4)
    return {
        "sample_pages": len(reference_pages),
        "sample_pages_checked": len(reference_pages),
        "char_edits": char_edits,
        "total_chars": total_chars,
        "cer": cer,
        "word_edits": word_edits,
        "total_words": total_words,
        "wer": wer,
    }


def run_pilot_dry_run(output_dir: Path, job_id: str) -> Path:
    """Emit sample provenance Markdown, numeric OCR error report, and manifest."""
    output_dir.mkdir(parents=True, exist_ok=True)
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
    hyps = [
        "1881-S Morgan Dollar mintage 12,760,000",
        "1893-S Morgan Dollar mintage 100,000",
        "1909-S VDB Lincoln Cent mintage 484,000",
        "1916-D Mercury Dime mintage 264,000",
        "1921 Peace Dollar High Relief mintage 1,006,478",
        "1922-D Lincoln Cent mintage 7,160,000",
        "1932-D Washington Quarter mintage 436,800",
        "1938-D Walking Liberty Half Dollar mintage 491,600",
        "1909-S Indian Head Cent mintage 309,000",
        "1895 Proof Morgan Dollar mintage 880",
    ]
    metrics = compute_ocr_error_rate(refs, hyps)
    md_lines = ["<!-- source: dry-run-mint-report.pdf -->\n"]
    for idx, text in enumerate(hyps, start=1):
        md_lines.append(f"<!-- page: {idx} -->\n{text}\n\n")
    (output_dir / "ocr_sample.md").write_bytes("".join(md_lines).encode("utf-8"))
    (output_dir / "ocr_error_report.json").write_bytes((json.dumps(metrics, indent=2) + "\n").encode("utf-8"))
    return build_manifest(
        job_id=job_id,
        milestone="M4",
        mode="pilot",
        output_dir=output_dir,
        model_name=M4_DEFAULT_MODEL,
        input_provenance=[{"source": "dry-run-mint-report.pdf", "pages": len(refs)}],
        extra_meta={"cer": metrics["cer"], "wer": metrics["wer"]},
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="M4 Bulk Historical Mint OCR")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--job-id", default="m4-handcheck")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--score-handcheck", type=Path, default=None)
    args = parser.parse_args()

    if args.score_handcheck is not None:
        report = score_handcheck_file(args.score_handcheck, args.output_dir / "ocr_error_report.json")
        print(f"M4 handcheck scored: CER={report['cer']} WER={report['wer']} pages={report['sample_pages_checked']}")
        return 0
    if args.dry_run:
        manifest = run_pilot_dry_run(args.output_dir, args.job_id)
        print(f"M4 dry-run manifest written: {manifest}")
        return 0
    raise NotImplementedError("Live GPU execution runs via `python -m tools.colab.runner --milestone M4`.")


if __name__ == "__main__":
    raise SystemExit(main())
