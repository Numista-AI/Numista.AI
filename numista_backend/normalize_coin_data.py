#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
normalize_coin_data.py
======================
Pre-heal data normalization pass for Numista.AI.

Targets the 662 "missing image" coin records for jseaman1204@gmail.com
and enforces Golden Schema field standards before the image-healing run.

Rules applied
-------------
1. DENOMINATION CORRECTION
   Maps all colloquial / type-name strings to the six canonical US Mint
   legal-tender denominations:
       Cent | Five Cents | Dime | Quarter Dollar | Half Dollar | Dollar
   Paper-currency face values (e.g. "$1 Silver Certificate") are preserved
   as-is and routed to the currency pipeline instead.

2. PROGRAM / SERIES RESCUE
   When a type name (e.g. "Washington Quarter") was stored in Denomination
   and the Program/Series field is blank, the type name is migrated there
   so no descriptive context is lost.

3. PROGRAM NAME CASING NORMALIZATION
   Collapses duplicate program entries that differ only in casing
   (e.g. "THE U.S. NICKEL COLLECTION" → "The U.S. Nickel Collection").

4. PAPER CURRENCY SEPARATION
   Detects paper-currency records by denomination pattern, program name,
   or explicit category and sets their Firestore `category` field to
   "paper_currency" so the coin-image matcher skips them.

Mode flags
----------
  --dry-run  (default)  Print what WOULD change; no Firestore writes.
  --execute             Apply changes to Firestore live.

Usage
-----
    python normalize_coin_data.py             # dry-run (safe)
    python normalize_coin_data.py --execute   # write to Firestore
"""

import sys
import re
import csv
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.field_path import FieldPath

# Force UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── CONFIG ────────────────────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).resolve().parent
SA_KEY      = SCRIPT_DIR / "serviceAccountKey.json.json"
TARGET_USER = "jseaman1204@gmail.com"
LOG_OUT     = SCRIPT_DIR.parent / "normalization_log.csv"

# ── INIT FIREBASE ─────────────────────────────────────────────────────────────
if not firebase_admin._apps:
    cred = credentials.Certificate(str(SA_KEY))
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ─────────────────────────────────────────────────────────────────────────────
# RULE 1 — CANONICAL DENOMINATION MAP
# Keys are lower-cased for matching. Value is the canonical US Mint string.
# ─────────────────────────────────────────────────────────────────────────────
DENOM_MAP: dict[str, str] = {
    # ── CENT ──────────────────────────────────────────────────────────────────
    "cent":                          "Cent",
    "1c":                            "Cent",
    "1 cent":                        "Cent",
    "one cent":                      "Cent",
    "penny":                         "Cent",
    "lincoln cent":                  "Cent",
    "lincoln head cent":             "Cent",
    "indian head cent":              "Cent",
    "flying eagle cent":             "Cent",
    "large cent":                    "Cent",
    "half cent":                     "Half Cent",   # obsolete — keep distinct
    "two-cent piece":                "Two Cents",   # obsolete — keep distinct
    "two cent piece":                "Two Cents",

    # ── FIVE CENTS ────────────────────────────────────────────────────────────
    "five cents":                    "Five Cents",
    "5c":                            "Five Cents",
    "5 cent":                        "Five Cents",
    "five cent":                     "Five Cents",
    "nickel":                        "Five Cents",
    "jefferson nickel":              "Five Cents",
    "buffalo nickel":                "Five Cents",
    "liberty head nickel":          "Five Cents",
    "shield nickel":                 "Five Cents",
    "three cent nickel":             "Three Cents",   # obsolete — keep distinct
    "three-cent nickel":             "Three Cents",
    "liberty seated half dime":      "Half Dime",     # obsolete — keep distinct
    "capped bust half dime":         "Half Dime",

    # ── DIME ──────────────────────────────────────────────────────────────────
    "dime":                          "Dime",
    "10c":                           "Dime",
    "10 cent":                       "Dime",
    "ten cents":                     "Dime",
    "roosevelt dime":                "Dime",
    "mercury dime":                  "Dime",
    "barber dime":                   "Dime",
    "liberty seated dime":           "Dime",
    "capped bust dime":              "Dime",
    "draped bust dime":              "Dime",
    "10c fractional currency":       "10 Cents (Fractional)",  # currency
    "15c fractional currency":       "15 Cents (Fractional)",

    # ── QUARTER DOLLAR ────────────────────────────────────────────────────────
    "quarter":                       "Quarter Dollar",
    "quarter dollar":                "Quarter Dollar",
    "25c":                           "Quarter Dollar",
    "25 cent":                       "Quarter Dollar",
    "washington quarter":            "Quarter Dollar",
    "state quarter":                 "Quarter Dollar",
    "statehood quarter":             "Quarter Dollar",
    "standing liberty quarter":      "Quarter Dollar",
    "barber quarter":                "Quarter Dollar",
    "liberty seated quarter":        "Quarter Dollar",
    "draped bust quarter":           "Quarter Dollar",
    "capped bust quarter":           "Quarter Dollar",
    "25c fractional currency":       "25 Cents (Fractional)",  # currency

    # ── HALF DOLLAR ───────────────────────────────────────────────────────────
    "half dollar":                   "Half Dollar",
    "50c":                           "Half Dollar",
    "50 cent":                       "Half Dollar",
    "fifty cents":                   "Half Dollar",
    "kennedy half dollar":           "Half Dollar",
    "franklin half dollar":          "Half Dollar",
    "walking liberty half dollar":   "Half Dollar",
    "barber half dollar":            "Half Dollar",
    "liberty seated half dollar":    "Half Dollar",
    "capped bust half dollar":       "Half Dollar",
    "50c fractional currency":       "50 Cents (Fractional)",  # currency

    # ── DOLLAR ────────────────────────────────────────────────────────────────
    "dollar":                        "Dollar",
    "dollar coin":                   "Dollar",
    "$1":                            "Dollar",
    "one dollar":                    "Dollar",
    "morgan silver dollar":          "Dollar",
    "peace silver dollar":           "Dollar",
    "peace dollar":                  "Dollar",
    "eisenhower dollar":             "Dollar",
    "presidential dollar":           "Dollar",
    "innovation dollar":             "Dollar",
    "$1 innovation dollar":          "Dollar",
    "american innovation dollar":    "Dollar",
    "native american dollar":        "Dollar",
    "native american $1 coin":       "Dollar",
    "silver dollar":                 "Dollar",
    "american silver eagle":         "Dollar",
    "silver eagle":                  "Dollar",
    "american silver eagle dollar":  "Dollar",
    "american eagle silver dollar":  "Dollar",
    "$1 silver eagle":               "Dollar",
    "silver eagle dollar":           "Dollar",
    "commemorative dollar":          "Dollar",
    # Already-canonical strings — add so they pass through cleanly
    "half dollar":                   "Half Dollar",
    "dime":                          "Dime",
    "dollar":                        "Dollar",
    # Multi-denom sets — leave as descriptive, map to special value
    "$1 american silver eagle":      "Dollar",
}

# ─────────────────────────────────────────────────────────────────────────────
# RULE 2 — TYPE-NAME → PROGRAM RESCUE
# When these strings sit in Denomination AND Program/Series is blank,
# migrate them to Program/Series.
# ─────────────────────────────────────────────────────────────────────────────
TYPE_TO_PROGRAM: dict[str, str] = {
    "washington quarter":           "Washington Quarter",
    "jefferson nickel":             "Jefferson Nickel",
    "buffalo nickel":               "Buffalo Nickel",
    "liberty head nickel":          "Liberty Head Nickel",
    "shield nickel":                "Shield Nickel",
    "roosevelt dime":               "Roosevelt Dime",
    "mercury dime":                 "Mercury Dime",
    "barber dime":                  "Barber Dime",
    "liberty seated dime":          "Liberty Seated Dime",
    "barber quarter":               "Barber Quarter",
    "liberty seated quarter":       "Liberty Seated Quarter",
    "capped bust quarter":          "Capped Bust Quarter",
    "draped bust quarter":          "Draped Bust Quarter",
    "kennedy half dollar":          "Kennedy Half Dollar",
    "franklin half dollar":         "Franklin Half Dollar",
    "walking liberty half dollar":  "Walking Liberty Half Dollar",
    "barber half dollar":           "Barber Half Dollar",
    "liberty seated half dollar":   "Liberty Seated Half Dollar",
    "capped bust half dollar":      "Capped Bust Half Dollar",
    "morgan silver dollar":         "Morgan Silver Dollar",
    "peace silver dollar":          "Peace Silver Dollar",
    "peace dollar":                 "Peace Dollar",
    "eisenhower dollar":            "Eisenhower Dollar",
    "american silver eagle":        "American Silver Eagle",
    "silver eagle":                 "American Silver Eagle",
    "presidential dollar":          "Presidential Dollar",
    "lincoln cent":                 "Lincoln Cent",
    "lincoln head cent":            "Lincoln Cent",
    "indian head cent":             "Indian Head Cent",
    "flying eagle cent":            "Flying Eagle Cent",
}

# ─────────────────────────────────────────────────────────────────────────────
# RULE 3 — PROGRAM CASING NORMALIZATION MAP
# Maps any casing variant to the canonical Title Case string.
# ─────────────────────────────────────────────────────────────────────────────
PROGRAM_CANONICAL: dict[str, str] = {
    # U.S. Nickel Collection variants
    "the u.s. nickel collection":                           "The U.S. Nickel Collection",
    "the u.s. nickel collection - shipment 9":              "The U.S. Nickel Collection - Shipment 9",
    "the u.s. nickel collection - shipment 11":             "The U.S. Nickel Collection - Shipment 11",
    "the u.s. nickel collection - shipment 13":             "The U.S. Nickel Collection - Shipment 13",
    # Dime collection variants
    "u.s. dime collection selection":                       "U.S. Dime Collection Selection",
    # American Eagle variants
    "the complete 2020 american eagle ngcx silver dollar set": "The Complete 2020 American Eagle NGCX Silver Dollar Set",
    # Silver Eagle variants
    "the west point burnished american eagle silver dollar collection": "The West Point Burnished American Eagle Silver Dollar Collection",
    # Silver Eagle Proof
    "the complete original-design proof silver eagle dollar collection": "The Complete Original-Design Proof Silver Eagle Dollar Collection",
    # Half Dollar Club
    "the half dollar club selection":                       "The Half Dollar Club Selection",
    # Carson City Morgan
    "officially sealed carson city mint morgan silver dollars": "Officially Sealed Carson City Mint Morgan Silver Dollars",
    # Statehood Innovation
    "the statehood innovation dollar coin collection":       "The Statehood Innovation Dollar Coin Collection",
    # Morgan & Peace
    "the ultimate modern morgan and peace silver dollar collection": "The Ultimate Modern Morgan and Peace Silver Dollar Collection",
    # America Revisited
    "year sets: america revisited selection":               "Year Sets: America Revisited Selection",
    # Coin denomination set
    "the u.s. coin complete denomination set":              "The U.S. Coin Complete Denomination Set",
    # Paper Money Club
    "american paper money club selection":                  "American Paper Money Club Selection",
    # Half dollar club
    "the half dollar club selection":                       "The Half Dollar Club Selection",
    # Uncirculated sets
    "u.s. uncirculated coin mint sets":                     "U.S. Uncirculated Coin Mint Sets",
    # Modern commemorative
    "modern commemorative club selection":                  "Modern Commemorative Club Selection",
    # Rarely seen peace dollars
    "rarely seen peace silver dollars":                     "Rarely Seen Peace Silver Dollars",
    # 20th cent half dollar
    "20th cent. half dollar club selection":                "20th Century Half Dollar Club Selection",
    # America's first cents
    "america's first small-size one-cent coins":            "America's First Small-Size One-Cent Coins",
}

# ─────────────────────────────────────────────────────────────────────────────
# RULE 4 — PAPER CURRENCY DETECTION
# Any record matching these patterns is routed to category="paper_currency".
# ─────────────────────────────────────────────────────────────────────────────
CURRENCY_DENOM_PATTERNS = [
    r"federal reserve",
    r"silver certificate",
    r"gold certificate",
    r"legal tender note",
    r"treasury note",
    r"bank note",
    r"continental currency",
    r"colonial currency",
    r"obsolete",
    r"fractional currency",
    r"state note",
    r"national bank note",
    r"\$\d+\s*(federal|silver|gold|legal|treasury|bank|state|national|obsolete|continental|colonial)",
    r"^\$\d+$",      # bare dollar amounts like "$50", "$10", "$7"
    r"^\$\d+/\d+",   # fractional like "$1/6"
    r"^\$\d+\s*$",   # "$7", "$5" with optional space
    r"indian territory note",
    r"colonial",
]

CURRENCY_PROGRAM_PATTERNS = [
    r"paper money",
    r"federal reserve note",
    r"federal reserve bank note",
    r"silver certificate",
    r"fractional currency",
    r"obsolete note",
    r"large size",
    r"west river bank note",
    r"state of missouri note",
    r"jamul indian nation",
    r"continental currency",
    r"colonial currency",
]

CURRENCY_CATEGORY_VALUES = {
    "paper_currency", "currency", "note", "banknote", "paper"
}


def _matches(text: str, patterns: list[str]) -> bool:
    t = text.lower().strip()
    return any(re.search(p, t) for p in patterns)


def is_paper_currency(denom: str, program: str, category: str) -> bool:
    if (category or "").lower().strip() in CURRENCY_CATEGORY_VALUES:
        return True
    if _matches(denom, CURRENCY_DENOM_PATTERNS):
        return True
    if _matches(program, CURRENCY_PROGRAM_PATTERNS):
        return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def get_val(d: dict, *keys) -> str:
    for k in keys:
        v = d.get(k)
        if v is not None:
            return str(v).strip()
    return ""


def normalize_denom(raw: str) -> str | None:
    """Return canonical denomination, or None if not in map."""
    return DENOM_MAP.get(raw.lower().strip())


def rescue_program(raw_denom: str, current_program: str) -> str | None:
    """
    If raw_denom is a type name (e.g. 'Washington Quarter') and
    current_program is blank, return the rescued program string.
    """
    if current_program:
        return None
    return TYPE_TO_PROGRAM.get(raw_denom.lower().strip())


def canonical_program(raw: str) -> str | None:
    """Return canonical program casing, or None if already correct."""
    mapped = PROGRAM_CANONICAL.get(raw.lower().strip())
    if mapped and mapped != raw:
        return mapped
    return None


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Data normalization pass for Numista.AI coin records."
    )
    parser.add_argument(
        "--execute", action="store_true",
        help="Apply changes to Firestore. Default is dry-run (read-only)."
    )
    args = parser.parse_args()
    dry_run = not args.execute

    mode_label = "DRY-RUN (read-only)" if dry_run else "⚠️  EXECUTE — WRITING TO FIRESTORE"
    print("=" * 70)
    print("NUMISTA.AI -- DATA NORMALIZATION PASS")
    print(f"Mode         : {mode_label}")
    print(f"Target user  : {TARGET_USER}")
    print(f"Run at       : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # ── Step 1: Pull all coins with missing images ────────────────────────────
    print(f"\n[STEP 1] Fetching coins for {TARGET_USER} ...")
    col_ref = db.collection("users").document(TARGET_USER).collection("coins")
    docs    = list(col_ref.stream())
    print(f"         Total documents: {len(docs):,}")

    missing = []
    for doc in docs:
        d   = doc.to_dict()
        obv = (d.get("image_url_obverse") or "").strip()
        rev = (d.get("image_url_reverse") or "").strip()
        if not obv and not rev:
            missing.append((doc.id, doc.reference, d))

    print(f"         Missing-image docs: {len(missing):,}")

    # ── Step 2: Compute changes ───────────────────────────────────────────────
    print(f"\n[STEP 2] Analysing {len(missing):,} records ...")

    counters = defaultdict(int)
    log_rows = []

    for doc_id, doc_ref, d in missing:
        raw_denom   = get_val(d, "Denomination", "denomination")
        raw_program = get_val(d, "Program/Series", "program", "Program", "series")
        raw_theme   = get_val(d, "Theme/Subject", "theme", "subject")
        raw_cat     = get_val(d, "category")

        updates: dict = {}
        changes: list[str] = []

        # ── Rule 4 first: detect paper currency ──────────────────────────────
        if is_paper_currency(raw_denom, raw_program, raw_cat):
            if raw_cat != "paper_currency":
                updates["category"] = "paper_currency"
                changes.append(f"category: {repr(raw_cat)} → 'paper_currency'")
                counters["paper_currency_tagged"] += 1
            # Do NOT apply coin denomination rules to paper currency
        else:
            # ── Rule 2: rescue program name from denomination field ───────────
            rescued = rescue_program(raw_denom, raw_program)
            if rescued:
                updates["Program/Series"] = rescued
                changes.append(f"Program/Series: '' → {repr(rescued)} (rescued from Denomination)")
                counters["program_rescued"] += 1

            # ── Rule 1: normalize denomination ───────────────────────────────
            canonical_d = normalize_denom(raw_denom)
            if canonical_d and canonical_d != raw_denom:
                updates["Denomination"] = canonical_d
                changes.append(f"Denomination: {repr(raw_denom)} → {repr(canonical_d)}")
                counters["denom_corrected"] += 1
            elif not canonical_d and raw_denom:
                counters["denom_unmapped"] += 1

        # ── Rule 3: normalize program casing ─────────────────────────────────
        prog_to_check = updates.get("Program/Series", raw_program)
        canonical_p = canonical_program(prog_to_check)
        if canonical_p:
            updates["Program/Series"] = canonical_p
            changes.append(f"Program/Series casing: {repr(prog_to_check)} → {repr(canonical_p)}")
            counters["program_casing_fixed"] += 1

        if updates:
            counters["total_docs_changed"] += 1
            if not dry_run:
                # Firestore treats '/' in update() dict keys as nested path
                # separators. Fields like 'Program/Series' are stored as
                # literal top-level field names in this collection, so we
                # use set(merge=True) which accepts a plain dict without
                # path-parsing the keys.
                doc_ref.set(updates, merge=True)
                counters["firestore_writes"] += 1

        log_rows.append({
            "doc_id":      doc_id,
            "dry_run":     dry_run,
            "raw_denom":   raw_denom,
            "raw_program": raw_program,
            "raw_category":raw_cat,
            "changes":     " | ".join(changes) if changes else "no change",
            "updates_applied": str(updates) if updates else "",
        })

    # ── Step 3: Write log ─────────────────────────────────────────────────────
    print(f"\n[STEP 3] Writing normalization log to {LOG_OUT.name} ...")
    with open(LOG_OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "doc_id", "dry_run", "raw_denom", "raw_program", "raw_category",
            "changes", "updates_applied"
        ])
        writer.writeheader()
        writer.writerows(log_rows)
    print(f"  [OK] {len(log_rows):,} rows written to {LOG_OUT.name}")

    # ── Summary table ─────────────────────────────────────────────────────────
    bar = "=" * 70
    total = len(missing)
    unchanged = total - counters["total_docs_changed"]
    print(f"\n{bar}")
    print("  NORMALIZATION SUMMARY")
    print(f"  Mode: {mode_label}")
    print(bar)
    print(f"  {'Target records (missing images)':<45}: {total:>5,}")
    print(f"  {'Records requiring changes':<45}: {counters['total_docs_changed']:>5,}")
    print(f"  {'Records already clean (no change)':<45}: {unchanged:>5,}")
    print(f"  {'-' * 51}")
    print(f"  {'Denomination corrections':<45}: {counters['denom_corrected']:>5,}")
    print(f"  {'Type name rescued → Program/Series':<45}: {counters['program_rescued']:>5,}")
    print(f"  {'Program casing normalized':<45}: {counters['program_casing_fixed']:>5,}")
    print(f"  {'Paper currency records tagged':<45}: {counters['paper_currency_tagged']:>5,}")
    print(f"  {'Unmapped denominations (review needed)':<45}: {counters['denom_unmapped']:>5,}")
    if not dry_run:
        print(f"  {'Firestore documents updated':<45}: {counters['firestore_writes']:>5,}")
    print(bar)
    if dry_run:
        print("\n  ► This was a DRY-RUN. No data was written.")
        print("  ► Run with --execute to apply these changes to Firestore.")
    else:
        print("\n  ✅ Changes written to Firestore successfully.")
    print()


if __name__ == "__main__":
    main()
