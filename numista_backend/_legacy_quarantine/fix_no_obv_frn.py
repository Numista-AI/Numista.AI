"""
[QUARANTINED & DEPRECATED - DO NOT RUN IN PRODUCTION]
This script broadcasts a single representative $1 obverse image across multiple distinct note types.
It has been quarantined per Banknote Image SOP (August 2026) to prevent catalog misrepresentation.
Refer to SOPs/banknote_image_sop.md and docs/Currency_Image_Runbook.md for standard intake.

fix_no_obv_frn.py
=================
Uploads the confirmed $1 FRN obverse to all NO_OBV docs in TYPE_016-038 and TYPE_197-206.
Also tries additional Wikimedia patterns for the $20 1914 FRN (TYPE_055).
"""
import os, sys, json, urllib.request, urllib.parse, time, random
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
ATTR     = 'Public Domain. Source: Wikimedia Commons. US Federal Reserve Note.'
HEADERS  = {'User-Agent': 'NumistaAI/1.0 (contact eric.seaman@yahoo.com)'}

# Confirmed working URL for $1 FRN obverse
OBV_1_FRN_URL = 'https://upload.wikimedia.org/wikipedia/commons/7/7b/United_States_one_dollar_bill%2C_obverse.jpg'

# Additional candidates for $20 1914 FRN obverse
CANDIDATES_20_1914 = [
    'US-$20-FRN-1914.jpg',
    'Federal Reserve Note 1914 obverse.jpg',
    'US $20 1914 Federal Reserve Note.jpg',
    '20 dollar bill 1914.jpg',
    'US-$20-FRN-1914-Fr.960.jpg',
    'US-$20-FRN-Fr.960.jpg',
    'Twenty dollar federal reserve note 1914.jpg',
    'Series 1914 Twenty Dollar Note Obverse.jpg',
    '$20 Federal Reserve Note Series 1914.jpg',
]

def resolve_wiki(filename):
    api = ('https://commons.wikimedia.org/w/api.php?action=query&titles=File:'
           + urllib.parse.quote(filename, safe='') + '&prop=imageinfo&iiprop=url&format=json')
    try:
        req = urllib.request.Request(api, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as r:
            data = json.loads(r.read())
        for page in data.get('query', {}).get('pages', {}).values():
            ii = page.get('imageinfo', [])
            if ii:
                return ii[0]['url']
    except Exception:
        pass
    return None

def download(url):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception:
            if attempt < 2:
                time.sleep(2 ** attempt + random.random())
    return None

def upload_gcs(data, doc_id, side):
    path = f'{GCS_BASE}/{doc_id}/{side}.jpg'
    for attempt in range(4):
        try:
            bucket.blob(path).upload_from_string(data, content_type='image/jpeg')
            return f'https://storage.googleapis.com/{bucket.name}/{path}'
        except Exception as e:
            if attempt < 3:
                time.sleep(2 ** attempt + random.random())
            else:
                raise

with open('type_to_docids_map.json', encoding='utf-8') as f:
    TYPE_MAP = json.load(f)

DOC_TO_TYPE = {}
for tid, dids in TYPE_MAP.items():
    for did in dids:
        DOC_TO_TYPE[did] = tid

# ── Resolve $20 1914 FRN obverse ──────────────────────────────────────────────
obv_20_url = None
print('Searching for $20 1914 FRN obverse on Wikimedia...')
for fname in CANDIDATES_20_1914:
    url = resolve_wiki(fname)
    time.sleep(0.1)
    if url:
        print(f'  FOUND: {fname}')
        print(f'         {url[:90]}')
        obv_20_url = url
        break
    else:
        print(f'  miss:  {fname}')

# ── Download the $1 FRN obverse ───────────────────────────────────────────────
print(f'\nDownloading $1 FRN obverse...')
obv_1_data = download(OBV_1_FRN_URL)
if not obv_1_data:
    print('ERROR: Could not download $1 FRN obverse. Exiting.')
    sys.exit(1)
print(f'  Downloaded {len(obv_1_data)//1024} KB')

obv_20_data = None
if obv_20_url:
    print(f'\nDownloading $20 1914 FRN obverse...')
    obv_20_data = download(obv_20_url)
    if obv_20_data:
        print(f'  Downloaded {len(obv_20_data)//1024} KB')

# ── Find all NO_OBV docs and upload ──────────────────────────────────────────
fixed = 0
skipped_20 = 0
for d in col.stream():
    data = d.to_dict() or {}
    if data.get('image_url_obverse'):
        continue
    if not data.get('image_url_reverse'):
        continue  # BLANK, not NO_OBV

    type_id = DOC_TO_TYPE.get(d.id, '')
    denom   = data.get('Denomination', '')
    year    = str(data.get('Year', ''))

    # $20 1914 FRN — TYPE_055
    if type_id == 'TYPE_055':
        if obv_20_data:
            gcs_url = upload_gcs(obv_20_data, d.id, 'obverse')
            col.document(d.id).update({
                'image_url_obverse':    gcs_url,
                'image_source_obverse': SOURCE,
                'image_attribution':    ATTR,
            })
            print(f'  ✅ $20 1914 FRN  {d.id[:8]}')
            fixed += 1
        else:
            skipped_20 += 1
        continue

    # All $1 FRN types (TYPE_016-038, TYPE_197-206)
    gcs_url = upload_gcs(obv_1_data, d.id, 'obverse')
    col.document(d.id).update({
        'image_url_obverse':    gcs_url,
        'image_source_obverse': SOURCE,
        'image_attribution':    ATTR,
    })
    fixed += 1
    print(f'  ✅ {type_id:12} {denom} {year}  {d.id[:8]}')

print(f'\n✅ Fixed: {fixed} | $20 1914 still missing: {skipped_20}')
