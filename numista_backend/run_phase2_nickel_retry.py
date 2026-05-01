import os
import urllib.request
import re
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from google.cloud import storage

BASE_DIR = r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images\US Mint\Bulk_Scrape\Nickel"
os.makedirs(BASE_DIR, exist_ok=True)
CSV_ARCHIVE = r"C:\Users\ericd\Documents\MyVertexProject\reference_library_export.csv"
BUCKET_NAME = "numista-reference-library"

COOKIES = "dwanonymous_b2cf918be9f3733e2d19f7e7beb4b6d7=bfSORPJwpNAdNU3a1qGbhncVuJ; _gcl_gs=2.1.k1$i1769457086$u255207436; _gcl_au=1.1.1031101466.1769457089; __cq_uuid=bfSORPJwpNAdNU3a1qGbhncVuJ; _ga=GA1.1.1077834011.1769457089; _fbp=fb.1.1769457089788.294347621354410369; _pin_unauth=dWlkPVpqUTVPRGN6WmpRdFpqa3paaTAwT0RFd0xXRmxOREF0TUdKalpqZG1aR0ZsTjJJdw; _gcl_aw=GCL.1769457111.Cj0KCQiAvtzLBhCPARIsALwhxdp_PjDfieajd6fpAa6NceOKLCWFaIRSBO2fqWH1Twd4FMD4G9fIXeEaAiWDEALw_wcB; _gcl_dc=GCL.1769457111.Cj0KCQiAvtzLBhCPARIsALwhxdp_PjDfieajd6fpAa6NceOKLCWFaIRSBO2fqWH1Twd4FMD4G9fIXeEaAiWDEALw_wcB; a1ashgd=tyddtw7bc4n00000tyddtw7bc4n00000; cqcid=bfSORPJwpNAdNU3a1qGbhncVuJ; __cq_dnt=0; dw_dnt=0; AMCVS_7A9335DD5CF935CA0A495FCD%40AdobeOrg=1; s_cc=true; cebs=1; _ce.clock_data=-58%2C24.246.138.41%2C1%2C91e1a2a41c0741f7f47615ab9de2fb8a%2CChrome%2CUS; __cq_seg=0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00; __cq_bc=%7B%22aarb-USM%22%3A%5B%7B%22id%22%3A%22MASTER_SEMIQMC%22%7D%5D%7D; dwsid=ft4G18N-VkMRAIjwjUu3NTqHT3mWTwj-2PEVpT1SKuZZOHNSwXVqe9ZrQ4mgcq1XljLUj-twfW64DbZiU1kZvg==; dwac_bcKmAiaageu6saaadbf1J7A92a=o096uJdr5CK_b5LTXuS6c94yZPDDcMpE0pA%3D|dw-only|USM13657498||USD|false|US%2FEastern|true; cquid=mK/4fKoufV2kYk1maHags5S0Ep914WfGI+GwqXDCdL0=|b83980aaac7d5af452acc14bc7123cafaeef222883452604c32fa5ec561f6061|b83980aaac7d5af452acc14bc7123cafaeef222883452604c32fa5ec561f6061; sid=RX9aqNaaXFIyDILlaF8RjgEmEwaDqwLv-_0; AMCV_7A9335DD5CF935CA0A495FCD%40AdobeOrg=179643557%7CMCIDTS%7C20558%7CMCMID%7C08909863047730330722103480248485599599%7CMCAAMLH-1776788515%7C7%7CMCAAMB-1776788515%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1776190915s%7CNONE%7CMCSYNCSOP%7C411-20487%7CvVersion%7C5.5.0; cf_clearance=m97OQWFJmvQ2T.T7Yr1h7_8uQrW4n1a7DLhs6zYQG1s-1776186381-1.2.1.1-3i0wf0KuoNBGZwTFXoQeudXqdiF0fFrQcuBtGQ1CTaYlsqtQPcqV031gpYNScJAkEMzM6NUmr5mH0hWVgtY4.3M_yAGTXE9krbD41TjffPRRPxPLPqua1tV7bR2nT_PHjIAFSzrp2f4e_HDwnqt6zdEEhMcyj8.3v4EgEDIYmDdDGPd5JR0Hzl9y5DV9hZW78T6i9aV_Zh_VLxu4HLfVbXvLskzSToa9LzZPtLl7fqdD.ADY8Yk5JGv.ZwSHChtBD6aZ79Yz_xaW16iKVr3HpMB3mzWfFTI9koRSGahGDPmW.m5Fep0xEHNAZAb7DydIaFCZUeq7vy8tPKP82c1piQ; __cf_bm=.Bw5DBcQi.0NfNstdbg5zhSypeu1MVLC8rqUuEuHWf8-1776186381.3491876-1.0.1.1-L4Kyv93SGuy4ZLPT8apOdY65.VlALfbX2sB60fFnWqnNTf.2txvVZO7ZlhkLumidpnWwFPTAtYKN3saSVK1CA4wdePJZlKlohVJzanq8ZCzaqbtDblxGbl653gAScpw7oKks.xXwzfD2UjbxnxDk8g; AWSALB=9ssCjTQcAfqPSf3SU4TFdNYTdVF0cpxHvdNQQAvRT7xCSj3HC/3J9b38uStGUl9+L8SkTKEblrxmaMj+exykLYjPuaYgf5FGTYEkHAPM14XNPhHjSUI0YMDoQqh+; AWSALBCORS=9ssCjTQcAfqPSf3SU4TFdNYTdVF0cpxHvdNQQAvRT7xCSj3HC/3J9b38uStGUl9+L8SkTKEblrxmaMj+exykLYjPuaYgf5FGTYEkHAPM14XNPhHjSUI0YMDoQqh+; _rdt_uuid=1769457089327.4df2ebdc-15ff-4b34-9ae8-d6e2096a5dc9; _uetsid=3c29db20380d11f1bd682500d035356d; _uetvid=683d4bb0faf011f09ddaef7abf1922b0; cebsp_=77; s_sq=%5B%5BB%5D%5D; _ga_804PW1F121=GS2.1.s1776176491$o5$g1$t1776186399$j25$l0$h0; _ce.s=v~aa565285b5c7305eeae8f9fe831b92ff8fe2c1d7~lcw~1776186421197~vir~new~lva~1776186403984~vpv~3~v11ls~31c31cb0-3822-11f1-a2f0-0bd4f98e222c~gtrk.la~mnyvjh96~v11.cs~226228~v11.s~31c31cb0-3822-11f1-a2f0-0bd4f98e222c~v11.vs~aa565285b5c7305eeae8f9fe831b92ff8fe2c1d7~v11.fsvd~eyJub3RNb2RpZmllZFVybCI6Imh0dHBzOi8vd3d3LnVzbWludC5nb3YvbGVhcm4vY29pbnMtYW5kLW1lZGFscy9jb2xsZWN0aWJsZS1jb2lucy9uYXRpdmUtYW1lcmljYW4tZG9sbGFyLWNvaW5zI2FjY29yZGlvbi1iMGQ5Y2UyYzIyLWl0ZW0tMGM4N2YzNjhjZiIsInVybCI6InVzbWludC5nb3YvbGVhcm4vY29pbnMtYW5kLW1lZGFscy9jb2xsZWN0aWJsZS1jb2lucy9uYXRpdmUtYW1lcmljYW4tZG9sbGFyLWNvaW5zIiwicmVmIjoiaHR0cHM6Ly93d3cudXNtaW50Lmdvdi9sZWFybi9jb2lucy1hbmQtbWVkYWxzL2NpcmN1bGF0aW5nLWNvaW5zL2RvbGxhci1jb2lucyIsInV0bSI6W119~v11.sla~1776185494020~v11.wss~1776185494022~lcw~1776186430746"
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

url = "https://www.usmint.gov/learn/coins-and-medals/circulating-coins/nickel"
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

try:
    master_df = pd.read_csv(CSV_ARCHIVE)
    existing_gcs_paths = set(master_df['gcs_path'].dropna().values)
except:
    existing_gcs_paths = set()

csv_rows = []
downloaded_count = 0

for link in links:
    filename = link.split('/')[-1]
    
    if 'nickel' not in filename.lower() and 'jefferson' not in filename.lower() and 'monticello' not in filename.lower():
        continue
        
    gcs_path = f"reference_library/bulk_programs/nickel/{filename}"
    if gcs_path in existing_gcs_paths:
        continue # skip ones we already have
        
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
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(local_path)
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{gcs_path}"
        
        # Parse names
        csv_rows.append({
            'denomination': 'Five Cents',
            'year': filename[:4] if filename[:4].isdigit() else "Varied",
            'side': 'reverse' if 'reverse' in filename.lower() else 'obverse',
            'source': 'us_mint_archive',
            'category': 'Circulation',
            'tags': "Nickel",
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
    print(f"Staged {len(csv_rows)} specific linkages ready for append.")
    try:
        master_df = pd.read_csv(CSV_ARCHIVE)
        master_df = pd.concat([master_df, staging_df], ignore_index=True)
        master_df.to_csv(CSV_ARCHIVE, index=False)
        print("Master CSV updated!")
    except Exception as e:
        print(f"Could not append to master: {e}")
else:
    print("No valid linkages created. All found assets already exist in the CSV.")

print(f"Phase 2 and 3 executed for Nickel re-fetch. {downloaded_count} physical assets processed.")
