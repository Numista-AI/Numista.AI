"""
coin_image_pipeline.py
======================
Ensures every coin in a user's Firestore collection has an image.

Priority order:
  1. Scan files already on disk (matched by year/series/mint)
  2. Existing GCS objects in the user-content bucket
  3. AI-generated image via Gemini Imagen (stored in GCS, URL saved to Firestore)

Run:
    python coin_image_pipeline.py
    python coin_image_pipeline.py --dry-run           # preview only
    python coin_image_pipeline.py --user other@email  # different account
    python coin_image_pipeline.py --generate-only     # skip scan matching, AI only
    python coin_image_pipeline.py --scans-only        # only upload existing scans
"""

import argparse
import io
import json
import mimetypes
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import google.auth
from google.cloud import firestore
from google.cloud import storage as gcs

from google import genai
from google.genai import types as genai_types

# ??? CONFIG ????????????????????????????????????????????????????????????????????
PROJECT_ID      = "studio-9101802118-8c9a8"
LOCATION        = "us-central1"
GCS_BUCKET      = "numista-uploads-studio-9101802118-8c9a8"
GCS_AI_PREFIX   = "ai_generated_coins"     # folder for AI-generated images
GCS_SCAN_PREFIX = "user_scans"             # folder for uploaded scans
TARGET_USER     = "jseaman1204@gmail.com"

# Local scan directories to search
SCAN_DIRS = [
    Path(r"C:\Users\ericd\Documents\MyVertexProject\Scans 28 JAN 2026"),
    Path(r"C:\Users\ericd\Documents\MyVertexProject\Scans AJ June 2026"),
    Path(r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images"),
    Path(r"C:\Users\ericd\Documents\MyVertexProject\new_coin_images"),
]

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".bmp"}
PDF_EXTENSION    = ".pdf"

# ??? HELPERS ???????????????????????????????????????????????????????????????????

def collect_local_scans() -> dict[str, list[Path]]:
    """
    Return all image and PDF files found in local scan directories.
    Returns dict with keys 'images' and 'pdfs'.

    NOTE: The Scans directories contain PDF binder pages (multi-coin pages),
    not individual coin photos. We handle both:
      - True image files (.jpg/.png/etc) ? upload directly
      - PDF files ? render first page to PNG via PyMuPDF, then upload
    """
    images = []
    pdfs   = []
    for d in SCAN_DIRS:
        if d.exists():
            for f in d.rglob("*"):
                if f.is_file():
                    ext = f.suffix.lower()
                    if ext in IMAGE_EXTENSIONS:
                        images.append(f)
                    elif ext == PDF_EXTENSION:
                        pdfs.append(f)
    print(f"  Found {len(images)} image files + {len(pdfs)} PDF binder pages")
    return {"images": images, "pdfs": pdfs}


def render_pdf_page_to_png(pdf_path: Path, page_index: int = 0, dpi: int = 150) -> bytes | None:
    """
    Render a single PDF page to PNG bytes using PyMuPDF (fitz).
    Returns None if PyMuPDF is not available or rendering fails.
    """
    try:
        import fitz  # PyMuPDF
        doc  = fitz.open(str(pdf_path))
        page = doc[page_index]
        mat  = fitz.Matrix(dpi / 72, dpi / 72)
        pix  = page.get_pixmap(matrix=mat)
        return pix.tobytes("png")
    except ImportError:
        print("    PyMuPDF not installed ? install with: pip install pymupdf")
        return None
    except Exception as e:
        print(f"    PDF render error: {e}")
        return None


def score_scan_match(filepath: Path, coin: dict) -> int:
    """
    Score how well a filename matches a coin record.
    Higher = better match. 0 = no match.
    """
    name = filepath.stem.lower()
    score = 0

    year = str(coin.get("Year", "")).strip()
    mint = str(coin.get("Mint Mark", "")).strip().lower()
    series = str(coin.get("Program/Series", "")).strip().lower()
    denom  = str(coin.get("Denomination", "")).strip().lower()

    # Year must match if present in filename
    if year and year in name:
        score += 10
    elif year and year not in name:
        return 0  # Year mismatch is disqualifying

    # Mint mark
    if mint and mint in name:
        score += 5

    # Series keywords
    series_words = [w for w in re.split(r'\W+', series) if len(w) > 3]
    for word in series_words:
        if word in name:
            score += 3

    # Denomination keywords
    denom_map = {
        "cent": ["cent", "penny", "lincoln", "wheat", "flying", "indian"],
        "nickel": ["nickel", "buffalo", "jefferson", "liberty"],
        "dime": ["dime", "mercury", "roosevelt", "barber"],
        "quarter": ["quarter", "washington", "state", "park", "national"],
        "half": ["half", "dollar", "kennedy", "franklin", "walker", "liberty"],
        "dollar": ["dollar", "morgan", "peace", "ike", "eisenhower", "susan",
                   "sacagawea", "presidential"],
    }
    for key, words in denom_map.items():
        if key in denom.lower():
            for w in words:
                if w in name:
                    score += 2
            break

    return score


def find_best_scan(coin: dict, all_scans: list[Path]) -> Path | None:
    """Find the best-matching scan for a coin. Returns None if no good match."""
    best_path  = None
    best_score = 0

    for scan in all_scans:
        s = score_scan_match(scan, coin)
        if s > best_score:
            best_score = s
            best_path  = scan

    # For true image files, require year + one other signal
    # For PDFs (binder pages), we can't reliably match by filename ? skip PDF matching
    if best_path and best_path.suffix.lower() == PDF_EXTENSION:
        return None  # Don't auto-match PDFs ? they're full binder pages not individual coins

    return best_path if best_score >= 12 else None


def upload_to_gcs(
    gcs_client: gcs.Client,
    local_path: Path,
    bucket_name: str,
    blob_path: str,
) -> str:
    """Upload a local file to GCS and return its public-read gs:// URL."""
    bucket  = gcs_client.bucket(bucket_name)
    blob    = bucket.blob(blob_path)
    mime, _ = mimetypes.guess_type(str(local_path))
    mime    = mime or "image/jpeg"
    blob.upload_from_filename(str(local_path), content_type=mime)
    return f"gs://{bucket_name}/{blob_path}"


def upload_bytes_to_gcs(
    gcs_client: gcs.Client,
    data: bytes,
    bucket_name: str,
    blob_path: str,
    content_type: str = "image/png",
) -> str:
    """Upload raw bytes to GCS and return gs:// URL."""
    bucket = gcs_client.bucket(bucket_name)
    blob   = bucket.blob(blob_path)
    blob.upload_from_string(data, content_type=content_type)
    return f"gs://{bucket_name}/{blob_path}"


def make_coin_image_prompt(coin: dict) -> str:
    """Build an Imagen prompt for a photorealistic coin obverse."""
    year   = coin.get("Year", "")
    series = coin.get("Program/Series", "")
    denom  = coin.get("Denomination", "")
    mint   = coin.get("Mint Mark", "")
    subj   = coin.get("Theme/Subject", "")
    cond   = coin.get("Condition", "circulated")

    wear = "lightly circulated with natural toning" if cond else "uncirculated mint state"

    prompt = (
        f"Photorealistic close-up photograph of a US {year} {series} {denom} coin, "
        f"obverse (front face) only, centered on a neutral dark gray background. "
        f"The coin shows natural copper/nickel/silver metal coloring, "
        f"{wear}. "
        f"Dramatic coin photography lighting from upper left. "
        f"Sharp focus on all design details, lettering, and relief. "
        f"No hands, no holders, no PCGS/NGC slabs. "
        f"Coin fills 85% of the frame. "
        f"High resolution numismatic reference photograph."
    )
    if subj:
        prompt += f" The reverse design features: {subj}."
    if mint:
        prompt += f" Mint mark: {mint}."

    return prompt


def generate_coin_image(client, coin: dict) -> bytes | None:
    """Generate an AI coin image using Imagen. Returns PNG bytes or None."""
    prompt = make_coin_image_prompt(coin)
    try:
        result = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt,
            config=genai_types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1",
                safety_filter_level="block_few",
                person_generation="dont_allow",
            )
        )
        if result.generated_images:
            return result.generated_images[0].image.image_bytes
        return None
    except Exception as e:
        print(f"      [AI] Generation failed: {e}")
        return None


def gcs_blob_exists(gcs_client: gcs.Client, bucket_name: str, blob_path: str) -> bool:
    """Check if a GCS blob already exists."""
    try:
        return gcs_client.bucket(bucket_name).blob(blob_path).exists()
    except Exception:
        return False


# ??? MAIN ??????????????????????????????????????????????????????????????????????

def main():
    parser = argparse.ArgumentParser(description="Fill coin image gaps for a user account")
    parser.add_argument("--user",          default=TARGET_USER, help="User email")
    parser.add_argument("--dry-run",       action="store_true",  help="Preview only")
    parser.add_argument("--generate-only", action="store_true",  help="Skip scan matching")
    parser.add_argument("--scans-only",    action="store_true",  help="Only use local scans")
    parser.add_argument("--limit",         type=int, default=0,  help="Max coins to process (0=all)")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  Numista.AI ? Coin Image Pipeline")
    print(f"  User:   {args.user}")
    print(f"  Mode:   {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"{'='*60}\n")

    # ?? Connect ???????????????????????????????????????????????????????????????
    print("Connecting to GCP...")
    credentials, _ = google.auth.default()
    db         = firestore.Client(credentials=credentials, project=PROJECT_ID)
    gcs_client = gcs.Client(credentials=credentials, project=PROJECT_ID)
    print("  Firestore + GCS connected ?")

    genai_client = None
    if not args.scans_only:
        try:
            genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
            print("  google-genai client initialized (Imagen 3 ready)")
        except Exception as e:
            print(f"  WARNING: Could not initialize google-genai client: {e}")
            print("  Will skip AI generation")

    # ?? Collect local scans ???????????????????????????????????????????????????
    all_scans = [] if args.generate_only else collect_local_scans()

    # ?? Fetch user's coins ????????????????????????????????????????????????????
    print(f"\nFetching coins for {args.user}...")
    coins_ref = db.collection("users").document(args.user).collection("coins")
    all_docs  = list(coins_ref.stream())
    print(f"  Found {len(all_docs)} coins in collection")

    # Filter to only those missing images
    needs_image = []
    for doc in all_docs:
        d = doc.to_dict()
        existing = d.get("image_url_obverse", "").strip()
        if not existing:
            needs_image.append((doc.id, d))

    print(f"  {len(needs_image)} coins need images")

    if args.limit > 0:
        needs_image = needs_image[:args.limit]
        print(f"  (Limited to {args.limit} for this run)")

    if not needs_image:
        print("\nAll coins already have images! Nothing to do.")
        return

    # ?? Process each coin ?????????????????????????????????????????????????????
    print(f"\nProcessing {len(needs_image)} coins...\n")
    stats = {"scan_matched": 0, "ai_generated": 0, "skipped": 0, "errors": 0}

    for idx, (doc_id, coin) in enumerate(needs_image, 1):
        label = (
            f"{coin.get('Year','')} "
            f"{coin.get('Program/Series','?')} "
            f"{coin.get('Mint Mark','')}"
        ).strip()
        print(f"  [{idx:3d}/{len(needs_image)}] {label}")

        gcs_url = ""
        method  = ""

        # ?? Try scan match first (true image files only) ??????????????????????
        scan_images = all_scans.get("images", []) if isinstance(all_scans, dict) else all_scans
        if scan_images and not args.generate_only:
            best_scan = find_best_scan(coin, scan_images)
            if best_scan:
                safe_name = re.sub(r'[^a-z0-9_\-]', '_', label.lower())
                blob_path = f"{GCS_SCAN_PREFIX}/{args.user}/{doc_id}_{best_scan.name}"
                print(f"    ? Scan match: {best_scan.name}")

                if not args.dry_run:
                    if not gcs_blob_exists(gcs_client, GCS_BUCKET, blob_path):
                        gcs_url = upload_to_gcs(gcs_client, best_scan, GCS_BUCKET, blob_path)
                    else:
                        gcs_url = f"gs://{GCS_BUCKET}/{blob_path}"
                else:
                    gcs_url = f"gs://{GCS_BUCKET}/{blob_path} [DRY RUN]"

                method = "scan"
                stats["scan_matched"] += 1

        # ?? Fallback: AI image generation ????????????????????????????????????
        if not gcs_url and not args.scans_only and genai_client:
            safe_name = re.sub(r'[^a-z0-9_\-]', '_', label.lower().replace(' ', '_'))
            blob_path = f"{GCS_AI_PREFIX}/{args.user}/{doc_id}_{safe_name}.png"
 
            if not args.dry_run:
                if gcs_blob_exists(gcs_client, GCS_BUCKET, blob_path):
                    gcs_url = f"gs://{GCS_BUCKET}/{blob_path}"
                    print(f"    ? AI image already in GCS (cached)")
                    method = "ai_cached"
                else:
                    print(f"    ? Generating AI image...")
                    img_bytes = generate_coin_image(genai_client, coin)
                    if img_bytes:
                        gcs_url = upload_bytes_to_gcs(
                            gcs_client, img_bytes, GCS_BUCKET, blob_path
                        )
                        print(f"    ? AI image generated and uploaded")
                        method = "ai_generated"
                        time.sleep(1)  # respect rate limits
                    else:
                        print(f"    ? Image generation failed")
                        stats["errors"] += 1
                        continue
            else:
                gcs_url = f"gs://{GCS_BUCKET}/{blob_path} [DRY RUN - would generate]"
                method  = "ai_generated"

            if method in ("ai_generated", "ai_cached"):
                stats["ai_generated"] += 1

        if not gcs_url:
            print(f"    ? No image source found, skipping")
            stats["skipped"] += 1
            continue

        # ?? Update Firestore ??????????????????????????????????????????????????
        if not args.dry_run:
            try:
                coins_ref.document(doc_id).update({
                    "image_url_obverse": gcs_url,
                    "image_source":      method,
                    "image_updated_at":  datetime.utcnow().isoformat(),
                })
            except Exception as e:
                print(f"    ERROR updating Firestore: {e}")
                stats["errors"] += 1
                continue
        else:
            print(f"    ? [DRY RUN] Would set image_url_obverse = {gcs_url}")

    # ?? Summary ???????????????????????????????????????????????????????????????
    print(f"\n{'='*60}")
    print(f"  Image Pipeline Complete!")
    print(f"  Matched from scans:   {stats['scan_matched']}")
    print(f"  AI generated:         {stats['ai_generated']}")
    print(f"  Skipped (no source):  {stats['skipped']}")
    print(f"  Errors:               {stats['errors']}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
