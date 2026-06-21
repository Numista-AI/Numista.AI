"""
cert_deep_inspect.py
Deep inspection: pull all docs with PMG/PCGS mentions.
Print every field of each matching doc.
Also scan for ANY numeric-like patterns that could be cert numbers.
"""
import os, sys, re, json
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

pmg_docs  = []
pcgs_docs = []
cert_num_pattern = re.compile(r'\b([0-9]{6,10})\b')

for doc in raw_docs:
    d     = doc.to_dict() or {}
    # Combine ALL text fields for matching
    all_text = " ".join(str(v) for v in d.values() if v).lower()
    desc  = str(d.get("Description",""))
    cond  = str(d.get("Condition",""))

    has_pmg  = "pmg" in all_text
    has_pcgs = "pcgs" in all_text

    # Find any 6-10 digit runs in the whole doc
    cert_candidates = cert_num_pattern.findall(all_text)

    if has_pmg:
        pmg_docs.append((doc.id, d, desc, cond, cert_candidates))
    if has_pcgs:
        pcgs_docs.append((doc.id, d, desc, cond, cert_candidates))

print(f"Docs mentioning PMG:  {len(pmg_docs)}")
print(f"Docs mentioning PCGS: {len(pcgs_docs)}")

print("\n\n=== ALL PMG DOCS ===")
for doc_id, d, desc, cond, certs in pmg_docs:
    print(f"\n--- {doc_id} ---")
    print(f"  Ref#:        {d.get('Personal Ref #','')}")
    print(f"  Description: {desc}")
    print(f"  Condition:   {cond}")
    print(f"  Denom:       {d.get('Denomination','')}")
    print(f"  Year:        {d.get('Year','')}")
    print(f"  Cost:        {d.get('Cost','')}")
    if certs:
        print(f"  Numeric candidates: {certs}")

print("\n\n=== ALL PCGS DOCS ===")
for doc_id, d, desc, cond, certs in pcgs_docs:
    print(f"\n--- {doc_id} ---")
    print(f"  Ref#:        {d.get('Personal Ref #','')}")
    print(f"  Description: {desc}")
    print(f"  Condition:   {cond}")
    print(f"  Denom:       {d.get('Denomination','')}")
    print(f"  Year:        {d.get('Year','')}")
    print(f"  Cost:        {d.get('Cost','')}")
    if certs:
        print(f"  Numeric candidates: {certs}")

# Summary
print(f"\n\nSUMMARY:")
print(f"  PMG docs:  {len(pmg_docs)}")
print(f"  PCGS docs: {len(pcgs_docs)}")
print(f"  Total graded: {len(set([x[0] for x in pmg_docs] + [x[0] for x in pcgs_docs]))}")

# Check if any doc has a 6+ digit number  
with_nums = [(d_id, certs) for d_id, _, _, _, certs in pmg_docs+pcgs_docs if certs]
print(f"  Docs with any 6+ digit number: {len(with_nums)}")
for d_id, certs in with_nums[:20]:
    print(f"    {d_id}: {certs}")
