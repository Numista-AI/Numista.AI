#!/usr/bin/env python3
"""
rare_coins_image_sourcing.py
============================
Sources obverse + reverse images for 4 specific rare/special coins in
jseaman1204@gmail.com's Firestore collection.

Target coins:
  1. 1987-S Constitution Commemorative Silver Dollar
  2. 2006-P Benjamin Franklin Commemorative Silver Dollar
  3. 2021-W American Silver Eagle Type 1 PF70
  4. 1883 Hawaiian Dime (PCGS slabbed)

Image sources (in priority order per coin):
  - PCGS TrueView API  (cert-based, highest quality)
  - Wikimedia Commons  (named file lookup + keyword search)
  - PCGS CoinFacts page (HTML scrape fallback)
  - Library of Congress (LOC Pictures API, for Hawaiian Dime)

GCS upload:
  users/jseaman1204@gmail.com/coins/{doc_id}/obverse.jpg
  users/jseaman1204@gmail.com/coins/{doc_id}/reverse.jpg
  (DO NOT call blob.make_public())

Usage:
    python rare_coins_image_sourcing.py [--dry-run]
"""

import io
import json
import os
import re
import sys
import time
import argparse
import urllib.parse
import urllib.request
import urllib.error

# ── Fix stdout encoding (Windows) ─────────────────────────────────────────────
sys.stdout = io.TextIOWrapper(
    sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
)

import requests as _req

# ── Config ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SA_KEY     = os.path.join(SCRIPT_DIR, "serviceAccountKey.json.json")
ENV_FILE   = os.path.join(SCRIPT_DIR, ".env")
USER       = "jseaman1204@gmail.com"
BUCKET     = "numista-uploads-studio-9101802118-8c9a8"
UA         = "NumistaAI/1.0 (eric@numista.ai)"
LOG_FILE   = os.path.join(SCRIPT_DIR, "rare_coins_sourcing_log.json")

WIKIMEDIA_API   = "https://commons.wikimedia.org/w/api.php"
PCGS_API_BASE   = "https://api.pcgs.com/publicapi"
LOC_SEARCH_BASE = "https://www.loc.gov/search"

# ── Load .env ─────────────────────────────────────────────────────────────────

def load_env(path: str) -> dict:
    """Parse a simple KEY=VALUE .env file (ignores comments, blank lines)."""
    env = {}
    if not os.path.exists(path):
        return env
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

ENV = load_env(ENV_FILE)
PCGS_TOKEN   = ENV.get("PCGS_ACCESS_TOKEN", "")
PCGS_TOKEN_2 = ENV.get("PCGS_ALT_TOKEN", "")   # alt token if primary fails

# ── Target coins (searched dynamically in Firestore; doc_ids filled at runtime) ─

# ── Hardcoded doc IDs (discovered by Firestore scan 2026-06-22) ───────────────
# Year field uses combined format: "1987S", "2006P" (no space between year & mint)
# Program/Series holds original description text, not a canonical program name
# Cert numbers: none found in these 4 docs — PCGS API not usable for these coins
TARGET_COINS = [
    {
        "id":    "coin1",
        "label": "1987-S Constitution Commemorative Silver Dollar",
        # Firestore doc: Year='1987S', Program/Series='Consitution silver dollar commemorative in case79.95'
        "doc_id":      "8fb30fc1-8a61-48c6-bd35-e5511ad31798",
        "cert_number": None,
        "doc_data":    None,
        "wikimedia_obverse_candidates": [
            "File:1987 Constitution Silver Dollar obverse.jpg",
            "File:1987-S Constitution commemorative silver dollar obverse.jpg",
            "File:US 1987 Constitution silver dollar obverse.jpg",
            "File:1987 US Constitution Bicentennial Dollar Obverse.jpg",
            "File:1987-S Constitution dollar obverse.jpg",
            "File:Constitution silver dollar 1987.jpg",
            "File:US-1987-Constitution-silver-dollar-obverse.jpg",
            "File:1987 US Constitution Bicentennial commemorative dollar obverse.jpg",
        ],
        "wikimedia_obverse_search": "1987 constitution silver dollar obverse commemorative",
        "wikimedia_reverse_candidates": [
            "File:1987 Constitution Silver Dollar reverse.jpg",
            "File:1987-S Constitution commemorative silver dollar reverse.jpg",
            "File:US 1987 Constitution silver dollar reverse.jpg",
            "File:1987 US Constitution Bicentennial Dollar Reverse.jpg",
            "File:Constitution silver dollar 1987 reverse.jpg",
            "File:1987-S Constitution dollar reverse.jpg",
        ],
        "wikimedia_reverse_search": "1987 constitution silver dollar reverse bicentennial",
        "pcgs_coinfacts_url": "https://www.pcgs.com/coinfacts/coin/1987-s-1-constitution-commem/9709",
    },
    {
        "id":    "coin2",
        "label": "2006-P Benjamin Franklin Commemorative Silver Dollar",
        # Firestore doc: Year='2006P', Program/Series='Franklin dollar commemorative "Scientist" no case PR63'
        "doc_id":      "739baa56-197f-414a-8df1-dd40c29fdbcf",
        "cert_number": None,
        "doc_data":    None,
        "wikimedia_obverse_candidates": [
            "File:2006 Franklin Founding Father Silver Dollar Obverse.jpg",
            "File:2006 Benjamin Franklin commemorative dollar obverse.jpg",
            "File:2006-P Benjamin Franklin dollar obverse.jpg",
            "File:Benjamin Franklin commemorative dollar 2006 obverse.jpg",
            "File:Franklin founding father dollar 2006.jpg",
            "File:2006 Benjamin Franklin Founding Father Commemorative Silver Dollar obverse.jpg",
            "File:US-2006-BenjaminFranklin-dollar-obverse.jpg",
        ],
        "wikimedia_obverse_search": "2006 benjamin franklin commemorative silver dollar obverse founding father",
        "wikimedia_reverse_candidates": [
            "File:2006 Franklin Founding Father Silver Dollar Reverse.jpg",
            "File:2006 Benjamin Franklin commemorative dollar reverse.jpg",
            "File:2006-P Benjamin Franklin dollar reverse.jpg",
            "File:Benjamin Franklin commemorative dollar 2006 reverse.jpg",
            "File:2006 Benjamin Franklin Founding Father Commemorative Silver Dollar reverse.jpg",
            "File:US-2006-BenjaminFranklin-dollar-reverse.jpg",
        ],
        "wikimedia_reverse_search": "2006 benjamin franklin commemorative dollar reverse founding father scientist",
        "pcgs_coinfacts_url": "https://www.pcgs.com/coinfacts/coin/2006-p-1-benjamin-franklin-founding-father-commem/93685",
    },
    {
        "id":    "coin3",
        "label": "2021-W American Silver Eagle Type 1 PF70",
        # Firestore doc: Year='2021', Mint Mark='W', Program/Series='2021 W ASE T-1 FDOI PF70 ULTRA CAMEO signed by John Mercanti'
        "doc_id":      "2e922f8d-b9ff-4fde-8868-c40414305f4a",
        "cert_number": None,   # no cert # in doc; PCGS API not applicable
        "doc_data":    None,
        "wikimedia_obverse_candidates": [
            "File:2021 American Silver Eagle Type 1 Proof obverse.jpg",
            "File:2021-W American Silver Eagle Proof obverse.jpg",
            "File:2021 Silver Eagle Type 1 proof obverse.jpg",
            "File:American Silver Eagle 2021 type 1 obverse.jpg",
            "File:2021 ASE Type I PF obverse.jpg",
            "File:Silver Eagle 2021 proof coin obverse.jpg",
            "File:2021 W American Silver Eagle T1 proof obverse.jpg",
        ],
        "wikimedia_obverse_search": "2021 american silver eagle type 1 proof obverse walking liberty",
        "wikimedia_reverse_candidates": [
            "File:2021 American Silver Eagle Type 1 Proof reverse.jpg",
            "File:2021-W American Silver Eagle Proof reverse.jpg",
            "File:2021 Silver Eagle Type 1 proof reverse.jpg",
            "File:American Silver Eagle 2021 type 1 reverse.jpg",
            "File:2021 W American Silver Eagle T1 proof reverse.jpg",
        ],
        "wikimedia_reverse_search": "2021 american silver eagle type 1 proof reverse heraldic eagle",
        "pcgs_coinfacts_url": None,
    },
    {
        "id":    "coin4",
        "label": "1883 Hawaiian Dime (PCGS slabbed)",
        # Firestore doc: Year='1883', Denomination='Dime', Program/Series='Hawaiian Silver Dime PCGS'
        "doc_id":      "d283d60b-5cb1-4632-a505-ba2dd6fbc754",
        "cert_number": None,
        "doc_data":    None,
        "wikimedia_obverse_candidates": [
            "File:1883 Hawaii dime obverse.jpg",
            "File:Hawaii dime 1883 obverse.jpg",
            "File:1883 Hawaiian dime obverse.jpg",
            "File:Hawaiian Kingdom dime 1883 obverse.jpg",
            "File:1883 Hawaii ten cents obverse.jpg",
            "File:Kalakaua dime 1883 obverse.jpg",
        ],
        "wikimedia_obverse_search": "1883 hawaii dime obverse hawaiian kingdom kalakaua",
        "wikimedia_reverse_candidates": [
            "File:1883 Hawaii dime reverse.jpg",
            "File:Hawaii dime 1883 reverse.jpg",
            "File:1883 Hawaiian dime reverse.jpg",
            "File:Hawaiian Kingdom dime 1883 reverse.jpg",
            "File:Kalakaua dime 1883 reverse.jpg",
            "File:KINGDOM OF HAWAII, KALAKAUA I, 1883 -DIME a - Flickr - woody1778a.jpg",
        ],
        "wikimedia_reverse_search": "1883 hawaii dime reverse hawaiian kalakaua kingdom",
        "pcgs_coinfacts_url": "https://www.pcgs.com/coinfacts/coin/1883-10c/4843",
        "loc_search": "hawaiian dime 1883 kalakaua",
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
# ── Step 1: Firestore — find the 4 coins ─────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def init_clients():
    """Initialize GCS + Firestore clients from service-account key."""
    from google.cloud import storage, firestore
    from google.oauth2 import service_account

    creds = service_account.Credentials.from_service_account_file(SA_KEY)
    gcs = storage.Client(credentials=creds, project=creds.project_id)
    db  = firestore.Client(credentials=creds, project=creds.project_id)
    return gcs, db


def _normalize(val) -> str:
    """Return a lowercase stripped string for fuzzy matching."""
    if val is None:
        return ""
    return str(val).lower().strip()


def _field_candidates(data: dict, *keys) -> list[str]:
    """Collect all non-empty values for any of the given keys."""
    out = []
    for k in keys:
        v = data.get(k)
        if v and str(v).strip():
            out.append(_normalize(v))
    return out


def match_coin(data: dict, target: dict) -> bool:
    """
    Return True if a Firestore document matches the target coin's criteria.
    Matching is intentionally fuzzy to handle varied field names.
    """
    # ── Year ──────────────────────────────────────────────────────────────────
    year_vals = _field_candidates(data, "Year", "year", "coin_year", "date")
    if target["year"] and not any(target["year"] in v for v in year_vals):
        return False

    # ── Mint mark (optional) ──────────────────────────────────────────────────
    if target.get("mint"):
        mint_vals = _field_candidates(
            data, "Mint", "Mint Mark", "mint_mark", "mintMark", "mint"
        )
        if not any(target["mint"].lower() in v for v in mint_vals):
            return False

    # ── Denomination (optional) ───────────────────────────────────────────────
    if target.get("denomination_contains"):
        denom_vals = _field_candidates(
            data, "Denomination", "denomination", "type", "currency"
        )
        want = target["denomination_contains"].lower()
        if not any(want in v for v in denom_vals):
            return False

    # ── Program / series / theme (contains match) ─────────────────────────────
    if target.get("program_contains"):
        prog_vals = _field_candidates(
            data,
            "Program/Series", "program", "Program", "Series", "series",
            "Theme", "theme", "Country", "country", "Description", "description",
            "name", "Name", "title",
        )
        want = target["program_contains"].lower()
        if not any(want in v for v in prog_vals):
            return False

    # ── Grade (optional, for Silver Eagle PF70) ────────────────────────────────
    if target.get("grade_contains"):
        grade_vals = _field_candidates(
            data,
            "Condition", "condition", "Grade", "grade",
            "Grading", "grading", "pcgs_grade", "ngc_grade",
        )
        want = target["grade_contains"].lower()
        if not any(want in v for v in grade_vals):
            # Soft-fail: if grade info completely missing (many docs don't have it),
            # still consider it a potential match if all other criteria pass.
            # Log a note but don't disqualify.
            pass

    return True


def extract_cert_number(data: dict) -> str | None:
    """Return the best cert/certification number from a document."""
    for k in (
        "Cert Number", "cert_number", "certNumber", "Cert #",
        "PCGS Cert #", "NGC Cert #", "CertNo", "cert_no",
        "certification_number", "CertificationNumber",
    ):
        v = data.get(k)
        if v and str(v).strip():
            return str(v).strip()
    return None


def find_coins_in_firestore(db) -> None:
    """
    Verify the 4 hardcoded Firestore doc IDs and load their data.
    Doc IDs were discovered by scanning the collection on 2026-06-22.
    """
    print("\n" + "=" * 60)
    print("STEP 1: Verifying 4 target coin docs in Firestore")
    print("=" * 60)

    coins_ref = db.collection(f"users/{USER}/coins")

    for target in TARGET_COINS:
        doc_id = target["doc_id"]
        print(f"\n  Verifying: {target['label']}")
        print(f"  doc_id: {doc_id}")

        doc = coins_ref.document(doc_id).get()
        if not doc.exists:
            print(f"    ✗ Doc NOT FOUND in Firestore — doc_id may be stale")
            target["doc_id"] = None
            continue

        data = doc.to_dict() or {}
        target["doc_data"] = data
        cert = extract_cert_number(data)
        target["cert_number"] = cert

        year  = data.get("Year", "")
        prog  = data.get("Program/Series", "")
        denom = data.get("Denomination", "")
        print(f"    ✓ Verified: Year={year!r}, Denom={denom!r}")
        print(f"    ✓ Program: {str(prog)[:70]!r}")
        print(f"    ✓ Cert#: {cert or '(none)'}")


# ═══════════════════════════════════════════════════════════════════════════════
# ── Step 2a: PCGS API helpers ─────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def pcgs_request(path: str, token: str) -> tuple[int, any]:
    """Make a GET request to the PCGS Public API."""
    url = PCGS_API_BASE + path
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept":        "application/json",
        "User-Agent":    UA,
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        return e.code, body
    except Exception as ex:
        return 0, str(ex)


def pcgs_get_images_by_cert(cert_no: str) -> dict | None:
    """
    Try PCGS GetCoinFactsByCertNumber and GetCoinImagesByCertNo endpoints.
    Returns a dict with 'obverse_url' and/or 'reverse_url' if found.
    """
    if not cert_no:
        return None

    tokens_to_try = [t for t in [PCGS_TOKEN, PCGS_TOKEN_2] if t]
    if not tokens_to_try:
        print("    ✗ No PCGS tokens available")
        return None

    # Clean cert number (strip any letters/spaces)
    cert_clean = re.sub(r"[^\d]", "", cert_no)
    if not cert_clean:
        print(f"    ✗ Could not parse cert number: {cert_no!r}")
        return None

    endpoints = [
        f"/coindetail/GetCoinFactsByCertNumber?certno={cert_clean}",
        f"/coindetail/GetCoinImagesByCertNo/{cert_clean}",
        f"/coindetail/GetCoinFactsByBarcode?barcode={cert_clean}",
    ]

    for token in tokens_to_try:
        token_label = "primary" if token == PCGS_TOKEN else "alt"
        for endpoint in endpoints:
            print(f"    PCGS [{token_label}] GET {endpoint[:60]}…")
            status, data = pcgs_request(endpoint, token)
            print(f"    → HTTP {status}")

            if status == 200 and isinstance(data, dict):
                result = {}
                # Look for image URLs in common PCGS response keys
                for key in (
                    "ObverseImageUrl", "obverseImageUrl", "ImageFront", "imagefront",
                    "ObvImage", "obvImage", "FrontImage", "frontImage",
                    "TrueViewFront", "trueviewFront", "ImageObverse", "imageObverse",
                ):
                    v = data.get(key, "")
                    if v and str(v).startswith("http"):
                        result["obverse_url"] = str(v)
                        break
                for key in (
                    "ReverseImageUrl", "reverseImageUrl", "ImageBack", "imageback",
                    "RevImage", "revImage", "BackImage", "backImage",
                    "TrueViewBack", "trueviewBack", "ImageReverse", "imageReverse",
                ):
                    v = data.get(key, "")
                    if v and str(v).startswith("http"):
                        result["reverse_url"] = str(v)
                        break

                # Also check nested structures
                for sub_key in ("images", "Images", "coinImages", "CoinImages"):
                    sub = data.get(sub_key)
                    if isinstance(sub, dict):
                        for ok in ("obverse", "front", "ObverseUrl", "FrontUrl"):
                            if sub.get(ok, "").startswith("http"):
                                result.setdefault("obverse_url", sub[ok])
                        for rk in ("reverse", "back", "ReverseUrl", "BackUrl"):
                            if sub.get(rk, "").startswith("http"):
                                result.setdefault("reverse_url", sub[rk])
                    elif isinstance(sub, list):
                        for item in sub:
                            if isinstance(item, dict):
                                for ok in ("obverse", "front", "ObverseUrl", "FrontUrl", "url"):
                                    if item.get(ok, "").startswith("http"):
                                        result.setdefault("obverse_url", item[ok])

                if result:
                    print(f"    ✓ PCGS images found: {list(result.keys())}")
                    return result
                else:
                    print(f"    · No image URLs in response (keys: {list(data.keys())[:8]})")

            time.sleep(0.5)

    print("    ✗ PCGS API — no images found for cert:", cert_no)
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# ── Step 2b: Wikimedia Commons helpers ───────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def wiki_resolve_filename(filename: str) -> str | None:
    """Resolve a Wikimedia 'File:...' title to a direct image URL."""
    params = {
        "action": "query",
        "titles": filename,
        "prop":   "imageinfo",
        "iiprop": "url|mediatype",
        "format": "json",
    }
    try:
        resp = _req.get(WIKIMEDIA_API, params=params,
                        headers={"User-Agent": UA}, timeout=15)
        resp.raise_for_status()
        pages = resp.json().get("query", {}).get("pages", {})
        for page in pages.values():
            if page.get("missing") is not None or page.get("ns") == -1:
                return None
            for info in page.get("imageinfo", []):
                url = info.get("url", "")
                mt  = info.get("mediatype", "")
                if mt in ("OFFICE", "PDF") or url.lower().endswith(".pdf"):
                    return None
                if url.startswith("http"):
                    return url
    except Exception as e:
        print(f"    ✗ wiki_resolve: {e}")
    return None


def wiki_search(query: str, limit: int = 15) -> list[str]:
    """Search Wikimedia Commons; return a list of 'File:...' titles."""
    params = {
        "action":      "query",
        "list":        "search",
        "srnamespace": "6",
        "srsearch":    query,
        "srlimit":     str(limit),
        "format":      "json",
    }
    try:
        resp = _req.get(WIKIMEDIA_API, params=params,
                        headers={"User-Agent": UA}, timeout=15)
        resp.raise_for_status()
        hits = resp.json().get("query", {}).get("search", [])
        results = []
        for h in hits:
            title = h.get("title", "")
            if title.startswith("File:"):
                ext = title.lower()
                if any(ext.endswith(s) for s in (".jpg", ".jpeg", ".png", ".tif", ".tiff")):
                    results.append(title)
        return results
    except Exception as e:
        print(f"    ✗ wiki_search error: {e}")
    return []


def find_wikimedia_image(candidates: list[str], search_query: str) -> tuple[str | None, str | None]:
    """
    Try named candidates then search.
    Returns (direct_image_url, filename_used) or (None, None).
    """
    # 1. Named candidates
    for filename in candidates:
        print(f"    Trying: {filename}")
        url = wiki_resolve_filename(filename)
        if url:
            print(f"    ✓ Found: {url[:90]}…")
            return url, filename
        time.sleep(0.25)

    # 2. Keyword search fallback
    if search_query:
        print(f"    Searching: '{search_query}'")
        hits = wiki_search(search_query)
        for title in hits:
            print(f"    Trying search result: {title}")
            url = wiki_resolve_filename(title)
            if url:
                print(f"    ✓ Found via search: {url[:90]}…")
                return url, title
            time.sleep(0.25)

    print(f"    ✗ No Wikimedia image found")
    return None, None


# ═══════════════════════════════════════════════════════════════════════════════
# ── Step 2c: Library of Congress fallback ────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def loc_search_image(query: str) -> str | None:
    """
    Search Library of Congress Pictures for a coin image.
    Returns a direct image URL if found.
    """
    params = {
        "q":  query,
        "fo": "json",
        "fa": "online-format:image",
        "c":  "5",
    }
    url = LOC_SEARCH_BASE + "?" + urllib.parse.urlencode(params)
    print(f"    LOC search: {url[:100]}…")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
        results = data.get("results", [])
        for item in results:
            # Try to get a JPEG URL from the item
            for img_key in ("image_url", "url", "thumb_gallery", "thumbnail"):
                img = item.get(img_key)
                if isinstance(img, list):
                    img = img[0] if img else None
                if img and str(img).startswith("http"):
                    print(f"    ✓ LOC image found: {str(img)[:80]}…")
                    return str(img)
    except Exception as e:
        print(f"    ✗ LOC search error: {e}")
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# ── Step 2d: PCGS CoinFacts page scrape (last resort) ────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def pcgs_coinfacts_scrape(url: str) -> dict | None:
    """
    Attempt to extract coin image URLs from a PCGS CoinFacts page.
    Returns {'obverse_url': ..., 'reverse_url': ...} or None.
    """
    if not url:
        return None
    print(f"    Scraping PCGS CoinFacts: {url}")
    headers = {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=25) as r:
            html = r.read().decode("utf-8", errors="replace")

        result = {}
        # PCGS typically serves coin images in <img> tags with src patterns:
        # https://images.pcgs.com/coinimages/...
        # https://d1olcj6yjca4eh.cloudfront.net/...
        img_patterns = [
            r'https://images\.pcgs\.com/[^"\'>\s]+\.jpg',
            r'https://d1olcj6yjca4eh\.cloudfront\.net/[^"\'>\s]+\.jpg',
            r'https://[^"\'>\s]*pcgs[^"\'>\s]*(?:obverse|obv|front)[^"\'>\s]*\.(?:jpg|png)',
            r'https://[^"\'>\s]*pcgs[^"\'>\s]*(?:reverse|rev|back)[^"\'>\s]*\.(?:jpg|png)',
        ]
        found_imgs = []
        for pat in img_patterns:
            found_imgs.extend(re.findall(pat, html, re.IGNORECASE))

        found_imgs = list(dict.fromkeys(found_imgs))  # deduplicate, preserve order

        if found_imgs:
            print(f"    ✓ Found {len(found_imgs)} PCGS CoinFacts image(s)")
            # First image → obverse, second → reverse (PCGS convention)
            if len(found_imgs) >= 1:
                result["obverse_url"] = found_imgs[0]
            if len(found_imgs) >= 2:
                result["reverse_url"] = found_imgs[1]
            return result if result else None

    except Exception as e:
        print(f"    ✗ CoinFacts scrape error: {e}")
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# ── Step 3: Source images for each coin ──────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def source_images_for_coin(target: dict) -> dict:
    """
    Run the full sourcing pipeline for a single target coin.
    Returns a result dict with obverse_url, reverse_url, sources.
    """
    label = target["label"]
    cert  = target["cert_number"]
    print(f"\n{'─'*60}")
    print(f"Sourcing images for: {label}")
    print(f"  doc_id:      {target['doc_id'] or '(not found)'}")
    print(f"  cert_number: {cert or '(none)'}")
    print(f"{'─'*60}")

    result = {
        "label":       label,
        "doc_id":      target["doc_id"],
        "cert_number": cert,
        "obverse_url":    None,
        "reverse_url":    None,
        "obverse_source": None,
        "reverse_source": None,
        "obverse_filename": None,
        "reverse_filename": None,
    }

    if target["doc_id"] is None:
        print("  ⚠ No Firestore doc found — skipping image sourcing")
        return result

    # ── A. Try PCGS TrueView (cert-based) ────────────────────────────────────
    if cert:
        print(f"\n  [A] PCGS TrueView API (cert={cert})")
        pcgs_result = pcgs_get_images_by_cert(cert)
        if pcgs_result:
            if pcgs_result.get("obverse_url"):
                result["obverse_url"]    = pcgs_result["obverse_url"]
                result["obverse_source"] = "pcgs_trueview"
                print(f"  ✓ PCGS obverse: {result['obverse_url'][:80]}…")
            if pcgs_result.get("reverse_url"):
                result["reverse_url"]    = pcgs_result["reverse_url"]
                result["reverse_source"] = "pcgs_trueview"
                print(f"  ✓ PCGS reverse: {result['reverse_url'][:80]}…")

    # ── B. Wikimedia Commons (obverse) ────────────────────────────────────────
    if not result["obverse_url"]:
        print(f"\n  [B] Wikimedia Commons — obverse")
        obv_url, obv_fn = find_wikimedia_image(
            target.get("wikimedia_obverse_candidates", []),
            target.get("wikimedia_obverse_search", ""),
        )
        if obv_url:
            result["obverse_url"]      = obv_url
            result["obverse_source"]   = "wikimedia_commons"
            result["obverse_filename"] = obv_fn

    # ── C. Wikimedia Commons (reverse) ────────────────────────────────────────
    if not result["reverse_url"]:
        print(f"\n  [C] Wikimedia Commons — reverse")
        rev_url, rev_fn = find_wikimedia_image(
            target.get("wikimedia_reverse_candidates", []),
            target.get("wikimedia_reverse_search", ""),
        )
        if rev_url:
            result["reverse_url"]      = rev_url
            result["reverse_source"]   = "wikimedia_commons"
            result["reverse_filename"] = rev_fn

    # ── D. PCGS CoinFacts scrape (if still missing) ───────────────────────────
    cf_url = target.get("pcgs_coinfacts_url")
    if cf_url and (not result["obverse_url"] or not result["reverse_url"]):
        print(f"\n  [D] PCGS CoinFacts scrape fallback")
        cf_result = pcgs_coinfacts_scrape(cf_url)
        if cf_result:
            if not result["obverse_url"] and cf_result.get("obverse_url"):
                result["obverse_url"]    = cf_result["obverse_url"]
                result["obverse_source"] = "pcgs_coinfacts"
            if not result["reverse_url"] and cf_result.get("reverse_url"):
                result["reverse_url"]    = cf_result["reverse_url"]
                result["reverse_source"] = "pcgs_coinfacts"

    # ── E. Library of Congress (Hawaiian Dime special case) ───────────────────
    loc_query = target.get("loc_search")
    if loc_query and not result["obverse_url"]:
        print(f"\n  [E] Library of Congress image search")
        loc_url = loc_search_image(loc_query)
        if loc_url:
            result["obverse_url"]    = loc_url
            result["obverse_source"] = "library_of_congress"

    print(f"\n  RESULT: obverse={'✓' if result['obverse_url'] else '✗'}  "
          f"reverse={'✓' if result['reverse_url'] else '✗'}")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# ── Step 4: Download + upload to GCS ─────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def download_bytes(url: str) -> bytes | None:
    """Download image bytes from any URL."""
    headers = {
        "User-Agent": UA,
        "Accept":     "image/*,*/*;q=0.8",
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        print(f"    Downloaded {len(data):,} bytes")
        return data
    except Exception as e:
        print(f"    ✗ Download failed: {e}")
        return None


def content_type_from_url(url: str) -> str:
    url_lower = url.lower().split("?")[0]
    if url_lower.endswith(".png"):
        return "image/png"
    if url_lower.endswith(".gif"):
        return "image/gif"
    if url_lower.endswith(".tif") or url_lower.endswith(".tiff"):
        return "image/tiff"
    return "image/jpeg"


def upload_to_gcs(gcs_client, image_bytes: bytes, gcs_path: str,
                  content_type: str = "image/jpeg") -> str | None:
    """Upload bytes to GCS. Returns public URL (no make_public call)."""
    bucket = gcs_client.bucket(BUCKET)
    blob   = bucket.blob(gcs_path)
    blob.upload_from_string(image_bytes, content_type=content_type)
    url = f"https://storage.googleapis.com/{BUCKET}/{gcs_path}"
    print(f"    ✓ Uploaded → {url}")
    return url


def upload_coin_images(
    gcs_client,
    doc_id: str,
    obverse_url_src: str | None,
    reverse_url_src: str | None,
    dry_run: bool,
) -> dict:
    """Download source images and upload to GCS. Returns dict of GCS URLs."""
    out = {"obverse_gcs_url": None, "reverse_gcs_url": None}

    for side, src_url in [("obverse", obverse_url_src), ("reverse", reverse_url_src)]:
        if not src_url:
            continue
        print(f"    Downloading {side}: {src_url[:80]}…")
        img_bytes = download_bytes(src_url)
        if not img_bytes:
            print(f"    ✗ Could not download {side} image")
            continue

        ct       = content_type_from_url(src_url)
        ext      = "jpg" if ct == "image/jpeg" else ct.split("/")[-1]
        gcs_path = f"users/{USER}/coins/{doc_id}/{side}.{ext}"

        if dry_run:
            gcs_url = f"https://storage.googleapis.com/{BUCKET}/{gcs_path}"
            print(f"    [DRY RUN] Would upload {side} → {gcs_url}")
        else:
            gcs_url = upload_to_gcs(gcs_client, img_bytes, gcs_path, ct)

        out[f"{side}_gcs_url"] = gcs_url

    return out


# ═══════════════════════════════════════════════════════════════════════════════
# ── Step 5: Firestore update ──────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def update_firestore(db, doc_id: str, updates: dict, dry_run: bool) -> dict:
    """Write image URL / source fields to Firestore."""
    if not updates:
        return {"status": "skipped"}

    if dry_run:
        print(f"    [DRY RUN] Would write to Firestore: {updates}")
        return {"status": "dry_run", "fields": list(updates.keys())}

    doc_ref = db.collection(f"users/{USER}/coins").document(doc_id)
    doc_ref.update(updates)
    print(f"    ✓ Firestore updated: {doc_id}")
    return {"status": "updated", "fields": list(updates.keys())}


# ═══════════════════════════════════════════════════════════════════════════════
# ── Step 6: Report ────────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def print_report(all_results: list[dict]) -> None:
    print("\n" + "=" * 70)
    print("FINAL REPORT — Rare Coin Image Sourcing")
    print("=" * 70)
    header = f"{'#':<3} {'Coin':<45} {'FS?':<5} {'OBV':<5} {'REV':<5} {'Source'}"
    print(header)
    print("-" * 70)
    for i, r in enumerate(all_results, 1):
        fs_found  = "YES" if r.get("doc_id") else "NO"
        obv_found = "YES" if r.get("obverse_gcs_url") else ("URL" if r.get("obverse_url") else "NO")
        rev_found = "YES" if r.get("reverse_gcs_url") else ("URL" if r.get("reverse_url") else "NO")
        src = r.get("obverse_source") or r.get("reverse_source") or "—"
        label = r["label"][:44]
        print(f"{i:<3} {label:<45} {fs_found:<5} {obv_found:<5} {rev_found:<5} {src}")

    print("=" * 70)
    print("\nDetailed per-coin results:")
    for r in all_results:
        print(f"\n  ► {r['label']}")
        print(f"    Firestore doc found:  {'YES — ' + r['doc_id'] if r.get('doc_id') else 'NO'}")
        print(f"    Cert number:          {r.get('cert_number') or '(none)'}")
        print(f"    Obverse uploaded:     {r.get('obverse_gcs_url') or '(no)'}")
        print(f"    Obverse source:       {r.get('obverse_source') or '—'}")
        print(f"    Obverse filename:     {r.get('obverse_filename') or '—'}")
        print(f"    Reverse uploaded:     {r.get('reverse_gcs_url') or '(no)'}")
        print(f"    Reverse source:       {r.get('reverse_source') or '—'}")
        print(f"    Reverse filename:     {r.get('reverse_filename') or '—'}")


# ═══════════════════════════════════════════════════════════════════════════════
# ── Main ──────────────────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Source images for 4 rare coins in jseaman1204@gmail.com Firestore collection."
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Simulate without writing to GCS or Firestore.")
    args    = parser.parse_args()
    dry_run = args.dry_run

    if dry_run:
        print("*** DRY RUN — no GCS uploads or Firestore writes ***\n")

    log = {
        "script":    "rare_coins_image_sourcing.py",
        "user":      USER,
        "dry_run":   dry_run,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results":   [],
    }

    # ── Init clients ─────────────────────────────────────────────────────────
    print("Initializing GCS and Firestore clients…")
    gcs, db = init_clients()
    print("✓ Clients ready\n")

    # ── Step 1: Find docs in Firestore ───────────────────────────────────────
    find_coins_in_firestore(db)

    # ── Steps 2–5: Per-coin sourcing + upload ─────────────────────────────────
    all_results = []

    print("\n" + "=" * 60)
    print("STEP 2–5: Sourcing, downloading, uploading images")
    print("=" * 60)

    for target in TARGET_COINS:
        # Source image URLs
        img_result = source_images_for_coin(target)

        # Upload to GCS
        if target["doc_id"]:
            print(f"\n  Uploading images for: {target['label']}")
            gcs_result = upload_coin_images(
                gcs,
                target["doc_id"],
                img_result.get("obverse_url"),
                img_result.get("reverse_url"),
                dry_run=dry_run,
            )
        else:
            gcs_result = {"obverse_gcs_url": None, "reverse_gcs_url": None}

        # Build Firestore update payload
        fs_update = {}
        if gcs_result.get("obverse_gcs_url"):
            fs_update["image_url_obverse"]    = gcs_result["obverse_gcs_url"]
            fs_update["image_source_obverse"] = img_result.get("obverse_source") or "unknown"
        if gcs_result.get("reverse_gcs_url"):
            fs_update["image_url_reverse"]    = gcs_result["reverse_gcs_url"]
            fs_update["image_source_reverse"] = img_result.get("reverse_source") or "unknown"

        # Write to Firestore
        fs_status = {}
        if target["doc_id"] and fs_update:
            fs_status = update_firestore(db, target["doc_id"], fs_update, dry_run=dry_run)

        # Merge result
        combined = {
            **img_result,
            **gcs_result,
            "obverse_filename": img_result.get("obverse_filename"),
            "reverse_filename": img_result.get("reverse_filename"),
            "firestore": fs_status,
        }
        all_results.append(combined)
        log["results"].append(combined)

        time.sleep(0.3)

    # ── Step 6: Report ────────────────────────────────────────────────────────
    print_report(all_results)

    # ── Save log ──────────────────────────────────────────────────────────────
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, default=str)
    print(f"\n📁 Log saved to: {LOG_FILE}")


if __name__ == "__main__":
    main()
