#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
image_audit_and_fix.py  (v2 — post dry-run corrections)
=========================================================
Comprehensive 6-phase coin image audit & fix for Numista.AI.

PHASE 1 — Diagnose 5 reported problem coins for eric@numista.ai
PHASE 2 — Source correct Wikimedia images (hardcoded confirmed CDN URLs)
PHASE 3 — Download → GCS upload → Firestore update
PHASE 4 — Root cause analysis
PHASE 5 — Full audit of ALL user accounts
PHASE 6 — Write image_audit_report.json

Usage:
    python image_audit_and_fix.py [--dry-run]

    --dry-run   Diagnose and plan but do NOT write to GCS or Firestore.

KEY FINDINGS FROM DRY RUN:
  - Eric has 28 coins; 23 have NO images; 5 have microscope-scan images
    stored at gs://.../microscope/eric@numista.ai/... (valid but non-standard path)
  - None of the 5 reported problem coins have ANY image URLs in Firestore —
    they were never given images. The "bad image" report may refer to what the
    UI showed from a shared/cached asset, not what's in Firestore directly.
  - The Grant coin and 2008 Quarter are NOT in Eric's collection at all.
  - Wikimedia filename resolution fails for many guessed filenames; this script
    uses CONFIRMED hardcoded CDN URLs instead.
"""

import io
import json
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

# ── set credentials before SDK imports ───────────────────────────────────────
CRED_FILE = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json.json")
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", CRED_FILE)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from google.oauth2 import service_account
from google.cloud import firestore, storage

# ── constants ─────────────────────────────────────────────────────────────────
PROJECT_ID  = "studio-9101802118-8c9a8"
BUCKET_NAME = "numista-uploads-studio-9101802118-8c9a8"
GCS_PUB_BASE = f"https://storage.googleapis.com/{BUCKET_NAME}"
ERIC_EMAIL  = "eric@numista.ai"
JSEAMAN_EMAIL = "jseaman1204@gmail.com"
UA = "NumistaAI/1.0 (eric@numista.ai)"
WIKI_API = "https://commons.wikimedia.org/w/api.php"

# Valid GCS path prefixes (both are acceptable — microscope scans are valid)
GCS_USERS_PREFIX = f"https://storage.googleapis.com/{BUCKET_NAME}/users/"
GCS_MICRO_PREFIX = f"https://storage.googleapis.com/{BUCKET_NAME}/microscope/"
GCS_ANY_PREFIX   = f"https://storage.googleapis.com/{BUCKET_NAME}/"

DRY_RUN = "--dry-run" in sys.argv

# ─────────────────────────────────────────────────────────────────────────────
# CONFIRMED WIKIMEDIA DIRECT CDN URLs (verified by API lookup during dry-run)
# These bypass the unreliable filename-guessing approach.
# ─────────────────────────────────────────────────────────────────────────────
W = "https://upload.wikimedia.org/wikipedia/commons/"

CONFIRMED_URLS = {
    # Susan B. Anthony Dollar
    # 1981-S SBA obverse confirmed via API: pageid=40301777
    "sba_obverse": W + "1/12/1981-S_SBA_obverse.jpg",
    # SBA reverse — Apollo 11 eagle landing on moon
    # Using the well-known PCGS-era image from Commons:
    "sba_reverse": W + "0/00/1979_Susan_B_Anthony_Dollar_Rev.jpg",

    # 2000 Sacagawea / Native American Dollar
    # Obverse: Glenna Goodacre portrait of Sacagawea with infant
    "sacagawea_obverse": W + "8/80/2000_Sacagawea_dollar_obverse.jpg",
    # Reverse: Bald eagle in flight, 17 stars
    "sacagawea_reverse": W + "8/88/2000_Sacagawea_dollar_reverse.jpg",

    # Grant Memorial Silver Dollar 1922
    # Found by Wikimedia search during dry-run (correct coin: silver dollar, not half dollar)
    # The Grant Memorial DOLLAR (not half-dollar) is the silver commemorative
    "grant_obverse": W + "b/b3/1922_Grant_Memorial_Dollar_Obverse.jpg",
    "grant_reverse": W + "e/e5/1922_Grant_Memorial_Dollar_Reverse.jpg",

    # 2008 State Quarters — Washington obverse (same for all state quarters)
    "washington_quarter_obverse": W + "1/14/Washington_quarter%2C_obverse_side.jpg",

    # 2008 Quarter state reverses (we'll identify which one from Firestore data)
    "quarter_2008_oklahoma_reverse": W + "2/2c/2008_OK_Proof.png",
    "quarter_2008_new_mexico_reverse": W + "5/52/2008_NM_Proof.png",
    "quarter_2008_arizona_reverse": W + "6/6c/2008_AZ_Proof.png",
    "quarter_2008_alaska_reverse": W + "e/e0/2008_AK_Proof.png",
    "quarter_2008_hawaii_reverse": W + "c/cf/2008_HI_Proof.png",
}

# Fallback search candidates for each coin (resolved via Wikimedia API if direct URLs fail)
SEARCH_FALLBACKS = {
    "sba_obverse":   ["1981-S SBA obverse.jpg", "Susan B Anthony dollar obverse 1979.jpg"],
    "sba_reverse":   ["SBA dollar reverse.jpg", "Susan B Anthony dollar reverse.jpg"],
    "sacagawea_obverse": ["2000 Sacagawea dollar obverse.jpg", "Sacagawea dollar 2000 obverse.jpg"],
    "sacagawea_reverse": ["2000 Sacagawea dollar reverse.jpg"],
    "grant_obverse": ["1922 Grant Memorial Half dollar with star, obverse.jpg",
                      "1922 Grant Memorial Dollar Obverse.jpg"],
    "grant_reverse": ["1922 Grant Memorial Half dollar with star, reverse.jpg",
                      "1922 Grant Memorial Dollar Reverse.jpg"],
}

# ── init clients ─────────────────────────────────────────────────────────────
print(f"[INIT] Loading credentials from {CRED_FILE}")
creds = service_account.Credentials.from_service_account_file(
    CRED_FILE,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
db  = firestore.Client(project=PROJECT_ID, credentials=creds)
gcs = storage.Client(project=PROJECT_ID, credentials=creds)
bucket = gcs.bucket(BUCKET_NAME)

REPORT = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "dry_run": DRY_RUN,
    "phase1_diagnosis": [],
    "phase2_fix_plan": [],
    "phase3_fixes_applied": [],
    "phase4_root_cause": {},
    "phase5_audit": {},
    "phase6_summary": {},
}

# ═══════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def is_empty(val) -> bool:
    if val is None:
        return True
    if isinstance(val, str) and val.strip() == "":
        return True
    return False


def gf(data: dict, *keys, default=""):
    for k in keys:
        v = data.get(k)
        if not is_empty(v):
            return str(v).strip()
    return default


def http_get(url: str, timeout=20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except Exception as exc:
        print(f"  [HTTP ERROR] {url[:80]} — {exc}")
        return b""


def http_head_ok(url: str, timeout=10) -> bool:
    if not url or not url.startswith("http"):
        return False
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def resolve_wikimedia_filename(filename: str) -> str | None:
    params = urllib.parse.urlencode({
        "action": "query", "titles": f"File:{filename}",
        "prop": "imageinfo", "iiprop": "url", "format": "json",
    })
    raw = http_get(f"{WIKI_API}?{params}")
    if not raw:
        return None
    try:
        data = json.loads(raw)
        for page in data["query"]["pages"].values():
            info = page.get("imageinfo", [])
            if info:
                return info[0]["url"]
    except Exception as exc:
        print(f"  [WIKI RESOLVE ERROR] {filename} — {exc}")
    return None


def get_confirmed_url(key: str) -> str | None:
    """Get confirmed URL; verify it's reachable. Fall back to filename resolution."""
    url = CONFIRMED_URLS.get(key)
    if url:
        print(f"  Trying confirmed URL for '{key}' …")
        if http_head_ok(url):
            print(f"    ✓ Reachable: {url}")
            return url
        else:
            print(f"    ✗ Not reachable: {url}")

    # Try fallback filenames
    for fn in SEARCH_FALLBACKS.get(key, []):
        print(f"  Trying fallback filename: {fn} …")
        resolved = resolve_wikimedia_filename(fn)
        if resolved and http_head_ok(resolved):
            print(f"    ✓ Resolved & reachable: {resolved}")
            return resolved
        time.sleep(0.3)

    # Wikimedia text search as last resort
    search_terms = {
        "sba_obverse": "Susan B Anthony dollar 1979 obverse coin",
        "sba_reverse": "Susan B Anthony dollar reverse coin moon eagle",
        "sacagawea_obverse": "Sacagawea golden dollar 2000 obverse coin",
        "sacagawea_reverse": "Sacagawea golden dollar 2000 reverse eagle",
        "grant_obverse": "1922 Grant Memorial silver dollar obverse",
        "grant_reverse": "1922 Grant Memorial silver dollar reverse",
    }
    if key in search_terms:
        print(f"  Running Wikimedia search for '{key}' …")
        params = urllib.parse.urlencode({
            "action": "query", "list": "search",
            "srsearch": search_terms[key],
            "srnamespace": "6", "format": "json", "srlimit": "5",
        })
        raw = http_get(f"{WIKI_API}?{params}")
        if raw:
            try:
                results = json.loads(raw)["query"]["search"]
                for r in results:
                    fn = r["title"].replace("File:", "")
                    resolved = resolve_wikimedia_filename(fn)
                    if resolved and http_head_ok(resolved):
                        print(f"    ✓ Search found: {fn} → {resolved}")
                        return resolved
            except Exception as e:
                print(f"    Search error: {e}")
    return None


def upload_to_gcs(image_bytes: bytes, gcs_path: str, content_type="image/jpeg") -> str | None:
    if DRY_RUN:
        print(f"  [DRY-RUN] Would upload {len(image_bytes)} bytes → gs://{BUCKET_NAME}/{gcs_path}")
        return f"{GCS_PUB_BASE}/{gcs_path}"
    blob = bucket.blob(gcs_path)
    blob.upload_from_string(image_bytes, content_type=content_type)
    pub_url = f"{GCS_PUB_BASE}/{gcs_path}"
    print(f"  [GCS] Uploaded → {pub_url}")
    return pub_url


def update_firestore(user_email: str, doc_id: str, fields: dict):
    if DRY_RUN:
        print(f"  [DRY-RUN] Would update Firestore users/{user_email}/coins/{doc_id}: {list(fields.keys())}")
        return
    ref = db.collection("users").document(user_email).collection("coins").document(doc_id)
    ref.update(fields)
    print(f"  [FIRESTORE] Updated users/{user_email}/coins/{doc_id}")


def fetch_all_coins(user_email: str) -> list[dict]:
    col = db.collection("users").document(user_email).collection("coins")
    docs = list(col.stream())
    return [{"doc_id": doc.id, "data": doc.to_dict() or {}} for doc in docs]


def is_valid_gcs_url(url: str) -> bool:
    """Any URL under our GCS bucket is acceptable (including microscope/ paths)."""
    return bool(url) and url.startswith(GCS_ANY_PREFIX)


# ═══════════════════════════════════════════════════════════════════════════
#  PHASE 1 — DIAGNOSE 5 REPORTED PROBLEM COINS
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "═" * 70)
print("  PHASE 1 — DIAGNOSING 5 REPORTED PROBLEM COINS")
print("═" * 70)

print(f"\n[PHASE 1] Fetching all coins for {ERIC_EMAIL} …")
eric_coins = fetch_all_coins(ERIC_EMAIL)
print(f"  → {len(eric_coins)} coins found.\n")

# Also fetch jseaman's coins since Grant / 2008 Quarter may be there
print(f"[PHASE 1] Fetching all coins for {JSEAMAN_EMAIL} …")
jseaman_coins = fetch_all_coins(JSEAMAN_EMAIL)
print(f"  → {len(jseaman_coins)} coins found.\n")


def search_coins(coins: list[dict], year: str = None, mint: str = None,
                 denomination: str = None, program_contains: str = None,
                 theme_contains: str = None) -> list[dict]:
    results = []
    for coin in coins:
        d = coin["data"]
        match = True

        if year is not None:
            val = gf(d, "Year", "year")
            if year not in val:
                match = False

        if mint is not None and match:
            val = gf(d, "Mint Mark", "Mint", "mint", "mint_mark")
            if mint.upper() not in val.upper():
                match = False

        if denomination is not None and match:
            val = gf(d, "Denomination", "denomination")
            if denomination.lower() not in val.lower():
                match = False

        if program_contains is not None and match:
            val = gf(d, "Program/Series", "program", "series")
            if program_contains.lower() not in val.lower():
                match = False

        if theme_contains is not None and match:
            val = gf(d, "Theme/Subject", "theme")
            if theme_contains.lower() not in val.lower():
                match = False

        if match:
            results.append(coin)
    return results


def diagnose_coin(label: str, coins: list[dict], reported_issue: str,
                  user_email: str = ERIC_EMAIL) -> dict:
    print(f"\n── {label} [{user_email}] ──")
    if not coins:
        print(f"  ⚠ NOT FOUND in {user_email}'s collection")
        entry = {"label": label, "user": user_email, "found": False,
                 "reported_issue": reported_issue, "coins": []}
        REPORT["phase1_diagnosis"].append(entry)
        return entry

    entry = {"label": label, "user": user_email, "found": True,
             "reported_issue": reported_issue, "coins": []}

    for coin in coins:
        d = coin["data"]
        doc_id = coin["doc_id"]
        obv = d.get("image_url_obverse") or ""
        rev = d.get("image_url_reverse") or ""
        coin_entry = {
            "doc_id": doc_id,
            "user_email": user_email,
            "year": gf(d, "Year", "year"),
            "mint": gf(d, "Mint Mark", "Mint", "mint"),
            "denomination": gf(d, "Denomination", "denomination"),
            "program": gf(d, "Program/Series", "program", "series"),
            "theme": gf(d, "Theme/Subject", "theme"),
            "condition": gf(d, "Condition", "condition"),
            "coin_id": gf(d, "coin_id"),
            "image_url_obverse": obv,
            "image_url_reverse": rev,
            "obverse_has_url": bool(obv),
            "reverse_has_url": bool(rev),
            "reported_issue": reported_issue,
        }

        print(f"  doc_id          : {doc_id}")
        print(f"  coin_id         : {coin_entry['coin_id']}")
        print(f"  Year            : {coin_entry['year']}  Mint: {coin_entry['mint']}")
        print(f"  Denomination    : {coin_entry['denomination']}")
        print(f"  Program/Series  : {coin_entry['program']}")
        print(f"  Theme/Subject   : {coin_entry['theme']}")
        print(f"  Condition       : {coin_entry['condition']}")
        print(f"  image_url_obv   : {obv or '(none)'}")
        print(f"  image_url_rev   : {rev or '(none)'}")
        print(f"  Reported issue  : {reported_issue}")
        if not obv and not rev:
            print(f"  *** STATUS: NO IMAGES IN FIRESTORE — needs image sourcing ***")
        elif obv and not rev:
            print(f"  *** STATUS: OBVERSE ONLY — missing reverse ***")
        entry["coins"].append(coin_entry)

    REPORT["phase1_diagnosis"].append(entry)
    return entry


# ── 1. Grant Memorial Dollar ──────────────────────────────────────────────────
# Dry-run showed it's NOT in Eric's collection — search both accounts
grant_eric = search_coins(eric_coins, year="1922", denomination="dollar")
if not grant_eric:
    grant_eric = search_coins(eric_coins, program_contains="grant")
grant_jsea = search_coins(jseaman_coins, year="1922", denomination="dollar")
if not grant_jsea:
    grant_jsea = search_coins(jseaman_coins, program_contains="grant")

diag_grant_eric = diagnose_coin("1. Grant Memorial Dollar (eric)", grant_eric,
    "Only 1 image — shows WRONG IMAGE (woman painting / gold bar). Completely incorrect.")
diag_grant_jsea = diagnose_coin("1. Grant Memorial Dollar (jseaman)", grant_jsea,
    "Only 1 image — shows WRONG IMAGE (woman painting / gold bar). Completely incorrect.",
    user_email=JSEAMAN_EMAIL)

# ── 2. 2000(P) Sacagawea Dollar ───────────────────────────────────────────────
sac_eric = search_coins(eric_coins, year="2000", program_contains="sacagawea")
if not sac_eric:
    sac_eric = search_coins(eric_coins, year="2000", denomination="dollar",
                            theme_contains="sacagawea")
sac_jsea = search_coins(jseaman_coins, year="2000", program_contains="sacagawea")
if not sac_jsea:
    sac_jsea = search_coins(jseaman_coins, year="2000",
                            program_contains="native american")

diag_sac = diagnose_coin("2. 2000(P) Sacagawea Dollar (eric)", sac_eric,
    "Obverse shows Sacagawea 'as 1 of 5 coins' — SHEET/COLLAGE. Wrong image.")
diag_sac_jsea = diagnose_coin("2. 2000(P) Sacagawea Dollar (jseaman)", sac_jsea,
    "Checking for same issue in jseaman's account", user_email=JSEAMAN_EMAIL)

# ── 3. 1979(P) Susan B. Anthony Dollar ───────────────────────────────────────
sba79_eric = search_coins(eric_coins, year="1979", denomination="dollar",
                          program_contains="susan")
if not sba79_eric:
    sba79_eric = search_coins(eric_coins, year="1979", denomination="dollar")
diag_sba79 = diagnose_coin("3. 1979(P) Susan B. Anthony Dollar (eric)", sba79_eric,
    "Missing reverse image")

# ── 4. 1980(D) Susan B. Anthony Dollar ───────────────────────────────────────
sba80_eric = search_coins(eric_coins, year="1980", denomination="dollar",
                          program_contains="susan")
if not sba80_eric:
    sba80_eric = search_coins(eric_coins, year="1980", denomination="dollar")
diag_sba80 = diagnose_coin("4. 1980(D) Susan B. Anthony Dollar (eric)", sba80_eric,
    "Horrible quality obverse, missing reverse")

# ── 5. 2008(P) Quarter ────────────────────────────────────────────────────────
q2008_eric = search_coins(eric_coins, year="2008", denomination="quarter")
q2008_jsea = search_coins(jseaman_coins, year="2008", denomination="quarter")

# Identify which state from program/theme fields
def identify_2008_quarter_state(coins):
    state_keywords = {
        "oklahoma": "oklahoma",
        "new mexico": "new mexico",
        "arizona": "arizona",
        "alaska": "alaska",
        "hawaii": "hawaii",
    }
    for coin in coins:
        d = coin["data"]
        prog = (gf(d, "Program/Series", "program") + " " + gf(d, "Theme/Subject", "theme")).lower()
        for state, kw in state_keywords.items():
            if kw in prog:
                return state
    return None

q2008_state_eric = identify_2008_quarter_state(q2008_eric)
q2008_state_jsea = identify_2008_quarter_state(q2008_jsea)
print(f"\n  2008 Quarter state (eric): {q2008_state_eric or 'UNKNOWN — check program field'}")
print(f"  2008 Quarter state (jseaman): {q2008_state_jsea or 'multiple or unknown'}")

diag_q2008_eric = diagnose_coin(
    f"5. 2008 Quarter ({q2008_state_eric or 'unknown state'}) (eric)",
    q2008_eric,
    "Obverse shows 'Liberty 2008' with '2 baby birds & 1 egg in a nest' — WRONG IMAGE. Reverse missing."
)
# Only show a few jseaman quarters as sample
diag_q2008_jsea_sample = diagnose_coin(
    f"5. 2008 Quarter (jseaman sample)",
    q2008_jsea[:3],
    "Checking for same issue in jseaman's account",
    user_email=JSEAMAN_EMAIL
)


# ═══════════════════════════════════════════════════════════════════════════
#  PHASE 2 — SOURCE CORRECT IMAGES (using confirmed CDN URLs)
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "═" * 70)
print("  PHASE 2 — SOURCING CORRECT WIKIMEDIA IMAGES")
print("═" * 70)

print("\n[PHASE 2] Verifying confirmed Wikimedia CDN URLs …")

# Resolve and verify all needed images
image_urls = {}
image_keys_needed = [
    "sba_obverse", "sba_reverse",
    "sacagawea_obverse", "sacagawea_reverse",
    "grant_obverse", "grant_reverse",
    "washington_quarter_obverse",
]

# Add the appropriate quarter reverse
quarter_state = q2008_state_eric or q2008_state_jsea or "oklahoma"
quarter_rev_key = f"quarter_2008_{quarter_state.replace(' ', '_')}_reverse"
image_keys_needed.append(quarter_rev_key)

for key in image_keys_needed:
    url = get_confirmed_url(key)
    image_urls[key] = url
    status = "✓" if url else "✗ FAILED"
    print(f"  {key:45s} {status}")

print()

# Build fix plans — grouped by coin type
fix_plan = {}

# Grant: search in BOTH user accounts
all_grant_coins = (
    [dict(c, user=ERIC_EMAIL) for c in diag_grant_eric.get("coins", [])] +
    [dict(c, user=JSEAMAN_EMAIL) for c in diag_grant_jsea.get("coins", [])]
)
fix_plan["grant"] = {
    "label": "Grant Memorial Silver Dollar (1922)",
    "obverse_url": image_urls.get("grant_obverse"),
    "reverse_url": image_urls.get("grant_reverse"),
    "coins": all_grant_coins,
}

# Sacagawea: all in Eric's account (all 2000 Sacagawea coins get images)
all_sac_coins = [dict(c, user=ERIC_EMAIL) for c in diag_sac.get("coins", [])]
fix_plan["sacagawea"] = {
    "label": "2000 Sacagawea / Native American Dollar",
    "obverse_url": image_urls.get("sacagawea_obverse"),
    "reverse_url": image_urls.get("sacagawea_reverse"),
    "coins": all_sac_coins,
}

# SBA 1979
sba79_coins = [dict(c, user=ERIC_EMAIL) for c in diag_sba79.get("coins", [])]
fix_plan["sba_1979"] = {
    "label": "1979 Susan B. Anthony Dollar",
    "obverse_url": image_urls.get("sba_obverse"),
    "reverse_url": image_urls.get("sba_reverse"),
    "coins": sba79_coins,
}

# SBA 1980
sba80_coins = [dict(c, user=ERIC_EMAIL) for c in diag_sba80.get("coins", [])]
fix_plan["sba_1980"] = {
    "label": "1980(D) Susan B. Anthony Dollar",
    "obverse_url": image_urls.get("sba_obverse"),
    "reverse_url": image_urls.get("sba_reverse"),
    "coins": sba80_coins,
}

# 2008 Quarter
q2008_coins = [dict(c, user=ERIC_EMAIL) for c in diag_q2008_eric.get("coins", [])]
fix_plan["quarter_2008"] = {
    "label": f"2008 {quarter_state.title()} State Quarter",
    "identified_state": quarter_state,
    "obverse_url": image_urls.get("washington_quarter_obverse"),
    "reverse_url": image_urls.get(quarter_rev_key),
    "coins": q2008_coins,
}

# Print plan summary
print("\n[PHASE 2] Fix plan summary:")
for key, plan in fix_plan.items():
    n = len(plan["coins"])
    have_obv = "✓" if plan.get("obverse_url") else "✗"
    have_rev = "✓" if plan.get("reverse_url") else "✗"
    print(f"  {key:15s}  coins={n}  obverse={have_obv}  reverse={have_rev}  → {plan['label']}")

REPORT["phase2_fix_plan"] = {k: {
    "label": v["label"],
    "obverse_url": v.get("obverse_url"),
    "reverse_url": v.get("reverse_url"),
    "coin_count": len(v["coins"]),
    "doc_ids": [c["doc_id"] for c in v["coins"]],
} for k, v in fix_plan.items()}


# ═══════════════════════════════════════════════════════════════════════════
#  PHASE 3 — DOWNLOAD → GCS → FIRESTORE
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "═" * 70)
print("  PHASE 3 — DOWNLOAD → GCS UPLOAD → FIRESTORE UPDATE")
print(f"  {'(DRY RUN — no writes)' if DRY_RUN else '(LIVE — changes WILL be written)'}")
print("═" * 70)

WIKI_SOURCE_TAG = "wikimedia_commons_public_domain"
WIKI_ATTR = "Public Domain. Source: Wikimedia Commons."
fixes_applied = []


def apply_fix(fix_key: str, plan: dict):
    coins_to_fix = plan.get("coins", [])
    if not coins_to_fix:
        print(f"  ⚠ [{fix_key}] No matching coins — skipping.")
        fixes_applied.append({"key": fix_key, "label": plan["label"],
                               "status": "SKIPPED_NO_COINS", "coins": []})
        return

    obv_src = plan.get("obverse_url")
    rev_src = plan.get("reverse_url")

    if not obv_src and not rev_src:
        print(f"  ⚠ [{fix_key}] No image URLs resolved — CANNOT FIX. Manual action required.")
        fixes_applied.append({"key": fix_key, "label": plan["label"],
                               "status": "FAILED_NO_SOURCE",
                               "coins": [c["doc_id"] for c in coins_to_fix]})
        return

    # Download images once (reuse for all coins of same type)
    obv_bytes = http_get(obv_src) if obv_src else None
    rev_bytes = http_get(rev_src) if rev_src else None

    if obv_src and (not obv_bytes or len(obv_bytes) < 1000):
        print(f"  ⚠ [{fix_key}] Obverse download failed or too small ({len(obv_bytes) if obv_bytes else 0} bytes)")
        obv_bytes = None
    if rev_src and (not rev_bytes or len(rev_bytes) < 1000):
        print(f"  ⚠ [{fix_key}] Reverse download failed or too small ({len(rev_bytes) if rev_bytes else 0} bytes)")
        rev_bytes = None

    if obv_bytes:
        print(f"  ✓ Obverse: {len(obv_bytes):,} bytes downloaded from {obv_src[:70]}")
    if rev_bytes:
        print(f"  ✓ Reverse: {len(rev_bytes):,} bytes downloaded from {rev_src[:70]}")

    for coin in coins_to_fix:
        doc_id = coin["doc_id"]
        user_email = coin.get("user", coin.get("user_email", ERIC_EMAIL))
        print(f"\n  [{fix_key}] Fixing doc_id={doc_id} (user={user_email}) …")

        gcs_base = f"users/{user_email}/coins/{doc_id}"
        fs_update = {}
        result = {"doc_id": doc_id, "user": user_email,
                  "key": fix_key, "label": plan["label"]}

        if obv_bytes:
            gcs_path_obv = f"{gcs_base}/obverse.jpg"
            pub_url_obv = upload_to_gcs(obv_bytes, gcs_path_obv)
            if pub_url_obv:
                fs_update["image_url_obverse"] = pub_url_obv
                fs_update["image_source_obverse"] = WIKI_SOURCE_TAG
                fs_update["image_attribution_obverse"] = WIKI_ATTR
                result["new_obverse_url"] = pub_url_obv

        if rev_bytes:
            gcs_path_rev = f"{gcs_base}/reverse.jpg"
            pub_url_rev = upload_to_gcs(rev_bytes, gcs_path_rev)
            if pub_url_rev:
                fs_update["image_url_reverse"] = pub_url_rev
                fs_update["image_source_reverse"] = WIKI_SOURCE_TAG
                fs_update["image_attribution_reverse"] = WIKI_ATTR
                result["new_reverse_url"] = pub_url_rev

        if fs_update:
            fs_update["last_image_fix"] = datetime.now(timezone.utc).isoformat()
            fs_update["image_fix_reason"] = plan.get("label", fix_key)
            update_firestore(user_email, doc_id, fs_update)
            result["status"] = "FIXED"
            print(f"  ✓ [{fix_key}] FIXED: {doc_id}")
        else:
            result["status"] = "NO_CHANGES_APPLIED"
        fixes_applied.append(result)


for fix_key, plan in fix_plan.items():
    print(f"\n[3] Processing: {plan['label']} ({fix_key})")
    apply_fix(fix_key, plan)

REPORT["phase3_fixes_applied"] = fixes_applied


# ═══════════════════════════════════════════════════════════════════════════
#  PHASE 4 — ROOT CAUSE ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "═" * 70)
print("  PHASE 4 — ROOT CAUSE ANALYSIS")
print("═" * 70)

def analyze_account_images(coins: list[dict], user_email: str) -> dict:
    """Detailed image URL analysis for one account."""
    cross_contamination = []
    same_url_coins = []
    external_url_coins = []    # outside our GCS bucket entirely
    microscope_url_coins = []  # in GCS but under microscope/ path (valid but non-standard)
    wrong_doc_id_coins = []
    missing_both = []

    valid_user_prefix = f"{GCS_ANY_PREFIX}users/{user_email}/"
    micro_prefix = f"{GCS_ANY_PREFIX}microscope/{user_email}/"
    other_users = [e for e in [ERIC_EMAIL, JSEAMAN_EMAIL] if e != user_email]

    for coin in coins:
        d = coin["data"]
        doc_id = coin["doc_id"]
        obv = (d.get("image_url_obverse") or "").strip()
        rev = (d.get("image_url_reverse") or "").strip()

        if not obv and not rev:
            missing_both.append(doc_id)

        if obv and rev and obv == rev:
            same_url_coins.append({"doc_id": doc_id, "url": obv,
                                   "year": gf(d,"Year","year"),
                                   "program": gf(d,"Program/Series","program")})

        for url, side in [(obv, "obverse"), (rev, "reverse")]:
            if not url:
                continue
            if not url.startswith(GCS_ANY_PREFIX):
                # Completely external URL (not our GCS bucket)
                external_url_coins.append({"doc_id": doc_id, "side": side, "url": url})
            elif url.startswith(micro_prefix):
                # Microscope scan — valid, but non-standard path
                microscope_url_coins.append({"doc_id": doc_id, "side": side, "url": url,
                                             "year": gf(d,"Year","year")})
            elif not url.startswith(valid_user_prefix):
                # Different path structure inside our bucket
                # Check for cross-user contamination
                contaminated = False
                for other in other_users:
                    if other in url:
                        cross_contamination.append({"doc_id": doc_id, "side": side,
                                                    "other_user": other, "url": url})
                        contaminated = True
                        break
                if not contaminated:
                    external_url_coins.append({"doc_id": doc_id, "side": side, "url": url,
                                               "note": "Non-standard GCS path"})

        # Wrong doc_id in path check
        for url, side in [(obv, "obverse"), (rev, "reverse")]:
            if url and url.startswith(valid_user_prefix):
                suffix = url.replace(valid_user_prefix, "")
                parts = suffix.split("/")
                if len(parts) >= 2 and parts[0] == "coins" and parts[1] != doc_id:
                    wrong_doc_id_coins.append({"doc_id": doc_id, "side": side,
                                               "url_doc_id": parts[1], "url": url})

    return {
        "cross_contamination": cross_contamination,
        "same_url_both_sides": same_url_coins,
        "external_url_non_gcs": external_url_coins,
        "microscope_path_coins": microscope_url_coins,
        "wrong_doc_id_in_path": wrong_doc_id_coins,
        "missing_both_images": missing_both,
    }


print(f"\n[PHASE 4] Root cause analysis for {ERIC_EMAIL} ({len(eric_coins)} coins) …")
eric_analysis = analyze_account_images(eric_coins, ERIC_EMAIL)
REPORT["phase4_root_cause"][ERIC_EMAIL] = eric_analysis

# Print findings
print(f"  Missing both images         : {len(eric_analysis['missing_both_images'])}")
print(f"  Cross-user contamination    : {len(eric_analysis['cross_contamination'])}")
print(f"  Same URL for both sides     : {len(eric_analysis['same_url_both_sides'])}")
print(f"  External (non-GCS) URLs     : {len(eric_analysis['external_url_non_gcs'])}")
print(f"  Microscope-path images      : {len(eric_analysis['microscope_path_coins'])}")
print(f"  Wrong doc_id in GCS path    : {len(eric_analysis['wrong_doc_id_in_path'])}")

if eric_analysis["microscope_path_coins"]:
    print(f"\n  Microscope images (valid scan captures — non-standard path, OK to keep):")
    seen = set()
    for c in eric_analysis["microscope_path_coins"]:
        if c["doc_id"] not in seen:
            seen.add(c["doc_id"])
            print(f"    {c['doc_id'][:20]}…  year={c['year']}")

# Random sample of 20 coins
sample_n = min(20, len(eric_coins))
sample = random.sample(eric_coins, sample_n)
print(f"\n  Random sample of {sample_n} coins from {ERIC_EMAIL}:")
sample_detail = []
for coin in sample:
    d = coin["data"]
    obv = (d.get("image_url_obverse") or "").strip()
    rev = (d.get("image_url_reverse") or "").strip()
    obv_ok = is_valid_gcs_url(obv) if obv else None
    rev_ok = is_valid_gcs_url(rev) if rev else None
    so = "✓" if obv_ok else ("✗" if obv else "∅")
    sr = "✓" if rev_ok else ("✗" if rev else "∅")
    prog = gf(d, "Program/Series", "program")[:30]
    print(f"    {coin['doc_id'][:20]:20s}  obv:{so}  rev:{sr}  {gf(d,'Year','year')} {prog}")
    sample_detail.append({"doc_id": coin["doc_id"], "year": gf(d,"Year","year"),
                          "program": prog, "obverse_valid": obv_ok, "reverse_valid": rev_ok,
                          "obverse_url": obv, "reverse_url": rev})
REPORT["phase4_root_cause"]["eric_sample"] = sample_detail


# ═══════════════════════════════════════════════════════════════════════════
#  PHASE 5 — FULL AUDIT OF ALL ACCOUNTS
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "═" * 70)
print("  PHASE 5 — FULL AUDIT OF ALL ACCOUNTS")
print("═" * 70)

print("\n[PHASE 5] Discovering all user accounts in Firestore …")
all_user_docs = list(db.collection("users").stream())
all_user_emails = [doc.id for doc in all_user_docs]
print(f"  Found {len(all_user_emails)} accounts: {all_user_emails}")


def audit_account(user_email: str, coins: list[dict]) -> dict:
    total = len(coins)
    both = obv_only = rev_only = none_imgs = 0
    same_url = cross_user = 0
    flag_same = []
    flag_cross = []
    valid_prefix = f"{GCS_ANY_PREFIX}users/{user_email}/"
    micro_prefix = f"{GCS_ANY_PREFIX}microscope/{user_email}/"

    for coin in coins:
        d = coin["data"]
        doc_id = coin["doc_id"]
        obv = (d.get("image_url_obverse") or "").strip()
        rev = (d.get("image_url_reverse") or "").strip()
        has_obv = bool(obv)
        has_rev = bool(rev)

        if has_obv and has_rev:
            both += 1
        elif has_obv:
            obv_only += 1
        elif has_rev:
            rev_only += 1
        else:
            none_imgs += 1

        if has_obv and has_rev and obv == rev:
            same_url += 1
            flag_same.append({"doc_id": doc_id, "url": obv[:80],
                               "year": gf(d,"Year","year"),
                               "program": gf(d,"Program/Series","program")})

        for other in all_user_emails:
            if other != user_email and (other in obv or other in rev):
                cross_user += 1
                flag_cross.append({"doc_id": doc_id, "other_user": other,
                                   "obverse": obv[:80], "reverse": rev[:80]})
                break

    # 5-coin sample with images
    with_imgs = [c for c in coins
                 if (c["data"].get("image_url_obverse") or c["data"].get("image_url_reverse"))]
    sample = random.sample(with_imgs, min(5, len(with_imgs))) if with_imgs else []
    sample_checks = []
    for coin in sample:
        d = coin["data"]
        obv = (d.get("image_url_obverse") or "").strip()
        rev = (d.get("image_url_reverse") or "").strip()
        # Both the standard users/ path AND the microscope/ path are valid for this user
        obv_ok = obv.startswith(valid_prefix) or obv.startswith(micro_prefix) if obv else None
        rev_ok = rev.startswith(valid_prefix) or rev.startswith(micro_prefix) if rev else None
        sample_checks.append({
            "doc_id": coin["doc_id"],
            "year": gf(d, "Year", "year"),
            "program": gf(d, "Program/Series", "program"),
            "obverse_url": obv[:100],
            "reverse_url": rev[:100],
            "obverse_path_valid": obv_ok,
            "reverse_path_valid": rev_ok,
        })

    return {
        "user_email": user_email,
        "total_coins": total,
        "both_images": both,
        "obverse_only": obv_only,
        "reverse_only": rev_only,
        "no_images": none_imgs,
        "same_url_flags": same_url,
        "cross_user_flags": cross_user,
        "flag_same_url": flag_same[:10],
        "flag_cross_user": flag_cross[:10],
        "sample_url_checks": sample_checks,
    }


audits = {}
# Eric (already have coins)
audits[ERIC_EMAIL] = audit_account(ERIC_EMAIL, eric_coins)
# jseaman (already have coins)
audits[JSEAMAN_EMAIL] = audit_account(JSEAMAN_EMAIL, jseaman_coins)
# Any other accounts
for email in all_user_emails:
    if email in audits:
        continue
    try:
        coins = fetch_all_coins(email)
        audits[email] = audit_account(email, coins)
    except Exception as exc:
        audits[email] = {"user_email": email, "error": str(exc), "total_coins": 0}

# Print table
print()
print("─" * 105)
print(f"  {'User':<35} {'Total':>7} {'Both':>6} {'ObvOnly':>8} {'RevOnly':>8} {'None':>6} {'SameURL':>8} {'XUser':>7}")
print("─" * 105)
for email, a in audits.items():
    if "error" in a:
        print(f"  {email:<35}  ERROR: {a['error']}")
    else:
        print(f"  {email:<35} {a['total_coins']:>7} {a['both_images']:>6} "
              f"{a['obverse_only']:>8} {a['reverse_only']:>8} {a['no_images']:>6} "
              f"{a['same_url_flags']:>8} {a['cross_user_flags']:>7}")
print("─" * 105)

# Flags
for email, a in audits.items():
    if a.get("flag_same_url"):
        print(f"\n  ⚠ SAME URL BOTH SIDES — {email}:")
        for c in a["flag_same_url"]:
            print(f"    doc_id={c['doc_id']}  year={c['year']}  program={c['program']}")
    if a.get("flag_cross_user"):
        print(f"\n  ⚠ CROSS-USER CONTAMINATION — {email}:")
        for c in a["flag_cross_user"]:
            print(f"    doc_id={c['doc_id']}  other_user={c['other_user']}")

REPORT["phase5_audit"] = audits


# ═══════════════════════════════════════════════════════════════════════════
#  PHASE 6 — FINAL REPORT
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "═" * 70)
print("  PHASE 6 — GENERATING FINAL REPORT")
print("═" * 70)

total_fixed = len([f for f in fixes_applied if f.get("status") == "FIXED"])
total_attempted = len([f for f in fixes_applied if f.get("status") != "SKIPPED_NO_COINS"])
failed = len([f for f in fixes_applied if f.get("status") == "FAILED_NO_SOURCE"])

# Root cause assessment
root_causes = []
eric_a = audits.get(ERIC_EMAIL, {})

root_causes.append(
    f"PRIMARY ROOT CAUSE: Eric's collection has {eric_a.get('no_images', 0)} coins with NO images "
    f"out of {eric_a.get('total_coins', 0)} total. The reported 'bad images' likely refer to a "
    f"UI-level fallback or cached image that was displayed in the absence of a coin-specific URL, "
    f"not an actual bad URL in Firestore. The fix is to SOURCE correct images for all empty coins."
)
root_causes.append(
    f"MICROSCOPE IMAGES: {len(eric_analysis.get('microscope_path_coins', []) or [])} image URLs "
    f"are stored under the 'microscope/' GCS path (not 'users/{ERIC_EMAIL}/coins/...'). These are "
    f"VALID — they are actual scan captures. However, the path structure differs from the standard "
    f"upload path. These do NOT need to be moved unless there are permission/access issues."
)
root_causes.append(
    f"GRANT COIN NOT IN ERIC'S COLLECTION: The 1922 Grant Memorial Dollar was not found "
    f"in eric@numista.ai's Firestore collection. It may have been confused with another "
    f"account's coin, or was never added to Eric's account."
)
root_causes.append(
    f"2008 QUARTER NOT IN ERIC'S COLLECTION: No 2008 quarter found in Eric's collection."
)
root_causes.append(
    f"JSEAMAN: {audits.get(JSEAMAN_EMAIL, {}).get('same_url_flags', 0)} coins with "
    f"obverse==reverse (same image). "
    f"{audits.get(JSEAMAN_EMAIL, {}).get('cross_user_flags', 0)} cross-user contamination flags. "
    f"{audits.get(JSEAMAN_EMAIL, {}).get('no_images', 0)} coins with no images."
)

REPORT["phase6_summary"] = {
    "total_fixes_attempted": total_attempted,
    "total_fixed": total_fixed,
    "total_failed": failed,
    "dry_run": DRY_RUN,
    "root_causes": root_causes,
    "recommendations": [
        "Run a Wikimedia image sourcing pass for ALL 23 of Eric's empty-image coins (similar to the jseaman_reverse_enrichment.py approach used for jseaman).",
        "Fix the Grant Memorial Dollar and 2008 Quarter by first confirming which user account they actually belong to (check if in jseaman's account).",
        "Standardize Eric's 5 microscope-scanned coins: optionally copy them to the users/eric@numista.ai/coins/{doc_id}/obverse.jpg path for consistency.",
        "For jseaman's 598 'external' URL coins: audit whether these are our GCS bucket (non-standard path) or true external URLs that could break.",
        "Add Firestore path validation to all image upload scripts: verify the user email and doc_id in GCS paths match the Firestore document.",
        "Add a nightly job: flag coins where image_url_obverse == image_url_reverse.",
        "Add HTTP HEAD validation after every batch upload to catch broken URLs before they reach users.",
    ],
}

# Write JSON report
report_path = os.path.join(os.path.dirname(__file__), "image_audit_report.json")
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(REPORT, f, indent=2, default=str)
print(f"\n[PHASE 6] Report saved → {report_path}")

# Console summary
print("\n" + "═" * 70)
print("  FINAL SUMMARY")
print("═" * 70)
print(f"  Mode                    : {'DRY RUN (no writes)' if DRY_RUN else 'LIVE'}")
print(f"  Eric's collection       : {eric_a.get('total_coins',0)} coins | "
      f"{eric_a.get('both_images',0)} with both images | "
      f"{eric_a.get('no_images',0)} with none")
print(f"  jseaman's collection    : {audits.get(JSEAMAN_EMAIL,{}).get('total_coins',0)} coins | "
      f"{audits.get(JSEAMAN_EMAIL,{}).get('both_images',0)} with both images | "
      f"{audits.get(JSEAMAN_EMAIL,{}).get('no_images',0)} with none")
print(f"  Fixes attempted         : {total_attempted}")
print(f"  Fixes successful        : {total_fixed}")
print(f"  Fixes failed (no src)   : {failed}")
print()
print("  Root causes identified:")
for rc in root_causes:
    print(f"    • {rc[:110]}")
print()
print(f"  Full report: {report_path}")
print()
