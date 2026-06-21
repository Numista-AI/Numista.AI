import os, sys
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore
creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('coins')
docs = list(col.stream())
results = []
for d in docs:
    data = d.to_dict() or {}
    prog = str(data.get('Program/Series', '')).lower()
    if 'women' in prog and 'quarter' in prog:
        results.append({
            'year': data.get('Year'),
            'theme': data.get('Theme/Subject', ''),
            'mint': data.get('Mint Mark', ''),
            'id': d.id
        })
results.sort(key=lambda x: (str(x['year']), str(x['theme'])))
seen = set()
for r in results:
    key = (r['year'], r['theme'])
    if key not in seen:
        seen.add(key)
        print(f"  {r['year']} | theme='{r['theme']}' | mint={r['mint']}")
print(f"\nTotal AWQ coins: {len(results)}")
print(f"Unique (year, theme) combos: {len(seen)}")
