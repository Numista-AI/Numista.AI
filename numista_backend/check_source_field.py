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

# Find Kennedy Half Dollars with source_file  
print('Kennedy Half Dollars with source_file:')
for d in docs:
    data = d.to_dict() or {}
    sf = data.get('source_file', '')
    prog = str(data.get('Program/Series', ''))
    if sf and 'Kennedy' in prog:
        yr = data.get('Year', '')
        src = data.get('source', '')
        inv = data.get('Invoice No.', '')
        cost = data.get('Cost', '')
        print(f'  ID={d.id[:12]}  Year={yr}  source={repr(src)}')
        print(f'  source_file={repr(sf[:60])}')
        print(f'  Invoice={inv}  Cost={cost}')
        print()

# Show all distinct source values
print()
sources = {}
for d in docs:
    data = d.to_dict() or {}
    src = str(data.get('source', '')).strip()
    has_sf = bool(data.get('source_file', ''))
    if src:
        key = (src, has_sf)
        sources[key] = sources.get(key, 0) + 1

print('Distinct source values (source, has_source_file) -> count:')
for (src, has_sf), cnt in sorted(sources.items()):
    print(f'  {repr(src):35s}  has_sf={has_sf}  count={cnt}')
