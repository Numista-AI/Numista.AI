# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

"""
retry_failed_invoices.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Retries only the failed files from the previous batch run, using the
batch_invoice_log.json produced by batch_process_aj_invoices.py.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json, time, requests
from pathlib import Path
from datetime import datetime, timezone

API_BASE   = "https://numista-backend-568985927038.us-central1.run.app"
ENDPOINT   = f"{API_BASE}/api/process_invoice"
USER_EMAIL = "jseaman1204@gmail.com"
LOG_FILE   = Path(__file__).parent / "batch_invoice_log.json"
RETRY_SESSION = f"lcc-aj-retry-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
TIMEOUT    = 180  # longer timeout for large PDFs that previously timed out

if not LOG_FILE.exists():
    print(f"[ERR] Log file not found: {LOG_FILE}")
    sys.exit(1)

with open(LOG_FILE, encoding="utf-8") as f:
    records = json.load(f)

failed = [r for r in records if r.get("status") != "success"]
print(f"\n  Found {len(failed)} failed file(s) to retry (session: {RETRY_SESSION})\n")

for i, rec in enumerate(failed, 1):
    pdf_path = Path(rec["path"])
    print(f"[{i}/{len(failed)}] {rec['filename']}", end="  ", flush=True)

    if not pdf_path.exists():
        print(f"  [SKIP] File not found: {pdf_path}")
        continue

    t0 = time.monotonic()
    try:
        with open(pdf_path, "rb") as fh:
            resp = requests.post(
                ENDPOINT,
                data={"user_email": USER_EMAIL, "import_session_id": RETRY_SESSION,
                      "receipt_id": "", "mask_pii": "false"},
                files={"file": (pdf_path.name, fh, "application/pdf")},
                timeout=TIMEOUT,
            )
        elapsed = time.monotonic() - t0
        if resp.status_code == 200:
            body = resp.json()
            extracted = body.get("extracted_items", 0)
            sets      = body.get("set_records",     0)
            pending   = body.get("pending_items",   0)
            print(f"  [OK]  {int(extracted or 0)} coin(s)  {int(sets or 0)} set(s)  {int(pending or 0)} pending  ({elapsed:.1f}s)")
            # Update record in log
            rec["status"]          = "success"
            rec["items_extracted"] = int(extracted or 0) + int(sets or 0) + int(pending or 0)
            rec["duration_s"]      = round(elapsed, 2)
            rec["error"]           = None
        else:
            print(f"  [ERR] HTTP {resp.status_code}: {resp.text[:120]}")
            rec["retry_error"] = resp.text[:300]
    except requests.exceptions.Timeout:
        elapsed = time.monotonic() - t0
        print(f"  [TIMEOUT] after {elapsed:.0f}s")
        rec["retry_error"] = f"Timeout after {TIMEOUT}s"
    except Exception as exc:
        print(f"  [EXCEPTION] {exc}")
        rec["retry_error"] = str(exc)

    time.sleep(2)

# Save updated log
with open(LOG_FILE, "w", encoding="utf-8") as f:
    json.dump(records, f, indent=2)

still_failed = [r for r in records if r.get("status") != "success"]
print(f"\n  Retry complete. {len(failed) - len(still_failed)}/{len(failed)} recovered.")
if still_failed:
    print("  Still failing:")
    for r in still_failed:
        print(f"    {r['filename']} — {r.get('retry_error', r.get('error',''))[:80]}")
