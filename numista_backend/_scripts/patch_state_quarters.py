"""
Patch master_coin_programs.json for:
1. 50 State Quarters (1999-2008) — 50 coins
2. D.C. & U.S. Territories Quarters (2009) — 6 coins
3. Washington Quarters classic (1932-1998) — already in JSON, just enrich
"""
import sys, json, re, os, urllib.request
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8')

# ── 50 State Quarters (in order of release) ───────────────────────────────────
STATE_QUARTERS = [
    ("1999","Delaware"),("1999","Pennsylvania"),("1999","New Jersey"),
    ("1999","Georgia"),("1999","Connecticut"),
    ("2000","Massachusetts"),("2000","Maryland"),("2000","South Carolina"),
    ("2000","New Hampshire"),("2000","Virginia"),
    ("2001","New York"),("2001","North Carolina"),("2001","Rhode Island"),
    ("2001","Vermont"),("2001","Kentucky"),
    ("2002","Tennessee"),("2002","Ohio"),("2002","Louisiana"),
    ("2002","Indiana"),("2002","Mississippi"),
    ("2003","Illinois"),("2003","Alabama"),("2003","Maine"),
    ("2003","Missouri"),("2003","Arkansas"),
    ("2004","Michigan"),("2004","Florida"),("2004","Texas"),
    ("2004","Iowa"),("2004","Wisconsin"),
    ("2005","California"),("2005","Minnesota"),("2005","Oregon"),
    ("2005","Kansas"),("2005","West Virginia"),
    ("2006","Nevada"),("2006","Nebraska"),("2006","Colorado"),
    ("2006","North Dakota"),("2006","South Dakota"),
    ("2007","Montana"),("2007","Washington"),("2007","Idaho"),
    ("2007","Wyoming"),("2007","Utah"),
    ("2008","Oklahoma"),("2008","New Mexico"),("2008","Arizona"),
    ("2008","Alaska"),("2008","Hawaii"),
]

# ── D.C. & Territories (2009) ─────────────────────────────────────────────────
DC_TERRITORIES = [
    ("2009","District of Columbia"),
    ("2009","Puerto Rico"),
    ("2009","Guam"),
    ("2009","American Samoa"),
    ("2009","U.S. Virgin Islands"),
    ("2009","Northern Mariana Islands"),
]

def make_quarter_coin(year, name, with_silver=True):
    varieties = [
        {"id": "P",        "label": "P"},
        {"id": "D",        "label": "D"},
        {"id": "S-PROOF",  "label": "S Proof"},
    ]
    if with_silver:
        varieties.append({"id": "S-SILVER", "label": "S Silver"})
    return {
        "id": f"stateq_{year}_{re.sub(r'[^a-z0-9]', '_', name.lower())}",
        "year": year,
        "name": name,
        "varieties": varieties,
    }

state_coins = [make_quarter_coin(y, n) for y, n in STATE_QUARTERS]
dc_coins    = [make_quarter_coin(y, n, with_silver=False) for y, n in DC_TERRITORIES]

print(f"50 State Quarters: {len(state_coins)} coins")
print(f"D.C. & Territories: {len(dc_coins)} coins")

# ── Patch JSON ─────────────────────────────────────────────────────────────────
master_path = os.path.join(os.path.dirname(__file__), "master_coin_programs.json")
with open(master_path, "r", encoding="utf-8") as f:
    master = json.load(f)

state_patched = dc_patched = False
for prog in master:
    name = prog.get("name", "").lower()

    if "50 state" in name or ("state" in name and "quarter" in name and "50" in name):
        prog["name"] = "50 State Quarters"
        prog["years"] = "1999-2008"
        prog["category"] = "Quarter"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |"
        prog["coins"] = state_coins
        state_patched = True
        print(f"Patched: {prog['name']}")

    elif "statehood" in name or ("d.c" in name or "dc" in name or "territories" in name) and "quarter" in name:
        prog["name"] = "D.C. & U.S. Territories Quarters"
        prog["years"] = "2009"
        prog["category"] = "Quarter"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |"
        prog["coins"] = dc_coins
        dc_patched = True
        print(f"Patched: {prog['name']}")

if not state_patched:
    print("WARNING: Could not find 50 State Quarters in JSON — check program name")
if not dc_patched:
    print("WARNING: Could not find DC/Territories Quarters in JSON — check program name")

with open(master_path, "w", encoding="utf-8") as f:
    json.dump(master, f, indent=2, ensure_ascii=False)
print("Saved.")
