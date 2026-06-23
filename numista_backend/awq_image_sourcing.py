#!/usr/bin/env python3
"""
awq_image_sourcing.py
=====================
Sources BOTH obverse and reverse images for American Women Quarters (AWQ)
in jseaman1204@gmail.com's collection that still have zero images.

Steps:
  1. Query Firestore live to find AWQ coins with missing images
  2. Build image map: check our reference library (GCS) then Wikimedia Commons
  3. Upload images to GCS per-coin paths
  4. Update Firestore with image URLs + source metadata
  5. Save script log as awq_sourcing_log.json

Usage:
    python awq_image_sourcing.py [--dry-run]
"""

import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import argparse

import requests as _req

sys.stdout = io.TextIOWrapper(
    sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True
)

# ─── Config ───────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SA_KEY     = os.path.join(SCRIPT_DIR, 'serviceAccountKey.json.json')
USER       = 'jseaman1204@gmail.com'
BUCKET     = 'numista-uploads-studio-9101802118-8c9a8'
UA         = 'NumistaAI/1.0 (eric@numista.ai)'
LOG_FILE   = os.path.join(SCRIPT_DIR, 'awq_sourcing_log.json')

WIKIMEDIA_API = 'https://commons.wikimedia.org/w/api.php'
WIKIMEDIA_IMG = 'https://commons.wikimedia.org/wiki/Special:FilePath/{filename}'

# ─── AWQ Design Map (Theme → slug used in Wikimedia searches) ────────────────
# Obverse: Washington portrait — same for ALL AWQ years (shared)
# Reverse: unique per design

THEME_SLUGS = {
    # 2022
    'Maya Angelou':      {'year': '2022', 'slug': 'maya-angelou',      'wiki': 'Maya Angelou'},
    'Dr. Sally Ride':    {'year': '2022', 'slug': 'sally-ride',        'wiki': 'Sally Ride'},
    'Wilma Mankiller':   {'year': '2022', 'slug': 'wilma-mankiller',   'wiki': 'Wilma Mankiller'},
    'Nina Otero-Warren': {'year': '2022', 'slug': 'nina-otero-warren', 'wiki': 'Nina Otero-Warren'},
    'Anna May Wong':     {'year': '2022', 'slug': 'anna-may-wong',     'wiki': 'Anna May Wong'},
    # 2023
    'Bessie Coleman':       {'year': '2023', 'slug': 'bessie-coleman',    'wiki': 'Bessie Coleman'},
    "Edith Kanaka'ole":     {'year': '2023', 'slug': 'edith-kanaka-ole',  'wiki': "Edith Kanakaʻole"},
    'Eleanor Roosevelt':    {'year': '2023', 'slug': 'eleanor-roosevelt', 'wiki': 'Eleanor Roosevelt'},
    'Jovita Idar':          {'year': '2023', 'slug': 'jovita-idar',       'wiki': 'Jovita Idar'},
    'Maria Tallchief':      {'year': '2023', 'slug': 'maria-tallchief',   'wiki': 'Maria Tallchief'},
    # 2024
    'Patsy Takemoto Mink':      {'year': '2024', 'slug': 'patsy-t-mink',        'wiki': 'Patsy Mink'},
    'Dr. Mary Edwards Walker':  {'year': '2024', 'slug': 'mary-edwards-walker', 'wiki': 'Mary Edwards Walker'},
    'Celia Cruz':               {'year': '2024', 'slug': 'celia-cruz',          'wiki': 'Celia Cruz'},
    'Zitkala-Sa':               {'year': '2024', 'slug': 'zitkala-sa',          'wiki': 'Zitkala-Sa'},
    'Pauli Murray':             {'year': '2024', 'slug': 'pauli-murray',        'wiki': 'Pauli Murray'},
}

# Aliases for Theme/Subject field variations in Firestore
THEME_ALIASES = {
    'Sally Ride': 'Dr. Sally Ride',
    'Dr Sally Ride': 'Dr. Sally Ride',
    'Patsy Mink': 'Patsy Takemoto Mink',
    'Patsy T. Mink': 'Patsy Takemoto Mink',
    'Mary Edwards Walker': 'Dr. Mary Edwards Walker',
    "Edith Kanakaʻole": "Edith Kanaka'ole",
    "Edith Kanaka'ole": "Edith Kanaka'ole",
}

# ─── Our reference library already has these reverse images ──────────────────
# These are GCS public URLs we can re-use (no Wikimedia needed for these)
REF_LIBRARY_REVERSES = {
    '2022': {
        'maya-angelou':      'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/american_women/American_Women_quarter_2022_Maya_Angelou.jpeg',
        'sally-ride':        'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/american_women/American_Women_quarter_2022_Sally_Ride.png',
        'wilma-mankiller':   'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/american_women/American_Women_quarter_2022_Wilma_Mankiller.png',
        'nina-otero-warren': 'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/american_women/American_Women_quarter_2022_Nina_Otero-Warren.png',
        'anna-may-wong':     'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/american_women/American_Women_Quarter_2022_Anna_May_Wong.jpg',
    },
    '2023': {
        'bessie-coleman':    'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/american_women/2023_Bessie_Coleman_Womens_Quarter.jpg',
        'edith-kanaka-ole':  'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/american_women/2023_Edith_Kanaka%CA%BBole_Womens_Quarter.jpg',
        'eleanor-roosevelt': 'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/american_women/2023_Eleanor_Roosevelt_Womens_Quarter.jpg',
        'jovita-idar':       'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/american_women/2023_Jovita_Idar_Womens_Quarter.jpg',
        'maria-tallchief':   'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/american_women/2023_Maria_Tallchief_Womens_Quarter.jpg',
    },
    '2024': {
        'patsy-t-mink':        'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/american_women/2024_Patsy_Takemoto_Mink_Womens_Quarter.jpg',
        'mary-edwards-walker': 'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/american_women/2024_Mary_Edwards_Walker_Womens_Quarter.jpg',
        'celia-cruz':          'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/american_women/2024_Celia_Cruz_Womens_Quarter.jpg',
        'zitkala-sa':          'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/american_women/2024_Zitkala_Sa_Womens_Quarter.jpg',
        'pauli-murray':        'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/american_women/2024_Pauli_Murray_Womens_Quarter.jpg',
    },
}

# Wikimedia Commons known-good direct filenames (fallback if ref library 404s)
WIKIMEDIA_DIRECT_FILENAMES = {
    # slug → Wikimedia filename
    'patsy-t-mink':        '2024_Patsy_Takemoto_Mink_Womens_Quarter.jpg',
    'zitkala-sa':          '2024_Zitkala-Sa_Womens_Quarter.jpg',
    'pauli-murray':        '2024_Pauli_Murray_Womens_Quarter.jpg',
    'celia-cruz':          '2024_Celia_Cruz_Womens_Quarter.jpg',
    'mary-edwards-walker': '2024_Mary_Edwards_Walker_Womens_Quarter.jpg',
    'bessie-coleman':      '2023_Bessie_Coleman_Womens_Quarter.jpg',
    'edith-kanaka-ole':    '2023_Edith_Kanakaole_Womens_Quarter.jpg',
    'eleanor-roosevelt':   '2023_Eleanor_Roosevelt_Womens_Quarter.jpg',
    'jovita-idar':         '2023_Jovita_Idar_Womens_Quarter.jpg',
    'maria-tallchief':     '2023_Maria_Tallchief_Womens_Quarter.jpg',
    'maya-angelou':        'American_Women_quarter_2022_Maya_Angelou.jpeg',
    'sally-ride':          'American_Women_quarter_2022_Sally_Ride.png',
    'wilma-mankiller':     'American_Women_quarter_2022_Wilma_Mankiller.png',
    'nina-otero-warren':   'American_Women_quarter_2022_Nina_Otero-Warren.png',
    'anna-may-wong':       'American_Women_Quarter_2022_Anna_May_Wong.jpg',
}

# Shared AWQ obverse (Washington portrait – same for all AWQ years)
AWQ_OBVERSE_REF = 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/2022-american-women-quarters-coin-uncirculated-obverse-philadelphia.jpg'

# ─── Clients ──────────────────────────────────────────────────────────────────
from google.oauth2 import service_account
from google.cloud import firestore, storage


def init_clients():
    creds  = service_account.Credentials.from_service_account_file(SA_KEY)
    db     = firestore.Client(project=creds.project_id, credentials=creds)
    gcs    = storage.Client(project=creds.project_id, credentials=creds)
    bucket = gcs.bucket(BUCKET)
    return db, bucket


# ─── HTTP helpers ─────────────────────────────────────────────────────────────
_session = None


def http():
    global _session
    if _session is None:
        _session = _req.Session()
        _session.headers.update({'User-Agent': UA})
    return _session


def download(url: str) -> tuple:
    """Download URL, return (bytes | None, content_type)."""
    try:
        r = http().get(url, timeout=30, stream=True)
        if r.status_code == 200:
            ct = r.headers.get('Content-Type', 'image/jpeg')
            return r.content, ct
        print(f'    HTTP {r.status_code}: {url[:80]}')
        return None, ''
    except Exception as e:
        print(f'    DL error: {e}')
        return None, ''


def ext_from_url_or_ct(url: str, ct: str) -> str:
    path = url.split('?')[0]
    for e in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
        if path.lower().endswith(f'.{e}'):
            return 'jpg' if e == 'jpeg' else e
    if 'png' in ct:
        return 'png'
    if 'webp' in ct:
        return 'webp'
    return 'jpg'


def upload_to_gcs(bucket, doc_id: str, side: str, data: bytes, url: str, ct: str) -> str | None:
    """Upload image bytes to GCS. Returns public URL (no make_public needed)."""
    ext = ext_from_url_or_ct(url, ct)
    gcs_path = f'users/{USER}/coins/{doc_id}/{side}.{ext}'
    try:
        blob = bucket.blob(gcs_path)
        ct_map = {
            'jpg':  'image/jpeg',
            'png':  'image/png',
            'webp': 'image/webp',
            'gif':  'image/gif',
        }
        blob.upload_from_string(data, content_type=ct_map.get(ext, 'image/jpeg'))
        return f'https://storage.googleapis.com/{BUCKET}/{gcs_path}'
    except Exception as e:
        print(f'    GCS upload error ({side}): {e}')
        return None


def update_firestore(db, doc_id: str, obs_url: str | None, rev_url: str | None,
                     obs_src: str, rev_src: str) -> bool:
    try:
        ref = (db.collection('users')
                 .document(USER)
                 .collection('coins')
                 .document(doc_id))
        updates = {}
        if obs_url:
            updates['image_url_obverse']    = obs_url
            updates['image_source_obverse'] = obs_src
            updates['obverse_image_enriched'] = True
        if rev_url:
            updates['image_url_reverse']    = rev_url
            updates['image_source_reverse'] = rev_src
            updates['reverse_image_enriched'] = True
        if updates:
            ref.update(updates)
        return True
    except Exception as e:
        print(f'    Firestore error: {e}')
        return False


# ─── Firestore query ──────────────────────────────────────────────────────────

def fetch_awq_coins_needing_images(db) -> list:
    """
    Query Firestore for jseaman's coins that:
      - Are in the American Women Quarters program (or Washington Quarter 2022+)
      - Have missing obverse OR reverse images
    """
    print('[firestore] Scanning jseaman collection for AWQ coins with missing images...')
    coins_ref = (db.collection('users')
                   .document(USER)
                   .collection('coins'))

    # Pull all AWQ program coins in one pass
    awq_docs = []

    # Primary filter: Program/Series contains 'Women'
    try:
        snap = coins_ref.stream()
        for doc in snap:
            d = doc.to_dict()
            program = d.get('Program/Series', d.get('program', ''))
            denom   = d.get('Denomination',   d.get('denomination', ''))
            year    = str(d.get('Year',        d.get('year',         '')))
            theme   = d.get('Theme/Subject',   d.get('theme',        ''))

            is_awq = (
                ('Women' in str(program)) or
                ('Quarter' in str(denom) and year.isdigit() and int(year) >= 2022)
            )
            if not is_awq:
                continue

            obs = d.get('image_url_obverse', d.get('Image URL Obverse', '')) or ''
            rev = d.get('image_url_reverse', d.get('Image URL Reverse', '')) or ''

            if obs and rev:
                continue  # already has both images

            awq_docs.append({
                'doc_id':    doc.id,
                'year':      year,
                'mint':      d.get('Mint Mark', d.get('mint', '')),
                'program':   program,
                'theme':     theme,
                'denom':     denom,
                'condition': d.get('Condition', d.get('condition', '')),
                'has_obv':   bool(obs),
                'has_rev':   bool(rev),
                'obs_url':   obs,
                'rev_url':   rev,
                'raw':       {k: v for k, v in d.items() if k in
                              ('Program/Series', 'Theme/Subject', 'Year',
                               'Denomination', 'Mint Mark', 'Condition',
                               'image_url_obverse', 'image_url_reverse')},
            })
    except Exception as e:
        print(f'[firestore] ERROR: {e}')
        raise

    print(f'[firestore] Found {len(awq_docs)} AWQ coins needing ≥1 image')
    return awq_docs


# ─── Theme resolution ─────────────────────────────────────────────────────────

def normalize_theme(raw_theme: str) -> str:
    """Resolve aliases and return canonical theme name."""
    t = raw_theme.strip()
    return THEME_ALIASES.get(t, t)


def get_theme_info(theme: str, year: str) -> dict | None:
    """Look up THEME_SLUGS entry, trying canonical name then year-based fallback."""
    norm = normalize_theme(theme)
    if norm in THEME_SLUGS:
        return THEME_SLUGS[norm]

    # Partial match: check if any slug key contains the theme words
    theme_lower = norm.lower()
    for k, v in THEME_SLUGS.items():
        if theme_lower in k.lower() or k.lower() in theme_lower:
            return v
    return None


# ─── Wikimedia Commons search ─────────────────────────────────────────────────

IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.tif', '.tiff')


def wikimedia_search(query: str, n: int = 8) -> list:
    """Search Wikimedia Commons for image files. Returns list of filename strings."""
    params = {
        'action':      'query',
        'list':        'search',
        'srnamespace': '6',       # File namespace
        'srsearch':    query,
        'srlimit':     str(n),
        'format':      'json',
    }
    try:
        r = http().get(WIKIMEDIA_API, params=params, timeout=15)
        data = r.json()
        results = data.get('query', {}).get('search', [])
        filenames = [re.sub(r'^File:', '', res['title']) for res in results]
        # Filter to image files only — skip PDFs, docs, etc.
        return [fn for fn in filenames
                if any(fn.lower().endswith(ext) for ext in IMAGE_EXTS)]
    except Exception as e:
        print(f'    Wikimedia search error: {e}')
        return []


def wikimedia_file_url(filename: str) -> str | None:
    """Get the direct image URL for a Wikimedia Commons filename."""
    params = {
        'action':  'query',
        'titles':  f'File:{filename}',
        'prop':    'imageinfo',
        'iiprop':  'url',
        'format':  'json',
    }
    try:
        r = http().get(WIKIMEDIA_API, params=params, timeout=15)
        data = r.json()
        pages = data.get('query', {}).get('pages', {})
        for page_id, page in pages.items():
            if page_id == '-1':
                continue
            ii = page.get('imageinfo', [])
            if ii:
                return ii[0]['url']
    except Exception as e:
        print(f'    Wikimedia imageinfo error: {e}')
    return None


def try_direct_wikimedia_filenames(name_variants: list) -> str | None:
    """Try a list of Wikimedia filename candidates and return the first resolvable URL."""
    for fname in name_variants:
        url = wikimedia_file_url(fname)
        if url:
            print(f'    ✓ Wikimedia direct: {fname}')
            return url
        time.sleep(0.3)
    return None


def search_wikimedia_for_obverse(theme: str, year: str, wiki_name: str) -> str | None:
    """Search Wikimedia Commons for a quarter obverse image. Returns direct image URL."""
    # Try direct filenames first (most reliable)
    direct_candidates = [
        f'{year} {wiki_name} quarter obverse.jpg',
        f'American Women Quarter {year} {wiki_name} obverse.jpg',
        f'{wiki_name} quarter obverse.jpg',
        f'2022 American Women Quarters {wiki_name} obverse.png',
    ]
    url = try_direct_wikimedia_filenames(direct_candidates)
    if url:
        return url

    # Fallback: search
    queries = [
        f'american women quarter {wiki_name} obverse',
        f'{year} american women quarters {wiki_name}',
        f'{wiki_name} quarter coin obverse',
    ]
    for q in queries:
        print(f'    Wikimedia search: {q!r}')
        filenames = wikimedia_search(q, n=5)
        for fn in filenames:
            fn_lower = fn.lower()
            if 'obverse' in fn_lower or 'quarter' in fn_lower:
                url = wikimedia_file_url(fn)
                if url:
                    print(f'    ✓ Found via search: {fn}')
                    return url
        time.sleep(0.5)

    return None


def search_wikimedia_for_obverse_by_slug(slug: str) -> str | None:
    """Try known Wikimedia filenames for a specific AWQ design (portrait/reverse side)."""
    fn = WIKIMEDIA_DIRECT_FILENAMES.get(slug)
    if fn:
        url = wikimedia_file_url(fn)
        if url:
            print(f'    ✓ Wikimedia direct ({slug}): {fn}')
            return url
    return None


def search_wikimedia_for_design_portrait(slug: str, theme: str, year: str,
                                          wiki_name: str) -> str | None:
    """
    Search Wikimedia for the AWQ design portrait image (the woman's side).
    In numismatic terminology for AWQ, this is the *reverse* of the coin.
    We call it the 'design portrait' to avoid confusion.
    """
    # Step 1: Try known-good Wikimedia filenames
    url = search_wikimedia_for_obverse_by_slug(slug)
    if url:
        return url

    # Step 2: Try common filename patterns
    safe_name = wiki_name.replace(' ', '_').replace("'", '')
    safe_name2 = wiki_name.replace(' ', '%20')
    direct_candidates = [
        f'{year}_{safe_name}_Womens_Quarter.jpg',
        f'{year}_{safe_name}_quarter.jpg',
        f'American_Women_quarter_{year}_{safe_name}.jpg',
        f'{year} {wiki_name} quarter obverse.jpg',
        f'{year} {wiki_name} American Women Quarter.jpg',
    ]
    url = try_direct_wikimedia_filenames(direct_candidates)
    if url:
        return url

    # Step 3: Search — only match image files, skip generics
    queries = [
        f'american women quarter {wiki_name} {year}',
        f'{year} american women quarters {wiki_name}',
        f'{wiki_name} womens quarter coin',
    ]
    for q in queries:
        print(f'    Wikimedia search: {q!r}')
        filenames = wikimedia_search(q, n=8)
        for fn in filenames:
            fn_lower = fn.lower()
            name_key = wiki_name.split()[-1].lower()  # last name
            if name_key in fn_lower and 'quarter' in fn_lower:
                url = wikimedia_file_url(fn)
                if url:
                    print(f'    ✓ Wikimedia search match: {fn}')
                    return url
        time.sleep(0.5)

    return None


# ─── Image resolution pipeline ────────────────────────────────────────────────

def resolve_obverse(theme_info: dict, theme: str, year: str, mint: str) -> tuple:
    """
    Return (image_url, source_label) for the obverse (Washington portrait).
    All AWQ coins share the same Washington obverse design.
    """
    return AWQ_OBVERSE_REF, 'us_mint_reference'


def resolve_reverse(db, theme_info: dict, theme: str, year: str, mint: str) -> tuple:
    """
    Return (image_url, source_label) for the reverse (design portrait).
    Pipeline: reference library → coin_image_index Firestore → Wikimedia Commons.
    """
    slug = theme_info.get('slug', '') if theme_info else ''
    wiki_name = theme_info.get('wiki', theme) if theme_info else theme

    # Tier 1: Check our reference library (GCS public URLs)
    year_map = REF_LIBRARY_REVERSES.get(year, {})
    if slug and slug in year_map:
        url = year_map[slug]
        try:
            r = http().head(url, timeout=10)
            if r.status_code == 200:
                print(f'    ✓ Ref library: {url[:80]}')
                return url, 'numista_reference_library'
            else:
                print(f'    ✗ Ref library 404 ({r.status_code}): {url[:60]}')
        except Exception as e:
            print(f'    ✗ Ref library error: {e}')

    # Tier 2: Check coin_image_index Firestore collection
    if slug:
        index_doc_id = f'{year}_{slug}_american-women-quarters_reverse'
        try:
            doc = db.collection('coin_image_index').document(index_doc_id).get()
            if doc.exists:
                d = doc.to_dict()
                url = d.get('reverse', {}).get('public_url', '')
                if url:
                    r = http().head(url, timeout=10)
                    if r.status_code == 200:
                        print(f'    ✓ coin_image_index: {url[:80]}')
                        return url, 'coin_image_index'
                    print(f'    ✗ coin_image_index URL 404: {url[:60]}')
        except Exception as e:
            print(f'    ✗ coin_image_index error: {e}')

    # Tier 3: Wikimedia Commons
    print(f'    → Wikimedia Commons for {year} {theme} design portrait...')
    wm_url = search_wikimedia_for_design_portrait(slug, theme, year, wiki_name)
    if wm_url:
        return wm_url, 'wikimedia_commons'

    return None, ''


# ─── Cache for shared images ──────────────────────────────────────────────────
_byte_cache: dict = {}


def get_bytes(url: str) -> tuple:
    if url not in _byte_cache:
        data, ct = download(url)
        if data:
            _byte_cache[url] = (data, ct)
    return _byte_cache.get(url, (None, ''))


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Source AWQ coin images')
    parser.add_argument('--dry-run', action='store_true',
                        help='Resolve URLs and report without uploading or writing Firestore')
    args = parser.parse_args()
    dry_run = args.dry_run

    if dry_run:
        print('[MODE] DRY RUN — no GCS uploads or Firestore writes will occur')

    print('[init] Connecting to Firestore + GCS...')
    db, bucket = init_clients()
    print('[init] ✓ Connected\n')

    # ── Step 1: Find AWQ coins needing images ─────────────────────────────────
    coins = fetch_awq_coins_needing_images(db)
    total = len(coins)

    if total == 0:
        print('[done] No AWQ coins found needing images. All done!')
        return

    # ── Step 2 & 3: Resolve → Download → Upload → Update ─────────────────────
    n_both = n_obs_only = n_rev_only = n_none = n_skip = n_fs_err = 0
    no_obverse_found = []
    no_reverse_found = []
    results = []

    print(f'\nProcessing {total} AWQ coins...\n{"─"*70}')

    for idx, coin in enumerate(coins, 1):
        doc_id    = coin['doc_id']
        theme_raw = coin['theme']
        year      = coin['year']
        mint      = coin.get('mint', '')
        has_obv   = coin['has_obv']
        has_rev   = coin['has_rev']

        theme_norm = normalize_theme(theme_raw)
        theme_info = get_theme_info(theme_raw, year)

        print(f'[{idx:3}/{total}] {year} {mint:<2}  {theme_norm}')

        if not theme_info and not has_obv and not has_rev:
            print(f'    ⚠ Unknown theme, no slug match — skipping')
            n_skip += 1
            results.append({**coin, 'result': 'unknown_theme',
                             'gcs_obverse': None, 'gcs_reverse': None})
            continue

        # ── Resolve source URLs ───────────────────────────────────────────────
        obs_src_url, obs_src_label = ('', '')
        rev_src_url, rev_src_label = ('', '')

        if not has_obv:
            obs_src_url, obs_src_label = resolve_obverse(theme_info, theme_norm, year, mint)

        if not has_rev:
            if theme_info:
                rev_src_url, rev_src_label = resolve_reverse(db, theme_info, theme_norm, year, mint)
            else:
                print(f'    ⚠ No theme_info — cannot resolve reverse')

        print(f'    obverse  src: {(obs_src_url or "N/A")[:80]}')
        print(f'    reverse  src: {(rev_src_url or "N/A")[:80]}')

        # ── Download + Upload ─────────────────────────────────────────────────
        obs_gcs = rev_gcs = None

        if dry_run:
            obs_gcs = obs_src_url or None
            rev_gcs = rev_src_url or None
        else:
            # Obverse
            if obs_src_url and not has_obv:
                obs_data, obs_ct = get_bytes(obs_src_url)
                if obs_data:
                    obs_gcs = upload_to_gcs(bucket, doc_id, 'obverse',
                                            obs_data, obs_src_url, obs_ct)
                    if obs_gcs:
                        print(f'    ✓ obverse → {obs_gcs[:80]}')
                else:
                    print(f'    ✗ obverse download failed')
                    no_obverse_found.append({'doc_id': doc_id, 'theme': theme_norm,
                                             'year': year, 'tried_url': obs_src_url})

            # Reverse
            if rev_src_url and not has_rev:
                rev_data, rev_ct = get_bytes(rev_src_url)
                if rev_data:
                    rev_gcs = upload_to_gcs(bucket, doc_id, 'reverse',
                                            rev_data, rev_src_url, rev_ct)
                    if rev_gcs:
                        print(f'    ✓ reverse → {rev_gcs[:80]}')
                else:
                    print(f'    ✗ reverse download failed')
                    no_reverse_found.append({'doc_id': doc_id, 'theme': theme_norm,
                                             'year': year, 'tried_url': rev_src_url})

        if not obs_src_url and not has_obv:
            no_obverse_found.append({'doc_id': doc_id, 'theme': theme_norm,
                                     'year': year, 'tried_url': None})

        if not rev_src_url and not has_rev:
            no_reverse_found.append({'doc_id': doc_id, 'theme': theme_norm,
                                     'year': year, 'tried_url': None})

        # ── Update Firestore ──────────────────────────────────────────────────
        if not dry_run and (obs_gcs or rev_gcs):
            ok = update_firestore(
                db, doc_id,
                obs_url=obs_gcs, rev_url=rev_gcs,
                obs_src=obs_src_label or 'awq_image_sourcing',
                rev_src=rev_src_label or 'awq_image_sourcing',
            )
            if not ok:
                n_fs_err += 1

        # ── Tally ─────────────────────────────────────────────────────────────
        # Count: "success" means we supplied something for what was missing
        got_obs = obs_gcs is not None or has_obv
        got_rev = rev_gcs is not None or has_rev

        if got_obs and got_rev:
            n_both += 1
            result = 'both'
        elif got_obs:
            n_obs_only += 1
            result = 'obverse_only'
        elif got_rev:
            n_rev_only += 1
            result = 'reverse_only'
        else:
            n_none += 1
            result = 'no_images'

        results.append({
            **coin,
            'theme_norm':    theme_norm,
            'theme_slug':    theme_info.get('slug', '') if theme_info else '',
            'result':        result,
            'obs_src_url':   obs_src_url,
            'obs_src_label': obs_src_label,
            'rev_src_url':   rev_src_url,
            'rev_src_label': rev_src_label,
            'gcs_obverse':   obs_gcs,
            'gcs_reverse':   rev_gcs,
        })

    # ── Final Report ──────────────────────────────────────────────────────────
    # Deduplicate no_reverse_found by theme+year (same design may appear multiple times)
    seen_rev = set()
    unique_no_rev = []
    for item in no_reverse_found:
        key = (item['theme'], item['year'])
        if key not in seen_rev:
            seen_rev.add(key)
            unique_no_rev.append(item)

    seen_obs = set()
    unique_no_obs = []
    for item in no_obverse_found:
        key = (item['theme'], item['year'])
        if key not in seen_obs:
            seen_obs.add(key)
            unique_no_obs.append(item)

    summary = {
        'total_awq_needing_images': total,
        'dry_run': dry_run,
        'results': {
            'both_images': n_both,
            'obverse_only': n_obs_only,
            'reverse_only': n_rev_only,
            'no_images': n_none,
            'unknown_theme_skipped': n_skip,
            'firestore_errors': n_fs_err,
        },
        'designs_missing_obverse': unique_no_obs,
        'designs_missing_reverse': unique_no_rev,
        'coins': results,
    }

    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print()
    print('=' * 70)
    print('AWQ IMAGE SOURCING COMPLETE' + (' [DRY RUN]' if dry_run else ''))
    print(f'  Total AWQ coins needing images : {total}')
    print(f'  ✓ Got both images              : {n_both}')
    print(f'  ~ Obverse only                 : {n_obs_only}')
    print(f'  ~ Reverse only                 : {n_rev_only}')
    print(f'  ✗ No images found              : {n_none}')
    print(f'  ⚠ Unknown theme (skipped)      : {n_skip}')
    if n_fs_err:
        print(f'  ✗ Firestore write errors       : {n_fs_err}')
    print('─' * 70)
    if unique_no_rev:
        print('  Designs still missing REVERSE (try PCGS next):')
        for item in unique_no_rev:
            print(f"    - {item['year']} {item['theme']}")
    if unique_no_obs:
        print('  Designs still missing OBVERSE (try PCGS next):')
        for item in unique_no_obs:
            print(f"    - {item['year']} {item['theme']}")
    print('=' * 70)
    print(f'Log saved → {LOG_FILE}')


if __name__ == '__main__':
    main()
