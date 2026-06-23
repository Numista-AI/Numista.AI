#!/usr/bin/env python3
"""Fix the 3 Patsy Mink coins that got obverse-only due to 404 reverse URL."""
import io, sys, json, requests, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
os.chdir(r'C:\Users\ericd\Documents\MyVertexProject\numista_backend')

from google.oauth2 import service_account
from google.cloud import firestore, storage

SA_KEY = 'serviceAccountKey.json.json'
USER   = 'jseaman1204@gmail.com'
BUCKET = 'numista-uploads-studio-9101802118-8c9a8'
UA     = 'NumistaAI/1.0 (eric@numista.ai)'

creds  = service_account.Credentials.from_service_account_file(SA_KEY)
db     = firestore.Client(project=creds.project_id, credentials=creds)
gcs    = storage.Client(project=creds.project_id, credentials=creds)
bucket = gcs.bucket(BUCKET)

s = requests.Session()
s.headers.update({'User-Agent': UA})

# Get the actual Patsy Mink index entry
print('Checking coin_image_index for patsy-mink...')
doc = db.collection('coin_image_index').document('2024_patsy-mink_american-women-quarters_reverse').get()
if doc.exists:
    d = doc.to_dict()
    print(f'  doc data: {d}')
    rev_url = d.get('reverse', {}).get('public_url','')
    print(f'  reverse URL: {rev_url}')
    # Test it
    r = s.head(rev_url, timeout=10)
    print(f'  HTTP status: {r.status_code}')
else:
    print('  NOT FOUND in index')
    # Search all patsy entries
    all_docs = list(db.collection('coin_image_index').stream())
    patsy = [d for d in all_docs if 'patsy' in d.id.lower() or 'mink' in d.id.lower()]
    print(f'  Patsy entries: {[d.id for d in patsy]}')
    for pd in patsy:
        dd = pd.to_dict()
        url = dd.get('reverse', dd.get('obverse', {})).get('public_url','')
        r2 = s.head(url, timeout=10) if url else None
        print(f'    {pd.id}: {url[:80]} -> {r2.status_code if r2 else "N/A"}')
