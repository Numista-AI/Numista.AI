import os, sys
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore

creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('coins')

docs = list(col.stream())
found = []
for d in docs:
    data = d.to_dict() or {}
    yr = str(data.get('Year', ''))
    prog = str(data.get('Program/Series', ''))
    if yr == '2024' and 'Kennedy' in prog and 'Half' in prog:
        found.append((d.id, data))

print(f'Found {len(found)} matching 2024 Kennedy Half Dollar docs')
for doc_id, data in found:
    sf = data.get('source_file', '[MISSING]')
    src = data.get('source', '[MISSING]')
    retailer = data.get('Retailer/Website', '[MISSING]')
    created = data.get('created_at', '[MISSING]')
    restored = data.get('restore_source', '[MISSING]')
    print(f'  ID: {doc_id}')
    print(f'  source_file: {sf!r}')
    print(f'  source: {src!r}')
    print(f'  Retailer/Website: {retailer!r}')
    print(f'  created_at: {created}')
    print(f'  restore_source: {restored}')
    print()
