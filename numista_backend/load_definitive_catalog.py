import os
import json
import sqlite3
import google.auth
from google import genai
from google.genai import types as genai_types
from firebase_admin import credentials, firestore, initialize_app, _apps

# Configuration
PROJECT_ID = "studio-9101802118-8c9a8"
GEMINI_LOCATION = os.environ.get("GEMINI_LOCATION", "global")
PRIMARY_MODEL = "gemini-3.5-flash"
DB_PATH = os.path.join("database", "numista_coins.db")
COINS_JSON = "definitive_catalog_full.json"
BANKNOTES_JSON = "banknotes_expanded.json"
KEY_PATH = "serviceAccountKey.json.json"

def get_medals_list(genai_client):
    print("\nGenerating definitive U.S. Medals list via Gemini...")
    prompt = """You are a senior numismatic expert specializing in U.S. Mint official medals.
Your task is to compile a catalog of the most famous, historically significant United States Mint medals, focusing on:
1. Congressional Gold Medals (e.g., George Washington, Winston Churchill, Tuskegee Airmen, etc.)
2. Presidential Medals (e.g., Thomas Jefferson, Abraham Lincoln, etc.)
3. Army/Navy/Military/Historical Commemorative Medals produced by the U.S. Mint.

Generate around 100-150 major entries.
For each medal, you must return a JSON object with these exact keys:
- "year": string (the year of authorization or issue, e.g. "1776", "1969")
- "denomination": string (always "Medal" to conform to database cleanliness rules)
- "mint_mark": string (always "")
- "variety": string (The recipient/event and medal type, e.g. "George Washington Congressional Gold Medal", "Winston Churchill / 1969")
- "note": string (Historical description of the recipient, why it was awarded, metal content of public versions, or U.S. Mint production details)
- "series": string (e.g., "Congressional Gold Medal", "Presidential Medal", "US Mint National Medal")

Your output MUST be a valid JSON array of objects. Do not wrap the JSON output in markdown ```json or ``` code blocks.
"""
    try:
        response = genai_client.models.generate_content(
            model=PRIMARY_MODEL,
            contents=[genai_types.Part.from_text(text=prompt)],
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0
            )
        )
        raw_text = response.text.strip()
        medals = json.loads(raw_text)
        print(f"  Successfully generated {len(medals)} medal entries.")
        return medals
    except Exception as e:
        print(f"  ERROR generating medals list: {e}")
        return []


def slugify(text):
    if not text:
        return "none"
    return "".join(c if c.isalnum() else "_" for c in text.lower()).strip("_")


def main():
    print("="*60)
    print("  Numista.AI - Definitive Catalog Consolidation & Loading")
    print("="*60)

    # 1. Load Coins
    coins = []
    if os.path.exists(COINS_JSON):
        print(f"Loading coins from {COINS_JSON}...")
        with open(COINS_JSON, "r", encoding="utf-8") as f:
            coins = json.load(f)
        print(f"  Loaded {len(coins)} coin entries.")
    else:
        print(f"  WARNING: {COINS_JSON} not found. Running coin catalog as empty.")

    # 2. Load Banknotes
    notes = []
    if os.path.exists(BANKNOTES_JSON):
        print(f"Loading banknotes from {BANKNOTES_JSON}...")
        with open(BANKNOTES_JSON, "r", encoding="utf-8") as f:
            notes = json.load(f)
        print(f"  Loaded {len(notes)} banknote entries.")
    else:
        print(f"  WARNING: {BANKNOTES_JSON} not found. Running banknote catalog as empty.")

    # 3. Setup Gemini & Generate Medals
    credentials_gcp, _ = google.auth.default()
    genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=GEMINI_LOCATION)
    medals = get_medals_list(genai_client)

    # 4. Consolidate Everything
    consolidated_catalog = []
    
    # Process Coins
    for c in coins:
        consolidated_catalog.append({
            "doc_id": f"ref_coin_{slugify(c.get('series'))}_{c.get('year')}_{slugify(c.get('mint_mark'))}_{slugify(c.get('variety'))}"[:100],
            "year": c.get("year", ""),
            "denomination": c.get("denomination", ""),
            "mint_mark": c.get("mint_mark", ""),
            "variety": c.get("variety", ""),
            "note": c.get("note", ""),
            "series": c.get("series", ""),
            "category": "coin"
        })

    # Process Notes
    for n in notes:
        consolidated_catalog.append({
            "doc_id": f"ref_note_{slugify(n.get('denomination'))}_{n.get('year')}_{slugify(n.get('variety'))}"[:100],
            "year": n.get("year", ""),
            "denomination": n.get("denomination", ""),
            "mint_mark": "",
            "variety": n.get("variety", ""),
            "note": n.get("note", ""),
            "series": "U.S. Banknotes",
            "category": "banknote"
        })

    # Process Medals
    for m in medals:
        consolidated_catalog.append({
            "doc_id": f"ref_medal_{slugify(m.get('series'))}_{m.get('year')}_{slugify(m.get('variety'))}"[:100],
            "year": m.get("year", ""),
            "denomination": m.get("denomination", "Medal"),
            "mint_mark": "",
            "variety": m.get("variety", ""),
            "note": m.get("note", ""),
            "series": m.get("series", "U.S. Medals"),
            "category": "medal"
        })

    print(f"\nConsolidated catalog size: {len(consolidated_catalog)} total entries.")

    # 5. Populate SQLite Local Cache (definitive_reference table)
    print(f"\nCaching in SQLite: {DB_PATH}")
    db_conn = sqlite3.connect(DB_PATH)
    db_cursor = db_conn.cursor()
    
    # Create Table
    db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS definitive_reference (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year TEXT,
            denomination TEXT,
            mint_mark TEXT,
            variety TEXT,
            note TEXT,
            series TEXT,
            category TEXT,
            doc_id TEXT UNIQUE
        );
    """)
    db_cursor.execute("CREATE INDEX IF NOT EXISTS idx_ref_lookup ON definitive_reference (year, mint_mark, category);")
    
    # Insert entries
    inserted_sqlite = 0
    for entry in consolidated_catalog:
        try:
            db_cursor.execute("""
                INSERT OR REPLACE INTO definitive_reference 
                (year, denomination, mint_mark, variety, note, series, category, doc_id) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                entry["year"],
                entry["denomination"],
                entry["mint_mark"],
                entry["variety"],
                entry["note"],
                entry["series"],
                entry["category"],
                entry["doc_id"]
            ))
            inserted_sqlite += 1
        except Exception as e:
            print(f"  SQLite Insert Error: {e}")
            
    db_conn.commit()
    db_conn.close()
    print(f"  Cached {inserted_sqlite} records in SQLite table 'definitive_reference'.")

    # 6. Upload to Firestore (coins_reference collection)
    print(f"\nUploading to Firestore collection 'coins_reference'...")
    if not _apps:
        cred = credentials.Certificate(KEY_PATH)
        initialize_app(cred)
    db = firestore.client()
    
    col_ref = db.collection("coins_reference")
    
    # Batch write in chunks of 400
    chunk_size = 400
    total_uploaded = 0
    
    for i in range(0, len(consolidated_catalog), chunk_size):
        chunk = consolidated_catalog[i:i+chunk_size]
        batch = db.batch()
        
        for entry in chunk:
            doc_ref = col_ref.document(entry["doc_id"])
            batch.set(doc_ref, {
                "year": entry["year"],
                "denomination": entry["denomination"],
                "mint_mark": entry["mint_mark"],
                "variety": entry["variety"],
                "note": entry["note"],
                "series": entry["series"],
                "category": entry["category"],
                "coin_id": entry["doc_id"] # backward compatibility
            })
            
        try:
            batch.commit()
            total_uploaded += len(chunk)
            print(f"  Uploaded batch: {total_uploaded} / {len(consolidated_catalog)} documents.")
        except Exception as fe:
            print(f"  Firestore upload error: {fe}")
            break

    print(f"\nLoading complete. Firestore count: {total_uploaded} documents loaded.")

if __name__ == "__main__":
    main()
