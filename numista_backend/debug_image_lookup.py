"""
Comprehensive debug: Check what exists in the image index and how lookups work.
"""
import os
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")

from google.cloud import firestore
import google.auth

credentials, _ = google.auth.default()
db = firestore.Client(credentials=credentials, project="studio-9101802118-8c9a8")

# 1. Count total entries and summarize
print("=== Image Index Summary ===")
all_docs = list(db.collection("coin_image_index").stream())
print(f"Total documents: {len(all_docs)}")

obverse_only = 0
reverse_only = 0
both = 0
neither = 0
programs = {}
for doc in all_docs:
    data = doc.to_dict()
    has_obv = 'obverse' in data and isinstance(data['obverse'], dict)
    has_rev = 'reverse' in data and isinstance(data['reverse'], dict)
    if has_obv and has_rev:
        both += 1
    elif has_obv:
        obverse_only += 1
    elif has_rev:
        reverse_only += 1
    else:
        neither += 1
    prog = data.get('program', 'unknown')
    programs[prog] = programs.get(prog, 0) + 1
    
print(f"  Has both obverse+reverse: {both}")
print(f"  Obverse only: {obverse_only}")
print(f"  Reverse only: {reverse_only}")
print(f"  Neither: {neither}")
print(f"\nPrograms ({len(programs)} distinct):")
for p in sorted(programs.keys()):
    print(f"  {p}: {programs[p]}")

# 2. Check entries where key has '_obverse' but doc doesn't have 'obverse' nested map
print("\n=== Mismatched keys ===")
mismatch = 0
for doc in all_docs:
    data = doc.to_dict()
    key = doc.id
    if '_obverse' in key and 'obverse' not in data:
        print(f"  Key says obverse but no 'obverse' nested map: {key}")
        print(f"    Fields: {list(data.keys())}")
        mismatch += 1
        if mismatch >= 5:
            break
    if '_reverse' in key and 'reverse' not in data:
        print(f"  Key says reverse but no 'reverse' nested map: {key}")
        print(f"    Fields: {list(data.keys())}")
        mismatch += 1
        if mismatch >= 5:
            break

if mismatch == 0:
    print("  None found — all keys match their nested maps.")

# 3. Sample a few documents to show exact structure
print("\n=== Sample Documents ===")
for doc in all_docs[:3]:
    data = doc.to_dict()
    print(f"\n  {doc.id}:")
    for k, v in data.items():
        if isinstance(v, dict):
            print(f"    {k}: (map)")
            for k2, v2 in v.items():
                val = str(v2)[:80]
                print(f"      {k2}: {val}")
        else:
            print(f"    {k}: {v}")
