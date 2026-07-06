# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
Generate a comprehensive CSV of ALL coins in the coin_image_index (what we HAVE)
vs. ALL coins in Eric's collection (what we NEED), and produces a gap report.
"""
import os
import csv
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")

from google.cloud import firestore
import google.auth

credentials, _ = google.auth.default()
db = firestore.Client(credentials=credentials, project="studio-9101802118-8c9a8")

# ── 1. Load the full coin_image_index ──────────────────────────────────────────
print("Loading coin_image_index...")
index_docs = list(db.collection("coin_image_index").stream())
print(f"  Total index docs: {len(index_docs)}")

# Build a lookup: program -> list of (year, mint, side, public_url, attribution)
index_rows = []
index_keys = set()
for doc in index_docs:
    d = doc.to_dict()
    key = doc.id
    year = d.get("year", "")
    mint = d.get("mint") or ""
    program = d.get("program", "")
    subject = d.get("subject") or ""
    # Each doc has either 'obverse' or 'reverse' nested map
    for side in ["obverse", "reverse"]:
        if side in d and isinstance(d[side], dict):
            url = d[side].get("public_url", "")
            attr = d[side].get("attribution", "")
            tier = d[side].get("source_tier", "")
            label = d[side].get("source_label", "")
            index_rows.append({
                "doc_key": key,
                "year": year,
                "mint": mint,
                "program": program,
                "subject": subject,
                "side": side,
                "public_url": url,
                "attribution": attr,
                "source_tier": tier,
                "source_label": label,
            })
            index_keys.add(f"{year}|{program}|{side}")

# ── 2. Load Eric's coins ───────────────────────────────────────────────────────
print("Loading Eric's coins...")
eric_coins = list(db.collection("users").document("eric.seaman@yahoo.com").collection("coins").stream())
print(f"  Total Eric coins: {len(eric_coins)}")

# ── 3. For each Eric coin, check if we have a reference image ─────────────────
gap_rows = []
have_rows = []

for c in eric_coins:
    d = c.to_dict()
    year = str(d.get("Year", "")).strip().replace(".0", "")
    mint = str(d.get("Mint Mark", "")).strip()
    program_raw = str(d.get("Program/Series", "")).strip()
    denom = str(d.get("Denomination", "")).strip()
    theme = str(d.get("Theme/Subject", "")).strip()
    condition = str(d.get("Condition", "")).strip()
    personal_obv = str(d.get("image_url_obverse", "")).strip()
    personal_rev = str(d.get("image_url_reverse", "")).strip()

    # Normalize program to slug (mirrors CoinImageService logic)
    program_map = {
        "american silver eagle": "american-eagle-silver",
        "american eagle silver dollar": "american-eagle-silver",
        "morgan silver dollar": "morgan-dollar",
        "morgan dollar": "morgan-dollar",
        "peace dollar": "peace-dollar",
        "kennedy half dollar": "kennedy-half-dollar",
        "50 state quarters": "50-state-quarters",
        "state quarters": "50-state-quarters",
        "presidential dollar": "presidential-dollars",
        "presidential dollars": "presidential-dollars",
        "sacagawea dollar": "native-american-dollar",
        "native american dollar": "native-american-dollar",
        "american women quarters": "american-women-quarters",
        "america the beautiful": "america-the-beautiful",
        "american innovation": "american-innovation",
        "eisenhower dollar": "dollar",
        "lincoln cent": "lincoln-cent",
        "jefferson nickel": "jefferson-nickel",
        "roosevelt dime": "dime",
        "walking liberty half dollar": "walking-liberty",
        "walking liberty": "walking-liberty",
        "buffalo nickel": "buffalo-nickel",
        "mercury dime": "mercury-dime",
        "saint-gaudens double eagle": "saint-gaudens",
        "saint gaudens": "saint-gaudens",
        "american liberty": "american-liberty",
        "commemorative": "commemorative",
        "quarter": "quarter",
        "half dollar": "kennedy-half-dollar",
        "dollar": "dollar",
        "dime": "dime",
        "nickel": "nickel",
        "cent": "lincoln-cent",
    }
    program_slug = None
    raw_lower = program_raw.lower()
    for k, v in sorted(program_map.items(), key=lambda x: -len(x[0])):
        if k in raw_lower:
            program_slug = v
            break
    if not program_slug:
        denom_lower = denom.lower().replace("$", "").strip()
        denom_map = {"1": "dollar", "0.50": "kennedy-half-dollar", "0.25": "quarter", "0.10": "dime", "0.05": "nickel", "0.01": "lincoln-cent"}
        program_slug = denom_map.get(denom_lower, "unknown")

    # Check image index for this coin
    has_obv_ref = f"{year}|{program_slug}|obverse" in index_keys
    has_rev_ref = f"{year}|{program_slug}|reverse" in index_keys

    row = {
        "coin_id": c.id,
        "year": year,
        "mint_mark": mint,
        "program_series": program_raw,
        "program_slug": program_slug,
        "theme_subject": theme,
        "denomination": denom,
        "condition": condition,
        "personal_obverse_url": personal_obv,
        "personal_reverse_url": personal_rev,
        "has_personal_obverse": "YES" if personal_obv else "NO",
        "has_personal_reverse": "YES" if personal_rev else "NO",
        "has_ref_obverse_in_index": "YES" if has_obv_ref else "NO",
        "has_ref_reverse_in_index": "YES" if has_rev_ref else "NO",
        "obverse_status": "personal" if personal_obv else ("ref_index" if has_obv_ref else "MISSING"),
        "reverse_status": "personal" if personal_rev else ("ref_index" if has_rev_ref else "MISSING"),
    }

    if row["obverse_status"] == "MISSING" or row["reverse_status"] == "MISSING":
        gap_rows.append(row)
    else:
        have_rows.append(row)

# ── 4. Write CSVs ──────────────────────────────────────────────────────────────
all_fieldnames = [
    "coin_id", "year", "mint_mark", "program_series", "program_slug",
    "theme_subject", "denomination", "condition",
    "personal_obverse_url", "personal_reverse_url",
    "has_personal_obverse", "has_personal_reverse",
    "has_ref_obverse_in_index", "has_ref_reverse_in_index",
    "obverse_status", "reverse_status",
]

with open("_scripts/eric_image_gap_report.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=all_fieldnames)
    w.writeheader()
    w.writerows(gap_rows + have_rows)

index_fieldnames = ["doc_key", "year", "mint", "program", "subject", "side", "public_url", "attribution", "source_tier", "source_label"]
with open("_scripts/image_index_full.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=index_fieldnames)
    w.writeheader()
    w.writerows(index_rows)

print(f"\n=== SUMMARY ===")
print(f"Eric's collection: {len(eric_coins)} coins")
print(f"Coins fully covered (obv + rev): {len(have_rows)}")
print(f"Coins with at least one MISSING image: {len(gap_rows)}")
print(f"\nMISSING breakdown:")
missing_obv = sum(1 for r in gap_rows if r["obverse_status"] == "MISSING")
missing_rev = sum(1 for r in gap_rows if r["reverse_status"] == "MISSING")
print(f"  Missing obverse: {missing_obv}")
print(f"  Missing reverse: {missing_rev}")
print(f"\nReference index: {len(index_docs)} docs / {len(index_rows)} images")

# ── 5. Check specifically for 2025 Silver Eagle ────────────────────────────────
print(f"\n=== 2025 Silver Eagle in index ===")
silver_2025 = [r for r in index_rows if "american-eagle-silver" in r["program"] and r["year"] == "2025"]
for r in silver_2025:
    print(f"  {r['doc_key']}: {r['side']} -> {r['public_url'][:80]}")
if not silver_2025:
    print("  NOT FOUND in index")

print(f"\nCSVs written:")
print(f"  _scripts/eric_image_gap_report.csv  ({len(gap_rows + have_rows)} rows)")
print(f"  _scripts/image_index_full.csv       ({len(index_rows)} rows)")
