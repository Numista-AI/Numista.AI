"""
seed_qc_fixtures.py — Numista QC Suite
Idempotent seeder for QA project fixture documents.
Self-protecting: aborts if targeting production project or a forbidden account.

Usage:
  python seed_qc_fixtures.py              # Create fixtures if missing
  python seed_qc_fixtures.py --reset      # Delete and recreate all qc_fixture_* docs
  python seed_qc_fixtures.py --check      # Verify fixtures exist, no writes
"""

import os
import sys
import json
import argparse
from pathlib import Path

# ---------------------------------------------------------------------------
# SELF-PROTECTION PRE-FLIGHT — runs before any import of firebase_admin
# ---------------------------------------------------------------------------
PRODUCTION_PROJECT_ID = 'studio-9101802118-8c9a8'
FORBIDDEN_ACCOUNTS = [
    'ericdcman@gmail.com',
    'eric.seaman@yahoo.com',
    'jseaman1204@gmail.com',
]

def _read_manifest_project():
    manifest_path = Path(__file__).parent.parent / 'SUITE_MANIFEST.json'
    if manifest_path.exists():
        with open(manifest_path) as f:
            return json.load(f).get('qa_project_id', '')
    return ''

def _read_service_account_email():
    sa_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', '')
    if sa_path and Path(sa_path).exists():
        try:
            with open(sa_path) as f:
                return json.load(f).get('client_email', '')
        except Exception:
            pass
    return ''

_target_project = os.environ.get('GOOGLE_CLOUD_PROJECT') or _read_manifest_project()
if _target_project == PRODUCTION_PROJECT_ID:
    sys.exit(
        f'ABORT: seed_qc_fixtures.py may not run against the production project '
        f'({PRODUCTION_PROJECT_ID}). Set GOOGLE_CLOUD_PROJECT to the QA project ID.'
    )

_cred_email = _read_service_account_email()
if any(f in _cred_email for f in FORBIDDEN_ACCOUNTS):
    sys.exit(
        f'ABORT: seed_qc_fixtures.py may not run with a forbidden account credential '
        f'({_cred_email}). Use a QA service account.'
    )

# ---------------------------------------------------------------------------
# Firebase admin — imported only after pre-flight passes
# ---------------------------------------------------------------------------
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    sys.exit('ABORT: firebase_admin not installed. Run: pip install firebase-admin')

# ---------------------------------------------------------------------------
# Fixture definitions
# ---------------------------------------------------------------------------
FIXTURES_COINS = [
    {
        'id': 'qc_fixture_title_ok_quarter',
        'data': {
            'series': 'State Quarter Program',
            'theme_subject': 'New Jersey',
            'title': '1999-D New Jersey State Quarter',
            'year': '1999',
            'mint_mark': 'D',
            'denomination': '25c',
            'country': 'United States',
            'is_foreign': False,
            'program_series': 'State Quarter Program',
            'review_status': 'approved',
        }
    },
    {
        'id': 'qc_fixture_title_ok_dollar',
        'data': {
            'series': 'Morgan Dollar',
            'theme_subject': '',
            'title': '1921 Morgan Dollar',
            'year': '1921',
            'mint_mark': '',
            'denomination': '$1',
            'country': 'United States',
            'is_foreign': False,
            'program_series': '',
            'review_status': 'approved',
        }
    },
    {
        'id': 'qc_fixture_title_FAIL_empty',
        'data': {
            'series': '',
            'theme_subject': '',
            'title': '',
            'program_series': '',
            'year': '1999',
            'mint_mark': 'D',
            'denomination': '25c',
            'country': 'United States',
            'is_foreign': False,
            'review_status': 'approved',
            '_qc_note': 'INTENTIONALLY BROKEN: all title fields empty. coin_data_audit MUST fail on this document.',
        }
    },
    {
        'id': 'qc_fixture_foreign_coin',
        'data': {
            'series': 'Mexican Libertad',
            'theme_subject': 'Libertad',
            'title': '1982 Mexican Libertad 1 oz Silver',
            'year': '1982',
            'mint_mark': 'Mo',
            'denomination': '1 oz',
            'country': 'Mexico',
            'is_foreign': True,
            'program_series': 'Libertad Series',
            'review_status': 'approved',
        }
    },
    {
        'id': 'qc_fixture_estate_coin',
        'data': {
            'series': 'Peace Dollar',
            'theme_subject': '',
            'title': '1922 Peace Dollar',
            'year': '1922',
            'mint_mark': '',
            'denomination': '$1',
            'country': 'United States',
            'is_foreign': False,
            'estimated_value': 125.00,
            'review_status': 'approved',
        }
    },
]

FIXTURES_CURRENCY = [
    {
        'id': 'qc_fixture_currency_excluded',
        'data': {
            'title': '1899 Silver Certificate $1',
            'denomination': '$1',
            'year': '1899',
            'country': 'United States',
            '_qc_note': 'Must be excluded from estate math. Never appears in users/{uid}/coins.',
        }
    },
]

FIXTURES_WORLD_ITEMS = [
    {
        'id': 'qc_fixture_exonumia_excluded',
        'data': {
            'title': '1925 Stone Mountain Memorial Medal',
            'item_type': 'medal',
            'year': '1925',
            'country': 'United States',
            '_qc_note': 'Must be excluded from estate math. Never appears in users/{uid}/coins.',
        }
    },
]

# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def get_db():
    if not firebase_admin._apps:
        sa_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if sa_path:
            cred = credentials.Certificate(sa_path)
        else:
            cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {
            'projectId': _target_project or os.environ.get('GOOGLE_CLOUD_PROJECT'),
        })
    return firestore.client()


def get_qc_uid(db):
    """Read qc_uid from SUITE_MANIFEST.json."""
    manifest_path = Path(__file__).parent.parent / 'SUITE_MANIFEST.json'
    with open(manifest_path) as f:
        manifest = json.load(f)
    uid = manifest.get('qc_uid')
    if not uid:
        sys.exit('ABORT: qc_uid not set in SUITE_MANIFEST.json. Provision the QA account first.')
    return uid


def seed_collection(db, uid, collection_name, fixtures, reset=False):
    coll_ref = db.collection('users').document(uid).collection(collection_name)
    created = 0
    skipped = 0
    deleted = 0

    if reset:
        for fix in fixtures:
            doc_ref = coll_ref.document(fix['id'])
            if doc_ref.get().exists:
                doc_ref.delete()
                deleted += 1

    for fix in fixtures:
        doc_ref = coll_ref.document(fix['id'])
        if reset or not doc_ref.get().exists:
            doc_ref.set(fix['data'])  # whole-document write, no merge
            created += 1
        else:
            skipped += 1

    return created, skipped, deleted


def check_collection(db, uid, collection_name, fixtures):
    coll_ref = db.collection('users').document(uid).collection(collection_name)
    missing = []
    for fix in fixtures:
        if not coll_ref.document(fix['id']).get().exists:
            missing.append(fix['id'])
    return missing


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reset', action='store_true',
                        help='Delete and recreate all qc_fixture_* documents')
    parser.add_argument('--check', action='store_true',
                        help='Verify fixtures exist without writing')
    args = parser.parse_args()

    db = get_db()
    uid = get_qc_uid(db)

    print(f'[seed_qc_fixtures] Project: {_target_project} | UID: {uid} | reset={args.reset} | check={args.check}')

    if args.check:
        all_missing = []
        all_missing += check_collection(db, uid, 'coins', FIXTURES_COINS)
        all_missing += check_collection(db, uid, 'currency', FIXTURES_CURRENCY)
        all_missing += check_collection(db, uid, 'world_items', FIXTURES_WORLD_ITEMS)
        if all_missing:
            print(f'FIXTURE_CHECK_FAIL: missing {all_missing}')
            sys.exit(1)
        print('FIXTURE_CHECK_OK: all fixtures present')
        return

    for coll_name, fixtures in [
        ('coins', FIXTURES_COINS),
        ('currency', FIXTURES_CURRENCY),
        ('world_items', FIXTURES_WORLD_ITEMS),
    ]:
        created, skipped, deleted = seed_collection(db, uid, coll_name, fixtures, reset=args.reset)
        print(f'  {coll_name}: created={created} skipped={skipped} deleted={deleted}')

    print('[seed_qc_fixtures] Done.')


if __name__ == '__main__':
    main()