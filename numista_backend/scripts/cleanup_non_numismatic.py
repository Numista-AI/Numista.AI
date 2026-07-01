
import sqlite3
import firebase_admin
from firebase_admin import firestore
import os

# Configuration
DB_PATH = "c:/Users/ericd/Documents/MyVertexProject/numista_backend/database/numista_coins.db"
KEY_PATH = "c:/Users/ericd/Documents/MyVertexProject/numista_backend/serviceAccountKey.json.json"

# Series to remove completely (Non-US Mint/BEP)
SERIES_TO_REMOVE = [
    "Casino & Gaming Tokens",
    "School, Play & Institutional Tokens",
    "Novelty & Replica Play Money",
    "Merchant & Local Tokens",
    "Institutional & Prison Tokens",
    "Sales Tax Tokens"
]

# Initialize Firestore
if not firebase_admin._apps:
    cred = firebase_admin.credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def cleanup():
    print("Starting non-numismatic cleanup...")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. Identify doc_ids to remove from SERIES_TO_REMOVE
    placeholders = ', '.join(['?'] * len(SERIES_TO_REMOVE))
    cur.execute(f"SELECT doc_id, variety FROM definitive_reference WHERE series IN ({placeholders})", SERIES_TO_REMOVE)
    to_remove = cur.fetchall()
    
    # 2. Identify Colonial items to remove (EXCEPT Fugio)
    cur.execute("SELECT doc_id, variety FROM definitive_reference WHERE series = 'Pre-Federal & Colonial Coinage' AND variety NOT LIKE '%Fugio Cent%'")
    to_remove += cur.fetchall()

    # 3. Identify Civil War items to remove (EXCEPT official Battlefield commemoratives)
    cur.execute("SELECT doc_id, variety FROM definitive_reference WHERE series = 'Civil War Tokens' AND variety NOT LIKE '%Battlefield%'")
    to_remove += cur.fetchall()
    
    print(f"Found {len(to_remove)} items to purge.")
    
    # Batch delete from Firestore (limit 500 per batch)
    batch = db.batch()
    count = 0
    total_purged = 0
    
    for doc_id, variety in to_remove:
        # Delete from SQLite
        cur.execute("DELETE FROM definitive_reference WHERE doc_id = ?", (doc_id,))
        
        # Delete from Firestore
        doc_ref = db.collection("coins_reference").document(doc_id)
        batch.delete(doc_ref)
        
        count += 1
        total_purged += 1
        
        if count >= 400:
            batch.commit()
            print(f"  ...committed batch of {count} deletions to Firestore.")
            batch = db.batch()
            count = 0
            
    if count > 0:
        batch.commit()
        print(f"  ...committed final batch of {count} deletions to Firestore.")
        
    conn.commit()
    conn.close()
    
    print(f"✅ Cleanup complete. Total items purged: {total_purged}")

if __name__ == "__main__":
    cleanup()
