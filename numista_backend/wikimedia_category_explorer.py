"""
wikimedia_category_explorer.py
Crawls Wikimedia Commons categories for US currency to find real filenames.
Then matches them to our remaining types by denomination/year/keyword.
"""
import urllib.request, urllib.parse, json, time, re
from collections import defaultdict

HEADERS  = {'User-Agent': 'NumistaAI/1.0 (contact eric.seaman@yahoo.com)'}
WIKI_API = 'https://commons.wikimedia.org/w/api.php'

def get_category_files(category, limit=500):
    """Return all File: titles in a category."""
    files = []
    cont  = {}
    while True:
        params = {
            'action': 'query', 'list': 'categorymembers',
            'cmtitle': f'Category:{category}',
            'cmnamespace': '6',  # File namespace only
            'cmlimit': '500', 'format': 'json',
        }
        params.update(cont)
        api = WIKI_API + '?' + urllib.parse.urlencode(params)
        try:
            req = urllib.request.Request(api, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read())
            for m in data.get('query', {}).get('categorymembers', []):
                files.append(m['title'])
            if 'continue' in data:
                cont = data['continue']
            else:
                break
        except Exception as e:
            print(f'  ERROR fetching {category}: {e}')
            break
        time.sleep(0.15)
    return files

def get_file_url(title):
    """Resolve a File: title to a direct URL."""
    params = {
        'action': 'query', 'titles': title,
        'prop': 'imageinfo', 'iiprop': 'url', 'format': 'json',
    }
    api = WIKI_API + '?' + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(api, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as r:
            data = json.loads(r.read())
        for page in data.get('query', {}).get('pages', {}).values():
            ii = page.get('imageinfo', [])
            if ii:
                return ii[0]['url']
    except Exception:
        pass
    return None

# ── Categories to crawl ───────────────────────────────────────────────────────
CATEGORIES = [
    'Silver certificates of the United States',
    'Legal tender notes of the United States',
    'Gold certificates of the United States',
    'Fractional currency of the United States',
    'Federal Reserve Bank Notes of the United States',
    'Federal Reserve Notes of the United States',
    'National bank notes of the United States',
    'Confederate States of America dollar notes',
    'Continental Congress currency',
]

all_files = {}
print('Crawling Wikimedia categories...\n')
for cat in CATEGORIES:
    files = get_category_files(cat)
    all_files[cat] = files
    print(f'  {cat}: {len(files)} files')

# Flatten all filenames
flat = []
for files in all_files.values():
    flat.extend(files)

# ── Search for specific denominations and back/reverse images ─────────────────
print('\n=== Reverse/back images found ===')

# Keywords to match reverse/back images
BACK_KW = ['back', 'reverse', 'Back', 'Reverse', '-back', '_back', 'Back.jpg', 'Reverse.jpg']

def is_back(title):
    t = title.lower()
    return 'back' in t or 'reverse' in t

def match_denomination(title, denom_str):
    """Check if a filename matches a denomination like '$1', '$5', '$10' etc."""
    t = title.lower()
    d = denom_str.lower().replace('$', '')
    patterns = [f'${d}', f'-{d}-', f'_{d}_', f'{d}-sc', f'{d}-lt', f'{d}-gc', f'{d}-sc-',
                f'${d}-sc', f'${d}-lt', f'${d}-gc']
    for p in patterns:
        if p in t:
            return True
    return False

# Group back images by category
for cat, files in all_files.items():
    backs = [f for f in files if is_back(f)]
    if backs:
        print(f'\n[{cat}] — {len(backs)} back/reverse images:')
        for f in backs[:30]:
            print(f'  {f}')
        if len(backs) > 30:
            print(f'  ... and {len(backs)-30} more')

# Specific searches relevant to our gap types
print('\n\n=== Targeted searches for specific gap types ===')
TARGET_SEARCHES = [
    ('SC $1 1935 back', lambda t: 'sc' in t.lower() and '1' in t and ('1935' in t or '1934' in t) and is_back(t)),
    ('SC $5 1934 back', lambda t: 'sc' in t.lower() and '5' in t and '1934' in t and is_back(t)),
    ('SC $10 1934 back', lambda t: 'sc' in t.lower() and '10' in t and '1934' in t and is_back(t)),
    ('SC Funnyback $1 1928', lambda t: ('funny' in t.lower() or '1928' in t) and 'sc' in t.lower()),
    ('LT $1 1917 any', lambda t: 'lt' in t.lower() and '1' in t and '1917' in t),
    ('LT $2 any', lambda t: ('lt' in t.lower() or 'legal' in t.lower()) and '-2-' in t.lower()),
    ('LT $5 any', lambda t: ('lt' in t.lower() or 'legal' in t.lower()) and '-5-' in t.lower()),
    ('GC $10 back', lambda t: 'gc' in t.lower() and '10' in t and is_back(t)),
    ('GC $20 back', lambda t: 'gc' in t.lower() and '20' in t and is_back(t)),
    ('FRN large-size back', lambda t: ('frn' in t.lower() or 'federal' in t.lower()) and '1914' in t and is_back(t)),
    ('Fractional 5c back', lambda t: 'fractional' in t.lower() and ('0.05' in t or '5c' in t.lower()) and is_back(t)),
    ('Fractional 10c back', lambda t: 'fractional' in t.lower() and ('0.10' in t or '10c' in t.lower()) and is_back(t)),
    ('Fractional 25c back', lambda t: 'fractional' in t.lower() and ('0.25' in t or '25c' in t.lower()) and is_back(t)),
    ('Fractional 50c back', lambda t: 'fractional' in t.lower() and ('0.50' in t or '50c' in t.lower()) and is_back(t)),
    ('NBN 1902 any', lambda t: 'nbn' in t.lower() and '1902' in t),
    ('NBN 1929 any', lambda t: 'nbn' in t.lower() and '1929' in t),
    ('Confederate back', lambda t: 'confederate' in t.lower() and is_back(t)),
]

for label, fn in TARGET_SEARCHES:
    matches = [f for f in flat if fn(f)]
    if matches:
        print(f'\n[{label}]:')
        for m in matches[:10]:
            print(f'  {m}')
    else:
        print(f'[{label}]: no matches')

# Save all files to JSON for analysis
with open('wikimedia_currency_files.json', 'w', encoding='utf-8') as f:
    json.dump(all_files, f, indent=2)
print('\n\nSaved all filenames to wikimedia_currency_files.json')
print(f'Total files catalogued: {len(flat)}')
