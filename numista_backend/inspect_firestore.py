"""
Inspect actual Firestore doc structure
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import firebase_admin
from firebase_admin import credentials, firestore

CRED_PATH = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json.json"
PROJECT_ID = "studio-9101802118-8c9a8"

cred = credentials.Certificate(CRED_PATH)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {'projectId': PROJECT_ID})
db = firestore.client()

print("=== ERIC - first 3 docs ===")
docs = db.collection('users').document('eric@numista.ai').collection('coins').limit(3).stream()
for doc in docs:
    d = doc.to_dict()
    print(f"\nDoc ID: {doc.id}")
    for k, v in sorted(d.items()):
        val = str(v)
        print(f"  {k}: {val[:120]}")

print()
print("=== JSEAMAN - first 3 docs ===")
docs = db.collection('users').document('jseaman1204@gmail.com').collection('coins').limit(3).stream()
for doc in docs:
    d = doc.to_dict()
    print(f"\nDoc ID: {doc.id}")
    for k, v in sorted(d.items()):
        val = str(v)
        print(f"  {k}: {val[:120]}")
