import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import urllib.parse
from google.cloud import storage
import re

CSV_ARCHIVE = r"C:\Users\ericd\Documents\MyVertexProject\reference_library_export.csv"
BUCKET_NAME = "numista-reference-library"
STAGE_DIR = r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images\wikipedia\historic_quarters"

def apply_watermark(image_path, text="Wikimedia / U.S. Mint"):
    try:
        img = Image.open(image_path).convert("RGBA")
        txt = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt)
        try:
            font = ImageFont.truetype("arial.ttf", int(img.size[1]*0.015))
        except:
            font = ImageFont.load_default()
            
        bbox = draw.textbbox((0, 0), text, font=font)
        padding = int(img.size[0] * 0.02)
        x = img.size[0] - (bbox[2] - bbox[0]) - padding
        y = img.size[1] - (bbox[3] - bbox[1]) - padding
        
        draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0, 100))
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 180))
        
        out = Image.alpha_composite(img, txt)
        out.convert("RGB").save(image_path, quality=95)
        return True
    except Exception as e:
        return False

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
    # Extract attribution
    attr = "Wikimedia / U.S. Mint"
    clean_filename = filename
    if '__attr__' in filename:
        parts = filename.split('__attr__')
        clean_filename = parts[0] + os.path.splitext(filename)[1]
        attr_part = parts[1].replace(os.path.splitext(filename)[1], '').replace('_', ' ')
        attr = f"{attr_part} / U.S. Mint"
    elif '_attr_' in filename:
        parts = filename.split('_attr_')
        clean_filename = parts[0] + os.path.splitext(filename)[1]
        attr_part = parts[1].replace(os.path.splitext(filename)[1], '').replace('_', ' ')
        attr = f"{attr_part} / U.S. Mint"
        
    safe_filename = clean_filename.replace(' ', '_').replace('(', '').replace(')', '')
    gcs_path = f"reference_library/bulk_programs/historic_quarters/{safe_filename}"
    
    if gcs_path in existing_gcs_paths:
        safe_skip_name = filename.encode('ascii', errors='replace').decode('ascii')
        print(f"Skipping {safe_skip_name} (Already in bucket index)")
        continue
        
    local_path = os.path.join(STAGE_DIR, filename)
    safe_print_name = filename.encode('ascii', errors='replace').decode('ascii')
    print(f"Processing local file: {safe_print_name}...")
    try:
        apply_watermark(local_path, text=attr)
        
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(local_path)
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{urllib.parse.quote(gcs_path)}"
        processed_count += 1
        
        # Parse year
        match = re.search(r'1[89]\d{2}|20\d{2}', filename)
        year = match.group(0) if match else "Varied"
        
        # Parse Series tags dynamically
        tags = "Historic Quarter"
        lower_name = filename.lower()
        if 'standing' in lower_name: tags = "Standing Liberty Quarter"
        elif 'seated' in lower_name: tags = "Seated Liberty Quarter"
        elif 'capped' in lower_name: tags = "Capped Bust"
        elif 'draped' in lower_name or 'drapped' in lower_name: tags = "Draped Bust"
        elif 'gobrecht' in lower_name: tags = "Gobrecht"
        
        denom = 'Quarter'
        if '50c' in lower_name or 'half' in lower_name: denom = 'Half Dollar'
        elif '10c' in lower_name or 'dime' in lower_name: denom = 'Dime'
        elif '$1' in lower_name or 'dollar' in lower_name: denom = 'One Dollar'
        elif '5c' in lower_name or 'nickel' in lower_name: denom = 'Nickel'
        elif '25c' in lower_name: denom = 'Quarter'
        
        side = 'obverse'
        if 'reverse' in lower_name: side = 'reverse'
        
        csv_rows.append({
            'denomination': denom,
            'year': year,
            'side': side,
            'source': 'wikipedia_archive',
            'category': 'Circulation',
            'tags': tags,
            'gcs_url': public_url,
            'gcs_path': gcs_path,
            'attribution': attr,
            'license': 'Public Domain',
            'filename': safe_filename,
            'source_name': 'en.wikipedia.org (Local Payload)'
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
