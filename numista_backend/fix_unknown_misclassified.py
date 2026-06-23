"""
fix_unknown_misclassified.py
Fixes 'Unknown' currency docs that are actually identifiable note types.
Copies already-uploaded GCS images from a matching doc in the same type.
Also patches currency_type_label and currency_type fields.
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

def get_ref_images(type_id):
    """Return the first doc in a type that has at least one image URL."""
    for doc_id in TYPE_MAP.get(type_id, []):
        data = col.document(doc_id).get().to_dict() or {}
        if data.get('image_url_obverse') or data.get('image_url_reverse'):
            return {
                'image_url_obverse':    data.get('image_url_obverse'),
                'image_url_reverse':    data.get('image_url_reverse'),
                'image_source_obverse': data.get('image_source_obverse'),
                'image_source_reverse': data.get('image_source_reverse'),
                'image_attribution':    data.get('image_attribution'),
            }
    return None

# ── Mapping: description fragment → (type_id, correct_type_key, correct_type_label) ──
# Ordered from most specific to least specific
RULES = [
    # Silver Certificates — by year in 'Year' field
    ('$1 silver certificate large size eagle', None,       'TYPE_139', 'silver_certificate', 'Silver Certificate'),
    ('$1 siver certificate',                   None,       'TYPE_139', 'silver_certificate', 'Silver Certificate'),
    ('$1 silver cerificate large size',        '1923',     'TYPE_145', 'silver_certificate', 'Silver Certificate'),
    ('$1 silver cerificate large size',        '1886',     'TYPE_138', 'silver_certificate', 'Silver Certificate'),
    ('ilver certificate large size',           None,       'TYPE_138', 'silver_certificate', 'Silver Certificate'),
    # Federal Reserve Notes — by year
    ('federal reserve note',                   '1963a',    'TYPE_019', 'federal_reserve_note', 'Federal Reserve Note'),
    ('fedreral reserve note',                  '1963a',    'TYPE_019', 'federal_reserve_note', 'Federal Reserve Note'),
    ('federal reservve note',                  '1969b',    'TYPE_023', 'federal_reserve_note', 'Federal Reserve Note'),
    ('ferderal reserve note',                  '1969b',    'TYPE_023', 'federal_reserve_note', 'Federal Reserve Note'),
    ('federal reserve note',                   '1969a',    'TYPE_022', 'federal_reserve_note', 'Federal Reserve Note'),
    ('federal reserve note',                   '1969b',    'TYPE_023', 'federal_reserve_note', 'Federal Reserve Note'),
    ('ferderal reserve note',                  '1969d',    'TYPE_025', 'federal_reserve_note', 'Federal Reserve Note'),
    ('federal reserve note',                   '1988a',    'TYPE_028', 'federal_reserve_note', 'Federal Reserve Note'),
    ('federal reserve note',                   '1993',     'TYPE_029', 'federal_reserve_note', 'Federal Reserve Note'),
    ('ferderal reserve star note',             '1999',     'TYPE_031', 'federal_reserve_note', 'Federal Reserve Note'),
    ('federal reserve note',                   '1999',     'TYPE_031', 'federal_reserve_note', 'Federal Reserve Note'),
    ('federal reserve star note',              '2003a',    'TYPE_034', 'federal_reserve_note', 'Federal Reserve Note'),
    ('ferderal reserve star note',             '2003a',    'TYPE_034', 'federal_reserve_note', 'Federal Reserve Note'),
    ('federal reserve note',                   '2003a',    'TYPE_034', 'federal_reserve_note', 'Federal Reserve Note'),
    ('frderal reserve note',                   '1963a',    'TYPE_019', 'federal_reserve_note', 'Federal Reserve Note'),
    ('federal rserve note',                    '1914',     'TYPE_061', 'federal_reserve_note', 'Federal Reserve Note'),
    # Legal Tender Notes
    ('legal tender note',                      '1928b',    'TYPE_117', 'legal_tender_note', 'Legal Tender Note'),
    ('legal tender note',                      '1953b',    'TYPE_121', 'legal_tender_note', 'Legal Tender Note'),
    ('legal tender note',                      '1953c',    'TYPE_123', 'legal_tender_note', 'Legal Tender Note'),
    ('leal tender star note',                  '1963',     'TYPE_114', 'legal_tender_note', 'Legal Tender Note'),
    ('egal tender note',                       '1928b',    'TYPE_117', 'legal_tender_note', 'Legal Tender Note'),
    # Fractional Currency
    ('gractional currency',                    None,       'TYPE_071', 'fractional_currency', 'Fractional Currency'),
    # Confederate — assign to known Confederate type
    ('conferate note',                         '1864',     'TYPE_003', 'confederate',         'Confederate'),   # $20 T-67
    ('confedwrate note',                       '1864',     'TYPE_003', 'confederate',         'Confederate'),   # $20
    ('conferate note',                         '1864',     'TYPE_001', 'confederate',         'Confederate'),   # $50
    # Starter sets — use representative image
    ('large size note starter set',            None,       'TYPE_145', 'silver_certificate', 'Silver Certificate'),
]

# Load all 'Unknown' or uncategorized docs
unknown_docs = []
for d in col.stream():
    data = d.to_dict() or {}
    lbl = data.get('currency_type_label', '')
    if lbl and lbl != 'Unknown':
        continue
    has_obv = bool(data.get('image_url_obverse'))
    has_rev = bool(data.get('image_url_reverse'))
    if has_obv and has_rev:
        continue
    unknown_docs.append((d.id, data))

print(f'Found {len(unknown_docs)} Unknown/uncategorized docs needing images\n')

fixed = 0
skipped = 0
for doc_id, data in unknown_docs:
    desc   = (data.get('Description', '') or '').lower()
    year   = str(data.get('Year', '') or '').lower()
    denom  = str(data.get('Denomination', '') or '').lower()
    matched = None
    for (desc_pat, year_pat, type_id, type_key, type_lbl) in RULES:
        if desc_pat.lower() in desc:
            if year_pat is None or year_pat.lower() in year:
                matched = (type_id, type_key, type_lbl)
                break

    if not matched:
        continue  # genuinely unknown, skip for now

    type_id, type_key, type_lbl = matched
    ref = get_ref_images(type_id)
    if not ref:
        print(f'  ⚠️  {doc_id[:8]} matched {type_id} but no reference images found')
        skipped += 1
        continue

    updates = {
        'currency_type':       type_key,
        'currency_type_label': type_lbl,
    }
    if ref.get('image_url_obverse') and not data.get('image_url_obverse'):
        updates['image_url_obverse']    = ref['image_url_obverse']
        updates['image_source_obverse'] = ref.get('image_source_obverse', '')
    if ref.get('image_url_reverse') and not data.get('image_url_reverse'):
        updates['image_url_reverse']    = ref['image_url_reverse']
        updates['image_source_reverse'] = ref.get('image_source_reverse', '')
    if ref.get('image_attribution'):
        updates['image_attribution'] = ref['image_attribution']

    col.document(doc_id).update(updates)
    fixed += 1
    desc_short = data.get('Description','')[:55]
    print(f'  ✅ {doc_id[:8]}  {type_id:12}  {desc_short}')

print(f'\n✅ Fixed: {fixed} | Skipped (no match): {skipped}')
