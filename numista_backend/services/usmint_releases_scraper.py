"""
US Mint Upcoming Releases Scraper Service
==========================================
Dual-source scraper for US Mint product schedule and catalog.
  Source 1: catalog.usmint.gov/product-schedule/2026.html (no cookies)
  Source 2: www.usmint.gov product detail pages (requires Firestore-stored cookies)

Stores data in Firestore collection: usmint_upcoming_releases
Logs deltas to: usmint_release_changelog

Called by:
  - POST /api/cron/sync-mint-releases  (Cloud Scheduler, daily 2AM ET)
  - sync_worker/main.py                (belt-and-suspenders redundancy)
"""

import json
import logging
import os
import re
import time
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("usmint_releases")

# ── Constants ─────────────────────────────────────────────────────────────────

PRODUCT_SCHEDULE_URL = "https://catalog.usmint.gov/product-schedule/{year}.html"
USMINT_BASE_URL = "https://www.usmint.gov"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Badge → canonical status mapping
BADGE_STATUS_MAP = {
    "new": "Available",
    "newlimited": "Available",
    "limited": "Available",
    "coming soon": "Coming Soon",
    "coming soonlimited": "Coming Soon",
    "pre-order": "Pre-Order",
    "limitedpre-order": "Pre-Order",
    "sold out": "Sold Out",
    "": "Available",
}

# ── Local catalog path (for initial seed / offline fallback) ──────────────────

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.dirname(_THIS_DIR)
LOCAL_CATALOG_PATH = os.path.join(_BACKEND_DIR, "usmint_2026_catalog.json")


# ── Price parsing ─────────────────────────────────────────────────────────────

def parse_price(price_str: str) -> Optional[float]:
    """Parse a price string like '$169.00' or 'TBD' to a float or None."""
    if not price_str or price_str.upper() in ("TBD", "N/A", "PENDING", ""):
        return None
    cleaned = re.sub(r"[^\d.]", "", price_str.replace(",", ""))
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def badge_to_status(badge: str) -> str:
    """Convert a raw badge string to a canonical status."""
    if not badge:
        return "Available"
    return BADGE_STATUS_MAP.get(badge.lower().strip(), "Available")


# ── Cookie retrieval ──────────────────────────────────────────────────────────

def get_stored_cookies(db) -> Optional[str]:
    """
    Read US Mint session cookies from Firestore config/usmint document.
    Returns the cookie string or None if not available/expired.
    """
    try:
        doc = db.collection("config").document("usmint").get()
        if not doc.exists:
            logger.info("[Cookies] No config/usmint document found.")
            return None
        data = doc.to_dict() or {}
        cookie_str = data.get("cookieString", "")
        updated_at = data.get("updated_at")
        if not cookie_str:
            logger.info("[Cookies] cookieString is empty.")
            return None
        # Warn if cookies are older than 14 days
        if updated_at:
            if hasattr(updated_at, "timestamp"):
                age_days = (datetime.now(timezone.utc) - datetime.fromtimestamp(
                    updated_at.timestamp(), tz=timezone.utc
                )).days
            else:
                try:
                    dt = datetime.fromisoformat(str(updated_at).replace("Z", "+00:00"))
                    age_days = (datetime.now(timezone.utc) - dt).days
                except Exception:
                    age_days = -1
            if age_days > 14:
                logger.warning(
                    "[Cookies] US Mint cookies are %d days old — likely expired.", age_days
                )
            elif age_days >= 0:
                logger.info("[Cookies] US Mint cookies are %d days old.", age_days)
        return cookie_str
    except Exception as e:
        logger.error("[Cookies] Failed to read Firestore config/usmint: %s", e)
        return None


# ── Source 1: Product schedule page (no cookies) ──────────────────────────────

def scrape_product_schedule(year: int = 2026) -> List[Dict[str, Any]]:
    """
    Scrape catalog.usmint.gov/product-schedule/{year}.html.
    This page is accessible without cookies.
    Returns a list of product dicts with basic info.
    """
    url = PRODUCT_SCHEDULE_URL.format(year=year)
    logger.info("[Schedule] Fetching %s", url)

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        logger.error("[Schedule] BeautifulSoup not installed.")
        return []

    try:
        req = urllib.request.Request(url, headers=DEFAULT_HEADERS)
        html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
    except Exception as e:
        logger.error("[Schedule] Failed to fetch schedule page: %s", e)
        return []

    products = []
    # Parse schedule rows — look for product entries
    for row in soup.find_all(["tr", "div", "li"], class_=re.compile(
        r"schedule|product|release", re.I
    )):
        text = row.get_text(strip=True)
        if len(text) < 10 or len(text) > 300:
            continue
        # Try to extract date and product name
        date_match = re.search(
            r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}", text
        )
        release_date = date_match.group(0) + f", {year}" if date_match else ""
        # Clean up product name
        name = re.sub(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\s*", "", text)
        name = name.strip()
        if name and len(name) > 5:
            products.append({
                "title": name,
                "release_date": release_date,
                "source": "product_schedule",
            })

    # Fallback: generic link/title extraction
    if not products:
        for link in soup.find_all("a", class_=re.compile(r"name|product|title", re.I)):
            name = link.get_text(strip=True)
            if name and len(name) > 5:
                href = link.get("href", "")
                products.append({
                    "title": name,
                    "product_url": href if href.startswith("http") else f"{USMINT_BASE_URL}{href}",
                    "source": "product_schedule",
                })

    logger.info("[Schedule] Found %d products from schedule page.", len(products))
    return products


# ── Source 2: Local catalog JSON ──────────────────────────────────────────────

def load_local_catalog() -> List[Dict[str, Any]]:
    """
    Load the existing usmint_2026_catalog.json as baseline data.
    This is the most reliable data source — already scraped and verified.
    """
    if not os.path.exists(LOCAL_CATALOG_PATH):
        logger.warning("[Catalog] Local catalog not found at %s", LOCAL_CATALOG_PATH)
        return []

    try:
        with open(LOCAL_CATALOG_PATH, "r", encoding="utf-8") as f:
            items = json.load(f)
        logger.info("[Catalog] Loaded %d items from local catalog.", len(items))
        return items
    except Exception as e:
        logger.error("[Catalog] Failed to load local catalog: %s", e)
        return []


# ── Issue Price Lookup (used by valuation fallback) ───────────────────────────

def get_mint_issue_price(
    db,
    year: str,
    denomination: str,
    mint_mark: str = "",
    theme: str = "",
    item_number: str = "",
) -> Optional[float]:
    """
    Look up the US Mint issue price for a coin from Firestore.
    Used as a valuation fallback when Greysheet can't match.

    Searches usmint_upcoming_releases collection by:
      1. Exact item_number match (best)
      2. Fuzzy title/denomination match (fallback)

    Returns the issue price as a float, or None if not found.
    """
    if not year or not year.startswith("20"):
        return None

    try:
        collection = db.collection("usmint_upcoming_releases")

        # Strategy 1: Exact item number match
        if item_number:
            doc = collection.document(item_number).get()
            if doc.exists:
                data = doc.to_dict() or {}
                return parse_price(data.get("price", ""))

        # Strategy 2: Search by title keywords
        search_terms = []
        if denomination:
            search_terms.append(denomination.lower())
        if theme:
            search_terms.append(theme.lower())
        if mint_mark:
            search_terms.append(mint_mark.upper())

        if not search_terms:
            return None

        # Read all products for the year and fuzzy match
        docs = collection.stream()
        best_match = None
        best_score = 0

        for doc in docs:
            data = doc.to_dict() or {}
            title = (data.get("title") or "").lower()
            price = parse_price(data.get("price", ""))
            if not price or price <= 0:
                continue

            # Score based on keyword matches
            score = 0
            for term in search_terms:
                if term in title:
                    score += 1

            if score > best_score:
                best_score = score
                best_match = price

        if best_match and best_score >= 1:
            return best_match

        return None

    except Exception as e:
        logger.error("[IssuePriceLookup] Error: %s", e)
        return None


# ── Sync to Firestore ─────────────────────────────────────────────────────────

def _normalize_product(item: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a product dict to the canonical Firestore schema."""
    badge = item.get("badge", "")
    price_str = item.get("price", "TBD")
    price_num = parse_price(price_str)

    images = item.get("images", [])
    image_url = images[0] if images else None

    return {
        "item_number": item.get("item_number", ""),
        "title": item.get("title", ""),
        "price": price_str,
        "price_numeric": price_num,
        "status": badge_to_status(badge),
        "badge": badge,
        "release_date": item.get("release_date", ""),
        "image_url": image_url,
        "image_urls": images,
        "product_url": item.get("url", ""),
        "program": item.get("program", ""),
        "category": item.get("category", "coin"),
        "mint_location": item.get("mint_location", ""),
        "mintage_limit": item.get("mintage_limit"),
        "household_limit": item.get("household_limit"),
        "finish": item.get("finish", ""),
        "description": item.get("description", ""),
        "metal_content": item.get("metal_content", ""),
        "last_scraped": datetime.now(timezone.utc).isoformat(),
    }


def sync_upcoming_releases(db) -> Dict[str, Any]:
    """
    Main sync function. Merges data from all sources and writes to Firestore.
    Returns a delta report.
    """
    logger.info("=== US Mint Upcoming Releases Sync Starting ===")
    report = {"new": [], "updated": [], "unchanged": 0, "errors": []}

    # Load catalog data (primary source — already verified)
    catalog_items = load_local_catalog()

    # Try schedule page for any new items
    schedule_items = scrape_product_schedule()

    # Merge: catalog is authoritative, schedule adds release dates
    schedule_titles = {s["title"].lower(): s for s in schedule_items}

    # Process catalog items
    for item in catalog_items:
        item_number = item.get("item_number", "")
        if not item_number:
            continue

        normalized = _normalize_product(item)

        # Enrich with schedule data if available
        title_lower = normalized["title"].lower()
        for sched_title, sched_data in schedule_titles.items():
            if sched_title in title_lower or title_lower in sched_title:
                if sched_data.get("release_date"):
                    normalized["release_date"] = sched_data["release_date"]
                break

        # Write to Firestore with delta detection
        try:
            doc_ref = db.collection("usmint_upcoming_releases").document(item_number)
            existing = doc_ref.get()

            if existing.exists:
                existing_data = existing.to_dict() or {}
                changes = _detect_changes(existing_data, normalized)

                if changes:
                    # Log each change to changelog
                    for field, (old_val, new_val) in changes.items():
                        _log_change(db, item_number, field, str(old_val), str(new_val))

                    # Preserve created_at, update the rest
                    normalized["created_at"] = existing_data.get("created_at")
                    normalized["updated_at"] = datetime.now(timezone.utc).isoformat()
                    doc_ref.update(normalized)
                    report["updated"].append({
                        "item_number": item_number,
                        "title": normalized["title"],
                        "changes": {k: v[1] for k, v in changes.items()},
                    })
                    logger.info(
                        "  [UPDATED] %s: %s", item_number,
                        ", ".join(f"{k}: {v[0]} → {v[1]}" for k, v in changes.items())
                    )
                else:
                    report["unchanged"] += 1
            else:
                # New product
                normalized["created_at"] = datetime.now(timezone.utc).isoformat()
                normalized["updated_at"] = datetime.now(timezone.utc).isoformat()
                doc_ref.set(normalized)
                _log_change(db, item_number, "new_product", "", normalized["title"])
                report["new"].append({
                    "item_number": item_number,
                    "title": normalized["title"],
                })
                logger.info("  [NEW] %s: %s", item_number, normalized["title"])

        except Exception as e:
            logger.error("  [ERROR] %s: %s", item_number, e)
            report["errors"].append({"item_number": item_number, "error": str(e)})

    logger.info(
        "=== Sync Complete: %d new, %d updated, %d unchanged, %d errors ===",
        len(report["new"]),
        len(report["updated"]),
        report["unchanged"],
        len(report["errors"]),
    )
    return report


def _detect_changes(
    existing: Dict[str, Any], incoming: Dict[str, Any]
) -> Dict[str, tuple]:
    """Compare existing vs incoming and return changed fields."""
    tracked_fields = ["price", "status", "badge", "release_date", "mintage_limit"]
    changes = {}
    for field in tracked_fields:
        old_val = existing.get(field)
        new_val = incoming.get(field)
        if old_val != new_val and new_val is not None:
            changes[field] = (old_val, new_val)
    return changes


def _log_change(
    db, item_number: str, field: str, old_value: str, new_value: str
) -> None:
    """Write a changelog entry to Firestore."""
    try:
        db.collection("usmint_release_changelog").add({
            "item_number": item_number,
            "field_changed": field,
            "old_value": old_value,
            "new_value": new_value,
            "detected_at": datetime.now(timezone.utc).isoformat(),
        })
    except Exception as e:
        logger.error("[Changelog] Failed to log change for %s: %s", item_number, e)


# ── Fetch products for API responses ──────────────────────────────────────────

def get_upcoming_products(db) -> List[Dict[str, Any]]:
    """
    Get products with status in [Coming Soon, Available, Pre-Order].
    Sorted by release date ascending (soonest first).
    """
    try:
        docs = db.collection("usmint_upcoming_releases").stream()
        products = []
        for doc in docs:
            data = doc.to_dict() or {}
            data["id"] = doc.id
            status = data.get("status", "")
            if status in ("Coming Soon", "Available", "Pre-Order"):
                products.append(data)

        # Sort by release_date (best-effort; strings sort lexicographically OK for months)
        products.sort(key=lambda p: p.get("release_date", "zzzz"))
        return products
    except Exception as e:
        logger.error("[GetUpcoming] Error: %s", e)
        return []


def get_all_products(db) -> List[Dict[str, Any]]:
    """
    Get ALL products from the catalog.
    """
    try:
        docs = db.collection("usmint_upcoming_releases").stream()
        products = []
        for doc in docs:
            data = doc.to_dict() or {}
            data["id"] = doc.id
            products.append(data)
        products.sort(key=lambda p: p.get("release_date", "zzzz"))
        return products
    except Exception as e:
        logger.error("[GetAll] Error: %s", e)
        return []
