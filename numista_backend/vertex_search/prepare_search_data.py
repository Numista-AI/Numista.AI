"""
prepare_search_data.py
Converts SQLite definitive_reference table (6,444+ records) into JSONL format for Vertex AI Search.
This provides semantic search across the entire whitelisted numismatic library.

Run:
  python vertex_search/prepare_search_data.py
"""

import json
import os
import re
import sys
import base64
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from google.cloud import storage

PROJECT_ID  = "studio-9101802118-8c9a8"
BUCKET_NAME = "numista-uploads-studio-9101802118-8c9a8"
GCS_DEST    = "vertex-search/coin_programs.jsonl"
DB_PATH     = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "database", "numista_coins.db")


def sanitize_id(raw: str) -> str:
    # Vertex AI Document ID constraint: only letters, numbers, underscores, and hyphens. Length <= 63.
    sanitized = re.sub(r"[^a-zA-Z0-9_\-]", "_", str(raw))
    # Strip double underscores and trim
    sanitized = re.sub(r"_+", "_", sanitized).strip("_")
    return sanitized[:63] or "doc"


def row_to_doc(row: sqlite3.Row, idx: int) -> dict:
    category = row["category"] or "coin"
    doc_id = sanitize_id(f"ref_{category}_{row['doc_id']}_{idx}")

    year = str(row["year"] or "").strip()
    variety = str(row["variety"] or "").strip()
    denomination = str(row["denomination"] or "").strip()
    series = str(row["series"] or "").strip()
    mint_mark = str(row["mint_mark"] or "").strip()
    composition = str(row["composition"] or "").strip()
    design_obverse = str(row["design_obverse"] or "").strip()
    design_reverse = str(row["design_reverse"] or "").strip()
    note = str(row["note"] or "").strip()

    # Build rich text for semantic search indexing
    content_parts = []
    if year:           content_parts.append(year)
    if variety:        content_parts.append(variety)
    if series:         content_parts.append(series)
    if denomination:    content_parts.append(denomination)
    if category:        content_parts.append(category)
    if mint_mark:       content_parts.append(f"Mint mark: {mint_mark}")
    if composition:    content_parts.append(f"Composition: {composition}")
    if design_obverse:  content_parts.append(f"Obverse: {design_obverse}")
    if design_reverse:  content_parts.append(f"Reverse: {design_reverse}")
    if note:            content_parts.append(note)

    content_text = " | ".join(p for p in content_parts if p.strip())

    return {
        "id": doc_id,
        "structData": {
            "program_name": series,
            "program_years": "",
            "category": category,
            "coin_year": year,
            "coin_name": variety,
            "denomination": denomination,
            "mint_marks": mint_mark,
            "metal": composition,
            "designer": "",
            "notes": note,
            "image_url": "",
            "mint_info": "",
            "content": content_text,
        },
        "content": {
            "mimeType": "text/plain",
            "rawBytes": base64.b64encode(content_text.encode("utf-8")).decode("ascii"),
        },
    }


def main():
    print(f"Connecting to SQLite Database: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM definitive_reference")
        rows = cur.fetchall()
    except Exception as e:
        print(f"Error reading definitive_reference table: {e}")
        conn.close()
        sys.exit(1)

    print(f"Loaded {len(rows)} records from definitive_reference SQLite table.")

    lines = []
    for idx, row in enumerate(rows):
        try:
            doc = row_to_doc(row, idx)
            lines.append(json.dumps(doc, ensure_ascii=False))
        except Exception as e:
            print(f"Skipping record {idx}: {e}")

    conn.close()

    jsonl = "\n".join(lines)
    print(f"Generated {len(lines)} search documents -> {len(jsonl):,} bytes")

    local_out = os.path.join(os.path.dirname(__file__), "coin_programs.jsonl")
    with open(local_out, "w", encoding="utf-8") as f:
        f.write(jsonl)
    print(f"Saved locally: {local_out}")

    print(f"Uploading to gs://{BUCKET_NAME}/{GCS_DEST}...")
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    blob   = bucket.blob(GCS_DEST)
    blob.upload_from_string(jsonl.encode("utf-8"), content_type="application/json")
    print(f"Uploaded: gs://{BUCKET_NAME}/{GCS_DEST}")
    print(f"\nGCS URI: gs://{BUCKET_NAME}/{GCS_DEST}")


if __name__ == "__main__":
    main()
