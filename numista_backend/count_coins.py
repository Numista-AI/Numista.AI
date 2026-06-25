"""
Coin Image Inventory Counter
Counts unique coins with images across GCS reference library and Firestore user collections.
"""

import csv
import os
import re
from collections import defaultdict
import json

# ─────────────────────────────────────────────────
# PART A: GCS REFERENCE LIBRARY
# ─────────────────────────────────────────────────

CSV_PATH = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\gcs_full_inventory.csv"

# Tokens to strip from filename ends (obverse/reverse/finish markers)
STRIP_TOKENS = {
    'obverse', 'reverse', 'front', 'back',
    'uncirculated', 'proof', 'unc', 'obv', 'rev',
    'bu', 'ms', 'pf',  # grading abbreviations sometimes used
}

def normalize_stem(stem: str) -> str:
    """
    Strip trailing orientation/finish tokens from a filename stem.
    Works for both hyphen-separated and underscore-separated filenames.
    """
    # Normalize separators to hyphens for splitting
    normalized = stem.lower().replace('_', '-')
    parts = normalized.split('-')
    # Strip from the right any tokens that are in STRIP_TOKENS
    while parts and parts[-1] in STRIP_TOKENS:
        parts.pop()
    return '-'.join(parts)


def map_category(path: str, category: str, coin_type: str) -> str:
    """Map a path to a human-readable category label."""
    p = path.lower()
    if 'atb_quarters' in p or 'atb-quarters' in p or 'america-the-beautiful' in p:
        return 'ATB Quarters'
    if 'presidential' in p:
        return 'Presidential $1'
    if 'morgan' in p:
        return 'Morgan Dollars'
    if 'peace' in p and 'dollar' in p:
        return 'Peace Dollars'
    if 'silver_eagle' in p or 'silver-eagle' in p:
        return 'Silver Eagles'
    if 'sba' in p or 'susan-b' in p or 'susan_b' in p:
        return 'SBA Dollars'
    if 'sacagawea' in p or 'native_american' in p or 'native-american' in p:
        return 'Sacagawea/Native American $1'
    if 'kennedy' in p:
        return 'Kennedy Half Dollars'
    if 'state_quarter' in p or 'state-quarter' in p or '50_states' in p:
        return '50 State Quarters'
    if 'innovation' in p or 'american_innovation' in p:
        return 'American Innovation $1'
    if 'clad_proof' in p or 'annual_proof' in p or 'proof_set' in p:
        return 'Proof Sets'
    if 'mint_set' in p or 'annual_uncirculated' in p:
        return 'Mint Sets'
    if 'reference_library' in p:
        return f'Reference Library (other) [{coin_type}]'
    if 'bulk_programs' in p:
        return f'Bulk Programs (other) [{coin_type}]'
    return f'Other [{category}]'


print("=" * 65)
print("PART A: GCS REFERENCE LIBRARY — UNIQUE COIN COUNT")
print("=" * 65)

# We only count reference/bulk paths (not user uploads, ai_generated, etc.)
REFERENCE_PREFIXES = ('reference_library/', 'bulk_programs/')

category_coins = defaultdict(set)  # category -> set of coin_keys
all_gcs_keys = set()

total_rows = 0
ref_rows = 0

with open(CSV_PATH, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        total_rows += 1
        path = row['path']
        category = row.get('category', '')
        coin_type = row.get('coin_type', '')

        # Only process reference/bulk library paths
        if not any(path.startswith(pfx) for pfx in REFERENCE_PREFIXES):
            continue
        ref_rows += 1

        # Get filename stem
        filename = os.path.basename(path)
        stem, _ = os.path.splitext(filename)

        # Normalize and strip orientation/finish tokens
        coin_key = normalize_stem(stem)

        if not coin_key:
            continue

        cat_label = map_category(path, category, coin_type)
        category_coins[cat_label].add(coin_key)
        all_gcs_keys.add(coin_key)

print(f"\nTotal CSV rows: {total_rows:,}")
print(f"Reference/bulk library rows: {ref_rows:,}")
print()

# Print by category
sorted_cats = sorted(category_coins.keys(), key=lambda c: -len(category_coins[c]))
print(f"{'Category':<45} {'Unique Coins':>12}")
print("-" * 60)
for cat in sorted_cats:
    print(f"{cat:<45} {len(category_coins[cat]):>12,}")
print("-" * 60)
print(f"{'TOTAL unique coins in GCS reference library':<45} {len(all_gcs_keys):>12,}")

# Sample some coin keys for verification
print("\nSample coin keys (first 10 from ATB Quarters):")
atb = category_coins.get('ATB Quarters', set())
for k in sorted(list(atb))[:10]:
    print(f"  {k}")

print("\nSample coin keys (first 10 from Presidential $1):")
pres = category_coins.get('Presidential $1', set())
for k in sorted(list(pres))[:10]:
    print(f"  {k}")


# ─────────────────────────────────────────────────
# PART B & C: FIRESTORE USER COLLECTIONS
# ─────────────────────────────────────────────────

print()
print("=" * 65)
print("PART B & C: FIRESTORE USER COLLECTIONS")
print("=" * 65)

try:
    import firebase_admin
    from firebase_admin import credentials, firestore

    CRED_PATH = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json.json"
    PROJECT_ID = "studio-9101802118-8c9a8"

    cred = credentials.Certificate(CRED_PATH)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {'projectId': PROJECT_ID})
    db = firestore.client()

    USERS = [
        ("eric@numista.ai", "Eric"),
        ("jseaman1204@gmail.com", "jseaman"),
    ]

    user_stats = {}
    combined_with_images = set()   # dedup key set
    combined_gcs = set()
    combined_wiki = set()
    combined_no_img = 0

    for email, label in USERS:
        docs = db.collection('users').document(email).collection('coins').stream()
        total = 0
        has_image = 0
        gcs_count = 0
        wiki_count = 0
        no_image = 0
        dedup_keys_with_img = set()

        for doc in docs:
            total += 1
            d = doc.to_dict()
            img = d.get('image_url_obverse', '') or ''
            img = str(img).strip()

            if img:
                has_image += 1
                # Build dedup key
                year = str(d.get('year', '')).strip()
                mint = str(d.get('mint_mark', '')).strip()
                ctype = str(d.get('coin_type', d.get('name', d.get('denomination', '')))).strip()
                key = f"{year}|{mint}|{ctype}"
                dedup_keys_with_img.add(key)
                combined_with_images.add(key)

                # Image source
                if 'storage.googleapis.com' in img:
                    gcs_count += 1
                    combined_gcs.add(key)
                elif 'wikimedia' in img.lower() or 'wikipedia' in img.lower():
                    wiki_count += 1
                    combined_wiki.add(key)
                else:
                    # Some other external source
                    wiki_count += 1  # count as external
                    combined_wiki.add(key)
            else:
                no_image += 1

        user_stats[label] = {
            'total': total,
            'has_image': has_image,
            'gcs': gcs_count,
            'wiki': wiki_count,
            'no_image': no_image,
            'unique_keys': dedup_keys_with_img,
        }
        print(f"\n  {label} ({email}):")
        print(f"    Total coin docs:         {total:>6,}")
        print(f"    Docs with image:         {has_image:>6,}")
        print(f"    → From GCS (our bucket): {gcs_count:>6,}")
        print(f"    → From Wikimedia/ext:    {wiki_count:>6,}")
        print(f"    Docs without image:      {no_image:>6,}")

    print()
    print(f"  Combined unique coins with images (deduplicated): {len(combined_with_images):,}")
    print(f"  Combined → from GCS:         {len(combined_gcs):,}")
    print(f"  Combined → from Wikimedia:   {len(combined_wiki):,}")

    # Overlap between users
    eric_keys = user_stats.get('Eric', {}).get('unique_keys', set())
    j_keys = user_stats.get('jseaman', {}).get('unique_keys', set())
    overlap = eric_keys & j_keys
    print(f"\n  Coins in both collections (overlap): {len(overlap):,}")

    firestore_ok = True

except Exception as e:
    print(f"\n  ERROR connecting to Firestore: {e}")
    firestore_ok = False
    combined_with_images = set()
    combined_gcs = set()
    combined_wiki = set()


# ─────────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────────

print()
print("=" * 65)
print("FINAL SUMMARY")
print("=" * 65)
print()
print(f"  GCS reference library unique coins:          {len(all_gcs_keys):>6,}")
if firestore_ok:
    print(f"  Firestore unique coins with images:          {len(combined_with_images):>6,}")
    print(f"    → Sourced from our GCS bucket:             {len(combined_gcs):>6,}")
    print(f"    → Sourced from Wikimedia/external:         {len(combined_wiki):>6,}")
    # Grand total: GCS library + Firestore coins NOT already in GCS library
    # (we can't perfectly cross-ref because keys differ, but give totals)
    print()
    print(f"  Grand total unique coin types with images:")
    print(f"    GCS library:                               {len(all_gcs_keys):>6,}")
    print(f"    Firestore user coins (with images):        {len(combined_with_images):>6,}")
    print()
    print("  (Note: GCS library and Firestore coins may partially overlap.")
    print("   The GCS library represents the reference image store;")
    print("   Firestore represents coins actively in user collections.)")
print()
print("Done.")
