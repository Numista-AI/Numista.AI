"""
coin_data_audit.py — Numista QC Suite
Data-layer audit for coins collection.
  - Quad title-field check (title, theme_subject, series, program_series)
  - Estate boundary: currency + world_items excluded, foreign coins stay in coins
  - snake_case field key validation
  - NO_QA_DATA hard fail if QA collection is empty

Usage:
  python coin_data_audit.py
  python coin_data_audit.py --verbose
"""

import os
import sys
import json
from pathlib import Path

# Pre-flight: must not run against production
PRODUCTION_PROJECT_ID = 'studio-9101802118-8c9a8'
_target_project = os.environ.get('GOOGLE_CLOUD_PROJECT', '')
if not _target_project:
    manifest_path = Path(__file__).parent.parent / 'SUITE_MANIFEST.json'
    if manifest_path.exists():
        with open(manifest_path) as f:
            _target_project = json.load(f).get('qa_project_id', '')

if _target_project == PRODUCTION_PROJECT_ID:
    sys.exit('ABORT: coin_data_audit.py may not run against the production project.')

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    sys.exit('ABORT: firebase_admin not installed.')

# ---------------------------------------------------------------------------
# Field sets
# ---------------------------------------------------------------------------
# The four title candidates — checked until canonical_title_field is recorded
TITLE_FIELDS = ['title', 'theme_subject', 'series', 'program_series']

# Program coin denominations that MUST have a meaningful title
PROGRAM_DENOMINATIONS = {'quarter', '25c', '$0.25', 'dollar', '$1', 'cent', '1c', 'nickel', '5c', 'dime', '10c'}

# Required snake_case fields that all coin documents must have
REQUIRED_SNAKE_CASE_FIELDS = [
    'coin_id', 'year', 'denomination', 'country',
    'is_foreign', 'review_status',
]

# ---------------------------------------------------------------------------
RESULTS = []

def fail(code, doc_id, detail):
    RESULTS.append({'status': 'FAIL', 'code': code, 'doc_id': doc_id, 'detail': detail})

def warn(code, doc_id, detail):
    RESULTS.append({'status': 'WARN', 'code': code, 'doc_id': doc_id, 'detail': detail})

def ok(code, detail):
    RESULTS.append({'status': 'PASS', 'code': code, 'detail': detail})


def load_manifest():
    manifest_path = Path(__file__).parent.parent / 'SUITE_MANIFEST.json'
    with open(manifest_path) as f:
        return json.load(f)


def get_canonical_field(manifest):
    """Returns canonical title field if confirmed, else None (use quad-check)."""
    return manifest.get('canonical_title_field')  # None means quad-check active


def init_db(manifest):
    if not firebase_admin._apps:
        sa_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        cred = credentials.Certificate(sa_path) if sa_path else credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {'projectId': _target_project})
    return firestore.client()


def check_title_fields(doc_id, data, canonical_field, verbose=False):
    """Check that at least one title field is non-empty."""
    if canonical_field:
        # Narrowed check: canonical + title always checked
        fields_to_check = list({canonical_field, 'title'})
    else:
        # Quad-check: all four until canonical confirmed
        fields_to_check = TITLE_FIELDS

    non_empty = [f for f in fields_to_check if data.get(f, '').strip()]
    if not non_empty:
        fail('COIN_TITLE_FAIL', doc_id,
             f'All title fields empty: {fields_to_check}. '
             f'Flutter _buildTitle() will degrade to year+mint only.')
    elif verbose:
        print(f'  [TITLE_OK] {doc_id}: non-empty fields={non_empty}')


def check_snake_case(doc_id, data):
    """Check required fields exist (snake_case enforcement)."""
    for field in REQUIRED_SNAKE_CASE_FIELDS:
        if field not in data:
            fail('SNAKE_CASE_MISSING', doc_id, f'Required field missing: {field}')


def audit_coins(db, uid, canonical_field, verbose=False):
    coins_ref = db.collection('users').document(uid).collection('coins')
    docs = list(coins_ref.stream())

    if not docs:
        sys.exit('NO_QA_DATA: users/{uid}/coins is empty. Run seed_qc_fixtures.py first.')

    # Track the intentionally-broken fixture
    found_fail_fixture = False
    title_fail_count = 0

    for doc in docs:
        data = doc.to_dict()
        doc_id = doc.id

        # Skip qc internal note field
        check_snake_case(doc_id, data)
        check_title_fields(doc_id, data, canonical_field, verbose)

        if doc_id == 'qc_fixture_title_FAIL_empty':
            found_fail_fixture = True

    # Count title failures
    title_fails = [r for r in RESULTS if r['code'] == 'COIN_TITLE_FAIL']
    title_fail_count = len(title_fails)

    # The intentionally broken fixture must be present and must have failed
    if not found_fail_fixture:
        warn('FIXTURE_MISSING', 'qc_fixture_title_FAIL_empty',
             'Intentionally-broken title fixture not found. Run seed_qc_fixtures.py.')
    else:
        fail_fixture_failed = any(
            r['doc_id'] == 'qc_fixture_title_FAIL_empty'
            for r in title_fails
        )
        if not fail_fixture_failed:
            fail('FIXTURE_SENTINEL_MISSED', 'qc_fixture_title_FAIL_empty',
                 'The intentionally-broken fixture did NOT trigger COIN_TITLE_FAIL. '
                 'The title guard is not working correctly.')
        else:
            ok('FIXTURE_SENTINEL_OK', 'Intentionally-broken fixture correctly triggered COIN_TITLE_FAIL.')

    ok('COINS_AUDITED', f'{len(docs)} coin documents checked. {title_fail_count} title failures.')


def audit_estate_boundary(db, uid, verbose=False):
    """
    Assert that currency and world_items collections are NOT included in estate math.
    We verify by confirming these collections exist separately from coins,
    and that their document IDs do not appear in coins collection.
    """
    coins_ref = db.collection('users').document(uid).collection('coins')
    currency_ref = db.collection('users').document(uid).collection('currency')
    world_items_ref = db.collection('users').document(uid).collection('world_items')

    coin_ids = {doc.id for doc in coins_ref.stream()}
    currency_ids = {doc.id for doc in currency_ref.stream()}
    world_ids = {doc.id for doc in world_items_ref.stream()}

    # No currency doc should share an ID with a coin doc (sanity check)
    overlap_currency = coin_ids & currency_ids
    if overlap_currency:
        fail('ESTATE_BOUNDARY_OVERLAP', 'currency',
             f'Document IDs appear in both coins and currency: {overlap_currency}')
    else:
        ok('ESTATE_CURRENCY_SEPARATED', f'{len(currency_ids)} currency docs confirmed separate from coins.')

    overlap_world = coin_ids & world_ids
    if overlap_world:
        fail('ESTATE_BOUNDARY_OVERLAP', 'world_items',
             f'Document IDs appear in both coins and world_items: {overlap_world}')
    else:
        ok('ESTATE_WORLD_SEPARATED', f'{len(world_ids)} world_items docs confirmed separate from coins.')

    # Foreign coins MUST remain in coins collection (non-negotiable)
    foreign_coins = [
        doc.id for doc in coins_ref.stream()
        if doc.to_dict().get('is_foreign') is True
    ]
    if foreign_coins:
        ok('FOREIGN_COINS_IN_COINS', f'{len(foreign_coins)} foreign coin(s) correctly in users/{{uid}}/coins.')
    elif verbose:
        print('  [INFO] No foreign coins in QA collection.')


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    manifest = load_manifest()
    uid = manifest.get('qc_uid')
    if not uid:
        sys.exit('ABORT: qc_uid not in SUITE_MANIFEST.json')

    canonical_field = get_canonical_field(manifest)
    if canonical_field:
        print(f'[coin_data_audit] Using confirmed canonical field: {canonical_field}')
    else:
        print(f'[coin_data_audit] No canonical_title_field in manifest — quad-check active ({TITLE_FIELDS})')

    db = init_db(manifest)

    print('[coin_data_audit] Auditing coins...')
    audit_coins(db, uid, canonical_field, verbose=args.verbose)

    print('[coin_data_audit] Auditing estate boundary...')
    audit_estate_boundary(db, uid, verbose=args.verbose)

    # Report
    fails = [r for r in RESULTS if r['status'] == 'FAIL']
    warns = [r for r in RESULTS if r['status'] == 'WARN']
    passes = [r for r in RESULTS if r['status'] == 'PASS']

    print(f'\n[coin_data_audit] RESULTS: {len(passes)} PASS / {len(warns)} WARN / {len(fails)} FAIL')
    for r in warns:
        print(f'  WARN  [{r["code"]}] {r["doc_id"]}: {r["detail"]}')
    for r in fails:
        print(f'  FAIL  [{r["code"]}] {r["doc_id"]}: {r["detail"]}')

    if fails:
        sys.exit(1)


if __name__ == '__main__':
    main()