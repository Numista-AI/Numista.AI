# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import urllib.parse
from google.cloud import storage

CSV_ARCHIVE = r"C:\Users\ericd\Documents\MyVertexProject\reference_library_export.csv"
BUCKET_NAME = "numista-reference-library"
STAGE_DIR = r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images\wikipedia\American_Women_quarters"

attributions = {
    'mary edwards': 'Phebe Hemphill',
    'anna may wong': 'John P. McGraw, Emily Damstra',
    'bessie coleman': 'Eric David Custer, Chris Costello',
    'edith kanaka': 'Emily Damstra'
}

def get_attribution(filename):
    lower_fname = filename.lower().replace('_', ' ').replace('-', ' ')
    for key, attr in attributions.items():
        if key in lower_fname:
            return attr
    return 'Wikimedia / U.S. Mint'

def apply_watermark(image_path):
    try:
        img = Image.open(image_path).convert("RGBA")
        txt = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt)
        try:
            font = ImageFont.truetype("arial.ttf", int(img.size[1]*0.015))
        except:
            font = ImageFont.load_default()
            
        # Dynamic text based on passing filename could be done, but we'll stick to standard watermark
        text = "Wikimedia / U.S. Mint"
        bbox = draw.textbbox((0, 0), text, font=font)
        padding = int(img.size[0] * 0.02)
        x = img.size[0] - (bbox[2] - bbox[0]) - padding
        y = img.size[1] - (bbox[3] - bbox[1]) - padding
        
        draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0, 100))
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 180))
        
        out = Image.alpha_composite(img, txt)
        # convert to rgb to allow saving as jpg if needed
        out.convert("RGB").save(image_path, quality=95)
        return True
    except Exception as e:
        return False

# 1. Update existing rows in CSV
print("Updating historical attributions in CSV...")
df = pd.read_csv(CSV_ARCHIVE)
updated_count = 0
for idx, row in df.iterrows():
    if pd.notna(row['filename']) and 'american' in str(row['tags']).lower():
        fname = str(row['filename'])
        new_attr = get_attribution(fname)
        if new_attr != 'Wikimedia / U.S. Mint' and row['attribution'] != new_attr:
            df.at[idx, 'attribution'] = new_attr
            updated_count += 1
            
df.to_csv(CSV_ARCHIVE, index=False)
print(f"Updated {updated_count} historical records in CSV.")

# 2. Ingest local Wikipedia dir
client = storage.Client()
bucket = client.bucket(BUCKET_NAME)

try:
    df = pd.read_csv(CSV_ARCHIVE)
    existing_gcs_paths = set(df['gcs_path'].dropna().values)
except:
    existing_gcs_paths = set()

local_files = [f for f in os.listdir(STAGE_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]

csv_rows = []
processed_count = 0

for filename in local_files:
    # Standardize format naming slightly 
    safe_filename = filename.replace(' ', '_').replace('(', '').replace(')', '')
    gcs_path = f"reference_library/bulk_programs/american_women/{safe_filename}"
    
    if gcs_path in existing_gcs_paths:
        safe_skip_name = filename.encode('ascii', errors='replace').decode('ascii')
        print(f"Skipping {safe_skip_name} (Already in bucket index)")
        continue
        
    local_path = os.path.join(STAGE_DIR, filename)
    safe_print_name = filename.encode('ascii', errors='replace').decode('ascii')
    print(f"Processing local file: {safe_print_name}...")
    try:
        apply_watermark(local_path)
        
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(local_path)
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{urllib.parse.quote(gcs_path)}"
        processed_count += 1
        
        # Get year if exists in string
        import re
        match = re.search(r'202[2-6]', filename)
        year = match.group(0) if match else "Varied"
        
        attr = get_attribution(safe_filename)
        
        csv_rows.append({
            'denomination': 'Quarter',
            'year': year,
            'side': 'reverse',
            'source': 'wikipedia_archive',
            'category': 'Circulation',
            'tags': "American Women Quarters",
            'gcs_url': public_url,
            'gcs_path': gcs_path,
            'attribution': attr,
            'license': 'Public Domain',
            'filename': safe_filename,
            'source_name': 'en.wikipedia.org'
        })
            
    except Exception as e:
        print(f"Failed processing on {safe_print_name}: {e}")

if csv_rows:
    staging_df = pd.DataFrame(csv_rows)
    print(f"\nStaged {len(csv_rows)} absolute linkages.")
    try:
        master_df = pd.read_csv(CSV_ARCHIVE)
        master_df = pd.concat([master_df, staging_df], ignore_index=True)
        master_df.to_csv(CSV_ARCHIVE, index=False)
        print("Master CSV updated!")
    except Exception as e:
        print(f"Could not append to master: {e}")
else:
    print("\nNo valid linkages created.")

print(f"Extraction complete. {processed_count} physical assets processed.")
