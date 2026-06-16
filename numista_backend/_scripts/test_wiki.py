import urllib.request
import re
import os

url = "https://en.wikipedia.org/wiki/American_Women_quarters"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

req = urllib.request.Request(url, headers=HEADERS)
try:
    html = urllib.request.urlopen(req).read().decode('utf-8')
    # find images in tables
    links = re.findall(r'src="//(upload\.wikimedia\.org/wikipedia/commons/thumb/[^"]+)"', html)
    
    hq_links = []
    for link in links:
        if 'quarter' in link.lower() or 'awq' in link.lower() or 'obverse' in link.lower() or 'reverse' in link.lower():
            # Example: upload.wikimedia.org/wikipedia/commons/thumb/6/69/2022_AWQ_Maya_Angelou_Reverse.jpg/150px-2022_AWQ_Maya_Angelou_Reverse.jpg
            # Convert to: upload.wikimedia.org/wikipedia/commons/6/69/2022_AWQ_Maya_Angelou_Reverse.jpg
            parts = link.split('/')
            if len(parts) >= 3 and parts[-1].endswith('.jpg'):
                # remove "thumb" which is at index 4
                # and remove the last element which is "150px-..."
                if 'thumb' in parts:
                    thumb_idx = parts.index('thumb')
                    hq_url = "https://" + "/".join(parts[:thumb_idx] + parts[thumb_idx+1:-1])
                    hq_links.append(hq_url)
    
    print(f"Found {len(set(hq_links))} high-res wikipedia links:")
    for hq in set(hq_links):
        print(hq)
except Exception as e:
    print(f"Failed: {e}")
