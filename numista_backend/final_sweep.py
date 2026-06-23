"""
final_sweep.py — Comprehensive final image sweep using real TYPE_IDs and corrected
Wikimedia filename conventions (Fr-XXXX with hyphen, not dot).
Targets every remaining partial/blank doc by type with multiple candidate filenames.
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
ATTR_WIKI = 'Public Domain. Source: Wikimedia Commons / Smithsonian National Numismatic Collection.'
HEADERS   = {'User-Agent': 'NumistaAI/1.0 (contact eric.seaman@yahoo.com)'}
WIKI_API  = 'https://commons.wikimedia.org/w/api.php'

with open('type_to_docids_map.json', encoding='utf-8') as f:
    TYPE_MAP = json.load(f)

# ── Comprehensive plan: real TYPE_IDs with corrected filename conventions ──────
# Format: type_id → {'obv': [candidate1, candidate2, ...], 'rev': [...]}
# Candidates tried in order; first successful one wins.
PLAN = {

    # ── $20 FRN 1914 (TYPE_055) — obverse still missing ──────────────────────
    'TYPE_055': {
        'obv': ['US-$20-FRN-1914-Fr-1010.jpg', 'US-$20-FRN-1914-Fr-958a.jpg',
                'US-$20-FRN-1914-Fr-958.jpg',  'US-$20-FRN-1914.jpg'],
    },

    # ── Federal Reserve Bank Notes ─────────────────────────────────────────────
    'TYPE_006': {  # $1 FRBN 1918
        'rev': ['US-$1-FRBN-1918-Fr-713-back.jpg', 'US-$1-FRBN-1918-Fr.713-back.jpg'],
    },
    'TYPE_009': {  # $20 FRBN 1929
        'rev': ['US-$20-FRBN-1929-Fr-1870-D-back.jpg', 'US-$20-FRBN-1929-Fr.1870-D-back.jpg'],
    },
    'TYPE_010': {  # $5 FRBN 1929
        'rev': ['US-$5-FRBN-1929-Fr-1850-B-back.jpg', 'US-$5-FRBN-1929-Fr.1850-B-back.jpg'],
    },

    # ── Federal Reserve Notes (large size / Hawaii / etc.) ────────────────────
    'TYPE_039': {  # $10 FRN 1914
        'rev': ['US-$10-FRN-1914-Fr-898a-back.jpg', 'US-$10-FRN-1914-Fr.898a-back.jpg'],
    },
    'TYPE_040': {  # $10 FRN 1934
        'obv': ['US-$10-FRN-1934-Fr-2003.jpg', 'US-$10-FRN-1934-Fr.2003.jpg'],
        'rev': ['US-$10-FRN-1999-back.jpg'],
    },
    'TYPE_041': {  # $10 FRN 1934A
        'obv': ['US-$10-FRN-1934A-Fr-2004.jpg', 'US-$10-FRN-1934A-Fr.2004.jpg'],
        'rev': ['US-$10-FRN-1999-back.jpg'],
    },
    'TYPE_042': {  # $10 FRN 1934C
        'obv': ['US-$10-FRN-1934C-Fr-2006.jpg', 'US-$10-FRN-1934C-Fr.2006.jpg'],
        'rev': ['US-$10-FRN-1999-back.jpg'],
    },
    'TYPE_043': {  # $10 FRN 1950C
        'obv': ['US-$10-FRN-1950C-Fr-2013.jpg', 'US-$10-FRN-1950C-Fr.2013.jpg'],
        'rev': ['US-$10-FRN-1999-back.jpg'],
    },
    'TYPE_044': {  # $10 FRN 1999
        'obv': ['US-$10-FRN-1999-Fr-2034.jpg', 'US-$10-FRN-1999-Fr.2034.jpg'],
        'rev': ['US-$10-FRN-1999-back.jpg'],
    },
    'TYPE_045': {  # $100 FRN 1914
        'rev': ['US-$100-FRN-1914-Fr-1074a-back.jpg', 'US-$100-FRN-1914-Fr.1074a-back.jpg'],
    },
    'TYPE_046': {  # $100 FRN 1934
        'obv': ['US-$100-FRN-1934-Fr-2152.jpg', 'US-$100-FRN-1934-Fr.2152.jpg'],
        'rev': ['US-$100-FRN-1934-back.jpg'],
    },
    'TYPE_056': {  # $20 FRN 1934A Hawaii
        'obv': ['US-$20-FRN-1934A-Hawaii.jpg'],
        'rev': ['US-$20-FRN-1985-back.jpg'],
    },
    'TYPE_057': {  # $20 FRN 1934A
        'obv': ['US-$20-FRN-1934A-Fr-2305.jpg', 'US-$20-FRN-1934A-Fr.2305.jpg'],
        'rev': ['US-$20-FRN-1985-back.jpg'],
    },
    'TYPE_058': {  # $20 FRN 1985
        'obv': ['US-$20-FRN-1985-Fr-2077.jpg', 'US-$20-FRN-1985-Fr.2077.jpg'],
        'rev': ['US-$20-FRN-1985-back.jpg'],
    },
    'TYPE_061': {  # $5 FRN 1914
        'rev': ['US-$5-FRN-1914-back.jpg'],
    },
    'TYPE_062': {  # $5 FRN 1928A
        'obv': ['US-$5-FRN-1928A-Fr-1951.jpg', 'US-$5-FRN-1928A-Fr.1951.jpg'],
        'rev': ['US-$5-FRN-2003-back.jpg'],
    },
    'TYPE_063': {  # $5 FRN 1934A Hawaii
        'obv': ['US-$5-FRN-1934A-Hawaii.jpg'],
        'rev': ['US-$5-FRN-2003-back.jpg'],
    },
    'TYPE_064': {  # $5 FRN 1999
        'obv': ['US-$5-FRN-1999-Fr-1984.jpg', 'US-$5-FRN-1999-Fr.1984.jpg'],
        'rev': ['US-$5-FRN-2003-back.jpg'],
    },
    'TYPE_065': {  # $5 FRN 2001
        'obv': ['US-$5-FRN-2001-Fr-1987.jpg', 'US-$5-FRN-2001-Fr.1987.jpg'],
        'rev': ['US-$5-FRN-2003-back.jpg'],
    },
    'TYPE_066': {  # $5 FRN 2003
        'obv': ['US-$5-FRN-2003-Fr-1988.jpg', 'US-$5-FRN-2003-Fr.1988.jpg'],
        'rev': ['US-$5-FRN-2003-back.jpg'],
    },
    'TYPE_067': {  # $5 FRN 2013
        'obv': ['US-$5-FRN-2013-Fr-2132.jpg', 'US-$5-FRN-2013-Fr.2132.jpg'],
        'rev': ['US-$5-FRN-2003-back.jpg'],
    },
    'TYPE_068': {  # $50 FRN 1914
        'rev': ['US-$50-FRN-1914-Fr-1019a-back.jpg', 'US-$50-FRN-1914-Fr.1019a-back.jpg'],
    },
    'TYPE_069': {  # $50 FRN 1934
        'obv': ['US-$50-FRN-1934-Fr-2102.jpg', 'US-$50-FRN-1934-Fr.2102.jpg'],
        'rev': ['US-$50-FRN-1934-back.jpg'],
    },
    'TYPE_070': {  # $500 FRN 1934
        'obv': ['US-$500-FRN-1934-Fr-2201.jpg', 'US-$500-FRN-1934-Fr.2201.jpg'],
        'rev': ['US-$500-FRN-1934-back.jpg'],
    },

    # ── Silver Certificates ────────────────────────────────────────────────────
    'TYPE_138': {  # $1 SC 1886
        'obv': ['US-$1-SC-1886-Fr-215.jpg', 'US-$1-SC-1886-Fr.215.jpg',
                'US-$1-SC-1886-Fr-217.jpg', 'US-$1-SC-1886-Fr.219.jpg'],
    },
    'TYPE_139': {  # $1 SC 1899 Eagle
        'obv': ['US-$1-SC-1899-Fr-226.jpg', 'US-$1-SC-1899-Fr-228.jpg'],
    },
    'TYPE_140': {  # $1 SC 1923 large
        'rev': ['US-$1-SC-1923-Fr-237-back.jpg', 'US-$1-SC-1923-Fr.237-back.jpg'],
    },
    'TYPE_141': {  # $1 SC
        'rev': ['US-$1-SC-1923-Fr-237-back.jpg'],
    },
    'TYPE_145': {  # $1 SC 1923 large
        'rev': ['US-$1-SC-1923-Fr-237-back.jpg', 'US-$1-SC-1935-Fr.1607-back.jpg'],
    },
    'TYPE_148': {  # $1 SC Funnyback 1928A
        'rev': ['1928A XA block Funnyback reverse.jpg', 'US-$1-SC-1928A-Fr-1600-back.jpg',
                'US-$1-SC-1928-Funnyback-back.jpg'],
    },
    'TYPE_149': {'rev': ['1928A XA block Funnyback reverse.jpg']},
    'TYPE_150': {'rev': ['1928A XA block Funnyback reverse.jpg']},
    'TYPE_151': {'rev': ['1928A XA block Funnyback reverse.jpg']},
    'TYPE_165': {  # $10 SC 1934
        'rev': ['US-$10-SC-1934-Fr-1701-back.jpg', 'US-$10-SC-1934-Fr.1701-back.jpg'],
    },
    'TYPE_166': {'rev': ['US-$10-SC-1934-Fr-1701-back.jpg']},
    'TYPE_167': {'rev': ['US-$10-SC-1934-Fr-1701-back.jpg']},
    'TYPE_168': {'rev': ['US-$10-SC-1934-Fr-1701-back.jpg']},
    'TYPE_169': {'rev': ['US-$10-SC-1934-Fr-1701-back.jpg']},
    'TYPE_170': {'rev': ['US-$10-SC-1934-Fr-1701-back.jpg']},
    'TYPE_172': {  # $2 SC 1899 large size
        'obv': ['US-$2-SC-1896-Educational.jpg', 'US-$2-SC-1891-Fr-245.jpg',
                'US-$2-SC-1899-Fr-253.jpg'],
        'rev': ['US-$2-SC-1896-Educational-back.jpg'],
    },
    'TYPE_174': {'rev': ['US-$5-SC-1934-Fr-1650-back.jpg', 'US-$5-SC-1934-Fr.1650-back.jpg']},
    'TYPE_175': {'rev': ['US-$5-SC-1934-Fr-1650-back.jpg']},
    'TYPE_176': {'rev': ['US-$5-SC-1934-Fr-1650-back.jpg']},
    'TYPE_177': {'rev': ['US-$5-SC-1934-Fr-1650-back.jpg']},
    'TYPE_178': {'rev': ['US-$5-SC-1934-Fr-1650-back.jpg']},
    'TYPE_179': {'rev': ['US-$5-SC-1934-Fr-1650-back.jpg']},
    'TYPE_180': {'rev': ['US-$5-SC-1934-Fr-1650-back.jpg']},
    'TYPE_181': {'rev': ['US-$5-SC-1934-Fr-1650-back.jpg']},
    'TYPE_171': {  # $2 SC 1896 Educational
        'rev': ['US-$2-SC-1896-Educational-back.jpg'],
    },
    'TYPE_194': {  # $1 SC 1899 Eagle (Unknown-classified)
        'obv': ['US-$1-SC-1899-Fr-226.jpg'],
        'rev': ['US-$1-SC-1899-Fr-226-back.jpg', 'US-$1-SC-1923-Fr-237-back.jpg'],
    },
    'TYPE_195': {  # large size starter set
        'rev': ['US-$1-SC-1923-Fr-237-back.jpg'],
    },

    # ── Legal Tender Notes ────────────────────────────────────────────────────
    'TYPE_097': {  # $1 LTN 1917
        'obv': ['US-$1-LT-1917-Fr-36.jpg',  'US-$1-LT-1917-Fr.36.jpg'],
        'rev': ['US-$1-LT-1917-back.jpg'],
    },
    'TYPE_098': {  # $1 LTN 1923
        'obv': ['US-$1-LT-1923-Fr-40.jpg',  'US-$1-LT-1923-Fr.40.jpg'],
        'rev': ['US-$1-LT-1923-back.jpg'],
    },
    'TYPE_099': {  # $1 LTN 1928
        'rev': ['US-$1-LT-1928-Fr-1500-back.jpg', 'US-$1-LT-1928-Fr.1500-back.jpg'],
    },
    'TYPE_100': {  # $10 LTN 1880
        'obv': ['US-$10-LT-1880-Fr-106.jpg', 'US-$10-LT-1880-Fr.106.jpg'],
        'rev': ['US-$10-LT-1880-back.jpg'],
    },
    'TYPE_101': {  # $10 LTN 1901 Bison
        'rev': ['US-$10-LT-1901-Fr-114-back.jpg', 'US-$10-LT-1901-Fr.114-back.jpg'],
    },
    'TYPE_102': {  # $100 LTN 1966
        'obv': ['US-$100-LT-1966-Fr-1550.jpg', 'US-$100-LT-1966-Fr.1550.jpg'],
        'rev': ['US-$100-LT-1966-back.jpg'],
    },
    'TYPE_103': {  # $2 LTN 1917
        'rev': ['US-$2-LT-1917-Fr-58-back.jpg', 'US-$2-LT-1917-Fr.58-back.jpg'],
    },
    'TYPE_104': {'obv': ['US-$2-LT-1928C-Fr-1504.jpg', 'US-$2-LT-1928C-Fr.1504.jpg'],
                 'rev': ['US-$2-LT-1917-Fr-58-back.jpg']},
    'TYPE_105': {'obv': ['US-$2-LT-1928D-Fr-1505.jpg', 'US-$2-LT-1928D-Fr.1505.jpg'],
                 'rev': ['US-$2-LT-1917-Fr-58-back.jpg']},
    'TYPE_106': {'obv': ['US-$2-LT-1928E-Fr-1506.jpg', 'US-$2-LT-1928E-Fr.1506.jpg'],
                 'rev': ['US-$2-LT-1917-Fr-58-back.jpg']},
    'TYPE_107': {'obv': ['US-$2-LT-1928F-Fr-1507.jpg', 'US-$2-LT-1928F-Fr.1507.jpg'],
                 'rev': ['US-$2-LT-1917-Fr-58-back.jpg']},
    'TYPE_108': {'obv': ['US-$2-LT-1928G-Fr-1508.jpg', 'US-$2-LT-1928G-Fr.1508.jpg'],
                 'rev': ['US-$2-LT-1917-Fr-58-back.jpg']},
    'TYPE_109': {'obv': ['US-$2-LT-1953-Fr-1509.jpg', 'US-$2-LT-1953-Fr.1509.jpg'],
                 'rev': ['US-$2-LT-1917-Fr-58-back.jpg']},
    'TYPE_110': {'obv': ['US-$2-LT-1953A-Fr-1510.jpg', 'US-$2-LT-1953A-Fr.1510.jpg'],
                 'rev': ['US-$2-LT-1917-Fr-58-back.jpg']},
    'TYPE_111': {'obv': ['US-$2-LT-1953B-Fr-1511.jpg', 'US-$2-LT-1953B-Fr.1511.jpg'],
                 'rev': ['US-$2-LT-1917-Fr-58-back.jpg']},
    'TYPE_112': {'obv': ['US-$2-LT-1953C-Fr-1512.jpg', 'US-$2-LT-1953C-Fr.1512.jpg'],
                 'rev': ['US-$2-LT-1917-Fr-58-back.jpg']},
    'TYPE_113': {'obv': ['US-$2-LT-1963-Fr-1513.jpg', 'US-$2-LT-1963-Fr.1513.jpg'],
                 'rev': ['US-$2-LT-1917-Fr-58-back.jpg']},
    'TYPE_114': {'obv': ['US-$2-LT-1963A-Fr-1514.jpg', 'US-$2-LT-1963A-Fr.1514.jpg'],
                 'rev': ['US-$2-LT-1917-Fr-58-back.jpg']},
    'TYPE_115': {'obv': ['US-$5-LT-1907-Fr-91.jpg', 'US-$5-LT-1907-Fr.91.jpg'],
                 'rev': ['US-$5-LT-1907-back.jpg']},
    'TYPE_116': {'obv': ['US-$5-LT-1907-Fr-91.jpg'], 'rev': ['US-$5-LT-1907-back.jpg']},
    'TYPE_117': {'rev': ['US-$5-LT-1928-Fr-1525-back.jpg', 'US-$5-LT-1928-Fr.1525-back.jpg']},
    'TYPE_118': {'obv': ['US-$5-LT-1928E-Fr-1530.jpg', 'US-$5-LT-1928E-Fr.1530.jpg'],
                 'rev': ['US-$5-LT-1928-Fr-1525-back.jpg']},
    'TYPE_119': {'obv': ['US-$5-LT-1928F-Fr-1531.jpg', 'US-$5-LT-1928F-Fr.1531.jpg'],
                 'rev': ['US-$5-LT-1928-Fr-1525-back.jpg']},
    'TYPE_120': {'obv': ['US-$5-LT-1953-Fr-1532.jpg', 'US-$5-LT-1953-Fr.1532.jpg'],
                 'rev': ['US-$5-LT-1953-back.jpg']},
    'TYPE_121': {'obv': ['US-$5-LT-1953B-Fr-1534.jpg', 'US-$5-LT-1953B-Fr.1534.jpg'],
                 'rev': ['US-$5-LT-1953-back.jpg']},
    'TYPE_122': {'obv': ['US-$5-LT-1953A-Fr-1533.jpg', 'US-$5-LT-1953A-Fr.1533.jpg'],
                 'rev': ['US-$5-LT-1953-back.jpg']},
    'TYPE_123': {'obv': ['US-$5-LT-1953C-Fr-1535.jpg', 'US-$5-LT-1953C-Fr.1535.jpg'],
                 'rev': ['US-$5-LT-1953-back.jpg']},
    'TYPE_124': {'obv': ['US-$5-LT-1963-Fr-1536.jpg', 'US-$5-LT-1963-Fr.1536.jpg'],
                 'rev': ['US-$5-LT-1963-back.jpg']},
    'TYPE_217': {'obv': ['US-$5-LT-1880-Fr-88.jpg', 'US-$5-LT-1880-Fr.88.jpg'],
                 'rev': ['US-$5-LT-1907-back.jpg']},
    'TYPE_220': {'rev': ['US-$5-LT-1928-Fr-1525-back.jpg']},  # $5 LTN 1928B misclassified

    # ── Gold Certificates ─────────────────────────────────────────────────────
    'TYPE_089': {  # $10 GC 1907-22 — needs reverse
        'rev': ['US-$10-GC-1907-back.jpg', 'US-$10-GC-1922-Fr-1173-back.jpg'],
    },
    'TYPE_090': {  # $10 GC 1922 — BLANK
        'obv': ['US-$10-GC-1922-Fr-1173.jpg'],
        'rev': ['US-$10-GC-1907-back.jpg', 'US-$10-GC-1922-Fr-1173-back.jpg'],
    },
    'TYPE_092': {  # $20 GC 1906 — BLANK
        'obv': ['US $20 gold certificate 1906.jpg', 'US-$20-GC-1906-Fr-1178.jpg',
                'US-$20-GC-1906-Fr.1178.jpg'],
        'rev': ['US-$20-GC-1906-back.jpg', 'US-$20-GC-1922-Fr-1187-back.jpg'],
    },
    'TYPE_093': {  # $20 GC 1922 — BLANK
        'obv': ['US-$20-GC-1922-Fr-1187.jpg'],
        'rev': ['US-$20-GC-1922-back.jpg', 'US-$20-GC-1906-back.jpg'],
    },
    'TYPE_094': {  # $20 GC 1928 — needs reverse
        'rev': ['US-$20-GC-1928-back.jpg'],
    },
    'TYPE_095': {  # $50 GC 1882 — BLANK
        'obv': ['US-$50-GC-1882-Fr-1191.jpg', 'US-$50-GC-1882-Fr.1191.jpg'],
        'rev': ['US-$50-GC-1882-back.jpg'],
    },

    # ── Fractional Currency ───────────────────────────────────────────────────
    'TYPE_071': {'rev': ['US-Fractional-(1st-Issue)-$0.05-Fr-1231-back.jpg',
                         'US-Fractional-(1st-Issue)-$0.05-Fr.1231-back.jpg']},
    'TYPE_072': {'rev': ['US-Fractional-(1st-Issue)-$0.10-Fr-1242-back.jpg',
                         'US-Fractional-(1st-Issue)-$0.10-Fr.1242-back.jpg']},
    'TYPE_073': {'rev': ['US-Fractional-(1st-Issue)-$0.10-Fr-1242-back.jpg']},
    'TYPE_075': {  # BLANK 10c Fractional
        'obv': ['US-Fractional-(2nd-Issue)-$0.10-Fr-1245.jpg',
                'US-Fractional-(3rd-Issue)-$0.10-Fr-1255.jpg'],
        'rev': ['US-Fractional-(2nd-Issue)-$0.10-Fr-1245-back.jpg'],
    },
    'TYPE_076': {'rev': ['US-Fractional-(5th-Issue)-$0.10-Fr-1264-back.jpg',
                         'US-Fractional-(5th-Issue)-$0.10-Fr.1264-back.jpg']},
    'TYPE_077': {'rev': ['US-Fractional-(5th-Issue)-$0.10-Fr-1264-back.jpg']},
    'TYPE_078': {'rev': ['US-Fractional-(3rd-Issue)-$0.15-Fr-1274-SP-back.jpg',
                         'US-Fractional-(3rd-Issue)-$0.15-Fr.1274-SP-back.jpg']},
    'TYPE_079': {'rev': ['US-Fractional-(3rd-Issue)-$0.15-Fr-1274-SP-back.jpg']},
    'TYPE_081': {'rev': ['US-Fractional-(1st-Issue)-$0.25-Fr-1280-back.jpg',
                         'US-Fractional-(1st-Issue)-$0.25-Fr.1280-back.jpg']},
    'TYPE_082': {'rev': ['US-Fractional-(1st-Issue)-$0.25-Fr-1280-back.jpg']},
    'TYPE_083': {'rev': ['US-Fractional-(5th-Issue)-$0.25-Fr-1308-back.jpg',
                         'US-Fractional-(5th-Issue)-$0.25-Fr.1308-back.jpg']},
    'TYPE_084': {'rev': ['US-Fractional-(1st-Issue)-$0.05-Fr-1231-back.jpg']},
    'TYPE_085': {'rev': ['US-Fractional-(1st-Issue)-$0.05-Fr-1231-back.jpg']},
    'TYPE_086': {'rev': ['US-Fractional-(1st-Issue)-$0.50-Fr-1312-back.jpg',
                         'US-Fractional-(1st-Issue)-$0.50-Fr.1312-back.jpg']},
    'TYPE_087': {'rev': ['US-Fractional-(3rd-Issue)-$0.50-Fr-1355-back.jpg',
                         'US-Fractional-(3rd-Issue)-$0.50-Fr.1355-back.jpg']},
    'TYPE_088': {'rev': ['US-Fractional-(3rd-Issue)-$0.50-Fr-1355-back.jpg']},

    # ── Treasury Notes ────────────────────────────────────────────────────────
    'TYPE_182': {  # $2 Treasury Note 1891
        'obv': ['US-$1-TN-1890-Fr-347.jpg'],  # representative
        'rev': ['US-$1-TN-1890-Fr-347-back.jpg', 'US-$2-TN-1890-Fr-353-back.jpg'],
    },
    'TYPE_183': {  # $1 Treasury Note 1891
        'obv': ['US-$1-TN-1890-Fr-347.jpg'],
        'rev': ['US-$1-TN-1890-Fr-347-back.jpg'],
    },

    # ── MPC remaining (correct type IDs) ─────────────────────────────────────
    'TYPE_125': {  # MPC 1969-70 (Series 681)
        'obv': ['1 Dollar - United States of America Military Payment Certificate (Series 681, 1969-1970) 01.jpg',
                'Military_Payment_Certificate_series_681_one_dollar_obverse.jpg'],
        'rev': ['1 Dollar - United States of America Military Payment Certificate (Series 681, 1969-1970) 02.jpg'],
    },
    'TYPE_126': {  # MPC $5 1968-69 (Series 661 or 681)
        'obv': ['5 Dollars - United States of America Military Payment Certificate (Series 681, 1969-1970) 01.jpg',
                '5 Dollars - United States of America Military Payment Certificate (Series 661, 1968-1969) 01.jpg'],
        'rev': ['5 Dollars - United States of America Military Payment Certificate (Series 681, 1969-1970) 02.jpg'],
    },

    # ── Confederate (missing reverses) ────────────────────────────────────────
    'TYPE_212': {  # $20 Confederate 1864
        'rev': ['US-$20-Confederate-1864-T-67-back.jpg', 'Confederate-$20-1864-back.jpg',
                'CSA-$20-1864-reverse.jpg'],
    },
    'TYPE_188': {  # $50 Confederate 1864
        'rev': ['US-$50-Confederate-1864-T-66-back.jpg', 'Confederate-$50-1864-back.jpg'],
    },

    # ── National Bank Notes — generic representative images ───────────────────
    'TYPE_127': {  # NBN Type 1 small size 1929
        'obv': ['US-$5-NBN-1929-Fr-1800.jpg', 'US-$5-NBN-1929-Fr.1800.jpg',
                'US National Bank Note $5 1929.jpg'],
        'rev': ['US-$5-NBN-1929-Fr-1800-back.jpg'],
    },
    'TYPE_128': {  # NBN large size 1902
        'obv': ['US-$10-NBN-1902-Fr-624.jpg', 'US-$10-NBN-1902-Fr.624.jpg',
                'US National Bank Note $10 1902.jpg'],
        'rev': ['US-$10-NBN-1902-Fr-624-back.jpg'],
    },
    'TYPE_131': {  # NBN $20 1929 T1
        'obv': ['US-$20-NBN-1929-Fr-1802.jpg', 'US-$20-NBN-1902-Fr-642.jpg'],
        'rev': ['US-$20-NBN-1929-Fr-1802-back.jpg'],
    },
    'TYPE_132': {  # NBN $5 1902
        'obv': ['US-$5-NBN-1902-Fr-598.jpg', 'US-$5-NBN-1902-Fr.598.jpg'],
        'rev': ['US-$5-NBN-1902-Fr-598-back.jpg'],
    },
    'TYPE_133': {  # NBN $5 1929 T2
        'obv': ['US-$5-NBN-1929-Fr-1801.jpg', 'US-$5-NBN-1929-Fr.1801.jpg',
                'US-$5-NBN-1929-Fr-1800.jpg'],
        'rev': ['US-$5-NBN-1929-Fr-1801-back.jpg'],
    },
}

# ── Helper functions ──────────────────────────────────────────────────────────
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

# ── Main loop ─────────────────────────────────────────────────────────────────
stats = {'resolved': 0, 'not_found': 0, 'uploaded': 0, 'skipped': 0}
not_found_list = []
img_cache = {}  # type_id/side -> image bytes

for type_id, spec in PLAN.items():
    doc_ids = TYPE_MAP.get(type_id, [])
    if not doc_ids:
        continue

    # Resolve and download images for this type
    images = {}
    for side in ['obv', 'rev']:
        candidates = spec.get(side, [])
        for fname in candidates:
            url = resolve_wiki(fname)
            time.sleep(0.08)
            if url:
                data = download(url)
                if data:
                    images[side] = data
                    stats['resolved'] += 1
                    break
        if side in images:
            pass
        elif candidates:
            not_found_list.append(f'{type_id}/{side}: tried {len(candidates)} candidates')
            stats['not_found'] += 1

    if not images:
        continue

    # Upload to each doc (only fill missing fields)
    for doc_id in doc_ids:
        doc_data = col.document(doc_id).get().to_dict() or {}
        updates  = {}
        for side, img_data in images.items():
            fs_field = 'image_url_' + ('obverse' if side == 'obv' else 'reverse')
            if doc_data.get(fs_field):
                stats['skipped'] += 1
                continue
            gcs_side = 'obverse' if side == 'obv' else 'reverse'
            gcs_url  = upload_gcs(img_data, doc_id, gcs_side)
            updates[fs_field] = gcs_url
            updates[f'image_source_{gcs_side}'] = SOURCE
            updates['image_attribution'] = ATTR_WIKI
            stats['uploaded'] += 1
        if updates:
            col.document(doc_id).update(updates)

    sides_done = list(images.keys())
    print(f'  {type_id}: {sides_done} → {len(doc_ids)} doc(s)')

print(f'\n✅ Resolved: {stats["resolved"]} | Uploaded: {stats["uploaded"]} | Already set: {stats["skipped"]} | Not found: {stats["not_found"]}')
if not_found_list:
    print(f'\nStill missing ({len(not_found_list)}):')
    for nf in not_found_list:
        print(f'  {nf}')
