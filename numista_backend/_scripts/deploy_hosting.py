# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
Deploy Flutter web build to Firebase Hosting via REST API.
Uses service account credentials (no browser auth needed).

Firebase Hosting REST API steps:
  1. Create a new version
  2. Populate files (get required upload hashes)
  3. Upload each required file
  4. Finalize the version (FINALIZED)
  5. Create a release (makes it live)
"""
import os, sys, json, hashlib, mimetypes, gzip, requests, base64
from pathlib import Path
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# ── Config ─────────────────────────────────────────────────────────────────
SA_KEY     = r'c:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json.json'
PROJECT_ID = 'studio-9101802118-8c9a8'
SITE_ID    = 'numista-vault'
BUILD_DIR  = Path(r'c:\Users\ericd\Documents\MyVertexProject\numista_mobile\build\web')
SCOPES     = ['https://www.googleapis.com/auth/cloud-platform',
              'https://www.googleapis.com/auth/firebase']

# ── Auth ────────────────────────────────────────────────────────────────────
print('Authenticating with service account...')
creds = service_account.Credentials.from_service_account_file(SA_KEY, scopes=SCOPES)
creds.refresh(Request())
headers = {'Authorization': f'Bearer {creds.token}', 'Content-Type': 'application/json'}
print(f'Token obtained (expires: {creds.expiry})')

BASE = 'https://firebasehosting.googleapis.com/v1beta1'

# ── Step 1: Create a new version ────────────────────────────────────────────
print(f'\n[1] Creating new hosting version for site: {SITE_ID}')
r = requests.post(f'{BASE}/sites/{SITE_ID}/versions',
    headers=headers,
    json={'config': {'rewrites': [{'glob': '**', 'path': '/index.html'}]}}
)
r.raise_for_status()
version_name = r.json()['name']
version_id   = version_name.split('/')[-1]
print(f'    Version: {version_id}')

# ── Step 2: Build file manifest (SHA256 hashes) ─────────────────────────────
print(f'\n[2] Scanning build directory: {BUILD_DIR}')
files = {}
file_data = {}

for path in BUILD_DIR.rglob('*'):
    if path.is_file():
        rel = '/' + path.relative_to(BUILD_DIR).as_posix()
        raw  = path.read_bytes()
        data = gzip.compress(raw, compresslevel=9)
        sha256 = hashlib.sha256(data).hexdigest()
        files[rel] = sha256
        file_data[sha256] = (rel, data, path)

print(f'    Found {len(files)} files')

# ── Step 3: Tell Firebase which files we have ────────────────────────────────
print(f'\n[3] Populating file manifest...')
r = requests.post(f'{BASE}/{version_name}:populateFiles',
    headers=headers,
    json={'files': files}
)
r.raise_for_status()
resp = r.json()
upload_url     = resp.get('uploadUrl', '')
required_hashes = resp.get('uploadRequiredHashes', [])
print(f'    Upload URL: {upload_url[:60]}...')
print(f'    Files to upload: {len(required_hashes)} (Firebase already has {len(files) - len(required_hashes)})')

# ── Step 4: Upload required files ───────────────────────────────────────────
if required_hashes:
    print(f'\n[4] Uploading {len(required_hashes)} files...')
    upload_headers = {'Authorization': f'Bearer {creds.token}'}
    for i, sha256 in enumerate(required_hashes):
        if sha256 not in file_data:
            print(f'    WARNING: hash {sha256[:16]} not found locally, skipping')
            continue
        rel, compressed, path = file_data[sha256]
        upload_headers_file = {**upload_headers, 'Content-Type': 'application/octet-stream'}
        r = requests.post(f'{upload_url}/{sha256}',
            headers=upload_headers_file,
            data=compressed
        )
        if r.status_code not in (200, 204):
            print(f'    ERROR uploading {rel}: {r.status_code} {r.text[:200]}')
        elif (i+1) % 10 == 0 or i < 5:
            print(f'    [{i+1}/{len(required_hashes)}] {rel} ({len(compressed):,} bytes)')
    print(f'    Upload complete.')
else:
    print(f'\n[4] No new files to upload (Firebase has all files cached).')

# ── Step 5: Finalize the version ─────────────────────────────────────────────
print(f'\n[5] Finalizing version...')
r = requests.patch(f'{BASE}/{version_name}?updateMask=status',
    headers=headers,
    json={'status': 'FINALIZED'}
)
r.raise_for_status()
print(f'    Status: {r.json()["status"]}')

# ── Step 6: Release (make live) ──────────────────────────────────────────────
print(f'\n[6] Creating release (making version live)...')
r = requests.post(f'{BASE}/sites/{SITE_ID}/releases?versionName={version_name}',
    headers=headers,
    json={'message': 'Numista.AI beta deploy via service account'}
)
r.raise_for_status()
release = r.json()
print(f'    Release: {release["name"]}')
print(f'\n✅ DEPLOYMENT COMPLETE')
print(f'   Live URL: https://{SITE_ID}.web.app')
print(f'   Also:     https://{SITE_ID}.firebaseapp.com')
