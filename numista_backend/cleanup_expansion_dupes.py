"""
cleanup_expansion_dupes.py
Remove set-expansion coins that duplicate existing coins in AJ's collection.
 
Logic: 
  - For each (Year, Denomination, Program, Mint Mark) group that has BOTH 
    set-expansion coins AND pre-existing coins, the expansion coins are removed.
  - Pre-existing coins (with richer historical data) are kept.
  - If a group has ONLY expansion coins (no pre-existing), they are kept.

DRY_RUN = True: prints what would be deleted without touching Firestore.
DRY_RUN = False: ACTUALLY deletes from Firestore (irreversible!).
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

DRY_RUN = True   # CHANGE TO False TO ACTUALLY DELETE

print(f'MODE: {"DRY RUN" if DRY_RUN else "*** LIVE DELETION ***"}')
print('Loading AJ coins...')
docs = list(col.stream())
all_coins = [{'id': d.id, 'data': d.to_dict() or {}} for d in docs]
print(f'Total: {len(all_coins)} coins\n')

expansion = [c for c in all_coins if 'set_expansion' in str(c['data'].get('import_batch', '')).lower()]
others    = [c for c in all_coins if 'set_expansion' not in str(c['data'].get('import_batch', '')).lower()]

# Build existing coin lookup
existing_keys = collections.defaultdict(list)
for c in others:
    d = c['data']
    key = (
        str(d.get('Year', '')).strip(),
        str(d.get('Denomination', '')).strip(),
        str(d.get('Program/Series', '')).strip(),
        str(d.get('Mint Mark', '')).strip(),
    )
    existing_keys[key].append(c)

# Find expansion coins to delete
to_delete = []
for c in expansion:
    d = c['data']
    key = (
        str(d.get('Year', '')).strip(),
        str(d.get('Denomination', '')).strip(),
        str(d.get('Program/Series', '')).strip(),
        str(d.get('Mint Mark', '')).strip(),
    )
    if key in existing_keys:
        to_delete.append({'id': c['id'], 'key': key, 'existing_count': len(existing_keys[key])})

print(f'Set expansion coins: {len(expansion)}')
print(f'Expansion coins overlapping existing → to DELETE: {len(to_delete)}')
print(f'Expansion coins with no overlap (KEPT): {len(expansion) - len(to_delete)}')
print()
print('Records to delete:')
for r in to_delete:
    yr, denom, prog, mint = r['key']
    print(f"  DELETE {r['id']} — {yr} {denom} [{prog}] (kept {r['existing_count']} existing)")

if not DRY_RUN:
    print(f'\n*** DELETING {len(to_delete)} RECORDS FROM FIRESTORE ***')
    batch = db.batch()
    for i, r in enumerate(to_delete):
        batch.delete(col.document(r['id']))
        if (i + 1) % 500 == 0:  # Firestore batch limit
            batch.commit()
            batch = db.batch()
    batch.commit()
    print(f'✅ Deleted {len(to_delete)} records.')
    print(f'AJ collection now has {len(all_coins) - len(to_delete)} coins.')
else:
    print(f'\nDRY RUN complete. Run with DRY_RUN = False to actually delete.')
