#!/usr/bin/env python3
"""
audit_db_baseline.py
--------------------
Establishes the true, exact baseline of existing image mappings and physical files
across SQLite, Firestore active collections, and Google Cloud Storage.
"""

import os
import sys
import sqlite3
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage as gcs

# Ensure output encoding is UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Configuration
PROJECT_ID = "studio-9101802118-8c9a8"
KEY_PATH = Path(__file__).parent / "serviceAccountKey.json.json"
BUCKETS = ["studio-9101802118-8c9a8-uploads", "numista-uploads-studio-9101802118-8c9a8"]

# Initialize Firebase Admin
if not firebase_admin._apps:
    if KEY_PATH.exists():
        firebase_admin.initialize_app(credentials.Certificate(str(KEY_PATH)), {"projectId": PROJECT_ID})
    else:
        firebase_admin.initialize_app(options={"projectId": PROJECT_ID})
db = firestore.client()

# Initialize GCS Client
if KEY_PATH.exists():
    gcs_client = gcs.Client.from_service_account_json(str(KEY_PATH), project=PROJECT_ID)
else:
    gcs_client = gcs.Client(project=PROJECT_ID)


def audit_sqlite():
    print("\n=== SQLite Databases Audit ===")
    backend_dir = Path(__file__).parent
    dbs = [
        backend_dir / "database" / "numista.db",
        backend_dir / "database" / "numista_coins.db"
    ]
    
    for db_path in dbs:
        if not db_path.exists():
            print(f"  - Database not found: {db_path}")
            continue
            
        print(f"  - Database: {db_path.name}")
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        
        # Get tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        
        for table in tables:
            cur.execute(f"PRAGMA table_info({table})")
            cols = [col[1] for col in cur.fetchall()]
            
            # Find columns that might contain image URLs
            img_cols = [c for c in cols if any(x in c.lower() for x in ["image", "pic", "photo", "url"])]
            if not img_cols:
                continue
                
            print(f"    * Table '{table}': found potential image columns {img_cols}")
            for col in img_cols:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} IS NOT NULL AND {col} != ''")
                    count = cur.fetchone()[0]
                    print(f"      - Column '{col}': {count} populated rows")
                except Exception as ex:
                    print(f"      - Column '{col}': error querying ({ex})")
        conn.close()


def audit_firestore():
    print("\n=== Firestore Active Collections Audit ===")
    
    # 1. Audit global_programs
    try:
        gp_docs = db.collection("global_programs").stream()
        gp_count = 0
        gp_with_images = 0
        for doc in gp_docs:
            gp_count += 1
            data = doc.to_dict()
            if data.get("image_url_obverse") or data.get("image_url_reverse") or data.get("images"):
                gp_with_images += 1
        print(f"  - Collection 'global_programs': {gp_count} total docs, {gp_with_images} with image links")
    except Exception as e:
        print(f"  - Collection 'global_programs': error ({e})")
        
    # 2. Audit mint_errors
    try:
        me_docs = db.collection("mint_errors").stream()
        me_count = 0
        me_with_images = 0
        for doc in me_docs:
            me_count += 1
            data = doc.to_dict()
            images = data.get("images", [])
            has_img = False
            for img in images:
                if img.get("url"):
                    has_img = True
                    break
            if has_img:
                me_with_images += 1
        print(f"  - Collection 'mint_errors': {me_count} total docs, {me_with_images} with image links")
    except Exception as e:
        print(f"  - Collection 'mint_errors': error ({e})")

    # 3. Audit User Coins Subcollections (users/{user_email}/coins and users/{user_email}/currency)
    try:
        # Check users collections by list_documents or collection group query
        # Let's list the documents in the users collection first
        users_col = db.collection("users")
        user_docs = list(users_col.list_documents())
        print(f"  - Found {len(user_docs)} user account documents.")
        
        for u_doc in user_docs:
            email = u_doc.id
            # Audit coins subcollection
            coins_ref = users_col.document(email).collection("coins")
            coins = list(coins_ref.stream())
            coins_with_images = 0
            for c in coins:
                d = c.to_dict()
                if d.get("image_url_obverse") or d.get("image_url_reverse") or d.get("imageUrlObverse_gcs"):
                    coins_with_images += 1
            print(f"    * User '{email}' -> 'coins': {len(coins)} total docs, {coins_with_images} with image links")
            
            # Audit currency subcollection
            curr_ref = users_col.document(email).collection("currency")
            curr = list(curr_ref.stream())
            curr_with_images = 0
            for cr in curr:
                d = cr.to_dict()
                if d.get("image_url_obverse") or d.get("image_url_reverse") or d.get("imageUrlObverse_gcs"):
                    curr_with_images += 1
            print(f"    * User '{email}' -> 'currency': {len(curr)} total docs, {curr_with_images} with image links")
            
    except Exception as e:
        print(f"  - Collection group audit error: {e}")


def audit_gcs():
    print("\n=== Google Cloud Storage Audit ===")
    for b_name in BUCKETS:
        try:
            bucket = gcs_client.bucket(b_name)
            if not bucket.exists():
                print(f"  - Bucket {b_name} does not exist.")
                continue
                
            print(f"  - Listing Bucket: {b_name}")
            
            # Count blobs in reference_library/
            ref_blobs = list(gcs_client.list_blobs(bucket, prefix="reference_library/"))
            # Count blobs in users/
            user_blobs = list(gcs_client.list_blobs(bucket, prefix="users/"))
            # Count blobs in error_library_illustrations/ or similar
            err_blobs = list(gcs_client.list_blobs(bucket, prefix="error_library_illustrations/"))
            
            total_blobs = len(ref_blobs) + len(user_blobs) + len(err_blobs)
            print(f"    * Total files under 'reference_library/': {len(ref_blobs)}")
            print(f"    * Total files under 'users/': {len(user_blobs)}")
            print(f"    * Total files under 'error_library_illustrations/': {len(err_blobs)}")
            print(f"    * Total tracked images in bucket: {total_blobs}")
            
        except Exception as e:
            print(f"  - Bucket {b_name} error listing: {e}")


if __name__ == "__main__":
    audit_sqlite()
    audit_firestore()
    audit_gcs()
