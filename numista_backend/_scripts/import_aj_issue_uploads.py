# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
import_aj_issue_uploads.py
──────────────────────────────────────────────────────────────────────────────
Imports AJ's "issue uploads" folder into Firestore for jseaman1204@gmail.com.
Skips Paper Money (goes to separate 'currency' collection - handled separately).

Source files (coins only):
  • National Park Quarters - 3.xlsx      (50 rows)
  • National Park Quarters - 4 - B.xlsx  (25 rows)
  • miscellaneous purchases.xlsx         (80 rows)
  • BUFFALO NICKELS.xlsx                 (4 rows)
  • JAS Gallery invoice.xlsx             (2 rows)
  • invoice Premier.xlsx                 (2 rows)
  • Mint Sets.xlsx                       (1 row)

Column mapping (AJ's format → Firestore):
  ID                  → Personal Ref # (as string)
  date/when purchased → Purchase Date
  Year / YEAR         → Year
  description / Name  → Original Description from source
  quality / Quality   → Condition
  amount paid / Paid  → Cost
  denomination        → Denomination
  name                → Program/Series
  notes               → Personal Notes
  QTY / qty           → Quantity

Usage:
    python _scripts/import_aj_issue_uploads.py --dry-run
    python _scripts/import_aj_issue_uploads.py
"""

import os, sys, uuid, glob, argparse
from datetime import datetime, timezone

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import openpyxl
import google.auth
from google.cloud import firestore

PROJECT        = "studio-9101802118-8c9a8"
TARGET_EMAIL   = "jseaman1204@gmail.com"
ISSUE_DIR      = r"C:\Users\ericd\Documents\MyVertexProject\AJ's Coins\issue uploads"
BATCH_SIZE     = 400

# Files to import as COINS (skip Paper Money)
COIN_FILES = [
    "National Park Quarters - 3.xlsx",
    "National Park Quarters - 4 - B.xlsx",
    "miscellaneous purchases.xlsx",
    "BUFFALO NICKELS.xlsx",
    "JAS Gallery invoice.xlsx",
    "invoice Premier.xlsx",
    "Mint Sets.xlsx",
]

# Column name normalization — maps various spellings to canonical keys
COL_MAP = {
    "id":                   "personal_ref",
    "date purchased":       "purchase_date",
    "when purchased":       "purchase_date",
    "year":                 "year",
    "description":          "description",
    "name of money":        "description",
    "name of park":         "description",
    "name":                 "program",
    "quality":              "condition",
    "amount paid":          "cost",
    "paid":                 "cost",
    "denomination":         "denomination",
    "notes":                "personal_notes",
    "qty":                  "quantity",
}

# Infer program/series from filename
PROGRAM_FROM_FILE = {
    "National Park Quarters - 3.xlsx":     "America the Beautiful",
    "National Park Quarters - 4 - B.xlsx": "America the Beautiful",
    "miscellaneous purchases.xlsx":        "",     # varied
    "BUFFALO NICKELS.xlsx":                "Buffalo Nickel",
    "JAS Gallery invoice.xlsx":            "",
    "invoice Premier.xlsx":                "",
    "Mint Sets.xlsx":                      "Mint Set",
}


def read_excel(filepath: str) -> list[dict]:
    wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        wb.close()
        return []
    # Normalize headers
    raw_headers = [str(h).strip().lower() if h else "" for h in rows[0]]
    headers = [COL_MAP.get(h, h) for h in raw_headers]
    records = []
    for row in rows[1:]:
        if all(v is None for v in row):
            continue
        rec = {}
        for h, v in zip(headers, row):
            if v is not None:
                rec[h] = v
        records.append(rec)
    wb.close()
    return records


def build_doc(rec: dict, filename: str) -> dict:
    now = datetime.now(tz=timezone.utc)
    default_program = PROGRAM_FROM_FILE.get(filename, "")

    year = str(rec.get("year", "") or "").strip()
    if year.endswith(".0"):
        year = year[:-2]

    cost = str(rec.get("cost", "") or "").strip()
    if cost and not cost.startswith("$"):
        try:
            cost = f"${float(cost):.2f}"
        except (ValueError, TypeError):
            pass

    qty = rec.get("quantity", 1)
    try:
        qty = int(float(str(qty))) if qty else 1
    except (ValueError, TypeError):
        qty = 1

    purchase_date = rec.get("purchase_date", "")
    if hasattr(purchase_date, "date"):
        purchase_date = str(purchase_date.date())
    else:
        purchase_date = str(purchase_date or "").strip()

    program = str(rec.get("program", "") or default_program).strip()
    description = str(rec.get("description", "") or "").strip()

    # If program is empty but description has info, use description
    if not program and description:
        program = description

    return {
        "Year":                          year,
        "Program/Series":                program,
        "Original Description from source": description,
        "Denomination":                  str(rec.get("denomination", "") or "").strip(),
        "Condition":                     str(rec.get("condition", "") or "").strip(),
        "Cost":                          cost,
        "Purchase Date":                 purchase_date,
        "Personal Notes":                str(rec.get("personal_notes", "") or "").strip(),
        "Personal Ref #":                str(rec.get("personal_ref", "") or "").strip(),
        "Quantity":                      qty,
        "Country":                       "US",
        "category":                      "coin",
        "source":                        "excel_import",
        "source_file":                   filename,
        "user_email":                    TARGET_EMAIL,
        "inventoryStatus":               "UNCHECKED",
        "deep_dive_status":              "PENDING",
        "created_at":                    now,
        "import_batch":                  "issue_uploads_2026-06-20",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.dry_run:
        print("⚠️  DRY RUN\n")

    credentials, _ = google.auth.default()
    db = firestore.Client(credentials=credentials, project=PROJECT)
    col_ref = db.collection("users").document(TARGET_EMAIL).collection("coins")

    batch = db.batch()
    batch_count = 0
    total = 0
    errors = 0

    for filename in COIN_FILES:
        filepath = os.path.join(ISSUE_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  MISSING: {filename}")
            continue

        records = read_excel(filepath)
        print(f"\n{filename}: {len(records)} rows")

        for rec in records:
            try:
                doc = build_doc(rec, filename)
                doc_id = str(uuid.uuid4())

                if not args.dry_run:
                    batch.set(col_ref.document(doc_id), doc)
                    batch_count += 1
                    if batch_count >= BATCH_SIZE:
                        batch.commit()
                        batch = db.batch()
                        batch_count = 0

                total += 1
                # Show sample
                if total <= 3 or records.index(rec) < 2:
                    yr  = doc.get("Year", "?")
                    pgm = doc.get("Program/Series", "?")[:35]
                    cst = doc.get("Cost", "")
                    print(f"  {yr:>6}  {pgm:<35}  {cst}")

            except Exception as e:
                print(f"  ERROR: {e}")
                errors += 1

    if not args.dry_run and batch_count > 0:
        batch.commit()

    print(f"\n{'DRY RUN ' if args.dry_run else ''}Results:")
    print(f"  Imported : {total}")
    print(f"  Errors   : {errors}")
    if not args.dry_run:
        print(f"  ✅  Done — {total} coins added to {TARGET_EMAIL}")


if __name__ == "__main__":
    main()
