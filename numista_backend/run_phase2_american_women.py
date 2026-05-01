import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import urllib.parse
from google.cloud import storage

# Path to the _files directory Chrome created
BASE_DIR = r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images\si_quarters\American Women Quarters™ Program _ Smithsonian American Women's History Museum_files"
CSV_ARCHIVE = r"C:\Users\ericd\Documents\MyVertexProject\reference_library_export.csv"
BUCKET_NAME = "numista-reference-library"

def apply_watermark(image_path):
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", int(img.size[1]*0.015))
        except:
            font = ImageFont.load_default()
        text = "U.S. Mint"
        bbox = draw.textbbox((0, 0), text, font=font)
        padding = int(img.size[0] * 0.02)
        x = img.size[0] - (bbox[2] - bbox[0]) - padding
        y = img.size[1] - (bbox[3] - bbox[1]) - padding
        draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0, 100))
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 180))
        img.save(image_path, quality=95)
        return True
    except:
        return False

# Initialize GCP Client
client = storage.Client()
bucket = client.bucket(BUCKET_NAME)

try:
    master_df = pd.read_csv(CSV_ARCHIVE)
    existing_gcs_paths = set(master_df['gcs_path'].dropna().values)
except:
    existing_gcs_paths = set()

# Grab only relevant images
local_files = [
    f for f in os.listdir(BASE_DIR) 
    if f.lower().endswith('.jpg') and ('2022' in f or '2023' in f or '2024' in f or '2025' in f)
]

csv_rows = []
processed_count = 0

for filename in local_files:
    local_path = os.path.join(BASE_DIR, filename)
    safe_filename = filename.replace(' ', '_').lower()
    gcs_path = f"reference_library/bulk_programs/american_women/{safe_filename}"
    
    if gcs_path in existing_gcs_paths:
        print(f"Skipping {filename} (Already exists)")
        continue
        
    print(f"Processing local file: {filename}...")
    try:
        apply_watermark(local_path)
        
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(local_path)
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{urllib.parse.quote(gcs_path)}"
        processed_count += 1
        
        parts = filename.split(' ')
        year = parts[0] if parts[0].isdigit() else "Varied"
        
        csv_rows.append({
            'denomination': 'Quarter',
            'year': year,
            'side': 'reverse', # Women program designs are on the reverse
            'source': 'us_mint_archive',
            'category': 'Circulation',
            'tags': "American Women Quarters",
            'gcs_url': public_url,
            'gcs_path': gcs_path,
            'attribution': 'U.S. Mint',
            'license': 'Public Domain',
            'filename': safe_filename,
            'source_name': 'womenshistory.si.edu'
        })
            
    except Exception as e:
        print(f"Failed processing on {filename}: {e}")

if csv_rows:
    staging_df = pd.DataFrame(csv_rows)
    print(f"\nStaged {len(csv_rows)} linkages.")
    try:
        master_df = pd.read_csv(CSV_ARCHIVE)
        master_df = pd.concat([master_df, staging_df], ignore_index=True)
        master_df.to_csv(CSV_ARCHIVE, index=False)
        print("Master CSV updated!")
    except Exception as e:
        print(f"Could not append to master: {e}")
else:
    print("\nNo valid linkages created.")

print(f"Phase 2/3 complete for American Women Quarters. {processed_count} assets processed.")
