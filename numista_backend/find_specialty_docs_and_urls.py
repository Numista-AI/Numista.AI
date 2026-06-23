"""
find_specialty_docs_and_urls.py
1. Verify the two real $20 1914 FRN filenames found via Wikimedia search
2. Query Firestore for all docs still needing images, grouped by type
3. Test working Wikimedia filenames for Treasury Notes, Continental Currency, LTN, Gold Certs
"""
import os, sys, json, urllib.request, urllib.parse, time
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore

creds, _ = google.auth.default()
db  = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('currency')

HEADERS  = {'User-Agent': 'NumistaAI/1.0 (contact eric.seaman@yahoo.com)'}
WIKI_API = 'https://commons.wikimedia.org/w/api.php'

def resolve_wiki(filename):
    api = (WIKI_API + '?action=query&titles=File:'
           + urllib.parse.quote(filename, safe='')
           + '&prop=imageinfo&iiprop=url&format=json')
    try:
        req = urllib.request.Request(api, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as r:
            data = json.loads(r.read())
        for page in data.get('query', {}).get('pages', {}).values():
            ii = page.get('imageinfo', [])
            if ii:
                return ii[0]['url']
    except Exception:
        pass
    return None

# ── 1. Verify $20 1914 FRN filenames ─────────────────────────────────────────
print('=== $20 1914 FRN ===')
for fname in ['US-$20-FRN-1914-Fr-1010.jpg', 'US-$20-FRN-1914-Fr-958a.jpg']:
    url = resolve_wiki(fname)
    if url:
        print(f'  FOUND: {fname}')
        print(f'         {url}')
    else:
        print(f'  miss:  {fname}')
    time.sleep(0.1)

# ── 2. Verify Treasury Note filenames ────────────────────────────────────────
print('\n=== Treasury Notes ===')
tn_candidates = [
    'US-$1-TN-1891-Fr.351.jpg',
    'US-$1-TN-1891-Fr-351.jpg',
    'US-$1-Treasury-Note-1891.jpg',
    'US-$2-TN-1891-Fr.374.jpg',
    'US-$2-TN-1891-Fr-374.jpg',
    'US-$2-Treasury-Note-1891.jpg',
    '$1 Treasury Note 1891.jpg',
    'Treasury Note 1891 one dollar.jpg',
    'US-$1-TN-1890-Fr.347.jpg',
    'US-$1-TN-1890-Fr-347.jpg',
]
for fname in tn_candidates:
    url = resolve_wiki(fname)
    if url:
        print(f'  FOUND: {fname}')
        print(f'         {url[:90]}')
    else:
        print(f'  miss:  {fname}')
    time.sleep(0.1)

# ── 3. Verify Continental Currency filenames ──────────────────────────────────
print('\n=== Continental Currency ===')
cc_candidates = [
    'Continental currency note 1776 2 dollars.jpg',
    'Continental currency 1776 2 dollars.jpg',
    'Continental-Currency-$2-May-10-1775.jpg',
    'Continental currency $2 1776.jpg',
    'US-$40-Continental-1778.jpg',
    'US-$40-Continental-1778-front.jpg',
    '1776 Continental Currency 2 Dollars.jpg',
]
for fname in cc_candidates:
    url = resolve_wiki(fname)
    if url:
        print(f'  FOUND: {fname}')
        print(f'         {url[:90]}')
    else:
        print(f'  miss:  {fname}')
    time.sleep(0.1)

# ── 4. Verify LTN filenames still missing ─────────────────────────────────────
print('\n=== LTN / Gold Certs still missing ===')
ltn_cands = [
    'US-$2-LT-1963A-Fr.1514.jpg', 'US-$2-LT-1963A-Fr-1514.jpg',
    'US-$5-LT-1953B-Fr.1534.jpg', 'US-$5-LT-1953B-Fr-1534.jpg',
    'US-$5-LT-1953C-Fr.1535.jpg', 'US-$5-LT-1953C-Fr-1535.jpg',
    'US-$5-LT-1953-back.jpg',      'US-$5-LT-1953-Fr.1532-back.jpg',
    'US-$2-LT-1917-Fr-58-back.jpg','US-$2-LT-1917-Fr.58-back.jpg',
    'US-$10-GC-1922-Fr.1173.jpg',  'US-$10-GC-1922-Fr-1173.jpg',
    'US-$20-GC-1906-Fr.1178.jpg',  'US-$20-GC-1906-Fr-1178.jpg',
    'US-$20-GC-1922-Fr.1187.jpg',  'US-$20-GC-1922-Fr-1187.jpg',
    'US-$50-GC-1882-Fr.1191.jpg',  'US-$50-GC-1882-Fr-1191.jpg',
    'US-$1-SC-1899-Fr.226.jpg',    'US-$1-SC-1899-Fr-226.jpg',
    'US-$1-SC-1899-Fr.228.jpg',    'US-$1-SC-1899-Fr-228.jpg',
]
for fname in ltn_cands:
    url = resolve_wiki(fname)
    if url:
        print(f'  FOUND: {fname}')
        print(f'         {url[:90]}')
    time.sleep(0.08)

# ── 5. Find remaining docs by type label ──────────────────────────────────────
print('\n=== Firestore: remaining blank/partial docs by type ===')
from collections import defaultdict
groups = defaultdict(list)
with open('type_to_docids_map.json', encoding='utf-8') as f:
    TYPE_MAP = json.load(f)
DOC_TO_TYPE = {did: tid for tid, dids in TYPE_MAP.items() for did in dids}

for ref in col.list_documents():
    doc_id = ref.id
    data = ref.get().to_dict() or {}
    has_obv = bool(data.get('image_url_obverse'))
    has_rev = bool(data.get('image_url_reverse'))
    if has_obv and has_rev:
        continue
    lbl   = data.get('currency_type_label', 'Unknown')
    denom = data.get('Denomination', '')
    year  = str(data.get('Year', ''))
    desc  = data.get('Description', '')[:50]
    tid   = DOC_TO_TYPE.get(doc_id, 'NOT_IN_MAP')
    status = 'BLANK' if (not has_obv and not has_rev) else ('NO_REV' if has_obv else 'NO_OBV')
    groups[lbl].append((doc_id, tid, denom, year, desc, status))

for lbl, docs in sorted(groups.items()):
    print(f'\n[{lbl}] ({len(docs)} docs)')
    for doc_id, tid, denom, year, desc, status in docs[:8]:
        print(f'  {status:8} {tid:12} {denom:5} {year:10} {doc_id[:8]}  {desc}')
    if len(docs) > 8:
        print(f'  ... and {len(docs)-8} more')
