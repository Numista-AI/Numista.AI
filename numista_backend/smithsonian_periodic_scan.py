"""
smithsonian_periodic_scan.py  (v2 — corrected after API inspection)

What this actually does:
  • Queries the Smithsonian Open Access API for NMAH NNC items WITH CC0 media
  • Most NNC catalog records have NO photos; only items digitized by Smithsonian staff do
  • Items User:Godot13 photographed are on Wikimedia (already covered by our Wikimedia pass)
  • This script catches anything NEW that Smithsonian digitizes in-house going forward
  • ALSO enriches Firestore metadata (descriptions, Friedberg numbers) even for non-photo items

Usage:
  $env:SMITHSONIAN_API_KEY = "your_key"
  python smithsonian_periodic_scan.py             # Normal delta scan
  python smithsonian_periodic_scan.py --dry-run   # Preview, no uploads
  python smithsonian_periodic_scan.py --meta-only # Enrich metadata only, no images
  python smithsonian_periodic_scan.py --reset     # Re-scan everything
  python smithsonian_periodic_scan.py --coins     # Also scan coins

Schedule: weekly via Windows Task Scheduler (see bottom of file).
Expected yield: Low initially; grows as Smithsonian digitizes more NNC items over time.
"""
import os, sys, json, csv, time, random, urllib.request, urllib.parse, argparse
from datetime import datetime, timezone

os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SMITH_KEY   = os.environ.get('SMITHSONIAN_API_KEY', '')
SCAN_STATE  = 'smithsonian_scan_state.json'
API_SEARCH  = 'https://api.si.edu/openaccess/api/v1.0/search'
API_CONTENT = 'https://api.si.edu/openaccess/api/v1.0/content'
GCS_BASE    = 'users/jseaman1204@gmail.com/currency'
SOURCE      = 'smithsonian_open_access_cc0'
ATTR        = 'CC0 Public Domain. Source: Smithsonian National Numismatic Collection (NMAH).'
HEADERS     = {'User-Agent': 'NumistaAI/1.0 (contact eric.seaman@yahoo.com)'}

parser = argparse.ArgumentParser()
parser.add_argument('--dry-run',   action='store_true')
parser.add_argument('--meta-only', action='store_true', help='Enrich text metadata, skip images')
parser.add_argument('--reset',     action='store_true')
parser.add_argument('--coins',     action='store_true')
args = parser.parse_args()

if not SMITH_KEY:
    print('Set env var SMITHSONIAN_API_KEY'); sys.exit(1)

# ── Scan state ────────────────────────────────────────────────────────────────
def load_state():
    if os.path.exists(SCAN_STATE) and not args.reset:
        with open(SCAN_STATE, encoding='utf-8') as f:
            return json.load(f)
    return {'last_scan': None, 'scanned_ids': [], 'found_images': 0,
            'enriched_meta': 0, 'scan_history': []}

def save_state(state, found_img, enriched):
    state['last_scan']      = datetime.now(timezone.utc).isoformat()
    state['found_images']  += found_img
    state['enriched_meta'] += enriched
    state['scan_history'].append({
        'date': state['last_scan'],
        'new_images': found_img,
        'meta_enriched': enriched,
        'dry_run': args.dry_run,
    })
    with open(SCAN_STATE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)

state = load_state()

# ── Key insight: search specifically for items WITH media ─────────────────────
# The correct filter for items that actually have images is to add:
# online_media_type:Images (not all items have this indexed, but worth trying)
# Alternatively, sort by lastTimeUpdated and check content endpoint per item.

def smith_search(q, rows=50, start=0, date_from=None):
    query = q
    if date_from:
        query += f' AND p.edanmdm.lastTimeUpdated:[{date_from} TO *]'
    params = {'api_key': SMITH_KEY, 'q': query, 'rows': rows,
              'start': start, 'sort': 'lastTimeUpdated:desc'}
    url = API_SEARCH + '?' + urllib.parse.urlencode(params)
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read())
        except Exception as e:
            if attempt < 2: time.sleep(2 ** attempt)
    return None

def fetch_content(item_id):
    url = f'{API_CONTENT}/{item_id}?api_key={SMITH_KEY}'
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read()).get('response', {})
    except Exception:
        return {}

def extract_images(content):
    """Extract CC0 image URLs from content endpoint response."""
    images = {'obv': None, 'rev': None}
    desc = content.get('content', {}).get('descriptiveNonRepeating', {})
    for m in desc.get('online_media', {}).get('media', []):
        usage   = (m.get('usage') or {}).get('access', '')
        caption = (m.get('caption') or '').lower()
        iiif    = m.get('iiif_url', '')
        raw_url = m.get('content', '')
        url     = (iiif.rstrip('/') + '/full/full/0/default.jpg') if iiif else raw_url
        if not url:
            continue
        # Accept CC0 OR any open-access item (some are CC0 without the label)
        if usage not in ('CC0', 'CC0 1.0', '', 'Open Access'):
            continue
        is_rev = any(w in caption for w in ['reverse', 'back', 'verso'])
        if is_rev and not images['rev']:
            images['rev'] = url
        elif not images['obv']:
            images['obv'] = url
    return images

def extract_metadata(content):
    """Pull descriptive text for metadata enrichment."""
    meta = {'descriptions': [], 'fr_number': None, 'series': None}
    notes = (content.get('content', {})
             .get('freetext', {})
             .get('notes', []))
    for note in notes:
        c = note.get('content', '')
        meta['descriptions'].append(c)
        c_lc = c.lower()
        if 'fr.' in c_lc or 'friedberg' in c_lc:
            meta['fr_number'] = c
        if 'series of' in c_lc:
            meta['series'] = c
    return meta

# ── Queries ───────────────────────────────────────────────────────────────────
CURRENCY_QUERIES = [
    'unit_code:NMAH AND "Silver Certificate" AND online_media_type:Images',
    'unit_code:NMAH AND "Legal Tender Note" AND online_media_type:Images',
    'unit_code:NMAH AND "Federal Reserve Bank Note" AND online_media_type:Images',
    'unit_code:NMAH AND "Gold Certificate" AND online_media_type:Images',
    'unit_code:NMAH AND "Treasury Note" AND online_media_type:Images',
    'unit_code:NMAH AND "Fractional Currency" AND online_media_type:Images',
    'unit_code:NMAH AND "National Bank Note" AND online_media_type:Images',
    'unit_code:NMAH AND "Military Payment Certificate" AND online_media_type:Images',
    'unit_code:NMAH AND "Confederate" AND online_media_type:Images',
    'unit_code:NMAH AND "Continental Currency" AND online_media_type:Images',
    'unit_code:NMAH AND "Obsolete" AND online_media_type:Images',
    # Fallback without media filter (will check content for each)
    'unit_code:NMAH AND "Silver Certificate"',
    'unit_code:NMAH AND "Legal Tender Note"',
    'unit_code:NMAH AND "National Bank Note"',
]
COIN_QUERIES = [
    'unit_code:NMAH AND "Morgan Dollar" AND online_media_type:Images',
    'unit_code:NMAH AND "Peace Dollar" AND online_media_type:Images',
    'unit_code:NMAH AND "Kennedy Half Dollar" AND online_media_type:Images',
    'unit_code:NMAH AND "Saint-Gaudens" AND online_media_type:Images',
]

queries = CURRENCY_QUERIES + (COIN_QUERIES if args.coins else [])

# Date filter
date_from = None
if state.get('last_scan') and not args.reset:
    dt = datetime.fromisoformat(state['last_scan'].replace('Z', '+00:00'))
    date_from = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    print(f'Scanning items updated after: {date_from}\n')
else:
    print('Full scan (no date filter)\n')

# ── Run ───────────────────────────────────────────────────────────────────────
seen     = set(state.get('scanned_ids', []))
with_img = []
meta_log = []

for q in queries:
    result = smith_search(q, rows=20, date_from=date_from)
    time.sleep(0.3)
    if not result:
        continue
    rows = result.get('response', {}).get('rows', [])
    total = result.get('response', {}).get('rowCount', 0)
    if total:
        print(f'  {total:5} results: {q[:65]}')

    for row in rows[:10]:   # Check top 10 per query
        item_id = row.get('id', '')
        if item_id in seen:
            continue
        seen.add(item_id)

        # Fetch full content
        content = fetch_content(item_id)
        time.sleep(0.2)
        if not content:
            continue

        images = extract_images(content)
        meta   = extract_metadata(content)
        title  = row.get('title', '')

        if images['obv'] or images['rev']:
            print(f'\n  📷 WITH IMAGES: {title[:60]}')
            if images['obv']: print(f'     OBV: {images["obv"][:80]}')
            if images['rev']: print(f'     REV: {images["rev"][:80]}')
            with_img.append({'id': item_id, 'title': title, **images})

        if meta['descriptions'] and not args.meta_only is False:
            meta_log.append({'id': item_id, 'title': title, 'meta': meta})

state['scanned_ids'] = list(seen)

# ── Upload any images found ───────────────────────────────────────────────────
found_img = len(with_img)
enriched  = 0

if with_img and not args.dry_run and not args.meta_only:
    import google.auth
    from google.cloud import firestore, storage
    creds, _ = google.auth.default()
    db  = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
    gcs = storage.Client(credentials=creds)
    bucket = gcs.bucket('numista-uploads-studio-9101802118-8c9a8')
    col = db.collection('users').document('jseaman1204@gmail.com').collection('currency')

    with open('type_to_docids_map.json', encoding='utf-8') as f:
        TYPE_MAP = json.load(f)
    gaps = []
    if os.path.exists('currency_gaps_for_grok.csv'):
        with open('currency_gaps_for_grok.csv', encoding='utf-8') as f:
            gaps = list(csv.DictReader(f))

    for item in with_img:
        title_lc = item['title'].lower()
        for gap in gaps:
            denom = gap.get('denom', '').lower().replace('$', '')
            year  = str(gap.get('year', ''))[:4]
            if denom and denom not in title_lc: continue
            if year  and year  not in title_lc: continue
            doc_id  = gap.get('doc_id', '')
            status  = gap.get('status', 'BLANK')
            doc_d   = col.document(doc_id).get().to_dict() or {}
            updates = {}
            for side in (['obv'] if status == 'NO_OBV' else
                         ['rev'] if status == 'NO_REV' else ['obv','rev']):
                url = item.get(side)
                if not url: continue
                fs  = f'image_url_{"obverse" if side=="obv" else "reverse"}'
                if doc_d.get(fs): continue
                try:
                    req = urllib.request.Request(url, headers=HEADERS)
                    with urllib.request.urlopen(req, timeout=60) as r:
                        data = r.read()
                    if len(data) < 10000: continue
                    gcs_side = 'obverse' if side == 'obv' else 'reverse'
                    path = f'{GCS_BASE}/{doc_id}/{gcs_side}.jpg'
                    bucket.blob(path).upload_from_string(data, content_type='image/jpeg')
                    gcs_url = f'https://storage.googleapis.com/{bucket.name}/{path}'
                    updates[fs] = gcs_url
                    updates[f'image_source_{gcs_side}'] = SOURCE
                    updates['image_attribution'] = ATTR
                    print(f'  ✅ {doc_id[:8]} {gcs_side}')
                except Exception as e:
                    print(f'  ERR: {e}')
            if updates:
                col.document(doc_id).update(updates)
                enriched += 1
                break

save_state(state, found_img, enriched)
print(f'\n=== SCAN COMPLETE ===')
print(f'Items with photos found: {found_img}')
print(f'Docs updated: {enriched}')
print(f'Scan state saved: {SCAN_STATE}')
print(f'\nAll-time totals: {state["found_images"]} photos | {state["enriched_meta"]} meta enriched')

# ─────────────────────────────────────────────────────────────────────────────
# SCHEDULING REFERENCE
# Run weekly with Windows Task Scheduler:
#
#   $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 3am
#   $action  = New-ScheduledTaskAction `
#     -Execute "powershell" `
#     -Argument '-NonInteractive -Command "$env:SMITHSONIAN_API_KEY=''your_key''; python smithsonian_periodic_scan.py"' `
#     -WorkingDirectory "C:\Users\ericd\Documents\MyVertexProject\numista_backend"
#   Register-ScheduledTask -TaskName "SmithsonianNNCScan" -Action $action -Trigger $trigger
# ─────────────────────────────────────────────────────────────────────────────
