"""
upload_confirmed_finals.py
Last targeted pass using ONLY confirmed Wikimedia filenames from category crawl.
"""
import os, sys, json, urllib.request, urllib.parse, time, random
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore, storage

creds, _ = google.auth.default()
db  = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
gcs = storage.Client(credentials=creds)
bucket = gcs.bucket('numista-uploads-studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('currency')

GCS_BASE  = 'users/jseaman1204@gmail.com/currency'
SOURCE    = 'wikimedia_commons_public_domain'
ATTR      = 'Public Domain. Source: Wikimedia Commons / Smithsonian National Numismatic Collection.'
HEADERS   = {'User-Agent': 'NumistaAI/1.0 (contact eric.seaman@yahoo.com)'}
WIKI_API  = 'https://commons.wikimedia.org/w/api.php'

with open('type_to_docids_map.json', encoding='utf-8') as f:
    TYPE_MAP = json.load(f)

# ── Plan: ALL confirmed working filenames from crawl ─────────────────────────
# Format: type_id → {side: filename_or_direct_url}
CONFIRMED_PLAN = {
    # FRN 1914 large-size obverses (all confirmed via API)
    'TYPE_039': {'obv': 'US-$10-FRN-1914-Fr-894b.jpg'},   # $10 FRN 1914
    'TYPE_045': {'obv': 'US-$100-FRN-1914-Fr-919a.jpg'},  # $100 FRN 1914 — try 919a
    'TYPE_061': {'obv': 'US-$5-FRN-1914-Fr-875.jpg'},      # $5 FRN 1914
    'TYPE_068': {'obv': 'US-$50-FRN-1914-Fr-1053.jpg'},    # $50 FRN 1914

    # SC $1 1899 reverse — confirmed filename (with parens)
    'TYPE_139': {'rev': '1899 Black eagle one dollar silver certificate (reverse).jpg'},
    'TYPE_194': {'rev': '1899 Black eagle one dollar silver certificate (reverse).jpg'},

    # SC $1 Funnyback reverse — confirmed filename (note: space before A)
    'TYPE_148': {'rev': '1928 A XA block Funnyback reverse.jpg'},
    'TYPE_149': {'rev': '1928 A XA block Funnyback reverse.jpg'},
    'TYPE_150': {'rev': '1928 A XA block Funnyback reverse.jpg'},
    'TYPE_151': {'rev': '1928 A XA block Funnyback reverse.jpg'},

    # SC $1 1928 small-size reverse
    'TYPE_152': {'rev': 'First Small Size Silver Certificate (reverse, 1928).jpg'},
    'TYPE_153': {'rev': 'US $1 1928 Silver Certificate reverse.jpg'},

    # LTN $2 1917 obverse (confirmed)
    'TYPE_097': {'obv': 'US-$1-LT-1917-Fr-36.jpg'},  # try $1 LTN 1917
    'TYPE_103': {'obv': 'US-$2-LT-1917-Fr-58.jpg'},
    'TYPE_104': {'obv': 'US-$2-LT-1917-Fr-58.jpg'},
    'TYPE_105': {'obv': 'US-$2-LT-1917-Fr-58.jpg'},
    'TYPE_106': {'obv': 'US-$2-LT-1917-Fr-58.jpg'},
    'TYPE_107': {'obv': 'US-$2-LT-1917-Fr-58.jpg'},
    'TYPE_108': {'obv': 'US-$2-LT-1917-Fr-58.jpg'},
    'TYPE_109': {'obv': 'US-$2-LT-1917-Fr-58.jpg'},
    'TYPE_110': {'obv': 'US-$2-LT-1917-Fr-58.jpg'},
    'TYPE_111': {'obv': 'US-$2-LT-1917-Fr-58.jpg'},
    'TYPE_112': {'obv': 'US-$2-LT-1917-Fr-58.jpg'},
    'TYPE_113': {'obv': 'US-$2-LT-1917-Fr-58.jpg'},
    'TYPE_114': {'obv': 'US-$2-LT-1917-Fr-58.jpg'},

    # FRN large-size — additional from NNC search
    'TYPE_040': {'obv': 'US-$10-FRN-1914-Fr-894b.jpg'},   # use 1914 as representative large FRN
    'TYPE_041': {'obv': 'US-$10-FRN-1914-Fr-919a.jpg'},
    'TYPE_070': {'obv': 'US-$500-FRN-1934-Fr-2201.jpg'},  # try again with hyphen
    'TYPE_046': {'obv': 'US-$100-FRN-1934-Fr-2152.jpg'},
    'TYPE_069': {'obv': 'US-$50-FRN-1934-Fr-2102.jpg'},
}

# Also try these additional NNC-style filenames
EXTRA_TRIES = {
    # More FRN 1914 patterns
    'TYPE_039': {'obv': ['US-$10-FRN-1914-Fr-894b.jpg', 'US-$10-FRN-1914-Fr-919a.jpg']},
    'TYPE_045': {'obv': ['US-$100-FRN-1914-Fr-1074a.jpg', 'US-$100-FRN-1914-Fr-1074.jpg']},
    'TYPE_061': {'obv': ['US-$5-FRN-1914-Fr-875.jpg', 'US-$5-FRN-1914-Fr-875a.jpg']},
    # SC $1 1935 — try NNC naming
    'TYPE_140': {'rev': ['US-$1-SC-1935-Fr-1608-back.jpg',
                         '1934 Funnyback silver certificate reverse.jpg']},
    'TYPE_141': {'rev': ['US-$1-SC-1935A-Fr-1609-back.jpg',
                         'US $1 1928 Silver Certificate reverse.jpg']},
    'TYPE_145': {'rev': ['US-$1-SC-1923-Fr-237-back.jpg',
                         'US-$1-SC-1923-Fr-241-back.jpg']},
    # GC backs
    'TYPE_089': {'rev': ['US-$10-GC-1922-Fr-1173-back.jpg',
                         'US-$10-GC-1907-Fr-1169-back.jpg']},
    'TYPE_090': {'rev': ['US-$10-GC-1922-Fr-1173-back.jpg']},
    'TYPE_092': {'obv': ['US $20 gold certificate 1906.jpg',
                         'US-$20-GC-1906-Fr-1178.jpg'],
                 'rev': ['US-$20-GC-1906-Fr-1178-back.jpg']},
    'TYPE_093': {'rev': ['US-$20-GC-1922-Fr-1187-back.jpg']},
    'TYPE_094': {'rev': ['US-$20-GC-1928-Fr-2402-back.jpg',
                         'US-$20-GC-1928-back.jpg']},
    'TYPE_095': {'obv': ['US-$50-GC-1882-Fr-1191.jpg',
                         'US-$50-GC-1882-Fr-1191a.jpg']},
}

url_cache = {}

def resolve_wiki(filename):
    if filename in url_cache:
        return url_cache[filename]
    api = (WIKI_API + '?action=query&titles=File:'
           + urllib.parse.quote(filename, safe='')
           + '&prop=imageinfo&iiprop=url&format=json')
    try:
        req = urllib.request.Request(api, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        for page in data.get('query', {}).get('pages', {}).values():
            ii = page.get('imageinfo', [])
            if ii:
                url_cache[filename] = ii[0]['url']
                return ii[0]['url']
    except Exception:
        pass
    url_cache[filename] = None
    return None

def resolve_candidates(candidates):
    if isinstance(candidates, str):
        candidates = [candidates]
    for fname in candidates:
        url = resolve_wiki(fname)
        time.sleep(0.08)
        if url:
            return url, fname
    return None, None

def download(url):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception:
            if attempt < 2:
                time.sleep(2 ** attempt + random.random())
    return None

def upload_gcs(data, doc_id, side):
    path = f'{GCS_BASE}/{doc_id}/{side}.jpg'
    for attempt in range(4):
        try:
            bucket.blob(path).upload_from_string(data, content_type='image/jpeg')
            return f'https://storage.googleapis.com/{bucket.name}/{path}'
        except Exception as e:
            if attempt < 3:
                time.sleep(2 ** attempt + random.random())
            else:
                raise

stats = {'uploaded': 0, 'skipped': 0, 'not_found': 0}
not_found = []

# Merge CONFIRMED_PLAN and EXTRA_TRIES
merged = {}
for tid, spec in CONFIRMED_PLAN.items():
    merged[tid] = {k: [v] if isinstance(v, str) else v for k, v in spec.items()}
for tid, spec in EXTRA_TRIES.items():
    if tid not in merged:
        merged[tid] = {}
    for side, val in spec.items():
        if side not in merged[tid]:
            merged[tid][side] = val if isinstance(val, list) else [val]
        else:
            merged[tid][side] = merged[tid][side] + (val if isinstance(val, list) else [val])

for type_id, spec in merged.items():
    doc_ids = TYPE_MAP.get(type_id, [])
    if not doc_ids:
        continue

    images = {}
    for side, candidates in spec.items():
        url, fname = resolve_candidates(candidates)
        if url:
            data = download(url)
            if data:
                images[side] = (data, fname)
        else:
            not_found.append(f'{type_id}/{side}')
            stats['not_found'] += 1

    if not images:
        continue

    for doc_id in doc_ids:
        doc_data = col.document(doc_id).get().to_dict() or {}
        updates  = {}
        for side, (img_data, fname) in images.items():
            fs_field = 'image_url_' + ('obverse' if side == 'obv' else 'reverse')
            if doc_data.get(fs_field):
                stats['skipped'] += 1
                continue
            gcs_side = 'obverse' if side == 'obv' else 'reverse'
            gcs_url  = upload_gcs(img_data, doc_id, gcs_side)
            updates[fs_field] = gcs_url
            updates[f'image_source_{gcs_side}'] = SOURCE
            updates['image_attribution'] = ATTR
            stats['uploaded'] += 1
        if updates:
            col.document(doc_id).update(updates)

    sides_done = list(images.keys())
    fnames_done = [v[1] for v in images.values()]
    print(f'  {type_id}: {sides_done} ({", ".join(fnames_done[:2])}) → {len(doc_ids)} doc(s)')

print(f'\n✅ Uploaded: {stats["uploaded"]} | Already set: {stats["skipped"]} | Not found: {stats["not_found"]}')
if not_found:
    print(f'\nStill missing: {not_found}')
