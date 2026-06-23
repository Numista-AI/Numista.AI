"""
currency_image_gaps.py
Queries all currency docs and reports image coverage by category.
"""
import os, sys
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore

creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('currency')

all_docs = list(col.stream())
print(f'Total currency docs: {len(all_docs)}\n')

gaps = []
by_category = {}

for d in all_docs:
    data = d.to_dict() or {}
    obv  = bool(data.get('image_url_obverse', ''))
    rev  = bool(data.get('image_url_reverse', ''))
    desc = str(data.get('Description', ''))
    cat  = str(data.get('currency_type_label', '') or data.get('Type', '') or 'Unknown')
    year = str(data.get('Year', '') or '')
    denom = str(data.get('denomination_parsed', '') or data.get('Denomination', '') or '')

    by_category.setdefault(cat, {'total': 0, 'no_obv': 0, 'no_rev': 0})
    by_category[cat]['total'] += 1
    if not obv: by_category[cat]['no_obv'] += 1
    if not rev: by_category[cat]['no_rev'] += 1

    if not obv or not rev:
        missing = []
        if not obv: missing.append('OBV')
        if not rev: missing.append('REV')
        gaps.append({
            'doc_id': d.id,
            'desc': desc[:50],
            'cat': cat,
            'year': year,
            'denom': denom,
            'missing': ', '.join(missing),
        })

print('=== COVERAGE BY CATEGORY ===')
for cat, stats in sorted(by_category.items()):
    complete = stats['total'] - max(stats['no_obv'], stats['no_rev'])
    print(f'{cat[:45]:45} total={stats["total"]:3}  missing_obv={stats["no_obv"]:3}  missing_rev={stats["no_rev"]:3}')

print(f'\n=== GAPS ({len(gaps)} docs need work) ===')
for g in gaps:
    print(f'{g["doc_id"][:8]}  {g["denom"]:8}  {g["year"]:6}  [{g["missing"]:7}]  {g["cat"][:30]:30}  {g["desc"]}')
