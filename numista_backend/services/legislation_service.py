"""
Numista.AI Legislation Index Service
Provides versioned statutory public law references for coin programs and subjects.
Queries legislation data from Firestore/SQLite or returns authoritative static snapshots.
"""

from typing import Dict, Any, List, Optional
import re

def slugify_law_key(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"[\s-]+", "-", s)

# Versioned statutory public law repository for coin programs and national sites
LEGISLATION_REGISTRY: Dict[str, List[Dict[str, Any]]] = {
    "america-the-beautiful": [
        {
            "id": "pl_110_456",
            "public_law_key": "110-456",
            "title": "America’s Beautiful National Parks Quarter Dollar Coin Act of 2008",
            "name": "America’s Beautiful National Parks Quarter Dollar Coin Act of 2008",
            "public_law": "110-456",
            "bill_number": "H.R. 6184",
            "statute_citation": "122 Stat. 5038 (31 U.S.C. § 5112(t))",
            "enacted": "December 23, 2008",
            "enactment_date": "2008-12-23",
            "congress": "110th Congress (2007–2008)",
            "chamber": "House / Senate",
            "actions_count": 8,
            "congress_url": "https://www.congress.gov/bill/110th-congress/house-bill/6184",
            "description": "Authorized the United States Mint to issue 56 quarter dollar coins honoring national parks and sites across all 50 states, the District of Columbia, and 5 US territories from 2010 through 2021.",
            "summary": "Authorized the United States Mint to issue 56 quarter dollar coins honoring national parks and sites across all 50 states, DC, and 5 US territories from 2010 through 2021.",
            "type": "program_authorizing_act"
        }
    ],
    "50-state-quarters": [
        {
            "id": "pl_105_124",
            "public_law_key": "105-124",
            "title": "50 States Commemorative Coin Program Act",
            "name": "50 States Commemorative Coin Program Act",
            "public_law": "105-124",
            "bill_number": "H.R. 2414",
            "statute_citation": "111 Stat. 2534 (31 U.S.C. § 5112(k))",
            "enacted": "December 1, 1997",
            "enactment_date": "1997-12-01",
            "congress": "105th Congress (1997–1998)",
            "chamber": "House / Senate",
            "actions_count": 12,
            "congress_url": "https://www.congress.gov/bill/105th-congress/house-bill/2414",
            "description": "Authorized a 10-year circulating commemorative coin program honoring each of the 50 United States in the order they ratified the Constitution or were admitted into the Union (1999–2008).",
            "summary": "Authorized a 10-year commemorative quarter program honoring all 50 States (1999–2008).",
            "type": "program_authorizing_act"
        }
    ],
    "district-of-columbia-and-us-territories": [
        {
            "id": "pl_110_161",
            "public_law_key": "110-161",
            "title": "District of Columbia and United States Territories Circulating Quarter Dollar Program Act",
            "name": "Consolidated Appropriations Act, 2008 (Div. D, Title VI, § 622 — DC & Territories Quarters)",
            "public_law": "110-161",
            "bill_number": "H.R. 2764",
            "statute_citation": "121 Stat. 2014 (31 U.S.C. § 5112(r))",
            "enacted": "December 26, 2007",
            "enactment_date": "2007-12-26",
            "congress": "110th Congress (2007–2008)",
            "chamber": "House / Senate",
            "actions_count": 15,
            "congress_url": "https://www.congress.gov/bill/110th-congress/house-bill/2764",
            "description": "Authorized 6 quarter dollars issued in 2009 honoring the District of Columbia, Puerto Rico, Guam, American Samoa, the U.S. Virgin Islands, and the Northern Mariana Islands.",
            "summary": "Authorized the 2009 DC and U.S. Territories Quarter Program.",
            "type": "program_authorizing_act"
        }
    ],
    "american-women-quarters": [
        {
            "id": "pl_116_330",
            "public_law_key": "116-330",
            "title": "Circulating Collectible Coin Redesign Act of 2020",
            "name": "Circulating Collectible Coin Redesign Act of 2020 (American Women Quarters)",
            "public_law": "116-330",
            "bill_number": "H.R. 1923",
            "statute_citation": "134 Stat. 5101 (31 U.S.C. § 5112(z))",
            "enacted": "January 13, 2021",
            "enactment_date": "2021-01-13",
            "congress": "116th Congress (2019–2020)",
            "chamber": "House / Senate",
            "actions_count": 9,
            "congress_url": "https://www.congress.gov/bill/116th-congress/house-bill/1923",
            "description": "Authorized up to five quarter dollar designs per year from 2022 through 2025 celebrating prominent American women and their contributions to the nation.",
            "summary": "Authorized American Women Quarters (2022–2025).",
            "type": "program_authorizing_act"
        }
    ],
    "presidential-dollars": [
        {
            "id": "pl_109_145",
            "public_law_key": "109-145",
            "title": "Presidential $1 Coin Act of 2005",
            "name": "Presidential $1 Coin Act of 2005",
            "public_law": "109-145",
            "bill_number": "S. 1047",
            "statute_citation": "119 Stat. 2664 (31 U.S.C. § 5112(p))",
            "enacted": "December 22, 2005",
            "enactment_date": "2005-12-22",
            "congress": "109th Congress (2005–2006)",
            "chamber": "Senate / House",
            "actions_count": 10,
            "congress_url": "https://www.congress.gov/bill/109th-congress/senate-bill/1047",
            "description": "Authorized $1 coins honoring former Presidents of the United States in the order of their service (2007–2016).",
            "summary": "Authorized Presidential $1 Coins (2007–2016).",
            "type": "program_authorizing_act"
        }
    ],
    "american-silver-eagle": [
        {
            "id": "pl_99_61",
            "public_law_key": "99-61",
            "title": "Liberty Coin Act",
            "name": "Liberty Coin Act (Title II — American Silver Eagle)",
            "public_law": "99-61",
            "bill_number": "H.R. 47",
            "statute_citation": "99 Stat. 113 (31 U.S.C. § 5112(e))",
            "enacted": "July 9, 1985",
            "enactment_date": "1985-07-09",
            "congress": "99th Congress (1985–1986)",
            "chamber": "House / Senate",
            "actions_count": 6,
            "congress_url": "https://www.congress.gov/bill/99th-congress/house-bill/47",
            "description": "Authorized the minting and issuance of American Silver Eagle 1 oz bullion coins containing .999 fine silver.",
            "summary": "Authorized American Silver Eagle bullion coins.",
            "type": "program_authorizing_act"
        }
    ],
    "tuskegee-airmen": [
        {
            "id": "pl_105_355",
            "public_law_key": "105-355",
            "title": "Tuskegee Airmen National Historic Site Act",
            "name": "Tuskegee Airmen National Historic Site Act",
            "public_law": "105-355",
            "bill_number": "H.R. 4230",
            "statute_citation": "112 Stat. 3254 (16 U.S.C. § 461 note)",
            "enacted": "November 6, 1998",
            "enactment_date": "1998-11-06",
            "congress": "105th Congress (1997–1998)",
            "chamber": "House / Senate",
            "actions_count": 7,
            "congress_url": "https://www.congress.gov/bill/105th-congress/house-bill/4230",
            "description": "Established Moton Field in Tuskegee, Alabama as a National Historic Site to commemorate the heroic service of the Tuskegee Airmen in WWII.",
            "summary": "Established Moton Field in Tuskegee, Alabama as a National Historic Site.",
            "type": "site_authorizing_act"
        }
    ]
}

# Aliases mapping variants to canonical registry keys
ALIASES: Dict[str, str] = {
    "atb": "america-the-beautiful",
    "atb-quarters": "america-the-beautiful",
    "america-the-beautiful-quarters": "america-the-beautiful",
    "national-park-quarters": "america-the-beautiful",
    "state-quarters": "50-state-quarters",
    "statehood-quarters": "50-state-quarters",
    "50-state": "50-state-quarters",
    "50-states": "50-state-quarters",
    "dc-territories": "district-of-columbia-and-us-territories",
    "dc-and-territories": "district-of-columbia-and-us-territories",
    "dc-and-us-territories": "district-of-columbia-and-us-territories",
    "district-of-columbia": "district-of-columbia-and-us-territories",
    "women-quarters": "american-women-quarters",
    "silver-eagle": "american-silver-eagle",
    "silver-eagles": "american-silver-eagle",
    "presidential-dollar": "presidential-dollars",
}

def get_legislation_for_coin(series_slug: str, subject_slug: str = "") -> List[Dict[str, Any]]:
    """
    Returns statutory legislation records matching program series or design subject.
    """
    results = []
    
    s_key = slugify_law_key(series_slug)
    s_canon = ALIASES.get(s_key, s_key)
    if s_canon in LEGISLATION_REGISTRY:
        results.extend(LEGISLATION_REGISTRY[s_canon])
        
    if subject_slug:
        sub_key = slugify_law_key(subject_slug)
        sub_canon = ALIASES.get(sub_key, sub_key)
        if sub_canon in LEGISLATION_REGISTRY:
            results.extend(LEGISLATION_REGISTRY[sub_canon])
        
    return results

def get_all_laws_dict() -> Dict[str, Dict[str, Any]]:
    """Returns a flat dictionary keyed by law key ('110-456') for metadata/coin_legislation."""
    laws = {}
    for program_key, law_list in LEGISLATION_REGISTRY.items():
        for law in law_list:
            key = law.get("public_law_key") or law.get("public_law", "")
            if key:
                laws[key] = law
    return laws
