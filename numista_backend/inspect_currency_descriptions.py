"""
inspect_currency_descriptions.py
Print ALL currency documents' Description field (and all fields)
so we can see exactly what text/patterns contain PMG/PCGS data.
"""
import os, sys, json
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KEY_PATH   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "serviceAccountKey.json.json")
USER_EMAIL = "jseaman1204@gmail.com"
COLLECTION = f"users/{USER_EMAIL}/currency"
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", KEY_PATH)

import firebase_admin
from firebase_admin import credentials, firestore as fs_admin
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(credentials.Certificate(KEY_PATH))

db = fs_admin.client()
raw_docs = list(db.collection(COLLECTION).stream())
print(f"Total docs: {len(raw_docs)}\n")

# Print every description (truncated at 400 chars) plus all field values
print("="*80)
keywords = ["pmg", "pcgs", "cert", "graded", "grade", "paper money guaranty",
            "ngc", "anacs", "serial", "#", "number"]

# First: print ALL docs that mention any keyword
print("DOCS WITH GRADING/CERT KEYWORDS:")
print("="*80)
graded_docs = []
for doc in raw_docs:
    d = doc.to_dict() or {}
    desc = str(d.get("Description","")).lower()
    cond = str(d.get("Condition","")).lower()
    combined = desc + " " + cond
    if any(k in combined for k in keywords):
        graded_docs.append((doc.id, d))
        print(f"\n--- {doc.id} ---")
        for k, v in sorted(d.items()):
            vs = str(v)
            print(f"  {k:<30}: {vs[:250]}")

print(f"\nTotal docs with keywords: {len(graded_docs)}")

# Also dump first 20 docs fully regardless
print("\n\n" + "="*80)
print("FIRST 20 DOCS (all fields, full):")
print("="*80)
for doc in raw_docs[:20]:
    d = doc.to_dict() or {}
    print(f"\n--- {doc.id} ---")
    for k, v in sorted(d.items()):
        vs = str(v)
        print(f"  {k:<30}: {vs[:400]}")
