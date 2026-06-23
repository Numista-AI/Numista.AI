"""discover_pcgs_endpoints.py — Find real endpoint names via ASP.NET Help and variations."""
import urllib.request, urllib.parse, json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TOKEN = 'H7yYuwz6oDnLmtz0M-8iaYFEdE9okmmZjL0u_EpOdVgYPOZUKHhaOjdJlPiXy-TTk_lOAzOsRzdm97n2hP3N5LpagAmjIX9xObLNmE3VBefWJU9dtNkU3QH4m1WFIHEiIzVbFUgdZplfWEKfThe3w0FGclodfBim0Vu0SPplpgrzprFzeqkF2Q7Q_zZsHGvXJ4sThOS_7VADHbn1ocRmqhFYb7rglbZ8vMb_wlAyiZjM9Yc7J-5e2A_OW-quh1WdziPtXT3Zxfg7mXOaA7NXDDmnzPkzYNPkKQElLpcY5W27AMDw'

BASE = 'https://api.pcgs.com/publicapi'
HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Accept': 'application/json',
    'User-Agent': 'NumistaAI/1.0 (eric@numista.ai)',
}

def call(path, params=None, raw=False):
    url = BASE + path
    if params:
        url += '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            body = r.read()
            if raw:
                return r.status, body.decode('utf-8', errors='replace')
            return r.status, json.loads(body)
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        if raw:
            return e.code, body
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body[:300]

# Try API help/swagger pages
print('=== Looking for API documentation pages ===')
for path in ['/help', '/Help', '/swagger', '/swagger/ui', '/', '/v1', '/v2',
             '/api', '/coindetail', '/CoinDetail']:
    status, data = call(path, raw=True)
    snippet = str(data)[:100].replace('\n', ' ')
    print(f'  {status} {path}: {snippet}')

# Try coindetail action name variations
print('\n=== CoinDetail action name variations ===')
ACTIONS = [
    'GetCoinFactsByCertNumber',
    'GetCoinFactsByCertNo',
    'GetByCertNumber',
    'GetByCertNo',
    'GetCoinByCertNumber',
    'GetCoinByCertNo',
    'CoinDetailByCertNo',
    'GetCoinDetail',
    'GetAll',
    'Get',
]
for action in ACTIONS:
    status, data = call(f'/coindetail/{action}', {'certno': 12345678})
    if isinstance(data, dict):
        print(f'  ✅ {action}: {status} — {json.dumps(data)[:150]}')
    else:
        short = str(data)[:80].replace('\n', ' ')
        print(f'  {status} {action}: {short}')

# Try price endpoint variations
print('\n=== Price endpoint variations ===')
PRICE_ACTIONS = [
    'GetCoinFactsByPCGSNo',
    'GetByPCGSNo',
    'GetPricesByPCGSNo',
    'GetCoinPrices',
    'CurrentPrices',
    'GetCurrentPrices',
]
for action in PRICE_ACTIONS:
    status, data = call(f'/coindetail/{action}', {'pcgsnumber': 7130})
    if isinstance(data, dict):
        print(f'  ✅ {action}: {status} — {json.dumps(data)[:150]}')
    else:
        short = str(data)[:80].replace('\n', ' ')
        print(f'  {status} {action}: {short}')

# Also try alternate controller names
print('\n=== Alternate controller names ===')
for ctrl in ['coinfacts', 'CoinFacts', 'coin', 'Coin', 'cert', 'Cert',
             'certification', 'Certification', 'prices', 'Prices']:
    status, data = call(f'/{ctrl}/GetCoinFactsByCertNumber', {'certno': 12345678})
    if isinstance(data, dict):
        print(f'  ✅ /{ctrl}/: {status} — {json.dumps(data)[:150]}')
    else:
        short = str(data)[:80].replace('\n', ' ')
        is_json = str(data).startswith('{')
        marker = '~JSON~' if is_json else ''
        print(f'  {status} /{ctrl}/: {marker}{short}')
