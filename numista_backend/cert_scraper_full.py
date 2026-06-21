"""
cert_scraper_full.py  –  Full PMG/PCGS cert scraper
Works even without explicit cert numbers by using description-based search.

Since no cert numbers are stored, this script:
1. Identifies all graded docs (mentioning PMG or PCGS)
2. For PMG: tries to search pmgnotes.com by description keywords
3. For PCGS: tries pcgs.com banknote search
4. Downloads any images found
5. Uploads to Firebase Storage
6. Updates Firestore docs
7. Writes a full report

Requires: playwright MCP browser tools (called via subprocess/API)
"""
import os, sys, re, json, time, requests, io
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
KEY_PATH    = os.path.join(SCRIPT_DIR, "serviceAccountKey.json.json")
USER_EMAIL  = "jseaman1204@gmail.com"
COLLECTION  = f"users/{USER_EMAIL}/currency"
BUCKET_NAME = "numista-uploads-studio-9101802118-8c9a8"
REPORT_DIR  = r"C:\Users\ericd\.gemini\antigravity\brain\26eebf0f-3c8f-47c1-940b-b41df002779f"
REPORT_PATH = os.path.join(REPORT_DIR, "cert_scraper_results.md")

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", KEY_PATH)

# ── Firebase / Firestore ────────────────────────────────────────────────────
import firebase_admin
from firebase_admin import credentials, firestore as fs_admin
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(credentials.Certificate(KEY_PATH))
db = fs_admin.client()

# ── Google Cloud Storage ────────────────────────────────────────────────────
from google.cloud import storage as gcs_storage
from google.oauth2 import service_account

sa_creds = service_account.Credentials.from_service_account_file(KEY_PATH)
gcs_client = gcs_storage.Client(credentials=sa_creds, project="studio-9101802118-8c9a8")
bucket = gcs_client.bucket(BUCKET_NAME)

def upload_image_bytes(img_bytes: bytes, gcs_path: str, content_type="image/jpeg") -> str:
    """Upload bytes to GCS, make public, return HTTPS URL."""
    blob = bucket.blob(gcs_path)
    blob.upload_from_string(img_bytes, content_type=content_type)
    blob.make_public()
    return blob.public_url

def download_image(url: str, timeout=20) -> bytes | None:
    """Download an image URL and return bytes, or None on failure."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": url,
        }
        r = requests.get(url, headers=headers, timeout=timeout)
        if r.status_code == 200 and len(r.content) > 1000:
            return r.content
    except Exception as e:
        print(f"    ⚠ Download failed: {e}")
    return None

# ── Step 1: Pull all graded docs ────────────────────────────────────────────
print("="*70)
print("STEP 1: Querying Firestore for graded currency documents")
print("="*70)

raw_docs = list(db.collection(COLLECTION).stream())
print(f"  → {len(raw_docs)} total docs")

graded = []
for doc in raw_docs:
    d = doc.to_dict() or {}
    all_text = " ".join(str(v) for v in d.values() if v).lower()
    if "pmg" in all_text:
        graded.append({"doc_id": doc.id, "data": d, "service": "PMG"})
    elif "pcgs" in all_text:
        graded.append({"doc_id": doc.id, "data": d, "service": "PCGS"})

print(f"  → {len(graded)} graded docs found")
for g in graded:
    d = g["data"]
    print(f"    {g['service']:<5}  Ref#{d.get('Personal Ref #','?'):<5}  {d.get('Description','')[:70]}")

# Save graded list
with open(os.path.join(SCRIPT_DIR, "graded_docs.json"), "w", encoding="utf-8") as f:
    # Convert Firestore DatetimeWithNanoseconds to string
    def safe_serial(obj):
        try:
            return str(obj)
        except:
            return repr(obj)
    json.dump([{
        "doc_id": g["doc_id"],
        "service": g["service"],
        "data": {k: safe_serial(v) for k, v in g["data"].items()}
    } for g in graded], f, indent=2, ensure_ascii=False)
print(f"\n  → Saved graded_docs.json")

print(f"\nDone. Found {len(graded)} graded docs (no cert numbers stored — service labels only).")
print("See graded_docs.json for full list.")
