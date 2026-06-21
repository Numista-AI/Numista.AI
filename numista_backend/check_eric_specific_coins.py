import os, sys
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore
creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')

# Find specific coins in Eric's collection
eric_col = db.collection('users').document('eric.seaman@yahoo.com').collection('coins')
eric_docs = {d.id: d.to_dict() for d in eric_col.stream()}

# Search for coins by invoice number
target_invoices = ['66327175', '67670995', '67556776']
print('Eric coins with matching invoice numbers:')
for doc_id, data in eric_docs.items():
    inv = data.get('Retailer Invoice #', '')
    if any(t in str(inv) for t in target_invoices):
        sf = data.get('source_file', '')
        print(f'  ID: {doc_id[:12]} | Year: {data.get("Year")} | Program: {data.get("Program/Series")[:30]}')
        print(f'    Invoice: {inv} | source_file: {repr(sf[:50])}')
        print()

# Also show total breakdown
with_sf = [d for d in eric_docs.values() if d.get('source_file')]
without_sf = [d for d in eric_docs.values() if not d.get('source_file')]
print(f'\nEric total: {len(eric_docs)} | With source_file: {len(with_sf)} | Without: {len(without_sf)}')
if without_sf:
    print(f'\nSample coins WITHOUT source_file (first 5):')
    for data in without_sf[:5]:
        print(f'  Year: {data.get("Year")} | Program: {data.get("Program/Series")[:40]} | Invoice: {data.get("Retailer Invoice #")}')
