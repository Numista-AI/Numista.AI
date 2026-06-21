import os, sys
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore
creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('coins')

# Find an invoice-scanned coin and show ALL its fields
for d in col.stream():
    data = d.to_dict() or {}
    sf = data.get('source_file', '')
    if sf and sf.startswith('invoices/queue/'):
        print(f'Invoice-scanned coin (ID: {d.id}):')
        for k, v in sorted(data.items()):
            print(f'  {repr(k):35s}: {repr(str(v)[:60])}')
        break  # Just show one example
