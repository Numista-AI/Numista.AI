"""
coin_legislation_map.py
Congress.gov API integration for Numista.AI.

Maps key numismatic legislation to coin/currency types in Firestore.
Each coin type can display its founding_law card in the detail modal.

Data structure returned per law:
  bill.title              → law name
  bill.congress           → congress number
  bill.introducedDate     → date introduced
  bill.latestAction.text  → "Became Public Law No. XX-YY"
  bill.latestAction.actionDate → enacted date
  bill.legislationUrl     → full congress.gov page
  bill.textVersions.url   → full text API link
"""
import os, sys, json, urllib.request
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore

creds, _ = google.auth.default()
db  = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')

CONGRESS_KEY  = 'gfdOhJU6atRmeO8dR0LuxN3fsUrcZmt5gwv6O1ek'
CONGRESS_BASE = 'https://api.congress.gov/v3'
HDR = {'User-Agent': 'NumistaAI/1.0 (eric@numista.ai)', 'Accept': 'application/json'}

def get_law(congress, law_num):
    url = f'{CONGRESS_BASE}/law/{congress}/pub/{law_num}?api_key={CONGRESS_KEY}&format=json'
    req = urllib.request.Request(url, headers=HDR)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
            # Response key is 'bill' (the bill that became this law)
            bill = data.get('bill', data.get('law', {}))
            if bill:
                enacted = bill.get('latestAction', {}).get('actionDate', '')
                return {
                    'name':          bill.get('title', ''),
                    'public_law':    f'{congress}-{law_num}',
                    'congress':      f'{congress}th Congress',
                    'enacted':       enacted,
                    'introduced':    bill.get('introducedDate', ''),
                    'chamber':       bill.get('originChamber', ''),
                    'congress_url':  bill.get('legislationUrl', ''),
                    'text_api_url':  bill.get('textVersions', {}).get('url', ''),
                    'actions_count': bill.get('actions', {}).get('count', 0),
                    'source':        'congress_gov_api',
                }
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None   # Law predates digital database (~pre-1973)
        print(f'  Error {e.code} for PL {congress}-{law_num}')
    except Exception as e:
        print(f'  Error: {e}')
    return None

# ── Master numismatic legislation table ──────────────────────────────────────
# Format: (congress, pub_law_no, [firestore_type_codes_to_tag])
NUMISMATIC_LAWS = [
    # ── Coins ──────────────────────────────────────────────────────────────
    (89,  81,   ['morgan_dollar', 'coinage_1965'],
     'Coinage Act of 1965 — removed silver from dimes, quarters, halves'),
    (91,  607,  ['eisenhower_dollar'],
     'Eisenhower Dollar Act 1970 \u2014 Title II of Bank Holding Company Act Amendments (PL 91-607)'),
    (95,  447,  ['susan_b_anthony'],
     'Susan B. Anthony Dollar — authorized mini dollar 1979-1981, 1999'),
    (99,  61,   ['silver_eagle', 'gold_eagle', 'bullion'],
     'Liberty Coin Act 1985 — created American Silver & Gold Eagle series'),
    (100, 274,  ['silver_eagle'],
     'United States Commemorative Coin Act 1987'),
    (105, 124,  ['state_quarters'],
     '50 State Quarters Program Act 1997 — 50 quarters over 10 years'),
    (106, 445,  ['sacagawea_dollar'],
     'United States $1 Coin Act 1997 — authorized golden dollar (Sacagawea)'),
    (109, 145,  ['presidential_dollar'],
     'Presidential $1 Coin Act 2005 — 4 presidents per year 2007-2016'),
    (110, 456,  ['america_beautiful'],
     'America\'s Beautiful National Parks Quarter Dollar Coin Act 2008'),
    (112, 209,  ['march_of_dimes'],
     'March of Dimes Commemorative Coin Act of 2012 \u2014 authorized silver dollars issued 2015'),
    # ── Currency / Paper Money ─────────────────────────────────────────────
    (73,  10,   ['federal_reserve_note', 'currency_modern'],
     'Gold Reserve Act 1934 — nationalized gold, ended Gold Certificates'),
    (96,  221,  ['federal_reserve_note'],
     'Depository Institutions Deregulation Act — reformed currency issuance'),
]

print('=== Fetching Numismatic Legislation from Congress.gov API ===\n')

legislation_db = {}

for congress, law_num, type_codes, description in NUMISMATIC_LAWS:
    law_data = get_law(congress, law_num)
    if law_data:
        print(f'✅ PL {congress}-{law_num}: {law_data["name"][:65]}')
        print(f'   Enacted: {law_data["enacted"]} | {law_data["congress"]} | {law_data["actions_count"]} actions')
        legislation_db[f'{congress}-{law_num}'] = {
            **law_data,
            'description': description,
            'applies_to_types': type_codes,
        }
    else:
        print(f'⚠️  PL {congress}-{law_num}: Not in digital database ({description[:50]})')

# ── Save legislation database ─────────────────────────────────────────────────
with open('coin_legislation_db.json', 'w', encoding='utf-8') as f:
    json.dump(legislation_db, f, indent=2)

print(f'\n{len(legislation_db)} laws fetched and saved to coin_legislation_db.json')

# ── Write to Firestore: metadata collection ────────────────────────────────────
print('\nWriting to Firestore metadata collection...')
meta_col = db.collection('metadata').document('coin_legislation')
meta_col.set({
    'laws': legislation_db,
    'last_updated': firestore.SERVER_TIMESTAMP,
    'source': 'congress_gov_api',
    'key_used': CONGRESS_KEY[:8] + '...',
})
print('✅ Saved to Firestore: metadata/coin_legislation')
print('\nUsage in Flutter: read metadata/coin_legislation.laws["{congress}-{law_num}"]')
print('Display in UI: coin detail modal → History tab → "Authorized by Public Law {n}"')
