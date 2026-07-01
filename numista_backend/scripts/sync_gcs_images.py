
import sqlite3
import subprocess
import re
import os
from pathlib import Path

# Configuration
DB_PATH = Path('c:/Users/ericd/Documents/MyVertexProject/numista_backend/database/numista_coins.db')
BUCKETS = [
    "gs://numista-reference-library",
    "gs://numista-uploads-studio-9101802118-8c9a8",
    "gs://us_mint_coin_images"
]

def list_bucket_files(bucket_url):
    print(f"  Listing files in {bucket_url}...")
    try:
        # Use gsutil ls -r to get all files. Use shell=True for Windows.
        result = subprocess.run(f'gsutil ls -r "{bucket_url}/**"', 
                               shell=True, capture_output=True, text=True, check=True)
        files = [line.strip() for line in result.stdout.split('\n') if line.strip().endswith(('.jpg', '.png', '.webp', '.jpeg'))]
        return files
    except Exception as e:
        print(f"    Error listing {bucket_url}: {e}")
        return []

def extract_keywords(path):
    # Extract the filename and remove extension
    filename = os.path.basename(path).lower()
    name_only = os.path.splitext(filename)[0]
    
    # Clean up common words
    clean = name_only.replace('_', ' ').replace('-', ' ').replace('final attributed', '')
    clean = clean.replace('obverse', '').replace('reverse', '').replace('(', '').replace(')', '')
    
    # Split into keywords
    keywords = [k for k in clean.split() if len(k) > 2]
    return set(keywords), "obverse" in name_only or "obv" in name_only, "reverse" in name_only or "rev" in name_only

def sync_images():
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    
    # Load all items from DB for matching
    print("Loading database items for matching...")
    cur.execute("SELECT id, variety, denomination, category, series FROM definitive_reference")
    db_items = cur.fetchall()
    
    total_matched = 0
    
    for bucket in BUCKETS:
        files = list_bucket_files(bucket)
        print(f"    Found {len(files)} images in {bucket}")
        
        for file_path in files:
            keywords, is_obv, is_rev = extract_keywords(file_path)
            if not keywords: continue
            
            # Simple matching logic: 
            # If variety and denomination are in keywords, it's a match
            best_match = None
            for db_id, variety, denom, cat, series in db_items:
                v = (variety or "").lower()
                d = (denom or "").lower()
                
                # Special check for Friedberg/Catalog numbers in filename
                match_variety = False
                if any(cat_code in keywords for cat_code in ['fr', 'pick', 'km', 'friedberg']):
                    # If the variety in DB has the same numbers
                    db_nums = re.findall(r'\d+', v)
                    file_nums = re.findall(r'\d+', os.path.basename(file_path))
                    if db_nums and any(n in file_nums for n in db_nums):
                        match_variety = True
                
                # Check if major keywords are present
                if match_variety or (v and all(k in keywords for k in v.split() if len(k) > 3)):
                    best_match = db_id
                    break
                    
            if best_match:
                # Update DB
                if is_obv:
                    cur.execute("UPDATE definitive_reference SET image_url_obverse = ? WHERE id = ?", (file_path, best_match))
                elif is_rev:
                    cur.execute("UPDATE definitive_reference SET image_url_reverse = ? WHERE id = ?", (file_path, best_match))
                else:
                    # Default to obverse if not specified
                    cur.execute("UPDATE definitive_reference SET image_url_obverse = ? WHERE id = ? AND (image_url_obverse IS NULL OR image_url_obverse = '')", (file_path, best_match))
                
                total_matched += 1
                if total_matched % 100 == 0:
                    print(f"      Matched {total_matched} images...")
                    conn.commit()

    conn.commit()
    conn.close()
    print(f"--- Sync Complete. Total images matched/linked: {total_matched} ---")

if __name__ == "__main__":
    print("--- Starting GCS Image Sync ---")
    sync_images()
