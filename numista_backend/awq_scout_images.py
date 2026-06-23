#!/usr/bin/env python3
"""
Scout Wikimedia Commons for all 10 AWQ obverse designs + 1 shared reverse.
Outputs: awq_image_map.json
"""
import io, sys, json, time, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

s = requests.Session()
s.headers.update({'User-Agent': 'NumistaAI/1.0 (eric@numista.ai)'})
API = 'https://commons.wikimedia.org/w/api.php'

DELAY = 0.3

def delay():
    time.sleep(DELAY)

def get_file_url(title):
    delay()
    r = s.get(API, params={'action':'query','titles':title,'prop':'imageinfo','iiprop':'url','format':'json'}, timeout=20)
    for p in r.json().get('query',{}).get('pages',{}).values():
        info = p.get('imageinfo',[])
        if info: return info[0]['url']
    return None

def search_files(q, limit=5):
    delay()
    r = s.get(API, params={'action':'query','list':'search','srsearch':q,'srnamespace':'6','srlimit':str(limit),'format':'json'}, timeout=20)
    return [h['title'] for h in r.json().get('query',{}).get('search',[])]

# 10 AWQ designs we need
DESIGNS = {
    # 2023
    'Bessie Coleman':       '2023',
    "Edith Kanaka'ole":     '2023',
    'Eleanor Roosevelt':    '2023',
    'Jovita Idar':          '2023',
    'Maria Tallchief':      '2023',
    # 2024
    'Patsy Takemoto Mink':  '2024',
    'Dr. Mary Edwards Walker': '2024',
    'Celia Cruz':           '2024',
    'Zitkala-Sa':           '2024',
    'Pauli Murray':         '2024',
}

# Known direct file titles to try first (from PCGS/Mint/Wikimedia known patterns)
DIRECT_ATTEMPTS = {
    'Bessie Coleman':       ['File:2023 Bessie Coleman Quarter (obverse).jpg', 'File:2023 American Women Quarter - Bessie Coleman - obverse.jpg'],
    "Edith Kanaka'ole":     ['File:2023 Edith Kanakaole Quarter (obverse).jpg'],
    'Eleanor Roosevelt':    ['File:2023 Eleanor Roosevelt Quarter (obverse).jpg'],
    'Jovita Idar':          ['File:2023 Jovita Idar Quarter (obverse).jpg'],
    'Maria Tallchief':      ['File:2023 Maria Tallchief Quarter (obverse).jpg'],
    'Patsy Takemoto Mink':  ['File:2024 Patsy Mink Quarter (obverse).jpg'],
    'Dr. Mary Edwards Walker': ['File:2024 Mary Edwards Walker Quarter (obverse).jpg'],
    'Celia Cruz':           ['File:2024 Celia Cruz Quarter (obverse).jpg'],
    'Zitkala-Sa':           ['File:2024 Zitkala-Sa Quarter (obverse).jpg'],
    'Pauli Murray':         ['File:2024 Pauli Murray Quarter (obverse).jpg'],
}

# AWQ shared reverse
AWQ_REVERSE_CANDIDATES = [
    'File:2022 American Women Quarter reverse.jpg',
    'File:American women quarter reverse.jpg',
    'File:AWQ reverse.jpg',
]

image_map = {}

# 1. Find the shared reverse first
print('=== AWQ SHARED REVERSE ===')
awq_rev_url = None
for f in AWQ_REVERSE_CANDIDATES:
    url = get_file_url(f)
    if url:
        awq_rev_url = url
        print(f'  FOUND: {f}')
        print(f'  -> {url[:100]}')
        break
    else:
        print(f'  MISS: {f}')

if not awq_rev_url:
    # Search for it
    for q in ['American women quarter reverse eagle 2022', 'AWQ reverse quarter eagle', 'Washington quarter reverse 2022 women']:
        results = search_files(q, 5)
        for t in results:
            if 'reverse' in t.lower() or 'rev' in t.lower():
                url = get_file_url(t)
                if url:
                    awq_rev_url = url
                    print(f'  SEARCH-FOUND: {t}')
                    print(f'  -> {url[:100]}')
                    break
        if awq_rev_url: break

image_map['_reverse_shared'] = awq_rev_url

print()
print('=== OBVERSE PER DESIGN ===')
for name, year in DESIGNS.items():
    print(f'\n{year} {name}:')
    found_url = None
    found_title = None

    # Try direct titles
    for f in DIRECT_ATTEMPTS.get(name, []):
        url = get_file_url(f)
        if url:
            found_url = url
            found_title = f
            print(f'  DIRECT: {f}')
            break

    if not found_url:
        # Search Wikimedia
        slug = name.replace("'","").replace('.','').replace('-',' ')
        queries = [
            f'American Women Quarter {slug} {year} obverse',
            f'{slug} quarter {year} coin obverse',
            f'{year} AWQ {slug} obverse',
        ]
        for q in queries:
            results = search_files(q, 6)
            for t in results:
                tl = t.lower()
                # Skip obvious reverses/non-coin images
                if 'reverse' in tl or 'rev.' in tl:
                    continue
                url = get_file_url(t)
                if url:
                    found_url = url
                    found_title = t
                    print(f'  SEARCH: {t}')
                    break
            if found_url: break

    if found_url:
        print(f'  URL: {found_url[:100]}')
    else:
        print(f'  NOT FOUND')

    image_map[name] = {'year': year, 'title': found_title, 'url': found_url}

with open('awq_image_map.json', 'w', encoding='utf-8') as f:
    json.dump(image_map, f, indent=2, ensure_ascii=False)
print(f'\nWrote awq_image_map.json')
print(f'Found obverse: {sum(1 for k,v in image_map.items() if k != "_reverse_shared" and v.get("url"))} / {len(DESIGNS)}')
print(f'Found reverse: {"YES" if awq_rev_url else "NO"}')
