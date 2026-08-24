"""
account_integrity.py — Numista QC Suite
Read-only Firestore audit of the QA account.
Use --apply-repairs to execute merge-only field repairs on existing documents.
Never deletes documents. Never mutates document IDs.

Usage:
  python account_integrity.py              # Read-only scan
  python account_integrity.py --verbose    # With document-level output
  python account_integrity.py --apply-repairs  # Execute queued merge repairs
"""

import os
import sys
import json
import argparse
from pathlib import Path

PRODUCTION_PROJECT_ID = 'studio-9101802118-8c9a8'
_target_project = os.environ.get('GOOGLE_CLOUD_PROJECT', '')
if not _target_project:
    manifest_path = Path(__file__).parent.parent / 'SUITE_MANIFEST.json'
    if manifest_path.exists():
        with open(manifest_path) as f:
            _target_project = json.load(f).get('qa_project_id', '')

if _target_project == PRODUCTION_PROJECT_ID:
    sys.exit('ABORT: account_integrity.py may not run against the production project.')

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    sys.exit('ABORT: firebase_admin not installed.')

REQUIRED_COIN_FIELDS = [
    'year', 'denomination', 'country', 'is_foreign', 'review_status'
]

REPAIR_LOG_PATH = Path(__file__).parent / '_repair_log.json'


def load_manifest():
    manifest_path = Path(__file__).parent.parent / 'SUITE_MANIFEST.json'
    with open(manifest_path) as f:
        return json.load(f)


def init_db(manifest):
    if not firebase_admin._apps:
        sa_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        cred = credentials.Certificate(sa_path) if sa_path else credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {'projectId': _target_project})
    return firestore.client()


def scan_coins(db, uid, verbose=False):
    coins_ref = db.collection('users').document(uid).collection('coins')
    docs = list(coins_ref.stream())
    repairs_needed = []
    issues = []

    for doc in docs:
        data = doc.to_dict()
        doc_id = doc.id

        missing = [f for f in REQUIRED_COIN_FIELDS if f not in data]
        if missing:
            issues.append(f'MISSING_FIELDS {doc_id}: {missing}')
            repairs_needed.append({
                'collection': 'coins',
                'doc_id': doc_id,
                'repair': {f: None for f in missing},
                'reason': f'Missing required fields: {missing}'
            })

        # Detect camelCase keys that should be snake_case
        camel_keys = [k for k in data.keys() if any(c.isupper() for c in k)]
        if camel_keys:
            issues.append(f'CAMEL_CASE_KEYS {doc_id}: {camel_keys}')

        if verbose:
            print(f'  [DOC] {doc_id}: fields={list(data.keys())}')

    return docs, repairs_needed, issues


def apply_repairs(db, uid, repairs):
    coins_ref = db.collection('users').document(uid).collection('coins')
    repaired = 0
    skipped = 0

    for repair in repairs:
        doc_ref = coins_ref.document(repair['doc_id'])
        existing = doc_ref.get()
        if not existing.exists:
            print(f'  REPAIR_TARGET_MISSING: {repair["doc_id"]} — skipping')
            skipped += 1
            continue
        # SetOptions(merge=True) — never replaces whole document
        doc_ref.set(repair['repair'], merge=True)
        print(f'  REPAIRED: {repair["doc_id"]} — {repair["reason"]}')
        repaired += 1

    return repaired, skipped


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--apply-repairs', action='store_true',
                        help='Execute merge-only repairs on existing documents')
    args = parser.parse_args()

    manifest = load_manifest()
    uid = manifest.get('qc_uid')
    if not uid:
        sys.exit('ABORT: qc_uid not in SUITE_MANIFEST.json')

    db = init_db(manifest)

    print(f'[account_integrity] Scanning QA account UID={uid}...')
    docs, repairs_needed, issues = scan_coins(db, uid, verbose=args.verbose)

    print(f'  Scanned {len(docs)} coin documents.')
    if issues:
        for issue in issues:
            print(f'  ISSUE: {issue}')
    else:
        print('  No issues found.')

    # Write repair log regardless of --apply-repairs
    if repairs_needed:
        with open(REPAIR_LOG_PATH, 'w') as f:
            json.dump(repairs_needed, f, indent=2)
        print(f'  Repair log written: {REPAIR_LOG_PATH} ({len(repairs_needed)} items)')

    if args.apply_repairs and repairs_needed:
        print(f'[account_integrity] Applying {len(repairs_needed)} repairs (merge=True only)...')
        repaired, skipped = apply_repairs(db, uid, repairs_needed)
        print(f'  Repaired={repaired} Skipped(target missing)={skipped}')
    elif args.apply_repairs:
        print('[account_integrity] No repairs needed.')
    else:
        if repairs_needed:
            print(f'[account_integrity] {len(repairs_needed)} repairs queued. Run with --apply-repairs to execute.')

    if issues:
        sys.exit(1)


if __name__ == '__main__':
    main()