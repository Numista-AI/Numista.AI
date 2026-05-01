"""
backfill_images.py
──────────────────
One-shot script to retroactively upload all images in verified_images/
to GCS and patch the matching Firestore coin documents with the correct
image_url_obverse / image_url_reverse URLs.

Run from numista_hardware/:
    python backfill_images.py

Safe to re-run — skips any Firestore doc that already has a URL.
"""

import os
import re
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

# ── Auth ────────────────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.abspath(os.path.join(_HERE, "..", "numista_backend", "serviceAccountKey.json.json"))

if not os.path.exists(KEY_FILE):
    logging.error(f"Service account key not found at: {KEY_FILE}")
    sys.exit(1)

import google.oauth2.service_account as sa
from google.cloud import storage, firestore

creds = sa.Credentials.from_service_account_file(KEY_FILE)
_db = firestore.Client(credentials=creds, project="studio-9101802118-8c9a8")
_gcs = storage.Client(credentials=creds)

BUCKET_NAME = "studio-9101802118-8c9a8-uploads"
USER_EMAIL  = "eric@numista.ai"
COINS_PATH  = f"users/{USER_EMAIL}/coins"
VERIFIED_DIR = os.path.join(_HERE, "verified_images")

# ── Helpers ─────────────────────────────────────────────────────────────────────
import datetime

def upload_file(local_path: str, blob_name: str) -> str | None:
    """Uploads local_path to GCS and returns the public HTTPS URL.
    
    NOTE: The bucket uses Uniform Bucket-Level Access, so objects are
    publicly readable only if the bucket has been granted allUsers:objectViewer
    via IAM. Run this once in GCP Console → Storage → bucket → Permissions:
        Add principal: allUsers, Role: Storage Object Viewer
    """
    try:
        bucket = _gcs.bucket(BUCKET_NAME)
        blob = bucket.blob(blob_name)
        blob.cache_control = "public, max-age=31536000"
        blob.upload_from_filename(local_path, content_type="image/jpeg")
        url = f"https://storage.googleapis.com/{BUCKET_NAME}/{blob_name}"
        logging.info(f"  ✅ Uploaded → {url}")
        return url
    except Exception as e:
        logging.error(f"  ❌ GCS upload failed: {e}")
        return None



def parse_filename(fname: str):
    """
    Parses a verified_images filename like:
      1963_Roosevelt_Dime_D_Obverse_20260411_1227.jpg
      2007_George_Washington_Presidential_Dollar_Reverse_20260324_1528.jpg

    Returns (slug_without_side, side_lower, timestamp) or None.
    """
    m = re.match(
        r"^(.+?)_(Obverse|Reverse)_(\d{8}_\d{4})\.jpg$", fname, re.IGNORECASE
    )
    if not m:
        return None
    slug = m.group(1)       # e.g. "1963_Roosevelt_Dime_D"
    side = m.group(2).lower()   # "obverse" | "reverse"
    ts   = m.group(3)       # "20260411_1227"
    return slug, side, ts


def slug_to_query_params(slug: str):
    """
    Extracts year + denomination keywords from the slug for a Firestore query.
    E.g. "1963_Roosevelt_Dime_D" → year=1963, denom contains "Dime"
    """
    parts = slug.split("_")
    year = parts[0] if parts and parts[0].isdigit() else None

    # Common denomination keywords
    denom_map = {
        "Cent":        ["Cent", "Penny"],
        "Nickel":      ["Nickel"],
        "Dime":        ["Dime"],
        "Quarter":     ["Quarter"],
        "Half":        ["Half"],
        "Dollar":      ["Dollar"],
    }
    matched_denom = None
    for canonical, keywords in denom_map.items():
        if any(k in parts for k in keywords):
            matched_denom = canonical
            break

    return year, matched_denom


def find_firestore_doc(year: str, denom_keyword: str | None, slug: str):
    """
    Finds the best matching coin document in Firestore.
    Strategy: match Year first, then filter client-side by Denomination.
    Returns the (doc_ref, doc_dict) tuple or (None, None).
    """
    col = _db.collection(COINS_PATH)
    query = col.where("Year", "==", year) if year else col
    docs = list(query.stream())

    if not docs:
        logging.warning(f"  No Firestore docs found for Year={year}")
        return None, None

    # Filter by denomination keyword (case-insensitive)
    if denom_keyword:
        filtered = [
            d for d in docs
            if denom_keyword.lower() in (d.to_dict().get("Denomination") or "").lower()
        ]
        if filtered:
            docs = filtered

    if len(docs) > 1:
        logging.warning(f"  Multiple matches ({len(docs)}) for slug '{slug}' — using first")

    doc = docs[0]
    return doc.reference, doc.to_dict()


# ── Main ─────────────────────────────────────────────────────────────────────────
def main():
    logging.info("=" * 60)
    logging.info("  Numista.AI Image Backfill")
    logging.info(f"  verified_images/ → gs://{BUCKET_NAME}/")
    logging.info(f"  Firestore: {COINS_PATH}")
    logging.info("=" * 60)

    if not os.path.isdir(VERIFIED_DIR):
        logging.error(f"verified_images/ not found at: {VERIFIED_DIR}")
        sys.exit(1)

    files = sorted(f for f in os.listdir(VERIFIED_DIR) if f.lower().endswith(".jpg"))
    logging.info(f"Found {len(files)} image(s) in verified_images/")

    # Group by slug so we process both sides together
    groups: dict[str, dict] = {}  # slug → {"obverse": path, "reverse": path, "ts": ts}
    for fname in files:
        parsed = parse_filename(fname)
        if not parsed:
            logging.warning(f"Skipping unrecognised filename: {fname}")
            continue
        slug, side, ts = parsed
        if slug not in groups:
            groups[slug] = {"ts": ts}
        # Keep the most recent timestamp if duplicates
        if ts > groups[slug].get("ts", ""):
            groups[slug]["ts"] = ts
        groups[slug][side] = os.path.join(VERIFIED_DIR, fname)

    uploaded = 0
    matched  = 0
    skipped  = 0
    errors   = 0

    for slug, info in groups.items():
        logging.info(f"\n── Processing: {slug}")
        year, denom_kw = slug_to_query_params(slug)
        doc_ref, doc_data = find_firestore_doc(year, denom_kw, slug)

        if doc_ref is None:
            logging.warning(f"  No Firestore match found — skipping")
            errors += 1
            continue
        matched += 1

        updates = {}

        for side in ("obverse", "reverse"):
            local_path = info.get(side)
            if not local_path or not os.path.exists(local_path):
                logging.warning(f"  No {side} image file found")
                continue

            field = f"image_url_{side}"
            existing_url = doc_data.get(field, "")

            if existing_url and existing_url.startswith("http"):
                logging.info(f"  {side}: already has URL — skipping upload")
                skipped += 1
                continue

            blob_name = f"microscope/{USER_EMAIL}/{os.path.basename(local_path)}"
            url = upload_file(local_path, blob_name)
            if url:
                updates[field] = url
                uploaded += 1
            else:
                errors += 1

        if updates:
            # Also stamp scan metadata
            updates["scan_source"] = "microscope"
            updates["scan_date"]   = info.get("ts", "")
            doc_ref.update(updates)
            logging.info(f"  ✅ Firestore updated: {list(updates.keys())}")
        else:
            logging.info(f"  No Firestore updates needed")

    logging.info("\n" + "=" * 60)
    logging.info(f"  Done!  Uploaded: {uploaded}  Matched: {matched}  Skipped: {skipped}  Errors: {errors}")
    logging.info("=" * 60)


if __name__ == "__main__":
    main()
