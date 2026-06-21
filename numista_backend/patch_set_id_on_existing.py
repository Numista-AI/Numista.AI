"""
patch_set_id_on_existing.py
For each timecapsule_{year} set that has fewer than 5 coins with set_id,
find the pre-existing (non-expansion) coins that fill the missing denominations
and write set_id to them.

Logic:
  - Expected denominations per year: Cent, Nickel, Dime, Quarter, Half Dollar
  - For years where the expansion set has fewer than 5, find pre-existing
    coins with the missing denomination and write set_id = timecapsule_{year}

DRY_RUN = True  → print what would be written, no Firestore changes
DRY_RUN = False → write set_id to pre-existing coins
"""
import os, sys, collections
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import google.auth
from google.cloud import firestore
creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('coins')

DRY_RUN = False   # CHANGED TO False FOR LIVE WRITE

EXPECTED_DENOMS = {'cent', 'nickel', 'dime', 'quarter', 'half dollar'}
TIMECAPSULE_YEARS = set(str(y) for y in range(1934, 1965))

def normalize_denom(raw: str) -> str:
    """Normalize denomination to one of: cent nickel dime quarter half dollar"""
    r = raw.lower().strip()
    if any(x in r for x in ('cent', '1c', '1 c', 'penny')):
        return 'cent'
    if any(x in r for x in ('nickel', '5c', '5 c')):
        return 'nickel'
    if any(x in r for x in ('dime', '10c', '10 c')):
        return 'dime'
    if any(x in r for x in ('quarter', '25c', '25 c')):
        return 'quarter'
    if any(x in r for x in ('half', '50c', '50 c')):
        return 'half dollar'
    return r  # unknown

# ── load all coins ─────────────────────────────────────────────────────────
print(f'MODE: {"DRY RUN" if DRY_RUN else "*** LIVE WRITE ***"}')
print('Loading all AJ coins...')
docs   = list(col.stream())
all_coins = [{'id': d.id, 'data': d.to_dict() or {}} for d in docs]
print(f'Total: {len(all_coins)} coins\n')

# ── build index of expansion set coins ─────────────────────────────────────
# For each timecapsule year, which denominations already have set_id?
covered = collections.defaultdict(set)   # year → {denom, ...}
for c in all_coins:
    sid = c['data'].get('set_id', '')
    if sid and sid.startswith('timecapsule_'):
        year = sid.split('_')[1]
        denom = normalize_denom(c['data'].get('Denomination', ''))
        covered[year].add(denom)

# ── find incomplete years ──────────────────────────────────────────────────
to_patch = []  # list of (coin_id, set_id, reason)

for year in sorted(TIMECAPSULE_YEARS):
    # Only process years where AJ actually had a Time Capsule set
    # (i.e. at least one expansion coin remains with this set_id)
    if not covered.get(year):
        continue

    missing = EXPECTED_DENOMS - covered[year]
    if not missing:
        continue  # full 5-coin set already tagged

    # For each missing denomination, pick ONE pre-existing coin (best match)
    # Prefer: same year + same normalized denom, not already tagged
    # If multiple exist, take the first by doc order (deterministic)
    remaining_missing = set(missing)
    for c in all_coins:
        if not remaining_missing:
            break
        d = c['data']
        if 'set_expansion' in str(d.get('import_batch', '')).lower():
            continue  # skip expansion coins
        if str(d.get('Year', '')).strip() != year:
            continue
        if d.get('set_id'):
            continue  # already tagged
        norm = normalize_denom(d.get('Denomination', ''))
        if norm in remaining_missing:
            to_patch.append({
                'id':     c['id'],
                'set_id': f'timecapsule_{year}',
                'year':   year,
                'denom':  norm,
                'prog':   d.get('Program/Series', ''),
            })
            remaining_missing.discard(norm)  # only one per missing denom

# ── report ─────────────────────────────────────────────────────────────────
print('=== INCOMPLETE SETS ===')
by_year = collections.defaultdict(list)
for p in to_patch:
    by_year[p['year']].append(p)

for year in sorted(by_year):
    coins_in_set = len(covered.get(year, set()))
    patches = by_year[year]
    print(f"  {year}: {coins_in_set}/5 expansion coins — "
          f"patching {len(patches)} pre-existing coin(s):")
    for p in patches:
        print(f"    → [{p['id'][:8]}] {p['year']} {p['denom']} [{p['prog']}] "
              f"set_id={p['set_id']}")

print(f'\nTotal pre-existing coins to receive set_id: {len(to_patch)}')

if not DRY_RUN:
    print(f'\n*** WRITING set_id TO {len(to_patch)} PRE-EXISTING COINS ***')
    batch = db.batch()
    for i, p in enumerate(to_patch):
        batch.update(col.document(p['id']), {'set_id': p['set_id']})
        if (i + 1) % 500 == 0:
            batch.commit()
            batch = db.batch()
    batch.commit()
    print(f'✅ Done. All timecapsule sets now have full denomination coverage.')
else:
    print('\nDRY RUN complete. Set DRY_RUN = False to write.')
