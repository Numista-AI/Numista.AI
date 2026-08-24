"""
backfill_is_foreign.py  — v4, three-phase protocol (P3-D-03 / P3-D-11)

PIPELINE ISOLATION:
  Adds is_foreign: False to coin documents missing the field only.
  Does NOT alter passport_pdf_generator.py, numista_bq_loader_job.py,
  or tier_gatekeeper.py query paths or output schemas.
  users/{uid}/world_items is never touched by this script.
  Adding is_foreign: False to US coins only confirms what those pipelines
  already assume. It does not change their read paths or output schemas.

Phase Q4-1: UID_FILTER=<uid> DRY_RUN=true   — print paths, no write. Eric reviews backfill_audit.json.
Phase Q4-2: UID_FILTER=<uid> DRY_RUN=false  — single user write only. Eric verifies in Firebase Console.
Phase Q4-3: UID_FILTER=''   DRY_RUN=false   — full collection-group. Requires second explicit approval.

Safety:
  - update() only — no other fields disturbed, no document ID changes, no hard deletes
  - Idempotent: documents already having is_foreign are skipped (no re-write)
  - Every document path logged to stdout AND to backfill_audit.json before any write
"""
import os
import json
import datetime
from google.cloud import firestore

DRY_RUN    = os.environ.get('DRY_RUN', 'true').lower() == 'true'
UID_FILTER = os.environ.get('UID_FILTER', '')  # empty string = collection-group (Q4-3 only)
db = firestore.Client()


def run():
    if UID_FILTER:
        docs  = db.collection('users').document(UID_FILTER).collection('coins').stream()
        scope = f'single user: {UID_FILTER}'
    else:
        docs  = db.collection_group('coins').stream()
        scope = 'ALL USERS (collection-group)'

    print(f'Scope : {scope}')
    print(f'DRY_RUN: {DRY_RUN}')
    print()

    touched_paths = []
    skipped = 0

    for doc in docs:
        data = doc.to_dict()
        if data is None:
            continue
        if 'is_foreign' not in data:
            touched_paths.append(doc.reference.path)
            action = '[DRY-RUN] would update' if DRY_RUN else 'updating'
            print(f'{action}: {doc.reference.path}')
            if not DRY_RUN:
                doc.reference.update({'is_foreign': False})
        else:
            skipped += 1

    # Write audit log — always, even on dry-run
    record = {
        'timestamp'     : datetime.datetime.utcnow().isoformat() + 'Z',
        'scope'         : scope,
        'dry_run'       : DRY_RUN,
        'touched_count' : len(touched_paths),
        'skipped_count' : skipped,
        'touched_paths' : touched_paths,
    }
    audit_path = 'backfill_audit.json'
    with open(audit_path, 'w', encoding='utf-8') as f:
        json.dump(record, f, indent=2)

    print()
    print(f'Done. touched={len(touched_paths)}  skipped={skipped}')
    print(f'Audit written to: {audit_path}')
    if DRY_RUN and touched_paths:
        print()
        print('Next step: review backfill_audit.json, then re-run with DRY_RUN=false')
        print('(requires explicit Eric approval before proceeding)')


if __name__ == '__main__':
    run()
