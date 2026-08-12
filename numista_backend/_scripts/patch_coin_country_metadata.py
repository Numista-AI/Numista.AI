import os
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore

# Determine service account key path
script_dir = Path(__file__).resolve().parent
backend_dir = script_dir.parent
key_path = backend_dir / "serviceAccountKey.json.json"
if not key_path.exists():
    key_path = backend_dir / "serviceAccountKey.json"

if not firebase_admin._apps:
    print(f"[patch_metadata] Initializing Firebase Admin with key: {key_path}")
    cred = credentials.Certificate(str(key_path))
    firebase_admin.initialize_app(cred)

db = firestore.client()

US_ALLOW_LIST = {
    "united states", "usa", "us", "united states of america", "u.s.", "u.s.a.", 
    "united states mint", "puerto rico", "guam", "u.s. virgin islands", "usvi", 
    "american samoa", "northern mariana islands", "confederate states", "csa", "us philippines"
}

def normalize_country(raw_country):
    if not raw_country or not str(raw_country).strip():
        return "", True, True  # empty/null -> country="", is_foreign=True, review_needed=True
    
    clean = str(raw_country).strip()
    clean_lower = clean.lower()
    
    if clean_lower in US_ALLOW_LIST:
        return "United States", False, False
    
    # Capitalize nicely if standard non-US
    return clean, True, False

def patch_user_collection(user_ref, user_identifier, dry_run=False):
    metrics = {
        "user": user_identifier,
        "examined": 0,
        "patched": 0,
        "already_valid": 0,
        "flagged_review": 0,
    }
    
    for subcoll in ["coins", "currency"]:
        docs = list(user_ref.collection(subcoll).stream())
        print(f"\n[patch_metadata] User '{user_identifier}' -> Subcollection '{subcoll}' (count: {len(docs)})")
        
        for doc in docs:
            metrics["examined"] += 1
            data = doc.to_dict() or {}
            
            raw_country = data.get("country")
            if raw_country is None:
                raw_country = data.get("Country")
                
            existing_is_foreign = data.get("is_foreign")
            existing_review_needed = data.get("review_needed", False)
            
            norm_country, is_foreign, review_needed = normalize_country(raw_country)
            
            # Determine if update is needed
            needs_update = False
            if raw_country != norm_country:
                needs_update = True
            if existing_is_foreign != is_foreign:
                needs_update = True
            if existing_review_needed != review_needed:
                needs_update = True
                
            if review_needed:
                metrics["flagged_review"] += 1
                
            if needs_update:
                metrics["patched"] += 1
                iso_ts = datetime.now(timezone.utc).isoformat()
                
                update_payload = {
                    "country": norm_country,
                    "is_foreign": is_foreign,
                    "review_needed": review_needed,
                    "country_normalized_at": iso_ts,
                }
                
                print(f"  [{'DRY-RUN' if dry_run else 'PATCHING'}] Doc ID: {doc.id}")
                print(f"    Raw Country: '{raw_country}' -> Norm Country: '{norm_country}'")
                print(f"    is_foreign: {existing_is_foreign} -> {is_foreign} | review_needed: {review_needed}")
                
                if not dry_run:
                    user_ref.collection(subcoll).document(doc.id).set(update_payload, merge=True)
            else:
                metrics["already_valid"] += 1
                
    return metrics

def main():
    parser = argparse.ArgumentParser(description="In-place Metadata Patch for Country and is_foreign")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing to Firestore")
    parser.add_argument("--user", type=str, help="Target specific user email or UID (default: all active users)")
    args = parser.parse_args()

    print(f"===============================================================")
    print(f"  FIRESTORE METADATA REPAIR RUNBOOK (Dry Run: {args.dry_run})")
    print(f"===============================================================")

    if args.user:
        target_users = [args.user]
    else:
        # Stream top-level users
        users_stream = list(db.collection("users").stream())
        target_users = [u.id for u in users_stream]

    total_metrics = {
        "examined": 0,
        "patched": 0,
        "already_valid": 0,
        "flagged_review": 0,
    }

    for user_id in target_users:
        user_ref = db.collection("users").document(user_id)
        m = patch_user_collection(user_ref, user_id, dry_run=args.dry_run)
        total_metrics["examined"] += m["examined"]
        total_metrics["patched"] += m["patched"]
        total_metrics["already_valid"] += m["already_valid"]
        total_metrics["flagged_review"] += m["flagged_review"]

    print(f"\n===============================================================")
    print(f"  EXECUTION SUMMARY REPORT")
    print(f"===============================================================")
    print(f"  Total Documents Examined: {total_metrics['examined']}")
    print(f"  Total Documents Patched:  {total_metrics['patched']}")
    print(f"  Total Already Valid:      {total_metrics['already_valid']}")
    print(f"  Total Flagged for Review: {total_metrics['flagged_review']}")
    print(f"===============================================================")

if __name__ == "__main__":
    main()
