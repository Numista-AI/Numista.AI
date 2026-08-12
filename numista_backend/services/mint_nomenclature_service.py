"""
Numista.AI Official US Mint Nomenclature Grounding Service
Translates informal collector jargon to official US Mint terms.
Ensures strict database grounding and canonical naming across all search & inventory functions.
"""

import os
import re
import sqlite3
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("mint_nomenclature_service")

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

# State/Subject mapping matching CoinImageService._subjectSlugMap
SUBJECT_STATE_MAP: Dict[str, str] = {
    "san antonio missions": "texas",
    "san antonio missions national historical park": "texas",
    "lowell": "massachusetts",
    "lowell national historical park": "massachusetts",
    "american memorial park": "northern-mariana-islands",
    "war in the pacific": "guam",
    "war in the pacific national historical park": "guam",
    "frank church": "idaho",
    "frank church river of no return wilderness": "idaho",
    "national park of american samoa": "american-samoa",
    "weir farm": "connecticut",
    "weir farm national historical park": "connecticut",
    "salt river bay": "us-virgin-islands",
    "salt river bay national historical park": "us-virgin-islands",
    "marsh-billings-rockefeller": "vermont",
    "marsh-billings-rockefeller national historical park": "vermont",
    "tallgrass prairie": "kansas",
    "tallgrass prairie national preserve": "kansas",
    "tuskegee airmen": "alabama",
    "tuskegee airmen national historic site": "alabama",
    "crossing the delaware": "new-jersey",
}


def slugify(text: str) -> str:
    """
    Standard canonical slugification rule:
    Lowercased, stripped of non-alphanumeric characters (except spaces/hyphens), spaces replaced with hyphens.
    Example: "San Antonio Missions" -> "san-antonio-missions"
             "America the Beautiful Quarters" -> "america-the-beautiful"
    """
    if not text:
        return ""
    t = text.lower().strip()
    t = re.sub(
        r"\b(quarters|quarter|cents|cent|dollars|dollar|half dollars|half dollar|nickels|nickel|dimes|dime|national historical park|national park|national monument|national forest|national lakeshore|national seashore|national military park|national scenic riverways|national preserve)\b",
        "",
        t,
    )
    t = re.sub(r"[^\w\s-]", "", t).strip()
    return re.sub(r"[\s_]+", "-", t)


def sanitize_denomination_title(denom: str) -> str:
    """
    Sanitizes denomination titles, stripping duplicate suffix tokens.
    Example: 'Quarter Dollar Dollar' -> 'Quarter Dollar'
    """
    if not denom:
        return denom
    cleaned = re.sub(r'\b(Dollar|Cent|Nickel|Dime)\s+\1\b', r'\1', denom, flags=re.IGNORECASE)
    return cleaned.strip()


def normalize_coin_nomenclature(text: str) -> str:
    """
    Translates informal text or denomination to official US Mint nomenclature.
    Example: '1909-S VDB Penny' -> '1909-S VDB Cent'
    """
    if not text:
        return text

    normalized = text
    sorted_map = sorted(NOMENCLATURE_MAP.items(), key=lambda x: len(x[0]), reverse=True)
    for informal, official in sorted_map:
        pattern = rf"\b{informal}\b"
        normalized = re.sub(pattern, official, normalized, flags=re.IGNORECASE)

    return sanitize_denomination_title(normalized)


def resolve_coin_catalog_metadata(
    year: str,
    denomination: str,
    mint_mark: str = "",
    program_series: str = "",
    theme_subject: str = "",
    variety: str = ""
) -> Dict[str, Any]:
    """
    Catalog-driven coin metadata resolution.
    Queries definitive_reference in SQLite numista_coins.db.
    Returns canonical program_series, theme_subject, variety, slugs, country, is_foreign, and baseline valuation.

    NO-MATCH CONTRACT: On zero matches, preserves raw user/Morgan input as-is or sets 'Unmapped'.
    Never invents synthesized generic strings like 'f"{year} {denomination}"'.
    """
    norm_denom = sanitize_denomination_title(normalize_coin_nomenclature(denomination or "").strip())
    if norm_denom in ["Quarter", "25c", "25 Cents"]:
        norm_denom = "Quarter Dollar"
    elif norm_denom in ["Cent", "Penny", "1c"]:
        norm_denom = "Cent"

    raw_series = (program_series or "").strip()
    raw_theme = (theme_subject or "").strip()
    raw_variety = (variety or "").strip()

    # Default result (unmapped / fail-closed baseline)
    result = {
        "year": str(year).strip(),
        "mint_mark": (mint_mark or "").strip().upper(),
        "denomination": norm_denom or "Quarter Dollar",
        "program_series": raw_series or "Unmapped / General Collection",
        "series_slug": slugify(raw_series or "unmapped"),
        "theme_subject": raw_theme or "Unmapped",
        "subject_slug": slugify(raw_theme or "unmapped"),
        "variety": raw_variety,
        "country": "United States",
        "is_foreign": False,
        "estimated_value": None,
        "valuation_source": "Unmapped – Manual Review Required",
        "catalog_matched": False,
    }

    # Attempt catalog lookup
    try:
        from numista_scraper.config import DB_PATH
        if os.path.exists(str(DB_PATH)):
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            search_query = f"%{raw_theme or raw_variety or raw_series}%"
            if search_query != "%%":
                cur.execute(
                    "SELECT year, denomination, series, variety, composition "
                    "FROM definitive_reference WHERE (variety LIKE ? OR series LIKE ? OR note LIKE ?) "
                    "AND year LIKE ? LIMIT 1",
                    (search_query, search_query, search_query, f"%{year}%")
                )
                row = cur.fetchone()
            else:
                row = None

            # Only fallback to generic year + denomination if no specific theme/series was requested
            if not row and not raw_theme and not raw_series:
                cur.execute(
                    "SELECT year, denomination, series, variety, composition "
                    "FROM definitive_reference WHERE year LIKE ? AND denomination LIKE ? LIMIT 1",
                    (f"%{year}%", f"%{norm_denom}%")
                )
                row = cur.fetchone()

            if row:
                series_db = row["series"] or ""
                variety_db = row["variety"] or ""

                # Special handling for ATB Quarters
                is_atb = (
                    "america the beautiful" in raw_series.lower()
                    or "america the beautiful" in series_db.lower()
                    or "national park" in raw_series.lower()
                    or any(k in (raw_theme or raw_variety or variety_db).lower() for k in SUBJECT_STATE_MAP)
                )

                if is_atb:
                    result["program_series"] = "America the Beautiful Quarters"
                    result["series_slug"] = "america-the-beautiful"
                elif series_db:
                    result["program_series"] = series_db
                    result["series_slug"] = slugify(series_db)

                if raw_theme:
                    result["theme_subject"] = raw_theme
                    resolved_state = SUBJECT_STATE_MAP.get(raw_theme.lower(), slugify(raw_theme))
                    result["subject_slug"] = resolved_state
                elif variety_db:
                    result["theme_subject"] = variety_db
                    resolved_state = SUBJECT_STATE_MAP.get(variety_db.lower(), slugify(variety_db))
                    result["subject_slug"] = resolved_state

                if raw_variety:
                    result["variety"] = raw_variety
                elif variety_db and variety_db != result["theme_subject"]:
                    result["variety"] = variety_db

                result["catalog_matched"] = True
                result["valuation_source"] = "Local Catalog Baseline"

            conn.close()
    except Exception as e:
        logger.warning(f"Catalog resolution exception: {e}")

    return result


