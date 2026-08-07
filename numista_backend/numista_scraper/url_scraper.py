#!/usr/bin/env python3
"""
url_scraper.py
==============
Source-aware URL ingestion engine.

Given any URL, this module:
  1. Detects the source type (wikipedia | usmint | generic_html)
  2. Extracts structured coin records from the page
  3. Fuzzy-matches each coin to existing definitive_reference docs
  4. Updates existing docs (≥ 92% match) OR creates new ai_approval_pending docs
  5. Downloads images via a 3-tier waterfall:
       Wikimedia Commons → US Mint website → logs as missing

Usage (standalone):
    from numista_scraper.url_scraper import scrape_url
    results = scrape_url("https://en.wikipedia.org/wiki/...", dry_run=True)
"""

import os
import re
import sys
import json
import time
import sqlite3
import hashlib
import requests
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse, quote

# ─── Relative imports with fallback ──────────────────────────────────────────
try:
    from .config import DB_PATH, KEY_PATH, BUCKET_NAME, GCP_PROJECT, get_scrape_proxy
    from .storage import db, gcs_client, upload_to_gcs, ensure_sqlite_schema, update_coin_images_in_databases
except ImportError:
    _here = Path(__file__).parent.parent
    sys.path.insert(0, str(_here))
    from numista_scraper.config import DB_PATH, KEY_PATH, BUCKET_NAME, GCP_PROJECT, get_scrape_proxy
    from numista_scraper.storage import db, gcs_client, upload_to_gcs, ensure_sqlite_schema, update_coin_images_in_databases

try:
    from rapidfuzz import fuzz, process as rfprocess
except ImportError:
    import difflib
    class FuzzFallback:
        @staticmethod
        def ratio(s1, s2):
            return difflib.SequenceMatcher(None, str(s1), str(s2)).ratio() * 100
        token_set_ratio = ratio
        WRatio = ratio

    class ProcessFallback:
        @staticmethod
        def extractOne(query, choices, scorer=None, score_cutoff=0):
            best_score = -1
            best_idx = 0
            for idx, choice in enumerate(choices):
                score = difflib.SequenceMatcher(None, str(query), str(choice)).ratio() * 100
                if score > best_score:
                    best_score = score
                    best_idx = idx
            if best_score >= score_cutoff:
                return (choices[best_idx], best_score, best_idx)
            return None

    fuzz = FuzzFallback()
    rfprocess = ProcessFallback()

# ─── Constants ────────────────────────────────────────────────────────────────
WIKI_API        = "https://en.wikipedia.org/api/rest_v1"
COMMONS_API     = "https://commons.wikimedia.org/w/api.php"
WIKI_UA         = "NumistaAICoinScraper/2.0 (https://numista-vault.web.app/; contact@numista.ai)"
AUTO_COMMIT_THRESHOLD = 0.92
GCS_COIN_PREFIX = "coins/"
PUBLIC_URL_BASE = f"https://storage.googleapis.com/{BUCKET_NAME}/{{}}"
ATTRIBUTION_WIKI = "Wikimedia Commons. Public domain (US government work). CC-BY-SA."
ATTRIBUTION_MINT = "United States Mint. Public domain (17 U.S.C. § 105). Source: usmint.gov"

# ─── 2026 Semiquincentennial Master Coin Definitions ─────────────────────────
# Keyed by a stable slug used to build doc_ids and Wikimedia filenames.
SEMIQ_COINS = [
    # ── Five Semiquincentennial Quarters ────────────────────────────────────
    {
        "slug":             "mayflower_compact",
        "series":           "Semiquincentennial Quarters",
        "denomination":     "Quarter Dollar",
        "variety":          "Mayflower Compact",
        "year":             "2026",
        "mints":            ["P", "D"],
        "mintage":          {"P": 115_200_000, "D": 121_400_000},
        "category":         "coin",
        "obverse_desc":     "Standard Washington portrait with dual date 1776–2026",
        "reverse_desc":     "Recognizes the colony at Plymouth and the Compact as a precursor to the Declaration of Independence and the U.S. Constitution.",
        "composition":      "Copper-nickel clad copper",
        "designer":         None,
        "wiki_file_stem":   "SemiQ-Mayflower",     # → SemiQ-Mayflower-Obverse-Unc-{Mint}.jpg
        "usmint_slug":      "mayflower-compact",
    },
    {
        "slug":             "revolutionary_war",
        "series":           "Semiquincentennial Quarters",
        "denomination":     "Quarter Dollar",
        "variety":          "Revolutionary War",
        "year":             "2026",
        "mints":            ["P", "D"],
        "mintage":          {"P": 100_400_000, "D": 101_400_000},
        "category":         "coin",
        "obverse_desc":     "Standard Washington portrait with dual date 1776–2026",
        "reverse_desc":     "Honors the will and strength to overcome the trials of war in pursuit of liberty.",
        "composition":      "Copper-nickel clad copper",
        "designer":         None,
        "wiki_file_stem":   "SemiQ-Revolutionary-War",
        "usmint_slug":      "revolutionary-war",
    },
    {
        "slug":             "declaration_of_independence",
        "series":           "Semiquincentennial Quarters",
        "denomination":     "Quarter Dollar",
        "variety":          "Declaration of Independence",
        "year":             "2026",
        "mints":            ["P", "D"],
        "mintage":          {"P": 63_000_000, "D": 84_800_000},
        "category":         "coin",
        "obverse_desc":     "Standard Washington portrait with dual date 1776–2026",
        "reverse_desc":     "Features the Liberty Bell, an iconic symbol of the country's founding era and a symbol closely associated with the Declaration of Independence.",
        "composition":      "Copper-nickel clad copper",
        "designer":         None,
        "wiki_file_stem":   "SemiQ-Declaration",
        "usmint_slug":      "declaration-of-independence",
    },
    {
        "slug":             "us_constitution",
        "series":           "Semiquincentennial Quarters",
        "denomination":     "Quarter Dollar",
        "variety":          "U.S. Constitution",
        "year":             "2026",
        "mints":            ["P", "D"],
        "mintage":          {"P": 1_600_000, "D": 1_400_000},
        "category":         "coin",
        "obverse_desc":     "Standard Washington portrait with dual date 1776–2026",
        "reverse_desc":     "Depicts Independence Hall in Philadelphia, where the Liberty Bell was housed and where both the Declaration of Independence and U.S. Constitution were written, debated, and signed.",
        "composition":      "Copper-nickel clad copper",
        "designer":         None,
        "wiki_file_stem":   "SemiQ-Constitution",
        "usmint_slug":      "us-constitution",
    },
    {
        "slug":             "gettysburg_address",
        "series":           "Semiquincentennial Quarters",
        "denomination":     "Quarter Dollar",
        "variety":          "Gettysburg Address",
        "year":             "2026",
        "mints":            ["P", "D"],
        "mintage":          {"P": 1_400_000, "D": 1_400_000},
        "category":         "coin",
        "obverse_desc":     "Standard Washington portrait with dual date 1776–2026",
        "reverse_desc":     "Honors the Gettysburg Address, recognized as one of the most poignant and moving speeches in American history.",
        "composition":      "Copper-nickel clad copper",
        "designer":         None,
        "wiki_file_stem":   "SemiQ-Gettysburg",
        "usmint_slug":      "gettysburg-address",
    },
    # ── Native American Dollar ───────────────────────────────────────────────
    {
        "slug":             "native_american_dollar_polly_cooper",
        "series":           "Native American Dollar",
        "denomination":     "Dollar",
        "variety":          "Polly Cooper — Oneida Allies at Valley Forge",
        "year":             "2026",
        "mints":            ["P", "D"],
        "mintage":          {},
        "category":         "coin",
        "obverse_desc":     "Portrait of Sacagawea carrying her infant son Jean-Baptiste. Inscriptions: LIBERTY, IN GOD WE TRUST.",
        "reverse_desc":     "Polly Cooper holding a basket as she shares the Oneidas' gift of corn with General Washington. Inscriptions: UNITED STATES OF AMERICA, POLLY COOPER, $1, ONEIDA ALLIES AT VALLEY FORGE.",
        "composition":      "Manganese brass",
        "designer":         None,
        "wiki_file_stem":   "SemiQ-Dollar",
        "usmint_slug":      "native-american-dollar",
    },
    # ── Enduring Liberty Half Dollar ─────────────────────────────────────────
    {
        "slug":             "enduring_liberty_half_dollar",
        "series":           "Semiquincentennial",
        "denomination":     "Half Dollar",
        "variety":          "Enduring Liberty",
        "year":             "2026",
        "mints":            ["P", "D"],
        "mintage":          {},
        "category":         "coin",
        "obverse_desc":     "Statue of Liberty (replaces Kennedy — one year only, 2026).",
        "reverse_desc":     "Presidential Coat of Arms (standard Kennedy reverse).",
        "composition":      "Copper-nickel clad copper",
        "designer":         None,
        "wiki_file_stem":   "SemiQ-Half-Dollar",
        "usmint_slug":      "half-dollar",
    },
    # ── Emerging Liberty Dime ────────────────────────────────────────────────
    {
        "slug":             "emerging_liberty_dime",
        "series":           "Semiquincentennial",
        "denomination":     "Dime",
        "variety":          "Emerging Liberty",
        "year":             "2026",
        "mints":            ["P", "D"],
        "mintage":          {},
        "category":         "coin",
        "obverse_desc":     "Liberty on obverse (first time since 1945).",
        "reverse_desc":     "Torch and olive branch (standard Roosevelt reverse).",
        "composition":      "Copper-nickel clad copper",
        "designer":         None,
        "wiki_file_stem":   "SemiQ-Dime",
        "usmint_slug":      "dime",
    },
    # ── Jefferson Nickel — Semiquincentennial ────────────────────────────────
    {
        "slug":             "jefferson_nickel_semiquincentennial",
        "series":           "Jefferson Nickel",
        "denomination":     "Five Cents",
        "variety":          "Semiquincentennial — 1776~2026",
        "year":             "2026",
        "mints":            ["P", "D"],
        "mintage":          {},
        "category":         "coin",
        "obverse_desc":     "Standard Jefferson portrait marked with dual dates 1776 ~ 2026.",
        "reverse_desc":     "Monticello (standard Jefferson reverse).",
        "composition":      "Copper-nickel",
        "designer":         None,
        "wiki_file_stem":   "SemiQ-Nickel",
        "usmint_slug":      "nickel",
    },
    # ── Lincoln Cent — Semiquincentennial ────────────────────────────────────
    {
        "slug":             "lincoln_cent_semiquincentennial",
        "series":           "Lincoln Cent",
        "denomination":     "Cent",
        "variety":          "Semiquincentennial — 1776~2026",
        "year":             "2026",
        "mints":            ["P", "D"],
        "mintage":          {},
        "category":         "coin",
        "obverse_desc":     "Standard Lincoln portrait marked with dual dates 1776 ~ 2026.",
        "reverse_desc":     "Union Shield (standard Lincoln cent reverse).",
        "composition":      "Copper plated zinc",
        "designer":         None,
        "wiki_file_stem":   "SemiQ-Penny",
        "usmint_slug":      "penny",
    },
]

# ─── Source Detection ─────────────────────────────────────────────────────────

def detect_source_type(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "wikipedia.org" in host:
        return "wikipedia"
    if "usmint.gov" in host:
        return "usmint"
    return "generic_html"


# ─── Wikimedia Commons Image Resolver ────────────────────────────────────────

def resolve_wikimedia_file_url(file_title: str) -> str | None:
    """
    Resolve a Wikimedia Commons File: title to its full-resolution URL.
    e.g. "File:SemiQ-Mayflower-Reverse-Unc.jpg"
         → "https://upload.wikimedia.org/wikipedia/commons/0/0d/SemiQ-Mayflower-Reverse-Unc.jpg"
    Returns None if the file doesn't exist.
    """
    params = {
        "action": "query",
        "titles": file_title,
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json",
    }
    try:
        resp = requests.get(
            COMMONS_API, params=params,
            headers={"User-Agent": WIKI_UA}, timeout=10
        )
        resp.raise_for_status()
        pages = resp.json().get("query", {}).get("pages", {})
        for page in pages.values():
            info = page.get("imageinfo", [])
            if info:
                return info[0]["url"]
    except Exception as e:
        print(f"    ⚠ Wikimedia resolve error for {file_title}: {e}")
    return None


def resolve_wikimedia_coin_images(coin: dict, mint: str) -> dict:
    """
    Try to find obverse + reverse on Wikimedia Commons using the SemiQ naming pattern.
    Returns {"obverse": url_or_none, "reverse": url_or_none, "source": "wikimedia"}
    """
    stem = coin.get("wiki_file_stem", "")
    if not stem:
        return {"obverse": None, "reverse": None, "source": "wikimedia"}

    results = {}
    for side in ("Obverse", "Reverse"):
        # Try mint-specific first, then generic
        candidates = [
            f"File:{stem}-{side}-Unc-{mint}.jpg",
            f"File:{stem}-{side}-Unc.jpg",
            f"File:{stem}-{side}-Proof-{mint}.jpg",
        ]
        found_url = None
        for candidate in candidates:
            url = resolve_wikimedia_file_url(candidate)
            if url:
                print(f"    [Wikimedia] ✓ {candidate}")
                found_url = url
                break
            else:
                print(f"    [Wikimedia] ✗ {candidate}")
        results[side.lower()] = found_url

    results["source"] = "wikimedia"
    return results


# ─── US Mint Image Fetcher ────────────────────────────────────────────────────

# ── Per-coin US Mint product page URLs ────────────────────────────────────────
# Maps coin slug → specific product page URL.
# Using dedicated per-denomination pages avoids scraping the generic program page
# which lists all coins together and causes wrong image matches.
_USMINT_COIN_PRODUCT_URLS = {
    "mayflower_compact":              "https://www.usmint.gov/coins/coin-programs/semiquincentennial/mayflower-compact-quarter",
    "revolutionary_war":              "https://www.usmint.gov/coins/coin-programs/semiquincentennial/revolutionary-war-quarter",
    "declaration_of_independence":    "https://www.usmint.gov/coins/coin-programs/semiquincentennial/declaration-of-independence-quarter",
    "us_constitution":                "https://www.usmint.gov/coins/coin-programs/semiquincentennial/us-constitution-quarter",
    "gettysburg_address":             "https://www.usmint.gov/coins/coin-programs/semiquincentennial/gettysburg-address-quarter",
    "native_american_dollar_polly_cooper": "https://www.usmint.gov/coins/coin-programs/native-american-dollar-coins/2026-native-american-dollar-coin",
    "enduring_liberty_half_dollar":   "https://www.usmint.gov/coins/coin-programs/semiquincentennial/enduring-liberty-half-dollar",
    "emerging_liberty_dime":          "https://www.usmint.gov/coins/coin-programs/semiquincentennial/emerging-liberty-dime",
    "jefferson_nickel_semiquincentennial": "https://www.usmint.gov/coins/coin-programs/semiquincentennial/jefferson-nickel",
    "lincoln_cent_semiquincentennial": "https://www.usmint.gov/coins/coin-programs/semiquincentennial/lincoln-penny",
}


def fetch_usmint_coin_images(coin: dict, mint: str) -> dict:
    """
    Try to scrape coin images from the US Mint website using stored session cookie.
    Only uses coin-specific product pages (never the generic program listing page)
    to avoid picking up the wrong coin's images.
    Returns {"obverse": url_or_none, "reverse": url_or_none, "source": "usmint"}
    """
    from curl_cffi import requests as curl_requests
    from bs4 import BeautifulSoup

    # Look up the specific product page for this coin
    slug = coin.get("slug", "")
    product_url = _USMINT_COIN_PRODUCT_URLS.get(slug)
    if not product_url:
        print(f"    [USMint] ✗ No specific product URL for slug: {slug} — skipping to avoid wrong image")
        return {"obverse": None, "reverse": None, "source": "usmint"}

    # Load session cookie from Firestore
    try:
        doc = db.collection("config").document("usmint").get()
        cookie_str = doc.to_dict().get("cookieString", "") if doc.exists else ""
        user_agent = doc.to_dict().get("userAgent", "") if doc.exists else ""
    except Exception:
        cookie_str = ""
        user_agent = ""

    if not cookie_str:
        print(f"    [USMint] ✗ No cookie configured — skipping")
        return {"obverse": None, "reverse": None, "source": "usmint"}

    headers = {
        "User-Agent": user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Cookie": cookie_str,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.usmint.gov/coins/coin-programs/semiquincentennial/",
    }

    try:
        resp = curl_requests.get(product_url, headers=headers, timeout=20, impersonate="chrome120")
        if resp.status_code != 200:
            print(f"    [USMint] ✗ HTTP {resp.status_code} for {product_url}")
            return {"obverse": None, "reverse": None, "source": "usmint"}

        soup = BeautifulSoup(resp.text, "html.parser")

        # On a per-coin page, look for images with obverse/reverse in URL or alt text
        img_urls = []
        for img in soup.find_all("img"):
            src = img.get("src", "") or img.get("data-src", "")
            alt = (img.get("alt", "") or "").lower()
            if not src or len(src) < 10:
                continue
            if src.startswith("/"):
                src = "https://www.usmint.gov" + src
            # Must be a usmint.gov image (not analytics/icons)
            if "usmint.gov" not in src:
                continue
            # Must be in the image-library or similar media path
            if not any(kw in src.lower() for kw in ["image-library", "coin", "/coins/", "/2026/"]):
                continue
            img_urls.append((alt, src))

        if not img_urls:
            print(f"    [USMint] ✗ No coin images found on {product_url}")
            return {"obverse": None, "reverse": None, "source": "usmint"}

        # Match obverse/reverse by alt text or URL keyword
        obv = next((u for a, u in img_urls if "obverse" in a or "obverse" in u.lower()), None)
        rev = next((u for a, u in img_urls if "reverse" in a or "reverse" in u.lower()), None)

        # Only fall back to positional if we got hits on this specific page
        if not obv and not rev and img_urls:
            obv = img_urls[0][1]
            rev = img_urls[1][1] if len(img_urls) > 1 else None

        if obv or rev:
            print(f"    [USMint] ✓ Found images on {product_url}")
        else:
            print(f"    [USMint] ✗ Images found but no obverse/reverse identified on {product_url}")

        return {"obverse": obv, "reverse": rev, "source": "usmint"}

    except Exception as e:
        print(f"    [USMint] ✗ Error fetching {product_url}: {e}")
        return {"obverse": None, "reverse": None, "source": "usmint"}


# ─── GCS Existence Check (Tier 0) ───────────────────────────────────────────

def check_gcs_existing(doc_id: str) -> dict:
    """
    Tier 0: Check whether we already have obverse and/or reverse images
    in our GCS bucket for this doc_id.  Tries .jpg, .png, .webp.
    Returns {"obverse": public_url_or_None, "reverse": public_url_or_None}.
    """
    bucket  = gcs_client.bucket(BUCKET_NAME)
    results = {"obverse": None, "reverse": None}
    for side in ("obverse", "reverse"):
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            blob_path = f"{GCS_COIN_PREFIX}{doc_id}_{side}{ext}"
            try:
                if bucket.blob(blob_path).exists():
                    results[side] = PUBLIC_URL_BASE.format(blob_path)
                    print(f"    [GCS-Tier0] ✓ Already have {side}: {blob_path}")
                    break
            except Exception as e:
                print(f"    [GCS-Tier0] ⚠ Check error for {blob_path}: {e}")
    return results


# ─── Image Download + GCS Upload ─────────────────────────────────────────────

def _download_bytes(url: str, is_wikimedia: bool = False, is_usmint: bool = False) -> bytes | None:
    """Download raw image bytes from a URL."""
    try:
        headers = {"User-Agent": WIKI_UA if is_wikimedia else
                   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        if is_usmint:
            from curl_cffi import requests as curl_requests
            try:
                doc = db.collection("config").document("usmint").get()
                cookie_str = doc.to_dict().get("cookieString", "") if doc.exists else ""
                if cookie_str:
                    headers["Cookie"] = cookie_str
            except Exception:
                pass
            resp = curl_requests.get(url, headers=headers, timeout=20, impersonate="chrome120")
        else:
            resp = requests.get(url, headers=headers, timeout=20)

        if resp.status_code == 200 and len(resp.content) > 2000:
            return resp.content
        else:
            print(f"    ⚠ Download failed {url} → HTTP {resp.status_code}")
    except Exception as e:
        print(f"    ⚠ Download error {url}: {e}")
    return None


def download_and_upload(image_url: str, doc_id: str, side: str,
                        attribution: str, dry_run: bool = False) -> str | None:
    """Download image from URL and upload to GCS. Returns public URL."""
    ext = ".jpg"
    if ".png" in image_url.lower():
        ext = ".png"
    elif ".webp" in image_url.lower():
        ext = ".webp"

    gcs_path  = f"{GCS_COIN_PREFIX}{doc_id}_{side}{ext}"
    public_url = PUBLIC_URL_BASE.format(gcs_path)

    if dry_run:
        print(f"    [DRY-RUN] Would download {image_url}")
        print(f"    [DRY-RUN] Would upload → gs://{BUCKET_NAME}/{gcs_path}")
        return public_url

    is_wiki   = "wikimedia.org" in image_url or "wikipedia.org" in image_url
    is_usmint = "usmint.gov" in image_url

    img_bytes = _download_bytes(image_url, is_wikimedia=is_wiki, is_usmint=is_usmint)
    if not img_bytes:
        return None

    try:
        bucket = gcs_client.bucket(BUCKET_NAME)
        blob   = bucket.blob(gcs_path)
        ct     = "image/jpeg" if ext == ".jpg" else ("image/png" if ext == ".png" else "image/webp")
        blob.upload_from_string(img_bytes, content_type=ct)
        blob.metadata = {
            "attribution": attribution,
            "source":      "wikimedia" if is_wiki else ("usmint_gov" if is_usmint else "scraped"),
            "license":     "cc_by_sa_4" if is_wiki else "public_domain_us_government",
            "copyright":   "Wikimedia Commons contributors" if is_wiki else "Public Domain",
        }
        blob.patch()
        try:
            blob.make_public()
        except Exception:
            pass
        print(f"    [GCS] ✅ Uploaded → {gcs_path}")
        return public_url
    except Exception as e:
        print(f"    ⚠ GCS upload error for {gcs_path}: {e}")
        return None


# ─── Catalog Matching ─────────────────────────────────────────────────────────

_catalog_cache: list = []

def _load_catalog() -> list:
    global _catalog_cache
    if _catalog_cache:
        return _catalog_cache
    print("📚 Loading definitive_reference catalog …")
    docs = db.collection("definitive_reference").stream()
    for doc in docs:
        d = doc.to_dict()
        d["doc_id"] = doc.id
        parts = [
            str(d.get("year") or ""),
            str(d.get("denomination") or ""),
            str(d.get("series") or ""),
            str(d.get("variety") or ""),
            str(d.get("mint_mark") or ""),
        ]
        match_str = " ".join(p for p in parts if p).lower()
        _catalog_cache.append({"doc_id": doc.id, "match_string": match_str, "data": d})
    print(f"  Loaded {len(_catalog_cache)} records.")
    return _catalog_cache


def match_to_catalog(coin_def: dict, mint: str) -> tuple:
    """
    Returns (doc_id, confidence, existing_data, action)
    action: "UPDATE" | "CREATE"
    """
    catalog = _load_catalog()
    query_parts = [
        coin_def.get("year", ""),
        coin_def.get("denomination", ""),
        coin_def.get("series", ""),
        coin_def.get("variety", ""),
        mint,
    ]
    query = " ".join(p for p in query_parts if p).lower()

    # Pre-filter by year
    year = coin_def.get("year", "")
    candidates = [c for c in catalog if year in c["match_string"]] if year else catalog
    if not candidates:
        candidates = catalog

    match_strings = [c["match_string"] for c in candidates]
    best_score, best_idx = 0, 0
    for scorer in (fuzz.token_set_ratio, fuzz.WRatio):
        result = rfprocess.extractOne(query, match_strings, scorer=scorer, score_cutoff=0)
        if result and result[1] > best_score:
            best_score, best_idx = result[1], result[2]

    confidence = best_score / 100.0
    best = candidates[best_idx]
    action = "UPDATE" if confidence >= AUTO_COMMIT_THRESHOLD else "CREATE"
    return best["doc_id"], confidence, best["data"], action


# ─── Firestore / SQLite Writers ───────────────────────────────────────────────

def _make_doc_id(coin_def: dict, mint: str) -> str:
    """Generate a canonical doc_id for a new coin or banknote."""
    slug  = coin_def.get("slug", "unknown")
    year  = coin_def.get("year", "2026")
    category = coin_def.get("category", "coin")
    mint_lc = mint.lower()
    
    if category == "banknote":
        return f"ref_note_confederate_{slug}_{year}"
    return f"ref_coin_semiquincentennial_{slug}_{year}_{mint_lc}"


def _build_firestore_record(coin_def: dict, mint: str,
                             obv_url: str, rev_url: str,
                             source_url: str) -> dict:
    mintage_dict = coin_def.get("mintage")
    mintage = mintage_dict.get(mint) if isinstance(mintage_dict, dict) else mintage_dict
    return {
        "year":              coin_def["year"],
        "denomination":      coin_def["denomination"],
        "series":            coin_def["series"],
        "variety":           coin_def["variety"],
        "mint_mark":         mint,
        "category":          coin_def.get("category", "coin"),
        "composition":       coin_def.get("composition", ""),
        "designer":          coin_def.get("designer") or "",
        "obverse_desc":      coin_def.get("obverse_desc", ""),
        "reverse_desc":      coin_def.get("reverse_desc", ""),
        "mintage":           mintage,
        "image_url_obverse": obv_url or "",
        "image_url_reverse": rev_url or "",
        "status":            "ai_approval_pending",
        "source_url":        source_url,
        "enrichment_source": "url_scraper",
        "last_enriched_at":  datetime.now(timezone.utc).isoformat(),
        "country":           "United States",
        "country_code":      "US",
    }


def commit_coin(coin_def: dict, mint: str, obv_url: str, rev_url: str,
                source_url: str, action: str, doc_id: str,
                dry_run: bool = False) -> dict:
    """Write or update Firestore + SQLite for one coin × mint."""
    now = datetime.now(timezone.utc).isoformat()

    if action == "CREATE":
        new_doc_id = _make_doc_id(coin_def, mint)
        record     = _build_firestore_record(coin_def, mint, obv_url, rev_url, source_url)
        if dry_run:
            print(f"    [DRY-RUN] Would CREATE Firestore doc: {new_doc_id}")
            print(f"              obverse: {obv_url or '(none)'}")
            print(f"              reverse: {rev_url or '(none)'}")
            return {"action": "CREATE", "doc_id": new_doc_id, "status": "dry_run"}

        try:
            db.collection("definitive_reference").document(new_doc_id).set(record)
            print(f"    [Firestore] ✅ CREATED {new_doc_id}")
        except Exception as e:
            print(f"    ⚠ Firestore create error {new_doc_id}: {e}")

        # SQLite insert
        try:
            ensure_sqlite_schema()
            conn = sqlite3.connect(str(DB_PATH))
            cur  = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO definitive_reference
                (doc_id, year, denomination, series, variety, mint_mark, category,
                 image_url_obverse, image_url_reverse)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (new_doc_id, record["year"], record["denomination"],
                  record["series"], record["variety"], record["mint_mark"],
                  record["category"], obv_url, rev_url))
            conn.commit()
            conn.close()
            print(f"    [SQLite]    ✅ INSERTED {new_doc_id}")
        except Exception as e:
            print(f"    ⚠ SQLite insert error {new_doc_id}: {e}")

        return {"action": "CREATE", "doc_id": new_doc_id, "status": "created"}
    else:  # UPDATE
        update = {"last_enriched_at": now, "enrichment_source": "url_scraper",
                  "source_url": source_url}
        if obv_url:
            update["image_url_obverse"] = obv_url
        if rev_url:
            update["image_url_reverse"] = rev_url
        
        existing_data = {}
        try:
            snap = db.collection("definitive_reference").document(doc_id).get()
            existing_data = snap.to_dict() or {}
        except Exception:
            pass

        for field, val in [
            ("obverse_desc",  coin_def.get("obverse_desc")),
            ("reverse_desc",  coin_def.get("reverse_desc")),
            ("composition",   coin_def.get("composition")),
        ]:
            if val and not existing_data.get(field):
                update[field] = val

        if dry_run:
            print(f"    [DRY-RUN] Would UPDATE {doc_id}: {list(update.keys())}")
            return {"action": "UPDATE", "doc_id": doc_id, "status": "dry_run"}

        try:
            db.collection("definitive_reference").document(doc_id).update(update)
            print(f"    [Firestore] ✅ UPDATED {doc_id}")
        except Exception as e:
            print(f"    ⚠ Firestore update error {doc_id}: {e}")

        if obv_url or rev_url:
            update_coin_images_in_databases(doc_id, obv_url or existing_data.get("image_url_obverse", ""),
                                            rev_url or existing_data.get("image_url_reverse", ""))

        return {"action": "UPDATE", "doc_id": doc_id, "status": "updated"}


def resolve_query_to_url(query: str) -> str | None:
    """
    Resolve a text query to a valid Wikipedia or US Mint URL.
    Attempts direct search first, then cleans query, then falls back to Wikipedia API.
    """
    import requests
    import re
    
    q = query
    print(f"  [Resolver] Resolving query: '{query}'")
    
    # Try Wikipedia Search API with cleaned terms
    for attempt in range(3):
        url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={requests.utils.quote(q)}&limit=5&namespace=0&format=json"
        try:
            resp = requests.get(url, headers={"User-Agent": WIKI_UA}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if len(data) >= 4 and data[3]:
                    # Find first url that is not generic portal
                    for u in data[3]:
                        if not any(x in u.lower() for x in ["/portal:", "/wiki/special:", "/wiki/category:"]):
                            print(f"  [Resolver] Resolved via Wikipedia: {u}")
                            return u
        except Exception as e:
            print(f"  [Resolver] Wikipedia search attempt {attempt} failed: {e}")
            
        # Clean query for next attempt
        if attempt == 0:
            # Strip specific terms
            q = re.sub(r'(one ounce|proof|unc|uncirculated|coin|us mint|united states mint|1 oz)', '', q, flags=re.IGNORECASE)
            q = re.sub(r'\s+', ' ', q).strip()
        elif attempt == 1:
            # Broaden to series
            if 'eagle' in q.lower():
                q = 'American Silver Eagle' if 'silver' in query.lower() else 'American Gold Eagle'
            else:
                break
                
    return None


def _scrape_generic_page(url: str, dry_run: bool, query_meta: dict = None) -> dict:
    """
    General-purpose page scraper. Extracts coin details, downloads images,
    fuzzy-matches with existing catalog, and writes to database.
    """
    from bs4 import BeautifulSoup
    import requests
    from curl_cffi import requests as curl_requests
    from urllib.parse import urlparse
    
    source_type = detect_source_type(url)
    query_meta = query_meta or {}
    
    # 1. Fetch page content
    html_text = ""
    if source_type == "usmint":
        # Load session cookies from Firestore
        try:
            doc = db.collection("config").document("usmint").get()
            cookie_str = doc.to_dict().get("cookieString", "") if doc.exists else ""
            user_agent = doc.to_dict().get("userAgent", "") if doc.exists else ""
        except Exception:
            cookie_str, user_agent = "", ""
            
        headers = {
            "User-Agent": user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Cookie": cookie_str,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.usmint.gov/"
        }
        try:
            resp = curl_requests.get(url, headers=headers, timeout=20, impersonate="chrome120")
            if resp.status_code == 200:
                html_text = resp.text
        except Exception as e:
            print(f"    [Scraper] Error fetching US Mint page: {e}")
    else:
        # Wikipedia, Smithsonian, or other generic sites
        # Try curl_cffi first (impersonate chrome120) to bypass Imperva/Cloudflare bot protection
        try:
            resp = curl_requests.get(url, impersonate="chrome120", timeout=15)
            if resp.status_code == 200:
                html_text = resp.text
        except Exception as e:
            print(f"    [Scraper] curl_cffi fetch attempt failed: {e}")

        if not html_text:
            headers = {"User-Agent": WIKI_UA}
            try:
                resp = requests.get(url, headers=headers, timeout=15)
                if resp.status_code == 200:
                    html_text = resp.text
            except Exception as e:
                print(f"    [Scraper] Error fetching page with requests: {e}")
            
    if not html_text:
        return {"status": "error", "message": f"Failed to fetch page content from {url}"}
        
    soup = BeautifulSoup(html_text, "html.parser")
    
    # 2. Parse title
    raw_title = ""
    title_el = soup.find("h1") or soup.find("title")
    if title_el:
        raw_title = title_el.get_text().strip()
        
    if not raw_title:
        raw_title = url.split("/")[-1].replace("-", " ").replace(".html", "")
        
    print(f"  Extracted page title: '{raw_title}'")
    
    # Check if page is a multi-item collection gallery (e.g., Wikipedia banknote/coin typeset, Smithsonian NNC collection)
    from urllib.parse import unquote
    multi_items = []
    
    # 2a. Wikipedia multi-item gallery detection
    for a in soup.find_all("a", class_="mw-file-description"):
        title = a.get("title", "")
        img = a.find("img")
        if not img:
            continue
        src = img.get("src", "")
        if "csa-t" in src.lower() or "csa-t" in title.lower() or "banknote" in title.lower():
            if "/thumb/" in src:
                cleaned = src.replace("/thumb/", "/")
                full_url = cleaned.rsplit("/", 1)[0]
                if full_url.startswith("//"):
                    full_url = "https:" + full_url
            else:
                full_url = "https:" + src if src.startswith("//") else src

            type_match = re.search(r'\(T(\d+)\)', title)
            type_id = f"T{type_match.group(1)}" if type_match else None
            
            denom_match = re.search(r'\$(\d+,?\d*)', title)
            denom = denom_match.group(0) if denom_match else ("$0.50" if "fifty cents" in title.lower() else "One Dollar")
            
            filename_decoded = unquote(full_url.split("/")[-1])
            year_match = re.search(r'\b(186\d|18\d{2}|19\d{2}|20\d{2})\b', filename_decoded)
            item_year = year_match.group(1) if year_match else "1861"
            
            mintage_match = re.search(r'\((\d+,?\d*)\s+issued\)', title, re.IGNORECASE)
            mintage_str = mintage_match.group(1) if mintage_match else None
            
            variety_clean = title
            if type_id: variety_clean = re.sub(r'\(\s*T\d+\s*\)', '', variety_clean)
            variety_clean = re.sub(r'\(\s*\d+,?\d*\s+issued\s*\)', '', variety_clean, flags=re.IGNORECASE)
            if denom: variety_clean = variety_clean.replace(denom, "")
            variety_clean = re.sub(r'\s+', ' ', variety_clean).strip()
            
            multi_items.append({
                "type_id": type_id or f"item_{len(multi_items)+1}",
                "denomination": denom,
                "year": item_year,
                "variety_clean": variety_clean,
                "title": title,
                "url": full_url,
                "filename": filename_decoded,
                "mintage": mintage_str
            })

    # 2b. Smithsonian NNC Collection multi-item gallery detection
    if not multi_items:
        for img in soup.find_all("img"):
            src = img.get("src", "")
            alt = img.get("alt", "") or img.get("title", "")
            if not src or not alt or len(alt) < 6:
                continue
            _abs_src = src if "://" in src else ("https:" + src if src.startswith("//") else "https://" + src)
            _netloc = urlparse(_abs_src).netloc
            if _netloc == "ids.si.edu" or _netloc.endswith(".ids.si.edu") or "collections" in src:
                denom_match = re.search(r'(\d+\s+Dollars?|\d+/\d+\s+Disme|\d+\s+Cents?|\$\d+)', alt, re.IGNORECASE)
                denom = denom_match.group(0) if denom_match else "One Dollar"
                
                year_match = re.search(r'\b(17\d{2}|18\d{2}|19\d{2}|20\d{2})\b', alt)
                item_year = year_match.group(1) if year_match else "1849"
                
                full_url = re.sub(r'max=\d+', 'max=2000', src)
                if full_url.startswith("//"):
                    full_url = "https:" + full_url
                elif full_url.startswith("/"):
                    full_url = "https://americanhistory.si.edu" + full_url
                    
                multi_items.append({
                    "type_id": f"si_{len(multi_items)+1}",
                    "denomination": denom,
                    "year": item_year,
                    "variety_clean": alt,
                    "title": alt,
                    "url": full_url,
                    "filename": f"smithsonian_{item_year}_{len(multi_items)+1}",
                    "mintage": None
                })

    if len(multi_items) > 1:
        deduped = {item["type_id"]: item for item in multi_items}
        print(f"📋 Detected collection page with {len(deduped)} items. Processing batch...\n")
        
        results = {
            "source_url": url,
            "created": [],
            "updated": [],
            "missing_images": [],
            "errors": [],
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        for item_key, b in sorted(deduped.items(), key=lambda x: int(re.sub(r'\D', '', str(x[0])) or 0)):
            is_banknote = "banknote" in raw_title.lower() or "csa" in b["filename"].lower() or "dollar" in raw_title.lower()
            cat = "banknote" if is_banknote else "coin"
            
            coin_def = {
                "slug":             f"csa_{b['type_id'].lower()}" if "csa" in b["filename"].lower() else re.sub(r'[^a-z0-9_]', '', b['variety_clean'].lower().replace(" ", "_")),
                "series":           "Confederate States Banknotes" if cat == "banknote" else "Commemoratives",
                "denomination":     b["denomination"],
                "variety":          f"Type {b['type_id']} - {b['variety_clean']}" if str(b['type_id']).startswith("T") else b['variety_clean'],
                "year":             b["year"],
                "mints":            ["Richmond"] if cat == "banknote" else ["P"],
                "category":         cat,
                "composition":      "Paper" if cat == "banknote" else "Clad",
                "obverse_desc":     b["variety_clean"],
                "reverse_desc":     "Plain or blank reverse" if cat == "banknote" else "",
                "mintage":          {"Richmond": b["mintage"]} if b["mintage"] else None
            }
            mint = coin_def["mints"][0]
            
            doc_id, confidence, existing_data, action = match_to_catalog(coin_def, mint)
            target_doc_id = doc_id if action == "UPDATE" else _make_doc_id(coin_def, mint)
            
            gcs_imgs = check_gcs_existing(target_doc_id)
            obv_url = gcs_imgs["obverse"]
            rev_url = gcs_imgs["reverse"]
            
            attribution = ATTRIBUTION_WIKI
            if not obv_url and b["url"]:
                obv_url = download_and_upload(b["url"], target_doc_id, "obverse", attribution, dry_run)
                
            res = commit_coin(coin_def, mint, obv_url, rev_url, url, action, target_doc_id, dry_run=dry_run)
            if res["status"] in ("created", "dry_run") and action == "CREATE":
                results["created"].append(res["doc_id"])
            elif res["status"] in ("updated", "dry_run") and action == "UPDATE":
                results["updated"].append(res["doc_id"])
                
            time.sleep(0.3)
            
        return results
    
    # Parse metadata from title (fallback to query_meta)
    year = query_meta.get("year")
    if not year:
        year_match = re.search(r'\b(20\d{2}|19\d{2})\b', raw_title)
        year = year_match.group(1) if year_match else "2026"
        
    denomination = query_meta.get("denomination")
    if not denomination:
        denomination = "One Dollar"
        for denom in ("Dollar", "Half Dollar", "Dime", "Nickel", "Cent", "Penny", "Quarter"):
            if denom.lower() in raw_title.lower():
                denomination = "Cent" if denom == "Penny" else denom
                break
            
    mint = query_meta.get("mint")
    if not mint:
        mint = "W" if "west point" in raw_title.lower() else ("S" if "san francisco" in raw_title.lower() else ("D" if "denver" in raw_title.lower() else "P"))
    
    # Clean variety name
    variety = raw_title
    for stopword in (year, "Coin", "US Mint", "United States Mint", "U.S. Mint", "Official", "Silver", "Gold", "Proof", "Uncirculated"):
        variety = re.sub(rf'\b{stopword}\b', '', variety, flags=re.IGNORECASE)
    variety = re.sub(r'\s+', ' ', variety).strip()
    if not variety or len(variety) < 3:
        variety = query_meta.get("original_query", raw_title)
        
    # 3. Extract description
    paragraphs = []
    for p in soup.find_all("p"):
        txt = p.get_text().strip()
        if txt and len(txt) > 80 and not any(kw in txt.lower() for kw in ["copyright", "subscribe", "newsletter"]):
            paragraphs.append(txt)
    desc = "\n\n".join(paragraphs[:3])
    
    # 4. Extract image candidates
    img_urls = []
    for img in soup.find_all("img"):
        src = img.get("src", "") or img.get("data-src", "")
        alt = (img.get("alt", "") or "").lower()
        if not src or len(src) < 10:
            continue
        if src.startswith("/"):
            src = "https://www.usmint.gov" + src if source_type == "usmint" else urlparse(url).scheme + "://" + urlparse(url).netloc + src
            
        # Filter down to potential coin images
        src_lc = src.lower()
        if any(kw in src_lc or kw in alt for kw in ["coin", "obverse", "reverse", "heads", "tails", "product"]):
            if not any(kw in src_lc for kw in ["logo", "icon", "banner", "150x", "300x"]):
                img_urls.append((alt, src))
                
    obv_src, rev_src = None, None
    if img_urls:
        obv_src = next((u for a, u in img_urls if "obverse" in a or "obverse" in u.lower() or "head" in a or "heads" in u.lower()), None)
        rev_src = next((u for a, u in img_urls if "reverse" in a or "reverse" in u.lower() or "tail" in a or "tails" in u.lower()), None)
        if not obv_src:
            obv_src = img_urls[0][1]
        if not rev_src and len(img_urls) > 1:
            rev_src = img_urls[1][1]
            
    # Assemble coin definition
    coin_def = {
        "slug":             re.sub(r'[^a-z0-9_]', '', variety.lower().replace(" ", "_")),
        "series":           "American Eagle" if "eagle" in raw_title.lower() or "eagle" in variety.lower() else "Circulating Coins",
        "denomination":     denomination,
        "variety":          variety,
        "year":             year,
        "mints":            [mint],
        "category":         "coin",
        "composition":      "99.9% Silver" if "silver" in raw_title.lower() or "silver" in variety.lower() else ("91.67% Gold" if "gold" in raw_title.lower() else "Clad"),
        "obverse_desc":     f"Obverse of {variety}",
        "reverse_desc":     f"Reverse of {variety}",
        "mintage":          None
    }
    
    print(f"  Resolved coin meta:")
    print(f"    Series: {coin_def['series']}")
    print(f"    Denomination: {coin_def['denomination']}")
    print(f"    Variety: {coin_def['variety']}")
    print(f"    Year: {coin_def['year']} | Mint: {mint}")
    
    # Match to catalog
    doc_id, confidence, existing_data, action = match_to_catalog(coin_def, mint)
    pct = f"{confidence * 100:.1f}%"
    print(f"  Catalog match: {pct} -> {action}  [{doc_id}]")
    
    # 5. Image waterfall (checks GCS -> uploads resolved)
    obv_url, rev_url = None, None
    attribution = ATTRIBUTION_MINT if source_type == "usmint" else ATTRIBUTION_WIKI
    target_doc_id = doc_id if action == "UPDATE" else _make_doc_id(coin_def, mint)
    
    print(f"  Checking GCS for existing images ...")
    gcs_imgs = check_gcs_existing(target_doc_id)
    obv_url  = gcs_imgs["obverse"]
    rev_url  = gcs_imgs["reverse"]
    
    if obv_url and rev_url:
        print(f"  Both sides already in GCS.")
    else:
        if obv_src and not obv_url:
            obv_url = download_and_upload(obv_src, target_doc_id, "obverse", attribution, dry_run)
        if rev_src and not rev_url:
            rev_url = download_and_upload(rev_src, target_doc_id, "reverse", attribution, dry_run)
            
    # Commit to DB
    result = commit_coin(coin_def, mint, obv_url, rev_url, url, action, doc_id, dry_run=dry_run)
    
    return {
        "status": "success",
        "created": [result["doc_id"]] if action == "CREATE" and result["status"] != "dry_run" else [],
        "updated": [doc_id] if action == "UPDATE" and result["status"] != "dry_run" else [],
        "missing_images": [{"coin": raw_title, "side": "obverse", "doc_id": target_doc_id}] if not obv_url else [],
        "errors": []
    }


def scrape_url(url_or_query: str, dry_run: bool = False) -> dict:
    """
    Main entry point. Accepts any URL or search query, resolves it,
    and ingests coin data and images.
    """
    url = url_or_query.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        print(f"🔍 Input is a query: '{url}'")
        resolved_url = resolve_query_to_url(url)
        if not resolved_url:
            print(f"⚠  Failed to resolve query to a Wikipedia or US Mint URL.")
            return {"status": "error", "message": f"Could not find a valid US Mint or Wikipedia URL for query: {url}"}
        print(f"✓ Resolved to URL: {resolved_url}")
        url = resolved_url
        
    source_type = detect_source_type(url)
    print(f"\n🔗 URL: {url}")
    print(f"   Source type: {source_type}")
    print(f"   Mode: {'DRY-RUN' if dry_run else 'LIVE'}\n")

    # For Wikipedia pages about US coin programs, use the master coin list
    if source_type == "wikipedia" and "semiquincentennial" in url.lower():
        return _ingest_semiquincentennial(url, dry_run)

    # Generic fallback for other URLs
    return _scrape_generic_page(url, dry_run)


def _ingest_semiquincentennial(source_url: str, dry_run: bool) -> dict:
    """
    Ingest all 2026 Semiquincentennial coins using the master definition list.
    Tries Wikimedia Commons first, then US Mint site, then marks as missing.
    """
    results = {
        "source_url": source_url,
        "created": [],
        "updated": [],
        "missing_images": [],
        "errors": [],
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
    }

    total_coins = sum(len(c["mints"]) for c in SEMIQ_COINS)
    print(f"📋 Processing {len(SEMIQ_COINS)} coin types × mints = {total_coins} records\n")

    for coin_def in SEMIQ_COINS:
        for mint in coin_def["mints"]:
            label = f"{coin_def['year']} {coin_def['denomination']} {coin_def['variety']} ({mint})"
            print(f"─── {label}")

            # 1. Match to catalog
            doc_id, confidence, existing_data, action = match_to_catalog(coin_def, mint)
            pct = f"{confidence * 100:.1f}%"
            print(f"  Catalog match: {pct} → {action}  [{doc_id}]")

            # 2. Waterfall image fetch
            obv_url, rev_url = None, None
            attribution = ATTRIBUTION_WIKI
            target_doc_id = _make_doc_id(coin_def, mint)

            # Tier 0: GCS — check our own bucket first
            print(f"  Checking GCS for existing images …")
            gcs_imgs = check_gcs_existing(target_doc_id)
            obv_url  = gcs_imgs["obverse"]
            rev_url  = gcs_imgs["reverse"]

            if obv_url and rev_url:
                print(f"  Both sides already in GCS — skipping external sources.")
            else:
                # Tier 1: Wikimedia Commons (only if GCS is missing one or both)
                print(f"  Fetching images from external sources …")
                wiki_imgs = resolve_wikimedia_coin_images(coin_def, mint)
                wiki_obv  = wiki_imgs["obverse"]
                wiki_rev  = wiki_imgs["reverse"]
                if wiki_obv and not obv_url:
                    obv_url = download_and_upload(wiki_obv, target_doc_id,
                                                   "obverse", ATTRIBUTION_WIKI, dry_run)
                if wiki_rev and not rev_url:
                    rev_url = download_and_upload(wiki_rev, target_doc_id,
                                                   "reverse", ATTRIBUTION_WIKI, dry_run)

                # Tier 2: US Mint website (if still missing one or both)
                if not obv_url or not rev_url:
                    mint_imgs = fetch_usmint_coin_images(coin_def, mint)
                    attribution = ATTRIBUTION_MINT
                    if mint_imgs["obverse"] and not obv_url:
                        obv_url = download_and_upload(mint_imgs["obverse"],
                                                       target_doc_id,
                                                       "obverse", ATTRIBUTION_MINT, dry_run)
                    if mint_imgs["reverse"] and not rev_url:
                        rev_url = download_and_upload(mint_imgs["reverse"],
                                                       target_doc_id,
                                                       "reverse", ATTRIBUTION_MINT, dry_run)

            # Tier 3: Log as missing
            if not obv_url:
                print(f"  ⚠  No obverse image found — added to missing_images_log")
                results["missing_images"].append({
                    "coin": label, "side": "obverse",
                    "doc_id": _make_doc_id(coin_def, mint),
                })
            if not rev_url:
                print(f"  ⚠  No reverse image found — added to missing_images_log")
                results["missing_images"].append({
                    "coin": label, "side": "reverse",
                    "doc_id": _make_doc_id(coin_def, mint),
                })

            # 3. Commit to DB
            result = commit_coin(coin_def, mint, obv_url, rev_url, source_url,
                                  action, doc_id, dry_run=dry_run)

            if result["status"] in ("created", "dry_run") and action == "CREATE":
                results["created"].append(result["doc_id"])
            elif result["status"] in ("updated", "dry_run") and action == "UPDATE":
                results["updated"].append(result["doc_id"])

            print()
            time.sleep(0.5)  # Polite delay

    # Summary
    print("═" * 60)
    print("INGEST SUMMARY")
    print("═" * 60)
    print(f"  Created  (new records) : {len(results['created'])}")
    print(f"  Updated  (existing)    : {len(results['updated'])}")
    print(f"  Missing images         : {len(results['missing_images'])}")
    print(f"  Errors                 : {len(results['errors'])}")
    print("═" * 60)

    if results["missing_images"]:
        print("\n📋 Missing images (add to manual_image_intake.py queue):")
        for m in results["missing_images"]:
            print(f"  {m['coin']} — {m['side']}")

    return results
