import os
import json
import sqlite3
import re
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

ALLOWED_COIN_SERIES = {
    # 31 Modern and Classic programs
    "2026 U.S. Circulating Coins",
    "50 State Quarters",
    "America the Beautiful Quarters (National Parks)",
    "American Innovation $1 Coin Program",
    "American Silver Eagles",
    "American Women Quarters",
    "Barber Dimes",
    "Barber Half Dollars",
    "Barber Quarters",
    "Buffalo Nickels",
    "D.C. & U.S. Territories Quarters",
    "Eisenhower Dollars",
    "Flying Eagle & Indian Head Cents",
    "Franklin Half Dollars",
    "Jefferson Nickels",
    "Kennedy Half Dollars",
    "Liberty Head (V) Nickels",
    "Liberty Walking Half Dollars",
    "Lincoln Bicentennial Cents (2009)",
    "Lincoln Cents",
    "Lincoln Memorial Cents",
    "Lincoln Shield Cents",
    "Lincoln Wheat Pennies",
    "Mercury Dimes",
    "Morgan Dollars",
    "Peace Dollars",
    "Presidential Dollars",
    "Roosevelt Dimes",
    "Sacagawea & Native American Dollars",
    "Susan B. Anthony Dollars",
    "Washington Quarters (Classic)",

    # Historical Design types and specific series
    "Flowing Hair Coinage",
    "Draped Bust Coinage",
    "Classic Head Coinage",
    "Capped Bust Coinage",
    "Seated Liberty Coinage",
    "Gobrecht Dollars",
    "Trade Dollars",
    "Coronet Head Coinage",
    "Liberty Head Coinage",
    "Saint-Gaudens Gold Coinage",
    "Early Commemorative Half Dollars",
    "Modern Commemorative Dollars",
    "U.S. Pattern Coinage",
    
    # Specific series
    "Standing Liberty Quarters",
    "Shield Nickels",
    "Shield Nickel",
    "Two Cents",
    "Three Cents (Nickel)",
    "Three Cents (Silver)",
    "Three Cent Nickels",
    "Half Dimes",
    "Half Dime",
    "Twenty Cents",
    "Half Cents",
    "Large Cents",
    "Liberty Cap Cents",
    "Liberty Cap Half Dimes",
    "Fractional Currency",
    "Postage Currency",
    "American Buffalo",
    "American Eagle",
    "American Gold Eagle",
    "American Silver Eagle",
    "American Platinum Eagle",
    "Double Eagle",
    "Double Eagles",
    "Quarter Eagle",
    "Quarter Eagles",
    "Half Eagle",
    "Half Eagles",
    "Eagle",
    "Eagles",
    "Stella",
    "Stellas",
    "Three Dollars",
    "Four Dollars",
    "Standing Liberty",
    "Mercury Dime",
    "Barber Quarter",
    "Barber Half Dollar",
    "Barber Dime",
    "Morgan Dollar",
    "Peace Dollar",
    "Sacagawea Dollar",
    "Eisenhower Dollar",
    "Susan B. Anthony Dollar",
    "Kennedy Half Dollar",
    "Franklin Half Dollar",
    "Walking Liberty Half Dollar",
    "Jefferson Nickel",
    "Buffalo Nickel",
    "Liberty Head V Nickel",
    "Roosevelt Dime",
    "Lincoln Cent",
    "Flying Eagle Cent",
    "Indian Head Cent",
    "Fugio Cent",
    
    # Newly added official series
    "First Spouse Gold Coins",
    "American Liberty Gold Coins",
    "American Palladium Eagles",
    "Jefferson Wartime Nickels",
    "Washington Silver Quarters",
    "Liberty Head/Braided Hair Cents",
    "Three Cents",
    "Trime",
    "Liberty Nickels",
    "Indian Head - Quarter Eagle",
    "Liberty Head / Matron Head",
    "Liberty Head / Matron Head Modified",
    "Metric Double Eagle / Quintuple Stella",
    "Large Indian Head",
    "Indian Princess Head",
    "Small Indian Head",
    "Braided Hair - Half Cents",
    "Liberty Cap",
    "Half Disme",
    "Capped Head - Quarter Eagle",
    "Indian Head",
    "Washington",
    "1/200 Dollar Liberty Cap, Head Facing Right, Half Cents",
    "American Liberty High Relief Gold",
    "1879 Quintuple Stella",
    "Half Eagle Restrike",
    "1878 Half Eagle",
    "Emerging Liberty Dimes",
    "Bess",
    "Lady Bird"
}

ALLOWED_MEDAL_SERIES = {
    "Congressional Gold Medal",
    "Presidential Medal",
    "US Mint National Medal",
    "U.S. Medals",
    "Official Medals",
    "US Mint Medals",
    "Congressional Gold Medals",
    "Presidential Medals",
    "US Mint National Medals"
}


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


def normalize_mint(raw):
    if not raw:
        return "P"
    s = str(raw).upper().strip()
    if s in ["NONE", "NULL", "P", "P-MINT", "P_MINT", ""]:
        return "P"
    return s

def extract_fr_number(variety):
    if not variety:
        return ""
    match = re.search(r"Fr\.\s*(\d+[a-zA-Z]?)", variety, re.IGNORECASE)
    if match:
        return f"fr. {match.group(1).lower()}"
    return variety.lower().strip()

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

    # Initialize Firebase Admin early to retrieve user collection records for self-healing
    print("Initializing Firebase Admin Client...")
    if not _apps:
        cred = credentials.Certificate(KEY_PATH)
        initialize_app(cred)
    db = firestore.client()

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

    # User-owned self-healing is disabled to prevent reference pollution in canonical master catalog
    user_coins = []
    user_notes = []

    # 4. Consolidate Everything
    consolidated_catalog = []

    # 4.0 Load the baseline 10,007 coins from the SQLite database
    baseline_coins_count = 0
    baseline_medals_count = 0
    baseline_rejected_count = 0
    
    print("\nLoading baseline coins from SQLite table 'coins'...")
    try:
        db_conn = sqlite3.connect(DB_PATH)
        db_conn.row_factory = sqlite3.Row
        db_cursor = db_conn.cursor()
        db_cursor.execute("SELECT id, title, issuer, value, composition, mintage, also_known_as, category FROM coins")
        baseline_rows = db_cursor.fetchall()
        db_conn.close()
        print(f"  Loaded {len(baseline_rows)} baseline coin rows.")

        # Load baseline series map
        baseline_map = {}
        map_path = "baseline_series_map.json"
        if os.path.exists(map_path):
            print(f"  Loading baseline series mapping from {map_path}...")
            with open(map_path, "r", encoding="utf-8") as f:
                baseline_map = json.load(f)
            print(f"    Loaded mapping for {len(baseline_map)} unique baseline titles.")
        else:
            print(f"    WARNING: {map_path} not found. Running baseline coins with default mapping.")

        REJECT_KEYWORDS = [
            "token", "privately struck", "private issue", "merchant", 
            "municipal", "exonumia", "wooden nickel", "poker chip", 
            "gaming", "replica", "copy", "novelty", "play money",
            "counterfeit", "souvenir medal", "fantasy issue", "reproduction"
        ]

        ACCEPT_MEDAL_KEYWORDS = [
            "congressional gold", 
            "presidential medal", 
            "us mint national", 
            "u.s. mint national",
            "official medal",
            "united states mint bicentennial",
            "u.s. centennial exposition (official medal)",
            "us centennial exposition (official medal)",
            "united states mint, philadelphia"
        ]

        def parse_denom_baseline(title):
            match = re.match(r"^([\d¼½¾⅓⅔⅛\s\-\/\u00bc\u00bd\u00be]+(?:Cent|Cents|Dollar|Dollars|Mill|Mills|Stella|Stellas|Dime|Dimes|Nickel|Nickels))\b", title, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                val = re.sub(r'\s*\-\s*$', '', val)
                return normalize_denom(val)
                
            lower_title = title.lower()
            if "one cent" in lower_title or "1 cent" in lower_title or "penny" in lower_title:
                return "One Cent"
            if "five cents" in lower_title or "5 cents" in lower_title or "nickel" in lower_title:
                return "Five Cents"
            if "one dime" in lower_title or "1 dime" in lower_title or "10 cents" in lower_title or "dime" in lower_title:
                return "One Dime"
            if "quarter" in lower_title or "25 cents" in lower_title or "¼ dollar" in lower_title:
                return "Quarter Dollar"
            if "half dollar" in lower_title or "50 cents" in lower_title or "½ dollar" in lower_title:
                return "Half Dollar"
            if "one dollar" in lower_title or "1 dollar" in lower_title or "dollar" in lower_title:
                return "One Dollar"
                
            match_ds = re.search(r"\$(\d+(?:\.\d+)?)", title)
            if match_ds:
                return normalize_denom(f"${match_ds.group(1)}")
                
            return "One Dollar"

        for r in baseline_rows:
            title = r["title"] or ""
            aka = r["also_known_as"] or ""
            issuer = r["issuer"] or ""
            combined = (title + " " + aka + " " + issuer).lower()
            
            # Check rejected
            is_rejected = False
            for kw in REJECT_KEYWORDS:
                if kw in combined:
                    is_rejected = True
                    break
                    
            if is_rejected:
                baseline_rejected_count += 1
                continue
                
            # Check medal
            is_medal = "medal" in combined or "medallion" in combined
            
            if is_medal:
                is_official_medal = False
                for kw in ACCEPT_MEDAL_KEYWORDS:
                    if kw in combined:
                        is_official_medal = True
                        break
                if "congressional" in combined or "presidential" in combined:
                    is_official_medal = True
                    
                if is_official_medal:
                    # Merge official medals from baseline
                    map_entry = baseline_map.get(title, {})
                    series_val = map_entry.get("series", "U.S. Medals")
                    year_val = map_entry.get("year", "")
                    mint_val = map_entry.get("mint_mark", "")

                    if series_val in ALLOWED_MEDAL_SERIES:
                        baseline_medals_count += 1
                        consolidated_catalog.append({
                            "doc_id": f"ref_coin_type_{r['id']}",
                            "year": year_val,
                            "denomination": "Medal",
                            "mint_mark": mint_val,
                            "variety": title,
                            "note": aka or f"Official U.S. Medal: {title}",
                            "series": series_val,
                            "category": "medal"
                        })
                    else:
                        baseline_rejected_count += 1
                else:
                    baseline_rejected_count += 1
            else:
                # Mapped baseline coin
                map_entry = baseline_map.get(title, {})
                series_val = map_entry.get("series", r["category"].title() if r["category"] else "U.S. Coins")
                year_val = map_entry.get("year", "")
                mint_val = map_entry.get("mint_mark", "")
                
                # Check for explicit rejections/souvenirs
                if "world fair of money" in combined and "fugio" in combined:
                    baseline_rejected_count += 1
                    continue
                if "hobo" in combined:
                    baseline_rejected_count += 1
                    continue
                # Connecticut coppers, Mailed bust, etc. (colonial pre-federal except Fugio)
                if any(kw in combined for kw in ["mailed bust", "connecticut", "vermont", "massachusetts", "new jersey"]):
                    if "fugio" not in combined:
                        baseline_rejected_count += 1
                        continue

                # Silver Rounds & Bullion mapping
                if series_val == 'Silver Rounds & Bullion':
                    if "Bullion Coinage" in title and "10 Dollars" in title:
                        series_val = "First Spouse Gold Coins"
                    elif "American Liberty" in title or "High Relief" in title:
                        series_val = "American Liberty Gold Coins"
                    elif "Palladium Eagle" in title:
                        series_val = "American Palladium Eagles"
                    elif "Pursuit of Happiness" in title:
                        series_val = "American Liberty Gold Coins"
                
                # Official banknotes in coins table mapping
                is_banknote = False
                if series_val in {'Educational Series', 'Horse Blanket', 'Greenback'} or (series_val == 'Martha' and "Silver Certificate" in title):
                    is_banknote = True
                    category_val = "banknote"
                    series_val = "U.S. Banknotes"
                else:
                    category_val = "coin"
                    
                if is_banknote:
                    baseline_coins_count += 1
                    consolidated_catalog.append({
                        "doc_id": f"ref_coin_type_{r['id']}",
                        "year": year_val,
                        "denomination": parse_denom_baseline(title) or "One Dollar",
                        "mint_mark": mint_val,
                        "variety": title,
                        "note": aka or f"Official U.S. Banknote: {title}",
                        "series": series_val,
                        "category": category_val
                    })
                elif series_val in ALLOWED_COIN_SERIES:
                    baseline_coins_count += 1
                    denom_val = parse_denom_baseline(title)
                    if not denom_val:
                        denom_val = r["category"].title() if r["category"] else "Coin"
                        
                    consolidated_catalog.append({
                        "doc_id": f"ref_coin_type_{r['id']}",
                        "year": year_val,
                        "denomination": denom_val,
                        "mint_mark": mint_val,
                        "variety": title,
                        "note": aka or f"Base coin type: {title}",
                        "series": series_val,
                        "category": category_val
                    })
                else:
                    baseline_rejected_count += 1
        print(f"  Baseline classification completed:")
        print(f"    Coins Mapped: {baseline_coins_count}")
        print(f"    Medals Mapped: {baseline_medals_count}")
        print(f"    Rejected/Filtered: {baseline_rejected_count}")
        
    except Exception as db_e:
        print(f"  ERROR loading baseline coins from SQLite: {db_e}")

    # Process Coins from definitive_catalog_full.json
    ref_coin_keys = set()
    for c in coins:
        year = str(c.get("year", "")).strip()
        denom = normalize_denom(c.get("denomination", ""), default="One Dollar")
        mint = normalize_mint(c.get("mint_mark", ""))
        variety = str(c.get("variety", "")).lower().strip()
        ref_coin_keys.add((year, denom, mint, variety))
        
        consolidated_catalog.append({
            "doc_id": f"ref_coin_{slugify(c.get('series'))}_{slugify(denom)}_{slugify(c.get('year'))}_{slugify(c.get('mint_mark'))}_{slugify(c.get('variety'))}"[:100],
            "year": c.get("year", ""),
            "denomination": denom,
            "mint_mark": c.get("mint_mark", ""),
            "variety": c.get("variety", ""),
            "note": c.get("note", ""),
            "series": c.get("series", ""),
            "category": "coin"
        })

    # Process Notes from banknotes_expanded.json
    ref_note_keys = set()
    for n in notes:
        year = str(n.get("year", "")).strip()
        denom = normalize_denom(n.get("denomination", ""), default="One Dollar")
        variety = str(n.get("variety", "")).lower().strip()
        fr_num = extract_fr_number(variety)
        ref_note_keys.add((year, denom, fr_num))
        
        consolidated_catalog.append({
            "doc_id": f"ref_note_{slugify(denom)}_{slugify(n.get('year'))}_{slugify(n.get('variety'))}"[:100],
            "year": n.get("year", ""),
            "denomination": denom,
            "mint_mark": "",
            "variety": n.get("variety", ""),
            "note": n.get("note", ""),
            "series": "U.S. Banknotes",
            "category": "banknote"
        })

    # Process Medals
    for m in medals:
        denom = normalize_denom(m.get("denomination", ""), default="Medal")
        consolidated_catalog.append({
            "doc_id": f"ref_medal_{slugify(m.get('series'))}_{slugify(m.get('year'))}_{slugify(m.get('variety'))}"[:100],
            "year": m.get("year", ""),
            "denomination": denom,
            "mint_mark": "",
            "variety": m.get("variety", ""),
            "note": m.get("note", ""),
            "series": m.get("series", "U.S. Medals"),
            "category": "medal"
        })

    # Final filter / guardrail pass to guarantee 100% compliance with U.S. Mint and BEP official items
    final_catalog = []
    skipped_count = 0
    for entry in consolidated_catalog:
        cat = entry.get("category", "")
        series = entry.get("series", "")
        title = entry.get("variety", "")
        note = entry.get("note", "")
        
        # Explicit checks for play money/casino/replicas/novelty
        combined = f"{title} {series} {note}".lower()
        
        # 1. Souvenir/reproduction Fugio or other explicit rejections
        if "world fair of money" in combined and "fugio" in combined:
            skipped_count += 1
            continue
            
        # 2. Hardcode skip Hobo nickels/dollars which map to "Morgan" or "Buffalo"
        if "hobo" in combined:
            skipped_count += 1
            continue
            
        # 3. Check for specific non-US token and replica items (checking only coins/medals)
        is_rejected = False
        REJECT_KEYWORDS = [
            "token", "privately struck", "private issue", "merchant", 
            "municipal", "exonumia", "wooden nickel", "poker chip", 
            "gaming", "replica", "copy", "novelty", "play money",
            "counterfeit", "souvenir medal", "fantasy issue", "reproduction",
            "tropicana", "readers digest", "reader's digest", "pooh bear"
        ]
        
        if cat in ["coin", "medal"]:
            for kw in REJECT_KEYWORDS:
                if kw in combined:
                    is_rejected = True
                    break
                    
        if is_rejected:
            skipped_count += 1
            continue
            
        # 4. Check whitelists
        if cat == "coin":
            # Check for Mailed bust, Connecticut copper, Vermont copper, etc. (colonial/pre-federal except Fugio)
            if any(kw in combined for kw in ["mailed bust", "connecticut", "vermont", "massachusetts", "new jersey"]):
                if "fugio" not in combined:
                    skipped_count += 1
                    continue
            if series in ALLOWED_COIN_SERIES:
                final_catalog.append(entry)
            else:
                skipped_count += 1
        elif cat == "medal":
            if series in ALLOWED_MEDAL_SERIES:
                final_catalog.append(entry)
            else:
                skipped_count += 1
        elif cat == "banknote":
            # For banknotes, we force category = banknote and series = U.S. Banknotes
            entry["series"] = "U.S. Banknotes"
            final_catalog.append(entry)
        else:
            skipped_count += 1
            
    consolidated_catalog = final_catalog
    print(f"\nConsolidated catalog size after whitelisting guardrails: {len(consolidated_catalog)} total entries.")
    print(f"Skipped/Filtered out: {skipped_count} entries.")

    # 5. Populate SQLite Local Cache (definitive_reference table)
    print(f"\nCaching in SQLite: {DB_PATH}")
    db_conn = sqlite3.connect(DB_PATH)
    db_cursor = db_conn.cursor()
    
    # Create Table
    db_cursor.execute("DROP TABLE IF EXISTS definitive_reference;")
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
    
    # Wipe the collection first to prevent reference pollution from previous runs
    print("Wiping existing documents in 'coins_reference' collection...")
    deleted_count = 0
    try:
        doc_refs = list(col_ref.list_documents())
        print(f"  Found {len(doc_refs)} existing reference documents to delete.")
        batch = db.batch()
        for doc_ref in doc_refs:
            batch.delete(doc_ref)
            deleted_count += 1
            if deleted_count % 400 == 0:
                batch.commit()
                batch = db.batch()
                print(f"  Deleted {deleted_count} documents from Firestore...")
        if deleted_count % 400 != 0:
            batch.commit()
        print(f"  Wipe complete. Total deleted: {deleted_count} documents.")
    except Exception as wipe_e:
        print(f"  WARNING: Error during Firestore wipe (continuing anyway): {wipe_e}")
    
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
