"""
expand_set_records.py
Expands multi-coin set records into individual coin records in AJ's collection.

Handles:
  1. Five-Coin Year Sets (Time Capsule / America Revisited) → 5 individual coins each
  2. 12-Coin Indian Head Cent album (1897-1908)
  3. 6-Coin Standing Liberty Quarter Set (1925-1930)
  4. 3-Coin 1943 Steel Cent PDS sets
  5. Ike Dollar set-level stub record (delete only — already expanded)

DRY_RUN = True prints what WOULD happen without writing to Firestore.
Set DRY_RUN = False to execute.
"""

import os, sys, uuid
from datetime import datetime, timezone

os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import google.auth
from google.cloud import firestore

DRY_RUN = False  # SET TO False TO EXECUTE

creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('coins')

# ── Coin composition per year ─────────────────────────────────────────────────
def coins_for_year(year_str):
    """Returns list of (program, denomination) tuples for the 5-coin year set."""
    try:
        yr = int(year_str)
    except:
        return []
    
    # Cent
    cent = ('Lincoln Memorial Cent', 'Cent') if yr >= 1959 else ('Lincoln Wheat Cent', 'Cent')
    
    # Nickel
    nickel = ('Jefferson Nickel', 'Nickel') if yr >= 1938 else ('Buffalo Nickel', 'Nickel')
    
    # Dime
    dime = ('Roosevelt Dime', 'Dime') if yr >= 1946 else ('Mercury Dime', 'Dime')
    
    # Quarter (Washington quarter throughout this era)
    quarter = ('Washington Quarter', 'Quarter')
    
    # Half Dollar
    if yr <= 1947:
        half = ('Walking Liberty Half Dollar', 'Half Dollar')
    elif yr <= 1963:
        half = ('Franklin Half Dollar', 'Half Dollar')
    else:
        half = ('Kennedy Half Dollar', 'Half Dollar')
    
    return [cent, nickel, dime, quarter, half]

def make_expanded_record(parent_data, year, program, denomination, part_cost, set_idx, total, parent_id):
    """Build a new individual coin record from a parent set record."""
    now = datetime.now(timezone.utc)
    rec = dict(parent_data)  # copy all fields
    
    # Override the set-specific fields
    rec['Year'] = year
    rec['Program/Series'] = program
    rec['Denomination'] = denomination
    rec['Quantity'] = 1
    
    # Split cost
    if part_cost > 0:
        rec['Cost'] = f'${part_cost:.2f}'
    
    # Update notes
    orig_notes = str(parent_data.get('Personal Notes', ''))
    parent_prog = parent_data.get('Program/Series', 'Year Set')
    parent_cost = parent_data.get('Cost', '')
    rec['Personal Notes'] = (
        f'Part of {parent_prog} ({year}) — coin {set_idx}/{total}. '
        f'Set purchase: {parent_cost}. Original set ID: {parent_id[:8]}. '
        + (orig_notes if orig_notes and 'Taxable' not in orig_notes else '')
    ).strip()
    
    # Clear denomination that was "5-Coin Set" etc
    # (already overwritten above)
    
    # Tag the import batch
    rec['import_batch'] = f'set_expansion_2026-06-20'
    rec['source_note'] = f'Expanded from set record {parent_id}'
    
    return rec

# ── Find all expandable records ───────────────────────────────────────────────
print('Loading all coins from Firestore...')
docs = list(col.stream())
print(f'Loaded {len(docs)} records.\n')

five_coin_sets = []
ike_set_stub = []
steel_cent_pds = []
indian_head_12 = []
slq_6 = []

for d in docs:
    data = d.to_dict() or {}
    denom = str(data.get('Denomination', '')).lower()
    prog = str(data.get('Program/Series', '')).lower()
    notes = str(data.get('Personal Notes', '')).lower()
    yr = str(data.get('Year', '')).strip().replace('.0', '')
    qty_raw = data.get('Quantity', '')
    try:
        qty = int(float(str(qty_raw))) if qty_raw not in ('', None) else 1
    except:
        qty = 1

    # 5-coin year sets
    if ('5-coin' in denom or '5 coin' in denom or 'assorted us coins' in denom or
        'mixed us coin' in denom or
        ('time capsule' in prog and qty <= 1) or
        'america revisited' in prog):
        five_coin_sets.append((d.id, yr, data))
    
    # Ike Dollar set-level stub
    elif '1971-1978 ike dollar set' in prog or ('ike dollar set' in prog):
        ike_set_stub.append((d.id, yr, data))
    
    # 1943 steel cent PDS (qty=3, notes say PDS or P/D/S)
    elif yr == '1943' and qty == 3 and ('pds' in notes or 'p, d, s' in notes or 'set of 3 steel' in notes):
        steel_cent_pds.append((d.id, yr, data))
    
    # Indian Head Cent album (12-coin)
    elif 'indian head cent' in prog and qty == 12:
        indian_head_12.append((d.id, yr, data))
    
    # Standing Liberty Quarter set (6-coin)
    elif 'standing liberty' in prog and qty == 6:
        slq_6.append((d.id, yr, data))

print(f'5-Coin Year Sets:              {len(five_coin_sets)}')
print(f'Ike Dollar Set stubs:          {len(ike_set_stub)}')
print(f'1943 Steel Cent PDS sets:      {len(steel_cent_pds)}')
print(f'12-Coin Indian Head albums:    {len(indian_head_12)}')
print(f'6-Coin Standing Liberty sets:  {len(slq_6)}')
print()

new_records = []
records_to_delete = []

# ── 1. FIVE-COIN YEAR SETS ────────────────────────────────────────────────────
print('=== EXPANDING FIVE-COIN YEAR SETS ===')
for parent_id, yr, data in five_coin_sets:
    prog = data.get('Program/Series', 'Time Capsule Year Set')
    cost_str = str(data.get('Cost', '$0')).replace('$', '').replace(',', '')
    try:
        total_cost = float(cost_str)
    except:
        total_cost = 0.0
    part_cost = round(total_cost / 5, 2)
    
    coins = coins_for_year(yr)
    if not coins:
        print(f'  SKIP {parent_id[:8]} Year={yr} — cannot determine year')
        continue
    
    print(f'  {yr} | {prog} | cost=${total_cost:.2f} → ${part_cost:.2f}/coin')
    for i, (coin_prog, coin_denom) in enumerate(coins, 1):
        new_rec = make_expanded_record(data, yr, coin_prog, coin_denom, part_cost, i, 5, parent_id)
        new_records.append(new_rec)
        print(f'    + [{i}/5] {coin_prog} ({coin_denom})')
    
    records_to_delete.append(parent_id)
    print()

# ── 2. IKE DOLLAR SET STUB ────────────────────────────────────────────────────
print('=== DELETING IKE DOLLAR SET STUBS (already expanded) ===')
for parent_id, yr, data in ike_set_stub:
    prog = data.get('Program/Series', '')
    print(f'  DELETE {parent_id[:8]} | {yr} | {prog}')
    records_to_delete.append(parent_id)
print()

# ── 3. 1943 STEEL CENT PDS ────────────────────────────────────────────────────
print('=== EXPANDING 1943 STEEL CENT PDS SETS ===')
for parent_id, yr, data in steel_cent_pds:
    prog = data.get('Program/Series', 'Lincoln Steel Cent')
    cost_str = str(data.get('Cost', '$0')).replace('$', '').replace(',', '')
    try:
        total_cost = float(cost_str)
    except:
        total_cost = 0.0
    part_cost = round(total_cost / 3, 2)
    
    print(f'  {yr} | {prog} → 3 coins (P, D, S)')
    for mint, mint_label in [('P', 'Philadelphia'), ('D', 'Denver'), ('S', 'San Francisco')]:
        new_rec = make_expanded_record(data, yr, 'Lincoln Steel Cent', 'Cent', part_cost, 
                                       ['P','D','S'].index(mint)+1, 3, parent_id)
        new_rec['Mint Mark'] = mint
        new_rec['Personal Notes'] = f'1943-{mint} WWII Steel Cent. Part of PDS set. Set cost: ${total_cost:.2f}. Original set ID: {parent_id[:8]}.'
        new_records.append(new_rec)
        print(f'    + 1943-{mint} Lincoln Steel Cent')
    
    records_to_delete.append(parent_id)
    print()

# ── 4. 12-COIN INDIAN HEAD CENT ALBUM (1897-1908) ────────────────────────────
print('=== EXPANDING 12-COIN INDIAN HEAD CENT ALBUM ===')
for parent_id, yr, data in indian_head_12:
    cost_str = str(data.get('Cost', '$0')).replace('$', '').replace(',', '')
    try:
        total_cost = float(cost_str)
    except:
        total_cost = 0.0
    part_cost = round(total_cost / 12, 2)
    cond = data.get('Condition', 'Good')
    
    print(f'  Album 1897-1908 | cost=${total_cost:.2f} → ${part_cost:.2f}/coin')
    for coin_yr in range(1897, 1909):  # 1897-1908
        new_rec = make_expanded_record(data, str(coin_yr), 'Indian Head Cent', 'Cent', 
                                       part_cost, coin_yr - 1896, 12, parent_id)
        new_records.append(new_rec)
        print(f'    + {coin_yr} Indian Head Cent')
    
    records_to_delete.append(parent_id)
    print()

# ── 5. 6-COIN STANDING LIBERTY QUARTER SET (1925-1930) ───────────────────────
print('=== EXPANDING 6-COIN STANDING LIBERTY QUARTER SET ===')
for parent_id, yr, data in slq_6:
    cost_str = str(data.get('Cost', '$0')).replace('$', '').replace(',', '')
    try:
        total_cost = float(cost_str)
    except:
        total_cost = 0.0
    part_cost = round(total_cost / 6, 2)
    
    print(f'  Set 1925-1930 | cost=${total_cost:.2f} → ${part_cost:.2f}/coin')
    for coin_yr in range(1925, 1931):  # 1925-1930
        new_rec = make_expanded_record(data, str(coin_yr), 'Standing Liberty Quarter', 'Quarter',
                                       part_cost, coin_yr - 1924, 6, parent_id)
        new_records.append(new_rec)
        print(f'    + {coin_yr} Standing Liberty Quarter')
    
    records_to_delete.append(parent_id)
    print()

# ── Summary ───────────────────────────────────────────────────────────────────
print(f'=== SUMMARY ===')
print(f'New individual records to create: {len(new_records)}')
print(f'Parent set records to delete:     {len(records_to_delete)}')
print(f'Net change to collection:         +{len(new_records) - len(records_to_delete)} records')
print()

if DRY_RUN:
    print('DRY RUN — no changes made. Set DRY_RUN = False to execute.')
else:
    print('EXECUTING...')
    # Write new records in batches of 500
    batch = db.batch()
    batch_count = 0
    created = 0
    for rec in new_records:
        new_id = str(uuid.uuid4())
        ref = col.document(new_id)
        batch.set(ref, rec)
        batch_count += 1
        created += 1
        if batch_count >= 499:
            batch.commit()
            batch = db.batch()
            batch_count = 0
    if batch_count > 0:
        batch.commit()
    print(f'Created {created} new records.')
    
    # Delete parent set records
    batch = db.batch()
    batch_count = 0
    deleted = 0
    for doc_id in records_to_delete:
        ref = col.document(doc_id)
        batch.delete(ref)
        batch_count += 1
        deleted += 1
        if batch_count >= 499:
            batch.commit()
            batch = db.batch()
            batch_count = 0
    if batch_count > 0:
        batch.commit()
    print(f'Deleted {deleted} parent set records.')
    print('Done!')
