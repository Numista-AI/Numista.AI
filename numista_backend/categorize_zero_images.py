# -*- coding: utf-8 -*-
"""
categorize_zero_images.py
--------------------------
Reads jseaman_image_gaps.csv, filters MISSING_BOTH rows (133 coins with
NO images at all), then categorizes each as:
  - SET/COLLECTION RECORD (no image needed by design)
  - SINGLE COIN NEEDS IMAGE (requires manual sourcing or generation)
"""

import csv
import re
import os

CSV_PATH   = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\jseaman_image_gaps.csv"
OUTPUT_CSV = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\jseaman_zero_image_breakdown.csv"

# ─── Keywords that flag a SET / COLLECTION record ────────────────────────────
# Matched case-insensitively against program/series AND denomination fields
SET_KEYWORDS = [
    r"\bset\b",
    r"\bcollection\b",
    r"\blot\b",
    r"\bfolder\b",
    r"\balbum\b",
    r"\bassorted\b",
    r"\b100\s*coins\b",
    r"\bioo\s*countries\b",
    r"\bcoins?\s+from\b",
    r"\bcoins?\s+of\b",
    r"\bworld\s+coins?\b",
    r"\bwwii\b",
    r"\byear\s*set\b",
    r"\bmint\s*set\b",
    r"\bproof\s*set\b",
    r"\btype\s*set\b",
    r"\bdate\s*set\b",
    r"\bcomplete\s+set\b",
    r"\btreasure\s*chest\b",
    r"\bstamp\s*set\b",
    r"\bnote\s*and\s*stamp\b",
    r"\bcoin\s*note\b",
    r"\bannual\s*set\b",
    r"\bcommemorative\s*set\b",
    r"\bp\s*&\s*d\b",
    r"\buncirculated\s*set\b",
    r"\bcountries\b",
    r"\bwidow",          # Widow's Mite sets / lots
    r"\bjannaeus\b",     # Ancient bronze lots
    r"\b103-",           # Ancient dated lots like "103-76BC"
    r"\bwashington.*note\b",
    r"\bgeorge\s+washington\b",  # usually a commemorative set item
    r"\bbook\b",
]

SET_PATTERN = re.compile("|".join(SET_KEYWORDS), re.IGNORECASE)


def is_set_record(denom: str, program: str) -> bool:
    combined = (denom + " " + program).strip()
    return bool(SET_PATTERN.search(combined))


def main():
    # ── Load CSV ──────────────────────────────────────────────────────────────
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        all_rows = list(csv.DictReader(f))

    missing_both = [r for r in all_rows if r["status"].strip().upper() == "MISSING_BOTH"]
    print(f"Total MISSING_BOTH rows: {len(missing_both)}")

    # ── Dump raw data for inspection ──────────────────────────────────────────
    print("\n--- RAW MISSING_BOTH RECORDS ---")
    print(f"{'#':>3}  {'Denom':<30}  {'Year':<6}  {'Mint':<5}  {'Program/Series'}")
    print("-" * 110)
    for i, r in enumerate(missing_both, 1):
        print(f"{i:>3}  {r['denomination']:<30}  {r['year']:<6}  {r['mint_mark']:<5}  {r['program']}")

    # ── Categorize ────────────────────────────────────────────────────────────
    sets   = []
    singles = []

    for r in missing_both:
        denom   = r["denomination"].strip()
        program = r["program"].strip()
        year    = r["year"].strip()
        mint    = r["mint_mark"].strip()

        category = "SET/COLLECTION RECORD" if is_set_record(denom, program) else "SINGLE COIN NEEDS IMAGE"
        r["category"] = category

        if category == "SET/COLLECTION RECORD":
            sets.append(r)
        else:
            singles.append(r)

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  CATEGORIZATION SUMMARY")
    print("=" * 70)
    print(f"  Total MISSING_BOTH records     : {len(missing_both)}")
    print(f"  SET/COLLECTION RECORDS         : {len(sets)}")
    print(f"  SINGLE COINS NEEDING IMAGES    : {len(singles)}")
    print("=" * 70)

    print(f"\n--- SINGLE COINS NEEDING IMAGES ({len(singles)}) ---")
    print(f"{'#':>3}  {'Year':<6}  {'Mint':<5}  {'Denomination':<30}  {'Program/Series'}")
    print("-" * 100)
    for i, r in enumerate(singles, 1):
        print(f"{i:>3}  {r['year']:<6}  {r['mint_mark']:<5}  {r['denomination']:<30}  {r['program']}")

    print(f"\n--- SET/COLLECTION RECORDS ({len(sets)}) ---")
    print(f"{'#':>3}  {'Year':<6}  {'Mint':<5}  {'Denomination':<30}  {'Program/Series'}")
    print("-" * 100)
    for i, r in enumerate(sets, 1):
        print(f"{i:>3}  {r['year']:<6}  {r['mint_mark']:<5}  {r['denomination']:<30}  {r['program']}")

    # ── Write output CSV ──────────────────────────────────────────────────────
    fieldnames = [
        "category", "status", "denomination", "year", "mint_mark", "program",
        "condition", "grading_service", "cert_number",
        "image_url_obverse", "image_url_reverse", "doc_id"
    ]
    output_rows = sorted(missing_both, key=lambda x: (x["category"], x["denomination"].lower()))

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"\nOutput CSV saved to: {OUTPUT_CSV}")
    print(f"  ({len(output_rows)} rows written)\n")


if __name__ == "__main__":
    main()
