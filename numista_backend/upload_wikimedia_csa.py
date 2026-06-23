"""
upload_wikimedia_csa.py
Downloads Wikimedia/Smithsonian CSA currency images and uploads to GCS + Firestore.
Handles composite images (obverse+reverse stacked) by cropping at midpoint.
"""
import os, sys, urllib.request, io
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from PIL import Image
import google.auth
from google.cloud import firestore, storage

creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
gcs = storage.Client(credentials=creds)
bucket = gcs.bucket('numista-uploads-studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('currency')

HEADERS = {'User-Agent': 'NumistaAI/1.0 (educational numismatic collection; contact eric.seaman@yahoo.com)'}

def download(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

def upload_bytes(data, gcs_path, ctype='image/jpeg'):
    blob = bucket.blob(gcs_path)
    blob.upload_from_string(data, content_type=ctype)
    return f'https://storage.googleapis.com/{bucket.name}/{gcs_path}'

def crop_top(data):
    """Crop top half of composite image (obverse)."""
    img = Image.open(io.BytesIO(data))
    w, h = img.size
    cropped = img.crop((0, 0, w, h // 2))
    buf = io.BytesIO()
    cropped.save(buf, format='JPEG', quality=92)
    return buf.getvalue()

def crop_bottom(data):
    """Crop bottom half of composite image (reverse)."""
    img = Image.open(io.BytesIO(data))
    w, h = img.size
    cropped = img.crop((0, h // 2, w, h))
    buf = io.BytesIO()
    cropped.save(buf, format='JPEG', quality=92)
    return buf.getvalue()

BASE_GCS = 'users/jseaman1204@gmail.com/currency'
SOURCE = 'smithsonian_national_numismatic_collection_wikimedia_pd'

# Plan: each entry is (doc_id, label, obverse_action, reverse_action)
# action = ('direct', url) | ('crop_top', url) | ('crop_bottom', url) | None
PLAN = [
    {
        'doc_id': '1c714347-d968-4cb4-9d2e-340b5c4cc9ea',
        'label': '$50 1864 T-66',
        'obverse': ('direct', 'https://upload.wikimedia.org/wikipedia/commons/a/a9/Recto_Confederate_States_of_America_50_dollars_1864_urn-3_HBS.Baker.AC_1142229.jpeg'),
        'reverse': ('direct', 'https://upload.wikimedia.org/wikipedia/commons/a/a3/Verso_Confederate_States_of_America_50_dollars_1864_urn-3_HBS.Baker.AC_1142226.jpeg'),
    },
    {
        'doc_id': '257a0f1b-5f4c-4a9b-8d2d-2e2c745d4157',
        'label': '$5 1861 T-12',
        'obverse': ('crop_top',    'https://upload.wikimedia.org/wikipedia/commons/2/27/CSA-T12-%245-1861.jpg'),
        'reverse': ('crop_bottom', 'https://upload.wikimedia.org/wikipedia/commons/2/27/CSA-T12-%245-1861.jpg'),
    },
    {
        'doc_id': '38f79268-6312-4e7b-9080-7f146190c0fc',
        'label': '$2 1862 T-54 (uniface)',
        'obverse': ('direct', 'https://upload.wikimedia.org/wikipedia/commons/d/dd/CSA-T54-%242-1862.jpg'),
        'reverse': None,  # Uniface note — no printed reverse exists
    },
    {
        'doc_id': '3ec35374-d5ed-4f0a-b123-d151089c441d',
        'label': '$20 1861 T-9',
        'obverse': ('direct', 'https://upload.wikimedia.org/wikipedia/commons/2/2e/CSA-T9-%2420-1861.jpg'),
        'reverse': ('direct', 'https://upload.wikimedia.org/wikipedia/commons/4/4e/Verso_Confederate_States_of_America_20_dollars_1861_urn-3_HBS.Baker.AC_1142176.jpeg'),
    },
    {
        'doc_id': '53f2d258-d5ad-4dca-b1e5-a1949cc60935',
        'label': '$100 1862-A T-39',
        'obverse': ('direct', 'https://upload.wikimedia.org/wikipedia/commons/9/90/CSA-T39-%24100-1862.jpg'),
        'reverse': ('direct', 'https://upload.wikimedia.org/wikipedia/commons/e/e2/Verso_Confederate_States_of_America_100_dollars_1862_urn-3_HBS.Baker.AC_1142186.jpeg'),
    },
    {
        'doc_id': '579c33da-3c39-4488-87b7-656dd128bf2a',
        'label': '$100 1862-B T-49',
        'obverse': ('crop_top',    'https://upload.wikimedia.org/wikipedia/commons/5/56/CSA-T49-%24100-1862.jpg'),
        'reverse': ('crop_bottom', 'https://upload.wikimedia.org/wikipedia/commons/5/56/CSA-T49-%24100-1862.jpg'),
    },
    {
        'doc_id': 'c67a200d-53e4-4f2d-8e6a-2dba272364bd',
        'label': '$2 1864 T-70',
        'obverse': ('direct', 'https://upload.wikimedia.org/wikipedia/commons/c/c7/CSA-T70-%242-1864.jpg'),
        'reverse': ('direct', 'https://upload.wikimedia.org/wikipedia/commons/1/15/Verso_Confederate_States_of_America_2_dollars_1864_urn-3_HBS.Baker.AC_1142218.jpeg'),
    },
    {
        'doc_id': 'd27ddc4f-063d-4adf-bfcd-9392e40239fa',
        'label': '$5 1864 T-69 (reverse only)',
        'obverse': None,  # Already uploaded (Grok pass)
        'reverse': ('crop_bottom', 'https://upload.wikimedia.org/wikipedia/commons/a/af/CSA-T69-%245-1864.jpg'),
    },
    {
        'doc_id': 'de0e80de-ebf3-4ac8-9998-6a87514be086',
        'label': '$5 1861 Cut-Cancelled (T-12 representative)',
        'obverse': ('crop_top',    'https://upload.wikimedia.org/wikipedia/commons/2/27/CSA-T12-%245-1861.jpg'),
        'reverse': ('crop_bottom', 'https://upload.wikimedia.org/wikipedia/commons/2/27/CSA-T12-%245-1861.jpg'),
    },
]

# Cache downloaded composites so we don't re-download
cache = {}

for item in PLAN:
    doc_id = item['doc_id']
    label  = item['label']
    print(f'\n=== {label} ({doc_id[:8]}) ===')

    updates = {}
    for side in ['obverse', 'reverse']:
        action = item[side]
        if action is None:
            if side == 'reverse':
                updates['image_source_reverse'] = 'uniface_note_no_reverse_exists'
            print(f'  {side.upper()}: skipped')
            continue

        mode, url = action
        if url not in cache:
            print(f'  Downloading {url[-40:]}...')
            try:
                cache[url] = download(url)
                print(f'  Downloaded {len(cache[url])/1024:.0f} KB')
            except Exception as e:
                print(f'  ERROR downloading: {e}')
                continue

        raw = cache[url]
        if mode == 'direct':
            data = raw
        elif mode == 'crop_top':
            data = crop_top(raw)
            print(f'  Cropped top (obverse) {len(data)/1024:.0f} KB')
        elif mode == 'crop_bottom':
            data = crop_bottom(raw)
            print(f'  Cropped bottom (reverse) {len(data)/1024:.0f} KB')

        gcs_path = f'{BASE_GCS}/{doc_id}/{side}.jpg'
        url_out = upload_bytes(data, gcs_path)
        updates[f'image_url_{side}'] = url_out
        updates[f'image_source_{side}'] = SOURCE
        updates['image_attribution'] = 'National Numismatic Collection, National Museum of American History (Smithsonian), via Wikimedia Commons. Public Domain.'
        print(f'  {side.upper()} → {url_out[:70]}')

    if updates:
        col.document(doc_id).update(updates)
        print(f'  Firestore updated.')

print('\n\n✅ All done.')
