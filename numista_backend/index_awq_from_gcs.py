"""
index_awq_from_gcs.py
======================
Indexes all AWQ designs from existing GCS content into coin_image_index.
Much faster than downloading from Wikimedia — uses images already in GCS.

Sources:
  - gs://numista-reference-library/reference_library/bulk_programs/american_women/
    (has all 2022-2024 designs, some 2025)
  - gs://numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/
    (has 2025 US Mint official images)

Doc format: {year}_{subject-slug}_american-women-quarters_{side}
"""
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage as gcs_storage

BACKEND_DIR = Path(__file__).parent
KEY_PATH    = BACKEND_DIR / "serviceAccountKey.json.json"
UPLOADS_BUCKET   = "numista-uploads-studio-9101802118-8c9a8"
REFERENCE_BUCKET = "numista-reference-library"
INDEX_COLLECTION = "coin_image_index"
PROGRAM = "american-women-quarters"

# ── AWQ Index Manifest ─────────────────────────────────────────────────────────
# (doc_id_suffix, side, bucket, blob_path, attribution, source_tier)
# blob_path may be URL-encoded (spaces as %20)
AWQ_INDEX_ENTRIES = [
    # ── 2022 Reverse Designs ──────────────────────────────────────────────────
    ("2022_maya-angelou",      "reverse", REFERENCE_BUCKET,
     "reference_library/bulk_programs/american_women/2022%20maya%20angelou.jpg",
     "Numista Reference Library", 2),
    ("2022_anna-may-wong",     "reverse", REFERENCE_BUCKET,
     "reference_library/bulk_programs/american_women/2022%20anna%20may%20wong.jpg",
     "Numista Reference Library", 2),
    ("2022_nina-otero-warren", "reverse", REFERENCE_BUCKET,
     "reference_library/bulk_programs/american_women/2022%20nina%20otero-warren.jpg",
     "Numista Reference Library", 2),
    ("2022_sally-ride",        "reverse", REFERENCE_BUCKET,
     "reference_library/bulk_programs/american_women/2022%20sally%20ride.jpg",
     "Numista Reference Library", 2),
    ("2022_wilma-mankiller",   "reverse", REFERENCE_BUCKET,
     "reference_library/bulk_programs/american_women/2022%20wilma%20mankiller.jpg",
     "Numista Reference Library", 2),
    # ── 2023 Reverse Designs ──────────────────────────────────────────────────
    ("2023_bessie-coleman",    "reverse", REFERENCE_BUCKET,
     "reference_library/bulk_programs/american_women/2023%20bessie%20coleman.jpg",
     "Numista Reference Library", 2),
    ("2023_edith-kanaka-ole",  "reverse", REFERENCE_BUCKET,
     "reference_library/bulk_programs/american_women/2023%20edith%20kanakaole.jpg",
     "Numista Reference Library", 2),
    ("2023_eleanor-roosevelt", "reverse", REFERENCE_BUCKET,
     "reference_library/bulk_programs/american_women/2023%20eleanor%20roosevelt.jpg",
     "Numista Reference Library", 2),
    ("2023_jovita-idar",       "reverse", REFERENCE_BUCKET,
     "reference_library/bulk_programs/american_women/2023%20jovita%20idar.jpg",
     "Numista Reference Library", 2),
    ("2023_maria-tallchief",   "reverse", REFERENCE_BUCKET,
     "reference_library/bulk_programs/american_women/2023%20maria%20tallchief.jpg",
     "Numista Reference Library", 2),
    # ── 2024 Reverse Designs ──────────────────────────────────────────────────
    # Actual 2024 AWQ designs: Patsy Mink, Celia Cruz, Zitkala-Sa,
    #                          Mary Edwards Walker, Pauli Murray
    ("2024_patsy-mink",           "reverse", REFERENCE_BUCKET,
     "reference_library/bulk_programs/american_women/2024%20patsy%20takemoto%20mink.jpg",
     "Numista Reference Library", 2),
    ("2024_celia-cruz",            "reverse", REFERENCE_BUCKET,
     "reference_library/bulk_programs/american_women/2024%20celia%20cruz.jpg",
     "Numista Reference Library", 2),
    ("2024_zitkala-sa",            "reverse", REFERENCE_BUCKET,
     "reference_library/bulk_programs/american_women/2024%20zitkala%20sa.jpg",
     "Numista Reference Library", 2),
    ("2024_mary-edwards-walker",   "reverse", REFERENCE_BUCKET,
     "reference_library/bulk_programs/american_women/2024%20mary%20edwards.jpg",
     "Numista Reference Library", 2),
    ("2024_pauli-murray",          "reverse", REFERENCE_BUCKET,
     "reference_library/bulk_programs/american_women/2024%20pauli%20murray.jpg",
     "Numista Reference Library", 2),
    # ── 2025 Reverse Designs (US Mint official + reference library) ────────────
    # Actual 2025 AWQ designs: Vera Rubin, Althea Gibson, Stacey Park Milbern,
    #                          Juliette Gordon Low, Ida B. Wells
    ("2025_vera-rubin",           "reverse", UPLOADS_BUCKET,
     "reference_images/us_mint/2025-american-women-quarters-coin-vera-rubin-uncirculated-reverse.jpg",
     "US Mint / Public Domain", 1),
    ("2025_althea-gibson",         "reverse", UPLOADS_BUCKET,
     "reference_images/us_mint/2025-american-women-quarters-coin-althea-gibson-uncirculated-reverse.jpg",
     "US Mint / Public Domain", 1),
    ("2025_stacey-park-milbern",   "reverse", UPLOADS_BUCKET,
     "reference_images/us_mint/2025-american-women-quarters-coin-stacey-park-milbern-uncirculated-reverse.jpg",
     "US Mint / Public Domain", 1),
    ("2025_juliette-gordon-low",   "reverse", UPLOADS_BUCKET,
     "reference_images/us_mint/2025-american-women-quarters-coin-juliette-gordon-low-uncirculated-reverse.jpg",
     "US Mint / Public Domain", 1),
    ("2025_ida-b-wells",           "reverse", UPLOADS_BUCKET,
     "reference_images/us_mint/2025-american-women-quarters-coin-ida-wells-uncirculated-reverse.jpg",
     "US Mint / Public Domain", 1),
    # ── Shared Obverses (Washington portrait) ─────────────────────────────────
    ("2022", "obverse", UPLOADS_BUCKET,
     "reference_images/us_mint/2022-american-women-quarters-coin-uncirculated-obverse-philadelphia.jpg",
     "US Mint / Public Domain", 1),
    ("2025", "obverse", UPLOADS_BUCKET,
     "reference_images/us_mint/2025-american-women-quarters-coin-uncirculated-obverse-philadelphia.jpg",
     "US Mint / Public Domain", 1),
]

def make_public_url(bucket_name: str, blob_path: str) -> str:
    """Build public HTTPS URL for a GCS blob. Handles URL-encoded paths."""
    from urllib.parse import unquote, quote
    decoded = unquote(blob_path)
    encoded = quote(decoded, safe='/')
    return f"https://storage.googleapis.com/{bucket_name}/{encoded}"

def resolve_blob_path(gcs_client, bucket_name: str, blob_path: str) -> str | None:
    """
    Find the actual blob path in GCS, trying both URL-encoded and decoded variants.
    GCS stores blob names with literal characters (spaces as spaces, not %20).
    Returns the actual blob name or None if not found.
    """
    from urllib.parse import unquote
    bucket = gcs_client.bucket(bucket_name)
    
    # Try 1: As-is (may be URL-encoded)
    blob = bucket.blob(blob_path)
    if blob.exists():
        return blob_path
    
    # Try 2: URL-decoded (spaces as spaces)
    decoded = unquote(blob_path)
    blob2 = bucket.blob(decoded)
    if blob2.exists():
        return decoded
    
    return None

def ensure_blob_public(gcs_client, bucket_name: str, actual_path: str) -> bool:
    """Make a blob publicly readable. Returns True on success."""
    bucket = gcs_client.bucket(bucket_name)
    blob = bucket.blob(actual_path)
    try:
        blob.make_public()
        return True
    except Exception as e:
        # May already be public or IAM-managed
        print(f"  [make_public skipped] {e}")
        return True

def init():
    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_admin.initialize_app(credentials.Certificate(str(KEY_PATH)))
    db = firestore.client()
    gcs = gcs_storage.Client.from_service_account_json(str(KEY_PATH))
    return db, gcs

def parse_doc_id(id_suffix: str) -> tuple[str, str | None]:
    """Parse '2022_maya-angelou' -> (year='2022', subject='maya-angelou')
       Parse '2022' -> (year='2022', subject=None)
    """
    parts = id_suffix.split("_", 1)
    year = parts[0]
    subject = parts[1] if len(parts) > 1 else None
    return year, subject

def index_doc(db, doc_id: str, side: str, year: str, subject: str | None,
              public_url: str, gcs_path: str, attribution: str,
              source_tier: int, dry_run: bool) -> bool:
    if dry_run:
        print(f"  [DRY RUN] {doc_id}  ({side})")
        print(f"    url: {public_url[:80]}")
        return True
    try:
        doc_ref = db.collection(INDEX_COLLECTION).document(doc_id)
        doc_ref.set({
            "year":    year,
            "mint":    None,
            "program": PROGRAM,
            "subject": subject,
            side: {
                "public_url":   public_url,
                "gcs_path":     gcs_path,
                "attribution":  attribution,
                "source_tier":  source_tier,
                "source_label": attribution.split("/")[0].strip(),
                "indexed_at":   datetime.now(timezone.utc).isoformat(),
            }
        }, merge=True)
        return True
    except Exception as e:
        print(f"  [Firestore error] {doc_id}: {e}")
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print("=" * 70)
        print("DRY RUN — no changes will be made")
        print("=" * 70)

    print("Initializing...")
    db, gcs = init()

    # Check existing docs
    print(f"\nChecking existing AWQ entries...")
    existing = set()
    for doc in db.collection(INDEX_COLLECTION).stream():
        if PROGRAM in doc.id or "american-women" in doc.id:
            existing.add(doc.id)
    print(f"  Found {len(existing)} existing AWQ docs")

    stats = {"indexed": 0, "skipped": 0, "missing_blob": 0, "errors": 0}
    indexed_years = set()

    print(f"\nProcessing {len(AWQ_INDEX_ENTRIES)} entries...")
    print("=" * 70)

    for id_suffix, side, bucket_name, blob_path, attribution, tier in AWQ_INDEX_ENTRIES:
        year, subject = parse_doc_id(id_suffix)

        if subject:
            doc_id = f"{year}_{subject}_{PROGRAM}_{side}"
        else:
            doc_id = f"{year}_{PROGRAM}_{side}"

        label = f"[{year}] {subject or '(shared obverse)'}"
        print(f"\n{label}")

        if doc_id in existing:
            print(f"  SKIP — already indexed: {doc_id}")
            stats["skipped"] += 1
            continue

        # Verify blob exists (handles URL-encoded vs decoded paths)
        actual_path = resolve_blob_path(gcs, bucket_name, blob_path)
        if actual_path is None:
            print(f"  MISSING blob: gs://{bucket_name}/{blob_path}")
            stats["missing_blob"] += 1
            continue

        public_url = make_public_url(bucket_name, actual_path)
        gcs_uri    = f"gs://{bucket_name}/{actual_path}"

        # Ensure publicly accessible
        if not args.dry_run:
            ensure_blob_public(gcs, bucket_name, actual_path)

        ok = index_doc(db, doc_id, side, year, subject,
                       public_url, gcs_uri, attribution, tier, args.dry_run)
        if ok:
            stats["indexed"] += 1
            print(f"  ✓ Indexed: {doc_id}")
            if subject:
                indexed_years.add(year)
        else:
            stats["errors"] += 1

    # ── Summary ────────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("AWQ GCS INDEXING COMPLETE")
    print("=" * 70)
    print(f"  Indexed:      {stats['indexed']}")
    print(f"  Skipped:      {stats['skipped']}")
    print(f"  Missing blob: {stats['missing_blob']}")
    print(f"  Errors:       {stats['errors']}")

    # 2024 gap check
    missing_2024 = []
    expected_2024 = ["patsy-mink", "ida-b-wells", "celia-cruz", "zitkala-sa", "miriam-slater",
                     "mary-edwards-walker", "pauli-murray"]
    for slug in expected_2024:
        doc_id = f"2024_{slug}_{PROGRAM}_reverse"
        existing_check = db.collection(INDEX_COLLECTION).document(doc_id).get()
        if not existing_check.exists:
            missing_2024.append(slug)

    if missing_2024:
        print(f"\nStill missing 2024 designs: {missing_2024}")

    print("\n2025 designs in reference library:")
    print("  vera-rubin, ida-b-wells, althea-gibson, stacey-park-milbern, juliette-gordon-low")
    print("  NOTE: These may differ from the gap report's 2025 list.")
    print("  Confirm correct slugs match AJ's coin Firestore Theme/Subject values!")

if __name__ == "__main__":
    main()
