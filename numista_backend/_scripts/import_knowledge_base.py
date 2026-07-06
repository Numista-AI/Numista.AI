# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
import_knowledge_base.py
========================
One-shot importer that reads all structured coin JSON files and writes them
to Firestore  coins_reference/{coin_id}  in project studio-9101802118-8c9a8.

Run:
    python import_knowledge_base.py
    python import_knowledge_base.py --dry-run      # preview without writing
    python import_knowledge_base.py --clear-first  # wipe existing before import
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import google.auth
from google.cloud import firestore

# ??? CONFIG ????????????????????????????????????????????????????????????????????
PROJECT_ID   = "studio-9101802118-8c9a8"
COLLECTION   = "coins_reference"

# Paths to source JSON files (relative to this script's location)
SCRIPT_DIR   = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
TRAINING_DIR = PROJECT_ROOT / "training_output"
AI_STUDIO_DIR = Path(r"C:\Users\ericd\antigravity\Numista-US-Currency-Knowledge-Base")

SOURCE_FILES = [
    TRAINING_DIR / "50_state_quarters.json",
    TRAINING_DIR / "bicentennial_1976_series.json.txt",  # .txt but valid JSON
    TRAINING_DIR / "washington_quarter_1993_1998.json",
]

# ??? HELPERS ???????????????????????????????????????????????????????????????????

def normalize_50sq(raw: dict) -> dict:
    """Convert 50_state_quarters.json entry to coins_reference schema."""
    return {
        "coin_id":            raw.get("coin_id", ""),
        "series":             raw.get("series", ""),
        "year":               str(raw.get("years", raw.get("issue_year", ""))),
        "denomination":       "Quarter Dollar",
        "face_value":         0.25,
        "composition":        raw.get("composition", "Copper-Nickel Clad Copper"),
        "design_obverse":     raw.get("design_obverse", "George Washington"),
        "design_reverse":     raw.get("design_reverse", ""),
        "design_description": raw.get("design_description", ""),
        "mint_marks":         raw.get("mint_marks_available", ["P", "D", "S"]),
        "issue_year":         raw.get("issue_year", 0),
        "issue_order":        raw.get("issue_order", 0),
        "statehood_year":     raw.get("statehood_year", 0),
        "image_url_obverse":  "",   # will be filled by coin_image_pipeline.py
        "image_url_reverse":  "",
        "source":             "json_import_50sq",
        "imported_at":        datetime.now(timezone.utc).isoformat(),
    }


def normalize_generic(raw: dict, source_tag: str) -> dict:
    """Best-effort normalisation for other JSON formats."""
    coin_id = (
        raw.get("coin_id")
        or raw.get("id")
        or f"US-{source_tag}-{raw.get('year', 'UNK')}-{raw.get('mint', 'P')}"
    )
    return {
        "coin_id":            coin_id,
        "series":             raw.get("series", raw.get("program", "")),
        "year":               str(raw.get("year", raw.get("years", raw.get("date", "")))),
        "denomination":       raw.get("denomination", ""),
        "face_value":         float(raw.get("face_value", 0)),
        "composition":        raw.get("composition", raw.get("metal", "")),
        "design_obverse":     raw.get("design_obverse", raw.get("obverse", "")),
        "design_reverse":     raw.get("design_reverse", raw.get("reverse", "")),
        "design_description": raw.get("design_description", raw.get("description", "")),
        "mint_marks":         raw.get("mint_marks_available", raw.get("mint_marks", [])),
        "image_url_obverse":  raw.get("image_url_obverse", raw.get("image_url", "")),
        "image_url_reverse":  raw.get("image_url_reverse", ""),
        "source":             f"json_import_{source_tag}",
        "imported_at":        datetime.now(timezone.utc).isoformat(),
    }


def load_ai_studio_data() -> list[dict]:
    """Try to load coin data from the AI Studio exported project."""
    results = []

    # The AI Studio project exports a TypeScript file like:
    # export const currencyDatabase: CurrencyItem[] = [ ... ];
    # We need to extract just the JSON array portion.
    for candidate in ["src/data.ts", "src/data.js", "src/currencyData.ts",
                      "src/currencyData.js", "src/coins.json"]:
        data_path = AI_STUDIO_DIR / candidate
        if data_path.exists():
            print(f"  Found AI Studio data at: {data_path}")
            try:
                text = data_path.read_text(encoding="utf-8")
                # Remove TypeScript type annotations and export statements
                # Strategy: find the first '[' and last ']' containing the array
                start = text.find('[')
                end   = text.rfind(']')
                if start != -1 and end != -1 and end > start:
                    json_str = text[start:end + 1]
                    # Remove TypeScript-specific syntax that breaks JSON parsing:
                    # - trailing commas before } or ]
                    import re as _re
                    json_str = _re.sub(r',\s*([}\]])', r'\1', json_str)
                    raw_list = json.loads(json_str)
                    if isinstance(raw_list, list):
                        for item in raw_list:
                            results.append(normalize_generic(item, "aistudio"))
                        print(f"  Loaded {len(results)} entries from AI Studio")
                        return results
            except Exception as e:
                print(f"  Warning: could not parse {data_path.name}: {e}")

    # Try plain JSON exports
    for candidate in ["public/data.json", "assets/coins.json", "data/coins.json"]:
        data_path = AI_STUDIO_DIR / candidate
        if data_path.exists():
            try:
                raw_list = json.loads(data_path.read_text(encoding="utf-8"))
                if isinstance(raw_list, list):
                    for item in raw_list:
                        results.append(normalize_generic(item, "aistudio"))
                    print(f"  Loaded {len(results)} entries from {data_path.name}")
                    return results
            except Exception as e:
                print(f"  Warning: {e}")

    print("  No AI Studio static data file found -- skipping AI Studio import")
    return results


def load_source_file(path: Path) -> list[dict]:
    """Load and normalise a single source JSON file."""
    if not path.exists():
        print(f"  SKIP (not found): {path.name}")
        return []

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  ERROR reading {path.name}: {e}")
        return []

    if not isinstance(raw, list):
        # Some files may be a dict at the top level
        if isinstance(raw, dict) and "coins" in raw:
            raw = raw["coins"]
        else:
            raw = [raw]

    tag = path.stem.replace("-", "_").replace(" ", "_")[:20]

    if "50_state" in path.stem:
        return [normalize_50sq(r) for r in raw]
    else:
        return [normalize_generic(r, tag) for r in raw]


# ??? MAIN ??????????????????????????????????????????????????????????????????????

def main():
    parser = argparse.ArgumentParser(description="Import coin knowledge base to Firestore")
    parser.add_argument("--dry-run",     action="store_true", help="Preview only, no writes")
    parser.add_argument("--clear-first", action="store_true", help="Delete existing coins_reference docs first")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  Numista.AI ? Knowledge Base Importer")
    print(f"  Project: {PROJECT_ID}  |  Collection: {COLLECTION}")
    print(f"  Mode: {'DRY RUN' if args.dry_run else 'LIVE WRITE'}")
    print(f"{'='*60}\n")

    # ?? 1. Collect all coins ???????????????????????????????????????????????????
    all_coins: list[dict] = []

    for src in SOURCE_FILES:
        print(f"Loading: {src.name}")
        coins = load_source_file(src)
        print(f"  -> {len(coins)} coins")
        all_coins.extend(coins)

    print(f"\nLoading: AI Studio Knowledge Base")
    ai_coins = load_ai_studio_data()
    all_coins.extend(ai_coins)

    # Deduplicate by coin_id (last-write wins)
    seen: dict[str, dict] = {}
    for c in all_coins:
        cid = c.get("coin_id", "")
        if cid:
            seen[cid] = c

    coins_to_write = list(seen.values())
    print(f"\nTotal unique coins to import: {len(coins_to_write)}")

    if not coins_to_write:
        print("Nothing to import. Exiting.")
        sys.exit(0)

    if args.dry_run:
        print("\n--- DRY RUN: First 5 entries ---")
        for c in coins_to_write[:5]:
            print(f"  {c['coin_id']:30s}  {c['series'][:30]:30s}  {c['year']}")
        print(f"\n[DRY RUN] Would write {len(coins_to_write)} documents to {COLLECTION}")
        return

    # ?? 2. Connect to Firestore ????????????????????????????????????????????????
    print("\nConnecting to Firestore...")
    try:
        credentials, _ = google.auth.default()
        db = firestore.Client(credentials=credentials, project=PROJECT_ID)
        print("  Connected ?")
    except Exception as e:
        print(f"  ERROR: {e}")
        sys.exit(1)

    # ?? 3. Optionally clear existing ???????????????????????????????????????????
    if args.clear_first:
        print(f"\nClearing existing {COLLECTION} documents...")
        coll_ref = db.collection(COLLECTION)
        deleted = 0
        for doc in coll_ref.stream():
            doc.reference.delete()
            deleted += 1
        print(f"  Deleted {deleted} documents")

    # ?? 4. Write in batches of 500 ????????????????????????????????????????????
    print(f"\nWriting {len(coins_to_write)} documents...")
    BATCH_SIZE = 400
    written = 0
    errors  = 0

    for i in range(0, len(coins_to_write), BATCH_SIZE):
        batch = db.batch()
        chunk = coins_to_write[i:i + BATCH_SIZE]
        for coin in chunk:
            doc_ref = db.collection(COLLECTION).document(coin["coin_id"])
            batch.set(doc_ref, coin, merge=True)
        try:
            batch.commit()
            written += len(chunk)
            print(f"  Batch {i // BATCH_SIZE + 1}: wrote {len(chunk)} docs  (total: {written})")
        except Exception as e:
            print(f"  Batch ERROR: {e}")
            errors += len(chunk)

    print(f"\n{'='*60}")
    print(f"  Import complete!")
    print(f"  Written: {written}   Errors: {errors}")
    print(f"  Collection: {PROJECT_ID}/{COLLECTION}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
