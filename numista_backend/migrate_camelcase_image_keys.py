"""
migrate_camelcase_image_keys.py
================================
One-shot migration script to normalize legacy camelCase image keys into lowercase snake_case.
Only copies camelCase keys into snake_case if snake_case is missing or empty.
Never overwrites an existing, valid snake_case field.

Usage:
  python migrate_camelcase_image_keys.py --email eric.seaman@yahoo.com --dry-run
  python migrate_camelcase_image_keys.py --email eric.seaman@yahoo.com --execute
"""

import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

# Force UTF-8 stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import firebase_admin
from firebase_admin import credentials, firestore

def run_migration(email: str, execute: bool = False):
    email = email.strip().lower()
    print(f"=== CamelCase Image Key Migration ===")
    print(f"Target User: users/{email}/coins")
    print(f"Execution Mode: {'LIVE EXECUTE' if execute else 'DRY RUN (Simulated)'}")
    print("=" * 40)

    key_path = Path(__file__).parent / "serviceAccountKey.json.json"
    if not key_path.exists():
        key_path = Path(__file__).parent / "serviceAccountKey.json"
    
    if not firebase_admin._apps:
        cred = credentials.Certificate(str(key_path))
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    coins_ref = db.collection("users").document(email).collection("coins")
    docs = list(coins_ref.stream())
    
    total_docs = len(docs)
    modified_docs = []

    for doc in docs:
        data = doc.to_dict() or {}
        updates = {}

        # Obverse
        legacy_obv = data.get("imageUrlObverse")
        canon_obv  = data.get("image_url_obverse")
        if legacy_obv and not canon_obv:
            updates["image_url_obverse"] = legacy_obv

        # Reverse
        legacy_rev = data.get("imageUrlReverse")
        canon_rev  = data.get("image_url_reverse")
        if legacy_rev and not canon_rev:
            updates["image_url_reverse"] = legacy_rev

        # Obverse GCS
        legacy_obv_gcs = data.get("imageUrlObverse_gcs")
        canon_obv_gcs  = data.get("image_url_obverse_gcs")
        if legacy_obv_gcs and not canon_obv_gcs:
            updates["image_url_obverse_gcs"] = legacy_obv_gcs

        # Reverse GCS
        legacy_rev_gcs = data.get("imageUrlReverse_gcs")
        canon_rev_gcs  = data.get("image_url_reverse_gcs")
        if legacy_rev_gcs and not canon_rev_gcs:
            updates["image_url_reverse_gcs"] = legacy_rev_gcs

        if updates:
            modified_docs.append({
                "doc_id": doc.id,
                "title": data.get("name") or data.get("title") or "Unknown",
                "updates": updates
            })

    print(f"Total documents inspected: {total_docs}")
    print(f"Documents requiring camelCase -> snake_case key migration: {len(modified_docs)}")

    for m in modified_docs[:10]:
        print(f"  - [{m['doc_id']}] {m['title']} -> Keys: {list(m['updates'].keys())}")
    if len(modified_docs) > 10:
        print(f"  ... and {len(modified_docs) - 10} more.")

    if execute and modified_docs:
        print(f"\nApplying atomic updates to {len(modified_docs)} documents ...")
        now_iso = datetime.now(timezone.utc).isoformat()
        for m in modified_docs:
            doc_ref = coins_ref.document(m["doc_id"])
            payload = {
                **m["updates"],
                "camelcase_migrated_at": now_iso
            }
            doc_ref.set(payload, merge=True)
        print("✓ All documents migrated to canonical lowercase snake_case.")
    elif not execute:
        print("\n[DRY RUN COMPLETE] 0 writes performed. Run with --execute to apply changes.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate camelCase image keys to snake_case")
    parser.add_argument("--email", required=True, help="User email")
    parser.add_argument("--execute", action="store_true", help="Perform live DB updates")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without writing")
    args = parser.parse_args()

    execute_flag = args.execute and not args.dry_run
    run_migration(args.email, execute=execute_flag)
