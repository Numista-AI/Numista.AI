import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json

key_path = r"C:\Users\ericd\Documents\MyVertexProject\serviceAccountKey.json.json"
cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred, {'projectId': 'studio-9101802118-8c9a8'})
db = firestore.client()

with open("result_full.json", "w") as f:
    out = {}
    for p in ["users/eric@numista.ai/coins", "users/eric.seaman@v3tees.com/coins", "coins"]:
        docs = db.collection(p).stream()
        out[p] = []
        for doc in docs:
            out[p].append({"id": doc.id, "data": doc.to_dict()})
    json.dump(out, f, indent=2)
