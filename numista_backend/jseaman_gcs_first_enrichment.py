# -*- coding: utf-8 -*-
"""
jseaman_gcs_first_enrichment.py
================================
Re-runs image enrichment for jseaman1204@gmail.com's remaining image gaps
using GCS-FIRST sourcing strategy.

Priority order:
  1. GCS reference library (numista-reference-library) via gcs_full_inventory.csv
  2. coin_image_index Firestore collection
  3. Wikimedia Commons (last resort)

Groups processed:
  - Group A: both images missing
  - Group B: obverse present, reverse missing (only reverse uploaded)

Usage:
  python jseaman_gcs_first_enrichment.py --dry-run
  python jseaman_gcs_first_enrichment.py --dry-run --limit 20
  python jseaman_gcs_first_enrichment.py           # full live run
"""

import argparse
import csv
import io
import json
import os
import re
import sys
import time
import requests
from collections import defaultdict
from urllib.parse import quote

# ── Force UTF-8 stdout ────────────────────────────────────────────────────────
try:
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
    )
except Exception:
    pass

# ── Config ────────────────────────────────────────────────────────────────────
SCRIPT_DIR       = os.path.dirname(os.path.abspath(__file__))
KEY_PATH         = os.path.join(SCRIPT_DIR, "serviceAccountKey.json.json")
PROJECT_ID       = "studio-9101802118-8c9a8"
USER_EMAIL       = "jseaman1204@gmail.com"
COINS_COLL       = f"users/{USER_EMAIL}/coins"
UPLOAD_BUCKET    = "numista-uploads-studio-9101802118-8c9a8"
REF_BUCKET       = "numista-reference-library"
GCS_INVENTORY    = os.path.join(SCRIPT_DIR, "gcs_full_inventory.csv")
PRES_JSON        = os.path.join(SCRIPT_DIR, "gcs_presidential_dollars.json")
USER_AGENT       = "NumistaAI/1.0 (eric@numista.ai)"
LOG_PATH         = os.path.join(SCRIPT_DIR, "jseaman_gcs_first_log.json")
UPLOAD_BASE_URL  = f"https://storage.googleapis.com/{UPLOAD_BUCKET}"

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", KEY_PATH)

print("[init] Connecting to Firestore and GCS …", flush=True)
from google.oauth2 import service_account
from google.cloud import firestore as gc_firestore
from google.cloud import storage as gcs_storage

_creds = service_account.Credentials.from_service_account_file(
    KEY_PATH,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
db = gc_firestore.Client(project=PROJECT_ID, credentials=_creds)
print("[init] Firestore OK", flush=True)

_sa = service_account.Credentials.from_service_account_file(KEY_PATH)
gcs_client   = gcs_storage.Client(credentials=_sa, project=PROJECT_ID)
upload_bkt   = gcs_client.bucket(UPLOAD_BUCKET)
ref_bkt      = gcs_client.bucket(REF_BUCKET)
print("[init] GCS OK", flush=True)

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})

# ── Load GCS Inventory ────────────────────────────────────────────────────────
print(f"[init] Loading GCS inventory from {GCS_INVENTORY} …", flush=True)
_gcs_rows: list[dict] = []
with open(GCS_INVENTORY, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        _gcs_rows.append(row)
print(f"[init] Loaded {len(_gcs_rows):,} GCS rows", flush=True)

# Only reference-library rows (the bucket we read from)
REF_ROWS = [r for r in _gcs_rows if r["bucket"] == REF_BUCKET]
print(f"[init] Reference library rows: {len(REF_ROWS):,}", flush=True)

# Build keyword → list[row] map (on path.lower())
_kw_index: dict[str, list[dict]] = defaultdict(list)
for row in REF_ROWS:
    p = row["path"].lower()
    _kw_index[p].append(row)   # exact
    # Also index by each slash-separated segment
    for seg in p.split("/"):
        if len(seg) > 3:
            _kw_index[seg].append(row)

# ── Load Presidential $1 JSON ─────────────────────────────────────────────────
print(f"[init] Loading presidential dollars JSON …", flush=True)
with open(PRES_JSON, encoding="utf-8") as f:
    PRES_DATA: dict = json.load(f)

# Build president-name → best obverse + reverse entries
# The JSON has keys like 'ford', 'lincoln', 'van_buren', full paths, etc.
PRES_OBVERSE: dict[str, dict] = {}   # name → row with bucket/path/public_url
PRES_REVERSE: dict[str, dict] = {}

# The universal presidential dollar reverse image
PRES_UNIVERSAL_REVERSE = {
    "bucket":     REF_BUCKET,
    "path":       "reference_library/wikimedia_uscoin/Dollar_coins_of_the_United_States/Presidential__1_Coin_Program/Presidential_dollar_coin_reverse.png",
    "public_url": "https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/Dollar_coins_of_the_United_States/Presidential__1_Coin_Program/Presidential_dollar_coin_reverse.png",
}

for key, entry in PRES_DATA.items():
    # Short name keys (ford, reagan, etc.) are president name lookups
    if "/" not in key and entry.get("bucket") == REF_BUCKET:
        name = key.lower().replace("_", " ")
        # Classify as obverse or reverse based on path content
        p = (entry.get("path") or "").lower()
        if any(x in p for x in ["reverse", "_rev", "-rev", "back"]):
            PRES_REVERSE[name] = entry
        else:
            PRES_OBVERSE[name] = entry

# Add the universal reverse to ALL presidents as fallback
_UNIVERSAL_REV_PATH = "reference_library/wikimedia_uscoin/Dollar_coins_of_the_United_States/Presidential__1_Coin_Program/Presidential_dollar_coin_reverse.png"

# ── Build typed keyword search helpers ────────────────────────────────────────

def gcs_find(keywords: list[str], side_hints: list[str] = None) -> dict | None:
    """
    Search REF_ROWS for first row whose path (lowercased) contains ALL keywords.
    If side_hints given, further filter to rows whose path contains at least one hint.
    Returns row dict or None.
    """
    kw_lower = [k.lower() for k in keywords]
    sh_lower = [s.lower() for s in (side_hints or [])]

    # Prefer bulk_programs paths first, then any match
    def score(row):
        p = row["path"].lower()
        bulk = "bulk_programs" in p
        return (0 if bulk else 1)

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


def gcs_find_any(keywords: list[str], side_hints: list[str] = None) -> dict | None:
    """Like gcs_find but tries each keyword list progressively shorter."""
    for length in range(len(keywords), 0, -1):
        result = gcs_find(keywords[:length], side_hints)
        if result:
            return result
    return None

# ── Coin classifier ───────────────────────────────────────────────────────────
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
    if "dollar" in d: return "morgan_dollar"  # generic fallback
    return ""


# ── GCS matching logic per coin type ─────────────────────────────────────────
# Maps coin_type → list of (obverse_keywords, reverse_keywords)
# Prefer 'bulk_programs' paths (handled by gcs_find score)

COIN_GCS_MAP = {
    "morgan_dollar": {
        "obverse": ["morgan", "obverse"],
        "reverse": ["morgan", "reverse"],
    },
    "peace_dollar": {
        "obverse": ["peace", "obverse"],
        "reverse": ["peace", "reverse"],
    },
    "eisenhower_dollar": {
        "obverse": ["eisenhower", "obverse"],
        "reverse": ["eisenhower", "reverse"],
    },
    "kennedy_half": {
        "obverse": ["kennedy", "obverse"],
        "reverse": ["kennedy", "reverse"],
    },
    "franklin_half": {
        "obverse": ["franklin", "obverse"],
        "reverse": ["franklin", "reverse"],
    },
    "walking_liberty": {
        "obverse": ["walking", "obverse"],
        "reverse": ["walking", "reverse"],
    },
    "barber_dime": {
        "obverse": ["barber", "dime", "obverse"],
        "reverse": ["barber", "dime", "reverse"],
    },
    "barber_quarter": {
        "obverse": ["barber", "quarter", "obverse"],
        "reverse": ["barber", "quarter", "reverse"],
    },
    "mercury_dime": {
        "obverse": ["mercury", "obverse"],
        "reverse": ["mercury", "reverse"],
    },
    "roosevelt_dime": {
        "obverse": ["roosevelt", "dime", "obverse"],
        "reverse": ["roosevelt", "dime", "reverse"],
    },
    "buffalo_nickel": {
        "obverse": ["buffalo", "obverse"],
        "reverse": ["buffalo", "reverse"],
    },
    "jefferson_nickel": {
        "obverse": ["jefferson", "nickel", "obverse"],
        "reverse": ["jefferson", "nickel", "reverse"],
    },
    "lincoln_wheat_cent": {
        "obverse": ["wheat", "obverse"],
        "reverse": ["wheat", "reverse"],
    },
    "wheat_cent": {
        "obverse": ["wheat", "obverse"],
        "reverse": ["wheat", "reverse"],
    },
    "memorial_cent": {
        "obverse": ["lincoln", "memorial", "obverse"],
        "reverse": ["lincoln", "memorial", "reverse"],
    },
    "indian_head_cent": {
        "obverse": ["indian", "cent", "obverse"],
        "reverse": ["indian", "cent", "reverse"],
    },
    "washington_quarter": {
        "obverse": ["washington", "quarter", "obverse"],
        "reverse": ["washington", "quarter", "reverse"],
    },
    "american_women_quarter": {
        "obverse": ["american", "women", "obverse"],
        "reverse": ["american", "women", "reverse"],
    },
    "america_beautiful": {
        "obverse": ["america", "beautiful", "obverse"],
        "reverse": ["america", "beautiful", "reverse"],
    },
    "native_american_dollar": {
        "obverse": ["native", "obverse"],
        "reverse": ["native", "reverse"],
    },
    "three_cent_nickel": {
        "obverse": ["three", "cent", "obverse"],
        "reverse": ["three", "cent", "reverse"],
    },
    "seated_liberty_quarter": {
        "obverse": ["seated", "obverse"],
        "reverse": ["seated", "reverse"],
    },
    "half_cent_classic_head": {
        "obverse": ["half", "cent", "obverse"],
        "reverse": ["half", "cent", "reverse"],
    },
}


def slugify(text: str) -> str:
    """Convert text to slug for GCS path matching."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def match_state_quarter(coin: dict) -> tuple[dict | None, dict | None]:
    """Special handler for 50-state quarters — match by state name."""
    theme = (coin.get("theme") or coin.get("program") or "").lower()
    program = (coin.get("program") or "").lower()

    # Extract state name from theme or program
    # e.g., "New Jersey", "Ohio", "Delaware"
    state = ""
    for field in [theme, program]:
        # Remove common prefixes
        cleaned = re.sub(r"(50 state|state quarter|statehood quarter|\d{4})", "", field, flags=re.I).strip()
        if cleaned and len(cleaned) > 2:
            state = cleaned.strip()
            break

    if not state:
        return None, None

    state_slug = slugify(state)
    # e.g. "new-jersey" → "new-jersey" in path
    obv = gcs_find(["50_state_quarters", state_slug], ["obverse", "uncirculated"])
    rev = gcs_find(["50_state_quarters", state_slug], ["reverse"])
    return obv, rev


def match_presidential_dollar(coin: dict) -> tuple[dict | None, dict | None]:
    """Special handler for Presidential $1 — match by president name."""
    theme = (coin.get("theme") or "").lower().strip()

    if not theme:
        return None, None

    # Try to find the president name in the PRES_DATA
    # First, exact/partial match on the name keys
    president_key = None
    theme_words = theme.lower().split()

    for key in PRES_DATA:
        if "/" in key:
            continue  # skip path-style keys
        key_lower = key.lower().replace("_", " ")
        if key_lower in theme or any(kw in key_lower for kw in theme_words if len(kw) > 3):
            president_key = key
            break

    # Try reverse match: is any word of the theme a key?
    if not president_key:
        for word in theme_words:
            if len(word) > 3 and word in PRES_DATA:
                president_key = word
                break

    # Also check bulk_programs/presidential folder by scanning inventory
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

    # Try bulk_programs/presidential with slugified president name
    president_slug = slugify(theme.split("(")[0].strip())  # remove "(21st president)" etc
    # Try first last name only
    name_parts = president_slug.split("-")
    for part in reversed(name_parts):  # last name tends to be last
        if len(part) > 3:
            bulk_obv = gcs_find(["bulk_programs", "presidential", part], ["obverse"])
            bulk_rev = gcs_find(["bulk_programs", "presidential", part], ["reverse"])
            if bulk_obv and not obv_row:
                obv_row = bulk_obv
            if bulk_rev and not rev_row:
                rev_row = bulk_rev
            if obv_row and rev_row:
                break

    # Universal presidential reverse as fallback
    if not rev_row:
        rev_row = PRES_UNIVERSAL_REVERSE

    return obv_row, rev_row


def match_native_american(coin: dict) -> tuple[dict | None, dict | None]:
    """Match Sacagawea / Native American dollars."""
    obv = gcs_find(["sacagawea"], ["obverse", "front"])
    if not obv:
        obv = gcs_find(["native_american"], ["obverse", "front"])
    if not obv:
        obv = gcs_find(["native", "american"], ["obverse"])

    rev = gcs_find(["sacagawea"], ["reverse", "back"])
    if not rev:
        rev = gcs_find(["native_american"], ["reverse"])
    if not rev:
        rev = gcs_find(["native", "american"], ["reverse"])
    return obv, rev


def match_america_beautiful(coin: dict) -> tuple[dict | None, dict | None]:
    """Match ATB quarters by park/design name from Theme/Subject."""
    theme = (coin.get("theme") or "").lower().strip()
    program = (coin.get("program") or "").lower()

    # Extract park name
    park = re.sub(r"(national park|national monument|quarter|\d{4})", "", theme, flags=re.I).strip()
    park_slug = slugify(park)
    park_parts = [p for p in park_slug.split("-") if len(p) > 2]

    obv = None
    rev = None

    if park_parts:
        obv = gcs_find(["america_beautiful"] + park_parts[:2], ["obverse"])
        rev = gcs_find(["america_beautiful"] + park_parts[:2], ["reverse"])

    if not obv:
        obv = gcs_find(["america_beautiful"], ["obverse"])
    if not rev:
        rev = gcs_find(["america_beautiful"], ["reverse"])
    return obv, rev


def match_american_women_quarter(coin: dict) -> tuple[dict | None, dict | None]:
    """Match American Women Quarters by subject name."""
    theme = (coin.get("theme") or "").lower().strip()
    theme_slug = slugify(theme)
    theme_parts = [p for p in theme_slug.split("-") if len(p) > 3]

    obv = None
    rev = None
    if theme_parts:
        obv = gcs_find(["american_women"] + theme_parts[:2], ["obverse"])
        rev = gcs_find(["american_women"] + theme_parts[:2], ["reverse"])

    if not obv:
        obv = gcs_find(["american_women"], ["obverse"])
    if not rev:
        rev = gcs_find(["american_women"], ["reverse"])
    return obv, rev


def match_generic(coin_type: str) -> tuple[dict | None, dict | None]:
    """Match using COIN_GCS_MAP keywords."""
    spec = COIN_GCS_MAP.get(coin_type)
    if not spec:
        return None, None

    obv_kw = spec.get("obverse", [])
    rev_kw = spec.get("reverse", [])

    obv = gcs_find(obv_kw)
    if not obv and len(obv_kw) > 2:
        obv = gcs_find(obv_kw[:-1])  # relax last keyword

    rev = gcs_find(rev_kw)
    if not rev and len(rev_kw) > 2:
        rev = gcs_find(rev_kw[:-1])
    return obv, rev


def gcs_match_coin(coin: dict) -> tuple[dict | None, dict | None]:
    """
    Master GCS match: returns (obverse_row, reverse_row) or None for each.
    Each row is a dict with at least: bucket, path, public_url.
    """
    denom   = coin.get("denomination", "")
    program = coin.get("program", "")
    year    = coin.get("year", "")
    theme   = coin.get("theme", "")

    coin_type = classify_coin(denom, program, year)

    if coin_type == "presidential_dollar":
        return match_presidential_dollar(coin)
    if coin_type == "native_american_dollar":
        return match_native_american(coin)
    if coin_type == "state_quarter":
        return match_state_quarter(coin)
    if coin_type == "america_beautiful":
        return match_america_beautiful(coin)
    if coin_type == "american_women_quarter":
        return match_american_women_quarter(coin)

    return match_generic(coin_type)


# ── coin_image_index lookup ───────────────────────────────────────────────────
_index_cache: dict[str, str | None] = {}

def lookup_index(year: str, mint: str, programs: list[str]) -> tuple[str | None, str | None]:
    """Try coin_image_index Firestore docs. Returns (obverse_url, reverse_url)."""
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

    def fetch(doc_id):
        if doc_id in _index_cache:
            return _index_cache[doc_id]
        try:
            doc = db.collection("coin_image_index").document(doc_id).get()
            url = doc.to_dict().get("image_url") if doc.exists else None
            _index_cache[doc_id] = url
            return url
        except Exception:
            _index_cache[doc_id] = None
            return None

    obv_url = None
    for cid in obv_candidates:
        u = fetch(cid)
        if u:
            obv_url = u
            break

    rev_url = None
    for cid in rev_candidates:
        u = fetch(cid)
        if u:
            rev_url = u
            break

    return obv_url, rev_url


COIN_TYPE_PROGRAMS = {
    "barber_dime":           ["barber-dime", "dime"],
    "barber_quarter":        ["barber-quarter", "quarter"],
    "buffalo_nickel":        ["buffalo-nickel", "nickel"],
    "indian_head_cent":      ["indian-head-cent", "cent"],
    "jefferson_nickel":      ["jefferson-nickel", "nickel"],
    "kennedy_half":          ["kennedy-half-dollar"],
    "franklin_half":         ["kennedy-half-dollar", "dollar"],
    "walking_liberty":       ["kennedy-half-dollar", "dollar"],
    "wheat_cent":            ["lincoln-cent", "cent"],
    "memorial_cent":         ["lincoln-cent", "cent"],
    "mercury_dime":          ["mercury-dime", "dime"],
    "morgan_dollar":         ["morgan-dollar", "dollar"],
    "peace_dollar":          ["dollar"],
    "eisenhower_dollar":     ["dollar"],
    "presidential_dollar":   ["presidential-dollars", "dollar"],
    "native_american_dollar":["native-american-dollar", "dollar"],
    "roosevelt_dime":        ["dime"],
    "state_quarter":         ["50-state-quarters", "quarter"],
    "american_women_quarter":["american-women-quarters", "quarter"],
    "america_beautiful":     ["america-the-beautiful", "quarter"],
    "washington_quarter":    ["quarter"],
    "three_cent_nickel":     ["nickel"],
    "seated_liberty_quarter":["quarter"],
    "half_cent_classic_head":["cent"],
}


# ── Wikimedia fallback ────────────────────────────────────────────────────────
WIKIMEDIA_QUERIES = {
    "barber_dime":           "Barber dime reverse 1892 coin",
    "barber_quarter":        "Barber quarter reverse 1892 coin",
    "buffalo_nickel":        "Buffalo nickel reverse bison 1913",
    "indian_head_cent":      "Indian Head penny cent reverse wreath",
    "jefferson_nickel":      "Jefferson nickel reverse Monticello",
    "kennedy_half":          "Kennedy half dollar reverse presidential seal",
    "franklin_half":         "Franklin half dollar reverse Liberty Bell",
    "walking_liberty":       "Walking Liberty half dollar reverse eagle",
    "wheat_cent":            "Lincoln wheat cent reverse penny",
    "memorial_cent":         "Lincoln Memorial cent reverse",
    "mercury_dime":          "Mercury dime reverse fasces 1916",
    "morgan_dollar":         "Morgan dollar reverse eagle 1921",
    "peace_dollar":          "Peace dollar reverse eagle",
    "eisenhower_dollar":     "Eisenhower dollar reverse eagle moon 1971",
    "presidential_dollar":   "Presidential dollar reverse torch Statue of Liberty",
    "native_american_dollar":"Native American dollar reverse Sacagawea",
    "roosevelt_dime":        "Roosevelt dime reverse torch 1946",
    "state_quarter":         "50 state quarter reverse",
    "american_women_quarter":"American Women Quarters reverse 2022",
    "america_beautiful":     "America the Beautiful quarter reverse national park",
    "washington_quarter":    "Washington quarter reverse eagle",
    "three_cent_nickel":     "Three cent nickel reverse Roman numeral III",
    "seated_liberty_quarter":"Seated Liberty quarter reverse eagle",
    "half_cent_classic_head":"Classic Head half cent reverse",
}

def wikimedia_search(query: str, side: str = "reverse") -> str | None:
    """Search Wikimedia Commons for a coin image. Returns URL or None."""
    full_query = f"{query} {side}"
    url = (
        "https://commons.wikimedia.org/w/api.php"
        f"?action=query&list=search&srsearch={quote(full_query)}"
        "&srnamespace=6&srlimit=5&format=json"
    )
    try:
        r = SESSION.get(url, timeout=15)
        r.raise_for_status()
        results = r.json().get("query", {}).get("search", [])
        for item in results:
            title = item.get("title", "")
            if not title.startswith("File:"):
                continue
            # Get image URL
            info_url = (
                "https://commons.wikimedia.org/w/api.php"
                f"?action=query&titles={quote(title)}&prop=imageinfo"
                "&iiprop=url&format=json"
            )
            ir = SESSION.get(info_url, timeout=15)
            ir.raise_for_status()
            pages = ir.json().get("query", {}).get("pages", {})
            for page in pages.values():
                img_url = (page.get("imageinfo") or [{}])[0].get("url")
                if img_url:
                    return img_url
    except Exception as e:
        print(f"    [wiki] Error: {e}", flush=True)
    return None


# ── Download + Re-upload ───────────────────────────────────────────────────────
def download_from_ref_bucket(ref_path: str) -> bytes | None:
    """Download bytes from numista-reference-library."""
    try:
        blob = ref_bkt.blob(ref_path)
        data = blob.download_as_bytes()
        return data
    except Exception as e:
        print(f"    [gcs-dl] Error downloading {ref_path}: {e}", flush=True)
        return None


def download_from_url(url: str) -> bytes | None:
    """Download image bytes from any HTTP URL (Wikimedia fallback)."""
    try:
        r = SESSION.get(url, timeout=30)
        r.raise_for_status()
        return r.content
    except Exception as e:
        print(f"    [url-dl] Error downloading {url}: {e}", flush=True)
        return None


def upload_to_user_bucket(doc_id: str, side: str, data: bytes, content_type: str = "image/jpeg") -> str:
    """
    Upload image to user bucket at users/{email}/coins/{doc_id}/{side}.jpg
    Returns the public URL.
    DO NOT call blob.make_public()
    """
    dest_path = f"users/{USER_EMAIL}/coins/{doc_id}/{side}.jpg"
    blob = upload_bkt.blob(dest_path)
    blob.upload_from_string(data, content_type=content_type)
    pub_url = f"{UPLOAD_BASE_URL}/{dest_path}"
    return pub_url


def update_firestore(doc_id: str, side: str, url: str, source: str):
    """Update image_url_obverse or image_url_reverse in Firestore."""
    field = f"image_url_{side}"
    db.collection(COINS_COLL).document(doc_id).update({
        field: url,
        "image_source": source,
        "image_enriched_at": gc_firestore.SERVER_TIMESTAMP,
    })


# ── Fetch jseaman gaps from Firestore ─────────────────────────────────────────
def fetch_gaps() -> tuple[list[dict], list[dict]]:
    """
    Returns:
      group_a: both images missing
      group_b: obverse present, reverse missing
    """
    print(f"[firestore] Fetching all coins from {COINS_COLL} …", flush=True)
    docs = list(db.collection(COINS_COLL).stream())
    print(f"[firestore] Retrieved {len(docs):,} docs", flush=True)

    group_a, group_b = [], []

    for doc in docs:
        data = doc.to_dict() or {}
        obv = (data.get("image_url_obverse") or "").strip()
        rev = (data.get("image_url_reverse") or "").strip()

        has_obv = bool(obv)
        has_rev = bool(rev)

        if has_obv and has_rev:
            continue  # complete, skip

        coin = {
            "doc_id":      doc.id,
            "year":        data.get("Year") or data.get("year") or "",
            "mint_mark":   data.get("Mint Mark") or data.get("mint_mark") or "",
            "denomination":data.get("Denomination") or data.get("denomination") or "",
            "program":     data.get("Program/Series") or data.get("program") or data.get("series") or "",
            "theme":       data.get("Theme/Subject") or data.get("theme") or "",
            "condition":   data.get("Condition") or data.get("condition") or "",
            "image_url_obverse": obv,
            "image_url_reverse": rev,
        }

        if not has_obv and not has_rev:
            group_a.append(coin)
        elif has_obv and not has_rev:
            group_b.append(coin)

    return group_a, group_b


# ── Process a single coin ──────────────────────────────────────────────────────
def process_coin(coin: dict, group: str, dry_run: bool) -> dict:
    """
    Returns a result dict describing what was done.
    group: 'A' (both missing) or 'B' (obverse present, reverse missing)
    """
    doc_id  = coin["doc_id"]
    denom   = coin["denomination"]
    program = coin["program"]
    year    = coin["year"]
    theme   = coin["theme"]
    coin_type = classify_coin(denom, program, year)

    result = {
        "doc_id":      doc_id,
        "year":        year,
        "denomination":denom,
        "program":     program,
        "theme":       theme,
        "coin_type":   coin_type,
        "group":       group,
        "obverse_url": coin.get("image_url_obverse", ""),
        "reverse_url": coin.get("image_url_reverse", ""),
        "obverse_source": None,
        "reverse_source": None,
        "obverse_fixed":  False,
        "reverse_fixed":  False,
        "errors":      [],
    }

    needs_obv = (group == "A")
    needs_rev = True  # both groups need reverse

    print(f"  [{group}] {doc_id} | {year} {denom} {program} ({coin_type})", flush=True)

    # ── STEP 1: GCS reference library match ──────────────────────────────────
    gcs_obv_row, gcs_rev_row = gcs_match_coin(coin)

    # ── STEP 2: coin_image_index fallback ────────────────────────────────────
    programs = COIN_TYPE_PROGRAMS.get(coin_type, [])
    idx_obv_url, idx_rev_url = lookup_index(year, coin.get("mint_mark", ""), programs)

    # ── STEP 3: Resolve final sources ────────────────────────────────────────
    def resolve_obverse() -> tuple[str | None, str | None]:
        """Returns (url_or_ref_path, source_label)"""
        if gcs_obv_row:
            return gcs_obv_row, "gcs_reference_library"
        if idx_obv_url:
            return idx_obv_url, "coin_image_index"
        # Wikimedia
        q = WIKIMEDIA_QUERIES.get(coin_type, f"{year} {denom} {program} obverse")
        url = wikimedia_search(q, side="obverse")
        if url:
            return url, "wikimedia"
        return None, None

    def resolve_reverse() -> tuple[str | None, str | None]:
        if gcs_rev_row:
            return gcs_rev_row, "gcs_reference_library"
        if idx_rev_url:
            return idx_rev_url, "coin_image_index"
        q = WIKIMEDIA_QUERIES.get(coin_type, f"{year} {denom} {program} reverse")
        url = wikimedia_search(q, side="reverse")
        if url:
            return url, "wikimedia"
        return None, None

    def do_side(side: str, source_data, source_label: str) -> bool:
        """Download, upload, and update Firestore for one side. Returns success."""
        if not source_data:
            return False

        if not dry_run:
            # Download
            if isinstance(source_data, dict):
                # GCS reference library row
                ref_path = source_data.get("path", "")
                img_bytes = download_from_ref_bucket(ref_path)
            elif isinstance(source_data, str) and source_data.startswith("http"):
                img_bytes = download_from_url(source_data)
            else:
                result["errors"].append(f"{side}: unknown source type {type(source_data)}")
                return False

            if not img_bytes:
                result["errors"].append(f"{side}: download failed")
                return False

            # Upload
            try:
                pub_url = upload_to_user_bucket(doc_id, side, img_bytes)
            except Exception as e:
                result["errors"].append(f"{side}: upload failed: {e}")
                return False

            # Firestore update
            try:
                update_firestore(doc_id, side, pub_url, source_label)
            except Exception as e:
                result["errors"].append(f"{side}: firestore update failed: {e}")
                return False

            result[f"{side}_url"] = pub_url
        else:
            # Dry run: just log what we'd do
            if isinstance(source_data, dict):
                result[f"{side}_url"] = f"[DRY_RUN] {source_data.get('public_url', source_data.get('path', '?'))}"
            else:
                result[f"{side}_url"] = f"[DRY_RUN] {source_data}"

        result[f"{side}_source"]  = source_label
        result[f"{side}_fixed"]   = True
        print(f"    ✓ {side} [{source_label}]", flush=True)
        return True

    # Process obverse (Group A only)
    if needs_obv:
        src, lbl = resolve_obverse()
        do_side("obverse", src, lbl)

    # Process reverse (both groups)
    src, lbl = resolve_reverse()
    do_side("reverse", src, lbl)

    return result


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="GCS-first image enrichment for jseaman")
    ap.add_argument("--dry-run", action="store_true", help="Do not write to GCS/Firestore")
    ap.add_argument("--limit",   type=int, default=0,  help="Max coins to process (0 = all)")
    ap.add_argument("--group",   choices=["A", "B", "all"], default="all",
                    help="Which group to process: A (both missing), B (reverse only), all")
    args = ap.parse_args()

    print(f"\n{'='*64}", flush=True)
    print(f"  GCS-FIRST IMAGE ENRICHMENT — {USER_EMAIL}", flush=True)
    print(f"  Dry Run: {args.dry_run}   Limit: {args.limit or 'all'}   Group: {args.group}", flush=True)
    print(f"{'='*64}\n", flush=True)

    # Fetch gaps
    group_a, group_b = fetch_gaps()
    print(f"\n[query] Group A (both missing): {len(group_a)}", flush=True)
    print(f"[query] Group B (reverse missing): {len(group_b)}", flush=True)

    # Build work list
    work: list[tuple[dict, str]] = []
    if args.group in ("A", "all"):
        work.extend((c, "A") for c in group_a)
    if args.group in ("B", "all"):
        work.extend((c, "B") for c in group_b)

    if args.limit:
        work = work[:args.limit]

    print(f"[run] Processing {len(work)} coins …\n", flush=True)

    results = []
    series_stats: dict[str, dict] = defaultdict(lambda: {"total": 0, "fixed_obv": 0, "fixed_rev": 0, "sources": defaultdict(int)})
    t_start = time.time()

    for i, (coin, grp) in enumerate(work, 1):
        print(f"[{i}/{len(work)}]", end=" ", flush=True)
        res = process_coin(coin, grp, args.dry_run)
        results.append(res)

        ct = res["coin_type"] or "unknown"
        series_stats[ct]["total"] += 1
        if res["obverse_fixed"]:
            series_stats[ct]["fixed_obv"] += 1
            src = res.get("obverse_source") or "unknown"
            series_stats[ct]["sources"][src] += 1
        if res["reverse_fixed"]:
            series_stats[ct]["fixed_rev"] += 1
            src = res.get("reverse_source") or "unknown"
            series_stats[ct]["sources"][src] += 1

    elapsed = time.time() - t_start

    # ── Summary ───────────────────────────────────────────────────────────────
    total_processed  = len(results)
    fixed_obv        = sum(1 for r in results if r["obverse_fixed"])
    fixed_rev        = sum(1 for r in results if r["reverse_fixed"])
    gcs_obv          = sum(1 for r in results if r.get("obverse_source") == "gcs_reference_library")
    gcs_rev          = sum(1 for r in results if r.get("reverse_source") == "gcs_reference_library")
    idx_obv          = sum(1 for r in results if r.get("obverse_source") == "coin_image_index")
    idx_rev          = sum(1 for r in results if r.get("reverse_source") == "coin_image_index")
    wiki_obv         = sum(1 for r in results if r.get("obverse_source") == "wikimedia")
    wiki_rev         = sum(1 for r in results if r.get("reverse_source") == "wikimedia")
    still_missing    = [r for r in results if not r["obverse_fixed"] and not r["reverse_fixed"]]
    errors           = [r for r in results if r["errors"]]

    print(f"\n{'='*64}", flush=True)
    print(f"  SUMMARY", flush=True)
    print(f"{'='*64}", flush=True)
    print(f"  Coins processed    : {total_processed}", flush=True)
    print(f"  Obverses fixed     : {fixed_obv}  (GCS:{gcs_obv} | index:{idx_obv} | wiki:{wiki_obv})", flush=True)
    print(f"  Reverses fixed     : {fixed_rev}  (GCS:{gcs_rev} | index:{idx_rev} | wiki:{wiki_rev})", flush=True)
    print(f"  Coins still empty  : {len(still_missing)}", flush=True)
    print(f"  Errors             : {len(errors)}", flush=True)
    print(f"  Elapsed            : {elapsed:.1f}s", flush=True)

    print(f"\n  By coin series:", flush=True)
    for ct, st in sorted(series_stats.items()):
        src_str = " ".join(f"{k}:{v}" for k, v in st["sources"].items())
        print(f"    {ct:<30} total:{st['total']:>3}  obv:{st['fixed_obv']:>3}  rev:{st['fixed_rev']:>3}  [{src_str}]", flush=True)

    if still_missing:
        print(f"\n  UNFIXED coins:", flush=True)
        for r in still_missing:
            print(f"    {r['doc_id']} | {r['year']} {r['denomination']} {r['program']} ({r['coin_type']})", flush=True)

    # ── Re-query Firestore for final coverage stats ───────────────────────────
    if not args.dry_run and total_processed > 0:
        print(f"\n[coverage] Re-querying Firestore for final coverage …", flush=True)
        all_docs = list(db.collection(COINS_COLL).stream())
        total_coins  = len(all_docs)
        has_both     = sum(1 for d in all_docs if
                           (d.to_dict() or {}).get("image_url_obverse", "").strip() and
                           (d.to_dict() or {}).get("image_url_reverse", "").strip())
        coverage_pct = (has_both / total_coins * 100) if total_coins else 0
        print(f"  Total coins       : {total_coins}", flush=True)
        print(f"  Full coverage (both imgs): {has_both}  ({coverage_pct:.1f}%)", flush=True)
    else:
        total_coins = None
        has_both    = None
        coverage_pct = None

    # ── Save log ──────────────────────────────────────────────────────────────
    log_data = {
        "run_timestamp":    time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dry_run":          args.dry_run,
        "group_filter":     args.group,
        "total_processed":  total_processed,
        "fixed_obverse":    fixed_obv,
        "fixed_reverse":    fixed_rev,
        "source_breakdown": {
            "gcs_reference_library": {"obverse": gcs_obv, "reverse": gcs_rev},
            "coin_image_index":      {"obverse": idx_obv, "reverse": idx_rev},
            "wikimedia":             {"obverse": wiki_obv, "reverse": wiki_rev},
        },
        "coverage": {
            "total_coins":    total_coins,
            "full_coverage":  has_both,
            "coverage_pct":   coverage_pct,
        },
        "series_breakdown": {
            ct: {k: (dict(v) if isinstance(v, defaultdict) else v) for k, v in st.items()}
            for ct, st in series_stats.items()
        },
        "unfixed_coins": [
            {"doc_id": r["doc_id"], "year": r["year"], "denomination": r["denomination"],
             "program": r["program"], "coin_type": r["coin_type"], "errors": r["errors"]}
            for r in still_missing
        ],
        "detail": results,
    }

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, default=str)
    print(f"\n[log] Saved to: {LOG_PATH}", flush=True)
    print("Done.\n", flush=True)


if __name__ == "__main__":
    main()
