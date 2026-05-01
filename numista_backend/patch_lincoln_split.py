"""
Split Lincoln Cents into 4 collector-friendly sub-checklists:
  1. Wheat Pennies         (1909–1958)
  2. Memorial Cents        (1959–2008)
  3. 2009 Bicentennial     (4 designs)
  4. Shield Cents          (2010–present)

Inserts all 4 as separate programs in master_coin_programs.json,
right after the original Lincoln Cents entry.
"""
import sys, json, re, os
sys.stdout.reconfigure(encoding='utf-8')

master_path = os.path.join(os.path.dirname(__file__), "master_coin_programs.json")
with open(master_path, "r", encoding="utf-8") as f:
    master = json.load(f)

# Find the existing Lincoln Cents entry
lincoln_idx = next((i for i,p in enumerate(master) if p.get("name") == "Lincoln Cents"), None)
if lincoln_idx is None:
    print("ERROR: Lincoln Cents not found")
    exit(1)

lincoln = master[lincoln_idx]
all_coins = lincoln.get("coins", [])
print(f"Total Lincoln Cents coins: {len(all_coins)}")

# ── Split by year ─────────────────────────────────────────────────────────────
wheat      = [c for c in all_coins if c.get("year","").isdigit() and 1909 <= int(c["year"]) <= 1958]
memorial   = [c for c in all_coins if c.get("year","").isdigit() and 1959 <= int(c["year"]) <= 2008]
bicent     = [c for c in all_coins if c.get("year","") == "2009"]
shield     = [c for c in all_coins if c.get("year","").isdigit() and int(c["year"]) >= 2010]

print(f"  Wheat Pennies:       {len(wheat)} coins")
print(f"  Memorial Cents:      {len(memorial)} coins")
print(f"  2009 Bicentennial:   {len(bicent)} coins")
print(f"  Shield Cents:        {len(shield)} coins")
print(f"  Total:               {len(wheat)+len(memorial)+len(bicent)+len(shield)} coins")

MINT_KEY = "Mint Mark Key: | Philadelphia - P (no mark pre-1980) | Denver - D | San Francisco - S |"

sub_programs = [
    {
        "id": "lincoln_wheat_pennies",
        "name": "Lincoln Wheat Pennies",
        "years": "1909-1958",
        "category": "Cent",
        "url": "",
        "mint_mark_locations": MINT_KEY,
        "coins": wheat,
    },
    {
        "id": "lincoln_memorial_cents",
        "name": "Lincoln Memorial Cents",
        "years": "1959-2008",
        "category": "Cent",
        "url": "",
        "mint_mark_locations": MINT_KEY,
        "coins": memorial,
    },
    {
        "id": "lincoln_bicentennial_2009",
        "name": "Lincoln Bicentennial Cents (2009)",
        "years": "2009",
        "category": "Cent",
        "url": "",
        "mint_mark_locations": MINT_KEY,
        "coins": bicent,
    },
    {
        "id": "lincoln_shield_cents",
        "name": "Lincoln Shield Cents",
        "years": "2010-Present",
        "category": "Cent",
        "url": "",
        "mint_mark_locations": MINT_KEY,
        "coins": shield,
    },
]

# Mark original Lincoln Cents as superseded (keep coins, but flag it)
lincoln["_superseded_by"] = ["lincoln_wheat_pennies", "lincoln_memorial_cents",
                              "lincoln_bicentennial_2009", "lincoln_shield_cents"]
lincoln["_skip_checklist"] = True  # don't generate PDF for the monolith

# Insert sub-programs right after the Lincoln entry
for i, sp in enumerate(sub_programs):
    master.insert(lincoln_idx + 1 + i, sp)

with open(master_path, "w", encoding="utf-8") as f:
    json.dump(master, f, indent=2, ensure_ascii=False)
print("\nSaved. Lincoln Cents split into 4 sub-checklists.")
