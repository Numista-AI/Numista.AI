import os, sys
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore
creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')

# Check AJ's currency sub-collection structure
user_path = 'users/jseaman1204@gmail.com'
user_doc = db.document(user_path).get()
print(f'User doc exists: {user_doc.exists}')

# Try sub-collections
try:
    curr_col = db.collection(f'{user_path}/currency')
    curr_docs = list(curr_col.limit(5).stream())
    print(f'\nCurrency sub-collection docs: {len(curr_docs)} (showing up to 5)')
    for d in curr_docs:
        data = d.to_dict() or {}
        print(f'\n  ID: {d.id[:12]}...')
        for k, v in sorted(data.items()):
            print(f'    {repr(k):35s}: {repr(str(v)[:60])}')
except Exception as e:
    print(f'Currency collection error: {e}')

# Also check the review queue / coins with item_type='paper_currency'
print('\n--- Coins collection paper_currency items ---')
coins_col = db.collection(f'{user_path}/coins')
paper_money = []
for d in coins_col.stream():
    data = d.to_dict() or {}
    if data.get('item_type') == 'paper_currency' or 'note' in str(data.get('Denomination','')).lower():
        paper_money.append((d.id, data))
        if len(paper_money) >= 5:
            break

print(f'Paper currency items found in coins collection: {len(paper_money)} (showing up to 5)')
for doc_id, data in paper_money:
    print(f'\n  ID: {doc_id[:12]}...')
    print(f'  Year: {data.get("Year")} | Program: {data.get("Program/Series")} | Denom: {data.get("Denomination")}')
    print(f'  item_type: {data.get("item_type")} | image_url_obverse: {bool(data.get("image_url_obverse"))}')
