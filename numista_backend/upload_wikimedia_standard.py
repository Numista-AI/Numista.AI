"""
upload_wikimedia_standard.py
Downloads Wikimedia Commons images for standard US currency types and
uploads to GCS, applying each image to all matching Firestore doc_ids.

Strategy:
- Confirmed URLs (from agent research) are hardcoded below
- Unresolved filenames are resolved via Wikimedia API
- One download per unique source URL; applied to all matching type_ids
- One GCS upload per doc_id (for individual override capability later)
"""
import os, sys, json, urllib.request, urllib.parse, io, time
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import google.auth
from google.cloud import firestore, storage

creds, _ = google.auth.default()
db  = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
gcs = storage.Client(credentials=creds)
bucket = gcs.bucket('numista-uploads-studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('currency')

HEADERS = {'User-Agent': 'NumistaAI/1.0 (educational numismatic archive; contact eric.seaman@yahoo.com)'}
WIKI_API = 'https://commons.wikimedia.org/w/api.php'
GCS_BASE  = 'users/jseaman1204@gmail.com/currency'
SOURCE    = 'wikimedia_commons_public_domain'
ATTR      = 'Public Domain. Source: Wikimedia Commons / National Numismatic Collection, Smithsonian Institution.'

# ── Load the doc_id mapping ──────────────────────────────────────────────────
with open('type_to_docids_map.json', encoding='utf-8') as f:
    TYPE_MAP = json.load(f)  # { "TYPE_001": ["doc-id-1", ...], ... }

# ── Known confirmed URLs ─────────────────────────────────────────────────────
# Format: TYPE_ID -> {'obv': url_or_None, 'rev': url_or_None, 'file_obv': filename_or_None, 'file_rev': filename_or_None}
# 'obv'/'rev' = direct URL (confirmed ✅)
# 'file_obv'/'file_rev' = Wikimedia filename needing API resolution (🔶/🔍)

W = 'https://upload.wikimedia.org/wikipedia/commons/'

PLAN = {
    # ── SILVER CERTIFICATES ───────────────────────────────────────────────
    'TYPE_137': {'obv': W+'a/a1/US-%241-SC-1923-Fr.237.jpg'},
    'TYPE_138': {'file_obv': 'US-$10-SC-1934-Fr.1701.jpg'},  # use 1934 as rep
    'TYPE_139': {'file_obv': 'US-$10-SC-1934-Fr.1701.jpg'},
    'TYPE_140': {'obv': W+'0/06/US-%241-SC-1957-Fr.1619.jpg'},
    'TYPE_141': {'obv': W+'a/a1/US-%241-SC-1923-Fr.237.jpg'},
    'TYPE_142': {'file_obv': 'US-$1-SC-1891-Fr.222.jpg'},
    'TYPE_143': {'obv': W+'e/ec/1896%241obv.jpg', 'rev': W+'6/64/1896%241rev.jpg'},
    'TYPE_144': {'file_obv': 'US-$1-SC-1899-Fr.226.jpg'},
    'TYPE_145': {'obv': W+'a/a1/US-%241-SC-1923-Fr.237.jpg'},
    'TYPE_146': {'obv': W+'e/e2/1928A_XA_block_Funnyback_obverse.jpg'},
    'TYPE_147': {'obv': W+'e/e2/1928A_XA_block_Funnyback_obverse.jpg'},
    'TYPE_148': {'obv': W+'e/e2/1928A_XA_block_Funnyback_obverse.jpg'},
    'TYPE_149': {'obv': W+'e/e2/1928A_XA_block_Funnyback_obverse.jpg'},
    'TYPE_150': {'obv': W+'e/e2/1928A_XA_block_Funnyback_obverse.jpg'},
    'TYPE_151': {'obv': W+'e/e2/1928A_XA_block_Funnyback_obverse.jpg'},
    'TYPE_152': {'obv': W+'0/06/US-%241-SC-1957-Fr.1619.jpg'},
    'TYPE_153': {'obv': W+'0/06/US-%241-SC-1957-Fr.1619.jpg'},
    'TYPE_154': {'obv': W+'0/06/US-%241-SC-1957-Fr.1619.jpg'},
    'TYPE_155': {'obv': W+'0/06/US-%241-SC-1957-Fr.1619.jpg'},
    'TYPE_156': {'obv': W+'0/06/US-%241-SC-1957-Fr.1619.jpg'},
    'TYPE_157': {'obv': W+'0/06/US-%241-SC-1957-Fr.1619.jpg'},
    'TYPE_158': {'obv': W+'0/06/US-%241-SC-1957-Fr.1619.jpg'},
    'TYPE_159': {'obv': W+'0/06/US-%241-SC-1957-Fr.1619.jpg'},
    'TYPE_160': {'obv': W+'0/06/US-%241-SC-1957-Fr.1619.jpg'},
    'TYPE_161': {'obv': W+'0/06/US-%241-SC-1957-Fr.1619.jpg'},
    'TYPE_162': {'obv': W+'0/06/US-%241-SC-1957-Fr.1619.jpg'},
    'TYPE_163': {'obv': W+'0/06/US-%241-SC-1957-Fr.1619.jpg'},
    'TYPE_164': {'obv': W+'0/06/US-%241-SC-1957-Fr.1619.jpg'},
    'TYPE_165': {'file_obv': 'US-$10-SC-1934-Fr.1701.jpg'},
    'TYPE_166': {'file_obv': 'US-$10-SC-1934-Fr.1701.jpg'},
    'TYPE_167': {'file_obv': 'US-$10-SC-1934-Fr.1701.jpg'},
    'TYPE_168': {'file_obv': 'US-$10-SC-1934-Fr.1701.jpg'},
    'TYPE_169': {'file_obv': 'US-$10-SC-1934-Fr.1701.jpg'},
    'TYPE_170': {'file_obv': 'US-$10-SC-1934-Fr.1701.jpg'},
    'TYPE_171': {'obv': W+'5/5a/1896%242obv.jpg'},
    'TYPE_172': {'file_obv': 'US-$2-SC-1899-Fr.252.jpg'},
    'TYPE_173': {'file_obv': 'US-$5-SC-1899-Fr.280.jpg'},
    'TYPE_174': {'file_obv': 'US-$5-SC-1934-Fr.1650.jpg'},
    'TYPE_175': {'file_obv': 'US-$5-SC-1934-Fr.1650.jpg'},
    'TYPE_176': {'file_obv': 'US-$5-SC-1934-Fr.1650.jpg'},
    'TYPE_177': {'file_obv': 'US-$5-SC-1934-Fr.1650.jpg'},
    'TYPE_178': {'file_obv': 'US-$5-SC-1934-Fr.1650.jpg'},
    'TYPE_179': {'file_obv': 'US-$5-SC-1934-Fr.1650.jpg'},
    'TYPE_180': {'file_obv': 'US-$5-SC-1934-Fr.1650.jpg'},
    'TYPE_181': {'file_obv': 'US-$5-SC-1934-Fr.1650.jpg'},
    # ── FEDERAL RESERVE BANK NOTES ────────────────────────────────────────
    'TYPE_005': {'obv': W+'a/a4/US-%241-FRBN-1918-Fr.713.jpg'},
    'TYPE_006': {'obv': W+'a/a4/US-%241-FRBN-1918-Fr.713.jpg'},
    'TYPE_007': {'obv': W+'c/c0/US-%2410-FRBN-1929-Fr.1860-B.jpg'},
    'TYPE_008': {'file_obv': 'US $2 1918 Federal Reserve Bank Note.jpg'},
    'TYPE_009': {'obv': W+'a/af/US-%2420-FRBN-1929-Fr.1870-D.jpg'},
    'TYPE_010': {'file_obv': 'US-$5-FRBN-1929-Fr.1850-B.jpg'},
    # ── FEDERAL RESERVE NOTES ─────────────────────────────────────────────
    'TYPE_011': {'obv': W+'5/53/US-%2410-FRN-1914-Fr.898a.jpg'},
    'TYPE_012': {'obv': W+'3/31/1917_%242_United_States_Note_Front_2.png'},
    'TYPE_013': {'obv': W+'3/31/1917_%242_United_States_Note_Front_2.png'},
    'TYPE_014': {'obv': W+'0/06/US-%241-SC-1957-Fr.1619.jpg'},
    'TYPE_015': {'obv': W+'a/a4/US-%241-FRBN-1918-Fr.713.jpg'},
    'TYPE_016': {'file_obv': 'US-$1-FRN-1963-Fr.1900.jpg'},
    'TYPE_017': {'file_obv': 'US-$1-FRN-1963-Fr.1900.jpg'},
    'TYPE_018': {'file_obv': 'US-$1-FRN-1963-Fr.1900.jpg'},
    'TYPE_019': {'file_obv': 'US-$1-FRN-1963-Fr.1900.jpg'},
    'TYPE_020': {'file_obv': 'US-$1-FRN-1963-Fr.1900.jpg'},
    'TYPE_021': {'file_obv': 'US-$1-FRN-1969-Fr.1903.jpg'},
    'TYPE_022': {'file_obv': 'US-$1-FRN-1969-Fr.1903.jpg'},
    'TYPE_023': {'file_obv': 'US-$1-FRN-1969-Fr.1903.jpg'},
    'TYPE_024': {'file_obv': 'US-$1-FRN-1969-Fr.1903.jpg'},
    'TYPE_025': {'file_obv': 'US-$1-FRN-1969-Fr.1903.jpg'},
    'TYPE_026': {'file_obv': 'US-$1-FRN-1974-Fr.1908.jpg'},
    'TYPE_027': {'file_obv': 'US-$1-FRN-1977-Fr.1909.jpg'},
    'TYPE_028': {'file_obv': 'US-$1-FRN-1988A-Fr.1915.jpg'},
    'TYPE_029': {'file_obv': 'US-$1-FRN-1993-Fr.1918.jpg'},
    'TYPE_030': {'file_obv': 'US-$1-FRN-1995-Fr.1921.jpg'},
    'TYPE_031': {'file_obv': 'US-$1-FRN-1999-Fr.1924.jpg'},
    'TYPE_032': {'file_obv': 'US-$1-FRN-2001-Fr.1926.jpg'},
    'TYPE_033': {'file_obv': 'US-$1-FRN-2003-Fr.1928.jpg'},
    'TYPE_034': {'file_obv': 'US-$1-FRN-2003A-Fr.1929.jpg'},
    'TYPE_035': {'file_obv': 'US-$1-FRN-2006-Fr.1933.jpg'},
    'TYPE_036': {'file_obv': 'US-$1-FRN-2009-Fr.1934.jpg'},
    'TYPE_037': {'file_obv': 'US-$1-FRN-2013-Fr.3000.jpg'},
    'TYPE_038': {'file_obv': 'US-$1-FRN-2017A-Fr.3004.jpg'},
    'TYPE_039': {'obv': W+'5/53/US-%2410-FRN-1914-Fr.898a.jpg'},
    'TYPE_040': {'file_obv': 'US-$10-FRN-1934-Fr.2003.jpg'},
    'TYPE_041': {'file_obv': 'US-$10-FRN-1934A-Fr.2004.jpg'},
    'TYPE_042': {'file_obv': 'US-$10-FRN-1934C-Fr.2006.jpg'},
    'TYPE_043': {'file_obv': 'US-$10-FRN-1950C-Fr.2013.jpg'},
    'TYPE_044': {'file_obv': 'US-$10-FRN-1999-Fr.2034.jpg'},
    'TYPE_045': {'obv': W+'4/4b/US-%24100-FRN-1914-Fr-1074a.jpg'},
    'TYPE_046': {'file_obv': 'US-$100-FRN-1934-Fr.2152.jpg'},
    'TYPE_047': {'obv': W+'4/4b/US-%24100-FRN-1914-Fr-1074a.jpg'},  # $14 typo -> treat as $100 1914
    'TYPE_048': {'file_obv': 'Two dollars (Obverse).jpg', 'file_rev': 'Two dollars (Reverse).jpg'},
    'TYPE_049': {'file_obv': 'US-$2-FRN-1976-Fr.1935.jpg'},
    'TYPE_050': {'file_obv': 'US-$2-FRN-1995-Fr.1937.jpg'},
    'TYPE_051': {'file_obv': 'US-$2-FRN-1995-Fr.1937.jpg'},
    'TYPE_052': {'file_obv': 'US-$2-FRN-2003-Fr.1938.jpg'},
    'TYPE_053': {'file_obv': 'US-$2-FRN-2003A-Fr.1939.jpg'},
    'TYPE_054': {'file_obv': 'US-$2-FRN-2013-Fr.1941.jpg'},
    'TYPE_055': {'rev': W+'2/20/Series_1914_Twenty_Dollar_Note_Reverse.jpg', 'file_obv': 'US-$20-FRN-1914-Fr.960a.jpg'},
    'TYPE_056': {'file_obv': 'US-$20-FRN-1934-Hawaii.jpg'},
    'TYPE_057': {'file_obv': 'US-$20-FRN-1934A-Fr.2305.jpg'},
    'TYPE_058': {'file_obv': 'US-$20-FRN-1985-Fr.2077.jpg'},
    'TYPE_059': {'obv': W+'9/9b/5_Dollars%2C_United_States%2C_series_1914_-_National_Museum_of_American_History_-_DSC00318.jpg'},
    'TYPE_060': {'obv': W+'9/9b/5_Dollars%2C_United_States%2C_series_1914_-_National_Museum_of_American_History_-_DSC00318.jpg'},
    'TYPE_061': {'obv': W+'9/9b/5_Dollars%2C_United_States%2C_series_1914_-_National_Museum_of_American_History_-_DSC00318.jpg'},
    'TYPE_062': {'file_obv': 'US-$5-FRN-1928A-Fr.1951.jpg'},
    'TYPE_063': {'file_obv': 'US-$5-FRN-1934A-Hawaii.jpg'},
    'TYPE_064': {'file_obv': 'US-$5-FRN-1999-Fr.1984.jpg'},
    'TYPE_065': {'file_obv': 'US-$5-FRN-2001-Fr.1987.jpg'},
    'TYPE_066': {'file_obv': 'US-$5-FRN-2003-Fr.1988.jpg'},
    'TYPE_067': {'file_obv': 'US-$5-FRN-2013-Fr.2132.jpg'},
    'TYPE_068': {'obv': W+'a/a4/US-%2450-FRN-1914-Fr-1019a.jpg'},
    'TYPE_069': {'file_obv': 'US-$50-FRN-1934-Fr.2102.jpg'},
    'TYPE_070': {'file_obv': 'US-$500-FRN-1934-Fr.2201.jpg'},
    # ── LEGAL TENDER NOTES ────────────────────────────────────────────────
    'TYPE_096': {'file_obv': 'US-$5-LT-1928C-Fr.1528.jpg'},
    'TYPE_097': {'file_obv': 'US-$1-LT-1917-Fr.36.jpg'},
    'TYPE_098': {'file_obv': 'US-$1-LT-1923-Fr.40.jpg'},
    'TYPE_099': {'file_obv': 'US-$1-LT-1928-Fr.1500.jpg'},
    'TYPE_100': {'file_obv': 'US-$10-LT-1880-Fr.106.jpg'},
    'TYPE_101': {'obv': W+'d/d4/US-%2410-LT-1901-Fr.114.jpg'},
    'TYPE_102': {'file_obv': 'US-$100-LT-1966-Fr.1550.jpg'},
    'TYPE_103': {'obv': W+'5/5e/US-%242-LT-1917-Fr-58.jpg'},
    'TYPE_104': {'file_obv': 'US-$2-LT-1928C-Fr.1504.jpg'},
    'TYPE_105': {'file_obv': 'US-$2-LT-1928D-Fr.1505.jpg'},
    'TYPE_106': {'file_obv': 'US-$2-LT-1928E-Fr.1506.jpg'},
    'TYPE_107': {'file_obv': 'US-$2-LT-1928F-Fr.1507.jpg'},
    'TYPE_108': {'file_obv': 'US-$2-LT-1928G-Fr.1508.jpg'},
    'TYPE_109': {'file_obv': 'US-$2-LT-1953-Fr.1509.jpg'},
    'TYPE_110': {'file_obv': 'US-$2-LT-1953A-Fr.1510.jpg'},
    'TYPE_111': {'file_obv': 'US-$2-LT-1953B-Fr.1511.jpg'},
    'TYPE_112': {'file_obv': 'US-$2-LT-1953C-Fr.1512.jpg'},
    'TYPE_113': {'file_obv': 'US-$2-LT-1963-Fr.1513.jpg'},
    'TYPE_114': {'file_obv': 'US-$2-LT-1963A-Fr.1514.jpg'},
    'TYPE_115': {'file_obv': 'US-$5-LT-1907-Fr.91.jpg'},
    'TYPE_116': {'file_obv': 'US-$5-LT-1907-Fr.91.jpg'},
    'TYPE_117': {'file_obv': 'US-$5-LT-1928-Fr.1525.jpg'},
    'TYPE_118': {'file_obv': 'US-$5-LT-1928E-Fr.1530.jpg'},
    'TYPE_119': {'file_obv': 'US-$5-LT-1928F-Fr.1531.jpg'},
    'TYPE_120': {'file_obv': 'US-$5-LT-1953-Fr.1532.jpg'},
    'TYPE_121': {'file_obv': 'US-$5-LT-1953B-Fr.1534.jpg'},
    'TYPE_122': {'file_obv': 'US-$5-LT-1953A-Fr.1533.jpg'},
    'TYPE_123': {'file_obv': 'US-$5-LT-1953C-Fr.1535.jpg'},
    'TYPE_124': {'file_obv': 'US-$5-LT-1963-Fr.1536.jpg'},
    # ── FRACTIONAL CURRENCY ───────────────────────────────────────────────
    'TYPE_071': {'obv': W+'e/e2/US-Fractional_%281st_Issue%29-%240.05-Fr.1231.jpg'},
    'TYPE_072': {'file_obv': 'US-Fractional (1st Issue)-$0.10-Fr.1242.jpg'},
    'TYPE_073': {'file_obv': 'US-Fractional (1st Issue)-$0.10-Fr.1242.jpg'},
    'TYPE_074': {'file_obv': 'US-Fractional (3rd Issue)-$0.10-Fr.1253.jpg'},
    'TYPE_075': {'file_obv': 'US-Fractional (3rd Issue)-$0.10-Fr.1253.jpg'},
    'TYPE_076': {'file_obv': 'US-Fractional (5th Issue)-$0.10-Fr.1264.jpg'},
    'TYPE_077': {'file_obv': 'US-Fractional (5th Issue)-$0.10-Fr.1264.jpg'},
    'TYPE_078': {'file_obv': 'US-Fractional (3rd Issue)-$0.15-Fr.1274-SP.jpg'},
    'TYPE_079': {'file_obv': 'US-Fractional (3rd Issue)-$0.15-Fr.1274-SP.jpg'},
    'TYPE_080': {'file_obv': 'US-Fractional (3rd Issue)-$0.02-Fr.1232.jpg'},
    'TYPE_081': {'file_obv': 'US-Fractional (1st Issue)-$0.25-Fr.1280.jpg'},
    'TYPE_082': {'file_obv': 'US-Fractional (1st Issue)-$0.25-Fr.1280.jpg'},
    'TYPE_083': {'file_obv': 'US-Fractional (5th Issue)-$0.25-Fr.1308.jpg'},
    'TYPE_084': {'obv': W+'e/e2/US-Fractional_%281st_Issue%29-%240.05-Fr.1231.jpg'},
    'TYPE_085': {'obv': W+'e/e2/US-Fractional_%281st_Issue%29-%240.05-Fr.1231.jpg'},
    'TYPE_086': {'file_obv': 'US-Fractional (1st Issue)-$0.50-Fr.1312.jpg'},
    'TYPE_087': {'file_obv': 'US-Fractional (3rd Issue)-$0.50-Fr.1355.jpg'},
    'TYPE_088': {'file_obv': 'US-Fractional (3rd Issue)-$0.50-Fr.1355.jpg'},
    # ── GOLD CERTIFICATES ─────────────────────────────────────────────────
    'TYPE_089': {'file_obv': 'US $10 1907 Gold Certificate.jpg'},
    'TYPE_090': {'file_obv': 'US-$10-GC-1922-Fr.1173.jpg'},
    'TYPE_091': {'obv': W+'9/93/1928_United_States_ten_dollar_gold_certificate_PMG_graded_55_EPQ.jpg',
                 'rev': W+'7/75/1928_United_States_ten_dollar_gold_certificate_PMG_graded_55_EPQ_rear.jpg'},
    'TYPE_092': {'file_obv': 'US $20 gold certificate 1906.jpg'},
    'TYPE_093': {'file_obv': 'US-$20-GC-1922-Fr.1187.jpg'},
    'TYPE_094': {'file_obv': 'US-$20-GC-1928-Fr-2402.jpg'},
    'TYPE_095': {'file_obv': 'US-$50-GC-1882-Fr.1191.jpg'},  # rare; may fall back to representative
}

# ── Helpers ──────────────────────────────────────────────────────────────────
url_cache = {}   # source_url -> bytes
resolved  = {}   # filename -> url (from API)

def resolve_wiki_filename(filename):
    """Resolve a Wikimedia Commons filename to a direct upload URL via API."""
    if filename in resolved:
        return resolved[filename]
    api_url = (WIKI_API + '?action=query&titles=File:'
               + urllib.parse.quote(filename, safe='')
               + '&prop=imageinfo&iiprop=url&format=json')
    try:
        req = urllib.request.Request(api_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        pages = data.get('query', {}).get('pages', {})
        for page in pages.values():
            ii = page.get('imageinfo', [])
            if ii:
                url = ii[0]['url']
                resolved[filename] = url
                return url
        resolved[filename] = None
        return None
    except Exception as e:
        print(f'    API error for {filename}: {e}')
        resolved[filename] = None
        return None

def download_url(url):
    if url in url_cache:
        return url_cache[url]
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        url_cache[url] = data
        return data
    except Exception as e:
        print(f'    Download error {url[-50:]}: {e}')
        return None

def upload_to_gcs(data, doc_id, side, ctype='image/jpeg'):
    path = f'{GCS_BASE}/{doc_id}/{side}.jpg'
    blob = bucket.blob(path)
    blob.upload_from_string(data, content_type=ctype)
    return f'https://storage.googleapis.com/{bucket.name}/{path}'

# ── Main loop ────────────────────────────────────────────────────────────────
stats = {'uploaded': 0, 'skipped_no_url': 0, 'skipped_no_docs': 0, 'errors': 0}

for type_id, spec in PLAN.items():
    doc_ids = TYPE_MAP.get(type_id, [])
    if not doc_ids:
        stats['skipped_no_docs'] += 1
        continue

    # Resolve URLs for both sides
    urls = {}
    for side in ['obv', 'rev']:
        direct_key  = side
        file_key    = 'file_' + side

        if direct_key in spec and spec[direct_key]:
            urls[side] = spec[direct_key]
        elif file_key in spec and spec[file_key]:
            resolved_url = resolve_wiki_filename(spec[file_key])
            if resolved_url:
                urls[side] = resolved_url
                time.sleep(0.1)  # be polite to the API
            else:
                urls[side] = None
        else:
            urls[side] = None

    # Download images
    images = {}
    for side, url in urls.items():
        if url:
            data = download_url(url)
            if data:
                images[side] = (data, url)

    if not images:
        print(f'{type_id}: no images resolved — skipping')
        stats['skipped_no_url'] += 1
        continue

    # Determine content type
    def ctype_for(url):
        return 'image/png' if url and url.endswith('.png') else 'image/jpeg'

    # Upload to each doc_id
    for doc_id in doc_ids:
        # Check if already has images (don't overwrite)
        doc = col.document(doc_id).get()
        if not doc.exists:
            continue
        existing = doc.to_dict() or {}
        updates = {}
        for side, (data, src_url) in images.items():
            fs_field = 'image_url_' + ('obverse' if side == 'obv' else 'reverse')
            if existing.get(fs_field):
                continue  # already has image, skip
            gcs_side = 'obverse' if side == 'obv' else 'reverse'
            gcs_url = upload_to_gcs(data, doc_id, gcs_side, ctype_for(src_url))
            updates[fs_field] = gcs_url
            updates[f'image_source_{gcs_side}'] = SOURCE
            updates['image_attribution'] = ATTR
            stats['uploaded'] += 1

        if updates:
            col.document(doc_id).update(updates)

    if images:
        sides = list(images.keys())
        print(f'{type_id}: uploaded {sides} to {len(doc_ids)} doc(s)')

print(f'\n✅ Done. Uploaded: {stats["uploaded"]} | No URL: {stats["skipped_no_url"]} | No docs: {stats["skipped_no_docs"]}')
