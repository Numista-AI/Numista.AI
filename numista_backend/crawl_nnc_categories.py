"""
crawl_nnc_categories.py
Crawls real Wikimedia Commons NNC/denomination categories to find actual back/reverse
images for SC, LTN, GC, Fractional Currency, and FRN types we still need.
"""
import urllib.request, urllib.parse, json, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HEADERS  = {'User-Agent': 'NumistaAI/1.0 (contact eric.seaman@yahoo.com)'}
WIKI_API = 'https://commons.wikimedia.org/w/api.php'

def get_category_files(category):
    files = []
    cont  = {}
    while True:
        params = {
            'action': 'query', 'list': 'categorymembers',
            'cmtitle': f'Category:{category}',
            'cmnamespace': '6', 'cmlimit': '500', 'format': 'json',
        }
        params.update(cont)
        try:
            req = urllib.request.Request(WIKI_API + '?' + urllib.parse.urlencode(params), headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read())
            for m in data.get('query', {}).get('categorymembers', []):
                files.append(m['title'])
            if 'continue' in data:
                cont = data['continue']
            else:
                break
        except Exception as e:
            print(f'  ERR {category}: {e}')
            break
        time.sleep(0.2)
    return files

def resolve_url(title):
    params = {'action': 'query', 'titles': title,
              'prop': 'imageinfo', 'iiprop': 'url', 'format': 'json'}
    try:
        req = urllib.request.Request(WIKI_API + '?' + urllib.parse.urlencode(params), headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as r:
            data = json.loads(r.read())
        for page in data.get('query', {}).get('pages', {}).values():
            ii = page.get('imageinfo', [])
            if ii:
                return ii[0]['url']
    except Exception:
        pass
    return None

# Real categories to crawl (discovered from known files)
CATEGORIES = [
    'NNC Silver Certificates',
    'NNC United States Banknotes (1861-present)',
    'NNC Treasury Notes (1890-91)',
    '1 dollar Silver Certificates',
    '5 dollar Silver Certificates',
    '10 dollar Silver Certificates',
    '1 dollar Legal Tender Notes',
    '5 dollar Legal Tender Notes',
    '10 dollar Legal Tender Notes',
    '1 dollar Coin Notes',
    '10 dollar Gold Certificates',
    '20 dollar Gold Certificates',
    '50 dollar Gold Certificates',
    'Fractional currency of the United States',
    'United States fractional currency',
    'Federal Reserve Notes of the United States (1914)',
    'Federal Reserve Bank Notes of the United States',
    'National bank notes of the United States (1863-1935)',
    'Confederate States paper money',
]

all_files = {}
print('Crawling real categories...\n')
for cat in CATEGORIES:
    files = get_category_files(cat)
    all_files[cat] = files
    count = len(files)
    print(f'  [{count:4}] {cat}')

# Flatten
flat = []
for files in all_files.values():
    flat.extend(f for f in files if f not in flat)

print(f'\nTotal unique files: {len(flat)}')

# Find back/reverse images
def is_back(t):
    t = t.lower()
    return 'back' in t or 'reverse' in t

backs = [f for f in flat if is_back(f)]
print(f'Back/reverse images: {len(backs)}\n')

# Save everything
with open('wikimedia_nnc_files.json', 'w', encoding='utf-8') as fp:
    json.dump({'all_files': all_files, 'backs': backs}, fp, indent=2)

# Print all back images organized by type
print('=== All back/reverse images found ===')
for f in sorted(backs):
    print(f'  {f}')

# Also search for specific types still missing
print('\n\n=== Specific file searches for missing types ===')
SPECIFIC = [
    # FRN 1914 large size (we found obverse patterns above)
    'US-$10-FRN-1914-Fr-894b.jpg',
    'US-$10-FRN-1914-Fr-919a.jpg',
    'US-$10-FRN-1914-Fr-919a-back.jpg',
    'US-$10-FRN-1914-Fr-898a.jpg',
    'US-$5-FRN-1914-Fr-875.jpg',
    'US-$5-FRN-1914-Fr-875-back.jpg',
    'US-$20-FRN-1914-Fr-1010.jpg',
    'US-$20-FRN-1914-Fr-958a.jpg',
    'US-$50-FRN-1914-Fr-1053.jpg',
    'US-$100-FRN-1914-Fr-1074.jpg',
    # SC reverses
    'US-$1-SC-1935-Fr-1608-back.jpg',
    'US-$1-SC-1934-Fr-1606-back.jpg',
    'US-$5-SC-1934-Fr-1650-back.jpg',
    'US-$10-SC-1934-Fr-1700-back.jpg',
    'US-$1-SC-1928A-Fr-1600-back.jpg',
    # LTN
    'US-$1-LT-1917-Fr-36.jpg',
    'US-$2-LT-1917-Fr-58.jpg',
    'US-$5-LT-1907-Fr-91.jpg',
    'US-$5-LT-1928-Fr-1525-back.jpg',
    # GC
    'US-$20-GC-1906-Fr-1178.jpg',
    'US-$50-GC-1882-Fr-1191.jpg',
    'US-$10-GC-1922-Fr-1173-back.jpg',
    'US-$20-GC-1922-Fr-1187-back.jpg',
    # Fractional
    'US-Fractional-5c-1st-issue-Fr-1228-back.jpg',
    'US Postal Currency 5 cent 1862 back 720a.tif',
    'US-Fractional-(1st-Issue)-$0.05-Fr-1231-back.jpg',
]

for fname in SPECIFIC:
    url = resolve_url(f'File:{fname}')
    time.sleep(0.1)
    if url:
        print(f'  FOUND: {fname}')
        print(f'         {url[:100]}')
    else:
        print(f'  miss:  {fname}')
