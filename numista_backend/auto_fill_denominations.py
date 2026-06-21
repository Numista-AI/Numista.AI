import os, sys
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore

creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('coins')

# Denomination map: Program/Series (lowercase key) → correct denomination
DENOM_MAP = {
    'morgan silver dollar': 'Silver Dollar',
    'morgan dollar': 'Silver Dollar',
    'peace dollar': 'Silver Dollar',
    'peace silver dollar': 'Silver Dollar',
    'eisenhower dollar': 'Dollar',
    'eisenhower': 'Dollar',
    'susan b. anthony dollar': 'Dollar',
    'sacagawea dollar': 'Dollar',
    'presidential dollar': 'Dollar',
    'native american dollar': 'Dollar',
    'american innovation dollar': 'Dollar',
    'franklin half dollar': 'Half Dollar',
    'kennedy half dollar': 'Half Dollar',
    'walking liberty half dollar': 'Half Dollar',
    'barber half dollar': 'Half Dollar',
    'liberty seated half dollar': 'Half Dollar',
    'washington quarter': 'Quarter',
    'state quarters': 'Quarter',
    'national park quarter': 'Quarter',
    'america the beautiful quarter': 'Quarter',
    'american women quarter': 'Quarter',
    'barber quarter': 'Quarter',
    'liberty seated quarter': 'Quarter',
    'standing liberty quarter': 'Quarter',
    'roosevelt dime': 'Dime',
    'mercury dime': 'Dime',
    'barber dime': 'Dime',
    'liberty seated dime': 'Dime',
    'jefferson nickel': 'Nickel',
    'buffalo nickel': 'Nickel',
    'liberty head nickel': 'Nickel',
    'lincoln cent': 'Cent',
    'lincoln memorial cent': 'Cent',
    'lincoln wheat cent': 'Cent',
    'lincoln shield cent': 'Cent',
    'indian head cent': 'Cent',
    'flying eagle cent': 'Cent',
    'american silver eagle': 'Silver Dollar',
    'american gold eagle': 'Gold Dollar',
    'saint-gaudens double eagle': '$20',
    'liberty double eagle': '$20',
    'morgan': 'Silver Dollar',
}

docs = list(col.stream())
updates = []
for d in docs:
    data = d.to_dict() or {}
    denom = str(data.get('Denomination', '')).strip()
    prog = str(data.get('Program/Series', '')).strip().lower()
    
    if denom and denom not in ('', 'nan', 'None', '[NONE]'):
        continue  # already has denomination
    
    # Try to match program to denomination
    matched_denom = None
    for key, val in DENOM_MAP.items():
        if key in prog:
            matched_denom = val
            break
    
    if matched_denom:
        updates.append((d.id, matched_denom, data.get('Program/Series', ''), data.get('Year', '')))

print(f'Found {len(updates)} coins with missing denomination that can be auto-filled:')
for doc_id, denom, prog, yr in updates[:40]:
    print(f'  [{yr}] {prog} → {denom}')

print(f'\nTotal to update: {len(updates)}')
print('\nTo actually apply, change DRY_RUN = False and re-run.')
DRY_RUN = True

if not DRY_RUN:
    batch = db.batch()
    for i, (doc_id, denom, prog, yr) in enumerate(updates):
        ref = col.document(doc_id)
        batch.update(ref, {'Denomination': denom})
        if (i + 1) % 500 == 0:
            batch.commit()
            batch = db.batch()
    batch.commit()
    print(f'Updated {len(updates)} coins.')
