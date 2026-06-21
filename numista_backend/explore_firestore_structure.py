"""
Explore Firestore structure for jseaman1204@gmail.com
to find currencies and any other subcollections.
"""
import os
import firebase_admin
from firebase_admin import credentials, firestore

KEY_PATH = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json.json")
USER_EMAIL = "jseaman1204@gmail.com"

try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 1. List all subcollections under users/jseaman1204@gmail.com
user_ref = db.document(f"users/{USER_EMAIL}")
print(f"Checking user doc: users/{USER_EMAIL}")
try:
    user_doc = user_ref.get()
    print(f"  User doc exists: {user_doc.exists}")
    if user_doc.exists:
        print(f"  User doc fields: {sorted(user_doc.to_dict().keys()) if user_doc.to_dict() else 'empty'}")
except Exception as e:
    print(f"  Error: {e}")

print("\nListing subcollections of users/{USER_EMAIL}:")
try:
    subcols = list(user_ref.collections())
    for sc in subcols:
        print(f"  Subcollection: {sc.id}")
        # Count docs in each
        try:
            docs = list(sc.limit(3).stream())
            print(f"    Sample doc count (limit 3): {len(docs)}")
            if docs:
                d = docs[0].to_dict()
                print(f"    First doc fields: {sorted(d.keys())}")
        except Exception as e2:
            print(f"    Error counting: {e2}")
except Exception as e:
    print(f"  Error listing subcollections: {e}")

# 2. Try alternate currency paths
alt_paths = [
    f"users/{USER_EMAIL}/currency",
    f"users/{USER_EMAIL}/paper_money",
    f"users/{USER_EMAIL}/banknotes",
    f"users/{USER_EMAIL}/notes",
    f"currencies",
    f"paper_money",
]
print("\nChecking alternate paths:")
for path in alt_paths:
    try:
        docs = list(db.collection(path).limit(2).stream())
        print(f"  {path}: {len(docs)} docs")
        if docs:
            print(f"    Fields: {sorted(docs[0].to_dict().keys())}")
    except Exception as e:
        print(f"  {path}: Error - {e}")

# 3. Try top-level collections
print("\nListing top-level collections:")
try:
    cols = list(db.collections())
    for c in cols:
        print(f"  {c.id}")
except Exception as e:
    print(f"  Error: {e}")

print("\nDone.")
