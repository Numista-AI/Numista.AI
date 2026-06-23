"""currency_partial_audit.py — pulls every partial/blank currency doc with full details"""
import os, sys, csv
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore
from collections import Counter, defaultdict

creds, _ = google.auth.default()
db  = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('currency')

rows = []
for d in col.stream():
    data = d.to_dict() or {}
    has_obv = bool(data.get('image_url_obverse'))
    has_rev = bool(data.get('image_url_reverse'))
    if has_obv and has_rev:
        continue
    status = 'BLANK' if (not has_obv and not has_rev) else ('NO_REV' if has_obv else 'NO_OBV')
    rows.append({
        'doc_id':      d.id,
        'type_label':  data.get('currency_type_label', ''),
        'type_key':    data.get('currency_type', ''),
        'denom':       data.get('Denomination', ''),
        'year':        data.get('Year', ''),
        'description': data.get('Description', ''),
        'series':      data.get('Series/Issuer', ''),
        'status':      status,
    })

rows.sort(key=lambda r: (r['type_label'], r['status'], r['denom'], str(r['year'])))

with open('currency_partial_audit.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['doc_id','type_label','type_key','denom','year','description','series','status'])
    w.writeheader()
    w.writerows(rows)

# Summary by type + status
ctr = Counter((r['type_label'] or 'Unknown', r['status']) for r in rows)
by_type = defaultdict(lambda: {'BLANK':0,'NO_REV':0,'NO_OBV':0})
for (lbl, st), cnt in ctr.items():
    by_type[lbl][st] = cnt

print(f'Total needing work: {len(rows)}\n')
print(f'{"Type":35} {"BLANK":>6} {"NO_REV":>7} {"NO_OBV":>7}')
print('-' * 60)
for lbl in sorted(by_type):
    d = by_type[lbl]
    print(f'{lbl:35} {d["BLANK"]:6} {d["NO_REV"]:7} {d["NO_OBV"]:7}')

# Print every Unknown-category doc's description so we can identify them
print('\n--- UNKNOWN category docs ---')
for r in rows:
    if not r['type_label'] or r['type_label'] == 'Unknown':
        print(f'  {r["status"]:8}  {r["denom"]:6}  {r["year"]:10}  {r["description"][:80]}')

print(f'\nExported: currency_partial_audit.csv')
