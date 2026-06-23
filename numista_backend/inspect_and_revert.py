#!/usr/bin/env python3
"""
Inspect full Firestore documents for the 28 blank coins.
Shows all fields including Country, notes, and the obverse image URL.
Also reverts the bad image upload for doc 4d7dcedd.
"""
import csv
import json
import os
import firebase_admin
from firebase_admin import credentials, firestore

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SA_KEY = os.path.join(SCRIPT_DIR, "serviceAccountKey.json.json")
GAP_CSV = os.path.join(SCRIPT_DIR, "jseaman_image_gaps.csv")
USER_EMAIL = "jseaman1204@gmail.com"

# Init Firestore
cred = credentials.Certificate(SA_KEY)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Find candidates
candidates = []
with open(GAP_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row.get("status", "").strip().upper() != "MISSING_REVERSE":
            continue
        doc_id = row.get("doc_id", "").strip()
        denom = row.get("denomination", "").strip()
        program = row.get("program", "").strip()
        if not denom and not program:
            candidates.append(doc_id)

print(f"Checking {len(candidates)} blank coins...\n")

# The bad one that got a wrong image uploaded
BAD_DOC = "4d7dcedd-9637-44ff-b833-d42b40be151d"

for doc_id in candidates:
    ref = db.collection("users").document(USER_EMAIL).collection("coins").document(doc_id)
    snap = ref.get()
    if not snap.exists:
        continue
    data = snap.to_dict()

    # Extract year + country + all keys
    year = str(data.get("year") or data.get("Year") or "")
    country = data.get("Country") or data.get("country") or ""
    obv = data.get("image_url_obverse") or ""
    rev = data.get("image_url_reverse") or ""
    notes = data.get("notes") or data.get("Notes") or data.get("description") or ""
    image_source = data.get("image_source") or ""

    print(f"  {doc_id}")
    print(f"    year={year}  country={country!r}  image_source={image_source!r}")
    print(f"    notes={notes!r}")
    print(f"    obverse_url={obv[-60:] if obv else 'NONE'}")
    print(f"    reverse_url={rev[-60:] if rev else 'NONE'}")
    # Show all non-empty fields
    non_empty = {k: v for k, v in data.items() if v and k not in
                 ['created_at', 'user_email', 'inventoryStatus', 'Purchase Date',
                  'restore_at', 'image_source', 'image_updated_at', 'Condition',
                  'Country', 'Melt Value', 'normalized_at', 'ai_value_confidence',
                  'restore_source', 'image_url_obverse', 'image_url_reverse']}
    if non_empty:
        print(f"    other_fields: {non_empty}")
    print()

    # Revert the bad upload
    if doc_id == BAD_DOC:
        print(f"  *** REVERTING bad image for {BAD_DOC} ***")
        ref.update({
            "image_url_reverse": firestore.DELETE_FIELD,
            "image_source_reverse": firestore.DELETE_FIELD,
        })
        print(f"  *** Cleared image_url_reverse and image_source_reverse ***\n")
