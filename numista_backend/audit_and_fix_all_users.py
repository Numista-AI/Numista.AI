#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_and_fix_all_users.py
==========================
Programmatic audit and healing of coin images for eric@numista.ai and jseaman1204@gmail.com.

Checks performed during audit:
1. Identical Sides: Obverse URL == Reverse URL (ignoring query parameters).
2. Denomination Mismatch: e.g., Quarter coin pointing to a cent or half dollar path.
3. Date Mismatch: Coin year != year in URL path (excluding known design/obverse fallbacks).
4. Cross-User Contamination: Coin points to another user's uploads folder.
5. Wrong Doc ID: GCS path doc ID does not match Firestore document ID.
6. Missing/Empty Images: One or both image URLs are empty.

Heal phase (activated via --heal):
- Matches coin to correct GCS reference library image (using inventory + lookup_index).
- Re-uploads correct image to user folder under GCS.
- Updates Firestore with cache-busted URLs (?t=<timestamp>), proper source tags, and US Mint attribution.

Usage:
    python audit_and_fix_all_users.py           # Runs audit, writes audit_findings.csv
    python audit_and_fix_all_users.py --heal    # Runs audit, then heals flagged coins
"""

import sys
import os
import csv
import re
import json
import time
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage

# Force UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ─── CONFIG ──────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
SA_KEY = SCRIPT_DIR / "serviceAccountKey.json.json"
PROJECT_ID = "studio-9101802118-8c9a8"
REF_BUCKET = "numista-reference-library"
UPLOADS_BUCKET = f"numista-uploads-{PROJECT_ID}"
GCS_PUB_BASE = f"https://storage.googleapis.com/{UPLOADS_BUCKET}"

GCS_INVENTORY = SCRIPT_DIR / "gcs_full_inventory.csv"
PRES_JSON = SCRIPT_DIR / "gcs_presidential_dollars.json"
CSV_OUT = SCRIPT_DIR.parent / "audit_findings.csv"

# Attributions
GCS_ATTRIBUTION = "United States Mint. Public domain (17 U.S.C. § 105). Source: usmint.gov"
WIKI_ATTRIBUTION = "Public Domain. Source: Wikimedia Commons"
DEFAULT_ATTRIBUTION = "Public Domain. Source: US Mint / GCS Reference Library."

# ─── INITIALIZE CLIENTS ──────────────────────────────────────────────────────
if not firebase_admin._apps:
    cred = credentials.Certificate(str(SA_KEY))
    firebase_admin.initialize_app(cred)

db = firestore.client()
gcs = storage.Client.from_service_account_json(str(SA_KEY))
ref_bucket_obj = gcs.bucket(REF_BUCKET)
uploads_bucket_obj = gcs.bucket(UPLOADS_BUCKET)

# ─── LOAD GCS INVENTORY & PRES DATA ──────────────────────────────────────────
print(f"[INIT] Loading GCS reference inventory from {GCS_INVENTORY} ...")
REF_ROWS = []
with open(GCS_INVENTORY, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["bucket"] == REF_BUCKET:
            REF_ROWS.append(row)
print(f"[INIT] Loaded {len(REF_ROWS):,} reference library rows.")

print(f"[INIT] Loading Presidential $1 JSON from {PRES_JSON} ...")
with open(PRES_JSON, encoding="utf-8") as f:
    PRES_DATA = json.load(f)

PRES_OBVERSE = {}
PRES_REVERSE = {}
PRES_UNIVERSAL_REVERSE = {
    "bucket": REF_BUCKET,
    "path": "reference_library/wikimedia_uscoin/Dollar_coins_of_the_United_States/Presidential__1_Coin_Program/Presidential_dollar_coin_reverse.png",
    "public_url": f"https://storage.googleapis.com/{REF_BUCKET}/reference_library/wikimedia_uscoin/Dollar_coins_of_the_United_States/Presidential__1_Coin_Program/Presidential_dollar_coin_reverse.png",
}

for key, entry in PRES_DATA.items():
    if "/" not in key and entry.get("bucket") == REF_BUCKET:
        name = key.lower().replace("_", " ")
        p = (entry.get("path") or "").lower()
        if any(x in p for x in ["reverse", "_rev", "-rev", "back"]):
            PRES_REVERSE[name] = entry
        else:
            PRES_OBVERSE[name] = entry

# ─── KEYWORD SEARCH INDEX ────────────────────────────────────────────────────
_kw_index = defaultdict(list)
for row in REF_ROWS:
    p = row["path"].lower()
    _kw_index[p].append(row)
    for seg in p.split("/"):
        if len(seg) > 3:
            _kw_index[seg].append(row)

# ─── HELPERS FOR MATCHING ────────────────────────────────────────────────────
def gcs_find(keywords: list[str], side_hints: list[str] = None) -> dict | None:
    kw_lower = [k.lower() for k in keywords]
    sh_lower = [s.lower() for s in (side_hints or [])]

    def score(row):
        p = row["path"].lower()
        return 0 if "bulk_programs" in p else 1

    candidates = []
    for row in REF_ROWS:
        p = row["path"].lower()
        if all(k in p for k in kw_lower):
            if sh_lower:
                if any(s in p for s in sh_lower):
                    candidates.append(row)
            else:
                candidates.append(row)
    candidates.sort(key=score)
    return candidates[0] if candidates else None

def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def classify_coin(denom: str, program: str, year: str) -> str:
    d = (denom or "").lower().strip()
    p = (program or "").lower().strip()
    y = str(year or "").strip()

    if "morgan" in p: return "morgan_dollar"
    if "peace" in p and ("dollar" in d or "dollar" in p): return "peace_dollar"
    if any(x in p for x in ["eisenhower", "ike"]) and "presidential" not in p: return "eisenhower_dollar"
    if "presidential" in p: return "presidential_dollar"
    if any(x in p for x in ["native american", "sacagawea", "native_american"]): return "native_american_dollar"

    if "kennedy" in p: return "kennedy_half"
    if "franklin" in p and ("half" in d or "half" in p): return "franklin_half"
    if any(x in p for x in ["walking liberty", "walking"]): return "walking_liberty"

    if any(x in p for x in ["state quarter", "50 state", "statehood", "50-state"]): return "state_quarter"
    if "american women" in p: return "american_women_quarter"
    if any(x in p for x in ["america the beautiful", "america beautiful", "national park", "atb", "america_beautiful"]): return "america_beautiful"
    if "barber" in p and ("quarter" in d or "25" in d or "quarter" in p): return "barber_quarter"
    if "capped bust" in p and "quarter" in d: return "capped_bust_quarter"
    if "seated liberty" in p and "quarter" in d: return "seated_liberty_quarter"
    if "washington" in p and "quarter" in d: return "washington_quarter"
    if "quarter" in d: return "washington_quarter"

    if any(x in p for x in ["barber dime", "barber series dime"]) or ("barber" in d and "dime" in d): return "barber_dime"
    if "mercury" in p: return "mercury_dime"
    if "roosevelt" in p and "dime" in d: return "roosevelt_dime"
    if "dime" in d:
        if y.isdigit() and int(y) < 1916: return "barber_dime"
        if y.isdigit() and 1916 <= int(y) <= 1945: return "mercury_dime"
        return "roosevelt_dime"

    if any(x in p for x in ["buffalo", "indian head nickel"]): return "buffalo_nickel"
    if any(x in p for x in ["three-cent nickel", "three cent nickel", "3 cent"]): return "three_cent_nickel"
    if "jefferson" in p: return "jefferson_nickel"
    if "nickel" in d:
        if y.isdigit() and int(y) <= 1938: return "buffalo_nickel"
        return "jefferson_nickel"

    if any(x in p for x in ["indian head cent", "indian head"]): return "indian_head_cent"
    if any(x in d for x in ["1 cent", "cent", "penny"]):
        if "indian" in p: return "indian_head_cent"
        if "wheat" in p or (y.isdigit() and 1909 <= int(y) <= 1958): return "wheat_cent"
        if "memorial" in p or (y.isdigit() and int(y) >= 1959): return "memorial_cent"
        return "wheat_cent"

    if "half cent" in d: return "half_cent_classic_head"
    if "dollar" in d: return "morgan_dollar"
    return ""

COIN_GCS_MAP = {
    "morgan_dollar": {"obverse": ["morgan", "obverse"], "reverse": ["morgan", "reverse"]},
    "peace_dollar": {"obverse": ["peace", "obverse"], "reverse": ["peace", "reverse"]},
    "eisenhower_dollar": {"obverse": ["eisenhower", "obverse"], "reverse": ["eisenhower", "reverse"]},
    "kennedy_half": {"obverse": ["kennedy", "obverse"], "reverse": ["kennedy", "reverse"]},
    "franklin_half": {"obverse": ["franklin", "obverse"], "reverse": ["franklin", "reverse"]},
    "walking_liberty": {"obverse": ["walking", "obverse"], "reverse": ["walking", "reverse"]},
    "barber_dime": {"obverse": ["barber", "dime", "obverse"], "reverse": ["barber", "dime", "reverse"]},
    "barber_quarter": {"obverse": ["barber", "quarter", "obverse"], "reverse": ["barber", "quarter", "reverse"]},
    "mercury_dime": {"obverse": ["mercury", "obverse"], "reverse": ["mercury", "reverse"]},
    "roosevelt_dime": {"obverse": ["roosevelt", "dime", "obverse"], "reverse": ["roosevelt", "dime", "reverse"]},
    "buffalo_nickel": {"obverse": ["buffalo", "obverse"], "reverse": ["buffalo", "reverse"]},
    "jefferson_nickel": {"obverse": ["jefferson", "nickel", "obverse"], "reverse": ["jefferson", "nickel", "reverse"]},
    "lincoln_wheat_cent": {"obverse": ["wheat", "obverse"], "reverse": ["wheat", "reverse"]},
    "wheat_cent": {"obverse": ["wheat", "obverse"], "reverse": ["wheat", "reverse"]},
    "memorial_cent": {"obverse": ["lincoln", "memorial", "obverse"], "reverse": ["lincoln", "memorial", "reverse"]},
    "indian_head_cent": {"obverse": ["indian", "cent", "obverse"], "reverse": ["indian", "cent", "reverse"]},
    "washington_quarter": {"obverse": ["washington", "quarter", "obverse"], "reverse": ["washington", "quarter", "reverse"]},
    "american_women_quarter": {"obverse": ["american", "women", "obverse"], "reverse": ["american", "women", "reverse"]},
    "america_beautiful": {"obverse": ["america", "beautiful", "obverse"], "reverse": ["america", "beautiful", "reverse"]},
    "native_american_dollar": {"obverse": ["native", "obverse"], "reverse": ["native", "reverse"]},
    "three_cent_nickel": {"obverse": ["three", "cent", "obverse"], "reverse": ["three", "cent", "reverse"]},
    "seated_liberty_quarter": {"obverse": ["seated", "obverse"], "reverse": ["seated", "reverse"]},
    "half_cent_classic_head": {"obverse": ["half", "cent", "obverse"], "reverse": ["half", "cent", "reverse"]},
}

def match_state_quarter(coin: dict) -> tuple[dict | None, dict | None]:
    theme = (coin.get("theme") or coin.get("program") or "").lower()
    program = (coin.get("program") or "").lower()
    state = ""
    for field in [theme, program]:
        cleaned = re.sub(r"(50 state|state quarter|statehood quarter|\d{4})", "", field, flags=re.I).strip()
        if cleaned and len(cleaned) > 2:
            state = cleaned.strip()
            break
    if not state:
        return None, None
    state_slug = slugify(state)
    obv = gcs_find(["50_state_quarters", state_slug], ["obverse", "uncirculated"])
    if not obv:
        obv = gcs_find(["50_state_quarters"], ["obverse", "Denver"])
    rev = gcs_find(["50_state_quarters", state_slug], ["reverse"])
    return obv, rev

def match_presidential_dollar(coin: dict) -> tuple[dict | None, dict | None]:
    theme = (coin.get("theme") or "").lower().strip()
    if not theme:
        return None, None
    president_key = None
    theme_words = theme.lower().split()
    for key in PRES_DATA:
        if "/" in key:
            continue
        key_lower = key.lower().replace("_", " ")
        if key_lower in theme or any(kw in key_lower for kw in theme_words if len(kw) > 3):
            president_key = key
            break
    if not president_key:
        for word in theme_words:
            if len(word) > 3 and word in PRES_DATA:
                president_key = word
                break

    obv_row = None
    rev_row = None
    if president_key:
        entry = PRES_DATA[president_key]
        if entry.get("bucket") == REF_BUCKET:
            p = entry.get("path", "").lower()
            if any(x in p for x in ["reverse", "_rev", "-rev", "back"]):
                rev_row = entry
            else:
                obv_row = entry

    president_slug = slugify(theme.split("(")[0].strip())
    name_parts = president_slug.split("-")
    for part in reversed(name_parts):
        if len(part) > 3:
            bulk_obv = gcs_find(["bulk_programs", "presidential", part], ["obverse"])
            bulk_rev = gcs_find(["bulk_programs", "presidential", part], ["reverse"])
            if bulk_obv and not obv_row:
                obv_row = bulk_obv
            if bulk_rev and not rev_row:
                rev_row = bulk_rev
            if obv_row and rev_row:
                break

    if not rev_row:
        rev_row = PRES_UNIVERSAL_REVERSE
    return obv_row, rev_row

def match_native_american(coin: dict) -> tuple[dict | None, dict | None]:
    obv = gcs_find(["sacagawea"], ["obverse", "front"]) or gcs_find(["native_american"], ["obverse", "front"])
    rev = gcs_find(["sacagawea"], ["reverse", "back"]) or gcs_find(["native_american"], ["reverse"])
    return obv, rev

def match_america_beautiful(coin: dict) -> tuple[dict | None, dict | None]:
    theme = (coin.get("theme") or "").lower().strip()
    park = re.sub(r"(national park|national monument|quarter|\d{4})", "", theme, flags=re.I).strip()
    park_slug = slugify(park)
    park_parts = [p for p in park_slug.split("-") if len(p) > 2]
    obv = rev = None
    if park_parts:
        obv = gcs_find(["america_beautiful"] + park_parts[:2], ["obverse"])
        rev = gcs_find(["america_beautiful"] + park_parts[:2], ["reverse"])
    if not obv:
        obv = gcs_find(["america_beautiful"], ["obverse"])
    if not rev:
        rev = gcs_find(["america_beautiful"], ["reverse"])
    return obv, rev

def match_american_women_quarter(coin: dict) -> tuple[dict | None, dict | None]:
    theme = (coin.get("theme") or "").lower().strip()
    theme_slug = slugify(theme)
    theme_parts = [p for p in theme_slug.split("-") if len(p) > 3]
    obv = rev = None
    if theme_parts:
        obv = gcs_find(["american_women"] + theme_parts[:2], ["obverse"])
        rev = gcs_find(["american_women"] + theme_parts[:2], ["reverse"])
    if not obv:
        obv = gcs_find(["american_women"], ["obverse"])
    if not rev:
        rev = gcs_find(["american_women"], ["reverse"])
    return obv, rev

def match_generic(coin_type: str) -> tuple[dict | None, dict | None]:
    spec = COIN_GCS_MAP.get(coin_type)
    if not spec:
        return None, None
    obv_kw = spec.get("obverse", [])
    rev_kw = spec.get("reverse", [])
    obv = gcs_find(obv_kw)
    if not obv and len(obv_kw) > 2:
        obv = gcs_find(obv_kw[:-1])
    rev = gcs_find(rev_kw)
    if not rev and len(rev_kw) > 2:
        rev = gcs_find(rev_kw[:-1])
    return obv, rev

def gcs_match_coin(coin: dict) -> tuple[dict | None, dict | None]:
    denom = coin.get("denomination", "")
    program = coin.get("program", "")
    year = coin.get("year", "")
    coin_type = classify_coin(denom, program, year)

    obv, rev = None, None
    if coin_type == "presidential_dollar":
        obv, rev = match_presidential_dollar(coin)
    elif coin_type == "native_american_dollar":
        obv, rev = match_native_american(coin)
    elif coin_type == "state_quarter":
        obv, rev = match_state_quarter(coin)
    elif coin_type == "america_beautiful":
        obv, rev = match_america_beautiful(coin)
    elif coin_type == "american_women_quarter":
        obv, rev = match_american_women_quarter(coin)
    else:
        obv, rev = match_generic(coin_type)
        
    return obv, rev

# ─── AUDIT CHECKS ────────────────────────────────────────────────────────────
def sanitize_path(url):
    if not url: return ""
    url = url.lower().split('?')[0]
    # Remove UUIDs (36-char strings with hyphens)
    url = re.sub(r'\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b', '', url)
    # Remove MD5-like or UUID-like 32-char hex strings
    url = re.sub(r'\b[a-f0-9]{32}\b', '', url)
    return url

def has_word(text, word):
    pattern = r'(?:^|[^a-z0-9])' + re.escape(word) + r'(?:$|[^a-z0-9])'
    return bool(re.search(pattern, text))

def extract_year(text):
    if not text: return None
    sanitized = sanitize_path(str(text))
    match = re.search(r'\b(17|18|19|20)\d{2}\b', sanitized)
    return match.group(0) if match else None

def clean_url(url):
    if not url: return ""
    return url.split('?')[0].strip()

def check_denom_mismatch(denom_str, url):
    if not denom_str or not url: return None
    denom_str = denom_str.lower().strip()
    url = sanitize_path(url)
    
    if "quarter eagle" in denom_str or "2.50" in denom_str or "2 1/2" in denom_str:
        return None
    if "half eagle" in denom_str or "$5" in denom_str:
        return None
    if "double eagle" in denom_str or "$20" in denom_str:
        return None
    if "eagle" in denom_str or "$10" in denom_str:
        return None
        
    if "quarter" in denom_str or "25c" in denom_str:
        for bad in ['cent', 'penny', 'dime', 'nickel', 'dollar', 'half_dollar', 'half-dollar', '50c', '10c', '5c', '1c', '50_cents']:
            if has_word(url, bad):
                if has_word(url, "quarter") or has_word(url, "25c"):
                    continue
                return f"Quarter coin but URL has '{bad}'"
                
    elif "half dollar" in denom_str or "50c" in denom_str or "half" in denom_str:
        for bad in ['cent', 'penny', 'quarter', 'dime', 'nickel', 'dollar', '25c', '10c', '5c', '1c']:
            if has_word(url, bad):
                if has_word(url, "half_dollar") or has_word(url, "half-dollar") or has_word(url, "50c") or has_word(url, "50_cents"):
                    continue
                return f"Half Dollar coin but URL has '{bad}'"
                
    elif "dime" in denom_str or "10c" in denom_str:
        for bad in ['cent', 'penny', 'quarter', 'nickel', 'dollar', 'half_dollar', 'half-dollar', '50c', '25c', '5c', '1c', '50_cents']:
            if has_word(url, bad):
                if has_word(url, "dime") or has_word(url, "10c"):
                    continue
                return f"Dime coin but URL has '{bad}'"
                
    elif "nickel" in denom_str or "5c" in denom_str or "five cents" in denom_str:
        for bad in ['cent', 'penny', 'quarter', 'dime', 'dollar', 'half_dollar', 'half-dollar', '50c', '25c', '10c', '1c', '50_cents']:
            if has_word(url, bad):
                if has_word(url, "nickel") or has_word(url, "5c") or has_word(url, "five_cents"):
                    continue
                return f"Nickel coin but URL has '{bad}'"
                
    elif "cent" in denom_str or "penny" in denom_str or "1c" in denom_str or "one cent" in denom_str:
        for bad in ['quarter', 'dime', 'nickel', 'dollar', 'half_dollar', 'half-dollar', '50c', '25c', '10c', '5c', '50_cents']:
            if has_word(url, bad):
                if has_word(url, "cent") or has_word(url, "penny") or has_word(url, "1c") or has_word(url, "one_cent"):
                    continue
                return f"Cent coin but URL has '{bad}'"
                
    elif "dollar" in denom_str or "$1" in denom_str or "one dollar" in denom_str:
        for bad in ['cent', 'penny', 'quarter', 'dime', 'nickel', 'half_dollar', 'half-dollar', '50c', '25c', '10c', '5c', '1c', '50_cents']:
            if has_word(url, bad):
                if has_word(url, "dollar") or has_word(url, "$1") or has_word(url, "one_dollar"):
                    continue
                return f"Dollar coin but URL has '{bad}'"
    return None

def check_date_mismatch(coin_year, coin_denom, coin_program, url):
    if not coin_year or not url: return None
    
    y_coin = extract_year(coin_year)
    if not y_coin: return None
    
    path_only = url.split('?')[0].split('storage.googleapis.com/')[-1]
    y_url = extract_year(path_only)
    if not y_url: return None
    
    if y_coin == y_url:
        return None
        
    denom = (coin_denom or "").lower()
    prog = (coin_program or "").lower()
    yc_int = int(y_coin)
    yu_int = int(y_url)
    
    # Washington Quarter obverse fallback
    if "quarter" in denom and yc_int >= 1932 and yc_int <= 1998 and yu_int >= 1932 and yu_int <= 1998:
        if "obverse" in url.lower() or "obv" in url.lower():
            return None
            
    # Wheat Penny fallback
    if ("cent" in denom or "penny" in denom) and yc_int >= 1909 and yc_int <= 1958 and yu_int >= 1909 and yu_int <= 1958:
        return None
        
    # Memorial Cent fallback
    if ("cent" in denom or "penny" in denom) and yc_int >= 1959 and yc_int <= 2008 and yu_int >= 1959 and yu_int <= 2008:
        return None

    # Shield Cent fallback
    if ("cent" in denom or "penny" in denom) and yc_int >= 2010 and yc_int <= 2026 and yu_int >= 2010 and yu_int <= 2026:
        return None
        
    # Jefferson Nickel fallback
    if "nickel" in denom and yc_int >= 1938 and yc_int <= 2003 and yu_int >= 1938 and yu_int <= 2003:
        return None
        
    # Roosevelt Dime fallback
    if "dime" in denom and yc_int >= 1946 and yc_int <= 2026 and yu_int >= 1946 and yu_int <= 2026:
        return None
        
    # Franklin Half fallback
    if "half" in denom and "franklin" in prog and yc_int >= 1948 and yc_int <= 1963 and yu_int >= 1948 and yu_int <= 1963:
        return None
        
    # Walking Liberty Half fallback
    if "half" in denom and "walking" in prog and yc_int >= 1916 and yc_int <= 1947 and yu_int >= 1916 and yu_int <= 1947:
        return None
        
    # Kennedy Half fallback (non-Bicentennial)
    if "half" in denom and "kennedy" in prog:
        if yc_int != 1976 and yu_int != 1976:
            if yc_int >= 1964 and yc_int <= 2026 and yu_int >= 1964 and yu_int <= 2026:
                return None
                
    # Susan B Anthony fallback
    if "dollar" in denom and "anthony" in prog and yc_int in [1979, 1980, 1981, 1999] and yu_int in [1979, 1980, 1981, 1999]:
        return None
        
    # Morgan Dollar fallback
    if "dollar" in denom and "morgan" in prog and yc_int >= 1878 and yc_int <= 1921 and yu_int >= 1878 and yu_int <= 1921:
        return None
        
    # Peace Dollar fallback
    if "dollar" in denom and "peace" in prog and yc_int >= 1921 and yc_int <= 1935 and yu_int >= 1921 and yu_int <= 1935:
        return None
        
    return f"Year mismatch: coin is {y_coin} but URL contains {y_url}"

def get_val(d, *keys, default=""):
    for k in keys:
        v = d.get(k)
        if v is not None and str(v).strip() not in ("", "None", "nan"):
            return str(v).strip()
    return default

def main():
    heal_mode = "--heal" in sys.argv
    print("=" * 70)
    print("NUMISTA.AI -- AUDIT AND HEAL SCRIPT FOR COIN IMAGES")
    print(f"Heal Mode: {heal_mode}")
    print(f"Run at   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    target_users = ["eric@numista.ai", "jseaman1204@gmail.com"]
    findings = []

    for user_email in target_users:
        print(f"\n[AUDIT] Scanning coins for {user_email} ...")
        col_ref = db.collection("users").document(user_email).collection("coins")
        docs = list(col_ref.stream())
        print(f"  Found {len(docs)} coin documents.")

        for doc in docs:
            doc_id = doc.id
            d = doc.to_dict()

            year = get_val(d, "Year", "year", "date", "Date")
            denom = get_val(d, "Denomination", "denomination", "face_value")
            program = get_val(d, "Program/Series", "program", "Program", "series", "Series", "coin_type", "type", "Type")
            theme = get_val(d, "Theme/Subject", "theme", "subject", "Subject")
            mint = get_val(d, "Mint Mark", "mint_mark", "mintMark", "mint")
            coin_name = f"{year} {mint} {denom} - {program}"

            obv = d.get("image_url_obverse", "").strip()
            rev = d.get("image_url_reverse", "").strip()

            clean_obv = clean_url(obv)
            clean_rev = clean_url(rev)

            mismatch_reasons = []

            # 1. Missing Images
            if not clean_obv and not clean_rev:
                mismatch_reasons.append("Missing both images")
            elif not clean_obv:
                mismatch_reasons.append("Missing obverse image")
            elif not clean_rev:
                mismatch_reasons.append("Missing reverse image")

            # 2. Identical Sides
            if clean_obv and clean_rev and clean_obv == clean_rev:
                mismatch_reasons.append("Identical sides (obv == rev)")

            # 3. Denomination Mismatch
            if clean_obv:
                m_obv = check_denom_mismatch(denom, clean_obv)
                if m_obv: mismatch_reasons.append(f"Obverse: {m_obv}")
            if clean_rev:
                m_rev = check_denom_mismatch(denom, clean_rev)
                if m_rev: mismatch_reasons.append(f"Reverse: {m_rev}")

            # 4. Date Mismatch
            if clean_obv:
                d_obv = check_date_mismatch(year, denom, program, clean_obv)
                if d_obv: mismatch_reasons.append(f"Obverse: {d_obv}")
            if clean_rev:
                d_rev = check_date_mismatch(year, denom, program, clean_rev)
                if d_rev: mismatch_reasons.append(f"Reverse: {d_rev}")

            # 5. Cross-User Contamination
            for other_email in target_users:
                if other_email != user_email:
                    if clean_obv and other_email in clean_obv:
                        mismatch_reasons.append(f"Obverse has other user: {other_email}")
                    if clean_rev and other_email in clean_rev:
                        mismatch_reasons.append(f"Reverse has other user: {other_email}")

            # 6. Wrong Doc ID in GCS path
            valid_user_prefix = f"users/{user_email}/"
            for url, side in [(clean_obv, "Obverse"), (clean_rev, "Reverse")]:
                if url and valid_user_prefix in url:
                    suffix = url.split(valid_user_prefix)[-1]
                    parts = suffix.split("/")
                    if len(parts) >= 2 and parts[0] == "coins" and parts[1] != doc_id:
                        mismatch_reasons.append(f"{side} GCS path has wrong doc_id: {parts[1]} (expected {doc_id})")

            if mismatch_reasons:
                findings.append({
                    "user_email": user_email,
                    "doc_id": doc_id,
                    "coin_name": coin_name,
                    "denomination": denom,
                    "program": program,
                    "year": year,
                    "theme": theme,
                    "mint_mark": mint,
                    "obverse_url": obv,
                    "reverse_url": rev,
                    "mismatches": "; ".join(mismatch_reasons)
                })

    print(f"\n[REPORT] Writing findings to {CSV_OUT} ...")
    with open(CSV_OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "user_email", "doc_id", "coin_name", "denomination", "program", "year", "theme", "mint_mark",
            "obverse_url", "reverse_url", "mismatches"
        ])
        writer.writeheader()
        for f_row in findings:
            writer.writerow(f_row)
    print(f"  [OK] Saved {len(findings)} flagged coins to {CSV_OUT}.")

    if heal_mode:
        print("\n" + "=" * 70)
        print("HEALING PHASE IN PROGRESS")
        print("=" * 70)
        
        success_count = 0
        failed_count = 0

        for idx, item in enumerate(findings):
            user_email = item["user_email"]
            doc_id = item["doc_id"]
            coin_name = item["coin_name"]
            mismatches = item["mismatches"]
            
            # Avoid healing Eric's coins since they were already manually fixed
            # unless there's still a bug. Let's heal AJ's coins primarily or all if needed.
            # However, if Eric's coins are already fixed, they won't have mismatches anymore!
            
            print(f"\n[{idx+1}/{len(findings)}] Sourcing correct images for: {coin_name} (doc={doc_id}, user={user_email})")
            print(f"  Mismatches: {mismatches}")

            try:
                coin_payload = {
                    "denomination": item["denomination"],
                    "program": item["program"],
                    "year": item["year"],
                    "theme": item["theme"],
                    "mint_mark": item["mint_mark"]
                }

                # 1. Try catalog match
                obv_row, rev_row = gcs_match_coin(coin_payload)
                
                # 2. Try lookup_index if catalog match failed
                if not obv_row or not rev_row:
                    idx_obv, idx_rev = lookup_index(item["year"], item["mint_mark"], [item["program"]])
                    if idx_obv and not obv_row:
                        obv_row = {"public_url": idx_obv}
                    if idx_rev and not rev_row:
                        rev_row = {"public_url": idx_rev}

                if not obv_row and not rev_row:
                    print(f"  [WARN] Could not find any reference matches for {coin_name}. Sourcing failed.")
                    failed_count += 1
                    continue

                fs_updates = {}
                gcs_base = f"users/{user_email}/coins/{doc_id}"

                # Sourcing Obverse
                if obv_row:
                    src_url = obv_row.get("public_url")
                    if not src_url and obv_row.get("path"):
                        src_url = f"https://storage.googleapis.com/{obv_row['bucket']}/{obv_row['path']}"
                    
                    if src_url:
                        print(f"  Obverse match found: {src_url}")
                        img_data = None
                        if obv_row.get("bucket") == REF_BUCKET and obv_row.get("path"):
                            try:
                                img_data = ref_bucket_obj.blob(obv_row["path"]).download_as_bytes()
                            except Exception as e:
                                print(f"    GCS download failed for obverse: {e}")
                        
                        if not img_data:
                            import requests
                            try:
                                r = requests.get(src_url, timeout=15)
                                if r.status_code == 200:
                                    img_data = r.content
                            except Exception as e:
                                print(f"    HTTP download failed for obverse: {e}")

                        if img_data:
                            dest_blob_path = f"{gcs_base}/obverse.jpg"
                            try:
                                uploads_bucket_obj.blob(dest_blob_path).delete()
                            except Exception:
                                pass
                            
                            dest_blob = uploads_bucket_obj.blob(dest_blob_path)
                            dest_blob.cache_control = "no-cache, no-store, must-revalidate"
                            dest_blob.upload_from_string(img_data, content_type="image/jpeg")
                            
                            fs_updates["image_url_obverse"] = f"{GCS_PUB_BASE}/{dest_blob_path}?t={int(time.time())}"
                            fs_updates["image_source_obverse"] = "gcs_reference_library"
                            fs_updates["image_attribution_obverse"] = GCS_ATTRIBUTION if "us_mint" in src_url.lower() or "bulk_programs" in src_url.lower() else WIKI_ATTRIBUTION
                            print("    [OK] Healed and uploaded obverse.")

                # Sourcing Reverse
                if rev_row:
                    src_url = rev_row.get("public_url")
                    if not src_url and rev_row.get("path"):
                        src_url = f"https://storage.googleapis.com/{rev_row['bucket']}/{rev_row['path']}"
                    
                    if src_url:
                        print(f"  Reverse match found: {src_url}")
                        img_data = None
                        if rev_row.get("bucket") == REF_BUCKET and rev_row.get("path"):
                            try:
                                img_data = ref_bucket_obj.blob(rev_row["path"]).download_as_bytes()
                            except Exception as e:
                                print(f"    GCS download failed for reverse: {e}")
                        
                        if not img_data:
                            import requests
                            try:
                                r = requests.get(src_url, timeout=15)
                                if r.status_code == 200:
                                    img_data = r.content
                            except Exception as e:
                                print(f"    HTTP download failed for reverse: {e}")

                        if img_data:
                            dest_blob_path = f"{gcs_base}/reverse.jpg"
                            try:
                                uploads_bucket_obj.blob(dest_blob_path).delete()
                            except Exception:
                                pass
                            
                            dest_blob = uploads_bucket_obj.blob(dest_blob_path)
                            dest_blob.cache_control = "no-cache, no-store, must-revalidate"
                            dest_blob.upload_from_string(img_data, content_type="image/jpeg")
                            
                            fs_updates["image_url_reverse"] = f"{GCS_PUB_BASE}/{dest_blob_path}?t={int(time.time())}"
                            fs_updates["image_source_reverse"] = "gcs_reference_library"
                            fs_updates["image_attribution_reverse"] = GCS_ATTRIBUTION if "us_mint" in src_url.lower() or "bulk_programs" in src_url.lower() else WIKI_ATTRIBUTION
                            print("    [OK] Healed and uploaded reverse.")

                if fs_updates:
                    attr_obv = fs_updates.get("image_attribution_obverse")
                    attr_rev = fs_updates.get("image_attribution_reverse")
                    if attr_obv == GCS_ATTRIBUTION or attr_rev == GCS_ATTRIBUTION:
                        fs_updates["image_attribution"] = GCS_ATTRIBUTION
                    else:
                        fs_updates["image_attribution"] = WIKI_ATTRIBUTION

                    fs_updates["updated_at"] = datetime.now(timezone.utc).isoformat()
                    fs_updates["last_image_fix"] = datetime.now(timezone.utc).isoformat()
                    fs_updates["image_fix_reason"] = "Auto-healed by audit pipeline: corrected mismatch/missing image."

                    doc_ref = db.collection("users").document(user_email).collection("coins").document(doc_id)
                    doc_ref.update(fs_updates)
                    success_count += 1
                    print("    [OK] Firestore updated.")
                else:
                    print("    [WARN] No updates applied (download failures).")
                    failed_count += 1
            except Exception as loop_err:
                print(f"  [ERR] Exception occurred while healing {coin_name}: {loop_err}")
                failed_count += 1

        print("\n" + "=" * 70)
        print("HEALING PHASE COMPLETE")
        print(f"Total processed: {len(findings)}")
        print(f"Healed successfully: {success_count}")
        print(f"Failed to heal     : {failed_count}")
        print("=" * 70)


def lookup_index(year: str, mint: str, programs: list[str]) -> tuple[str | None, str | None]:
    year_str = str(year).strip() if year else ""
    mint_str = str(mint).strip().upper() if mint else ""
    obv_candidates = []
    rev_candidates = []
    for prog in programs:
        if year_str and mint_str:
            obv_candidates.append(f"{year_str}_{mint_str}_{prog}_obverse")
            rev_candidates.append(f"{year_str}_{mint_str}_{prog}_reverse")
        if year_str:
            obv_candidates.append(f"{year_str}_{prog}_obverse")
            rev_candidates.append(f"{year_str}_{prog}_reverse")
        obv_candidates.append(f"{prog}_obverse")
        rev_candidates.append(f"{prog}_reverse")

    obv_url = None
    for cid in obv_candidates:
        try:
            doc = db.collection("coin_image_index").document(cid).get()
            if doc.exists:
                obv_url = doc.to_dict().get("image_url")
                if obv_url: break
        except Exception:
            pass

    rev_url = None
    for cid in rev_candidates:
        try:
            doc = db.collection("coin_image_index").document(cid).get()
            if doc.exists:
                rev_url = doc.to_dict().get("image_url")
                if rev_url: break
        except Exception:
            pass

    return obv_url, rev_url


if __name__ == "__main__":
    main()
