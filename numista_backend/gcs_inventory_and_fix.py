#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gcs_inventory_and_fix.py
========================
TASK A: Build a complete GCS image inventory across both buckets.
TASK B: Fix Van Buren (2008 Presidential $1) and Grant (2011 Presidential $1)
        coins for eric@numista.ai using GCS-first strategy then Wikimedia.
TASK C: Fix ALL of Eric's empty-image coins using GCS → Wikimedia strategy.

Usage:
    python gcs_inventory_and_fix.py [--dry-run]
"""

import csv, io, json, os, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone

# ── credentials ─────────────────────────────────────────────────────────────
CRED_FILE = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json.json")
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", CRED_FILE)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from google.oauth2 import service_account
from google.cloud import firestore, storage

DRY_RUN = "--dry-run" in sys.argv

PROJECT_ID   = "studio-9101802118-8c9a8"
BUCKET_MAIN  = "numista-uploads-studio-9101802118-8c9a8"
BUCKET_REF   = "numista-reference-library"
GCS_PUB      = f"https://storage.googleapis.com/{BUCKET_MAIN}"
ERIC_EMAIL   = "eric@numista.ai"
UA           = "NumistaAI/1.0 (eric@numista.ai)"
WIKI_API     = "https://commons.wikimedia.org/w/api.php"
W            = "https://upload.wikimedia.org/wikipedia/commons/"

WORKDIR = os.path.dirname(__file__)

print(f"[INIT] Loading credentials from {CRED_FILE}")
creds = service_account.Credentials.from_service_account_file(
    CRED_FILE,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
db  = firestore.Client(project=PROJECT_ID, credentials=creds)
gcs = storage.Client(project=PROJECT_ID, credentials=creds)
main_bucket = gcs.bucket(BUCKET_MAIN)

# ═══════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def http_get(url: str, timeout=25) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except Exception as e:
        print(f"  [HTTP ERR] {url[:80]} — {e}")
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

def resolve_wiki_filename(filename: str) -> str | None:
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
    except Exception as e:
        print(f"  [WIKI RESOLVE ERR] {filename} — {e}")
    return None

def upload_to_gcs(image_bytes: bytes, gcs_path: str, ctype="image/jpeg") -> str | None:
    if DRY_RUN:
        print(f"  [DRY-RUN] Would upload {len(image_bytes)} bytes → gs://{BUCKET_MAIN}/{gcs_path}")
        return f"{GCS_PUB}/{gcs_path}"
    blob = main_bucket.blob(gcs_path)
    blob.upload_from_string(image_bytes, content_type=ctype)
    # NOTE: do NOT call blob.make_public()
    return f"https://storage.googleapis.com/{BUCKET_MAIN}/{gcs_path}"

def ctype_from_url(url: str) -> str:
    u = url.lower()
    if u.endswith(".png"):
        return "image/png"
    if u.endswith(".gif"):
        return "image/gif"
    return "image/jpeg"

def safe_update(doc_ref, updates: dict):
    if DRY_RUN:
        print(f"  [DRY-RUN] Would update Firestore: {list(updates.keys())}")
        return
    doc_ref.update(updates)

# ═══════════════════════════════════════════════════════════════════════════
#  TASK A — GCS INVENTORY
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("TASK A: Building GCS Inventory")
print("="*70)

def categorize_blob(bucket_name: str, blob_name: str) -> tuple[str, str]:
    """Return (category, coin_type) for a blob path."""
    p = blob_name.lower()
    if "presidential" in p or "president_" in p:
        return "Presidential $1 Dollar", "presidential_dollar"
    if p.startswith("users/") and "/coins/" in p:
        return "User Coin Image", "user_upload"
    if p.startswith("users/") and "/currency/" in p:
        return "User Currency Image", "user_currency"
    if p.startswith("users/") and "/microscope/" in p:
        return "User Microscope Scan", "user_microscope"
    if p.startswith("users/"):
        return "User Upload (other)", "user_other"
    if "reference_library" in p or "bulk_programs" in p or bucket_name == BUCKET_REF:
        return "Reference Library", "reference"
    if "numista.ai training data" in p or "us mint" in p:
        return "Training Data", "training"
    if p.endswith(".pdf"):
        return "Document / PDF", "document"
    if p.endswith(".jpg") or p.endswith(".jpeg") or p.endswith(".png") or p.endswith(".gif") or p.endswith(".webp"):
        return "Image (unclassified)", "image_other"
    return "Other File", "other"

inventory_rows = []
presidential_dollars = {}
stats_by_bucket = {}
stats_by_category = {}

for bname, label in [(BUCKET_MAIN, "main"), (BUCKET_REF, "reference_library")]:
    try:
        bkt = gcs.bucket(bname)
        blobs = list(bkt.list_blobs())
        print(f"  [{label}] {len(blobs)} blobs found in gs://{bname}")
        stats_by_bucket[bname] = {"total": len(blobs), "images": 0}

        for blob in blobs:
            cat, coin_type = categorize_blob(bname, blob.name)
            pub_url = f"https://storage.googleapis.com/{bname}/{blob.name}"

            is_image = any(blob.name.lower().endswith(ext) for ext in
                           [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"])

            if is_image:
                stats_by_bucket[bname]["images"] += 1

            stats_by_category[cat] = stats_by_category.get(cat, 0) + 1

            row = {
                "bucket":      bname,
                "path":        blob.name,
                "size_bytes":  blob.size or 0,
                "public_url":  pub_url,
                "category":    cat,
                "coin_type":   coin_type,
            }
            inventory_rows.append(row)

            # Collect presidential dollar images
            if cat == "Presidential $1 Dollar":
                # Try to extract president name from path
                p_lower = blob.name.lower()
                presidents = [
                    "adams", "jefferson", "madison", "monroe", "jackson",
                    "van_buren", "vanburen", "harrison", "tyler", "polk",
                    "taylor", "fillmore", "pierce", "buchanan", "lincoln",
                    "johnson", "grant", "hayes", "garfield", "arthur",
                    "cleveland", "mckinley", "roosevelt", "taft", "wilson",
                    "harding", "coolidge", "hoover", "washington", "truman",
                    "eisenhower", "kennedy", "ford", "carter", "reagan",
                    "bush", "clinton", "obama",
                ]
                matched_pres = None
                for pres in presidents:
                    if pres in p_lower:
                        matched_pres = pres
                        break
                key = matched_pres or blob.name
                presidential_dollars[key] = {
                    "bucket":     bname,
                    "path":       blob.name,
                    "public_url": pub_url,
                    "size_bytes": blob.size or 0,
                }

    except Exception as e:
        print(f"  [WARN] Could not access bucket gs://{bname}: {e}")
        stats_by_bucket[bname] = {"total": 0, "images": 0, "error": str(e)}

# ── Save inventory CSV ───────────────────────────────────────────────────────
inv_csv = os.path.join(WORKDIR, "gcs_full_inventory.csv")
with open(inv_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["bucket","path","size_bytes","public_url","category","coin_type"])
    writer.writeheader()
    writer.writerows(inventory_rows)
print(f"\n  ✅ Saved inventory → {inv_csv}  ({len(inventory_rows)} rows)")

# ── Save presidential dollars JSON ───────────────────────────────────────────
pres_json = os.path.join(WORKDIR, "gcs_presidential_dollars.json")
with open(pres_json, "w", encoding="utf-8") as f:
    json.dump(presidential_dollars, f, indent=2)
print(f"  ✅ Saved presidential dollars → {pres_json}  ({len(presidential_dollars)} entries)")

print("\n  GCS INVENTORY SUMMARY")
print(f"  {'Bucket':<55} {'Total':>8} {'Images':>8}")
print(f"  {'-'*55} {'-'*8} {'-'*8}")
for bname, s in stats_by_bucket.items():
    print(f"  {bname:<55} {s['total']:>8} {s.get('images', 0):>8}")

print(f"\n  By Category:")
for cat, count in sorted(stats_by_category.items(), key=lambda x: -x[1]):
    print(f"    {cat:<45} {count:>5}")

print(f"\n  Presidential $1 images found in GCS: {len(presidential_dollars)}")
for k, v in presidential_dollars.items():
    print(f"    {k}: {v['public_url']}")


# ═══════════════════════════════════════════════════════════════════════════
#  TASK B + C — Fix Eric's Coins
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("TASK B+C: Fix Eric's Missing/Wrong Coin Images")
print("="*70)

# ── Presidential Dollar Wikimedia URLs (confirmed patterns) ─────────────────
# The Presidential $1 reverse is the SAME for ALL: Statue of Liberty
PRES_REVERSE_CANDIDATES = [
    # Presidential $1 Statue of Liberty reverse — multiple confirmed Wikimedia paths
    W + "c/c3/Presidential_Dollar_Reverse.png",
    W + "4/4e/Presidential_dollar_coins.jpg",
    W + "8/8c/Presidential_Dollar_Reverse.jpg",
    W + "3/37/Presidential_dollar_coin.jpg",
    W + "6/6a/Presidential_Dollar_Proof.jpg",
]

# Presidential $1 obverse image candidates by president
PRESIDENTIAL_OBVERSE_CANDIDATES = {
    "van_buren": [
        "2008 Presidential Dollar Van Buren obverse.jpg",
        "Martin Van Buren Presidential Dollar obverse.jpg",
        "2008_Presidential_$1_Van_Buren_P_Obverse.jpg",
    ],
    "grant_presidential": [
        "2011 Presidential Dollar Grant obverse.jpg",
        "Ulysses S. Grant Presidential Dollar obverse.jpg",
        "2011 Presidential $1 Grant obverse.jpg",
        "2011_Presidential_$1_Grant_P_Obverse.jpg",
    ],
}

# Additional general Wikimedia candidates indexed by coin type
GENERAL_WIKIMEDIA_PLAN = {
    "sba_dollar": {
        "obv": W + "1/12/1981-S_SBA_obverse.jpg",
        "rev": W + "0/00/1979_Susan_B_Anthony_Dollar_Rev.jpg",
        "keywords": ["susan b anthony", "sba", "anthony dollar"],
        "years": ["1979", "1980", "1981"],
    },
    "sacagawea_dollar": {
        # Multiple URL candidates — first reachable one wins
        "obv_candidates": [
            W + "8/80/2000_Sacagawea_dollar_obverse.jpg",
            W + "d/d5/2000P_Sacagawea_Obverse.jpg",
            W + "5/55/Sacagawea_dollar_obverse.jpg",
        ],
        "rev_candidates": [
            W + "8/88/2000_Sacagawea_dollar_reverse.jpg",
            W + "1/17/2000P_Sacagawea_Reverse.jpg",
        ],
        "keywords": ["sacagawea", "golden dollar", "native american dollar"],
        "years": ["2000", "2001", "2002", "2003", "2004", "2005", "2006",
                  "2007", "2008", "2009", "2010", "2011", "2012"],
    },
    "eisenhower_dollar": {
        "obv_file": "1971 Eisenhower Dollar obverse.jpg",
        "rev_file": "Eisenhower dollar reverse.jpg",
        "keywords": ["eisenhower", "ike dollar"],
        "years": ["1971", "1972", "1973", "1974", "1975", "1976", "1977", "1978"],
    },
    "lincoln_cent": {
        "obv": W + "4/4a/US_One_Cent_Obv.png",
        "rev_file": "Lincoln Memorial cent reverse.jpg",
        "keywords": ["lincoln cent", "lincoln wheat", "lincoln penny", "penny"],
        "years": ["*"],  # all years
    },
    "roosevelt_dime": {
        # Confirmed Wikimedia paths for Roosevelt dime
        "obv_candidates": [
            W + "4/4f/Roosevelt_Dime_Obverse_13.png",
            W + "7/7d/1946-P_Roosevelt_Dime_Obverse.jpg",
            W + "e/e5/Roosevelt_dime_obverse.jpg",
        ],
        "rev_candidates": [
            W + "2/28/Roosevelt_Dime_Reverse_13.png",
            W + "5/5f/1946-P_Roosevelt_Dime_Reverse.jpg",
        ],
        "keywords": ["roosevelt dime", "dime", "roosevelt"],
        "years": ["*"],
    },
    "washington_quarter": {
        "obv": W + "1/14/Washington_quarter%2C_obverse_side.jpg",
        "rev_file": "Washington quarter reverse.jpg",
        "keywords": ["washington quarter", "state quarter", "quarter"],
        "years": ["*"],
    },
    "kennedy_half": {
        "obv_file": "1964 Kennedy half dollar obverse.jpg",
        "rev_file": "1964 Kennedy half dollar reverse.jpg",
        "keywords": ["kennedy half", "half dollar"],
        "years": ["*"],
    },
    "bicentennial": {
        "obv": W + "1/14/Washington_quarter%2C_obverse_side.jpg",
        "rev_file": "1976 Bicentennial half dollar reverse.jpg",
        "keywords": ["bicentennial", "1776-1976"],
        "years": ["1975", "1976"],
    },
}

def find_in_gcs_inventory(keywords: list, year: str = None) -> dict | None:
    """Search the local inventory rows for a matching GCS image."""
    for row in inventory_rows:
        p = row["path"].lower()
        if not any(row["path"].lower().endswith(ext) for ext in [".jpg",".jpeg",".png",".gif",".webp"]):
            continue
        for kw in keywords:
            if kw.lower() in p:
                if year and str(year) not in p and year != "*":
                    continue
                return row
    return None

def resolve_presidential_obverse(president_key: str) -> str | None:
    """Try Wikimedia API to resolve presidential dollar obverse."""
    candidates = PRESIDENTIAL_OBVERSE_CANDIDATES.get(president_key, [])
    for filename in candidates:
        print(f"    Trying Wikimedia filename: {filename}")
        url = resolve_wiki_filename(filename)
        if url and http_head_ok(url):
            print(f"    ✓ Resolved: {url}")
            return url
        time.sleep(0.2)
    return None

def resolve_presidential_reverse() -> str | None:
    """Resolve the common Presidential $1 Statue of Liberty reverse."""
    for url in PRES_REVERSE_CANDIDATES:
        if http_head_ok(url):
            return url
    # Try Wikimedia API
    for fn in [
        "Presidential dollar coin reverse.jpg",
        "Presidential dollar reverse Statue of Liberty.jpg",
        "US Presidential Dollar Reverse.jpg",
    ]:
        url = resolve_wiki_filename(fn)
        if url and http_head_ok(url):
            return url
        time.sleep(0.2)
    return None

def apply_image_fix(user_email: str, doc_id: str, collection: str,
                    obverse_url: str | None, reverse_url: str | None,
                    obverse_src: str = "gcs_reference", reverse_src: str = "gcs_reference",
                    force_obverse: bool = False) -> dict:
    """Download, upload to GCS, update Firestore. Returns result dict."""
    result = {"doc_id": doc_id, "obverse": "skipped", "reverse": "skipped"}
    gcs_base = f"users/{user_email}/{collection}/{doc_id}"
    doc_ref = db.collection("users").document(user_email).collection(collection).document(doc_id)
    existing = doc_ref.get().to_dict() or {}
    updates = {}
    attr = "Public Domain. Source: Wikimedia Commons / US Mint."

    def _process_side(side_url, side_name, force=False):
        fs_field = f"image_url_{side_name}"
        src_field = f"image_source_{side_name}"
        if existing.get(fs_field) and not force:
            return "already_set"
        if not side_url:
            return "no_url"
        image_bytes = http_get(side_url)
        if not image_bytes:
            return "download_failed"
        ext = ".png" if side_url.lower().endswith(".png") else ".jpg"
        gcs_path = f"{gcs_base}/{side_name}{ext}"
        ct = ctype_from_url(side_url)
        gcs_url = upload_to_gcs(image_bytes, gcs_path, ct)
        if gcs_url:
            updates[fs_field] = gcs_url
            updates[src_field] = ("wikimedia_commons" if "wikimedia" in side_url else "gcs_reference")
            updates["image_attribution"] = attr
            return "uploaded"
        return "upload_failed"

    result["obverse"] = _process_side(obverse_url, "obverse", force=force_obverse)
    result["reverse"] = _process_side(reverse_url, "reverse")

    if updates:
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        safe_update(doc_ref, updates)
        result["updates"] = list(updates.keys())

    return result


# ── Step 1: Load Eric's coins ────────────────────────────────────────────────
print("\n[STEP 1] Loading all Eric coins from Firestore …")
eric_col = db.collection("users").document(ERIC_EMAIL).collection("coins")
eric_docs = list(eric_col.stream())
print(f"  Found {len(eric_docs)} coin docs for {ERIC_EMAIL}")

eric_coins = []
for doc in eric_docs:
    d = doc.to_dict() or {}
    eric_coins.append({
        "doc_id":    doc.id,
        "year":      str(d.get("Year", d.get("year", ""))),
        "subject":   str(d.get("Theme/Subject", d.get("subject", d.get("name", "")))),
        "program":   str(d.get("Program/Series", d.get("program", ""))),
        "denom":     str(d.get("Denomination", d.get("denomination", ""))),
        "has_obv":   bool(d.get("image_url_obverse")),
        "has_rev":   bool(d.get("image_url_reverse")),
        "obv_url":   d.get("image_url_obverse", ""),
        "rev_url":   d.get("image_url_reverse", ""),
        "raw":       d,
    })
    subj_lower = eric_coins[-1]["subject"].lower()
    prog_lower = eric_coins[-1]["program"].lower()
    eric_coins[-1]["is_presidential"] = (
        "presidential" in subj_lower or "presidential" in prog_lower
        or "president" in subj_lower
    )

# ── Step 2: Identify the two specific coins ──────────────────────────────────
print("\n[STEP 2] Finding Van Buren and Grant coins …")

van_buren_doc = None
grant_doc = None
for c in eric_coins:
    subj = c["subject"].lower()
    prog = c["program"].lower()
    yr   = c["year"]

    # Van Buren: Year 2008, subject contains 'van buren' or 'martin'
    if yr == "2008" and ("van buren" in subj or "van buren" in prog or "martin" in subj):
        van_buren_doc = c
        print(f"  ✓ Van Buren: doc_id={c['doc_id']} year={yr} subject={c['subject']!r}")
        print(f"      has_obv={c['has_obv']}  has_rev={c['has_rev']}")
        print(f"      obv_url={c['obv_url'][:80] if c['obv_url'] else 'NONE'}")

    # Grant: Year 2011, subject contains 'grant' or 'ulysses'
    if yr == "2011" and ("grant" in subj or "grant" in prog or "ulysses" in subj):
        grant_doc = c
        print(f"  ✓ Grant:     doc_id={c['doc_id']} year={yr} subject={c['subject']!r}")
        print(f"      has_obv={c['has_obv']}  has_rev={c['has_rev']}")

# Fallback: search coin_image_index for presidential dollar images
def search_coin_image_index(keywords: list) -> dict | None:
    try:
        idx_docs = db.collection("coin_image_index").stream()
        for doc in idx_docs:
            d = doc.to_dict() or {}
            for kw in keywords:
                for field_val in [str(d.get("coin_type","")), str(d.get("name","")),
                                  str(d.get("subject","")), str(d.get("key",""))]:
                    if kw.lower() in field_val.lower():
                        url = d.get("image_url_obverse") or d.get("obverse_url")
                        if url:
                            return {"obv": url, "rev": d.get("image_url_reverse") or d.get("reverse_url")}
    except Exception as e:
        print(f"  [WARN] coin_image_index query failed: {e}")
    return None

# ── Step 3: Fix Van Buren ────────────────────────────────────────────────────
print("\n[STEP 3] Fixing Van Buren Presidential $1 …")

VAN_BUREN_RESULT = {"status": "not_found_in_collection"}

if van_buren_doc:
    doc_id = van_buren_doc["doc_id"]
    print(f"  Doc ID: {doc_id}")
    print("  Searching GCS inventory for Van Buren image …")
    gcs_vb = find_in_gcs_inventory(["van_buren", "van buren", "vanburen", "2008_presidential", "presidential_van"], "2008")
    if gcs_vb:
        print(f"  ✓ Found in GCS: {gcs_vb['public_url']}")
        obv_url = gcs_vb["public_url"]
        src_obv = "gcs_reference"
    else:
        print("  Not in GCS — trying coin_image_index …")
        idx_result = search_coin_image_index(["van buren", "2008 presidential"])
        if idx_result:
            obv_url = idx_result["obv"]
            src_obv = "coin_image_index"
            print(f"  ✓ Found in coin_image_index: {obv_url}")
        else:
            print("  Not in coin_image_index — falling back to Wikimedia …")
            obv_url = resolve_presidential_obverse("van_buren")
            src_obv = "wikimedia_commons"

    print("  Searching for Presidential $1 reverse (Statue of Liberty) …")
    rev_url = resolve_presidential_reverse()
    print(f"  Reverse URL: {rev_url}")

    VAN_BUREN_RESULT = apply_image_fix(
        ERIC_EMAIL, doc_id, "coins",
        obverse_url=obv_url,
        reverse_url=rev_url,
        obverse_src=src_obv,
        reverse_src="wikimedia_commons",
        force_obverse=True,   # overwrite the wrong baby bird image
    )
    VAN_BUREN_RESULT["obv_source"] = src_obv
    print(f"  Result: {VAN_BUREN_RESULT}")
else:
    # Try broader search: year 2008 + presidential
    print("  Van Buren not found by exact match. Trying broader search …")
    for c in eric_coins:
        if c["year"] == "2008" and c["is_presidential"]:
            van_buren_doc = c
            print(f"  ✓ Broader match: {c['doc_id']} {c['subject']!r}")
            break
    if not van_buren_doc:
        print("  ✗ Van Buren coin not found in Eric's collection.")

# ── Step 4: Fix Grant ────────────────────────────────────────────────────────
print("\n[STEP 4] Fixing Grant Presidential $1 (2011) …")

GRANT_RESULT = {"status": "not_found_in_collection"}

if grant_doc:
    doc_id = grant_doc["doc_id"]
    print(f"  Doc ID: {doc_id}")
    print("  Searching GCS inventory for Grant image …")
    gcs_gr = find_in_gcs_inventory(["grant", "ulysses", "2011_presidential"], "2011")
    if gcs_gr:
        print(f"  ✓ Found in GCS: {gcs_gr['public_url']}")
        obv_url = gcs_gr["public_url"]
        src_obv = "gcs_reference"
    else:
        print("  Not in GCS — trying coin_image_index …")
        idx_result = search_coin_image_index(["grant", "2011 presidential", "ulysses"])
        if idx_result:
            obv_url = idx_result["obv"]
            src_obv = "coin_image_index"
            print(f"  ✓ Found in coin_image_index: {obv_url}")
        else:
            print("  Not in coin_image_index — falling back to Wikimedia …")
            obv_url = resolve_presidential_obverse("grant_presidential")
            src_obv = "wikimedia_commons"

    rev_url = resolve_presidential_reverse()
    GRANT_RESULT = apply_image_fix(
        ERIC_EMAIL, doc_id, "coins",
        obverse_url=obv_url,
        reverse_url=rev_url,
        obverse_src=src_obv,
        reverse_src="wikimedia_commons",
    )
    GRANT_RESULT["obv_source"] = src_obv
    print(f"  Result: {GRANT_RESULT}")
else:
    print("  Grant coin not found in Eric's collection by exact match.")
    # Broader: any 2011 presidential
    for c in eric_coins:
        if c["year"] == "2011" and c["is_presidential"]:
            grant_doc = c
            print(f"  ✓ Broader match: {c['doc_id']} {c['subject']!r}")
            break

# ═══════════════════════════════════════════════════════════════════════════
#  TASK C — Fix ALL of Eric's empty-image coins
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("TASK C: Fix ALL of Eric's empty-image coins")
print("="*70)

# Identify which coins have no images
empty_coins = [c for c in eric_coins if not c["has_obv"] and not c["has_rev"]]
print(f"\n  Eric has {len(eric_coins)} coins total, {len(empty_coins)} with NO images")

fix_stats = {"gcs": 0, "coin_image_index": 0, "wikimedia": 0, "skipped": 0, "failed": 0}
fix_log = []

def match_plan_key(coin: dict) -> str | None:
    """Match a coin to a GENERAL_WIKIMEDIA_PLAN key."""
    subj = coin["subject"].lower()
    prog = coin["program"].lower()
    denom = coin["denom"].lower()
    yr = coin["year"]

    for plan_key, plan in GENERAL_WIKIMEDIA_PLAN.items():
        kws = plan.get("keywords", [])
        yrs = plan.get("years", ["*"])
        kw_match = any(kw.lower() in subj or kw.lower() in prog or kw.lower() in denom for kw in kws)
        yr_match = ("*" in yrs) or (yr in yrs)
        if kw_match and yr_match:
            return plan_key
    return None

def get_wiki_urls_for_plan(plan_key: str) -> tuple[str | None, str | None]:
    plan = GENERAL_WIKIMEDIA_PLAN[plan_key]

    def _resolve_candidates(candidates_key, direct_key, file_key):
        """Try candidate list first, then direct URL, then file resolution."""
        # Try each pre-built candidate URL
        for url in plan.get(candidates_key, []):
            if http_head_ok(url):
                return url
            time.sleep(0.05)
        # Try direct confirmed URL
        url = plan.get(direct_key)
        if url and http_head_ok(url):
            return url
        # Try filename resolution via API
        fn = plan.get(file_key)
        if fn:
            url = resolve_wiki_filename(fn)
            time.sleep(0.15)
            if url and http_head_ok(url):
                return url
        return None

    obv_url = _resolve_candidates("obv_candidates", "obv", "obv_file")
    rev_url = _resolve_candidates("rev_candidates", "rev", "rev_file")
    return obv_url, rev_url

resolved_plan_cache: dict[str, tuple] = {}

for i, coin in enumerate(empty_coins):
    doc_id  = coin["doc_id"]
    subj    = coin["subject"]
    yr      = coin["year"]
    prog    = coin["program"]
    print(f"\n  [{i+1}/{len(empty_coins)}] {yr} {prog!r} {subj!r} ({doc_id[:12]}…)")

    obv_url = None
    rev_url = None
    src     = "none"

    # 1. GCS inventory search
    kws = [w for w in (subj + " " + prog).lower().split() if len(w) > 3]
    gcs_hit = None
    for kw in kws:
        gcs_hit = find_in_gcs_inventory([kw], yr)
        if gcs_hit:
            break
    if gcs_hit:
        obv_url = gcs_hit["public_url"]
        src = "gcs"
        print(f"    ✓ GCS hit: {obv_url[:80]}")

    # 2. coin_image_index
    if not obv_url:
        idx = search_coin_image_index(kws[:3])
        if idx:
            obv_url = idx["obv"]
            rev_url = idx["rev"]
            src = "coin_image_index"
            print(f"    ✓ Index hit: {obv_url[:80] if obv_url else 'N/A'}")

    # 3. Wikimedia via plan
    if not obv_url:
        plan_key = match_plan_key(coin)
        if plan_key:
            if plan_key not in resolved_plan_cache:
                print(f"    Resolving Wikimedia plan: {plan_key}")
                resolved_plan_cache[plan_key] = get_wiki_urls_for_plan(plan_key)
            obv_url, rev_url = resolved_plan_cache[plan_key]
            if obv_url:
                src = "wikimedia"
                print(f"    ✓ Wikimedia plan [{plan_key}]: {obv_url[:80]}")
            else:
                print(f"    ✗ Wikimedia plan [{plan_key}] — no reachable URL")

    # 4. Presidential dollar special handling
    if not obv_url and (coin.get("is_presidential") or "presidential" in prog.lower()):
        print("    Presidential dollar — trying special resolution …")
        pres_name = subj.lower().split()[-1] if subj else "unknown"
        plan_key_check = f"{pres_name}_presidential"
        pres_obv = resolve_presidential_obverse(
            "van_buren" if "van" in subj.lower() else
            "grant_presidential" if "grant" in subj.lower() else
            plan_key_check
        )
        pres_rev = resolve_presidential_reverse()
        if pres_obv:
            obv_url = pres_obv
            rev_url = pres_rev
            src = "wikimedia"

    # Apply fix
    if obv_url:
        fix_result = apply_image_fix(
            ERIC_EMAIL, doc_id, "coins",
            obverse_url=obv_url,
            reverse_url=rev_url,
        )
        fix_result["source"] = src
        fix_result["coin_year"] = yr
        fix_result["coin_subject"] = subj
        fix_log.append(fix_result)

        if src == "gcs":
            fix_stats["gcs"] += 1
        elif src == "coin_image_index":
            fix_stats["coin_image_index"] += 1
        elif src == "wikimedia":
            fix_stats["wikimedia"] += 1

        print(f"    → Applied: obv={fix_result.get('obverse')} rev={fix_result.get('reverse')} src={src}")
    else:
        fix_stats["failed"] += 1
        fix_log.append({
            "doc_id": doc_id, "coin_year": yr, "coin_subject": subj,
            "source": "none", "status": "NO_IMAGE_FOUND",
        })
        print(f"    ✗ No image found — coin remains empty")

# ═══════════════════════════════════════════════════════════════════════════
#  FINAL REPORT
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("FINAL REPORT")
print("="*70)

total_blobs = len(inventory_rows)
total_images = sum(1 for r in inventory_rows if any(r["path"].lower().endswith(e)
                   for e in [".jpg",".jpeg",".png",".gif",".webp"]))

print(f"""
[TASK A — GCS INVENTORY]
  Total blobs scanned:        {total_blobs}
  Total image files:          {total_images}
  Presidential $1 in GCS:     {len(presidential_dollars)}
  Inventory saved to:         gcs_full_inventory.csv
  Presidential JSON saved to: gcs_presidential_dollars.json

[TASK B — VAN BUREN & GRANT FIXES]
  Van Buren (2008):  {VAN_BUREN_RESULT}
  Grant (2011):      {GRANT_RESULT}

[TASK C — ERIC'S EMPTY COINS]
  Total empty coins:          {len(empty_coins)}
  Fixed from GCS:             {fix_stats['gcs']}
  Fixed from coin_image_index:{fix_stats['coin_image_index']}
  Fixed from Wikimedia:       {fix_stats['wikimedia']}
  Failed (no image found):    {fix_stats['failed']}
""")

still_empty = [c for c in fix_log if c.get("status") == "NO_IMAGE_FOUND"]
if still_empty:
    print("  Still-empty coins after run:")
    for c in still_empty:
        print(f"    {c.get('coin_year','?')} {c.get('coin_subject','?')!r} ({c.get('doc_id','')[:12]}…)")

# Save fix log
fix_log_path = os.path.join(WORKDIR, "gcs_inventory_fix_log.json")
report = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "dry_run": DRY_RUN,
    "inventory_summary": {
        "total_blobs": total_blobs,
        "total_images": total_images,
        "by_bucket": stats_by_bucket,
        "by_category": stats_by_category,
        "presidential_dollars_in_gcs": len(presidential_dollars),
    },
    "van_buren_fix": VAN_BUREN_RESULT,
    "grant_fix": GRANT_RESULT,
    "empty_coin_fixes": {
        "total_empty": len(empty_coins),
        "fixed_gcs": fix_stats["gcs"],
        "fixed_index": fix_stats["coin_image_index"],
        "fixed_wikimedia": fix_stats["wikimedia"],
        "failed": fix_stats["failed"],
        "log": fix_log,
    },
}
with open(fix_log_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, default=str)
print(f"\n  ✅ Full fix log saved → {fix_log_path}")
print("\nDone." + (" (DRY RUN — no writes performed)" if DRY_RUN else ""))
