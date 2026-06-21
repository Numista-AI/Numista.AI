"""
scrape_usmint_awq.py
====================
Uses Playwright MCP to scrape AWQ coin images from usmint.gov
and index them into coin_image_index Firestore collection.

Run after index_awq_into_coin_image_index.py to fill in designs
not available on Wikimedia Commons.
"""
import sys
import time
import requests
from datetime import datetime, timezone
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage as gcs_storage

BACKEND_DIR = Path(__file__).parent
KEY_PATH    = BACKEND_DIR / "serviceAccountKey.json.json"
STORAGE_BUCKET = "numista-uploads-studio-9101802118-8c9a8"
INDEX_COLLECTION = "coin_image_index"
PROGRAM = "american-women-quarters"

# Designs to scrape from US Mint (not found on Wikimedia)
USMINT_DESIGNS = [
    (2023, "edith-kanaka-ole",  "Edith Kanakaole"),
    (2023, "eleanor-roosevelt", "Eleanor Roosevelt"),
    (2023, "jovita-idar",       "Jovita Idar"),
    (2023, "maria-tallchief",   "Maria Tallchief"),
    (2024, "patsy-mink",        "Patsy Mink"),
    (2024, "ida-b-wells",       "Ida B. Wells"),
    (2024, "celia-cruz",        "Celia Cruz"),
    (2024, "zitkala-sa",        "Zitkala-Sa"),
    (2024, "miriam-slater",     "Miriam Slater"),
    (2025, "vera-rubin",        "Vera Rubin"),
    (2025, "stagecoach-mary",   "Stagecoach Mary"),
    (2025, "harriet-tubman",    "Harriet Tubman"),
    (2025, "ada-lovelace",      "Ada Lovelace"),
    (2025, "susan-la-flesche",  "Susan La Flesche Picotte"),
]

USMINT_BASE = "https://www.usmint.gov/coins/coin-medal-programs/american-women-quarters"

def init():
    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_admin.initialize_app(credentials.Certificate(str(KEY_PATH)))
    db = firestore.client()
    gcs = gcs_storage.Client.from_service_account_json(str(KEY_PATH))
    bucket = gcs.bucket(STORAGE_BUCKET)
    return db, bucket

def upload_image_from_url(bucket, image_url: str, gcs_path: str) -> tuple[str, str]:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    r = requests.get(image_url, headers=headers, timeout=30)
    r.raise_for_status()
    blob = bucket.blob(gcs_path)
    content_type = "image/jpeg" if ".jpg" in image_url.lower() else "image/png"
    blob.upload_from_string(r.content, content_type=content_type)
    blob.make_public()
    return blob.public_url, f"gs://{STORAGE_BUCKET}/{gcs_path}"

def index_doc(db, doc_id: str, side: str, data: dict):
    doc_ref = db.collection(INDEX_COLLECTION).document(doc_id)
    doc_ref.set({
        "year":    data["year"],
        "mint":    None,
        "program": PROGRAM,
        "subject": data.get("subject"),
        side: {
            "public_url":   data["public_url"],
            "gcs_path":     data["gcs_path"],
            "attribution":  "US Mint / Public Domain",
            "source_tier":  1,  # Tier 1 = US Mint official
            "source_label": "US Mint",
            "indexed_at":   datetime.now(timezone.utc).isoformat(),
        }
    }, merge=True)

if __name__ == "__main__":
    print("NOTE: This script requires manual image URLs from usmint.gov.")
    print("Use the Playwright browser to navigate to each page, find the")
    print("reverse coin image URL, then call this script with those URLs.\n")
    print("US Mint pages to scrape:")
    for year, slug, name in USMINT_DESIGNS:
        url = f"{USMINT_BASE}/{slug}"
        rev_doc = f"{year}_{slug}_{PROGRAM}_reverse"
        print(f"  [{year}] {name}")
        print(f"    Page:  {url}")
        print(f"    DocID: {rev_doc}")
