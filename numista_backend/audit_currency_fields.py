"""
audit_currency_fields.py
Prints all unique field keys across AJ's 413 currency docs,
plus 30 full raw documents to understand the actual schema.
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
records  = [(d.id, d.to_dict() or {}) for d in raw_docs]
print(f"Total docs: {len(records)}\n")

# All unique field keys
all_keys = set()
for _, data in records:
    all_keys.update(data.keys())

print("=== ALL UNIQUE FIELD KEYS ===")
for k in sorted(all_keys):
    count = sum(1 for _, data in records if data.get(k) not in (None, "", []))
    print(f"  {k:<35} populated in {count:>4}/{len(records)} docs")

print("\n=== FIRST 30 FULL DOCUMENTS (raw) ===")
for i, (doc_id, data) in enumerate(records[:30], 1):
    print(f"\n--- Doc #{i}: {doc_id} ---")
    for k, v in sorted(data.items()):
        val = str(v)[:120]
        print(f"  {k:<30}: {val}")

# Also print docs where Year is blank
print("\n=== DOCS WHERE YEAR IS BLANK ===")
blank_yr = [(doc_id, data) for doc_id, data in records
            if not any(str(data.get(f, "")).strip() for f in ["Year","year","series_year"])]
print(f"Total blank-Year docs: {len(blank_yr)}")
for doc_id, data in blank_yr[:20]:
    desc = data.get("Description","")
    yr   = data.get("Year","")
    print(f"  {doc_id[:22]}  Year={yr!r:15}  Desc={desc[:80]!r}")
