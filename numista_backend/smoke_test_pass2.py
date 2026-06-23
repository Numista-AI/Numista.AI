#!/usr/bin/env python3
"""Quick smoke test — verify URL lookups per series."""
import io, sys, os, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

os.chdir(r'C:\Users\ericd\Documents\MyVertexProject\numista_backend')

import requests

WIKIMEDIA_UA = "NumistaAI/1.0 (eric@numista.ai)"
s = requests.Session()
s.headers.update({'User-Agent': WIKIMEDIA_UA})

SERIES_DIRECT_FILES = {
    'buffalo_nickel':   'File:Indian Head Buffalo Reverse.jpg',
    'roosevelt_dime':   'File:2015-W proof Roosevelt dime reverse.jpg',
    'walking_liberty':  'File:Walking Liberty Half Dollar 1945D Reverse.png',
    'franklin_half':    'File:Franklin Half 1963 D Reverse.png',
    'indian_head_cent': 'File:1859 Indian Head cent reverse.png',
    'washington_quarter': 'File:Circulated Washington quarter reverse.jpg',
}

def get_url(f):
    time.sleep(0.25)
    r = s.get('https://commons.wikimedia.org/w/api.php',
              params={'action':'query','titles':f,'prop':'imageinfo','iiprop':'url','format':'json'}, timeout=20)
    for page in r.json().get('query',{}).get('pages',{}).values():
        info = page.get('imageinfo',[])
        if info: return info[0]['url']
    return None

for series, fname in SERIES_DIRECT_FILES.items():
    url = get_url(fname)
    if url:
        sys.stdout.write(f"OK  {series}: {url[:90]}\n")
    else:
        sys.stdout.write(f"FAIL {series}: {fname}\n")
    sys.stdout.flush()
