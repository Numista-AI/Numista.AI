#!/usr/bin/env python3
"""
migrate_pcgs_field.py — Ensures all PCGS-imported coins have the full extended schema.

For any coin where Grading Service = 'PCGS' or source = 'pcgs_api' that is
missing new fields added in the April 28 PCGS API integration, this script
adds safe default values so downstream queries and the Flutter app don't break.

Fields ensured:
  PCGS Number, Die Variety, Series Name, Population,
  Is Silver (bool), Is NFC Secure (bool), source

Usage:
    python migrate_pcgs_field.py
    python migrate_pcgs_field.py --user eric@numista.ai
    python migrate_pcgs_field.py --dry-run
"""
import argparse
import firebase_admin
from firebase_admin import credentials, firestore

SERVICE_ACCOUNT_KEY = "serviceAccountKey.json.json"

PCGS_DEFAULTS = {
    "PCGS Number":   "",
    "Die Variety":   "",
    "Series Name":   "",
    "Population":    "",
    "Is Silver":     False,
    "Is NFC Secure": False,
    "source":        "pcgs_api",
}


def is_pcgs(data: dict) -> bool:
    grading = str(data.get("Grading Service") or "").upper()
    source  = str(data.get("source") or "").lower()
    return "PCGS" in grading or source == "pcgs_api"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", help="Limit to one user email")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    firebase_admin.initialize_app(credentials.Certificate(SERVICE_ACCOUNT_KEY))
    db = firestore.client()

    user_refs = ([db.collection("users").document(args.user)]
                 if args.user else list(db.collection("users").stream()))

    total_pcgs = updated = skipped = 0

    for ur in user_refs:
        uid     = ur.id
        doc_ref = ur.reference if hasattr(ur, "reference") else ur
        print(f"\n── {uid} ──")

        for doc in doc_ref.collection("coins").stream():
            data = doc.to_dict() or {}
            if not is_pcgs(data):
                continue

            total_pcgs += 1
            missing = {k: v for k, v in PCGS_DEFAULTS.items() if k not in data}

            if not missing:
                skipped += 1
                continue

            if args.dry_run:
                print(f"  [DRY] {doc.id[:24]} → +{list(missing.keys())}")
            else:
                doc.reference.update(missing)
                print(f"  ✅ {doc.id[:24]} → +{list(missing.keys())}")
            updated += 1

    print(f"\n{'='*50}")
    print(f"{'DRY RUN ' if args.dry_run else ''}DONE  pcgs_coins={total_pcgs}  updated={updated}  complete={skipped}")

if __name__ == "__main__":
    main()
