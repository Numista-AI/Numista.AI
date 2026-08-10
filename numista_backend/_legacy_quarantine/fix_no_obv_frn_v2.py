"""
[QUARANTINED & DEPRECATED - DO NOT RUN IN PRODUCTION]
This script broadcasts a single representative $1 obverse image across multiple distinct note types.
It has been quarantined per Banknote Image SOP (August 2026) to prevent catalog misrepresentation.
Refer to SOPs/banknote_image_sop.md and docs/Currency_Image_Runbook.md for standard intake.

fix_no_obv_frn_v2.py
====================
Uploads the confirmed $1 FRN obverse to all NO_OBV docs.
Iterates by TYPE_MAP directly (avoids Firestore full-collection stream timeout).
"""
import os, sys, json, urllib.request, time, random
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore, storage

creds, _ = google.auth.default()
db  = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
gcs = storage.Client(credentials=creds)
bucket = gcs.bucket('numista-uploads-studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('currency')

GCS_BASE = 'users/jseaman1204@gmail.com/currency'
SOURCE   = 'wikimedia_commons_public_domain'
ATTR     = 'Public Domain. Source: Wikimedia Commons. US Federal Reserve Note representative image.'
HEADERS  = {'User-Agent': 'NumistaAI/1.0 (contact eric.seaman@yahoo.com)'}

# Confirmed working $1 FRN obverse
OBV_1_URL = 'https://upload.wikimedia.org/wikipedia/commons/7/7b/United_States_one_dollar_bill%2C_obverse.jpg'

# $20 1914 FRN — try direct confirmed URL from researcher
OBV_20_1914_CANDIDATES = [
    'https://upload.wikimedia.org/wikipedia/commons/4/4b/US-%2420-FRN-1914-Fr.960a.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/e/e0/US-%2420-FRN-1914-large-size.jpg',
]

with open('type_to_docids_map.json', encoding='utf-8') as f:
    TYPE_MAP = json.load(f)

# Types needing $1 FRN obverse
FRN_1_TYPES = [
    'TYPE_016','TYPE_017','TYPE_018','TYPE_019','TYPE_020',
    'TYPE_021','TYPE_022','TYPE_023','TYPE_024','TYPE_025',
    'TYPE_026','TYPE_027','TYPE_028','TYPE_029','TYPE_030',
    'TYPE_031','TYPE_032','TYPE_033','TYPE_034','TYPE_035',
    'TYPE_036','TYPE_037','TYPE_038',
    'TYPE_197','TYPE_198','TYPE_199','TYPE_200','TYPE_201',
    'TYPE_202','TYPE_203','TYPE_206',
]
TYPE_055_IDS = TYPE_MAP.get('TYPE_055', [])

def download(url):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt + random.random())
            else:
                return None

def upload_gcs(data, doc_id, side):
    path = f'{GCS_BASE}/{doc_id}/{side}.jpg'
    for attempt in range(4):
        try:
            bucket.blob(path).upload_from_string(data, content_type='image/jpeg')
            return f'https://storage.googleapis.com/{bucket.name}/{path}'
        except Exception as e:
            if attempt < 3:
                wait = 2 ** attempt + random.random()
                print(f'    GCS retry {attempt+1} ({e.__class__.__name__}) — {wait:.1f}s')
                time.sleep(wait)
            else:
                raise

# ── Download $1 FRN obverse ───────────────────────────────────────────────────
print('Downloading $1 FRN obverse...')
obv_1_data = download(OBV_1_URL)
if not obv_1_data:
    print('ERROR: could not download $1 FRN obverse'); sys.exit(1)
print(f'  {len(obv_1_data)//1024} KB ready\n')

# ── Download $20 1914 FRN obverse ─────────────────────────────────────────────
obv_20_data = None
for url in OBV_20_1914_CANDIDATES:
    data = download(url)
    if data and len(data) > 50000:   # real image, not error page
        obv_20_data = data
        print(f'$20 1914 FRN obverse: {len(data)//1024} KB from {url[:60]}')
        break
if not obv_20_data:
    print('$20 1914 FRN obverse: not found — will skip TYPE_055')

fixed = 0; skipped = 0

# ── Fix $1 FRN types ──────────────────────────────────────────────────────────
for type_id in FRN_1_TYPES:
    doc_ids = TYPE_MAP.get(type_id, [])
    for doc_id in doc_ids:
        data = col.document(doc_id).get().to_dict() or {}
        if data.get('image_url_obverse'):
            skipped += 1
            continue
        if not data.get('image_url_reverse'):
            # fully blank doc — not our target here, skip
            continue
        gcs_url = upload_gcs(obv_1_data, doc_id, 'obverse')
        col.document(doc_id).update({
            'image_url_obverse':    gcs_url,
            'image_source_obverse': SOURCE,
            'image_attribution':    ATTR,
        })
        fixed += 1
        print(f'  ✅ {type_id:12} {doc_id[:8]}')

# ── Fix TYPE_055 ($20 1914 FRN) ───────────────────────────────────────────────
if obv_20_data:
    for doc_id in TYPE_055_IDS:
        data = col.document(doc_id).get().to_dict() or {}
        if data.get('image_url_obverse'):
            skipped += 1
            continue
        gcs_url = upload_gcs(obv_20_data, doc_id, 'obverse')
        col.document(doc_id).update({
            'image_url_obverse':    gcs_url,
            'image_source_obverse': SOURCE,
            'image_attribution':    ATTR,
        })
        fixed += 1
        print(f'  ✅ TYPE_055      {doc_id[:8]} ($20 1914 FRN)')

print(f'\n✅ Fixed: {fixed} | Already had obverse: {skipped}')
