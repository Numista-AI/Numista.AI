import os, sys
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore

creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('coins')

docs = list(col.stream())
multi_qty = []
for d in docs:
    data = d.to_dict() or {}
    qty_raw = data.get('Quantity', '')
    try:
        qty = int(float(str(qty_raw))) if qty_raw not in ('', None) else 1
    except:
        qty = 0
    if qty > 1:
        multi_qty.append((qty, d.id, data))

multi_qty.sort(reverse=True)

print(f'Records with Quantity > 1: {len(multi_qty)}')
print()
for qty, doc_id, data in multi_qty:
    yr = str(data.get('Year', '')).replace('.0', '').strip()
    prog = data.get('Program/Series', '[NONE]')
    denom = data.get('Denomination', '[NONE]')
    cond = data.get('Condition', '')
    notes = str(data.get('Personal Notes', ''))[:80]
    print(f'  Qty={qty:3d}  Year={yr:12s}  {prog} | {denom} | {cond}')
    if notes:
        print(f'           Notes: {notes}')
    print()
