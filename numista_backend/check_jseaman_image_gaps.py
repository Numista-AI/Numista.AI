# -*- coding: utf-8 -*-
"""
check_jseaman_image_gaps.py
----------------------------
Queries Firestore for all coins in the jseaman1204@gmail.com account and
identifies which coins are missing obverse and/or reverse images.

Collection path: users/jseaman1204@gmail.com/coins
Project: studio-9101802118-8c9a8
"""

import csv
import json
import os
import sys

from google.oauth2 import service_account
from google.cloud import firestore

# ─── Configuration ───────────────────────────────────────────────────────────
PROJECT_ID      = "studio-9101802118-8c9a8"
CREDENTIALS_FILE = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json.json"
USER_EMAIL      = "jseaman1204@gmail.com"
OUTPUT_CSV      = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\jseaman_image_gaps.csv"

# Firestore collection path (matches auth_service.dart: 'users/${user.email}/coins')
COINS_COLLECTION = f"users/{USER_EMAIL}/coins"

# ─── Helpers ─────────────────────────────────────────────────────────────────

def is_empty(val) -> bool:
    """Return True if a field is missing, None, or an empty/whitespace string."""
    if val is None:
        return True
    if isinstance(val, str) and val.strip() == "":
        return True
    return False


def get_field(doc: dict, *keys, default=""):
    """Return the first non-empty value found among the given keys, or default."""
    for key in keys:
        val = doc.get(key)
        if not is_empty(val):
            return val
    return default


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    # 1. Authenticate
    if not os.path.exists(CREDENTIALS_FILE):
        sys.exit(f"ERROR: Credentials file not found: {CREDENTIALS_FILE}")

    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    db = firestore.Client(project=PROJECT_ID, credentials=credentials)

    # 2. Fetch all coins
    print(f"Fetching all coins from: {COINS_COLLECTION} …")
    coins_ref = db.collection(COINS_COLLECTION)
    docs = list(coins_ref.stream())
    total = len(docs)
    print(f"  -> {total} coin documents retrieved.")

    # 3. Classify each coin
    both_missing   = []   # no images at all
    only_obverse   = []   # has obverse, missing reverse
    only_reverse   = []   # has reverse, missing obverse
    has_both       = []   # both images present

    for doc in docs:
        data = doc.to_dict() or {}
        obverse = data.get("image_url_obverse")
        reverse = data.get("image_url_reverse")

        has_obv = not is_empty(obverse)
        has_rev = not is_empty(reverse)

        entry = {
            "doc_id":          doc.id,
            "year":            get_field(data, "Year", "year", "coin_year", default=""),
            "mint_mark":       get_field(data, "Mint Mark", "mint_mark", "mintMark", "Mint", default=""),
            "denomination":    get_field(data, "Denomination", "denomination", default=""),
            "program":         get_field(data, "Program/Series", "program", "series", default=""),
            "condition":       get_field(data, "Condition", "condition", default=""),
            "grading_service": get_field(data, "Grading Service", "grading_service", "gradingService", default=""),
            "cert_number":     get_field(data, "Cert Number", "cert_number", "certNumber",
                                         "PCGS Cert #", "NGC Cert #", "Cert #", default=""),
            "image_url_obverse": obverse or "",
            "image_url_reverse": reverse or "",
            "status": "",
        }

        if not has_obv and not has_rev:
            entry["status"] = "MISSING_BOTH"
            both_missing.append(entry)
        elif has_obv and not has_rev:
            entry["status"] = "MISSING_REVERSE"
            only_obverse.append(entry)
        elif not has_obv and has_rev:
            entry["status"] = "MISSING_OBVERSE"
            only_reverse.append(entry)
        else:
            entry["status"] = "HAS_BOTH"
            has_both.append(entry)

    # 4. All coins with at least one missing image (sorted by denomination)
    incomplete = both_missing + only_obverse + only_reverse
    incomplete.sort(key=lambda x: (x["denomination"].lower(), x["year"]))

    # 5. Print summary
    print("\n" + "=" * 60)
    print(f"  IMAGE GAP REPORT — {USER_EMAIL}")
    print("=" * 60)
    print(f"  Total coins in collection : {total}")
    print(f"  Both images present        : {len(has_both)}")
    print(f"  Completely missing (no img): {len(both_missing)}")
    print(f"  Missing reverse only       : {len(only_obverse)}")
    print(f"  Missing obverse only       : {len(only_reverse)}")
    print(f"  Total with any gap         : {len(incomplete)}")
    print("=" * 60)

    if incomplete:
        print(f"\n{'#':<4} {'Denom':<22} {'Year':<6} {'Mint':<5} {'Program':<28} {'Condition':<12} {'Grading Svc':<14} {'Cert #':<14} {'Status'}")
        print("-" * 130)
        for i, c in enumerate(incomplete, 1):
            print(
                f"{i:<4} "
                f"{c['denomination']:<22} "
                f"{c['year']:<6} "
                f"{c['mint_mark']:<5} "
                f"{c['program']:<28} "
                f"{c['condition']:<12} "
                f"{c['grading_service']:<14} "
                f"{c['cert_number']:<14} "
                f"{c['status']}"
            )
    else:
        print("\nAll coins have both images!")

    # 6. Write CSV
    fieldnames = [
        "status", "denomination", "year", "mint_mark", "program",
        "condition", "grading_service", "cert_number",
        "image_url_obverse", "image_url_reverse", "doc_id"
    ]
    all_coins = incomplete + has_both  # missing first, then complete
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_coins)

    print(f"\nCSV saved to: {OUTPUT_CSV}")
    print(f"  ({len(all_coins)} rows written - missing coins listed first)\n")


if __name__ == "__main__":
    main()
