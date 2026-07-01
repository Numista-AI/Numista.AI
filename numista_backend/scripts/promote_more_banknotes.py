
import sqlite3
import json
from pathlib import Path

# Configuration
DB_PATH = Path('c:/Users/ericd/Documents/MyVertexProject/numista_backend/database/numista_coins.db')
JSON_PATH = Path('c:/Users/ericd/Documents/MyVertexProject/numista_backend/scratch/more_banknotes.json')

def promote_filtered():
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        items = json.load(f)
        
    added_count = 0
    skipped_count = 0
    
    for item in items:
        # Check issuer
        if item.get('issuer', {}).get('code') != 'etats-unis':
            continue
            
        doc_id = f"ref_banknote_{item['id']}"
        
        # Check if exists
        cur.execute("SELECT id FROM definitive_reference WHERE doc_id = ?", (doc_id,))
        if cur.fetchone():
            skipped_count += 1
            continue
            
        title = item.get('title', '')
        
        cur.execute("""
            INSERT INTO definitive_reference 
            (year, denomination, variety, note, series, category, doc_id, image_url_obverse, image_url_reverse)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item.get('min_year'),
            None,
            title,
            f"Sourced from Numista ID {item['id']}",
            "United States",
            "banknote",
            doc_id,
            item.get('obverse_thumbnail'),
            item.get('reverse_thumbnail')
        ))
        added_count += 1
        
    conn.commit()
    conn.close()
    print(f"--- Promoted {added_count} US Banknotes, skipped {skipped_count} ---")

if __name__ == "__main__":
    promote_filtered()
