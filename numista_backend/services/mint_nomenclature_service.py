"""
Numista.AI Official US Mint Nomenclature Grounding Service
Translates informal collector jargon to official US Mint terms.
Ensures strict database grounding and canonical naming across all search & inventory functions.
"""

from typing import Dict, Any, List

NOMENCLATURE_MAP: Dict[str, str] = {
    "buffalo nickel": "Five Cents (Buffalo)",
    "silver eagle": "American Eagle One Ounce Silver Uncirculated Coin",
    "gold eagle": "American Eagle One Ounce Gold Coin",
    "half dollar": "Half Dollar",
    "quarter dollar": "Quarter Dollar",
    "pennies": "Cents",
    "nickles": "Five Cents",
    "quarters": "Quarter Dollars",
    "penny": "Cent",
    "nickel": "Five Cents",
    "dime": "Dime",
    "quarter": "Quarter Dollar",
}

def normalize_coin_nomenclature(text: str) -> str:
    """
    Translates informal text or denomination to official US Mint nomenclature.
    Example: '1909-S VDB Penny' -> '1909-S VDB Cent'
    """
    if not text:
        return text
        
    normalized = text
    # Sort keys by length descending so longer phrases take precedence
    sorted_map = sorted(NOMENCLATURE_MAP.items(), key=lambda x: len(x[0]), reverse=True)
    import re
    for informal, official in sorted_map:
        pattern = rf"\b{informal}\b"
        normalized = re.sub(pattern, official, normalized, flags=re.IGNORECASE)
        
    return normalized

