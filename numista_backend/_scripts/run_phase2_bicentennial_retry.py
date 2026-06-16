import os
import urllib.request
import re
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from google.cloud import storage

BASE_DIR = r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images\US Mint\Bulk_Scrape\Bicentennial_Retry_2"
os.makedirs(BASE_DIR, exist_ok=True)
CSV_ARCHIVE = r"C:\Users\ericd\Documents\MyVertexProject\reference_library_export.csv"
BUCKET_NAME = "numista-reference-library"

COOKIES = "dwanonymous_b2cf918be9f3733e2d19f7e7beb4b6d7=bfSORPJwpNAdNU3a1qGbhncVuJ; _gcl_gs=2.1.k1$i1769457086$u255207436; _gcl_au=1.1.1031101466.1769457089; __cq_uuid=bfSORPJwpNAdNU3a1qGbhncVuJ; _ga=GA1.1.1077834011.1769457089; _fbp=fb.1.1769457089788.294347621354410369; _pin_unauth=dWlkPVpqUTVPRGN6WmpRdFpqa3paaTAwT0RFd0xXRmxOREF0TUdKalpqZG1aR0ZsTjJJdw; _gcl_aw=GCL.1769457111.Cj0KCQiAvtzLBhCPARIsALwhxdp_PjDfieajd6fpAa6NceOKLCWFaIRSBO2fqWH1Twd4FMD4G9fIXeEaAiWDEALw_wcB; _gcl_dc=GCL.1769457111.Cj0KCQiAvtzLBhCPARIsALwhxdp_PjDfieajd6fpAa6NceOKLCWFaIRSBO2fqWH1Twd4FMD4G9fIXeEaAiWDEALw_wcB; a1ashgd=tyddtw7bc4n00000tyddtw7bc4n00000; cqcid=bfSORPJwpNAdNU3a1qGbhncVuJ; __cq_dnt=0; dw_dnt=0; AMCVS_7A9335DD5CF935CA0A495FCD%40AdobeOrg=1; s_cc=true; cebs=1; _ce.clock_data=-58%2C24.246.138.41%2C1%2C91e1a2a41c0741f7f47615ab9de2fb8a%2CChrome%2CUS; __cq_seg=0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00; dwsid=ft4G18N-VkMRAIjwjUu3NTqHT3mWTwj-2PEVpT1SKuZZOHNSwXVqe9ZrQ4mgcq1XljLUj-twfW64DbZiU1kZvg==; dwac_bcKmAiaageu6saaadbf1J7A92a=o096uJdr5CK_b5LTXuS6c94yZPDDcMpE0pA%3D|dw-only|USM13657498||USD|false|US%2FEastern|true; cquid=mK/4fKoufV2kYk1maHags5S0Ep914WfGI+GwqXDCdL0=|b83980aaac7d5af452acc14bc7123cafaeef222883452604c32fa5ec561f6061|b83980aaac7d5af452acc14bc7123cafaeef222883452604c32fa5ec561f6061; sid=RX9aqNaaXFIyDILlaF8RjgEmEwaDqwLv-_0; AMCV_7A9335DD5CF935CA0A495FCD%40AdobeOrg=179643557%7CMCIDTS%7C20558%7CMCMID%7C08909863047730330722103480248485599599%7CMCAAMLH-1776788515%7C7%7CMCAAMB-1776788515%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1776190915s%7CNONE%7CMCSYNCSOP%7C411-20487%7CvVersion%7C5.5.0; QSI_SI_DFYLmpo864lbgXf_intercept=true; cf_clearance=dapLusQhmHkCbK.H5efuenuKXuH.snkHn5m9EXxp9zU-1776186955-1.2.1.1-X3kjkc9oRyEFZKa8ZzIOPK4DFtvau9JzKF3ezeH72gy12jQo_qT9mQ98RLCMo3rFLuBJh092J90wZxrkHZPV9Uj7QEPdqK4MT5gAnLbR8VtWgv.xLw0dpq3mna8hP86XFqsrV.e7tBMeInncM1Hs8ErYE7BF5bk9dMOn92U4jqlY2cPNHVhmOfg1kdJz7rKFIC_vATmY.9fdsEcC3BsCSGi25Tv.Anr18ZTKypbXtSfdYFhGyHAVfcWF_x3qtwK7hrh_o.R7mf6kE4W7K5motY6KnrP3tykXToFkfUKZhnFIN7yyi_.7UEpSp_onpgZezkcJ9yUqiyqy2ARer8kjhw; __cf_bm=SyB0T5ZizAuGBTIHLPhbCnVWPyIcMQr3o1uAP6.bD0E-1776187419.5104747-1.0.1.1-yahgC.hVq_c3NmCMvzUyOeHi5dbAg49w0itV.3n0oGkjw4R5fLTCWWF8Bj0xCHTP9cQhTkCX83XJmxbMByT1NCcTiqrK_YGkDrnK92irwlAD1Xb9.r5pCaxFHq_gZxnXAQ9UfhnIrHzRGJCLC2LQYQ; s_sq=%5B%5BB%5D%5D; __cfwaitingroom=ChhZeU1JY2pidkZld056WHF6WjBMU3VnPT0SgAJWK0pSSktzQVpNU3pnWE5HckROb1FWRGw0WTJ3MmM4V2svcFdjaU4wRTQ1M2lwcWRQSk4rdHJZeEVHSmRTcDhnSTNhWlYyOXlLZk5zUWdhOGJ2a3pXL29GaTR5RWdRdmk2NmRtWmFoa1RLbU82V1Bqb0pwZU5JdGxiMEhRWGsvZyt0NUhMMzQyTytWUitjdFNURnNnam9GQm13dTdnb080eWoxL2Z1TnNCQWZpNzB3Vk5lenZFZWtjMyttQjd2WFlZVnk1bDRiaEh4Zmxtb3lCSTZyMVRPa2RyREplQVg5bWM2ditHd3Y3UmRJM3M0WHZSdytkampIaXorSWVOZGdj; __cq_bc=%7B%22aarb-USM%22%3A%5B%7B%22id%22%3A%22429%22%7D%2C%7B%22id%22%3A%2226BM4%22%7D%2C%7B%22id%22%3A%2226EA%22%7D%2C%7B%22id%22%3A%22MASTER_SEMIQMC%22%7D%5D%7D; _rdt_uuid=1769457089327.4df2ebdc-15ff-4b34-9ae8-d6e2096a5dc9; _uetsid=3c29db20380d11f1bd682500d035356d; _uetvid=683d4bb0faf011f09ddaef7abf1922b0; cebsp_=84; _ga_804PW1F121=GS2.1.s1776176491$o5$g1$t1776187553$j42$l0$h0; AWSALB=mAPEXM5qONtdt/7k/F8QL1Z54wQAsB+GZxZuwJQxnzDu9kiTjZs5BulcPfJQ6TYj8/SLYb93UDN7ZN2cNvpky8HhhAP2MgVgj0HK/3eQ+Iqc/IGe/xjT7JdGrsUO; AWSALBCORS=mAPEXM5qONtdt/7k/F8QL1Z54wQAsB+GZxZuwJQxnzDu9kiTjZs5BulcPfJQ6TYj8/SLYb93UDN7ZN2cNvpky8HhhAP2MgVgj0HK/3eQ+Iqc/IGe/xjT7JdGrsUO; _ce.s=v~aa565285b5c7305eeae8f9fe831b92ff8fe2c1d7~lcw~1776187790907~vir~new~lva~1776187535299~vpv~3~v11ls~31c31cb0-3822-11f1-a2f0-0bd4f98e222c~gtrk.la~mnywd2iw~v11.cs~226228~v11.s~98b816b0-3826-11f1-a507-dd71752e2e01~v11.vs~aa565285b5c7305eeae8f9fe831b92ff8fe2c1d7~v11.fsvd~eyJub3RNb2RpZmllZFVybCI6Imh0dHBzOi8vd3d3LnVzbWludC5nb3YvbGVhcm4vY29pbnMtYW5kLW1lZGFscy9jb2xsZWN0aWJsZS1jb2lucyIsInVybCI6InVzbWludC5nb3YvbGVhcm4vY29pbnMtYW5kLW1lZGFscy9jb2xsZWN0aWJsZS1jb2lucyIsInJlZiI6Imh0dHBzOi8vd3d3LnVzbWludC5nb3YvbGVhcm4vY29pbnMtYW5kLW1lZGFscy9jb2xsZWN0aWJsZS1jb2lucy9hbWVyaWNhbi1pbm5vdmF0aW9uLWRvbGxhci1jb2lucyIsInV0bSI6W119~v11.sla~1776187384741~v11.wss~1776187384743~lcw~1776187811336"
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

url = "https://www.usmint.gov/learn/coins-and-medals/bicentennial-coins-and-medals"
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
    gcs_path = f"reference_library/bulk_programs/bicentennial/{filename}"
    
    # We will STILL check existing_gcs_paths because if we re-download the exact
    # same file, we shouldn't append a duplicate row to the CSV.
    if gcs_path in existing_gcs_paths:
        continue
        
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
            'denomination': 'Varied',
            'year': filename[:4] if filename[:4].isdigit() else "1976",
            'side': 'reverse' if 'reverse' in filename.lower() else 'obverse',
            'source': 'us_mint_archive',
            'category': 'Circulation',
            'tags': "Bicentennial",
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

print(f"Phase 2 and 3 executed for Bicentennial Retry 2. {downloaded_count} physical assets processed.")
