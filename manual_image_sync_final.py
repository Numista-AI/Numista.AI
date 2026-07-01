import sqlite3
import os
import subprocess
import json

# Configuration
DB_PATH = 'numista_backend/database/numista_coins.db'
SCRATCH_DIR = 'scratch'
GCS_BUCKET = 'numista-reference-library'
GCS_PREFIX = 'reference_library/wikimedia_uscoin/'

# Mapping of filename to (denomination, year)
FILE_MAPPING = {
    '1943_1c_obverse.jpg': ('One Cent', '1943'),
    '1940_2c_obverse.jpg': ('Two Cents', '1940'),
    '1940_3c_obverse.jpg': ('Three Cents', '1940'),
    '1990_eisenhower_centennial_obverse.jpg': [('One Dollar', '1990')],
    '1942_walking_liberty_obverse.jpg': ('Half Dollar', '1942'),
    '1942_washington_quarter_obverse.jpg': ('Quarter Dollar', '1942'),
    '1937_buffalo_nickel_obverse.png': ('Five Cents', '1937'),
    '1951_franklin_half_obverse.png': ('Half Dollar', '1951'),
    '2024_kennedy_half_obverse.jpg': ('Half Dollar', '2024'),
    '2024_jefferson_nickel_obverse.jpg': ('Five Cents', '2024'),
    '2024_lincoln_cent_obverse.png': ('One Cent', '2024'),
    '2024_roosevelt_dime_obverse.jpg': ('One Dime', '2024'),
    '2023_kennedy_half_obverse.png': ('Half Dollar', '2023'),
    '2022_lincoln_cent_obverse.jpg': ('One Cent', '2022'),
    '2022_jefferson_nickel_obverse.jpg': ('Five Cents', '2022'),
    '2023_jefferson_nickel_obverse.jpg': ('Five Cents', '2023'),
    '2022_roosevelt_dime_obverse.jpg': ('One Dime', '2022'),
    '2023_roosevelt_dime_obverse.png': ('One Dime', '2023')
}

def upload_to_gcs(local_path, gcs_path):
    print(f"Uploading {local_path} to gs://{GCS_BUCKET}/{gcs_path}...")
    try:
        subprocess.run(['gcloud', 'storage', 'cp', local_path, f"gs://{GCS_BUCKET}/{gcs_path}"], check=True, shell=True)
        return f"https://storage.googleapis.com/{GCS_BUCKET}/{gcs_path}"
    except subprocess.CalledProcessError as e:
        print(f"  Error uploading {local_path}: {e}")
        return None

def update_db(denomination, year, image_url):
    print(f"Updating DB for {denomination} ({year}) with {image_url}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("UPDATE definitive_reference SET image_url_obverse = ? WHERE denomination = ? AND year = ?", (image_url, denomination, year))
    count = cursor.rowcount
    if count > 0:
        print(f"  Success: Updated {count} records")
    else:
        print(f"  Warning: No record found for {denomination} ({year})")
    conn.commit()
    conn.close()

def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    for filename, mapping in FILE_MAPPING.items():
        local_path = os.path.join(SCRATCH_DIR, filename)
        if not os.path.exists(local_path):
            print(f"Skipping {filename} (not found in scratch)")
            continue
            
        if os.path.getsize(local_path) < 10000:
            print(f"Skipping {filename} (file too small, likely error page)")
            continue

        gcs_path = GCS_PREFIX + filename
        public_url = upload_to_gcs(local_path, gcs_path)
        
        if public_url:
            if isinstance(mapping, list):
                for denom, year in mapping:
                    update_db(denom, year, public_url)
            else:
                denom, year = mapping
                update_db(denom, year, public_url)

if __name__ == '__main__':
    main()
