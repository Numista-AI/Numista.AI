# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import urllib.parse
from google.cloud import storage

BASE_DIR = r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images\US Mint\Bulk_Scrape\Presidential"
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

# Process all JPG files in the directory
local_files = [f for f in os.listdir(BASE_DIR) if f.lower().endswith('.jpg') or f.lower().endswith('.png')]

csv_rows = []
processed_count = 0

for filename in local_files:
    local_path = os.path.join(BASE_DIR, filename)
    gcs_path = f"reference_library/bulk_programs/presidential/{filename}"
    
    # We will STILL check existing_gcs_paths to avoid duplicates in CSV
    if gcs_path in existing_gcs_paths:
        print(f"Skipping {filename} (Already exists in GCS index)")
        continue
        
    print(f"Processing local file: {filename}...")
    try:
        # Watermark
        apply_watermark(local_path)
        
        # Deploy to GCS
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(local_path)
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{urllib.parse.quote(gcs_path)}"
        processed_count += 1
        
        # Parse names automatically like "2007-presidential-dollar-coin-george-washington-uncirculated-obverse.jpg"
        parts = filename.replace('.jpg','').split('-')
        year = parts[0] if parts[0].isdigit() else "Varied"
        
        csv_rows.append({
            'denomination': 'One Dollar',
            'year': year,
            'side': 'reverse' if 'reverse' in filename.lower() else 'obverse',
            'source': 'us_mint_archive',
            'category': 'Circulation',
            'tags': "Presidential Dollar",
            'gcs_url': public_url,
            'gcs_path': gcs_path,
            'attribution': 'U.S. Mint',
            'license': 'Public Domain',
            'filename': filename,
            'source_name': 'usmint.gov (local payload)'
        })
            
    except Exception as e:
        print(f"Failed processing on {filename}: {e}")

if csv_rows:
    staging_df = pd.DataFrame(csv_rows)
    print(f"\nStaged {len(csv_rows)} specific linkages ready for append.")
    try:
        master_df = pd.read_csv(CSV_ARCHIVE)
        master_df = pd.concat([master_df, staging_df], ignore_index=True)
        master_df.to_csv(CSV_ARCHIVE, index=False)
        print("Master CSV updated!")
    except Exception as e:
        print(f"Could not append to master: {e}")
else:
    print("\nNo valid linkages created. All found local assets already exist in the CSV.")

print(f"Local Phase 2/3 complete for Presidential Dollars. {processed_count} physical assets processed.")
