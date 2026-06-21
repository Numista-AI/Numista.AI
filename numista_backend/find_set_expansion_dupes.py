"""
find_set_expansion_dupes.py
Find records created by the set expansion that may overlap with existing records.
Only flags pairs where one has import_batch='set_expansion_...' and one doesn't.
"""
import os, sys, collections
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import google.auth
from google.cloud import firestore
creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('coins')

print('Loading AJ coins...')
docs = list(col.stream())
print(f'Total: {len(docs)} coins')

# Find coins created by set expansion
set_expansion_coins = []
for d in docs:
    data = d.to_dict() or {}
    batch = str(data.get('import_batch', ''))
    if 'set_expansion' in batch.lower():
        set_expansion_coins.append({'id': d.id, 'data': data})

print(f'\nCoins from set expansion: {len(set_expansion_coins)}')

if not set_expansion_coins:
    print('No set expansion coins found. Checking all import batches...')
    batches = set(str(d.to_dict().get('import_batch', '')) for d in docs)
    print(f'All import batches: {sorted(batches)}')
    
    # Look for any that might be related to sets
    print('\nCoins with set-related program/series:')
    for d in docs:
        data = d.to_dict() or {}
        prog = str(data.get('Program/Series', '')).lower()
        qty = str(data.get('Quantity', '1'))
        if ('set' in prog or 'album' in prog or 'folder' in prog) and qty != '1':
            print(f"  ID: {d.id[:12]} | Year: {data.get('Year')} | Prog: {data.get('Program/Series')[:50]} | Qty: {qty}")
else:
    print('\nSet expansion coins:')
    for c in set_expansion_coins[:20]:
        data = c['data']
        print(f"  ID: {c['id'][:12]} | Year: {data.get('Year')} | {data.get('Program/Series')[:40]} | {data.get('Denomination')} | Mint: {data.get('Mint Mark')}")
