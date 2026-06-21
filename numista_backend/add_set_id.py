"""
add_set_id.py
Add a set_id field to all set-expansion coins in AJ's collection.

set_id format: lowercase, underscored, year-specific
  Time Capsule 5-Coin Year Sets → "timecapsule_{year}"   e.g. "timecapsule_1950"
  1943 Steel Cent PDS Sets      → "steelcent_pds_1943"
  Indian Head Cent Album        → "indianhead_album"
  Standing Liberty Quarter Set  → "standinglib_quarter"

DRY_RUN = True  → print what would be written, no Firestore changes
DRY_RUN = False → write set_id to every expansion coin
"""
import os, sys, re, collections
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import google.auth
from google.cloud import firestore
creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('coins')

DRY_RUN = True   # CHANGE TO False TO WRITE TO FIRESTORE

# ── helpers ────────────────────────────────────────────────────────────────
def derive_set_id(data: dict) -> str | None:
    """Return a set_id string from a coin's data, or None if not determinable."""
    notes  = str(data.get('Notes', '') or data.get('notes', '')).lower()
    batch  = str(data.get('import_batch', '')).lower()
    year   = str(data.get('Year', '')).strip()
    prog   = str(data.get('Program/Series', '') or '').lower()
    denom  = str(data.get('Denomination', '') or '').lower()

    # Indian Head Cent Album (1897–1908)
    if 'indian head' in notes or 'indian head' in prog:
        return "indianhead_album"

    # Standing Liberty Quarter Set (1925–1930)
    if 'standing liberty' in notes or 'standing liberty' in prog:
        return "standinglib_quarter"

    # 1943 Steel Cent PDS sets
    if ('1943' in notes and ('steel' in notes or 'pds' in notes)) or \
       'steel' in denom or \
       (year == '1943' and 'cent' in denom):
        return "steelcent_pds_1943"

    # Time Capsule / America Revisited 5-coin year sets (1934–1964)
    # These have empty Notes — identified by year range + standard denomination
    TIMECAPSULE_DENOMS = {'cent', 'nickel', 'dime', 'quarter', 'half dollar'}
    if year.isdigit() and 1934 <= int(year) <= 1964 and denom in TIMECAPSULE_DENOMS:
        return f"timecapsule_{year}"

    # Fallback: try to parse "expanded from: X YYYY" pattern in notes
    m = re.search(r'expanded from[:\s]+(.+?)(?:\s+(\d{4}))?$', notes)
    if m:
        label = re.sub(r'[^a-z0-9]+', '_', m.group(1).strip()).strip('_')
        yr = m.group(2) or year
        return f"{label}_{yr}" if yr else label

    return None

# ── main ───────────────────────────────────────────────────────────────────
print(f'MODE: {"DRY RUN" if DRY_RUN else "*** LIVE WRITE ***"}')
print('Loading AJ expansion coins...')

docs = list(col.stream())
expansion = [
    {'id': d.id, 'data': d.to_dict() or {}}
    for d in docs
    if 'set_expansion' in str((d.to_dict() or {}).get('import_batch', '')).lower()
]
print(f'Found {len(expansion)} expansion coins\n')

# Sample — show first 10 raw notes fields so we can tune the logic
print('=== SAMPLE DATA (first 10 expansion coins) ===')
for c in expansion[:10]:
    d = c['data']
    print(f"  [{c['id'][:8]}] Year={d.get('Year')} Denom={d.get('Denomination')} "
          f"Prog={d.get('Program/Series')} Notes={str(d.get('Notes',''))[:80]}")

print()
print('=== SET_ID ASSIGNMENT PREVIEW ===')
by_set = collections.defaultdict(list)
no_id  = []

for c in expansion:
    sid = derive_set_id(c['data'])
    if sid:
        by_set[sid].append(c['id'])
    else:
        no_id.append(c)

for sid, ids in sorted(by_set.items()):
    print(f"  {sid:35s} → {len(ids)} coins")

if no_id:
    print(f"\n  ⚠️  {len(no_id)} coins could NOT be assigned a set_id:")
    for c in no_id:
        d = c['data']
        print(f"     [{c['id'][:8]}] {d.get('Year')} {d.get('Denomination')} "
              f"notes='{str(d.get('Notes',''))[:60]}'")

print(f'\nTotal: {sum(len(v) for v in by_set.values())} will get set_id, '
      f'{len(no_id)} cannot be determined')

if not DRY_RUN:
    if no_id:
        print('\n⚠️  Some coins have no determinable set_id — aborting for safety.')
        print('   Fix derive_set_id() logic and re-run.')
        sys.exit(1)
    print(f'\n*** WRITING set_id TO {len(expansion)} COINS IN FIRESTORE ***')
    batch = db.batch()
    count = 0
    for sid, ids in by_set.items():
        for coin_id in ids:
            batch.update(col.document(coin_id), {'set_id': sid})
            count += 1
            if count % 500 == 0:
                batch.commit()
                batch = db.batch()
    batch.commit()
    print(f'✅ set_id written to {count} coins.')
else:
    print('\nDRY RUN complete. Set DRY_RUN = False to write to Firestore.')
