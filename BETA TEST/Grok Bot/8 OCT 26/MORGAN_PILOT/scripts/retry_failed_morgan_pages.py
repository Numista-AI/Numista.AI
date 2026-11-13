import os, re, json, time, base64
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from dex import *

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
PAGES = PKG / 'mint_pages_morgan'
PAGES.mkdir(exist_ok=True)

RETRIES = [
  ("2025_morgan_peace_reverse_proof_press", [
    "https://web.archive.org/web/20251218150313/https://www.usmint.gov/news/press-releases/morgan-and-peace-dollar-2025-reverse-proof-two-coin-set-available-on-december-11",
    "https://web.archive.org/web/20251218/https://www.usmint.gov/news/press-releases/morgan-and-peace-dollar-2025-reverse-proof-two-coin-set-available-on-december-11",
    "https://web.archive.org/web/2026/https://www.usmint.gov/news/press-releases/morgan-and-peace-dollar-2025-reverse-proof-two-coin-set-available-on-december-11",
  ], "Morgan and Peace Dollar 2025 Reverse Proof Two-Coin Set Available"),
  ("2023_morgan_peace_reverse_proof_press", [
    "https://web.archive.org/web/20231110005655/https://www.usmint.gov/news/press-releases/2023-morgan-peace-dollar-reverse-proof-two-coin-set-s-available-november-9-at-noon",
    "https://web.archive.org/web/20231111/https://www.usmint.gov/news/press-releases/2023-morgan-peace-dollar-reverse-proof-two-coin-set-s-available-november-9-at-noon",
    "https://web.archive.org/web/2024/https://www.usmint.gov/news/press-releases/2023-morgan-peace-dollar-reverse-proof-two-coin-set-s-available-november-9-at-noon",
  ], "2023 Morgan and Peace Dollar Reverse Proof Two-Coin Set (S) Available"),
  ("2026_morgan_enhanced_unc_26XE", [
    "https://web.archive.org/web/20261004090713/https://www.usmint.gov/morgan-silver-dollar-2026-enhanced-uncirculated-coin-26XE.html",
    "https://web.archive.org/web/20261004/https://www.usmint.gov/morgan-silver-dollar-2026-enhanced-uncirculated-coin-26XE.html",
    "https://web.archive.org/web/2026/https://www.usmint.gov/morgan-silver-dollar-2026-enhanced-uncirculated-coin-26XE.html",
  ], "Morgan Silver Dollar 2026 Enhanced Uncirculated Coin (26XE)"),
  ("historic_coin_production_facilities", [
    "https://web.archive.org/web/20210424145952/https://www.usmint.gov/learn/history/historic-coin-production",
    "https://web.archive.org/web/20210424/https://www.usmint.gov/learn/history/historic-coin-production",
    "https://web.archive.org/web/2022/https://www.usmint.gov/learn/history/historic-coin-production",
  ], "Historic Coin Production Facilities (mint marks)"),
]

EMAIL=re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
PRICE=re.compile(r'\$\s?\d[\d,]*\.\d{2}')
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36'}

def scrub(t):
    t=EMAIL.sub('[email removed]',t)
    t=re.sub(r'Welcome,(\s|\n)*[A-Z][A-Za-z]+','Welcome, [user]',t)
    t=re.sub(r'\bEric\b(?! David Custer)|\bERIC\b(?! DAVID)','[owner]',t)
    t=PRICE.sub('[price removed]',t)
    return t

def html_to_text(html, uri):
    soup=BeautifulSoup(html,'html.parser')
    for tag in soup(['script','style','noscript','svg','iframe']): tag.decompose()
    text=re.sub(r'\n{3,}','\n\n', soup.get_text('\n', strip=True))
    return f'The Wayback Machine - {uri}\n\n'+text

def slug(s):
    return re.sub(r'[^a-z0-9_-]+','-',s.lower()).strip('-')[:80]

docs=[]; failed=[]; used=[]
session=requests.Session(); session.headers.update(UA)

# Prefer local saved 26XE from workspace copy if present on laptop
local_candidates = [
  Path(r'C:\Users\ericd\Documents\MyVertexProject\scratch\mint_evidence'),
  PKG / 'mint_pages_morgan',
]
# Also check for prior box copy synced somewhere
for p in [
  Path(r'C:\Users\ericd\OneDrive\Desktop\coins\morgan-silver-dollar-2026-enhanced-uncirculated-coin-26XE.html'),
]:
  if p.exists():
    print('FOUND local', p)

for key, urls, title in RETRIES:
    ok=False
    for url in urls:
        print('TRY', key, url[:100])
        try:
            r=session.get(url, timeout=120, allow_redirects=True)
            print(' ', r.status_code, len(r.content))
            if r.status_code!=200:
                time.sleep(6); continue
            text=scrub(html_to_text(r.text, str(r.url)))
            if len(text)<400:
                print('  short', len(text)); time.sleep(4); continue
            (PAGES/f'{key}.html').write_bytes(r.content)
            (PAGES/f'{key}.txt').write_text(text, encoding='utf-8')
            docs.append({
              'id': 'page-morgan-'+slug(key),
              'structData': {'title': title[:200], 'uri': str(r.url), 'source_type':'us_mint', 'publisher':'U.S. Mint', 'orig_file': f'mint_pages_morgan/{key}.txt'},
              'content': {'mimeType':'text/plain', 'rawBytes': base64.b64encode(text.encode()).decode('ascii')}
            })
            used.append({'key':key,'url':str(r.url),'chars':len(text),'title':title})
            print('  OK', len(text))
            ok=True
            time.sleep(5)
            break
        except Exception as e:
            print('  ERR', str(e)[:220])
            time.sleep(10)
    if not ok:
        failed.append(key)

print('docs', len(docs), 'failed', failed)
if docs:
    DS=f'{COL}/dataStores/morgan-docs/branches/default_branch'
    s,j=call('POST', f'{DS}/documents:import', body={'inlineSource':{'documents':docs}, 'reconciliationMode':'INCREMENTAL'}, log_resp=False)
    print('import', s, j.get('name'), j.get('error'))
    assert s==200, j
    op=j.get('name'); t0=time.time()
    while time.time()-t0<600:
        s,j=call('GET', op, log_resp=False)
        if j.get('done'): break
        time.sleep(8)
    print('done', j.get('done'), j.get('metadata'), j.get('error'), j.get('response'))
    total=0; token=None
    while True:
        params={'pageSize':1000}
        if token: params['pageToken']=token
        s,j=call('GET', f'{DS}/documents', params=params, log_resp=False)
        total += len(j.get('documents',[]))
        token=j.get('nextPageToken')
        if not token: break
    print('docs_listed_total', total)
    (PKG/'out'/'MORGAN_MINT_INGEST_RETRY.json').write_text(json.dumps({'used':used,'failed':failed,'docs_listed_total':total}, indent=2), encoding='utf-8')
else:
    print('NO DOCS')
