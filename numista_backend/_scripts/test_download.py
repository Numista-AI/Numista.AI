# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import os
import urllib.request
import re
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images\US Mint"
os.makedirs(BASE_DIR, exist_ok=True)

obverse_filename = "2026_quarter_dollar_revolutionary_war_obverse.jpg"
reverse_filename = "2026_quarter_dollar_revolutionary_war_reverse.jpg"

obverse_path = os.path.join(BASE_DIR, obverse_filename)
reverse_path = os.path.join(BASE_DIR, reverse_filename)

MEDIA_KIT_URL = "https://www.usmint.gov/coins/coin-programs/semiquincentennial/"
COOKIES = "dwanonymous_b2cf918be9f3733e2d19f7e7beb4b6d7=bfSORPJwpNAdNU3a1qGbhncVuJ; _gcl_gs=2.1.k1$i1769457086$u255207436; _gcl_au=1.1.1031101466.1769457089; __cq_uuid=bfSORPJwpNAdNU3a1qGbhncVuJ; _ga=GA1.1.1077834011.1769457089; _fbp=fb.1.1769457089788.294347621354410369; _pin_unauth=dWlkPVpqUTVPRGN6WmpRdFpqa3paaTAwT0RFd0xXRmxOREF0TUdKalpqZG1aR0ZsTjJJdw; _gcl_aw=GCL.1769457111.Cj0KCQiAvtzLBhCPARIsALwhxdp_PjDfieajd6fpAa6NceOKLCWFaIRSBO2fqWH1Twd4FMD4G9fIXeEaAiWDEALw_wcB; _gcl_dc=GCL.1769457111.Cj0KCQiAvtzLBhCPARIsALwhxdp_PjDfieajd6fpAa6NceOKLCWFaIRSBO2fqWH1Twd4FMD4G9fIXeEaAiWDEALw_wcB; a1ashgd=tyddtw7bc4n00000tyddtw7bc4n00000; cqcid=bfSORPJwpNAdNU3a1qGbhncVuJ; __cq_dnt=0; dw_dnt=0; AMCVS_7A9335DD5CF935CA0A495FCD%40AdobeOrg=1; AMCV_7A9335DD5CF935CA0A495FCD%40AdobeOrg=179643557%7CMCIDTS%7C20558%7CMCMID%7C08909863047730330722103480248485599599%7CMCAAMLH-1776781291%7C7%7CMCAAMB-1776781291%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1776183691s%7CNONE%7CMCSYNCSOP%7C411-20487%7CvVersion%7C5.5.0; s_cc=true; cebs=1; _ce.clock_data=-58%2C24.246.138.41%2C1%2C91e1a2a41c0741f7f47615ab9de2fb8a%2CChrome%2CUS; __cq_seg=0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00; __cq_bc=%7B%22aarb-USM%22%3A%5B%7B%22id%22%3A%22MASTER_SEMIQMC%22%7D%5D%7D; AWSALB=WZ67zRGUYDOL4b+5d74sIAXsSJQF4E45rGHxn/7gjCTI6c9tI8csuXoo75DLpTndCi6ZureLz4mlXuO3S2bcwuBwiqUHBCJyvBlfPSYt5R389F0TiEjwqJuhrDgs; AWSALBCORS=WZ67zRGUYDOL4b+5d74sIAXsSJQF4E45rGHxn/7gjCTI6c9tI8csuXoo75DLpTndCi6ZureLz4mlXuO3S2bcwuBwiqUHBCJyvBlfPSYt5R389F0TiEjwqJuhrDgs; cf_clearance=5q9dVwLqyGBBF0KPxyK5GlIuPXzXEAGh2OzMSUcdgVc-1776178865-1.2.1.1-8CeaQlWTaR2OHLHyebJQ78l_Z5Pcik4EakV28Qu3LfTnoM2pccHMy0965lqkKto2sQcc5UcCt7alk.qdBxqHB.RTHM7MO7hexLa7XWTWA0PJMLF5obVHkFHLY_0tPn_p076ryDNY_jg.o48tQNgndl4CFZvriN0mRWOBK7MBTd4aebf8XaE5bAvFTEgitAHVbnf0GBgS7tVJKQlTNsBMvyBid4ZJaVwU8ewR682T50rWnIUE1wlFLpDe3ctXOOA2aRlSBv.n8su7SRMmFXkLVYebG2hjBecxbhIkoO1tzo2Cubw.I28Coh1edDztj08CnKlYGG8gEcsXUzv68Sc0HQ; __cf_bm=SFX6GWCnWreqkCxwmZuUXpExBzk3Bp75eMhV0JzF_qU-1776178865.6220028-1.0.1.1-nYWDYPd3hgx8qfsFuR5B281p0i7uuuOmg0QsTQd8tk2UTNkrFVYnV6bFprFi_Ma9efMzGnxkMVltJf2jrog8j7FPG6RdVxgiIfa.QR0282KUCZQgQ21qd9THbpM26eTIEb3KmYhNaFtjkjESIGXlmw; dwsid=ft4G18N-VkMRAIjwjUu3NTqHT3mWTwj-2PEVpT1SKuZZOHNSwXVqe9ZrQ4mgcq1XljLUj-twfW64DbZiU1kZvg==; dwac_bcKmAiaageu6saaadbf1J7A92a=o096uJdr5CK_b5LTXuS6c94yZPDDcMpE0pA%3D|dw-only|USM13657498||USD|false|US%2FEastern|true; cquid=mK/4fKoufV2kYk1maHags5S0Ep914WfGI+GwqXDCdL0=|b83980aaac7d5af452acc14bc7123cafaeef222883452604c32fa5ec561f6061|b83980aaac7d5af452acc14bc7123cafaeef222883452604c32fa5ec561f6061; sid=RX9aqNaaXFIyDILlaF8RjgEmEwaDqwLv-_0; _rdt_uuid=1769457089327.4df2ebdc-15ff-4b34-9ae8-d6e2096a5dc9; _uetsid=3c29db20380d11f1bd682500d035356d; _uetvid=683d4bb0faf011f09ddaef7abf1922b0; s_sq=%5B%5BB%5D%5D; cebsp_=15; _ga_804PW1F121=GS2.1.s1776176491$o5$g1$t1776179214$j60$l0$h0; __cfwaitingroom=ChhaeWdQVk1JY1FTc3pzcHZnRllXeXhnPT0SgAJ6bGZvc1hlMjAzeU5iVTNBcWpjTVh6WXhmUnY1cXNHRHlnKzZhZzdXN1lhVTVOU3RzVFNwdjVjS1p4azNvSnpGakZZcHpVR1loUDNyRDJZUDVOQXM5TjVhVmx2UlFDRlA4eXNZejhnTXNLREJzenU5anVDVFFYZEUwOVg3YVZhQWtCTFl5YkQxaU5qM09sRzdVK2dIa3A0cGRHUU15WHRwYnp6dFdLWWlySUhwWGhkUXRvdFVXbUd0UytKcHRneDhXdW5ublBIMkk1QzJsZDlDaGlzdDhSV2RVclFhMTRjeU9BZEljSnVEOFIzNXRFMW9razJXZ1d1eHA5RTdSVlRS; _ce.s=v~aa565285b5c7305eeae8f9fe831b92ff8fe2c1d7~lcw~1776179336748~vir~new~lva~1776179208678~vpv~3~v11ls~c35720f0-3812-11f1-853c-81b72bf83000~gtrk.la~mnyrc03n~v11.cs~226228~v11.s~c35720f0-3812-11f1-853c-81b72bf83000~v11.vs~aa565285b5c7305eeae8f9fe831b92ff8fe2c1d7~v11.fsvd~eyJub3RNb2RpZmllZFVybCI6Imh0dHBzOi8vd3d3LnVzbWludC5nb3YvYWNjb3VudC1sb2dpbiIsInVybCI6InVzbWludC5nb3YvYWNjb3VudC1sb2dpbiIsInJlZiI6Imh0dHBzOi8vd3d3LnVzbWludC5nb3YvbmV3cy9tZWRpYS1raXQvc2VtaXEtcmVzb3VyY2VzIiwidXRtIjpbXX0%3D~v11.sla~1776178866309~v11.wss~1776178866310~lcw~1776179363460"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Cookie': COOKIES,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Referer': 'https://www.google.com/'
}

print(f"Fetching: {MEDIA_KIT_URL}")
try:
    req = urllib.request.Request(MEDIA_KIT_URL, headers=HEADERS)
    html = urllib.request.urlopen(req).read().decode('utf-8')
except Exception as e:
    print(f"Error fetching URL: {e}")
    exit(1)

# Look for links targeting Revolutionary War Quarter images
matches = re.findall(r'(src|href)=["\']([^"\']+\.jpe?g)["\']', html, re.I)
hires_links = [m[1] for m in matches]

obv_url = None
rev_url = None

for link in hires_links:
    link_lower = link.lower()
    if 'revolutionary' in link_lower or 'quarter' in link_lower:
        full_link = link if link.startswith('http') else 'https://www.usmint.gov' + link
        # avoid thumbnails if possible
        if '300x' not in link_lower and '150x' not in link_lower:
            if 'obv' in link_lower or 'heads' in link_lower:
                obv_url = full_link
            elif 'rev' in link_lower or 'tails' in link_lower:
                rev_url = full_link

# Fallback hardcoded URLs
if not obv_url:
    obv_url = "https://www.usmint.gov/wordpress/wp-content/uploads/2024/09/2026-semiquincentennial-proof-quarter-revolutionary-war-obverse-hi-res.jpg"
if not rev_url:
    rev_url = "https://www.usmint.gov/wordpress/wp-content/uploads/2024/09/2026-semiquincentennial-proof-quarter-revolutionary-war-reverse-hi-res.jpg"

def download_and_watermark(url, save_path):
    print(f"Downloading {url} ...")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req) as response:
            with open(save_path, 'wb') as out_file:
                out_file.write(response.read())
                
        # Watermark
        img = Image.open(save_path)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", int(img.size[1]*0.015))
        except:
            font = ImageFont.load_default()
            
        text = "U.S. Mint"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        padding = int(img.size[0] * 0.02)
        x = img.size[0] - text_w - padding
        y = img.size[1] - text_h - padding
        
        draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0, 100))
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 180))
        
        img.save(save_path, quality=95)
        print(f"Saved and watermarked to {save_path}")
        return True
    except Exception as e:
        print(f"Failed processing {url}: {e}")
        return False

success_obv = download_and_watermark(obv_url, obverse_path)
success_rev = download_and_watermark(rev_url, reverse_path)

if success_obv and success_rev:
    print("Test download and processing successful!")
else:
    print("Test failed.")
