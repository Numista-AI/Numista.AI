import os, sys, csv
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore

creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('currency')
all_docs = list(col.stream())

by_cat = {}
gaps = []

for d in all_docs:
    data = d.to_dict() or {}
    obv  = bool(data.get('image_url_obverse',''))
    rev  = bool(data.get('image_url_reverse',''))
    cat  = str(data.get('currency_type_label','') or 'Unknown').strip() or 'Unknown'
    desc = str(data.get('Description',''))
    year = str(data.get('Year','') or '')
    denom= str(data.get('denomination_parsed','') or data.get('Denomination','') or '')

    by_cat.setdefault(cat, {'total':0,'complete':0,'partial':0,'blank':0})
    by_cat[cat]['total'] += 1
    if obv and rev:
        by_cat[cat]['complete'] += 1
    elif obv or rev:
        by_cat[cat]['partial'] += 1
        missing = 'REV' if obv else 'OBV'
        gaps.append({'doc_id': d.id, 'cat': cat, 'denom': denom, 'year': year, 'desc': desc, 'missing': missing})
    else:
        by_cat[cat]['blank'] += 1
        gaps.append({'doc_id': d.id, 'cat': cat, 'denom': denom, 'year': year, 'desc': desc, 'missing': 'OBV+REV'})

total    = len(all_docs)
complete = sum(v['complete'] for v in by_cat.values())
partial  = sum(v['partial']  for v in by_cat.values())
blank    = sum(v['blank']    for v in by_cat.values())

print(f'TOTAL: {total}  |  Complete: {complete}  |  Partial (1 side): {partial}  |  Blank (0 sides): {blank}')
print(f'Needs work: {partial + blank} docs')
print()

header = f"{'Category':<38} {'Tot':>4} {'Done':>5} {'Part':>5} {'Blank':>6}"
print(header)
print('-' * 62)
for cat, v in sorted(by_cat.items(), key=lambda x: -x[1]['total']):
    print(f"{cat[:38]:<38} {v['total']:>4} {v['complete']:>5} {v['partial']:>5} {v['blank']:>6}")

# Export gap list to CSV for Grok
out_csv = r'C:\Users\ericd\Documents\MyVertexProject\numista_backend\currency_gaps_for_grok.csv'
with open(out_csv, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['doc_id','cat','denom','year','desc','missing'])
    w.writeheader()
    w.writerows(gaps)
print(f'\nGap list exported: {out_csv} ({len(gaps)} rows)')
