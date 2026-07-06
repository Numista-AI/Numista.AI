# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json

key_path = r"C:\Users\ericd\Documents\MyVertexProject\serviceAccountKey.json.json"
cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred, {'projectId': 'studio-9101802118-8c9a8'})
db = firestore.client()

with open("result_full.txt", "w", encoding="utf-8") as f:
    for p in ["users/eric@numista.ai/coins", "users/eric.seaman@v3tees.com/coins", "coins"]:
        docs = list(db.collection(p).stream())
        f.write(f"--- PATH: {p} ({len(docs)} documents) ---\n")
        for doc in docs:
            d = doc.to_dict()
            f.write(f"Doc ID: {doc.id}\n")
            f.write(f"  Year: {d.get('Year', 'N/A')}\n")
            f.write(f"  Denomination: {d.get('Denomination', 'N/A')}\n")
            f.write(f"  Condition: {d.get('Condition', 'N/A')}\n")
            f.write(f"  AI Estimated Value: {d.get('AI Estimated Value', 'N/A')}\n")
        f.write("\n")
