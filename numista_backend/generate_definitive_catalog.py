import os
import json
import sqlite3
import google.auth
from google import genai
from google.genai import types as genai_types

# Configuration
PROJECT_ID = "studio-9101802118-8c9a8"
GEMINI_LOCATION = os.environ.get("GEMINI_LOCATION", "global")
PRIMARY_MODEL = "gemini-3.5-flash"
DB_PATH = os.path.join("database", "numista_coins.db")
MASTER_JSON_PATH = "master_coin_programs.json"
OUTPUT_JSON_PATH = "definitive_catalog_full.json"

# Generalized validation guardrail matching historical baseline
def is_valid_combination(year, mint_mark, baseline_mints_by_year):
    try:
        int_year = int(year)
    except ValueError:
        return False, f"Invalid non-integer year '{year}'"

    # Always allow modern commemorative/anniversary years for standard mints
    if int_year in [2024, 2026]:
        if mint_mark in ["P", "D", "S", "W"]:
            return True, "Valid modern commemorative issue."

    # Check if year exists in baseline
    if year not in baseline_mints_by_year:
        return False, f"Year {year} is not active for this series."

    # Normalize and verify mint mark against baseline mints for this year
    valid_mints = baseline_mints_by_year[year]
    valid_mints_norm = []
    for vm in valid_mints:
        if vm and "-" in vm:
            vm = vm.split("-")[0]
        if vm in ["None", "none", "", None]:
            vm = "P"
        valid_mints_norm.append(vm)

    if mint_mark in valid_mints_norm:
        return True, "Valid baseline combination."
    else:
        return False, f"Mint '{mint_mark}' was not striking this coin in {year}. Valid: {valid_mints_norm}"


def get_batches_for_program(program_name, coins):
    # Sort coins by year to process chronologically
    sorted_coins = sorted(coins, key=lambda x: int(x["year"]) if x["year"].isdigit() else 0)
    
    # If less than or equal to 25 combinations, do it in a single batch
    if len(sorted_coins) <= 25:
        return [{"name": f"{program_name} (Full)", "coins": sorted_coins}]
    
    # Otherwise, chunk into batches of ~25 coins
    batches = []
    chunk_size = 25
    for i in range(0, len(sorted_coins), chunk_size):
        chunk = sorted_coins[i:i+chunk_size]
        start_year = chunk[0]["year"]
        end_year = chunk[-1]["year"]
        batches.append({"name": f"{program_name} ({start_year}-{end_year})", "coins": chunk})
    return batches


def run_curation():
    print("="*60)
    print("  Numista.AI - Definitive Catalog Orchestrator (COA 3 - Scaled)")
    print("="*60)

    # 1. Load Master Programs
    print(f"Loading program details from: {MASTER_JSON_PATH}")
    with open(MASTER_JSON_PATH, "r", encoding="utf-8") as f:
        master_programs = json.load(f)

    # 2. Setup Gemini Client
    print(f"Initializing Vertex AI GenAI Client (Model: {PRIMARY_MODEL}, Location: {GEMINI_LOCATION})")
    credentials, _ = google.auth.default()
    genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=GEMINI_LOCATION)

    all_catalog_entries = []

    # Iterate through all programs
    for program in master_programs:
        program_name = program.get("name", "")
        category = program.get("category", "")
        
        # Skip reference guides and proof packaging templates that aren't actual series
        if category in ["Reference", "Proof Sets"] or "Littleton" in program_name:
            print(f"\nSkipping program: {program_name} (Category: {category})")
            continue

        print(f"\nProcessing Program: {program_name} (Category: {category})")

        # Map baseline coins
        baseline_coins = []
        baseline_mints_by_year = {}
        
        for c in program.get("coins", []):
            year = c.get("year", "").strip()
            if not year:
                continue
            mints = [v.get("id") for v in c.get("varieties", [])]
            
            # Map for validation lookup
            baseline_mints_by_year[year] = mints
            baseline_coins.append({"year": year, "mints": mints})

        # Inject modern years (2024 and 2026) manually for circulating/bullion series if missing
        if category in ["Cent", "Nickel", "Dime", "Quarter", "Half Dollar", "Dollar", "Bullion"]:
            existing_years = set(baseline_mints_by_year.keys())
            
            if "2024" not in existing_years:
                baseline_coins.append({"year": "2024", "mints": ["P", "D", "S"]})
                baseline_mints_by_year["2024"] = ["P", "D", "S"]
            if "2026" not in existing_years:
                # Add P, D, S, W as base modern mint options
                baseline_coins.append({"year": "2026", "mints": ["P", "D", "S", "W"]})
                baseline_mints_by_year["2026"] = ["P", "D", "S", "W"]

        if not baseline_coins:
            print(f"  No valid coin entries found in program {program_name}. Skipping.")
            continue

        # Get batches
        batches = get_batches_for_program(program_name, baseline_coins)
        print(f"  Total baseline combinations: {len(baseline_coins)} -> Split into {len(batches)} batches.")

        for idx, batch in enumerate(batches):
            print(f"    Batch {idx+1}/{len(batches)}: {batch['name']}")
            
            prompt = f"""You are a senior numismatic cataloger compiling the definitive United States coin variety database.
Your task is to expand the baseline year/mint mark list of the '{program_name}' series into a complete catalog of all standard issues and major Red Book die varieties.

Here is the baseline list of active years and mint marks for the current batch:
{json.dumps(batch['coins'], indent=2)}

For each year and mint mark in the baseline, you must generate:
1. The standard issue (regular strike) coin. For this standard coin, the variety field should be "" (empty string).
2. All major Red Book die varieties (e.g., overdates, over mintmarks, major doubled dies, key design/reverse transitions, or privy mark variations).
   Example variety names: "Doubled Die Obverse" (DDO), "Reverse of 1938", "Wide AM", "Capped CC", "3 Legged", etc.
   If there are no major varieties for a year/mint combination, do not invent them—just output the standard strike with variety="".

Special Mappings:
- 2021 O and CC Morgan Dollars: If the program name is Morgan Dollars, variety MUST be "O Privy Mark" / "CC Privy Mark" and the note must describe them as Philadelphia strikes with privy marks.
- 2026 Semiquincentennial (250th Anniversary) Coins: The standard variety MUST be "Liberty Bell 250 Privy Mark" (or Proof/Reverse Proof/Enhanced Uncirculated equivalent). The note must specify the dual date "1776 ~ 2026" and mention it commemorates the 250th Anniversary.

Your output MUST be a valid JSON array of objects. Each object must have these exact keys:
- "year": string (e.g. "1878")
- "denomination": string (e.g., "One Cent", "Five Cents", "One Dime", "Quarter Dollar", "Half Dollar", "One Dollar")
- "mint_mark": string (e.g. "P", "D", "S", "O", "CC", "W")
- "variety": string (the specific variety name, or "" for the normal regular strike)
- "note": string (description of the variety, historical mintage details, identification features, or significance)

Do not include any other fields. Ensure absolute historical accuracy. Do not wrap the JSON output in markdown ```json or ``` code blocks.
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
                
                valid_batch_entries = 0
                for item in batch_results:
                    year = str(item.get("year", "")).strip()
                    mint = str(item.get("mint_mark", "")).strip()
                    variety = str(item.get("variety", "")).strip()
                    note = str(item.get("note", "")).strip()
                    denom = str(item.get("denomination", category)).strip()
                    
                    # Normalize mint mark
                    if mint and "-" in mint:
                        mint = mint.split("-")[0]
                    if mint in ["None", "none", "P", "P-MINT", "P_MINT", "P-Privy", "P-PROOF"]:
                        mint = "P"

                    # Apply general baseline-existence guardrails
                    is_valid, msg = is_valid_combination(year, mint, baseline_mints_by_year)
                    if not is_valid:
                        # Log but filter out
                        print(f"      [GUARDRAIL REJECTED]: {year}-{mint} {variety} -> {msg}")
                        continue

                    # Auto-corrections
                    int_year = int(year)
                    if int_year == 2021 and "Morgan" in program_name:
                        if mint == "O" and "Privy Mark" not in variety:
                            variety = "O Privy Mark"
                            note = "Struck at Philadelphia Mint with New Orleans Privy Mark. " + note
                        elif mint == "CC" and "Privy Mark" not in variety:
                            variety = "CC Privy Mark"
                            note = "Struck at Philadelphia Mint with Carson City Privy Mark. " + note
                    
                    if int_year == 2026:
                        if not variety:
                            variety = "Liberty Bell 250 Privy Mark"
                        elif "Privy Mark" not in variety:
                            variety = variety + " (Liberty Bell 250 Privy Mark)"
                        if "1776" not in note:
                            note = "Dual dated 1776 ~ 2026. Struck to commemorate the United States Semiquincentennial (250th Anniversary). " + note

                    all_catalog_entries.append({
                        "year": year,
                        "denomination": denom,
                        "mint_mark": mint,
                        "variety": variety,
                        "note": note,
                        "series": program_name
                    })
                    valid_batch_entries += 1
                
                print(f"      Valid entries: {valid_batch_entries} / {len(batch_results)}")
                
            except Exception as e:
                print(f"      ERROR processing batch: {e}")

    # Deduplicate entries
    seen = set()
    deduped_catalog = []
    for item in all_catalog_entries:
        key = (item["series"], item["year"], item["mint_mark"], item["variety"])
        if key not in seen:
            seen.add(key)
            deduped_catalog.append(item)

    print(f"\nFinal catalog compilation completed. Total coin entries: {len(deduped_catalog)}")

    # Write output to file
    print(f"Saving coin catalog to: {OUTPUT_JSON_PATH}")
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as out_f:
        json.dump(deduped_catalog, out_f, indent=2)

    print("Success. Run completed.")

if __name__ == "__main__":
    run_curation()
