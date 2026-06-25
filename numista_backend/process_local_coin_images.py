#!/usr/bin/env python3
"""
process_local_coin_images.py
============================
Processes local coin image files and uploads them to GCS reference library,
then updates Firestore for matching coins in all user accounts.

Tasks:
  TASK 1: Upload 86 ATB quarter images from Manual downloaded Coin Images/America the Beautiful/
  TASK 2: Upload New Coin Images (Hawaii/Jamul, Other special coins, generic denominations)
  TASK 3: Update Firestore ATB coins — replace Wikimedia URLs with GCS, fill empty URLs
  TASK 4: Update Firestore Silver/Gold Eagle coins

Usage:
    python process_local_coin_images.py [--dry-run]

Output:
    local_image_upload_log.json
"""

import io
import json
import os
import re
import sys
import time
import shutil
import argparse
from pathlib import Path
from datetime import datetime

import requests

sys.stdout = io.TextIOWrapper(
    sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True
)

# ─── Config ───────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
SA_KEY       = os.path.join(SCRIPT_DIR, 'serviceAccountKey.json.json')
PROJECT_ID   = 'studio-9101802118-8c9a8'
REF_BUCKET   = 'numista-reference-library'
UPL_BUCKET   = 'numista-uploads-studio-9101802118-8c9a8'
LOG_FILE     = os.path.join(SCRIPT_DIR, 'local_image_upload_log.json')
USERS        = ['eric@numista.ai', 'jseaman1204@gmail.com']

# Source directories
BASE_MANUAL  = r'C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images'
ATB_DIR      = os.path.join(BASE_MANUAL, 'America the Beautiful')
NEW_COINS_BASE = r'C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\Coin Images\New Coin Images'
HAWAII_DIR   = os.path.join(NEW_COINS_BASE, 'Hawaii')
OTHER_DIR    = os.path.join(NEW_COINS_BASE, 'Other')
GENERIC_DIR  = NEW_COINS_BASE   # root files
US_MINT_2026 = r'C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\Coin Images\US MINT\2026'

# ─── GCS Destination Paths ────────────────────────────────────────────────────
ATB_GCS_PREFIX       = 'reference_library/atb_quarters/'
JAMUL_GCS_PREFIX     = 'reference_library/novelty/jamul_sovereign_nation/'
GOLD_EAGLE_PREFIX    = 'reference_library/gold_eagles/'
SILVER_EAGLE_PREFIX  = 'reference_library/silver_eagles/'
GENERIC_PREFIX       = 'reference_library/generic_denominations/'
US_MINT_2026_PREFIX  = 'reference_library/us_mint_official/2026/'

PUBLIC_URL_BASE      = 'https://storage.googleapis.com/{bucket}/{path}'

# ─── Init Firebase ────────────────────────────────────────────────────────────
import firebase_admin
from firebase_admin import credentials, firestore, storage as fb_storage

cred = credentials.Certificate(SA_KEY)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'storageBucket': UPL_BUCKET,
        'projectId': PROJECT_ID,
    })

db = firestore.client()

from google.cloud import storage as gcs_storage
gcs_client = gcs_storage.Client.from_service_account_json(SA_KEY)
ref_bucket_obj = gcs_client.bucket(REF_BUCKET)
upl_bucket_obj = gcs_client.bucket(UPL_BUCKET)

# ─── Logging ──────────────────────────────────────────────────────────────────
log = {
    'run_timestamp': datetime.utcnow().isoformat() + 'Z',
    'task1_atb_uploads': [],
    'task2_new_coin_uploads': [],
    'task3_firestore_atb_updates': [],
    'task4_firestore_eagle_updates': [],
    'errors': [],
    'summary': {}
}

def log_error(msg, exc=None):
    entry = {'error': msg}
    if exc:
        entry['exception'] = str(exc)
    log['errors'].append(entry)
    print(f'  [ERROR] {msg}' + (f' — {exc}' if exc else ''))

def save_log():
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print(f'\n[LOG] Saved to {LOG_FILE}')

# ─── Attribution Constants ────────────────────────────────────────────────────
ATTRIB = {
    'usmint': {
        'attribution': 'United States Mint. Public domain (17 U.S.C. § 105). Source: usmint.gov',
        'source': 'usmint_gov',
        'license': 'public_domain_us_government',
        'copyright': 'Public Domain',
    },
    'jamul': {
        'attribution': 'Jamul Indian Village of California, 2018',
        'source': 'novelty_collector_item',
        'license': 'collector_reference',
        'copyright': 'Jamul Indian Village of California',
    },
    'generic': {
        'attribution': 'Generic denomination reference image',
        'source': 'gcs_reference_library',
        'license': 'public_domain',
        'copyright': 'Public Domain',
    },
}


def upload_to_gcs(local_path, gcs_path, bucket_obj, dry_run=False, attrib_key='usmint'):
    """Upload file to GCS with attribution metadata. Returns public URL."""
    public_url = PUBLIC_URL_BASE.format(bucket=bucket_obj.name, path=gcs_path)
    if dry_run:
        print(f'  [DRY-RUN] Would upload: {os.path.basename(local_path)} → gs://{bucket_obj.name}/{gcs_path}')
        return public_url
    try:
        blob = bucket_obj.blob(gcs_path)
        # Determine content type
        ext = Path(local_path).suffix.lower()
        ct_map = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                  '.png': 'image/png', '.webp': 'image/webp'}
        ct = ct_map.get(ext, 'image/jpeg')
        blob.upload_from_filename(local_path, content_type=ct)
        # NOTE: No ACL call needed — bucket uses Uniform Bucket-Level Access (UBLA)
        # Public access is controlled via IAM at the bucket level
        # Set attribution metadata
        meta = ATTRIB.get(attrib_key, ATTRIB['usmint'])
        blob.metadata = {
            'attribution': meta['attribution'],
            'source':      meta['source'],
            'license':     meta['license'],
            'copyright':   meta['copyright'],
        }
        blob.patch()
        print(f'  [GCS] Uploaded: {os.path.basename(local_path)} → {gcs_path}')
        return public_url
    except Exception as e:
        log_error(f'Failed upload {local_path} to {gcs_path}', e)
        return None

# ─── ATB Park Name Extraction ─────────────────────────────────────────────────
def parse_atb_filename(filename):
    """
    Parse ATB filename like:
      2014-america-the-beautiful-quarters-coin-great-smoky-mountains-tennessee-uncirculated-reverse.jpg
      2014-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg
      2014-america-the-beautiful-quarters-coin-proof-obverse-s.jpg
    Returns dict with: year, park_key, side, mint, is_obverse
    """
    stem = Path(filename).stem.lower()
    # Remove common prefix
    stem = re.sub(r'^(\d{4})-america-the-beautiful-quarters-(?:five-ounce-silver-)?(?:uncirculated-)?coin-', '', stem)
    
    year_match = re.match(r'^(\d{4})', Path(filename).stem)
    year = year_match.group(1) if year_match else None

    # Detect obverse files
    if 'obverse' in stem:
        # e.g. uncirculated-obverse-d, proof-obverse-s, uncirculated-obverse-denver
        mint = None
        for m in ['philadelphia', 'denver', '-p', '-d', '-s']:
            if stem.endswith(m):
                mint_map = {'philadelphia': 'P', 'denver': 'D', '-p': 'P', '-d': 'D', '-s': 'S'}
                mint = mint_map[m]
                break
        if not mint:
            # last token after final dash
            parts = stem.rsplit('-', 1)
            mint = parts[-1].upper() if len(parts) > 1 else 'P'
        quality = 'proof' if 'proof' in stem else 'uncirculated'
        return {
            'year': year, 'park_key': None, 'side': 'obverse',
            'mint': mint, 'quality': quality, 'is_obverse': True
        }

    # Detect reverse / five-ounce silver
    if 'reverse' in stem:
        # Strip trailing -uncirculated-reverse or -proof-reverse or -five-ounce-silver-...-reverse
        park_part = re.sub(r'-(uncirculated|proof|five-ounce-silver-uncirculated|five-ounce-silver)-?reverse.*$', '', stem)
        # Remove trailing state name (last hyphenated word that looks like a state)
        # e.g. great-smoky-mountains-tennessee → great-smoky-mountains
        parts = park_part.split('-')
        # Last part is usually state abbreviation word
        park_key = '-'.join(parts)  # keep full for matching
        quality = 'proof' if 'proof' in Path(filename).stem.lower() else 'uncirculated'
        return {
            'year': year, 'park_key': park_key, 'side': 'reverse',
            'mint': None, 'quality': quality, 'is_obverse': False
        }

    return {'year': year, 'park_key': stem, 'side': 'unknown',
            'mint': None, 'quality': 'uncirculated', 'is_obverse': False}


def make_park_search_key(park_key_raw):
    """Convert park_key like 'great-smoky-mountains-tennessee' to
    a set of search terms for matching Firestore Theme/Subject fields."""
    if not park_key_raw:
        return set()
    cleaned = park_key_raw.replace('-', ' ').lower()
    words = cleaned.split()
    # Remove trailing US state names / territories
    us_states = {
        'alabama','alaska','arizona','arkansas','california','colorado','connecticut',
        'delaware','florida','georgia','hawaii','idaho','illinois','indiana','iowa',
        'kansas','kentucky','louisiana','maine','maryland','massachusetts','michigan',
        'minnesota','mississippi','missouri','montana','nebraska','nevada',
        'new hampshire','new jersey','new mexico','new york','north carolina',
        'north dakota','ohio','oklahoma','oregon','pennsylvania','rhode island',
        'south carolina','south dakota','tennessee','texas','utah','vermont',
        'virginia','washington','west virginia','wisconsin','wyoming',
        # territories
        'puerto rico','guam','virgin islands','american samoa',
        'northern mariana islands','district of columbia','iowa',
    }
    # Build two versions: with and without trailing state word
    full = ' '.join(words)
    # Remove last word if it's a state
    if words and words[-1] in us_states:
        without_state = ' '.join(words[:-1])
    elif len(words) >= 2 and ' '.join(words[-2:]) in us_states:
        without_state = ' '.join(words[:-2])
    else:
        without_state = full
    return {full, without_state, cleaned}


# ─── TASK 1: Upload ATB Quarter Images ────────────────────────────────────────
def task1_upload_atb(dry_run=False):
    print('\n' + '='*60)
    print('TASK 1: Uploading ATB Quarter Images')
    print('='*60)

    if not os.path.isdir(ATB_DIR):
        log_error(f'ATB source directory not found: {ATB_DIR}')
        return {}

    files = sorted(os.listdir(ATB_DIR))
    print(f'  Found {len(files)} files in ATB directory')

    # Build GCS lookup map: park_slug → {obverse: url, reverse: url}
    atb_gcs_map = {}  # park_slug (year-park) → {obverse_url, reverse_url, year}

    for filename in files:
        local_path = os.path.join(ATB_DIR, filename)
        if not os.path.isfile(local_path):
            continue

        ext = Path(filename).suffix.lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
            continue

        # Skip duplicate (1) files
        if '(1)' in filename:
            print(f'  [SKIP] Duplicate file: {filename}')
            continue

        gcs_path = ATB_GCS_PREFIX + filename
        parsed = parse_atb_filename(filename)
        year = parsed.get('year', 'unknown')

        url = upload_to_gcs(local_path, gcs_path, ref_bucket_obj, dry_run=dry_run)
        if url:
            entry = {
                'filename': filename,
                'gcs_path': gcs_path,
                'url': url,
                'year': year,
                'side': parsed['side'],
                'park_key': parsed.get('park_key'),
                'mint': parsed.get('mint'),
                'quality': parsed.get('quality'),
            }
            log['task1_atb_uploads'].append(entry)

            # Build lookup map
            if parsed['side'] == 'reverse' and parsed.get('park_key'):
                pk = parsed['park_key']
                slot = f"{year}-{pk}"
                if slot not in atb_gcs_map:
                    atb_gcs_map[slot] = {'year': year, 'park_key': pk}
                atb_gcs_map[slot]['reverse_url'] = url
                atb_gcs_map[slot]['reverse_quality'] = parsed['quality']
            elif parsed['side'] == 'obverse':
                mint = parsed.get('mint', 'P')
                quality = parsed.get('quality', 'uncirculated')
                obv_slot = f"{year}-obverse-{mint}-{quality}"
                if obv_slot not in atb_gcs_map:
                    atb_gcs_map[obv_slot] = {'year': year, 'mint': mint}
                atb_gcs_map[obv_slot]['obverse_url'] = url

    print(f'\n  ATB uploads complete: {len(log["task1_atb_uploads"])} files')
    return atb_gcs_map


# ─── TASK 2: Upload New Coin Images ───────────────────────────────────────────
def task2_upload_new_coins(dry_run=False):
    print('\n' + '='*60)
    print('TASK 2: Uploading New Coin Images')
    print('='*60)

    uploaded_map = {}  # filename → url (for Task 4 matching)

    # 2a: Hawaii / Jamul Sovereign Nation (12 images)
    print('\n  [2a] Jamul Sovereign Nation coins (Hawaii dir)...')
    hawaii_dir = HAWAII_DIR
    if os.path.isdir(hawaii_dir):
        for fname in sorted(os.listdir(hawaii_dir)):
            fpath = os.path.join(hawaii_dir, fname)
            if not os.path.isfile(fpath):
                continue
            ext = Path(fname).suffix.lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                continue
            gcs_name = fname.lower().replace(' ', '_')
            gcs_path = JAMUL_GCS_PREFIX + gcs_name
            url = upload_to_gcs(fpath, gcs_path, ref_bucket_obj, dry_run=dry_run, attrib_key='jamul')
            if url:
                entry = {'filename': fname, 'gcs_path': gcs_path, 'url': url,
                         'category': 'jamul_sovereign_nation'}
                log['task2_new_coin_uploads'].append(entry)
                uploaded_map[fname] = url
    else:
        log_error(f'Hawaii dir not found: {hawaii_dir}')

    # 2b: Other special coins
    print('\n  [2b] Other special coins (Gold Eagle, Silver Eagles, Army Eagle)...')
    other_map = {
        '1989W Gold American Eagle $50 Reverse.jpg':
            (GOLD_EAGLE_PREFIX + '1989w_gold_eagle_50_reverse.jpg', 'gold_eagle'),
        'American Eagle 2023 One Ounce Silver Proof Coin Obverse.jpg':
            (SILVER_EAGLE_PREFIX + '2023_silver_eagle_proof_obverse.jpg', 'silver_eagle_2023'),
        'American Eagle 2023 One Ounce Silver Proof Coin Reverse.jpg':
            (SILVER_EAGLE_PREFIX + '2023_silver_eagle_proof_reverse.jpg', 'silver_eagle_2023'),
        'US Army Silver Eagle $1 Obverse.jpg':
            (SILVER_EAGLE_PREFIX + 'us_army_silver_eagle_obverse.jpg', 'us_army_silver_eagle'),
    }
    if os.path.isdir(OTHER_DIR):
        for fname, (gcs_path, category) in other_map.items():
            fpath = os.path.join(OTHER_DIR, fname)
            if not os.path.isfile(fpath):
                log_error(f'Other file not found: {fpath}')
                continue
            url = upload_to_gcs(fpath, gcs_path, ref_bucket_obj, dry_run=dry_run)
            if url:
                entry = {'filename': fname, 'gcs_path': gcs_path, 'url': url,
                         'category': category}
                log['task2_new_coin_uploads'].append(entry)
                uploaded_map[fname] = url
    else:
        log_error(f'Other dir not found: {OTHER_DIR}')

    # 2c: Generic denomination images (root of New Coin Images)
    print('\n  [2c] Generic denomination images...')
    if os.path.isdir(GENERIC_DIR):
        for fname in sorted(os.listdir(GENERIC_DIR)):
            fpath = os.path.join(GENERIC_DIR, fname)
            if not os.path.isfile(fpath):
                continue
            ext = Path(fname).suffix.lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                continue
            # Only upload root-level generic images (not subdir images)
            gcs_name = fname.lower().replace(' ', '_').replace(',', '').replace('-_copy', '')
            gcs_path = GENERIC_PREFIX + gcs_name
            url = upload_to_gcs(fpath, gcs_path, ref_bucket_obj, dry_run=dry_run, attrib_key='generic')
            if url:
                entry = {'filename': fname, 'gcs_path': gcs_path, 'url': url,
                         'category': 'generic_denomination'}
                log['task2_new_coin_uploads'].append(entry)
                uploaded_map[fname] = url
    else:
        log_error(f'Generic dir not found: {GENERIC_DIR}')

    # 2d: US MINT/2026 coins
    print('\n  [2d] US Mint 2026 coins...')
    if os.path.isdir(US_MINT_2026):
        for fname in sorted(os.listdir(US_MINT_2026)):
            fpath = os.path.join(US_MINT_2026, fname)
            if not os.path.isfile(fpath):
                continue
            ext = Path(fname).suffix.lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                continue
            gcs_name = fname.lower().replace(' ', '_')
            gcs_path = US_MINT_2026_PREFIX + gcs_name
            url = upload_to_gcs(fpath, gcs_path, ref_bucket_obj, dry_run=dry_run)
            if url:
                entry = {'filename': fname, 'gcs_path': gcs_path, 'url': url,
                         'category': 'us_mint_2026'}
                log['task2_new_coin_uploads'].append(entry)
                uploaded_map[fname] = url
    else:
        log_error(f'US Mint 2026 dir not found: {US_MINT_2026}')

    print(f'\n  Task 2 uploads complete: {len(log["task2_new_coin_uploads"])} files')
    return uploaded_map


# ─── Firestore Query Helpers ──────────────────────────────────────────────────
def get_all_coins_for_user(email):
    """Fetch all coins from a user's collection."""
    coins = []
    try:
        docs = db.collection('users').document(email).collection('coins').stream()
        for doc in docs:
            d = doc.to_dict()
            d['_doc_id'] = doc.id
            d['_user'] = email
            coins.append(d)
    except Exception as e:
        log_error(f'Error fetching coins for {email}', e)
    return coins


def is_wikimedia_url(url):
    if not url:
        return False
    url = url.lower()
    return 'wikimedia' in url or 'wikipedia' in url or 'upload.wiki' in url


def is_our_gcs_url(url):
    if not url:
        return False
    return 'storage.googleapis.com' in url and (REF_BUCKET in url or UPL_BUCKET in url)


def is_empty_url(url):
    return not url or url.strip() == ''


# ─── Copy image to user-specific path ────────────────────────────────────────
def copy_ref_to_user_path(ref_gcs_path, user_email, doc_id, side, dry_run=False):
    """Copy reference image to users/{email}/coins/{doc_id}/{side}.jpg path."""
    user_path = f"users/{user_email}/coins/{doc_id}/{side}.jpg"
    public_url = PUBLIC_URL_BASE.format(bucket=UPL_BUCKET, path=user_path)
    if dry_run:
        print(f'    [DRY-RUN] Would copy ref image to user path: {user_path}')
        return public_url
    try:
        ref_blob = ref_bucket_obj.blob(ref_gcs_path)
        upl_blob = upl_bucket_obj.blob(user_path)
        # Copy using rewrite
        src_uri = f"gs://{REF_BUCKET}/{ref_gcs_path}"
        # Download and re-upload (cross-bucket copy)
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            tmp_path = tmp.name
        ref_blob.download_to_filename(tmp_path)
        upl_blob.upload_from_filename(tmp_path, content_type='image/jpeg')
        # NOTE: No ACL call needed — bucket uses Uniform Bucket-Level Access
        os.unlink(tmp_path)
        print(f'    [GCS] Copied to user path: {user_path}')
        return public_url
    except Exception as e:
        log_error(f'Failed to copy ref image to user path {user_path}', e)
        return PUBLIC_URL_BASE.format(bucket=REF_BUCKET, path=ref_gcs_path)


def update_firestore_coin(email, doc_id, updates, dry_run=False):
    """Update a coin document in Firestore."""
    if dry_run:
        print(f'    [DRY-RUN] Would update Firestore: users/{email}/coins/{doc_id}')
        # Strip non-serializable sentinel values for logging
        safe_updates = {k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v
                        for k, v in updates.items()}
        print(f'             Updates: {json.dumps(safe_updates, indent=6)}')
        return True
    try:
        db.collection('users').document(email).collection('coins').document(doc_id).update(updates)
        print(f'    [FS] Updated users/{email}/coins/{doc_id}')
        return True
    except Exception as e:
        log_error(f'Failed Firestore update for {email}/{doc_id}', e)
        return False


# ─── ATB Park Name Matching ────────────────────────────────────────────────────
def build_atb_park_lookup(atb_gcs_map):
    """
    Build a lookup: normalized_park_keywords → {year, reverse_url, obverse_urls by year}
    Returns: park_reverse_lookup, year_obverse_lookup
    """
    park_reverse_lookup = {}  # park_key_slug → {year, reverse_url, reverse_quality}
    year_obverse_lookup = {}  # year → {P: url, D: url, S: url}

    for slot, data in atb_gcs_map.items():
        if 'reverse_url' in data:
            park_key = data.get('park_key', '')
            year = data.get('year', '')
            search_keys = make_park_search_key(park_key)
            for sk in search_keys:
                park_reverse_lookup[sk] = {
                    'year': year,
                    'reverse_url': data['reverse_url'],
                    'reverse_quality': data.get('reverse_quality', 'uncirculated'),
                    'park_key_raw': park_key,
                    'gcs_path': ATB_GCS_PREFIX + slot.split('-', 1)[1] + '-uncirculated-reverse.jpg'  # approx
                }
        if 'obverse_url' in data:
            year = data.get('year', '')
            mint = data.get('mint', 'P')
            if year not in year_obverse_lookup:
                year_obverse_lookup[year] = {}
            year_obverse_lookup[year][mint] = data['obverse_url']

    return park_reverse_lookup, year_obverse_lookup


def match_atb_coin(coin_data, park_reverse_lookup, year_obverse_lookup):
    """
    Try to match a Firestore ATB coin to GCS images.
    Returns: (reverse_url, obverse_url) or (None, None)
    """
    # Extract year
    year = str(coin_data.get('Year', coin_data.get('year', ''))).strip()
    # Strip non-numeric
    year_match = re.search(r'(20\d{2})', year)
    year = year_match.group(1) if year_match else ''

    # Extract theme/subject for park matching
    theme = (coin_data.get('Theme/Subject', '') or
             coin_data.get('Theme', '') or
             coin_data.get('Subject', '') or
             coin_data.get('Name', '') or '').strip().lower()

    program = (coin_data.get('Program/Series', '') or
               coin_data.get('Program', '') or
               coin_data.get('Series', '') or '').strip().lower()

    search_text = (theme + ' ' + program).strip()
    if not search_text:
        return None, None

    # Try direct park_key matching
    matched_reverse = None
    matched_reverse_path = None
    best_score = 0

    for park_slug, rv_data in park_reverse_lookup.items():
        if year and rv_data.get('year') != year:
            continue  # strict year match when year is known
        # Check if park_slug words appear in search_text
        park_words = set(park_slug.split())
        search_words = set(search_text.split())
        common = park_words & search_words
        if len(common) >= max(1, len(park_words) // 2):
            score = len(common) / max(len(park_words), 1)
            if score > best_score:
                best_score = score
                matched_reverse = rv_data['reverse_url']
                # Build approximate GCS path for cross-bucket copy
                matched_reverse_path = ATB_GCS_PREFIX + rv_data.get('park_key_raw', park_slug) + '-uncirculated-reverse.jpg'

    if best_score < 0.4:
        matched_reverse = None

    # Get obverse by year
    matched_obverse = None
    if year and year in year_obverse_lookup:
        # Prefer P mint, then D
        yr_obvs = year_obverse_lookup[year]
        matched_obverse = yr_obvs.get('P') or yr_obvs.get('D') or next(iter(yr_obvs.values()), None)

    return matched_reverse, matched_obverse


# ─── TASK 3: Update Firestore ATB Coins ───────────────────────────────────────
def task3_update_atb_firestore(atb_gcs_map, dry_run=False):
    print('\n' + '='*60)
    print('TASK 3: Updating Firestore ATB Coins')
    print('='*60)

    park_reverse_lookup, year_obverse_lookup = build_atb_park_lookup(atb_gcs_map)
    print(f'  Built ATB lookup: {len(park_reverse_lookup)} park reverse entries, '
          f'{len(year_obverse_lookup)} years of obverse images')

    # Also build a direct filename lookup from upload log
    # slot: year-park_key → {reverse_url, gcs_path}
    atb_reverse_by_filename = {}
    for entry in log['task1_atb_uploads']:
        if entry['side'] == 'reverse' and entry.get('park_key'):
            atb_reverse_by_filename[entry['filename']] = entry

    atb_programs = [
        'america the beautiful', 'atb', 'national park',
        'america the beautiful quarters', 'national monument',
        'national military park', 'national historic', 'national recreation',
        'national forest', 'national wildlife',
    ]

    for email in USERS:
        print(f'\n  Processing account: {email}')
        coins = get_all_coins_for_user(email)
        print(f'    Fetched {len(coins)} total coins')

        atb_coins = []
        for c in coins:
            prog = (c.get('Program/Series', '') or c.get('Program', '') or '').lower()
            theme = (c.get('Theme/Subject', '') or c.get('Theme', '') or '').lower()
            combined = prog + ' ' + theme
            # Also check Program field alone (eric's account may use 'Program' not 'Program/Series')
            prog_only = (c.get('Program', '') or '').lower()
            series_only = (c.get('Series', '') or '').lower()
            full_check = combined + ' ' + prog_only + ' ' + series_only
            if any(kw in full_check for kw in atb_programs):
                atb_coins.append(c)

        print(f'    Found {len(atb_coins)} ATB coins')

        for coin in atb_coins:
            doc_id = coin['_doc_id']
            curr_obv = coin.get('image_url_obverse', '') or ''
            curr_rev = coin.get('image_url_reverse', '') or ''

            # Determine which images need updating
            need_obverse = is_empty_url(curr_obv) or is_wikimedia_url(curr_obv)
            need_reverse = is_empty_url(curr_rev) or is_wikimedia_url(curr_rev)

            if not need_obverse and is_our_gcs_url(curr_obv):
                if not need_reverse and is_our_gcs_url(curr_rev):
                    print(f'    [SKIP] {doc_id} — already has GCS images')
                    continue

            if not need_obverse and not need_reverse:
                print(f'    [SKIP] {doc_id} — images already set (not Wikimedia)')
                continue

            # Try to find matching GCS images
            new_rev_url, new_obv_url = match_atb_coin(coin, park_reverse_lookup, year_obverse_lookup)

            updates = {}
            log_entry = {
                'doc_id': doc_id,
                'email': email,
                'theme': coin.get('Theme/Subject', coin.get('Theme', '')),
                'year': coin.get('Year', ''),
                'old_obverse': curr_obv,
                'old_reverse': curr_rev,
            }

            if need_obverse and new_obv_url:
                # Find the actual uploaded GCS path for this year's obverse from upload log
                year = str(coin.get('Year', '')).strip()
                yr_m = re.search(r'(20\d{2})', year)
                yr = yr_m.group(1) if yr_m else 'unknown'
                # Try P/Philadelphia mint first, then any
                obv_gcs_path = None
                for up_entry in log['task1_atb_uploads']:
                    if (up_entry.get('side') == 'obverse' and
                            up_entry.get('year') == yr and
                            up_entry.get('mint') in ('P',) and
                            'proof' not in up_entry.get('filename', '').lower()):
                        obv_gcs_path = up_entry['gcs_path']
                        break
                if not obv_gcs_path:
                    for up_entry in log['task1_atb_uploads']:
                        if (up_entry.get('side') == 'obverse' and up_entry.get('year') == yr
                                and 'proof' not in up_entry.get('filename', '').lower()):
                            obv_gcs_path = up_entry['gcs_path']
                            break
                if obv_gcs_path:
                    user_url = copy_ref_to_user_path(obv_gcs_path, email, doc_id, 'obverse', dry_run=dry_run)
                    updates['image_url_obverse'] = user_url or new_obv_url
                else:
                    updates['image_url_obverse'] = new_obv_url  # fallback to direct reference URL
                updates['image_source'] = 'gcs_usmint_official'
                updates['image_source_obverse'] = 'usmint_gov'
                updates['image_attribution'] = ATTRIB['usmint']['attribution']
                updates['image_license'] = ATTRIB['usmint']['license']
                log_entry['new_obverse'] = updates['image_url_obverse']
                if is_wikimedia_url(curr_obv):
                    log_entry['action_obverse'] = 'replaced_wikimedia'
                else:
                    log_entry['action_obverse'] = 'filled_empty'

            if need_reverse and new_rev_url:
                # Find GCS path for this reverse
                rev_path = None
                for entry in log['task1_atb_uploads']:
                    if entry['side'] == 'reverse' and entry.get('url') == new_rev_url:
                        rev_path = entry['gcs_path']
                        break
                if rev_path:
                    user_url = copy_ref_to_user_path(rev_path, email, doc_id, 'reverse', dry_run=dry_run)
                    updates['image_url_reverse'] = user_url or new_rev_url
                else:
                    updates['image_url_reverse'] = new_rev_url
                updates['image_source'] = 'gcs_usmint_official'
                updates['image_source_reverse'] = 'usmint_gov'
                if 'image_attribution' not in updates:
                    updates['image_attribution'] = ATTRIB['usmint']['attribution']
                if 'image_license' not in updates:
                    updates['image_license'] = ATTRIB['usmint']['license']
                log_entry['new_reverse'] = updates.get('image_url_reverse')
                if is_wikimedia_url(curr_rev):
                    log_entry['action_reverse'] = 'replaced_wikimedia'
                else:
                    log_entry['action_reverse'] = 'filled_empty'
            elif need_reverse and not new_rev_url:
                log_entry['action_reverse'] = 'no_match_found'

            if updates:
                updates['updated_at'] = firestore.SERVER_TIMESTAMP
                success = update_firestore_coin(email, doc_id, updates, dry_run=dry_run)
                log_entry['status'] = 'updated' if success else 'failed'
                log['task3_firestore_atb_updates'].append(log_entry)
            else:
                log_entry['status'] = 'no_update_needed'
                log['task3_firestore_atb_updates'].append(log_entry)

    wiki_replaced = sum(1 for e in log['task3_firestore_atb_updates']
                        if e.get('action_obverse') == 'replaced_wikimedia'
                        or e.get('action_reverse') == 'replaced_wikimedia')
    empty_filled = sum(1 for e in log['task3_firestore_atb_updates']
                       if e.get('action_obverse') == 'filled_empty'
                       or e.get('action_reverse') == 'filled_empty')
    print(f'\n  Task 3 complete: {len(log["task3_firestore_atb_updates"])} ATB coins processed')
    print(f'    Wikimedia URLs replaced: {wiki_replaced}')
    print(f'    Empty URLs filled: {empty_filled}')


# ─── TASK 4: Update Eagle Coins in Firestore ──────────────────────────────────
def task4_update_eagle_firestore(new_coin_urls, dry_run=False):
    print('\n' + '='*60)
    print('TASK 4: Updating Eagle Coins in Firestore')
    print('='*60)

    # Build URL map from task2 uploads
    ase_2023_obv_url = None
    ase_2023_rev_url = None
    gold_eagle_1989_rev_url = None

    for entry in log['task2_new_coin_uploads']:
        cat = entry.get('category', '')
        gcs_path = entry.get('gcs_path', '')
        url = entry.get('url', '')
        if cat == 'silver_eagle_2023':
            if 'obverse' in gcs_path:
                ase_2023_obv_url = url
            elif 'reverse' in gcs_path:
                ase_2023_rev_url = url
        elif cat == 'gold_eagle':
            gold_eagle_1989_rev_url = url

    print(f'  ASE 2023 Obverse URL: {ase_2023_obv_url}')
    print(f'  ASE 2023 Reverse URL: {ase_2023_rev_url}')
    print(f'  Gold Eagle 1989W Rev URL: {gold_eagle_1989_rev_url}')

    silver_eagle_keywords = ['silver eagle', 'american eagle silver', 'american silver eagle',
                              'silver bullion', 'ase']
    gold_eagle_keywords = ['gold eagle', 'american eagle gold', 'american gold eagle',
                           'gold bullion', 'age']

    for email in USERS:
        print(f'\n  Processing account: {email}')
        coins = get_all_coins_for_user(email)

        for coin in coins:
            doc_id = coin['_doc_id']
            name = (coin.get('Name', '') or '').lower()
            prog = (coin.get('Program/Series', '') or coin.get('Program', '') or '').lower()
            year = str(coin.get('Year', '') or '').strip()
            combined = name + ' ' + prog

            curr_obv = coin.get('image_url_obverse', '') or ''
            curr_rev = coin.get('image_url_reverse', '') or ''

            # Silver Eagle 2023 check
            if ase_2023_obv_url or ase_2023_rev_url:
                is_ase = any(kw in combined for kw in silver_eagle_keywords)
                yr_match = re.search(r'(20\d{2})', year)
                coin_year = yr_match.group(1) if yr_match else ''
                is_2023 = (coin_year == '2023')
                if is_ase and is_2023:
                    updates = {}
                    log_entry = {
                        'doc_id': doc_id, 'email': email,
                        'type': 'silver_eagle_2023',
                        'year': year,
                        'old_obverse': curr_obv, 'old_reverse': curr_rev
                    }
                    if (is_empty_url(curr_obv) or is_wikimedia_url(curr_obv)) and ase_2023_obv_url:
                        updates['image_url_obverse'] = ase_2023_obv_url
                        log_entry['new_obverse'] = ase_2023_obv_url
                        log_entry['action_obverse'] = 'replaced_wikimedia' if is_wikimedia_url(curr_obv) else 'filled_empty'
                    if (is_empty_url(curr_rev) or is_wikimedia_url(curr_rev)) and ase_2023_rev_url:
                        updates['image_url_reverse'] = ase_2023_rev_url
                        log_entry['new_reverse'] = ase_2023_rev_url
                        log_entry['action_reverse'] = 'replaced_wikimedia' if is_wikimedia_url(curr_rev) else 'filled_empty'
                    if updates:
                        updates['image_source'] = 'gcs_usmint_official'
                        updates['image_source_obverse'] = 'usmint_gov'
                        updates['image_source_reverse'] = 'usmint_gov'
                        updates['image_attribution'] = ATTRIB['usmint']['attribution']
                        updates['image_license'] = ATTRIB['usmint']['license']
                        updates['updated_at'] = firestore.SERVER_TIMESTAMP
                        success = update_firestore_coin(email, doc_id, updates, dry_run=dry_run)
                        log_entry['status'] = 'updated' if success else 'failed'
                        log['task4_firestore_eagle_updates'].append(log_entry)

            # Gold Eagle 1989W check
            if gold_eagle_1989_rev_url:
                is_gold_eagle = any(kw in combined for kw in gold_eagle_keywords)
                yr_match = re.search(r'(1989)', year)
                coin_year = yr_match.group(1) if yr_match else ''
                mint_mark = (coin.get('Mint Mark', '') or coin.get('MintMark', '') or '').upper()
                is_1989w = (coin_year == '1989') and ('W' in mint_mark or 'W' in name or 'w' in prog)
                if is_gold_eagle and (is_1989w or coin_year == '1989'):
                    if is_empty_url(curr_rev) or is_wikimedia_url(curr_rev):
                        updates = {
                            'image_url_reverse': gold_eagle_1989_rev_url,
                            'image_source': 'gcs_usmint_official',
                            'image_source_reverse': 'usmint_gov',
                            'image_attribution': ATTRIB['usmint']['attribution'],
                            'image_license': ATTRIB['usmint']['license'],
                            'updated_at': firestore.SERVER_TIMESTAMP
                        }
                        log_entry = {
                            'doc_id': doc_id, 'email': email,
                            'type': 'gold_eagle_1989w',
                            'year': year,
                            'old_reverse': curr_rev,
                            'new_reverse': gold_eagle_1989_rev_url,
                            'action_reverse': 'replaced_wikimedia' if is_wikimedia_url(curr_rev) else 'filled_empty'
                        }
                        success = update_firestore_coin(email, doc_id, updates, dry_run=dry_run)
                        log_entry['status'] = 'updated' if success else 'failed'
                        log['task4_firestore_eagle_updates'].append(log_entry)

    print(f'\n  Task 4 complete: {len(log["task4_firestore_eagle_updates"])} eagle coins updated')


# ─── Report ───────────────────────────────────────────────────────────────────
def build_report(atb_gcs_map):
    total_atb_uploads = len(log['task1_atb_uploads'])
    total_new_uploads = len(log['task2_new_coin_uploads'])
    total_uploads = total_atb_uploads + total_new_uploads

    # ATB reverse images (unique parks)
    atb_reverses = [e for e in log['task1_atb_uploads'] if e['side'] == 'reverse']
    atb_obverses = [e for e in log['task1_atb_uploads'] if e['side'] == 'obverse']

    # Task 3 stats
    t3_updated = [e for e in log['task3_firestore_atb_updates'] if e.get('status') == 'updated']
    t3_wiki_replaced = sum(1 for e in log['task3_firestore_atb_updates']
                           if e.get('action_obverse') == 'replaced_wikimedia'
                           or e.get('action_reverse') == 'replaced_wikimedia')
    t3_empty_filled = sum(1 for e in log['task3_firestore_atb_updates']
                          if e.get('action_obverse') == 'filled_empty'
                          or e.get('action_reverse') == 'filled_empty')

    # Task 4 stats
    t4_updated = [e for e in log['task4_firestore_eagle_updates'] if e.get('status') == 'updated']
    t4_wiki_replaced = sum(1 for e in log['task4_firestore_eagle_updates']
                           if e.get('action_obverse') == 'replaced_wikimedia'
                           or e.get('action_reverse') == 'replaced_wikimedia')
    t4_empty_filled = sum(1 for e in log['task4_firestore_eagle_updates']
                          if e.get('action_obverse') == 'filled_empty'
                          or e.get('action_reverse') == 'filled_empty')

    # ATB designs found vs expected
    atb_park_names = set()
    for e in atb_reverses:
        if e.get('park_key'):
            atb_park_names.add(e['park_key'])

    report = {
        'total_atb_images_uploaded': total_atb_uploads,
        'atb_reverse_images': len(atb_reverses),
        'atb_obverse_images': len(atb_obverses),
        'atb_unique_designs_found': len(atb_park_names),
        'atb_total_designs_expected': 56,
        'total_new_coin_images_uploaded': total_new_uploads,
        'total_images_uploaded_to_gcs': total_uploads,
        'firestore_atb_coins_processed': len(log['task3_firestore_atb_updates']),
        'firestore_atb_coins_updated': len(t3_updated),
        'firestore_wikimedia_urls_replaced_atb': t3_wiki_replaced,
        'firestore_empty_urls_filled_atb': t3_empty_filled,
        'firestore_eagle_coins_updated': len(t4_updated),
        'firestore_wikimedia_urls_replaced_eagles': t4_wiki_replaced,
        'firestore_empty_urls_filled_eagles': t4_empty_filled,
        'total_errors': len(log['errors']),
        'atb_designs_found': sorted(list(atb_park_names)),
    }

    log['summary'] = report

    print('\n' + '='*60)
    print('FINAL REPORT')
    print('='*60)
    print(f'  ATB images uploaded:           {total_atb_uploads} ({len(atb_reverses)} reverses, {len(atb_obverses)} obverses)')
    print(f'  ATB unique designs found:      {len(atb_park_names)} / 56 expected')
    print(f'  Other new coin images:         {total_new_uploads}')
    print(f'  TOTAL images uploaded to GCS:  {total_uploads}')
    print(f'  Firestore ATB coins updated:   {len(t3_updated)} ({t3_wiki_replaced} wiki→GCS, {t3_empty_filled} empty filled)')
    print(f'  Firestore Eagle coins updated: {len(t4_updated)} ({t4_wiki_replaced} wiki→GCS, {t4_empty_filled} empty filled)')
    print(f'  Errors: {len(log["errors"])}')
    if len(atb_park_names) < 56:
        missing = 56 - len(atb_park_names)
        print(f'\n  NOTE: {missing} of 56 ATB designs not found in local image set.')
        print(f'  (This is expected for the 2011 Gettysburg and some others)')

    return report


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Process local coin images and upload to GCS')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would happen without making changes')
    args = parser.parse_args()

    if args.dry_run:
        print('[DRY-RUN MODE] No actual changes will be made.\n')

    print('Starting process_local_coin_images.py')
    print(f'Timestamp: {datetime.utcnow().isoformat()}Z')
    print(f'Dry run: {args.dry_run}')

    # Task 1: Upload ATB images
    atb_gcs_map = task1_upload_atb(dry_run=args.dry_run)

    # Task 2: Upload new coin images
    new_coin_urls = task2_upload_new_coins(dry_run=args.dry_run)

    # Task 3: Update Firestore ATB coins
    task3_update_atb_firestore(atb_gcs_map, dry_run=args.dry_run)

    # Task 4: Update Firestore Eagle coins
    task4_update_eagle_firestore(new_coin_urls, dry_run=args.dry_run)

    # Build and print report
    build_report(atb_gcs_map)

    # Save log
    save_log()
    print('\nDone.')


if __name__ == '__main__':
    main()
