import os
import urllib.request
import re
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from google.cloud import storage
import time

BASE_DIR = r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images\US Mint\Bulk_Scrape\Commemoratives_All"
os.makedirs(BASE_DIR, exist_ok=True)
CSV_ARCHIVE = r"C:\Users\ericd\Documents\MyVertexProject\reference_library_export.csv"
BUCKET_NAME = "numista-reference-library"

COOKIES = "dwanonymous_b2cf918be9f3733e2d19f7e7beb4b6d7=bfSORPJwpNAdNU3a1qGbhncVuJ; _gcl_gs=2.1.k1$i1769457086$u255207436; _gcl_au=1.1.1031101466.1769457089; __cq_uuid=bfSORPJwpNAdNU3a1qGbhncVuJ; _ga=GA1.1.1077834011.1769457089; _fbp=fb.1.1769457089788.294347621354410369; _pin_unauth=dWlkPVpqUTVPRGN6WmpRdFpqa3paaTAwT0RFd0xXRmxOREF0TUdKalpqZG1aR0ZsTjJJdw; _gcl_aw=GCL.1769457111.Cj0KCQiAvtzLBhCPARIsALwhxdp_PjDfieajd6fpAa6NceOKLCWFaIRSBO2fqWH1Twd4FMD4G9fIXeEaAiWDEALw_wcB; _gcl_dc=GCL.1769457111.Cj0KCQiAvtzLBhCPARIsALwhxdp_PjDfieajd6fpAa6NceOKLCWFaIRSBO2fqWH1Twd4FMD4G9fIXeEaAiWDEALw_wcB; a1ashgd=tyddtw7bc4n00000tyddtw7bc4n00000; cqcid=bfSORPJwpNAdNU3a1qGbhncVuJ; __cq_dnt=0; dw_dnt=0; AMCVS_7A9335DD5CF935CA0A495FCD%40AdobeOrg=1; s_cc=true; cebs=1; _ce.clock_data=-58%2C24.246.138.41%2C1%2C91e1a2a41c0741f7f47615ab9de2fb8a%2CChrome%2CUS; dwsid=ft4G18N-VkMRAIjwjUu3NTqHT3mWTwj-2PEVpT1SKuZZOHNSwXVqe9ZrQ4mgcq1XljLUj-twfW64DbZiU1kZvg==; dwac_bcKmAiaageu6saaadbf1J7A92a=o096uJdr5CK_b5LTXuS6c94yZPDDcMpE0pA%3D|dw-only|USM13657498||USD|false|US%2FEastern|true; cquid=mK/4fKoufV2kYk1maHags5S0Ep914WfGI+GwqXDCdL0=|b83980aaac7d5af452acc14bc7123cafaeef222883452604c32fa5ec561f6061|b83980aaac7d5af452acc14bc7123cafaeef222883452604c32fa5ec561f6061; sid=RX9aqNaaXFIyDILlaF8RjgEmEwaDqwLv-_0; AMCV_7A9335DD5CF935CA0A495FCD%40AdobeOrg=179643557%7CMCIDTS%7C20558%7CMCMID%7C08909863047730330722103480248485599599%7CMCAAMLH-1776788515%7C7%7CMCAAMB-1776788515%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1776190915s%7CNONE%7CMCSYNCSOP%7C411-20487%7CvVersion%7C5.5.0; QSI_SI_DFYLmpo864lbgXf_intercept=true; cf_clearance=OR22cFMQE2St4zLJDk1i89.vqdwJqTpAQC2FH6GjqnU-1776188246-1.2.1.1-Bv930mkFSnjoPidloA2O6KCBMTREyKjuLXmcdIhjWWsud0Rn2xBQQqLNTZuEXj6Bp7iMj6pR04B8Gpk.Bf4YMPlJPBzzeAq7g194KigGKPQcUwwOXuF_kl2WJdavFnyLXGLRg9XM4SUePy.P87yegn1IblTrvf6NslE5fJQWrND4Cq6EGWuanMmjPvDqJzbjmaZVr9O2vtHoYuWSleNs6rkoV50wr666S5s9ALtzs.zeJ5l7cLIc4gHGqRxJtWn5icQcx5mrA7UPi.lDk1QxOrKq3YF8k4o1SiY9KcMOt6gca4wzeTXgWW9n8e8yAk7eqtspPxtSzT0_mumTK0v9zg; __cq_bc=%7B%22aarb-USM%22%3A%5B%7B%22id%22%3A%2226BM1%22%7D%2C%7B%22id%22%3A%2226EA%22%7D%2C%7B%22id%22%3A%22429%22%7D%2C%7B%22id%22%3A%2226BM4%22%7D%2C%7B%22id%22%3A%22MASTER_SEMIQMC%22%7D%5D%7D; __cq_seg=0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00; __cfwaitingroom=ChhEMHVXQ3ZPTzh3RjlTUWlIazEyYkVnPT0SgAJPaFVzbDNIampkNFZ2aWFxRHhsNUJJVUlqcWhuVHlnY1VaSkhZejNKWk15UDNyVFh4NVBZRGs1N0NhZlN0cWE2dW5heHF5VmxtYUJBb2pvdURrOHlLT24zVzZSNVE5TnJuQTNHVkJLbHc5K2tjQjZ2MU9ITXhOUGhsL0NFSE1lcmx2RkYyQ1BiVTRvbkVGQnprSjl6MzRGM0lWL2xHY01CbVhaU2lObVBzaE9GRXl0OVdoWm5oU3JJb2lNRjBzU0ZSRVVzaldFQk4wdmlQTUh0a2ZLZWZ6TStSVjJJVkplSFNybkNlckpEQ1B2UXJRVzJKV0hiQnliSkpYWUljeWFm; AWSALB=4lEuEmSKSBvSjwNKZBofIpO63cVcy8w/0rFZGIOOEEHJBEn6wFFXzRXMZi+pvV8Jyv5P3ki5wEM4iCQRcaWI/vJUnJt46VQ26Czr4CVdTuHj7o8cwHK3NfC/Xfb0; AWSALBCORS=4lEuEmSKSBvSjwNKZBofIpO63cVcy8w/0rFZGIOOEEHJBEn6wFFXzRXMZi+pvV8Jyv5P3ki5wEM4iCQRcaWI/vJUnJt46VQ26Czr4CVdTuHj7o8cwHK3NfC/Xfb0; __cf_bm=_Cu4btna_DDG2xGmiV8gtc7Dw8REtZyoxmnxJqySA1c-1776188531.2109878-1.0.1.1-wS1MvdbUlsoB511hksEEPhIrL64BudtYp9oz0bMgobCkE6.i.Wb3jFPi9LTF9cUMszFNT1B1Drm9m0vJlZ6OMcJwnfZf7VesLEAlLY8o8A39fO00aSL0yXHMeWPTdAWean_Pmukng0HCw4F83c_cKA; _rdt_uuid=1769457089327.4df2ebdc-15ff-4b34-9ae8-d6e2096a5dc9; _uetsid=3c29db20380d11f1bd682500d035356d; _uetvid=683d4bb0faf011f09ddaef7abf1922b0; s_sq=%5B%5BB%5D%5D; cebsp_=109; _ga_804PW1F121=GS2.1.s1776176491$o5$g1$t1776188531$j38$l0$h0; _ce.s=v~aa565285b5c7305eeae8f9fe831b92ff8fe2c1d7~lcw~1776188541828~vir~new~lva~1776188536103~vpv~3~v11ls~98b816b0-3826-11f1-a507-dd71752e2e01~gtrk.la~mnywsy6h~v11.cs~226228~v11.s~98b816b0-3826-11f1-a507-dd71752e2e01~v11.vs~aa565285b5c7305eeae8f9fe831b92ff8fe2c1d7~v11.fsvd~eyJub3RNb2RpZmllZFVybCI6Imh0dHBzOi8vd3d3LnVzbWludC5nb3YvbGVhcm4vY29pbnMtYW5kLW1lZGFscy9jb2xsZWN0aWJsZS1jb2lucyIsInVybCI6InVzbWludC5nb3YvbGVhcm4vY29pbnMtYW5kLW1lZGFscy9jb2xsZWN0aWJsZS1jb2lucyIsInJlZiI6Imh0dHBzOi8vd3d3LnVzbWludC5nb3YvbGVhcm4vY29pbnMtYW5kLW1lZGFscy9jb2xsZWN0aWJsZS1jb2lucy9hbWVyaWNhbi1pbm5vdmF0aW9uLWRvbGxhci1jb2lucyIsInV0bSI6W119~v11.sla~1776187384741~v11.wss~1776187384743~lcw~1776188552201"
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

# STEP 1: Gather all subpages
index_url = "https://www.usmint.gov/learn/coins-and-medals/commemorative-coins"
print(f"Fetching Parent Node: {index_url}...")
try:
    req = urllib.request.Request(index_url, headers=HEADERS)
    html = urllib.request.urlopen(req).read().decode('utf-8')
except Exception as e:
    print(f"Failed to fetch {index_url}: {e}")
    exit(1)

subpages_abs = set(re.findall(r'href="(https://www.usmint.gov/learn/coins-and-medals/commemorative-coins/[^\"]+)"', html, re.I))
subpages_rel = set(re.findall(r'href="(/learn/coins-and-medals/commemorative-coins/[^\"]+)"', html, re.I))

subpages = list(subpages_abs)
for s in subpages_rel:
    abs_url = "https://www.usmint.gov" + s
    if abs_url not in subpages:
        subpages.append(abs_url)

print(f"Discovered {len(subpages)} Commemorative sub-programs capable of deep crawl.")

# STEP 2: Scrape them all
client = storage.Client()
bucket = client.bucket(BUCKET_NAME)

try:
    master_df = pd.read_csv(CSV_ARCHIVE)
    existing_gcs_paths = set(master_df['gcs_path'].dropna().values)
except:
    existing_gcs_paths = set()

csv_rows = []
downloaded_count = 0
processed_links = set() # Avoid downloading the same exact image across subpages

for url in subpages:
    print(f"\nCrawling subpage: {url}")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        sub_html = urllib.request.urlopen(req).read().decode('utf-8')
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        continue
        
    links = set(re.findall(r'(/content/dam/usmint/[^\'\"\?]+\.jpg)', sub_html, re.I | re.MULTILINE))
    links = [f"https://www.usmint.gov{l}" for l in links if '150x' not in l and '300x' not in l and '500x' not in l]

    for link in links:
        if link in processed_links:
            continue
        processed_links.add(link)
        
        filename = urllib.parse.unquote(link.split('/')[-1])
            
        gcs_path = f"reference_library/bulk_programs/commemoratives_all/{filename}"
        
        if gcs_path in existing_gcs_paths:
            print(f"Skipping {filename} (Already in GCS Master)")
            continue
            
        local_path = os.path.join(BASE_DIR, filename)
        print(f"Extracting {filename}...")
        try:
            safe_link = link.replace(' ', '%20').replace('', '')
            img_req = urllib.request.Request(safe_link, headers=HEADERS)
            with urllib.request.urlopen(img_req) as resp:
                with open(local_path, 'wb') as out_f:
                    out_f.write(resp.read())
            apply_watermark(local_path)
            downloaded_count += 1
            
            # Deploy to GCS
            blob = bucket.blob(gcs_path)
            blob.upload_from_filename(local_path)
            public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{urllib.parse.quote(gcs_path)}"
            
            # Determine Denomination
            denom = 'Varied'
            if 'half' in filename.lower():
                denom = 'Half Dollar'
            elif 'dollar' in filename.lower() and 'half' not in filename.lower():
                denom = 'One Dollar'
            elif 'five' in filename.lower():
                denom = 'Five Dollars'
                
            # Parse names
            csv_rows.append({
                'denomination': denom,
                'year': filename[:4] if filename[:4].isdigit() else "Varied",
                'side': 'reverse' if 'reverse' in filename.lower() else 'obverse',
                'source': 'us_mint_archive',
                'category': 'Commemorative',
                'tags': "Commemorative",
                'gcs_url': public_url,
                'gcs_path': gcs_path,
                'attribution': 'U.S. Mint',
                'license': 'Public Domain',
                'filename': filename,
                'source_name': 'usmint.gov'
            })
                
        except Exception as e:
            print(f"Failed extraction on {safe_link}: {e}")
            
    # Small sleep so we don't hammer the WAF too aggressively
    time.sleep(1)

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
    print("\nNo valid linkages created. All found assets already exist in the CSV.")

print(f"Phase 2 and 3 executed for ALL COMMEMORATIVES. {downloaded_count} physical assets processed.")
