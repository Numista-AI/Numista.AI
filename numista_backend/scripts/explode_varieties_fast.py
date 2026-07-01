
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

def fetch_issues(type_id):
    url = f"{NUMISTA_API_BASE}/types/{type_id}/issues"
    headers = {
        'Numista-API-Key': NUMISTA_API_KEY,
        'Accept': 'application/json'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"Error fetching issues for {type_id}: {e}")
    return []

def explode_varieties():
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    
    # Get all banknotes and medals - LIMIT 100 for fast test
    print("Fetching 100 items for variety expansion...")
    cur.execute("SELECT id, doc_id, variety, category FROM definitive_reference WHERE category IN ('banknote', 'medal') LIMIT 100")
    base_items = cur.fetchall()
    
    added_count = 0
    
    for db_id, doc_id, variety, category in base_items:
        numista_id = doc_id.split('_')[-1]
        if not numista_id.isdigit(): continue
        
        print(f"  Expanding {doc_id} ({variety})...")
        issues = fetch_issues(numista_id)
        
        seen_refs = set()
        
        for issue in issues:
            ref_num = None
            for ref in issue.get('references', []):
                code = ref.get('catalogue', {}).get('code', '')
                if code in ['Fr US', 'P', 'KM', 'C']:
                    ref_num = f"{code} {ref.get('number')}"
                    break
            
            if ref_num and ref_num not in seen_refs:
                seen_refs.add(ref_num)
                new_doc_id = f"{doc_id}_{ref_num.replace(' ', '_')}"
                
                cur.execute("SELECT id FROM definitive_reference WHERE doc_id = ?", (new_doc_id,))
                if cur.fetchone(): continue
                
                new_variety = f"{variety} ({ref_num})"
                cur.execute("""
                    INSERT INTO definitive_reference 
                    (year, denomination, variety, note, series, category, doc_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (issue.get('year'), None, new_variety, issue.get('comment', ''), "United States", category, new_doc_id))
                added_count += 1
                
        time.sleep(0.1)

    conn.commit()
    conn.close()
    print(f"--- Fast Expansion Complete. Added {added_count} varieties. ---")

if __name__ == "__main__":
    explode_varieties()
