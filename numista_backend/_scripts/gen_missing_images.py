"""
gen_missing_images.py
Analyzes jseaman1204@gmail.com's coin collection against the Firestore image
index and writes a CSV of coins that have no reference image yet.
"""

import firebase_admin
from firebase_admin import credentials, firestore as fb_firestore
import csv
import re
import sys
from collections import defaultdict

# ── Init ─────────────────────────────────────────────────────────────
cred = credentials.Certificate("serviceAccountKey.json.json")
firebase_admin.initialize_app(cred)
db = fb_firestore.client()

# ── Load entire image index into memory (paginated) ──────────────────
print("Loading image index...", flush=True)
index_docs = set()
col = db.collection("coin_image_index")
last_doc = None
PAGE = 500
while True:
    q = col.order_by("__name__").limit(PAGE)
    if last_doc:
        q = q.start_after(last_doc)
    page = list(q.stream())
    if not page:
        break
    for doc in page:
        index_docs.add(doc.id)
    last_doc = page[-1]
    if len(page) < PAGE:
        break
print(f"  {len(index_docs)} index entries loaded", flush=True)

# ── Key-resolution mirrors coin_image_service.dart ───────────────────
PROGRAM_MAP = {
    "silver eagle": "american-eagle-silver",
    "american eagle silver": "american-eagle-silver",
    "gold eagle": "american-eagle-gold",
    "american eagle gold": "american-eagle-gold",
    "platinum eagle": "american-eagle-platinum",
    "american eagle platinum": "american-eagle-platinum",
    "palladium eagle": "american-eagle-palladium",
    "state quarter": "50-state-quarters",
    "50 state": "50-state-quarters",
    "50-state": "50-state-quarters",
    "statehood quarter": "50-state-quarters",
    "american women": "american-women-quarters",
    "women quarter": "american-women-quarters",
    "america the beautiful": "america-the-beautiful",
    "national park": "america-the-beautiful",
    "american innovation": "american-innovation",
    "presidential dollar": "presidential-dollars",
    "president dollar": "presidential-dollars",
    "native american": "native-american-dollar",
    "sacagawea": "native-american-dollar",
    "kennedy": "kennedy-half-dollar",
    "half dollar": "kennedy-half-dollar",
    "morgan": "morgan-dollar",
    "peace dollar": "peace-dollar",
    "lincoln": "lincoln-cent",
    "wheat": "lincoln-cent",
    "jefferson": "jefferson-nickel",
    "buffalo nickel": "buffalo-nickel",
    "indian head nickel": "buffalo-nickel",
    "mercury dime": "mercury-dime",
    "winged liberty": "mercury-dime",
    "barber": "barber",
    "saint gaudens": "saint-gaudens",
    "st. gaudens": "saint-gaudens",
    "walking liberty": "walking-liberty",
    "franklin": "franklin-half-dollar",
    "bicentennial": "bicentennial",
    "commemorative": "commemorative",
    "quarter": "quarter",
    "dollar": "dollar",
    "dime": "dime",
    "nickel": "nickel",
    "cent": "cent",
    "penny": "cent",
}

SUBJECT_PROGRAMS = {
    "50-state-quarters", "american-women-quarters", "presidential-dollars",
    "native-american-dollar", "america-the-beautiful", "american-innovation",
}

STATE_SLUG_MAP = {
    "delaware": "delaware", "pennsylvania": "pennsylvania", "new jersey": "new-jersey",
    "georgia": "georgia", "connecticut": "connecticut", "massachusetts": "massachusetts",
    "maryland": "maryland", "south carolina": "south-carolina",
    "new hampshire": "new-hampshire", "virginia": "virginia",
    "new york": "new-york", "north carolina": "north-carolina",
    "rhode island": "rhode-island", "vermont": "vermont", "kentucky": "kentucky",
    "tennessee": "tennessee", "ohio": "ohio", "louisiana": "louisiana",
    "indiana": "indiana", "mississippi": "mississippi", "illinois": "illinois",
    "alabama": "alabama", "maine": "maine", "missouri": "missouri",
    "arkansas": "arkansas", "michigan": "michigan", "florida": "florida",
    "texas": "texas", "iowa": "iowa", "wisconsin": "wisconsin",
    "california": "california", "minnesota": "minnesota", "oregon": "oregon",
    "kansas": "kansas", "west virginia": "west-virginia", "nevada": "nevada",
    "nebraska": "nebraska", "colorado": "colorado",
    "north dakota": "north-dakota", "south dakota": "south-dakota",
    "montana": "montana", "washington": "washington", "idaho": "idaho",
    "wyoming": "wyoming", "utah": "utah", "oklahoma": "oklahoma",
    "new mexico": "new-mexico", "arizona": "arizona",
    "alaska": "alaska", "hawaii": "hawaii",
    # Presidential dollars
    "george washington": "george-washington", "john adams": "john-adams",
    "thomas jefferson": "thomas-jefferson", "james madison": "james-madison",
    "james monroe": "james-monroe", "john quincy adams": "john-quincy-adams",
    "andrew jackson": "andrew-jackson", "martin van buren": "martin-van-buren",
    "william henry harrison": "william-henry-harrison",
    "john tyler": "john-tyler", "james polk": "james-polk",
    "zachary taylor": "zachary-taylor", "millard fillmore": "millard-fillmore",
    "franklin pierce": "franklin-pierce", "james buchanan": "james-buchanan",
    "abraham lincoln": "abraham-lincoln", "andrew johnson": "andrew-johnson",
    "ulysses grant": "ulysses-grant", "ulysses s. grant": "ulysses-grant",
    "rutherford hayes": "rutherford-hayes", "james garfield": "james-garfield",
    "chester arthur": "chester-arthur", "grover cleveland": "grover-cleveland",
    "benjamin harrison": "benjamin-harrison", "william mckinley": "william-mckinley",
    "theodore roosevelt": "theodore-roosevelt", "william taft": "william-taft",
    "woodrow wilson": "woodrow-wilson", "warren harding": "warren-harding",
    "calvin coolidge": "calvin-coolidge", "herbert hoover": "herbert-hoover",
    "franklin roosevelt": "franklin-roosevelt", "harry truman": "harry-truman",
    "dwight eisenhower": "dwight-eisenhower", "john kennedy": "john-kennedy",
    "lyndon johnson": "lyndon-johnson", "richard nixon": "richard-nixon",
    "gerald ford": "gerald-ford", "ronald reagan": "ronald-reagan",
    # American Women quarters
    "maya angelou": "maya-angelou", "dr. sally ride": "dr-sally-ride",
    "sally ride": "dr-sally-ride", "wilma mankiller": "wilma-mankiller",
    "nina otero-warren": "nina-otero-warren", "anna may wong": "anna-may-wong",
    "bessie coleman": "bessie-coleman", "eleanor roosevelt": "eleanor-roosevelt",
    "jovita idar": "jovita-idar", "maria tallchief": "maria-tallchief",
    "celia cruz": "celia-cruz", "zitkala-sa": "zitkala-sa",
    "patsy takemoto mink": "patsy-takemoto-mink", "pauli murray": "pauli-murray",
    "mary edwards walker": "mary-edwards-walker",
}


def resolve_program(denom, series):
    for raw in [series, denom]:
        if not raw:
            continue
        key = raw.strip().lower()
        if key in PROGRAM_MAP:
            return PROGRAM_MAP[key]
        for k, v in PROGRAM_MAP.items():
            if k in key or key in k:
                return v
    return None


def resolve_subject(subject, program):
    if not subject or program not in SUBJECT_PROGRAMS:
        return None
    key = subject.strip().lower()
    if key in STATE_SLUG_MAP:
        return STATE_SLUG_MAP[key]
    for k, v in sorted(STATE_SLUG_MAP.items(), key=lambda x: -len(x[0])):
        if k in key or key in k:
            return v
    return None


def candidate_bases(year, mint, program, subject=None):
    bases = []
    m = mint.upper() if mint else None
    if subject:
        if m:
            bases.append(f"{year}_{m}_{subject}_{program}")
        bases.append(f"{year}_{subject}_{program}")
    if m:
        bases.append(f"{year}_{m}_{program}")
    bases.append(f"{year}_{program}")
    simple_map = {
        "lincoln-cent": "cent", "kennedy-half-dollar": "dollar",
        "native-american-dollar": "dollar", "presidential-dollars": "dollar",
        "morgan-dollar": "dollar", "peace-dollar": "dollar",
        "50-state-quarters": "quarter", "american-women-quarters": "quarter",
        "american-innovation": "quarter", "america-the-beautiful": "quarter",
        "jefferson-nickel": "nickel", "buffalo-nickel": "nickel",
        "mercury-dime": "dime",
    }
    simple = simple_map.get(program)
    if simple:
        if m:
            bases.append(f"{year}_{m}_{simple}")
        bases.append(f"{year}_{simple}")
    return bases


def check_image(year, mint, denom, series, subject):
    prog = resolve_program(denom, series)
    if not prog:
        return False, "—no match—", "UNKNOWN", ""
    subj_slug = resolve_subject(subject, prog)
    bases = candidate_bases(year, mint, prog, subj_slug)
    for base in bases:
        if f"{base}_obverse" in index_docs or f"{base}_reverse" in index_docs:
            return True, base, prog, subj_slug or ""
    best = bases[0] if bases else "?"
    return False, best, prog, subj_slug or ""


# ── Query jseaman's collection ────────────────────────────────────────
EMAIL = "jseaman1204@gmail.com"
print(f"Loading coins for {EMAIL}...", flush=True)
coin_stream = db.collection("users").document(EMAIL).collection("coins").stream()

total = found = skipped_no_year = 0
missing_rows = []
YEAR_MINT_RE = re.compile(r"^(\d{4})\s*([A-Z]?)$", re.IGNORECASE)

for doc in coin_stream:
    total += 1
    c = doc.to_dict()

    raw_year = str(c.get("Year", "") or "").strip().replace(".0", "")
    raw_mint = str(c.get("Mint Mark", "") or "").strip()

    # Handle mint embedded in year (e.g. '2006S', '1994 P')
    m = YEAR_MINT_RE.match(raw_year)
    if m:
        year = m.group(1)
        mint = (m.group(2) or raw_mint).strip()
    else:
        year = raw_year
        mint = raw_mint

    if not year or not year.isdigit():
        skipped_no_year += 1
        continue

    denom  = str(c.get("Denomination", "") or "").strip()
    series = str(c.get("Program/Series", "") or "").strip()
    subj   = str(c.get("Theme/Subject", "") or "").strip()

    ok, best_key, prog, subj_slug = check_image(year, mint, denom, series, subj)
    if ok:
        found += 1
    else:
        missing_rows.append({
            "Year": year,
            "Mint": mint,
            "Denomination": denom,
            "Program/Series": series,
            "Theme/Subject": subj,
            "Resolved_Program": prog,
            "Resolved_Subject": subj_slug,
            "Best_Key_Tried": best_key,
        })

print(
    f"Total: {total} | With image: {found} ({found*100//total}%) | "
    f"Missing: {len(missing_rows)} | No year/skipped: {skipped_no_year}",
    flush=True,
)

# ── De-duplicate by canonical key, tally count ───────────────────────
dedup = {}
for row in missing_rows:
    k = row["Best_Key_Tried"]
    if k not in dedup:
        dedup[k] = dict(row)
        dedup[k]["Count"] = 1
    else:
        dedup[k]["Count"] += 1

rows = sorted(dedup.values(), key=lambda x: (-x["Count"], x["Year"], x["Denomination"]))

# ── Write CSV ─────────────────────────────────────────────────────────
OUT = "missing_coin_images.csv"
fields = ["Count", "Year", "Mint", "Denomination", "Program/Series",
          "Theme/Subject", "Resolved_Program", "Resolved_Subject", "Best_Key_Tried"]

with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

print(f"CSV written: {OUT}  ({len(rows)} unique gaps)", flush=True)
print("\nTop 20 missing (by count of coins affected):", flush=True)
for r in rows[:20]:
    print(f"  [{r['Count']:3d}x]  {r['Best_Key_Tried']:<55}  {r['Denomination']}", flush=True)
