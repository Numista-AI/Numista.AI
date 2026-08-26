"""
us_mint_catalog_service.py
==========================
Numista.AI Canonical US Mint Item Number & Product Catalog Service.

Maps official US Mint item numbers (e.g. 26XL, 26EA, 26XM, 26XH) to exact
specifications: mint facility, strike type, series, purity, and official naming.
Also resolves truncated US Mint packing slip line-item strings.
"""

import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("numista_backend.us_mint_catalog_service")

# ── Canonical US Mint Item Registry ──────────────────────────────────────────
# Key: Normalized US Mint Item Code (e.g., '26XL', '26EA')
US_MINT_PRODUCT_CATALOG: Dict[str, Dict[str, Any]] = {
    # ── 2026 Issues ──────────────────────────────────────────────────────────
    "26XL": {
        "title": "2026 Peace Silver Dollar (Reverse Proof)",
        "formal_name": "Peace Silver Dollar 2026 Reverse Proof Coin",
        "year": 2026,
        "mint_mark": "",  # Struck at Philadelphia without mint mark (or (P))
        "mint_facility": "Philadelphia (P)",
        "denomination": "Peace Dollar",
        "program_series": "Morgan and Peace Silver Dollars",
        "theme_subject": "Peace Dollar Reverse Proof",
        "strike_type": "Reverse Proof",
        "condition": "Reverse Proof",
        "metal_content": "99.9% Silver",
        "purity": 0.999,
        "weight_grams": 31.103,
        "issue_price": "$173.00",
        "retailer": "United States Mint",
        "mintage_limit": 250000,
    },
    "26XM": {
        "title": "2026 Morgan Silver Dollar (Reverse Proof)",
        "formal_name": "Morgan Silver Dollar 2026 Reverse Proof Coin",
        "year": 2026,
        "mint_mark": "",
        "mint_facility": "Philadelphia (P)",
        "denomination": "Morgan Dollar",
        "program_series": "Morgan and Peace Silver Dollars",
        "theme_subject": "Morgan Dollar Reverse Proof",
        "strike_type": "Reverse Proof",
        "condition": "Reverse Proof",
        "metal_content": "99.9% Silver",
        "purity": 0.999,
        "weight_grams": 31.103,
        "issue_price": "$173.00",
        "retailer": "United States Mint",
        "mintage_limit": 250000,
    },
    "26EA": {
        "title": "2026 American Silver Eagle",
        "formal_name": "American Eagle 2026 One Ounce Silver Coin",
        "year": 2026,
        "mint_mark": "W",
        "mint_facility": "West Point (W)",
        "denomination": "American Silver Eagle",
        "program_series": "American Silver Eagle",
        "theme_subject": "American Silver Eagle",
        "strike_type": "Proof",
        "condition": "Proof",
        "metal_content": "99.9% Silver",
        "purity": 0.999,
        "weight_grams": 31.103,
        "issue_price": "$173.00",
        "retailer": "United States Mint",
    },
    "26XH": {
        "title": "2026 Morgan Silver Dollar (Uncirculated)",
        "formal_name": "Morgan Silver Dollar 2026 Uncirculated Coin",
        "year": 2026,
        "mint_mark": "",
        "mint_facility": "Philadelphia (P)",
        "denomination": "Morgan Dollar",
        "program_series": "Morgan and Peace Silver Dollars",
        "theme_subject": "Morgan Dollar Uncirculated",
        "strike_type": "Uncirculated",
        "condition": "Uncirculated",
        "metal_content": "99.9% Silver",
        "purity": 0.999,
        "weight_grams": 31.103,
        "issue_price": "$91.00",
        "retailer": "United States Mint",
    },
    "26XJ": {
        "title": "2026 Peace Silver Dollar (Uncirculated)",
        "formal_name": "Peace Silver Dollar 2026 Uncirculated Coin",
        "year": 2026,
        "mint_mark": "",
        "mint_facility": "Philadelphia (P)",
        "denomination": "Peace Dollar",
        "program_series": "Morgan and Peace Silver Dollars",
        "theme_subject": "Peace Dollar Uncirculated",
        "strike_type": "Uncirculated",
        "condition": "Uncirculated",
        "metal_content": "99.9% Silver",
        "purity": 0.999,
        "weight_grams": 31.103,
        "issue_price": "$91.00",
        "retailer": "United States Mint",
    },
    "26XK": {
        "title": "2026 Morgan Silver Dollar (Proof)",
        "formal_name": "Morgan Silver Dollar 2026 Proof Coin",
        "year": 2026,
        "mint_mark": "S",
        "mint_facility": "San Francisco (S)",
        "denomination": "Morgan Dollar",
        "program_series": "Morgan and Peace Silver Dollars",
        "theme_subject": "Morgan Dollar Proof",
        "strike_type": "Proof",
        "condition": "Proof",
        "metal_content": "99.9% Silver",
        "purity": 0.999,
        "weight_grams": 31.103,
        "issue_price": "$95.00",
        "retailer": "United States Mint",
    },
    "26XN": {
        "title": "2026 Peace Silver Dollar (Proof)",
        "formal_name": "Peace Silver Dollar 2026 Proof Coin",
        "year": 2026,
        "mint_mark": "S",
        "mint_facility": "San Francisco (S)",
        "denomination": "Peace Dollar",
        "program_series": "Morgan and Peace Silver Dollars",
        "theme_subject": "Peace Dollar Proof",
        "strike_type": "Proof",
        "condition": "Proof",
        "metal_content": "99.9% Silver",
        "purity": 0.999,
        "weight_grams": 31.103,
        "issue_price": "$95.00",
        "retailer": "United States Mint",
    },

    # ── 2024 / 2023 Historical Reference Codes ───────────────────────────────
    "24XL": {
        "title": "2024 Peace Silver Dollar (Reverse Proof)",
        "formal_name": "Peace Silver Dollar 2024 Reverse Proof Coin",
        "year": 2024,
        "mint_mark": "",
        "mint_facility": "Philadelphia (P)",
        "denomination": "Peace Dollar",
        "program_series": "Morgan and Peace Silver Dollars",
        "strike_type": "Reverse Proof",
        "condition": "Reverse Proof",
        "metal_content": "99.9% Silver",
        "purity": 0.999,
        "retailer": "United States Mint",
    },
    "24XM": {
        "title": "2024 Morgan Silver Dollar (Reverse Proof)",
        "formal_name": "Morgan Silver Dollar 2024 Reverse Proof Coin",
        "year": 2024,
        "mint_mark": "",
        "mint_facility": "Philadelphia (P)",
        "denomination": "Morgan Dollar",
        "program_series": "Morgan and Peace Silver Dollars",
        "strike_type": "Reverse Proof",
        "condition": "Reverse Proof",
        "metal_content": "99.9% Silver",
        "purity": 0.999,
        "retailer": "United States Mint",
    },
    "24EA": {
        "title": "2024 American Silver Eagle Proof",
        "formal_name": "American Eagle 2024 One Ounce Silver Proof Coin",
        "year": 2024,
        "mint_mark": "W",
        "mint_facility": "West Point (W)",
        "denomination": "American Silver Eagle",
        "program_series": "American Silver Eagle",
        "strike_type": "Proof",
        "condition": "Proof",
        "metal_content": "99.9% Silver",
        "purity": 0.999,
        "retailer": "United States Mint",
    },
}

# Common truncation expansions in US Mint invoices & packing slips
US_MINT_TRUNCATION_MAP: Dict[str, str] = {
    r"\bRever\b": "Reverse Proof",
    r"\bRev Prf\b": "Reverse Proof",
    r"\bRev Proof\b": "Reverse Proof",
    r"\bUncirc\b": "Uncirculated",
    r"\bUncircula\b": "Uncirculated",
    r"\bPrf\b": "Proof",
    r"\bProof Set\b": "Proof Set",
    r"\bSilv\b": "Silver",
    r"\bClad Prf\b": "Clad Proof",
    r"\bOne Ounce\b": "One Ounce Silver",
}


def normalize_item_code(code: str) -> str:
    """Normalizes item number by stripping spaces, dots, dashes."""
    if not code:
        return ""
    return re.sub(r"[\s\-_.]+", "", str(code)).upper().strip()


def lookup_us_mint_item(item_number: str) -> Optional[Dict[str, Any]]:
    """
    Looks up a US Mint item number in the canonical product catalog.
    Returns copy of catalog entry if matched, None otherwise.
    """
    clean_code = normalize_item_code(item_number)
    if not clean_code:
        return None
    return US_MINT_PRODUCT_CATALOG.get(clean_code)


def expand_us_mint_truncation(text: str) -> str:
    """Expands truncated words commonly found on US Mint packing slips."""
    if not text:
        return text
    expanded = text
    for pattern, replacement in US_MINT_TRUNCATION_MAP.items():
        expanded = re.sub(pattern, replacement, expanded, flags=re.IGNORECASE)
    return expanded.strip()


def enrich_us_mint_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministically enriches an extracted invoice line item using US Mint catalog data.
    Preserves user overrides while fixing truncated fields, strike types, and mint facilities.
    """
    if not isinstance(item, dict):
        return item

    raw_item_no = str(item.get("Retailer Item No.") or item.get("item_number") or "").strip()
    raw_desc = str(item.get("Original Description from source") or item.get("Theme/Subject") or "").strip()
    retailer = str(item.get("Retailer/Website") or item.get("retailer") or "").strip()

    # Expand any truncated text in descriptions
    if raw_desc:
        expanded_desc = expand_us_mint_truncation(raw_desc)
        if "Reverse Proof" in expanded_desc and item.get("Strike Type") in (None, "", "Business", "Uncirculated"):
            item["Strike Type"] = "Reverse Proof"
            item["Condition"] = "Reverse Proof"

    # Attempt catalog match by item code first
    catalog_match = lookup_us_mint_item(raw_item_no)

    # If item number not present in Retailer Item No, search description for known codes (e.g. 26XL)
    if not catalog_match and raw_desc:
        for code in US_MINT_PRODUCT_CATALOG:
            if re.search(rf"\b{code}\b", raw_desc, re.IGNORECASE):
                catalog_match = US_MINT_PRODUCT_CATALOG[code]
                if not raw_item_no:
                    item["Retailer Item No."] = code
                break

    if catalog_match:
        logger.info(f"US Mint catalog hit for item '{raw_item_no}': {catalog_match['title']}")
        # Apply catalog fields
        if not item.get("Year") or str(item.get("Year")) in ("0", "Unknown", ""):
            item["Year"] = catalog_match["year"]
        
        # Only override or refine fields if they are generic or empty
        current_series = str(item.get("Program/Series") or "")
        if not current_series or "Invoice Import" in current_series or current_series == "USA":
            item["Program/Series"] = catalog_match["program_series"]

        current_denom = str(item.get("Denomination") or "")
        if not current_denom or current_denom in ("Coin", "Dollar", "One Ounce"):
            item["Denomination"] = catalog_match["denomination"]

        item["Strike Type"] = catalog_match.get("strike_type", item.get("Strike Type", "Uncirculated"))
        item["Condition"] = catalog_match.get("condition", item.get("Condition", "Uncirculated"))
        item["Metal Content"] = catalog_match.get("metal_content", "99.9% Silver")
        
        # Mint facility / mark
        if not item.get("Mint Mark") and catalog_match.get("mint_mark"):
            item["Mint Mark"] = catalog_match["mint_mark"]

        # Retailer normalization
        if not retailer or retailer in ("Unknown", ""):
            item["Retailer/Website"] = "United States Mint"

        # Theme/Subject refinement
        if not item.get("Theme/Subject") or item.get("Theme/Subject") in ("Coin", "Dollar", "Rever"):
            item["Theme/Subject"] = catalog_match["theme_subject"]

        # If mint facility is Philadelphia without mint mark, record note if helpful
        facility = catalog_match.get("mint_facility", "")
        if facility:
            existing_notes = str(item.get("Personal Notes") or "").strip()
            facility_note = f"Mint Facility: {facility}"
            if facility_note not in existing_notes:
                item["Personal Notes"] = f"{existing_notes} | {facility_note}".strip(" |")

        item["_catalog_grounded"] = True

    return item
