import os
import sqlite3
import requests
from google.cloud import storage as gcs_storage
from google.oauth2 import service_account
import firebase_admin
from firebase_admin import credentials, firestore

# Load configuration settings
try:
    from .config import DB_PATH, KEY_PATH, BUCKET_NAME, GCP_PROJECT
except ImportError:
    DB_PATH = "database/numista_coins.db"
    KEY_PATH = "serviceAccountKey.json.json"
    BUCKET_NAME = "numista-uploads-studio-9101802118-8c9a8"
    GCP_PROJECT = "studio-9101802118-8c9a8"

# ─── Initialization ──────────────────────────────────────────────────────────

# Initialize Firebase Admin if not already initialized
try:
    firebase_admin.get_app()
except ValueError:
    if os.path.exists(KEY_PATH):
        firebase_admin.initialize_app(credentials.Certificate(str(KEY_PATH)))
    else:
        # Fallback to Application Default Credentials
        firebase_admin.initialize_app(options={"projectId": GCP_PROJECT})

db = firestore.client()

# Initialize Google Cloud Storage
if os.path.exists(KEY_PATH):
    sa_creds = service_account.Credentials.from_service_account_file(str(KEY_PATH))
    gcs_client = gcs_storage.Client(credentials=sa_creds, project=GCP_PROJECT)
else:
    gcs_client = gcs_storage.Client(project=GCP_PROJECT)
bucket = gcs_client.bucket(BUCKET_NAME)

# ─── Storage Operations ───────────────────────────────────────────────────────

def download_image(url):
    """
    Download raw image bytes from a URL.
    """
    if not url:
        return None
    try:
        # Use standard headers to avoid blocks
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 200 and len(resp.content) > 1000:
            return resp.content
    except Exception as e:
        print(f"    ⚠ Error downloading image from {url}: {e}")
    return None


def upload_to_gcs(img_bytes, gcs_path):
    """
    Upload raw image bytes to GCS bucket and make public.
    """
    try:
        blob = bucket.blob(gcs_path)
        # Determine content type (usually jpeg)
        content_type = "image/jpeg"
        if gcs_path.endswith(".png"):
            content_type = "image/png"
        elif gcs_path.endswith(".webp"):
            content_type = "image/webp"
            
        blob.upload_from_string(img_bytes, content_type=content_type)
        try:
            blob.make_public()
        except Exception:
            # Skip ACL settings if bucket has Uniform Bucket-Level Access enabled
            pass
        return blob.public_url
    except Exception as e:
        print(f"    ⚠ GCS upload error for path {gcs_path}: {e}")
    return None

# ─── Database Operations ───────────────────────────────────────────────────────

def ensure_sqlite_schema():
    """
    Ensure the definitive_reference table has image, pricing, and population columns.
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(definitive_reference);")
        cols = [r[1] for r in cur.fetchall()]
        
        # Add columns if missing
        if "image_url_obverse" not in cols:
            cur.execute("ALTER TABLE definitive_reference ADD COLUMN image_url_obverse TEXT;")
            print("    SQLite: Added column 'image_url_obverse' to definitive_reference.")
        if "image_url_reverse" not in cols:
            cur.execute("ALTER TABLE definitive_reference ADD COLUMN image_url_reverse TEXT;")
            print("    SQLite: Added column 'image_url_reverse' to definitive_reference.")
        if "price_guide" not in cols:
            cur.execute("ALTER TABLE definitive_reference ADD COLUMN price_guide TEXT;")
            print("    SQLite: Added column 'price_guide' to definitive_reference.")
        if "population_total" not in cols:
            cur.execute("ALTER TABLE definitive_reference ADD COLUMN population_total INTEGER;")
            print("    SQLite: Added column 'population_total' to definitive_reference.")
        if "apr_history" not in cols:
            cur.execute("ALTER TABLE definitive_reference ADD COLUMN apr_history TEXT;")
            print("    SQLite: Added column 'apr_history' to definitive_reference.")
            
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"    ⚠ SQLite schema alignment error: {e}")


def update_coin_images_in_databases(doc_id, obv_url, rev_url, row=None):
    """
    Update both SQLite definitive_reference and Firestore coins_reference
    with GCS image URLs and new pricing/census fields.
    """
    import json
    
    # Safe dictionary extracts
    price_guide_str = "{}"
    apr_history_str = "[]"
    pop_total = None
    
    if row and isinstance(row, dict):
        price_guide_str = json.dumps(row.get("price_guide") or {})
        apr_history_str = json.dumps(row.get("apr_history") or [])
        pop_total = row.get("population_total")
        
        # If pop_total is present but not an int, convert it
        if pop_total is not None:
            try:
                pop_total = int(pop_total)
            except (ValueError, TypeError):
                pop_total = None

    # 1. Update SQLite
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        cur.execute("""
            UPDATE definitive_reference
            SET image_url_obverse = ?, 
                image_url_reverse = ?,
                price_guide = ?,
                population_total = ?,
                apr_history = ?
            WHERE doc_id = ?
        """, (obv_url, rev_url, price_guide_str, pop_total, apr_history_str, doc_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"    ⚠ SQLite update error for {doc_id}: {e}")

    # 2. Update Firestore (coins_reference)
    try:
        col_ref = db.collection("coins_reference")
        doc_ref = col_ref.document(doc_id)
        if doc_ref.get().exists:
            update_data = {
                "image_url_obverse": obv_url,
                "image_url_reverse": rev_url,
            }
            if row and isinstance(row, dict):
                update_data["price_guide"] = row.get("price_guide") or {}
                update_data["population_total"] = pop_total
                update_data["apr_history"] = row.get("apr_history") or []
                
            doc_ref.update(update_data)
    except Exception as e:
        print(f"    ⚠ Firestore update error for coins_reference doc {doc_id}: {e}")



def update_mint_error_images_in_firestore(error_id, images_payload):
    """
    Update Firestore mint_errors collection with new images metadata payload.
    images_payload should be a list of image dicts matching the schema.
    """
    try:
        doc_ref = db.collection("mint_errors").document(error_id)
        if doc_ref.get().exists:
            # Fetch existing images to merge or update
            existing = doc_ref.get().to_dict().get("images", [])
            
            # Simple merge: replace existing or append new ones
            merged = []
            seen_sources = set()
            for img in images_payload + existing:
                src = img.get("source")
                if src not in seen_sources:
                    merged.append(img)
                    seen_sources.add(src)
            
            doc_ref.update({
                "images": merged
            })
            return True
    except Exception as e:
        print(f"    ⚠ Firestore update error for mint_errors doc {error_id}: {e}")
    return False
