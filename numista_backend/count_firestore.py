"""
Firestore coin counter - Part B & C only
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import firebase_admin
from firebase_admin import credentials, firestore
from collections import defaultdict

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
combined_with_images = set()
combined_gcs = set()
combined_wiki = set()

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
            year = str(d.get('year', '')).strip()
            mint = str(d.get('mint_mark', '')).strip()
            ctype = str(d.get('coin_type', d.get('name', d.get('denomination', '')))).strip()
            key = f"{year}|{mint}|{ctype}"
            dedup_keys_with_img.add(key)
            combined_with_images.add(key)

            if 'storage.googleapis.com' in img:
                gcs_count += 1
                combined_gcs.add(key)
            elif 'wikimedia' in img.lower() or 'wikipedia' in img.lower():
                wiki_count += 1
                combined_wiki.add(key)
            else:
                # Other external URL - print sample to understand
                print(f"  OTHER URL for {label}: {img[:100]}")
                wiki_count += 1
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
    print(f"\n{label} ({email}):")
    print(f"  Total coin docs:           {total}")
    print(f"  Docs with image:           {has_image}")
    print(f"    From GCS (our bucket):   {gcs_count}")
    print(f"    From Wikimedia/ext:      {wiki_count}")
    print(f"  Docs without image:        {no_image}")

print()
eric_keys = user_stats.get('Eric', {}).get('unique_keys', set())
j_keys = user_stats.get('jseaman', {}).get('unique_keys', set())
overlap = eric_keys & j_keys
print(f"Combined unique coins with images (deduped): {len(combined_with_images)}")
print(f"Combined from GCS:                           {len(combined_gcs)}")
print(f"Combined from Wikimedia/external:            {len(combined_wiki)}")
print(f"Overlap (same coin in both accounts):        {len(overlap)}")

print()
print("Sample Eric coin keys:")
for k in sorted(list(eric_keys))[:15]:
    print(f"  {k}")

print()
print("Sample jseaman coin keys:")
for k in sorted(list(j_keys))[:15]:
    print(f"  {k}")
