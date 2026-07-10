import sqlite3
import firebase_admin
from firebase_admin import credentials, firestore
import os
from pathlib import Path

# Config
DB_PATH = Path("database/numista_coins.db")
KEY_PATH = Path("serviceAccountKey.json.json")

# Initialize Firebase
if KEY_PATH.exists():
    cred = credentials.Certificate(str(KEY_PATH))
    firebase_admin.initialize_app(cred)
else:
    # Fallback to ADC
    firebase_admin.initialize_app()

db = firestore.client()
col_ref = db.collection("definitive_reference")

def sync_to_firestore():
    print(f"Connecting to SQLite: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM definitive_reference")
    rows = cur.fetchall()
    print(f"Found {len(rows)} local records. Starting upload to Firestore...")

    # Wipe collection to avoid stale grouped _none entries
    print("Wiping existing documents in 'definitive_reference' collection...")
    deleted_count = 0
    try:
        doc_refs = list(col_ref.list_documents())
        print(f"  Found {len(doc_refs)} existing reference documents to delete.")
        batch = db.batch()
        for doc_ref in doc_refs:
            batch.delete(doc_ref)
            deleted_count += 1
            if deleted_count % 400 == 0:
                batch.commit()
                batch = db.batch()
                print(f"  Deleted {deleted_count} documents from Firestore...")
        if deleted_count % 400 != 0:
            batch.commit()
        print(f"  Wipe complete. Total deleted: {deleted_count} documents.")
    except Exception as wipe_e:
        print(f"  WARNING: Error during Firestore wipe (continuing anyway): {wipe_e}")
    
    batch = db.batch()
    count = 0
    total = 0
    
    for row in rows:
        data = dict(row)
        doc_id = data.get("doc_id")
        if not doc_id:
            continue
            
        doc_ref = col_ref.document(doc_id)
        batch.set(doc_ref, data)
        
        count += 1
        total += 1
        
        # Firestore batches are limited to 500 operations
        if count >= 400:
            batch.commit()
            print(f"  Uploaded {total} records...")
            batch = db.batch()
            count = 0
            
    # Final commit
    if count > 0:
        batch.commit()
        
    print(f"DONE! Successfully synced {total} records to Firestore 'definitive_reference'.")
    conn.close()

if __name__ == "__main__":
    sync_to_firestore()
