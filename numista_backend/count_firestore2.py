"""
Full Firestore coin counter with correct field names.
Fields: Year, Mint Mark, Program/Series, coin_id
"""
import sys, io
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

def get_dedup_key(d):
    """Build a deduplication key from the doc."""
    # Try coin_id first (most canonical)
    coin_id = str(d.get('coin_id', '')).strip()
    if coin_id:
        return coin_id
    # Fallback: Year + Mint Mark + Program/Series
    year = str(d.get('Year', '')).strip()
    mint = str(d.get('Mint Mark', '')).strip()
    series = str(d.get('Program/Series', '')).strip()
    return f"{year}|{mint}|{series}"

def classify_url(url):
    url = str(url).lower()
    if 'storage.googleapis.com' in url:
        # Distinguish our GCS bucket sub-paths
        if '/ai_generated' in url:
            return 'gcs_ai_generated'
        elif '/reference_library' in url or '/bulk_programs' in url:
            return 'gcs_reference'
        else:
            return 'gcs_user_upload'
    elif 'wikimedia' in url or 'wikipedia' in url:
        return 'wikimedia'
    elif url:
        return 'other_external'
    return 'none'

user_stats = {}
combined_with_images = set()
combined_no_image = set()
combined_gcs = set()        # any GCS URL
combined_gcs_ref = set()    # reference library specifically
combined_gcs_ai = set()     # AI-generated
combined_gcs_upload = set() # user-uploaded personal photos
combined_wiki = set()
combined_other_ext = set()

for email, label in USERS:
    docs = db.collection('users').document(email).collection('coins').stream()
    total = 0
    has_image = 0
    gcs_ref = 0
    gcs_ai = 0
    gcs_upload = 0
    wiki_count = 0
    ext_count = 0
    no_image = 0
    keys_with_img = set()
    keys_no_img = set()

    for doc in docs:
        total += 1
        d = doc.to_dict()
        img = d.get('image_url_obverse', '') or ''
        img = str(img).strip()
        key = get_dedup_key(d)

        if img:
            has_image += 1
            keys_with_img.add(key)
            combined_with_images.add(key)
            src = classify_url(img)
            if src == 'gcs_reference':
                gcs_ref += 1
                combined_gcs_ref.add(key)
                combined_gcs.add(key)
            elif src == 'gcs_ai_generated':
                gcs_ai += 1
                combined_gcs_ai.add(key)
                combined_gcs.add(key)
            elif src == 'gcs_user_upload':
                gcs_upload += 1
                combined_gcs_upload.add(key)
                combined_gcs.add(key)
            elif src == 'wikimedia':
                wiki_count += 1
                combined_wiki.add(key)
            else:
                ext_count += 1
                combined_other_ext.add(key)
        else:
            no_image += 1
            keys_no_img.add(key)
            combined_no_image.add(key)

    user_stats[label] = {
        'total': total,
        'has_image': has_image,
        'gcs_ref': gcs_ref,
        'gcs_ai': gcs_ai,
        'gcs_upload': gcs_upload,
        'wiki': wiki_count,
        'ext': ext_count,
        'no_image': no_image,
        'keys': keys_with_img,
    }

    total_gcs = gcs_ref + gcs_ai + gcs_upload
    print(f"\n{label} ({email}):")
    print(f"  Total coin docs:                 {total:>6,}")
    print(f"  With image (obverse):            {has_image:>6,}")
    print(f"    GCS (total):                   {total_gcs:>6,}")
    print(f"      - Reference library images:  {gcs_ref:>6,}")
    print(f"      - AI-generated images:       {gcs_ai:>6,}")
    print(f"      - User-uploaded photos:      {gcs_upload:>6,}")
    print(f"    Wikimedia/Wikipedia:           {wiki_count:>6,}")
    print(f"    Other external:                {ext_count:>6,}")
    print(f"  Without image:                   {no_image:>6,}")

print()
eric_keys = user_stats.get('Eric', {}).get('keys', set())
j_keys = user_stats.get('jseaman', {}).get('keys', set())
overlap = eric_keys & j_keys

print("=" * 55)
print("COMBINED (DEDUPLICATED ACROSS BOTH ACCOUNTS)")
print("=" * 55)
print(f"  Unique coins with image:             {len(combined_with_images):>6,}")
print(f"    From any GCS path:                 {len(combined_gcs):>6,}")
print(f"      - Reference library:             {len(combined_gcs_ref):>6,}")
print(f"      - AI-generated:                  {len(combined_gcs_ai):>6,}")
print(f"      - User-uploaded:                 {len(combined_gcs_upload):>6,}")
print(f"    From Wikimedia:                    {len(combined_wiki):>6,}")
print(f"    From other external:               {len(combined_other_ext):>6,}")
print(f"  Unique coins without image:          {len(combined_no_image):>6,}")
print(f"  Coins shared between both accounts:  {len(overlap):>6,}")

# Also count by series for jseaman (the big collection)
print()
print("=" * 55)
print("JSEAMAN - BREAKDOWN BY PROGRAM/SERIES (top 20)")
print("=" * 55)
docs2 = db.collection('users').document('jseaman1204@gmail.com').collection('coins').stream()
series_count = defaultdict(int)
for doc in docs2:
    d = doc.to_dict()
    img = d.get('image_url_obverse', '') or ''
    if str(img).strip():
        s = str(d.get('Program/Series', 'Unknown')).strip()
        series_count[s] += 1
for series, cnt in sorted(series_count.items(), key=lambda x: -x[1])[:20]:
    print(f"  {series:<45} {cnt:>5,}")
