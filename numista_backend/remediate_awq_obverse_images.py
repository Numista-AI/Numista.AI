"""
remediate_awq_obverse_images.py
================================
Safe, idempotent remediation script for American Women Quarters (AWQ) obverse images.
Replaces the US Mint composite split banner (half Washington / half Maya Angelou)
with the official clean Laura Gardin Fraser George Washington portrait obverse.

Remediates:
1. The global reference index `coin_image_index` (which feeds CoinImageService across Flutter).
2. User collections `users/{email}/coins` where coins reference the old composite URL.

Usage:
  python remediate_awq_obverse_images.py --email eric.seaman@yahoo.com --dry-run
  python remediate_awq_obverse_images.py --email eric.seaman@yahoo.com --execute
"""

import os
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

OLD_COMPOSITE_URLS = [
    "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/2022-american-women-quarters-coin-uncirculated-obverse-philadelphia.jpg",
    "https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/generic_quarters/2022-american-women-quarters-coin-uncirculated-obverse-philadelphia.jpg",
]

CLEAN_FRASER_OBVERSE_URL = "https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/american_women_quarters/awq_fraser_washington_obverse.jpg"
CLEAN_FRASER_GCS_PATH = "gs://numista-reference-library/reference_library/bulk_programs/american_women_quarters/awq_fraser_washington_obverse.jpg"

def is_user_uploaded(url: str, email: str) -> bool:
    if not url:
        return False
    if url.startswith("data:image"):
        return True
    email_clean = email.strip().lower()
    if f"users/{email_clean}/photo_id/" in url or f"users/{email_clean}/" in url:
        return True
    return False

def run_remediation(email: str, execute: bool = False):
    email = email.strip().lower()
    print(f"=== AWQ Obverse Remediation ===")
    print(f"Target User Collection: users/{email}/coins")
    print(f"Target Global Index: coin_image_index")
    print(f"Execution Mode: {'LIVE EXECUTE' if execute else 'DRY RUN (Simulated)'}")
    print(f"Replacement Asset: {CLEAN_FRASER_OBVERSE_URL}")
    print("=" * 40)

    key_path = Path(__file__).parent / "serviceAccountKey.json.json"
    if not key_path.exists():
        key_path = Path(__file__).parent / "serviceAccountKey.json"
    
    if not firebase_admin._apps:
        cred = credentials.Certificate(str(key_path))
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    now_iso = datetime.now(timezone.utc).isoformat()
    
    # ── 1. Remediate coin_image_index ──────────────────────────────────────────
    print("\n--- Scanning coin_image_index ---")
    idx_ref = db.collection("coin_image_index")
    idx_docs = list(idx_ref.where("program", "==", "american-women-quarters").stream())
    
    matched_idx = []
    for doc in idx_docs:
        data = doc.to_dict() or {}
        obv_obj = data.get("obverse")
        if isinstance(obv_obj, dict):
            pub_url = obv_obj.get("public_url") or ""
            if pub_url in OLD_COMPOSITE_URLS:
                matched_idx.append({
                    "doc_id": doc.id,
                    "type": "coin_image_index",
                    "old_url": pub_url,
                    "new_url": CLEAN_FRASER_OBVERSE_URL
                })
    
    print(f"[coin_image_index] Total AWQ Index Docs: {len(idx_docs)}")
    print(f"[coin_image_index] Matched Composite Obverses: {len(matched_idx)}")
    for m in matched_idx:
        print(f"  - [{m['doc_id']}]")

    # ── 2. Remediate User Coins Collection ────────────────────────────────────
    print(f"\n--- Scanning users/{email}/coins ---")
    coins_ref = db.collection("users").document(email).collection("coins")
    docs = list(coins_ref.stream())
    
    matched_coins = []
    skipped_user_uploads = []
    
    for doc in docs:
        data = doc.to_dict() or {}
        obv = data.get("image_url_obverse") or data.get("imageUrlObverse") or ""
        
        # Check if user uploaded
        if is_user_uploaded(obv, email):
            skipped_user_uploads.append(doc.id)
            continue
            
        # Match old composite URLs
        if obv in OLD_COMPOSITE_URLS:
            matched_coins.append({
                "doc_id": doc.id,
                "type": "user_coin",
                "title": data.get("name") or data.get("title") or data.get("Coin Name") or "Unknown",
                "old_url": obv,
                "new_url": CLEAN_FRASER_OBVERSE_URL,
            })

    print(f"[users/{email}/coins] Total documents: {len(docs)}")
    print(f"[users/{email}/coins] Matched Composite Obverses: {len(matched_coins)}")
    print(f"[users/{email}/coins] Skipped User Uploads: {len(skipped_user_uploads)}")

    all_matched = matched_idx + matched_coins

    # Save rollback JSON
    tmp_dir = Path(__file__).parent / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    rollback_file = tmp_dir / f"awq_rollback_{email.replace('@', '_at_')}.json"
    
    with open(rollback_file, "w", encoding="utf-8") as f:
        json.dump(all_matched, f, indent=2)
    print(f"\nRollback manifest written to: {rollback_file}")

    if execute:
        print(f"\nApplying atomic updates ...")
        # Update index docs
        for m in matched_idx:
            doc_ref = idx_ref.document(m["doc_id"])
            doc_ref.set({
                "obverse": {
                    "attribution": "US Mint",
                    "source_tier": 1,
                    "gcs_path": CLEAN_FRASER_GCS_PATH,
                    "source_label": "us_mint",
                    "indexed_at": now_iso,
                    "public_url": CLEAN_FRASER_OBVERSE_URL,
                    "previous_public_url": m["old_url"],
                    "remediated_at": now_iso,
                    "remediated_by": "remediate_awq_obverse_v4",
                }
            }, merge=True)
        print(f"✓ Remediated {len(matched_idx)} coin_image_index documents.")

        # Update user coins docs
        for m in matched_coins:
            doc_ref = coins_ref.document(m["doc_id"])
            doc_ref.set({
                "image_url_obverse": CLEAN_FRASER_OBVERSE_URL,
                "previous_image_url_obverse": m["old_url"],
                "remediated_at": now_iso,
                "remediated_by": "remediate_awq_obverse_v4",
            }, merge=True)
        print(f"✓ Remediated {len(matched_coins)} user coin documents.")
        print("\n[EXECUTE COMPLETE] In-place remediation finished cleanly.")
    else:
        print("\n[DRY RUN COMPLETE] 0 writes performed. Run with --execute to apply changes.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remediate AWQ obverse composite images")
    parser.add_argument("--email", required=True, help="User email (e.g. eric.seaman@yahoo.com)")
    parser.add_argument("--execute", action="store_true", help="Perform live DB updates")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without writing")
    args = parser.parse_args()

    execute_flag = args.execute and not args.dry_run
    run_remediation(args.email, execute=execute_flag)
