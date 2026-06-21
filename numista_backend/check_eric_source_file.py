import os, sys
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore
creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')

# Check Eric's collection for invoice-scanned coins
eric_col = db.collection('users').document('eric.seaman@yahoo.com').collection('coins')
eric_docs = list(eric_col.stream())

with_sf = [(d.id, d.to_dict()) for d in eric_docs if d.to_dict().get('source_file')]
print(f"Eric's account: {len(eric_docs)} total coins, {len(with_sf)} with source_file")

if with_sf:
    doc_id, data = with_sf[0]
    print(f'\nExample invoice-scanned coin in Eric account:')
    print(f'  ID: {doc_id}')
    print(f'  Year: {data.get("Year")}')
    print(f'  Program: {data.get("Program/Series")}')
    print(f'  source_file: {data.get("source_file")}')
    print(f'  source: {data.get("source")}')
    print(f'  Cost: {data.get("Cost")} | Purchase Cost: {data.get("Purchase Cost")}')
else:
    print('\nNo source_file coins in Eric account.')
    # Check source values
    sources = set(str(d.to_dict().get('source', '')) for d in eric_docs)
    print(f'Source values: {sources}')
