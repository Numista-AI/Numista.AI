"""
G3b diagnostic probe — read one 2002-P 50SQ coin from Eric's collection.
Fields printed: program_id, Theme/Subject, theme_subject, Title, name,
                Year, Mint Mark, Program/Series, program_series
Read-only. No writes.
"""
import os, json, sys
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "serviceAccountKey.json"
from google.cloud import firestore

# Eric's UID is his email (Firebase auth email as doc ID)
ERIC_UID = "eric.seaman@yahoo.com"
TARGET_FIELDS = [
    "program_id", "Theme/Subject", "theme_subject",
    "Title", "name", "Year", "year",
    "Mint Mark", "mint_mark", "Program/Series", "program_series",
    "import_session_id", "import_batch_id",
]

db = firestore.Client(project="studio-9101802118-8c9a8")
coins_ref = db.collection("users").document(ERIC_UID).collection("coins")

# Grab up to 20 quarters and find one that is 2002-P
docs = list(coins_ref.limit(200).stream())
found = []
for d in docs:
    data = d.to_dict() or {}
    yr = str(data.get("Year") or data.get("year") or "")
    mm = str(data.get("Mint Mark") or data.get("mint_mark") or "")
    dn = str(data.get("Denomination") or data.get("denomination") or "").lower()
    ps = str(data.get("Program/Series") or data.get("program_series") or "").lower()
    ts = str(data.get("Theme/Subject") or data.get("theme_subject") or "").lower()
    if yr == "2002" and "quarter" in dn and ("50 state" in ps or "tennessee" in ts or "state quarter" in ps):
        found.append((d.id, data))
    if len(found) >= 3:
        break

if not found:
    print("No 2002 50SQ coins found in first 200 docs — try expanding query")
    sys.exit(1)

for doc_id, data in found:
    print(f"\n=== Document ID: {doc_id[:16]}... ===")
    for f in TARGET_FIELDS:
        val = data.get(f, "<ABSENT>")
        print(f"  {f}: {val!r}")
