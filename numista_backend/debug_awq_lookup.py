"""
debug_awq_lookup.py
Checks Eric's AWQ coins and simulates the CoinImageService lookup to find why
reverse images aren't appearing.
"""
import os, sys
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import re
import google.auth
from google.cloud import firestore

creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')

# ── 1. Check Eric's AWQ coins ──────────────────────────────────────────────
print('=== ERIC AWQ COINS ===')
col = db.collection('users').document('eric.seaman@yahoo.com').collection('coins')
docs = list(col.stream())
awq = []
for d in docs:
    data = d.to_dict() or {}
    prog = str(data.get('Program/Series', '')).lower()
    if 'women' in prog and 'quarter' in prog:
        awq.append({'id': d.id, 'data': data})

for c in awq:
    d = c['data']
    print(f"\n  [{c['id'][:8]}] {d.get('Year')} {d.get('Theme/Subject')} ({d.get('Mint Mark','')})")
    print(f"    Program/Series: '{d.get('Program/Series','')}' ")
    print(f"    image_url_obverse: '{d.get('image_url_obverse','')[:60] if d.get('image_url_obverse') else 'BLANK'}'")
    print(f"    image_url_reverse: '{d.get('image_url_reverse','')[:60] if d.get('image_url_reverse') else 'BLANK'}'")

print(f"\nTotal Eric AWQ coins: {len(awq)}")

# ── 2. Simulate the slug resolution ───────────────────────────────────────
SUBJECT_SLUG_MAP = {
    'maya angelou': 'maya-angelou', 'sally ride': 'sally-ride',
    'wilma mankiller': 'wilma-mankiller', 'nina otero warren': 'nina-otero-warren',
    'nina otero-warren': 'nina-otero-warren', 'adelina otero-warren': 'nina-otero-warren',
    'anna may wong': 'anna-may-wong', 'anna mae wong': 'anna-may-wong',
    'bessie coleman': 'bessie-coleman',
    'edith kanaka ole': 'edith-kanaka-ole',
    'eleanor roosevelt': 'eleanor-roosevelt',
    'jovita idar': 'jovita-idar', 'maria tallchief': 'maria-tallchief',
    'patsy mink': 'patsy-mink', 'patsy takemoto mink': 'patsy-mink',
    'celia cruz': 'celia-cruz',
    'zitkala-sa': 'zitkala-sa', 'zitkala sa': 'zitkala-sa',
    'mary edwards walker': 'mary-edwards-walker',
    'pauli murray': 'pauli-murray',
    'ida b. wells': 'ida-b-wells', 'ida b wells': 'ida-b-wells',
    'vera rubin': 'vera-rubin',
    'althea gibson': 'althea-gibson',
    'stacey park milbern': 'stacey-park-milbern',
    'juliette gordon low': 'juliette-gordon-low',
}

def resolve_subject(subject):
    if not subject: return None
    key = subject.strip().lower()
    if key in SUBJECT_SLUG_MAP: return SUBJECT_SLUG_MAP[key]
    for k, v in sorted(SUBJECT_SLUG_MAP.items(), key=lambda x: -len(x[0])):
        if key in k or k in key: return v
    return None

PROGRAM_MAP = {
    'american women quarters': 'american-women-quarters',
    'american-women-quarters': 'american-women-quarters',
}
def resolve_program(series):
    if not series: return None
    key = series.strip().lower()
    if key in PROGRAM_MAP: return PROGRAM_MAP[key]
    for k, v in PROGRAM_MAP.items():
        if key in k or k in key: return v
    return None

print('\n=== SIMULATED COIN_IMAGE_INDEX LOOKUPS ===')
for c in awq:
    d = c['data']
    year = str(d.get('Year',''))
    theme = d.get('Theme/Subject','')
    prog_raw = d.get('Program/Series','')
    subject_slug = resolve_subject(theme)
    program_slug = resolve_program(prog_raw)
    candidate = f"{year}_{subject_slug}_{program_slug}_reverse" if subject_slug and program_slug else "CANNOT RESOLVE"
    print(f"\n  [{c['id'][:8]}] theme='{theme}' prog='{prog_raw}'")
    print(f"    subject_slug={subject_slug}  program_slug={program_slug}")
    print(f"    → candidate key: '{candidate}'")

# ── 3. Check if those keys exist in coin_image_index ─────────────────────
print('\n=== COIN_IMAGE_INDEX EXISTENCE CHECK ===')
idx = db.collection('coin_image_index')
for c in awq:
    d = c['data']
    year = str(d.get('Year',''))
    theme = d.get('Theme/Subject','')
    prog_raw = d.get('Program/Series','')
    subject_slug = resolve_subject(theme)
    program_slug = resolve_program(prog_raw)
    if not subject_slug or not program_slug:
        print(f"  SKIP (can't resolve): theme='{theme}' prog='{prog_raw}'")
        continue
    key = f"{year}_{subject_slug}_{program_slug}_reverse"
    doc = idx.document(key).get()
    if doc.exists:
        data = doc.to_dict() or {}
        url = (data.get('reverse') or {}).get('public_url','MISSING URL')
        print(f"  ✅ FOUND: {key}")
        print(f"     URL: {str(url)[:80]}")
    else:
        print(f"  ❌ NOT FOUND: {key}")
        # Try without year
        key2 = f"{subject_slug}_{program_slug}_reverse"
        doc2 = idx.document(key2).get()
        print(f"     Also tried {key2}: {'✅ exists' if doc2.exists else '❌ not found'}")
