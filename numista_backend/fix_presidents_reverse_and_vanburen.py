#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_presidents_reverse_and_vanburen.py
=======================================
Targeted fixes after the main inventory+fix run:

1. Fix Van Buren obverse (got Andrew Jackson's image by accident — correct it
   with the confirmed bulk_programs URL from GCS inventory)
2. Add Presidential $1 Statue of Liberty reverse to all 13 of Eric's presidential
   $1 coins (the reverse image IS in GCS at Presidential_dollar_coin_reverse.png)
3. Fix the 2 still-empty coins: 2001 Sacagawea + 1990 Roosevelt Dime
   — searching GCS inventory for exact matches first
4. Report final state

Usage:
    python fix_presidents_reverse_and_vanburen.py [--dry-run]
"""

import io, json, os, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone

CRED_FILE = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json.json")
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", CRED_FILE)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from google.oauth2 import service_account
from google.cloud import firestore, storage

DRY_RUN = "--dry-run" in sys.argv
WORKDIR = os.path.dirname(__file__)

PROJECT_ID   = "studio-9101802118-8c9a8"
BUCKET_MAIN  = "numista-uploads-studio-9101802118-8c9a8"
BUCKET_REF   = "numista-reference-library"
GCS_PUB_MAIN = f"https://storage.googleapis.com/{BUCKET_MAIN}"
ERIC_EMAIL   = "eric@numista.ai"
UA           = "NumistaAI/1.0 (eric@numista.ai)"
WIKI_API     = "https://commons.wikimedia.org/w/api.php"
W            = "https://upload.wikimedia.org/wikipedia/commons/"

print(f"[INIT] Credentials: {CRED_FILE}")
creds = service_account.Credentials.from_service_account_file(
    CRED_FILE, scopes=["https://www.googleapis.com/auth/cloud-platform"])
db  = firestore.Client(project=PROJECT_ID, credentials=creds)
gcs = storage.Client(project=PROJECT_ID, credentials=creds)
main_bucket = gcs.bucket(BUCKET_MAIN)
ref_bucket  = gcs.bucket(BUCKET_REF)

# ── GCS presidential reverse (confirmed from inventory) ──────────────────────
PRES_REVERSE_GCS_PATH = ("reference_library/wikimedia_uscoin/Dollar_coins_of_the_United_States"
                          "/Presidential__1_Coin_Program/Presidential_dollar_coin_reverse.png")
PRES_REVERSE_GCS_URL  = f"https://storage.googleapis.com/{BUCKET_REF}/{PRES_REVERSE_GCS_PATH}"

# ── Van Buren correct obverse (confirmed from inventory) ─────────────────────
VAN_BUREN_GCS_PATH = ("reference_library/bulk_programs/presidential/"
                       "2008-presidential-dollar-coin-martin-van-buren-uncirculated-obverse.jpg")
VAN_BUREN_GCS_URL  = f"https://storage.googleapis.com/{BUCKET_REF}/{VAN_BUREN_GCS_PATH}"

# ── Grant correct obverse (confirmed from inventory) ─────────────────────────
GRANT_GCS_PATH = ("reference_library/bulk_programs/presidential/"
                   "2011-presidential-dollar-coin-grant-obverse.jpg")
GRANT_GCS_URL  = f"https://storage.googleapis.com/{BUCKET_REF}/{GRANT_GCS_PATH}"

# ── Helpers ─────────────────────────────────────────────────────────────────

def http_get(url: str, timeout=30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except Exception as e:
        print(f"  [HTTP ERR] {url[-80:]} — {e}")
        return b""

def http_head_ok(url: str, timeout=10) -> bool:
    if not url or not url.startswith("http"):
        return False
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False

def resolve_wiki(filename: str) -> str | None:
    params = urllib.parse.urlencode({
        "action": "query", "titles": f"File:{filename}",
        "prop": "imageinfo", "iiprop": "url", "format": "json",
    })
    raw = http_get(f"{WIKI_API}?{params}")
    if not raw:
        return None
    try:
        for page in json.loads(raw)["query"]["pages"].values():
            ii = page.get("imageinfo", [])
            if ii:
                return ii[0]["url"]
    except Exception as e:
        print(f"  [WIKI ERR] {filename} — {e}")
    return None

def gcs_download(bucket, path: str) -> bytes:
    """Download directly from GCS (no HTTP auth needed for service account)."""
    try:
        blob = bucket.blob(path)
        return blob.download_as_bytes()
    except Exception as e:
        print(f"  [GCS DL ERR] {path} — {e}")
        return b""

def upload_to_main(image_bytes: bytes, gcs_path: str, ctype="image/jpeg") -> str:
    if DRY_RUN:
        print(f"  [DRY-RUN] Would upload {len(image_bytes)} bytes → gs://{BUCKET_MAIN}/{gcs_path}")
        return f"{GCS_PUB_MAIN}/{gcs_path}"
    blob = main_bucket.blob(gcs_path)
    blob.upload_from_string(image_bytes, content_type=ctype)
    return f"{GCS_PUB_MAIN}/{gcs_path}"

def firestore_update(email: str, col: str, doc_id: str, updates: dict):
    if DRY_RUN:
        print(f"  [DRY-RUN] Firestore update {doc_id[:12]}… : {list(updates.keys())}")
        return
    db.collection("users").document(email).collection(col).document(doc_id).update(updates)

def ctype_from_path(p: str) -> str:
    return "image/png" if p.lower().endswith(".png") else "image/jpeg"

# ═══════════════════════════════════════════════════════════════════════════
# Step 1 — Load Eric's coins and identify presidential ones
# ═══════════════════════════════════════════════════════════════════════════

print("\n[STEP 1] Loading Eric's 28 coins …")
coins = {}
for doc in db.collection("users").document(ERIC_EMAIL).collection("coins").stream():
    d = doc.to_dict() or {}
    coins[doc.id] = {
        "doc_id":  doc.id,
        "year":    str(d.get("Year", d.get("year", ""))),
        "subject": str(d.get("Theme/Subject", d.get("subject", d.get("name", "")))),
        "program": str(d.get("Program/Series", d.get("program", ""))),
        "obv":     d.get("image_url_obverse", ""),
        "rev":     d.get("image_url_reverse", ""),
    }
    coins[doc.id]["is_presidential"] = (
        "presidential" in coins[doc.id]["program"].lower()
        or "presidential" in coins[doc.id]["subject"].lower()
    )

print(f"  Loaded {len(coins)} coins")

# ── Identify the two specific docs we need ───────────────────────────────────
van_buren_id = None
grant_id     = None
pres_ids     = []  # ALL presidential $1 doc IDs

for c in coins.values():
    subj = c["subject"].lower()
    if c["is_presidential"]:
        pres_ids.append(c["doc_id"])
    if "van buren" in subj or "martin van buren" in subj:
        van_buren_id = c["doc_id"]
    if "ulysses" in subj or ("grant" in subj and c["year"] == "2011"):
        grant_id = c["doc_id"]

print(f"  Van Buren doc_id: {van_buren_id}")
print(f"  Grant doc_id:     {grant_id}")
print(f"  Presidential $1 coins: {len(pres_ids)}")

# ═══════════════════════════════════════════════════════════════════════════
# Step 2 — Download the presidential reverse ONCE from GCS
# ═══════════════════════════════════════════════════════════════════════════

print(f"\n[STEP 2] Downloading Presidential $1 reverse from GCS …")
print(f"  Source: gs://{BUCKET_REF}/{PRES_REVERSE_GCS_PATH}")
pres_rev_bytes = gcs_download(ref_bucket, PRES_REVERSE_GCS_PATH)
if pres_rev_bytes:
    print(f"  ✓ Downloaded {len(pres_rev_bytes):,} bytes")
else:
    print("  ✗ Failed to download presidential reverse!")

# ═══════════════════════════════════════════════════════════════════════════
# Step 3 — Fix Van Buren obverse (FORCE overwrite Andrew Jackson)
# ═══════════════════════════════════════════════════════════════════════════

print(f"\n[STEP 3] Fixing Van Buren obverse …")
print(f"  Downloading correct image: gs://{BUCKET_REF}/{VAN_BUREN_GCS_PATH}")

vb_bytes = gcs_download(ref_bucket, VAN_BUREN_GCS_PATH)
if vb_bytes and van_buren_id:
    print(f"  ✓ Downloaded {len(vb_bytes):,} bytes")
    gcs_path = f"users/{ERIC_EMAIL}/coins/{van_buren_id}/obverse.jpg"
    gcs_url  = upload_to_main(vb_bytes, gcs_path, "image/jpeg")
    updates  = {
        "image_url_obverse":    gcs_url,
        "image_source_obverse": "gcs_reference_library",
        "image_attribution":    "Public Domain. Source: US Mint / GCS Reference Library.",
        "updated_at":           datetime.now(timezone.utc).isoformat(),
    }
    # Also add reverse if we have it
    if pres_rev_bytes:
        rev_path = f"users/{ERIC_EMAIL}/coins/{van_buren_id}/reverse.png"
        rev_url  = upload_to_main(pres_rev_bytes, rev_path, "image/png")
        updates["image_url_reverse"]    = rev_url
        updates["image_source_reverse"] = "gcs_reference_library"
    firestore_update(ERIC_EMAIL, "coins", van_buren_id, updates)
    print(f"  ✓ Van Buren fixed — obv: {gcs_url[-60:]}")
    print(f"                       rev: {updates.get('image_url_reverse','(not set)')[-60:]}")
else:
    print(f"  ✗ Could not fix Van Buren (bytes={len(vb_bytes)}, doc={van_buren_id})")

# ═══════════════════════════════════════════════════════════════════════════
# Step 4 — Fix Grant reverse (grant obverse was correct, just needs reverse)
# ═══════════════════════════════════════════════════════════════════════════

print(f"\n[STEP 4] Adding reverse to Grant coin …")
if grant_id and pres_rev_bytes:
    rev_path = f"users/{ERIC_EMAIL}/coins/{grant_id}/reverse.png"
    rev_url  = upload_to_main(pres_rev_bytes, rev_path, "image/png")
    updates  = {
        "image_url_reverse":    rev_url,
        "image_source_reverse": "gcs_reference_library",
        "image_attribution":    "Public Domain. Source: US Mint / GCS Reference Library.",
        "updated_at":           datetime.now(timezone.utc).isoformat(),
    }
    # Verify Grant obverse is the correct one (not a wrong match)
    grant_doc = coins.get(grant_id, {})
    if grant_doc.get("obv", "").endswith("obverse.jpg"):
        print(f"  Current Grant obverse: {grant_doc['obv'][-80:]}")
        # Check if it actually has a correct Grant image (from bulk_programs)
        if "grant" in grant_doc.get("obv", "").lower():
            print("  Grant obverse looks correct ✓")
        else:
            # Re-upload correct Grant obverse too
            print("  Re-checking Grant obverse …")
            gr_bytes = gcs_download(ref_bucket, GRANT_GCS_PATH)
            if gr_bytes:
                obv_path = f"users/{ERIC_EMAIL}/coins/{grant_id}/obverse.jpg"
                obv_url  = upload_to_main(gr_bytes, obv_path, "image/jpeg")
                updates["image_url_obverse"]    = obv_url
                updates["image_source_obverse"] = "gcs_reference_library"
                print(f"  Re-uploaded Grant obverse: {obv_url[-60:]}")
    firestore_update(ERIC_EMAIL, "coins", grant_id, updates)
    print(f"  ✓ Grant reverse added: {rev_url[-60:]}")
else:
    print(f"  ✗ Skipped (grant_id={grant_id}, rev_bytes={len(pres_rev_bytes) if pres_rev_bytes else 0})")

# ═══════════════════════════════════════════════════════════════════════════
# Step 5 — Add reverses to all other presidential $1 coins
# ═══════════════════════════════════════════════════════════════════════════

print(f"\n[STEP 5] Adding Presidential $1 reverse to all {len(pres_ids)} presidential coins …")

if pres_rev_bytes:
    attr = "Public Domain. Source: US Mint / GCS Reference Library."
    for i, doc_id in enumerate(pres_ids):
        if doc_id in (van_buren_id, grant_id):
            continue  # already handled above
        c = coins.get(doc_id, {})
        # Skip if already has a reverse
        if c.get("rev"):
            print(f"  [{i+1}] {c.get('subject','?')} — already has reverse, skipping")
            continue
        print(f"  [{i+1}] {c.get('subject','?')} ({doc_id[:12]}…) — adding reverse …")
        rev_path = f"users/{ERIC_EMAIL}/coins/{doc_id}/reverse.png"
        rev_url  = upload_to_main(pres_rev_bytes, rev_path, "image/png")
        updates  = {
            "image_url_reverse":    rev_url,
            "image_source_reverse": "gcs_reference_library",
            "image_attribution":    attr,
            "updated_at":           datetime.now(timezone.utc).isoformat(),
        }
        firestore_update(ERIC_EMAIL, "coins", doc_id, updates)
        print(f"      ✓ reverse: {rev_url[-60:]}")
else:
    print("  ✗ No reverse bytes available — skipping")

# ═══════════════════════════════════════════════════════════════════════════
# Step 6 — Fix the 2 still-empty coins: Sacagawea 2001 + Roosevelt Dime 1990
# ═══════════════════════════════════════════════════════════════════════════

print(f"\n[STEP 6] Fixing the 2 still-empty coins …")

STILL_EMPTY = {
    "29f511ee-d7bb-45fd-a075-69e38a1186b6": {
        "label":    "2001 Sacagawea Dollar",
        "gcs_search_paths": [
            # Try specific bulk_programs paths
            "reference_library/bulk_programs/sacagawea/2001-sacagawea-dollar-obverse.jpg",
            "reference_library/bulk_programs/native-american/sacagawea-dollar-obverse.jpg",
        ],
        "wiki_filenames": [
            "2001 Sacagawea dollar obverse.jpg",
            "Sacagawea dollar obverse.jpg",
            "2000P Sacagawea Obverse.jpg",
            "Sacagawea dollar 2000.jpg",
            "Native American dollar obverse.jpg",
        ],
        "wiki_direct": [
            W + "8/80/2000_Sacagawea_dollar_obverse.jpg",
            W + "d/d5/2000P_Sacagawea_Obverse.jpg",
            W + "9/99/2000-P_Sacagawea_Dollar_Obverse.jpg",
            W + "5/55/Sacagawea-dollar-obverse.jpg",
        ],
        "rev_direct": [
            W + "8/88/2000_Sacagawea_dollar_reverse.jpg",
            W + "1/17/2000P_Sacagawea_Reverse.jpg",
        ],
    },
    "670ed8fd-b87c-4761-9ade-20795f05df3c": {
        "label":    "1990 Roosevelt Dime",
        "gcs_search_paths": [
            "reference_library/bulk_programs/dime/roosevelt-dime-obverse.jpg",
            "reference_library/wikimedia_uscoin/Dime/Roosevelt_dime_obverse.jpg",
        ],
        "wiki_filenames": [
            "Roosevelt Dime Obverse 13.png",
            "Roosevelt dime obverse.jpg",
            "1946 Roosevelt dime obverse.jpg",
            "US_One_Dime_Obv.png",
        ],
        "wiki_direct": [
            W + "4/4f/Roosevelt_Dime_Obverse_13.png",
            W + "7/7d/1946-P_Roosevelt_Dime_Obverse.jpg",
            W + "e/e5/Roosevelt_dime_obverse.jpg",
            W + "3/31/US_One_Dime_Obv.png",
            W + "8/8a/US_One_Dime_Rev.png",
        ],
        "rev_direct": [
            W + "2/28/Roosevelt_Dime_Reverse_13.png",
            W + "5/5f/1946-P_Roosevelt_Dime_Reverse.jpg",
            W + "8/8a/US_One_Dime_Rev.png",
        ],
    },
}

for doc_id, spec in STILL_EMPTY.items():
    print(f"\n  Fixing: {spec['label']} ({doc_id[:12]}…)")
    obv_bytes = None
    obv_url_str = None
    rev_bytes = None
    rev_url_str = None

    # 1. Try GCS search paths directly
    for gcs_path in spec["gcs_search_paths"]:
        print(f"    Trying GCS path: {gcs_path}")
        data = gcs_download(ref_bucket, gcs_path)
        if data:
            obv_bytes = data
            obv_url_str = f"https://storage.googleapis.com/{BUCKET_REF}/{gcs_path}"
            print(f"    ✓ GCS found: {len(data):,} bytes")
            break

    # 2. Try direct Wikimedia CDN URLs
    if not obv_bytes:
        print("    Trying Wikimedia direct URLs …")
        for url in spec["wiki_direct"]:
            print(f"    Trying: {url[-70:]}")
            data = http_get(url)
            if data and len(data) > 5000:
                obv_bytes = data
                obv_url_str = url
                print(f"    ✓ Downloaded {len(data):,} bytes")
                break
            time.sleep(0.1)

    # 3. Try Wikimedia API filename resolution
    if not obv_bytes:
        print("    Trying Wikimedia API filename resolution …")
        for fn in spec["wiki_filenames"]:
            resolved = resolve_wiki(fn)
            if resolved:
                data = http_get(resolved)
                if data and len(data) > 5000:
                    obv_bytes = data
                    obv_url_str = resolved
                    print(f"    ✓ Resolved {fn} → {len(data):,} bytes")
                    break
            time.sleep(0.2)

    # Get reverse
    for rev_url in spec["rev_direct"]:
        data = http_get(rev_url)
        if data and len(data) > 5000:
            rev_bytes = data
            rev_url_str = rev_url
            break
        time.sleep(0.1)

    # Apply
    if obv_bytes:
        ext = ".png" if (obv_url_str or "").lower().endswith(".png") else ".jpg"
        ct  = "image/png" if ext == ".png" else "image/jpeg"
        obv_path = f"users/{ERIC_EMAIL}/coins/{doc_id}/obverse{ext}"
        gcs_obv  = upload_to_main(obv_bytes, obv_path, ct)

        updates = {
            "image_url_obverse":    gcs_obv,
            "image_source_obverse": ("gcs_reference_library" if BUCKET_REF in (obv_url_str or "")
                                     else "wikimedia_commons"),
            "image_attribution":    "Public Domain. Source: Wikimedia Commons / US Mint.",
            "updated_at":           datetime.now(timezone.utc).isoformat(),
        }
        if rev_bytes:
            r_ext    = ".png" if (rev_url_str or "").lower().endswith(".png") else ".jpg"
            r_ct     = "image/png" if r_ext == ".png" else "image/jpeg"
            rev_path = f"users/{ERIC_EMAIL}/coins/{doc_id}/reverse{r_ext}"
            gcs_rev  = upload_to_main(rev_bytes, rev_path, r_ct)
            updates["image_url_reverse"]    = gcs_rev
            updates["image_source_reverse"] = "wikimedia_commons"

        firestore_update(ERIC_EMAIL, "coins", doc_id, updates)
        print(f"    ✓ FIXED: {spec['label']}")
        print(f"       obverse: {gcs_obv[-60:]}")
        if "image_url_reverse" in updates:
            print(f"       reverse: {updates['image_url_reverse'][-60:]}")
    else:
        print(f"    ✗ STILL EMPTY: {spec['label']} — no image source found")

# ═══════════════════════════════════════════════════════════════════════════
# Final Report
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("FINAL STATE CHECK")
print("="*70)

print("\nReloading all Eric coins from Firestore …")
still_missing = []
now_fixed = []
for doc in db.collection("users").document(ERIC_EMAIL).collection("coins").stream():
    d = doc.to_dict() or {}
    has_obv = bool(d.get("image_url_obverse"))
    has_rev = bool(d.get("image_url_reverse"))
    subj = d.get("Theme/Subject", d.get("subject", d.get("name", "?")))
    yr   = d.get("Year", d.get("year", "?"))
    if not has_obv:
        still_missing.append(f"  {yr} {subj!r} ({doc.id[:12]}…) — obverse MISSING")
    elif not has_rev:
        still_missing.append(f"  {yr} {subj!r} ({doc.id[:12]}…) — reverse missing")

print(f"\n  Total coins with remaining gaps: {len(still_missing)}")
for m in still_missing:
    print(m)

print(f"\n{'(DRY RUN — no writes performed)' if DRY_RUN else 'Done.'}")
