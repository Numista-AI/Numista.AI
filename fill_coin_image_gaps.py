#!/usr/bin/env python3
"""
fill_coin_image_gaps.py
=======================
Fills image gaps from images_needed.csv by:
1. Copying reference images from numista-reference-library GCS bucket 
   to the numista-uploads bucket at the correct target paths
2. Falling back to Wikimedia Commons for images not already in GCS
3. Updating the SQLite definitive_reference table with resulting GCS URLs

Usage:
    python fill_coin_image_gaps.py --dry-run
    python fill_coin_image_gaps.py
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
SCRIPT_DIR     = Path(__file__).parent
KEY_PATH       = SCRIPT_DIR / "numista_backend" / "serviceAccountKey.json.json"
PROJECT_ID     = "studio-9101802118-8c9a8"
UPLOAD_BUCKET  = "numista-uploads-studio-9101802118-8c9a8"
REF_BUCKET     = "numista-reference-library"
DB_PATH        = SCRIPT_DIR / "numista_backend" / "database" / "numista_coins.db"
CSV_PATH       = SCRIPT_DIR / "images_needed.csv"
LOG_DIR        = SCRIPT_DIR / "numista_backend" / "output"
UPLOAD_BASE    = f"https://storage.googleapis.com/{UPLOAD_BUCKET}"
UA             = "NumistaAI/1.0 (educational numismatic archive; eric.seaman@yahoo.com)"

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", str(KEY_PATH))

print("[init] Connecting to GCS...", flush=True)
from google.oauth2 import service_account
from google.cloud import storage as gcs_storage

_creds = service_account.Credentials.from_service_account_file(
    str(KEY_PATH),
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
gcs = gcs_storage.Client(credentials=_creds, project=PROJECT_ID)
upload_bkt = gcs.bucket(UPLOAD_BUCKET)
ref_bkt    = gcs.bucket(REF_BUCKET)
print("[init] GCS OK", flush=True)

# ── Source image map: coin type -> GCS reference path in numista-reference-library ──
# These are already in GCS - just need to be copied to the target location
REF_LIB_BASE = "reference_library/wikimedia_uscoin"

SOURCE_IMAGES = {
    # Lincoln Cents (wheat/memorial/shield - same obverse portrait)
    "Lincoln Cent": f"{REF_LIB_BASE}/United_States_cents/Lincoln_cents/Lincoln_Shield_cent/2018-S_proof_Lincoln_cent_obverse__28deep_cameo_29.jpg",
    "1c": f"{REF_LIB_BASE}/United_States_cents/Lincoln_cents/Lincoln_Shield_cent/2018-S_proof_Lincoln_cent_obverse__28deep_cameo_29.jpg",

    # Jefferson Nickels
    "Jefferson Nickel": f"{REF_LIB_BASE}/United_States_nickels/Jefferson_nickel/Jefferson-Nickel-Unc-Obv.jpg",

    # Mercury Dimes
    "Mercury Dime": f"{REF_LIB_BASE}/United_States_dimes/Mercury_dimes/1942-Mercury-Dime-Obverse.jpg",

    # Roosevelt Dimes
    "Roosevelt Dime": f"{REF_LIB_BASE}/United_States_dimes/Roosevelt_dimes/United_States_dime_2C_obverse_2C_2002.jpg",

    # Washington Quarters (silver / classic)
    "Washington Quarter": f"{REF_LIB_BASE}/United_States_quarters/Washington_quarter/Obverses_of_Washington_quarters/1932_Washington_quarter_obverse.jpg",

    # Walking Liberty Half Dollars
    "Walking Liberty Half Dollar": f"{REF_LIB_BASE}/Half_dollar__United_States_/Walking_Liberty_half_dollars/1941_U.S._half_dollar_obverse.png",

    # Franklin Half Dollars
    "Franklin Half Dollar": f"{REF_LIB_BASE}/Half_dollar__United_States_/Franklin_half_dollar/Franklin_HalfObverse.jpg",

    # Kennedy Half Dollars
    "Kennedy Half Dollar": f"{REF_LIB_BASE}/Half_dollar__United_States_/Kennedy_half_dollar/US_Half_Dollar_Obverse_2015.png",

    # Buffalo Nickels
    "Buffalo Nickel": f"{REF_LIB_BASE}/United_States_nickels/Buffalo_nickels/Indian_Head_Buffalo_Obverse.jpg",

    # Eisenhower Centennial Silver Dollar (1990 commemorative)
    "Eisenhower Centennial Silver Dollar": f"{REF_LIB_BASE}/Dollar_coins_of_the_United_States/Commemorative_United_States_dollar_coins/Commemorative_silver_dollars_of_the_United_States/Eisenhower_Centennial_silver_dollar/1990_Eisenhower_Silver__241_Obverse.jpg",
    "Eisenhower Silver Dollar": f"{REF_LIB_BASE}/Dollar_coins_of_the_United_States/Commemorative_United_States_dollar_coins/Commemorative_silver_dollars_of_the_United_States/Eisenhower_Centennial_silver_dollar/1990_Eisenhower_Silver__241_Obverse.jpg",
}

# Wikimedia Commons fallback URLs (confirmed working)
WIKI_FALLBACKS = {
    "1c": "https://upload.wikimedia.org/wikipedia/commons/a/ac/1943_steel_cent_obverse.JPG",
    "2c": "https://upload.wikimedia.org/wikipedia/commons/6/60/1865_Two_Cent_Obverse.png",
}

# ── Series map: coin name -> SQLite series values ──────────────────────────────
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
    "Eisenhower Centennial Silver Dollar": ["Modern Commemorative Dollars"],
    "Eisenhower Silver Dollar":  ["Modern Commemorative Dollars"],
    "2c": [],  # Two-cent pieces - not in DB series
    "3c": [],  # Three-cent pieces - not in DB series
}

# ── GCS helpers ───────────────────────────────────────────────────────────────

def copy_from_ref_library(ref_path, dest_path):
    """Copy a blob from numista-reference-library to numista-uploads.
    Returns (public_url, error_message) or (url, None) on success.
    """
    src_blob = ref_bkt.blob(ref_path)
    if not src_blob.exists():
        return None, f"Source blob not found: {ref_path}"
    
    dest_blob = upload_bkt.blob(dest_path)
    # Server-side copy (rewrite)
    token = None
    while True:
        token, bytes_rewritten, total_bytes = dest_blob.rewrite(src_blob, token=token)
        if token is None:
            break
    
    # Don't call make_public() -- bucket uses uniform bucket-level access (IAM)
    # The bucket is already configured for public read via IAM policy
    return f"{UPLOAD_BASE}/{dest_path}", None

def download_and_upload(url, dest_path):
    """Download from URL and upload to upload bucket.
    Does NOT call make_public() -- bucket uses IAM-based public access.
    """
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        img_bytes = resp.read()
        content_type = resp.headers.get("Content-Type", "image/jpeg")
    
    if "png" in content_type.lower() or url.lower().endswith(".png"):
        content_type = "image/png"
    else:
        content_type = "image/jpeg"
    
    blob = upload_bkt.blob(dest_path)
    blob.upload_from_string(img_bytes, content_type=content_type)
    # No make_public() -- IAM-based public access at bucket level
    return f"{UPLOAD_BASE}/{dest_path}"

# ── SQLite helper ─────────────────────────────────────────────────────────────

def update_sqlite_image_gaps(denomination, gcs_url):
    """Update all image-gap rows in SQLite for a given denomination's series."""
    series_list = SERIES_MAP.get(denomination, [])
    if not series_list:
        return 0
    
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    placeholders = ",".join(["?" for _ in series_list])
    
    # Update ALL matching type-level docs that still have no image
    cur.execute(f"""UPDATE definitive_reference
                    SET image_url_obverse = ?
                    WHERE series IN ({placeholders})
                    AND (image_url_obverse IS NULL OR image_url_obverse = '')""",
                [gcs_url] + series_list)
    updated = cur.rowcount
    conn.commit()
    conn.close()
    return updated

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    print(f"\n{'='*65}")
    print(f"  Coin Image Gap Filler  (dry_run={args.dry_run})")
    print(f"{'='*65}\n")

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    
    print(f"Loaded {len(rows)} items from images_needed.csv\n")

    log = []
    processed = skipped = successes = 0
    failures = []
    
    # Track which denominations have already been sourced (avoid re-downloading same source)
    already_copied = {}  # denomination -> gcs_url

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
            skipped += 1
            continue
        
        # Skip ambiguous years
        if year_str in ("21st Century",):
            print(f"  [SKIP]      {denomination} {year_str} - ambiguous year")
            skipped += 1
            continue

        dest_path = f"{gcs_folder}/{naming_conv}"
        dest_url  = f"{UPLOAD_BASE}/{dest_path}"
        
        print(f"\n→ [{priority}] {denomination} {year_str}", flush=True)
        print(f"    GCS dest: {dest_path}", flush=True)

        if args.dry_run:
            source_ref = SOURCE_IMAGES.get(denomination)
            fallback   = WIKI_FALLBACKS.get(denomination)
            if source_ref:
                print(f"    [DRY RUN] Would copy: {REF_BUCKET}/{source_ref}")
            elif fallback:
                print(f"    [DRY RUN] Would download: {fallback}")
            else:
                print(f"    [DRY RUN] NO SOURCE FOUND")
            processed += 1
            successes += 1
            log.append({"denomination": denomination, "year": year_str,
                       "status": "DRY_RUN", "dest": dest_path})
            continue

        # Check if dest already exists in upload bucket
        try:
            dest_blob = upload_bkt.blob(dest_path)
            if dest_blob.exists():
                print(f"    ⏭ Already exists at dest, updating SQLite only")
                rows_updated = update_sqlite_image_gaps(denomination, dest_url)
                print(f"    ✓ SQLite: {rows_updated} rows updated")
                log.append({"denomination": denomination, "year": year_str,
                           "status": "ALREADY_EXISTS", "gcs_url": dest_url,
                           "sqlite_rows": rows_updated})
                processed += 1
                successes += 1
                continue
        except Exception:
            pass

        # Try GCS reference library copy first
        source_ref = SOURCE_IMAGES.get(denomination)
        gcs_url = None
        
        if source_ref:
            try:
                print(f"    Copying from ref-library: {source_ref[-60:]}", flush=True)
                gcs_url, err = copy_from_ref_library(source_ref, dest_path)
                if err:
                    print(f"    ⚠ Ref-lib copy failed: {err}", flush=True)
                    gcs_url = None
                else:
                    print(f"    ✓ Copied to: {gcs_url}", flush=True)
            except Exception as e:
                print(f"    ⚠ Ref-lib copy exception: {e}", flush=True)
                gcs_url = None
        
        # Try Wikimedia fallback
        if not gcs_url:
            fallback_url = WIKI_FALLBACKS.get(denomination)
            if fallback_url:
                try:
                    print(f"    Downloading from Wikimedia: {fallback_url[-60:]}", flush=True)
                    gcs_url = download_and_upload(fallback_url, dest_path)
                    print(f"    ✓ Uploaded: {gcs_url}", flush=True)
                except Exception as e:
                    print(f"    ✗ Wikimedia download failed: {e}", flush=True)
        
        if not gcs_url:
            print(f"    ✗ No source found for {denomination}", flush=True)
            failures.append({"denomination": denomination, "year": year_str,
                             "reason": "No source image available"})
            log.append({"denomination": denomination, "year": year_str,
                       "status": "NO_SOURCE"})
            processed += 1
            continue

        # Update SQLite
        rows_updated = update_sqlite_image_gaps(denomination, gcs_url)
        if rows_updated:
            print(f"    ✓ SQLite: {rows_updated} rows updated for '{denomination}'", flush=True)
        else:
            print(f"    ⚠ No SQLite rows updated (may already have images or series not matched)", flush=True)
        
        log.append({"denomination": denomination, "year": year_str,
                   "status": "SUCCESS", "gcs_url": gcs_url,
                   "sqlite_rows_updated": rows_updated})
        successes += 1
        processed += 1
        time.sleep(0.5)

    # Write log
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / "coin_image_gap_fill_log.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, default=str)

    print(f"\n{'='*65}")
    print(f"  Results: {successes} succeeded / {len(failures)} failed / {skipped} skipped")
    print(f"  Total processed: {processed}")
    if failures:
        print(f"\n  ✗ Failures:")
        for item in failures:
            print(f"    - {item['denomination']} {item['year']}: {item['reason']}")
    print(f"\n  Log written to: {log_path}")
    print(f"{'='*65}\n")

if __name__ == "__main__":
    main()
