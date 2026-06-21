"""
upload_corrected_renders.py
Uploads the AI-corrected CSA currency images to GCS and updates Firestore.
- T-63 (187bffa4): replaces both sides with corrected renders
- $1 1864 (1af7178f): uploads corrected obverse + passing reverse from Grok
"""
import os, sys, json, datetime
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore, storage

creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
gcs = storage.Client(credentials=creds)
bucket = gcs.bucket('numista-uploads-studio-9101802118-8c9a8')

USER_EMAIL = 'jseaman1204@gmail.com'
GCS_PREFIX = f'users/{USER_EMAIL}/currency'
ARTIFACTS  = r'C:\Users\ericd\.gemini\antigravity\brain\26eebf0f-3c8f-47c1-940b-b41df002779f'
EXTRACT    = r'C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\Coin Images\Coins Images to Find\Downloads from Grok\_new_extract\pilot_confederate_5\images'
TRACKER    = r'C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\Coin Images\Coins Images to Find\Downloads from Grok\processed_renders.json'

UPLOADS = [
    # (doc_id, side, local_path, content_type, source_label)
    (
        '187bffa4-81a3-4df7-95a8-77b76e06c47f', 'obverse',
        os.path.join(ARTIFACTS, 't63_jefferson_davis_obverse_corrected_1782081528548.png'),
        'image/png', 'antigravity_corrected_render'
    ),
    (
        '187bffa4-81a3-4df7-95a8-77b76e06c47f', 'reverse',
        os.path.join(ARTIFACTS, 't63_jefferson_davis_reverse_corrected_1782081547137.png'),
        'image/png', 'antigravity_corrected_render'
    ),
    (
        '1af7178f-a7d4-463b-ae66-a508a6912da2', 'obverse',
        os.path.join(ARTIFACTS, 'csa_1dollar_1864_obverse_corrected_1782081571287.png'),
        'image/png', 'antigravity_corrected_render'
    ),
    (
        '1af7178f-a7d4-463b-ae66-a508a6912da2', 'reverse',
        os.path.join(EXTRACT, '1af7178f-a7d4-463b-ae66-a508a6912da2_reverse.jpg'),
        'image/jpeg', 'grok_render_qc_pass'
    ),
]

col = db.collection('users').document(USER_EMAIL).collection('currency')
results = []

for doc_id, side, local_path, ctype, source in UPLOADS:
    print(f'\n[{doc_id[:8]}] {side.upper()}')
    if not os.path.exists(local_path):
        print(f'  ERROR: file not found — {local_path}')
        continue

    ext = 'png' if ctype == 'image/png' else 'jpg'
    gcs_path = f'{GCS_PREFIX}/{doc_id}/{side}.{ext}'
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(local_path, content_type=ctype)
    url = f'https://storage.googleapis.com/{bucket.name}/{gcs_path}'
    print(f'  Uploaded → {url[:75]}')

    # Write to Firestore (overwrite existing)
    field = f'image_url_{side}'
    source_field = f'image_source_{side}'
    col.document(doc_id).update({field: url, source_field: source})
    print(f'  Firestore updated: {field}')
    results.append({'doc_id': doc_id, 'side': side, 'url': url, 'source': source})

print('\n✅ All uploads complete.')

# Update tracker
with open(TRACKER, 'r', encoding='utf-8') as f:
    tracker = json.load(f)

tracker['processed'].append({
    'entry': 'pilot_confederate_5.zip (v2 — corrected)',
    'type': 'zip',
    'zip_size_bytes': 2990912,
    'processed_at': datetime.datetime.utcnow().isoformat() + 'Z',
    'qc_result': 'corrected_by_antigravity',
    'qc_notes': (
        'T-63 obverse: "Confedereerrate" fixed. '
        'T-63 reverse: fully garbled — regenerated clean. '
        '$1 obverse: multiple garbled strings — regenerated clean. '
        '$1 reverse: passed Grok QC, uploaded as-is.'
    ),
    'items_uploaded': results,
})

with open(TRACKER, 'w', encoding='utf-8') as f:
    json.dump(tracker, f, indent=2)
print('Tracker updated.')
