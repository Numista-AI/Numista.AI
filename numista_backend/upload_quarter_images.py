"""
upload_quarter_images.py
========================
Uploads America the Beautiful (ATB) and American Women Quarter (AWQ) 
coin images to Firebase Storage and updates Firestore coin documents.

STRATEGY:
  ATB (2010-2021): Images already exist in GCS at numista-reference-library bucket.
                   Uses gcs_url from staging_atb_quarters.csv directly — no download needed.
  AWQ (2022-2025): Uses Wikimedia Commons API to discover and download images.
  
  For BOTH programs:
    - One unique design image (reverse) is shared across P, D, S mint marks for same year/design
    - Washington obverse is the same for all ATB quarters (one image, reused)
    - AWQ Washington obverse (Laura Gardin Fraser) is same for all AWQ quarters

USAGE:
    python upload_quarter_images.py --dry-run        # Print plan, no changes
    python upload_quarter_images.py --atb-only       # Only ATB quarters
    python upload_quarter_images.py --awq-only       # Only AWQ quarters
    python upload_quarter_images.py                  # Full live run

REQUIREMENTS:
    pip install firebase-admin requests Pillow
"""

import argparse
import csv
import io
import os
import re
import sys
import time
import unicodedata
from pathlib import Path
from collections import defaultdict

# Force UTF-8 output on Windows (handles special chars like ʻ in Kanakaʻole)
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import requests
from PIL import Image

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage as gcs_storage

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

BACKEND_DIR = Path(__file__).parent
KEY_PATH = BACKEND_DIR / "serviceAccountKey.json.json"
USER_EMAIL = "jseaman1204@gmail.com"
COINS_PATH = f"users/{USER_EMAIL}/coins"
STORAGE_BUCKET = "numista-uploads-studio-9101802118-8c9a8"
# GCS path pattern for user coin images (matches main app convention)
COIN_IMAGE_GCS_PREFIX = "users/{user}/coins/{coin_id}/{side}.jpg"
TEMP_DIR = BACKEND_DIR / "temp_quarter_images"

ATB_STAGING_CSV = BACKEND_DIR / "staging_atb_quarters.csv"

# Standard ATB obverse (reused for all ATB quarters regardless of mint mark)
ATB_OBVERSE_GCS_URL = (
    "https://storage.googleapis.com/numista-reference-library/"
    "reference_library/bulk_programs/america_the_beautiful/"
    "white-background-1600x662.jpg"
)
# Better ATB obverse - standard Washington portrait from the actual coin
ATB_OBVERSE_WIKIMEDIA = (
    "https://upload.wikimedia.org/wikipedia/commons/f/f3/"
    "America_the_Beautiful_quarter_obverse_%28Philadeplhia%29.jpg"
)

WIKIMEDIA_API = "https://commons.wikimedia.org/w/api.php"
WIKIMEDIA_HEADERS = {
    "User-Agent": "NumistaAI/1.0 (coin-collection-app; contact: ericd+numista@gmail.com)"
}
WIKIMEDIA_DELAY = 3.5  # seconds between Wikimedia requests (avoid 429)

# Standard image size for Firebase Storage
TARGET_SIZE = (800, 800)
JPEG_QUALITY = 90

# ──────────────────────────────────────────────────────────────────────────────
# ATB DESIGN MANIFEST (year -> list of park slugs)
# Maps ATB years to park keyword for Firestore matching
# ──────────────────────────────────────────────────────────────────────────────

ATB_DESIGNS = {
    2010: ["hot springs", "yellowstone", "yosemite", "grand canyon", "mount hood"],
    2011: ["gettysburg", "glacier", "olympic", "vicksburg", "chickasaw"],
    2012: ["el yunque", "chaco culture", "acadia", "hawaii volcanoes", "denali"],
    2013: ["white mountain", "perrys victory", "great basin", "fort mchenry", "mount rushmore"],
    2014: ["great smoky mountains", "shenandoah", "arches", "great sand dunes", "everglades"],
    2015: ["homestead", "kisatchie", "blue ridge parkway", "bombay hook", "saratoga"],
    2016: ["shawnee", "cumberland gap", "harpers ferry", "theodore roosevelt", "fort moultrie"],
    2017: ["effigy mounds", "frederick douglass", "ozark riverways", "ellis island", "george rogers clark"],
    2018: ["pictured rocks", "apostle islands", "voyageurs", "cumberland island", "block island"],
    2019: ["lowell", "american memorial park", "war in the pacific", "san antonio missions", "river of no return"],
    2020: ["national park of american samoa", "weir farm", "salt river bay", "marsh billings rockefeller", "tallgrass prairie"],
    2021: ["tuskegee airmen"],
}

# AWQ design manifest
AWQ_DESIGNS = {
    2022: ["maya angelou", "sally ride", "wilma mankiller", "nina otero-warren", "anna may wong"],
    2023: ["bessie coleman", "edith kanakaoole", "eleanor roosevelt", "jovita idar", "maria tallchief"],
    2024: ["pauli murray", "patsy takemoto mink", "mary edwards walker", "celia cruz", "zitkala-sa"],
    2025: ["ida b. wells", "juliette gordon low", "vera rubin", "stacey park milbern", "althea gibson"],
}

# ──────────────────────────────────────────────────────────────────────────────
# FIREBASE INIT
# ──────────────────────────────────────────────────────────────────────────────

def init_firebase():
    """Initialize Firebase app and GCS client (idempotent)."""
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(str(KEY_PATH))
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    # Use google-cloud-storage directly (same pattern as main.py)
    gcs_client = gcs_storage.Client.from_service_account_json(str(KEY_PATH))
    bucket = gcs_client.bucket(STORAGE_BUCKET)
    return db, bucket

# ──────────────────────────────────────────────────────────────────────────────
# FIRESTORE HELPERS
# ──────────────────────────────────────────────────────────────────────────────

IMAGE_FIELDS = [
    "image_url_obverse", "obverse_image_url", "image_url",
    "imageUrl", "image", "Image", "reverse_image_url", "image_url_reverse",
]

def get_field(d, *keys, default=""):
    for k in keys:
        v = d.get(k)
        if v and str(v).strip() not in ("", "None", "nan"):
            return str(v).strip()
    return default

def has_any_image(d: dict) -> bool:
    return any(d.get(k) and str(d.get(k)).strip() for k in IMAGE_FIELDS)

def load_quarter_coins(db, programs: list[str], years: list[int]) -> list[dict]:
    """
    Load all ATB or AWQ coin documents from Firestore.
    Returns list of dicts with coin data + doc_id.
    """
    print(f"  Loading coins from Firestore: {COINS_PATH}...")
    all_docs = list(db.collection(COINS_PATH).stream())
    print(f"  Total docs: {len(all_docs)}")

    matched = []
    prog_lower = [p.lower() for p in programs]
    for doc in all_docs:
        d = doc.to_dict()
        prog = get_field(d, "Program/Series", "program", "Program", "series", "Series",
                         "coin_type", "type", "Type", "Theme/Subject").lower()
        year_str = get_field(d, "Year", "year", "date", "Date")
        
        # Check program match
        prog_match = any(p in prog for p in prog_lower)
        if not prog_match:
            continue
        
        # Check year match (if years specified)
        if years:
            try:
                year_int = int(re.sub(r"[^0-9]", "", year_str)[:4])
                if year_int not in years:
                    continue
            except (ValueError, TypeError):
                continue
        
        theme = get_field(d, "Theme/Subject", "theme", "subject", "design").lower()
        # CRITICAL: Many coins store design in "Original Description from source" field
        if not theme or len(theme) < 3:
            orig_desc = get_field(d, "Original Description from source",
                                  "original_description", "description", "Description").lower()
            if orig_desc:
                theme = orig_desc
        mint = get_field(d, "Mint Mark", "mint_mark", "mintMark", "mint")
        
        matched.append({
            "doc_id": doc.id,
            "year": year_str,
            "program": prog,
            "theme": theme,
            "mint": mint,
            "has_image": has_any_image(d),
            "raw": d,
        })
    
    print(f"  Matched {len(matched)} coins for programs: {programs}")
    return matched

# ──────────────────────────────────────────────────────────────────────────────
# ATB IMAGE LOADING (from staging_atb_quarters.csv - no download needed!)
# ──────────────────────────────────────────────────────────────────────────────

def load_atb_staging_images() -> dict:
    """
    Load ATB reference images from staging_atb_quarters.csv.
    Returns dict: year_str -> {park_slug -> gcs_url}
    """
    index = defaultdict(dict)  # {year: {park_keywords: gcs_url}}
    
    with open(ATB_STAGING_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = row.get("year", "").strip()
            side = row.get("side", "").strip().lower()
            gcs_url = row.get("gcs_url", "").strip()
            tags = row.get("tags", "").strip().lower()
            
            if not gcs_url or not year:
                continue
            
            if side == "reverse":
                index[year][tags] = gcs_url
            elif side == "obverse":
                index[year]["__obverse__"] = gcs_url
    
    print(f"  ATB staging index loaded: {len(index)} years, "
          f"{sum(len(v) for v in index.values())} images")
    return index

def match_atb_image(coin: dict, atb_index: dict) -> tuple[str | None, str | None]:
    """
    Find the obverse and reverse GCS URLs for an ATB coin from the staging index.
    Returns (obverse_url, reverse_url) or (None, None) if not found.
    """
    year = coin["year"].strip()
    theme = coin["theme"]
    
    # ATB obverse: use the staging obverse or known Wikimedia URL
    obverse_url = None
    for yr_key, images in atb_index.items():
        if year in yr_key or yr_key in year:
            obverse_url = images.get("__obverse__")
            if obverse_url:
                break
    if not obverse_url:
        obverse_url = ATB_OBVERSE_WIKIMEDIA
    
    # ATB reverse: search by theme keywords across ALL index entries for this year
    reverse_url = None
    theme_words = [w for w in theme.split() if len(w) > 3]
    
    # First pass: look in the exact year bucket
    for yr_key, images in atb_index.items():
        if year not in yr_key and yr_key not in year:
            continue
        for tag_key, url in images.items():
            if tag_key == "__obverse__":
                continue
            for word in theme_words:
                if word in tag_key:
                    reverse_url = url
                    break
            if reverse_url:
                break
        if reverse_url:
            break
    
    # Second pass: broader search across ALL years using theme words
    if not reverse_url and theme_words:
        for yr_key, images in atb_index.items():
            for tag_key, url in images.items():
                if tag_key == "__obverse__":
                    continue
                for word in theme_words:
                    if word in tag_key:
                        # Only use if the year appears in the tag or matches
                        if year in tag_key or not year:
                            reverse_url = url
                            break
                if reverse_url:
                    break
            if reverse_url:
                break
    
    return obverse_url, reverse_url

# ──────────────────────────────────────────────────────────────────────────────
# WIKIMEDIA IMAGE FETCHING (for AWQ quarters)
# ──────────────────────────────────────────────────────────────────────────────

def wikimedia_search(query: str, limit: int = 5) -> list[dict]:
    """Search Wikimedia Commons for coin images."""
    time.sleep(WIKIMEDIA_DELAY)
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srnamespace": 6,  # File namespace
        "srlimit": limit,
        "format": "json",
    }
    try:
        r = requests.get(WIKIMEDIA_API, params=params, headers=WIKIMEDIA_HEADERS, timeout=15)
        r.raise_for_status()
        return r.json().get("query", {}).get("search", [])
    except Exception as e:
        print(f"  [Wikimedia search error] {query}: {e}")
        return []

def wikimedia_get_url(filename: str) -> str | None:
    """Get direct download URL for a Wikimedia Commons file."""
    time.sleep(WIKIMEDIA_DELAY)
    params = {
        "action": "query",
        "titles": f"File:{filename}",
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json",
    }
    try:
        r = requests.get(WIKIMEDIA_API, params=params, headers=WIKIMEDIA_HEADERS, timeout=15)
        r.raise_for_status()
        pages = r.json()["query"]["pages"]
        for page in pages.values():
            info = page.get("imageinfo", [])
            if info:
                return info[0].get("url")
    except Exception as e:
        print(f"  [Wikimedia URL error] {filename}: {e}")
    return None

def download_image(url: str, dest_path: Path) -> bool:
    """Download an image from URL to dest_path. Returns True on success."""
    time.sleep(WIKIMEDIA_DELAY)
    try:
        r = requests.get(url, headers=WIKIMEDIA_HEADERS, stream=True, timeout=30)
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"  [Download error] {url}: {e}")
        return False

def find_awq_image(person_name: str, year: int) -> tuple[str | None, str | None]:
    """
    Find AWQ reverse and obverse images on Wikimedia Commons.
    Returns (obverse_url, reverse_url) or (None, None) if not found.
    """
    # Normalize name variants (handle data entry errors and alternate spellings)
    name_aliases = [person_name]
    name_lower = person_name.lower()
    # Known spelling aliases
    if 'anna mae wong' in name_lower or 'anna may wong' in name_lower:
        name_aliases = ['anna may wong', 'anna mae wong']  # both spellings
    elif 'edith kanaka' in name_lower:
        name_aliases = ['edith kanakaoole', 'edith kanaka ole', 'edith kanakaole']
    elif 'otero' in name_lower:
        name_aliases = ['nina otero-warren', 'adelina otero-warren', 'nina otero warren']
    elif 'zitkala' in name_lower:
        name_aliases = ['zitkala-sa', 'zitkala sa', 'zitkala']
    
    # Build search queries from all aliases
    all_queries = []
    for name in name_aliases:
        all_queries += [
            f"American Women Quarter {year} {name}",
            f"{name} quarter reverse {year}",
            f"AWQ {year} {name}",
        ]
    
    reverse_url = None
    for q in all_queries:
        results = wikimedia_search(q)
        for result in results:
            title = result.get('title', '')
            if title.startswith('File:'):
                filename = title[5:]
                name_lower_check = filename.lower()
                person_first = name_aliases[0].lower().split()[0]  # first name
                if (str(year) in name_lower_check or person_first in name_lower_check) and \
                   any(ext in name_lower_check for ext in ['.jpg', '.png', '.jpeg']):
                    url = wikimedia_get_url(filename)
                    if url:
                        reverse_url = url
                        safe_name = filename.encode('ascii', errors='replace').decode('ascii')
                        print(f"    Found: {safe_name}")
                        break
        if reverse_url:
            break
    
    # AWQ obverse: standard Washington portrait (same for all AWQ)
    # Use the known stable Wikimedia URL for the Washington obverse from AWQ series
    awq_obverse_queries = [
        "American Women Quarter obverse Washington 2022",
        "Washington quarter obverse Laura Gardin Fraser",
    ]
    obverse_url = None
    for q in awq_obverse_queries:
        results = wikimedia_search(q)
        for result in results:
            title = result.get("title", "")
            if title.startswith("File:") and "obverse" in title.lower():
                filename = title[5:]
                url = wikimedia_get_url(filename)
                if url:
                    obverse_url = url
                    break
        if obverse_url:
            break
    
    # Final fallback obverse: ATB obverse is close enough (same Washington portrait era)
    if not obverse_url:
        obverse_url = ATB_OBVERSE_WIKIMEDIA
    
    return obverse_url, reverse_url

# ──────────────────────────────────────────────────────────────────────────────
# IMAGE RESIZE
# ──────────────────────────────────────────────────────────────────────────────

def resize_image(src_path: Path, dest_path: Path) -> bool:
    """Resize image to TARGET_SIZE with white background, save as JPEG."""
    try:
        img = Image.open(src_path).convert("RGBA")
        img.thumbnail(TARGET_SIZE, Image.LANCZOS)
        background = Image.new("RGB", TARGET_SIZE, (255, 255, 255))
        offset = (
            (TARGET_SIZE[0] - img.width) // 2,
            (TARGET_SIZE[1] - img.height) // 2,
        )
        background.paste(img, offset, img)
        background.save(dest_path, "JPEG", quality=JPEG_QUALITY)
        return True
    except Exception as e:
        print(f"  [Resize error] {src_path}: {e}")
        return False

# ──────────────────────────────────────────────────────────────────────────────
# FIREBASE STORAGE UPLOAD
# ──────────────────────────────────────────────────────────────────────────────

def upload_to_storage(bucket, local_path: Path, coin_id: str, side: str = "obverse") -> str | None:
    """
    Upload image to GCS bucket.
    Returns public HTTPS URL (required for Image.network() in Flutter).
    """
    remote_path = COIN_IMAGE_GCS_PREFIX.format(
        user=USER_EMAIL, coin_id=coin_id, side=side
    )
    try:
        blob = bucket.blob(remote_path)
        blob.upload_from_filename(str(local_path), content_type="image/jpeg")
        # Make public so Flutter's Image.network() can load it directly
        blob.make_public()
        return blob.public_url  # returns https://storage.googleapis.com/...
    except Exception as e:
        print(f"  [Upload error] {coin_id}/{side}: {e}")
        return None

def upload_from_url(bucket, image_url: str, coin_id: str, side: str, temp_path: Path) -> str | None:
    """Download from URL, resize, and upload to Firebase Storage."""
    # Download
    raw_path = temp_path / f"{coin_id}_{side}_raw"
    success = download_image(image_url, raw_path)
    if not success:
        return None
    
    # Resize
    resized_path = temp_path / f"{coin_id}_{side}.jpg"
    if not resize_image(raw_path, resized_path):
        raw_path.unlink(missing_ok=True)
        return None
    raw_path.unlink(missing_ok=True)
    
    # Upload
    url = upload_to_storage(bucket, resized_path, coin_id, side)
    resized_path.unlink(missing_ok=True)
    return url

# ──────────────────────────────────────────────────────────────────────────────
# FIRESTORE UPDATE
# ──────────────────────────────────────────────────────────────────────────────

def update_firestore(db, coin_id: str, obverse_url: str = None, reverse_url: str = None):
    """Update coin document with image URLs."""
    updates = {}
    if obverse_url:
        updates["image_url_obverse"] = obverse_url
    if reverse_url:
        updates["image_url_reverse"] = reverse_url
    if updates:
        db.collection(COINS_PATH).document(coin_id).update(updates)

# ──────────────────────────────────────────────────────────────────────────────
# MAIN LOGIC
# ──────────────────────────────────────────────────────────────────────────────

def process_atb_quarters(db, bucket, dry_run: bool, force: bool = False):
    """Process all ATB (America the Beautiful) quarter coins."""
    print("\n" + "="*70)
    print("PROCESSING: America the Beautiful Quarters (ATB, 2010-2021)")
    print("="*70)
    
    ATB_PROGRAMS = [
        "national park quarters", "america the beautiful", "atb",
        "national park", "america the beautiful quarters"
    ]
    atb_years = list(ATB_DESIGNS.keys())
    
    # Load Firestore coins
    coins = load_quarter_coins(db, ATB_PROGRAMS, atb_years)
    
    # Load staging image index (GCS URLs already prepared)
    atb_index = load_atb_staging_images()
    
    # Group coins by (year, theme) to detect design sharing
    design_groups = defaultdict(list)
    for coin in coins:
        year_clean = re.sub(r"[^0-9]", "", coin["year"])[:4]
        theme_clean = coin["theme"][:30]
        design_groups[(year_clean, theme_clean)].append(coin)
    
    print(f"\nDesign groups found: {len(design_groups)}")
    
    stats = {"updated": 0, "skipped_has_image": 0, "no_reverse_found": 0, "error": 0}
    design_cache = {}  # (year, theme) -> (obverse_url, reverse_url)
    
    for (year, theme), group_coins in sorted(design_groups.items()):
        # Find images for this design (lookup once, apply to all in group)
        if (year, theme) not in design_cache:
            sample = group_coins[0]
            obverse_url, reverse_url = match_atb_image(sample, atb_index)
            design_cache[(year, theme)] = (obverse_url, reverse_url)
        else:
            obverse_url, reverse_url = design_cache[(year, theme)]
        
        if not reverse_url:
            print(f"  [NO REVERSE FOUND] Year={year}, Theme={theme}")
            stats["no_reverse_found"] += len(group_coins)
            continue
        
        for coin in group_coins:
            if coin["has_image"] and not dry_run and not force:
                stats["skipped_has_image"] += 1
                continue
            
            if dry_run:
                print(f"  DRY RUN: Would update {coin['doc_id'][:20]}... "
                      f"Year={year}, Theme={theme[:25]}, Mint={coin['mint']}")
                print(f"    Obverse: {obverse_url[:60]}...")
                print(f"    Reverse: {reverse_url[:60]}...")
                stats["updated"] += 1
                continue
            
            # For ATB: GCS URLs are already public — use them directly without re-uploading!
            # Just update Firestore with the staging GCS URL
            try:
                update_firestore(db, coin["doc_id"],
                                 obverse_url=obverse_url,
                                 reverse_url=reverse_url)
                stats["updated"] += 1
                print(f"  Updated: {coin['doc_id'][:20]}... Year={year}, Theme={theme[:25]}")
            except Exception as e:
                print(f"  [ERROR] {coin['doc_id']}: {e}")
                stats["error"] += 1
            
            time.sleep(0.1)  # Firestore rate limit
    
    print(f"\nATB Results: {stats}")
    return stats

def process_awq_quarters(db, bucket, dry_run: bool, force: bool = False):
    """Process all American Women Quarter coins."""
    print("\n" + "="*70)
    print("PROCESSING: American Women Quarters (AWQ, 2022-2025)")
    print("="*70)
    
    AWQ_PROGRAMS = [
        "american women quarters", "american women", "awq",
        "us women's quarters", "women quarters"
    ]
    awq_years = list(AWQ_DESIGNS.keys())
    
    coins = load_quarter_coins(db, AWQ_PROGRAMS, awq_years)
    
    # Group by (year, person/theme)
    design_groups = defaultdict(list)
    for coin in coins:
        year_clean = re.sub(r"[^0-9]", "", coin["year"])[:4]
        theme_clean = coin["theme"][:30]
        design_groups[(year_clean, theme_clean)].append(coin)
    
    print(f"\nDesign groups found: {len(design_groups)}")
    
    TEMP_DIR.mkdir(exist_ok=True)
    stats = {"updated": 0, "skipped_has_image": 0, "no_image_found": 0, "error": 0}
    design_cache = {}  # (year, theme) -> (obverse_url, reverse_url)
    
    for (year, theme), group_coins in sorted(design_groups.items()):
        if (year, theme) not in design_cache:
            # Find AWQ person name from theme
            try:
                year_int = int(year)
            except ValueError:
                year_int = 2022
            
            person_name = theme.strip() if theme else f"{year} quarter"
            print(f"\n  Searching Wikimedia for: {year} {person_name}")
            obverse_url, reverse_url = find_awq_image(person_name, year_int)
            design_cache[(year, theme)] = (obverse_url, reverse_url)
        else:
            obverse_url, reverse_url = design_cache[(year, theme)]
        
        if not reverse_url:
            print(f"  [NO IMAGE FOUND] Year={year}, Theme={theme}")
            stats["no_image_found"] += len(group_coins)
            continue
        
        for coin in group_coins:
            if coin["has_image"] and not dry_run and not force:
                stats["skipped_has_image"] += 1
                continue
            
            if dry_run:
                print(f"  DRY RUN: Would update {coin['doc_id'][:20]}... "
                      f"Year={year}, Theme={theme[:25]}, Mint={coin['mint']}")
                print(f"    Obverse: {str(obverse_url)[:60]}")
                print(f"    Reverse: {str(reverse_url)[:60]}")
                stats["updated"] += 1
                continue
            
            # For AWQ: download from Wikimedia, resize, upload to Firebase Storage
            try:
                # Upload obverse (download once, upload for each coin)
                obverse_storage_url = upload_from_url(
                    bucket, obverse_url, coin["doc_id"], "obverse", TEMP_DIR
                )
                # Upload reverse
                reverse_storage_url = upload_from_url(
                    bucket, reverse_url, coin["doc_id"], "reverse", TEMP_DIR
                )
                
                if obverse_storage_url or reverse_storage_url:
                    update_firestore(db, coin["doc_id"],
                                     obverse_url=obverse_storage_url,
                                     reverse_url=reverse_storage_url)
                    stats["updated"] += 1
                    print(f"  Updated: {coin['doc_id'][:20]}... Year={year}")
                else:
                    stats["error"] += 1
            except Exception as e:
                print(f"  [ERROR] {coin['doc_id']}: {e}")
                stats["error"] += 1
            
            time.sleep(0.2)
    
    print(f"\nAWQ Results: {stats}")
    return stats

# ──────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Upload quarter coin images to Firebase")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be done without making changes")
    parser.add_argument("--atb-only", action="store_true",
                        help="Only process ATB (America the Beautiful) quarters")
    parser.add_argument("--awq-only", action="store_true",
                        help="Only process AWQ (American Women) quarters")
    parser.add_argument("--force", action="store_true",
                        help="Update even coins that already have images")
    parser.add_argument("--limit", type=int, default=0,
                        help="Limit number of coins to process (0 = no limit)")
    args = parser.parse_args()
    
    if args.dry_run:
        print("=" * 70)
        print("DRY RUN MODE — no changes will be made to Firebase")
        print("=" * 70)
    
    print(f"Initializing Firebase...")
    db, bucket = init_firebase()
    print(f"  Connected to Firestore and Storage: {STORAGE_BUCKET}")
    
    TEMP_DIR.mkdir(exist_ok=True)
    
    total_stats = {"updated": 0, "errors": 0}
    
    if not args.awq_only:
        atb_stats = process_atb_quarters(db, bucket, dry_run=args.dry_run, force=args.force)
        total_stats["updated"] += atb_stats.get("updated", 0)
        total_stats["errors"] += atb_stats.get("error", 0)
    
    if not args.atb_only:
        awq_stats = process_awq_quarters(db, bucket, dry_run=args.dry_run, force=args.force)
        total_stats["updated"] += awq_stats.get("updated", 0)
        total_stats["errors"] += awq_stats.get("error", 0)
    
    print("\n" + "="*70)
    print(f"COMPLETE — Updated: {total_stats['updated']} coins, Errors: {total_stats['errors']}")
    print("="*70)
    
    if args.dry_run:
        print("\nTo run for real: python upload_quarter_images.py")
        print("ATB only:        python upload_quarter_images.py --atb-only")
        print("AWQ only:        python upload_quarter_images.py --awq-only")

if __name__ == "__main__":
    main()
