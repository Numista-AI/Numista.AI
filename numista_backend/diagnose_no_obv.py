"""diagnose_no_obv.py — identify new types and test Wikimedia filenames for $1 FRN"""
import os, sys, json, urllib.request, urllib.parse
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore

creds, _ = google.auth.default()
db  = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
col = db.collection('users').document('jseaman1204@gmail.com').collection('currency')

with open('type_to_docids_map.json', encoding='utf-8') as f:
    TYPE_MAP = json.load(f)

print('=== TYPE_197-206 identity ===')
for tid in ['TYPE_197','TYPE_198','TYPE_199','TYPE_200','TYPE_201','TYPE_202','TYPE_203','TYPE_206']:
    for doc_id in TYPE_MAP.get(tid, [])[:1]:
        data = col.document(doc_id).get().to_dict() or {}
        lbl  = data.get('currency_type_label','')
        denom = data.get('Denomination','')
        year  = data.get('Year','')
        desc  = data.get('Description','')[:70]
        print(f'  {tid}: {lbl} | {denom} | {year} | {desc}')
    if tid not in TYPE_MAP:
        print(f'  {tid}: NOT IN MAP')

HEADERS = {'User-Agent': 'NumistaAI/1.0 (contact eric.seaman@yahoo.com)'}

print('\n=== Wikimedia $1 FRN obverse filename tests ===')
candidates = [
    'US_One_Dollar_Bill_obverse.jpg',
    'United States one dollar bill, obverse.jpg',
    'US-$1-FRN-1988.jpg',
    'US-$1-FRN-2009-Fr.3000.jpg',
    'One dollar bill.jpg',
    'US $1 bill obverse.jpg',
    'US-$1-FRN-1969.jpg',
    '$1 Federal Reserve Note obverse.jpg',
    'US-$1-FRN-2017.jpg',
    'Series 2009 $1 Federal Reserve Note.jpg',
]
for fname in candidates:
    api = ('https://commons.wikimedia.org/w/api.php?action=query&titles=File:'
           + urllib.parse.quote(fname, safe='') + '&prop=imageinfo&iiprop=url&format=json')
    try:
        req = urllib.request.Request(api, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        found = False
        for page in data.get('query', {}).get('pages', {}).values():
            ii = page.get('imageinfo', [])
            if ii:
                print(f'  FOUND: {fname}')
                print(f'         {ii[0]["url"][:100]}')
                found = True
        if not found:
            print(f'  miss:  {fname}')
    except Exception as e:
        print(f'  error: {fname} — {e}')

print('\n=== Wikimedia $20 1914 FRN obverse tests ===')
candidates20 = [
    'US-$20-FRN-1914-Fr.960a.jpg',
    'US-$20-FRN-1914-large-size.jpg',
    '$20 Federal Reserve Note 1914.jpg',
    'US $20 Federal Reserve Note 1914 obverse.jpg',
    'US-$20-Federal-Reserve-Note-1914.jpg',
]
for fname in candidates20:
    api = ('https://commons.wikimedia.org/w/api.php?action=query&titles=File:'
           + urllib.parse.quote(fname, safe='') + '&prop=imageinfo&iiprop=url&format=json')
    try:
        req = urllib.request.Request(api, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        found = False
        for page in data.get('query', {}).get('pages', {}).values():
            ii = page.get('imageinfo', [])
            if ii:
                print(f'  FOUND: {fname}')
                print(f'         {ii[0]["url"][:100]}')
                found = True
        if not found:
            print(f'  miss:  {fname}')
    except Exception as e:
        print(f'  error: {fname} — {e}')
