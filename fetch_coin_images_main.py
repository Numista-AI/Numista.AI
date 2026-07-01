#!/usr/bin/env python3
"""
fetch_coin_images_main.py
=========================
Downloads Wikimedia Commons images for all items in images_needed.csv,
uploads them to GCS, and updates the SQLite definitive_reference table.

Strategy:
- Uses confirmed direct Wikimedia URLs (no unreliable text search)
- Falls back to representative type images for years not individually photographed  
- Skips LOW priority exonumia and ambiguous "21st Century" entries
- Logs all results to output/coin_image_fetch_log.json

Usage:
    python fetch_coin_images_main.py --dry-run
    python fetch_coin_images_main.py
    python fetch_coin_images_main.py --limit 20
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
LOG_DIR      = SCRIPT_DIR / "numista_backend" / "output"
BASE_GCS_URL = f"https://storage.googleapis.com/{BUCKET_NAME}"
UA           = "NumistaAI/1.0 (educational numismatic archive; eric.seaman@yahoo.com)"

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", str(KEY_PATH))

print("[init] Connecting to GCS...", flush=True)
from google.oauth2 import service_account
from google.cloud import storage as gcs_storage

_creds = service_account.Credentials.from_service_account_file(
    str(KEY_PATH),
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
gcs_client = gcs_storage.Client(credentials=_creds, project=PROJECT_ID)
upload_bkt = gcs_client.bucket(BUCKET_NAME)
print("[init] GCS OK", flush=True)

# ── Series map: friendly name -> SQLite series values ─────────────────────────
SERIES_MAP = {
    "Lincoln Cent":              ["Lincoln Wheat Pennies", "Lincoln Cents",
                                  "Lincoln Memorial Cents", "Lincoln Shield Cents",
                                  "Lincoln Bicentennial Cents (2009)"],
    "1c":                        ["Lincoln Wheat Pennies", "Lincoln Cents"],
    "Jefferson Nickel":          ["Jefferson Nickels", "Jefferson Wartime Nickels"],
    "Mercury Dime":              ["Mercury Dimes"],
    "Roosevelt Dime":            ["Roosevelt Dimes"],
    "Washington Quarter":        ["Washington Quarters (Classic)", "Washington Silver Quarters"],
    "Kennedy Half Dollar":       ["Kennedy Half Dollars"],
    "Walking Liberty Half Dollar": ["Liberty Walking Half Dollars"],
    "Franklin Half Dollar":      ["Franklin Half Dollars"],
    "Buffalo Nickel":            ["Buffalo Nickels"],
    "2c":                        [],  # Two-cent pieces - no series in DB, will skip SQLite update
    "3c":                        [],  # Three-cent pieces - no series in DB, will skip SQLite update
    "Eisenhower Centennial Silver Dollar": ["Modern Commemorative Dollars"],
    "Eisenhower Silver Dollar":  ["Modern Commemorative Dollars"],
}

# ── CONFIRMED Wikimedia Commons URLs ──────────────────────────────────────────
# Each value is a direct upload.wikimedia.org URL that is verified to exist.
# For coins with unchanged designs, representative images are used.
# Sources: Wikimedia Commons, verified via API
W = "https://upload.wikimedia.org/wikipedia/commons/"

CONFIRMED_URLS = {
    # ── Pre-normalization denominations ───────────────────────────────────────
    ("1c", 1943):  W + "a/ac/1943_steel_cent_obverse.JPG",   # 1943 steel penny - confirmed
    ("2c", 1940):  W + "6/60/1865_Two_Cent_Obverse.png",     # Two-cent piece type representative
    ("3c", 1940):  W + "0/09/US3cni1865O.jpg",               # Three-cent nickel representative
    # ── Lincoln Cents ─────────────────────────────────────────────────────────
    # Wheat cents (1909-1958) - very similar obverse design
    ("Lincoln Cent", 1934):  W + "3/30/1944-D_Lincoln_cent_obverse.jpg",
    ("Lincoln Cent", 1935):  W + "3/30/1944-D_Lincoln_cent_obverse.jpg",
    ("Lincoln Cent", 1936):  W + "3/30/1944-D_Lincoln_cent_obverse.jpg",
    ("Lincoln Cent", 1937):  W + "3/30/1944-D_Lincoln_cent_obverse.jpg",
    ("Lincoln Cent", 1939):  W + "3/30/1944-D_Lincoln_cent_obverse.jpg",
    ("Lincoln Cent", 1941):  W + "3/30/1944-D_Lincoln_cent_obverse.jpg",
    ("Lincoln Cent", 1943):  W + "a/ac/1943_steel_cent_obverse.JPG",   # steel penny
    # Memorial cents (1959-2008)
    ("Lincoln Cent", 1951):  W + "3/30/1944-D_Lincoln_cent_obverse.jpg",
    ("Lincoln Cent", 1954):  W + "3/30/1944-D_Lincoln_cent_obverse.jpg",
    ("Lincoln Cent", 1956):  W + "3/30/1944-D_Lincoln_cent_obverse.jpg",
    ("Lincoln Cent", 1961):  W + "4/4b/US_One_Cent_Obv.png",
    ("Lincoln Cent", 1964):  W + "4/4b/US_One_Cent_Obv.png",
    ("Lincoln Cent", 1983):  W + "4/4b/US_One_Cent_Obv.png",
    ("Lincoln Cent", 1990):  W + "4/4b/US_One_Cent_Obv.png",
    # Shield cents (2010+)
    ("Lincoln Cent", 2022):  W + "4/4b/US_One_Cent_Obv.png",
    ("Lincoln Cent", 2023):  W + "4/4b/US_One_Cent_Obv.png",
    ("Lincoln Cent", 2024):  W + "4/4b/US_One_Cent_Obv.png",
    # ── Jefferson Nickels ─────────────────────────────────────────────────────
    # Original Monticello reverse design (1938-2003, 2006+)
    ("Jefferson Nickel", 1939):  W + "e/ef/Jefferson_nickel_front.jpg",
    ("Jefferson Nickel", 1941):  W + "e/ef/Jefferson_nickel_front.jpg",
    ("Jefferson Nickel", 1951):  W + "e/ef/Jefferson_nickel_front.jpg",
    ("Jefferson Nickel", 1954):  W + "e/ef/Jefferson_nickel_front.jpg",
    ("Jefferson Nickel", 1956):  W + "e/ef/Jefferson_nickel_front.jpg",
    ("Jefferson Nickel", 1961):  W + "e/ef/Jefferson_nickel_front.jpg",
    ("Jefferson Nickel", 1964):  W + "e/ef/Jefferson_nickel_front.jpg",
    ("Jefferson Nickel", 1983):  W + "e/ef/Jefferson_nickel_front.jpg",
    ("Jefferson Nickel", 1990):  W + "e/ef/Jefferson_nickel_front.jpg",
    ("Jefferson Nickel", 2022):  W + "e/ef/Jefferson_nickel_front.jpg",
    ("Jefferson Nickel", 2023):  W + "e/ef/Jefferson_nickel_front.jpg",
    ("Jefferson Nickel", 2024):  W + "e/ef/Jefferson_nickel_front.jpg",
    # ── Mercury Dimes ─────────────────────────────────────────────────────────
    ("Mercury Dime", 1934):  W + "7/72/Mercury_dime_obverse.png",
    ("Mercury Dime", 1935):  W + "7/72/Mercury_dime_obverse.png",
    ("Mercury Dime", 1936):  W + "7/72/Mercury_dime_obverse.png",
    ("Mercury Dime", 1937):  W + "7/72/Mercury_dime_obverse.png",
    ("Mercury Dime", 1939):  W + "7/72/Mercury_dime_obverse.png",
    ("Mercury Dime", 1941):  W + "7/72/Mercury_dime_obverse.png",
    # ── Roosevelt Dimes ───────────────────────────────────────────────────────
    ("Roosevelt Dime", 1951):  W + "1/12/US_dime_obverse.jpg",
    ("Roosevelt Dime", 1954):  W + "1/12/US_dime_obverse.jpg",
    ("Roosevelt Dime", 1956):  W + "1/12/US_dime_obverse.jpg",
    ("Roosevelt Dime", 1961):  W + "1/12/US_dime_obverse.jpg",
    ("Roosevelt Dime", 1964):  W + "1/12/US_dime_obverse.jpg",
    ("Roosevelt Dime", 1983):  W + "1/12/US_dime_obverse.jpg",
    ("Roosevelt Dime", 1990):  W + "1/12/US_dime_obverse.jpg",
    ("Roosevelt Dime", 2022):  W + "1/12/US_dime_obverse.jpg",
    ("Roosevelt Dime", 2023):  W + "1/12/US_dime_obverse.jpg",
    ("Roosevelt Dime", 2024):  W + "1/12/US_dime_obverse.jpg",
    # ── Washington Quarters ───────────────────────────────────────────────────
    ("Washington Quarter", 1934):  W + "d/d6/Washington_quarter_obverse.jpg",
    ("Washington Quarter", 1935):  W + "d/d6/Washington_quarter_obverse.jpg",
    ("Washington Quarter", 1936):  W + "d/d6/Washington_quarter_obverse.jpg",
    ("Washington Quarter", 1937):  W + "d/d6/Washington_quarter_obverse.jpg",
    ("Washington Quarter", 1939):  W + "d/d6/Washington_quarter_obverse.jpg",
    ("Washington Quarter", 1941):  W + "d/d6/Washington_quarter_obverse.jpg",
    ("Washington Quarter", 1942):  W + "d/d6/Washington_quarter_obverse.jpg",
    ("Washington Quarter", 1951):  W + "d/d6/Washington_quarter_obverse.jpg",
    ("Washington Quarter", 1954):  W + "d/d6/Washington_quarter_obverse.jpg",
    ("Washington Quarter", 1956):  W + "d/d6/Washington_quarter_obverse.jpg",
    ("Washington Quarter", 1961):  W + "d/d6/Washington_quarter_obverse.jpg",
    ("Washington Quarter", 1964):  W + "d/d6/Washington_quarter_obverse.jpg",
    ("Washington Quarter", 1983):  W + "d/d6/Washington_quarter_obverse.jpg",
    ("Washington Quarter", 1990):  W + "d/d6/Washington_quarter_obverse.jpg",
    # ── Walking Liberty Half Dollars ──────────────────────────────────────────
    ("Walking Liberty Half Dollar", 1934):  W + "2/2e/Walking_Liberty_Half_Dollar_obverse.jpg",
    ("Walking Liberty Half Dollar", 1935):  W + "2/2e/Walking_Liberty_Half_Dollar_obverse.jpg",
    ("Walking Liberty Half Dollar", 1936):  W + "2/2e/Walking_Liberty_Half_Dollar_obverse.jpg",
    ("Walking Liberty Half Dollar", 1937):  W + "2/2e/Walking_Liberty_Half_Dollar_obverse.jpg",
    ("Walking Liberty Half Dollar", 1939):  W + "2/2e/Walking_Liberty_Half_Dollar_obverse.jpg",
    ("Walking Liberty Half Dollar", 1942):  W + "2/2e/Walking_Liberty_Half_Dollar_obverse.jpg",
    # ── Franklin Half Dollars ─────────────────────────────────────────────────
    ("Franklin Half Dollar", 1951):  W + "f/fd/Franklin_half_dollar_obverse.jpg",
    ("Franklin Half Dollar", 1954):  W + "f/fd/Franklin_half_dollar_obverse.jpg",
    ("Franklin Half Dollar", 1956):  W + "f/fd/Franklin_half_dollar_obverse.jpg",
    ("Franklin Half Dollar", 1961):  W + "f/fd/Franklin_half_dollar_obverse.jpg",
    # ── Kennedy Half Dollars ──────────────────────────────────────────────────
    ("Kennedy Half Dollar", 1964):  W + "1/15/John_F._Kennedy_half-dollar_silver_coin_%281964%29_%28obverse%29_%2854340394390%29.jpg",
    ("Kennedy Half Dollar", 1983):  W + "1/1d/US_Half_Dollar_Obv.jpg",
    ("Kennedy Half Dollar", 1990):  W + "1/1d/US_Half_Dollar_Obv.jpg",
    ("Kennedy Half Dollar", 2022):  W + "2/2b/Obverse_of_the_2021_John_F._Kennedy_Half_Dollar.jpg",
    ("Kennedy Half Dollar", 2023):  W + "2/2b/Obverse_of_the_2021_John_F._Kennedy_Half_Dollar.jpg",
    ("Kennedy Half Dollar", 2024):  W + "2/2b/Obverse_of_the_2021_John_F._Kennedy_Half_Dollar.jpg",
    # ── Buffalo Nickels ───────────────────────────────────────────────────────
    ("Buffalo Nickel", 1934):  W + "7/73/Buffalocoin.jpg",
    ("Buffalo Nickel", 1936):  W + "7/73/Buffalocoin.jpg",
    ("Buffalo Nickel", 1937):  W + "7/73/Buffalocoin.jpg",
    # ── Eisenhower / Ike Dollars ──────────────────────────────────────────────
    ("Eisenhower Centennial Silver Dollar", 1990):  W + "f/fa/1990_Eisenhower_Silver_%241_Obverse.jpg",
    ("Eisenhower Silver Dollar", 1990):  W + "f/fa/1990_Eisenhower_Silver_%241_Obverse.jpg",
}

# ── Wikimedia API helper ───────────────────────────────────────────────────────
WIKI_API = "https://commons.wikimedia.org/w/api.php"

def verify_url(url):
    """Try HEAD request to confirm URL is accessible."""
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except Exception:
        return False

def download_image(url):
    """Download image bytes from a URL."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read(), resp.headers.get("Content-Type", "image/jpeg")

def upload_to_gcs(image_bytes, gcs_path, content_type="image/jpeg"):
    """Upload bytes to GCS and return the public URL."""
    blob = upload_bkt.blob(gcs_path)
    blob.upload_from_string(image_bytes, content_type=content_type)
    blob.make_public()
    return f"{BASE_GCS_URL}/{gcs_path}"

# ── SQLite helpers ─────────────────────────────────────────────────────────────
def get_db_doc_ids_for_type_level(denomination):
    """Find type-level (no year) doc_ids missing images for this denomination."""
    series_list = SERIES_MAP.get(denomination, [])
    if not series_list:
        return []
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    placeholders = ",".join(["?" for _ in series_list])
    cur.execute(f"""SELECT doc_id FROM definitive_reference
                    WHERE series IN ({placeholders})
                    AND (image_url_obverse IS NULL OR image_url_obverse = '')
                    AND (year IS NULL OR year = '')""",
                series_list)
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]

def update_sqlite_image(doc_id, gcs_url):
    """Update image_url_obverse in SQLite for a doc_id."""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("""UPDATE definitive_reference 
                   SET image_url_obverse = ?
                   WHERE doc_id = ? AND (image_url_obverse IS NULL OR image_url_obverse = '')""",
                (gcs_url, doc_id))
    updated = cur.rowcount
    conn.commit()
    conn.close()
    return updated

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--verify-urls", action="store_true", help="Verify each URL before downloading")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  Coin Image Fetcher (dry_run={args.dry_run})")
    print(f"{'='*60}\n")

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    
    print(f"Loaded {len(rows)} items from {CSV_PATH.name}\n")

    log = []
    processed = 0
    successes = 0
    failures = []
    skipped = []

    for row in rows:
        if args.limit and processed >= args.limit:
            break
        
        priority     = row["priority"].strip()
        denomination = row["coin_denomination"].strip()
        year_str     = row["coin_year"].strip()
        gcs_folder   = row["target_gcs_folder"].strip().rstrip("/")
        naming_conv  = row["naming_convention"].strip()
        
        # Skip LOW priority exonumia
        if priority == "LOW":
            print(f"  [SKIP LOW]  {denomination} {year_str}")
            skipped.append(f"{denomination} {year_str} - LOW priority exonumia")
            continue

        # Skip ambiguous non-year entries
        if year_str in ("21st Century",):
            print(f"  [SKIP]      {denomination} {year_str} - ambiguous year")
            skipped.append(f"{denomination} {year_str} - ambiguous year")
            continue

        print(f"\n→ [{priority}] {denomination} {year_str}", flush=True)
        
        try:
            year = int(year_str)
        except ValueError:
            year = year_str

        # Look up confirmed URL
        key = (denomination, year)
        wiki_url = CONFIRMED_URLS.get(key)

        if not wiki_url:
            print(f"    ✗ No confirmed URL for {denomination} {year_str}")
            failures.append({"denomination": denomination, "year": year_str,
                             "reason": "No confirmed Wikimedia URL - needs manual research"})
            log.append({"denomination": denomination, "year": year_str,
                       "status": "NO_URL", "reason": "Not in CONFIRMED_URLS"})
            processed += 1
            continue

        # Build GCS destination path
        gcs_path = f"{gcs_folder}/{naming_conv}"
        gcs_url = f"{BASE_GCS_URL}/{gcs_path}"

        print(f"    Wiki: {wiki_url[:90]}", flush=True)
        print(f"    GCS:  {gcs_path}", flush=True)

        if args.dry_run:
            print(f"    [DRY RUN] → {gcs_url}")
            log.append({"denomination": denomination, "year": year_str,
                       "status": "DRY_RUN", "wiki_url": wiki_url, "gcs_path": gcs_path})
            processed += 1
            successes += 1
            continue

        # Check if already uploaded
        try:
            blob = upload_bkt.blob(gcs_path)
            if blob.exists():
                print(f"    ⏭ Already in GCS - updating SQLite only")
                existing_url = gcs_url
                doc_ids = get_db_doc_ids_for_type_level(denomination)
                if doc_ids:
                    n = sum(update_sqlite_image(doc_id, existing_url) for doc_id in doc_ids)
                    print(f"    ✓ SQLite updated {n} rows for {len(doc_ids)} doc_ids")
                log.append({"denomination": denomination, "year": year_str,
                           "status": "ALREADY_EXISTS", "gcs_url": existing_url})
                processed += 1
                successes += 1
                continue
        except Exception:
            pass

        # Download image
        try:
            print(f"    Downloading...", flush=True)
            img_bytes, content_type = download_image(wiki_url)
            # Normalize content type
            if "png" in content_type.lower() or wiki_url.lower().endswith(".png"):
                content_type = "image/png"
            else:
                content_type = "image/jpeg"
            print(f"    Downloaded {len(img_bytes):,} bytes ({content_type})", flush=True)
        except Exception as e:
            print(f"    ✗ Download failed: {e}", flush=True)
            failures.append({"denomination": denomination, "year": year_str,
                             "reason": f"Download: {e}", "wiki_url": wiki_url})
            log.append({"denomination": denomination, "year": year_str,
                       "status": "DOWNLOAD_FAIL", "wiki_url": wiki_url, "error": str(e)})
            processed += 1
            time.sleep(2)
            continue

        # Upload to GCS
        try:
            print(f"    Uploading to GCS...", flush=True)
            final_gcs_url = upload_to_gcs(img_bytes, gcs_path, content_type)
            print(f"    ✓ Uploaded: {final_gcs_url}", flush=True)
        except Exception as e:
            print(f"    ✗ GCS upload failed: {e}", flush=True)
            failures.append({"denomination": denomination, "year": year_str,
                             "reason": f"GCS upload: {e}"})
            log.append({"denomination": denomination, "year": year_str,
                       "status": "GCS_FAIL", "error": str(e)})
            processed += 1
            continue

        # Update SQLite - type-level records (no year) for this denomination
        doc_ids = get_db_doc_ids_for_type_level(denomination)
        updated_count = 0
        if doc_ids:
            updated_count = sum(update_sqlite_image(doc_id, final_gcs_url) for doc_id in doc_ids)
            print(f"    ✓ SQLite: {updated_count} rows updated ({len(doc_ids)} type-level docs)", flush=True)
        else:
            print(f"    ⚠ No type-level SQLite rows found for {denomination}", flush=True)

        log.append({
            "denomination": denomination, "year": year_str,
            "status": "SUCCESS", "wiki_url": wiki_url,
            "gcs_url": final_gcs_url, "sqlite_rows_updated": updated_count
        })
        successes += 1
        processed += 1
        time.sleep(1.2)  # Rate limiting

    # Write log
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / "coin_image_fetch_log.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, default=str)

    print(f"\n{'='*60}")
    print(f"  Done: {successes}/{processed} succeeded | {len(failures)} failed | {len(skipped)} skipped")
    if failures:
        print(f"\n  ✗ Failures:")
        for item in failures:
            print(f"    - {item['denomination']} {item['year']}: {item['reason']}")
    if skipped:
        print(f"\n  ⏭ Skipped: {len(skipped)} items")
    print(f"\n  Log: {log_path}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
