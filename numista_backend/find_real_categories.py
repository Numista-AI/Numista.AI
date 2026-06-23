"""find_real_categories.py — Use known files to discover actual Wikimedia category names,
then crawl those categories for back/reverse images."""
import urllib.request, urllib.parse, json, time

HEADERS  = {'User-Agent': 'NumistaAI/1.0 (contact eric.seaman@yahoo.com)'}
WIKI_API = 'https://commons.wikimedia.org/w/api.php'

# Known files that resolved successfully — use to discover real category names
SEED_FILES = [
    'US-$1-TN-1890-Fr-347.jpg',
    'US-$10-GC-1922-Fr-1173.jpg',
    'US-$1-SC-1899-Fr-226.jpg',
    'US-$1-FRBN-1918-Fr.713-back.jpg',   # try this even though it may not resolve
    '1928A XA block Funnyback reverse.jpg',
    'US-$2-SC-1896-Educational-back.jpg',
    'US-$10-LT-1901-Fr.114-back.jpg',
    'US-$10-GC-1907-back.jpg',
]

print('=== Categories from known files ===')
all_cats = set()
for fname in SEED_FILES:
    params = {
        'action': 'query', 'titles': f'File:{fname}',
        'prop': 'categories', 'cllimit': '50', 'format': 'json',
    }
    api = WIKI_API + '?' + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(api, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as r:
            data = json.loads(r.read())
        found_cats = []
        for page in data.get('query', {}).get('pages', {}).values():
            if page.get('missing') is not None:
                continue
            for cat in page.get('categories', []):
                cname = cat['title'].replace('Category:', '')
                found_cats.append(cname)
                all_cats.add(cname)
        if found_cats:
            print(f'\n  {fname}:')
            for c in found_cats:
                print(f'    {c}')
    except Exception as e:
        print(f'  Error for {fname}: {e}')
    time.sleep(0.15)

print(f'\n\nAll categories discovered: {len(all_cats)}')
for c in sorted(all_cats):
    print(f'  {c}')

# Now try a fulltext search for back images of the types we need
print('\n\n=== Wikimedia fulltext search for missing back/reverse images ===')
SEARCHES = [
    '$1 SC 1935 back',
    '$5 SC 1934 back',
    '$10 SC 1934 back',
    'US-$1-SC-1935 back',
    'US silver certificate back',
    'US legal tender back',
    '$5 legal tender back',
    '$10 legal tender back',
    'fractional currency back',
    'national bank note back',
    'US-$10-FRN-1914 back',
]
for q in SEARCHES:
    params = {
        'action': 'query', 'list': 'search',
        'srsearch': f'File: {q}', 'srnamespace': '6',
        'srlimit': '5', 'format': 'json',
    }
    api = WIKI_API + '?' + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(api, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as r:
            data = json.loads(r.read())
        results = data.get('query', {}).get('search', [])
        if results:
            print(f'\n["{q}"]:')
            for r in results[:5]:
                print(f'  {r["title"]}')
        else:
            print(f'["{q}"]: no results')
    except Exception as e:
        print(f'Error for "{q}": {e}')
    time.sleep(0.15)
