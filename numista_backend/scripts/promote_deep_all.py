
import sqlite3
import json
from pathlib import Path

# Configuration
DB_PATH = Path('c:/Users/ericd/Documents/MyVertexProject/numista_backend/database/numista_coins.db')

def promote_items(filename, category):
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    
    json_path = Path(f'c:/Users/ericd/Documents/MyVertexProject/numista_backend/scratch/{filename}')
    if not json_path.exists():
        print(f"File {filename} not found.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        items = json.load(f)
        
    added_count = 0
    skipped_count = 0
    
    for item in items:
        # doc_id for banknotes
        prefix = "ref_banknote" if category == "banknote" else "ref_medal"
        doc_id = f"{prefix}_{item['id']}"
        
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
            category,
            doc_id,
            item.get('obverse_thumbnail'),
            item.get('reverse_thumbnail')
        ))
        added_count += 1
        
    conn.commit()
    conn.close()
    print(f"--- Promoted {added_count} {category}s, skipped {skipped_count} ---")

if __name__ == "__main__":
    promote_items('all_us_banknotes_deep.json', 'banknote')
    promote_items('all_us_medals_deep.json', 'medal')
