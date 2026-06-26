import os
import json
import re
import google.auth
from google import genai
from google.genai import types as genai_types

# Configuration
PROJECT_ID = "studio-9101802118-8c9a8"
GEMINI_LOCATION = os.environ.get("GEMINI_LOCATION", "global")
PRIMARY_MODEL = "gemini-3.5-flash"
OUTPUT_JSON_PATH = "banknotes_expanded.json"

def normalize_denom(raw, default="One Dollar"):
    if not raw:
        return default
    s = str(raw).lower().strip()
    
    # 1. Handle dollar sign with numbers anywhere in the string
    match_ds = re.search(r"\$(\d+(?:\.\d+)?)", s)
    if match_ds:
        val_str = match_ds.group(1)
        val_map = {
            "0.01": "One Cent",
            "0.05": "Five Cents",
            "0.10": "One Dime",
            "0.1": "One Dime",
            "0.25": "Quarter Dollar",
            "0.50": "Half Dollar",
            "0.5": "Half Dollar",
            "1": "One Dollar",
            "2": "Two Dollars",
            "2.5": "Two and a Half Dollars",
            "3": "Three Dollars",
            "4": "Four Dollars",
            "5": "Five Dollars",
            "10": "Ten Dollars",
            "20": "Twenty Dollars",
            "25": "Twenty-Five Dollars",
            "50": "Fifty Dollars",
            "100": "One Hundred Dollars",
            "500": "Five Hundred Dollars",
            "1000": "One Thousand Dollars",
            "5000": "Five Thousand Dollars",
            "10000": "Ten Thousand Dollars",
            "100000": "One Hundred Thousand Dollars"
        }
        if val_str in val_map:
            return val_map[val_str]
            
    # 2. Check specific multi-digit or compound names first to avoid collision
    if "half cent" in s or "½ cent" in s or "1/2 cent" in s:
        return "Half Cent"
    if "quarter cent" in s or "1/4 cent" in s:
        return "Quarter Cent"
    if "two cent" in s or "2 cent" in s:
        return "Two Cents"
    if "three cent" in s or "3 cent" in s:
        return "Three Cents"
        
    # Check half dimes BEFORE dime and nickel!
    if "half dime" in s or "½ dime" in s or "1/2 dime" in s:
        return "Half Dime"
        
    if "five cent" in s or "5 cent" in s or "nickel" in s:
        return "Five Cents"
        
    # Check two and a half dollars/quarter eagles BEFORE half dollar/dollar!
    if "two and a half dollar" in s or "2.5 dollar" in s or "2-1/2 dollar" in s or "2½ dollar" in s or "quarter eagle" in s:
        return "Two and a Half Dollars"
        
    if "fifty cent" in s or "50 cent" in s or "half dollar" in s or "½ dollar" in s or "1/2 dollar" in s:
        return "Half Dollar"
    if "quarter dollar" in s or "¼ dollar" in s or "1/4 dollar" in s or "twenty-five cent" in s or "25 cent" in s or "quarter" in s:
        return "Quarter Dollar"
    if "twenty cent" in s or "20 cent" in s:
        return "Twenty Cents"
    if "one dime" in s or "1 dime" in s or "ten cent" in s or "10 cent" in s or "dime" in s:
        return "One Dime"
    if "one cent" in s or "1 cent" in s or "penny" in s or "pennies" in s or "cent" in s:
        return "One Cent"
        
    # 3. Check dollar coins (after checking half/quarter dollar/two and a half dollar)
    if "dollar" in s or "stella" in s or "double eagle" in s or "eagle" in s or "half eagle" in s or "gold clause" in s:
        if "double eagle" in s or "twenty dollar" in s or "20 dollar" in s:
            return "Twenty Dollars"
        if "half eagle" in s or "five dollar" in s or "5 dollar" in s:
            return "Five Dollars"
        if "eagle" in s or "ten dollar" in s or "10 dollar" in s:
            return "Ten Dollars"
        if "fifty dollar" in s or "50 dollar" in s:
            return "Fifty Dollars"
        if "hundred dollar" in s or "100 dollar" in s:
            return "One Hundred Dollars"
        if "five hundred dollar" in s or "500 dollar" in s:
            return "Five Hundred Dollars"
        if "thousand dollar" in s or "1000 dollar" in s:
            return "One Thousand Dollars"
        if "five thousand dollar" in s or "5000 dollar" in s:
            return "Five Thousand Dollars"
        if "ten thousand dollar" in s or "10000 dollar" in s:
            return "Ten Thousand Dollars"
        if "one hundred thousand dollar" in s or "100000 dollar" in s:
            return "One Hundred Thousand Dollars"
        if "two dollar" in s or "2 dollar" in s:
            return "Two Dollars"
        if "three dollar" in s or "3 dollar" in s:
            return "Three Dollars"
        if "four dollar" in s or "4 dollar" in s or "stella" in s:
            return "Four Dollars"
            
        return "One Dollar"
        
    if "medal" in s:
        return "Medal"
        
    return s.title()

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
                denom_val = normalize_denom(item.get("denomination", denom['name']))
                variety = str(item.get("variety", "")).strip()
                note = str(item.get("note", "")).strip()
                
                if not variety or "Fr." not in variety:
                    # Best effort prefixing if it forgot Fr.
                    if variety.isdigit():
                        variety = f"Fr. {variety}"
                    else:
                        # Skip if it is not a valid variety
                        continue

                entry = {
                    "year": year,
                    "denomination": denom_val,
                    "mint_mark": "",
                    "variety": variety,
                    "note": note,
                    "series": "US Banknotes"
                }

                # Check if it's a Federal Reserve Note (or Federal Reserve Bank Note)
                is_frn = "federal reserve note" in variety.lower() or "federal reserve note" in note.lower() or \
                         "federal reserve bank note" in variety.lower() or "federal reserve bank note" in note.lower()

                if is_frn:
                    match = re.search(r"Fr\.\s*(\d+)(?:-[A-L])?", variety, re.IGNORECASE)
                    if match:
                        base_num = match.group(1)
                        districts = {
                            'A': 'Boston', 'B': 'New York', 'C': 'Philadelphia', 'D': 'Cleveland',
                            'E': 'Richmond', 'F': 'Atlanta', 'G': 'Chicago', 'H': 'St. Louis',
                            'I': 'Minneapolis', 'J': 'Kansas City', 'K': 'Dallas', 'L': 'San Francisco'
                        }
                        for letter, name in districts.items():
                            new_entry = dict(entry)
                            old_fr = match.group(0)
                            new_fr = f"Fr. {base_num}-{letter}"
                            new_variety = variety.replace(old_fr, new_fr)
                            if name.lower() not in new_variety.lower():
                                new_variety = f"{new_variety} - {name} [{letter}]"
                            new_entry["variety"] = new_variety
                            new_entry["note"] = f"{note} Issued by the Federal Reserve Bank of {name} ({letter})."
                            valid_entries.append(new_entry)
                    else:
                        valid_entries.append(entry)
                else:
                    valid_entries.append(entry)
            
            print(f"  Valid and expanded entries: {len(valid_entries)}")
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
