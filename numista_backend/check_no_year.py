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
no_year = []
for d in docs:
    data = d.to_dict() or {}
    yr = str(data.get('Year', '')).strip().replace('.0', '')
    if not yr or yr == 'nan' or yr == 'None':
        no_year.append((d.id, data))

print(f'Coins with no year: {len(no_year)}')
print()
for doc_id, data in no_year:
    prog = data.get('Program/Series', '[NONE]')
    denom = data.get('Denomination', '[NONE]')
    theme = data.get('Theme/Subject', '[NONE]')
    notes = data.get('Personal Notes', '')
    qty = data.get('Quantity', '')
    retailer = data.get('Retailer/Website', '')
    cond = data.get('Condition', '')
    desc = data.get('Original Description', '')
    print(f'  ID: {doc_id[:12]}...')
    print(f'  Program/Series: {prog}')
    print(f'  Denomination: {denom}')
    print(f'  Theme/Subject: {theme}')
    print(f'  Condition: {cond}')
    print(f'  Quantity: {qty}')
    print(f'  Retailer: {retailer}')
    print(f'  Notes: {str(notes)[:60]}')
    print(f'  Desc: {str(desc)[:80]}')
    print()
