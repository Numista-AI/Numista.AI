"""
gen_aj_questions_report.py
──────────────────────────────────────────────────────────────────────────────
Scans jseaman1204@gmail.com's Firestore collection and flags every coin/record
that has missing key info or is ambiguous enough that we need to ask AJ about it.

Flags checked:
  1. Missing Year (blank or unparseable)
  2. Missing Program/Series AND missing Denomination
  3. Description looks like a SET not an individual coin
  4. Looks like currency/paper money (should be in currency collection)
  5. Quantity > 1 with no breakdown (set entered as single record)
  6. Year looks like a date range (e.g., "1880-1885CC")
  7. Missing Denomination only
  8. Program/Series is very generic or unclear

Output: AJ_questions_report_YYYY-MM-DD.csv  (sorted by flag priority)
"""

import os, sys, re, csv
from datetime import datetime

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import google.auth
from google.cloud import firestore

PROJECT      = "studio-9101802118-8c9a8"
TARGET_EMAIL = "jseaman1204@gmail.com"
OUTPUT_DIR   = r"C:\Users\ericd\Documents\MyVertexProject"

# Keywords that suggest a SET, not an individual coin
SET_KEYWORDS = [
    "set", "sets", "proof set", "mint set", "collection", "series",
    "mixed", "lot", "piece", "pcs", "assorted", "complete",
    "type set", "year set", "date set",
]

# Keywords that suggest CURRENCY / PAPER MONEY
CURRENCY_KEYWORDS = [
    "note", "notes", "bill", "bills", "federal reserve",
    "bank note", "banknote", "paper money", "currency",
    "silver certificate", "gold certificate", "treasury note",
    "frn", "legal tender",
]

# Generic/unclear program names that need clarification
VAGUE_PROGRAMS = {
    "miscellaneous", "misc", "unknown", "other", "coin", "coins",
    "silver", "gold", "copper", "us coin", "american coin",
}

YEAR_RE = re.compile(r'^\d{4}[A-Z]?$')

def flag_record(data: dict) -> list[tuple[int, str]]:
    """Returns list of (priority, flag_description) for this record. Empty = no issues."""
    flags = []

    year    = str(data.get("Year", "") or "").strip().replace(".0", "")
    program = str(data.get("Program/Series", "") or "").strip()
    denom   = str(data.get("Denomination", "") or "").strip()
    desc    = str(data.get("Original Description from source", "") or "").strip().lower()
    notes   = str(data.get("Personal Notes", "") or "").strip().lower()
    cond    = str(data.get("Condition", "") or "").strip()
    cost    = str(data.get("Cost", "") or "").strip()
    qty_raw = data.get("Quantity", 1)

    try:
        qty = int(float(str(qty_raw))) if qty_raw else 1
    except (ValueError, TypeError):
        qty = 1

    full_text = (program + " " + desc + " " + notes).lower()

    # ── Flag: looks like paper money ─────────────────────────────────────
    if any(kw in full_text for kw in CURRENCY_KEYWORDS):
        flags.append((1, "Possible CURRENCY — should be in currency collection"))

    # ── Flag: looks like a SET ────────────────────────────────────────────
    is_set = any(kw in full_text for kw in SET_KEYWORDS)
    if is_set and qty > 1:
        flags.append((1, f"SET with Qty={qty} — needs individual coin breakdown"))
    elif is_set:
        flags.append((2, "Looks like a SET — confirm if individual coin or set record"))

    # ── Flag: year is a date range ────────────────────────────────────────
    if re.search(r'\d{4}[-–]\d{2,4}', year):
        flags.append((1, f"Year is a range '{year}' — which specific year(s)?"))

    # ── Flag: missing year ────────────────────────────────────────────────
    if not year:
        flags.append((2, "Missing Year"))
    elif not YEAR_RE.match(year) and not re.match(r'^\d{4}[A-Z]?$', year):
        if not re.search(r'\d{4}', year):
            flags.append((2, f"Year '{year}' looks invalid"))

    # ── Flag: missing program AND denomination ────────────────────────────
    if not program and not denom:
        flags.append((2, "Missing both Program/Series and Denomination"))

    # ── Flag: vague/unclear program ───────────────────────────────────────
    if program and program.lower() in VAGUE_PROGRAMS:
        flags.append((3, f"Program/Series '{program}' is too generic — what coin is this?"))

    # ── Flag: missing denomination only ──────────────────────────────────
    if not denom and program:
        flags.append((3, "Missing Denomination"))

    # ── Flag: missing condition ───────────────────────────────────────────
    if not cond:
        flags.append((4, "Missing Condition/Grade"))

    return flags


def main():
    credentials, _ = google.auth.default()
    db = firestore.Client(credentials=credentials, project=PROJECT)

    print(f"Loading coins for {TARGET_EMAIL}...")
    coins = list(
        db.collection("users").document(TARGET_EMAIL).collection("coins").stream()
    )
    print(f"  {len(coins):,} coins loaded")

    flagged_rows = []
    flag_counts = {}

    for doc in coins:
        data = doc.to_dict() or {}
        flags = flag_record(data)
        if not flags:
            continue

        year    = str(data.get("Year", "") or "").strip().replace(".0", "")
        program = str(data.get("Program/Series", "") or "").strip()
        denom   = str(data.get("Denomination", "") or "").strip()
        cond    = str(data.get("Condition", "") or "").strip()
        cost    = str(data.get("Cost", "") or "").strip()
        mint    = str(data.get("Mint Mark", "") or "").strip()
        desc    = str(data.get("Original Description from source", "") or "").strip()
        notes   = str(data.get("Personal Notes", "") or "").strip()
        qty     = str(data.get("Quantity", "") or "1").strip()
        src_file = str(data.get("source_file", "") or "").strip()

        for priority, flag_text in flags:
            flag_counts[flag_text] = flag_counts.get(flag_text, 0) + 1
            flagged_rows.append({
                "priority":     priority,
                "flag":         flag_text,
                "coin_id":      doc.id,
                "year":         year,
                "program":      program,
                "denomination": denom,
                "mint_mark":    mint,
                "condition":    cond,
                "cost":         cost,
                "quantity":     qty,
                "description":  desc[:80],
                "personal_notes": notes[:60],
                "source_file":  src_file,
                "question_for_AJ": "",  # left blank for Eric/AJ to fill in
            })

    # Sort: priority first, then program
    flagged_rows.sort(key=lambda r: (r["priority"], r["program"], r["year"]))

    # Write CSV
    date_str = datetime.now().strftime("%Y-%m-%d")
    out_path = os.path.join(OUTPUT_DIR, f"AJ_questions_report_{date_str}.csv")

    if flagged_rows:
        with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=flagged_rows[0].keys())
            writer.writeheader()
            writer.writerows(flagged_rows)

    # ── Summary ─────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  AJ Questions Report — {date_str}")
    print(f"{'='*60}")
    print(f"  Total coins scanned  : {len(coins):,}")
    print(f"  Records with flags   : {len(set(r['coin_id'] for r in flagged_rows)):,}")
    print(f"  Total flag instances : {len(flagged_rows):,}")
    print(f"\n  By flag type:")
    for flag_text, count in sorted(flag_counts.items(), key=lambda x: -x[1]):
        print(f"    {count:>4}  {flag_text}")
    print(f"\n  Output: {out_path}")

    # Show top 10 priority-1 items
    p1 = [r for r in flagged_rows if r["priority"] == 1]
    if p1:
        print(f"\n  PRIORITY 1 — Needs immediate clarification ({len(set(r['coin_id'] for r in p1))} records):")
        seen = set()
        for r in p1[:15]:
            if r["coin_id"] in seen:
                continue
            seen.add(r["coin_id"])
            yr  = r["year"] or "(no year)"
            pgm = r["program"] or r["description"][:30] or "(no program)"
            print(f"    {yr:>10}  {pgm[:45]:<45}  {r['flag'][:50]}")


if __name__ == "__main__":
    main()
