# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import os
import urllib.request
import re
import time
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from google.cloud import storage

BASE_DIR = r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images\US Mint\Bulk_Scrape\Presidential"
os.makedirs(BASE_DIR, exist_ok=True)
CSV_ARCHIVE = r"C:\Users\ericd\Documents\MyVertexProject\reference_library_export.csv"
BUCKET_NAME = "numista-reference-library"

COOKIES = "dwanonymous_b2cf918be9f3733e2d19f7e7beb4b6d7=bfSORPJwpNAdNU3a1qGbhncVuJ; _gcl_gs=2.1.k1$i1769457086$u255207436; _gcl_au=1.1.1031101466.1769457089; __cq_uuid=bfSORPJwpNAdNU3a1qGbhncVuJ; _ga=GA1.1.1077834011.1769457089; _fbp=fb.1.1769457089788.294347621354410369; _pin_unauth=dWlkPVpqUTVPRGN6WmpRdFpqa3paaTAwT0RFd0xXRmxOREF0TUdKalpqZG1aR0ZsTjJJdw; _gcl_aw=GCL.1769457111.Cj0KCQiAvtzLBhCPARIsALwhxdp_PjDfieajd6fpAa6NceOKLCWFaIRSBO2fqWH1Twd4FMD4G9fIXeEaAiWDEALw_wcB; _gcl_dc=GCL.1769457111.Cj0KCQiAvtzLBhCPARIsALwhxdp_PjDfieajd6fpAa6NceOKLCWFaIRSBO2fqWH1Twd4FMD4G9fIXeEaAiWDEALw_wcB; a1ashgd=tyddtw7bc4n00000tyddtw7bc4n00000; cqcid=bfSORPJwpNAdNU3a1qGbhncVuJ; __cq_dnt=0; dw_dnt=0; AMCVS_7A9335DD5CF935CA0A495FCD%40AdobeOrg=1; s_cc=true; cebs=1; _ce.clock_data=-58%2C24.246.138.41%2C1%2C91e1a2a41c0741f7f47615ab9de2fb8a%2CChrome%2CUS; __cq_seg=0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00; __cq_bc=%7B%22aarb-USM%22%3A%5B%7B%22id%22%3A%22MASTER_SEMIQMC%22%7D%5D%7D; dwsid=ft4G18N-VkMRAIjwjUu3NTqHT3mWTwj-2PEVpT1SKuZZOHNSwXVqe9ZrQ4mgcq1XljLUj-twfW64DbZiU1kZvg==; dwac_bcKmAiaageu6saaadbf1J7A92a=o096uJdr5CK_b5LTXuS6c94yZPDDcMpE0pA%3D|dw-only|USM13657498||USD|false|US%2FEastern|true; cquid=mK/4fKoufV2kYk1maHags5S0Ep914WfGI+GwqXDCdL0=|b83980aaac7d5af452acc14bc7123cafaeef222883452604c32fa5ec561f6061|b83980aaac7d5af452acc14bc7123cafaeef222883452604c32fa5ec561f6061; sid=RX9aqNaaXFIyDILlaF8RjgEmEwaDqwLv-_0; AMCV_7A9335DD5CF935CA0A495FCD%40AdobeOrg=179643557%7CMCIDTS%7C20558%7CMCMID%7C08909863047730330722103480248485599599%7CMCAAMLH-1776788515%7C7%7CMCAAMB-1776788515%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1776190915s%7CNONE%7CMCSYNCSOP%7C411-20487%7CvVersion%7C5.5.0; cf_clearance=z6EX43B5Mui_qmHnJYCHT29UNGj6h2v.HNTPbAEd7tk-1776185100-1.2.1.1-wvpOAiiSdEox2e2GMJ.Sys.AXM8aLADUSTnqVWMhiEiQ7co5P1EDiplkKlB92Xp2RGlOmTjIRsMw5Cy3t4mWsfc.pNuA8YGlWZM2QzSJnq4mcbsALbON4fxRd8dH3ca94bsHI0tvRpujw12EFiQf9mOz2prOezI9ALH9_dEzl_ooJBeEt5o9cUGI1vw4WmbBQeGHxiIRn71JCy7vdUtrM0ocpLhCfTDPvgTnCwePRk2wuPZeP666chUeY_jTuCG4nIueagZaHAcSNKHwmh0YDehL20_b.qbhB6rAxUbg07GaW4NBFV.yhurDafgcU8F8aHAobMowgc8Xt_PcRU1HNg; __cf_bm=WaoPmUSwOkvpw7whOfY5PuyEB2LT0azd03hd5qTcZNE-1776185493.8099806-1.0.1.1-h46ANW653hGZy4pWt7FiDiLGkmhaw7VnIqVI5u6WbhrhQDWsoJNoPN8CgOGF2MQ.fndnqyxLbadsET3yleVVd1J59QiRS_TH7eujmdlWtL3KO5XVTSHDm0N.a_yqt4w_cpWFxbV0cvvLNwf0SZUk8g; AWSALB=qId/nUmVyESG4v5saVJjAnQiWSK3F/1no9lu7HzeDVViBES64PINNz0tYlEaUwFPf4XJsrW9GsVpRLa/DGsZzsu9hez0bhVnXVQcHVmr/bDgD2uIvNmBErmhhxnn; AWSALBCORS=qId/nUmVyESG4v5saVJjAnQiWSK3F/1no9lu7HzeDVViBES64PINNz0tYlEaUwFPf4XJsrW9GsVpRLa/DGsZzsu9hez0bhVnXVQcHVmr/bDgD2uIvNmBErmhhxnn; s_sq=%5B%5BB%5D%5D; _uetsid=3c29db20380d11f1bd682500d035356d; _uetvid=683d4bb0faf011f09ddaef7abf1922b0; _rdt_uuid=1769457089327.4df2ebdc-15ff-4b34-9ae8-d6e2096a5dc9; cebsp_=58; _ga_804PW1F121=GS2.1.s1776176491$o5$g1$t1776185507$j45$l0$h0; _ce.s=v~aa565285b5c7305eeae8f9fe831b92ff8fe2c1d7~lcw~1776185518992~vir~new~lva~1776185111765~vpv~3~v11ls~31c31cb0-3822-11f1-a2f0-0bd4f98e222c~gtrk.la~mnyv06ev~v11.cs~226228~v11.s~31c31cb0-3822-11f1-a2f0-0bd4f98e222c~v11.vs~aa565285b5c7305eeae8f9fe831b92ff8fe2c1d7~v11.fsvd~eyJub3RNb2RpZmllZFVybCI6Imh0dHBzOi8vd3d3LnVzbWludC5nb3YvbGVhcm4vY29pbnMtYW5kLW1lZGFscy9jb2xsZWN0aWJsZS1jb2lucy9uYXRpdmUtYW1lcmljYW4tZG9sbGFyLWNvaW5zI2FjY29yZGlvbi1iMGQ5Y2UyYzIyLWl0ZW0tMGM4N2YzNjhjZiIsInVybCI6InVzbWludC5nb3YvbGVhcm4vY29pbnMtYW5kLW1lZGFscy9jb2xsZWN0aWJsZS1jb2lucy9uYXRpdmUtYW1lcmljYW4tZG9sbGFyLWNvaW5zIiwicmVmIjoiaHR0cHM6Ly93d3cudXNtaW50Lmdvdi9sZWFybi9jb2lucy1hbmQtbWVkYWxzL2NpcmN1bGF0aW5nLWNvaW5zL2RvbGxhci1jb2lucyIsInV0bSI6W119~v11.sla~1776185494020~v11.wss~1776185494022~lcw~1776185530231"
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

# Step 1: Scrape the main index
main_url = "https://www.usmint.gov/learn/coins-and-medals/collectible-coins/presidential-dollar-coins"
print(f"Fetching Main Index: {main_url}")
try:
    req = urllib.request.Request(main_url, headers=HEADERS)
    html = urllib.request.urlopen(req).read().decode('utf-8')
except Exception as e:
    print(f"Failed to fetch {main_url}: {e}")
    exit(1)

# Find child president pages
president_links = set(re.findall(r'href=[\'\"](/learn/coins-and-medals/presidential-dollar-coin/[^\'\"]+)[\'\"]', html, re.I))
president_links = [f"https://www.usmint.gov{l}" for l in president_links]

print(f"Discovered {len(president_links)} individual President pages.")

client = storage.Client()
bucket = client.bucket(BUCKET_NAME)

csv_rows = []
downloaded_count = 0
seen_files = set()

# Load master beforehand
try:
    master_df = pd.read_csv(CSV_ARCHIVE)
    existing_gcs_paths = set(master_df['gcs_path'].dropna().values)
except:
    existing_gcs_paths = set()

for i, link in enumerate(president_links):
    print(f"[{i+1}/{len(president_links)}] Scanning {link}...")
    try:
        preq = urllib.request.Request(link, headers=HEADERS)
        phtml = urllib.request.urlopen(preq).read().decode('utf-8')
    except Exception as e:
        print(f"  Failed: {e}")
        continue
    
    img_links = set(re.findall(r'(/content/dam/usmint/[^\'\"\?]+\.jpg)', phtml, re.I))
    img_links = [f"https://www.usmint.gov{il}" for il in img_links if '150x' not in il and '300x' not in il and '500x' not in il]
    
    for ilink in img_links:
        filename = ilink.split('/')[-1]
        
        # Don't download duplicates or non-presidential things that bleed in
        if filename in seen_files:
            continue
        if 'presidential' not in filename.lower() and 'dollar' not in filename.lower() and 'obverse' not in filename.lower():
            continue
            
        gcs_path = f"reference_library/bulk_programs/presidential/{filename}"
        if gcs_path in existing_gcs_paths:
            seen_files.add(filename)
            continue
            
        local_path = os.path.join(BASE_DIR, filename)
        
        try:
            ireq = urllib.request.Request(ilink, headers=HEADERS)
            with urllib.request.urlopen(ireq) as resp:
                with open(local_path, 'wb') as out_f:
                    out_f.write(resp.read())
            
            apply_watermark(local_path)
            downloaded_count += 1
            seen_files.add(filename)
            
            # Deploy to GCS
            blob = bucket.blob(gcs_path)
            blob.upload_from_filename(local_path)
            public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{gcs_path}"
            
            # Parse names
            csv_rows.append({
                'denomination': 'One Dollar',
                'year': filename[:4] if filename[:4].isdigit() else "Varied",
                'side': 'reverse' if 'reverse' in filename.lower() else 'obverse',
                'source': 'us_mint_archive',
                'category': 'Circulation',
                'tags': "Presidential Dollar",
                'gcs_url': public_url,
                'gcs_path': gcs_path,
                'attribution': 'U.S. Mint',
                'license': 'Public Domain',
                'filename': filename,
                'source_name': 'usmint.gov'
            })
            print(f"    -> Harvested {filename}")
        except Exception as ex:
            print(f"    -> Warning: Failed to extract {filename}: {ex}")
            
    time.sleep(0.5)

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
    print("\nNo new valid linkages created.")

print(f"Phase 2 and 3 executed recursively for Presidential Dollars. {downloaded_count} new physical assets processed.")
