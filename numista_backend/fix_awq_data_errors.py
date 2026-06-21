"""
fix_awq_data_errors.py
Corrects two data entry errors in AJ's AWQ coins:
1. 'Ida B. Wells' with Year=2022 or Year=2024 → Year=2025 (she's a 2025 design)
2. 'Adelina Otero-Warren' → 'Nina Otero-Warren' (wrong first name)
"""
import os, sys
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore

DRY_RUN = False  # CHANGE TO False TO APPLY

creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('coins')

print(f'MODE: {"DRY RUN" if DRY_RUN else "*** LIVE WRITE ***"}')

docs = list(col.stream())
fixes = []

for d in docs:
    data = d.to_dict() or {}
    prog = str(data.get('Program/Series', '')).lower()
    if 'women' not in prog or 'quarter' not in prog:
        continue

    theme = data.get('Theme/Subject', '')
    year  = str(data.get('Year', ''))
    updates = {}

    # Fix 1: Ida B. Wells incorrectly tagged as 2022 or 2024
    if 'ida b' in theme.lower() and year in ('2022', '2024'):
        updates['Year'] = '2025'
        print(f"  FIX YEAR: [{d.id[:8]}] '{theme}' Year {year} → 2025")

    # Fix 2: Adelina Otero-Warren → Nina Otero-Warren
    if 'adelina' in theme.lower():
        updates['Theme/Subject'] = 'Nina Otero-Warren'
        print(f"  FIX NAME: [{d.id[:8]}] '{theme}' → 'Nina Otero-Warren'")

    if updates:
        fixes.append({'id': d.id, 'updates': updates})

print(f'\nTotal fixes: {len(fixes)}')

if not DRY_RUN and fixes:
    for f in fixes:
        # Must use set(merge=True) — batch.update() misparses 'Theme/Subject' as a path
        col.document(f['id']).set(f['updates'], merge=True)
    print(f'✅ Done. {len(fixes)} records updated.')
else:
    print('DRY RUN complete. Set DRY_RUN = False to apply.')
