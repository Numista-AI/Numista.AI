#!/usr/bin/env python3
"""
patch_atb_attribution.py
========================
Patch run after process_local_coin_images.py:
1. Add attribution metadata to already-uploaded ATB GCS blobs
2. Fix user-specific obverse copies for 2016-2020 coins (those that got 404 in first run)
3. Add attribution fields to Firestore ATB coin documents already updated

Usage:
    python patch_atb_attribution.py [--dry-run]
"""

import io
import json
import os
import re
import sys
import tempfile
import argparse
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(
    sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True
)

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
SA_KEY      = os.path.join(SCRIPT_DIR, 'serviceAccountKey.json.json')
PROJECT_ID  = 'studio-9101802118-8c9a8'
REF_BUCKET  = 'numista-reference-library'
UPL_BUCKET  = 'numista-uploads-studio-9101802118-8c9a8'
LOG_FILE    = os.path.join(SCRIPT_DIR, 'local_image_upload_log.json')
PATCH_LOG   = os.path.join(SCRIPT_DIR, 'patch_attribution_log.json')
ATB_PREFIX  = 'reference_library/atb_quarters/'
USERS       = ['eric@numista.ai', 'jseaman1204@gmail.com']

PUBLIC_URL_BASE = 'https://storage.googleapis.com/{bucket}/{path}'

ATTRIB = {
    'usmint': {
        'attribution': 'United States Mint. Public domain (17 U.S.C. \u00a7 105). Source: usmint.gov',
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

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage as gcs_storage

cred = credentials.Certificate(SA_KEY)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {'projectId': PROJECT_ID})
db = firestore.client()

gcs_client = gcs_storage.Client.from_service_account_json(SA_KEY)
ref_bucket_obj = gcs_client.bucket(REF_BUCKET)
upl_bucket_obj = gcs_client.bucket(UPL_BUCKET)

patch_log = {
    'run_timestamp': datetime.now().isoformat() + 'Z',
    'gcs_metadata_patched': [],
    'user_obverse_copies_fixed': [],
    'firestore_attribution_updates': [],
    'errors': [],
}

def log_error(msg, exc=None):
    entry = {'error': msg}
    if exc:
        entry['exception'] = str(exc)
    patch_log['errors'].append(entry)
    print(f'  [ERROR] {msg}' + (f' \u2014 {exc}' if exc else ''))


# ─── Load the original run log ─────────────────────────────────────────────────
def load_run_log():
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


# ─── 1. Patch GCS blob metadata for all uploaded ATB images ───────────────────
def patch_gcs_metadata(run_log, dry_run=False):
    print('\n' + '='*60)
    print('STEP 1: Patching GCS blob attribution metadata')
    print('='*60)

    all_uploads = run_log.get('task1_atb_uploads', []) + run_log.get('task2_new_coin_uploads', [])
    print(f'  Found {len(all_uploads)} uploaded blobs to patch')

    for entry in all_uploads:
        gcs_path = entry.get('gcs_path', '')
        cat = entry.get('category', '')
        # Choose attrib key
        if 'jamul' in gcs_path or cat == 'jamul_sovereign_nation':
            attrib_key = 'jamul'
        elif 'generic' in gcs_path or cat == 'generic_denomination':
            attrib_key = 'generic'
        else:
            attrib_key = 'usmint'

        meta = ATTRIB[attrib_key]

        if dry_run:
            print(f'  [DRY-RUN] Would patch metadata: {gcs_path} ({attrib_key})')
            patch_log['gcs_metadata_patched'].append({'gcs_path': gcs_path, 'attrib_key': attrib_key, 'status': 'dry_run'})
            continue

        try:
            # Try ref bucket first, then uploads bucket
            bucket = ref_bucket_obj if REF_BUCKET in entry.get('url', '') else upl_bucket_obj
            blob = bucket.blob(gcs_path)
            blob.reload()
            blob.metadata = {
                'attribution': meta['attribution'],
                'source':      meta['source'],
                'license':     meta['license'],
                'copyright':   meta['copyright'],
            }
            blob.patch()
            print(f'  [GCS] Patched metadata: {gcs_path}')
            patch_log['gcs_metadata_patched'].append({'gcs_path': gcs_path, 'attrib_key': attrib_key, 'status': 'ok'})
        except Exception as e:
            log_error(f'Failed to patch metadata for {gcs_path}', e)
            patch_log['gcs_metadata_patched'].append({'gcs_path': gcs_path, 'attrib_key': attrib_key, 'status': 'error', 'error': str(e)})

    ok = sum(1 for e in patch_log['gcs_metadata_patched'] if e.get('status') == 'ok')
    print(f'\n  GCS metadata patched: {ok}/{len(all_uploads)}')


# ─── 2. Fix user-specific obverse copies ──────────────────────────────────────
def fix_obverse_user_copies(run_log, dry_run=False):
    print('\n' + '='*60)
    print('STEP 2: Fixing user-specific obverse copies (2016-2020)')
    print('='*60)

    # Build year → actual uploaded obverse GCS path
    year_to_obverse_path = {}
    for entry in run_log.get('task1_atb_uploads', []):
        if entry.get('side') == 'obverse' and 'proof' not in entry.get('filename', '').lower():
            yr = entry.get('year', '')
            mint = entry.get('mint', 'P')
            if yr and (yr not in year_to_obverse_path or mint == 'P'):
                year_to_obverse_path[yr] = entry['gcs_path']

    print(f'  Year→obverse map: {len(year_to_obverse_path)} years')
    for yr, path in sorted(year_to_obverse_path.items()):
        print(f'    {yr}: {path}')

    # Find Firestore updates where the obverse URL is a reference library URL
    # (not a user-specific uploads URL — meaning the copy failed)
    ref_prefix = f'https://storage.googleapis.com/{REF_BUCKET}/'

    for email in USERS:
        print(f'\n  Checking account: {email}')
        try:
            docs = db.collection('users').document(email).collection('coins').stream()
        except Exception as e:
            log_error(f'Error streaming coins for {email}', e)
            continue

        fixes = 0
        for doc in docs:
            d = doc.to_dict()
            doc_id = doc.id
            curr_obv = d.get('image_url_obverse', '') or ''

            # Only fix coins where obverse is our reference library URL (not user-specific)
            if not curr_obv.startswith(ref_prefix + ATB_PREFIX):
                continue

            # Get year from the existing reference URL
            yr_m = re.search(r'/(20\d{2})-america', curr_obv)
            if not yr_m:
                continue
            yr = yr_m.group(1)

            if yr not in year_to_obverse_path:
                continue

            obv_gcs_path = year_to_obverse_path[yr]
            user_path = f'users/{email}/coins/{doc_id}/obverse.jpg'
            user_url = PUBLIC_URL_BASE.format(bucket=UPL_BUCKET, path=user_path)

            if dry_run:
                print(f'    [DRY-RUN] Would copy {obv_gcs_path} to {user_path}')
                patch_log['user_obverse_copies_fixed'].append({
                    'doc_id': doc_id, 'email': email, 'year': yr,
                    'src_path': obv_gcs_path, 'dest_path': user_path, 'status': 'dry_run'
                })
                fixes += 1
                continue

            try:
                ref_blob = ref_bucket_obj.blob(obv_gcs_path)
                upl_blob = upl_bucket_obj.blob(user_path)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                    tmp_path = tmp.name
                ref_blob.download_to_filename(tmp_path)
                upl_blob.upload_from_filename(tmp_path, content_type='image/jpeg')
                # Set attribution on copied blob
                upl_blob.metadata = {
                    'attribution': ATTRIB['usmint']['attribution'],
                    'source':      ATTRIB['usmint']['source'],
                    'license':     ATTRIB['usmint']['license'],
                    'copyright':   ATTRIB['usmint']['copyright'],
                }
                upl_blob.patch()
                os.unlink(tmp_path)
                print(f'    [GCS] Copied to user path: {user_path}')

                # Update Firestore with user-specific URL + attribution fields
                db.collection('users').document(email).collection('coins').document(doc_id).update({
                    'image_url_obverse': user_url,
                    'image_source': 'gcs_usmint_official',
                    'image_source_obverse': ATTRIB['usmint']['source'],
                    'image_attribution': ATTRIB['usmint']['attribution'],
                    'image_license': ATTRIB['usmint']['license'],
                    'updated_at': firestore.SERVER_TIMESTAMP,
                })
                print(f'    [FS] Updated {doc_id} with user-specific URL')
                patch_log['user_obverse_copies_fixed'].append({
                    'doc_id': doc_id, 'email': email, 'year': yr,
                    'src_path': obv_gcs_path, 'dest_path': user_path,
                    'new_url': user_url, 'status': 'ok'
                })
                fixes += 1
            except Exception as e:
                log_error(f'Failed to fix obverse copy for {email}/{doc_id}', e)
                patch_log['user_obverse_copies_fixed'].append({
                    'doc_id': doc_id, 'email': email, 'year': yr,
                    'status': 'error', 'error': str(e)
                })

        print(f'    Fixed {fixes} obverse user copies')

    total = sum(1 for e in patch_log['user_obverse_copies_fixed'] if e.get('status') == 'ok')
    print(f'\n  Total obverse user copies fixed: {total}')


# ─── 3. Add attribution fields to Firestore coins already updated ─────────────
def patch_firestore_attribution(run_log, dry_run=False):
    print('\n' + '='*60)
    print('STEP 3: Adding attribution fields to updated Firestore coins')
    print('='*60)

    # Find coins that were updated in Task 3 but don't yet have attribution fields
    updated_entries = [e for e in run_log.get('task3_firestore_atb_updates', [])
                       if e.get('status') == 'updated']
    print(f'  Found {len(updated_entries)} coins to patch with attribution fields')

    attribution_updates = {
        'image_source_obverse': ATTRIB['usmint']['source'],
        'image_source_reverse': ATTRIB['usmint']['source'],
        'image_attribution': ATTRIB['usmint']['attribution'],
        'image_license': ATTRIB['usmint']['license'],
        'updated_at': firestore.SERVER_TIMESTAMP,
    }

    patched = 0
    errors = 0
    for entry in updated_entries:
        doc_id = entry['doc_id']
        email = entry['email']

        # Only add fields that weren't in the original update
        # Check if attribution already written (reload doc)
        if dry_run:
            print(f'  [DRY-RUN] Would patch attribution: {email}/{doc_id}')
            patch_log['firestore_attribution_updates'].append({
                'doc_id': doc_id, 'email': email, 'status': 'dry_run'
            })
            patched += 1
            continue

        try:
            # Check current doc to avoid overwriting if already set
            doc_ref = db.collection('users').document(email).collection('coins').document(doc_id)
            snap = doc_ref.get()
            if not snap.exists:
                continue
            current = snap.to_dict()
            if current.get('image_attribution'):
                # Already has attribution, just verify image_source fields
                update = {}
                if not current.get('image_source_obverse') and current.get('image_url_obverse'):
                    update['image_source_obverse'] = ATTRIB['usmint']['source']
                if not current.get('image_source_reverse') and current.get('image_url_reverse'):
                    update['image_source_reverse'] = ATTRIB['usmint']['source']
                if update:
                    doc_ref.update(update)
                continue

            doc_ref.update(attribution_updates)
            print(f'  [FS] Patched attribution: {email}/{doc_id}')
            patch_log['firestore_attribution_updates'].append({
                'doc_id': doc_id, 'email': email, 'status': 'ok'
            })
            patched += 1
        except Exception as e:
            log_error(f'Failed attribution patch for {email}/{doc_id}', e)
            patch_log['firestore_attribution_updates'].append({
                'doc_id': doc_id, 'email': email, 'status': 'error', 'error': str(e)
            })
            errors += 1

    print(f'\n  Firestore attribution patches: {patched} ok, {errors} errors')


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    if args.dry_run:
        print('[DRY-RUN MODE]\n')

    print(f'patch_atb_attribution.py — {datetime.now().isoformat()}')

    run_log = load_run_log()
    print(f'Loaded run log: {len(run_log.get("task1_atb_uploads", []))} ATB uploads, '
          f'{len(run_log.get("task3_firestore_atb_updates", []))} Firestore updates')

    patch_gcs_metadata(run_log, dry_run=args.dry_run)
    fix_obverse_user_copies(run_log, dry_run=args.dry_run)
    patch_firestore_attribution(run_log, dry_run=args.dry_run)

    print('\n' + '='*60)
    print('PATCH SUMMARY')
    print('='*60)
    print(f'  GCS blobs patched with metadata: {len(patch_log["gcs_metadata_patched"])}')
    print(f'  User obverse copies fixed:       {sum(1 for e in patch_log["user_obverse_copies_fixed"] if e.get("status") == "ok")}')
    print(f'  Firestore attribution updates:   {sum(1 for e in patch_log["firestore_attribution_updates"] if e.get("status") == "ok")}')
    print(f'  Errors: {len(patch_log["errors"])}')

    with open(PATCH_LOG, 'w', encoding='utf-8') as f:
        json.dump(patch_log, f, indent=2, ensure_ascii=False)
    print(f'\n[LOG] Saved to {PATCH_LOG}')
    print('\nDone.')


if __name__ == '__main__':
    main()
