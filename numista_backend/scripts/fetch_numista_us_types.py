import requests
import sqlite3
import sys

# Configuration
API_KEY = "ExpST6TaGRDXkcEt6QajYJ0Lj76JZ8oqBPPpWhe"
BASE_URL = "https://api.numista.com/v3"
DB_PATH = r"c:\Users\ericd\Documents\MyVertexProject\numista_backend\database\numista_coins.db"

def main():
    print("="*60)
    print("  Numista.AI - US Types Gap Analysis via Numista.com API")
    print("="*60)
    
    # 1. Connect to local SQLite DB and fetch existing core coin IDs (from coins table)
    print(f"Connecting to database at {DB_PATH}...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id FROM coins")
        existing_ids = {row[0] for row in cur.fetchall()}
        conn.close()
        print(f"  Found {len(existing_ids)} existing core coin IDs in 'coins' table.")
    except Exception as e:
        print(f"  Error reading local database: {e}")
        sys.exit(1)

    # 2. Query Numista API for US coin types
    url = f"{BASE_URL}/types"
    params = {
        "q": "United States",
        "count": 50,
        "lang": "en"
    }
    headers = {
        "Numista-API-Key": API_KEY,
        "Accept": "application/json"
    }
    
    print("\nQuerying Numista API for United States types...")
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        types = data.get("types", [])
        print(f"  Received {len(types)} types from Numista API search.")
    except Exception as e:
        print(f"  Error calling Numista API: {e}")
        sys.exit(1)

    # 3. Perform gap analysis
    missing = []
    for t in types:
        num_id = t.get("id")
        title = t.get("title")
        if num_id not in existing_ids:
            missing.append({"id": num_id, "title": title})

    print(f"\nGap Analysis Results:")
    print(f"  Total analyzed: {len(types)}")
    print(f"  Total missing in baseline 'coins' table: {len(missing)}")
    
    if missing:
        print("\nFirst 10 missing types:")
        for i, item in enumerate(missing[:10]):
            print(f"  {i+1}. ID: {item['id']} | Title: {item['title']}")
    else:
        print("  All fetched types from the search query are already present in the baseline coins database!")

    print("\nGap analysis run completed successfully.")

if __name__ == "__main__":
    main()
