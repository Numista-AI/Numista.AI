"""
index_awq_into_coin_image_index.py
====================================
Sources AWQ (American Women Quarters) coin images from Wikimedia Commons
and indexes them into the coin_image_index Firestore collection so that
CoinImageService can serve them to ALL users automatically.

Key format written:
  {year}_{subject-slug}_american-women-quarters_{side}
  e.g. 2022_maya-angelou_american-women-quarters_reverse

Doc structure matches existing coin_image_index schema exactly.

Also writes a shared obverse per year (generic Washington portrait):
  {year}_american-women-quarters_obverse
"""
import re
import sys
import time
import requests
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

# Force UTF-8 for special characters like Kanakaʻole
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage as gcs_storage

# ── Config ────────────────────────────────────────────────────────────────────
BACKEND_DIR = Path(__file__).parent
KEY_PATH    = BACKEND_DIR / "serviceAccountKey.json.json"
STORAGE_BUCKET = "numista-uploads-studio-9101802118-8c9a8"
INDEX_COLLECTION = "coin_image_index"
PROGRAM = "american-women-quarters"
TEMP_DIR = BACKEND_DIR / "temp_awq_index"

WIKIMEDIA_API = "https://commons.wikimedia.org/w/api.php"
WIKIMEDIA_DELAY = 4.0  # seconds between API calls
WIKIMEDIA_HEADERS = {
    "User-Agent": "NumistaApp/1.0 (numista-ai-project; image-indexing-bot) python-requests"
}

# Known Wikimedia Commons filenames discovered in search sessions
# These bypass the search API entirely — direct URL lookups are more reliable
KNOWN_WIKIMEDIA_FILES = {
    # 2022
    "maya-angelou":      "American Women Quarter 2022 Maya Angelou.jpg",
    "sally-ride":        "2022 Dr. Sally Ride Womens Quarter.jpg",
    "wilma-mankiller":   "2022 Wilma Mankiller Womens Quarter.jpg",
    "nina-otero-warren": "2022 Nina Otero-Warren Womens Quarter.jpg",
    "anna-may-wong":     "American Women Quarter 2022 Anna May Wong.jpg",
    # 2023
    "bessie-coleman":    "2023 Bessie Coleman Womens Quarter.jpg",
    "edith-kanaka-ole":  "2023 Edith Kanaka\u02BBole Womens Quarter.jpg",  # with okina
    "eleanor-roosevelt": "2023 Eleanor Roosevelt Womens Quarter.jpg",
    # 2024
    "celia-cruz":        "2024 Celia Cruz Womens Quarter.jpg",
    "zitkala-sa":        "2024 Zitkala-Sa Womens Quarter.jpg",
    "patsy-mink":        "Patsy Mink Quarter Pour April 2024.jpg",
}

# ── All AWQ designs (2022–2025 official program) ──────────────────────────────
# Format: (year, subject_slug, display_name, search_queries)
AWQ_DESIGNS = [
    # 2022
    (2022, "maya-angelou",      "Maya Angelou",
     ["American Women Quarter 2022 Maya Angelou", "2022 Maya Angelou quarter"]),
    (2022, "sally-ride",        "Sally Ride",
     ["2022 Dr. Sally Ride Womens Quarter", "2022 Sally Ride quarter"]),
    (2022, "wilma-mankiller",   "Wilma Mankiller",
     ["2022 Wilma Mankiller Womens Quarter", "2022 Wilma Mankiller quarter"]),
    (2022, "nina-otero-warren", "Nina Otero-Warren",
     ["2022 Nina Otero-Warren Womens Quarter", "nina otero-warren quarter 2022"]),
    (2022, "anna-may-wong",     "Anna May Wong",
     ["American Women Quarter 2022 Anna May Wong", "anna may wong quarter 2022",
      "anna mae wong quarter 2022"]),  # both spellings
    # 2023
    (2023, "bessie-coleman",    "Bessie Coleman",
     ["2023 Bessie Coleman Womens Quarter", "2023 Bessie Coleman quarter"]),
    (2023, "edith-kanaka-ole",  "Edith Kanakaʻole",
     ["2023 Edith Kanakaole Womens Quarter", "edith kanaka ole quarter 2023",
      "edith kanakaole quarter"]),
    (2023, "eleanor-roosevelt", "Eleanor Roosevelt",
     ["2023 Eleanor Roosevelt Womens Quarter", "2023 Eleanor Roosevelt quarter"]),
    (2023, "jovita-idar",       "Jovita Idar",
     ["2023 Jovita Idar Womens Quarter", "2023 Jovita Idar quarter"]),
    (2023, "maria-tallchief",   "Maria Tallchief",
     ["2023 Maria Tallchief Womens Quarter", "2023 Maria Tallchief quarter"]),
    # 2024
    (2024, "patsy-mink",        "Patsy Mink",
     ["2024 Patsy Mink Womens Quarter", "2024 Patsy Mink quarter"]),
    (2024, "ida-b-wells",       "Ida B. Wells",
     ["2024 Ida B Wells Womens Quarter", "ida b wells quarter 2024"]),
    (2024, "celia-cruz",        "Celia Cruz",
     ["2024 Celia Cruz Womens Quarter", "2024 Celia Cruz quarter"]),
    (2024, "zitkala-sa",        "Zitkala-Ša",
     ["2024 Zitkala-Sa Womens Quarter", "zitkala sa quarter 2024", "2024 zitkala quarter"]),
    (2024, "miriam-slater",     "Miriam Slater",
     ["2024 Miriam Slater Womens Quarter", "2024 Miriam Slater quarter"]),
    # 2025
    (2025, "vera-rubin",        "Vera Rubin",
     ["2025 Vera Rubin Womens Quarter", "2025 Vera Rubin quarter"]),
    (2025, "stagecoach-mary",   "Stagecoach Mary Fields",
     ["2025 Stagecoach Mary quarter", "2025 Mary Fields quarter"]),
    (2025, "harriet-tubman",    "Harriet Tubman",
     ["2025 Harriet Tubman Womens Quarter", "2025 Harriet Tubman quarter"]),
    (2025, "ada-lovelace",      "Ada Lovelace",
     ["2025 Ada Lovelace Womens Quarter", "2025 Ada Lovelace quarter"]),
    (2025, "susan-la-flesche",  "Susan La Flesche Picotte",
     ["2025 Susan La Flesche Womens Quarter", "2025 Susan La Flesche quarter"]),
]

# Known obverse URL (shared Washington portrait for all AWQ coins)
# Already indexed as 2022_american-women-quarters_obverse — reuse that URL
AWQ_OBVERSE_FALLBACK = (
    "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/"
    "reference_images/us_mint/2022-american-women-quarters-coin-uncirculated-obverse-philadelphia.jpg"
)

# ── Firebase init ──────────────────────────────────────────────────────────────
def init():
    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_admin.initialize_app(credentials.Certificate(str(KEY_PATH)))
    db = firestore.client()
    gcs = gcs_storage.Client.from_service_account_json(str(KEY_PATH))
    bucket = gcs.bucket(STORAGE_BUCKET)
    return db, bucket

# ── Wikimedia helpers ──────────────────────────────────────────────────────────
_last_wiki_call = 0.0

def wikimedia_search(query: str) -> list[dict]:
    global _last_wiki_call
    elapsed = time.time() - _last_wiki_call
    if elapsed < WIKIMEDIA_DELAY:
        time.sleep(WIKIMEDIA_DELAY - elapsed)
    _last_wiki_call = time.time()
    params = {
        "action": "query", "list": "search",
        "srsearch": query, "srnamespace": 6,
        "srlimit": 10, "format": "json",
    }
    try:
        r = requests.get(WIKIMEDIA_API, params=params,
                         headers=WIKIMEDIA_HEADERS, timeout=15)
        r.raise_for_status()
        return r.json().get("query", {}).get("search", [])
    except Exception as e:
        print(f"  [Wikimedia search error] {e}")
        return []

def wikimedia_get_url(filename: str) -> str | None:
    """Get the direct image URL for a Wikimedia Commons filename."""
    global _last_wiki_call
    elapsed = time.time() - _last_wiki_call
    if elapsed < WIKIMEDIA_DELAY:
        time.sleep(WIKIMEDIA_DELAY - elapsed)
    _last_wiki_call = time.time()
    params = {
        "action": "query", "titles": f"File:{filename}",
        "prop": "imageinfo", "iiprop": "url",
        "format": "json",
    }
    try:
        r = requests.get(WIKIMEDIA_API, params=params,
                         headers=WIKIMEDIA_HEADERS, timeout=15)
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
        for page in pages.values():
            info = page.get("imageinfo", [{}])
            if info:
                return info[0].get("url")
    except Exception as e:
        print(f"  [Wikimedia URL error] {e}")
    return None

def find_wikimedia_reverse(slug: str, queries: list[str], year: int) -> str | None:
    """Try known filename first, then search queries. Returns direct image URL or None."""
    # 1. Check known files first (direct URL lookup — no search API needed)
    if slug in KNOWN_WIKIMEDIA_FILES:
        filename = KNOWN_WIKIMEDIA_FILES[slug]
        safe = filename.encode("ascii", errors="replace").decode("ascii")
        print(f"  Known file: {safe}")
        url = wikimedia_get_url(filename)
        if url:
            return url
        print(f"  [Known file URL lookup failed — falling through to search]")

    # 2. Fall back to search API
    for q in queries:
        print(f"  Searching: {q}")
        results = wikimedia_search(q)
        for result in results:
            title = result.get("title", "")
            if not title.startswith("File:"):
                continue
            filename = title[5:]
            fname_lower = filename.lower()
            if not any(ext in fname_lower for ext in [".jpg", ".png", ".jpeg"]):
                continue
            if "quarter" in fname_lower or "coin" in fname_lower or str(year) in fname_lower:
                url = wikimedia_get_url(filename)
                if url:
                    safe = filename.encode("ascii", errors="replace").decode("ascii")
                    print(f"    → Found: {safe}")
                    return url
    return None

# ── GCS upload ─────────────────────────────────────────────────────────────────
def upload_image_from_url(bucket, image_url: str, gcs_path: str) -> tuple[str, str]:
    """
    Download image from URL and upload to GCS.
    Wikimedia CDN (upload.wikimedia.org) requires proper User-Agent and referrer.
    Returns (public_url, gcs_uri).
    """
    headers = {
        "User-Agent": WIKIMEDIA_HEADERS["User-Agent"],
        "Referer": "https://commons.wikimedia.org/",
        "Accept": "image/jpeg,image/png,image/*,*/*",
    }
    r = requests.get(image_url, headers=headers, timeout=45, allow_redirects=True)
    r.raise_for_status()
    content_type = r.headers.get("content-type", "image/jpeg").split(";")[0].strip()
    if "png" in content_type:
        ext = ".png"
    else:
        ext = ".jpg"
    # Ensure path ends with correct extension
    if not gcs_path.endswith(ext):
        gcs_path = gcs_path.rsplit(".", 1)[0] + ext
    blob = bucket.blob(gcs_path)
    blob.upload_from_string(r.content, content_type=content_type)
    blob.make_public()
    return blob.public_url, f"gs://{STORAGE_BUCKET}/{gcs_path}"

# ── Firestore index write ──────────────────────────────────────────────────────
def index_doc(db, doc_id: str, side: str, data: dict, dry_run: bool) -> bool:
    """Write one obverse or reverse index doc. Returns True if written."""
    if dry_run:
        print(f"  [DRY RUN] Would write: {doc_id}  url={data.get('public_url','')[:70]}")
        return True
    try:
        doc_ref = db.collection(INDEX_COLLECTION).document(doc_id)
        doc_ref.set({
            "year":    data["year"],
            "mint":    data.get("mint"),
            "program": PROGRAM,
            "subject": data.get("subject"),
            side: {
                "public_url":   data["public_url"],
                "gcs_path":     data["gcs_path"],
                "attribution":  "Wikimedia Commons / Public Domain",
                "source_tier":  4,   # Tier 4 = Wikimedia
                "source_label": "Wikimedia Commons",
                "indexed_at":   datetime.now(timezone.utc).isoformat(),
            }
        }, merge=True)
        return True
    except Exception as e:
        print(f"  [Firestore error] {doc_id}: {e}")
        return False

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print("=" * 70)
        print("DRY RUN — no changes written to Firestore or GCS")
        print("=" * 70)

    print("Initializing Firebase + GCS...")
    db, bucket = init()
    print(f"  Connected. Index collection: {INDEX_COLLECTION}")

    TEMP_DIR.mkdir(exist_ok=True)

    stats = {
        "found":   0,
        "missing": 0,
        "indexed": 0,
        "errors":  0,
        "skipped": 0,
    }
    not_found = []

    # Check which docs already exist so we don't overwrite good data
    print(f"\nChecking existing AWQ entries in {INDEX_COLLECTION}...")
    existing = set()
    existing_docs = db.collection(INDEX_COLLECTION).stream()
    for d in existing_docs:
        if PROGRAM in d.id or "american-women" in d.id:
            existing.add(d.id)
    print(f"  Found {len(existing)} existing AWQ-related docs")

    print(f"\nProcessing {len(AWQ_DESIGNS)} AWQ designs...")
    print("=" * 70)

    # Track which years need obverse indexed
    years_with_obverse_indexed = set()

    for year, slug, display_name, queries in AWQ_DESIGNS:
        print(f"\n[{year}] {display_name} (slug: {slug})")

        rev_doc_id = f"{year}_{slug}_{PROGRAM}_reverse"
        obv_doc_id = f"{year}_{slug}_{PROGRAM}_obverse"
        year_obv_id = f"{year}_{PROGRAM}_obverse"

        # ── Reverse (design-specific) ──────────────────────────────────────
        if rev_doc_id in existing:
            print(f"  SKIP reverse — already indexed: {rev_doc_id}")
            stats["skipped"] += 1
        else:
            rev_url = find_wikimedia_reverse(slug, queries, year)
            if rev_url:
                stats["found"] += 1
                # Upload to GCS
                gcs_path = f"reference_images/awq/{year}_{slug}_reverse.jpg"
                try:
                    if not args.dry_run:
                        public_url, gcs_uri = upload_image_from_url(bucket, rev_url, gcs_path)
                    else:
                        public_url = rev_url
                        gcs_uri = f"gs://{STORAGE_BUCKET}/{gcs_path}"

                    ok = index_doc(db, rev_doc_id, "reverse", {
                        "year": str(year), "subject": slug,
                        "public_url": public_url, "gcs_path": gcs_uri,
                    }, dry_run=args.dry_run)
                    if ok:
                        stats["indexed"] += 1
                        print(f"  ✓ Indexed reverse: {rev_doc_id}")
                    else:
                        stats["errors"] += 1
                except Exception as e:
                    print(f"  [Error] Upload/index failed: {e}")
                    stats["errors"] += 1
            else:
                print(f"  ✗ NOT FOUND on Wikimedia: {display_name} ({year})")
                not_found.append((year, slug, display_name))
                stats["missing"] += 1

        # ── Obverse (shared Washington portrait per year) ──────────────────
        # Only need one per year — use the existing US Mint obverse if already there
        if year_obv_id not in existing and year not in years_with_obverse_indexed:
            # Check if US Mint already has this year's obverse
            existing_year_obv = db.collection(INDEX_COLLECTION).document(year_obv_id).get()
            if existing_year_obv.exists:
                print(f"  Obverse already in index: {year_obv_id}")
                years_with_obverse_indexed.add(year)
            else:
                # Use the AWQ obverse fallback URL (Washington portrait)
                gcs_path = f"reference_images/awq/{year}_awq_obverse.jpg"
                try:
                    if not args.dry_run:
                        public_url, gcs_uri = upload_image_from_url(
                            bucket, AWQ_OBVERSE_FALLBACK, gcs_path
                        )
                    else:
                        public_url = AWQ_OBVERSE_FALLBACK
                        gcs_uri = f"gs://{STORAGE_BUCKET}/{gcs_path}"

                    ok = index_doc(db, year_obv_id, "obverse", {
                        "year": str(year), "subject": None,
                        "public_url": public_url, "gcs_path": gcs_uri,
                    }, dry_run=args.dry_run)
                    if ok:
                        print(f"  ✓ Indexed obverse: {year_obv_id}")
                        years_with_obverse_indexed.add(year)
                except Exception as e:
                    print(f"  [Error] Obverse upload failed: {e}")

    # ── Summary ────────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("AWQ INDEXING COMPLETE")
    print("=" * 70)
    print(f"  Designs found on Wikimedia:  {stats['found']}")
    print(f"  Designs NOT found:           {stats['missing']}")
    print(f"  Docs indexed to Firestore:   {stats['indexed']}")
    print(f"  Docs skipped (existed):      {stats['skipped']}")
    print(f"  Errors:                      {stats['errors']}")

    if not_found:
        print(f"\n{'='*70}")
        print("DESIGNS NOT FOUND ON WIKIMEDIA — Need manual sourcing from usmint.gov:")
        print(f"{'='*70}")
        for year, slug, name in not_found:
            us_mint_url = f"https://www.usmint.gov/coins/coin-medal-programs/american-women-quarters/{slug}"
            print(f"  [{year}] {name}")
            print(f"    Slug: {slug}")
            print(f"    Try:  {us_mint_url}")

if __name__ == "__main__":
    main()
