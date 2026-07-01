import sqlite3
import requests
import json
import os
from pathlib import Path
from google.cloud import storage

# ── Configuration ─────────────────────────────────────────────────────────────
DB_PATH = Path("numista_backend/database/numista_coins.db")
GCS_BUCKET = "numista-uploads-studio-9101802118-8c9a8"
GCS_BASE_DIR = "reference_library/wikimedia_uscoin"

# List of manually sourced items from subagent
MANUAL_ITEMS = [
    {"denomination": "Kennedy Half Dollar", "year": "2024", "url": "https://upload.wikimedia.org/wikipedia/commons/2/2b/Obverse_of_the_2021_John_F._Kennedy_Half_Dollar.jpg", "filename": "2024_kennedy_half_obverse.jpg"},
    {"denomination": "Jefferson Nickel", "year": "2024", "url": "https://upload.wikimedia.org/wikipedia/commons/e/ee/Jefferson-Nickel-Obverse.jpg", "filename": "2024_jefferson_nickel_obverse.jpg"},
    {"denomination": "Lincoln Cent", "year": "2024", "url": "https://upload.wikimedia.org/wikipedia/commons/0/07/US_One_Cent_Obv.png", "filename": "2024_lincoln_cent_obverse.png"},
    {"denomination": "Roosevelt Dime", "year": "2024", "url": "https://upload.wikimedia.org/wikipedia/commons/3/3c/United_States_dime%2C_obverse%2C_2002.jpg", "filename": "2024_roosevelt_dime_obverse.jpg"},
    {"denomination": "Walking Liberty Half Dollar", "year": "1942", "url": "https://upload.wikimedia.org/wikipedia/commons/7/7b/1942_Walking_Liberty_Half_Dollar_Obverse.jpg", "filename": "1942_walking_liberty_obverse.jpg"},
    {"denomination": "Washington Quarter", "year": "1942", "url": "https://upload.wikimedia.org/wikipedia/commons/7/77/Monnaie_-_Etats-Unis%2C_1-4_dollar%2C_Philadelphie%2C_1942_-_btv1b113366180.jpg", "filename": "1942_washington_quarter_obverse.jpg"},
    {"denomination": "Eisenhower Centennial Silver Dollar", "year": "1990", "url": "https://upload.wikimedia.org/wikipedia/commons/d/da/1990_Eisenhower_Silver_%241_Obverse.jpg", "filename": "1990_eisenhower_centennial_obverse.jpg"},
    {"denomination": "Buffalo Nickel", "year": "1937", "url": "https://upload.wikimedia.org/wikipedia/commons/a/ae/Buffalo_nickel_obverse.jpg", "filename": "1937_buffalo_nickel_obverse.jpg"},
    {"denomination": "Franklin Half Dollar", "year": "1951", "url": "https://upload.wikimedia.org/wikipedia/commons/d/d7/Franklin_half_dollar_obverse.jpg", "filename": "1951_franklin_half_obverse.jpg"},
]

SERIES_MAP = {
    "Kennedy Half Dollar": ["Kennedy Half Dollars"],
    "Jefferson Nickel": ["Jefferson Nickels", "Jefferson Wartime Nickels"],
    "Lincoln Cent": ["Lincoln Cents", "Lincoln Memorial Cents", "Lincoln Shield Cents", "Lincoln Wheat Pennies"],
    "Roosevelt Dime": ["Roosevelt Dimes"],
    "Walking Liberty Half Dollar": ["Liberty Walking Half Dollars"],
    "Washington Quarter": ["Washington Silver Quarters", "Washington Quarters (Classic)"],
    "Eisenhower Centennial Silver Dollar": ["Modern Commemorative Dollars"],
    "Buffalo Nickel": ["Buffalo Nickels"],
    "Franklin Half Dollar": ["Franklin Half Dollars"]
}

def download_and_upload(url, filename, gcs_path):
    print(f"  Downloading {url}...")
    headers = {"User-Agent": "NumistaAI/1.0 (Contact: numista.ai@example.com)"}
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        # Upload to GCS
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET)
        blob = bucket.blob(gcs_path)
        blob.upload_from_string(resp.content, content_type=resp.headers.get("content-type"))
        return f"https://storage.googleapis.com/{GCS_BUCKET}/{gcs_path}"
    except Exception as e:
        print(f"    Error: {e}")
        return None

def update_db(denomination, year, gcs_url):
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    
    series_list = SERIES_MAP.get(denomination, [])
    if not series_list:
        print(f"    No series mapping for {denomination}")
        return 0
        
    placeholders = ",".join(["?" for _ in series_list])
    query = f"""UPDATE definitive_reference 
                SET image_url_obverse = ? 
                WHERE series IN ({placeholders}) 
                AND (year = ? OR year LIKE ? OR year LIKE ?)"""
    params = [gcs_url] + series_list + [str(year), f"{year}%", f"%{year}%"]
    
    cur.execute(query, params)
    count = conn.total_changes
    conn.commit()
    conn.close()
    return count

def main():
    print("Starting Manual Image Sync...")
    for item in MANUAL_ITEMS:
        denom = item["denomination"]
        year = item["year"]
        url = item["url"]
        filename = item["filename"]
        
        print(f"\n-> {denom} {year}")
        gcs_path = f"{GCS_BASE_DIR}/{filename}"
        
        gcs_url = download_and_upload(url, filename, gcs_path)
        if gcs_url:
            print(f"    Uploaded to: {gcs_url}")
            count = update_db(denom, year, gcs_url)
            print(f"    Updated {count} database rows")

if __name__ == "__main__":
    main()
