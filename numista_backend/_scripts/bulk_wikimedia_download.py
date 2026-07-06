# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
bulk_wikimedia_download.py  (v2 — thumbnail API, batched requests, backoff)

Uses iiurlwidth=1200 to get Wikimedia thumbnail URLs (CDN-served, no rate limits)
instead of full-size direct downloads. Batches imageinfo calls 50 at a time.
Backs off 30s on any 429.
"""

import requests
import re
import time
import os
import google.auth
from google.cloud import storage

# ── GCS Config ────────────────────────────────────────────────────────
GCS_BUCKET  = "numista-reference-library"
GCS_PREFIX  = "reference_library/wikimedia_uscoin/"
API_URL     = "https://commons.wikimedia.org/w/api.php"
THUMB_WIDTH = 1200  # px — large enough for reference quality

# ── Categories to scan ────────────────────────────────────────────────
CATEGORIES = [
    # (wikimedia_category,          gcs_subfolder,          max_files)
    ("Lincoln_cent",                "Lincoln_cents",         500),
    ("Eisenhower_dollar",           "Eisenhower_dollars",    200),
    ("Peace_dollar",                "Peace_dollars",         200),
    ("Franklin_half_dollar",        "Franklin_half_dollars", 200),
    ("Barber_dime",                 "Barber_coinage",        200),
    ("Barber_quarter",              "Barber_coinage",        200),
    ("Barber_half_dollar",          "Barber_coinage",        200),
    ("Mercury_dimes",               "Mercury_dimes",         300),
    ("Buffalo_nickels",             "Buffalo_nickels",       300),
    ("Morgan_dollar",               "Morgan_dollars",        200),
    ("Walking_Liberty_half_dollar", "Walking_liberty",       200),
    ("Indian_Head_cent",            "Indian_head_cents",     200),
    ("2021_Morgan_dollar",          "Morgan_dollars",        100),
    ("2022_Morgan_dollar",          "Morgan_dollars",        100),
]

# ── Side / year detection ─────────────────────────────────────────────
OBV_RE  = re.compile(r"\bobv|obverse|front|left\b|anv|avers", re.I)
REV_RE  = re.compile(r"\brev|reverse|back|right\b|revers", re.I)
YEAR_RE = re.compile(r"\b(1[89]\d{2}|20[012]\d)\b")
IMG_EXT = {".jpg", ".jpeg", ".png", ".gif"}

def detect_side(name):
    n = name.lower()
    if OBV_RE.search(n): return "obverse"
    if REV_RE.search(n): return "reverse"
    return None

def detect_year(name):
    m = YEAR_RE.search(name)
    return m.group(1) if m else None

# ── HTTP session ──────────────────────────────────────────────────────
SES = requests.Session()
SES.headers["User-Agent"] = "NumistaAI/1.0 (numista-vault.web.app; bot)"

def api_get(backoff=30, **params):
    params.setdefault("format", "json")
    for attempt in range(4):
        try:
            r = SES.get(API_URL, params=params, timeout=30)
            if r.status_code == 429:
                wait = backoff * (2 ** attempt)
                print(f"  [429] Rate limited. Waiting {wait}s...", flush=True)
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json()
        except requests.HTTPError:
            raise
        except Exception as e:
            print(f"  [WARN] API error ({attempt+1}/4): {e}", flush=True)
            time.sleep(5 * (attempt + 1))
    return {}

def download_url(url, backoff=30):
    for attempt in range(4):
        try:
            r = SES.get(url, timeout=60)
            if r.status_code == 429:
                wait = backoff * (2 ** attempt)
                print(f"  [429] Rate limited on download. Waiting {wait}s...", flush=True)
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.content
        except requests.HTTPError:
            raise
        except Exception as e:
            print(f"  [WARN] Download error ({attempt+1}/4): {e}", flush=True)
            time.sleep(5 * (attempt + 1))
    return None

# ── Category member enumeration ───────────────────────────────────────
def get_category_files(category, limit=500):
    files = []
    cont = {}
    while len(files) < limit:
        data = api_get(
            action="query", list="categorymembers",
            cmtitle=f"Category:{category}", cmtype="file",
            cmlimit=min(limit - len(files), 500),
            **cont,
        )
        members = data.get("query", {}).get("categorymembers", [])
        files.extend(m["title"] for m in members)
        if "continue" not in data:
            break
        cont = data["continue"]
        time.sleep(0.5)
    return files

# ── Batched imageinfo (thumbnail URLs) ───────────────────────────────
def get_thumb_urls(titles, width=THUMB_WIDTH):
    """Return {title: thumb_url} for a batch of ≤50 titles."""
    result = {}
    data = api_get(
        action="query",
        titles="|".join(titles),
        prop="imageinfo",
        iiprop="url",
        iiurlwidth=width,
    )
    for page in data.get("query", {}).get("pages", {}).values():
        title = page.get("title", "")
        ii_list = page.get("imageinfo", [{}])
        if ii_list:
            ii = ii_list[0]
            # Prefer thumburl (CDN); fall back to url for small originals
            url = ii.get("thumburl") or ii.get("url", "")
            size = ii.get("thumbwidth", 0) or ii.get("size", 0)
            if url:
                result[title] = url
    time.sleep(0.3)
    return result

# ── GCS ───────────────────────────────────────────────────────────────
creds, _ = google.auth.default()
gcs = storage.Client(credentials=creds)
bucket = gcs.bucket(GCS_BUCKET)

# Pre-load existing blob names for fast exists-check
print("Pre-loading existing GCS blobs for dedup...", flush=True)
existing = {b.name for b in bucket.list_blobs(prefix=GCS_PREFIX)}
print(f"  {len(existing)} files already in GCS under {GCS_PREFIX}", flush=True)

def upload(blob_path, data, ct="image/jpeg"):
    blob = bucket.blob(blob_path)
    blob.upload_from_string(data, content_type=ct)
    existing.add(blob_path)

# ── Main ──────────────────────────────────────────────────────────────
total_uploaded = 0
total_skipped_exists = 0
total_skipped_no_meta = 0
total_failed = 0

print("\n" + "=" * 65, flush=True)
print("BULK WIKIMEDIA DOWNLOADER  (v2 — thumbnail API)", flush=True)
print("=" * 65, flush=True)

for category, subfolder, max_files in CATEGORIES:
    print(f"\n📂 Category:{category} → {subfolder}", flush=True)
    titles = get_category_files(category, limit=max_files)
    # Filter to image files only
    titles = [t for t in titles
              if os.path.splitext(t.replace("File:", "").lower())[1] in IMG_EXT]
    print(f"  {len(titles)} image files found", flush=True)

    cat_up = 0
    # Process in batches of 50 (API limit for titles|)
    BATCH = 50
    for i in range(0, len(titles), BATCH):
        batch = titles[i:i+BATCH]

        # Build GCS paths first to skip existing quickly
        to_fetch = {}
        for title in batch:
            filename = title.replace("File:", "").strip()
            ext = os.path.splitext(filename)[1].lower()
            safe = re.sub(r"[^\w.\-]", "_", filename)
            blob_path = f"{GCS_PREFIX}{subfolder}/{safe}"
            if blob_path in existing:
                total_skipped_exists += 1
                continue

            side = detect_side(os.path.splitext(filename)[0])
            year = detect_year(filename)
            if not side or not year:
                total_skipped_no_meta += 1
                continue

            to_fetch[title] = (blob_path, ext)

        if not to_fetch:
            continue

        # Batch imageinfo request
        thumb_map = get_thumb_urls(list(to_fetch.keys()))

        # Download and upload
        for title, (blob_path, ext) in to_fetch.items():
            url = thumb_map.get(title)
            if not url:
                total_skipped_no_meta += 1
                continue

            data = download_url(url)
            if not data:
                total_failed += 1
                continue

            ct = "image/png" if ext == ".png" else "image/jpeg"
            upload(blob_path, data, ct)
            total_uploaded += 1
            cat_up += 1
            time.sleep(1.2)  # stay polite to Wikimedia CDN

    print(f"  ✓ {cat_up} new images uploaded", flush=True)

print("\n" + "=" * 65, flush=True)
print("COMPLETE", flush=True)
print(f"  Uploaded     : {total_uploaded}", flush=True)
print(f"  Already exist: {total_skipped_exists}", flush=True)
print(f"  No year/side : {total_skipped_no_meta}", flush=True)
print(f"  Failed       : {total_failed}", flush=True)
print("=" * 65, flush=True)
