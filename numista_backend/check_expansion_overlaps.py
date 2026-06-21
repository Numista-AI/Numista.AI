"""
check_expansion_overlaps.py
For each set-expansion coin, find if there's another coin in AJ's collection
with the SAME Year, Denomination, Program/Series, and Mint Mark.
These are the true duplicates that need resolution.
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
all_coins = [{'id': d.id, 'data': d.to_dict() or {}} for d in docs]
print(f'Total: {len(all_coins)} coins')

# Separate set expansion coins from others
expansion = [c for c in all_coins if 'set_expansion' in str(c['data'].get('import_batch', '')).lower()]
others = [c for c in all_coins if 'set_expansion' not in str(c['data'].get('import_batch', '')).lower()]

print(f'Set expansion coins: {len(expansion)}')
print(f'Other coins: {len(others)}')

# Build lookup of existing coins by (Year, Denomination, Program/Series, Mint Mark)
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

# Check each expansion coin against existing
print('\n--- Expansion coins that OVERLAP existing records ---')
overlaps = []
for c in expansion:
    d = c['data']
    key = (
        str(d.get('Year', '')).strip(),
        str(d.get('Denomination', '')).strip(),
        str(d.get('Program/Series', '')).strip(),
        str(d.get('Mint Mark', '')).strip(),
    )
    if key in existing_keys:
        overlaps.append({'expansion_coin': c, 'existing': existing_keys[key], 'key': key})

print(f'Found {len(overlaps)} overlapping sets')
for ov in overlaps[:20]:
    yr, denom, prog, mint = ov['key']
    n = len(ov['existing'])
    ec = ov['expansion_coin']
    print(f'\n  {yr} {denom} [{prog}] Mint:{mint!r} — expansion ID: {ec["id"][:12]}')
    for ex in ov['existing'][:3]:
        exd = ex['data']
        print(f'    existing ID: {ex["id"][:12]} | source={exd.get("source")} | inv={exd.get("Retailer Invoice #")} | batch={exd.get("import_batch")}')
    if n > 3:
        print(f'    ... and {n-3} more')
