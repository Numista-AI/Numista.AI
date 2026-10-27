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
        "denomination": "Dollar",
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
        "denomination": "Dollar",
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
    "26XE": {
        "title": "2026 Morgan Silver Dollar (Enhanced Uncirculated)",
        "formal_name": "Morgan Silver Dollar 2026 Enhanced Uncirculated Coin",
        "year": 2026,
        "mint_mark": "",  # Struck at West Point without mint mark
        "mint_facility": "West Point (no mint mark)",
        "denomination": "Dollar",
        "program_series": "Morgan and Peace Silver Dollars",
        "theme_subject": "Morgan Dollar Enhanced Uncirculated (Liberty Bell 250 Privy, 1776~2026)",
        "variety": "Liberty Bell 250 Privy, 1776~2026 Dual Date",
        "strike_type": "Enhanced Uncirculated",
        "condition": "Enhanced Uncirculated",
        "metal_content": "99.9% Silver (0.859 oz ASW)",
        "purity": 0.999,
        "weight_grams": 26.73,
        "issue_price": "$169.00",
        "retailer": "United States Mint",
        "mintage_limit": 250000,
    },
    "26XH": {
        "title": "2026 Peace Silver Dollar (Enhanced Uncirculated)",
        "formal_name": "Peace Silver Dollar 2026 Enhanced Uncirculated Coin",
        "year": 2026,
        "mint_mark": "",  # Struck at West Point without mint mark
        "mint_facility": "West Point (no mint mark)",
        "denomination": "Dollar",
        "program_series": "Morgan and Peace Silver Dollars",
        "theme_subject": "Peace Dollar Enhanced Uncirculated (Liberty Bell 250 Privy, 1776~2026)",
        "variety": "Liberty Bell 250 Privy, 1776~2026 Dual Date",
        "strike_type": "Enhanced Uncirculated",
        "condition": "Enhanced Uncirculated",
        "metal_content": "99.9% Silver (0.859 oz ASW)",
        "purity": 0.999,
        "weight_grams": 26.73,
        "issue_price": "$169.00",
        "retailer": "United States Mint",
        "mintage_limit": 250000,
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
    # Official US Mint: https://catalog.usmint.gov/
    # Product 26SQRP: 2026 Semiquincentennial Presidential $1 Coin 25-Coin Roll ($61.00)
    # Note: Circulating $1 coins carry no mint mark on obverse/reverse. 26SQRD does not exist.
    "26SQRP": {
        "title": "2026 Semiquincentennial Presidential $1 Coin 25-Coin Roll",
        "formal_name": "2026 Semiquincentennial President Donald J. Trump $1 Coin 25-Coin Roll (Philadelphia)",
        "year": 2026,
        "pack_quantity": 25,
        "mint_mark": "",
        "mint_facility": "Philadelphia (P)",
        "denomination": "Dollar",
        "program_series": "Presidential $1 Coins",
        "theme_subject": "Donald J. Trump Semiquincentennial 250th Anniversary Presidential $1 Coin (Philadelphia)",
        "strike_type": "Circulating",
        "condition": "Uncirculated",
        "metal_content": "Manganese-Brass (88.5% Cu, 6% Zn, 3.5% Mn, 2% Ni)",
        "issue_price": "$61.00",
        "retailer": "United States Mint",
        "catalog_url": "https://catalog.usmint.gov/",
    },

    # ── 2026 Sets & Rolls (Plan.v3 C2 / IG-2) ─────────────────────────────────
    "26RJ": {
        "title": "2026 US Mint Uncirculated Coin Set (250th Anniversary)",
        "formal_name": "250th Anniversary 2026 Uncirculated Coin Set",
        "year": 2026,
        "mint_mark": "P & D",
        "mint_facility": "Philadelphia & Denver (P & D)",
        "denomination": "Set",
        "program_series": "Uncirculated Sets",
        "theme_subject": "250th Anniversary Uncirculated Coin Set",
        "strike_type": "Uncirculated",
        "condition": "Uncirculated",
        "metal_content": "Cupronickel / Clad",
        "is_set": True,
        "set_id": "uncirculated-coin-set-2026",
        "item_type": "set",
        "image_url_obverse": "https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_a.jpg",
        "image_url_reverse": "https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg",
        "issue_price": 124.50,
        "retailer": "United States Mint",
    },
    "26AGA": {
        "title": "2026 American Innovation $1 Coin 25-Coin Roll (Philadelphia)",
        "formal_name": "2026 American Innovation $1 Coin 25-Coin Roll - Philadelphia",
        "year": 2026,
        "pack_quantity": 25,
        "mint_mark": "",
        "mint_facility": "Philadelphia (P)",
        "denomination": "Dollar",
        "program_series": "American Innovation $1",
        "theme_subject": "American Innovation $1 Coin",
        "strike_type": "Circulating",
        "condition": "Uncirculated",
        "metal_content": "Manganese-Brass (88.5% Cu, 6% Zn, 3.5% Mn, 2% Ni)",
        "issue_price": "$45.00",
        "retailer": "United States Mint",
    },
    "26AGB": {
        "title": "2026 American Innovation $1 Coin 25-Coin Roll (Denver)",
        "formal_name": "2026 American Innovation $1 Coin 25-Coin Roll - Denver",
        "year": 2026,
        "pack_quantity": 25,
        "mint_mark": "",
        "mint_facility": "Denver (D)",
        "denomination": "Dollar",
        "program_series": "American Innovation $1",
        "theme_subject": "American Innovation $1 Coin",
        "strike_type": "Circulating",
        "condition": "Uncirculated",
        "metal_content": "Manganese-Brass (88.5% Cu, 6% Zn, 3.5% Mn, 2% Ni)",
        "issue_price": "$45.00",
        "retailer": "United States Mint",
    },
    "26GC": {
        "title": "2026 American Innovation $1 Coin Reverse Proof",
        "formal_name": "2026 American Innovation $1 Coin Reverse Proof Coin",
        "year": 2026,
        "mint_mark": "S",
        "mint_facility": "San Francisco (S)",
        "denomination": "Dollar",
        "program_series": "American Innovation $1",
        "theme_subject": "American Innovation $1 Coin",
        "strike_type": "Reverse Proof",
        "condition": "Reverse Proof",
        "metal_content": "Manganese-Brass",
        "issue_price": "$60.00",
        "retailer": "United States Mint",
    },

    # ── 2024 / 2023 Historical Reference Codes ───────────────────────────────
    "23RH": {
        "title": "2023 United States Mint Silver Proof Set",
        "formal_name": "2023 United States Mint Silver Proof Set",
        "year": 2023,
        "mint_mark": "S",
        "mint_facility": "San Francisco (S)",
        "denomination": "Set",
        "program_series": "Silver Proof Sets",
        "theme_subject": "Silver Proof Set 2023",
        "strike_type": "Proof",
        "condition": "Proof",
        "metal_content": "99.9% Silver",
        "is_set": True,
        "set_id": "silver-proof-set-2023",
        "item_type": "set",
        "issue_price": 130.00,
        "retailer": "United States Mint",
    },
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
    r"\bEnhanced Un\b": "Enhanced Uncirculated",
    r"\bEnh Uncirc\b": "Enhanced Uncirculated",
    r"\bEnh Uncirculated\b": "Enhanced Uncirculated",
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

    # If item number not present in Retailer Item No, search description and personal notes for known codes (e.g. 26XL, 26SQRP)
    raw_notes = str(item.get("Personal Notes") or item.get("personalNotes") or "").strip()
    search_corpus = f"{raw_desc} {raw_notes}".strip()
    if not catalog_match and search_corpus:
        for code in US_MINT_PRODUCT_CATALOG:
            if re.search(rf"\b{code}\b", search_corpus, re.IGNORECASE):
                catalog_match = US_MINT_PRODUCT_CATALOG[code]
                if not raw_item_no or raw_item_no.upper() in ("N/A", "UNKNOWN", "NONE"):
                    item["Retailer Item No."] = code
                break

    if catalog_match:
        logger.info(f"US Mint catalog hit for item '{raw_item_no}': {catalog_match['title']}")
        # Apply catalog fields
        if not item.get("Year") or str(item.get("Year")) in ("0", "Unknown", ""):
            item["Year"] = catalog_match["year"]
        
        # Only override or refine fields if they are generic or empty
        current_series = str(item.get("Program/Series") or "")
        if not current_series or "Invoice Import" in current_series or current_series == "USA" or current_series in ("Uncirculated Coin Set", "Uncirculated Coin Sets"):
            item["Program/Series"] = catalog_match["program_series"]

        current_denom = str(item.get("Denomination") or "")
        if not current_denom or current_denom in ("Coin", "Dollar", "One Ounce"):
            item["Denomination"] = catalog_match["denomination"]

        # Plan.v3 C2 / IG-2: Wrap Strike Type / Condition / Metal Content in fill-missing-only guards
        if not item.get("Strike Type") or item.get("Strike Type") in ("Unspecified", "Business", ""):
            item["Strike Type"] = catalog_match.get("strike_type", item.get("Strike Type", "Uncirculated"))
        if not item.get("Condition") or item.get("Condition") in ("Unspecified", ""):
            item["Condition"] = catalog_match.get("condition", item.get("Condition", "Uncirculated"))
        if not item.get("Metal Content") or item.get("Metal Content") in ("Unspecified", ""):
            item["Metal Content"] = catalog_match.get("metal_content", "99.9% Silver")
        
        # Mint facility / mark
        if not item.get("Mint Mark") and "mint_mark" in catalog_match:
            item["Mint Mark"] = catalog_match["mint_mark"]

        # Retailer normalization
        if not retailer or retailer in ("Unknown", ""):
            item["Retailer/Website"] = "United States Mint"

        # Theme/Subject refinement
        if not item.get("Theme/Subject") or item.get("Theme/Subject") in ("Coin", "Dollar", "Rever"):
            item["Theme/Subject"] = catalog_match["theme_subject"]

        # Variety refinement (e.g. Privy mark, dual date)
        if catalog_match.get("variety") and not item.get("Variety"):
            item["Variety"] = catalog_match["variety"]

        # Weight in grams (for accurate ASW calculation)
        if catalog_match.get("weight_grams") and not item.get("weight_grams"):
            item["weight_grams"] = catalog_match["weight_grams"]

        # Plan.v3 C2 / IG-2: fill-missing-only copy for set & image & valuation fields
        for fld in ("is_set", "set_id", "item_type", "image_url_obverse", "image_url_reverse", "issue_price"):
            if fld in catalog_match and not item.get(fld):
                item[fld] = catalog_match[fld]

        # Also fill item_number / retailer_item_num when blank
        sku_code = catalog_match.get("code") or raw_item_no
        if sku_code:
            if not item.get("Retailer Item No."):
                item["Retailer Item No."] = sku_code
            if not item.get("retailer_item_num"):
                item["retailer_item_num"] = sku_code
            if not item.get("item_number"):
                item["item_number"] = sku_code

        # If mint facility is recorded, note in Personal Notes if not already present
        facility = catalog_match.get("mint_facility", "")
        if facility:
            existing_notes = str(item.get("Personal Notes") or "").strip()
            facility_note = f"Mint Facility: {facility}"
            if facility_note not in existing_notes:
                item["Personal Notes"] = f"{existing_notes} | {facility_note}".strip(" |")

        # Pack Quantity Expansion (C1, C2, B1, B2, B4)
        pack_qty = catalog_match.get("pack_quantity")
        if pack_qty and isinstance(pack_qty, int) and pack_qty > 1 and not item.get("pack_expanded"):
            raw_qty = item.get("Quantity") or item.get("quantity") or 1
            try:
                curr_qty = int(raw_qty)
            except (ValueError, TypeError):
                curr_qty = 1
                
            # C2: Guard against expanding if quantity is already a multiple of pack_qty or > 10
            if curr_qty <= 10 and (curr_qty % pack_qty != 0):
                new_qty = curr_qty * pack_qty
                item["Quantity"] = new_qty
                item["quantity"] = new_qty
                item["pack_expanded"] = True
                item["pack_quantity_multiplier"] = pack_qty

                # Override Cost/Allocated Fees with canonical catalog unit price if available (NET-538 / NET-539)
                cat_issue_price = catalog_match.get("issue_price") or catalog_match.get("unit_price")
                if cat_issue_price:
                    try:
                        clean_cat_price = float(re.sub(r"[^\d.]", "", str(cat_issue_price)))
                        if clean_cat_price > 0.0:
                            canonical_lot_cost = round(clean_cat_price * curr_qty, 2)
                            alloc_fees = float(item.get("Allocated Fees") or item.get("allocated_fees") or 0.0)
                            item["Sticker Price"] = canonical_lot_cost
                            item["Allocated Fees"] = alloc_fees
                            item["Cost"] = round(canonical_lot_cost + alloc_fees, 2)
                            item["Purchase Cost"] = round(canonical_lot_cost + alloc_fees, 2)
                            item["cost"] = round(canonical_lot_cost + alloc_fees, 2)
                    except Exception as e:
                        logger.warning(f"Failed parsing cat_issue_price '{cat_issue_price}': {e}")
                
                # B2/B4: Ensure unit_cost is calculated from lot total Cost
                cost_val = item.get("Cost") or item.get("Purchase Cost") or item.get("cost") or 0.0
                try:
                    cost_float = float(cost_val)
                    if cost_float > 0.0:
                        unit_c = round(cost_float / new_qty, 4)
                        item["unit_cost"] = unit_c
                        item["set_cost_label"] = f"${cost_float:.2f} ({new_qty} @ ${cost_float / new_qty:.2f})"
                except (ValueError, TypeError):
                    pass

        item["_catalog_grounded"] = True

    return item
