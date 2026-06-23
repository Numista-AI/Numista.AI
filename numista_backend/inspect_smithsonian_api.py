"""inspect_smithsonian_api.py — Debug raw Smithsonian API response structure."""
import os, urllib.request, urllib.parse, json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

KEY = os.environ.get('SMITHSONIAN_API_KEY', '')
if not KEY:
    print('Set SMITHSONIAN_API_KEY env var'); sys.exit(1)

API = 'https://api.si.edu/openaccess/api/v1.0/search'
HEADERS = {'User-Agent': 'NumistaAI/1.0 (contact eric.seaman@yahoo.com)'}

# Test queries
TESTS = [
    'unit_code:NMAH AND "Silver Certificate"',
    'unit_code:NMAH AND online_media.usage.access:CC0',
    'unit_code:NMAH AND Silver Certificate',
    'unit_code:NMAH AND type:edanmdm AND "Silver Certificate"',
]

for q in TESTS:
    params = {'api_key': KEY, 'q': q, 'rows': 1}
    url = API + '?' + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        total = data.get('response', {}).get('rowCount', 0)
        rows  = data.get('response', {}).get('rows', [])
        print(f'\nQuery: {q[:60]}')
        print(f'  Total: {total} results')
        if rows:
            row   = rows[0]
            title = row.get('title', '')
            print(f'  First: {title[:70]}')
            # Drill into media
            content   = row.get('content', {})
            desc      = content.get('descriptiveNonRepeating', {})
            media_blk = desc.get('online_media', {})
            media_lst = media_blk.get('media', [])
            print(f'  Media count: {len(media_lst)}')
            for i, m in enumerate(media_lst[:2]):
                print(f'  media[{i}] keys: {list(m.keys())}')
                print(f'    usage: {m.get("usage")}')
                print(f'    iiif:  {str(m.get("iiif_url",""))[:70]}')
                print(f'    thumb: {str(m.get("thumbnail",""))[:70]}')
                print(f'    caption: {str(m.get("caption",""))[:50]}')
    except Exception as e:
        print(f'  ERROR: {e}')

# Also dump full first row of first working query
print('\n\n=== FULL FIRST ROW JSON ===')
params = {'api_key': KEY, 'q': 'unit_code:NMAH AND Silver Certificate', 'rows': 1}
url = API + '?' + urllib.parse.urlencode(params)
req = urllib.request.Request(url, headers=HEADERS)
with urllib.request.urlopen(req, timeout=15) as r:
    data = json.loads(r.read())
rows = data.get('response', {}).get('rows', [])
if rows:
    # Print just the media section
    desc = rows[0].get('content', {}).get('descriptiveNonRepeating', {})
    print(json.dumps(desc.get('online_media', {}), indent=2)[:3000])
