#!/usr/bin/env python3
"""Fix C: Clean poisoned image URLs from grokbot coin docs.

assign_coin_images.py stamped wrong reverse URLs (e.g., Fort McHenry on all
2013 ATB quarters, Maya Angelou on all 2022 AWQ) because it ignored Theme/Subject.

This script wipes image_url_obverse, image_url_reverse, image_source, and
image_updated_at on affected docs so the client-side CoinImageService (now
fixed) resolves correct images via coin_image_index.

Usage:
  python fix_grokbot_images.py                 # dry-run (default)
  python fix_grokbot_images.py --write         # actually write to Firestore
"""

import argparse
import os
import firebase_admin
from firebase_admin import credentials, firestore

TARGET_EMAIL = "grokbot@numista.ai"
SA_KEY_PATH = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json"
PROJECT_ID = "studio-9101802118-8c9a8"

# Fields to wipe
POISON_FIELDS = [
    "image_url_obverse",
    "image_url_reverse",
    "image_source",
    "image_updated_at",
]

def main():
    parser = argparse.ArgumentParser(description="Clean poisoned image URLs from grokbot coins")
    parser.add_argument("--write", action="store_true", help="Actually write to Firestore")
    args = parser.parse_args()

    if not firebase_admin._apps:
        cred = credentials.Certificate(SA_KEY_PATH)
        firebase_admin.initialize_app(cred, {"projectId": PROJECT_ID})

    db = firestore.client()
    coins_ref = db.collection("users").document(TARGET_EMAIL).collection("coins")

    docs = list(coins_ref.stream())
    print(f"Total grokbot coins: {len(docs)}", flush=True)

    to_clean = []
    already_clean = 0
    for doc in docs:
        data = doc.to_dict()
        has_poison = False
        # Check if doc has image URLs that were stamped by assign_coin_images
        img_source = data.get("image_source", "")
        img_rev = data.get("image_url_reverse", "")
        img_obv = data.get("image_url_obverse", "")

        if img_source == "gcs_reference" or img_rev or img_obv:
            has_poison = True

        if has_poison:
            theme = data.get("Theme/Subject", data.get("theme_subject", ""))
            denom = data.get("Denomination", data.get("denomination", ""))
            year = data.get("Year", data.get("year", ""))
            to_clean.append({
                "id": doc.id,
                "year": year,
                "denom": denom,
                "theme": theme,
                "rev_url": img_rev[:60] if img_rev else "",
                "source": img_source,
            })
        else:
            already_clean += 1

    print(f"\nDocs to clean: {len(to_clean)}", flush=True)
    print(f"Already clean: {already_clean}", flush=True)

    if to_clean:
        print("\n--- Sample of docs to clean ---", flush=True)
        for c in to_clean[:10]:
            print(f"  {c['year']} {c['denom']} ({c['theme'][:40]}) rev={c['rev_url']}", flush=True)
        if len(to_clean) > 10:
            print(f"  ... and {len(to_clean) - 10} more", flush=True)

    if args.write:
        print(f"\n--- WRITING: clearing {len(to_clean)} docs ---", flush=True)
        cleared = 0
        for c in to_clean:
            update = {field: firestore.DELETE_FIELD for field in POISON_FIELDS}
            coins_ref.document(c["id"]).update(update)
            cleared += 1
            if cleared % 50 == 0:
                print(f"  cleared {cleared}/{len(to_clean)}", flush=True)
        print(f"\nDONE: cleared {cleared} docs", flush=True)
    else:
        print(f"\n--- DRY RUN --- would clear {len(to_clean)} docs. Use --write to execute.", flush=True)

if __name__ == "__main__":
    main()
