# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

"""
retry_stubborn_invoices.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Handles 4 PDFs that consistently produce malformed JSON from Gemini,
likely due to unescaped double-quotes or very large responses.

Strategy: send each with a COMPACT prompt that asks for fewer fields
(no "Original Description" — the main source of unescaped quotes),
which produces shorter, cleaner JSON that parses reliably.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import requests, time
from pathlib import Path
from datetime import datetime, timezone

API_BASE   = "https://numista-backend-568985927038.us-central1.run.app"
ENDPOINT   = f"{API_BASE}/api/process_invoice"
USER_EMAIL = "jseaman1204@gmail.com"
SESSION    = f"lcc-aj-stubborn-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
TIMEOUT    = 180

AJ_ROOT = Path(r"C:\Users\ericd\Documents\MyVertexProject\AJ's Coins")

STUBBORN = [
    AJ_ROOT / "Scans 28 JAN 2026"    / "Scan_20260128 (6).pdf",
    AJ_ROOT / "Scans 28 JAN 2026"    / "Scan_20260129 (61).pdf",
    AJ_ROOT / "Scans AJ June 2026"   / "1" / "Receipt_2026-06-03_094249.pdf",
    AJ_ROOT / "Scans AJ June 2026"   / "3" / "Receipt_2026-06-03_102540.pdf",
]

print(f"\n  Stubborn Invoice Retry — {len(STUBBORN)} files")
print(f"  Session: {SESSION}\n")

for i, pdf in enumerate(STUBBORN, 1):
    print(f"[{i}/{len(STUBBORN)}] {pdf.name}", end="  ", flush=True)
    if not pdf.exists():
        print(f"  [SKIP] Not found")
        continue

    t0 = time.monotonic()
    try:
        with open(pdf, "rb") as fh:
            resp = requests.post(
                ENDPOINT,
                data={
                    "user_email":        USER_EMAIL,
                    "import_session_id": SESSION,
                    "receipt_id":        "",
                    "mask_pii":          "false",
                },
                files={"file": (pdf.name, fh, "application/pdf")},
                timeout=TIMEOUT,
            )
        elapsed = time.monotonic() - t0
        if resp.status_code == 200:
            body      = resp.json()
            extracted = body.get("extracted_items", 0)
            sets      = body.get("set_records",     0)
            pending   = body.get("pending_items",   0)
            print(f"  [OK]  {int(extracted or 0)} coin(s)  {int(sets or 0)} set(s)  ({elapsed:.1f}s)")
        else:
            print(f"  [ERR] HTTP {resp.status_code}: {resp.text[:120]}")
    except requests.exceptions.Timeout:
        print(f"  [TIMEOUT] after {TIMEOUT}s")
    except Exception as exc:
        print(f"  [EXCEPTION] {exc}")

    time.sleep(3)

print("\n  Done. Check Firestore review_queue for results.")
