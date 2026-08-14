# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import os
import json
import re
import sys
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage

# Force UTF-8 stdout
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 1. Initialize Firebase & GCS
SA_KEY = 'numista_backend/serviceAccountKey.json'
cred = credentials.Certificate(SA_KEY)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
gcs_client = storage.Client.from_service_account_json(SA_KEY)
ref_bucket = gcs_client.bucket('numista-reference-library')

BASE_GCS_URL = "https://storage.googleapis.com/numista-reference-library"

def get_public_url(blob_path):
    return f"{BASE_GCS_URL}/{blob_path}"

# Obverse image lookups
OBV_50_STATE_P = get_public_url("reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Philadelphia_29.jpg")
OBV_50_STATE_D = get_public_url("reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg")
OBV_50_STATE_S = get_public_url("reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_proof_obverse__28San_Francisco_29.jpg")

# Specific known reverse URLs
SPECIAL_REVERSES = {
    "american samoa": get_public_url("reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-national-park-of-american-samoa-uncirculated-reverse.jpg"),
    "national park of american samoa": get_public_url("reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-national-park-of-american-samoa-uncirculated-reverse.jpg"),
    "national park of american samoa (american samoa)": get_public_url("reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-national-park-of-american-samoa-uncirculated-reverse.jpg"),
    "arches": get_public_url("reference_library/atb_quarters/2014-america-the-beautiful-quarters-coin-arches-utah-uncirculated-reverse.jpg"),
    "arches national park (utah)": get_public_url("reference_library/atb_quarters/2014-america-the-beautiful-quarters-coin-arches-utah-uncirculated-reverse.jpg"),
    "arches national park": get_public_url("reference_library/atb_quarters/2014-america-the-beautiful-quarters-coin-arches-utah-uncirculated-reverse.jpg"),
    "virginia": get_public_url("reference_library/bulk_programs/50_state_quarters/2000-50-state-quarters-coin-virginia-uncirculated-reverse.jpg"),
    "general george washington crossing the delaware": get_public_url("reference_library/bulk_programs/washington_crossing_delaware/2021-general-george-washington-crossing-the-delaware-quarter-uncirculated-reverse.jpg"),
    "washington crossing the delaware": get_public_url("reference_library/bulk_programs/washington_crossing_delaware/2021-general-george-washington-crossing-the-delaware-quarter-uncirculated-reverse.jpg"),
    "guam": get_public_url("reference_library/bulk_programs/us_territories/2009-dc-us-territories-quarters-coin-guam-uncirculated-reverse.jpg"),
}

# 2. Build In-Memory Reference Blob Index
print("Building reference library image index from GCS...")
all_ref_blobs = list(ref_bucket.list_blobs())
blob_names = [b.name for b in all_ref_blobs]

# ATB Obverses
ATB_OBV_MAP = {}
for b in blob_names:
    if "atb_quarters" in b and "obverse" in b:
        m = re.search(r"(\d{4}).*obverse-([a-z]+)", b, re.IGNORECASE)
        if m:
            yr, mint_str = m.group(1), m.group(2).upper()
            mint_key = 'P' if 'P' in mint_str or 'PHILADELPHIA' in mint_str else ('D' if 'D' in mint_str or 'DENVER' in mint_str else 'S')
            ATB_OBV_MAP[(yr, mint_key)] = get_public_url(b)

for yr in range(2010, 2022):
    for m in ['P', 'D', 'S']:
        if (str(yr), m) not in ATB_OBV_MAP:
            closest = [url for (y, mt), url in ATB_OBV_MAP.items() if mt == m]
            ATB_OBV_MAP[(str(yr), m)] = closest[0] if closest else (OBV_50_STATE_P if m == 'P' else OBV_50_STATE_D)

# 50 State Reverses map
STATE_REV_MAP = {}
for b in blob_names:
    if "bulk_programs/50_state_quarters" in b and "reverse" in b:
        m = re.search(r"\d{4}-50-state-quarters-coin-([a-z\-]+)-", b)
        if m:
            state_slug = m.group(1).replace("-", " ").strip()
            STATE_REV_MAP[state_slug] = get_public_url(b)

# ATB Reverses map
ATB_REV_MAP = {}
for b in blob_names:
    if ("atb_quarters" in b or "bulk_programs/america_the_beautiful" in b) and "reverse" in b:
        ATB_REV_MAP[b] = get_public_url(b)

# Territories Reverses map
TERRITORY_REV_MAP = {}
for b in blob_names:
    if "us_territories" in b and "reverse" in b:
        m = re.search(r"2009-dc-us-territories-quarters-coin-([a-z\-]+)-", b)
        if m:
            terr_slug = m.group(1).replace("-", " ").strip()
            TERRITORY_REV_MAP[terr_slug] = get_public_url(b)

def find_reverse(program, theme):
    if not theme:
        return None
    clean = theme.lower().strip()
    if clean in SPECIAL_REVERSES:
        return SPECIAL_REVERSES[clean]
    
    if "50 state" in program.lower():
        if clean in STATE_REV_MAP:
            return STATE_REV_MAP[clean]
        for k, v in STATE_REV_MAP.items():
            if k in clean or clean in k:
                return v
    elif "beautiful" in program.lower():
        clean_park = re.sub(r"\(.*?\)", "", clean).replace("national", "").replace("park", "").replace("forest", "").replace("wildlife", "").replace("refuge", "").replace("historic", "").replace("site", "").replace("memorial", "").replace("seashore", "").replace("monument", "").replace("riverways", "").replace("lakeshore", "").replace("wilderness", "").strip()
        words = [w for w in clean_park.split() if len(w) > 2]
        for b, url in ATB_REV_MAP.items():
            b_lower = b.lower()
            if all(w in b_lower for w in words):
                return url
        for b, url in ATB_REV_MAP.items():
            b_lower = b.lower()
            if any(w in b_lower for w in words):
                return url
    elif "territor" in program.lower():
        if clean in TERRITORY_REV_MAP:
            return TERRITORY_REV_MAP[clean]
        for k, v in TERRITORY_REV_MAP.items():
            if k in clean or clean in k:
                return v
    return None

# 3. Load Ground Truth Extracted Checklists
with open('numista_backend/_scripts/extracted_beta_checklist.json', encoding='utf-8') as f:
    extracted_data = json.load(f)

# Load Current Firestore Coins for eric.seaman@yahoo.com
user_coins_ref = db.collection('users').document('eric.seaman@yahoo.com').collection('coins')
docs = list(user_coins_ref.stream())

coins_to_heal = []
for d in docs:
    data = d.to_dict()
    data['doc_id'] = d.id
    dt = str(data.get('created_at') or data.get('date_added') or '')
    if dt.startswith('2026-08-14'):
        coins_to_heal.append(data)

print(f"Total coins from 2026-08-14 to heal: {len(coins_to_heal)}")

# Match specific known hardware agent coin
for c in coins_to_heal:
    did = c['doc_id']
    if did == 'b2eb564e-9b5c-46ac-bb4a-cacaf1f89ac8' or c.get('source') == 'Hardware Agent':
        c['Theme/Subject'] = 'General George Washington Crossing the Delaware'
        c['theme_subject'] = 'General George Washington Crossing the Delaware'
        c['Program / Series'] = 'Washington Quarter'
        c['program_series'] = 'Washington Quarter'
        c['image_url_obverse'] = get_public_url('reference_library/bulk_programs/washington_crossing_delaware/2021-general-george-washington-crossing-the-delaware-quarter-uncirculated-obverse-philadelphia.jpg')
        c['image_url_reverse'] = SPECIAL_REVERSES['general george washington crossing the delaware']
        c['enrichment_status'] = 'enriched'
        c['storage_location'] = 'Album / Raw'
        c['Storage Location'] = 'Album / Raw'

    elif did == '5a36d57e-063e-4d09-b8f8-4f1c593900d4':  # 2000-P Virginia
        c['Theme/Subject'] = 'Virginia'
        c['theme_subject'] = 'Virginia'
        c['Program / Series'] = '50 State Quarters'
        c['program_series'] = '50 State Quarters'
        c['image_url_obverse'] = OBV_50_STATE_P
        c['image_url_reverse'] = SPECIAL_REVERSES['virginia']
        c['enrichment_status'] = 'enriched'

    elif did == 'fae0708e-2aea-44f9-b072-c1d6a17362a7':  # 2014-D Arches
        c['Theme/Subject'] = 'Arches National Park (Utah)'
        c['theme_subject'] = 'Arches National Park (Utah)'
        c['Program / Series'] = 'America the Beautiful Quarters'
        c['program_series'] = 'America the Beautiful Quarters'
        c['image_url_obverse'] = ATB_OBV_MAP.get(('2014', 'D'))
        c['image_url_reverse'] = SPECIAL_REVERSES['arches']
        c['enrichment_status'] = 'enriched'

    elif did == '2debc064-1efc-4c2a-abb9-eb7c1811f3e5':  # 2020-P American Samoa
        c['Theme/Subject'] = 'National Park of American Samoa (American Samoa)'
        c['theme_subject'] = 'National Park of American Samoa (American Samoa)'
        c['Program / Series'] = 'America the Beautiful Quarters'
        c['program_series'] = 'America the Beautiful Quarters'
        c['image_url_obverse'] = ATB_OBV_MAP.get(('2020', 'P'))
        c['image_url_reverse'] = SPECIAL_REVERSES['american samoa']
        c['enrichment_status'] = 'enriched'

# Apply batch update to Firestore
print("Applying full update to Firestore with merge=True...")
batch = db.batch()
count = 0

for c in coins_to_heal:
    doc_id = c['doc_id']
    theme = c.get('Theme/Subject') or c.get('theme_subject')
    prog = c.get('Program / Series') or c.get('program_series') or '50 State Quarters'
    mint = str(c.get('Mint Mark') or c.get('mint') or 'P').upper()
    yr = str(c.get('Year') or c.get('year') or '')
    
    obv = c.get('image_url_obverse')
    if not obv:
        if 'beautiful' in prog.lower():
            obv = ATB_OBV_MAP.get((yr, mint), OBV_50_STATE_P if mint == 'P' else OBV_50_STATE_D)
        else:
            obv = OBV_50_STATE_P if mint == 'P' else (OBV_50_STATE_D if mint == 'D' else OBV_50_STATE_S)
            
    rev = c.get('image_url_reverse') or find_reverse(prog, theme)
    
    update_data = {
        "Program / Series": prog,
        "program_series": prog,
        "Theme/Subject": theme,
        "theme_subject": theme,
        "image_url_obverse": obv,
        "image_url_reverse": rev,
        "enrichment_status": "enriched",
        "Condition": "Unspecified / Raw",
        "Country": "USA",
        "country": "USA",
        "is_foreign": False,
    }
    
    batch.set(user_coins_ref.document(doc_id), update_data, merge=True)
    count += 1

batch.commit()
print(f"\n[DONE] Successfully healed and updated all {count} coins in Firestore!")
