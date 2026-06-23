# -*- coding: utf-8 -*-
"""
jseaman_reverse_enrichment.py  (v3 — uses google.cloud.firestore directly)
==============================
Finds reverse images for all 379 coins in jseaman1204@gmail.com's collection
that have an obverse image but no reverse.

Source priority:
  1. coin_image_index Firestore collection (direct doc-ID lookup by year+program)
  2. Wikimedia Commons API search
  3. Static fallback library (fixed-reverse coin types)

Usage:
  python jseaman_reverse_enrichment.py --dry-run --limit 20
  python jseaman_reverse_enrichment.py --dry-run --series barber_dime
  python jseaman_reverse_enrichment.py           # full run
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

# Force line-buffered stdout (critical for batch/task-runner mode)
try:
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
    )
except Exception:
    pass

# ─── Config ───────────────────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
KEY_PATH    = os.path.join(SCRIPT_DIR, "serviceAccountKey.json.json")
PROJECT_ID  = "studio-9101802118-8c9a8"
USER_EMAIL  = "jseaman1204@gmail.com"
COINS_COLL  = f"users/{USER_EMAIL}/coins"
BUCKET_NAME = "numista-uploads-studio-9101802118-8c9a8"
GAP_CSV     = os.path.join(SCRIPT_DIR, "jseaman_image_gaps.csv")
USER_AGENT  = "NumistaAI/1.0 (eric@numista.ai)"
LOG_PATH    = os.path.join(SCRIPT_DIR, "reverse_enrichment_log.json")

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", KEY_PATH)

# ─── Firestore + GCS init ────────────────────────────────────────────────────
# Use google.cloud.firestore directly (same as check_jseaman_image_gaps.py)
print("[init] Connecting to Firestore …", flush=True)
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
gcs_client = gcs_storage.Client(credentials=_sa, project=PROJECT_ID)
bucket = gcs_client.bucket(BUCKET_NAME)
print("[init] GCS OK", flush=True)

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})

# ─── Coin classifier ──────────────────────────────────────────────────────────
# Maps each coin to (coin_type_key, index_programs) where index_programs is
# a list of program slugs to try in coin_image_index doc lookups.
# Doc IDs follow pattern: {year}_{program}_reverse OR {year}_{mint}_{program}_reverse

COIN_TYPE_PROGRAMS = {
    # (classifier_key): [program slugs in coin_image_index order of preference]
    "barber_dime":           ["barber-dime",   "dime",       "mercury-dime"],
    "barber_quarter":        ["barber-quarter", "quarter",    "coins__nnc_"],
    "buffalo_nickel":        ["buffalo-nickel", "nickel"],
    "indian_head_cent":      ["indian-head-cent", "cent", "lincoln-cent"],
    "jefferson_nickel":      ["jefferson-nickel", "nickel"],
    "kennedy_half":          ["kennedy-half-dollar"],
    "franklin_half":         ["kennedy-half-dollar", "dollar"],
    "walking_liberty":       ["kennedy-half-dollar", "dollar"],
    "lincoln_wheat_cent":    ["lincoln-cent",  "cent"],
    "wheat_cent":            ["lincoln-cent",  "cent"],
    "memorial_cent":         ["lincoln-cent",  "cent"],
    "mercury_dime":          ["mercury-dime",  "dime"],
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
    "three_cent_nickel":     ["nickel", "coins__nnc_"],
    "seated_liberty_quarter":["quarter", "coins__nnc_"],
    "capped_bust_quarter":   ["quarter", "coins__nnc_"],
    "half_cent_classic_head":["cent", "coins__nnc_"],
    "draped_bust_dollar":    ["dollar"],
}

GCS_BASE = "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8"
STATIC_FALLBACKS = {
    # These are static fallback URLs if index lookup fails
    "morgan_dollar":    f"{GCS_BASE}/reference_images/us_mint/1921-morgan-silver-dollar-reverse.jpg",
    "kennedy_half":     f"{GCS_BASE}/reference_images/us_mint/1964-kennedy-half-dollar-reverse.jpg",
    "franklin_half":    f"{GCS_BASE}/reference_images/us_mint/1963-franklin-half-dollar-reverse.jpg",
    "walking_liberty":  f"{GCS_BASE}/reference_images/us_mint/1943-walking-liberty-half-dollar-reverse.jpg",
    "wheat_cent":       f"{GCS_BASE}/reference_images/us_mint/lincoln-wheat-cent-reverse.jpg",
    "memorial_cent":    f"{GCS_BASE}/reference_images/us_mint/lincoln-memorial-cent-reverse.jpg",
    "roosevelt_dime":   f"{GCS_BASE}/reference_images/us_mint/1946-roosevelt-dime-reverse.jpg",
    "mercury_dime":     f"{GCS_BASE}/reference_images/us_mint/1916-mercury-dime-reverse.jpg",
    "barber_dime":      f"{GCS_BASE}/reference_images/us_mint/1892-barber-dime-reverse.jpg",
    "barber_quarter":   f"{GCS_BASE}/reference_images/us_mint/1892-barber-quarter-reverse.jpg",
    "washington_quarter": f"{GCS_BASE}/reference_images/us_mint/2008-50-state-quarters-coin-uncirculated-obverse.jpg",
    "jefferson_nickel": f"{GCS_BASE}/reference_images/us_mint/2005-westward-journey-nickel-series-uncirculated-obverse.jpg",
    "buffalo_nickel":   f"{GCS_BASE}/reference_images/us_mint/1913-buffalo-nickel-type-2-reverse.jpg",
    "indian_head_cent": f"{GCS_BASE}/reference_images/us_mint/1907-indian-head-cent-reverse.jpg",
    "eisenhower_dollar": f"{GCS_BASE}/reference_images/us_mint/1971-eisenhower-dollar-reverse.jpg",
}

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
    "presidential_dollar":   "Presidential dollar reverse torch",
    "native_american_dollar":"Native American dollar reverse Sacagawea",
    "roosevelt_dime":        "Roosevelt dime reverse torch 1946",
    "state_quarter":         "50 state quarter reverse",
    "american_women_quarter":"American Women Quarters reverse 2022",
    "america_beautiful":     "America the Beautiful quarter reverse national park",
    "washington_quarter":    "Washington quarter reverse eagle",
    "three_cent_nickel":     "Three cent nickel reverse Roman numeral III",
    "seated_liberty_quarter":"Seated Liberty quarter reverse eagle",
    "capped_bust_quarter":   "Capped Bust quarter reverse eagle 1825",
    "half_cent_classic_head":"Classic Head half cent reverse",
}


def classify_coin(denom: str, program: str, year: str) -> str:
    d = (denom or "").lower().strip()
    p = (program or "").lower().strip()
    y = str(year or "").strip()

    # Dollars
    if "morgan" in p: return "morgan_dollar"
    if "peace" in p and "dollar" in d: return "peace_dollar"
    if any(x in p for x in ["eisenhower", "ike"]): return "eisenhower_dollar"
    if "presidential" in p: return "presidential_dollar"
    if any(x in p for x in ["native american", "sacagawea"]): return "native_american_dollar"

    # Half Dollars
    if "kennedy" in p: return "kennedy_half"
    if "franklin" in p and ("half" in d or "dollar" in d): return "franklin_half"
    if any(x in p for x in ["walking liberty", "walking"]): return "walking_liberty"

    # Quarters
    if any(x in p for x in ["state quarter", "50 state", "statehood", "50-state"]): return "state_quarter"
    if "american women" in p: return "american_women_quarter"
    if any(x in p for x in ["america the beautiful", "america beautiful", "national park", "america_beautiful"]): return "america_beautiful"
    if "barber" in p and ("quarter" in d or "25" in d): return "barber_quarter"
    if "barber silver quarter" in p: return "barber_quarter"
    if "barber" in d and "quarter" in d: return "barber_quarter"
    if "capped bust" in p and "quarter" in d: return "capped_bust_quarter"
    if "seated liberty" in p and "quarter" in d: return "seated_liberty_quarter"
    if "washington" in p and "quarter" in d: return "washington_quarter"
    if "quarter" in d: return "washington_quarter"

    # Dimes
    if any(x in p for x in ["barber dime", "barber series", "barber dimes"]) or ("barber" in d and "dime" in d): return "barber_dime"
    if "barber silver dime" in d: return "barber_dime"
    if "mercury" in p: return "mercury_dime"
    if "roosevelt" in p: return "roosevelt_dime"
    if "barber" in d: return "barber_dime"
    if "dime" in d:
        if y.isdigit() and int(y) < 1916: return "barber_dime"
        if y.isdigit() and 1916 <= int(y) <= 1945: return "mercury_dime"
        return "roosevelt_dime"

    # Nickels
    if any(x in p for x in ["buffalo", "indian head nickel"]): return "buffalo_nickel"
    if any(x in p for x in ["three-cent nickel", "three cent nickel"]): return "three_cent_nickel"
    if "jefferson" in p: return "jefferson_nickel"
    if "nickel" in d:
        if y.isdigit() and 1866 <= int(y) <= 1883: return "three_cent_nickel"
        if y.isdigit() and int(y) <= 1938: return "buffalo_nickel"
        return "jefferson_nickel"

    # Cents / Pennies
    if any(x in p for x in ["indian head cent", "indian head"]): return "indian_head_cent"
    if any(x in d for x in ["1 cent", "cent", "penny"]):
        if "indian" in p: return "indian_head_cent"
        if "wheat" in p or (y.isdigit() and 1909 <= int(y) <= 1958): return "wheat_cent"
        if "memorial" in p or (y.isdigit() and int(y) >= 1959): return "memorial_cent"
        if "vdb" in p: return "wheat_cent"
        return "wheat_cent"
    if "1 cent" in d or "cent" in d: return "wheat_cent"
    if "penny" in d: return "wheat_cent"
    if "vdb" in p: return "wheat_cent"

    # Half Cents
    if "half cent" in d: return "half_cent_classic_head"

    return ""


# ─── coin_image_index direct lookup ──────────────────────────────────────────
# Doc ID pattern: {year}_{mint}_{program}_reverse  OR  {year}_{program}_reverse

_index_cache: dict[str, str | None] = {}

def lookup_index_by_doc_id(year: str, mint: str, programs: list[str]) -> tuple[str, str] | tuple[None, None]:
    """
    Try direct doc ID lookups in coin_image_index.
    Returns (public_url, doc_id_used) or (None, None).
    """
    year_str = str(year).strip() if year else ""
    mint_str = str(mint).strip().upper() if mint else ""

    candidates = []
    for prog in programs:
        if year_str and mint_str:
            candidates.append(f"{year_str}_{mint_str}_{prog}_reverse")
        if year_str:
            candidates.append(f"{year_str}_{prog}_reverse")
        # Also try without year (generic)
        candidates.append(f"{prog}_reverse")

    # Remove duplicates, preserve order
    seen = set()
    unique = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique.append(c)

    for doc_id in unique:
        if doc_id in _index_cache:
            cached = _index_cache[doc_id]
            if cached:
                return cached, doc_id
            continue

        try:
            doc = db.collection("coin_image_index").document(doc_id).get()
            if doc.exists:
                data = doc.to_dict() or {}
                rev = data.get("reverse")
                if isinstance(rev, dict):
                    url = rev.get("public_url") or rev.get("url")
                elif isinstance(rev, str):
                    url = rev
                else:
                    url = None
                _index_cache[doc_id] = url
                if url:
                    return url, doc_id
            else:
                _index_cache[doc_id] = None
        except Exception as e:
            print(f"    ⚠ Index lookup error ({doc_id}): {e}")
            _index_cache[doc_id] = None

    return None, None


# ─── Wikimedia lookup ─────────────────────────────────────────────────────────
_wikimedia_cache: dict[str, str | None] = {}

def search_wikimedia(coin_type: str, program: str = "", year: str = "", state: str = "") -> str | None:
    if coin_type == "state_quarter" and state:
        query = f"{state.title()} state quarter reverse coin"
    elif coin_type in WIKIMEDIA_QUERIES:
        query = WIKIMEDIA_QUERIES[coin_type]
    elif program:
        query = f"{program} reverse coin"
    else:
        return None

    if query in _wikimedia_cache:
        return _wikimedia_cache[query]

    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query", "list": "search",
        "srsearch": query, "srnamespace": "6",
        "srlimit": "8", "format": "json",
    }
    try:
        r = SESSION.get(url, params=params, timeout=15)
        if r.status_code != 200:
            return None
        data = r.json()
        results = data.get("query", {}).get("search", [])
        for hit in results:
            title = hit.get("title", "")
            if not title.startswith("File:"):
                continue
            fname_lower = title.lower()
            if not any(kw in fname_lower for kw in ["reverse", "rev"]):
                continue
            img_url = _get_wikimedia_image_url(title[5:])
            if img_url:
                _wikimedia_cache[query] = img_url
                return img_url
    except Exception as e:
        print(f"    ⚠ Wikimedia error: {e}")

    _wikimedia_cache[query] = None
    return None


def _get_wikimedia_image_url(filename: str) -> str | None:
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query", "titles": f"File:{filename}",
        "prop": "imageinfo", "iiprop": "url", "format": "json",
    }
    try:
        r = SESSION.get(url, params=params, timeout=10)
        data = r.json()
        for page in data.get("query", {}).get("pages", {}).values():
            info = page.get("imageinfo", [])
            if info:
                return info[0].get("url")
    except Exception:
        pass
    return None


def _extract_state(program: str) -> str:
    """Extract US state name from program string."""
    states = [
        "alabama","alaska","arizona","arkansas","california","colorado","connecticut",
        "delaware","florida","georgia","hawaii","idaho","illinois","indiana","iowa",
        "kansas","kentucky","louisiana","maine","maryland","massachusetts","michigan",
        "minnesota","mississippi","missouri","montana","nebraska","nevada",
        "new hampshire","new jersey","new mexico","new york","north carolina",
        "north dakota","ohio","oklahoma","oregon","pennsylvania","rhode island",
        "south carolina","south dakota","tennessee","texas","utah","vermont",
        "virginia","washington","west virginia","wisconsin","wyoming",
    ]
    p = program.lower()
    for s in states:
        if s in p:
            return s.title()
    return ""


# ─── GCS helpers ──────────────────────────────────────────────────────────────

def download_image(url: str) -> bytes | None:
    try:
        r = SESSION.get(url, timeout=30)
        if r.status_code == 200 and len(r.content) > 1000:
            ct = r.headers.get("Content-Type", "")
            if "image" in ct or any(url.lower().endswith(e) for e in (".jpg",".jpeg",".png",".svg",".webp")):
                return r.content
    except Exception as e:
        print(f"    ⚠ Download error: {e}")
    return None


def upload_gcs(img_bytes: bytes, gcs_path: str, content_type: str = "image/jpeg") -> str | None:
    try:
        blob = bucket.blob(gcs_path)
        blob.upload_from_string(img_bytes, content_type=content_type)
        return blob.public_url
    except Exception as e:
        print(f"    ⚠ GCS error: {e}")
        return None


def update_firestore(doc_id: str, image_url_reverse: str, source: str) -> bool:
    try:
        db.collection(COINS_COLL).document(doc_id).update({
            "image_url_reverse": image_url_reverse,
            "reverse_image_source": source,
        })
        return True
    except Exception as e:
        print(f"    ⚠ Firestore error: {e}")
        return False


# ─── CSV loader ───────────────────────────────────────────────────────────────

def load_obverse_only_coins(csv_path: str) -> list[dict]:
    coins = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("status", "").strip() == "MISSING_REVERSE":
                coins.append(row)
    return coins


def series_breakdown(coins: list[dict]) -> dict:
    counts = defaultdict(int)
    for c in coins:
        ct = classify_coin(c["denomination"], c["program"], c["year"])
        key = ct if ct else f"UNCLASSIFIED | denom={c['denomination']!r} prog={c['program'][:25]!r}"
        counts[key] += 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Reverse image enrichment for jseaman coins")
    parser.add_argument("--dry-run", action="store_true", help="Skip GCS/Firestore writes")
    parser.add_argument("--limit", type=int, default=0, help="Limit to N coins (0=all)")
    parser.add_argument("--series", default="", help="Filter to a specific coin type key")
    parser.add_argument("--skip-unclassified", action="store_true",
                        help="Skip coins with no coin-type match")
    args = parser.parse_args()

    print("=" * 72)
    print(f"REVERSE ENRICHMENT — {USER_EMAIL}")
    print(f"  dry_run={args.dry_run}  limit={args.limit or 'ALL'}  series={args.series or 'ALL'}")
    print("=" * 72)

    # 1. Load CSV
    print(f"\nLoading: {GAP_CSV}")
    all_coins = load_obverse_only_coins(GAP_CSV)
    print(f"  → {len(all_coins)} MISSING_REVERSE coins")

    # 2. Breakdown
    breakdown = series_breakdown(all_coins)
    print(f"\n{'─'*62}")
    print("SERIES BREAKDOWN (all 379 obverse-only coins):")
    print(f"{'─'*62}")
    classified = sum(v for k, v in breakdown.items() if not k.startswith("UNCLASSIFIED"))
    for ct, cnt in breakdown.items():
        programs = COIN_TYPE_PROGRAMS.get(ct, []) if not ct.startswith("UNCLASSIFIED") else []
        prog_str = f"  → index progs: {programs}" if programs else ""
        print(f"  {cnt:>4}  {ct}{prog_str}")
    print(f"{'─'*62}")
    print(f"  Classified:   {classified}")
    print(f"  Unclassified: {len(all_coins) - classified}")

    # 3. Filter
    coins = all_coins
    if args.series:
        coins = [c for c in coins if classify_coin(c["denomination"], c["program"], c["year"]) == args.series]
        print(f"\n  Filtered to '{args.series}': {len(coins)} coins")
    if args.skip_unclassified:
        coins = [c for c in coins if classify_coin(c["denomination"], c["program"], c["year"])]
        print(f"  After skip-unclassified: {len(coins)} coins")
    if args.limit:
        coins = coins[:args.limit]
        print(f"  After limit={args.limit}: {len(coins)} coins")

    print(f"\nProcessing {len(coins)} coins …\n")

    results = []
    n_index = n_wikimedia = n_static = n_none = n_fail = 0

    for idx, row in enumerate(coins, 1):
        doc_id  = row["doc_id"]
        denom   = row["denomination"]
        program = row["program"]
        year    = row["year"]
        mint    = row["mint_mark"]

        coin_type = classify_coin(denom, program, year)
        label = (f"[{idx:>4}/{len(coins)}] {(denom or '?'):<15} "
                 f"{(year or '?'):<6} {(mint or '-'):<3} "
                 f"{(program or '?')[:28]:<28} type={coin_type or 'UNCLASSIFIED'}")
        print(label)

        reverse_url = None
        source = ""
        index_doc = ""

        # ── Priority 1: coin_image_index ──────────────────────────────────
        if coin_type:
            programs_to_try = COIN_TYPE_PROGRAMS.get(coin_type, [])
            if programs_to_try:
                reverse_url, index_doc = lookup_index_by_doc_id(year, mint, programs_to_try)
                if reverse_url:
                    source = f"coin_image_index:{index_doc}"
                    n_index += 1

        # ── Priority 2: Wikimedia Commons ─────────────────────────────────
        if not reverse_url:
            time.sleep(0.25)
            state = _extract_state(program) if coin_type == "state_quarter" else ""
            reverse_url = search_wikimedia(coin_type, program, year, state)
            if reverse_url:
                source = "wikimedia_commons"
                n_wikimedia += 1

        # ── Priority 3: Static fallback ───────────────────────────────────
        if not reverse_url and coin_type in STATIC_FALLBACKS:
            reverse_url = STATIC_FALLBACKS[coin_type]
            source = "static_fallback"
            n_static += 1

        if not reverse_url:
            print(f"    ✗ No reverse found")
            n_none += 1
            results.append({**row, "result": "not_found", "source": "", "reverse_url": ""})
            continue

        src_short = source.split(":")[0]
        print(f"    ✓ {src_short}: {reverse_url[:80]}…")

        if args.dry_run:
            print(f"      [DRY RUN] No writes")
            results.append({**row, "result": "would_update", "source": source, "reverse_url": reverse_url})
            continue

        # ── Download ──────────────────────────────────────────────────────
        img_bytes = download_image(reverse_url)
        if not img_bytes:
            print(f"    ✗ Download failed")
            n_fail += 1
            results.append({**row, "result": "download_failed", "source": source, "reverse_url": reverse_url})
            continue

        ext = "png" if reverse_url.lower().endswith(".png") else "jpg"
        content_type = f"image/{ext}"

        # ── Upload GCS ────────────────────────────────────────────────────
        gcs_path = f"users/{USER_EMAIL}/coins/{doc_id}/reverse.{ext}"
        public_url = upload_gcs(img_bytes, gcs_path, content_type)
        if not public_url:
            n_fail += 1
            results.append({**row, "result": "upload_failed", "source": source, "reverse_url": reverse_url})
            continue

        # ── Firestore ─────────────────────────────────────────────────────
        ok = update_firestore(doc_id, public_url, source)
        if ok:
            print(f"      ✓ Written: {public_url[:80]}…")
            results.append({**row, "result": "success", "source": source, "reverse_url": public_url})
        else:
            n_fail += 1
            results.append({**row, "result": "firestore_failed", "source": source, "reverse_url": public_url})

        time.sleep(0.4)

    # ─── Summary ─────────────────────────────────────────────────────────────
    success = len([r for r in results if r["result"] in ("success", "would_update")])
    print(f"\n{'='*72}")
    print(f"DONE  — {'DRY RUN, no writes' if args.dry_run else 'LIVE RUN, writes performed'}")
    print(f"  ✓ Found  : {success}")
    print(f"    • coin_image_index : {n_index}")
    print(f"    • Wikimedia Commons: {n_wikimedia}")
    print(f"    • Static fallback  : {n_static}")
    print(f"  ✗ Not found        : {n_none}")
    print(f"  ⚠ Failed           : {n_fail}")
    print(f"{'='*72}")

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"Log: {LOG_PATH}")


if __name__ == "__main__":
    main()
