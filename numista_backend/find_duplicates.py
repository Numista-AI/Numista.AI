"""
find_duplicates.py
Find potential duplicate coin records in AJ's Firestore collection.
Groups coins by (Year, Denomination, Program/Series) and finds groups with 2+ records.
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

# Group by key: (Year, Denomination, Program/Series)
groups = collections.defaultdict(list)
for d in docs:
    data = d.to_dict() or {}
    yr   = str(data.get('Year', '')).strip()
    denom = str(data.get('Denomination', '')).strip()
    prog  = str(data.get('Program/Series', '')).strip()
    key = (yr, denom, prog)
    groups[key].append({'id': d.id, 'data': data})

# Find duplicates
dupes = [(k, v) for k, v in groups.items() if len(v) > 1]
dupes.sort(key=lambda x: -len(x[1]))  # Most duplicates first

print(f'\nFound {len(dupes)} groups with 2+ records:')
print()

total_dup_count = 0
for key, coins_list in dupes[:30]:  # Show top 30
    yr, denom, prog = key
    n = len(coins_list)
    total_dup_count += (n - 1)
    print(f'{yr} {denom} [{prog}] — {n} records')
    for c in coins_list:
        data = c['data']
        source = data.get('source', '')
        sf = (data.get('source_file', '') or '')[:30]
        inv = data.get('Retailer Invoice #', '')
        import_batch = data.get('import_batch', '')
        created = str(data.get('created_at', ''))[:10]
        print(f"  ID: {c['id'][:12]} | source={source} | import_batch={import_batch} | inv={inv} | created={created}")

print(f'\nTotal potential duplicate records to remove: {total_dup_count}')
print(f'(keeping 1 of each group = removes {total_dup_count} records)')
