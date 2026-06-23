#!/usr/bin/env python3
"""
Extract all AWQ image URLs from coin_image_index and map them to the 36 coins.
Output: awq_full_image_map.json
"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
os.chdir(r'C:\Users\ericd\Documents\MyVertexProject\numista_backend')

from google.oauth2 import service_account
from google.cloud import firestore

creds = service_account.Credentials.from_service_account_file('serviceAccountKey.json.json')
db = firestore.Client(project=creds.project_id, credentials=creds)

# Fetch all 2022-2024 AWQ coin_image_index entries
print('Fetching all AWQ index entries...')
all_docs = list(db.collection('coin_image_index').stream())
awq_docs = [d for d in all_docs if d.id.startswith(('2022_','2023_','2024_')) and
            any(k in d.id.lower() for k in ['women', 'quarter'])]

print(f'Found {len(awq_docs)} AWQ index entries')
full_map = {}
for d in awq_docs:
    full_map[d.id] = d.to_dict()
    dd = d.to_dict()
    side = 'obv' if 'obverse' in dd else 'rev'
    url = dd.get('obverse', dd.get('reverse', {})).get('public_url', '?')
    print(f'  {d.id}: [{side}] {url[:90]}')

with open('awq_index_full.json', 'w', encoding='utf-8') as f:
    json.dump(full_map, f, indent=2, ensure_ascii=False, default=str)
print(f'\nWrote awq_index_full.json')

# Load live coin data
with open('awq_coins_live.json', encoding='utf-8') as f:
    coins = json.load(f)

# Build a lookup: theme -> {obverse_url, reverse_url}
# Key normalizations
def slug(name):
    return name.lower().replace(' ', '-').replace('.', '').replace("'", '').replace('–','-').replace('á','a').replace('ā','a').replace('ó','o')

# Build from index
obverse_by_year = {}  # year -> obverse_url (shared obverse per year)
reverse_by_subject = {}  # subject_slug -> reverse_url
obverse_by_subject = {}  # subject_slug -> specific obverse_url (if exists)

for doc_id, data in full_map.items():
    parts = doc_id.split('_')
    year = parts[0]
    
    if 'obverse' in data:
        url = data['obverse'].get('public_url', '')
        if url:
            subject = data.get('subject') or ''
            if subject:
                obverse_by_subject[subject] = url
                print(f'Obverse subject={subject}: {url[:80]}')
            else:
                obverse_by_year[year] = url
                print(f'Obverse year={year}: {url[:80]}')
    
    if 'reverse' in data:
        url = data['reverse'].get('public_url', '')
        if url:
            subject = data.get('subject') or ''
            if subject:
                reverse_by_subject[subject] = url
            else:
                # Generic reverse for that year
                reverse_by_subject[f'_{year}_generic'] = url

print(f'\nobverse_by_year: {list(obverse_by_year.keys())}')
print(f'obverse_by_subject: {list(obverse_by_subject.keys())}')
print(f'reverse_by_subject count: {len(reverse_by_subject)}')

# Theme slug mapping
THEME_SLUGS = {
    'Bessie Coleman':           'bessie-coleman',
    "Edith Kanaka'ole":         'edith-kanaka-ole',
    'Eleanor Roosevelt':        'eleanor-roosevelt',
    'Jovita Idar':              'jovita-idar',
    'Maria Tallchief':          'maria-tallchief',
    'Patsy Takemoto Mink':      'patsy-t-mink',
    'Dr. Mary Edwards Walker':  'mary-edwards-walker',
    'Celia Cruz':               'celia-cruz',
    'Zitkala-Sa':               'zitkala-sa',
    'Pauli Murray':             'pauli-murray',
}

print('\n=== MAPPING COINS TO IMAGES ===')
resolved = []
for coin in coins:
    theme = coin['theme']
    year  = str(coin['year'])
    t_slug = THEME_SLUGS.get(theme, slug(theme))
    
    # Find obverse: try subject-specific first, then year-generic
    obs_url = obverse_by_subject.get(t_slug) or obverse_by_year.get(year) or obverse_by_year.get(year, '')
    
    # Find reverse: try subject-specific first
    rev_url = reverse_by_subject.get(t_slug) or reverse_by_subject.get(f'_{year}_generic', '')
    
    # Also try common slug variations
    for slug_var in [t_slug, t_slug.replace('-',''), slug(theme)]:
        if not obs_url:
            obs_url = obverse_by_subject.get(slug_var, '')
        if not rev_url:
            rev_url = reverse_by_subject.get(slug_var, '')
    
    status = 'BOTH' if obs_url and rev_url else ('OBV_ONLY' if obs_url else ('REV_ONLY' if rev_url else 'NONE'))
    print(f"  {year} {theme:<30} t_slug={t_slug:<25} -> {status}")
    
    resolved.append({
        **coin,
        'theme_slug': t_slug,
        'obverse_url': obs_url,
        'reverse_url': rev_url,
        'resolve_status': status,
    })

with open('awq_full_image_map.json', 'w', encoding='utf-8') as f:
    json.dump({'index': full_map, 'obverse_by_year': obverse_by_year,
               'obverse_by_subject': obverse_by_subject,
               'reverse_by_subject': reverse_by_subject,
               'coins': resolved}, f, indent=2, ensure_ascii=False, default=str)

both = sum(1 for c in resolved if c['resolve_status'] == 'BOTH')
print(f'\nTotal: {len(resolved)} | BOTH: {both} | Missing: {len(resolved)-both}')
