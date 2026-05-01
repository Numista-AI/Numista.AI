"""
upload_reference_library.py — Numista.AI Reference Library Ingestion
=====================================================================
Uploads all 3 Kaggle coin datasets to GCS and indexes them in Firestore.

Usage:
    python upload_reference_library.py [--dry-run] [--limit N]

What it does:
  1. Walks all image files in each dataset folder
  2. Parses denomination, year, side (obverse/reverse) from filenames
  3. Uploads to GCS under:  gs://[BUCKET]/reference_library/[source]/[filename]
  4. Creates a Firestore document in:  reference_library/{image_id}
  5. Saves attribution metadata with every document

Firestore schema per image:
  {
    "image_id":    string,       # unique hash
    "gcs_url":     string,       # public GCS URL
    "source":      string,       # dataset slug
    "attribution": string,       # human-readable credit line
    "license":     string,       # dataset license
    "category":    string,       # folder name / coin type
    "denomination": string,      # parsed: cent, dime, quarter, etc.
    "year":        int|None,     # parsed from filename if possible
    "side":        string,       # "obverse" | "reverse" | "unknown"
    "filename":    string,       # original filename
    "uploaded_at": timestamp,
    "tags":        list[str],    # searchable tags
  }
"""

import os
import re
import hashlib
import logging
import argparse
import mimetypes
from pathlib import Path
from dotenv import load_dotenv
from google.cloud import storage, firestore

load_dotenv()

# ─── Configuration ─────────────────────────────────────────────────────────────
GCS_BUCKET          = "numista-reference-library"   # dedicated; separate from us_mint_coin_images
FIRESTORE_COLLECTION = "reference_library"
USER_EMAIL          = "eric@numista.ai"

KAGGLE_CACHE = Path(r"C:\Users\ericd\.cache\kagglehub\datasets")

# ─── Dataset Registry ──────────────────────────────────────────────────────────
# All licensed sources with proper attribution metadata
DATASETS = [
    {
        "slug":        "kaggerator/us-coins-subset-from-wikimedia",
        "version":     "5",
        "source_name": "US Coins Subset from Wikimedia",
        "attribution": "kaggerator via Kaggle; original images from Wikimedia Commons contributors",
        "license":     "CC BY-SA (Wikimedia Commons)",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "kaggle_url":  "https://www.kaggle.com/datasets/kaggerator/us-coins-subset-from-wikimedia",
        "source_key":  "wikimedia_uscoin",
    },
    {
        "slug":        "balabaskar/count-coins-image-dataset",
        "version":     "1",
        "source_name": "Count Coins Image Dataset",
        "attribution": "balabaskar via Kaggle",
        "license":     "Unknown / Kaggle dataset terms",
        "license_url": "https://www.kaggle.com/datasets/balabaskar/count-coins-image-dataset",
        "kaggle_url":  "https://www.kaggle.com/datasets/balabaskar/count-coins-image-dataset",
        "source_key":  "balabaskar_coins",
    },
    {
        "slug":        "jaronfralick/rare-us-coin-image-dataset",
        "version":     "1",
        "source_name": "Rare US Coin Image Dataset",
        "attribution": "jaronfralick via Kaggle",
        "license":     "Unknown / Kaggle dataset terms",
        "license_url": "https://www.kaggle.com/datasets/jaronfralick/rare-us-coin-image-dataset",
        "kaggle_url":  "https://www.kaggle.com/datasets/jaronfralick/rare-us-coin-image-dataset",
        "source_key":  "rare_uscoin",
    },
]

# ─── Denomination Parser ───────────────────────────────────────────────────────
_DENOM_RULES = [
    (r'\bsilver.?eagle\b',           'Silver Eagle'),
    (r'\bgold.?eagle\b',             'Gold Eagle'),
    (r'\bmorgan\b',                  'Morgan Dollar'),
    (r'\bpeace.?dollar\b',           'Peace Dollar'),
    (r'\bsacagawea\b',               'Sacagawea Dollar'),
    (r'\bpresidential.?dollar\b',    'Presidential Dollar'),
    (r'\beisenhower\b',              'Eisenhower Dollar'),
    (r'\bsusan.?b.?anthony\b',       'SBA Dollar'),
    (r'\bdollar\b|\b\$1\b',           'Dollar'),
    (r'\bwalking.?liberty\b',        'Walking Liberty Half'),
    (r'\bfranklin.?half\b',          'Franklin Half Dollar'),
    (r'\bkennedy\b',                 'Kennedy Half Dollar'),
    (r'\bhalf.?dollar\b|\b50.?cent\b','Half Dollar'),
    (r'\bwashington.?quarter\b',     'Washington Quarter'),
    (r'\bstate.?quarter\b',          'State Quarter'),
    (r'\bquarter\b|\b25.?cent\b',    'Quarter'),
    (r'\bmerc\b|\bmercury\b',        'Mercury Dime'),
    (r'\broosevelt\b',               'Roosevelt Dime'),
    (r'\bdime\b|\b10.?cent\b',       'Dime'),
    (r'\bjefferson\b',               'Jefferson Nickel'),
    (r'\bnickel\b|\b5.?cent\b',      'Nickel'),
    (r'\blincoln\b|\bwheat\b',       'Lincoln Cent'),
    (r'\bcent\b|\bpenny\b|\b1.?cent\b','Cent'),
]

def _parse_denomination(text: str) -> str:
    text = text.lower().replace('_', ' ').replace('-', ' ')
    for pattern, label in _DENOM_RULES:
        if re.search(pattern, text, re.IGNORECASE):
            return label
    return 'Unknown'

def _parse_year(text: str) -> int | None:
    # Look for 4-digit year between 1792 and 2030
    matches = re.findall(r'\b(1[789]\d{2}|20[012]\d)\b', text)
    return int(matches[0]) if matches else None

def _parse_side(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ['obverse', 'obv', 'heads', 'front', 'avers']):
        return 'obverse'
    if any(w in t for w in ['reverse', 'rev', 'tails', 'back', 'revers']):
        return 'reverse'
    return 'unknown'

def _parse_tags(folder: str, filename: str, denomination: str) -> list:
    tags = []
    combined = f"{folder} {filename}".lower().replace('_', ' ')
    if denomination != 'Unknown':
        tags.append(denomination.lower())
    if 'silver' in combined:  tags.append('silver')
    if 'gold'   in combined:  tags.append('gold')
    if 'proof'  in combined:  tags.append('proof')
    if 'mint'   in combined:  tags.append('mint-state')
    if 'error'  in combined:  tags.append('error-coin')
    if 'rare'   in combined:  tags.append('rare')
    return list(set(tags))

def _image_id(source_key: str, rel_path: str) -> str:
    raw = f"{source_key}:{rel_path}"
    return hashlib.md5(raw.encode()).hexdigest()

# ─── GCS + Firestore clients ───────────────────────────────────────────────────
def _get_gcs():
    return storage.Client()

def _get_db():
    return firestore.Client()

# ─── Main Upload Loop ──────────────────────────────────────────────────────────
VALID_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.tif', '.tiff'}

def upload_dataset(ds: dict, gcs_client, db, dry_run: bool, limit: int):
    dataset_path = (
        KAGGLE_CACHE
        / ds["slug"]
        / "versions"
        / ds["version"]
    )

    if not dataset_path.exists():
        logging.error(f"[SKIP] Dataset not found locally: {dataset_path}")
        return 0, 0

    bucket = gcs_client.bucket(GCS_BUCKET) if not dry_run else None
    coll   = db.collection(FIRESTORE_COLLECTION) if not dry_run else None

    uploaded = 0
    skipped  = 0
    image_files = [
        f for f in dataset_path.rglob('*')
        if f.is_file() and f.suffix.lower() in VALID_EXTS
    ]

    if limit:
        image_files = image_files[:limit]

    logging.info(f"[{ds['source_key']}] Found {len(image_files)} images in {dataset_path}")

    for img_path in image_files:
        try:
            rel      = img_path.relative_to(dataset_path)
            category = rel.parts[0] if len(rel.parts) > 1 else 'uncategorized'
            filename = img_path.name
            stem     = img_path.stem

            image_id   = _image_id(ds["source_key"], str(rel))
            gcs_dest   = f"reference_library/{ds['source_key']}/{rel.as_posix()}"
            gcs_url    = f"https://storage.googleapis.com/{GCS_BUCKET}/{gcs_dest}"
            denom      = _parse_denomination(f"{category} {stem}")
            # If filename alone didn't yield a result, try folder name as hint
            if denom == 'Unknown':
                denom = _parse_denomination(category)
            year       = _parse_year(stem) or _parse_year(category)
            side       = _parse_side(stem)
            tags       = _parse_tags(category, stem, denom)
            mime, _    = mimetypes.guess_type(filename)

            doc = {
                "image_id":    image_id,
                "gcs_url":     gcs_url,
                "gcs_path":    gcs_dest,
                "source":      ds["source_key"],
                "source_name": ds["source_name"],
                "attribution": ds["attribution"],
                "license":     ds["license"],
                "license_url": ds["license_url"],
                "kaggle_url":  ds["kaggle_url"],
                "category":    category,
                "denomination": denom,
                "year":        year,
                "side":        side,
                "filename":    filename,
                "tags":        tags,
                "uploaded_at": firestore.SERVER_TIMESTAMP,
            }

            if dry_run:
                logging.info(f"  [DRY RUN] Would upload → {gcs_dest}  ({denom}, {year}, {side})")
                uploaded += 1
                continue

            # Upload to GCS
            blob = bucket.blob(gcs_dest)
            if blob.exists():
                skipped += 1
                continue
            blob.upload_from_filename(str(img_path), content_type=mime or 'image/jpeg')

            # Write Firestore doc
            coll.document(image_id).set(doc, merge=True)
            uploaded += 1

            if uploaded % 100 == 0:
                logging.info(f"  [{ds['source_key']}] {uploaded} uploaded so far...")

        except Exception as e:
            logging.error(f"  [ERROR] {img_path}: {e}")

    return uploaded, skipped


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s  %(levelname)s  %(message)s',
        datefmt='%H:%M:%S',
    )

    parser = argparse.ArgumentParser(description='Upload Numista.AI reference image library')
    parser.add_argument('--dry-run', action='store_true',
                        help='Parse and log without uploading to GCS/Firestore')
    parser.add_argument('--limit', type=int, default=0,
                        help='Max images per dataset (0 = all)')
    parser.add_argument('--source', type=str, default='',
                        help='Only upload this source_key (e.g. wikimedia_uscoin)')
    args = parser.parse_args()

    if args.dry_run:
        logging.info('DRY RUN MODE — nothing will be uploaded')
        gcs = None
        db  = None
    else:
        gcs = _get_gcs()
        db  = _get_db()

    total_up = 0
    total_sk = 0

    for ds in DATASETS:
        if args.source and ds['source_key'] != args.source:
            continue
        logging.info(f"\n{'='*60}")
        logging.info(f"Dataset : {ds['source_name']}")
        logging.info(f"Credit  : {ds['attribution']}")
        logging.info(f"License : {ds['license']}")
        logging.info(f"{'='*60}")
        up, sk = upload_dataset(ds, gcs, db, args.dry_run, args.limit)
        logging.info(f"  Uploaded: {up}  |  Skipped (already exists): {sk}")
        total_up += up
        total_sk += sk

    logging.info(f"\n{'='*60}")
    logging.info(f"TOTAL UPLOADED : {total_up}")
    logging.info(f"TOTAL SKIPPED  : {total_sk}")
    logging.info(f"{'='*60}")


if __name__ == '__main__':
    main()
