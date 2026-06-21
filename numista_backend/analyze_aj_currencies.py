"""
Analysis 1 (final): AJ's Currency Collection
Parses Description field for denomination since Denomination field is empty.
"""
import json
import os
import re
from collections import Counter, defaultdict

import firebase_admin
from firebase_admin import credentials, firestore

KEY_PATH = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json.json")
USER_EMAIL = "jseaman1204@gmail.com"
CURRENCIES_PATH = f"users/{USER_EMAIL}/currency"

try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("Querying currency collection ...")
docs = list(db.collection(CURRENCIES_PATH).stream())
print(f"  -> {len(docs)} documents found")
records = [doc.to_dict() for doc in docs]

def safe_str(v, default="?"):
    if v is None:
        return default
    s = str(v).strip()
    return s if s else default

def has_image(d):
    for k in ["image_url", "imageUrl", "image_url_obverse", "obverse_image_url",
              "image", "Image", "reverse_image_url", "image_url_reverse"]:
        v = d.get(k)
        if v and str(v).strip():
            return True
    return False

def extract_denomination(d):
    """Try Denomination field first, then parse Description."""
    denom = safe_str(d.get("Denomination"), "")
    if denom and denom != "?":
        return denom
    desc = safe_str(d.get("Description"), "")
    # Look for patterns like $1, $2, $5, $10, $20, $50, $100, 5C, 10C, 15C, 25C, 50C
    m = re.search(r'\$(\d+(?:\.\d+)?)', desc)
    if m:
        val = float(m.group(1))
        return f"${int(val) if val == int(val) else val}"
    m = re.search(r'(\d+)C', desc, re.IGNORECASE)
    if m:
        return f"{m.group(1)}c"
    return "Unknown"

CURRENCY_TYPE_LABELS = {
    "federal_reserve_note": "Federal Reserve Note",
    "silver_certificate": "Silver Certificate",
    "gold_certificate": "Gold Certificate",
    "fractional_currency": "Fractional Currency",
    "treasury_note": "Treasury/Demand Note",
    "national_bank_note": "National Bank Note",
    "confederate": "Confederate Currency",
    "other": "Other / Miscellaneous",
    "?": "Unknown",
}

rows = []
for d in records:
    currency_type = safe_str(d.get("currency_type"), "other")
    rows.append({
        "denomination":    extract_denomination(d),
        "currency_type":   currency_type,
        "type_label":      CURRENCY_TYPE_LABELS.get(currency_type, currency_type),
        "year":            safe_str(d.get("Year"), "?"),
        "condition":       safe_str(d.get("Condition"), "?"),
        "cost":            safe_str(d.get("Cost"), "?"),
        "country":         safe_str(d.get("Country"), "US"),
        "description":     safe_str(d.get("Description"), ""),
        "quantity":        safe_str(d.get("Quantity"), "1"),
        "has_image":       has_image(d),
        "series_issuer":   safe_str(d.get("Series/Issuer"), ""),
        "personal_ref":    safe_str(d.get("Personal Ref #"), ""),
    })

total = len(rows)
with_img = sum(1 for r in rows if r["has_image"])
without_img = total - with_img

type_counter  = Counter(r["type_label"] for r in rows)
denom_counter = Counter(r["denomination"] for r in rows)

print("\n" + "="*70)
print("ANALYSIS 1 -- AJ'S CURRENCY COLLECTION")
print("="*70)
print(f"\nTotal currency items : {total}")
print(f"With images          : {with_img}")
print(f"Missing images       : {without_img}")

print("\n--- Breakdown by Type ---")
for t, cnt in type_counter.most_common():
    print(f"  {t:<45} {cnt}")

print("\n--- Breakdown by Denomination ---")
for d2, cnt in denom_counter.most_common():
    print(f"  {d2:<20} {cnt}")

print("\n--- Full Currency Inventory ---")
print(f"{'#':<4} {'Ref#':<6} {'Denom':<10} {'Type':<28} {'Year':<10} {'Cond':<18} {'Img?':<5} {'Cost':<12} {'Description'}")
print("-"*150)
for i, r in enumerate(rows, 1):
    print(
        f"{i:<4}"
        f"{r['personal_ref']:<6}"
        f"{r['denomination']:<10}"
        f"{r['type_label']:<28}"
        f"{r['year']:<10}"
        f"{r['condition']:<18}"
        f"{'Y' if r['has_image'] else 'N':<5}"
        f"{r['cost']:<12}"
        f"{r['description'][:70]}"
    )

print("\nDone.")
