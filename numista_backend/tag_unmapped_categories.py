#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
tag_unmapped_categories.py
==========================
Phase 2 of the pre-heal normalization pass.

Targets the 53 unmapped denomination records and applies category tags
to Firestore so the image-healing engine and melt-value calculator
can correctly skip or route non-standard items.

Rules applied
-------------
SET records (category: "set")
    Denominations: 5-Coin Set, Mint Set, Proof Set, Prestige Proof Set,
    Birth Year Set, Year Set, Various, Mixed, and any multi-coin text
    combinations (e.g. "Kennedy Half Dollar & Native American Dollar").

OTHER records (category: "other", inventory_status: "pending_review")
    Commercial / administrative placeholders:
    "Advertisement Items", "Coins-on-Approval".

Usage
-----
    python tag_unmapped_categories.py             # dry-run
    python tag_unmapped_categories.py --execute   # write to Firestore
"""

import sys
import re
import csv
import argparse
from pathlib import Path
from datetime import datetime
from collections import Counter

import firebase_admin
from firebase_admin import credentials, firestore

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR  = Path(__file__).resolve().parent
SA_KEY      = SCRIPT_DIR / "serviceAccountKey.json.json"
TARGET_USER = "jseaman1204@gmail.com"
UNMAPPED_CSV = SCRIPT_DIR.parent / "unmapped_denominations.csv"
TAG_LOG_OUT  = SCRIPT_DIR.parent / "category_tag_log.csv"

if not firebase_admin._apps:
    cred = credentials.Certificate(str(SA_KEY))
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ── CLASSIFICATION RULES ──────────────────────────────────────────────────────

# Denominations that unambiguously identify a multi-coin SET container
SET_DENOM_EXACT = {
    "5-coin set", "mint set", "proof set", "prestige proof set",
    "birth year set", "year set", "various", "mixed",
    "decade set", "transition set",
}

# Programs that imply a set even if denomination looks canonical
SET_PROGRAM_KEYWORDS = [
    "time capsule year set", "birth year set", "birth year sets",
    "year sets:", "mint sets", "proof set", "prestige proof set",
    "coin set", "america revisited",   # America Revisited = multi-coin sets
    "world war ii u.s. coin collection",  # multi-denom collection sets
    "denomination set",
    "coins-on-approval",
]

# Denominations containing '&' or ',' with multiple coin types
def is_multi_denom_text(denom: str) -> bool:
    d = denom.lower()
    return ("&" in d or "," in d) and len(denom) > 10

# Placeholder / commercial records
OTHER_PROGRAM_EXACT = {
    "advertisement items",
    "coins-on-approval",
}
OTHER_DENOM_EXACT = {
    "advertisement items",
    "coins-on-approval",
}


def classify(raw_denom: str, raw_program: str, current_cat: str) -> tuple[str, str]:
    """
    Returns (new_category, reason) or ('', '') if no change needed.
    """
    d = raw_denom.lower().strip()
    p = raw_program.lower().strip()
    c = (current_cat or "").lower().strip()

    # Already correctly tagged
    if c in ("set", "other", "paper_currency"):
        return "", "already tagged"

    # OTHER: commercial placeholders
    if d in OTHER_DENOM_EXACT or p in OTHER_PROGRAM_EXACT:
        return "other", "commercial placeholder"

    # SET: exact denomination match
    if d in SET_DENOM_EXACT:
        return "set", f"set denomination: {raw_denom}"

    # SET: multi-coin text in denomination field
    if is_multi_denom_text(raw_denom):
        return "set", f"multi-coin denomination text: {raw_denom}"

    # SET: program keyword match
    for kw in SET_PROGRAM_KEYWORDS:
        if kw in p:
            return "set", f"set program keyword '{kw}': {raw_program}"

    return "", ""


# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Tag multi-coin sets and placeholder records in Firestore."
    )
    parser.add_argument("--execute", action="store_true",
                        help="Write category tags to Firestore (default: dry-run).")
    args = parser.parse_args()
    dry_run = not args.execute

    mode = "DRY-RUN (read-only)" if dry_run else "EXECUTE — WRITING TO FIRESTORE"
    print("=" * 70)
    print("NUMISTA.AI -- CATEGORY TAGGING PASS (Phase 2)")
    print(f"Mode   : {mode}")
    print(f"Run at : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    rows = list(csv.DictReader(open(UNMAPPED_CSV, encoding="utf-8")))
    print(f"\n[LOAD] {len(rows)} rows from {UNMAPPED_CSV.name}")

    col_ref = db.collection("users").document(TARGET_USER).collection("coins")
    counters = Counter()
    log_rows = []

    for r in rows:
        doc_id      = r["doc_id"]
        raw_denom   = r["raw_denom"]
        raw_program = r["raw_program"]
        raw_cat     = r.get("raw_category", "")
        src_file    = r.get("source_document_name", "")
        inv_num     = r.get("invoice_number", "")
        orig_desc   = r.get("original_description", "")

        new_cat, reason = classify(raw_denom, raw_program, raw_cat)

        updates = {}
        if new_cat == "set":
            updates = {"category": "set"}
            counters["set_tagged"] += 1
        elif new_cat == "other":
            updates = {"category": "other", "inventoryStatus": "pending_review"}
            counters["other_tagged"] += 1
        else:
            counters["no_change"] += 1

        if updates and not dry_run:
            col_ref.document(doc_id).set(updates, merge=True)
            counters["firestore_writes"] += 1

        log_rows.append({
            "doc_id":               doc_id,
            "raw_denom":            raw_denom,
            "raw_program":          raw_program,
            "source_document_name": src_file,
            "invoice_number":       inv_num,
            "original_description": orig_desc,
            "assigned_category":    new_cat or "(no change)",
            "reason":               reason,
            "dry_run":              dry_run,
        })

    # Write log
    print(f"\n[LOG] Writing tag log to {TAG_LOG_OUT.name} ...")
    with open(TAG_LOG_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "doc_id", "raw_denom", "raw_program", "source_document_name",
            "invoice_number", "original_description",
            "assigned_category", "reason", "dry_run"
        ])
        w.writeheader()
        w.writerows(log_rows)
    print(f"  [OK] {len(log_rows)} rows written.")

    # Summary
    bar = "=" * 70
    print(f"\n{bar}")
    print("  CATEGORY TAGGING SUMMARY")
    print(f"  Mode: {mode}")
    print(bar)
    print(f"  {'Records evaluated':<40}: {len(rows):>5}")
    print(f"  {'Tagged as category: set':<40}: {counters['set_tagged']:>5}")
    print(f"  {'Tagged as category: other':<40}: {counters['other_tagged']:>5}")
    print(f"  {'No change (already clean)':<40}: {counters['no_change']:>5}")
    if not dry_run:
        print(f"  {'Firestore documents updated':<40}: {counters['firestore_writes']:>5}")
    print(bar)
    if dry_run:
        print("\n  ► DRY-RUN complete. Run with --execute to apply.")
    else:
        print("\n  ✅ Tags written to Firestore.")

    # Preview table
    print("\n  PREVIEW — ASSIGNED CATEGORIES:")
    print(f"  {'Category':<12} {'Denomination':<45} {'Source File'}")
    print("  " + "-" * 85)
    for row in log_rows:
        cat   = row["assigned_category"]
        denom = row["raw_denom"][:43]
        src   = row["source_document_name"] or "(unknown)"
        print(f"  {cat:<12} {denom:<45} {src}")
    print()


if __name__ == "__main__":
    main()
