"""
prepare_search_data.py
Converts master_coin_programs.json into JSONL format for Vertex AI Search.
Explodes each coin entry into its own document (1,913+ records) for
fine-grained search (e.g., "1921 Morgan Dollar CC" finds the exact coin).

Run once (or whenever the reference library updates):
  python vertex_search/prepare_search_data.py
"""

import json, os, re, sys, base64

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from google.cloud import storage

PROJECT_ID  = "studio-9101802118-8c9a8"
BUCKET_NAME = "numista-uploads-studio-9101802118-8c9a8"
GCS_DEST    = "vertex-search/coin_programs.jsonl"
SOURCE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "master_coin_programs.json")


def sanitize_id(raw: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", str(raw))[:63] or "doc"


def coin_to_doc(program: dict, coin: dict, idx: int) -> dict:
    prog_name   = program.get("name", "")
    prog_years  = program.get("years", "")
    prog_cat    = program.get("category", "")
    mint_desc   = program.get("mint_mark_description", "")
    mint_locs   = program.get("mint_mark_locations", "")

    coin_year   = str(coin.get("year", ""))
    coin_name   = str(coin.get("name", ""))
    coin_denom  = str(coin.get("denomination", coin_name))
    coin_notes  = str(coin.get("notes", coin.get("description", "")))
    coin_metal  = str(coin.get("metal", coin.get("composition", "")))
    coin_design = str(coin.get("design", coin.get("designer", "")))
    coin_img    = str(coin.get("image_url", ""))

    varieties = coin.get("varieties", [])
    mints_text = ", ".join(
        v.get("label", v.get("id", "")) for v in varieties
        if isinstance(v, dict)
    )

    # Build a rich human-readable content for semantic search
    content_parts = []
    if coin_year:   content_parts.append(coin_year)
    if coin_name:   content_parts.append(coin_name)
    if prog_name:   content_parts.append(prog_name)
    if prog_cat:    content_parts.append(prog_cat)
    if mints_text:  content_parts.append(f"Mint marks: {mints_text}")
    if coin_metal:  content_parts.append(f"Metal: {coin_metal}")
    if coin_design: content_parts.append(f"Designer: {coin_design}")
    if coin_notes:  content_parts.append(coin_notes)
    if mint_desc:   content_parts.append(mint_desc)
    content_text = " | ".join(p for p in content_parts if p.strip())

    doc_id = sanitize_id(f"{prog_cat}_{prog_name}_{coin_year}_{coin_name}_{idx}")

    return {
        "id": doc_id,
        "structData": {
            "program_name": prog_name,
            "program_years": prog_years,
            "category": prog_cat,
            "coin_year": coin_year,
            "coin_name": coin_name,
            "denomination": coin_denom,
            "mint_marks": mints_text,
            "metal": coin_metal,
            "designer": coin_design,
            "notes": coin_notes,
            "image_url": coin_img,
            "mint_info": mint_locs,
            "content": content_text,
        },
        "content": {
            "mimeType": "text/plain",
            "rawBytes": base64.b64encode(content_text.encode("utf-8")).decode("ascii"),
        },
    }


def program_to_doc(program: dict, idx: int) -> dict:
    """Fallback: index the program itself if it has no coins list."""
    name   = program.get("name", f"Program {idx}")
    years  = program.get("years", "")
    cat    = program.get("category", "")
    desc   = program.get("mint_mark_description", "")
    content = f"{name} {years} {cat} {desc}".strip()
    doc_id = sanitize_id(f"prog_{name}_{idx}")
    return {
        "id": doc_id,
        "structData": {
            "program_name": name,
            "program_years": years,
            "category": cat,
            "content": content,
        },
        "content": {
            "mimeType": "text/plain",
            "rawBytes": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        },
    }


def main():
    print(f"Loading {SOURCE_FILE}...")
    with open(SOURCE_FILE, encoding="utf-8") as f:
        programs = json.load(f)
    print(f"  {len(programs)} programs loaded")

    lines = []
    coin_count = 0
    for i, prog in enumerate(programs):
        coins = prog.get("coins", [])
        if coins:
            for j, coin in enumerate(coins):
                try:
                    doc = coin_to_doc(prog, coin, coin_count)
                    lines.append(json.dumps(doc, ensure_ascii=False))
                    coin_count += 1
                except Exception as e:
                    print(f"  Skipping coin {coin_count}: {e}")
        else:
            # Program with no coins — index program itself
            try:
                doc = program_to_doc(prog, i)
                lines.append(json.dumps(doc, ensure_ascii=False))
            except Exception as e:
                print(f"  Skipping program {i}: {e}")

    jsonl = "\n".join(lines)
    print(f"  {len(lines)} search documents -> {len(jsonl):,} bytes")

    local_out = os.path.join(os.path.dirname(__file__), "coin_programs.jsonl")
    with open(local_out, "w", encoding="utf-8") as f:
        f.write(jsonl)
    print(f"  Saved locally: {local_out}")

    print(f"Uploading to gs://{BUCKET_NAME}/{GCS_DEST}...")
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    blob   = bucket.blob(GCS_DEST)
    blob.upload_from_string(jsonl.encode("utf-8"), content_type="application/json")
    print(f"  Uploaded: gs://{BUCKET_NAME}/{GCS_DEST}")
    print(f"\nGCS URI: gs://{BUCKET_NAME}/{GCS_DEST}")


if __name__ == "__main__":
    main()
