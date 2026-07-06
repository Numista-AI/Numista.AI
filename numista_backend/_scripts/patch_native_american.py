# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
Patch master_coin_programs.json with accurate Sacagawea & Native American Dollar data.
The coin has two phases:
  - Sacagawea Dollar (2000-2008): Plain edge, single design
  - Native American $1 Coin (2009-present): Lettered edge, unique reverse design each year
"""
import sys, json, re, os, urllib.request
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8')

# Native American / Sacagawea theme by year (scraped from Wikipedia + US Mint)
# 2000-2008 = Sacagawea; 2009-present = Native American series with changing reverses
NATIVE_AMERICAN_THEMES = {
    "2000": "Sacagawea & Eagle",
    "2001": "Sacagawea & Eagle",
    "2002": "Sacagawea & Eagle",
    "2003": "Sacagawea & Eagle",
    "2004": "Sacagawea & Eagle",
    "2005": "Sacagawea & Eagle",
    "2006": "Sacagawea & Eagle",
    "2007": "Sacagawea & Eagle",
    "2008": "Sacagawea & Eagle",
    "2009": "Three Sisters Agriculture",
    "2010": "Hiawatha Belt — Great Law of Peace",
    "2011": "Wampanoag Treaty of 1621",
    "2012": "Trade Routes in the 17th Century",
    "2013": "Delaware Treaty of 1778",
    "2014": "Native Hospitality",
    "2015": "Mohawk Ironworkers",
    "2016": "Code Talkers",
    "2017": "Sequoyah",
    "2018": "Jim Thorpe",
    "2019": "American Indians in the Space Program",
    "2020": "Elizabeth Peratrovich — Anti-Discrimination Law",
    "2021": "Indigenous Peoples' Contributions",
    "2022": "Ely S. Parker",
    "2023": "Maria Tallchief",
    "2024": "Tayo — Code Talker Novels",
    "2025": "TBA",
}

coins = []
for year, theme in NATIVE_AMERICAN_THEMES.items():
    yr = int(year)
    if yr <= 2008:
        varieties = [
            {"id": "P",       "label": "P"},
            {"id": "D",       "label": "D"},
            {"id": "S-PROOF", "label": "Proof"},
        ]
    else:
        # Edge lettered (2009+) — P, D, S proof only; no W unless special
        varieties = [
            {"id": "P",       "label": "P"},
            {"id": "D",       "label": "D"},
            {"id": "S-PROOF", "label": "Proof"},
        ]
    
    coins.append({
        "id": f"na_dollar_{year}",
        "year": year,
        "name": theme,
        "varieties": varieties,
    })

print(f"Built {len(coins)} coins:")
for c in coins:
    print(f"  {c['year']} - {c['name']}")

# Patch JSON
master_path = os.path.join(os.path.dirname(__file__), "master_coin_programs.json")
with open(master_path, "r", encoding="utf-8") as f:
    master = json.load(f)

patched = False
for prog in master:
    name = prog.get("name", "").lower()
    if "sacagawea" in name or "native american" in name:
        prog["name"] = "Sacagawea & Native American Dollars"
        prog["years"] = "2000-2025"
        prog["category"] = "Dollar"
        # Edge lettering 2009+ — important note for collector
        prog["mint_mark_locations"] = (
            "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |\n"
            "Note: From 2009 onward, the mint mark is on the EDGE of the coin."
        )
        prog["edge_diagram"] = True
        prog["coins"] = coins
        patched = True
        print(f"\nPatched: {prog['name']}")
        break

if not patched:
    print("WARNING: Could not find Sacagawea/Native American program in JSON!")

with open(master_path, "w", encoding="utf-8") as f:
    json.dump(master, f, indent=2, ensure_ascii=False)

print("master_coin_programs.json saved.")
