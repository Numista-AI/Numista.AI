import os, sys
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore
creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('currency')

all_docs = list(col.stream())
csa = [d for d in all_docs if 'confederate' in str(d.to_dict().get('Description', '')).lower()
       or 'confederate' in str(d.to_dict().get('currency_type_label', '')).lower()]

print('NEEDS WORK:')
for d in csa:
    data = d.to_dict() or {}
    obv = bool(data.get('image_url_obverse'))
    rev = bool(data.get('image_url_reverse'))
    if obv and rev:
        continue
    desc  = str(data.get('Description', ''))
    year  = str(data.get('Year', '') or data.get('year_parsed', '') or '')
    denom = str(data.get('denomination_parsed', '') or data.get('Denomination', ''))
    notes = str(data.get('Notes', '') or data.get('Grade', '') or '')
    missing = []
    if not obv: missing.append('OBV')
    if not rev: missing.append('REV')
    print(f'\n{d.id}')
    print(f'  Desc:  {desc}')
    print(f'  Year:  {year}  Denom: {denom}')
    print(f'  Notes: {notes}')
    print(f'  MISSING: {", ".join(missing)}')
