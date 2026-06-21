"""
Analysis 2 (corrected): AJ's Coin Image Gap Analysis
Key field for images: image_url_obverse (from schema discovery)
"""
import csv
import os
from collections import defaultdict

import firebase_admin
from firebase_admin import credentials, firestore

KEY_PATH = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json.json")
USER_EMAIL = "jseaman1204@gmail.com"
COINS_PATH = f"users/{USER_EMAIL}/coins"
CSV_OUT = r"C:\Users\ericd\Documents\MyVertexProject\AJ_Image_Gap_Report.csv"

try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("Querying coins collection (may take a moment for 4000+ docs)...")
docs = list(db.collection(COINS_PATH).stream())
print(f"  -> {len(docs)} coin documents found")

# Known image fields from schema discovery
IMAGE_FIELDS = [
    "image_url_obverse",   # primary discovered field
    "obverse_image_url",
    "image_url",
    "imageUrl",
    "image",
    "Image",
    "reverse_image_url",
    "image_url_reverse",
]

def has_image(d: dict) -> bool:
    for k in IMAGE_FIELDS:
        v = d.get(k)
        if v and str(v).strip():
            return True
    return False

def get(d, *keys, default="Unknown"):
    for k in keys:
        v = d.get(k)
        if v is not None and str(v).strip() not in ("", "None", "nan"):
            return str(v).strip()
    return default

# Aggregate per (year, denomination, program/series, mint_mark)
agg = defaultdict(lambda: {"count_missing": 0, "count_has_image": 0})
series_stats = defaultdict(lambda: {"has": 0, "missing": 0})

total_coins = 0
total_with = 0
total_without = 0

# Track image field distribution
image_field_hits = defaultdict(int)

for doc in docs:
    d = doc.to_dict()
    total_coins += 1

    img = has_image(d)
    if img:
        total_with += 1
        for k in IMAGE_FIELDS:
            v = d.get(k)
            if v and str(v).strip():
                image_field_hits[k] += 1
    else:
        total_without += 1

    year    = get(d, "Year", "year", "date", "Date")
    denom   = get(d, "Denomination", "denomination", "face_value")
    program = get(d, "Program/Series", "program", "Program", "series", "Series",
                  "coin_type", "type", "Type", "Theme/Subject")
    mint    = get(d, "Mint Mark", "mint_mark", "mintMark", "mint", default="")

    key = (year, denom, program, mint)
    if img:
        agg[key]["count_has_image"] += 1
    else:
        agg[key]["count_missing"] += 1

    series_stats[program]["has" if img else "missing"] += 1

# Write CSV
print(f"\nWriting CSV to {CSV_OUT}...")
with open(CSV_OUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Year", "Denomination", "Program/Series", "Mint Mark",
                     "Count_Missing", "Count_Has_Image"])
    for (year, denom, program, mint), counts in sorted(
        agg.items(), key=lambda x: -x[1]["count_missing"]
    ):
        writer.writerow([year, denom, program, mint,
                         counts["count_missing"], counts["count_has_image"]])
print("  -> CSV written.")

pct = (total_with / total_coins * 100) if total_coins else 0

print("\n" + "="*70)
print("ANALYSIS 2 -- AJ'S COIN IMAGE GAP ANALYSIS")
print("="*70)
print(f"\nTotal coins         : {total_coins}")
print(f"  With images       : {total_with}  ({pct:.1f}%)")
print(f"  WITHOUT images    : {total_without}  ({100-pct:.1f}%)")

print("\n--- Image field distribution (which fields are populated) ---")
for k, cnt in sorted(image_field_hits.items(), key=lambda x: -x[1]):
    print(f"  {k:<30} {cnt}")

# Top 20 missing
sorted_missing = sorted(
    [(k, v) for k, v in agg.items() if v["count_missing"] > 0],
    key=lambda x: -x[1]["count_missing"]
)
print(f"\n--- Top 20 Coin Types Missing Images ---")
print(f"{'Year':<8} {'Denom':<12} {'Program/Series':<45} {'Mint':<6} {'Missing':>8}")
print("-"*85)
for (year, denom, program, mint), counts in sorted_missing[:20]:
    print(f"{year:<8} {denom:<12} {program:<45} {mint:<6} {counts['count_missing']:>8}")

# Breakdown by series (all)
print(f"\n--- Breakdown by Program/Series (Top 40 by total coins) ---")
print(f"{'Program/Series':<50} {'Has Image':>10} {'Missing':>8} {'Coverage%':>10}")
print("-"*85)
for prog, stats in sorted(series_stats.items(),
                           key=lambda x: -(x[1]["has"] + x[1]["missing"]))[:40]:
    total_s = stats["has"] + stats["missing"]
    cov = (stats["has"] / total_s * 100) if total_s else 0
    print(f"{prog:<50} {stats['has']:>10} {stats['missing']:>8} {cov:>9.0f}%")

print("\nDone.")
