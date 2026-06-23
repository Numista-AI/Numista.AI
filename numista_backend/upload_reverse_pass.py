"""
upload_reverse_pass.py
Second pass: finds and uploads missing REVERSE images, and fills in
missing obverses for modern FRNs using denomination-representative files.
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

GCS_BASE = 'users/jseaman1204@gmail.com/currency'
SOURCE   = 'wikimedia_commons_public_domain'
ATTR     = 'Public Domain. Source: Wikimedia Commons / Smithsonian National Numismatic Collection.'
HEADERS  = {'User-Agent': 'NumistaAI/1.0 (educational; contact eric.seaman@yahoo.com)'}
WIKI_API = 'https://commons.wikimedia.org/w/api.php'
W        = 'https://upload.wikimedia.org/wikipedia/commons/'

# ── Load type→doc_id map ──────────────────────────────────────────────────────
with open('type_to_docids_map.json', encoding='utf-8') as f:
    TYPE_MAP = json.load(f)
# Invert: doc_id → type_id
DOC_TO_TYPE = {}
for tid, dids in TYPE_MAP.items():
    for did in dids:
        DOC_TO_TYPE[did] = tid

# ── Reverse-image plan by TYPE_ID ────────────────────────────────────────────
# Each entry: type_id -> {'rev_url': confirmed_url} OR {'rev_file': filename_to_resolve}
#             and optionally 'obv_url'/'obv_file' for still-missing obverses

# Representative reverse images (denomination-standard, confirmed or high-confidence)
# $1 small-size reverse (Great Seal / pyramid) — used by both SC 1935-1957 and FRN 1963+
REV_1_SMALL = 'United States one dollar bill, reverse.jpg'
# $2 FRN reverse — Declaration of Independence signing
REV_2_FRN   = 'US-$2-FRN-1976-Fr.1935-back.jpg'
# $5 reverse (Lincoln Memorial) — used by FRN $5 modern
REV_5_FRN   = 'US-$5-FRN-2003-back.jpg'
# $10 reverse (Treasury Building)
REV_10_FRN  = 'US-$10-FRN-1999-back.jpg'
# $20 reverse (White House)
REV_20_FRN  = 'US-$20-FRN-1985-back.jpg'
# $50 reverse (US Capitol)
REV_50_FRN  = 'US-$50-FRN-1934-back.jpg'
# $100 reverse (Independence Hall)
REV_100_FRN = 'US-$100-FRN-1934-back.jpg'
# $1 large size (1918 FRN / 1917 LTN) — Eagle reverse
REV_1_LARGE = 'US-$1-FRBN-1918-Fr.713-back.jpg'
# $2 large size reverse
REV_2_LARGE = 'US-$2-LT-1917-Fr-58-back.jpg'
# $5 SC 1934 reverse
REV_5_SC    = 'US-$5-SC-1934-Fr.1650-back.jpg'
# $10 SC 1934 reverse
REV_10_SC   = 'US-$10-SC-1934-Fr.1701-back.jpg'
# $1 SC 1923 large reverse
REV_1_SC_1923 = 'US-$1-SC-1923-Fr.237-back.jpg'
# $1 Funnyback SC reverse
REV_FUNNYBACK = '1928A XA block Funnyback reverse.jpg'
# $10 1901 Bison reverse (Columbia/Bison scene)
REV_BISON   = 'US-$10-LT-1901-Fr.114-back.jpg'
# $2 LTN reverse
REV_2_LTN   = 'US-$2-LT-1917-Fr-58-back.jpg'
# Gold Certificate $10 1928 — already have both via Heritage for TYPE_091
# $20 FRN 1914 large size obverse (was missing)
OBV_20_1914 = 'US-$20-FRN-1914-Fr.960a.jpg'

REVERSE_PLAN = {
    # ── Silver Certificates ───────────────────────────────────────────────
    # $1 large size 1923
    'TYPE_137': {'rev_file': REV_1_SC_1923},
    'TYPE_141': {'rev_file': REV_1_SC_1923},
    'TYPE_145': {'rev_file': REV_1_SC_1923},
    # $1 small size 1935-1957 (all share Great Seal reverse)
    'TYPE_140': {'rev_file': REV_1_SMALL},
    'TYPE_152': {'rev_file': REV_1_SMALL},
    'TYPE_153': {'rev_file': REV_1_SMALL},
    'TYPE_154': {'rev_file': REV_1_SMALL},
    'TYPE_155': {'rev_file': REV_1_SMALL},
    'TYPE_156': {'rev_file': REV_1_SMALL},
    'TYPE_157': {'rev_file': REV_1_SMALL},
    'TYPE_158': {'rev_file': REV_1_SMALL},
    'TYPE_159': {'rev_file': REV_1_SMALL},
    'TYPE_160': {'rev_file': REV_1_SMALL},
    'TYPE_161': {'rev_file': REV_1_SMALL},
    'TYPE_162': {'rev_file': REV_1_SMALL},
    'TYPE_163': {'rev_file': REV_1_SMALL},
    'TYPE_164': {'rev_file': REV_1_SMALL},
    'TYPE_146': {'rev_file': REV_FUNNYBACK},
    'TYPE_147': {'rev_file': REV_FUNNYBACK},
    'TYPE_148': {'rev_file': REV_FUNNYBACK},
    'TYPE_149': {'rev_file': REV_FUNNYBACK},
    'TYPE_150': {'rev_file': REV_FUNNYBACK},
    'TYPE_151': {'rev_file': REV_FUNNYBACK},
    # $5 SC 1934 series
    'TYPE_174': {'rev_file': REV_5_SC},
    'TYPE_175': {'rev_file': REV_5_SC},
    'TYPE_176': {'rev_file': REV_5_SC},
    'TYPE_177': {'rev_file': REV_5_SC},
    'TYPE_178': {'rev_file': REV_5_SC},
    'TYPE_179': {'rev_file': REV_5_SC},
    'TYPE_180': {'rev_file': REV_5_SC},
    'TYPE_181': {'rev_file': REV_5_SC},
    # $10 SC 1934 series
    'TYPE_165': {'rev_file': REV_10_SC},
    'TYPE_166': {'rev_file': REV_10_SC},
    'TYPE_167': {'rev_file': REV_10_SC},
    'TYPE_168': {'rev_file': REV_10_SC},
    'TYPE_169': {'rev_file': REV_10_SC},
    'TYPE_170': {'rev_file': REV_10_SC},
    # $1 1896 Educational — already complete (TYPE_143 has both)
    # $2 1896 Educational
    'TYPE_171': {'rev_file': 'US-$2-SC-1896-Educational-back.jpg'},
    # ── Federal Reserve Bank Notes ────────────────────────────────────────
    # $1 1918 FRBN Eagle reverse — use Heritage image already uploaded for TYPE_005
    'TYPE_006': {'rev_file': 'US-$1-FRBN-1918-Fr.713-back.jpg'},
    # $5 1929 FRBN reverse
    'TYPE_010': {'rev_file': 'US-$5-FRBN-1929-Fr.1850-B-back.jpg'},
    # $20 1929 FRBN reverse
    'TYPE_009': {'rev_file': 'US-$20-FRBN-1929-Fr.1870-D-back.jpg'},
    # ── Federal Reserve Notes ─────────────────────────────────────────────
    # Large size 1914
    'TYPE_039': {'rev_file': 'US-$10-FRN-1914-Fr.898a-back.jpg'},
    'TYPE_045': {'rev_file': 'US-$100-FRN-1914-Fr-1074a-back.jpg'},
    'TYPE_055': {'rev_url': W+'2/20/Series_1914_Twenty_Dollar_Note_Reverse.jpg',  # already confirmed
                 'obv_file': OBV_20_1914},
    'TYPE_061': {'rev_file': 'US-$5-FRN-1914-back.jpg'},
    'TYPE_068': {'rev_file': 'US-$50-FRN-1914-Fr-1019a-back.jpg'},
    # Modern small size — denomination-representative reverses
    'TYPE_011': {'rev_file': REV_1_SMALL},   # 1934A FRN — use $1 representative
    'TYPE_012': {'rev_file': REV_1_SMALL},
    'TYPE_013': {'rev_file': REV_1_SMALL},
    'TYPE_014': {'rev_file': REV_1_SMALL},
    'TYPE_015': {'rev_file': REV_1_SMALL},
    # $2 FRN 1976+ reverse
    'TYPE_048': {'rev_url': W+'3/3f/US-$2-FRN-1976-back.jpg'},   # attempt
    # ── Legal Tender Notes ────────────────────────────────────────────────
    'TYPE_101': {'rev_file': REV_BISON},
    'TYPE_103': {'rev_file': REV_2_LTN},
    'TYPE_099': {'rev_file': 'US-$1-LT-1928-Fr.1500-back.jpg'},
    'TYPE_117': {'rev_file': 'US-$5-LT-1928-Fr.1525-back.jpg'},
    # ── Fractional Currency ───────────────────────────────────────────────
    'TYPE_071': {'rev_file': 'US-Fractional-(1st-Issue)-$0.05-Fr.1231-back.jpg'},
    'TYPE_072': {'rev_file': 'US-Fractional-(1st-Issue)-$0.10-Fr.1242-back.jpg'},
    'TYPE_073': {'rev_file': 'US-Fractional-(1st-Issue)-$0.10-Fr.1242-back.jpg'},
    'TYPE_076': {'rev_file': 'US-Fractional-(5th-Issue)-$0.10-Fr.1264-back.jpg'},
    'TYPE_077': {'rev_file': 'US-Fractional-(5th-Issue)-$0.10-Fr.1264-back.jpg'},
    'TYPE_078': {'rev_file': 'US-Fractional-(3rd-Issue)-$0.15-Fr.1274-SP-back.jpg'},
    'TYPE_079': {'rev_file': 'US-Fractional-(3rd-Issue)-$0.15-Fr.1274-SP-back.jpg'},
    'TYPE_081': {'rev_file': 'US-Fractional-(1st-Issue)-$0.25-Fr.1280-back.jpg'},
    'TYPE_082': {'rev_file': 'US-Fractional-(1st-Issue)-$0.25-Fr.1280-back.jpg'},
    'TYPE_083': {'rev_file': 'US-Fractional-(5th-Issue)-$0.25-Fr.1308-back.jpg'},
    'TYPE_084': {'rev_file': 'US-Fractional-(1st-Issue)-$0.05-Fr.1231-back.jpg'},
    'TYPE_085': {'rev_file': 'US-Fractional-(1st-Issue)-$0.05-Fr.1231-back.jpg'},
    'TYPE_086': {'rev_file': 'US-Fractional-(1st-Issue)-$0.50-Fr.1312-back.jpg'},
    'TYPE_087': {'rev_file': 'US-Fractional-(3rd-Issue)-$0.50-Fr.1355-back.jpg'},
    'TYPE_088': {'rev_file': 'US-Fractional-(3rd-Issue)-$0.50-Fr.1355-back.jpg'},
    # ── Gold Certificates ─────────────────────────────────────────────────
    'TYPE_089': {'rev_file': 'US-$10-GC-1907-back.jpg'},
    'TYPE_094': {'rev_file': 'US-$20-GC-1928-back.jpg'},
    # ── Modern FRN — obverses + reverses (all blank) ─────────────────────
    # Try alternate filenames for modern $1 FRN series
    'TYPE_016': {'obv_file': 'US-$1-FRN-1963-Fr.1900.jpg', 'rev_file': REV_1_SMALL},
    'TYPE_017': {'obv_file': 'US-$1-FRN-1969D-Fr.1906.jpg', 'rev_file': REV_1_SMALL},
    'TYPE_018': {'obv_file': 'US-$1-FRN-1963-Fr.1900.jpg', 'rev_file': REV_1_SMALL},
    'TYPE_019': {'obv_file': 'US-$1-FRN-1963A-Fr.1901.jpg', 'rev_file': REV_1_SMALL},
    'TYPE_020': {'obv_file': 'US-$1-FRN-1963B-Fr.1902.jpg', 'rev_file': REV_1_SMALL},
    'TYPE_021': {'obv_file': 'US-$1-FRN-1969-Fr.1903.jpg', 'rev_file': REV_1_SMALL},
    'TYPE_022': {'obv_file': 'US-$1-FRN-1969A-Fr.1904.jpg', 'rev_file': REV_1_SMALL},
    'TYPE_023': {'obv_file': 'US-$1-FRN-1969B-Fr.1905.jpg', 'rev_file': REV_1_SMALL},
    'TYPE_024': {'obv_file': 'US-$1-FRN-1969C-Fr.1905.jpg', 'rev_file': REV_1_SMALL},
    'TYPE_025': {'obv_file': 'US-$1-FRN-1969D-Fr.1906.jpg', 'rev_file': REV_1_SMALL},
    'TYPE_026': {'obv_file': 'US-$1-FRN-1974-Fr.1908.jpg', 'rev_file': REV_1_SMALL},
    'TYPE_027': {'obv_file': 'US-$1-FRN-1977-Fr.1909.jpg', 'rev_file': REV_1_SMALL},
    'TYPE_028': {'obv_file': 'US-$1-FRN-1988A-Fr.1915.jpg', 'rev_file': REV_1_SMALL},
    'TYPE_029': {'obv_file': 'US-$1-FRN-1993-Fr.1918.jpg', 'rev_file': REV_1_SMALL},
    'TYPE_030': {'obv_file': 'US-$1-FRN-1995-Fr.1921.jpg', 'rev_file': REV_1_SMALL},
    'TYPE_031': {'obv_file': 'US-$1-FRN-1999-Fr.1924.jpg', 'rev_file': REV_1_SMALL},
    'TYPE_032': {'obv_file': 'US-$1-FRN-2001-Fr.1926.jpg', 'rev_file': REV_1_SMALL},
    'TYPE_033': {'obv_file': 'US-$1-FRN-2003-Fr.1928.jpg', 'rev_file': REV_1_SMALL},
    'TYPE_034': {'obv_file': 'US-$1-FRN-2003A-Fr.1929.jpg', 'rev_file': REV_1_SMALL},
    'TYPE_035': {'obv_file': 'US-$1-FRN-2006-Fr.1933.jpg', 'rev_file': REV_1_SMALL},
    'TYPE_036': {'obv_file': 'US-$1-FRN-2009-Fr.1934.jpg', 'rev_file': REV_1_SMALL},
    'TYPE_037': {'obv_file': 'US-$1-FRN-2013-Fr.3000.jpg', 'rev_file': REV_1_SMALL},
    'TYPE_038': {'obv_file': 'US-$1-FRN-2017A-Fr.3004.jpg', 'rev_file': REV_1_SMALL},
    # $2 FRN
    'TYPE_049': {'obv_file': 'US-$2-FRN-1976-Fr.1935.jpg', 'rev_file': REV_2_FRN},
    'TYPE_050': {'obv_file': 'US-$2-FRN-1995-Fr.1937.jpg', 'rev_file': REV_2_FRN},
    'TYPE_051': {'obv_file': 'US-$2-FRN-1995-Fr.1937.jpg', 'rev_file': REV_2_FRN},
    'TYPE_052': {'obv_file': 'US-$2-FRN-2003-Fr.1938.jpg', 'rev_file': REV_2_FRN},
    'TYPE_053': {'obv_file': 'US-$2-FRN-2003A-Fr.1939.jpg', 'rev_file': REV_2_FRN},
    'TYPE_054': {'obv_file': 'US-$2-FRN-2013-Fr.1941.jpg', 'rev_file': REV_2_FRN},
    # $5 FRN
    'TYPE_062': {'obv_file': 'US-$5-FRN-1928A-Fr.1951.jpg', 'rev_file': REV_5_FRN},
    'TYPE_063': {'obv_file': 'US-$5-FRN-1934A-Hawaii.jpg', 'rev_file': REV_5_FRN},
    'TYPE_064': {'obv_file': 'US-$5-FRN-1999-Fr.1984.jpg', 'rev_file': REV_5_FRN},
    'TYPE_065': {'obv_file': 'US-$5-FRN-2001-Fr.1987.jpg', 'rev_file': REV_5_FRN},
    'TYPE_066': {'obv_file': 'US-$5-FRN-2003-Fr.1988.jpg', 'rev_file': REV_5_FRN},
    'TYPE_067': {'obv_file': 'US-$5-FRN-2013-Fr.2132.jpg', 'rev_file': REV_5_FRN},
    # $10 FRN
    'TYPE_040': {'obv_file': 'US-$10-FRN-1934-Fr.2003.jpg', 'rev_file': REV_10_FRN},
    'TYPE_041': {'obv_file': 'US-$10-FRN-1934A-Fr.2004.jpg', 'rev_file': REV_10_FRN},
    'TYPE_042': {'obv_file': 'US-$10-FRN-1934C-Fr.2006.jpg', 'rev_file': REV_10_FRN},
    'TYPE_043': {'obv_file': 'US-$10-FRN-1950C-Fr.2013.jpg', 'rev_file': REV_10_FRN},
    'TYPE_044': {'obv_file': 'US-$10-FRN-1999-Fr.2034.jpg', 'rev_file': REV_10_FRN},
    # $20 FRN
    'TYPE_056': {'obv_file': 'US-$20-FRN-1934A-Hawaii.jpg', 'rev_file': REV_20_FRN},
    'TYPE_057': {'obv_file': 'US-$20-FRN-1934A-Fr.2305.jpg', 'rev_file': REV_20_FRN},
    'TYPE_058': {'obv_file': 'US-$20-FRN-1985-Fr.2077.jpg', 'rev_file': REV_20_FRN},
    # $50 FRN
    'TYPE_069': {'obv_file': 'US-$50-FRN-1934-Fr.2102.jpg', 'rev_file': REV_50_FRN},
    # $100 FRN
    'TYPE_046': {'obv_file': 'US-$100-FRN-1934-Fr.2152.jpg', 'rev_file': REV_100_FRN},
    # $500 FRN
    'TYPE_070': {'obv_file': 'US-$500-FRN-1934-Fr.2201.jpg', 'rev_file': 'US-$500-FRN-1934-back.jpg'},
    # ── Legal Tender — additional ─────────────────────────────────────────
    'TYPE_096': {'obv_file': 'US-$5-LT-1928C-Fr.1528.jpg', 'rev_file': 'US-$5-LT-1928-Fr.1525-back.jpg'},
    'TYPE_097': {'obv_file': 'US-$1-LT-1917-Fr.36.jpg', 'rev_file': 'US-$1-LT-1917-back.jpg'},
    'TYPE_098': {'obv_file': 'US-$1-LT-1923-Fr.40.jpg', 'rev_file': 'US-$1-LT-1923-back.jpg'},
    'TYPE_100': {'obv_file': 'US-$10-LT-1880-Fr.106.jpg', 'rev_file': 'US-$10-LT-1880-back.jpg'},
    'TYPE_102': {'obv_file': 'US-$100-LT-1966-Fr.1550.jpg', 'rev_file': 'US-$100-LT-1966-back.jpg'},
    'TYPE_104': {'obv_file': 'US-$2-LT-1928C-Fr.1504.jpg', 'rev_file': REV_2_LTN},
    'TYPE_105': {'obv_file': 'US-$2-LT-1928D-Fr.1505.jpg', 'rev_file': REV_2_LTN},
    'TYPE_106': {'obv_file': 'US-$2-LT-1928E-Fr.1506.jpg', 'rev_file': REV_2_LTN},
    'TYPE_107': {'obv_file': 'US-$2-LT-1928F-Fr.1507.jpg', 'rev_file': REV_2_LTN},
    'TYPE_108': {'obv_file': 'US-$2-LT-1928G-Fr.1508.jpg', 'rev_file': REV_2_LTN},
    'TYPE_109': {'obv_file': 'US-$2-LT-1953-Fr.1509.jpg', 'rev_file': REV_2_LTN},
    'TYPE_110': {'obv_file': 'US-$2-LT-1953A-Fr.1510.jpg', 'rev_file': REV_2_LTN},
    'TYPE_111': {'obv_file': 'US-$2-LT-1953B-Fr.1511.jpg', 'rev_file': REV_2_LTN},
    'TYPE_112': {'obv_file': 'US-$2-LT-1953C-Fr.1512.jpg', 'rev_file': REV_2_LTN},
    'TYPE_113': {'obv_file': 'US-$2-LT-1963-Fr.1513.jpg', 'rev_file': REV_2_LTN},
    'TYPE_114': {'obv_file': 'US-$2-LT-1963A-Fr.1514.jpg', 'rev_file': REV_2_LTN},
    'TYPE_115': {'obv_file': 'US-$5-LT-1907-Fr.91.jpg', 'rev_file': 'US-$5-LT-1907-back.jpg'},
    'TYPE_116': {'obv_file': 'US-$5-LT-1907-Fr.91.jpg', 'rev_file': 'US-$5-LT-1907-back.jpg'},
    'TYPE_118': {'obv_file': 'US-$5-LT-1928E-Fr.1530.jpg', 'rev_file': 'US-$5-LT-1928-Fr.1525-back.jpg'},
    'TYPE_119': {'obv_file': 'US-$5-LT-1928F-Fr.1531.jpg', 'rev_file': 'US-$5-LT-1928-Fr.1525-back.jpg'},
    'TYPE_120': {'obv_file': 'US-$5-LT-1953-Fr.1532.jpg', 'rev_file': 'US-$5-LT-1953-back.jpg'},
    'TYPE_121': {'obv_file': 'US-$5-LT-1953B-Fr.1534.jpg', 'rev_file': 'US-$5-LT-1953-back.jpg'},
    'TYPE_122': {'obv_file': 'US-$5-LT-1953A-Fr.1533.jpg', 'rev_file': 'US-$5-LT-1953-back.jpg'},
    'TYPE_123': {'obv_file': 'US-$5-LT-1953C-Fr.1535.jpg', 'rev_file': 'US-$5-LT-1953-back.jpg'},
    'TYPE_124': {'obv_file': 'US-$5-LT-1963-Fr.1536.jpg', 'rev_file': 'US-$5-LT-1963-back.jpg'},
    # ── Gold Certificates ─────────────────────────────────────────────────
    'TYPE_090': {'obv_file': 'US-$10-GC-1922-Fr.1173.jpg', 'rev_file': 'US-$10-GC-1922-back.jpg'},
    'TYPE_092': {'obv_file': 'US $20 gold certificate 1906.jpg', 'rev_file': 'US-$20-GC-1906-back.jpg'},
    'TYPE_093': {'obv_file': 'US-$20-GC-1922-Fr.1187.jpg', 'rev_file': 'US-$20-GC-1922-back.jpg'},
    'TYPE_095': {'obv_file': 'US-$50-GC-1882-Fr.1191.jpg', 'rev_file': 'US-$50-GC-1882-back.jpg'},
}

# ── Helpers ───────────────────────────────────────────────────────────────────
url_cache = {}
resolved  = {}

def resolve_wiki(filename):
    if filename in resolved:
        return resolved[filename]
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
                resolved[filename] = ii[0]['url']
                return resolved[filename]
    except Exception as e:
        pass
    resolved[filename] = None
    return None

def download(url):
    if url in url_cache:
        return url_cache[url]
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            url_cache[url] = data
            return data
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt + random.random())
            else:
                url_cache[url] = None
                return None

def upload_gcs(data, doc_id, side, is_png=False):
    ct   = 'image/png' if is_png else 'image/jpeg'
    path = f'{GCS_BASE}/{doc_id}/{side}.jpg'
    for attempt in range(4):
        try:
            bucket.blob(path).upload_from_string(data, content_type=ct)
            return f'https://storage.googleapis.com/{bucket.name}/{path}'
        except Exception as e:
            if attempt < 3:
                wait = 2 ** attempt + random.random()
                print(f'    GCS retry {attempt+1} for {doc_id}/{side} ({e.__class__.__name__}) — waiting {wait:.1f}s')
                time.sleep(wait)
            else:
                raise

# ── Main ──────────────────────────────────────────────────────────────────────
stats = {'resolved': 0, 'not_found': 0, 'uploaded': 0, 'skipped': 0}
not_found = []

for type_id, spec in REVERSE_PLAN.items():
    doc_ids = TYPE_MAP.get(type_id, [])
    if not doc_ids:
        continue

    # Resolve URLs
    urls = {}
    for side in ['obv', 'rev']:
        direct = spec.get(f'{side}_url')
        fname  = spec.get(f'{side}_file')
        if direct:
            urls[side] = direct
        elif fname:
            url = resolve_wiki(fname)
            time.sleep(0.08)
            if url:
                urls[side] = url
            else:
                not_found.append(f'{type_id}/{side}: {fname}')
                stats['not_found'] += 1

    if not urls:
        continue

    # Download
    images = {}
    for side, url in urls.items():
        data = download(url)
        if data:
            images[side] = (data, url.endswith('.png'))
            stats['resolved'] += 1

    if not images:
        continue

    # Upload to each doc (only fill missing fields)
    for doc_id in doc_ids:
        doc_data = col.document(doc_id).get().to_dict() or {}
        updates = {}
        for side, (data, is_png) in images.items():
            fs_field = 'image_url_' + ('obverse' if side == 'obv' else 'reverse')
            if doc_data.get(fs_field):
                stats['skipped'] += 1
                continue
            gcs_url = upload_gcs(data, doc_id, 'obverse' if side == 'obv' else 'reverse', is_png)
            updates[fs_field] = gcs_url
            updates[f'image_source_{"obverse" if side == "obv" else "reverse"}'] = SOURCE
            updates['image_attribution'] = ATTR
            stats['uploaded'] += 1
        if updates:
            col.document(doc_id).update(updates)

    sides_done = list(images.keys())
    print(f'{type_id}: {sides_done} → {len(doc_ids)} doc(s)')

print(f'\n✅ Resolved: {stats["resolved"]} | Uploaded: {stats["uploaded"]} | Skipped (already set): {stats["skipped"]} | Not found: {stats["not_found"]}')
if not_found:
    print(f'\nMissing on Wikimedia ({len(not_found)}):')
    for nf in not_found:
        print(f'  {nf}')
