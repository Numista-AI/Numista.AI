"""
fix_awq_index_urls.py
The coin_image_index has public_urls pointing to GCS blobs that have literal %20 in
their names. Browsers decode %20 as space, causing 404s. 

Fix: for each AWQ reverse doc, check if the stored URL 404s and if so find a working
alternative (underscore-named version in GCS) and update the index.
"""
import os, sys, urllib.parse
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore, storage

DRY_RUN = False

creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
gcs = storage.Client(credentials=creds)
bucket = gcs.bucket('numista-reference-library')

# List all files in the american_women folder
prefix = 'reference_library/bulk_programs/american_women/'
blobs = {b.name: b for b in bucket.list_blobs(prefix=prefix)}

def best_public_url(blob):
    """Returns a properly encoded public URL for a blob."""
    # URL-encode the path so %20 blobs are addressed as %2520
    encoded_name = urllib.parse.quote(blob.name, safe='/')
    return f"https://storage.googleapis.com/numista-reference-library/{encoded_name}"

print("GCS files:")
for name in sorted(blobs.keys()):
    print(f"  {name}")

# Slug to preferred blob name mapping
# Prefer underscore-named files (more URL-friendly) over %20-named ones
SLUG_TO_BLOB = {
    'maya-angelou':       'reference_library/bulk_programs/american_women/American_Women_quarter_2022_Maya_Angelou.jpeg',
    'anna-may-wong':      'reference_library/bulk_programs/american_women/American_Women_Quarter_2022_Anna_May_Wong.jpg',
    'nina-otero-warren':  'reference_library/bulk_programs/american_women/American_Women_quarter_2022_Nina_Otero-Warren.png',
    'sally-ride':         'reference_library/bulk_programs/american_women/American_Women_quarter_2022_Sally_Ride.png',
    'wilma-mankiller':    'reference_library/bulk_programs/american_women/American_Women_quarter_2022_Wilma_Mankiller.png',
    'bessie-coleman':     'reference_library/bulk_programs/american_women/2023_Bessie_Coleman_Womens_Quarter.jpg',
    'edith-kanaka-ole':   'reference_library/bulk_programs/american_women/2023_Edith_Kanakaʻole_Womens_Quarter.jpg',
    'eleanor-roosevelt':  'reference_library/bulk_programs/american_women/2023_Eleanor_Roosevelt_Womens_Quarter.jpg',
    'jovita-idar':        'reference_library/bulk_programs/american_women/2023_Jovita_Idar_Womens_Quarter.jpg',
    'maria-tallchief':    'reference_library/bulk_programs/american_women/2023%20maria%20tallchief.jpg',  # only %20 version exists
    'celia-cruz':         'reference_library/bulk_programs/american_women/2024_Celia_Cruz_Womens_Quarter.jpg',
    'mary-edwards-walker':'reference_library/bulk_programs/american_women/2024_Mary_Edwards_Walker_Womens_Quarter.jpg',
    'patsy-mink':         'reference_library/bulk_programs/american_women/2024_Patsy_Takemoto_Mink_Womens_Quarter.jpg',
    'pauli-murray':       'reference_library/bulk_programs/american_women/2024%20pauli%20murray.jpg',  # only %20 version
    'zitkala-sa':         'reference_library/bulk_programs/american_women/2024%20zitkala%20sa.jpg',  # only %20 version
    'althea-gibson':      'reference_library/bulk_programs/american_women/Althea_Gibson_quarter.webp',
    'stacey-park-milbern':'reference_library/bulk_programs/american_women/Stacey_Milbern_quarter.webp',
    'vera-rubin':         'reference_library/bulk_programs/american_women/Design_of_U_S_quarter_featuring_Dr_Vera_C_Rubin_rubin-2025-americanwomen-quarterscoin-verarubin.jpg',
}

# For blobs with %20 in name, the public_url must double-encode %20 → %2520 so browser
# decodes to %20 (matching the blob name). OR better: just copy to a clean name.
# Simplest fix: for %20 blobs, create a copy with underscores and use that URL.

print('\n\nFixing coin_image_index URLs...')
idx = db.collection('coin_image_index')
# Get all AWQ reverse docs
years = ['2022', '2023', '2024', '2025']
fixes = []

for year in years:
    # List all AWQ reverse docs for this year
    docs = list(idx.where('program', '==', 'american-women-quarters').where('year', '==', year).stream())
    for d in docs:
        if not d.id.endswith('_reverse'):
            continue
        data = d.to_dict() or {}
        subject = data.get('subject', '')
        rev = data.get('reverse') or {}
        current_url = rev.get('public_url', '')
        
        preferred_blob_name = SLUG_TO_BLOB.get(subject)
        if not preferred_blob_name:
            print(f"  SKIP (no blob mapping): {d.id}")
            continue
        
        # Verify blob exists
        blob = blobs.get(preferred_blob_name)
        if not blob:
            print(f"  MISSING BLOB: {preferred_blob_name}")
            continue
        
        # Generate correct URL
        # For blobs with literal %20 in name, use double-encoding
        if '%20' in preferred_blob_name or '%' in preferred_blob_name:
            # Double-encode: %20 → %2520
            encoded_name = preferred_blob_name.replace('%', '%25')
            new_url = f"https://storage.googleapis.com/numista-reference-library/{encoded_name}"
        else:
            new_url = blob.public_url  # Standard URL for clean names
        
        if current_url != new_url:
            print(f"  FIX: {d.id}")
            print(f"    OLD: {current_url[:80]}")
            print(f"    NEW: {new_url[:80]}")
            fixes.append({'id': d.id, 'new_url': new_url, 'rev': rev})
        else:
            print(f"  OK:  {d.id} → {new_url[:60]}")

print(f'\nTotal fixes: {len(fixes)}')

if not DRY_RUN and fixes:
    for f in fixes:
        updated_rev = dict(f['rev'])
        updated_rev['public_url'] = f['new_url']
        idx.document(f['id']).update({'reverse': updated_rev})
    print('✅ Done.')
