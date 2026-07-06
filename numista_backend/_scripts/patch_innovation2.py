# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import json
import re
import os

with open('wiki_data.json', 'r', encoding='utf-8') as f:
    wiki = json.load(f)

coins = []
current_year = ""
for row in wiki[1:]: # skip header
    if len(row) < 3: continue
    
    if row[0].isdigit() and len(row[0]) == 4:
        current_year = row[0]
        state = row[2]
        inov = row[3]
    elif row[0].isdigit() and len(row[0]) in [1, 2]:
        state = row[1]
        inov = row[2]
    else:
        continue
    
    if current_year == "": continue
        
    inov = re.sub(r'\[\d+\]', '', inov).strip()
    state = re.sub(r'\[\d+\]', '', state).strip()
    
    # Exclude Gold section noise
    if "Liberty Head" in state: continue
    
    name = f"{state} {inov}" if "TBA" not in inov else state

    coins.append({
        "year": current_year,
        "name": name,
        "varieties": ["P", "D", "S", "Proof"]
    })

file_path = os.path.join(os.path.dirname(__file__), 'master_coin_programs.json')
with open(file_path, 'r', encoding='utf-8') as f:
    master = json.load(f)

for prog in master:
    if prog.get('name') == 'INNOVATION DOLLARS' or prog.get('name') == 'American Innovation $1 Coin Program':
        prog['name'] = 'American Innovation $1 Coin Program'
        prog['coins'] = coins
        # Update mint mark locations text while we are here:
        prog['mint_mark_locations'] = "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |"
        break

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(master, f, indent=2)

print(f"Updated with {len(coins)} coins.")
