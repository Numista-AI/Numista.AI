"""
fix_set_membership.py

Two operations in one pass:

1. UNDO: Remove set_id from any non-expansion coin that got incorrectly tagged.
   (Individual purchases are NOT part of a set just because they share year/denom.)

2. RECREATE: For each timecapsule_{year} set that is missing denominations,
   recreate the expansion coin using a surviving sibling expansion coin as a
   template (same year, same purchase context), swapping denomination/program.

DRY_RUN = True  → print changes, no writes
DRY_RUN = False → apply to Firestore
"""
import os, sys, uuid, collections
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import google.auth
from google.cloud import firestore
creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('coins')

DRY_RUN = True   # CHANGE TO False TO APPLY CHANGES

EXPECTED_DENOMS = {'cent', 'nickel', 'dime', 'quarter', 'half dollar'}

# Correct denomination + program for each year
def correct_denom_info(year: int, norm_denom: str) -> tuple[str, str]:
    """Return (Denomination, Program/Series) for a given year + normalised denom."""
    y = int(year)
    if norm_denom == 'cent':
        prog = 'Lincoln Memorial Cent' if y >= 1959 else 'Lincoln Wheat Cent'
        return 'Cent', prog
    if norm_denom == 'nickel':
        prog = 'Jefferson Nickel' if y >= 1938 else 'Buffalo Nickel'
        return 'Nickel', prog
    if norm_denom == 'dime':
        prog = 'Roosevelt Dime' if y >= 1946 else 'Mercury Dime'
        return 'Dime', prog
    if norm_denom == 'quarter':
        return 'Quarter', 'Washington Quarter'
    if norm_denom == 'half dollar':
        if y <= 1947:   prog = 'Liberty Walking Half Dollar'
        elif y <= 1963: prog = 'Franklin Half Dollar'
        else:           prog = 'Kennedy Half Dollar'
        return 'Half Dollar', prog
    return norm_denom.title(), ''

def normalize_denom(raw: str) -> str:
    r = raw.lower().strip()
    if any(x in r for x in ('cent', '1c', 'penny')): return 'cent'
    if any(x in r for x in ('nickel', '5c')):         return 'nickel'
    if any(x in r for x in ('dime', '10c')):          return 'dime'
    if any(x in r for x in ('quarter', '25c')):       return 'quarter'
    if any(x in r for x in ('half', '50c')):          return 'half dollar'
    return r

# ── load all coins ─────────────────────────────────────────────────────────
print(f'MODE: {"DRY RUN" if DRY_RUN else "*** LIVE WRITE ***"}')
print('Loading all AJ coins...')
docs = list(col.stream())
all_coins = [{'id': d.id, 'data': d.to_dict() or {}} for d in docs]
print(f'Total: {len(all_coins)} coins\n')

expansion = [c for c in all_coins
             if 'set_expansion' in str(c['data'].get('import_batch','')).lower()]
others    = [c for c in all_coins
             if 'set_expansion' not in str(c['data'].get('import_batch','')).lower()]

# ── STEP 1: Find non-expansion coins that incorrectly got set_id ───────────
to_clear = [c for c in others if c['data'].get('set_id','').startswith('timecapsule_')]

print(f'=== STEP 1: REMOVE set_id from {len(to_clear)} individual purchases ===')
for c in to_clear:
    d = c['data']
    print(f"  CLEAR [{c['id'][:8]}] {d.get('Year')} {d.get('Denomination')} "
          f"[{d.get('Program/Series','')}] — removing set_id={d.get('set_id')}")

# ── STEP 2: Find which timecapsule sets are missing denominations ──────────
covered = collections.defaultdict(set)   # year → {norm_denom, ...}
for c in expansion:
    sid = c['data'].get('set_id','')
    if sid.startswith('timecapsule_'):
        year = sid.split('_')[1]
        norm = normalize_denom(c['data'].get('Denomination',''))
        covered[year].add(norm)

# Build template index: year → list of expansion coins (for field inheritance)
templates = collections.defaultdict(list)
for c in expansion:
    sid = c['data'].get('set_id','')
    if sid.startswith('timecapsule_'):
        year = sid.split('_')[1]
        templates[year].append(c['data'])

to_create = []  # list of dicts to insert into Firestore
print(f'\n=== STEP 2: RECREATE missing set coins ===')
for year in sorted(covered.keys()):
    missing = EXPECTED_DENOMS - covered[year]
    if not missing:
        continue
    tmpl_list = templates[year]
    if not tmpl_list:
        print(f"  ⚠️  {year}: no template available — skipping")
        continue
    tmpl = tmpl_list[0]  # use first sibling as template for inherited fields
    for norm_denom in sorted(missing):
        denom_str, prog_str = correct_denom_info(int(year), norm_denom)
        new_doc = {k: v for k, v in tmpl.items()}  # copy all template fields
        new_doc['Denomination']    = denom_str
        new_doc['Program/Series'] = prog_str
        new_doc['set_id']          = f'timecapsule_{year}'
        new_doc['import_batch']    = tmpl.get('import_batch', 'set_expansion_2026-06-20')
        # Clear fields that are denomination-specific
        new_doc.pop('Grade', None)
        new_doc.pop('PCGS #', None)
        new_doc.pop('NGC #', None)
        new_doc.pop('Cert #', None)
        new_id = str(uuid.uuid4())
        to_create.append({'id': new_id, 'data': new_doc})
        print(f"  CREATE {year} {denom_str} [{prog_str}] "
              f"set_id=timecapsule_{year} "
              f"(cost={new_doc.get('Cost', new_doc.get('Purchase Cost','?'))})")

print(f'\nSummary:')
print(f'  {len(to_clear)} coins will have set_id CLEARED (they are individual purchases)')
print(f'  {len(to_create)} set coins will be RECREATED')

if not DRY_RUN:
    batch = db.batch()
    count = 0
    # Step 1: clear set_id from individual purchases
    for c in to_clear:
        batch.update(col.document(c['id']), {'set_id': firestore.DELETE_FIELD})
        count += 1
        if count % 500 == 0: batch.commit(); batch = db.batch()
    # Step 2: create missing set coins
    for item in to_create:
        batch.set(col.document(item['id']), item['data'])
        count += 1
        if count % 500 == 0: batch.commit(); batch = db.batch()
    batch.commit()
    print(f'\n✅ Done. {len(to_clear)} cleared, {len(to_create)} created.')
    print(f'AJ collection: {len(all_coins) - len(to_clear) + len(to_create)} coins')
else:
    print('\nDRY RUN complete. Set DRY_RUN = False to apply.')
