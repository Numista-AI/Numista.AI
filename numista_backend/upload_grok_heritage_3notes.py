"""
upload_grok_heritage_3notes.py
Uploads the 6 Heritage Auctions images from Grok's manual download.
Overwrites obverses (superior quality) and fills in missing reverses.
"""
import os, sys, json
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore, storage

creds, _ = google.auth.default()
db  = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
gcs = storage.Client(credentials=creds)
bucket = gcs.bucket('numista-uploads-studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('currency')

DROP = r'C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\Coin Images\Coins Images to Find\Downloads from Grok'
GCS_BASE = 'users/jseaman1204@gmail.com/currency'
SOURCE   = 'heritage_auctions_professional'
ATTR     = 'Professional auction photography. Source: Heritage Auctions, HA.com. Used for educational numismatic reference.'

with open('type_to_docids_map.json', encoding='utf-8') as f:
    TYPE_MAP = json.load(f)

IMAGES = [
    # (type_id, side, filename, description)
    ('TYPE_005', 'obverse', r'1918, Federal Reserve Bank Note Large size PMG, TYPE_005_OBVERSE.JPG',
     '$1 1918 FRBN Boston PMG 64 EPQ — Heritage Auctions'),
    ('TYPE_005', 'reverse', r'1918, Federal Reserve Bank Note Large size PMG, TYPE_005_REVERSE.jpg',
     '$1 1918 FRBN Boston PMG 64 EPQ reverse — Heritage Auctions'),
    ('TYPE_007', 'obverse', r'1929 Heritage Auctions $10 Federal Reserve Bank Note Obverse.jpg',
     '$10 1929 FRBN St. Louis PCGS 67 PPQ — Heritage Auctions'),
    ('TYPE_007', 'reverse', r'1929 Heritage Auctions $10 Federal Reserve Bank Note Reverse.jpg',
     '$10 1929 FRBN St. Louis PCGS 67 PPQ reverse — Heritage Auctions'),
    ('TYPE_008', 'obverse', r'1918, $2 Federal Reserve Bank Note Large size Obverse.jpg',
     '$2 1918 FRBN Cleveland PMG 66 EPQ (Battleship Note) — Heritage Auctions'),
    ('TYPE_008', 'reverse', r'1918, $2 Federal Reserve Bank Note Large size Reverse.jpg',
     '$2 1918 FRBN Cleveland PMG 66 EPQ (Battleship Note) reverse — Heritage Auctions'),
]

# Build upload plan keyed by doc_id
upload_plan = {}   # doc_id -> {side -> (path, desc)}
for type_id, side, filename, desc in IMAGES:
    doc_ids = TYPE_MAP.get(type_id, [])
    path = os.path.join(DROP, filename)
    if not os.path.exists(path):
        print(f'WARNING: file not found: {filename}')
        continue
    for doc_id in doc_ids:
        upload_plan.setdefault(doc_id, {})[side] = (path, desc)

print(f'Uploading to {len(upload_plan)} docs...\n')
total = 0
for doc_id, sides in upload_plan.items():
    updates = {}
    for side, (path, desc) in sides.items():
        with open(path, 'rb') as f:
            data = f.read()
        ext  = 'png' if path.lower().endswith('.png') else 'jpg'
        ct   = 'image/png' if ext == 'png' else 'image/jpeg'
        gcs_path = f'{GCS_BASE}/{doc_id}/{side}.jpg'
        blob = bucket.blob(gcs_path)
        blob.upload_from_string(data, content_type=ct)
        gcs_url = f'https://storage.googleapis.com/{bucket.name}/{gcs_path}'
        updates[f'image_url_{side}'] = gcs_url
        updates[f'image_source_{side}'] = SOURCE
        updates['image_attribution'] = ATTR
        total += 1
        print(f'  {doc_id[:8]}  {side:8}  {desc[:60]}')

    col.document(doc_id).update(updates)

print(f'\n✅ Done — {total} images uploaded across {len(upload_plan)} docs.')
