"""
import_aj_currency.py
──────────────────────────────────────────────────────────────────────────────
Imports AJ's paper money / currency items into a SEPARATE Firestore collection:
    users/jseaman1204@gmail.com/currency

Source: AJ's Coins/issue uploads/Paper Money.xlsx
Schema mirrors the coin schema but with currency-specific fields.

Columns in Paper Money.xlsx:
  ID, when purchased, Year, Name of money, quality, amount paid,
  Denomination, Name, notes, QTY

Firestore fields:
  Year                     → Year (string)
  Name of money            → Description (what the note is)
  Name                     → Issuer / Series name (e.g. "Federal Reserve Note")
  quality                  → Condition
  amount paid              → Cost
  Denomination             → Denomination (e.g. "$1", "$20")
  when purchased           → Purchase Date
  notes                    → Personal Notes
  QTY                      → Quantity
  category                 → "currency"  (distinguishes from coins)
  currency_type            → inferred: "federal_reserve_note", "silver_certificate", etc.
  country                  → "US" (default)
  source                   → "excel_import"
  source_file              → "Paper Money.xlsx"

Usage:
    python _scripts/import_aj_currency.py --dry-run
    python _scripts/import_aj_currency.py
"""

import os, sys, uuid, re, argparse
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import openpyxl
import google.auth
from google.cloud import firestore

PROJECT       = "studio-9101802118-8c9a8"
TARGET_EMAIL  = "jseaman1204@gmail.com"
SOURCE_FILE   = r"C:\Users\ericd\Documents\MyVertexProject\AJ's Coins\issue uploads\Paper Money.xlsx"
BATCH_SIZE    = 400

# Column name normalization
COL_MAP = {
    "id":               "personal_ref",
    "when purchased":   "purchase_date",
    "year":             "year",
    "name of money":    "description",
    "quality":          "condition",
    "amount paid":      "cost",
    "denomination":     "denomination_raw",
    "name":             "series_name",
    "notes":            "personal_notes",
    "qty":              "quantity",
}

# Infer currency_type from description / series_name
CURRENCY_TYPE_MAP = [
    ("federal reserve",      "federal_reserve_note"),
    ("silver certificate",   "silver_certificate"),
    ("gold certificate",     "gold_certificate"),
    ("treasury note",        "treasury_note"),
    ("united states note",   "united_states_note"),
    ("national bank",        "national_bank_note"),
    ("fractional",           "fractional_currency"),
    ("confederate",          "confederate"),
    ("colonial",             "colonial"),
    ("foreign",              "foreign"),
]

def infer_currency_type(description: str, series: str) -> str:
    combined = (description + " " + series).lower()
    for keyword, ctype in CURRENCY_TYPE_MAP:
        if keyword in combined:
            return ctype
    return "other"

def normalize_denomination(raw: str) -> str:
    """Normalize denomination — ensure $ prefix for US amounts."""
    raw = str(raw or "").strip()
    if not raw:
        return ""
    # If it's already a dollar amount like $1, $20, return as-is
    if raw.startswith("$"):
        return raw
    # If it's a number, add $
    try:
        val = float(raw)
        if val >= 1:
            return f"${int(val)}"
        return raw
    except (ValueError, TypeError):
        return raw

def read_excel(filepath: str) -> list[dict]:
    wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        wb.close()
        return []
    raw_headers = [str(h).strip().lower() if h else "" for h in rows[0]]
    headers = [COL_MAP.get(h, h) for h in raw_headers]
    records = []
    for row in rows[1:]:
        if all(v is None for v in row):
            continue
        rec = {h: v for h, v in zip(headers, row) if v is not None}
        records.append(rec)
    wb.close()
    return records

def build_doc(rec: dict) -> dict:
    now = datetime.now(tz=timezone.utc)

    year = str(rec.get("year", "") or "").strip()
    if year.endswith(".0"):
        year = year[:-2]

    cost = str(rec.get("cost", "") or "").strip()
    if cost and not cost.startswith("$"):
        try:
            cost = f"${float(cost):.2f}"
        except (ValueError, TypeError):
            pass

    purchase_date = rec.get("purchase_date", "")
    if hasattr(purchase_date, "date"):
        purchase_date = str(purchase_date.date())
    else:
        purchase_date = str(purchase_date or "").strip()

    description = str(rec.get("description", "") or "").strip()
    series_name = str(rec.get("series_name", "") or "").strip()
    denom_raw   = str(rec.get("denomination_raw", "") or "").strip()
    denomination = normalize_denomination(denom_raw)

    qty = rec.get("quantity", 1)
    try:
        qty = int(float(str(qty))) if qty else 1
    except (ValueError, TypeError):
        qty = 1

    return {
        "Year":              year,
        "Description":       description,
        "Series/Issuer":     series_name,
        "Denomination":      denomination,
        "Condition":         str(rec.get("condition", "") or "").strip(),
        "Cost":              cost,
        "Purchase Date":     purchase_date,
        "Personal Notes":    str(rec.get("personal_notes", "") or "").strip(),
        "Personal Ref #":    str(rec.get("personal_ref", "") or "").strip(),
        "Quantity":          qty,
        "Country":           "US",
        "category":          "currency",
        "currency_type":     infer_currency_type(description, series_name),
        "source":            "excel_import",
        "source_file":       "Paper Money.xlsx",
        "user_email":        TARGET_EMAIL,
        "inventoryStatus":   "UNCHECKED",
        "created_at":        now,
        "import_batch":      "currency_import_2026-06-20",
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.dry_run:
        print("⚠️  DRY RUN\n")

    credentials, _ = google.auth.default()
    db = firestore.Client(credentials=credentials, project=PROJECT)

    # Currency goes into a SEPARATE sub-collection
    col_ref = db.collection("users").document(TARGET_EMAIL).collection("currency")

    records = read_excel(SOURCE_FILE)
    print(f"Paper Money.xlsx: {len(records)} records\n")

    # Show currency type breakdown
    types = {}
    for rec in records:
        d = str(rec.get("description","") or "")
        s = str(rec.get("series_name","") or "")
        t = infer_currency_type(d, s)
        types[t] = types.get(t, 0) + 1
    print("Currency type breakdown:")
    for t, n in sorted(types.items(), key=lambda x: -x[1]):
        print(f"  {n:>4}  {t}")
    print()

    batch    = db.batch()
    batch_ct = 0
    total    = 0
    errors   = 0

    for rec in records:
        try:
            doc = build_doc(rec)
            doc_id = str(uuid.uuid4())

            if not args.dry_run:
                batch.set(col_ref.document(doc_id), doc)
                batch_ct += 1
                if batch_ct >= BATCH_SIZE:
                    batch.commit()
                    batch = db.batch()
                    batch_ct = 0

            total += 1
            if total <= 5 or (total % 50 == 0):
                yr   = doc.get("Year", "?")
                desc = doc.get("Description", "?")[:40]
                dnom = doc.get("Denomination", "")
                cond = doc.get("Condition", "")
                print(f"  {yr:>6}  {desc:<42}  {dnom:>5}  {cond}")

        except Exception as e:
            print(f"  ERROR: {e}")
            errors += 1

    if not args.dry_run and batch_ct > 0:
        batch.commit()

    print(f"\n{'DRY RUN ' if args.dry_run else ''}Results:")
    print(f"  Imported : {total}")
    print(f"  Errors   : {errors}")
    if not args.dry_run:
        print(f"\n  ✅  {total} currency items added to")
        print(f"      users/{TARGET_EMAIL}/currency")

if __name__ == "__main__":
    main()
