"""inspect_smithsonian_content.py — Test the content endpoint for image URLs."""
import os, urllib.request, urllib.parse, json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

KEY = os.environ.get('SMITHSONIAN_API_KEY', '')
API_SEARCH  = 'https://api.si.edu/openaccess/api/v1.0/search'
API_CONTENT = 'https://api.si.edu/openaccess/api/v1.0/content'
HEADERS = {'User-Agent': 'NumistaAI/1.0 (contact eric.seaman@yahoo.com)'}

# Step 1: Search for Silver Certificates, get IDs
params = {'api_key': KEY, 'q': 'unit_code:NMAH AND Silver Certificate', 'rows': 5}
url = API_SEARCH + '?' + urllib.parse.urlencode(params)
req = urllib.request.Request(url, headers=HEADERS)
with urllib.request.urlopen(req, timeout=15) as r:
    data = json.loads(r.read())

rows = data.get('response', {}).get('rows', [])
print(f'Search returned {len(rows)} rows\n')

# Step 2: For first 3 IDs, call content endpoint
for row in rows[:3]:
    item_id = row.get('id', '')
    title   = row.get('title', '')
    print(f'Item: {title[:60]}')
    print(f'  ID: {item_id}')

    content_url = f'{API_CONTENT}/{item_id}?api_key={KEY}'
    req2 = urllib.request.Request(content_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req2, timeout=15) as r2:
            content_data = json.loads(r2.read())
        # Find media in content response
        resp = content_data.get('response', {})
        desc = resp.get('content', {}).get('descriptiveNonRepeating', {})
        media_blk = desc.get('online_media', {})
        media_lst = media_blk.get('media', [])
        print(f'  Media count: {len(media_lst)}')
        for i, m in enumerate(media_lst[:3]):
            print(f'  [{i}] type={m.get("type")} usage={m.get("usage")}')
            print(f'       iiif:    {str(m.get("iiif_url",""))[:80]}')
            print(f'       content: {str(m.get("content",""))[:80]}')
            print(f'       caption: {str(m.get("caption",""))[:60]}')
        if not media_lst:
            # Dump the full resp keys to understand structure
            print(f'  Content keys: {list(resp.keys())}')
            print(f'  Desc keys: {list(desc.keys())}')
            # Try alternate media path
            for key in resp:
                if 'media' in str(key).lower() or 'image' in str(key).lower():
                    print(f'  Found key with media: {key}')
    except Exception as e:
        print(f'  ERROR: {e}')
    print()

# Step 3: Also try the open access content endpoint with a known NNC item
# Use the item we know exists: "1 Dollar, Silver Certificate, United States, 1899"
print('\n=== Searching for specific known item ===')
params = {
    'api_key': KEY,
    'q': 'unit_code:NMAH AND "1 Dollar, Silver Certificate, United States, 1899"',
    'rows': 1,
}
url2 = API_SEARCH + '?' + urllib.parse.urlencode(params)
req3 = urllib.request.Request(url2, headers=HEADERS)
with urllib.request.urlopen(req3, timeout=15) as r3:
    data2 = json.loads(r3.read())

rows2 = data2.get('response', {}).get('rows', [])
if rows2:
    item_id = rows2[0].get('id', '')
    print(f'Found ID: {item_id}')
    content_url = f'{API_CONTENT}/{item_id}?api_key={KEY}'
    req4 = urllib.request.Request(content_url, headers=HEADERS)
    with urllib.request.urlopen(req4, timeout=15) as r4:
        raw = r4.read()
    full_data = json.loads(raw)
    # Print first 4000 chars of full response to understand structure
    print(json.dumps(full_data, indent=2)[:4000])
