# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import os
import urllib.request
import re
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import urllib.parse
from google.cloud import storage
import time

CSV_ARCHIVE = r"C:\Users\ericd\Documents\MyVertexProject\reference_library_export.csv"
BUCKET_NAME = "numista-reference-library"
STAGE_DIR = r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images\wikipedia\American_Women_quarters"
os.makedirs(STAGE_DIR, exist_ok=True)

def apply_watermark(image_path):
    try:
        img = Image.open(image_path).convert("RGBA")
        txt = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt)
        try:
            font = ImageFont.truetype("arial.ttf", int(img.size[1]*0.015))
        except:
            font = ImageFont.load_default()
            
        text = "Wikimedia / U.S. Mint"
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
    master_df = pd.read_csv(CSV_ARCHIVE)
    existing_gcs_paths = set(master_df['gcs_path'].dropna().values)
except:
    existing_gcs_paths = set()

url = "https://en.wikipedia.org/wiki/American_Women_quarters"
USER_COOKIES = "WMF-Last-Access=14-Apr-2026; WMF-Last-Access-Global=14-Apr-2026; WMF-DP=5c3; GeoIP=US:NC:Hendersonville:35.36:-82.43:v4; NetworkProbeLimit=0.001; WMF-Uniq=HdU1Bp3X-NJMZOVd_tbI-gNCAAEBAFvdl0amK5B6VPuPD5YiwMzB-4lVMAgHP0XV; enwikimwuser-sessionId=8c2c986f948548b5cf3e"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Firefox) Chrome/120.0.0.0 Safari/537.36',
    'Cookie': USER_COOKIES,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
}

print("Fetching Wikipedia...")
req = urllib.request.Request(url, headers=HEADERS)
html = urllib.request.urlopen(req).read().decode('utf-8')

links = re.findall(r'src="//(upload\.wikimedia\.org/wikipedia/commons/thumb/[^\"]+)"', html)
hq_links = []
for link in links:
    if 'quarter' in link.lower() or 'awq' in link.lower() or 'roosevelt' in link.lower() or 'cruz' in link.lower():
        parts = link.split('/')
        if len(parts) >= 3 and parts[-1].endswith('.jpg'):
            if 'thumb' in parts:
                thumb_idx = parts.index('thumb')
                hq_url = "https://" + "/".join(parts[:thumb_idx] + parts[thumb_idx+1:-1])
                hq_links.append(hq_url)

hq_links = list(set(hq_links))
print(f"Discovered {len(hq_links)} Wikipedia master resolutions.")

csv_rows = []
downloaded = 0

for hq_url in hq_links:
    filename = hq_url.split('/')[-1]
    filename = urllib.parse.unquote(filename).replace(' ', '_').replace('(', '').replace(')', '')
    gcs_path = f"reference_library/bulk_programs/american_women/{filename}"
    
    if gcs_path in existing_gcs_paths:
        print(f"Skipping {filename} (Already in bucket)")
        continue
        
    local_path = os.path.join(STAGE_DIR, filename)
    safe_print_name = filename.encode('ascii', errors='replace').decode('ascii')
    print(f"Downloading {safe_print_name} from Wikipedia...")
    try:
        req_img = urllib.request.Request(hq_url.replace(' ', '_'), headers=HEADERS)
        with urllib.request.urlopen(req_img) as resp:
            with open(local_path, 'wb') as f:
                f.write(resp.read())
                
        apply_watermark(local_path)
        
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(local_path)
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{urllib.parse.quote(gcs_path)}"
        
        match = re.search(r'202[2-6]', filename)
        year = match.group(0) if match else "Varied"
        
        csv_rows.append({
            'denomination': 'Quarter',
            'year': year,
            'side': 'reverse',
            'source': 'wikipedia_archive',
            'category': 'Circulation',
            'tags': "American Women Quarters",
            'gcs_url': public_url,
            'gcs_path': gcs_path,
            'attribution': 'Wikimedia / U.S. Mint',
            'license': 'Public Domain',
            'filename': filename,
            'source_name': 'en.wikipedia.org'
        })
        downloaded += 1
        time.sleep(2) # Slight delay
    except Exception as e:
        print(f"Failed to process {hq_url}: {e}")

if csv_rows:
    staging_df = pd.DataFrame(csv_rows)
    print(f"\nStaged {len(csv_rows)} linkages.")
    try:
        master_df = pd.read_csv(CSV_ARCHIVE)
        master_df = pd.concat([master_df, staging_df], ignore_index=True)
        master_df.to_csv(CSV_ARCHIVE, index=False)
        print("Master CSV updated!")
    except Exception as e:
        pass
else:
    print("\nNo new valid linkages created.")

print(f"Wikipedia Pipeline complete. {downloaded} assets pushed.")
