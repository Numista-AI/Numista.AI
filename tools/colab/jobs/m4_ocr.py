"""M4 — Bulk Historical Mint Pamphlet & Reference OCR (OlmOCR Apache-2.0 default).

Enforces Muse / CoS pilot condition #2: requires a hand-checked sample of pilot
OCR pages (>= 10) and reports numeric Character Error Rate (CER) and Word Error Rate (WER).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.colab.config import M4_DEFAULT_MODEL, M4_OCR_HANDCHECK_MIN_SAMPLE
from tools.colab.guards import GuardViolation, build_manifest


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
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        manifest = run_pilot_dry_run(args.output_dir, args.job_id)
        print(f"M4 dry-run manifest written: {manifest}")
        return 0
    raise NotImplementedError("Live GPU execution runs inside Colab via `colab run`.")


if __name__ == "__main__":
    raise SystemExit(main())
