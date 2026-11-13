# ingest_state_quarters_batch_b.py — fetch Mint Wayback State Quarters pages + production Excels,
# scrub/convert to text, INCREMENTAL import to morgan-docs. Project: numista-morgan-pilot ONLY.
import os, re, json, time, base64, datetime, io
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import xlrd
from dex import *

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
PAGES = PKG / 'mint_pages_state_quarters'
PAGES.mkdir(exist_ok=True)
MANIFEST = PKG / 'out' / 'STATE_QUARTERS_MINT_INGEST_MANIFEST.json'
OUT_BATCHES = HERE / 'upload_batches_state_quarters_b.json'
RESULT = PKG / 'out' / 'STATE_QUARTERS_MINT_INGEST_RESULT.json'

# Official Mint / archived Mint only. Excel production tables are Mint-published circulating figures.
HTML_URLS = [
  ("50sq_designs_201002", "https://web.archive.org/web/20100204054242/http://www.usmint.gov/mint_programs/50sq_program/?action=designs_50sq", "U.S. Mint 50 State Quarters Program — designs by year"),
  ("50sq_learn_201807", "https://web.archive.org/web/20180705203015/https://www.usmint.gov/learn/coin-and-medal-programs/50-state-quarters", "50 State Quarters Program (U.S. Mint learn page)"),
  ("50sq_schedule_200901", "https://web.archive.org/web/20090101120000/http://www.usmint.gov/mint_programs/50sq_program/?action=schedule", "50 State Quarters Program release schedule"),
  ("coin_production_index_201210", "https://web.archive.org/web/20121011075339/http://www.usmint.gov/about_the_mint/coin_production/index.cfm?action=production_figures&allCoinsYear=2012", "U.S. Mint Coin Production Figures index (links 50 State Quarters 1999-2008)"),
]

# Wayback timestamps from CDX (2012-10-21) for Mint Excels
EXCEL_YEARS = {
  1999: "20121021063656",
  2000: "20121021063635",
  2001: "20121021063809",
  2002: "20121021063904",
  2003: "20121021063820",
  2004: "20121021063833",
  2005: "20121021063815",
  2006: "20121021063627",
  2007: "20121021063643",
  2008: "20121021063920",
}

EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
PRICE = re.compile(r'\$\s?\d[\d,]*\.\d{2}')
UA = {'User-Agent': 'Mozilla/5.0 (compatible; NumistaMorganPilot/1.0; research; eric@numista.ai)'}

def scrub(t):
    t = EMAIL.sub('[email removed]', t)
    t = re.sub(r'Welcome,(\s|\n)*[A-Z][A-Za-z]+', 'Welcome, [user]', t)
    t = re.sub(r'\bEric\b(?! David Custer)|\bERIC\b(?! DAVID)', '[owner]', t)
    t = PRICE.sub('[price removed]', t)
    t = re.sub(r'\bHOLIDAY\d{4}\b', '[promo]', t)
    return t

def html_to_text(html, uri):
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style', 'noscript', 'svg', 'iframe']):
        tag.decompose()
    text = soup.get_text('\n', strip=True)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return f'The Wayback Machine - {uri}\n\n' + text

def slug(s):
    return re.sub(r'[^a-z0-9_-]+', '-', s.lower()).strip('-')[:80]

def fmt_num(v):
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    if isinstance(v, (int, float)):
        return f'{int(v):,}'
    return str(v).strip()

def excel_to_text(year, data, uri):
    wb = xlrd.open_workbook(file_contents=data)
    lines = [
        f'The Wayback Machine - {uri}',
        '',
        f'United States Mint — {year} 50 State Quarters Program Production (circulating)',
        'Source: U.S. Mint Circulating Coins Production Excel (archived).',
        'Facilities: Denver and Philadelphia circulating departments. Totals may include numismatic bags/rolls/boxes from circulating departments. Does not include proof or uncirculated-set quality coins.',
        '',
        'Design | Denver | Philadelphia | Total',
    ]
    sheet = wb.sheet_by_index(0)
    for r in range(sheet.nrows):
        vals = [sheet.cell_value(r, c) for c in range(sheet.ncols)]
        # skip empty
        if not any(str(v).strip() for v in vals):
            continue
        # header-ish rows already covered; emit data rows with numbers
        design = str(vals[0]).strip() if vals else ''
        if design.lower() in ('design', '') and r < 3:
            continue
        if 'grand total' in ' '.join(str(v).lower() for v in vals):
            # find numeric total
            nums = [v for v in vals if isinstance(v, (int, float)) and v]
            total = fmt_num(nums[-1]) if nums else ''
            lines.append(f'Grand Total: {total}')
            continue
        if len(vals) >= 4 and design and design.lower() != 'design':
            d, p, t = vals[1], vals[2], vals[3]
            if isinstance(d, (int, float)) or isinstance(p, (int, float)):
                lines.append(f'{design} | Denver {fmt_num(d)} | Philadelphia {fmt_num(p)} | Total {fmt_num(t)}')
            else:
                lines.append(' | '.join(str(v).strip() for v in vals if str(v).strip()))
        else:
            lines.append(' | '.join(str(v).strip() for v in vals if str(v).strip()))
    return '\n'.join(lines) + '\n'

def fetch_html(key, url, title):
    raw_path = PAGES / f'{key}.html'
    txt_path = PAGES / f'{key}.txt'
    meta = {'key': key, 'url': url, 'title': title, 'kind': 'html', 'ok': False}
    try:
        r = requests.get(url, timeout=90, headers=UA, allow_redirects=True)
        meta['http'] = r.status_code
        meta['bytes'] = len(r.content)
        if r.status_code != 200:
            meta['error'] = f'HTTP {r.status_code}'
            return meta, None
        raw_path.write_bytes(r.content)
        text = scrub(html_to_text(r.text, url))
        if len(text) < 400:
            meta['error'] = f'text too short ({len(text)})'
            return meta, None
        low = text.lower()
        if 'state quarter' not in low and '50 state' not in low and 'coin production' not in low:
            meta['error'] = 'page does not appear to be State Quarters / production'
            return meta, None
        txt_path.write_text(text, encoding='utf-8')
        meta['ok'] = True
        meta['chars'] = len(text)
        meta['txt'] = str(txt_path)
        markers = ['Delaware', 'Virginia', 'Hawaii', 'Oklahoma', 'Philadelphia', 'Denver', 'Washington', '10-year', '10 weeks']
        meta['markers'] = {m: (m.lower() in low) for m in markers}
        return meta, text
    except Exception as e:
        meta['error'] = str(e)[:300]
        return meta, None

def fetch_excel(year, ts):
    key = f'prod_excel_{year}'
    orig = f'http://www.usmint.gov/about_the_mint/coin_production/Excels/{year}_50_State_Quarters_Program_Production.xls'
    url = f'https://web.archive.org/web/{ts}id_/{orig}'
    title = f'{year} 50 State Quarters Program Production (U.S. Mint Excel)'
    xls_path = PAGES / f'{key}.xls'
    txt_path = PAGES / f'{key}.txt'
    meta = {'key': key, 'url': url, 'title': title, 'kind': 'excel', 'year': year, 'ok': False}
    try:
        r = requests.get(url, timeout=90, headers=UA, allow_redirects=True)
        meta['http'] = r.status_code
        meta['bytes'] = len(r.content)
        if r.status_code != 200:
            meta['error'] = f'HTTP {r.status_code}'
            return meta, None
        if r.content[:4] != b'\xd0\xcf\x11\xe0':
            meta['error'] = 'not an OLE/XLS file'
            return meta, None
        xls_path.write_bytes(r.content)
        text = scrub(excel_to_text(year, r.content, url))
        if len(text) < 200:
            meta['error'] = f'text too short ({len(text)})'
            return meta, None
        txt_path.write_text(text, encoding='utf-8')
        meta['ok'] = True
        meta['chars'] = len(text)
        meta['txt'] = str(txt_path)
        # list designs found
        designs = []
        for line in text.splitlines():
            if ' | Denver ' in line and 'Grand Total' not in line:
                designs.append(line.split(' | ')[0].strip())
        meta['designs'] = designs
        return meta, text
    except Exception as e:
        meta['error'] = str(e)[:300]
        return meta, None

def to_doc(key, title, uri, text):
    did = 'page-stateq-' + slug(key)
    return {
        'id': did,
        'structData': {
            'title': title[:200],
            'uri': uri,
            'source_type': 'us_mint',
            'publisher': 'U.S. Mint',
            'orig_file': f'mint_pages_state_quarters/{key}.txt',
            'program': '50_state_quarters',
        },
        'content': {
            'mimeType': 'text/plain',
            'rawBytes': base64.b64encode(text.encode('utf-8')).decode('ascii'),
        },
    }

def main():
    print('AUTH probe…')
    s, j = call('GET', f'{COL}/engines/morgan-pilot-search', log_resp=False)
    print('engine', s, j.get('displayName'), j.get('name'))
    assert s == 200, j

    # before count
    before = 0; token = None
    DS = f'{COL}/dataStores/morgan-docs/branches/default_branch'
    while True:
        params = {'pageSize': 1000}
        if token: params['pageToken'] = token
        s, j = call('GET', f'{DS}/documents', params=params, log_resp=False)
        assert s == 200, j
        before += len(j.get('documents', []))
        token = j.get('nextPageToken')
        if not token: break
    print('docs_before', before)

    docs = []; manifest = []; failed = []
    for key, url, title in HTML_URLS:
        print('FETCH_HTML', key)
        meta, text = fetch_html(key, url, title)
        manifest.append(meta)
        if text is None:
            failed.append(meta); print('  FAIL', meta.get('error'), meta.get('http')); continue
        docs.append(to_doc(key, title, url, text))
        print('  OK chars', meta['chars'], 'markers', meta.get('markers'))

    for year, ts in EXCEL_YEARS.items():
        print('FETCH_XLS', year)
        meta, text = fetch_excel(year, ts)
        manifest.append(meta)
        if text is None:
            failed.append(meta); print('  FAIL', meta.get('error'), meta.get('http')); continue
        docs.append(to_doc(meta['key'], meta['title'], meta['url'], text))
        print('  OK chars', meta['chars'], 'designs', meta.get('designs'))

    MANIFEST.parent.mkdir(exist_ok=True)
    MANIFEST.write_text(json.dumps({
        'ts': datetime.datetime.now().isoformat(timespec='seconds'),
        'project': 'numista-morgan-pilot',
        'docs_before': before,
        'docs_ok': len(docs),
        'failed': failed,
        'manifest': manifest,
    }, indent=2), encoding='utf-8')
    print('OK', len(docs), 'FAILED', len(failed))
    if not docs:
        raise SystemExit('NO_DOCS_FETCHED')

    batches = [docs[i:i+4] for i in range(0, len(docs), 4)]
    OUT_BATCHES.write_text(json.dumps(batches), encoding='utf-8')
    print('wrote', OUT_BATCHES, 'batches', len(batches))

    call('PATCH', f'{COL}/engines/morgan-pilot-search', params={'updateMask': 'observabilityConfig'},
         body={'observabilityConfig': {'observabilityEnabled': False}}, log_resp=False)

    ops = []
    for i, b in enumerate(batches):
        s, j = call('POST', f'{DS}/documents:import',
                    body={'inlineSource': {'documents': b}, 'reconciliationMode': 'INCREMENTAL'},
                    log_resp=False)
        print('import batch', i, len(b), s, json.dumps({k: j.get(k) for k in ('name', 'error', 'done')})[:400])
        if s >= 300:
            print('IMPORT_FAIL', json.dumps(j)[:800])
            raise SystemExit('IMPORT_FAILED')
        ops.append(j.get('name'))

    for op in ops:
        if not op: continue
        t0 = time.time()
        while time.time() - t0 < 900:
            s, j = call('GET', op, log_resp=False)
            if j.get('done'): break
            time.sleep(10)
        print('op done', j.get('done'), 'meta', json.dumps(j.get('metadata', {}))[:400],
              'err', json.dumps(j.get('error', {}))[:400],
              'resp', json.dumps(j.get('response', {}))[:600])

    after = 0; token = None
    while True:
        params = {'pageSize': 1000}
        if token: params['pageToken'] = token
        s, j = call('GET', f'{DS}/documents', params=params, log_resp=False)
        assert s == 200, j
        after += len(j.get('documents', []))
        token = j.get('nextPageToken')
        if not token: break
    print('docs_after', after)
    RESULT.write_text(json.dumps({
        'docs_before': before,
        'docs_imported': len(docs),
        'docs_listed_total': after,
        'failed': failed,
        'ids': [d['id'] for d in docs],
    }, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
