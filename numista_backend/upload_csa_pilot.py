"""
upload_csa_pilot.py
Uploads the Confederate pilot images to GCS and writes URLs to Firestore.
Respects existing data: only fills BLANK fields.
"""
import os, sys
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore, storage

creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
gcs = storage.Client(credentials=creds)
bucket = gcs.bucket('numista-uploads-studio-9101802118-8c9a8')

IMAGE_DIR = r'C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\Coin Images\Coins Images to Find\21 JUN 26\pilot_confederate_5\pilot_confederate_5\images'
USER_EMAIL = 'jseaman1204@gmail.com'
GCS_PREFIX = f'users/{USER_EMAIL}/currency'

# Items: (doc_id, local_obverse_filename, local_reverse_filename, description)
ITEMS = [
    (
        '2ea45a00-908d-477b-8eeb-20a127ae6db2',
        '2ea45a00-908d-477b-8eeb-20a127ae6db2_obverse.jpg',
        '2ea45a00-908d-477b-8eeb-20a127ae6db2_reverse.jpg',
        'T-64 $500 Stonewall Jackson (1864)',
    ),
    (
        '187bffa4-81a3-4df7-95a8-77b76e06c47f',
        '187bffa4-81a3-4df7-95a8-77b76e06c47f_obverse.jpg',
        '187bffa4-81a3-4df7-95a8-77b76e06c47f_reverse.jpg',
        'T-63 50c Jefferson Davis (1863)',
    ),
]

col = db.collection('users').document(USER_EMAIL).collection('currency')

def upload_image(local_path, gcs_path):
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(local_path, content_type='image/jpeg')
    return f'https://storage.googleapis.com/{bucket.name}/{gcs_path}'

for doc_id, obv_file, rev_file, desc in ITEMS:
    print(f'\n--- {desc} ({doc_id[:8]}...) ---')
    
    # Check current Firestore state
    d = col.document(doc_id).get()
    if not d.exists:
        print(f'  WARNING: Document not found in Firestore!')
        continue
    
    data = d.to_dict() or {}
    current_obv = data.get('image_url_obverse', '') or ''
    current_rev = data.get('image_url_reverse', '') or ''
    updates = {}

    # Obverse: only upload if blank
    if not current_obv:
        local_obv = os.path.join(IMAGE_DIR, obv_file)
        if os.path.exists(local_obv):
            gcs_path = f'{GCS_PREFIX}/{doc_id}/obverse.jpg'
            url = upload_image(local_obv, gcs_path)
            updates['image_url_obverse'] = url
            updates['image_source_obverse'] = 'pilot_confederate_5_ai_render'
            print(f'  OBV uploaded → {url[:70]}')
        else:
            print(f'  OBV file not found: {local_obv}')
    else:
        print(f'  OBV skipped (already set): {current_obv[:60]}')

    # Reverse: only upload if blank
    if not current_rev:
        local_rev = os.path.join(IMAGE_DIR, rev_file)
        if os.path.exists(local_rev):
            gcs_path = f'{GCS_PREFIX}/{doc_id}/reverse.jpg'
            url = upload_image(local_rev, gcs_path)
            updates['image_url_reverse'] = url
            updates['image_source_reverse'] = 'pilot_confederate_5_ai_render'
            print(f'  REV uploaded → {url[:70]}')
        else:
            print(f'  REV file not found: {local_rev}')
    else:
        print(f'  REV skipped (already set): {current_rev[:60]}')

    if updates:
        col.document(doc_id).update(updates)
        print(f'  Firestore updated with {list(updates.keys())}')
    else:
        print(f'  No updates needed.')

print('\n✅ Done.')
