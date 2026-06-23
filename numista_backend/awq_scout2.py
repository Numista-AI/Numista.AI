#!/usr/bin/env python3
"""
Find AWQ images via:
1. coin_image_index Firestore - look for any AWQ entries
2. PCGS coin detail pages for each AWQ design
3. CoinNews.net / CoinWorld article images
4. Direct US Mint CDN image pattern
"""
import io, sys, json, time, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

s = requests.Session()
s.headers.update({'User-Agent': 'NumistaAI/1.0 (eric@numista.ai)'})

DESIGNS_2023 = ['Bessie Coleman', 'Edith Kanakaole', 'Eleanor Roosevelt', 'Jovita Idar', 'Maria Tallchief']
DESIGNS_2024 = ['Patsy T. Mink', 'Mary Edwards Walker', 'Celia Cruz', 'Zitkala-Sa', 'Pauli Murray']

results = {}

# --- Try US Mint CDN image patterns ---
print('=== US MINT CDN PATTERNS ===')
# The Mint uses patterns like: https://catalog.usmint.gov/dw/image/v2/AASK_PRD/on/demandware.static/...
# But easier: try their product pages for the images
# The Mint often serves coin images at these paths:
mint_slugs = {
    'Bessie Coleman':         '2023-american-women-quarters-proof-set',
    'Eleanor Roosevelt':      '2023-american-women-quarters-proof-set',
    'Jovita Idar':            '2023-american-women-quarters-proof-set',
    # Try direct image CDN
}

# Try PCGS CoinFacts which has great coin images
# AWQ PCGS IDs can be looked up via their search
pcgs_searches = {
    'Bessie Coleman 2023':        'https://www.pcgs.com/coins/detail/2023-p-25c-bessie-coleman-ngc-ms69',
    'Eleanor Roosevelt 2023':     'https://www.pcgs.com/coins/detail/2023-p-25c-eleanor-roosevelt',
}

# Try CoinNews (they always have official Mint images)
print('Fetching CoinNews AWQ articles...')
cn_urls = [
    'https://www.coinnews.net/2023/01/03/2023-american-women-quarters-designs/',
    'https://www.coinnews.net/2024/01/09/2024-american-women-quarters-designs/',
]
for url in cn_urls:
    try:
        r = s.get(url, timeout=15)
        if r.status_code == 200:
            text = r.text
            # Find img tags with quarter designs
            import re
            imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', text)
            quarter_imgs = [i for i in imgs if any(k in i.lower() for k in ['quarter','awq','2023','2024','women'])]
            print(f'\n  {url}')
            print(f'  Status: {r.status_code} | Total imgs: {len(imgs)} | Quarter imgs: {len(quarter_imgs)}')
            for img in quarter_imgs[:10]:
                print(f'    {img[:120]}')
        else:
            print(f'  {url}: {r.status_code}')
    except Exception as e:
        print(f'  {url}: ERROR {e}')

# Try Coin World
print('\nFetching Coin World...')
cw_url = 'https://www.coinworld.com/news/american-coins/2024-american-women-quarters-designs-announced'
try:
    r = s.get(cw_url, timeout=15)
    if r.status_code == 200:
        import re
        imgs = re.findall(r'https?://[^\s"\'<>]+\.(?:jpg|png|webp)[^\s"\'<>]*', r.text)
        quarter_imgs = [i for i in imgs if any(k in i.lower() for k in ['quarter','awq','2024','women','coin'])]
        print(f'  Status: {r.status_code} | Quarter imgs: {len(quarter_imgs)}')
        for img in quarter_imgs[:10]:
            print(f'    {img[:120]}')
    else:
        print(f'  {r.status_code}')
except Exception as e:
    print(f'  ERROR: {e}')

# Try the US Mint product catalog (direct image links)
print('\nTrying US Mint catalog images...')
mint_designs = {
    '2023 Bessie Coleman':      ['https://catalog.usmint.gov/dw/image/v2/AASK_PRD/on/demandware.static/-/Sites-US-Mint-master/default/dw/images/coins/quarters/2023/bessie-coleman-quarter-obverse.jpg'],
}

# Check Firestore coin_image_index for any AWQ entries
print('\nChecking coin_image_index for AWQ...')
import os
os.chdir(r'C:\Users\ericd\Documents\MyVertexProject\numista_backend')
from google.oauth2 import service_account
from google.cloud import firestore

creds = service_account.Credentials.from_service_account_file('serviceAccountKey.json.json')
db = firestore.Client(project=creds.project_id, credentials=creds)

# Search coin_image_index for women/quarters/2023/2024
try:
    all_docs = list(db.collection('coin_image_index').stream())
    print(f'  Total coin_image_index docs: {len(all_docs)}')
    awq_docs = [d for d in all_docs if any(k in d.id.lower() for k in ['women','2023_quarter','2024_quarter','awq','american-women'])]
    print(f'  AWQ-related docs: {len(awq_docs)}')
    for d in awq_docs:
        print(f'    {d.id}: {d.to_dict()}')
    
    # Also check 2022/2023/2024 quarter entries
    yr_docs = [d for d in all_docs if d.id.startswith(('2022_','2023_','2024_')) and 'quarter' in d.id.lower()]
    print(f'  2022-2024 quarter docs: {len(yr_docs)}')
    for d in yr_docs[:20]:
        dd = d.to_dict()
        print(f'    {d.id}: {str(dd)[:120]}')
except Exception as e:
    print(f'  ERROR: {e}')
