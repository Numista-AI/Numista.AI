# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
Add 50 State Quarters as new program (they live separately from classic Washington Quarters).
Also enrich classic Washington Quarters with proper mint mark variety data.
"""
import sys, json, re, os
sys.stdout.reconfigure(encoding='utf-8')

master_path = os.path.join(os.path.dirname(__file__), "master_coin_programs.json")
with open(master_path, "r", encoding="utf-8") as f:
    master = json.load(f)

# ── 50 State Quarters data ────────────────────────────────────────────────────
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

state_coins = [{
    "id": f"stateq_{y}_{re.sub(r'[^a-z0-9]','_',n.lower())}",
    "year": y, "name": n,
    "varieties": [
        {"id":"P","label":"P"},{"id":"D","label":"D"},
        {"id":"S-PROOF","label":"S Proof"},{"id":"S-SILVER","label":"S Silver"},
    ]
} for y, n in STATE_QUARTERS]

# Check if 50 State Quarters already exists as a program
exists = any("50 state" in p.get("name","").lower() for p in master)

if not exists:
    # Insert after DC Territories entry
    new_prog = {
        "id": "fifty_state_quarters",
        "name": "50 State Quarters",
        "years": "1999-2008",
        "category": "Quarter",
        "url": "",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |",
        "coins": state_coins,
    }
    # Find DC/Territories position and insert before it
    dc_idx = next((i for i, p in enumerate(master) if "territories" in p.get("name","").lower()), len(master))
    master.insert(dc_idx, new_prog)
    print(f"Inserted '50 State Quarters' with {len(state_coins)} coins at index {dc_idx}")
else:
    for prog in master:
        if "50 state" in prog.get("name","").lower():
            prog["coins"] = state_coins
            print(f"Updated '50 State Quarters'")

# ── Enrich classic Washington Quarters varieties ──────────────────────────────
# The classic series has specific mint mark patterns by era
CLASSIC_VARIETIES = {
    # 1932-1964 silver era: P (no mark), D, S
    "silver": {"years": range(1932, 1965),
               "varieties": [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S","label":"S"}]},
    # 1965-1967: SMS only (no P/D/S mint marks during transition)
    "sms": {"years": [1965,1966,1967],
            "varieties": [{"id":"SMS","label":"SMS"}]},
    # 1968-1998 clad era: P, D, S proof
    "clad": {"years": range(1968, 1999),
              "varieties": [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S-PROOF","label":"S Proof"}]},
}

for prog in master:
    if prog.get("name") == "WASHINGTON QUARTERS":
        prog["name"] = "Washington Quarters (Classic)"
        prog["years"] = "1932-1998"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P (no mark pre-1980) | Denver - D | San Francisco - S |"
        # Enrich coin varieties based on era
        for coin in prog.get("coins", []):
            yr = int(coin.get("year", 0)) if str(coin.get("year","")).isdigit() else 0
            if 1932 <= yr <= 1964:
                coin["varieties"] = [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S","label":"S"}]
            elif yr in (1965, 1966, 1967):
                coin["varieties"] = [{"id":"SMS","label":"SMS"}]
            elif yr == 1976:
                coin["varieties"] = [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S-PROOF","label":"S Proof"},{"id":"S-SILVER","label":"S Silver"}]
            elif 1968 <= yr <= 1998:
                coin["varieties"] = [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S-PROOF","label":"S Proof"}]
            elif yr == 2021:
                # 2021 Crossing the Delaware (PL 110-456) is NOT a Classic series member.
                # See implementation_planv6.md. master_coin_programs.json is canonical;
                # do NOT re-run this script against the already-corrected file.
                print("WARNING: Skipping year 2021 in Washington Classic patch — "
                      "not a Classic coin (PL 110-456). Do not reinsert.")
        print(f"Enriched Washington Quarters (Classic) with era-correct varieties")

with open(master_path, "w", encoding="utf-8") as f:
    json.dump(master, f, indent=2, ensure_ascii=False)
print("Saved.")
