
import sqlite3
import requests
import json
import os
import time
from pathlib import Path

# Configuration
NUMISTA_API_KEY = 'ExpST6TaGRDXkcEt6QajYJ0Lj76JZ8oqBPPpWhe'
NUMISTA_API_BASE = 'https://api.numista.com/v3'
DB_PATH = Path('c:/Users/ericd/Documents/MyVertexProject/numista_backend/database/numista_coins.db')

def search_numista(category):
    """Search Numista for US items in a specific category."""
    url = f"{NUMISTA_API_BASE}/types"
    params = {
        'q': '', 
        'issuer': 'etats-unis',
        'category': category
    }
    headers = {
        'Numista-API-Key': NUMISTA_API_KEY,
        'Accept': 'application/json',
        'User-Agent': 'NumistaAI/1.0 (eric@numista.ai)'
    }
    
    all_types = []
    page = 1
    while True:
        params['page'] = page
        print(f"  Querying {category} - Page {page}...")
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        if resp.status_code != 200:
            print(f"    Error {resp.status_code}: {resp.text}")
            break
        
        data = resp.json()
        types = data.get('types', [])
        if not types:
            break
            
        all_types.extend(types)
        page += 1
        if page > 20: # Safety break for now, but we might need more
            break
        time.sleep(0.5) # Rate limiting
        
    return all_types

def promote_to_reference(items, category_label):
    """Add items to the definitive_reference table."""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    
    added_count = 0
    skipped_count = 0
    
    for item in items:
        doc_id = f"ref_{category_label}_{item['id']}"
        
        # Check if exists
        cur.execute("SELECT id FROM definitive_reference WHERE doc_id = ?", (doc_id,))
        if cur.fetchone():
            skipped_count += 1
            continue
            
        # Basic promotion
        # Schema: year, denomination, variety, note, series, category, doc_id
        # We'll use the title as variety for now
        title = item.get('title', '')
        issuer_name = item.get('issuer', {}).get('name', 'United States')
        
        cur.execute("""
            INSERT INTO definitive_reference 
            (year, denomination, variety, note, series, category, doc_id, image_url_obverse, image_url_reverse)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            None, # Year (we'll leave null for base types)
            None, # Denomination (can extract from title)
            title,
            f"Sourced from Numista ID {item['id']}",
            issuer_name,
            category_label,
            doc_id,
            item.get('obverse_thumbnail'),
            item.get('reverse_thumbnail')
        ))
        added_count += 1
        
    conn.commit()
    conn.close()
    return added_count, skipped_count

if __name__ == "__main__":
    print("--- Starting Library Expansion ---")
    
    # 1. Expand Banknotes
    print("Expanding Banknotes...")
    banknotes = search_numista('banknote')
    added_bn, skipped_bn = promote_to_reference(banknotes, 'banknote')
    print(f"  Added {added_bn} new banknotes, skipped {skipped_bn} duplicates.")
    
    # 2. Expand Medals (Exonumia)
    print("Expanding Medals (Exonumia)...")
    medals = search_numista('exonumia')
    added_m, skipped_m = promote_to_reference(medals, 'medal')
    print(f"  Added {added_m} new medals, skipped {skipped_m} duplicates.")
    
    # 3. Final Count
    conn = sqlite3.connect(str(DB_PATH))
    total = conn.execute("SELECT COUNT(*) FROM definitive_reference").fetchone()[0]
    conn.close()
    
    print(f"--- Expansion Complete. Total Library Size: {total} ---")
