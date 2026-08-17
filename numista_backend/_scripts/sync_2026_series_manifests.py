#!/usr/bin/env python3
"""
sync_2026_series_manifests.py
─────────────────────────────────────────────────────────────────────────────
Refreshes all indexes, manifests, and caches referencing
gs://numista-reference-library/reference_library/2026_series/

Updates:
1. numista_backend/gcs_full_inventory.csv (All 25 official stills with size/URL)
2. Firestore collection 'coin_image_index' (Canonical documents & side maps)
3. numista_backend/_scripts/image_index_full.csv
"""

import os
import csv
import sys
from datetime import datetime, timezone
from google.cloud import storage, firestore
from google.oauth2 import service_account

# Force UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ID = "studio-9101802118-8c9a8"
BUCKET_NAME = "numista-reference-library"
PREFIX = "reference_library/2026_series/"

# Locate credentials
cred_candidates = [
    os.path.join(BACKEND_DIR, "serviceAccountKey.json"),
    os.path.join(BACKEND_DIR, "serviceAccountKey.json.json"),
]
cred_path = next((p for p in cred_candidates if os.path.exists(p)), None)
if not cred_path:
    raise FileNotFoundError("Service account key not found.")

creds = service_account.Credentials.from_service_account_file(
    cred_path,
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

storage_client = storage.Client(project=PROJECT_ID, credentials=creds)
db = firestore.Client(project=PROJECT_ID, credentials=creds)

print("=" * 75)
print("  NUMISTA.AI — 2026 SERIES INDEX & MANIFEST REFRESH")
print("=" * 75)

# ── 1. Fetch all blobs in 2026_series/ ──────────────────────────────────────────
bucket = storage_client.bucket(BUCKET_NAME)
blobs = list(bucket.list_blobs(prefix=PREFIX))
print(f"\n[1/3] Found {len(blobs)} blobs in gs://{BUCKET_NAME}/{PREFIX}")

if len(blobs) != 25:
    print(f"  [WARN] Expected 25 blobs, found {len(blobs)}")
else:
    print("  ✓ Confirmed full 25-still canonical series present in GCS.")

# ── 2. Update gcs_full_inventory.csv ───────────────────────────────────────────
inv_csv = os.path.join(BACKEND_DIR, "gcs_full_inventory.csv")
print(f"\n[2/3] Updating inventory CSV: {inv_csv}")

existing_rows = []
if os.path.exists(inv_csv):
    with open(inv_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            # Skip old 2026_series rows to replace them cleanly
            if PREFIX not in row.get("path", ""):
                existing_rows.append(row)

new_2026_rows = []
now_iso = datetime.now(timezone.utc).isoformat()

for blob in sorted(blobs, key=lambda b: b.name):
    fname = blob.name.split("/")[-1]
    pub_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{blob.name}"
    row = {
        "bucket": BUCKET_NAME,
        "path": blob.name,
        "size_bytes": blob.size or 0,
        "public_url": pub_url,
        "category": "Reference Library",
        "coin_type": "reference",
    }
    new_2026_rows.append(row)

combined_rows = existing_rows + new_2026_rows
with open(inv_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["bucket", "path", "size_bytes", "public_url", "category", "coin_type"])
    writer.writeheader()
    writer.writerows(combined_rows)

print(f"  ✓ Updated {inv_csv} with {len(new_2026_rows)} 2026 series rows (Total: {len(combined_rows):,} rows)")

# ── 3. Map & Sync to Firestore coin_image_index ───────────────────────────────
print(f"\n[3/3] Syncing 2026 stills to Firestore 'coin_image_index'...")

# Definition of the 25 files and their canonical mappings
INDEX_ENTRIES = [
    # 1. 2026 Lincoln Cent
    {
        "keys": ["2026_cent_obverse", "2026_lincoln-cent_obverse", "2026_america250_cent_obverse"],
        "filename": "2026_cent_collector-only_1776~2026_obverse.jpg",
        "side": "obverse", "year": "2026", "program": "lincoln-cent", "subject": "1776~2026 Collector Cent",
    },
    {
        "keys": ["2026_cent_reverse", "2026_lincoln-cent_reverse", "2026_america250_cent_reverse"],
        "filename": "2026_cent_collector-only_1776~2026_reverse.jpg",
        "side": "reverse", "year": "2026", "program": "lincoln-cent", "subject": "1776~2026 Collector Cent",
    },
    # 2. 2026 Jefferson Nickel
    {
        "keys": ["2026_nickel_obverse", "2026_jefferson-nickel_obverse", "2026_america250_nickel_obverse"],
        "filename": "2026_five_cents_1776~2026_dual_date_obverse.jpg",
        "side": "obverse", "year": "2026", "program": "jefferson-nickel", "subject": "1776~2026 Dual Date Jefferson",
    },
    {
        "keys": ["2026_nickel_reverse", "2026_jefferson-nickel_reverse", "2026_america250_nickel_reverse"],
        "filename": "2026_five_cents_1776~2026_dual_date_reverse.jpg",
        "side": "reverse", "year": "2026", "program": "jefferson-nickel", "subject": "1776~2026 Dual Date Jefferson",
    },
    # 3. Emerging Liberty Dime
    {
        "keys": ["2026_dime_obverse", "2026_emerging-liberty_dime_obverse", "2026_america250_dime_obverse"],
        "filename": "2026_dime_emerging_liberty_obverse.jpg",
        "side": "obverse", "year": "2026", "program": "dime", "subject": "Emerging Liberty",
    },
    {
        "keys": ["2026_dime_reverse", "2026_emerging-liberty_dime_reverse", "2026_america250_dime_reverse"],
        "filename": "2026_dime_emerging_liberty_reverse.jpg",
        "side": "reverse", "year": "2026", "program": "dime", "subject": "Emerging Liberty",
    },
    # 4. Mayflower Compact Quarter
    {
        "keys": ["2026_quarter_mayflower_obverse", "2026_mayflower-compact_quarter_obverse", "2026_mayflower_quarter_obverse"],
        "filename": "2026_quarter_dollar_mayflower_compact_obverse.jpg",
        "side": "obverse", "year": "2026", "program": "america250-quarters", "subject": "Mayflower Compact",
    },
    {
        "keys": ["2026_quarter_mayflower_reverse", "2026_mayflower-compact_quarter_reverse", "2026_mayflower_quarter_reverse"],
        "filename": "2026_quarter_dollar_mayflower_compact_reverse.jpg",
        "side": "reverse", "year": "2026", "program": "america250-quarters", "subject": "Mayflower Compact",
    },
    # 5. Revolutionary War Quarter
    {
        "keys": ["2026_quarter_valleyforge_obverse", "2026_revolutionary-war_quarter_obverse", "2026_valleyforge_quarter_obverse"],
        "filename": "2026_quarter_dollar_revolutionary_war_obverse.jpg",
        "side": "obverse", "year": "2026", "program": "america250-quarters", "subject": "Revolutionary War",
    },
    {
        "keys": ["2026_quarter_valleyforge_reverse", "2026_revolutionary-war_quarter_reverse", "2026_valleyforge_quarter_reverse"],
        "filename": "2026_quarter_dollar_revolutionary_war_reverse.jpg",
        "side": "reverse", "year": "2026", "program": "america250-quarters", "subject": "Revolutionary War",
    },
    # 6. Declaration of Independence Quarter
    {
        "keys": ["2026_quarter_declaration_obverse", "2026_declaration-of-independence_quarter_obverse", "2026_declaration_quarter_obverse"],
        "filename": "2026_quarter_dollar_declaration_of_independence_obverse.jpg",
        "side": "obverse", "year": "2026", "program": "america250-quarters", "subject": "Declaration of Independence",
    },
    {
        "keys": ["2026_quarter_declaration_reverse", "2026_declaration-of-independence_quarter_reverse", "2026_declaration_quarter_reverse"],
        "filename": "2026_quarter_dollar_declaration_of_independence_reverse.jpg",
        "side": "reverse", "year": "2026", "program": "america250-quarters", "subject": "Declaration of Independence",
    },
    # 7. U.S. Constitution Quarter
    {
        "keys": ["2026_quarter_constitution_obverse", "2026_us-constitution_quarter_obverse", "2026_constitution_quarter_obverse"],
        "filename": "2026_quarter_dollar_us_constitution_obverse.jpg",
        "side": "obverse", "year": "2026", "program": "america250-quarters", "subject": "U.S. Constitution",
    },
    {
        "keys": ["2026_quarter_constitution_reverse", "2026_us-constitution_quarter_reverse", "2026_constitution_quarter_reverse"],
        "filename": "2026_quarter_dollar_us_constitution_reverse.jpg",
        "side": "reverse", "year": "2026", "program": "america250-quarters", "subject": "U.S. Constitution",
    },
    # 8. Gettysburg Address Quarter
    {
        "keys": ["2026_quarter_gettysburg_obverse", "2026_gettysburg-address_quarter_obverse", "2026_gettysburg_quarter_obverse"],
        "filename": "2026_quarter_dollar_gettysburg_address_obverse.jpg",
        "side": "obverse", "year": "2026", "program": "america250-quarters", "subject": "Gettysburg Address",
    },
    {
        "keys": ["2026_quarter_gettysburg_reverse", "2026_gettysburg-address_quarter_reverse", "2026_gettysburg_quarter_reverse"],
        "filename": "2026_quarter_dollar_gettysburg_address_reverse.jpg",
        "side": "reverse", "year": "2026", "program": "america250-quarters", "subject": "Gettysburg Address",
    },
    # 9. Enduring Liberty Half Dollar
    {
        "keys": ["2026_half_dollar_obverse", "2026_enduring-liberty_half-dollar_obverse", "2026_half-dollar_obverse", "2026_kennedy-half-dollar_obverse"],
        "filename": "2026_half_dollar_enduring_liberty_obverse.jpg",
        "side": "obverse", "year": "2026", "program": "kennedy-half-dollar", "subject": "Enduring Liberty",
    },
    {
        "keys": ["2026_half_dollar_reverse", "2026_enduring-liberty_half-dollar_reverse", "2026_half-dollar_reverse", "2026_kennedy-half-dollar_reverse"],
        "filename": "2026_half_dollar_enduring_liberty_reverse.jpg",
        "side": "reverse", "year": "2026", "program": "kennedy-half-dollar", "subject": "Enduring Liberty",
    },
    # 10. Native American $1 (Polly Cooper)
    {
        "keys": ["2026_polly-cooper_native-american-dollar_obverse", "2026_native-american-dollar_obverse", "2026_sacagawea_dollar_obverse"],
        "filename": "2026_native_american_dollar_polly_cooper_obverse.jpg",
        "side": "obverse", "year": "2026", "program": "native-american-dollar", "subject": "Polly Cooper",
    },
    {
        "keys": ["2026_polly-cooper_native-american-dollar_reverse", "2026_native-american-dollar_reverse", "2026_sacagawea_dollar_reverse"],
        "filename": "2026_native_american_dollar_polly_cooper_reverse.jpg",
        "side": "reverse", "year": "2026", "program": "native-american-dollar", "subject": "Polly Cooper",
    },
    # 11. American Innovation $1 (Shared Obverse)
    {
        "keys": ["2026_american-innovation_obverse", "2026_innovation-dollar_obverse"],
        "filename": "2026_american_innovation_obverse.jpg",
        "side": "obverse", "year": "2026", "program": "american-innovation", "subject": "Statue of Liberty 250 Privy",
    },
    # 12. American Innovation $1 Reverses (Iowa, Wisconsin, California, Minnesota)
    {
        "keys": ["2026_iowa_american-innovation_reverse", "2026_innovation-iowa_reverse"],
        "filename": "2026_american_innovation_iowa_reverse.jpg",
        "side": "reverse", "year": "2026", "program": "american-innovation", "subject": "iowa",
    },
    {
        "keys": ["2026_wisconsin_american-innovation_reverse", "2026_innovation-wisconsin_reverse"],
        "filename": "2026_american_innovation_wisconsin_reverse.jpg",
        "side": "reverse", "year": "2026", "program": "american-innovation", "subject": "wisconsin",
    },
    {
        "keys": ["2026_california_american-innovation_reverse", "2026_innovation-california_reverse"],
        "filename": "2026_american_innovation_california_reverse.jpg",
        "side": "reverse", "year": "2026", "program": "american-innovation", "subject": "california",
    },
    {
        "keys": ["2026_minnesota_american-innovation_reverse", "2026_innovation-minnesota_reverse"],
        "filename": "2026_american_innovation_minnesota_reverse.jpg",
        "side": "reverse", "year": "2026", "program": "american-innovation", "subject": "minnesota",
    },
]

batch = db.batch()
batch_count = 0
total_indexed_keys = 0

for entry in INDEX_ENTRIES:
    fname = entry["filename"]
    gcs_path = f"gs://{BUCKET_NAME}/{PREFIX}{fname}"
    pub_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{PREFIX}{fname}"
    side = entry["side"]

    doc_data = {
        side: {
            "gcs_path": gcs_path,
            "public_url": pub_url,
            "source_tier": 1,
            "source_label": "US Mint Official Photography",
            "attribution": "United States Mint (Public Domain, 17 U.S.C. § 105)",
            "indexed_at": now_iso,
        },
        "year": entry["year"],
        "program": entry["program"],
        "subject": entry.get("subject"),
    }

    for key in entry["keys"]:
        doc_ref = db.collection("coin_image_index").document(key)
        batch.set(doc_ref, doc_data, merge=True)
        batch_count += 1
        total_indexed_keys += 1

        if batch_count >= 400:
            batch.commit()
            batch = db.batch()
            batch_count = 0

if batch_count > 0:
    batch.commit()

print(f"  ✓ Indexed {len(INDEX_ENTRIES)} still definitions across {total_indexed_keys} Firestore keys in 'coin_image_index'.")

# ── 4. Re-export _scripts/image_index_full.csv ─────────────────────────────────
print(f"\n[4/4] Updating _scripts/image_index_full.csv...")
all_index_docs = list(db.collection("coin_image_index").stream())
index_rows = []
for doc in all_index_docs:
    d = doc.to_dict()
    key = doc.id
    for side in ("obverse", "reverse"):
        if side in d and isinstance(d[side], dict):
            sdata = d[side]
            index_rows.append({
                "doc_key": key,
                "year": d.get("year", ""),
                "mint": d.get("mint", ""),
                "program": d.get("program", ""),
                "subject": d.get("subject", ""),
                "side": side,
                "public_url": sdata.get("public_url", ""),
                "attribution": sdata.get("attribution", ""),
                "source_tier": sdata.get("source_tier", ""),
                "source_label": sdata.get("source_label", ""),
            })

img_idx_csv = os.path.join(SCRIPT_DIR, "image_index_full.csv")
with open(img_idx_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "doc_key", "year", "mint", "program", "subject", "side", "public_url", "attribution", "source_tier", "source_label"
    ])
    writer.writeheader()
    writer.writerows(index_rows)

print(f"  ✓ Exported {len(index_rows):,} rows into {img_idx_csv}")

print("\n" + "=" * 75)
print("  🎉 2026 CANONICAL SERIES REFRESH COMPLETED SUCCESSFULLY (EXIT 0)")
print("=" * 75)
