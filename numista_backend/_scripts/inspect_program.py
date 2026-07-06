# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""Inspect the morgan_dollars program structure in Firestore."""
import firebase_admin
from firebase_admin import credentials, firestore

cred_path = r'c:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json.json'
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

doc = db.collection('global_programs').document('morgan_dollars').get()
if not doc.exists:
    print("ERROR: morgan_dollars not found in global_programs!")
else:
    data = doc.to_dict()
    coins = data.get('coins', [])
    print(f"Program: {data.get('name')}")
    print(f"Total coins: {len(coins)}")
    print("\nFirst 15 coins (id | year | name):")
    for c in coins[:15]:
        print(f"  [{c.get('id')}] year={c.get('year')} name={c.get('name')} varieties={[v.get('id') for v in c.get('varieties', [])]}")
    print("\n--- Page 1 chunk (coins 0-34) ---")
    chunk_size = -(-len(coins) // 3)
    for c in coins[:chunk_size]:
        print(f"  [{c.get('id')}] {c.get('year')} {c.get('name','')}")
