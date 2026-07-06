# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""Verify what was written to Firestore for the test user after the scan."""
import firebase_admin
from firebase_admin import credentials, firestore

cred_path = r'c:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json.json'
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Test user UID from the logs: K9Ud5RZiY0TbQzsjrh5IDf15tEF3
USER_ID = 'K9Ud5RZiY0TbQzsjrh5IDf15tEF3'

print("=== CHECKLIST ENTRIES (morgan_dollars) ===")
entries = db.collection('users').document(USER_ID).collection('checklist_entries') \
    .where('program_id', '==', 'morgan_dollars').stream()

owned_count = 0
unowned_count = 0
for doc in entries:
    data = doc.to_dict()
    status = "✅ OWNED" if data.get('owned') else "⬜ UNOWNED"
    qty = data.get('qty', 0)
    print(f"  {status} | {doc.id} | qty={qty} | notes={data.get('notes')}")
    if data.get('owned'):
        owned_count += 1
    else:
        unowned_count += 1

print(f"\nTotal owned: {owned_count}, Total unowned: {unowned_count}")

print("\n=== WISHLIST (morgan_dollars) ===")
wishlist = db.collection('users').document(USER_ID).collection('wishlist') \
    .where('program_id', '==', 'morgan_dollars').stream()

wish_count = 0
for doc in wishlist:
    wish_count += 1
    data = doc.to_dict()
    print(f"  🎯 {doc.id}")

print(f"Total wishlist items: {wish_count}")
