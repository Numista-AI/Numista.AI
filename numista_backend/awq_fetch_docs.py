#!/usr/bin/env python3
"""
Fetch Firestore docs for the 36 AWQ coins and check coin_image_index.
Outputs: awq_coins_live.json, awq_image_index.json
"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
os.chdir(r'C:\Users\ericd\Documents\MyVertexProject\numista_backend')

from google.oauth2 import service_account
from google.cloud import firestore

SA_KEY = 'serviceAccountKey.json.json'
USER = 'jseaman1204@gmail.com'

AWQ_DOC_IDS = [
    # 2023
    '164dd6b9-e049-4856-9aec-acf21b7500bf', '1dec046e-52bf-42f8-8d3c-f08c8263c63f',
    '32c862a4-a4ce-4501-8305-848320b0081f', '33b72c4a-030e-4f53-9bb6-db18c380716a',
    '6c442551-200a-490c-ba0e-457572ae7c9a', '86d48b2f-1066-46eb-8b51-01a982bef40b',
    '8ded18a3-50ce-457f-9d4d-354d63990a98', '9a450d35-cca8-4e9d-b812-c8e5cae9b0b2',
    'a30614b8-2b63-4e2d-84ba-7325a0a34305', 'a34ce55b-846c-4b8b-a035-e2b66ed557f7',
    'c731f144-73a5-4048-bf57-7e191a547153', 'd9797ec2-5c2a-43e7-9af2-25feb6ba605d',
    'e3af3be5-2c6c-4033-8dae-46fe13ea9fd8', 'e63bb5b7-e2ea-4ce7-846d-fbecb4ba88a2',
    'ec9e51e5-050e-4cd8-bbde-5836021a9f30',
    # 2024
    '1339742c-737f-47d7-853b-50c2dc95b76b', '1bf11658-89d5-4e76-b691-5a0514425f2d',
    '259f5738-ba14-4987-ac71-8869f78bb5d2', '380064e6-44e3-49cc-83c2-3f00ef525a69',
    '45854b50-a3bc-431b-928b-fc92420b0644', '59ba65c4-fc37-4aeb-bcab-a9dcea74b1d2',
    '65bce2a8-4509-4e41-b103-62bd1a64a634', '6da29950-10fb-42b8-b8ae-6e0896170004',
    '75631af9-903f-43fc-8708-46f027a1afc0', '75748608-aff4-4b82-bbec-f842294fcc2a',
    '987e1aad-b8c0-4ef3-80a9-c40a4d483065', '9f1d0319-1267-453a-a2bc-f94c59d41118',
    '9f51e0a1-a7d2-4de4-89c0-89633abcf24e', 'be83a83f-f21a-4533-bdc7-64f4a0452e0d',
    'ce446654-0cbb-4736-a730-04f5488f98ae', 'df84b4ed-5802-4e80-9119-3ba68a6b9f2e',
    'dfcc44ff-585e-405d-aec4-442211ad1abf', 'e428e26c-3915-48c1-b061-2172eb296a0e',
    'e8ee38b9-871b-4562-85af-05eae7cf827c', 'effecf13-03c9-4a17-896c-3d4c311e68e2',
    'f9089b68-bf65-482a-b1bd-66ef105327a6',
]

creds = service_account.Credentials.from_service_account_file(SA_KEY)
db = firestore.Client(project=creds.project_id, credentials=creds)

# 1. Fetch all AWQ coin documents
print(f'Fetching {len(AWQ_DOC_IDS)} AWQ coin documents...')
coins = []
for doc_id in AWQ_DOC_IDS:
    ref = db.collection('users').document(USER).collection('coins').document(doc_id)
    snap = ref.get()
    if snap.exists:
        d = snap.to_dict()
        coins.append({
            'doc_id': doc_id,
            'year': d.get('Year') or d.get('year',''),
            'mint': d.get('Mint Mark') or d.get('mint_mark',''),
            'program': d.get('Program/Series') or d.get('program',''),
            'theme': d.get('Theme/Subject') or d.get('theme','') or d.get('Subject',''),
            'denomination': d.get('Denomination') or d.get('denomination',''),
            'condition': d.get('Condition') or d.get('condition',''),
            'image_url_obverse': d.get('image_url_obverse',''),
            'image_url_reverse': d.get('image_url_reverse',''),
            'all_keys': sorted(d.keys()),
        })
        print(f'  {doc_id[:8]} | year={d.get("Year","")} mint={d.get("Mint Mark","")} theme={d.get("Theme/Subject","?")} keys={[k for k in d.keys() if "theme" in k.lower() or "subject" in k.lower() or "program" in k.lower()]}')
    else:
        print(f'  {doc_id[:8]} MISSING')

with open('awq_coins_live.json', 'w', encoding='utf-8') as f:
    json.dump(coins, f, indent=2, ensure_ascii=False)
print(f'\nWrote {len(coins)} coin records to awq_coins_live.json')

# 2. Check coin_image_index for AWQ entries
print('\nChecking coin_image_index for AWQ...')
awq_index = []
# Try user-level index first
for coll in ['coin_image_index']:
    try:
        docs = list(db.collection('coin_image_index').stream())
        awq_docs = [d for d in docs if 'american' in d.id.lower() or 'women' in d.id.lower() or 'quarter' in d.id.lower()]
        print(f'  Global coin_image_index AWQ entries: {len(awq_docs)}')
        for d in awq_docs[:10]:
            print(f'    {d.id}')
            awq_index.append({'id': d.id, 'data': d.to_dict()})
    except Exception as e:
        print(f'  Error querying coin_image_index: {e}')

with open('awq_image_index.json', 'w', encoding='utf-8') as f:
    json.dump(awq_index, f, indent=2, ensure_ascii=False, default=str)
print(f'Wrote {len(awq_index)} index entries to awq_image_index.json')

# Show unique themes
themes = sorted(set(c['theme'] for c in coins if c['theme']))
print(f'\nUnique themes found: {len(themes)}')
for t in themes:
    print(f'  {t}')

# Show sample all_keys from first coin
if coins:
    print(f'\nAll keys in first coin doc: {coins[0]["all_keys"]}')
