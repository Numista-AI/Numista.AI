#!/usr/bin/env python3
"""
audit_all_buckets.py
--------------------
Audits each of the specific Google Cloud Storage buckets listed by the user,
counting total blobs in each to establish the exact physical starting point.
"""

import os
import sys
from pathlib import Path
from google.cloud import storage as gcs

# Ensure output encoding is UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Configuration
PROJECT_ID = "studio-9101802118-8c9a8"
KEY_PATH = Path(__file__).parent / "serviceAccountKey.json.json"

# List of buckets provided by the user
BUCKET_LIST = [
    "568985927038-us-central1-blueprint-config",
    "numista-reference-library",
    "numista-uploads-studio-9101802118-8c9a8",
    "studio-9101802118-8c9a8-uploads",
    "studio-9101802118-8c9a8.firebasestorage.app",
    "us_mint_coin_images"
]

def main():
    print("="*60)
    print("  Numista.AI - Multi-Bucket Google Cloud Storage Audit")
    print("="*60)

    # Initialize GCS Client
    try:
        if KEY_PATH.exists():
            gcs_client = gcs.Client.from_service_account_json(str(KEY_PATH), project=PROJECT_ID)
            print(f"Loaded credentials from {KEY_PATH.name}")
        else:
            gcs_client = gcs.Client(project=PROJECT_ID)
            print("Using default application credentials (ADC)")
    except Exception as e:
        print(f"Error initializing GCS client: {e}")
        sys.exit(1)

    checked_buckets = {}
    
    for b_name in BUCKET_LIST:
        print(f"\nAuditing bucket: gs://{b_name} ...")
        try:
            bucket = gcs_client.bucket(b_name)
            # Try to list blobs (without prefix limits) to get total count
            blobs = list(gcs_client.list_blobs(bucket))
            file_count = len(blobs)
            print(f"  ✓ ACCESSIBLE: Found {file_count} total file(s) in gs://{b_name}")
            
            # Print breakdown of top-level prefixes/extensions if any
            if file_count > 0:
                extensions = {}
                folders = set()
                for b in blobs[:1000]: # check first 1000 for summary
                    ext = Path(b.name).suffix.lower()
                    extensions[ext] = extensions.get(ext, 0) + 1
                    parts = b.name.split('/')
                    if len(parts) > 1:
                        folders.add(parts[0])
                print(f"    * Top folders present: {list(folders)[:5]}")
                print(f"    * Sample extensions: {dict(list(extensions.items())[:5])}")
                
            checked_buckets[b_name] = {
                "accessible": True,
                "count": file_count,
                "error": None
            }
        except Exception as e:
            print(f"  ✗ INACCESSIBLE: Error listing gs://{b_name} ({e})")
            checked_buckets[b_name] = {
                "accessible": False,
                "count": 0,
                "error": str(e)
            }

    print("\n" + "="*60)
    print("  Audit Summary Report")
    print("="*60)
    total_images = 0
    for b_name, info in checked_buckets.items():
        status = "✓ Checked" if info["accessible"] else "✗ Failed"
        count = info["count"]
        total_images += count
        err_msg = f" | Error: {info['error']}" if info["error"] else ""
        print(f"  - gs://{b_name:<45} | {status} | Count: {count}{err_msg}")
        
    print(f"\n  Total Combined Images Checked: {total_images}")
    print("="*60)

if __name__ == "__main__":
    main()
