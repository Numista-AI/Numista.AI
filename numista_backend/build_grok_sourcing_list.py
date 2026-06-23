"""
build_grok_sourcing_list.py
Collapses 401 gap docs into unique note types.
Grok only needs one image per type; we apply it to all matching docs.
"""
import os, sys, csv, json
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore

creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('currency')
all_docs = list(col.stream())

# Group by (category, denomination, year) — these share the same representative image
type_groups = {}
for d in all_docs:
    data = d.to_dict() or {}
    obv  = bool(data.get('image_url_obverse',''))
    rev  = bool(data.get('image_url_reverse',''))
    if obv and rev:
        continue  # already complete

    cat   = str(data.get('currency_type_label','') or 'Unknown').strip() or 'Unknown'
    desc  = str(data.get('Description','') or '')
    year  = str(data.get('Year','') or data.get('year_parsed','') or '')
    denom = str(data.get('denomination_parsed','') or data.get('Denomination','') or '')
    series= str(data.get('Series','') or data.get('series_parsed','') or '')
    missing_obv = not obv
    missing_rev = not rev

    # Build a type key — same cat+denom+year+series = same representative image
    type_key = f'{cat}|{denom}|{year}|{series}'

    if type_key not in type_groups:
        type_groups[type_key] = {
            'type_key': type_key,
            'cat': cat,
            'denom': denom,
            'year': year,
            'series': series,
            'example_desc': desc,
            'doc_ids': [],
            'need_obv': False,
            'need_rev': False,
        }
    type_groups[type_key]['doc_ids'].append(d.id)
    if missing_obv: type_groups[type_key]['need_obv'] = True
    if missing_rev: type_groups[type_key]['need_rev'] = True

# Sort by category then denom
groups = sorted(type_groups.values(), key=lambda x: (x['cat'], x['denom'], x['year']))

# Write the sourcing list for Grok
out_csv = r'C:\Users\ericd\Documents\MyVertexProject\numista_backend\grok_sourcing_list.csv'
with open(out_csv, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['type_id','category','denomination','year','series','need_obverse','need_reverse','doc_count','example_description','doc_ids'])
    for i, g in enumerate(groups):
        type_id = f'TYPE_{i+1:03d}'
        w.writerow([
            type_id,
            g['cat'],
            g['denom'],
            g['year'],
            g['series'],
            'YES' if g['need_obv'] else 'NO',
            'YES' if g['need_rev'] else 'NO',
            len(g['doc_ids']),
            g['example_desc'][:80],
            '|'.join(g['doc_ids']),
        ])

# Print summary
print(f'Unique note types needing images: {len(groups)}')
print(f'Total docs covered: {sum(len(g["doc_ids"]) for g in groups)}')
print()
by_cat = {}
for g in groups:
    by_cat.setdefault(g['cat'], 0)
    by_cat[g['cat']] += 1

print('Types per category:')
for cat, cnt in sorted(by_cat.items(), key=lambda x: -x[1]):
    print(f'  {cat:<38} {cnt} unique types')

print(f'\nGrok sourcing list: {out_csv}')

# Also write the doc_id mapping as JSON for later batch application
mapping_out = r'C:\Users\ericd\Documents\MyVertexProject\numista_backend\type_to_docids_map.json'
mapping = {f'TYPE_{i+1:03d}': g['doc_ids'] for i, g in enumerate(groups)}
with open(mapping_out, 'w', encoding='utf-8') as f:
    json.dump(mapping, f, indent=2)
print(f'Doc ID mapping: {mapping_out}')
