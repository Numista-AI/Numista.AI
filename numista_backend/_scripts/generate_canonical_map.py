import json
import os

master_path = r'c:\Users\ericd\Documents\MyVertexProject\numista_backend\master_coin_programs.json'
with open(master_path, 'r', encoding='utf-8') as f:
    master_programs = json.load(f)

# Built-in Program Alias Map
program_aliases = {
    "50 state quarters": "fifty_state_quarters",
    "50 state quarters program": "fifty_state_quarters",
    "state quarters": "fifty_state_quarters",
    "presidential $1 coin program": "presidential_dollars",
    "presidential dollars": "presidential_dollars",
    "presidential $1": "presidential_dollars",
    "america the beautiful quarters (national parks)": "america_the_beautiful_quarters",
    "america the beautiful quarters": "america_the_beautiful_quarters",
    "national park quarters": "america_the_beautiful_quarters",
    "american innovation $1 coin program": "american_innovation_dollars",
    "american innovation dollars": "american_innovation_dollars",
    "d.c. & u.s. territories quarters": "dc_territories_quarters",
    "dc & us territories quarters": "dc_territories_quarters",
    "american women quarters": "american_women_quarters",
    "washington quarters (classic)": "washington_quarters_classic",
    "washington quarter": "washington_quarters_classic",
    "roosevelt dimes": "roosevelt_dimes",
    "roosevelt dime": "roosevelt_dimes",
    "jefferson nickels": "jefferson_nickels",
    "jefferson nickel": "jefferson_nickels",
    "kennedy half dollars": "kennedy_half_dollars",
    "kennedy half": "kennedy_half_dollars",
    "sacagawea & native american dollars": "sacagawea_native_american_dollars",
    "sacagawea": "sacagawea_native_american_dollars",
    "native american": "sacagawea_native_american_dollars",
    "lincoln cents": "lincoln_cents",
    "lincoln wheat pennies": "lincoln_wheat_pennies",
    "lincoln memorial cents": "lincoln_memorial_cents",
    "lincoln bicentennial cents (2009)": "lincoln_bicentennial_cents_2009",
    "lincoln shield cents": "lincoln_shield_cents",
    "morgan dollars": "morgan_dollars",
    "peace dollars": "peace_dollars",
    "eisenhower dollars": "eisenhower_dollars",
    "susan b. anthony dollars": "susan_b_anthony_dollars",
    "american silver eagles": "american_silver_eagles",
    "flying eagle & indian head cents": "flying_eagle_indian_head_cents",
    "liberty head (v) nickels": "liberty_head_v_nickels",
    "buffalo nickels": "buffalo_nickels",
    "mercury dimes": "mercury_dimes",
    "franklin half dollars": "franklin_half_dollars",
    "liberty walking half dollars": "liberty_walking_half_dollars",
    "barber dimes": "barber_dimes",
    "barber quarters": "barber_quarters",
    "barber half dollars": "barber_half_dollars",
    "u.s. proof sets": "u_s_proof_sets",
    "2026 america250 - circulating currency": "2026_semiquincentennial_currency",
    "2026 america250 - numismatic collectibles": "2026_semiquincentennial_collectibles",
    "2026 u.s. circulating coins": "2026_semiquincentennial_currency",
}

design_slug_map = {}

def slugify(text):
    import re
    clean = re.sub(r'[^a-z0-9]+', '_', text.lower()).strip('_')
    return clean

for prog in master_programs:
    name = prog.get('Name') or prog.get('name') or ''
    if not name:
        continue
    prog_id = prog.get('id') or prog.get('doc_id') or slugify(name)
    coins = prog.get('Coins') or prog.get('coins') or []
    
    design_slug_map[prog_id] = {}
    for c in coins:
        c_name = c.get('name') or c.get('official_title') or ''
        c_theme = c.get('theme') or c.get('Theme/Subject') or c_name
        c_slug = c.get('design_slug') or slugify(c_name)
        
        if c_name:
            design_slug_map[prog_id][c_name.lower()] = c_slug
        if c_theme and c_theme.lower() != c_name.lower():
            design_slug_map[prog_id][c_theme.lower()] = c_slug

map_artifact = {
    "version": "1.0.0",
    "program_aliases": program_aliases,
    "design_slug_map": design_slug_map
}

out_path = r'c:\Users\ericd\Documents\MyVertexProject\numista_backend\_scripts\canonical_catalog_map.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(map_artifact, f, indent=2)

print(f"Generated canonical_catalog_map.json with {len(program_aliases)} program aliases and {len(design_slug_map)} program design maps.")
