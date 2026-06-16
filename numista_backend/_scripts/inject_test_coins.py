import firebase_admin
from firebase_admin import credentials, firestore
import uuid
import time
from datetime import datetime

# Initialize Firebase (reuse existing logic from shell.py)
key_path = "serviceAccountKey.json.json"
try:
    cred = credentials.Certificate(key_path)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Auth Init Error: {e}")
    exit(1)

# Add 2 coins to guest@numista.ai
email = "guest@numista.ai"
coins_ref = db.collection(f"users/{email}/coins")

# Coin 1: 1909 Lincoln Cent (Value 50)
coin1_id = str(uuid.uuid4())
coins_ref.document(coin1_id).set({
    "id": coin1_id,
    "user_email": email,
    "year": "1909",
    "denomination": "Cent",
    "coinName": "Lincoln Cent",
    "mint_mark": "",
    "grade": "XF-40",
    "cost": 50.0,
    "value": 50.0,
    "source": "Manual Entry Test",
    "date_added": firestore.SERVER_TIMESTAMP
})

# Coin 2: 1921 Peace Dollar (Value 150)
coin2_id = str(uuid.uuid4())
coins_ref.document(coin2_id).set({
    "id": coin2_id,
    "user_email": email,
    "year": "1921",
    "denomination": "Dollar",
    "coinName": "Peace Dollar",
    "mint_mark": "",
    "grade": "AU-50",
    "cost": 150.0,
    "value": 150.0,
    "source": "Manual Entry Test",
    "date_added": firestore.SERVER_TIMESTAMP
})

print("Successfully injected 2 test coins to Firestore for guest@numista.ai.")
