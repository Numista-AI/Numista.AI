# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import firebase_admin
from firebase_admin import credentials, firestore
import uuid

key_path = "serviceAccountKey.json.json"
try:
    cred = credentials.Certificate(key_path)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Auth Init Error: {e}")
    exit(1)

email = "guest@numista.ai"
coins_ref = db.collection(f"users/{email}/coins")

coin_id = str(uuid.uuid4())
coins_ref.document(coin_id).set({
    "id": coin_id,
    "user_email": email,
    "year": "1891",
    "denomination": "Dollar",
    "coinName": "Morgan Silver Dollar",
    "program": "Morgan Silver Dollar",
    "mint_mark": "CC",
    "grade": "MS-63",
    "cost": 100.0,
    "value": 100.0,
    "source": "Manual Entry Test",
    "date_added": firestore.SERVER_TIMESTAMP
})
print("Successfully injected 1891 Morgan Silver Dollar.")
