import os, sys
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore
creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')

doc_ids = [
    '2ea45a00-908d-477b-8eeb-20a127ae6db2',  # T-64 $500 Stonewall Jackson
    '187bffa4-81a3-4df7-95a8-77b76e06c47f',  # T-63 50c Jefferson Davis
]

# Try different collection paths
paths = [
    'currency',
    'paper_money',
    'notes',
]

user_ref = db.collection('users').document('jseaman1204@gmail.com')
for path in paths:
    for did in doc_ids:
        d = user_ref.collection(path).document(did).get()
        if d.exists:
            data = d.to_dict() or {}
            desc = str(data.get('Description', ''))[:80]
            obv = str(data.get('image_url_obverse', ''))[:70] or 'BLANK'
            rev = str(data.get('image_url_reverse', ''))[:70] or 'BLANK'
            src = data.get('cert_image_source', 'none')
            print(f'FOUND in /{path}/: {did[:8]}...')
            print(f'  Description: {desc}')
            print(f'  image_url_obverse: {obv}')
            print(f'  image_url_reverse: {rev}')
            print(f'  cert_image_source: {src}')

# Also check top-level collections
print('\nChecking top-level collections for these IDs...')
for path in paths:
    col = db.collection(path)
    for did in doc_ids:
        d = col.document(did).get()
        if d.exists:
            print(f'FOUND in top-level /{path}/: {did[:8]}...')
