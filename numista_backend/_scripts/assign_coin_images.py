# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
assign_coin_images.py
=====================
Matches jseaman1204@gmail.com's coins to GCS reference images and writes
image_url_obverse (and image_url_reverse where available) to Firestore.

Strategy:
  1. Build a searchable index of all GCS reference images
  2. For each coin missing an image, score GCS images by:
     - Year match (+3)
     - Series keyword overlap (+1 per keyword)
     - Series-specific boosts
  3. Write the best matching obverse URL to Firestore
  4. Also write reverse URL if available
  5. Track which coins were matched vs still missing

Run:
    python assign_coin_images.py --dry-run    # preview only
    python assign_coin_images.py              # live write to Firestore
    python assign_coin_images.py --limit 100  # test on 100 coins first
"""

import argparse
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import google.auth
from google.cloud import storage as gcs, firestore

# ── CONFIG ─────────────────────────────────────────────────────────────────────
PROJECT      = 'studio-9101802118-8c9a8'
BUCKET_NAME  = 'numista-uploads-studio-9101802118-8c9a8'
USER_EMAIL   = 'jseaman1204@gmail.com'

# GCS prefixes to search (ordered by quality preference)
GCS_PREFIXES = [
    'reference_images/us_mint/',      # Official US Mint press images — highest quality
    'reference_images/new_coin_images/',
    'kaggle/morgan/',
    'kaggle/franklin/',
    'kaggle/kennedy/',
    'kaggle/eisenhower/',
    'kaggle/susan_anthony/',
    'kaggle/state_quarters/',
    'kaggle/us_coins/',
    'kaggle/training/',
    'kaggle/misc/',
    'reference_images/memoir_coin/',  # Lowest preference — replicas
]

# Series name -> keywords likely in GCS filenames
SERIES_KEYWORDS = {
    'lincoln':              ['lincoln', 'cent', 'penny', 'wheat'],
    'roosevelt':            ['roosevelt', 'dime'],
    'washington':           ['washington', 'quarter'],
    'kennedy':              ['kennedy', 'half'],
    'jefferson':            ['jefferson', 'nickel'],
    'morgan':               ['morgan', 'dollar'],
    'peace':                ['peace', 'dollar'],
    'eagle':                ['eagle'],
    'buffalo':              ['buffalo', 'nickel'],
    'mercury':              ['mercury', 'dime', 'winged'],
    'barber':               ['barber'],
    'presidential':         ['presidential', 'dollar'],
    'eisenhower':           ['eisenhower', 'dollar', 'ike'],
    'sacagawea':            ['sacagawea', 'native'],
    'state quarter':        ['quarter', 'state'],
    'bicentennial':         ['bicentennial'],
    'walking liberty':      ['walking', 'liberty'],
    'standing liberty':     ['standing', 'liberty'],
    'franklin':             ['franklin', 'half'],
    'american women':       ['quarter', 'women'],
    'atb':                  ['quarter', 'beautiful'],
    'gold eagle':           ['eagle', 'gold'],
    'silver eagle':         ['eagle', 'silver'],
    'gold buffalo':         ['buffalo', 'gold'],
    'susan':                ['susan', 'anthony'],
    'susan b':              ['susan', 'anthony'],
    'civil war':            ['civil', 'war'],
    'baseball':             ['baseball', 'hall'],
    'basketball':           ['basketball'],
    'apollo':               ['apollo'],
    'purple heart':         ['purple', 'heart'],
    'bald eagle':           ['bald', 'eagle'],
    'statue of liberty':    ['statue', 'liberty'],
    'ellis island':         ['ellis', 'island'],
    'wwii':                 ['world', 'war'],
    'world war':            ['world', 'war'],
    'half dollar':          ['half', 'dollar'],
    'trade dollar':         ['trade', 'dollar'],
    'flying eagle':         ['flying', 'eagle', 'cent'],
    'shield nickel':        ['shield', 'nickel'],
    'liberty head nickel':  ['liberty', 'nickel'],
    'braided hair':         ['braided', 'hair', 'cent'],
    'capped bust':          ['capped', 'bust'],
    'classic head':         ['classic', 'head'],
    'draped bust':          ['draped', 'bust'],
    'liberty seated':       ['liberty', 'seated'],
    'seated liberty':       ['seated', 'liberty'],
    '20 cent':              ['cent', 'twenty'],
    'three cent':           ['three', 'cent'],
}


def build_gcs_index(bucket) -> list[dict]:
    """Load all GCS reference images into a searchable index."""
    print("Building GCS image index...")
    index = []
    seen_names = set()

    for prefix in GCS_PREFIXES:
        blobs = list(bucket.list_blobs(prefix=prefix))
        priority = GCS_PREFIXES.index(prefix)  # lower = higher quality

        for blob in blobs:
            filename = blob.name.split('/')[-1].lower()
            if not re.search(r'\.(jpg|jpeg|png|webp)$', filename):
                continue

            stem   = re.sub(r'\.(jpg|jpeg|png|webp)$', '', filename)
            tokens = set(re.split(r'[-_\s.]+', stem))
            tokens = {t for t in tokens if len(t) >= 2}

            year_m = re.search(r'(1[6789]\d{2}|20\d{2})', stem)
            year   = year_m.group(1) if year_m else None

            side = ('obverse' if re.search(r'ob[vs]|front|head|obverse', stem)
                    else 'reverse' if re.search(r'rev|back|tail|reverse', stem)
                    else 'unknown')

            url = (f'https://storage.googleapis.com/{BUCKET_NAME}/{blob.name}')

            index.append({
                'url':      url,
                'blob':     blob.name,
                'tokens':   tokens,
                'year':     year,
                'side':     side,
                'priority': priority,
                'stem':     stem,
            })

    print(f"  Index built: {len(index)} images across {len(GCS_PREFIXES)} sources")
    return index


def score_match(entry: dict, year_s: str, search_tokens: set, series_lower: str) -> float:
    score = 0.0

    # Year match — strong signal
    if year_s and entry['year'] == year_s:
        score += 4.0

    # Token overlap
    overlap = len(search_tokens & entry['tokens'])
    score  += overlap * 1.0

    # Series-specific keyword boosts
    for kw, boosts in SERIES_KEYWORDS.items():
        if kw in series_lower:
            boost = sum(1 for b in boosts if b in entry['tokens'])
            score += boost * 0.8

    # Penalize lower-quality sources slightly
    score -= entry['priority'] * 0.1

    # Prefer obverse for primary match
    if entry['side'] == 'obverse':
        score += 0.5

    return score


def find_best_match(year, series, denom, index: list[dict]) -> tuple[str | None, str | None]:
    """Return (obverse_url, reverse_url) best matches."""
    year_s  = str(year).strip() if year else ''
    s_lower = (series or '').lower()
    d_lower = (denom  or '').lower()

    search = set(re.split(r'[-_\s/,]+', f'{s_lower} {d_lower}'))
    search = {t for t in search if len(t) >= 3
              and t not in ('the','and','for','set','coin','unc','proof','all','series')}

    best_obv_score = 0.0
    best_rev_score = 0.0
    best_obv_url   = None
    best_rev_url   = None

    for entry in index:
        sc = score_match(entry, year_s, search, s_lower)
        if sc < 1.5:
            continue

        if entry['side'] in ('obverse', 'unknown'):
            if sc > best_obv_score:
                best_obv_score = sc
                best_obv_url   = entry['url']
        if entry['side'] == 'reverse':
            if sc > best_rev_score:
                best_rev_score = sc
                best_rev_url   = entry['url']

    return best_obv_url, best_rev_url


# ── MAIN ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Preview only, no Firestore writes')
    parser.add_argument('--limit',   type=int, default=0,  help='Only process N coins (0=all)')
    args = parser.parse_args()

    creds, _ = google.auth.default()
    gcs_client = gcs.Client(credentials=creds, project=PROJECT)
    fs_client  = firestore.Client(credentials=creds, project=PROJECT)

    bucket = gcs_client.bucket(BUCKET_NAME)
    index  = build_gcs_index(bucket)

    # Fetch all coins missing images
    print(f"\nFetching {USER_EMAIL} coins...")
    coins_ref = (fs_client.collection('users')
                 .document(USER_EMAIL)
                 .collection('coins'))
    all_coins = list(coins_ref.stream())

    missing = [c for c in all_coins if not (c.to_dict().get('image_url_obverse') or '').strip()]
    print(f"  Total coins:   {len(all_coins)}")
    print(f"  Missing image: {len(missing)}")

    if args.limit:
        missing = missing[:args.limit]
        print(f"  Processing:    {len(missing)} (limited)")

    print(f"\n{'DRY RUN — ' if args.dry_run else ''}Matching and {'previewing' if args.dry_run else 'writing'}...\n")

    matched   = 0
    no_match  = 0
    written   = 0
    errors    = 0
    gap_series = Counter()

    now = datetime.now(timezone.utc).isoformat()

    for i, coin in enumerate(missing):
        d      = coin.to_dict()
        series = d.get('Program/Series', '') or ''
        year   = d.get('Year', '')            or ''
        denom  = d.get('Denomination', '')    or ''
        ref_no = d.get('Personal Ref #', '')  or ''

        obv_url, rev_url = find_best_match(year, series, denom, index)

        if obv_url:
            matched += 1
            if args.dry_run:
                if i < 20:  # show first 20 in dry run
                    print(f"  [{ref_no}] {year} {series[:40]}")
                    print(f"       OBV: {obv_url.split('/')[-1]}")
                    if rev_url:
                        print(f"       REV: {rev_url.split('/')[-1]}")
            else:
                try:
                    update = {
                        'image_url_obverse': obv_url,
                        'image_source':      'gcs_reference',
                        'image_updated_at':  now,
                    }
                    if rev_url:
                        update['image_url_reverse'] = rev_url
                    coins_ref.document(coin.id).update(update)
                    written += 1
                    if written % 100 == 0:
                        print(f"  Written {written}/{matched}...")
                    time.sleep(0.05)  # rate limit
                except Exception as e:
                    print(f"  ERROR coin {coin.id}: {e}")
                    errors += 1
        else:
            no_match += 1
            key = series.strip() or '(blank)'
            gap_series[key] += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"  Assignment {'Preview' if args.dry_run else 'Complete'}!")
    print(f"  Matched:      {matched}")
    print(f"  Written:      {written}")
    print(f"  No match:     {no_match}")
    print(f"  Errors:       {errors}")
    print(f"{'='*60}")
    print(f"\nRemaining gaps ({no_match} coins) — candidates for AI generation:")
    for series, count in gap_series.most_common(25):
        print(f"  {count:>4}  {series}")


if __name__ == '__main__':
    main()
