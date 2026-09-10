#!/usr/bin/env python3
"""
One-shot Firestore key migration for grokbot@numista.ai coins.

Normalizes lowercase/snake_case field names to PascalCase canonical keys
so Cards, sort, and image lookups work correctly.

Usage:
  python migrate_grokbot_keys.py                # dry-run (default)
  python migrate_grokbot_keys.py --write         # actually write changes
  python migrate_grokbot_keys.py --write --stats  # write + rebuild collection_stats

Safety rails:
  - ONLY touches grokbot@numista.ai — hard-coded, never parameterized
  - Additive: never deletes the lowercase key, only adds PascalCase if missing
  - Dry-run by default
"""

import argparse
import os
import sys

import firebase_admin
from firebase_admin import credentials, firestore

# ── Hard-coded safety rail ──
TARGET_EMAIL = "grokbot@numista.ai"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SA_KEY_PATH = os.path.join(SCRIPT_DIR, "..", "serviceAccountKey.json")
PROJECT_ID = "studio-9101802118-8c9a8"

FIELD_MAP = {
    "year": "Year",
    "mint_mark": "Mint Mark",
    "denomination": "Denomination",
    "condition": "Condition",
    "cost_basis": "Cost",
    "cost": "Cost",
    "purchase_cost": "Cost",
    "variety": "Variety",
    "theme_subject": "Theme/Subject",
    "program_series": "Program/Series",
    "storage_location": "Storage Location",
    "certification_number": "Certification Number",
}


def main():
    parser = argparse.ArgumentParser(description="Migrate grokbot coin keys to PascalCase")
    parser.add_argument("--write", action="store_true", help="Actually write changes (default: dry-run)")
    parser.add_argument("--stats", action="store_true", help="Rebuild collection_stats after migration")
    args = parser.parse_args()

    # Initialize Firebase (same pattern as create_grokbot_account.py)
    if not firebase_admin._apps:
        if os.path.exists(SA_KEY_PATH):
            cred = credentials.Certificate(SA_KEY_PATH)
            firebase_admin.initialize_app(cred, {"projectId": PROJECT_ID})
        else:
            firebase_admin.initialize_app(options={"projectId": PROJECT_ID})
    db = firestore.client()

    user_ref = db.collection("users").document(TARGET_EMAIL)
    coins_ref = user_ref.collection("coins")

    print(f"{'WRITE MODE' if args.write else 'DRY-RUN'} — target: {TARGET_EMAIL}")
    print(f"Scanning users/{TARGET_EMAIL}/coins ...")

    docs = list(coins_ref.stream())
    print(f"Found {len(docs)} coin documents.\n")

    migrated_count = 0
    already_ok_count = 0
    sample_before = []
    sample_after = []

    for doc in docs:
        data = doc.to_dict()
        updates = {}

        for lc_key, canonical in FIELD_MAP.items():
            if lc_key in data and canonical not in data:
                updates[canonical] = data[lc_key]

        if updates:
            migrated_count += 1
            if len(sample_before) < 5:
                sample_before.append({
                    "doc_id": doc.id,
                    "year_lc": data.get("year"),
                    "Year_pc": data.get("Year"),
                    "mint_lc": data.get("mint_mark"),
                    "Mint_pc": data.get("Mint Mark"),
                    "denom_lc": data.get("denomination"),
                    "Denom_pc": data.get("Denomination"),
                })
                after = dict(sample_before[-1])
                after.update({f"[+]{k}": v for k, v in updates.items()})
                sample_after.append(after)

            if args.write:
                coins_ref.document(doc.id).update(updates)
        else:
            already_ok_count += 1

    print("=" * 60)
    print(f"Total docs:     {len(docs)}")
    print(f"Need migration: {migrated_count}")
    print(f"Already OK:     {already_ok_count}")
    print("=" * 60)

    if sample_before:
        print("\n── Sample BEFORE (up to 5 docs) ──")
        for s in sample_before:
            print(f"  {s}")
        print("\n── Sample AFTER (keys added) ──")
        for s in sample_after:
            print(f"  {s}")

    if args.write:
        print(f"\n[OK] WROTE {migrated_count} doc updates to Firestore.")
    else:
        print(f"\n[DRY-RUN] complete. Use --write to apply changes.")

    # Rebuild collection_stats if requested
    if args.write and args.stats:
        print("\n-- Rebuilding collection_stats --")
        stats_ref = user_ref.collection("metadata").document("collection_stats")
        coins_snap = list(coins_ref.stream())
        coin_count = 0
        supply_count = 0
        est_value = 0.0

        for doc in coins_snap:
            d = doc.to_dict()
            if d.get("item_type") == "supply" or d.get("is_supply") is True:
                supply_count += 1
            else:
                coin_count += 1
                # Sum best available value
                for val_key in ("cpgRetail", "greysheetBid", "AI Estimated Value"):
                    raw = d.get(val_key)
                    if raw is not None:
                        try:
                            v = float(str(raw).replace("$", "").replace(",", "").strip())
                            if v > 0:
                                est_value += v
                                break
                        except (ValueError, TypeError):
                            continue

        stats_data = {
            "coin_count": coin_count,
            "supply_count": supply_count,
            "est_value": round(est_value, 2),
            "last_rebuilt": firestore.SERVER_TIMESTAMP,
        }
        stats_ref.set(stats_data, merge=True)
        print(f"  coin_count:   {coin_count}")
        print(f"  supply_count: {supply_count}")
        print(f"  est_value:    ${est_value:.2f}")
        print("  [OK] collection_stats rebuilt.")


if __name__ == "__main__":
    main()
