#!/usr/bin/env python3
"""
fetch_wikimedia_coins.py
========================
Fetches year-specific coin images from Wikimedia Commons for all items in images_needed.csv.
Downloads and uploads to GCS, then updates the SQLite definitive_reference table.

Usage:
    python fetch_wikimedia_coins.py --dry-run
    python fetch_wikimedia_coins.py
"""
import sys
import io
import os
import csv
import json
import time
import sqlite3
import urllib.request
import urllib.parse
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── Config ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).parent
KEY_PATH     = SCRIPT_DIR / "numista_backend" / "serviceAccountKey.json.json"
PROJECT_ID   = "studio-9101802118-8c9a8"
BUCKET_NAME  = "numista-uploads-studio-9101802118-8c9a8"
DB_PATH      = SCRIPT_DIR / "numista_backend" / "database" / "numista_coins.db"
CSV_PATH     = SCRIPT_DIR / "images_needed.csv"
LOG_PATH     = SCRIPT_DIR / "numista_backend" / "output" / "wikimedia_fetch_log.json"
BASE_GCS_URL = f"https://storage.googleapis.com/{BUCKET_NAME}"
UA           = "NumistaAI/1.0 (educational numismatic archive; eric.seaman@yahoo.com)"
WIKI_API     = "https://commons.wikimedia.org/w/api.php"
WIKI_UPLOAD  = "https://upload.wikimedia.org/wikipedia/commons/"

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", str(KEY_PATH))

print("[init] Importing GCS client...", flush=True)
from google.oauth2 import service_account
from google.cloud import storage as gcs_storage

_creds = service_account.Credentials.from_service_account_file(
    str(KEY_PATH),
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
gcs_client = gcs_storage.Client(credentials=_creds, project=PROJECT_ID)
upload_bkt = gcs_client.bucket(BUCKET_NAME)
print("[init] GCS OK", flush=True)

# ── Wikimedia Commons Helpers ──────────────────────────────────────────────────

def wiki_search(query, limit=10):
    """Search Wikimedia Commons for image files."""
    params = {
        "action": "query",
        "list": "search",
        "srnamespace": "6",
        "srsearch": query,
        "srlimit": limit,
        "format": "json"
    }
    url = WIKI_API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())

def wiki_resolve_filename(filename):
    """Get the direct URL for a Wikimedia Commons file by filename."""
    params = {
        "action": "query",
        "titles": f"File:{filename}",
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json"
    }
    url = WIKI_API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read())
    pages = data.get("query", {}).get("pages", {})
    for pid, page in pages.items():
        if pid != "-1":
            ii = page.get("imageinfo", [])
            if ii:
                return ii[0].get("url", "")
    return ""

def wiki_get_category_images(category, limit=50):
    """Get list of image files in a Wikimedia Commons category."""
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmtype": "file",
        "cmlimit": limit,
        "format": "json"
    }
    url = WIKI_API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read())
    members = data.get("query", {}).get("categorymembers", [])
    return [m["title"].replace("File:", "") for m in members]

def download_image(url):
    """Download image bytes from a URL."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()

def upload_to_gcs(image_bytes, gcs_path, content_type="image/jpeg"):
    """Upload bytes to GCS and return the public URL."""
    blob = upload_bkt.blob(gcs_path)
    blob.upload_from_string(image_bytes, content_type=content_type)
    try:
        blob.make_public()
    except Exception as e:
        # If UBLA is enabled, make_public() fails, but if the bucket is already public-readable,
        # the URL will still work.
        print(f"      (Note: make_public failed, likely UBLA enabled: {e})", flush=True)
    return f"{BASE_GCS_URL}/{gcs_path}"

# ── SQLite Helpers ─────────────────────────────────────────────────────────────

# Map from (friendly_name, series_keyword) pairs for lookup
SERIES_MAP = {
    "Lincoln Cent": ["Lincoln Wheat Pennies", "Lincoln Cents", "Lincoln Memorial Cents",
                     "Lincoln Shield Cents", "Lincoln Bicentennial Cents (2009)"],
    "1c": ["Lincoln Wheat Pennies", "Lincoln Cents"],  # pre-normalization alias
    "Jefferson Nickel": ["Jefferson Nickels", "Jefferson Wartime Nickels"],
    "Mercury Dime": ["Mercury Dimes"],
    "Roosevelt Dime": ["Roosevelt Dimes"],
    "Washington Quarter": ["Washington Quarters (Classic)", "Washington Silver Quarters"],
    "Kennedy Half Dollar": ["Kennedy Half Dollars"],
    "Walking Liberty Half Dollar": ["Liberty Walking Half Dollars"],
    "Franklin Half Dollar": ["Franklin Half Dollars"],
    "Buffalo Nickel": ["Buffalo Nickels"],
    "2c": ["Two-Cent Pieces"],  # pre-normalization alias
    "3c": ["Three-Cent Pieces"],  # pre-normalization alias
    "Eisenhower Centennial Silver Dollar": ["Modern Commemorative Dollars"],
    "Eisenhower Silver Dollar": ["Modern Commemorative Dollars"],
}

def get_db_doc_ids(denomination, year):
    """Find all doc_ids in SQLite that match this coin type and year."""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    
    series_list = SERIES_MAP.get(denomination, [])
    if not series_list:
        conn.close()
        return []
    
    # Try to find records matching the year
    placeholders = ",".join(["?" for _ in series_list])
    
    # Handle special cases
    if str(year).strip() in ("", "21st Century", "n/a"):
        # No year filter - get all matching series
        cur.execute(f"""SELECT doc_id FROM definitive_reference
                        WHERE series IN ({placeholders})
                        AND (image_url_obverse IS NULL OR image_url_obverse = '')""",
                    series_list)
    else:
        # Match by year - year column may be empty (type-level) or have year
        year_str = str(year).strip()
        cur.execute(f"""SELECT doc_id FROM definitive_reference
                        WHERE series IN ({placeholders})
                        AND (year = ? OR year LIKE ? OR year LIKE ?)
                        AND (image_url_obverse IS NULL OR image_url_obverse = '')""",
                    series_list + [year_str, f"{year_str}%", f"%{year_str}%"])
    
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]

def update_sqlite_image(doc_id, gcs_url):
    """Update image_url_obverse in SQLite for a doc_id."""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("""UPDATE definitive_reference 
                   SET image_url_obverse = ?
                   WHERE doc_id = ?""", (gcs_url, doc_id))
    updated = cur.rowcount
    conn.commit()
    conn.close()
    return updated

# ── Wikimedia URL Database ─────────────────────────────────────────────────────
# Pre-researched confirmed Wikimedia Commons URLs for each coin type+year.
# Format: (denomination, year) -> {'obv': url, 'search': search_term}
# We use the "thumb" API URL pattern for consistent file retrieval.

W = "https://upload.wikimedia.org/wikipedia/commons/"

WIKIMEDIA_URLS = {
    # ── HIGH Priority pre-normalization denominations ────────────────────────
    ("1c", 1943): {"search": "1943 Lincoln cent obverse", "cat": "1943 Lincoln cents"},
    ("2c", 1940): {"search": "Two cent piece 1864 obverse coin United States"},
    ("3c", 1940): {"search": "Three cent nickel obverse"},
    # ── Lincoln Wheat Cents (1909-1958) ───────────────────────────────────────
    ("Lincoln Cent", 1934): {"search": "Lincoln cent 1934 obverse", "cat": "1934 Lincoln cents"},
    ("Lincoln Cent", 1935): {"search": "Lincoln cent 1935 obverse", "cat": "1935 Lincoln cents"},
    ("Lincoln Cent", 1936): {"search": "Lincoln cent 1936 obverse", "cat": "1936 Lincoln cents"},
    ("Lincoln Cent", 1937): {"search": "Lincoln cent 1937 obverse", "cat": "1937 Lincoln cents"},
    ("Lincoln Cent", 1939): {"search": "Lincoln cent 1939 obverse", "cat": "1939 Lincoln cents"},
    ("Lincoln Cent", 1941): {"search": "Lincoln cent 1941 obverse", "cat": "1941 Lincoln cents"},
    ("Lincoln Cent", 1943): {"search": "1943 Lincoln cent obverse", "cat": "1943 Lincoln cents"},
    ("Lincoln Cent", 1951): {"search": "Lincoln cent 1951 obverse", "cat": "1951 Lincoln cents"},
    ("Lincoln Cent", 1954): {"search": "Lincoln cent 1954 obverse", "cat": "1954 Lincoln cents"},
    ("Lincoln Cent", 1956): {"search": "Lincoln cent 1956 obverse", "cat": "1956 Lincoln cents"},
    ("Lincoln Cent", 1961): {"search": "Lincoln cent 1961 obverse", "cat": "1961 Lincoln cents"},
    ("Lincoln Cent", 1964): {"search": "Lincoln cent 1964 obverse", "cat": "1964 Lincoln cents"},
    ("Lincoln Cent", 1983): {"search": "Lincoln cent 1983 obverse", "cat": "1983 Lincoln cents"},
    ("Lincoln Cent", 1990): {"search": "Lincoln cent 1990 obverse", "cat": "1990 Lincoln cents"},
    ("Lincoln Cent", 2022): {"search": "Lincoln cent 2022 obverse", "cat": "2022 Lincoln cents"},
    ("Lincoln Cent", 2023): {"search": "Lincoln cent 2023 obverse", "cat": "2023 Lincoln cents"},
    ("Lincoln Cent", 2024): {"search": "Lincoln cent 2024 obverse", "cat": "2024 Lincoln cents"},
    # ── Jefferson Nickels ─────────────────────────────────────────────────────
    ("Jefferson Nickel", 1939): {"search": "Jefferson nickel 1939 obverse", "cat": "1939 Jefferson nickels"},
    ("Jefferson Nickel", 1941): {"search": "Jefferson nickel 1941 obverse", "cat": "1941 Jefferson nickels"},
    ("Jefferson Nickel", 1951): {"search": "Jefferson nickel 1951 obverse", "cat": "1951 Jefferson nickels"},
    ("Jefferson Nickel", 1954): {"search": "Jefferson nickel 1954 obverse", "cat": "1954 Jefferson nickels"},
    ("Jefferson Nickel", 1956): {"search": "Jefferson nickel 1956 obverse", "cat": "1956 Jefferson nickels"},
    ("Jefferson Nickel", 1961): {"search": "Jefferson nickel 1961 obverse", "cat": "1961 Jefferson nickels"},
    ("Jefferson Nickel", 1964): {"search": "Jefferson nickel 1964 obverse", "cat": "1964 Jefferson nickels"},
    ("Jefferson Nickel", 1983): {"search": "Jefferson nickel 1983 obverse", "cat": "1983 Jefferson nickels"},
    ("Jefferson Nickel", 1990): {"search": "Jefferson nickel 1990 obverse", "cat": "1990 Jefferson nickels"},
    ("Jefferson Nickel", 2022): {"search": "Jefferson nickel 2022 obverse", "cat": "2022 Jefferson nickels"},
    ("Jefferson Nickel", 2023): {"search": "Jefferson nickel 2023 obverse", "cat": "2023 Jefferson nickels"},
    ("Jefferson Nickel", 2024): {"search": "Jefferson nickel 2024 obverse", "cat": "2024 Jefferson nickels"},
    # ── Mercury Dimes ─────────────────────────────────────────────────────────
    ("Mercury Dime", 1934): {"search": "Mercury dime 1934 obverse", "cat": "1934 Mercury dimes"},
    ("Mercury Dime", 1935): {"search": "Mercury dime 1935 obverse", "cat": "1935 Mercury dimes"},
    ("Mercury Dime", 1936): {"search": "Mercury dime 1936 obverse", "cat": "1936 Mercury dimes"},
    ("Mercury Dime", 1937): {"search": "Mercury dime 1937 obverse", "cat": "1937 Mercury dimes"},
    ("Mercury Dime", 1939): {"search": "Mercury dime 1939 obverse", "cat": "1939 Mercury dimes"},
    ("Mercury Dime", 1941): {"search": "Mercury dime 1941 obverse", "cat": "1941 Mercury dimes"},
    # ── Roosevelt Dimes ───────────────────────────────────────────────────────
    ("Roosevelt Dime", 1951): {"search": "Roosevelt dime 1951 obverse", "cat": "1951 Roosevelt dimes"},
    ("Roosevelt Dime", 1954): {"search": "Roosevelt dime 1954 obverse", "cat": "1954 Roosevelt dimes"},
    ("Roosevelt Dime", 1956): {"search": "Roosevelt dime 1956 obverse", "cat": "1956 Roosevelt dimes"},
    ("Roosevelt Dime", 1961): {"search": "Roosevelt dime 1961 obverse", "cat": "1961 Roosevelt dimes"},
    ("Roosevelt Dime", 1964): {"search": "Roosevelt dime 1964 obverse", "cat": "1964 Roosevelt dimes"},
    ("Roosevelt Dime", 1983): {"search": "Roosevelt dime 1983 obverse", "cat": "1983 Roosevelt dimes"},
    ("Roosevelt Dime", 1990): {"search": "Roosevelt dime 1990 obverse", "cat": "1990 Roosevelt dimes"},
    ("Roosevelt Dime", 2022): {"search": "Roosevelt dime 2022 obverse", "cat": "2022 Roosevelt dimes"},
    ("Roosevelt Dime", 2023): {"search": "Roosevelt dime 2023 obverse", "cat": "2023 Roosevelt dimes"},
    ("Roosevelt Dime", 2024): {"search": "Roosevelt dime 2024 obverse", "cat": "2024 Roosevelt dimes"},
    # ── Washington Quarters ───────────────────────────────────────────────────
    ("Washington Quarter", 1934): {"search": "Washington quarter 1934 obverse", "cat": "1934 Washington quarters"},
    ("Washington Quarter", 1935): {"search": "Washington quarter 1935 obverse", "cat": "1935 Washington quarters"},
    ("Washington Quarter", 1936): {"search": "Washington quarter 1936 obverse", "cat": "1936 Washington quarters"},
    ("Washington Quarter", 1937): {"search": "Washington quarter 1937 obverse", "cat": "1937 Washington quarters"},
    ("Washington Quarter", 1939): {"search": "Washington quarter 1939 obverse", "cat": "1939 Washington quarters"},
    ("Washington Quarter", 1941): {"search": "Washington quarter 1941 obverse", "cat": "1941 Washington quarters"},
    ("Washington Quarter", 1942): {"search": "Washington quarter 1942 obverse", "cat": "1942 Washington quarters"},
    ("Washington Quarter", 1951): {"search": "Washington quarter 1951 obverse", "cat": "1951 Washington quarters"},
    ("Washington Quarter", 1954): {"search": "Washington quarter 1954 obverse", "cat": "1954 Washington quarters"},
    ("Washington Quarter", 1956): {"search": "Washington quarter 1956 obverse", "cat": "1956 Washington quarters"},
    ("Washington Quarter", 1961): {"search": "Washington quarter 1961 obverse", "cat": "1961 Washington quarters"},
    ("Washington Quarter", 1964): {"search": "Washington quarter 1964 obverse", "cat": "1964 Washington quarters"},
    ("Washington Quarter", 1983): {"search": "Washington quarter 1983 obverse", "cat": "1983 Washington quarters"},
    ("Washington Quarter", 1990): {"search": "Washington quarter 1990 obverse", "cat": "1990 Washington quarters"},
    # ── Walking Liberty Half Dollars ──────────────────────────────────────────
    ("Walking Liberty Half Dollar", 1934): {"search": "Walking Liberty half dollar 1934 obverse", "cat": "1934 Walking Liberty half dollars"},
    ("Walking Liberty Half Dollar", 1935): {"search": "Walking Liberty half dollar 1935 obverse", "cat": "1935 Walking Liberty half dollars"},
    ("Walking Liberty Half Dollar", 1936): {"search": "Walking Liberty half dollar 1936 obverse", "cat": "1936 Walking Liberty half dollars"},
    ("Walking Liberty Half Dollar", 1937): {"search": "Walking Liberty half dollar 1937 obverse", "cat": "1937 Walking Liberty half dollars"},
    ("Walking Liberty Half Dollar", 1939): {"search": "Walking Liberty half dollar 1939 obverse", "cat": "1939 Walking Liberty half dollars"},
    ("Walking Liberty Half Dollar", 1942): {"search": "Walking Liberty half dollar 1942 obverse", "cat": "1942 Walking Liberty half dollars"},
    # ── Franklin Half Dollars ─────────────────────────────────────────────────
    ("Franklin Half Dollar", 1951): {"search": "Franklin half dollar 1951 obverse", "cat": "1951 Franklin half dollars"},
    ("Franklin Half Dollar", 1954): {"search": "Franklin half dollar 1954 obverse", "cat": "1954 Franklin half dollars"},
    ("Franklin Half Dollar", 1956): {"search": "Franklin half dollar 1956 obverse", "cat": "1956 Franklin half dollars"},
    ("Franklin Half Dollar", 1961): {"search": "Franklin half dollar 1961 obverse", "cat": "1961 Franklin half dollars"},
    # ── Kennedy Half Dollars ──────────────────────────────────────────────────
    ("Kennedy Half Dollar", 1964): {"search": "Kennedy half dollar 1964 obverse", "cat": "1964 Kennedy half dollars"},
    ("Kennedy Half Dollar", 1983): {"search": "Kennedy half dollar 1983 obverse", "cat": "1983 Kennedy half dollars"},
    ("Kennedy Half Dollar", 1990): {"search": "Kennedy half dollar 1990 obverse", "cat": "1990 Kennedy half dollars"},
    ("Kennedy Half Dollar", 2022): {"search": "Kennedy half dollar 2022 obverse", "cat": "2022 Kennedy half dollars"},
    ("Kennedy Half Dollar", 2023): {"search": "Kennedy half dollar 2023 obverse", "cat": "2023 Kennedy half dollars"},
    ("Kennedy Half Dollar", 2024): {"search": "Kennedy half dollar 2024 obverse", "cat": "2024 Kennedy half dollars"},
    # ── Buffalo Nickels ───────────────────────────────────────────────────────
    ("Buffalo Nickel", 1934): {"search": "Buffalo nickel 1934 obverse", "cat": "1934 Buffalo nickels"},
    ("Buffalo Nickel", 1936): {"search": "Buffalo nickel 1936 obverse", "cat": "1936 Buffalo nickels"},
    ("Buffalo Nickel", 1937): {"search": "Buffalo nickel 1937 obverse", "cat": "1937 Buffalo nickels"},
    # ── Eisenhower / Ike Dollar ───────────────────────────────────────────────
    ("Eisenhower Centennial Silver Dollar", 1990): {"search": "Eisenhower centennial silver dollar 1990"},
    ("Eisenhower Silver Dollar", 1990): {"search": "Eisenhower dollar obverse 1971"},
    ("Silver Commemorative", 1942): {"search": "Walking Liberty half dollar 1942 obverse"},
    ("Silver Commemorative Medal/Coin", 1942): {"search": "Walking Liberty half dollar 1942 obverse"},
}

def find_best_image_url(denomination, year):
    """
    Try to find the best Wikimedia Commons image for a given coin type + year.
    Returns (url, filename) or (None, None).
    """
    key = (denomination, int(year)) if str(year).strip().isdigit() else (denomination, year)
    entry = WIKIMEDIA_URLS.get(key)
    if not entry:
        return None, None
    
    # 1. Try searching by category first
    if "cat" in entry:
        try:
            files = wiki_get_category_images(entry["cat"], limit=30)
            # Filter to jpg/png images
            files = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png"))]
            # Filter out non-coin images (e.g. paintings, medals, etc.)
            files = [f for f in files if not any(w in f.lower() for w in ["hadrian", "filarete", "painting", "statue", "medal", "sculpture"])]
            if files:
                # Prefer images with "obverse" or "front" in name
                preferred = [f for f in files if any(w in f.lower() for w in ["obverse", "front", "obv"])]
                candidate = preferred[0] if preferred else imgs[0]
                url = wiki_resolve_filename(candidate)
                if url:
                    print(f"      ✓ Category hit: {candidate[:80]}", flush=True)
                    return url, candidate
        except Exception as e:
            print(f"      ⚠ Category lookup failed: {e}", flush=True)
        time.sleep(0.3)
    
    # 2. Fall back to search
    search_term = entry.get("search", f"{year} {denomination} coin obverse")
    try:
        results = wiki_search(search_term, limit=15)
        hits = results.get("query", {}).get("search", [])
        for hit in hits:
            title = hit.get("title", "")
            if title.lower().startswith("file:") and title.lower().endswith((".jpg", ".jpeg", ".png")):
                filename = title.replace("File:", "").replace("file:", "")
                url = wiki_resolve_filename(filename)
                if url:
                    print(f"      ✓ Search hit: {filename[:80]}", flush=True)
                    return url, filename
    except Exception as e:
        print(f"      ⚠ Search failed: {e}", flush=True)
    
    return None, None


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  Wikimedia Coin Image Fetcher  (dry_run={args.dry_run})")
    print(f"{'='*60}\n")

    # Read the CSV
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Loaded {len(rows)} items from {CSV_PATH.name}\n")

    log = []
    processed = 0
    successes = 0
    failures = []

    for row in rows:
        if args.limit and processed >= args.limit:
            break
        
        priority    = row["priority"].strip()
        denomination = row["coin_denomination"].strip()
        year_str    = row["coin_year"].strip()
        gcs_folder  = row["target_gcs_folder"].strip().rstrip("/")
        naming_conv = row["naming_convention"].strip()
        
        # Skip LOW priority exonumia for now
        if priority == "LOW":
            print(f"  [SKIP LOW] {denomination} {year_str} - exonumia placeholder")
            continue

        # Skip "21st Century" ambiguous entries 
        if year_str in ("21st Century",):
            print(f"  [SKIP] {denomination} {year_str} - ambiguous year, manual handling needed")
            continue
        
        print(f"\n→ [{priority}] {denomination} {year_str}", flush=True)
        
        # Try to convert year
        try:
            year = int(year_str)
        except ValueError:
            year = year_str

        # 1. Find Wikimedia URL
        print(f"    Searching Wikimedia Commons...", flush=True)
        img_url, img_filename = find_best_image_url(denomination, year)
        time.sleep(5)  # Be nice to Wikimedia API
        
        if not img_url:
            print(f"    ✗ No image found for {denomination} {year_str}", flush=True)
            failures.append({"denomination": denomination, "year": year_str, "reason": "No Wikimedia image found"})
            log.append({"denomination": denomination, "year": year_str, "status": "FAILED", "reason": "No Wikimedia image"})
            processed += 1
            continue

        # 2. Build GCS destination path
        gcs_path = f"{gcs_folder}/{naming_conv}"
        gcs_url = f"{BASE_GCS_URL}/{gcs_path}"
        
        print(f"    Source: {img_url[:90]}", flush=True)
        print(f"    GCS dest: {gcs_path}", flush=True)
        
        if args.dry_run:
            print(f"    [DRY RUN] Would upload to: {gcs_url}", flush=True)
            log.append({"denomination": denomination, "year": year_str, "status": "DRY_RUN",
                        "wiki_url": img_url, "gcs_path": gcs_path})
            processed += 1
            successes += 1
            continue
        
        # 3. Download image
        try:
            print(f"    Downloading image...", flush=True)
            img_bytes = download_image(img_url)
            print(f"    Downloaded {len(img_bytes):,} bytes", flush=True)
        except Exception as e:
            print(f"    ✗ Download failed: {e}", flush=True)
            failures.append({"denomination": denomination, "year": year_str, "reason": f"Download failed: {e}"})
            log.append({"denomination": denomination, "year": year_str, "status": "FAILED", "reason": f"Download: {e}"})
            processed += 1
            continue
        
        # 4. Upload to GCS
        try:
            content_type = "image/jpeg" if img_url.lower().endswith((".jpg", ".jpeg")) else "image/png"
            print(f"    Uploading to GCS...", flush=True)
            gcs_url = upload_to_gcs(img_bytes, gcs_path, content_type)
            print(f"    ✓ Uploaded: {gcs_url}", flush=True)
        except Exception as e:
            print(f"    ✗ GCS upload failed: {e}", flush=True)
            failures.append({"denomination": denomination, "year": year_str, "reason": f"GCS upload failed: {e}"})
            log.append({"denomination": denomination, "year": year_str, "status": "FAILED", "reason": f"GCS: {e}"})
            processed += 1
            continue
        
        # 5. Update SQLite
        doc_ids = get_db_doc_ids(denomination, year_str)
        if doc_ids:
            updated_count = 0
            for doc_id in doc_ids:
                n = update_sqlite_image(doc_id, gcs_url)
                updated_count += n
            print(f"    ✓ Updated {updated_count} SQLite row(s) for {len(doc_ids)} doc_id(s)", flush=True)
        else:
            print(f"    ⚠ No SQLite rows found for {denomination} {year_str} (type-level only)", flush=True)
        
        log.append({
            "denomination": denomination, "year": year_str, "status": "SUCCESS",
            "wiki_url": img_url, "gcs_url": gcs_url, "doc_ids_updated": doc_ids
        })
        successes += 1
        processed += 1
        time.sleep(1.0)  # Rate limiting between uploads

    # ── Write log ──────────────────────────────────────────────────────────────
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, default=str)

    print(f"\n{'='*60}")
    print(f"  Run complete:")
    print(f"  Total processed: {processed}")
    print(f"  Successes: {successes}")
    print(f"  Failures: {len(failures)}")
    if failures:
        print(f"\n  Failed items:")
        for item in failures:
            print(f"    - {item['denomination']} {item['year']}: {item['reason']}")
    print(f"\n  Log written to: {LOG_PATH}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
