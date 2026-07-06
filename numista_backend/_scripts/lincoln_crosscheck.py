# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
lincoln_crosscheck.py
──────────────────────────────────────────────────────────────────────────────
Cross-checks the 6 Lincoln penny Excel files against Firestore for
jseaman1204@gmail.com and identifies coins that are in the Excel but NOT
in Firestore.

The 6 files:
  Lincoln head pennies including wheaties - 1.xlsx    (370 rows)
  Lincoln head pennies including wheaties - 1B.xlsx   (373 rows)
  Lincoln head pennies including wheaties - 2.xlsx    (373 rows)
  Lincoln head pennies including wheaties - 2B.xlsx   (371 rows)
  Lincoln head pennies including wheaties - 3.xlsx    (368 rows)
  Lincoln head pennies including wheaties - 3B.xlsx   (421 rows)
  Total: 2,276 rows (many expected to already be in Firestore)

Strategy:
  1. Load all Lincoln cent coins from Firestore
  2. Load all rows from the 6 Excel files
  3. Build a composite key: Year + Mint + Condition (normalised)
  4. Find rows that have NO matching key in Firestore
  5. Write missing rows to lincoln_missing_YYYY-MM-DD.csv

Usage:
    python _scripts/lincoln_crosscheck.py --dry-run
    python _scripts/lincoln_crosscheck.py
"""

import os, sys, csv, re, argparse, glob
from datetime import datetime
from collections import defaultdict

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import openpyxl
import google.auth
from google.cloud import firestore

PROJECT        = "studio-9101802118-8c9a8"
TARGET_EMAIL   = "jseaman1204@gmail.com"
LINCOLN_DIR    = r"C:\Users\ericd\Documents\MyVertexProject\AJ's Coins\AJ excel Completed uploads"
OUTPUT_DIR     = r"C:\Users\ericd\Documents\MyVertexProject"

LINCOLN_FILES = [
    "Lincoln head pennies including wheaties - 1.xlsx",
    "Lincoln head pennies including wheaties - 1B.xlsx",
    "Lincoln head pennies including wheaties - 2.xlsx",
    "Lincoln head pennies including wheaties - 2B.xlsx",
    "Lincoln head pennies including wheaties - 3.xlsx",
    "Lincoln head pennies including wheaties - 3B.xlsx",
]

COL_MAP = {
    "id":               "personal_ref",
    "date purchased":   "purchase_date",
    "when purchased":   "purchase_date",
    "year":             "year",
    "description":      "description",
    "name":             "description",
    "quality":          "condition",
    "amount paid":      "cost",
    "denomination":     "denomination",
    "notes":            "personal_notes",
    "qty":              "quantity",
}

def norm_year(y) -> str:
    if y is None:
        return ""
    y = str(y).strip().replace(".0", "")
    # Handle mint-mark-in-year like "1955S" or "1943D"
    return y.upper()

def norm_cond(c) -> str:
    if c is None:
        return ""
    return str(c).strip().lower().replace("-", "").replace(" ", "")

def make_key(year: str, mint: str, condition: str) -> str:
    return f"{norm_year(year)}|{(mint or '').strip().upper()}|{norm_cond(condition)}"

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
        rec = {h: v for h, v in zip(headers, row)}
        rec["_source_file"] = os.path.basename(filepath)
        records.append(rec)
    wb.close()
    return records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="Analyse only, do not import missing coins")
    args = ap.parse_args()

    credentials, _ = google.auth.default()
    db = firestore.Client(credentials=credentials, project=PROJECT)
    col_ref = db.collection("users").document(TARGET_EMAIL).collection("coins")

    # ── Load Lincoln cents from Firestore ─────────────────────────────────
    print("Loading Lincoln cents from Firestore...")
    firestore_keys = set()
    print("  Loading all coins for key comparison (filtering locally)...")
    all_docs = list(col_ref.stream())
    for doc in all_docs:
        data = doc.to_dict() or {}
        prog = str(data.get("Program/Series", "") or "").lower()
        if "lincoln" not in prog and "wheat" not in prog and "penny" not in prog:
            continue
        year = str(data.get("Year", "") or "")
        mint = str(data.get("Mint Mark", "") or "")
        cond = str(data.get("Condition", "") or "")
        cost = str(data.get("Cost", "") or "")
        firestore_keys.add(make_key(year, mint, cond))
        # Also add cost-free key variant
        firestore_keys.add(make_key(year, mint, ""))

    print(f"  Found {len(firestore_keys):,} unique Lincoln key variants in Firestore\n")

    # ── Load all Excel rows ───────────────────────────────────────────────
    excel_rows = []
    for filename in LINCOLN_FILES:
        fp = os.path.join(LINCOLN_DIR, filename)
        rows = read_excel(fp)
        print(f"  {filename}: {len(rows)} rows")
        excel_rows.extend(rows)

    print(f"\n  Total Excel rows: {len(excel_rows):,}\n")

    # ── Cross-check ───────────────────────────────────────────────────────
    missing  = []
    matched  = 0
    no_year  = 0

    for rec in excel_rows:
        year  = str(rec.get("year", "") or "").strip().replace(".0", "")
        # Extract mint from year if appended (e.g. "1909S" → year=1909, mint=S)
        mint_from_year = ""
        m = re.match(r'^(\d{4})([A-Z])$', year.upper())
        if m:
            year, mint_from_year = m.group(1), m.group(2)

        mint  = str(rec.get("mint", "") or mint_from_year).strip().upper()
        cond  = str(rec.get("condition", "") or "").strip()
        cost  = str(rec.get("cost", "") or "").strip()

        if not year:
            no_year += 1
            continue

        key      = make_key(year, mint, cond)
        key_bare = make_key(year, mint, "")

        if key in firestore_keys or key_bare in firestore_keys:
            matched += 1
        else:
            missing.append({
                "year":          year,
                "mint_mark":     mint,
                "condition":     cond,
                "cost":          cost,
                "description":   str(rec.get("description", "") or ""),
                "personal_notes":str(rec.get("personal_notes", "") or ""),
                "source_file":   rec.get("_source_file", ""),
                "personal_ref":  str(rec.get("personal_ref", "") or ""),
                "purchase_date": str(rec.get("purchase_date", "") or ""),
            })

    # ── Results ───────────────────────────────────────────────────────────
    print(f"{'='*55}")
    print(f"  Lincoln Penny Cross-Check Results")
    print(f"{'='*55}")
    print(f"  Total Excel rows      : {len(excel_rows):,}")
    print(f"  No year (skipped)     : {no_year:,}")
    print(f"  Matched in Firestore  : {matched:,}")
    print(f"  MISSING from Firestore: {len(missing):,}")

    if not missing:
        print("\n  ✅  All Lincoln pennies accounted for!")
        return

    # Write missing CSV
    date_str = datetime.now().strftime("%Y-%m-%d")
    out_path = os.path.join(OUTPUT_DIR, f"lincoln_missing_{date_str}.csv")
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=missing[0].keys())
        writer.writeheader()
        writer.writerows(missing)

    print(f"\n  CSV saved: {out_path}")

    # Year distribution of missing
    year_counts = defaultdict(int)
    for r in missing:
        year_counts[r["year"]] += 1
    print(f"\n  Top years missing:")
    for yr, ct in sorted(year_counts.items(), key=lambda x: -x[1])[:20]:
        print(f"    {yr}: {ct}")

    if not args.dry_run:
        print(f"\n  Run with --import flag to add these {len(missing)} coins to Firestore.")
        print(f"  (import functionality coming in next version)")

if __name__ == "__main__":
    main()
