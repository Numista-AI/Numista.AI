import os
import json
import google.auth
from google import genai
from google.genai import types as genai_types

# Configuration
PROJECT_ID = "studio-9101802118-8c9a8"
GEMINI_LOCATION = os.environ.get("GEMINI_LOCATION", "global")
PRIMARY_MODEL = "gemini-3.5-flash"
OUTPUT_JSON_PATH = "banknotes_expanded.json"

def run_banknotes_ingestion():
    print("="*60)
    print("  Numista.AI - Banknote Variety Cataloger (BEP Ingestion)")
    print("="*60)

    # Setup Gemini Client
    print(f"Initializing Vertex AI GenAI Client (Model: {PRIMARY_MODEL}, Location: {GEMINI_LOCATION})")
    credentials, _ = google.auth.default()
    genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=GEMINI_LOCATION)

    denominations = [
        {"name": "$1 Note", "prompt_tag": "$1 Notes"},
        {"name": "$2 Note", "prompt_tag": "$2 Notes"},
        {"name": "$5 Note", "prompt_tag": "$5 Notes"},
        {"name": "$10 Note", "prompt_tag": "$10 Notes"},
        {"name": "$20 Note", "prompt_tag": "$20 Notes"},
        {"name": "$50 Note", "prompt_tag": "$50 Notes"},
        {"name": "$100 Note", "prompt_tag": "$100 Notes"},
        {"name": "High Denominations", "prompt_tag": "High Denomination Notes ($500, $1,000, $5,000, $10,000, and $100,000 Gold Certificates)"}
    ]

    all_banknotes = []

    for denom in denominations:
        print(f"\nProcessing Banknotes: {denom['name']}")
        
        prompt = f"""You are a senior paper money cataloger specializing in United States federal paper currency (BEP issues).
Your task is to compile the definitive variety catalog of US federal paper currency for {denom['prompt_tag']}.

You must return a JSON array of objects, where each object represents a distinct variety cataloged by its official Friedberg (FR) Number.
Include all major series from large size notes (1861-1923) to small size notes (1928-present), covering:
- Demand Notes (1861)
- Legal Tender Notes (United States Notes)
- Silver Certificates
- Treasury or Coin Notes (1890-1891)
- Gold Certificates
- Federal Reserve Bank Notes
- Federal Reserve Notes

Each object in the JSON output must have these exact keys:
- "year": string (the Series Year of the note, e.g., "1899", "1917", "1923", "1928", "1934", "1957", "1996", "2013")
- "denomination": string (For standard issues, use exactly "{denom['name']}". For High Denominations, use the clean monetary string representing the note's face value, e.g. "$500 Note", "$1000 Note", "$5000 Note", "$10000 Note", "$100000 Note")
- "mint_mark": string (always "" since paper money does not have mint marks)
- "variety": string (MUST contain the Friedberg Number, e.g. "Fr. 237", "Fr. 140", and a short description of the signatures or seal, e.g. "Fr. 237 - Lyons/Treat Signatures - Red Seal")
- "note": string (description of the note, seal color, signatures, historical significance, obverse/reverse portraits, or BEP mintage details)

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
            batch_results = json.loads(raw_text)
            
            print(f"  Generated {len(batch_results)} raw banknote catalog entries.")
            
            # Basic validation
            valid_entries = []
            for item in batch_results:
                year = str(item.get("year", "")).strip()
                denom_val = str(item.get("denomination", denom['name'])).strip()
                variety = str(item.get("variety", "")).strip()
                note = str(item.get("note", "")).strip()
                
                if not variety or "Fr." not in variety:
                    # Best effort prefixing if it forgot Fr.
                    if variety.isdigit():
                        variety = f"Fr. {variety}"
                    else:
                        # Skip if it is not a valid variety
                        continue

                valid_entries.append({
                    "year": year,
                    "denomination": denom_val,
                    "mint_mark": "",
                    "variety": variety,
                    "note": note,
                    "series": "US Banknotes"
                })
            
            print(f"  Valid entries: {len(valid_entries)}")
            all_banknotes.extend(valid_entries)
            
        except Exception as e:
            print(f"  ERROR processing banknotes {denom['name']}: {e}")

    # Deduplicate
    seen = set()
    deduped_banknotes = []
    for item in all_banknotes:
        key = (item["denomination"], item["year"], item["variety"])
        if key not in seen:
            seen.add(key)
            deduped_banknotes.append(item)

    print(f"\nFinal catalog compilation completed. Total banknote entries: {len(deduped_banknotes)}")

    # Write output to file
    print(f"Saving banknote catalog to: {OUTPUT_JSON_PATH}")
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as out_f:
        json.dump(deduped_banknotes, out_f, indent=2)

    print("Success. Run completed.")

if __name__ == "__main__":
    run_banknotes_ingestion()
