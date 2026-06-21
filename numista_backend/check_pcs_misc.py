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

# The 8 miscellaneous PCS items to check for
search_terms = [
    'twenty cent',
    'twenty-cent',
    'gold coin folio',
    'first dollar gold',
    'largest silver',
    'denver mint morgan',
    '1921-d',
    '1921 d morgan',
    'first and last san francisco',
    'walking liberty mint collection',
    'micro o',
    'seated liberty 20',
    'carson city seated',
]

print('Searching existing collection for PCS Miscellaneous items...\n')
for d in docs:
    data = d.to_dict() or {}
    prog = str(data.get('Program/Series', '')).lower()
    notes = str(data.get('Personal Notes', '')).lower()
    theme = str(data.get('Theme/Subject', '')).lower()
    denom = str(data.get('Denomination', '')).lower()
    combined = f'{prog} {notes} {theme} {denom}'
    
    for term in search_terms:
        if term in combined:
            print(f'FOUND [{term}]:')
            print(f'  ID: {d.id}')
            print(f'  Year: {data.get("Year")} | Program: {data.get("Program/Series")}')
            print(f'  Notes: {str(data.get("Personal Notes",""))[:80]}')
            print()
            break

# Also search for Walking Liberty Half collections
print('\n--- Walking Liberty Half Dollar collections ---')
for d in docs:
    data = d.to_dict() or {}
    prog = str(data.get('Program/Series', '')).lower()
    if 'walking liberty' in prog and ('collection' in prog or 'mint' in prog or 'complete' in prog):
        print(f'  {d.id[:8]}... Year={data.get("Year")} | {data.get("Program/Series")}')

print('\n--- Twenty Cent coins ---')
for d in docs:
    data = d.to_dict() or {}
    denom = str(data.get('Denomination', '')).lower()
    prog = str(data.get('Program/Series', '')).lower()
    if 'twenty' in denom or 'twenty' in prog or '20 cent' in denom or '20 cent' in prog:
        print(f'  {d.id[:8]}... Year={data.get("Year")} | Denom={data.get("Denomination")} | {data.get("Program/Series")}')

print('\n--- $1 Gold coins ---')
for d in docs:
    data = d.to_dict() or {}
    denom = str(data.get('Denomination', '')).lower()
    prog = str(data.get('Program/Series', '')).lower()
    if '$1 gold' in denom or '$1 gold' in prog or ('gold' in prog and '1' in denom):
        print(f'  {d.id[:8]}... Year={data.get("Year")} | Denom={data.get("Denomination")} | {data.get("Program/Series")}')

print('\nSearch complete.')
