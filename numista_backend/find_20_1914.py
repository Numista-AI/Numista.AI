"""find_20_1914.py — find the correct Wikimedia Commons URL for the $20 1914 FRN"""
import urllib.request, urllib.parse, json, time

HEADERS = {'User-Agent': 'NumistaAI/1.0 (contact eric.seaman@yahoo.com)'}
WIKI_API = 'https://commons.wikimedia.org/w/api.php'

candidates = [
    # Try the confirmed Fr.960a pattern with encoding variants
    'US-$20-FRN-1914-Fr.960a.jpg',
    'US-%2420-FRN-1914-Fr.960a.jpg',
    'US $20 FRN 1914 Fr.960a.jpg',
    # Common patterns for large-size FRN
    'US-$20-FRN-1914-Fr960a.jpg',
    'Series1914TwentyDollarFederalReserveNoteObverse.jpg',
    '$20 Federal Reserve Note 1914 obverse.jpg',
    'Twenty Dollar Federal Reserve Note 1914.jpg',
    'US20dollarFRN1914.jpg',
    # Search Wikimedia categories
]

for fname in candidates:
    api = (WIKI_API + '?action=query&titles=File:'
           + urllib.parse.quote(fname, safe='')
           + '&prop=imageinfo&iiprop=url&format=json')
    try:
        req = urllib.request.Request(api, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as r:
            data = json.loads(r.read())
        found = False
        for page in data.get('query', {}).get('pages', {}).values():
            ii = page.get('imageinfo', [])
            if ii:
                print(f'FOUND: {fname}')
                print(f'  URL: {ii[0]["url"]}')
                found = True
        if not found:
            print(f'miss:  {fname}')
    except Exception as e:
        print(f'error: {fname} — {e}')
    time.sleep(0.12)

# Also try a category search
print('\n--- Category search for 1914 FRN ---')
api = (WIKI_API + '?action=query&list=categorymembers'
       + '&cmtitle=Category:1914+Federal+Reserve+Notes'
       + '&cmlimit=20&format=json')
try:
    req = urllib.request.Request(api, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=12) as r:
        data = json.loads(r.read())
    for m in data.get('query', {}).get('categorymembers', []):
        print(f'  {m.get("title","")}')
except Exception as e:
    print(f'Category search error: {e}')

# Try fulltext search
print('\n--- Fulltext search: $20 FRN 1914 ---')
api = (WIKI_API + '?action=query&list=search&srsearch=File:$20+FRN+1914'
       + '&srnamespace=6&srlimit=10&format=json')
try:
    req = urllib.request.Request(api, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=12) as r:
        data = json.loads(r.read())
    for m in data.get('query', {}).get('search', []):
        print(f'  {m.get("title","")}')
except Exception as e:
    print(f'Search error: {e}')
