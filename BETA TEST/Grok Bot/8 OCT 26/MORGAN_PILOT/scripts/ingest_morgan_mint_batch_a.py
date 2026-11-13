# ingest_morgan_mint_batch_a.py — fetch Mint Wayback pages for Batch A, scrub, INCREMENTAL import to morgan-docs.
# Project: numista-morgan-pilot ONLY. No secrets. Report-only.
import os, re, json, time, base64, hashlib, datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from dex import *

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
PAGES = PKG / 'mint_pages_morgan'
PAGES.mkdir(exist_ok=True)
MANIFEST = PKG / 'out' / 'MORGAN_MINT_INGEST_MANIFEST.json'
OUT_BATCHES = HERE / 'upload_batches_morgan_a.json'

# Official Mint / archived Mint only (legal-tender Morgan dollars). Skip GlobeNewswire.
# Extra: 2021 May press release cited in Tier A notes for product limit.
URLS = [
  ("2023_morgan_peace_proof_press", "https://web.archive.org/web/20230810134920/https://www.usmint.gov/news/press-releases/united-states-mint-opens-sales-for-the-2023-morgan-and-peace-proof-silver-dollars-on-august-9", "United States Mint Opens Sales for the 2023 Morgan and Peace Proof Silver Dollars"),
  ("2021_morgan_dollar_program", "https://web.archive.org/web/20210709183332/https://www.usmint.gov/coins/coin-medal-programs/morgan-peace-dollar-anniversary-coins/2021-morgan-dollar", "2021 Morgan Dollar (program page)"),
  ("2021_morgan_peace_preorder_press", "https://web.archive.org/web/20210525060415/https://www.usmint.gov/news/press-releases/united-states-mint-offering-2021-morgan-and-peace-dollars-in-three-pre-order-windows", "United States Mint Offering 2021 Morgan and Peace Dollars in Three Pre-Order Windows"),
  ("2024_morgan_peace_unc_press", "https://web.archive.org/web/20240713042030/https://www.usmint.gov/news/press-releases/united-states-mint-opens-sales-for-the-2024-morgan-and-peace-uncirculated-silver-dollars-on-july-11", "United States Mint Opens Sales for the 2024 Morgan and Peace Uncirculated Silver Dollars"),
  ("2024_morgan_peace_program_landing", "https://web.archive.org/web/20261004090710/https://www.usmint.gov/coins/coin-programs/morgan-and-peace-silver-dollar-coins/", "Morgan and Peace Silver Dollar Coins (program landing)"),
  ("2024_morgan_peace_reverse_proof_press", "https://web.archive.org/web/20241206144121/https://www.usmint.gov/news/press-releases/united-states-mint-2024-morgan-and-peace-dollar-reverse-proof-two-coin-set-now-available", "2024 Morgan and Peace Dollar Reverse Proof Two-Coin Set Now Available"),
  ("2025_morgan_peace_unc_press", "https://web.archive.org/web/20250907103931/https://www.usmint.gov/news/press-releases/2025-morgan-and-peace-uncirculated-silver-dollars-available-on-july-10", "2025 Morgan and Peace Uncirculated Silver Dollars Available"),
  ("2025_morgan_peace_proof_press", "https://web.archive.org/web/20250906083100/https://www.usmint.gov/news/press-releases/2025-morgan-and-peace-dollar-proof-coins-available-on-september-11", "2025 Morgan and Peace Dollar Proof Coins Available"),
  ("2025_morgan_peace_reverse_proof_press", "https://web.archive.org/web/20251218150313/https://www.usmint.gov/news/press-releases/morgan-and-peace-dollar-2025-reverse-proof-two-coin-set-available-on-december-11", "Morgan and Peace Dollar 2025 Reverse Proof Two-Coin Set Available"),
  ("2023_morgan_peace_reverse_proof_press", "https://web.archive.org/web/20231110005655/https://www.usmint.gov/news/press-releases/2023-morgan-peace-dollar-reverse-proof-two-coin-set-s-available-november-9-at-noon", "2023 Morgan & Peace Dollar Reverse Proof Two-Coin Set (S) Available"),
  ("2026_morgan_enhanced_unc_26XE", "https://web.archive.org/web/20261004090713/https://www.usmint.gov/morgan-silver-dollar-2026-enhanced-uncirculated-coin-26XE.html", "Morgan Silver Dollar 2026 Enhanced Uncirculated Coin (26XE)"),
  ("historic_coin_production_facilities", "https://web.archive.org/web/20210424145952/https://www.usmint.gov/learn/history/historic-coin-production", "Historic Coin Production Facilities (mint marks)"),
]

EMAIL=re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
PRICE=re.compile(r'\$\s?\d[\d,]*\.\d{2}')
UA={'User-Agent':'Mozilla/5.0 (compatible; NumistaMorganPilot/1.0; research; eric@numista.ai)'}

def scrub(t):
    t=EMAIL.sub('[email removed]',t)
    t=re.sub(r'Welcome,(\s|\n)*[A-Z][A-Za-z]+','Welcome, [user]',t)
    t=re.sub(r'\bEric\b(?! David Custer)|\bERIC\b(?! DAVID)','[owner]',t)
    t=PRICE.sub('[price removed]',t)
    t=re.sub(r'\bHOLIDAY\d{4}\b','[promo]',t)
    return t

def html_to_text(html, uri):
    soup=BeautifulSoup(html,'html.parser')
    for tag in soup(['script','style','noscript','svg','iframe']):
        tag.decompose()
    text=soup.get_text('\n', strip=True)
    text=re.sub(r'\n{3,}','\n\n',text)
    # Prefixed Wayback line like AWQ saved copies
    header=f'The Wayback Machine - {uri}\n\n'
    return header+text

def slug(s):
    return re.sub(r'[^a-z0-9_-]+','-',s.lower()).strip('-')[:80]

def fetch(key, url, title):
    raw_path = PAGES / f'{key}.html'
    txt_path = PAGES / f'{key}.txt'
    meta = {'key':key,'url':url,'title':title,'ok':False}
    try:
        r=requests.get(url, timeout=90, headers=UA, allow_redirects=True)
        meta['http']=r.status_code
        meta['bytes']=len(r.content)
        if r.status_code!=200:
            meta['error']=f'HTTP {r.status_code}'
            return meta, None
        raw_path.write_bytes(r.content)
        text=html_to_text(r.text, url)
        text=scrub(text)
        if len(text)<400:
            meta['error']=f'text too short ({len(text)})'
            return meta, None
        # Reject medals-only pages if they somehow appear
        low=text.lower()
        if 'morgan' not in low and 'peace dollar' not in low and 'historic coin production' not in low and 'carson city' not in low:
            meta['error']='page does not appear to be Morgan/Peace/historic mint marks'
            return meta, None
        txt_path.write_text(text, encoding='utf-8')
        meta['ok']=True
        meta['chars']=len(text)
        meta['txt']=str(txt_path)
        # Spot-check markers for Batch A claims
        markers=['San Francisco','Philadelphia','privy','Production is limited','reverse proof','West Point','Carson City','New Orleans']
        meta['markers']={m: (m.lower() in low) for m in markers}
        return meta, text
    except Exception as e:
        meta['error']=str(e)[:300]
        return meta, None

def to_doc(key, title, uri, text):
    did='page-morgan-'+slug(key)
    return {
        'id': did,
        'structData': {
            'title': title[:200],
            'uri': uri,
            'source_type': 'us_mint',
            'publisher': 'U.S. Mint',
            'orig_file': f'mint_pages_morgan/{key}.txt',
        },
        'content': {
            'mimeType': 'text/plain',
            'rawBytes': base64.b64encode(text.encode('utf-8')).decode('ascii'),
        },
    }

def main():
    print('AUTH probe…')
    s,j=call('GET', f'{COL}/engines/morgan-pilot-search', log_resp=False)
    print('engine', s, j.get('name'))
    assert s==200, j

    docs=[]; manifest=[]
    failed=[]
    for key,url,title in URLS:
        print('FETCH', key)
        meta, text = fetch(key,url,title)
        manifest.append(meta)
        if text is None:
            failed.append(meta)
            print('  FAIL', meta.get('error'), meta.get('http'))
            continue
        docs.append(to_doc(key,title,url,text))
        print('  OK chars', meta['chars'], 'markers', meta.get('markers'))

    MANIFEST.parent.mkdir(exist_ok=True)
    MANIFEST.write_text(json.dumps({'ts':datetime.datetime.now().isoformat(timespec='seconds'),'project':'numista-morgan-pilot','docs_ok':len(docs),'failed':failed,'manifest':manifest}, indent=2), encoding='utf-8')
    print('OK', len(docs), 'FAILED', len(failed))
    if not docs:
        raise SystemExit('NO_DOCS_FETCHED')

    # Batches of 4 (pages can be large after base64)
    batches=[docs[i:i+4] for i in range(0,len(docs),4)]
    OUT_BATCHES.write_text(json.dumps(batches), encoding='utf-8')
    print('wrote', OUT_BATCHES, 'batches', len(batches))

    DS=f'{COL}/dataStores/morgan-docs/branches/default_branch'
    # observability off
    call('PATCH', f'{COL}/engines/morgan-pilot-search', params={'updateMask':'observabilityConfig'}, body={'observabilityConfig':{'observabilityEnabled':False}}, log_resp=False)

    ops=[]
    for i,b in enumerate(batches):
        s,j=call('POST', f'{DS}/documents:import', body={'inlineSource':{'documents':b}, 'reconciliationMode':'INCREMENTAL'}, log_resp=False)
        print('import batch', i, len(b), s, json.dumps({k:j.get(k) for k in ('name','error','done')})[:400])
        if s>=300:
            print('IMPORT_FAIL', json.dumps(j)[:800])
            raise SystemExit('IMPORT_FAILED')
        ops.append(j.get('name'))

    for op in ops:
        if not op: continue
        t0=time.time()
        while time.time()-t0<900:
            s,j=call('GET', op, log_resp=False)
            if j.get('done'): break
            time.sleep(10)
        print('op done', j.get('done'), 'meta', json.dumps(j.get('metadata',{}))[:400], 'err', json.dumps(j.get('error',{}))[:400], 'resp', json.dumps(j.get('response',{}))[:600])

    # list docs count (page through)
    total=0; token=None
    while True:
        params={'pageSize':1000}
        if token: params['pageToken']=token
        s,j=call('GET', f'{DS}/documents', params=params, log_resp=False)
        assert s==200, j
        total += len(j.get('documents',[]))
        token=j.get('nextPageToken')
        if not token: break
    print('docs_listed_total', total)
    # save ingest summary snippet
    (PKG/'out'/'MORGAN_MINT_INGEST_RESULT.json').write_text(json.dumps({'docs_imported':len(docs),'docs_listed_total':total,'failed':failed,'ids':[d['id'] for d in docs]}, indent=2), encoding='utf-8')

if __name__=='__main__':
    main()
