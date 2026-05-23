import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './serviceAccountKey.json.json'
from google.cloud import firestore
db = firestore.Client(project='studio-9101802118-8c9a8')

candidates = [
    '1943_D_lincoln-cent_obverse',
    '1943_lincoln-cent_obverse',
    '1943_D_cent_obverse',
    '1943_cent_obverse',
]
print('Testing candidate keys for 1943-D penny:')
for k in candidates:
    doc = db.collection('coin_image_index').document(k).get()
    status = 'EXISTS' if doc.exists else 'MISSING'
    print(f'  {k}: {status}')
    if doc.exists:
        data = doc.to_dict()
        obv = data.get('obverse', {})
        url = str(obv.get('public_url', ''))[:80]
        print(f'    URL: {url}')

# Also check what the denomination field looks like
print()
print('Checking _F field names in the Dart code:')
