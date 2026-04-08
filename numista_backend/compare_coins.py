import json
import re

with open('indexed_coins.json', 'r') as f:
    pdf_data = json.load(f)

eisenhower_raw = pdf_data['Eisenhower']['coins']

with open('db_assets.json', 'r') as f:
    db_data = json.load(f)

db_titles = [d.get('coin_title', '').lower() for d in db_data if d.get('coin_title')]

missing_coins = []
insert_statements = []
seen_titles = set()

for raw_name in eisenhower_raw:
    # Example raw_name: "1971", "1971-S Silver Clad", "1976 Variety I*"
    year_match = re.search(r'(197\d)', raw_name)
    year = year_match.group(1) if year_match else ''
    
    mm_match = re.search(r'-([A-Z])', raw_name)
    if mm_match:
        mm = mm_match.group(1)
    else:
        mm = 'P'
        
    formatted_title = f"{year} Eisenhower Dollar - {mm}"
    
    if formatted_title in seen_titles:
        continue
    seen_titles.add(formatted_title)
    
    found = any(year in t and 'eisenhower' in t for t in db_titles)
    
    if not found:
        missing_coins.append(formatted_title)
        sql = f"INSERT INTO us_mint_assets (coin_title) VALUES ('{formatted_title}');"
        insert_statements.append(sql)

print(f"Total Unique PDF Coins: {len(seen_titles)}")
print(f"Missing Coins found: {len(missing_coins)}")

with open('c:\\Users\\ericd\\.gemini\\antigravity\\brain\\11e0ab1b-0c7e-470a-97c1-3147223fd329\\missing_inserts.sql', 'w') as f:
    f.write("-- Missing Eisenhower Dollars\n")
    for sql in insert_statements:
        f.write(sql + "\n")
