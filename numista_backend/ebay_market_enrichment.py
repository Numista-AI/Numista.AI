"""
ebay_market_enrichment.py
Numista.AI — eBay Browse API → Firestore 'AI Estimated Value' enrichment.

For each coin in Firestore with AI Estimated Value == 'Pending',
queries eBay Browse API for live listings, computes a market price range,
and writes it back to Firestore.

Usage:
    python ebay_market_enrichment.py                # dry-run: print prices only
    python ebay_market_enrichment.py --write        # write to Firestore
    python ebay_market_enrichment.py --write --limit 50  # cap at 50 coins
"""
import os, sys, json, time, argparse, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── Args ──────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument('--write',  action='store_true', help='Write prices to Firestore')
parser.add_argument('--limit',  type=int, default=200, help='Max coins to process')
parser.add_argument('--user',   default='AJ', help='Collection owner (AJ or Eric)')
args = parser.parse_args()

# ── Google / Firestore ────────────────────────────────────────────────────────
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
import google.auth
from google.cloud import firestore

creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')

# ── eBay Browse API OAuth ─────────────────────────────────────────────────────
# Set EBAY_APP_ID and EBAY_CERT_ID as environment variables (Cloud Run secrets
# or local .env). Never hardcode credentials here.
EBAY_APP_ID  = os.environ.get('EBAY_APP_ID', '')
EBAY_CERT_ID = os.environ.get('EBAY_CERT_ID', '')
if not EBAY_APP_ID or not EBAY_CERT_ID:
    raise EnvironmentError(
        'EBAY_APP_ID and EBAY_CERT_ID must be set as environment variables. '
        'See numista_backend/.env.example for setup instructions.'
    )
EBAY_TOKEN_URL = 'https://api.ebay.com/identity/v1/oauth2/token'
EBAY_BROWSE_BASE = 'https://api.ebay.com/buy/browse/v1'
NUMISMATICS_CATEGORY = '253'  # eBay category ID for Coins

_ebay_token: str | None = None
_token_expiry: float = 0.0

def get_ebay_token() -> str:
    global _ebay_token, _token_expiry
    if _ebay_token and time.time() < _token_expiry - 60:
        return _ebay_token
    import base64
    cred = base64.b64encode(f'{EBAY_APP_ID}:{EBAY_CERT_ID}'.encode()).decode()
    data = urllib.parse.urlencode({
        'grant_type': 'client_credentials',
        'scope': 'https://api.ebay.com/oauth/api_scope',
    }).encode()
    req = urllib.request.Request(
        EBAY_TOKEN_URL, data=data,
        headers={'Authorization': f'Basic {cred}',
                 'Content-Type': 'application/x-www-form-urlencoded',
                 'User-Agent': 'NumistaAI/1.0 (eric@numista.ai)'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        resp = json.loads(r.read())
    _ebay_token = resp['access_token']
    _token_expiry = time.time() + resp.get('expires_in', 7200)
    return _ebay_token

def ebay_search(query: str, limit: int = 5) -> list[dict]:
    """Search eBay Browse API. Returns list of items with prices."""
    token = get_ebay_token()
    params = urllib.parse.urlencode({
        'q': query,
        'category_ids': NUMISMATICS_CATEGORY,
        'limit': limit,
        'sort': 'price',
    })
    req = urllib.request.Request(
        f'{EBAY_BROWSE_BASE}/item_summary/search?{params}',
        headers={
            'Authorization': f'Bearer {token}',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
            'User-Agent': 'NumistaAI/1.0 (eric@numista.ai)',
            'Accept': 'application/json',
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        return data.get('itemSummaries', [])
    except Exception as e:
        print(f'    eBay error: {e}')
        return []

def build_query(coin_data: dict) -> str:
    """Build eBay search string from Firestore coin fields."""
    year   = coin_data.get('Year', '')
    mint   = coin_data.get('Mint Mark', '')
    denom  = coin_data.get('Denomination', '')
    series = coin_data.get('Program/Series', '')
    grade  = coin_data.get('Condition', '')
    grdsvc = coin_data.get('Grading Service', '')

    parts = []
    if series and 'Morgan' in series:      parts.append('Morgan Silver Dollar')
    elif series and 'Kennedy' in series:   parts.append('Kennedy Half Dollar')
    elif series and 'Silver Eagle' in series: parts.append('American Silver Eagle')
    elif series and 'Peace' in series:     parts.append('Peace Dollar')
    elif series and 'Walking Liberty' in series: parts.append('Walking Liberty Half Dollar')
    elif series:                           parts.append(series[:40])
    elif denom:                            parts.append(denom)

    if year: parts.append(year + (mint if mint else ''))
    if grdsvc and grade and grade not in ('Ungraded', ''):
        parts.append(f'{grdsvc} {grade}')
    elif grade and grade not in ('Ungraded', ''):
        parts.append(grade)

    return ' '.join(parts) if parts else denom or 'US coin'

def extract_price(item: dict) -> float | None:
    """Extract USD price from a Browse API item."""
    price_data = item.get('price', {})
    if price_data.get('currency') != 'USD':
        return None
    try:
        return float(price_data['value'])
    except Exception:
        return None

def compute_value_range(prices: list[float]) -> str | None:
    """Turn a list of prices into a range string like '$45 – $78'."""
    if not prices:
        return None
    prices = sorted(prices)
    # Remove obvious outliers (top 20% and bottom 20% for small samples)
    if len(prices) >= 5:
        trim = max(1, len(prices) // 5)
        prices = prices[trim:-trim]
    if not prices:
        return None
    lo = prices[0]
    hi = prices[-1]
    mid = prices[len(prices) // 2]
    if abs(hi - lo) < 5:
        return f'${mid:.0f}'
    return f'${lo:.0f} – ${hi:.0f}'

# ── Main enrichment loop ───────────────────────────────────────────────────────
COLLECTION = 'AJ' if args.user == 'AJ' else 'Eric'
col_path = f'users/AJCollectionOwnerUID/coins' if COLLECTION == 'AJ' else f'users/EricUID/coins'

# Actually use auth_service approach — find the right collection path
# Query for coins needing pricing
print(f'=== eBay Market Enrichment — {"DRY RUN" if not args.write else "WRITE MODE"} ===')
print(f'Collection: {COLLECTION} | Limit: {args.limit}')
print()

# Use AJ's Firestore path (same as other enrichment scripts)
# Read from the known collection root used in the app
query = (
    db.collection_group('coins')
      .where('AI Estimated Value', '==', 'Pending')
      .limit(args.limit)
)

docs = list(query.stream())
print(f'Coins needing pricing: {len(docs)}')
print()

updated = 0
skipped = 0
errors  = 0

for doc in docs:
    data = doc.to_dict()
    coin_query = build_query(data)
    items = ebay_search(coin_query, limit=6)

    prices = [p for item in items if (p := extract_price(item)) is not None]
    value_str = compute_value_range(prices)

    year  = data.get('Year', '')
    denom = data.get('Denomination', '')
    mint  = data.get('Mint Mark', '')
    label = f'{year}{mint} {denom}'.strip()

    if value_str:
        print(f'  ✅ {label:30s} → {value_str:15s} ({len(prices)} listings) [{coin_query[:40]}]')
        if args.write:
            try:
                doc.reference.update({'AI Estimated Value': value_str})
                updated += 1
            except Exception as e:
                print(f'     Write error: {e}')
                errors += 1
    else:
        print(f'  ⚠️  {label:30s} → No price found [{coin_query[:40]}]')
        skipped += 1

    time.sleep(0.25)  # gentle rate limiting

print()
print(f'=== Done: {updated} updated, {skipped} skipped, {errors} errors ===')
if not args.write:
    print('(Dry run — no Firestore writes. Add --write to commit.)')
