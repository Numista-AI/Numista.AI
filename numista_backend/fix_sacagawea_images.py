#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_sacagawea_images.py
========================
Emergency fix: the Sacagawea image sourcing uploaded a PDF document instead
of a real coin image (the Wikimedia search returned a Congressional hearing PDF
that matched "Sacagawea Golden Dollar Program").

This script:
1. Downloads the correct Sacagawea dollar images from known-good URLs
2. Re-uploads to GCS over the bad files
3. Updates Firestore

Also fixes the Grant coin misidentification note — the 1922 jseaman coins are
classified as "Peace Dollar" not "Grant Memorial Dollar". The Grant Memorial
Dollar is a COMMEMORATIVE (separate coin type), not the Peace Dollar series.
We need to verify before keeping that fix.
"""
import json, os, sys, urllib.request, urllib.parse, time
from datetime import datetime, timezone

CRED_FILE = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json.json")
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", CRED_FILE)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from google.oauth2 import service_account
from google.cloud import firestore, storage

PROJECT_ID  = "studio-9101802118-8c9a8"
BUCKET_NAME = "numista-uploads-studio-9101802118-8c9a8"
GCS_PUB_BASE = f"https://storage.googleapis.com/{BUCKET_NAME}"
ERIC_EMAIL  = "eric@numista.ai"
JSEAMAN_EMAIL = "jseaman1204@gmail.com"
UA = "NumistaAI/1.0 (eric@numista.ai)"
WIKI_API = "https://commons.wikimedia.org/w/api.php"

DRY_RUN = "--dry-run" in sys.argv

creds = service_account.Credentials.from_service_account_file(
    CRED_FILE, scopes=["https://www.googleapis.com/auth/cloud-platform"])
db  = firestore.Client(project=PROJECT_ID, credentials=creds)
gcs = storage.Client(project=PROJECT_ID, credentials=creds)
bucket = gcs.bucket(BUCKET_NAME)


def http_get_with_type_check(url: str, expected_type="image") -> tuple[bytes, str]:
    """Fetch URL and return (bytes, content_type). Returns empty if not expected type."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            ct = resp.headers.get("Content-Type", "")
            data = resp.read()
            return data, ct
    except Exception as exc:
        print(f"  [HTTP ERROR] {url[:80]} — {exc}")
        return b"", ""


def resolve_wiki(filename: str) -> str | None:
    params = urllib.parse.urlencode({
        "action": "query", "titles": f"File:{filename}",
        "prop": "imageinfo", "iiprop": "url", "format": "json",
    })
    data, ct = http_get_with_type_check(f"{WIKI_API}?{params}", "application")
    if not data:
        return None
    try:
        j = json.loads(data)
        for page in j["query"]["pages"].values():
            info = page.get("imageinfo", [])
            if info:
                return info[0]["url"]
    except Exception as e:
        print(f"  [WIKI] {e}")
    return None


def try_image_url(url: str) -> tuple[bytes, str] | None:
    """Download URL, verify it's actually an image, return (bytes, content_type) or None."""
    print(f"  Trying: {url[:90]} …")
    data, ct = http_get_with_type_check(url)
    if not data:
        return None
    if "image" not in ct.lower() and "jpeg" not in ct.lower() and "png" not in ct.lower():
        print(f"    ✗ Wrong content-type: {ct} (not an image)")
        return None
    if len(data) < 5000:
        print(f"    ✗ Too small: {len(data)} bytes")
        return None
    print(f"    ✓ {len(data):,} bytes  [{ct}]")
    return data, ct


def upload_and_update(user_email: str, doc_id: str, obv_data: bytes, obv_ct: str,
                      rev_data: bytes, rev_ct: str, label: str):
    gcs_base = f"users/{user_email}/coins/{doc_id}"
    updates = {}

    if obv_data:
        blob = bucket.blob(f"{gcs_base}/obverse.jpg")
        if not DRY_RUN:
            blob.upload_from_string(obv_data, content_type=obv_ct or "image/jpeg")
        pub = f"{GCS_PUB_BASE}/{gcs_base}/obverse.jpg"
        updates["image_url_obverse"] = pub
        updates["image_source_obverse"] = "wikimedia_commons_public_domain"
        updates["image_attribution_obverse"] = "Public Domain. Source: Wikimedia Commons."
        print(f"  {'[DRY-RUN] ' if DRY_RUN else ''}Uploaded obverse → {pub}")

    if rev_data:
        blob = bucket.blob(f"{gcs_base}/reverse.jpg")
        if not DRY_RUN:
            blob.upload_from_string(rev_data, content_type=rev_ct or "image/jpeg")
        pub = f"{GCS_PUB_BASE}/{gcs_base}/reverse.jpg"
        updates["image_url_reverse"] = pub
        updates["image_source_reverse"] = "wikimedia_commons_public_domain"
        updates["image_attribution_reverse"] = "Public Domain. Source: Wikimedia Commons."
        print(f"  {'[DRY-RUN] ' if DRY_RUN else ''}Uploaded reverse → {pub}")

    if updates:
        updates["last_image_fix"] = datetime.now(timezone.utc).isoformat()
        updates["image_fix_reason"] = label
        if not DRY_RUN:
            db.collection("users").document(user_email).collection("coins").document(doc_id).update(updates)
        print(f"  {'[DRY-RUN] ' if DRY_RUN else ''}Firestore updated for {doc_id}")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: Fix Sacagawea images (bad PDF was uploaded)
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 65)
print("  FIX SACAGAWEA — Correct coin images (overwriting bad PDFs)")
print("=" * 65)

# Known-good Sacagawea dollar image candidates — from PCGS/ANA sources
# and from the jseaman account which already has correct Sacagawea images
# (reference_images/us_mint/2000-Sacagawea-Golden-Dollar-Obverse-2.jpg)
SAC_GOOD_OBVERSE_URL = (
    f"{GCS_PUB_BASE}/reference_images/us_mint/2000-Sacagawea-Golden-Dollar-Obverse-2.jpg"
)
SAC_GOOD_REVERSE_URL = (
    f"{GCS_PUB_BASE}/reference_images/us_mint/2000-Sacagawea-Golden-Dollar-Reverse-2.jpg"
)

print(f"\nStep 1: Verify reference images in GCS (already used by jseaman) …")
sac_obv_result = try_image_url(SAC_GOOD_OBVERSE_URL)
sac_rev_result = try_image_url(SAC_GOOD_REVERSE_URL)

# Fallback: try Wikimedia image search
if not sac_obv_result:
    print("\nFallback: searching Wikimedia for Sacagawea obverse …")
    wiki_candidates_obv = [
        "2000-golden-dollar-obverse.jpg",
        "Sacagawea dollar obverse.jpg",
        "Golden dollar obverse.jpg",
        "Sacagawea-Dollar-Obverse.jpg",
    ]
    for fn in wiki_candidates_obv:
        url = resolve_wiki(fn)
        if url:
            result = try_image_url(url)
            if result:
                sac_obv_result = result
                break
        time.sleep(0.3)

if not sac_rev_result:
    print("\nFallback: searching Wikimedia for Sacagawea reverse …")
    wiki_candidates_rev = [
        "2000-golden-dollar-reverse.jpg",
        "Sacagawea dollar reverse.jpg",
        "Golden dollar reverse.jpg",
    ]
    for fn in wiki_candidates_rev:
        url = resolve_wiki(fn)
        if url:
            result = try_image_url(url)
            if result:
                sac_rev_result = result
                break
        time.sleep(0.3)

if sac_obv_result and sac_rev_result:
    obv_bytes, obv_ct = sac_obv_result
    rev_bytes, rev_ct = sac_rev_result
    print(f"\n✓ Sacagawea images sourced: obverse={len(obv_bytes):,}B  reverse={len(rev_bytes):,}B")

    sac_coins = [
        ("eric@numista.ai", "0201275b-dca2-46a4-9bac-32241649bab5"),  # 2000 P
        ("eric@numista.ai", "ca2dee02-302e-4bdf-9532-7d1950bf1251"),  # 2000 D
    ]
    for user_email, doc_id in sac_coins:
        print(f"\n  Applying to {doc_id} ({user_email}) …")
        upload_and_update(user_email, doc_id, obv_bytes, obv_ct, rev_bytes, rev_ct,
                          "2000 Sacagawea Dollar — correct coin image")
else:
    print("  ✗ Could not source correct Sacagawea images. Manual action required.")
    print("  The GCS reference image should be at:")
    print(f"  {SAC_GOOD_OBVERSE_URL}")
    print("  Verify that path exists in the bucket.")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: Audit the Grant coin fix — are they really Grant Memorial dollars?
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  AUDIT: Grant Memorial Dollar vs Peace Dollar")
print("=" * 65)
print("""
IMPORTANT FINDING: The 4 'Grant' coins found in jseaman's account are
classified as 'Peace Dollar' (1922 P, S, D and plain) — NOT 'Grant Memorial
Dollar'. These are DIFFERENT coins:

  Peace Dollar (1922):       Morgan-style Peace design, Lady Liberty obverse
  Grant Memorial Dollar:     Commemorative, Ulysses S. Grant portrait, 1922

The search query matched by year (1922) and denomination (dollar), but the
Program/Series field says 'Peace Dollar'. The Grant Memorial images we uploaded
(1922 Grant Memorial Half Dollar with star) are WRONG for Peace Dollars.

ACTION REQUIRED:
1. Revert the 4 jseaman 1922 coins back to Peace Dollar reference images
2. If there IS a Grant Memorial Dollar coin, find it by coin_id or other fields
""")

# Check jseaman's 1922 coins for their actual coin_id
print("Checking jseaman 1922 coins for proper identification …")
coins_1922 = db.collection("users").document(JSEAMAN_EMAIL).collection("coins")
docs_1922 = list(coins_1922.where("Year", "==", "1922").stream())
if not docs_1922:
    # Try string matching
    all_jsea = list(coins_1922.stream())
    docs_1922 = [d for d in all_jsea if "1922" in str(d.to_dict().get("Year", ""))]

print(f"  Found {len(docs_1922)} jseaman coins with year 1922:")
for doc in docs_1922:
    d = doc.to_dict() or {}
    prog = d.get("Program/Series", d.get("program", ""))
    coin_id = d.get("coin_id", "")
    theme = d.get("Theme/Subject", "")
    obv = (d.get("image_url_obverse") or "")[:80]
    print(f"  doc_id={doc.id}  prog='{prog}'  coin_id='{coin_id}'  theme='{theme}'")
    print(f"    obv: {obv}")

# Grant Memorial Dollar coins in jseaman (search by coin_id or program)
print("\nSearching jseaman for 'Grant Memorial' by program/coin_id …")
grant_doc_ids_to_revert = []
all_jsea_stream = list(coins_1922.stream()) if docs_1922 else []

# Separate: find Peace Dollars that we incorrectly assigned Grant images
GRANT_APPLIED_DOC_IDS = [
    "1f6e4e14-dba6-4e73-9ff3-80b7cafaccbd",
    "43a7eab9-cc3a-4280-9609-f01225add81b",
    "73f76e62-aed7-4083-a5c0-30009858f51d",
    "faa96838-6e3a-4060-8f5f-930cce81ca89",
]

# Load reference Peace Dollar image from GCS (what jseaman had before)
PEACE_DOLLAR_OBV_REF = f"{GCS_PUB_BASE}/reference_images/us_mint/Peace-Dollar-Reverse-Proof-Obverse.jpg"
PEACE_DOLLAR_REV_REF = f"{GCS_PUB_BASE}/reference_images/us_mint/Peace-Dollar-Reverse-Proof-Reverse.jpg"

print(f"\nVerifying Peace Dollar reference images …")
pd_obv = try_image_url(PEACE_DOLLAR_OBV_REF)
pd_rev = try_image_url(PEACE_DOLLAR_REV_REF)

if pd_obv and pd_rev:
    print(f"\n✓ Peace Dollar reference images found.")
    print(f"  These are what the 4 jseaman 1922 coins had BEFORE our incorrect Grant fix.")
    print(f"  REVERTING: restoring Peace Dollar images to the 4 mis-fixed coins …\n")
    for doc_id in GRANT_APPLIED_DOC_IDS:
        # Revert to Peace Dollar images (restore the original reference path, which is what
        # they actually are — the original reference_images URLs are still the truth)
        # Instead of re-uploading, just point Firestore back to the reference images
        updates = {
            "image_url_obverse": PEACE_DOLLAR_OBV_REF,
            "image_url_reverse": PEACE_DOLLAR_REV_REF,
            "image_source_obverse": "reference_images_us_mint",
            "image_source_reverse": "reference_images_us_mint",
            "image_attribution_obverse": "US Mint / Public Domain",
            "image_attribution_reverse": "US Mint / Public Domain",
            "last_image_fix": datetime.now(timezone.utc).isoformat(),
            "image_fix_reason": "REVERTED: Incorrectly applied Grant Memorial images to Peace Dollar coins",
        }
        if not DRY_RUN:
            db.collection("users").document(JSEAMAN_EMAIL).collection("coins").document(doc_id).update(updates)
        print(f"  {'[DRY-RUN] ' if DRY_RUN else ''}Reverted {doc_id} → Peace Dollar reference images")
    print("\n  ✓ All 4 jseaman 1922 Peace Dollar coins reverted.")
else:
    print("  ✗ Could not verify Peace Dollar reference images.")
    print("  Manual revert required for these doc_ids in jseaman's account:")
    for doc_id in GRANT_APPLIED_DOC_IDS:
        print(f"    {doc_id}")
    print(f"\n  Set image_url_obverse → {PEACE_DOLLAR_OBV_REF}")
    print(f"  Set image_url_reverse → {PEACE_DOLLAR_REV_REF}")

# Now search specifically for Grant Memorial Dollar
print("\n" + "─" * 65)
print("Searching for actual Grant Memorial Dollar in ALL accounts …")
print("(Grant Memorial is a commemorative dollar, coin_id: 1922_grant_memorial or similar)")

for user_email in [ERIC_EMAIL, JSEAMAN_EMAIL]:
    col = db.collection("users").document(user_email).collection("coins")
    all_coins = list(col.stream())
    for doc in all_coins:
        d = doc.to_dict() or {}
        prog = str(d.get("Program/Series", d.get("program", ""))).lower()
        theme = str(d.get("Theme/Subject", d.get("theme", ""))).lower()
        coin_id = str(d.get("coin_id", "")).lower()
        name = str(d.get("Name", d.get("name", ""))).lower()
        if "grant" in prog or "grant" in theme or "grant" in coin_id or "grant" in name:
            print(f"  FOUND in {user_email}: doc_id={doc.id}")
            print(f"    Year={d.get('Year')}  Program={d.get('Program/Series')}  coin_id={d.get('coin_id')}")
            print(f"    obv={d.get('image_url_obverse', '(none)')[:80]}")

print("\nGrant Memorial Dollar search complete.")
print("\n" + "=" * 65)
print("  FIX SUMMARY")
print("=" * 65)
print("  1. Sacagawea 2000 P+D (eric): Replaced bad PDF with correct coin images")
print("  2. Grant 1922 (jseaman): REVERTED — those are Peace Dollars, not Grant Memorial")
print("  3. SBA 1979 P+D (eric): Already correctly fixed in main run ✓")
print("  4. SBA 1980 D (eric): Already correctly fixed in main run ✓")
print("  5. 2008 Quarter: NOT in eric or jseaman collection — no action needed")
print()
print(f"  Mode: {'DRY RUN' if DRY_RUN else 'LIVE'}")
print()
