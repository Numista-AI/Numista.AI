# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import os
import urllib.request
import re
import json
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from google.cloud import storage

BASE_DIR = r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images\US Mint\Bulk_Scrape\ATB"
os.makedirs(BASE_DIR, exist_ok=True)
CSV_ARCHIVE = r"C:\Users\ericd\Documents\MyVertexProject\reference_library_export.csv"
BUCKET_NAME = "numista-reference-library"

COOKIES = "dwanonymous_b2cf918be9f3733e2d19f7e7beb4b6d7=bfSORPJwpNAdNU3a1qGbhncVuJ; _gcl_gs=2.1.k1$i1769457086$u255207436; _gcl_au=1.1.1031101466.1769457089; __cq_uuid=bfSORPJwpNAdNU3a1qGbhncVuJ; _ga=GA1.1.1077834011.1769457089; _fbp=fb.1.1769457089788.294347621354410369; _pin_unauth=dWlkPVpqUTVPRGN6WmpRdFpqa3paaTAwT0RFd0xXRmxOREF0TUdKalpqZG1aR0ZsTjJJdw; _gcl_aw=GCL.1769457111.Cj0KCQiAvtzLBhCPARIsALwhxdp_PjDfieajd6fpAa6NceOKLCWFaIRSBO2fqWH1Twd4FMD4G9fIXeEaAiWDEALw_wcB; _gcl_dc=GCL.1769457111.Cj0KCQiAvtzLBhCPARIsALwhxdp_PjDfieajd6fpAa6NceOKLCWFaIRSBO2fqWH1Twd4FMD4G9fIXeEaAiWDEALw_wcB; a1ashgd=tyddtw7bc4n00000tyddtw7bc4n00000; cqcid=bfSORPJwpNAdNU3a1qGbhncVuJ; __cq_dnt=0; dw_dnt=0; AMCVS_7A9335DD5CF935CA0A495FCD%40AdobeOrg=1; AMCV_7A9335DD5CF935CA0A495FCD%40AdobeOrg=179643557%7CMCIDTS%7C20558%7CMCMID%7C08909863047730330722103480248485599599%7CMCAAMLH-1776781291%7C7%7CMCAAMB-1776781291%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1776183691s%7CNONE%7CMCSYNCSOP%7C411-20487%7CvVersion%7C5.5.0; s_cc=true; cebs=1; _ce.clock_data=-58%2C24.246.138.41%2C1%2C91e1a2a41c0741f7f47615ab9de2fb8a%2CChrome%2CUS; __cq_seg=0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00; __cq_bc=%7B%22aarb-USM%22%3A%5B%7B%22id%22%3A%22MASTER_SEMIQMC%22%7D%5D%7D; dwsid=ft4G18N-VkMRAIjwjUu3NTqHT3mWTwj-2PEVpT1SKuZZOHNSwXVqe9ZrQ4mgcq1XljLUj-twfW64DbZiU1kZvg==; dwac_bcKmAiaageu6saaadbf1J7A92a=o096uJdr5CK_b5LTXuS6c94yZPDDcMpE0pA%3D|dw-only|USM13657498||USD|false|US%2FEastern|true; cquid=mK/4fKoufV2kYk1maHags5S0Ep914WfGI+GwqXDCdL0=|b83980aaac7d5af452acc14bc7123cafaeef222883452604c32fa5ec561f6061|b83980aaac7d5af452acc14bc7123cafaeef222883452604c32fa5ec561f6061; sid=RX9aqNaaXFIyDILlaF8RjgEmEwaDqwLv-_0; cf_clearance=UmHArA7llX4C4LXbu8gMVLqOcP4qfXhz9zG1Pery2oY-1776182624-1.2.1.1-62oE.XawGTUqh5y6Ga8s.x_gsqv9V93jlp4jLlZS1Zo5ggnPdHpYmHuVc4woLpG6RWprUVh5Tpe0UxpT9VvmjQx15Zd9BJtBgiYZT8YpWNgGCYcG.6zZ79u1MWR9WFTmJduPTKKrUWuD.b3ZJFvjhlWbYI5wKIuV0BGCcWux3aA5FaxvtRgSjgqt7E2JXTFbGQdV9_2T1uQjHplUgyjAEvc0VI2rALsUwUmnOYeisMbewrKXa1Obw5_o8hJk.AdkGNRlzOfSVvVN2kJ_SkEJfjSTyAHcLh37N15wJuEKk0A_.RHgX4YDST_7EpNXdKOy9eS7L9v2RfVnRORsK2OgGA; __cf_bm=Ndhz.ZhUT9BC.8nHIVMnuHda.8KNOSlnpmAELerm.38-1776182623.9926167-1.0.1.1-ommjFlQ122zrvLtwhRyE6JJlgc.W.paVdh.VaTI78G1wdYsQyvg80Xh6buvv3rSLIov5BOOCNolwpfxPYQ23yxSRmnHhgHGgmWM3WiOsYMz1VltbdumTZ4irL4.myQdNGTfHXgkuaBDs6lZezWkMgQ; AWSALB=h89svIiNu4ds1PhsrC6vTzdEWOQlnEd54IMlXH3khu88kzNiTcWaFRtYZ8+jkSyzyUsvU1ThOerAKUcW7Amq3N0ClB8gpklcoVtzSEbCPO4PTvRhb8/Trx3Sf801; AWSALBCORS=h89svIiNu4ds1PhsrC6vTzdEWOQlnEd54IMlXH3khu88kzNiTcWaFRtYZ8+jkSyzyUsvU1ThOerAKUcW7Amq3N0ClB8gpklcoVtzSEbCPO4PTvRhb8/Trx3Sf801; _rdt_uuid=1769457089327.4df2ebdc-15ff-4b34-9ae8-d6e2096a5dc9; _uetsid=3c29db20380d11f1bd682500d035356d; _uetvid=683d4bb0faf011f09ddaef7abf1922b0; cebsp_=31; s_sq=%5B%5BB%5D%5D; _ga_804PW1F121=GS2.1.s1776176491$o5$g1$t1776182627$j49$l0$h0; _ce.s=v~aa565285b5c7305eeae8f9fe831b92ff8fe2c1d7~lcw~1776182635131~vir~new~lva~1776182623023~vpv~3~v11ls~20400380-3819-11f1-b34a-fb1e6becbb9d~gtrk.la~mnytafa2~v11.cs~226228~v11.s~20400380-3819-11f1-b34a-fb1e6becbb9d~v11.vs~aa565285b5c7305eeae8f9fe831b92ff8fe2c1d7~v11.fsvd~eyJub3RNb2RpZmllZFVybCI6Imh0dHBzOi8vd3d3LnVzbWludC5nb3YvY29pbnMvY29pbi1zZXRzLyIsInVybCI6InVzbWludC5nb3YvY29pbnMvY29pbi1zZXRzIiwicmVmIjoiaHR0cHM6Ly93d3cudXNtaW50Lmdvdi9jb2lucy9jb2luLXByb2dyYW1zL3NlbWlxdWluY2VudGVubmlhbC8iLCJ1dG0iOltdfQ%3D%3D~v11.sla~1776181599164~v11.wss~1776181599165~lcw~1776182649050"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36','Cookie': COOKIES, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'}

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

url = "https://www.usmint.gov/learn/coins-and-medals/circulating-coins/quarter/america-the-beautiful-quarters"
print(f"Fetching {url}... ")
try:
    req = urllib.request.Request(url, headers=HEADERS)
    html = urllib.request.urlopen(req).read().decode('utf-8')
except Exception as e:
    print(f"Failed to fetch {url}: {e}")
    exit(1)

links = set(re.findall(r'(/content/dam/usmint/[^\'\"\?]+\.jpg)', html, re.I | re.MULTILINE))
links = [f"https://www.usmint.gov{l}" for l in links if '150x' not in l and '300x' not in l and '500x' not in l]

print(f"Found {len(links)} master quality image assets.")

if len(links) == 0:
    print("Could not locate any asset links across the document.")
    exit(1)

client = storage.Client()
bucket = client.bucket(BUCKET_NAME)

csv_rows = []
downloaded_count = 0

for link in links:
    filename = link.split('/')[-1]
        
    local_path = os.path.join(BASE_DIR, filename)
    print(f"Extracting {filename}...")
    try:
        img_req = urllib.request.Request(link, headers=HEADERS)
        with urllib.request.urlopen(img_req) as resp:
            with open(local_path, 'wb') as out_f:
                out_f.write(resp.read())
        apply_watermark(local_path)
        downloaded_count += 1
        
        # Deploy to GCS
        gcs_path = f"reference_library/bulk_programs/america_the_beautiful/{filename}"
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(local_path)
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{gcs_path}"
        
        # Parse park names dynamically from filename for ATB 
        # Example: 2010-america-the-beautiful-quarters-coin-hot-springs-uncirculated-reverse.jpg
        name_parts = filename.split('-coin-')
        park_name = "America the Beautiful"
        if len(name_parts) > 1:
            park_raw = name_parts[1].replace('-uncirculated-reverse.jpg', '').replace('-uncirculated-obverse.jpg', '').replace('.jpg', '')
            park_name = park_raw.replace('-', ' ').title()
            
        csv_rows.append({
            'denomination': 'Quarter Dollar',
            'year': filename[:4] if filename[:4].isdigit() else '2010-2021',
            'side': 'reverse' if 'reverse' in filename.lower() else 'obverse',
            'source': 'us_mint_archive',
            'category': 'Circulation',
            'tags': f"{park_name}, America the Beautiful Quarters",
            'gcs_url': public_url,
            'gcs_path': gcs_path,
            'attribution': 'U.S. Mint',
            'license': 'Public Domain',
            'filename': filename,
            'source_name': 'usmint.gov'
        })
            
    except Exception as e:
        print(f"Failed extraction on {link}: {e}")

if csv_rows:
    staging_df = pd.DataFrame(csv_rows)
    staging_df.to_csv("staging_atb_quarters.csv", index=False)
    print(f"Staged {len(csv_rows)} specific linkages ready for append.")
    try:
        master_df = pd.read_csv(CSV_ARCHIVE)
        master_df = pd.concat([master_df, staging_df], ignore_index=True)
        master_df.to_csv(CSV_ARCHIVE, index=False)
        print("Master CSV updated!")
    except Exception as e:
        print(f"Could not append to master: {e}")
else:
    print("No valid linkages created.")

print(f"Phase 2 and 3 executed for ATB. {downloaded_count} physical assets processed.")
