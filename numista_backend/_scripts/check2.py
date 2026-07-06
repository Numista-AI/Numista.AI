# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

key_path = r"C:\Users\ericd\Documents\MyVertexProject\serviceAccountKey.json.json"
cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred, {'projectId': 'studio-9101802118-8c9a8'})
db = firestore.client()

with open("result.txt", "w") as f:
    for p in ["users/eric@numista.ai/coins", "users/eric.seaman@v3tees.com/coins", "coins"]:
        count = sum(1 for _ in db.collection(p).limit(1).stream())
        f.write(f"{p}: {count}\n")
