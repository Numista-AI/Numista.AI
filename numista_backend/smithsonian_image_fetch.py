"""
smithsonian_image_fetch.py
Queries the Smithsonian Open Access API (NMAH unit — National Numismatic Collection)
for each gap item, extracts CC0 image URLs (obverse + reverse), and uploads to GCS.

API key: free at https://api.data.gov/signup/
Set env var: SMITHSONIAN_API_KEY=your_key
"""
import os, sys, json, csv, time, random, urllib.request, urllib.parse
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore, storage

SMITH_KEY = os.environ.get('SMITHSONIAN_API_KEY', '')
if not SMITH_KEY:
    print('ERROR: Set env var SMITHSONIAN_API_KEY=your_key')
    print('Get a free key at: https://api.data.gov/signup/')
    sys.exit(1)

creds, _ = google.auth.default()
db  = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
gcs = storage.Client(credentials=creds)
bucket = gcs.bucket('numista-uploads-studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('currency')

GCS_BASE = 'users/jseaman1204@gmail.com/currency'
SOURCE   = 'smithsonian_open_access_cc0'
ATTR     = 'CC0 Public Domain. Source: Smithsonian National Numismatic Collection (NMAH), Smithsonian Open Access.'
SMITH_API = 'https://api.si.edu/openaccess/api/v1.0/search'
HEADERS   = {'User-Agent': 'NumistaAI/1.0 (contact eric.seaman@yahoo.com)'}

with open('type_to_docids_map.json', encoding='utf-8') as f:
    TYPE_MAP = json.load(f)

# Build reverse lookup: doc_id → type_id
DOC_TO_TYPE = {did: tid for tid, dids in TYPE_MAP.items() for did in dids}

# ── Load gap CSV ──────────────────────────────────────────────────────────────
gaps = []
with open('currency_gaps_for_grok.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        gaps.append(row)

print(f'Loaded {len(gaps)} gap items\n')

# ── Target categories for Smithsonian search ──────────────────────────────────
# Maps our category names → Smithsonian search terms
SMITHSONIAN_CAT_MAP = {
    'Silver Certificate':       'Silver Certificate',
    'Legal Tender Note':        'Legal Tender Note',
    'Fractional Currency':      'Fractional Currency',
    'Federal Reserve Bank Note':'Federal Reserve Bank Note',
    'Gold Certificate':         'Gold Certificate',
    'Treasury Note':            'Treasury Note',
    'National Bank Note':       'National Bank Note',
    'Federal Reserve Note':     'Federal Reserve Note',
    'Confederate':              'Confederate States',
    'Military Payment Certificate': 'Military Payment Certificate',
}

def smithsonian_search(query, row_limit=3):
    """Search Smithsonian Open Access API."""
    params = {
        'api_key': SMITH_KEY,
        'q': f'unit_code:NMAH AND {query}',
        'rows': row_limit,
    }
    url = SMITH_API + '?' + urllib.parse.urlencode(params)
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read())
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                return None

def extract_image_urls(result):
    """Extract image URLs from a Smithsonian API result item."""
    if not result:
        return {}
    urls = {'obv': None, 'rev': None}
    for row in result.get('response', {}).get('rows', []):
        content = row.get('content', {})
        descriptive = content.get('descriptiveNonRepeating', {})
        online_media = descriptive.get('online_media', {})
        media_list = online_media.get('media', [])

        for media in media_list:
            iiif = media.get('iiif_url')
            media_url = media.get('content', media.get('thumbnail'))
            usage = media.get('usage', {}).get('access', '')
            caption = media.get('caption', '').lower()

            if usage != 'CC0':
                continue  # Skip non-CC0

            # Determine obverse vs reverse from caption/filename
            url = iiif or media_url
            if not url:
                continue

            # Make high-res IIIF URL if available
            if iiif:
                url = iiif.rstrip('/') + '/full/full/0/default.jpg'

            is_rev = any(w in caption for w in ['reverse', 'back', 'verso'])
            is_obv = any(w in caption for w in ['obverse', 'front', 'recto']) or not is_rev

            if is_rev and not urls['rev']:
                urls['rev'] = url
            elif is_obv and not urls['obv']:
                urls['obv'] = url

        if urls['obv'] or urls['rev']:
            break  # Got what we need from first matching result

    return urls

def download(url):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
                if len(data) > 10000:   # Must be a real image
                    return data
        except Exception:
            pass
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

# ── Main loop ─────────────────────────────────────────────────────────────────
stats = {'searched': 0, 'found': 0, 'uploaded': 0, 'skipped': 0, 'no_cc0': 0}
results_log = []

for gap in gaps:
    cat    = gap.get('category', gap.get('cat', ''))
    doc_id = gap.get('doc_id', '')
    denom  = gap.get('denom', gap.get('Denomination', ''))
    year   = gap.get('year', gap.get('Year', ''))
    desc   = gap.get('desc', gap.get('Description', ''))[:60]
    status = gap.get('status', '')

    smith_cat = SMITHSONIAN_CAT_MAP.get(cat)
    if not smith_cat:
        continue  # Skip categories Smithsonian won't have

    # Build search query: category + denomination + year
    query_parts = [smith_cat]
    if denom:
        query_parts.append(denom)
    if year and year not in ('', 'nan', 'None'):
        query_parts.append(str(year)[:4])

    query = ' '.join(query_parts)
    stats['searched'] += 1

    result = smithsonian_search(query)
    time.sleep(0.2)  # Rate limiting

    if not result:
        continue

    urls = extract_image_urls(result)
    if not (urls.get('obv') or urls.get('rev')):
        stats['no_cc0'] += 1
        continue

    stats['found'] += 1
    print(f'\n  [{cat}] {denom} {year} — {desc}')
    if urls.get('obv'):
        print(f'    OBV: {urls["obv"][:80]}')
    if urls.get('rev'):
        print(f'    REV: {urls["rev"][:80]}')

    # Download and upload only the side(s) this doc is missing
    doc_data = col.document(doc_id).get().to_dict() or {}
    sides_needed = []
    if status in ('BLANK', 'NO_OBV') and not doc_data.get('image_url_obverse') and urls.get('obv'):
        sides_needed.append(('obv', urls['obv']))
    if status in ('BLANK', 'NO_REV') and not doc_data.get('image_url_reverse') and urls.get('rev'):
        sides_needed.append(('rev', urls['rev']))

    updates = {}
    for side, url in sides_needed:
        data = download(url)
        if not data:
            continue
        gcs_side = 'obverse' if side == 'obv' else 'reverse'
        gcs_url  = upload_gcs(data, doc_id, gcs_side)
        updates[f'image_url_{gcs_side}'] = gcs_url
        updates[f'image_source_{gcs_side}'] = SOURCE
        updates['image_attribution'] = ATTR
        stats['uploaded'] += 1
        print(f'    ✅ Uploaded {gcs_side}')

    if updates:
        col.document(doc_id).update(updates)
    results_log.append({'doc_id': doc_id, 'cat': cat, 'query': query, 'urls': urls})

print(f'\n=== SMITHSONIAN PASS COMPLETE ===')
print(f'Searched: {stats["searched"]} | Found CC0: {stats["found"]} | Uploaded: {stats["uploaded"]}')
print(f'No CC0 result: {stats["no_cc0"]}')

# Save what we found for review
with open('smithsonian_results.json', 'w', encoding='utf-8') as f:
    json.dump(results_log, f, indent=2)
print(f'\nResults saved to smithsonian_results.json')
