# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
Patch master_coin_programs.json for:
1. Presidential Dollars (2007-2016, 2020) — edge lettered
2. America the Beautiful / National Park Quarters (2010-2021)
"""
import sys, json, re, os, urllib.request
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8')

# ── Presidential Dollars (curated — Wikipedia table is fragmented) ────────────
PRESIDENTS = [
    ("2007", "George Washington"),    ("2007", "John Adams"),
    ("2007", "Thomas Jefferson"),     ("2007", "James Madison"),
    ("2008", "James Monroe"),         ("2008", "John Quincy Adams"),
    ("2008", "Andrew Jackson"),       ("2008", "Martin Van Buren"),
    ("2009", "William Henry Harrison"),("2009","John Tyler"),
    ("2009", "James K. Polk"),        ("2009", "Zachary Taylor"),
    ("2010", "Millard Fillmore"),     ("2010", "Franklin Pierce"),
    ("2010", "James Buchanan"),       ("2010", "Abraham Lincoln"),
    ("2011", "Andrew Johnson"),       ("2011", "Ulysses S. Grant"),
    ("2011", "Rutherford B. Hayes"),  ("2011", "James Garfield"),
    ("2012", "Chester Arthur"),       ("2012", "Grover Cleveland (1st term)"),
    ("2012", "Benjamin Harrison"),    ("2012", "Grover Cleveland (2nd term)"),
    ("2013", "William McKinley"),     ("2013", "Theodore Roosevelt"),
    ("2013", "William Howard Taft"),  ("2013", "Woodrow Wilson"),
    ("2014", "Warren G. Harding"),    ("2014", "Calvin Coolidge"),
    ("2014", "Herbert Hoover"),       ("2014", "Franklin D. Roosevelt"),
    ("2015", "Harry S. Truman"),      ("2015", "Dwight D. Eisenhower"),
    ("2015", "John F. Kennedy"),      ("2015", "Lyndon B. Johnson"),
    ("2016", "Richard Nixon"),        ("2016", "Gerald Ford"),
    ("2016", "Ronald Reagan"),
    ("2020", "George H.W. Bush"),
]

pres_coins = []
for year, name in PRESIDENTS:
    pres_coins.append({
        "id": f"pres_{year}_{re.sub(r'[^a-z0-9]', '_', name.lower())}",
        "year": year,
        "name": name,
        "varieties": [
            {"id": "P",       "label": "P"},
            {"id": "D",       "label": "D"},
            {"id": "S-PROOF", "label": "Proof"},
        ],
    })

print(f"Presidential Dollars: {len(pres_coins)} coins")

# ── America the Beautiful Quarters (scraped from Wikipedia) ──────────────────
ATB_URL = "https://en.wikipedia.org/wiki/America_the_Beautiful_quarters"
req = urllib.request.Request(ATB_URL, headers={"User-Agent": "NumistaAI-DataSync/1.0"})
html = urllib.request.urlopen(req).read().decode("utf-8")
soup = BeautifulSoup(html, "html.parser")

atb_coins = []
current_year = ""

for table in soup.find_all("table"):
    rows = table.find_all("tr")
    header = [c.get_text(strip=True) for c in rows[0].find_all(["th","td"])] if rows else []
    # Only process the main release table (has Year, No., Jurisdiction, Site)
    if "Jurisdiction" not in " ".join(header) and "Site" not in " ".join(header):
        continue
    for row in rows[1:]:
        cells = row.find_all(["th", "td"])
        text = [c.get_text(separator=" ", strip=True) for c in cells]
        if len(text) < 3:
            continue

        year_match = re.match(r"^(\d{4})", text[0])
        if year_match:
            current_year = year_match.group(1)
            state = text[2] if len(text) > 2 else ""
            site  = text[3] if len(text) > 3 else ""
        elif re.match(r"^\d{1,2}$", text[0]) and current_year:
            state = text[1] if len(text) > 1 else ""
            site  = text[2] if len(text) > 2 else ""
        else:
            continue

        state = re.sub(r"\[.*?\]", "", state).strip()
        site  = re.sub(r"\[.*?\]", "", site).strip()

        if not state or not site or "release" in site.lower():
            continue

        name = f"{site} ({state})"
        atb_coins.append({
            "id": f"atb_{current_year}_{re.sub(r'[^a-z0-9]', '_', site.lower()[:30])}",
            "year": current_year,
            "name": name,
            "varieties": [
                {"id": "P",       "label": "P"},
                {"id": "D",       "label": "D"},
                {"id": "S",       "label": "S"},
                {"id": "S-PROOF", "label": "Proof"},
            ],
        })

print(f"ATB Quarters: {len(atb_coins)} coins")
for c in atb_coins:
    print(f"  {c['year']} - {c['name']}")

# ── Patch master JSON ─────────────────────────────────────────────────────────
master_path = os.path.join(os.path.dirname(__file__), "master_coin_programs.json")
with open(master_path, "r", encoding="utf-8") as f:
    master = json.load(f)

for prog in master:
    name = prog.get("name", "").lower()
    if "presidential" in name:
        prog["name"] = "Presidential Dollars"
        prog["years"] = "2007-2020"
        prog["category"] = "Dollar"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |"
        prog["edge_diagram"] = True
        prog["coins"] = pres_coins
        print(f"\nPatched: {prog['name']} ({len(pres_coins)} coins)")

    elif "national park" in name or "america the beautiful" in name or "atb" in name:
        prog["name"] = "America the Beautiful Quarters (National Parks)"
        prog["years"] = "2010-2021"
        prog["category"] = "Quarter"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |"
        prog["coins"] = atb_coins
        print(f"Patched: {prog['name']} ({len(atb_coins)} coins)")

with open(master_path, "w", encoding="utf-8") as f:
    json.dump(master, f, indent=2, ensure_ascii=False)

print("\nmaster_coin_programs.json saved.")
