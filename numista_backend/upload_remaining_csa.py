import os, sys
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore, storage

creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
gcs = storage.Client(credentials=creds)
bucket = gcs.bucket('numista-uploads-studio-9101802118-8c9a8')

col = db.collection('users').document('jseaman1204@gmail.com').collection('currency')
USER_EMAIL = 'jseaman1204@gmail.com'
IMAGES_DIR = r'C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\Coin Images\Coins Images to Find\Downloads from Grok\_remaining_extract\pilot_confederate_remaining_v1\images'

# Doc IDs from manifest
ids = {
    'c1b68828-53c5-4b9d-ab69-3eb3b636f69e': '$10 Confederate 1864',
    '3ec35374-d5ed-4f0a-b123-d151089c441d': '$20 Confederate 1864',
    'd27ddc4f-063d-4adf-bfcd-9392e40239fa': '$5 Confederate 1864',
}

print('=== Firestore Doc Check ===')
for did, label in ids.items():
    d = col.document(did).get()
    if d.exists:
        data = d.to_dict() or {}
        desc = str(data.get('Description', ''))[:60]
        obv = str(data.get('image_url_obverse', '') or '')[:40] or 'BLANK'
        print(f'FOUND ({label}): {did[:8]}')
        print(f'  Description: {desc}')
        print(f'  Obverse: {obv}')
    else:
        print(f'NOT FOUND: {did[:8]} — {label}')

# Upload the 2 passing images
# WhHb1.jpg = $5 obverse (d27ddc4f) -> PASS
# qvhPc.jpg = $10 reverse (c1b68828) -> PASS
UPLOADS = [
    ('d27ddc4f-063d-4adf-bfcd-9392e40239fa', 'obverse', 'WhHb1.jpg', '$5 1864 obverse'),
    ('c1b68828-53c5-4b9d-ab69-3eb3b636f69e', 'reverse', 'qvhPc.jpg', '$10 1864 reverse'),
]

print('\n=== Uploading Passing Images ===')
for doc_id, side, filename, label in UPLOADS:
    d = col.document(doc_id).get()
    if not d.exists:
        print(f'SKIP (doc not in Firestore): {label}')
        continue
    local = os.path.join(IMAGES_DIR, filename)
    gcs_path = f'users/{USER_EMAIL}/currency/{doc_id}/{side}.jpg'
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(local, content_type='image/jpeg')
    url = f'https://storage.googleapis.com/{bucket.name}/{gcs_path}'
    col.document(doc_id).update({
        f'image_url_{side}': url,
        f'image_source_{side}': 'grok_render_qc_pass',
    })
    print(f'  Uploaded {label}: {url[:70]}')

print('\nDone.')
