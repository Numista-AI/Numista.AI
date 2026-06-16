"""
Gap analysis v3 - using correct Firestore field names.
Fields: 'Program/Series', 'Year', 'Denomination', 'Mint Mark', 'image_url_obverse'
"""
import re
import google.auth
from google.cloud import storage as gcs, firestore
from collections import Counter

creds, _ = google.auth.default()
gcs_client = gcs.Client(credentials=creds, project='studio-9101802118-8c9a8')
fs_client  = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')

# ── 1. Index GCS images ────────────────────────────────────────────────────────
bucket    = gcs_client.bucket('numista-uploads-studio-9101802118-8c9a8')
all_blobs = list(bucket.list_blobs(prefix='reference_images/us_mint/'))
print(f'GCS US Mint images: {len(all_blobs)}')

gcs_index = []
for b in all_blobs:
    filename = b.name.split('/')[-1].lower()
    filename = re.sub(r'\.(jpg|jpeg|png|webp)$', '', filename)
    tokens   = set(re.split(r'[-_\s]+', filename))
    year_m   = re.search(r'(1[789]\d{2}|20\d{2})', filename)
    gcs_index.append({
        'url':    f'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/{b.name}',
        'tokens': tokens,
        'year':   year_m.group(1) if year_m else None,
        'name':   filename,
        'side':   'obverse' if 'obverse' in filename else 'reverse' if 'reverse' in filename else 'unknown'
    })

SERIES_KEYWORDS = {
    'lincoln':          ['lincoln','cent','penny','wheat'],
    'roosevelt':        ['roosevelt','dime'],
    'washington':       ['washington','quarter'],
    'kennedy':          ['kennedy','half'],
    'jefferson':        ['jefferson','nickel'],
    'morgan':           ['morgan','dollar'],
    'peace':            ['peace','dollar'],
    'eagle':            ['eagle'],
    'buffalo':          ['buffalo','nickel'],
    'mercury':          ['mercury','dime','winged'],
    'barber':           ['barber'],
    'presidential':     ['presidential','dollar'],
    'eisenhower':       ['eisenhower'],
    'sacagawea':        ['sacagawea','native'],
    'state quarter':    ['quarter','state'],
    'bicentennial':     ['bicentennial'],
    'walking liberty':  ['walking','liberty'],
    'standing liberty': ['standing','liberty'],
    'franklin':         ['franklin','half'],
    'american women':   ['quarter','women'],
    'atb':              ['quarter','beautiful'],
    'gold eagle':       ['eagle','gold'],
    'silver eagle':     ['eagle','silver'],
    'gold buffalo':     ['buffalo','gold'],
    'baseball':         ['baseball','hall'],
    'basketball':       ['basketball','hall'],
    'apollo':           ['apollo'],
    'purple heart':     ['purple','heart'],
    'bald eagle':       ['bald','eagle'],
}

def match_coin(year, series, denom):
    year_s  = str(year).strip() if year else ''
    s_lower = series.lower() if series else ''
    d_lower = denom.lower()  if denom  else ''

    # Build search tokens from series + denomination
    search  = set(re.split(r'[-_\s/]+', f'{s_lower} {d_lower}'))
    search  = {t for t in search if len(t) >= 3 and t not in ('the','and','for','set','coin','unc','proof')}

    best_score = 0
    best_obv   = None
    best_rev   = None

    for entry in gcs_index:
        score = 0
        if year_s and entry['year'] == year_s:
            score += 3
        overlap = len(search & entry['tokens'])
        score  += overlap
        for kw, boosts in SERIES_KEYWORDS.items():
            if kw in s_lower:
                score += sum(1 for b in boosts if b in entry['tokens'])

        if score > best_score:
            best_score = score
            if entry['side'] == 'obverse':
                best_obv = entry['url']
            elif entry['side'] == 'reverse':
                best_rev = entry['url']

    if best_score >= 2:
        return best_obv or best_rev
    return None

# ── 2. Fetch jseaman collection ────────────────────────────────────────────────
print('Fetching jseaman collection...')
coins_ref = (fs_client.collection('users')
             .document('jseaman1204@gmail.com')
             .collection('coins'))
all_coins = list(coins_ref.stream())

has_image    = 0
no_image     = 0
can_match    = 0
series_gaps  = Counter()
series_has   = Counter()

for coin in all_coins:
    d      = coin.to_dict()
    img    = d.get('image_url_obverse', '') or ''
    series = d.get('Program/Series', '') or ''
    year   = d.get('Year', '')            or ''
    denom  = d.get('Denomination', '')    or ''

    if img.strip():
        has_image += 1
        series_has[series] += 1
        continue

    no_image += 1
    match = match_coin(year, series, denom)
    if match:
        can_match += 1
    else:
        key = series.strip() or '(blank)'
        series_gaps[key] += 1

print(f'\nTotal coins:       {len(all_coins)}')
print(f'Have image:        {has_image}')
print(f'Missing image:     {no_image}')
print(f'  Matchable now:   {can_match}  ({int(can_match/no_image*100) if no_image else 0}%)')
print(f'  Still missing:   {no_image - can_match}')

print(f'\nTop series WITH images already:')
for s, c in series_has.most_common(10):
    print(f'  {c:>4}  {s}')

print(f'\nTop series STILL MISSING images (most urgent to scrape/generate):')
for s, c in series_gaps.most_common(30):
    print(f'  {c:>4}  {s}')
