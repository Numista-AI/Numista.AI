"""
find_unmatched_atb_coins.py
===========================
Queries Firestore for ATB coins that have no Theme/Subject (no design text),
which prevents automatic image matching. Prints Year, Mint, Description fields
so we can manually determine which design each coin represents.
"""
import os
import re
from pathlib import Path
from collections import defaultdict

import firebase_admin
from firebase_admin import credentials, firestore

BACKEND_DIR = Path(__file__).parent
KEY_PATH = BACKEND_DIR / "serviceAccountKey.json.json"
USER_EMAIL = "jseaman1204@gmail.com"
COINS_PATH = f"users/{USER_EMAIL}/coins"

ATB_PROGRAMS = [
    "national park quarters", "america the beautiful", "atb",
    "national park", "america the beautiful quarters"
]

def get_field(d, *keys, default=""):
    for k in keys:
        v = d.get(k)
        if v and str(v).strip() not in ("", "None", "nan"):
            return str(v).strip()
    return default

def init_firebase():
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(str(KEY_PATH))
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firebase()

print("Loading Firestore coins...")
all_docs = list(db.collection(COINS_PATH).stream())
print(f"Total docs: {len(all_docs)}")

atb_coins = []
for doc in all_docs:
    d = doc.to_dict()
    prog = get_field(d, "Program/Series", "program", "Program", "series", "Series",
                     "coin_type", "type", "Type", "Theme/Subject").lower()
    prog_match = any(p in prog for p in ATB_PROGRAMS)
    if not prog_match:
        continue
    
    year = get_field(d, "Year", "year", "date", "Date")
    theme = get_field(d, "Theme/Subject", "theme", "subject", "design")
    mint = get_field(d, "Mint Mark", "mint_mark", "mintMark", "mint")
    denom = get_field(d, "Denomination", "denomination", "face_value")
    
    # Collect all non-empty fields that might describe the design
    all_fields = {}
    for k, v in d.items():
        if v and str(v).strip() not in ("", "None", "nan"):
            all_fields[k] = str(v).strip()[:80]
    
    atb_coins.append({
        "doc_id": doc.id,
        "year": year,
        "mint": mint,
        "denom": denom,
        "theme": theme,
        "program": prog,
        "all_fields": all_fields
    })

print(f"\nTotal ATB coins found: {len(atb_coins)}")

# Find coins with no theme
unmatched = [c for c in atb_coins if not c["theme"] or len(c["theme"]) < 3]
matched = [c for c in atb_coins if c["theme"] and len(c["theme"]) >= 3]

print(f"Coins WITH theme/design: {len(matched)}")
print(f"Coins WITHOUT theme/design: {len(unmatched)}")

print("\n" + "="*80)
print("UNMATCHED ATB COINS (no Theme/Subject field)")
print("="*80)
print(f"{'Doc ID':<38} {'Year':<6} {'Mint':<5} {'All Identifying Fields'}")
print("-"*80)

# Group by year+mint for cleaner display
by_year_mint = defaultdict(list)
for c in unmatched:
    by_year_mint[(c["year"], c["mint"])].append(c)

for (year, mint), coins in sorted(by_year_mint.items()):
    print(f"\n  Year={year} Mint={mint}  ({len(coins)} coin(s))")
    for c in coins[:3]:  # Show first 3 examples
        # Print all fields that might identify the design
        desc_fields = {k: v for k, v in c["all_fields"].items()
                       if k.lower() not in ("image_url_obverse", "image_url_reverse",
                                             "obverse_image_url", "reverse_image_url",
                                             "imageurl", "image", "image_url")}
        print(f"    Doc: {c['doc_id'][:36]}")
        for k, v in sorted(desc_fields.items()):
            print(f"      {k}: {v[:70]}")

print("\n" + "="*80)
print("SUMMARY OF FIELD KEYS in unmatched coins (to find hidden design fields):")
all_keys = defaultdict(int)
for c in unmatched:
    for k in c["all_fields"]:
        all_keys[k] += 1
for k, cnt in sorted(all_keys.items(), key=lambda x: -x[1]):
    print(f"  {k:<40} {cnt} coins")
