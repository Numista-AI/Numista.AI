# -*- coding: utf-8 -*-
import sys, io, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from pathlib import Path

pdf = Path(r"C:\Users\ericd\Documents\MyVertexProject\AJ's Coins\Scans AJ June 2026\4\Receipt_2026-06-03_102540.pdf")

if not pdf.exists():
    print(f"NOT FOUND: {pdf}")
    sys.exit(1)

print(f"Found: {pdf.name} ({pdf.stat().st_size:,} bytes) — posting...")

with open(pdf, "rb") as fh:
    resp = requests.post(
        "https://numista-backend-568985927038.us-central1.run.app/api/process_invoice",
        data={"user_email": "jseaman1204@gmail.com",
              "import_session_id": "lcc-aj-stubborn-final",
              "receipt_id": "", "mask_pii": "false"},
        files={"file": (pdf.name, fh, "application/pdf")},
        timeout=180,
    )

if resp.status_code == 200:
    b = resp.json()
    print(f"[OK]  {b.get('extracted_items',0)} coin(s)  {b.get('set_records',0)} set(s)  {b.get('pending_items',0)} pending")
else:
    print(f"[ERR] HTTP {resp.status_code}: {resp.text[:300]}")
