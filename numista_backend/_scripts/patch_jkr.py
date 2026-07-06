# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
Batch patch Kennedy Half Dollars, Roosevelt Dimes, and Jefferson Nickels
with accurate, era-specific variety data.
"""
import sys, json, re, os
sys.stdout.reconfigure(encoding='utf-8')

master_path = os.path.join(os.path.dirname(__file__), "master_coin_programs.json")
with open(master_path, "r", encoding="utf-8") as f:
    master = json.load(f)


# ──────────────────────────────────────────────────────────────────────────────
# KENNEDY HALF DOLLARS (1964-present)
# ──────────────────────────────────────────────────────────────────────────────
# Era breakdown:
#  1964         → P, D (90% silver)
#  1965–1969    → P, D (40% silver clad). S proof 1968-69
#  1970         → D only (circulating), S proof
#  1971–1974    → P, D, S proof (clad)
#  1975–1976    → Bicentennial: P, D, S proof, S silver proof
#  1977–2001    → P, D, S proof (clad)
#  2002-present → D, S proof (no P for circulation; collector only)

def kennedy_varieties(yr):
    if yr == 1964:
        return [{"id":"P","label":"P"},{"id":"D","label":"D"}]
    elif yr in (1965,1966,1967):
        return [{"id":"P","label":"P"},{"id":"D","label":"D"}]
    elif yr in (1968,1969):
        return [{"id":"P","label":"P (40% Ag)"},{"id":"D","label":"D (40% Ag)"},{"id":"S-PROOF","label":"S Proof"}]
    elif yr == 1970:
        return [{"id":"D","label":"D (40% Ag)"},{"id":"S-PROOF","label":"S Proof"}]
    elif yr in (1971,1972,1973,1974):
        return [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S-PROOF","label":"S Proof"}]
    elif yr == 1976:
        return [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S-PROOF","label":"S Proof"},{"id":"S-SILVER","label":"S Silver"}]
    elif 1977 <= yr <= 2001:
        return [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S-PROOF","label":"S Proof"}]
    elif yr >= 2002:
        return [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S-PROOF","label":"S Proof"},{"id":"S-SILVER","label":"S Silver"}]
    return [{"id":"P","label":"P"},{"id":"D","label":"D"}]

kennedy_years = list(range(1964,1976)) + [1976] + list(range(1977,2025))
kennedy_years = [y for y in kennedy_years if y != 1975]  # no 1975 Kennedy (used 1975-76)
kennedy_coins = []
for yr in kennedy_years:
    name = "Bicentennial Coinage" if yr == 1976 else "Kennedy Half Dollar"
    kennedy_coins.append({
        "id": f"kennedy_{yr}",
        "year": str(yr),
        "name": name,
        "varieties": kennedy_varieties(yr),
    })

print(f"Kennedy Half Dollars: {len(kennedy_coins)} coins ({kennedy_coins[0]['year']}–{kennedy_coins[-1]['year']})")


# ──────────────────────────────────────────────────────────────────────────────
# ROOSEVELT DIMES (1946-present)
# ──────────────────────────────────────────────────────────────────────────────
# 1946-1964 → P, D, S (silver)
# 1965-1967 → P only (transition, SMS sets)
# 1968-present → P, D, S proof (clad)
# Note: no S dime struck for circulation after 1955; S proof returns 1968

def roosevelt_varieties(yr):
    if 1946 <= yr <= 1964:
        return [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S","label":"S"}]
    elif yr in (1965,1966,1967):
        return [{"id":"SMS","label":"SMS"}]
    elif yr >= 1968:
        return [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S-PROOF","label":"S Proof"}]
    return [{"id":"P","label":"P"},{"id":"D","label":"D"}]

# Some years skipped: no S in certain years (for simplicity a flag)
SKIP_S_CIRCULATION = {1965,1966,1967}

roosevelt_coins = []
for yr in range(1946, 2025):
    roosevelt_coins.append({
        "id": f"roosevelt_{yr}",
        "year": str(yr),
        "name": "Roosevelt Dime",
        "varieties": roosevelt_varieties(yr),
    })

print(f"Roosevelt Dimes: {len(roosevelt_coins)} coins ({roosevelt_coins[0]['year']}–{roosevelt_coins[-1]['year']})")


# ──────────────────────────────────────────────────────────────────────────────
# JEFFERSON NICKELS (1938-present)
# ──────────────────────────────────────────────────────────────────────────────
# 1938-1942  → P, D, S
# 1942-1945  → P (with P mint mark!), D, S (35% silver War Nickels)
# 1946-1964  → P, D, S
# 1965-1967  → P, D, S (no SMS for nickels unlike other denom)
# 1968-2003  → P, D, S proof
# 2004-2005  → Westward Journey series: P, D, S proof
# 2006+      → P, D, S proof + special designs

def jefferson_varieties(yr):
    if yr in (1942, 1943, 1944, 1945):
        # War nickels (silver), P has explicit mint mark above dome
        return [{"id":"P","label":"P (Silver)"},{"id":"D","label":"D (Silver)"},{"id":"S","label":"S (Silver)"}]
    elif 1938 <= yr <= 1964:
        return [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S","label":"S"}]
    elif 1965 <= yr <= 1967:
        return [{"id":"P","label":"P"},{"id":"D","label":"D"}]
    elif yr >= 1968:
        return [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S-PROOF","label":"S Proof"}]
    return [{"id":"P","label":"P"},{"id":"D","label":"D"}]

WESTWARD_JOURNEY = {
    2004: ["Peace Medal","Keelboat"],
    2005: ["American Bison","Ocean in View"],
}

jefferson_coins = []
for yr in range(1938, 2025):
    if yr in WESTWARD_JOURNEY:
        for design in WESTWARD_JOURNEY[yr]:
            jefferson_coins.append({
                "id": f"jefferson_{yr}_{re.sub(r'[^a-z0-9]','_',design.lower())}",
                "year": str(yr),
                "name": design,
                "varieties": jefferson_varieties(yr),
            })
    else:
        name = "Jefferson Nickel" if yr not in (1942,1943,1944,1945) else "War Nickel (35% Silver)"
        jefferson_coins.append({
            "id": f"jefferson_{yr}",
            "year": str(yr),
            "name": name,
            "varieties": jefferson_varieties(yr),
        })

print(f"Jefferson Nickels: {len(jefferson_coins)} coins ({jefferson_coins[0]['year']}–{jefferson_coins[-1]['year']})")


# ──────────────────────────────────────────────────────────────────────────────
# Patch JSON
# ──────────────────────────────────────────────────────────────────────────────
for prog in master:
    name = prog.get("name","").upper()
    if "KENNEDY" in name:
        prog["name"] = "Kennedy Half Dollars"
        prog["years"] = "1964-2024"
        prog["category"] = "Half Dollar"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |"
        prog["coins"] = kennedy_coins
        print(f"Patched: {prog['name']}")
    elif "ROOSEVELT" in name and "DIME" in name:
        prog["name"] = "Roosevelt Dimes"
        prog["years"] = "1946-2024"
        prog["category"] = "Dime"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |"
        prog["coins"] = roosevelt_coins
        print(f"Patched: {prog['name']}")
    elif "JEFFERSON" in name:
        prog["name"] = "Jefferson Nickels"
        prog["years"] = "1938-2024"
        prog["category"] = "Nickel"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |"
        prog["coins"] = jefferson_coins
        print(f"Patched: {prog['name']}")

with open(master_path, "w", encoding="utf-8") as f:
    json.dump(master, f, indent=2, ensure_ascii=False)
print("\nmaster_coin_programs.json saved.")
