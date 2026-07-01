
import sys
from pathlib import Path
import sqlite3
import json

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from numista_scraper.scrapers import search_numista_api, scrape_numista_api
from numista_scraper.storage import db

DB_PATH = "c:/Users/ericd/Documents/MyVertexProject/numista_backend/database/numista_coins.db"

def add_aafes_pogs():
    print("Searching for AAFES POGs on Numista...")
    results = search_numista_api("AAFES")
    
    if not results:
        print("  - No AAFES results found on Numista API.")
        return

    print(f"  - Found {len(results)} potential items.")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    added_count = 0
    for coin in results:
        # We only want actual AAFES Pogs/Tokens
        title = coin.get("title", "").upper()
        if "AAFES" in title or "POG" in title:
            doc_id = f"ref_coin_type_{coin['id']}"
            
            # Check if already exists
            cur.execute("SELECT doc_id FROM definitive_reference WHERE doc_id = ?", (doc_id,))
            if cur.fetchone():
                continue
                
            print(f"  + Fetching details for: {coin['title']} (ID: {coin['id']})")
            details = scrape_numista_api(coin['id'])
            if not details:
                continue

            # Insert into SQLite
            cur.execute("""
                INSERT INTO definitive_reference (doc_id, variety, category, series, image_url_obverse, image_url_reverse)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                doc_id,
                details.get("title"),
                "coin",
                "AAFES Pogs (Military)",
                details.get("obverse_url", ""),
                details.get("reverse_url", "")
            ))
            
            # Insert into Firestore
            db.collection("coins_reference").document(doc_id).set({
                "doc_id": doc_id,
                "variety": details.get("title"),
                "category": "coin",
                "series": "AAFES Pogs (Military)",
                "image_url_obverse": details.get("obverse_url", ""),
                "image_url_reverse": details.get("reverse_url", ""),
                "is_active": True
            })
            added_count += 1
            
    conn.commit()
    conn.close()
    print(f"Finished. Added {added_count} AAFES items.")

if __name__ == "__main__":
    add_aafes_pogs()
