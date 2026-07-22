"""
ingest_semiq_manual_images.py
==============================
Direct ingest of manually-downloaded Semiquincentennial coin images.

These files follow the Wikimedia SemiQ-* naming convention, so we can
map them to doc_ids deterministically ? no fuzzy matching needed.

Usage:
    .venv\Scripts\python.exe ingest_semiq_manual_images.py --dry-run
    .venv\Scripts\python.exe ingest_semiq_manual_images.py
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from numista_scraper.url_scraper import download_and_upload, commit_coin, SEMIQ_COINS, _make_doc_id
from numista_scraper.storage import db, gcs_client, BUCKET_NAME, update_coin_images_in_databases
from numista_scraper.config import DB_PATH

# --- Source folder -------------------------------------------------------------
SRC_DIR = Path("C:/Users/ericd/Documents/MyVertexProject/Manual downloaded Coin Images/US Mint/HighRes_Scrape")
ATTRIBUTION = "United States Mint. Public domain (17 U.S.C. ? 105). Source: usmint.gov"
GCS_PREFIX  = "coins/"
PUBLIC_BASE = f"https://storage.googleapis.com/{BUCKET_NAME}/"

# --- Deterministic filename -> (doc_id_slug, side, mints) mapping --------------
# Key = stem pattern (case-insensitive prefix match on filename)
# Value = (coin slug from SEMIQ_COINS, side, list of mints this shared image covers)
# "shared" images (no mint suffix) apply to BOTH P and D mints.
FILE_MAP = {
    # Quarters
    "SemiQ-Mayflower-Obverse-Unc-D":         ("mayflower_compact",           "obverse", ["D"]),
    "SemiQ-Mayflower-Obverse-Unc-P":         ("mayflower_compact",           "obverse", ["P"]),
    "SemiQ-Mayflower-Reverse-Unc":           ("mayflower_compact",           "reverse", ["P", "D"]),
    "SemiQ-Revolutionary-War-Obverse-Unc-D": ("revolutionary_war",           "obverse", ["D"]),
    "SemiQ-Revolutionary-War-Obverse-Unc-P": ("revolutionary_war",           "obverse", ["P"]),
    "SemiQ-Revolutionary-War-Reverse-Unc":   ("revolutionary_war",           "reverse", ["P", "D"]),
    "SemiQ-Declaration-Obverse-Unc-P":       ("declaration_of_independence", "obverse", ["P", "D"]),
    "SemiQ-Declaration-Obverse-Unc-D":       ("declaration_of_independence", "obverse", ["D"]),
    "SemiQ-Declaration-Reverse-Unc":         ("declaration_of_independence", "reverse", ["P", "D"]),
    "SemiQ-Constitution-Obverse-Unc-D":      ("us_constitution",             "obverse", ["P", "D"]),
    "SemiQ-Constitution-Obverse-Unc-P":      ("us_constitution",             "obverse", ["P"]),
    "SemiQ-Constitution-Reverse-Unc":        ("us_constitution",             "reverse", ["P", "D"]),
    "SemiQ-Gettysburg-Obverse-Unc-P":        ("gettysburg_address",          "obverse", ["P", "D"]),
    "SemiQ-Gettysburg-Obverse-Unc-D":        ("gettysburg_address",          "obverse", ["D"]),
    "SemiQ-Gettysburg-Reverse-Unc":          ("gettysburg_address",          "reverse", ["P", "D"]),
    # Half Dollar
    "SemiQ-Half-Dollar-Obverse-Unc-P":       ("enduring_liberty_half_dollar","obverse", ["P", "D"]),
    "SemiQ-Half-Dollar-Obverse-Unc-D":       ("enduring_liberty_half_dollar","obverse", ["D"]),
    "SemiQ-Half-Dollar-Reverse-Unc":         ("enduring_liberty_half_dollar","reverse", ["P", "D"]),
    # Dime
    "SemiQ-Dime-Obverse-Unc-D":             ("emerging_liberty_dime",       "obverse", ["P", "D"]),
    "SemiQ-Dime-Obverse-Unc-P":             ("emerging_liberty_dime",       "obverse", ["P"]),
    "SemiQ-Dime-Reverse-Unc":               ("emerging_liberty_dime",       "reverse", ["P", "D"]),
    # Nickel
    "SemiQ-Nickel-Obverse-Unc-D":           ("jefferson_nickel_semiquincentennial","obverse", ["P", "D"]),
    "SemiQ-Nickel-Obverse-Unc-P":           ("jefferson_nickel_semiquincentennial","obverse", ["P"]),
    "SemiQ-Nickel-Reverse-Unc":             ("jefferson_nickel_semiquincentennial","reverse", ["P", "D"]),
    # Penny
    "SemiQ-Penny-Obverse-Unc-D":            ("lincoln_cent_semiquincentennial","obverse", ["D"]),
    "SemiQ-Penny-Obverse-Unc-P":            ("lincoln_cent_semiquincentennial","obverse", ["P"]),
    "SemiQ-Penny-Reverse-Unc":              ("lincoln_cent_semiquincentennial","reverse", ["P", "D"]),
    # Native American Dollar
    "native-american-1-unc-reverse":         ("native_american_dollar_polly_cooper","reverse", ["P", "D"]),
    "Sacagawea_dollar_obverse":              ("native_american_dollar_polly_cooper","obverse", ["P", "D"]),
}

# Build slug -> coin_def lookup
_SLUG_TO_DEF = {c["slug"]: c for c in SEMIQ_COINS}


def upload_local_file(filepath: Path, gcs_path: str, dry_run: bool) -> str | None:
    """Upload a local file directly to GCS. Returns public URL."""
    ext = filepath.suffix.lower()
    ct  = {"jpg": "image/jpeg", ".jpg": "image/jpeg",
           ".jpeg": "image/jpeg", ".png": "image/png",
           ".webp": "image/webp"}.get(ext, "image/jpeg")
    public_url = f"{PUBLIC_BASE}{gcs_path}"

    if dry_run:
        print(f"    [DRY-RUN] Would upload {filepath.name} -> gs://{BUCKET_NAME}/{gcs_path}")
        return public_url

    try:
        data = filepath.read_bytes()
        bucket = gcs_client.bucket(BUCKET_NAME)
        blob   = bucket.blob(gcs_path)
        blob.upload_from_string(data, content_type=ct)
        blob.metadata = {
            "attribution": ATTRIBUTION,
            "source":      "usmint_manual",
            "license":     "public_domain_us_government",
            "copyright":   "Public Domain",
        }
        blob.patch()
        try:
            blob.make_public()
        except Exception:
            pass
        print(f"    [GCS] [OK] Uploaded -> {gcs_path}")
        return public_url
    except Exception as e:
        print(f"    !! GCS upload error: {e}")
        return None


def update_firestore_image(doc_id: str, side: str, url: str, dry_run: bool):
    """Update Firestore and SQLite with the new image URL."""
    field = f"image_url_{side}"
    if dry_run:
        print(f"    [DRY-RUN] Would update Firestore {doc_id} -> {field} = {url[:60]}...")
        return
    try:
        db.collection("definitive_reference").document(doc_id).update({field: url})
        print(f"    [Firestore] [OK] Updated {doc_id}.{field}")
    except Exception as e:
        print(f"    !! Firestore error for {doc_id}: {e}")

    # SQLite
    try:
        import sqlite3
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute(f"UPDATE definitive_reference SET {field} = ? WHERE doc_id = ?", (url, doc_id))
        conn.commit()
        conn.close()
        print(f"    [SQLite]    [OK] Updated {doc_id}.{field}")
    except Exception as e:
        print(f"    !! SQLite error for {doc_id}: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    mode = "DRY-RUN" if args.dry_run else "LIVE"
    print(f"\n[SOURCE] {SRC_DIR}")
    print(f"   Mode: {mode}\n")

    files = [f for f in SRC_DIR.iterdir() if f.is_file() and f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")]
    print(f"Found {len(files)} image files.")
    print()

    uploaded = 0
    skipped  = 0
    unmatched = []

    for filepath in sorted(files):
        stem = filepath.stem  # filename without extension

        # Find matching entry in FILE_MAP (case-insensitive)
        match_key = next((k for k in FILE_MAP if k.lower() == stem.lower()), None)
        if not match_key:
            print(f"!!  Unrecognized filename: {filepath.name} ? skipping")
            unmatched.append(filepath.name)
            continue

        coin_slug, side, mints = FILE_MAP[match_key]
        coin_def = _SLUG_TO_DEF.get(coin_slug)
        if not coin_def:
            print(f"!!  No coin definition for slug '{coin_slug}' ? skipping {filepath.name}")
            continue

        print(f"-- {filepath.name}")
        print(f"   -> {coin_def['denomination']} {coin_def['variety']} | {side.upper()} | mints: {mints}")

        for mint in mints:
            doc_id  = _make_doc_id(coin_def, mint)
            gcs_key = f"{GCS_PREFIX}{doc_id}_{side}{filepath.suffix.lower()}"

            # Check if already exists in Firestore
            if not args.dry_run:
                try:
                    snap = db.collection("definitive_reference").document(doc_id).get()
                    existing = snap.to_dict() or {} if snap.exists else {}
                    already  = existing.get(f"image_url_{side}", "")
                    if already and "storage.googleapis.com" in already:
                        print(f"    [SKIP] {doc_id} already has {side} image ? use --force to overwrite")
                        skipped += 1
                        continue
                except Exception:
                    existing = {}

            url = upload_local_file(filepath, gcs_key, args.dry_run)
            if url:
                update_firestore_image(doc_id, side, url, args.dry_run)
                uploaded += 1

        print()

    print("=" * 60)
    print("INGEST SUMMARY")
    print("=" * 60)
    print(f"  Uploaded + updated : {uploaded}")
    print(f"  Skipped (exists)   : {skipped}")
    print(f"  Unmatched files    : {len(unmatched)}")
    if unmatched:
        print("  Unmatched:")
        for f in unmatched:
            print(f"    {f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
