"""
Add missing PCS Miscellaneous coins that are confirmed not in AJ's collection:
1. 1921-D Morgan Silver Dollar ('The only Denver Mint Morgan silver dollar') - $139
2. 1878-S Morgan Silver Dollar (first SF Morgan) - part of $259 pair
3. 1921-S Morgan Silver Dollar (last SF Morgan) - part of $259 pair
"""
import os, sys, uuid
from datetime import datetime, timezone

os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore

creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('coins')

# First verify these aren't already in the collection
docs = list(col.stream())

has_1921d = any(
    str(d.to_dict().get('Year','')).startswith('1921') and
    d.to_dict().get('Mint Mark','') == 'D' and
    'Morgan' in str(d.to_dict().get('Program/Series',''))
    for d in docs
)
has_1878s = any(
    str(d.to_dict().get('Year','')).startswith('1878') and
    d.to_dict().get('Mint Mark','') == 'S' and
    'Morgan' in str(d.to_dict().get('Program/Series',''))
    for d in docs
)
has_1921s = any(
    str(d.to_dict().get('Year','')).startswith('1921') and
    d.to_dict().get('Mint Mark','') == 'S' and
    'Morgan' in str(d.to_dict().get('Program/Series',''))
    for d in docs
)

print(f'1921-D Morgan already in collection: {has_1921d}')
print(f'1878-S Morgan already in collection: {has_1878s}')
print(f'1921-S Morgan already in collection: {has_1921s}')

coins_to_add = []

if not has_1921d:
    coins_to_add.append({
        'Year': '1921',
        'Mint Mark': 'D',
        'Program/Series': 'Morgan Silver Dollar',
        'Denomination': 'Silver Dollar',
        'Country': 'USA',
        'Metal Content': 'Silver',
        'Condition': 'Ungraded',
        'Purchase Cost': '$139.00',
        'Retailer/Website': 'PCS Stamps & Coins',
        'Personal Notes': 'The only Denver Mint Morgan Silver Dollar. Purchased from PCS Stamps & Coins (Miscellaneous Shipments). See PCS tracking file: Miscellaneous shupments.xlsx.',
        'source': 'excel_import',
        'source_file': 'PCS Folder/Miscellaneous shupments.xlsx',
        'import_batch': 'pcs_misc_2026-06-21',
    })
    print('Will add: 1921-D Morgan Silver Dollar')

if not has_1878s:
    coins_to_add.append({
        'Year': '1878',
        'Mint Mark': 'S',
        'Program/Series': 'Morgan Silver Dollar',
        'Denomination': 'Silver Dollar',
        'Country': 'USA',
        'Metal Content': 'Silver',
        'Condition': 'Ungraded',
        'Purchase Cost': '$129.50',  # half of $259
        'Retailer/Website': 'PCS Stamps & Coins',
        'Personal Notes': 'First San Francisco Mint Morgan Silver Dollar (1878-S was the first year). Purchased as a pair with 1921-S (last SF Morgan). Total set cost: $259.00. PCS Stamps & Coins Miscellaneous Shipments.',
        'source': 'excel_import',
        'source_file': 'PCS Folder/Miscellaneous shupments.xlsx',
        'import_batch': 'pcs_misc_2026-06-21',
    })
    print('Will add: 1878-S Morgan Silver Dollar')

if not has_1921s:
    coins_to_add.append({
        'Year': '1921',
        'Mint Mark': 'S',
        'Program/Series': 'Morgan Silver Dollar',
        'Denomination': 'Silver Dollar',
        'Country': 'USA',
        'Metal Content': 'Silver',
        'Condition': 'Ungraded',
        'Purchase Cost': '$129.50',  # half of $259
        'Retailer/Website': 'PCS Stamps & Coins',
        'Personal Notes': 'Last San Francisco Mint Morgan Silver Dollar (1921-S was the last year). Purchased as a pair with 1878-S (first SF Morgan). Total set cost: $259.00. PCS Stamps & Coins Miscellaneous Shipments.',
        'source': 'excel_import',
        'source_file': 'PCS Folder/Miscellaneous shupments.xlsx',
        'import_batch': 'pcs_misc_2026-06-21',
    })
    print('Will add: 1921-S Morgan Silver Dollar')

if coins_to_add:
    batch = db.batch()
    for rec in coins_to_add:
        rec['timestamp'] = datetime.now(timezone.utc)
        new_id = str(uuid.uuid4())
        ref = col.document(new_id)
        batch.set(ref, rec)
        print(f'  Adding {rec["Year"]}-{rec.get("Mint Mark","")} {rec["Program/Series"]} as ID={new_id[:8]}...')
    batch.commit()
    print(f'\nAdded {len(coins_to_add)} coins.')
else:
    print('\nAll coins already in collection — nothing to add.')
