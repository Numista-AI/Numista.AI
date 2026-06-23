#!/usr/bin/env python3
"""
Diagnostic: Fetch all 28 unclassified coins from Firestore and show their real fields.
"""
import csv
import json
import os
import firebase_admin
from firebase_admin import credentials, firestore

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SA_KEY = os.path.join(SCRIPT_DIR, "serviceAccountKey.json.json")
GAP_CSV = os.path.join(SCRIPT_DIR, "jseaman_image_gaps.csv")
PASS1_LOG = os.path.join(SCRIPT_DIR, "reverse_enrichment_log.json")
PASS2_LOG = os.path.join(SCRIPT_DIR, "reverse_enrichment_pass2_log.json")
USER_EMAIL = "jseaman1204@gmail.com"

# Init Firestore
cred = credentials.Certificate(SA_KEY)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Load already-processed
processed_ids = set()
for log_path in [PASS1_LOG, PASS2_LOG]:
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            try:
                for r in json.load(f):
                    if r.get("result") == "success":
                        processed_ids.add(r["doc_id"])
            except json.JSONDecodeError:
                pass

# Find MISSING_REVERSE with blank denom+program
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

print(f"Found {len(candidates)} blank denom+program MISSING_REVERSE coins\n")

# Fetch each from Firestore
results = []
for doc_id in candidates:
    ref = db.collection("users").document(USER_EMAIL).collection("coins").document(doc_id)
    snap = ref.get()
    if not snap.exists:
        print(f"  MISSING: {doc_id}")
        results.append({"doc_id": doc_id, "status": "not_found"})
        continue

    data = snap.to_dict()
    # Extract all relevant fields - try multiple key variations
    result = {
        "doc_id": doc_id,
        "denomination": data.get("denomination") or data.get("Denomination") or "",
        "program": data.get("program") or data.get("Program/Series") or data.get("program_series") or "",
        "year": str(data.get("year") or data.get("Year") or ""),
        "mint_mark": data.get("mint_mark") or data.get("Mint Mark") or data.get("mint") or "",
        "theme": data.get("theme") or data.get("Theme/Subject") or data.get("theme_subject") or "",
        "image_url_obverse": (data.get("image_url_obverse") or "")[:80],
        "image_url_reverse": (data.get("image_url_reverse") or "")[:80],
        "all_keys": list(data.keys()),
    }
    results.append(result)
    has_rev = bool(result["image_url_reverse"])
    has_obv = bool(result["image_url_obverse"])
    print(f"  {doc_id}")
    print(f"    denom={result['denomination']!r}  prog={result['program']!r}  year={result['year']}  mint={result['mint_mark']}")
    print(f"    theme={result['theme']!r}")
    print(f"    has_obverse={has_obv}  has_reverse={has_rev}")
    if not result["denomination"] and not result["program"] and not result["theme"]:
        print(f"    [ALL BLANK] keys: {result['all_keys'][:10]}")
    print()

# Save
with open("unclassified_firestore_data.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nSaved to unclassified_firestore_data.json")

# Summary
all_blank = [r for r in results if r.get("status") != "not_found" and not r.get("denomination") and not r.get("program") and not r.get("theme")]
has_some = [r for r in results if r.get("status") != "not_found" and (r.get("denomination") or r.get("program") or r.get("theme"))]
print(f"\nSummary:")
print(f"  All fields blank (truly unidentifiable): {len(all_blank)}")
print(f"  Has at least one field (can be classified): {len(has_some)}")
