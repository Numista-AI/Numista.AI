#!/usr/bin/env python3
"""
misc_coins_image_sourcing.py
============================
Sources obverse AND reverse images for three groups of zero-image coins
in jseaman1204@gmail.com's Firestore collection:

  GROUP 1: Washington Crossing the Delaware Quarters (2021, P/D/S/W)
  GROUP 2: Lincoln Steel Cents 1943 (P/D/S)
  GROUP 3: Indian Head Cents 1899-1909 (5 coins) + 1909 Lincoln Cents

Strategy:
  - Each group shares the same design — download image ONCE, upload per doc_id
  - Images sourced from Wikimedia Commons API
  - Uploaded to GCS: users/{user}/coins/{doc_id}/obverse.jpg and /reverse.jpg
  - Firestore updated with URLs and source metadata

Usage:
    python misc_coins_image_sourcing.py [--dry-run]
"""

import io
import json
import os
import sys
import time
import argparse
import urllib.parse
import urllib.request
import tempfile

# Fix stdout encoding for Windows
sys.stdout = io.TextIOWrapper(
    sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True
)

import requests as _req

# ─── Config ───────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SA_KEY     = os.path.join(SCRIPT_DIR, 'serviceAccountKey.json.json')
USER       = 'jseaman1204@gmail.com'
BUCKET     = 'numista-uploads-studio-9101802118-8c9a8'
UA         = 'NumistaAI/1.0 (eric@numista.ai)'
LOG_FILE   = os.path.join(SCRIPT_DIR, 'misc_coins_sourcing_log.json')

WIKIMEDIA_API = 'https://commons.wikimedia.org/w/api.php'

# ─── Target Coin Groups ────────────────────────────────────────────────────────

# GROUP 1: Washington Crossing the Delaware Quarters (2021)
# Same obverse (Washington portrait) + same reverse (crossing scene) for all mints
CROSSING_DELAWARE_COINS = [
    {'doc_id': 'fd14d0d4-245b-4cbd-b106-7ef55afe7673', 'label': '2021-D Washington Crossing Delaware Quarter'},
    {'doc_id': 'abde55bf-a51a-49be-a344-303d271e3cf1', 'label': '2021-P Washington Crossing Delaware Quarter'},
    {'doc_id': '71f71910-ff08-4582-90f3-7141811e53b4', 'label': '2021-S Silver Washington Crossing Delaware Quarter'},
    {'doc_id': 'c6f6b9b9-696c-4fc0-826a-7c0cd4dc427b', 'label': '2021-S Clad Washington Crossing Delaware Quarter'},
]

# GROUP 2: Lincoln Steel Cents 1943 (P/D/S)
# Same obverse (Lincoln portrait) + same reverse (Wheat Ears) for all mints
STEEL_CENT_COINS = [
    {'doc_id': 'eaabfde2-3cc6-4105-ba20-2504d7cd1245', 'label': '1943-P Lincoln Steel Cent'},
    {'doc_id': 'cffe4e8d-026f-4334-bf00-6db1f6cf49f5', 'label': '1943-D Lincoln Steel Cent'},
    {'doc_id': '416cadeb-1436-4edd-948a-11d94eedfeee', 'label': '1943-S Lincoln Steel Cent'},
]

# GROUP 3: Indian Head Cents (1899, 1900, 1908) + 1909 Lincoln Cents (Wheat reverse)
# Indian Head: same obverse (Indian head) + same reverse (oak wreath) for all years 1864-1909
# 1909 Lincoln Wheat Cents: share Lincoln portrait + Wheat reverse — close enough to use same images
INDIAN_HEAD_COINS = [
    {'doc_id': '491cd15e-25d9-455c-a02e-356055cb4bbf', 'label': '1899 Indian Head Cent',  'type': 'indian_head'},
    {'doc_id': '041191a5-08b7-4e80-b569-0f9f9400fe2d', 'label': '1900 Indian Head Cent',  'type': 'indian_head'},
    {'doc_id': 'bac811e8-5bf2-49b7-a16d-be737d064c4a', 'label': '1908 Indian Head Cent',  'type': 'indian_head'},
    {'doc_id': '79af72ea-e5a1-4770-b862-52c5e7302a43', 'label': '1909 Lincoln Wheat Cent (VF)', 'type': 'lincoln_wheat'},
    {'doc_id': '810c17b4-dea9-44cc-8abc-7b37fc2ce920', 'label': '1909 Lincoln Wheat Cent (XF)', 'type': 'lincoln_wheat'},
]

# ─── Wikimedia Search Candidates ───────────────────────────────────────────────
# Ordered candidate filenames to try; first valid image URL wins

WIKIMEDIA_CANDIDATES = {
    'crossing_delaware_obverse': [
        # Confirmed working Wikimedia filenames for Washington quarter obverse
        'File:2021-P US Quarter Obverse.jpg',           # 2021 quarter — exact year match
        'File:America the Beautiful quarter obverse (Philadeplhia).jpg',  # ATB series obverse
        'File:United States quarter, obverse, 2004.jpg',  # 2004 quarter portrait
        'File:1994-P Washington quarter obverse.jpg',   # classic portrait photo
        'File:50 State and Territories quarter obverse (Philadelphia).jpg',
        'File:1932 Washington quarter obverse.jpg',     # original design — same portrait
    ],
    'crossing_delaware_obverse_search': 'washington quarter obverse coin portrait',
    'crossing_delaware_reverse': [
        # Specific 2021 Crossing of the Delaware ATB quarter reverse
        'File:United States Quarter Reverse 2021.jpg',
        'File:2021 ATB Quarter Crossing of the Delaware.jpg',
        'File:Washington Crossing the Delaware quarter reverse.jpg',
        'File:2021 ATB Quarter Delaware.jpg',
        'File:Crossing of the Delaware quarter.jpg',
        'File:2021 crossing delaware quarter reverse.jpg',
    ],
    'crossing_delaware_reverse_search': 'washington crossing delaware quarter reverse 2021',

    'steel_cent_obverse': [
        'File:Lincoln cent obverse 08.jpg',
        'File:2009 cent obverse.png',
        'File:Lincoln-head cent obverse.jpg',
        'File:Lincoln-cents-obverse.jpg',
        'File:1943 Steel Cent obverse.jpg',
    ],
    'steel_cent_obverse_search': '1943 steel cent lincoln wheat obverse',

    'steel_cent_reverse': [
        'File:Wheat-cent-reverse.jpg',
        'File:Lincoln-Wheat-Cent-Reverse.jpg',
        'File:Lincoln cent wheat reverse.jpg',
        'File:Wheat cents reverse.jpg',
        'File:Lincoln Wheat Cent Reverse.jpg',
    ],
    'steel_cent_reverse_search': 'lincoln wheat cent reverse',

    'indian_head_obverse': [
        'File:Indian-head-cent-obverse.jpg',
        'File:Indian Head Cent obverse.jpg',
        'File:Indianheadcent.jpg',
        'File:Indian head cent obv.jpg',
        'File:Indian-cents-obverse.jpg',
    ],
    'indian_head_obverse_search': 'indian head cent obverse penny',

    'indian_head_reverse': [
        'File:Indian-head-cent-reverse.jpg',
        'File:Indian Head Cent reverse.jpg',
        'File:Indian head cent rev.jpg',
        'File:Indian-cents-reverse.jpg',
    ],
    'indian_head_reverse_search': 'indian head cent reverse penny',

    'lincoln_wheat_obverse': [
        'File:Lincoln cent obverse 08.jpg',
        'File:2009 cent obverse.png',
        'File:Lincoln-head cent obverse.jpg',
    ],
    'lincoln_wheat_obverse_search': 'lincoln cent wheat penny obverse 1909',

    'lincoln_wheat_reverse': [
        'File:Wheat-cent-reverse.jpg',
        'File:Lincoln-Wheat-Cent-Reverse.jpg',
        'File:Lincoln cent wheat reverse.jpg',
    ],
    'lincoln_wheat_reverse_search': 'lincoln wheat cent reverse penny',
}


# ─── Wikimedia Commons API helpers ────────────────────────────────────────────

def wiki_resolve_filename(filename: str) -> str | None:
    """
    Resolve a Wikimedia filename like 'File:Foo.jpg' to its direct image URL.
    Returns None if not found or not an image type.
    """
    params = {
        'action': 'query',
        'titles': filename,
        'prop': 'imageinfo',
        'iiprop': 'url|mediatype',
        'format': 'json',
    }
    try:
        resp = _req.get(WIKIMEDIA_API, params=params,
                        headers={'User-Agent': UA}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        pages = data.get('query', {}).get('pages', {})
        for page in pages.values():
            if page.get('ns') == -1:  # Missing page
                return None
            imageinfo = page.get('imageinfo', [])
            if not imageinfo:
                return None
            info = imageinfo[0]
            url = info.get('url', '')
            mediatype = info.get('mediatype', '')
            # Only accept bitmap images (skip PDFs, SVGs, etc.)
            ext = url.lower().split('?')[0]
            if ext.endswith('.pdf') or mediatype in ('OFFICE', 'PDF'):
                print(f"    ✗ Skipping non-image: {filename} (mediatype={mediatype})")
                return None
            if url:
                return url
    except Exception as e:
        print(f"    ✗ wiki_resolve_filename error for '{filename}': {e}")
    return None


def wiki_search(query: str, limit: int = 10) -> list[dict]:
    """
    Search Wikimedia Commons for files matching query.
    Returns list of {'title': 'File:...', 'url': '...'} for image files.
    """
    params = {
        'action': 'query',
        'list': 'search',
        'srnamespace': '6',
        'srsearch': query,
        'srlimit': str(limit),
        'format': 'json',
    }
    results = []
    try:
        resp = _req.get(WIKIMEDIA_API, params=params,
                        headers={'User-Agent': UA}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        hits = data.get('query', {}).get('search', [])
        for hit in hits:
            title = hit.get('title', '')
            if title.startswith('File:'):
                ext = title.lower()
                if ext.endswith(('.jpg', '.jpeg', '.png', '.gif', '.tif', '.tiff')):
                    results.append(title)
    except Exception as e:
        print(f"    ✗ wiki_search error for '{query}': {e}")
    return results


def find_wikimedia_image(candidate_key: str) -> tuple[str | None, str | None]:
    """
    Try candidate filenames first, then fall back to search.
    Returns (direct_image_url, wikimedia_filename_used) or (None, None).
    """
    candidates = WIKIMEDIA_CANDIDATES.get(candidate_key, [])
    search_key = candidate_key + '_search'
    search_query = WIKIMEDIA_CANDIDATES.get(search_key, '')

    # 1. Try known filenames
    for filename in candidates:
        print(f"    Trying: {filename}")
        url = wiki_resolve_filename(filename)
        if url:
            print(f"    ✓ Found: {url[:80]}...")
            return url, filename
        time.sleep(0.3)

    # 2. Fall back to search
    if search_query:
        print(f"    Searching: '{search_query}'")
        hits = wiki_search(search_query)
        for title in hits:
            print(f"    Trying search result: {title}")
            url = wiki_resolve_filename(title)
            if url:
                print(f"    ✓ Found via search: {url[:80]}...")
                return url, title
            time.sleep(0.3)

    print(f"    ✗ No image found for: {candidate_key}")
    return None, None


# ─── GCS / Firestore helpers ─────────────────────────────────────────────────

def init_gcs_and_firestore():
    """Initialize GCS and Firestore clients using service account key."""
    from google.cloud import storage, firestore
    from google.oauth2 import service_account

    creds = service_account.Credentials.from_service_account_file(SA_KEY)
    gcs = storage.Client(credentials=creds, project=creds.project_id)
    db  = firestore.Client(credentials=creds, project=creds.project_id)
    return gcs, db


def download_image(url: str) -> bytes | None:
    """Download image bytes from a URL."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()
    except Exception as e:
        print(f"    ✗ Download failed: {e}")
        return None


def upload_to_gcs(gcs_client, image_bytes: bytes, gcs_path: str,
                  content_type: str = 'image/jpeg') -> str | None:
    """
    Upload image bytes to GCS. Returns the public URL (constructed, not make_public).
    """
    bucket = gcs_client.bucket(BUCKET)
    blob   = bucket.blob(gcs_path)
    blob.upload_from_string(image_bytes, content_type=content_type)
    # Construct public URL directly (DO NOT call blob.make_public())
    url = f"https://storage.googleapis.com/{BUCKET}/{gcs_path}"
    print(f"    ✓ Uploaded to GCS: {url}")
    return url


def update_firestore(db, doc_id: str,
                     obverse_url: str | None, reverse_url: str | None,
                     obverse_src: str | None, reverse_src: str | None,
                     dry_run: bool = False) -> dict:
    """Write image URLs and source metadata to Firestore."""
    update = {}
    if obverse_url:
        update['image_url_obverse']    = obverse_url
        update['image_source_obverse'] = obverse_src or 'wikimedia_commons'
    if reverse_url:
        update['image_url_reverse']    = reverse_url
        update['image_source_reverse'] = reverse_src or 'wikimedia_commons'

    if not update:
        return {'status': 'skipped', 'reason': 'no urls to write'}

    if dry_run:
        print(f"    [DRY RUN] Would write to Firestore: {update}")
        return {'status': 'dry_run', 'update': update}

    doc_ref = db.collection(f'users/{USER}/coins').document(doc_id)
    doc_ref.update(update)
    print(f"    ✓ Firestore updated: {doc_id}")
    return {'status': 'updated', 'fields': list(update.keys())}


# ─── Image content-type helper ────────────────────────────────────────────────

def content_type_from_url(url: str) -> str:
    url_lower = url.lower().split('?')[0]
    if url_lower.endswith('.png'):
        return 'image/png'
    if url_lower.endswith('.gif'):
        return 'image/gif'
    return 'image/jpeg'


def gcs_ext_from_url(url: str) -> str:
    url_lower = url.lower().split('?')[0]
    if url_lower.endswith('.png'):
        return 'png'
    if url_lower.endswith('.gif'):
        return 'gif'
    return 'jpg'


# ─── Main processing logic ────────────────────────────────────────────────────

def process_group(
    group_name: str,
    coins: list[dict],
    obverse_key: str,
    reverse_key: str,
    gcs: object,
    db: object,
    log: dict,
    dry_run: bool,
):
    """
    Process a group of coins sharing the same design.
    Downloads obverse + reverse ONCE, then uploads to each coin's GCS path.
    """
    print(f"\n{'='*60}")
    print(f"GROUP: {group_name}")
    print(f"Coins: {len(coins)}")
    print(f"{'='*60}")

    log['groups'][group_name] = {
        'coins': [c['label'] for c in coins],
        'obverse_key': obverse_key,
        'reverse_key': reverse_key,
        'image_fetch': {},
        'coin_results': [],
    }

    # ── Step 1: Find images ──────────────────────────────────────────────────
    print(f"\n[1/3] Finding obverse image ({obverse_key})...")
    obv_url, obv_filename = find_wikimedia_image(obverse_key)
    log['groups'][group_name]['image_fetch']['obverse'] = {
        'wiki_filename': obv_filename, 'wiki_url': obv_url,
    }

    print(f"\n[1/3] Finding reverse image ({reverse_key})...")
    rev_url, rev_filename = find_wikimedia_image(reverse_key)
    log['groups'][group_name]['image_fetch']['reverse'] = {
        'wiki_filename': rev_filename, 'wiki_url': rev_url,
    }

    # ── Step 2: Download images ──────────────────────────────────────────────
    obv_bytes = None
    rev_bytes = None

    if obv_url:
        print(f"\n[2/3] Downloading obverse image...")
        obv_bytes = download_image(obv_url)
        log['groups'][group_name]['image_fetch']['obverse']['downloaded'] = obv_bytes is not None
    else:
        print(f"\n[2/3] ✗ No obverse URL — skipping download.")

    if rev_url:
        print(f"[2/3] Downloading reverse image...")
        rev_bytes = download_image(rev_url)
        log['groups'][group_name]['image_fetch']['reverse']['downloaded'] = rev_bytes is not None
    else:
        print(f"[2/3] ✗ No reverse URL — skipping download.")

    # ── Step 3: Upload + update each coin ───────────────────────────────────
    print(f"\n[3/3] Processing {len(coins)} coin doc(s)...")
    for coin in coins:
        doc_id = coin['doc_id']
        label  = coin['label']
        print(f"\n  ── {label} ({doc_id}) ──")

        coin_result = {
            'doc_id': doc_id,
            'label': label,
            'obverse_gcs_url': None,
            'reverse_gcs_url': None,
            'firestore': None,
            'errors': [],
        }

        # Upload obverse
        final_obv_url = None
        if obv_bytes:
            ext = gcs_ext_from_url(obv_url)
            ct  = content_type_from_url(obv_url)
            gcs_path = f"users/{USER}/coins/{doc_id}/obverse.{ext}"
            if not dry_run:
                final_obv_url = upload_to_gcs(gcs, obv_bytes, gcs_path, ct)
            else:
                final_obv_url = f"https://storage.googleapis.com/{BUCKET}/{gcs_path}"
                print(f"    [DRY RUN] Would upload obverse to: {final_obv_url}")
            coin_result['obverse_gcs_url'] = final_obv_url
        else:
            coin_result['errors'].append('obverse image not found or download failed')

        # Upload reverse
        final_rev_url = None
        if rev_bytes:
            ext = gcs_ext_from_url(rev_url)
            ct  = content_type_from_url(rev_url)
            gcs_path = f"users/{USER}/coins/{doc_id}/reverse.{ext}"
            if not dry_run:
                final_rev_url = upload_to_gcs(gcs, rev_bytes, gcs_path, ct)
            else:
                final_rev_url = f"https://storage.googleapis.com/{BUCKET}/{gcs_path}"
                print(f"    [DRY RUN] Would upload reverse to: {final_rev_url}")
            coin_result['reverse_gcs_url'] = final_rev_url
        else:
            coin_result['errors'].append('reverse image not found or download failed')

        # Update Firestore
        fs_result = update_firestore(
            db, doc_id,
            final_obv_url, final_rev_url,
            'wikimedia_commons' if final_obv_url else None,
            'wikimedia_commons' if final_rev_url else None,
            dry_run=dry_run,
        )
        coin_result['firestore'] = fs_result

        log['groups'][group_name]['coin_results'].append(coin_result)
        time.sleep(0.2)

    return log


def process_mixed_group(
    group_name: str,
    coins: list[dict],
    gcs: object,
    db: object,
    log: dict,
    dry_run: bool,
):
    """
    Process Group 3 which has two coin types sharing different image sets:
      - indian_head type: uses indian_head_obverse + indian_head_reverse
      - lincoln_wheat type: uses lincoln_wheat_obverse + lincoln_wheat_reverse
    Downloads each design set ONCE.
    """
    print(f"\n{'='*60}")
    print(f"GROUP: {group_name}")
    print(f"Coins: {len(coins)}")
    print(f"{'='*60}")

    log['groups'][group_name] = {
        'coins': [c['label'] for c in coins],
        'image_fetch': {},
        'coin_results': [],
    }

    # ── Fetch images for each sub-type ──────────────────────────────────────
    image_cache = {}
    design_keys = {
        'indian_head':    ('indian_head_obverse',   'indian_head_reverse'),
        'lincoln_wheat':  ('lincoln_wheat_obverse',  'lincoln_wheat_reverse'),
    }

    for design_type, (obv_key, rev_key) in design_keys.items():
        print(f"\n  Finding images for design: {design_type}")

        print(f"    Obverse ({obv_key}):")
        obv_url, obv_fn = find_wikimedia_image(obv_key)
        print(f"    Reverse ({rev_key}):")
        rev_url, rev_fn = find_wikimedia_image(rev_key)

        obv_bytes = download_image(obv_url) if obv_url else None
        rev_bytes = download_image(rev_url) if rev_url else None

        image_cache[design_type] = {
            'obv_url': obv_url, 'obv_fn': obv_fn, 'obv_bytes': obv_bytes,
            'rev_url': rev_url, 'rev_fn': rev_fn, 'rev_bytes': rev_bytes,
        }
        log['groups'][group_name]['image_fetch'][design_type] = {
            'obverse': {'wiki_filename': obv_fn, 'wiki_url': obv_url},
            'reverse': {'wiki_filename': rev_fn, 'wiki_url': rev_url},
        }

    # ── Upload + update each coin ────────────────────────────────────────────
    print(f"\nProcessing {len(coins)} coin doc(s)...")
    for coin in coins:
        doc_id      = coin['doc_id']
        label       = coin['label']
        design_type = coin.get('type', 'indian_head')
        print(f"\n  ── {label} ({doc_id}) [{design_type}] ──")

        imgs = image_cache[design_type]
        obv_url   = imgs['obv_url']
        rev_url   = imgs['rev_url']
        obv_bytes = imgs['obv_bytes']
        rev_bytes = imgs['rev_bytes']

        coin_result = {
            'doc_id': doc_id, 'label': label, 'design_type': design_type,
            'obverse_gcs_url': None, 'reverse_gcs_url': None,
            'firestore': None, 'errors': [],
        }

        # Upload obverse
        final_obv_url = None
        if obv_bytes:
            ext = gcs_ext_from_url(obv_url)
            ct  = content_type_from_url(obv_url)
            gcs_path = f"users/{USER}/coins/{doc_id}/obverse.{ext}"
            if not dry_run:
                final_obv_url = upload_to_gcs(gcs, obv_bytes, gcs_path, ct)
            else:
                final_obv_url = f"https://storage.googleapis.com/{BUCKET}/{gcs_path}"
                print(f"    [DRY RUN] Would upload obverse: {final_obv_url}")
            coin_result['obverse_gcs_url'] = final_obv_url
        else:
            coin_result['errors'].append('obverse not found or download failed')

        # Upload reverse
        final_rev_url = None
        if rev_bytes:
            ext = gcs_ext_from_url(rev_url)
            ct  = content_type_from_url(rev_url)
            gcs_path = f"users/{USER}/coins/{doc_id}/reverse.{ext}"
            if not dry_run:
                final_rev_url = upload_to_gcs(gcs, rev_bytes, gcs_path, ct)
            else:
                final_rev_url = f"https://storage.googleapis.com/{BUCKET}/{gcs_path}"
                print(f"    [DRY RUN] Would upload reverse: {final_rev_url}")
            coin_result['reverse_gcs_url'] = final_rev_url
        else:
            coin_result['errors'].append('reverse not found or download failed')

        # Firestore
        fs_result = update_firestore(
            db, doc_id,
            final_obv_url, final_rev_url,
            'wikimedia_commons' if final_obv_url else None,
            'wikimedia_commons' if final_rev_url else None,
            dry_run=dry_run,
        )
        coin_result['firestore'] = fs_result
        log['groups'][group_name]['coin_results'].append(coin_result)
        time.sleep(0.2)

    return log


# ─── Summary helper ───────────────────────────────────────────────────────────

def print_summary(log: dict):
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    both_updated   = []
    one_updated    = []
    not_updated    = []

    for group_name, group_data in log.get('groups', {}).items():
        for result in group_data.get('coin_results', []):
            has_obv = bool(result.get('obverse_gcs_url'))
            has_rev = bool(result.get('reverse_gcs_url'))
            label   = result['label']
            if has_obv and has_rev:
                both_updated.append(label)
            elif has_obv or has_rev:
                one_updated.append(label)
            else:
                not_updated.append((label, result.get('errors', [])))

    total_fs = len(both_updated) + len(one_updated)
    print(f"\n✅ Both images updated ({len(both_updated)}):")
    for x in both_updated:
        print(f"   • {x}")

    print(f"\n⚠️  Only one image updated ({len(one_updated)}):")
    for x in one_updated:
        print(f"   • {x}")

    print(f"\n❌ Not updated ({len(not_updated)}):")
    for x, errs in not_updated:
        print(f"   • {x}: {errs}")

    print(f"\n📄 Total Firestore docs written: {total_fs}")
    log['summary'] = {
        'both_images_updated': both_updated,
        'one_image_updated':   one_updated,
        'not_updated':         [{'label': x, 'errors': e} for x, e in not_updated],
        'total_firestore_docs_written': total_fs,
    }


# ─── Entry Point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Source images for misc coin groups.')
    parser.add_argument('--dry-run', action='store_true',
                        help='Simulate all steps without writing to GCS or Firestore.')
    args = parser.parse_args()
    dry_run = args.dry_run

    if dry_run:
        print("*** DRY RUN MODE — no GCS uploads or Firestore writes ***\n")

    log = {
        'script': 'misc_coins_image_sourcing.py',
        'user': USER,
        'dry_run': dry_run,
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'groups': {},
    }

    print("Initializing GCS and Firestore clients...")
    gcs, db = init_gcs_and_firestore()
    print("✓ Clients initialized.\n")

    # ── GROUP 1: Washington Crossing the Delaware ─────────────────────────
    process_group(
        group_name='Washington Crossing the Delaware Quarters (2021)',
        coins=CROSSING_DELAWARE_COINS,
        obverse_key='crossing_delaware_obverse',
        reverse_key='crossing_delaware_reverse',
        gcs=gcs, db=db, log=log, dry_run=dry_run,
    )

    # ── GROUP 2: Lincoln Steel Cents 1943 ────────────────────────────────
    process_group(
        group_name='Lincoln Steel Cents 1943 (P/D/S)',
        coins=STEEL_CENT_COINS,
        obverse_key='steel_cent_obverse',
        reverse_key='steel_cent_reverse',
        gcs=gcs, db=db, log=log, dry_run=dry_run,
    )

    # ── GROUP 3: Indian Head Cents + 1909 Lincoln Wheat Cents ────────────
    process_mixed_group(
        group_name='Indian Head Cents 1899-1909 + Lincoln Wheat 1909',
        coins=INDIAN_HEAD_COINS,
        gcs=gcs, db=db, log=log, dry_run=dry_run,
    )

    # ── Summary ──────────────────────────────────────────────────────────
    print_summary(log)

    # ── Save log ─────────────────────────────────────────────────────────
    log_copy = {k: v for k, v in log.items()}
    # Remove non-serializable bytes from log before saving
    for gname, gdata in log_copy.get('groups', {}).items():
        if 'image_fetch' in gdata:
            for key, val in gdata['image_fetch'].items():
                if isinstance(val, dict):
                    val.pop('bytes', None)

    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log_copy, f, indent=2, default=str)

    print(f"\n📁 Log saved to: {LOG_FILE}")


if __name__ == '__main__':
    main()
