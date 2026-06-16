"""
Patch master_coin_programs.json with accurate American Women Quarters data
scraped from Wikipedia, and update the sync_worker to handle this program.
"""
import json
import re
import os
import sys
import urllib.request
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

WIKI_URL = "https://en.wikipedia.org/wiki/American_Women_quarters"

req = urllib.request.Request(WIKI_URL, headers={"User-Agent": "NumistaAI-DataSync/1.0"})
html = urllib.request.urlopen(req).read().decode("utf-8")
soup = BeautifulSoup(html, "html.parser")

coins = []
current_year = ""

for table in soup.find_all("table"):
    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all(["th", "td"])
        text = [cell.get_text(separator=" ", strip=True) for cell in cells]

        if len(text) < 3:
            continue

        # Detect year row — first cell starts with a 4-digit year
        year_match = re.match(r"^(\d{4})", text[0])
        if year_match:
            current_year = year_match.group(1)
            # Row has: Year | No. | Woman | ...
            woman = re.sub(r"\[.*?\]", "", text[2]).strip() if len(text) > 2 else ""
        elif re.match(r"^\d{1,2}$", text[0]) and current_year:
            # Continuation row: No. | Woman | ...
            woman = re.sub(r"\[.*?\]", "", text[1]).strip() if len(text) > 1 else ""
        else:
            continue

        # Normalize special Unicode apostrophes/quotes to ASCII
        woman = re.sub(r"[\u02bb\u2018\u2019\u02bc]", "'", woman).strip()
        if not woman or woman in ("Woman", "No.", "Year"):
            continue
        # Skip junk at page bottom
        if "Liberty Head" in woman or len(woman) > 60:
            continue

        coins.append({
            "id": f"awq_{current_year}_{re.sub(r'[^a-z0-9]', '_', woman.lower())}",
            "year": current_year,
            "name": woman,
            "varieties": [
                {"id": "P", "label": "P"},
                {"id": "D", "label": "D"},
                {"id": "S", "label": "S"},
                {"id": "S-PROOF", "label": "Proof"},
            ]
        })

print(f"Scraped {len(coins)} coins:")
for c in coins:
    print(f"  {c['year']} - {c['name']}")

# Patch master_coin_programs.json
master_path = os.path.join(os.path.dirname(__file__), "master_coin_programs.json")
with open(master_path, "r", encoding="utf-8") as f:
    master = json.load(f)

for prog in master:
    if "WOMEN" in prog.get("name", "").upper() or "WOMEN" in prog.get("id", "").upper():
        prog["name"] = "American Women Quarters"
        prog["years"] = "2022-2025"
        prog["category"] = "Quarter"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |"
        prog["coins"] = coins
        print(f"\nPatched program: {prog['name']}")
        break

with open(master_path, "w", encoding="utf-8") as f:
    json.dump(master, f, indent=2, ensure_ascii=False)

print("master_coin_programs.json saved.")
