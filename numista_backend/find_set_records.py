import os, sys, uuid
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore
from datetime import datetime, timezone

creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('coins')

docs = list(col.stream())
five_coin_sets = []
ike_sets = []
steel_cent_pds = []
showpak_2024 = []
indian_head_albums = []
slq_sets = []

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
    if '5-coin set' in denom or '5 coin set' in denom or ('time capsule' in prog and qty <= 1) or 'america revisited' in prog:
        five_coin_sets.append((d.id, yr, data))
    
    # Ike Dollar set-level record
    if '1971' in yr and 'ike' in prog.replace('-','') or ('eisenhower' in prog and '1971' in yr and qty == 1 and 'set' in notes):
        ike_sets.append((d.id, yr, data))
    
    # 1943 steel cent PDS 
    if yr == '1943' and qty == 3 and ('steel' in prog or 'steel' in denom or 'pds' in notes):
        steel_cent_pds.append((d.id, yr, data))
    
    # 2024 Showpak
    if '2024' in yr and ('showpak' in prog or 'showpak' in notes) and qty >= 4:
        showpak_2024.append((d.id, yr, data))
    
    # Indian Head album 12-coin
    if 'indian head' in prog and qty == 12:
        indian_head_albums.append((d.id, yr, data))
    
    # Standing Liberty Quarter 6-coin set
    if 'standing liberty' in prog and qty == 6:
        slq_sets.append((d.id, yr, data))

print('=== 5-COIN YEAR SETS ===')
for doc_id, yr, data in five_coin_sets:
    print(f'  ID: {doc_id}')
    print(f'  Year: {yr} | Denom: {data.get("Denomination")} | Prog: {data.get("Program/Series")}')
    print(f'  Qty: {data.get("Quantity")} | Condition: {data.get("Condition")} | Cost: {data.get("Cost")}')
    print(f'  Notes: {str(data.get("Personal Notes",""))[:100]}')
    print()

print('=== IKE DOLLAR SET-LEVEL RECORDS ===')
for doc_id, yr, data in ike_sets:
    print(f'  ID: {doc_id} | Year: {yr} | Prog: {data.get("Program/Series")} | Qty: {data.get("Quantity")}')
    print()

print('=== 1943 STEEL CENT PDS SETS ===')
for doc_id, yr, data in steel_cent_pds:
    print(f'  ID: {doc_id} | Year: {yr} | Prog: {data.get("Program/Series")}')
    print(f'  Notes: {str(data.get("Personal Notes",""))[:100]}')
    print()

print('=== 2024 SHOWPAK ===')
for doc_id, yr, data in showpak_2024:
    print(f'  ID: {doc_id} | Year: {yr}')
    print(f'  Notes: {str(data.get("Personal Notes",""))[:100]}')
    print()

print('=== 12-COIN INDIAN HEAD CENT ALBUMS ===')
for doc_id, yr, data in indian_head_albums:
    print(f'  ID: {doc_id} | Year: {yr} | Prog: {data.get("Program/Series")}')
    print()

print('=== 6-COIN STANDING LIBERTY QUARTER SET ===')
for doc_id, yr, data in slq_sets:
    print(f'  ID: {doc_id} | Year: {yr} | Prog: {data.get("Program/Series")}')
    print()
