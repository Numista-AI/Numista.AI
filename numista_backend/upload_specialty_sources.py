"""
upload_specialty_sources.py
Uploads images for specialty note types: Treasury Notes, Continental Currency,
MPC Series 681 & 692, National Bank Notes (generic representative images),
and remaining Legal Tender series.
Uses confirmed Wikimedia filenames from researcher verification.
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
ATTR_WIKI = 'Public Domain. Source: Wikimedia Commons / Smithsonian National Numismatic Collection.'
HEADERS   = {'User-Agent': 'NumistaAI/1.0 (contact eric.seaman@yahoo.com)'}
WIKI_API  = 'https://commons.wikimedia.org/w/api.php'

with open('type_to_docids_map.json', encoding='utf-8') as f:
    TYPE_MAP = json.load(f)

DOC_TO_TYPE = {}
for tid, dids in TYPE_MAP.items():
    for did in dids:
        DOC_TO_TYPE[did] = tid

# ── Plan: type_id → {obv_file, rev_file, obv_url, rev_url} ──────────────────
# Only filenames confirmed to resolve via Wikimedia API by researcher
PLAN = {
    # Treasury Notes
    'TYPE_125': {  # $1 Treasury Note 1891
        'obv_file': 'US-$1-TN-1891-Fr.351.jpg',
        'rev_file': 'US-$1-TN-1891-Fr.351-back.jpg',
    },
    'TYPE_126': {  # $2 Treasury Note 1891
        'obv_file': 'US-$2-TN-1891-Fr.374.jpg',
        'rev_file': 'US-$2-TN-1891-Fr.374-back.jpg',
    },
    # Continental Currency
    'TYPE_127': {  # $2 Continental 1776
        'obv_file': 'Continental currency note 1776 2 dollars.jpg',
        'rev_file': 'Continental currency note 1776 2 dollars back.jpg',
    },
    'TYPE_128': {  # $40 Continental 1778
        'obv_file': 'US-$40-Continental-1778.jpg',
        'rev_file': 'US-$40-Continental-1778-back.jpg',
    },
    # MPC Series 681 ($1 and $5/$10/$20 Vietnam era)
    'TYPE_129': {  # MPC Series 681
        'obv_file': '1 Dollar - United States of America Military Payment Certificate (Series 681, 1969-1970) 01.jpg',
        'rev_file': '1 Dollar - United States of America Military Payment Certificate (Series 681, 1969-1970) 02.jpg',
    },
    'TYPE_130': {  # MPC Series 692
        'obv_file': '1 Dollar - United States of America Military Payment Certificate (Series 692, 1970-1973) 01.jpg',
        'rev_file': '1 Dollar - United States of America Military Payment Certificate (Series 692, 1970-1973) 02.jpg',
    },
    # National Bank Notes — generic representative images by denomination/era
    # 1902 Plain Back / Date Back series (most common era)
    'TYPE_131': {'obv_file': 'US-$5-NBN-1902-Fr.598.jpg'},
    'TYPE_132': {'obv_file': 'US-$10-NBN-1902-Fr.624.jpg'},
    'TYPE_133': {'obv_file': 'US-$20-NBN-1902-Fr.642.jpg'},
    'TYPE_134': {'obv_file': 'US-$50-NBN-1902-Fr.664.jpg'},
    'TYPE_135': {'obv_file': 'US-$100-NBN-1902-Fr.686.jpg'},
    # 1929 Small Size National Bank Notes
    'TYPE_136': {'obv_file': 'US-$5-NBN-1929-Fr.1800.jpg'},
    # Legal Tender series that still need images (TYPE_114, 121, 123)
    'TYPE_114': {  # $2 LTN 1963A — try alternate filenames
        'obv_file': 'US-$2-LT-1963A-Fr.1514.jpg',
        'rev_file': 'US-$2-LT-1917-Fr-58-back.jpg',
    },
    'TYPE_121': {  # $5 LTN 1953B
        'obv_file': 'US-$5-LT-1953B-Fr.1534.jpg',
        'rev_file': 'US-$5-LT-1953-back.jpg',
    },
    'TYPE_123': {  # $5 LTN 1953C
        'obv_file': 'US-$5-LT-1953C-Fr.1535.jpg',
        'rev_file': 'US-$5-LT-1953-back.jpg',
    },
    # Gold Certificates still missing obverse
    'TYPE_090': {'obv_file': 'US-$10-GC-1922-Fr.1173.jpg'},
    'TYPE_092': {'obv_file': 'US-$20-GC-1906-Fr.1178.jpg'},
    'TYPE_093': {'obv_file': 'US-$20-GC-1922-Fr.1187.jpg'},
    'TYPE_095': {'obv_file': 'US-$50-GC-1882-Fr.1191.jpg'},
    # $1 FRN 1969 series specific
    'TYPE_016': {'obv_file': 'US-$1-FRN-1969-Fr.1903.jpg'},
    'TYPE_017': {'obv_file': 'US-$1-FRN-1969-Fr.1903.jpg'},
    # Silver Cert 1899 large size Eagle — alternate pattern
    'TYPE_138': {'obv_file': 'US-$1-SC-1899-Fr.228.jpg'},
    'TYPE_139': {'obv_file': 'US-$1-SC-1899-Fr.226.jpg'},
    # $20 1914 FRN — confirmed by researcher
    'TYPE_055': {
        'obv_file': 'US-$20-FRN-1914-Fr.960a.jpg',
        'rev_file': 'Series 1914 Twenty Dollar Note Reverse.jpg',
    },
}

def resolve_wiki(filename):
    api = (WIKI_API + '?action=query&titles=File:'
           + urllib.parse.quote(filename, safe='')
           + '&prop=imageinfo&iiprop=url&format=json')
    try:
        req = urllib.request.Request(api, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as r:
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

stats = {'resolved': 0, 'not_found': 0, 'uploaded': 0, 'skipped': 0}
not_found = []

for type_id, spec in PLAN.items():
    doc_ids = TYPE_MAP.get(type_id, [])
    if not doc_ids:
        continue

    # Resolve URLs
    urls = {}
    for side in ['obv', 'rev']:
        direct = spec.get(f'{side}_url')
        fname  = spec.get(f'{side}_file')
        if direct:
            urls[side] = direct
        elif fname:
            url = resolve_wiki(fname)
            time.sleep(0.1)
            if url:
                urls[side] = url
            else:
                not_found.append(f'{type_id}/{side}: {fname}')
                stats['not_found'] += 1

    if not urls:
        continue

    # Download images
    images = {}
    for side, url in urls.items():
        data = download(url)
        if data:
            images[side] = data
            stats['resolved'] += 1

    if not images:
        continue

    # Upload to each doc (only fill missing fields)
    for doc_id in doc_ids:
        doc_data = col.document(doc_id).get().to_dict() or {}
        updates  = {}
        for side, data in images.items():
            fs_field = 'image_url_' + ('obverse' if side == 'obv' else 'reverse')
            if doc_data.get(fs_field):
                stats['skipped'] += 1
                continue
            gcs_url = upload_gcs(data, doc_id, 'obverse' if side == 'obv' else 'reverse')
            updates[fs_field] = gcs_url
            updates[f'image_source_{"obverse" if side == "obv" else "reverse"}'] = SOURCE
            updates['image_attribution'] = ATTR_WIKI
            stats['uploaded'] += 1
        if updates:
            col.document(doc_id).update(updates)

    sides_done = list(images.keys())
    print(f'  {type_id}: {sides_done} → {len(doc_ids)} doc(s)')

print(f'\n✅ Resolved: {stats["resolved"]} | Uploaded: {stats["uploaded"]} | Already set: {stats["skipped"]} | Not found: {stats["not_found"]}')
if not_found:
    print(f'\nStill missing ({len(not_found)}):')
    for nf in not_found:
        print(f'  {nf}')
