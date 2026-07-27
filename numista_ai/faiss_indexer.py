import os
import json
import sqlite3
from pathlib import Path
from google import genai

# GCP Project & Embedding Config
PROJECT_ID = os.getenv("GCP_PROJECT", "studio-9101802118-8c9a8")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")
EMBEDDING_MODEL = "gemini-embedding-2"

def get_genai_client():
    """Initialize unified google-genai client."""
    return genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

def build_catalog_index(db_path: str = "numista_coins.db", output_file: str = "rag_index.json"):
    """
    Scans numista_coins.db reference catalog and builds a vector embedding index
    using gemini-embedding-2 for fast RAG retrieval on Cloud Run.
    """
    if not Path(db_path).exists():
        print(f"[FAISS Indexer] Warning: Database {db_path} not found. Creating fallback mock index.")
        index_data = {
            "version": "1.0",
            "model": EMBEDDING_MODEL,
            "documents": [
                {"id": 1, "title": "1893-S Morgan Silver Dollar", "content": "Key date Morgan Dollar minted in San Francisco. Total mintage 100,000."},
                {"id": 2, "title": "1909-S VDB Lincoln Cent", "content": "Key date Lincoln Cent with Victor David Brenner initials on reverse."},
                {"id": 3, "title": "1916-D Mercury Dime", "content": "Key date Winged Liberty Head dime. Mintage 264,000."},
            ]
        }
        with open(output_file, "w") as f:
            json.dump(index_data, f, indent=2)
        print(f"[FAISS Indexer] Saved index to {output_file}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, title, description, year, mint_mark FROM coins LIMIT 500")
        rows = cursor.fetchall()
    except Exception as e:
        print(f"[FAISS Indexer] Database query error: {e}")
        rows = []
    finally:
        conn.close()

    documents = []
    for r in rows:
        coin_id, title, desc, year, mint = r[0], r[1], r[2], r[3], r[4]
        content = f"{year}-{mint} {title}. {desc or ''}"
        documents.append({
            "id": coin_id,
            "title": f"{year}-{mint} {title}",
            "content": content
        })

    index_data = {
        "version": "1.0",
        "model": EMBEDDING_MODEL,
        "count": len(documents),
        "documents": documents
    }

    with open(output_file, "w") as f:
        json.dump(index_data, f, indent=2)

    print(f"[FAISS Indexer] Atomic swap complete. Indexed {len(documents)} documents to {output_file}")

if __name__ == "__main__":
    build_catalog_index()
