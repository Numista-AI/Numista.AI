# -*- coding: utf-8 -*-
import sys, io
# Force UTF-8 output on Windows so emoji/special chars don't crash cp1252 console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

"""
batch_process_aj_invoices.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AJ's Littleton Receipt Batch Processor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE:
    Submits all of AJ's Littleton Coin Company receipt PDFs to
    POST /api/process_invoice on the live Cloud Run backend.

    Each PDF is sent as a multipart/form-data upload — exactly the same
    format the Flutter app uses. Extracted line items land in:
        users/jseaman1204@gmail.com/review_queue/{uuid}

    A log file is written to:
        batch_invoice_log.json   (per-file results, timings, any errors)
        batch_invoice_summary.txt (human-readable final report)

USAGE:
    python batch_process_aj_invoices.py
    (Run from inside numista_backend/ with the .venv active)

    Optional flags:
        --dry-run       List all PDFs that would be sent, but do not POST.
        --jan-only      Only process Scans 28 JAN 2026
        --jun-only      Only process Scans AJ June 2026
        --delay 3       Seconds to pause between requests (default: 2)
        --limit 10      Stop after N files (useful for spot-checking)
        --skip-errors   Continue past HTTP errors without stopping
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime, timezone

# ─── Configuration ────────────────────────────────────────────────────────────

API_BASE    = "https://numista-backend-568985927038.us-central1.run.app"
ENDPOINT    = f"{API_BASE}/api/process_invoice"
USER_EMAIL  = "jseaman1204@gmail.com"

# Session ID ties all records from this batch run together in Firestore
IMPORT_SESSION_ID = f"lcc-aj-batch-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

# All source folders — ordered oldest → newest
SCRIPT_DIR = Path(__file__).parent

AJ_COINS_ROOT = Path(r"C:\Users\ericd\Documents\MyVertexProject\AJ's Coins")

SCAN_FOLDERS = {
    "jan_2026": AJ_COINS_ROOT / "Scans 28 JAN 2026",
    "jun_2026_1": AJ_COINS_ROOT / "Scans AJ June 2026" / "1",
    "jun_2026_2": AJ_COINS_ROOT / "Scans AJ June 2026" / "2",
    "jun_2026_3": AJ_COINS_ROOT / "Scans AJ June 2026" / "3",
    "jun_2026_4": AJ_COINS_ROOT / "Scans AJ June 2026" / "4",
    "jun_2026_5": AJ_COINS_ROOT / "Scans AJ June 2026" / "5",
    "jun_2026_6": AJ_COINS_ROOT / "Scans AJ June 2026" / "6",
    # "Uploaded folder" is intentionally excluded — already processed
}

LOG_FILE     = SCRIPT_DIR / "batch_invoice_log.json"
SUMMARY_FILE = SCRIPT_DIR / "batch_invoice_summary.txt"

REQUEST_TIMEOUT_SECONDS = 120   # Gemini multimodal PDF parse can take up to 60s on large files


# ─── Argument parsing ─────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Batch process AJ's Littleton receipt PDFs")
    p.add_argument("--dry-run",    action="store_true", help="List files only; do not POST")
    p.add_argument("--jan-only",   action="store_true", help="Only process Jan 2026 scans")
    p.add_argument("--jun-only",   action="store_true", help="Only process June 2026 scans")
    p.add_argument("--delay",      type=float, default=1.5,
                   help="Seconds between requests (default: 1.5)")
    p.add_argument("--limit",      type=int,   default=0,
                   help="Max files to process; 0 = unlimited")
    p.add_argument("--skip-errors",action="store_true", help="Continue past HTTP errors")
    p.add_argument("--yes",        action="store_true", help="Skip confirmation prompt")
    return p.parse_args()


# ─── Collect PDF paths ────────────────────────────────────────────────────────

def collect_pdfs(args) -> list[Path]:
    """Walk configured scan folders and return sorted list of PDF paths."""
    all_pdfs = []

    for label, folder in SCAN_FOLDERS.items():
        # Apply --jan-only / --jun-only filters
        if args.jan_only and not label.startswith("jan"):
            continue
        if args.jun_only and not label.startswith("jun"):
            continue

        if not folder.exists():
            print(f"  [WARN] Folder not found, skipping: {folder}")
            continue

        pdfs = sorted(folder.glob("*.pdf"))
        print(f"  {label}: {len(pdfs)} PDF(s) in {folder}")
        all_pdfs.extend(pdfs)

    return all_pdfs


# ─── Single-file POST ─────────────────────────────────────────────────────────

def post_invoice(pdf_path: Path, index: int, total: int, delay: float) -> dict:
    """
    POST one PDF to /api/process_invoice.
    Returns a result dict with: path, status, items_extracted, duration_s, error.
    """
    result = {
        "index":           index,
        "total":           total,
        "path":            str(pdf_path),
        "filename":        pdf_path.name,
        "folder":          pdf_path.parent.name,
        "status":          "pending",
        "http_code":       None,
        "items_extracted": 0,
        "duration_s":      0.0,
        "error":           None,
        "timestamp":       datetime.now(timezone.utc).isoformat(),
    }

    print(f"\n[{index}/{total}] {pdf_path.name}", end="  ", flush=True)

    t0 = time.monotonic()
    try:
        with open(pdf_path, "rb") as fh:
            response = requests.post(
                ENDPOINT,
                data={
                    "user_email":        USER_EMAIL,
                    "import_session_id": IMPORT_SESSION_ID,
                    "receipt_id":        "",
                    "mask_pii":          "false",
                },
                files={"file": (pdf_path.name, fh, "application/pdf")},
                timeout=REQUEST_TIMEOUT_SECONDS,
            )

        elapsed = time.monotonic() - t0
        result["duration_s"] = round(elapsed, 2)
        result["http_code"]  = response.status_code

        if response.status_code == 200:
            try:
                body = response.json()
                # process_invoice returns:
                #   extracted_items (int), set_records (int), pending_items (int),
                #   supplies_logged (int), data (list of item dicts)
                extracted = body.get("extracted_items", 0)
                sets      = body.get("set_records",      0)
                pending   = body.get("pending_items",    0)
                supplies  = body.get("supplies_logged",  0)
                total_extracted = int(extracted or 0) + int(sets or 0) + int(pending or 0) + int(supplies or 0)

                result["status"]          = "success"
                result["items_extracted"] = total_extracted
                print(f"  [OK]  {int(extracted or 0)} coin(s)  {int(sets or 0)} set(s)  {int(pending or 0)} pending  ({elapsed:.1f}s)")

            except Exception as parse_err:
                result["status"] = "json_parse_error"
                result["error"]  = str(parse_err)
                print(f"  [WARN] 200 OK but JSON parse failed: {parse_err}")
        else:
            result["status"] = f"http_{response.status_code}"
            result["error"]  = response.text[:300]
            print(f"  [ERR] HTTP {response.status_code}: {response.text[:120]}")

    except requests.exceptions.Timeout:
        elapsed = time.monotonic() - t0
        result["status"]     = "timeout"
        result["error"]      = f"Request timed out after {REQUEST_TIMEOUT_SECONDS}s"
        result["duration_s"] = round(elapsed, 2)
        print(f"  [TIMEOUT] after {elapsed:.0f}s")

    except Exception as exc:
        elapsed = time.monotonic() - t0
        result["status"]     = "exception"
        result["error"]      = str(exc)
        result["duration_s"] = round(elapsed, 2)
        print(f"  [EXCEPTION] {exc}")

    # Polite delay between requests to avoid saturating Cloud Run / Gemini quota
    if delay > 0:
        time.sleep(delay)

    return result


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    print("=" * 65)
    print("  Numista.AI — AJ's Littleton Receipt Batch Processor")
    print("=" * 65)
    print(f"  Endpoint:    {ENDPOINT}")
    print(f"  User:        {USER_EMAIL}")
    print(f"  Session ID:  {IMPORT_SESSION_ID}")
    print(f"  Delay:       {args.delay}s between requests")
    if args.dry_run:
        print("  Mode:        DRY RUN (no data will be sent)")
    print()

    # ── Collect files ──────────────────────────────────────────────────────────
    print("Scanning folders...")
    pdfs = collect_pdfs(args)
    total = len(pdfs)

    if args.limit > 0:
        pdfs = pdfs[: args.limit]
        print(f"\n  --limit {args.limit} applied: processing {len(pdfs)} of {total} files.")
        total = len(pdfs)

    print(f"\n  Total PDFs to process: {total}")

    if total == 0:
        print("  Nothing to do. Exiting.")
        return

    if args.dry_run:
        print("\n  DRY RUN — files that would be sent:")
        for i, p in enumerate(pdfs, 1):
            print(f"    {i:>3}. {p.relative_to(AJ_COINS_ROOT)}")
        return

    # ── Confirm before sending ────────────────────────────────────────────────
    print(f"\n  About to POST {total} PDF(s) to Cloud Run.")
    print(f"  Estimated time: {int(total * (args.delay + 15) / 60)}–{int(total * (args.delay + 45) / 60)} minutes")
    print(f"  Results will land in Firestore review_queue for {USER_EMAIL}")
    if not args.yes:
        confirm = input("\n  Proceed? [y/N]: ").strip().lower()
        if confirm != "y":
            print("  Aborted.")
            return
    else:
        print("\n  Proceeding (--yes flag set)...")

    # ── Process ───────────────────────────────────────────────────────────────
    log_records = []
    errors      = []
    total_items = 0
    t_start     = time.monotonic()

    for i, pdf in enumerate(pdfs, 1):
        record = post_invoice(pdf, i, total, args.delay)
        log_records.append(record)

        if record["status"] == "success":
            total_items += record["items_extracted"]
        else:
            errors.append(record)
            if not args.skip_errors and record["status"] not in (
                "json_parse_error", f"http_422", "timeout"
            ):
                print(f"\n  Stopping on error (use --skip-errors to continue). File: {pdf.name}")
                break

        # Write log incrementally so a crash doesn't lose all progress
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(log_records, f, indent=2)

    elapsed_total = time.monotonic() - t_start

    # ── Summary ───────────────────────────────────────────────────────────────
    successful   = sum(1 for r in log_records if r["status"] == "success")
    failed       = len(log_records) - successful
    avg_duration = (
        sum(r["duration_s"] for r in log_records) / len(log_records)
        if log_records else 0
    )

    summary_lines = [
        "=" * 65,
        "  AJ Littleton Batch — Final Summary",
        "=" * 65,
        f"  Session ID:       {IMPORT_SESSION_ID}",
        f"  Files processed:  {len(log_records)} / {total}",
        f"  Successful:       {successful}",
        f"  Failed:           {failed}",
        f"  Total items:      {total_items} (landed in review_queue)",
        f"  Avg response:     {avg_duration:.1f}s per file",
        f"  Total time:       {elapsed_total/60:.1f} minutes",
        f"  Log:              {LOG_FILE}",
        "",
    ]

    if errors:
        summary_lines.append("  ERRORS:")
        for e in errors:
            summary_lines.append(f"    [{e['status']}] {e['filename']} — {e.get('error','')[:80]}")

    summary_text = "\n".join(summary_lines)
    print("\n" + summary_text)

    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print(f"\n  Log saved to:     {LOG_FILE}")
    print(f"  Summary saved to: {SUMMARY_FILE}")
    print(f"\n  Done. Check Firestore review_queue for {USER_EMAIL} to review extracted items.")


if __name__ == "__main__":
    main()
