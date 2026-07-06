# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
Numista.AI Data Sync Worker
============================
Runs as a Cloud Run Job on a monthly schedule.
Scrapes all active US Mint coin program data from Wikipedia,
compares against the existing Firestore global_programs collection,
and merges in any new or corrected coin releases.

To add a new program: add an entry to PROGRAMS below.
"""

import logging
import os
import re
import sys
import urllib.request

from bs4 import BeautifulSoup
from google.cloud import firestore

logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

PROJECT_ID = os.environ.get("GCP_PROJECT", "studio-9101802118-8c9a8")
COLLECTION = "global_programs"

# ── Program Registry ────────────────────────────────────────────────────────
# Each entry defines how to scrape and store one coin program.
# To add a new program, append an entry here.
PROGRAMS = [
    {
        "doc_id": "american_innovation_dollars",
        "name": "American Innovation $1 Coin Program",
        "category": "Dollar",
        "years": "2018-2032",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |",
        "wiki_url": "https://en.wikipedia.org/wiki/American_Innovation_dollars",
        "scraper": "innovation",
    },
    {
        "doc_id": "american_women_quarters",
        "name": "American Women Quarters",
        "category": "Quarter",
        "years": "2022-2025",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |",
        "wiki_url": "https://en.wikipedia.org/wiki/American_Women_quarters",
        "scraper": "women_quarters",
    },
    {
        "doc_id": "sacagawea_native_american_dollars",
        "name": "Sacagawea & Native American Dollars",
        "category": "Dollar",
        "years": "2000-2025",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S | Note: From 2009 onward, look along the EDGE of the coin for the mint mark.",
        "wiki_url": "https://en.wikipedia.org/wiki/Sacagawea_dollar",
        "scraper": "native_american",
    },
    {
        "doc_id": "presidential_dollars",
        "name": "Presidential Dollars",
        "category": "Dollar",
        "years": "2007-2020",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S | Note: Mint mark is on the EDGE of the coin.",
        "wiki_url": "https://en.wikipedia.org/wiki/Presidential_dollar_coin",
        "scraper": "presidential",
    },
    {
        "doc_id": "america_the_beautiful_quarters",
        "name": "America the Beautiful Quarters (National Parks)",
        "category": "Quarter",
        "years": "2010-2021",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |",
        "wiki_url": "https://en.wikipedia.org/wiki/America_the_Beautiful_quarters",
        "scraper": "atb_quarters",
    },
    {
        "doc_id": "fifty_state_quarters",
        "name": "50 State Quarters",
        "category": "Quarter",
        "years": "1999-2008",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |",
        "wiki_url": "https://en.wikipedia.org/wiki/50_State_quarters",
        "scraper": "state_quarters",
    },
    {
        "doc_id": "dc_territories_quarters",
        "name": "D.C. & U.S. Territories Quarters",
        "category": "Quarter",
        "years": "2009",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |",
        "wiki_url": "https://en.wikipedia.org/wiki/District_of_Columbia_and_United_States_Territories_quarters",
        "scraper": "dc_territories",
    },
    {
        "doc_id": "washington_quarters_classic",
        "name": "Washington Quarters (Classic)",
        "category": "Quarter",
        "years": "1932-1998",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P (no mark pre-1980) | Denver - D | San Francisco - S |",
        "wiki_url": "https://en.wikipedia.org/wiki/Washington_quarter",
        "scraper": "washington_classic",
    },
    {
        "doc_id": "kennedy_half_dollars",
        "name": "Kennedy Half Dollars",
        "category": "Half Dollar",
        "years": "1964-2024",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |",
        "wiki_url": "https://en.wikipedia.org/wiki/Kennedy_half_dollar",
        "scraper": "kennedy",
    },
    {
        "doc_id": "roosevelt_dimes",
        "name": "Roosevelt Dimes",
        "category": "Dime",
        "years": "1946-2024",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |",
        "wiki_url": "https://en.wikipedia.org/wiki/Roosevelt_dime",
        "scraper": "roosevelt",
    },
    {
        "doc_id": "jefferson_nickels",
        "name": "Jefferson Nickels",
        "category": "Nickel",
        "years": "1938-2024",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |",
        "wiki_url": "https://en.wikipedia.org/wiki/Jefferson_nickel",
        "scraper": "jefferson",
    },
    {
        "doc_id": "lincoln_cents",
        "name": "Lincoln Cents",
        "category": "Cent",
        "years": "1909-2025",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P (no mark pre-1909-S era) | Denver - D | San Francisco - S |",
        "wiki_url": "https://en.wikipedia.org/wiki/Lincoln_cent",
        "scraper": "lincoln",
    },
    {
        "doc_id": "morgan_dollars",
        "name": "Morgan Dollars",
        "category": "Dollar",
        "years": "1878-1921 (+ 2021, 2023)",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P | Denver - D | New Orleans - O | San Francisco - S | Carson City - CC | West Point - W |",
        "wiki_url": "https://en.wikipedia.org/wiki/Morgan_dollar",
        "scraper": "morgan",
    },
    {
        "doc_id": "buffalo_nickels",
        "name": "Buffalo Nickels",
        "category": "Nickel",
        "years": "1913-1938",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P (no mark) | Denver - D | San Francisco - S |",
        "wiki_url": "https://en.wikipedia.org/wiki/Buffalo_nickel",
        "scraper": "buffalo",
    },
    {
        "doc_id": "mercury_dimes",
        "name": "Mercury Dimes",
        "category": "Dime",
        "years": "1916-1945",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P (no mark) | Denver - D | San Francisco - S |",
        "wiki_url": "https://en.wikipedia.org/wiki/Mercury_dime",
        "scraper": "mercury",
    },
    {
        "doc_id": "flying_eagle_indian_head_cents",
        "name": "Flying Eagle & Indian Head Cents",
        "category": "Cent",
        "years": "1856-1909",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P (no mark) | San Francisco - S |",
        "wiki_url": "https://en.wikipedia.org/wiki/Indian_Head_cent",
        "scraper": "static",
    },
    {
        "doc_id": "liberty_head_nickels",
        "name": "Liberty Head (V) Nickels",
        "category": "Nickel",
        "years": "1883-1912",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P (no mark) | Denver - D | San Francisco - S |",
        "wiki_url": "https://en.wikipedia.org/wiki/Liberty_Head_nickel",
        "scraper": "static",
    },
    {
        "doc_id": "liberty_walking_halves",
        "name": "Liberty Walking Half Dollars",
        "category": "Half Dollar",
        "years": "1916-1947",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P (no mark) | Denver - D | San Francisco - S |",
        "wiki_url": "https://en.wikipedia.org/wiki/Walking_Liberty_half_dollar",
        "scraper": "static",
    },
    {
        "doc_id": "franklin_half_dollars",
        "name": "Franklin Half Dollars",
        "category": "Half Dollar",
        "years": "1948-1963",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P (no mark) | Denver - D | San Francisco - S |",
        "wiki_url": "https://en.wikipedia.org/wiki/Franklin_half_dollar",
        "scraper": "static",
    },
    {
        "doc_id": "peace_dollars",
        "name": "Peace Dollars",
        "category": "Dollar",
        "years": "1921-1935 (+ 2021, 2023)",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P (no mark) | Denver - D | San Francisco - S |",
        "wiki_url": "https://en.wikipedia.org/wiki/Peace_dollar",
        "scraper": "static",
    },
    {
        "doc_id": "eisenhower_dollars",
        "name": "Eisenhower Dollars",
        "category": "Dollar",
        "years": "1971-1978",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |",
        "wiki_url": "https://en.wikipedia.org/wiki/Eisenhower_dollar",
        "scraper": "static",
    },
    {
        "doc_id": "susan_b_anthony_dollars",
        "name": "Susan B. Anthony Dollars",
        "category": "Dollar",
        "years": "1979-1981, 1999",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |",
        "wiki_url": "https://en.wikipedia.org/wiki/Susan_B._Anthony_dollar",
        "scraper": "static",
    },
    {
        "doc_id": "american_silver_eagles",
        "name": "American Silver Eagles",
        "category": "Bullion",
        "years": "1986-2024",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P | San Francisco - S | West Point - W |",
        "wiki_url": "https://en.wikipedia.org/wiki/American_Silver_Eagle",
        "scraper": "static",
    },
    {
        "doc_id": "barber_quarters",
        "name": "Barber Quarters",
        "category": "Quarter",
        "years": "1892-1916",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P (no mark) | Denver - D | New Orleans - O | San Francisco - S |",
        "wiki_url": "https://en.wikipedia.org/wiki/Barber_coinage",
        "scraper": "static",
    },
    {
        "doc_id": "barber_dimes",
        "name": "Barber Dimes",
        "category": "Dime",
        "years": "1892-1916",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P (no mark) | New Orleans - O | San Francisco - S |",
        "wiki_url": "https://en.wikipedia.org/wiki/Barber_coinage",
        "scraper": "static",
    },
    {
        "doc_id": "barber_half_dollars",
        "name": "Barber Half Dollars",
        "category": "Half Dollar",
        "years": "1892-1915",
        "mint_mark_locations": "Mint Mark Key: | Philadelphia - P (no mark) | New Orleans - O | San Francisco - S |",
        "wiki_url": "https://en.wikipedia.org/wiki/Barber_coinage",
        "scraper": "static",
    },
]


# ── Scrapers ─────────────────────────────────────────────────────────────────

def scrape_innovation(wiki_url: str) -> list[dict]:
    """Scrapes the American Innovation $1 Coin Program table."""
    log.info("Fetching: %s", wiki_url)
    req = urllib.request.Request(wiki_url, headers={"User-Agent": "NumistaAI-DataSync/1.0"})
    html = urllib.request.urlopen(req).read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    coins = []
    current_year = ""

    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            text = [c.get_text(separator=" ", strip=True) for c in row.find_all(["th", "td"])]
            if len(text) < 3:
                continue
            if re.match(r"^\d{4}$", text[0]):
                current_year = text[0]
                state, feature = text[2] if len(text) > 2 else "", text[3] if len(text) > 3 else ""
            elif re.match(r"^\d{1,2}$", text[0]) and current_year:
                state, feature = text[1] if len(text) > 1 else "", text[2] if len(text) > 2 else ""
            else:
                continue

            if not current_year or "Liberty Head" in state:
                continue

            state = re.sub(r"\[\d+\]", "", state).strip()
            feature = re.sub(r"\[\d+\]", "", feature).strip()
            name = f"{state} – {feature}" if feature and "TBA" not in feature else state

            coins.append({"year": current_year, "name": name, "varieties": ["P", "D", "S", "Proof"]})

    log.info("  Scraped %d coins.", len(coins))
    return coins


def scrape_women_quarters(wiki_url: str) -> list[dict]:
    """Scrapes the American Women Quarters table."""
    log.info("Fetching: %s", wiki_url)
    req = urllib.request.Request(wiki_url, headers={"User-Agent": "NumistaAI-DataSync/1.0"})
    html = urllib.request.urlopen(req).read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    coins = []
    current_year = ""

    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            text = [c.get_text(separator=" ", strip=True) for c in row.find_all(["th", "td"])]
            if len(text) < 2:
                continue
            year_match = re.match(r"^(\d{4})", text[0])
            if year_match:
                current_year = year_match.group(1)
                woman = text[2] if len(text) > 2 else ""
            elif re.match(r"^\d{1,2}$", text[0]) and current_year:
                woman = text[1] if len(text) > 1 else ""
            else:
                continue

            woman = re.sub(r"\[.*?\]", "", woman).strip()
            woman = re.sub(r"[\u02bb\u2018\u2019\u02bc]", "'", woman)
            if not woman or woman in ("Woman", "No.", "Year") or len(woman) > 60:
                continue

            coins.append({
                "year": current_year,
                "name": woman,
                "varieties": [
                    {"id": "P",       "label": "P"},
                    {"id": "D",       "label": "D"},
                    {"id": "S",       "label": "S"},
                    {"id": "S-PROOF", "label": "Proof"},
                ],
            })

    log.info("  Scraped %d coins.", len(coins))
    return coins

def scrape_native_american(wiki_url: str) -> list[dict]:
    """Returns the Sacagawea/Native American theme map. Semi-static since Wikipedia
    table structure varies; we use a curated theme dict and supplement from the page."""
    THEMES = {
        "2000": "Sacagawea & Eagle", "2001": "Sacagawea & Eagle",
        "2002": "Sacagawea & Eagle", "2003": "Sacagawea & Eagle",
        "2004": "Sacagawea & Eagle", "2005": "Sacagawea & Eagle",
        "2006": "Sacagawea & Eagle", "2007": "Sacagawea & Eagle",
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
    for year, theme in THEMES.items():
        varieties = [
            {"id": "P", "label": "P"},
            {"id": "D", "label": "D"},
            {"id": "S-PROOF", "label": "Proof"},
        ]
        coins.append({"year": year, "name": theme, "varieties": varieties})
    log.info("  Built %d Native American dollar entries.", len(coins))
    return coins



def scrape_presidential(wiki_url: str) -> list[dict]:
    """Returns the curated Presidential Dollar list (edge-lettered)."""
    PRESIDENTS = [
        ("2007","George Washington"),("2007","John Adams"),
        ("2007","Thomas Jefferson"),("2007","James Madison"),
        ("2008","James Monroe"),("2008","John Quincy Adams"),
        ("2008","Andrew Jackson"),("2008","Martin Van Buren"),
        ("2009","William Henry Harrison"),("2009","John Tyler"),
        ("2009","James K. Polk"),("2009","Zachary Taylor"),
        ("2010","Millard Fillmore"),("2010","Franklin Pierce"),
        ("2010","James Buchanan"),("2010","Abraham Lincoln"),
        ("2011","Andrew Johnson"),("2011","Ulysses S. Grant"),
        ("2011","Rutherford B. Hayes"),("2011","James Garfield"),
        ("2012","Chester Arthur"),("2012","Grover Cleveland (1st term)"),
        ("2012","Benjamin Harrison"),("2012","Grover Cleveland (2nd term)"),
        ("2013","William McKinley"),("2013","Theodore Roosevelt"),
        ("2013","William Howard Taft"),("2013","Woodrow Wilson"),
        ("2014","Warren G. Harding"),("2014","Calvin Coolidge"),
        ("2014","Herbert Hoover"),("2014","Franklin D. Roosevelt"),
        ("2015","Harry S. Truman"),("2015","Dwight D. Eisenhower"),
        ("2015","John F. Kennedy"),("2015","Lyndon B. Johnson"),
        ("2016","Richard Nixon"),("2016","Gerald Ford"),
        ("2016","Ronald Reagan"),("2020","George H.W. Bush"),
    ]
    coins = []
    for year, name in PRESIDENTS:
        coins.append({"year": year, "name": name,
            "varieties": [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S-PROOF","label":"Proof"}]})
    log.info("  Built %d Presidential Dollar entries.", len(coins))
    return coins


def scrape_atb_quarters(wiki_url: str) -> list[dict]:
    """Scrapes America the Beautiful Quarters (National Parks) from Wikipedia."""
    log.info("Fetching: %s", wiki_url)
    req = urllib.request.Request(wiki_url, headers={"User-Agent": "NumistaAI-DataSync/1.0"})
    html = urllib.request.urlopen(req).read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    coins = []
    current_year = ""
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        header = [c.get_text(strip=True) for c in rows[0].find_all(["th","td"])] if rows else []
        if "Jurisdiction" not in " ".join(header) and "Site" not in " ".join(header):
            continue
        for row in rows[1:]:
            text = [c.get_text(separator=" ", strip=True) for c in row.find_all(["th","td"])]
            if len(text) < 3: continue
            year_match = re.match(r"^(\d{4})", text[0])
            if year_match:
                current_year = year_match.group(1)
                state, site = (text[2] if len(text)>2 else ""), (text[3] if len(text)>3 else "")
            elif re.match(r"^\d{1,2}$", text[0]) and current_year:
                state, site = (text[1] if len(text)>1 else ""), (text[2] if len(text)>2 else "")
            else:
                continue
            state = re.sub(r"\[.*?\]", "", state).strip()
            site  = re.sub(r"\[.*?\]", "", site).strip()
            if not state or not site or "release" in site.lower(): continue
            coins.append({"year": current_year, "name": f"{site} ({state})",
                "varieties": [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S","label":"S"},{"id":"S-PROOF","label":"Proof"}]})
    log.info("  Scraped %d ATB Quarter entries.", len(coins))
    return coins



def scrape_state_quarters(wiki_url: str) -> list[dict]:
    """Curated 50 State Quarters (1999-2008)."""
    STATES = [
        ("1999","Delaware"),("1999","Pennsylvania"),("1999","New Jersey"),("1999","Georgia"),("1999","Connecticut"),
        ("2000","Massachusetts"),("2000","Maryland"),("2000","South Carolina"),("2000","New Hampshire"),("2000","Virginia"),
        ("2001","New York"),("2001","North Carolina"),("2001","Rhode Island"),("2001","Vermont"),("2001","Kentucky"),
        ("2002","Tennessee"),("2002","Ohio"),("2002","Louisiana"),("2002","Indiana"),("2002","Mississippi"),
        ("2003","Illinois"),("2003","Alabama"),("2003","Maine"),("2003","Missouri"),("2003","Arkansas"),
        ("2004","Michigan"),("2004","Florida"),("2004","Texas"),("2004","Iowa"),("2004","Wisconsin"),
        ("2005","California"),("2005","Minnesota"),("2005","Oregon"),("2005","Kansas"),("2005","West Virginia"),
        ("2006","Nevada"),("2006","Nebraska"),("2006","Colorado"),("2006","North Dakota"),("2006","South Dakota"),
        ("2007","Montana"),("2007","Washington"),("2007","Idaho"),("2007","Wyoming"),("2007","Utah"),
        ("2008","Oklahoma"),("2008","New Mexico"),("2008","Arizona"),("2008","Alaska"),("2008","Hawaii"),
    ]
    coins = [{"year":y,"name":n,"varieties":[{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S-PROOF","label":"S Proof"},{"id":"S-SILVER","label":"S Silver"}]} for y,n in STATES]
    log.info("  Built %d State Quarter entries.", len(coins))
    return coins


def scrape_dc_territories(wiki_url: str) -> list[dict]:
    """Curated D.C. & U.S. Territories Quarters (2009)."""
    TERRITORIES = ["District of Columbia","Puerto Rico","Guam","American Samoa","U.S. Virgin Islands","Northern Mariana Islands"]
    coins = [{"year":"2009","name":t,"varieties":[{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S-PROOF","label":"S Proof"}]} for t in TERRITORIES]
    log.info("  Built %d DC/Territory Quarter entries.", len(coins))
    return coins


def scrape_washington_classic(wiki_url: str) -> list[dict]:
    """Curated classic Washington Quarters (1932-1998) with era-accurate varieties."""
    coins = []
    for yr in list(range(1932,1965)) + [1965,1966,1967] + list(range(1968,1999)) + [2021]:
        if yr in (1933,1975): continue  # not minted
        if 1932 <= yr <= 1964:
            v = [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S","label":"S"}]
        elif yr in (1965,1966,1967):
            v = [{"id":"SMS","label":"SMS"}]
        elif yr == 1976:
            v = [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S-PROOF","label":"S Proof"},{"id":"S-SILVER","label":"S Silver"}]
        elif yr == 2021:
            v = [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S-PROOF","label":"S Proof"},{"id":"W","label":"W"}]
        else:
            v = [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S-PROOF","label":"S Proof"}]
        name = "Bicentennial Coinage" if yr == 1976 else ("Washington Crossing the Delaware" if yr == 2021 else "Washington Quarter")
        coins.append({"year": str(yr), "name": name, "varieties": v})
    log.info("  Built %d classic Washington Quarter entries.", len(coins))
    return coins


def scrape_kennedy(wiki_url: str) -> list[dict]:
    """Curated Kennedy Half Dollars with era-accurate varieties."""
    coins = []
    for yr in [y for y in list(range(1964,1976)) + [1976] + list(range(1977,2025)) if y != 1975]:
        if yr == 1964:
            v = [{"id":"P","label":"P"},{"id":"D","label":"D"}]
        elif yr in (1965,1966,1967):
            v = [{"id":"P","label":"P (40% Ag)"},{"id":"D","label":"D (40% Ag)"}]
        elif yr in (1968,1969):
            v = [{"id":"P","label":"P (40% Ag)"},{"id":"D","label":"D (40% Ag)"},{"id":"S-PROOF","label":"S Proof"}]
        elif yr == 1970:
            v = [{"id":"D","label":"D (40% Ag)"},{"id":"S-PROOF","label":"S Proof"}]
        elif yr in (1971,1972,1973,1974):
            v = [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S-PROOF","label":"S Proof"}]
        elif yr == 1976:
            v = [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S-PROOF","label":"S Proof"},{"id":"S-SILVER","label":"S Silver"}]
        else:
            v = [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S-PROOF","label":"S Proof"},{"id":"S-SILVER","label":"S Silver"}]
        name = "Bicentennial Coinage" if yr == 1976 else "Kennedy Half Dollar"
        coins.append({"year": str(yr), "name": name, "varieties": v})
    log.info("  Built %d Kennedy Half Dollar entries.", len(coins))
    return coins


def scrape_roosevelt(wiki_url: str) -> list[dict]:
    """Curated Roosevelt Dimes with era-accurate varieties."""
    coins = []
    for yr in range(1946, 2025):
        if 1946 <= yr <= 1964:
            v = [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S","label":"S"}]
        elif yr in (1965,1966,1967):
            v = [{"id":"SMS","label":"SMS"}]
        else:
            v = [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S-PROOF","label":"S Proof"}]
        coins.append({"year": str(yr), "name": "Roosevelt Dime", "varieties": v})
    log.info("  Built %d Roosevelt Dime entries.", len(coins))
    return coins


def scrape_jefferson(wiki_url: str) -> list[dict]:
    """Curated Jefferson Nickels with era-accurate varieties including War Nickels and Westward Journey."""
    WESTWARD = {2004: ["Peace Medal","Keelboat"], 2005: ["American Bison","Ocean in View"]}
    coins = []
    for yr in range(1938, 2025):
        if yr in (1942,1943,1944,1945):
            v = [{"id":"P","label":"P (Silver)"},{"id":"D","label":"D (Silver)"},{"id":"S","label":"S (Silver)"}]
            name = "War Nickel (35% Silver)"
        elif 1938 <= yr <= 1964:
            v = [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S","label":"S"}]
            name = "Jefferson Nickel"
        elif yr in (1965,1966,1967):
            v = [{"id":"P","label":"P"},{"id":"D","label":"D"}]
            name = "Jefferson Nickel"
        else:
            v = [{"id":"P","label":"P"},{"id":"D","label":"D"},{"id":"S-PROOF","label":"S Proof"}]
            name = "Jefferson Nickel"
        if yr in WESTWARD:
            for design in WESTWARD[yr]:
                coins.append({"year": str(yr), "name": design, "varieties": v})
        else:
            coins.append({"year": str(yr), "name": name, "varieties": v})
    log.info("  Built %d Jefferson Nickel entries.", len(coins))
    return coins


def _load_from_firestore_or_master(doc_id: str, wiki_url: str, log_label: str) -> list[dict] | None:
    """For static/historic series: Firestore is seeded once and never re-scraped.
    Returns None to signal a clean skip (distinct from an empty scrape = error)."""
    log.info("  %s is a static series — Firestore already seeded, skipping.", log_label)
    return None  # None = intentional no-op (not an error)


def scrape_lincoln(wiki_url: str) -> list[dict]:
    return _load_from_firestore_or_master("lincoln_cents", wiki_url, "Lincoln Cents")

def scrape_morgan(wiki_url: str) -> list[dict]:
    return _load_from_firestore_or_master("morgan_dollars", wiki_url, "Morgan Dollars")

def scrape_buffalo(wiki_url: str) -> list[dict]:
    return _load_from_firestore_or_master("buffalo_nickels", wiki_url, "Buffalo Nickels")

def scrape_mercury(wiki_url: str) -> list[dict]:
    return _load_from_firestore_or_master("mercury_dimes", wiki_url, "Mercury Dimes")


SCRAPER_MAP = {
    "innovation":         scrape_innovation,
    "women_quarters":     scrape_women_quarters,
    "native_american":    scrape_native_american,
    "presidential":       scrape_presidential,
    "atb_quarters":       scrape_atb_quarters,
    "state_quarters":     scrape_state_quarters,
    "dc_territories":     scrape_dc_territories,
    "washington_classic": scrape_washington_classic,
    "kennedy":            scrape_kennedy,
    "roosevelt":          scrape_roosevelt,
    "jefferson":          scrape_jefferson,
    "lincoln":            scrape_lincoln,
    "morgan":             scrape_morgan,
    "buffalo":            scrape_buffalo,
    "mercury":            scrape_mercury,
    "static":             scrape_lincoln,  # no-op: static series never needs re-scraping
}


# ── Firestore Sync ────────────────────────────────────────────────────────────

def sync_program(db: firestore.Client, program: dict, scraped_coins: list[dict]) -> None:
    doc_ref = db.collection(COLLECTION).document(program["doc_id"])
    snap = doc_ref.get()
    existing_coins = snap.to_dict().get("coins", []) if snap.exists else []

    existing_keys = {(c["year"], c["name"]) for c in existing_coins}
    scraped_keys  = {(c["year"], c["name"]) for c in scraped_coins}

    new_keys     = scraped_keys  - existing_keys
    removed_keys = existing_keys - scraped_keys

    if new_keys:
        log.info("  NEW coins (%d): %s", len(new_keys), new_keys)
    if removed_keys:
        log.info("  Removed from Wikipedia (%d): %s", len(removed_keys), removed_keys)

    if not new_keys and not removed_keys:
        log.info("  No changes — already up-to-date.")
        return

    doc_ref.set({
        "name":                program["name"],
        "category":            program["category"],
        "years":               program["years"],
        "mint_mark_locations": program["mint_mark_locations"],
        "coins":               scraped_coins,
        "last_synced":         firestore.SERVER_TIMESTAMP,
    }, merge=True)
    log.info("  Firestore updated with %d coins.", len(scraped_coins))



# ── Weekly US Mint Product Curation & GCS Upload ───────────────────────────────

import json

def slugify(text):
    if not text:
        return "none"
    return "".join(c if c.isalnum() else "_" for c in text.lower()).strip("_")

def rebuild_sqlite_and_upload_gcs(db):
    log.info("Rebuilding SQLite definitive_reference table from Firestore...")
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "numista_coins.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Query all from Firestore coins_reference
    col_ref = db.collection("coins_reference")
    docs = col_ref.stream()
    
    import sqlite3
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS definitive_reference (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year TEXT,
            denomination TEXT,
            mint_mark TEXT,
            variety TEXT,
            note TEXT,
            series TEXT,
            category TEXT,
            doc_id TEXT UNIQUE
        );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ref_lookup ON definitive_reference (year, mint_mark, category);")
    
    inserted = 0
    for doc in docs:
        d = doc.to_dict()
        doc_id = doc.id
        try:
            cur.execute("""
                INSERT OR REPLACE INTO definitive_reference 
                (year, denomination, mint_mark, variety, note, series, category, doc_id) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                d.get("year", ""),
                d.get("denomination", ""),
                d.get("mint_mark", ""),
                d.get("variety", ""),
                d.get("note", ""),
                d.get("series", ""),
                d.get("category", ""),
                doc_id
            ))
            inserted += 1
        except Exception as se:
            log.error("SQLite insert error: %s", se)
            
    conn.commit()
    conn.close()
    log.info("Successfully rebuilt SQLite database. Total rows: %d", inserted)
    
    # Upload to GCS
    log.info("Uploading rebuilt SQLite database to GCS...")
    try:
        from google.cloud import storage
        storage_client = storage.Client()
        bucket = storage_client.bucket("numista-reference-library")
        blob = bucket.blob("numista_coins.db")
        blob.upload_from_filename(db_path)
        log.info("Successfully uploaded database to GCS.")
    except Exception as ge:
        log.error("Failed to upload database to GCS: %s", ge)


def sync_usmint_product_schedule(db):
    log.info("--- Syncing US Mint 2026 Product Schedule ---")
    url = "https://catalog.usmint.gov/product-schedule/2026.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    products = []
    try:
        req = urllib.request.Request(url, headers=headers)
        html = urllib.request.urlopen(req, timeout=10).read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all("a", class_=re.compile(r"name|product|title", re.I)):
            name = link.get_text(strip=True)
            if name and name not in products:
                products.append(name)
        if not products:
            for item in soup.find_all(["div", "h3", "h4"]):
                text = item.get_text(strip=True)
                if "2026" in text and len(text) < 150:
                    products.append(text)
    except Exception as e:
        log.warning("Scraper failed directly: %s. Using Wikipedia/Fallback feed.", e)
        
    if not products:
        products = [
            "2026-P Semiquincentennial Clad Half Dollar - Liberty Bell Privy",
            "2026-D Semiquincentennial Clad Half Dollar - Liberty Bell Privy",
            "2026-S Semiquincentennial Clad Half Dollar Proof",
            "2026-P Semiquincentennial Silver Dollar - Liberty Bell Privy",
            "2026-W Semiquincentennial Silver Dollar Enhanced Uncirculated",
            "2026-S Semiquincentennial Silver Dollar Proof",
            "2026-P Semiquincentennial Gold Five Dollars",
            "2026-W Semiquincentennial Gold Five Dollars Proof"
        ]
        
    log.info("Found %d products to evaluate.", len(products))
    
    try:
        from google import genai
        from google.genai import types as genai_types
        genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    except Exception as ge:
        log.error("Failed to initialize GenAI client: %s", ge)
        return

    delta_found = False
    
    for prod in products[:15]:
        log.info("Evaluating product: %s", prod)
        
        prompt = f"""You are a senior numismatic expert.
Analyze this US Mint product release:
Product: {prod}

Extract the following fields and return as a JSON object:
- "year": string (e.g. "2026")
- "denomination": string (e.g., "One Cent", "Five Cents", "One Dime", "Quarter Dollar", "Half Dollar", "One Dollar", "Five Dollars", "Medal")
- "mint_mark": string (e.g. "P", "D", "S", "W", "O", "CC", or "" if none)
- "variety": string (e.g. "Liberty Bell 250 Privy Mark", "Enhanced Uncirculated", "Proof", or "" if standard)
- "note": string (short historical description or release details)
- "series": string (the program series name, e.g. "2026 U.S. Circulating Coins" or "United States Semiquincentennial Coins")
- "category": string (always "coin" or "medal")

Ensure the output is valid JSON. Do not wrap in markdown blocks.
"""
        try:
            response = genai_client.models.generate_content(
                model="gemini-3.5-flash",
                contents=[genai_types.Part.from_text(text=prompt)],
                config=genai_types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0
                )
            )
            raw_text = response.text.strip()
            item = json.loads(raw_text)
            
            year = str(item.get("year", "2026")).strip()
            denom = str(item.get("denomination", "")).strip()
            mint = str(item.get("mint_mark", "")).strip()
            variety = str(item.get("variety", "")).strip()
            note = str(item.get("note", "")).strip()
            series = str(item.get("series", "2026 U.S. Circulating Coins")).strip()
            category = str(item.get("category", "coin")).strip()
            
            doc_id = f"ref_coin_{slugify(series)}_{year}_{slugify(mint)}_{slugify(variety)}"[:100]
            
            doc_ref = db.collection("coins_reference").document(doc_id)
            if not doc_ref.get().exists:
                log.info("  [DELTA FOUND]: Adding new reference doc %s", doc_id)
                doc_ref.set({
                    "year": year,
                    "denomination": denom,
                    "mint_mark": mint,
                    "variety": variety,
                    "note": note,
                    "series": series,
                    "category": category,
                    "coin_id": doc_id
                })
                delta_found = True
            else:
                log.info("  Product already exists in reference catalog.")
                
        except Exception as e:
            log.error("  Error evaluating product: %s", e)
            
    if delta_found:
        log.info("New delta changes found. Recompiling database...")
        rebuild_sqlite_and_upload_gcs(db)
    else:
        log.info("No delta changes found. SQLite database is up-to-date.")


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    log.info("=== Numista.AI Data Sync Worker starting (%d programs) ===", len(PROGRAMS))
    db = firestore.Client(project=PROJECT_ID)

    for program in PROGRAMS:
        log.info("--- Syncing: %s ---", program["name"])
        scraper_fn = SCRAPER_MAP.get(program["scraper"])
        if not scraper_fn:
            log.warning("  No scraper found for '%s' — skipping.", program["scraper"])
            continue

        try:
            coins = scraper_fn(program["wiki_url"])
            if coins is None:
                log.info("  Static series — skipped (Firestore already seeded).")
                continue
            if not coins:
                log.error("  Scraper returned 0 coins — skipping to avoid data loss.")
                continue
            sync_program(db, program, coins)
        except Exception as e:
            log.error("  FAILED for %s: %s", program["name"], e)

    # Sync modern 2026 US Mint product schedule
    try:
        sync_usmint_product_schedule(db)
    except Exception as e:
        log.error("Failed syncing US Mint product schedule: %s", e)

    log.info("=== Sync complete ===")


if __name__ == "__main__":
    main()

