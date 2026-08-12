"""
Numista.AI Legislation Index Service
Provides versioned statutory public law references for coin programs and subjects.
Queries legislation data from Firestore/SQLite or returns authoritative static snapshots.
"""

from typing import Dict, Any, List, Optional

# Versioned statutory public law repository for coin programs and national sites
LEGISLATION_REGISTRY: Dict[str, List[Dict[str, Any]]] = {
    "america-the-beautiful": [
        {
            "id": "pl_110_456",
            "title": "America’s Beautiful National Parks Quarter Dollar Coin Act of 2008",
            "public_law": "Public Law 110-456",
            "statute_citation": "122 Stat. 5038 (31 U.S.C. § 5112(t))",
            "enactment_date": "2008-12-23",
            "congress_url": "https://www.congress.gov/bill/110th-congress/house-bill/6184",
            "summary": "Authorized the United States Mint to issue 56 quarter dollar coins honoring national parks and sites across all 50 states, DC, and 5 US territories from 2010 through 2021.",
            "type": "program_authorizing_act"
        }
    ],
    "tuskegee-airmen": [
        {
            "id": "pl_105_355",
            "title": "Tuskegee Airmen National Historic Site Act",
            "public_law": "Public Law 105-355",
            "statute_citation": "112 Stat. 3254 (16 U.S.C. § 461 note)",
            "enactment_date": "1998-11-06",
            "congress_url": "https://www.congress.gov/bill/105th-congress/house-bill/4230",
            "summary": "Established Moton Field in Tuskegee, Alabama as a National Historic Site to commemorate the heroic service of the Tuskegee Airmen in WWII.",
            "type": "site_authorizing_act"
        }
    ]
}


def get_legislation_for_coin(series_slug: str, subject_slug: str = "") -> List[Dict[str, Any]]:
    """
    Returns statutory legislation records matching program series or design subject.
    """
    results = []
    
    # Match program series laws
    if series_slug in LEGISLATION_REGISTRY:
        results.extend(LEGISLATION_REGISTRY[series_slug])
        
    # Match specific subject laws
    if subject_slug in LEGISLATION_REGISTRY:
        results.extend(LEGISLATION_REGISTRY[subject_slug])
        
    return results
