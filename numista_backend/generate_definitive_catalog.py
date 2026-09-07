import os
import json
import sqlite3
import re
import google.auth
from google import genai
from google.genai import types as genai_types
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
PROJECT_ID = "studio-9101802118-8c9a8"
GEMINI_LOCATION = os.environ.get("GEMINI_LOCATION", "global")
PRIMARY_MODEL = "gemini-3.8-flash"
DB_PATH = os.path.join("database", "numista_coins.db")
MASTER_JSON_PATH = "master_coin_programs.json"
OUTPUT_JSON_PATH = "definitive_catalog_full.json"

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


def process_single_batch(genai_client, program_name, category, baseline_mints_by_year, batch, idx, total_batches):
    print(f"    [Start] Program: {program_name} | Batch {idx+1}/{total_batches}: {batch['name']}")
    
    has_designs = any("design" in c for c in batch['coins'])
    if has_designs:
        prompt = f"""You are a senior numismatic cataloger compiling the definitive United States coin variety database.
Your task is to expand the baseline list of active years, designs, and mint marks of the '{program_name}' series into a complete catalog of all standard issues and major Red Book die varieties.

Here is the baseline list of active years, designs, and mint marks for the current batch:
{json.dumps(batch['coins'], indent=2)}

For each entry in the baseline list and each mint mark listed in its "mints" array, you must generate:
1. The standard issue (regular strike) coin. For this standard coin:
   - The variety field MUST be the design name from the baseline list (e.g., "Delaware", "Yosemite", "Maya Angelou").
   - Do not use empty string variety for these standard issues—always set it to the design name.
2. All major Red Book die varieties (e.g., overdates, over mintmarks, major doubled dies, or design transitions) for that coin.
   Example variety names: "Doubled Die Obverse" (DDO), "Reverse of 1938", etc.
   If there are no major varieties, do not invent them—just output the standard strike.

Special Mappings:
- 2026 Semiquincentennial (250th Anniversary) Coins: Circulating coins (Jefferson Nickel, Emerging Liberty Dime, Enduring Liberty Half Dollar) and standard American Innovation Dollars do NOT carry a privy mark; they carry only the dual date "1776 ~ 2026". The standard circulating 2026 Declaration of Independence Quarter is dual-dated and has a special circulating version featuring the "July 4th Privy Mark" on the obverse. Official numismatic collector or bullion products (such as American Eagle and Gold Buffalo coins) carry the "Liberty Bell 250 Privy Mark". The note must specify the dual date "1776 ~ 2026" and mention it commemorates the 250th Anniversary.

Your output MUST be a valid JSON array of objects. Each object must have these exact keys:
- "year": string (e.g. "1999")
- "denomination": string (e.g., "Quarter Dollar", "One Dollar")
- "mint_mark": string (e.g. "P", "D", "S", "W")
- "variety": string (the design/variety name)
- "note": string (description of the design, mintage details, identification features, or significance of this specific coin design)

Do not include any other fields. Ensure absolute historical accuracy. Do not wrap the JSON output in markdown ```json or ``` code blocks.
"""
    else:
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
- 2026 Semiquincentennial (250th Anniversary) Coins: Circulating coins (Jefferson Nickel, Emerging Liberty Dime, Enduring Liberty Half Dollar) and standard American Innovation Dollars do NOT carry a privy mark; they carry only the dual date "1776 ~ 2026". The standard circulating 2026 Declaration of Independence Quarter is dual-dated and has a special circulating version featuring the "July 4th Privy Mark" on the obverse. Official numismatic collector or bullion products (such as American Eagle and Gold Buffalo coins) carry the "Liberty Bell 250 Privy Mark". The note must specify the dual date "1776 ~ 2026" and mention it commemorates the 250th Anniversary.

Your output MUST be a valid JSON array of objects. Each object must have these exact keys:
- "year": string (e.g. "1878")
- "denomination": string (e.g., "One Cent", "Five Cents", "One Dime", "Quarter Dollar", "Half Dollar", "One Dollar")
- "mint_mark": string (e.g. "P", "D", "S", "O", "CC", "W")
- "variety": string (the specific variety name, or "" for the normal regular strike)
- "note": string (description of the variety, historical mintage details, identification features, or significance)

Do not include any other fields. Ensure absolute historical accuracy. Do not wrap the JSON output in markdown ```json or ``` code blocks.
"""

    batch_entries = []
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
            denom = normalize_denom(item.get("denomination", category))
            
            # Normalize mint mark
            if mint and "-" in mint:
                mint = mint.split("-")[0]
            if mint in ["None", "none", "P", "P-MINT", "P_MINT", "P-Privy", "P-PROOF"]:
                mint = "P"

            # Apply general baseline-existence guardrails
            is_valid, msg = is_valid_combination(year, mint, baseline_mints_by_year)
            if not is_valid:
                # Log but filter out
                print(f"      [GUARDRAIL REJECTED]: {program_name} {year}-{mint} {variety} -> {msg}")
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
                # 1. Bullion & collector products get "Liberty Bell 250 Privy Mark"
                is_bullion_collector = any(x in program_name.lower() or x in variety.lower() or x in note.lower() for x in ["american eagle", "american buffalo", "proof set", "uncirculated set", "silver eagle", "gold eagle"])
                
                # 2. Declaration of Independence Quarter has standard and special July 4th versions
                is_declaration_quarter = "declaration of independence" in variety.lower() or "declaration of independence" in program_name.lower() or "declaration of independence" in note.lower()
                
                # 3. Apply mappings
                if is_bullion_collector:
                    if not variety:
                        variety = "Liberty Bell 250 Privy Mark"
                    elif "Liberty Bell" not in variety:
                        variety = variety + " (Liberty Bell 250 Privy Mark)"
                elif is_declaration_quarter and ("july 4" in variety.lower() or "july 4" in note.lower()):
                    variety = "July 4th Privy Mark"
                    if "july 4" not in note.lower():
                        note = "Special circulating release featuring the July 4th privy mark. " + note
                else:
                    if "Liberty Bell 250 Privy Mark" in variety:
                        variety = variety.replace(" (Liberty Bell 250 Privy Mark)", "").replace("Liberty Bell 250 Privy Mark", "").strip()
                
                if "1776" not in note:
                    note = "Dual dated 1776 ~ 2026. Struck to commemorate the United States Semiquincentennial (250th Anniversary). " + note

            batch_entries.append({
                "year": year,
                "denomination": denom,
                "mint_mark": mint,
                "variety": variety,
                "note": note,
                "series": program_name
            })
            valid_batch_entries += 1
        
        print(f"    [Done] Program: {program_name} | Batch {idx+1}/{total_batches}: {batch['name']} | Valid entries: {valid_batch_entries} / {len(batch_results)}")
        
    except Exception as e:
        print(f"    [Error] Program: {program_name} | Batch {idx+1}/{total_batches}: {batch['name']} | ERROR: {e}")
        
    return batch_entries


def run_curation():
    print("="*60)
    print("  Numista.AI - Definitive Catalog Orchestrator (COA 3 - Parallel)")
    print("="*60)

    # 1. Load Master Programs
    print(f"Loading program details from: {MASTER_JSON_PATH}")
    with open(MASTER_JSON_PATH, "r", encoding="utf-8") as f:
        master_programs = json.load(f)

    # 2. Setup Gemini Client
    print(f"Initializing Vertex AI GenAI Client (Model: {PRIMARY_MODEL}, Location: {GEMINI_LOCATION})")
    credentials, _ = google.auth.default()
    genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=GEMINI_LOCATION)

    all_batch_tasks = []

    # Iterate through all programs to build the task list
    for program in master_programs:
        program_name = program.get("Name", "")
        category = program.get("Category", "")
        
        # Skip reference guides and proof packaging templates that aren't actual series
        if category in ["Reference", "Proof Sets"] or "Littleton" in program_name:
            continue

        # Determine if it's a multi-design program where designs are parsed from Coins list
        MULTI_DESIGN_SERIES = {
            "50 State Quarters",
            "America the Beautiful Quarters (National Parks)",
            "American Innovation $1 Coin Program",
            "American Women Quarters",
            "D.C. & U.S. Territories Quarters"
        }
        is_multi_design = program_name in MULTI_DESIGN_SERIES

        baseline_coins = []
        baseline_mints_by_year = {}

        if is_multi_design:
            for c in program.get("Coins", []):
                year = c.get("year", "").strip()
                name = c.get("name", "").strip()
                if not year or not name:
                    continue
                
                # Extract mints
                mints = []
                for v in c.get("varieties", []):
                    if isinstance(v, dict):
                        mints.append(v.get("id"))
                    elif isinstance(v, str):
                        mints.append(v)
                
                # Normalize mints
                mints_norm = []
                for m in mints:
                    if m and "-" in m:
                        m = m.split("-")[0]
                    if m in ["None", "none", "", None]:
                        m = "P"
                    if m not in mints_norm:
                        mints_norm.append(m)
                
                baseline_coins.append({
                    "year": year,
                    "design": name,
                    "mints": mints_norm
                })
                
                # Build baseline_mints_by_year for validation guardrails
                if year not in baseline_mints_by_year:
                    baseline_mints_by_year[year] = []
                for m in mints_norm:
                    if m not in baseline_mints_by_year[year]:
                        baseline_mints_by_year[year].append(m)
        else:
            year_to_mints = {}
            for c in program.get("Coins", []):
                year = c.get("year", "").strip()
                if not year:
                    continue
                
                # Handle hyphenated years with mint suffix, e.g., "1908-S" -> year "1908", mint "S"
                if "-" in year and not year.startswith("-"):
                    parts = year.split("-")
                    if parts[0].isdigit() and len(parts[1]) == 1:
                        year = parts[0]
                        mints = [parts[1]]
                    else:
                        mints = []
                        for v in c.get("varieties", []):
                            if isinstance(v, dict):
                                mints.append(v.get("id"))
                            elif isinstance(v, str):
                                mints.append(v)
                else:
                    mints = []
                    for v in c.get("varieties", []):
                        if isinstance(v, dict):
                            mints.append(v.get("id"))
                        elif isinstance(v, str):
                            mints.append(v)
                
                if year not in year_to_mints:
                    year_to_mints[year] = []
                for m in mints:
                    if m and "-" in m:
                        m = m.split("-")[0]
                    if m in ["None", "none", "", None]:
                        m = "P"
                    if m not in year_to_mints[year]:
                        year_to_mints[year].append(m)
            
            # Inject modern years (2024 and 2026) manually for circulating/bullion series if missing
            if category in ["Cent", "Nickel", "Dime", "Quarter", "Half Dollar", "Dollar", "Bullion"]:
                if "2024" not in year_to_mints:
                    year_to_mints["2024"] = ["P", "D", "S"]
                if "2026" not in year_to_mints:
                    year_to_mints["2026"] = ["P", "D", "S", "W"]
            
            baseline_mints_by_year = year_to_mints
            baseline_coins = [{"year": y, "mints": m} for y, m in sorted(year_to_mints.items())]

        if not baseline_coins:
            continue

        # Get batches
        batches = get_batches_for_program(program_name, baseline_coins)
        for idx, batch in enumerate(batches):
            all_batch_tasks.append({
                "program_name": program_name,
                "category": category,
                "baseline_mints_by_year": baseline_mints_by_year,
                "batch": batch,
                "idx": idx,
                "total_batches": len(batches)
            })

    print(f"\nCollected {len(all_batch_tasks)} total batches across all programs.")
    print("Processing batches in parallel via ThreadPoolExecutor (max_workers=6)...")

    all_catalog_entries = []

    # Process in parallel
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(
                process_single_batch,
                genai_client,
                task["program_name"],
                task["category"],
                task["baseline_mints_by_year"],
                task["batch"],
                task["idx"],
                task["total_batches"]
            ): task for task in all_batch_tasks
        }
        
        for future in as_completed(futures):
            batch_entries = future.result()
            all_catalog_entries.extend(batch_entries)

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
