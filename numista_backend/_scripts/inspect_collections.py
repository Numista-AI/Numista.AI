import os, sys, google.auth
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from google.cloud import firestore
creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project="studio-9101802118-8c9a8")

coins = list(db.collection("users").document("eric.seaman@yahoo.com").collection("coins").limit(2000).stream())
print(f"Total coins: {len(coins)}")

no_year = []
has_year = 0
program_no_year = {}

for c in coins:
    d = c.to_dict() or {}
    year = str(d.get("Year", "") or "").strip()
    prog = str(d.get("Program/Series", "") or "").strip()
    cond = str(d.get("Condition", "") or "").strip()
    notes = str(d.get("Personal Notes I", "") or "").strip()
    orig  = str(d.get("Original Description from source", "") or "").strip()
    
    if year and year not in ("None", "null", "0", "", "Unknown"):
        has_year += 1
    else:
        no_year.append({
            "id": c.id,
            "program": prog,
            "cond": cond[:60],
            "notes": notes[:60],
            "orig": orig[:80],
        })
        program_no_year[prog] = program_no_year.get(prog, 0) + 1

print(f"Has year: {has_year}")
print(f"No year:  {len(no_year)}")
print()
print("Programs with missing years (top 20):")
for prog, cnt in sorted(program_no_year.items(), key=lambda x: -x[1])[:20]:
    print(f"  {cnt:3d}  {prog}")

print()
print("Sample no-year coins with text data:")
for c in no_year[:10]:
    print(f"  [{c['program'][:40]}]")
    if c["orig"]: print(f"    orig_desc: {c['orig']}")
    if c["cond"]: print(f"    condition: {c['cond']}")
    if c["notes"]: print(f"    notes:     {c['notes']}")
