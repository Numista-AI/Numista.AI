"""
fix_no_obv.py
For every doc that has image_url_reverse but no image_url_obverse,
find a sibling doc in the same TYPE that already has an obverse and copy it.
If no sibling has one, skip (will be handled by next Wikimedia pass).
"""
import os, sys, json
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore

creds, _ = google.auth.default()
db  = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('currency')

with open('type_to_docids_map.json', encoding='utf-8') as f:
    TYPE_MAP = json.load(f)

DOC_TO_TYPE = {}
for tid, dids in TYPE_MAP.items():
    for did in dids:
        DOC_TO_TYPE[did] = tid

# Cache of type_id -> reference obverse URL (from a sibling that has one)
type_obv_cache = {}

def get_ref_obverse(type_id):
    if type_id in type_obv_cache:
        return type_obv_cache[type_id]
    for doc_id in TYPE_MAP.get(type_id, []):
        data = col.document(doc_id).get().to_dict() or {}
        if data.get('image_url_obverse'):
            result = {
                'image_url_obverse':    data['image_url_obverse'],
                'image_source_obverse': data.get('image_source_obverse', ''),
                'image_attribution':    data.get('image_attribution', ''),
            }
            type_obv_cache[type_id] = result
            return result
    type_obv_cache[type_id] = None
    return None

# Find all NO_OBV docs
no_obv_docs = []
for d in col.stream():
    data = d.to_dict() or {}
    if data.get('image_url_obverse'):
        continue
    if not data.get('image_url_reverse'):
        continue
    no_obv_docs.append((d.id, data))

print(f'Found {len(no_obv_docs)} NO_OBV docs\n')

fixed = 0
no_sibling = []
for doc_id, data in no_obv_docs:
    type_id = DOC_TO_TYPE.get(doc_id)
    if not type_id:
        no_sibling.append(f'{doc_id[:8]} NOT_IN_MAP')
        continue

    ref = get_ref_obverse(type_id)
    if not ref:
        denom = data.get('Denomination','')
        year  = data.get('Year','')
        no_sibling.append(f'{doc_id[:8]} {type_id} {denom} {year}')
        continue

    col.document(doc_id).update({
        'image_url_obverse':    ref['image_url_obverse'],
        'image_source_obverse': ref['image_source_obverse'],
        'image_attribution':    ref['image_attribution'],
    })
    fixed += 1
    print(f'  ✅ {doc_id[:8]}  {type_id}  copied obverse from sibling')

print(f'\n✅ Fixed: {fixed} | No sibling obverse available: {len(no_sibling)}')
if no_sibling:
    print('\nTypes with no obverse anywhere in the group:')
    from collections import Counter
    ctr = Counter(s.split()[1] if len(s.split()) > 1 else s for s in no_sibling)
    for t, n in sorted(ctr.items()):
        print(f'  {t}: {n} docs')
