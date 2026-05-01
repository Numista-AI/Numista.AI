"""
Export Reference Library — Firestore → CSV

Reads all documents from the `reference_library` Firestore collection and
writes them to a CSV so you can audit coverage and find gaps.

Usage:
    python export_reference_library.py                     # default output
    python export_reference_library.py --output my_file.csv
    python export_reference_library.py --us-only           # only US coin entries
"""

import argparse
import csv
import os
import sys
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore


# ── Firebase init ────────────────────────────────────────────────────────────
def _init_firebase():
    """Initialize Firebase Admin SDK if not already running."""
    if not firebase_admin._apps:
        # Use Application Default Credentials (gcloud auth)
        firebase_admin.initialize_app()


def export_reference_library(output_path: str, us_only: bool = False):
    """Fetch every doc in `reference_library` and write to CSV."""
    _init_firebase()
    db = firestore.client()

    print("Querying Firestore collection: reference_library ...")
    docs = db.collection("reference_library").stream()

    # Collect all rows first so we can discover every possible field key
    rows = []
    all_keys = set()
    for doc in docs:
        data = doc.to_dict()
        data["doc_id"] = doc.id
        all_keys.update(data.keys())
        rows.append(data)

    if not rows:
        print("[!] No documents found in reference_library!")
        return

    # Optional: filter to US coins only
    if us_only:
        before = len(rows)
        rows = [r for r in rows if _is_us_coin(r)]
        print(f"  Filtered to US coins: {len(rows)} / {before}")

    # Sort columns in a friendly order
    priority = [
        "doc_id", "denomination", "year", "year_int", "side",
        "source", "category", "tags",
        "gcs_url", "gcs_path",
        "attribution", "license", "license_url", "kaggle_url",
    ]
    ordered_cols = [k for k in priority if k in all_keys]
    ordered_cols += sorted(all_keys - set(ordered_cols))

    # Write CSV
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ordered_cols, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"[OK] Exported {len(rows)} reference images -> {os.path.abspath(output_path)}")

    # Quick stats
    denoms = {}
    for r in rows:
        d = r.get("denomination", "Unknown") or "Unknown"
        denoms[d] = denoms.get(d, 0) + 1
    print("\n-- Coverage Summary --")
    for denom, count in sorted(denoms.items(), key=lambda x: -x[1]):
        print(f"  {denom:20s}  {count:>5}")


def _is_us_coin(row: dict) -> bool:
    """Heuristic check whether a reference image is a US coin."""
    text = " ".join(str(v) for v in row.values()).lower()
    us_indicators = [
        "us ", "united states", "usa", "u.s.", "american",
        "quarter", "dime", "nickel", "cent", "penny",
        "half dollar", "morgan", "peace dollar", "silver eagle",
        "walking liberty", "mercury", "buffalo", "lincoln",
        "jefferson", "roosevelt", "kennedy", "franklin",
        "washington", "sacagawea", "eisenhower",
    ]
    return any(ind in text for ind in us_indicators)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Export Firestore reference_library to CSV"
    )
    parser.add_argument(
        "--output", "-o",
        default=f"reference_library_export_{datetime.now().strftime('%Y%m%d')}.csv",
        help="Output CSV filename (default: reference_library_export_YYYYMMDD.csv)",
    )
    parser.add_argument(
        "--us-only",
        action="store_true",
        help="Only include entries that appear to be US coins",
    )
    args = parser.parse_args()
    export_reference_library(args.output, us_only=args.us_only)
