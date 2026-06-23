"""read_pcgs_swagger.py — Find real endpoint paths from the PCGS Swagger UI."""
import urllib.request, json, sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TOKEN = 'H7yYuwz6oDnLmtz0M-8iaYFEdE9okmmZjL0u_EpOdVgYPOZUKHhaOjdJlPiXy-TTk_lOAzOsRzdm97n2hP3N5LpagAmjIX9xObLNmE3VBefWJU9dtNkU3QH4m1WFIHEiIzVbFUgdZplfWEKfThe3w0FGclodfBim0Vu0SPplpgrzprFzeqkF2Q7Q_zZsHGvXJ4sThOS_7VADHbn1ocRmqhFYb7rglbZ8vMb_wlAyiZjM9Yc7J-5e2A_OW-quh1WdziPtXT3Zxfg7mXOaA7NXDDmnzPkzYNPkKQElLpcY5W27AMDw'
HEADERS = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/json',
           'User-Agent': 'NumistaAI/1.0 (eric@numista.ai)'}

# Read Swagger HTML page to find spec JSON URL
req = urllib.request.Request('https://api.pcgs.com/publicapi/swagger', headers=HEADERS)
with urllib.request.urlopen(req, timeout=15) as r:
    html = r.read().decode('utf-8', errors='replace')

# Extract URLs from swagger page
print('=== Links found in Swagger HTML ===')
urls_found = re.findall(r'(?:url|href|src)\s*[=:]\s*["\']([^"\']+)["\']', html)
for u in urls_found[:20]:
    print(f'  {u}')

# Save full swagger page for manual inspection
with open('pcgs_swagger.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f'\nSwagger HTML saved ({len(html)} chars) → pcgs_swagger.html')

# Try common swagger JSON spec locations
print('\n=== Trying Swagger JSON spec endpoints ===')
SPEC_PATHS = [
    '/publicapi/swagger/docs/v1',
    '/publicapi/swagger/docs/v2',
    '/publicapi/swagger/v1/swagger.json',
    '/publicapi/swagger/v2/swagger.json',
    '/publicapi/api-docs',
    '/publicapi/api-docs/v1',
]
for path in SPEC_PATHS:
    url = 'https://api.pcgs.com' + path
    req2 = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req2, timeout=10) as r2:
            data = json.loads(r2.read())
            print(f'FOUND SPEC at {path}:')
            for ep in list(data.get('paths', {}).keys())[:30]:
                print(f'  {ep}')
            with open('pcgs_swagger_spec.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print(f'Full spec saved to pcgs_swagger_spec.json')
            break
    except urllib.error.HTTPError as e:
        print(f'  {path}: HTTP {e.code}')
    except Exception as e:
        print(f'  {path}: {e}')
