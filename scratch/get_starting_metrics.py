import sqlite3
import firebase_admin
from firebase_admin import credentials, firestore
import os

DB_PATH = r"c:\Users\ericd\Documents\MyVertexProject\numista_backend\database\numista_coins.db"
KEY_PATH = r"c:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json.json"

def main():
    print("=== Starting Point Metrics ===")
    
    # 1. SQLite Coins Reference Table
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Check total rows
        cur.execute("SELECT COUNT(*) FROM definitive_reference")
        total_ref = cur.fetchone()[0]
        
        # Check columns
        cur.execute("PRAGMA table_info(definitive_reference)")
        cols = [r[1] for r in cur.fetchall()]
        
        has_images = "image_url_obverse" in cols
        obv_count = 0
        if has_images:
            cur.execute("SELECT COUNT(*) FROM definitive_reference WHERE image_url_obverse IS NOT NULL AND image_url_obverse != ''")
            obv_count = cur.fetchone()[0]
            
        print(f"SQLite definitive_reference (US Numismatic Database):")
        print(f"  - Total records: {total_ref}")
        if has_images:
            print(f"  - Records with obverse images: {obv_count}")
            print(f"  - Records missing obverse images: {total_ref - obv_count}")
        else:
            print(f"  - Records with obverse images: 0 (schema lacks image columns)")
            print(f"  - Records missing obverse images: {total_ref}")
            
        # Break down by category
        cur.execute("SELECT category, COUNT(*) FROM definitive_reference GROUP BY category")
        for cat, cnt in cur.fetchall():
            print(f"    * {cat or 'unknown'}: {cnt}")
            
        conn.close()
    except Exception as e:
        print(f"SQLite Error: {e}")

    # 2. Firestore Mint Errors
    try:
        if os.path.exists(KEY_PATH):
            if not firebase_admin._apps:
                firebase_admin.initialize_app(credentials.Certificate(KEY_PATH))
            db = firestore.client()
            
            errors = list(db.collection("mint_errors").stream())
            total_errors = len(errors)
            with_images = 0
            with_desc = 0
            
            for doc in errors:
                d = doc.to_dict()
                images = d.get("images", [])
                has_img = False
                for img in images:
                    if img.get("url"):
                        has_img = True
                        break
                if has_img:
                    with_images += 1
                if d.get("description"):
                    with_desc += 1
                    
            print(f"\nFirestore mint_errors (US Mint Error Database):")
            print(f"  - Total records: {total_errors}")
            print(f"  - Records with detailed descriptions: {with_desc}")
            print(f"  - Records with images: {with_images}")
            print(f"  - Records missing images/renderings: {total_errors - with_images}")
        else:
            print("\nFirestore: Credentials not found at serviceAccountKey.json.json")
    except Exception as e:
        print(f"Firestore Error: {e}")

if __name__ == "__main__":
    main()
