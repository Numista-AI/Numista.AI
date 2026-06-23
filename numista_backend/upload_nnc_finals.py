"""
upload_nnc_finals.py — Upload last batch of confirmed NNC filenames found via category crawl.
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

# All confirmed from NNC category file list
PLAN = {
    # $5 FRN 1914 large-size obverse
    'TYPE_061': {'obv': ['US-$5-FRN-1914-Fr-832a.jpg', 'US-$5-FRN-1914-Fr-848.jpg']},
    # $50 FRN 1934 obverse
    'TYPE_069': {'obv': ['US-$50-FRN-1934-Fr.2102-J.jpg', 'US-$50-FRN-1928-Fr-2100-J.jpg']},
    # $100 FRN — use 1928 as representative (no 1934 in NNC)
    'TYPE_046': {'obv': ['US-$100-FRN-1928-Fr.2150-G.jpg', 'US-$100-FRN-1914-Fr-1074a.jpg']},
    # $500 FRN 1934 — use 1928 as close representative
    'TYPE_070': {'obv': ['US-$500-FRN-1928-Fr-2200g.jpg', 'US-$500-FRN-1918-Fr-1132d.jpg']},
    # $20 GC 1906 obverse — Fr.1185 confirmed in NNC list
    'TYPE_092': {'obv': ['US-$20-GC-1906-Fr-1185.jpg', 'US-$20-GC-1905-Fr-1180.jpg',
                          'US $20 1905 Gold Certificate.jpg']},
    # $50 GC 1882 obverse — multiple Fr numbers in NNC list
    'TYPE_095': {'obv': ['US-$50-GC-1882-Fr-1189a.jpg', 'US-$50-GC-1882-Fr-1195.jpg',
                          'US-$50-GC-1922-Fr-1200a.jpg']},
    # $10 GC reverse — PMG graded rear image from NNC
    'TYPE_089': {'rev': ['1928 United States ten dollar gold certificate PMG graded 55 EPQ rear.jpg',
                          'US-$10-GC-1928-Fr-2400.jpg']},
    'TYPE_090': {'rev': ['1928 United States ten dollar gold certificate PMG graded 55 EPQ rear.jpg']},
    # $20 GC 1928 obverse+reverse
    'TYPE_094': {'obv': ['US-$20-GC-1928-Fr-2402.jpg'],
                 'rev': ['1928 United States ten dollar gold certificate PMG graded 55 EPQ rear.jpg']},
    # $1 LTN 1917 — use $10 LT 1923 as best available representative
    'TYPE_097': {'obv': ['US-$10-LT-1923-Fr-123.jpg']},
    # More FRN large-size using actual NNC filenames
    'TYPE_040': {'obv': ['US-$10-FRN-1934-A-Fr.2303.jpg']},     # 1934A as representative for 1934
    'TYPE_058': {'obv': ['US-$20-FRN-1934-A-Fr.2305.jpg']},     # 1934A
    'TYPE_057': {'obv': ['US-$20-FRN-1928-Fr-2050-G.jpg']},     # 1928 large
    'TYPE_063': {'obv': ['US-$5-FRN-1928B-Fr-1952-J.jpg']},     # $5 FRN 1928B for Hawaii rep
    # $10 FRN 1914 alt Friedberg numbers (NNC list confirms these exist with .)
    'TYPE_039': {'obv': ['US-$10-FRN-1914-Fr.898a.jpg', 'US-$10-FRN-1914-Fr.943a.jpg']},
    # $50 FRN 1914 alt — another confirmed NNC file
    'TYPE_068': {'obv': ['US-$50-FRN-1914-Fr-1019a.jpg']},      # Fr-1019a (not 1053)
}

url_cache = {}

def resolve_candidates(candidates):
    for fname in candidates:
        if fname in url_cache:
            if url_cache[fname]:
                return url_cache[fname], fname
            continue
        api = (WIKI_API + '?action=query&titles=File:'
               + urllib.parse.quote(fname, safe='')
               + '&prop=imageinfo&iiprop=url&format=json')
        try:
            req = urllib.request.Request(api, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=12) as r:
                data = json.loads(r.read())
            for page in data.get('query', {}).get('pages', {}).values():
                ii = page.get('imageinfo', [])
                if ii:
                    url_cache[fname] = ii[0]['url']
                    return ii[0]['url'], fname
        except Exception:
            pass
        url_cache[fname] = None
        time.sleep(0.1)
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
        except Exception:
            if attempt < 3:
                time.sleep(2 ** attempt + random.random())
            else:
                raise

stats = {'uploaded': 0, 'skipped': 0, 'not_found': 0}

for type_id, spec in PLAN.items():
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
            stats['not_found'] += 1
            print(f'  miss: {type_id}/{side}')

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

    sides = list(images.keys())
    fnames = [v[1] for v in images.values()]
    print(f'  {type_id}: {sides} ({fnames[0][:50]}) → {len(doc_ids)} doc(s)')

print(f'\n✅ Uploaded: {stats["uploaded"]} | Skipped: {stats["skipped"]} | Not found: {stats["not_found"]}')
