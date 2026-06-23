import yfinance as yf
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import io
import uuid
import json
import base64
from datetime import datetime
import pandas as pd
from google.cloud import firestore
from google.cloud import storage as gcs
import google.auth
from google.cloud import documentai

# AI SDK — google-genai (replaces deprecated vertexai SDK, shutdown Jun 24 2026)
# Migration guide: https://cloud.google.com/vertex-ai/generative-ai/docs/deprecations/genai-vertexai-sdk
from google import genai
from google.genai import types as genai_types
import feedparser
import re

# Morgan's coin knowledge base RAG lookup
try:
    from morgan_knowledge import get_coin_context
    MORGAN_KNOWLEDGE_AVAILABLE = True
except ImportError:
    MORGAN_KNOWLEDGE_AVAILABLE = False
    print("[startup] morgan_knowledge.py not found — coin reference lookup disabled")

app = FastAPI(title="Numista.AI Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://numista.ai",
        "https://www.numista.ai",
        "https://numista-vault.web.app",      # Firebase Hosting (production)
        "https://numista-vault.firebaseapp.com",  # Firebase Hosting (alt URL)
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── VERTEX AI SEARCH — Coin Reference Library ───────────────────────────────
# Registers GET /api/coin_search — open endpoint, no auth required.
# Data store: numista-coin-library (1,913 coin documents, Enterprise + LLM tier)
try:
    from vertex_search.coin_search_endpoint import register_coin_search
    register_coin_search(app)
    print("[startup] Vertex AI Search endpoint registered: GET /api/coin_search")
except Exception as _vx_err:
    print(f"[startup] Vertex AI Search not available: {_vx_err}")

PROJECT_ID = "studio-9101802118-8c9a8"
LOCATION = "us-central1"

# ─── GCS USER CONTENT BUCKET ────────────────────────────────────────────────
# All user-uploaded files live here under a structured path:
#   gs://numista-user-content/{user_email}/{content_type}/{uuid}/
# Sub-folders: binder_scans/ | checklists/ | microscope/ | invoices/
USER_CONTENT_BUCKET = "numista-uploads-studio-9101802118-8c9a8"

# Initialize Firebase/Firestore 
credentials, _ = google.auth.default()
db = firestore.Client(credentials=credentials, project=PROJECT_ID)

# Initialize GCS client (shares same SA credentials)
gcs_client = gcs.Client(credentials=credentials, project=PROJECT_ID)

# ─── GEMINI MODEL CONFIGURATION ──────────────────────────────────────────────
# Per official deprecation schedule as of Jun 11, 2026
# (see: Gemini Models as of 11 JUN 2026.png)
#
#   gemini-3.5-flash       Released May 19, 2026. NO shutdown announced. → PRIMARY
#   gemini-3.1-pro-preview Released Feb 19, 2026. NO shutdown announced. → PRO
#   gemini-3.1-flash-lite  Released May 7, 2026.  Shutdown May 7, 2027.  → lite tasks
#
# NOTE: gemini-3-pro-preview SHUT DOWN Mar 9, 2026 — do NOT use.
# NOTE: All Gemini 3.x models require location='global' on Vertex AI.
PRIMARY_MODEL = "gemini-3.5-flash"
PRO_MODEL     = "gemini-3.1-pro-preview"

# Initialize google-genai client (Vertex AI backend)
# REGION: gemini-3-x-preview models require 'global' — stable gemini-2.5-x
# models could use 'us-central1', but since we're on preview, global is correct.
# Override via GEMINI_LOCATION env var if needed.
GEMINI_LOCATION = os.environ.get("GEMINI_LOCATION", "global")
genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=GEMINI_LOCATION)


# --- NUMISMATIC CONSTANTS ---
COIN_DICTIONARY = [
    { "val": 0.01, "formal": "Lincoln Cent", "slang": ["penny", "wheatie", "steelie", "red cent", "lincoln wheat cent", "wheat cent"] },
    { "val": 0.05, "formal": "Jefferson Nickel", "slang": ["nickel", "buffalo", "war nickel", "v-nickel", "buffalo nickel"] },
    { "val": 0.10, "formal": "Roosevelt Dime", "slang": ["dime", "mercury", "rosie", "winged liberty", "mercury dime"] },
    { "val": 0.25, "formal": "Washington Quarter", "slang": ["quarter", "two bits", "state quarter", "2026 semiquin"] },
    { "val": 0.50, "formal": "Kennedy Half Dollar", "slang": ["half", "fifty cent", "franklin", "walker", "walking liberty"] },
    { "val": 1.00, "formal": "Morgan Silver Dollar", "slang": ["morgan", "silver dollar", "cartwheel", "peace dollar", "peace"] }
]

# ── Normalization dictionaries ─────────────────────────────────────────────────
# Used by import_spreadsheet and the backfill endpoint to interpret colloquial,
# abbreviated, or inconsistently-formatted coin data entered by collectors.

# Coin nicknames → official Program/Series name
COIN_NICKNAMES: dict[str, str] = {
    # Dollars
    'ike': 'Eisenhower Dollar',
    'ike dollar': 'Eisenhower Dollar',
    'eisenhower': 'Eisenhower Dollar',
    'morgan': 'Morgan Silver Dollar',
    'morgan dollar': 'Morgan Silver Dollar',
    'peace': 'Peace Dollar',
    'peace dollar': 'Peace Dollar',
    'sba': 'Susan B. Anthony Dollar',
    'sba dollar': 'Susan B. Anthony Dollar',
    'susan b anthony': 'Susan B. Anthony Dollar',
    'sacagawea': 'Sacagawea Dollar',
    'golden dollar': 'Sacagawea Dollar',
    'trade dollar': 'Trade Dollar',
    'trade': 'Trade Dollar',
    'flowing hair': 'Flowing Hair Dollar',
    'draped bust': 'Draped Bust Dollar',
    'gobrecht': 'Gobrecht Dollar',
    # Half Dollars
    'walker': 'Walking Liberty Half Dollar',
    'walking liberty': 'Walking Liberty Half Dollar',
    'franklin': 'Franklin Half Dollar',
    'franklin half': 'Franklin Half Dollar',
    'kennedy': 'Kennedy Half Dollar',
    'kennedy half': 'Kennedy Half Dollar',
    'jfk': 'Kennedy Half Dollar',
    'barber half': 'Barber Half Dollar',
    'seated liberty half': 'Seated Liberty Half Dollar',
    # Quarters
    'barber quarter': 'Barber Quarter',
    'seated liberty quarter': 'Seated Liberty Quarter',
    'standing liberty': 'Standing Liberty Quarter',
    'washington quarter': 'Washington Quarter',
    # Dimes
    'merc': 'Mercury Dime',
    'mercury': 'Mercury Dime',
    'mercury dime': 'Mercury Dime',
    'winged liberty': 'Mercury Dime',
    'barber dime': 'Barber Dime',
    'seated liberty dime': 'Seated Liberty Dime',
    'rosie': 'Roosevelt Dime',
    'roosevelt dime': 'Roosevelt Dime',
    'roosevelt': 'Roosevelt Dime',
    # Nickels
    'buffalo nickel': 'Buffalo Nickel',
    'indian nickel': 'Buffalo Nickel',
    'war nickel': 'Jefferson Wartime Nickel',
    'wartime nickel': 'Jefferson Wartime Nickel',
    'v nickel': 'Liberty V Nickel',
    'v-nickel': 'Liberty V Nickel',
    'liberty nickel': 'Liberty V Nickel',
    'shield nickel': 'Shield Nickel',
    'jefferson nickel': 'Jefferson Nickel',
    # Cents
    'wheat penny': 'Lincoln Wheat Cent',
    'wheat cent': 'Lincoln Wheat Cent',
    'wheatie': 'Lincoln Wheat Cent',
    'wheats': 'Lincoln Wheat Cent',
    'indian cent': 'Indian Head Cent',
    'indian penny': 'Indian Head Cent',
    'flying eagle': 'Flying Eagle Cent',
    'large cent': 'Large Cent',
    'half cent': 'Half Cent',
    'steel penny': 'Lincoln Steel Cent',
    'steelie': 'Lincoln Steel Cent',
    'memorial cent': 'Lincoln Memorial Cent',
    'bicentennial cent': 'Lincoln Bicentennial Cent',
    # Gold
    'ase': 'American Eagle Silver Dollar',
    'silver eagle': 'American Eagle Silver Dollar',
    'american silver eagle': 'American Eagle Silver Dollar',
    'age': 'American Eagle Gold Coin',
    'gold eagle': 'American Eagle Gold Coin',
    'american gold eagle': 'American Eagle Gold Coin',
    'st. gaudens': 'Saint-Gaudens Double Eagle',
    'saint gaudens': 'Saint-Gaudens Double Eagle',
    'st gaudens': 'Saint-Gaudens Double Eagle',
    'double eagle': 'Saint-Gaudens Double Eagle',
    'gold buffalo': 'Gold Buffalo',
    'buffalo gold': 'Gold Buffalo',
    'platinum eagle': 'Platinum Eagle',
    'palladium eagle': 'Palladium Eagle',
    'liberty gold': 'Liberty Head Gold',
    'indian head gold': 'Indian Head Gold',
    # Misc
    'commem': 'Commemorative',
    'commemorative': 'Commemorative',
    'proof set': 'Proof Set',
    'mint set': 'Uncirculated Mint Set',
}

# Mint place-names / abbreviations → mint mark code
MINT_NAMES: dict[str, str] = {
    'philadelphia': 'P',
    'philly': 'P',
    'no mint': 'P',
    'no mint mark': 'P',
    'no mark': 'P',
    'p': 'P',
    'denver': 'D',
    'd': 'D',
    'san francisco': 'S',
    'sf': 'S',
    's': 'S',
    'west point': 'W',
    'w': 'W',
    'new orleans': 'O',
    'no': 'O',
    'o': 'O',
    'carson city': 'CC',
    'cc': 'CC',
    'charlotte': 'C',
    'dahlonega': 'D',
    'manila': 'M',
    'm': 'M',
}

# Condition / grade strings → standard numismatic grade
CONDITION_MAP: dict[str, str] = {
    # Uncirculated / Mint State — numeric
    'ms60': 'MS-60', 'ms-60': 'MS-60',
    'ms61': 'MS-61', 'ms-61': 'MS-61',
    'ms62': 'MS-62', 'ms-62': 'MS-62',
    'ms63': 'MS-63', 'ms-63': 'MS-63',
    'ms64': 'MS-64', 'ms-64': 'MS-64',
    'ms65': 'MS-65', 'ms-65': 'MS-65',
    'ms66': 'MS-66', 'ms-66': 'MS-66',
    'ms67': 'MS-67', 'ms-67': 'MS-67',
    'ms68': 'MS-68', 'ms-68': 'MS-68',
    'ms69': 'MS-69', 'ms-69': 'MS-69',
    'ms70': 'MS-70', 'ms-70': 'MS-70',
    # Uncirculated — descriptive
    'bu': 'Uncirculated',
    'brilliant uncirculated': 'Uncirculated',
    'brilliant unc': 'Uncirculated',
    'unc': 'Uncirculated',
    'uncirculated': 'Uncirculated',
    'mint state': 'Mint State',
    'ms': 'Mint State',
    'gem bu': 'MS-65',
    'gem brilliant uncirculated': 'MS-65',
    'gem unc': 'MS-65',
    'ch bu': 'MS-63',
    'choice bu': 'MS-63',
    'choice brilliant uncirculated': 'MS-63',
    # Proof — numeric
    'proof60': 'Proof-60', 'proof-60': 'Proof-60', 'pr60': 'Proof-60', 'pf60': 'Proof-60',
    'proof61': 'Proof-61', 'proof-61': 'Proof-61', 'pr61': 'Proof-61', 'pf61': 'Proof-61',
    'proof62': 'Proof-62', 'proof-62': 'Proof-62', 'pr62': 'Proof-62', 'pf62': 'Proof-62',
    'proof63': 'Proof-63', 'proof-63': 'Proof-63', 'pr63': 'Proof-63', 'pf63': 'Proof-63',
    'proof64': 'Proof-64', 'proof-64': 'Proof-64', 'pr64': 'Proof-64', 'pf64': 'Proof-64',
    'proof65': 'Proof-65', 'proof-65': 'Proof-65', 'pr65': 'Proof-65', 'pf65': 'Proof-65',
    'proof66': 'Proof-66', 'proof-66': 'Proof-66', 'pr66': 'Proof-66', 'pf66': 'Proof-66',
    'proof67': 'Proof-67', 'proof-67': 'Proof-67', 'pr67': 'Proof-67', 'pf67': 'Proof-67',
    'proof68': 'Proof-68', 'proof-68': 'Proof-68', 'pr68': 'Proof-68', 'pf68': 'Proof-68',
    'proof69': 'Proof-69', 'proof-69': 'Proof-69', 'pr69': 'Proof-69', 'pf69': 'Proof-69',
    'proof70': 'Proof-70', 'proof-70': 'Proof-70', 'pr70': 'Proof-70', 'pf70': 'Proof-70',
    # Proof — descriptive
    'proof': 'Proof',
    'gem proof': 'Proof-65',
    'gem pf': 'Proof-65',
    'ch proof': 'Proof-63',
    'choice proof': 'Proof-63',
    'ch proof 63': 'Proof-63',
    'ch pf63': 'Proof-63',
    'ch pr63': 'Proof-63',
    'proof 63 cameo': 'Proof-63 Cameo',
    'proof 65 cameo': 'Proof-65 Cameo',
    'proof 65 dcam': 'Proof-65 Deep Cameo',
    'pf63 cam': 'Proof-63 Cameo',
    'pf65 cam': 'Proof-65 Cameo',
    'pf65 dcam': 'Proof-65 Deep Cameo',
    'pr63 cam': 'Proof-63 Cameo',
    'pr65 cam': 'Proof-65 Cameo',
    'pr65 dcam': 'Proof-65 Deep Cameo',
    'dcam': 'Deep Cameo',
    'deep cameo': 'Deep Cameo',
    'cameo': 'Cameo',
    'cam': 'Cameo',
    # About Uncirculated
    'au50': 'AU-50', 'au-50': 'AU-50',
    'au55': 'AU-55', 'au-55': 'AU-55',
    'au58': 'AU-58', 'au-58': 'AU-58',
    'au': 'About Uncirculated',
    'slider': 'AU-58',
    'almost uncirculated': 'About Uncirculated',
    'about uncirculated': 'About Uncirculated',
    # Extremely Fine
    'ef': 'Extremely Fine',
    'xf': 'Extremely Fine',
    'ef40': 'EF-40', 'ef-40': 'EF-40', 'xf40': 'EF-40', 'xf-40': 'EF-40',
    'ef45': 'EF-45', 'ef-45': 'EF-45', 'xf45': 'EF-45', 'xf-45': 'EF-45',
    'extremely fine': 'Extremely Fine',
    'extra fine': 'Extremely Fine',
    # Very Fine
    'vf': 'Very Fine',
    'vf20': 'VF-20', 'vf-20': 'VF-20',
    'vf25': 'VF-25', 'vf-25': 'VF-25',
    'vf30': 'VF-30', 'vf-30': 'VF-30',
    'vf35': 'VF-35', 'vf-35': 'VF-35',
    'very fine': 'Very Fine',
    # Fine
    'f': 'Fine',
    'f12': 'F-12', 'f-12': 'F-12',
    'f15': 'F-15', 'f-15': 'F-15',
    'fine': 'Fine',
    # Very Good
    'vg': 'Very Good',
    'vg8': 'VG-8', 'vg-8': 'VG-8',
    'vg10': 'VG-10', 'vg-10': 'VG-10',
    'very good': 'Very Good',
    # Good
    'g': 'Good',
    'g4': 'G-4', 'g-4': 'G-4',
    'g6': 'G-6', 'g-6': 'G-6',
    'good': 'Good',
    # About Good / Poor / Fair
    'ag': 'About Good',
    'ag3': 'AG-3', 'ag-3': 'AG-3',
    'about good': 'About Good',
    'poor': 'Poor',
    'fair': 'Fair',
    'fr2': 'FR-2', 'fr-2': 'FR-2',
    # Circulated / Ungraded
    'circulated': 'Circulated',
    'circ': 'Circulated',
    'ungraded': 'Ungraded',
    'n/a': 'Ungraded',
    'na': 'Ungraded',
    '': 'Ungraded',
}


def _parse_year_mint(raw: str) -> tuple[str, str]:
    """
    Parse a combined or standalone year+mint string into (year, mint_mark).
    Handles: '2007W', '2007 w', '2007-W', '2007/W', '1943-S', '2007', 'West Point'.
    Returns ('', '') if nothing is recognized.
    """
    raw = str(raw).strip()
    if not raw or raw.lower() in ('nan', 'none', ''):
        return ('', '')

    # Pattern: 4-digit year optionally followed by a mint letter/pair
    m = re.match(r'^(\d{4})\s*[-/]?\s*([a-zA-Z]{1,2})$', raw)
    if m:
        year = m.group(1)
        mint = m.group(2).upper()
        if mint in ('P', 'D', 'S', 'W', 'O', 'C', 'M'):
            return (year, mint)
        if mint == 'CC':
            return (year, 'CC')
        if mint in ('NO',):
            return (year, 'O')
        # Unrecognised suffix — keep year, discard suffix
        return (year, '')

    # Pure 4-digit year
    if re.match(r'^\d{4}$', raw):
        return (raw, '')

    # 2-digit year — ambiguous, pass through as-is
    if re.match(r'^\d{2}$', raw):
        return (raw, '')

    # Named mint
    key = raw.lower().strip()
    for name, code in MINT_NAMES.items():
        if key == name:
            return ('', code)

    # Nothing matched
    return (raw, '')


def _norm_condition(raw: str) -> str:
    """
    Normalize a colloquial or abbreviated condition/grade string to the
    standard Numista.AI grade format.  Falls back to title-cased original
    if not in the lookup table (preserves user data rather than guessing).
    """
    if not raw or str(raw).strip().lower() in ('nan', 'none', ''):
        return 'Ungraded'
    cleaned = re.sub(r'\s+', ' ', str(raw).strip().lower())
    if cleaned in CONDITION_MAP:
        return CONDITION_MAP[cleaned]
    # Try without spaces
    if cleaned.replace(' ', '') in CONDITION_MAP:
        return CONDITION_MAP[cleaned.replace(' ', '')]
    # Try without hyphens
    if cleaned.replace('-', '') in CONDITION_MAP:
        return CONDITION_MAP[cleaned.replace('-', '')]
    # Preserve user value unchanged (title-cased)
    return str(raw).strip()


import time as _time

# ── Community nickname cache (refreshed every 60 s) ───────────────────────────
_community_cache: dict[str, str] = {}
_community_cache_ts: float = 0.0

def _community_nicknames() -> dict[str, str]:
    """Returns approved community nicknames merged with the hardcoded dict."""
    global _community_cache, _community_cache_ts
    if _time.time() - _community_cache_ts > 60:
        try:
            docs = db.collection('coin_nickname_suggestions') \
                     .where('status', '==', 'approved').stream()
            _community_cache = {
                d.to_dict()['nickname'].strip().lower(): d.to_dict()['maps_to']
                for d in docs
            }
        except Exception as e:
            print(f"[community_cache] refresh error: {e}")
        _community_cache_ts = _time.time()
    return {**COIN_NICKNAMES, **_community_cache}


def _expand_series(text: str) -> str:
    """
    Expand a colloquial coin name to the official Program/Series name.
    Checks hardcoded dict + live community-approved terms.
    Case-insensitive. Returns original text if no match found.
    """
    if not text:
        return text
    key = str(text).strip().lower()
    return _community_nicknames().get(key, text)



class CommitReviewsRequest(BaseModel):
    user_email: str
    review_ids: list[str]

class BulkUpdateRequest(BaseModel):
    user_email: str
    review_ids: list[str]
    updates: dict

@app.get("/")
def read_root():
    return {"status": "ok", "service": "Numista.AI Backend"}

@app.get("/api/spot_prices")
def get_live_metal_prices():
    try:
        gold = yf.Ticker("GC=F").fast_info.last_price
        silver = yf.Ticker("SI=F").fast_info.last_price
        plat = yf.Ticker("PL=F").fast_info.last_price
        pall = yf.Ticker("PA=F").fast_info.last_price
        return {
            "Gold": float(gold) if gold else 3100.0,
            "Silver": float(silver) if silver else 35.0,
            "Platinum": float(plat) if plat else 1000.0,
            "Palladium": float(pall) if pall else 1000.0
        }
    except Exception as e:
        print(f"Error fetching metals: {e}")
        return {"Gold": 3100.0, "Silver": 35.0, "Platinum": 1000.0, "Palladium": 1000.0}


# ─── WORLD ITEM IDENTIFICATION ────────────────────────────────────────────────
# New endpoint: POST /api/identify-world-item
#
# Two-stage pipeline:
#   1. Gemini Vision analyses the uploaded image (or text hints) and returns a
#      structured JSON identification with a 0–1 confidence score.
#   2. If confidence ≥ 0.90, we query the Numista API v3 text search for up to
#      3 catalogue matches.  Below 0.90 we skip the API call and return the
#      Gemini-only result with show_disclaimer = True.
#
# The Numista API key is the same one already used in scripts/fetch_numista_coins.py.
# Text search is FREE — no per-request charges.

NUMISTA_API_KEY    = "ExpST6TaGRDXkcEt6QajYJ0Lj76JZ8oqBPPpWhe"
NUMISTA_SEARCH_URL = "https://api.numista.com/v3/types"

# Confidence threshold below which we show the AI-estimate disclaimer
_WORLD_CONFIDENCE_THRESHOLD = 0.90

_WORLD_ITEM_PROMPT = """You are an expert numismatist and world-currency specialist.
Examine the provided image carefully. Identify what this appears to be.

Your response MUST be valid JSON only — no markdown, no commentary outside the JSON.
Return exactly these fields:

{
  "identification": "<one complete natural-language sentence starting with 'This appears to be'>",
  "item_type": "<one of: coin | banknote | bullion | medal | token | collectible | ancient_coin | unknown>",
  "country": "<best-guess issuing country in English, or 'Unknown'>",
  "era": "<year, decade, or period — e.g. '1921', '1860s', 'Roman Imperial c.250 AD', or 'Unknown'>",
  "denomination": "<denomination text as it appears on the item, or null>",
  "material": "<dominant metal or material — e.g. 'Silver', 'Gold', 'Bronze', 'Paper', or null>",
  "design_keywords": ["<2–4 short keyword phrases describing key design elements for catalogue search>"],
  "confidence": <float 0.0–1.0 — your confidence in the above identification>,
  "confidence_notes": "<brief plain-English reason if confidence < 0.90, otherwise null>"
}

Rules:
- Start 'identification' with the phrase 'This appears to be'.
- 'confidence' must be a raw float, not a string.
- If only text hints are provided (no image), base confidence on how specific those hints are.
- Be conservative: prefer lower confidence over false precision.
"""

_WORLD_TEXT_ONLY_PROMPT = """You are an expert numismatist and world-currency specialist.
The collector has provided the following hints (no image available):
Country: {country}
Year / Era: {year}
Item type: {item_type}
Additional notes: {notes}

Your response MUST be valid JSON only — no markdown, no commentary outside the JSON.
Return exactly these fields:

{{
  "identification": "<one complete natural-language sentence starting with 'This appears to be'>",
  "item_type": "<one of: coin | banknote | bullion | medal | token | collectible | ancient_coin | unknown>",
  "country": "<best-guess issuing country in English, or 'Unknown'>",
  "era": "<year, decade, or period, or 'Unknown'>",
  "denomination": "<denomination text or null>",
  "material": "<dominant metal or material, or null>",
  "design_keywords": ["<2–4 keyword phrases for catalogue search>"],
  "confidence": <float 0.0–1.0>,
  "confidence_notes": "<brief reason if confidence < 0.90, otherwise null>"
}}

Rules:
- Start 'identification' with the phrase 'This appears to be'.
- Confidence should reflect how specific and certain the provided hints are.
- Text-only identifications should generally score ≤ 0.75 unless highly specific.
"""


def _numista_search(gemini: dict) -> list:
    """
    Query Numista API v3 text search based on Gemini extraction.
    Returns up to 3 catalogue matches (list of dicts), or [] on error.
    """
    try:
        # Build a search string from the most informative Gemini fields
        parts = []
        if gemini.get("denomination"):
            parts.append(gemini["denomination"])
        if gemini.get("era") and gemini["era"] != "Unknown":
            parts.append(gemini["era"].split(" ")[0])  # first token (e.g. "1921")
        if gemini.get("design_keywords"):
            parts.extend(gemini["design_keywords"][:2])

        query = " ".join(parts).strip() or gemini.get("country", "")

        params = {
            "q":     query[:200],   # API max query length
            "count": 5,
            "lang":  "en",
        }
        if gemini.get("country") and gemini["country"] != "Unknown":
            # Numista uses lowercase ISO-like issuer codes; sending the country
            # name as a supplemental hint (it falls back to text search).
            params["issuer"] = gemini["country"]

        resp = __import__("requests").get(
            NUMISTA_SEARCH_URL,
            headers={"Numista-API-Key": NUMISTA_API_KEY, "Accept": "application/json"},
            params=params,
            timeout=10,
        )
        if resp.status_code != 200:
            print(f"[world_item] Numista API {resp.status_code}: {resp.text[:200]}")
            return []

        types = resp.json().get("types", [])[:3]
        results = []
        for t in types:
            results.append({
                "numista_id":      t.get("id"),
                "title":           t.get("title"),
                "issuer":          t.get("issuer", {}).get("name") if isinstance(t.get("issuer"), dict) else t.get("issuer"),
                "min_year":        t.get("min_year"),
                "max_year":        t.get("max_year"),
                "composition":     t.get("composition", {}).get("text") if isinstance(t.get("composition"), dict) else t.get("composition"),
                "image_obverse":   t.get("obverse_thumbnail") or t.get("obverse_picture"),
                "catalogue_url":   f"https://en.numista.com/catalogue/pieces/{t.get('id')}",
            })
        return results

    except Exception as e:
        print(f"[world_item] Numista search error: {e}")
        return []


@app.post("/api/identify-world-item")
async def identify_world_item(
    image:             Optional[UploadFile] = File(None),
    country_hint:      str = Form(''),
    year_hint:         str = Form(''),
    item_type_hint:    str = Form('unknown'),
    notes_hint:        str = Form(''),
):
    """
    Identify a foreign coin, world currency, bullion, ancient coin, or specialty
    collectible using Gemini Vision + Numista catalogue lookup.

    Pipeline:
      1. If an image is provided  → call Gemini Vision with world-item prompt.
      2. If no image              → call Gemini text model with hint-only prompt.
      3. If Gemini confidence ≥ 0.90 → search Numista catalogue for matches.
      4. Return combined result.

    Response shape:
    {
      "gemini": {
        "identification": "This appears to be…",
        "item_type": "coin",
        "country": "Germany",
        "era": "1921",
        "denomination": "3 Mark",
        "material": "Silver",
        "design_keywords": ["Weimar eagle", "oak wreath"],
        "confidence": 0.94,
        "confidence_notes": null
      },
      "numista_matches": [ { numista_id, title, issuer, min_year, max_year, composition, image_obverse, catalogue_url }, … ],
      "show_disclaimer": false,
      "disclaimer_reason": null
    }
    """
    # ── Stage 1: Gemini identification ────────────────────────────────────────
    gemini_result: dict = {}
    try:
        if image is not None:
            # Image path — use Gemini Vision
            img_bytes = await image.read()
            img_b64   = base64.b64encode(img_bytes).decode()

            # Determine MIME type from filename / content sniff
            fname = (image.filename or "").lower()
            if fname.endswith(".png"):
                mime = "image/png"
            elif fname.endswith(".gif"):
                mime = "image/gif"
            elif fname.endswith(".webp"):
                mime = "image/webp"
            else:
                mime = "image/jpeg"

            response = genai_client.models.generate_content(
                model=PRIMARY_MODEL,
                contents=[
                    genai_types.Part.from_bytes(data=img_bytes, mime_type=mime),
                    genai_types.Part.from_text(_WORLD_ITEM_PROMPT),
                ],
                config=genai_types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=800,
                ),
            )
        else:
            # Text-only path — hints only
            filled_prompt = _WORLD_TEXT_ONLY_PROMPT.format(
                country=country_hint   or "Unknown",
                year=year_hint         or "Unknown",
                item_type=item_type_hint or "unknown",
                notes=notes_hint       or "None provided",
            )
            response = genai_client.models.generate_content(
                model=PRIMARY_MODEL,
                contents=[genai_types.Part.from_text(filled_prompt)],
                config=genai_types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=600,
                ),
            )

        raw_text = response.text.strip()
        # Strip markdown code fences if model wraps in ```json … ```
        if raw_text.startswith("```"):
            raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.MULTILINE)
            raw_text = re.sub(r"\s*```$",          "", raw_text, flags=re.MULTILINE)

        gemini_result = json.loads(raw_text)

        # Normalise confidence to float in [0, 1]
        conf = gemini_result.get("confidence", 0.5)
        if isinstance(conf, str):
            conf = float(conf.replace("%", "")) / (100 if "%" in conf else 1)
        gemini_result["confidence"] = max(0.0, min(1.0, float(conf)))

        # Always ensure identification starts correctly
        ident = gemini_result.get("identification", "")
        if ident and not ident.startswith("This appears to be"):
            gemini_result["identification"] = "This appears to be " + ident

    except json.JSONDecodeError as e:
        # Gemini returned non-JSON — wrap the raw text gracefully
        print(f"[world_item] Gemini JSON parse error: {e}. Raw: {raw_text[:300]}")
        gemini_result = {
            "identification":   "This appears to be an unidentified numismatic item.",
            "item_type":        "unknown",
            "country":          "Unknown",
            "era":              "Unknown",
            "denomination":     None,
            "material":         None,
            "design_keywords":  [],
            "confidence":       0.30,
            "confidence_notes": "AI returned an unstructured response. Please fill in details manually.",
        }
    except Exception as e:
        print(f"[world_item] Gemini call error: {e}")
        raise HTTPException(status_code=500, detail=f"AI identification failed: {str(e)}")

    # ── Stage 2: Numista lookup (only when confidence is high enough) ─────────
    numista_matches = []
    if gemini_result.get("confidence", 0) >= _WORLD_CONFIDENCE_THRESHOLD:
        numista_matches = _numista_search(gemini_result)

    # ── Stage 3: Build response ───────────────────────────────────────────────
    show_disclaimer   = gemini_result.get("confidence", 0) < _WORLD_CONFIDENCE_THRESHOLD
    disclaimer_reason = gemini_result.get("confidence_notes") if show_disclaimer else None

    return {
        "gemini":          gemini_result,
        "numista_matches": numista_matches,
        "show_disclaimer": show_disclaimer,
        "disclaimer_reason": disclaimer_reason,
    }


# ─── END WORLD ITEM IDENTIFICATION ───────────────────────────────────────────

@app.post("/api/import_spreadsheet")
async def import_spreadsheet(
    user_email:        str = Form(...),
    file:              UploadFile = File(...),
    import_name:       str = Form(''),   # optional label e.g. "Aunt's Access DB - Jan 2026"
    import_session_id: str = Form(''),   # set by Bulk Import flow; links coins to a session
):
    """
    Ingests an Excel/CSV file into the user's review_queue.

    Pipeline:
      1. AI maps column NAMES to the Golden Schema (one call, fast).
      2. Per-row rule-based normalization:
           - Year column: split combined "2007W" → Year + Mint Mark
           - Condition: expand abbreviations/colloquial grades
           - Program/Series: expand coin nicknames (Ike, Merc, Walker …)
      3. AI fallback: rows whose Condition or Series still look unresolved
         go through a lightweight AI interpretation pass (batched, 10 rows/call).
    """
    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents)) if str(file.filename).lower().endswith('.csv') \
             else pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}")

    # ── 1. AI column-name mapping ────────────────────────────────────────────
    headers = list(df.columns)
    nickname_hint = ', '.join(f'"{k}" → "{v}"' for k, v in list(COIN_NICKNAMES.items())[:20])
    mapping_prompt = f"""You are an expert data migration agent for a numismatic (coin collecting) application.

Golden Schema keys:
["Program/Series", "Theme/Subject", "Year", "Country", "Denomination",
 "Mint Mark", "Condition", "Cost", "Purchase Date", "Retailer Name",
 "Retailer Invoice #", "Retailer Item No.", "Storage Location", "Notes"]

User spreadsheet headers: {headers}

Map each user header to the closest schema key. Common abbreviations:
  Yr/Date → Year, Grade/Quality → Condition, Purchased For/Amount Paid/Price → Cost,
  Series/Type/Kind → Program/Series, Desc/Description/Subject → Theme/Subject,
  Mint/MM → Mint Mark, Qty → Quantity, Location → Storage Location.

Coin nickname reference (first 20): {nickname_hint}

Output ONLY a raw JSON object: {{"user_header": "schema_key", ...}}
Omit any user headers with no reasonable match."""

    try:
        resp = genai_client.models.generate_content(
            model=PRIMARY_MODEL,
            contents=[genai_types.Part.from_text(text=mapping_prompt)],
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        mapping: dict = json.loads(resp.text)
    except Exception as e:
        print(f"[import_spreadsheet] AI column-mapping error: {e}")
        mapping = {h: h for h in headers}   # 1-to-1 fallback

    # ── 2. Per-row ingestion + rule-based normalization ──────────────────────
    added_count = 0
    ai_fallback_needed: list[tuple] = []   # (doc_ref, partial_doc) for AI pass

    col_ref = db.collection('users').document(user_email).collection('review_queue')
    batch    = db.batch()

    for _, row in df.iterrows():
        new_doc: dict = {
            'Program/Series':   '',
            'Theme/Subject':    '',
            'Year':             '',
            'Mint Mark':        '',
            'Denomination':     '',
            'Condition':        'Ungraded',
            'Cost':             '',
            'Purchase Date':    '',
            'Country':          'United States',
            'Quantity':         1,
            'deep_dive_status': 'PENDING',
        }

        # Apply column mapping (raw values)
        for user_col, schema_col in mapping.items():
            if user_col in row and pd.notna(row[user_col]):
                new_doc[schema_col] = str(row[user_col]).strip()

        # ── Rule-based normalizations ──────────────────────────────────────

        # Year + Mint Mark: if Year field looks like "2007W", split it
        raw_year = new_doc.get('Year', '')
        yr, mm = _parse_year_mint(raw_year)
        new_doc['Year'] = yr
        # Only overwrite Mint Mark if it's empty (don't clobber explicit column)
        if mm and not new_doc.get('Mint Mark', '').strip():
            new_doc['Mint Mark'] = mm

        # Condition normalization
        raw_cond = new_doc.get('Condition', '')
        norm_cond = _norm_condition(raw_cond)
        new_doc['Condition'] = norm_cond
        cond_resolved = norm_cond != raw_cond or raw_cond.lower() in CONDITION_MAP

        # Program/Series nickname expansion
        raw_series = new_doc.get('Program/Series', '')
        expanded = _expand_series(raw_series)
        new_doc['Program/Series'] = expanded
        series_resolved = expanded != raw_series

        # Theme/Subject nickname expansion (handles "Ike" in the wrong column)
        raw_theme = new_doc.get('Theme/Subject', '')
        expanded_theme = _expand_series(raw_theme)
        new_doc['Theme/Subject'] = expanded_theme

        # Strip leading $ from Cost/Denomination
        for fld in ('Cost', 'Denomination'):
            if new_doc.get(fld, '').startswith('$'):
                new_doc[fld] = new_doc[fld][1:]

        # ── Source provenance ──────────────────────────────────────────────
        new_doc['upload_method']       = 'spreadsheet_import'
        new_doc['source_file']         = file.filename
        new_doc['import_name']         = import_name or file.filename
        new_doc['created_at']          = firestore.SERVER_TIMESTAMP
        if import_session_id:
            new_doc['import_session_id'] = import_session_id

        # Confidence: lower when AI fallback will be needed
        needs_ai = (not cond_resolved and raw_cond) or \
                   (not series_resolved and raw_series and not raw_series.strip().isdigit())
        new_doc['confidence_score'] = 0.75 if needs_ai else 0.95

        doc_ref = col_ref.document(str(uuid.uuid4()))
        batch.set(doc_ref, new_doc)
        added_count += 1

        if needs_ai:
            ai_fallback_needed.append((doc_ref.id, raw_series, raw_cond))

        if added_count % 490 == 0:
            batch.commit()
            batch = db.batch()

    if added_count % 490 != 0:
        batch.commit()

    # ── 3. AI fallback for unresolved rows (batched 10 at a time) ───────────
    ai_fixed = 0
    if ai_fallback_needed:
        for i in range(0, len(ai_fallback_needed), 10):
            chunk = ai_fallback_needed[i:i + 10]
            rows_text = '\n'.join(
                f'{j+1}. Series="{r[1]}" Condition="{r[2]}"'
                for j, r in enumerate(chunk)
            )
            fallback_prompt = f"""You are a US coin expert. For each row, provide the standardized
Program/Series and Condition. Use official numismatic terminology.

Rows:
{rows_text}

Output JSON array: [{{"series": "...", "condition": "..."}}]
Preserve order. Use empty string if truly unknown."""
            try:
                fb_resp = genai_client.models.generate_content(
                    model=PRIMARY_MODEL,
                    contents=[genai_types.Part.from_text(text=fallback_prompt)],
                    config=genai_types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                interpretations = json.loads(fb_resp.text)
                fb_batch = db.batch()
                for (doc_id, _, _), interp in zip(chunk, interpretations):
                    updates: dict = {'confidence_score': 0.88}
                    if interp.get('series'):
                        updates['Program/Series'] = interp['series']
                    if interp.get('condition'):
                        updates['Condition'] = interp['condition']
                    fb_batch.update(col_ref.document(doc_id), updates)
                    ai_fixed += 1
                fb_batch.commit()
            except Exception as e:
                print(f"[import_spreadsheet] AI fallback error (chunk {i}): {e}")

    return {
        "status":        "success",
        "count":         added_count,
        "ai_fallback":   ai_fixed,
        "mapping_used":  mapping,
        "extracted_items": added_count,   # alias for Flutter progress display
    }


@app.get("/api/template")
def download_template():
    """Returns a pre-formatted CSV template with the Numista.AI Golden Schema headers."""
    from fastapi.responses import Response
    headers_row = (
        "Year,Mint Mark,Denomination,Program/Series,Theme/Subject,Country,"
        "Condition,Strike Type,Holder Type,Grading Service,Certification Number,"
        "Metal Content,Purchase Cost,Purchase Date,Retailer/Website,"
        "Retailer Invoice #,Retailer Item No.,Variety,Personal Notes I,"
        "Personal Reference #,Storage Location,Original Description from source\n"
    )
    example_row = (
        '1921,D,Dollar,Morgan Silver Dollar,Morgan Dollar,USA,'
        'VF-30,,Raw,,,Silver,42.00,1995-06-15,Local Coin Shop,,,'
        ',,Safe Deposit Box,Rim nick at 3 o\'clock\n'
    )
    csv_content = headers_row + example_row
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=numista_ai_template.csv"},
    )


@app.post("/api/normalize_backfill")
async def normalize_backfill(user_email: str = Form(...)):
    """
    One-time normalization pass over all existing coins for a user.

    Applies _parse_year_mint, _norm_condition, and _expand_series to every
    coin in the coins collection.  Only writes back when a field actually
    changes.  Returns a summary of changes made.
    """
    coins_ref = db.collection('users').document(user_email).collection('coins')
    docs      = list(coins_ref.stream())

    changed      = 0
    unchanged    = 0
    batch        = db.batch()
    batch_count  = 0
    changes_log: list[dict] = []

    for doc in docs:
        d       = doc.to_dict()
        updates = {}

        # ── Year + Mint Mark ─────────────────────────────────────────────
        raw_year = str(d.get('Year', '')).strip()
        yr, mm   = _parse_year_mint(raw_year)
        if yr != raw_year:
            updates['Year'] = yr
        existing_mm = str(d.get('Mint Mark', '')).strip()
        if mm and not existing_mm:
            updates['Mint Mark'] = mm

        # ── Condition ────────────────────────────────────────────────────
        raw_cond  = str(d.get('Condition', '')).strip()
        norm_cond = _norm_condition(raw_cond)
        if norm_cond != raw_cond:
            updates['Condition'] = norm_cond

        # ── Program/Series ───────────────────────────────────────────────
        raw_series  = str(d.get('Program/Series', '')).strip()
        exp_series  = _expand_series(raw_series)
        if exp_series != raw_series:
            updates['Program/Series'] = exp_series

        # ── Theme/Subject ────────────────────────────────────────────────
        raw_theme  = str(d.get('Theme/Subject', '')).strip()
        exp_theme  = _expand_series(raw_theme)
        if exp_theme != raw_theme:
            updates['Theme/Subject'] = exp_theme

        if updates:
            # Log BEFORE adding SERVER_TIMESTAMP — Sentinel isn't JSON-serializable
            log_entry = {k: str(v) for k, v in updates.items()}
            changes_log.append({'id': doc.id, 'changes': log_entry})

            updates['normalized_at'] = firestore.SERVER_TIMESTAMP
            # Use set(merge=True) instead of update() — update() treats '/'
            # as a Firestore field-path separator, breaking 'Theme/Subject' etc.
            batch.set(coins_ref.document(doc.id), updates, merge=True)
            batch_count += 1
            changed += 1
            if batch_count >= 490:
                batch.commit()
                batch = db.batch()
                batch_count = 0
        else:
            unchanged += 1

    if batch_count > 0:
        batch.commit()

    print(f"[normalize_backfill] {user_email}: {changed} updated, {unchanged} unchanged")
    return {
        "status":    "success",
        "changed":   changed,
        "unchanged": unchanged,
        "changes":   changes_log[:50],   # return first 50 for preview
    }


# ════════════════════════════════════════════════════════════════════════════
#  Community Coin Nickname System
# ════════════════════════════════════════════════════════════════════════════

NICKNAME_COLLECTION = 'coin_nickname_suggestions'

NICKNAME_CATEGORIES = [
    'Cent', 'Nickel', 'Dime', 'Quarter',
    'Half Dollar', 'Dollar', 'Gold', 'Silver', 'Other'
]


@app.post("/api/nicknames/submit")
async def submit_nickname(
    user_email: str  = Form(...),
    nickname:   str  = Form(...),
    maps_to:    str  = Form(...),
    category:   str  = Form('Other'),
    example:    str  = Form(''),
    notes:      str  = Form(''),
):
    """Submit a new coin nickname/slang term for community review."""
    nickname_clean = nickname.strip()
    maps_to_clean  = maps_to.strip()
    key = nickname_clean.lower()

    # ── Check hardcoded dictionary first ────────────────────────────────────
    if key in COIN_NICKNAMES:
        official = COIN_NICKNAMES[key]
        return {
            "status":  "already_known",
            "message": f'✨ Great minds think alike! "{nickname_clean}" is already in the '
                       f'Numista.AI dictionary — it maps to "{official}". '
                       f'No need to submit it again.',
            "maps_to": official,
        }

    # ── Check existing community submissions ─────────────────────────────────
    existing = db.collection(NICKNAME_COLLECTION) \
                 .where('nickname_lower', '==', key) \
                 .limit(1).stream()
    existing_list = list(existing)
    if existing_list:
        doc = existing_list[0].to_dict()
        status = doc.get('status', 'pending')
        if status == 'approved':
            return {
                "status":  "already_known",
                "message": f'"{nickname_clean}" was already submitted by the community '
                           f'and approved — it maps to "{doc.get("maps_to", "")}"! '
                           f'Head to the Approved Dictionary tab to see it.',
                "maps_to": doc.get('maps_to', ''),
            }
        elif status == 'pending':
            return {
                "status":  "already_pending",
                "message": f'"{nickname_clean}" is already in community review — '
                           f'go vote on it in the Community Review tab!',
                "doc_id":  existing_list[0].id,
            }
        # Rejected — allow resubmission

    # ── Create new submission ────────────────────────────────────────────────
    doc_ref = db.collection(NICKNAME_COLLECTION).document()
    doc_ref.set({
        'nickname':       nickname_clean,
        'nickname_lower': key,
        'maps_to':        maps_to_clean,
        'category':       category if category in NICKNAME_CATEGORIES else 'Other',
        'example':        example.strip(),
        'notes':          notes.strip(),
        'submitted_by':   user_email,
        'submitted_at':   firestore.SERVER_TIMESTAMP,
        'status':         'pending',
        'ratings':        {},        # { email: 1-5 }
        'avg_rating':     0.0,
        'vote_count':     0,
        'in_ai_dict':     False,
    })
    return {
        "status":  "submitted",
        "doc_id":  doc_ref.id,
        "message": f'🎉 "{nickname_clean}" is now in community review! '
                   f'Share it with other collectors to get votes.',
    }


@app.get("/api/nicknames")
def list_nicknames(status: str = 'pending', limit: int = 50, offset: int = 0):
    """List community nickname submissions, filterable by status."""
    valid_statuses = ('pending', 'approved', 'rejected', 'all')
    if status not in valid_statuses:
        status = 'pending'

    col = db.collection(NICKNAME_COLLECTION)
    if status != 'all':
        col = col.where('status', '==', status)

    # order_by + where requires a composite index that may not exist yet.
    # Gracefully fall back to unordered if the index is missing.
    try:
        docs = list(
            col.order_by('submitted_at', direction=firestore.Query.DESCENDING)
               .limit(limit + offset).stream()
        )
    except Exception:
        try:
            docs = list(col.limit(limit + offset).stream())
        except Exception:
            docs = []
    docs = docs[offset:]

    results = []
    for doc in docs:
        d = doc.to_dict()
        results.append({
            'id':           doc.id,
            'nickname':     d.get('nickname', ''),
            'maps_to':      d.get('maps_to', ''),
            'category':     d.get('category', 'Other'),
            'example':      d.get('example', ''),
            'notes':        d.get('notes', ''),
            'submitted_by': d.get('submitted_by', ''),
            'status':       d.get('status', 'pending'),
            'avg_rating':   round(d.get('avg_rating', 0.0), 1),
            'vote_count':   d.get('vote_count', 0),
            'in_ai_dict':   d.get('in_ai_dict', False),
            'is_builtin':   False,
        })

    # When requesting approved — also include a sample of built-ins for context
    if status == 'approved':
        builtin_sample = [
            {'id': f'builtin_{k}', 'nickname': k.title(), 'maps_to': v,
             'category': 'Built-In', 'example': '', 'notes': '',
             'submitted_by': 'Numista.AI', 'status': 'approved',
             'avg_rating': 5.0, 'vote_count': 0, 'in_ai_dict': True, 'is_builtin': True}
            for k, v in list(COIN_NICKNAMES.items())[:20]
        ]
        results = builtin_sample + results

    return {"status": "ok", "results": results, "count": len(results)}


@app.post("/api/nicknames/{doc_id}/vote")
async def vote_nickname(
    doc_id:     str,
    user_email: str = Form(...),
    rating:     int = Form(...),
):
    """Cast or update a star rating (1–5) on a community nickname submission."""
    if not 1 <= rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5.")

    doc_ref = db.collection(NICKNAME_COLLECTION).document(doc_id)
    doc     = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Nickname not found.")

    d = doc.to_dict()

    # Block self-voting
    if d.get('submitted_by') == user_email:
        raise HTTPException(status_code=403,
                            detail="You cannot vote on your own submission.")
    if d.get('status') not in ('pending',):
        raise HTTPException(status_code=400,
                            detail="You can only vote on pending submissions.")

    # Update ratings map
    ratings: dict = d.get('ratings', {})
    ratings[user_email] = rating

    # Recalculate stats
    vote_count = len(ratings)
    avg_rating = sum(ratings.values()) / vote_count

    # Determine new status
    new_status  = d.get('status', 'pending')
    in_ai_dict  = d.get('in_ai_dict', False)
    status_msg  = 'Vote recorded.'

    if avg_rating >= 4.0 and vote_count >= 3:
        new_status = 'approved'
        in_ai_dict = True
        _community_cache_ts_reset()   # bust cache immediately
        status_msg = f'🎉 AUTO-APPROVED! "{d["nickname"]}" is now in the AI dictionary!'
    elif avg_rating < 2.5 and vote_count >= 5:
        new_status = 'rejected'
        status_msg = f'"{d["nickname"]}" was rejected by community vote.'

    doc_ref.set({
        'ratings':    ratings,
        'avg_rating': round(avg_rating, 2),
        'vote_count': vote_count,
        'status':     new_status,
        'in_ai_dict': in_ai_dict,
    }, merge=True)

    return {
        "status":      "ok",
        "new_avg":     round(avg_rating, 1),
        "vote_count":  vote_count,
        "new_status":  new_status,
        "message":     status_msg,
        "your_rating": rating,
    }


def _community_cache_ts_reset():
    """Force immediate cache refresh on next _expand_series call."""
    global _community_cache_ts
    _community_cache_ts = 0.0


@app.get("/api/nicknames/stats")
def nickname_stats():
    """Community nickname submission statistics for the dashboard header."""
    all_docs = list(db.collection(NICKNAME_COLLECTION).stream())
    pending  = sum(1 for d in all_docs if d.to_dict().get('status') == 'pending')
    approved = sum(1 for d in all_docs if d.to_dict().get('status') == 'approved')
    rejected = sum(1 for d in all_docs if d.to_dict().get('status') == 'rejected')

    # Top contributor (most submissions)
    by_user: dict[str, int] = {}
    for d in all_docs:
        u = d.to_dict().get('submitted_by', '')
        if u:
            by_user[u] = by_user.get(u, 0) + 1
    top_user = max(by_user, key=by_user.get) if by_user else ''

    return {
        "total":    len(all_docs),
        "pending":  pending,
        "approved": approved,
        "rejected": rejected,
        "builtin":  len(COIN_NICKNAMES),
        "top_contributor": top_user.split('@')[0] if top_user else '—',
    }


# ════════════════════════════════════════════════════════════════════════════
#  AI Grade Review System
# ════════════════════════════════════════════════════════════════════════════

from datetime import datetime as _dt

# Sources that indicate an AI assigned the grade
AI_SOURCES = {'Binder Scan', 'PDF Invoice', 'Binder Checklist'}

# Confidence threshold below which a coin is "low confidence"
LOW_CONFIDENCE_THRESHOLD = 0.85


@app.get("/api/grade_review/queue")
def grade_review_queue(user_email: str, limit: int = 30):
    """
    Returns the user's own AI-graded coins that haven't been reviewed yet,
    sorted by confidence_score ascending (lowest = most urgently needs review).
    """
    coins_ref = db.collection('users').document(user_email).collection('coins')

    # ── Server-side filter: only pull AI-sourced coins (avoids full-collection scan) ──
    seen_ids: set[str] = set()
    raw_docs: list     = []
    try:
        q1 = coins_ref.where('source', 'in', list(AI_SOURCES)).stream()
        for doc in q1:
            if doc.id not in seen_ids:
                seen_ids.add(doc.id)
                raw_docs.append(doc)
    except Exception as e:
        print(f"[grade_review_queue] source query failed: {e}, falling back to full scan")
        raw_docs = list(coins_ref.stream())
        seen_ids = {d.id for d in raw_docs}

    # Also catch low-confidence coins from other sources (e.g. AI-fixed CSV rows)
    try:
        q2 = coins_ref.where('confidence_score', '<', 0.95).stream()
        for doc in q2:
            if doc.id not in seen_ids:
                seen_ids.add(doc.id)
                raw_docs.append(doc)
    except Exception:
        pass  # Index may not exist yet — source filter above handles main cases

    # Also catch manually flagged coins
    try:
        q3 = coins_ref.where('grade_review_status', '==', 'pending').stream()
        for doc in q3:
            if doc.id not in seen_ids:
                seen_ids.add(doc.id)
                raw_docs.append(doc)
    except Exception:
        pass

    results = []
    for doc in raw_docs:
        d      = doc.to_dict()
        source = d.get('source', '')
        conf   = float(d.get('confidence_score', 1.0))

        # Skip already reviewed by this user
        reviews = d.get('grade_reviews', [])
        if any(r.get('reviewer') == user_email for r in reviews):
            continue

        results.append({
            'coin_id':             doc.id,
            'year':                d.get('Year', ''),
            'mint_mark':           d.get('Mint Mark', ''),
            'denomination':        d.get('Denomination', ''),
            'program_series':      d.get('Program/Series', ''),
            'theme_subject':       d.get('Theme/Subject', ''),
            'condition':           d.get('Condition', 'Ungraded'),
            'ai_assigned_condition': d.get('ai_assigned_condition',
                                          d.get('Condition', 'Ungraded')),
            'confidence_score':    round(conf, 2),
            'low_confidence':      conf < LOW_CONFIDENCE_THRESHOLD,
            'source':              source,
            'image_url_obverse':   d.get('image_url_obverse', ''),
            'grade_review_status': d.get('grade_review_status', 'pending'),
            'grade_review_count':  d.get('grade_review_count', 0),
        })

    # Lowest confidence first
    results.sort(key=lambda x: x['confidence_score'])
    return {
        'status':  'ok',
        'results': results[:limit],
        'total':   len(results),
    }


@app.post("/api/grade_review/submit")
async def submit_grade_review(
    user_email:      str = Form(...),
    coin_id:         str = Form(...),
    action:          str = Form(...),    # 'confirmed' or 'corrected'
    suggested_grade: str = Form(''),
    rating:          int = Form(...),    # 1-5 AI accuracy stars
    notes:           str = Form(''),
):
    """
    Record a grade review on one of the user's own coins.
    No auto-correction — if 2/3+ of reviews disagree with the AI grade,
    the coin is flagged in admin_grade_flags for human review.
    """
    if not 1 <= rating <= 5:
        raise HTTPException(status_code=400,
                            detail="Rating must be between 1 and 5.")
    if action not in ('confirmed', 'corrected'):
        raise HTTPException(status_code=400,
                            detail="Action must be 'confirmed' or 'corrected'.")
    if action == 'corrected' and not suggested_grade.strip():
        raise HTTPException(status_code=400,
                            detail="suggested_grade is required when action=corrected.")

    coins_ref = db.collection('users').document(user_email).collection('coins')
    coin_ref  = coins_ref.document(coin_id)
    coin_doc  = coin_ref.get()
    if not coin_doc.exists:
        raise HTTPException(status_code=404, detail="Coin not found.")

    d = coin_doc.to_dict()

    # Prevent duplicate reviews
    reviews = list(d.get('grade_reviews', []))
    if any(r.get('reviewer') == user_email for r in reviews):
        raise HTTPException(status_code=400,
                            detail="You have already reviewed this coin.")

    # Snapshot original AI grade on first review
    ai_assigned = d.get('ai_assigned_condition') or d.get('Condition', 'Ungraded')

    # Append new review
    reviews.append({
        'reviewer':        user_email,
        'action':          action,
        'suggested_grade': suggested_grade.strip() if action == 'corrected' else '',
        'rating':          rating,
        'notes':           notes.strip(),
        'reviewed_at':     _dt.utcnow().isoformat(),
    })

    review_count  = len(reviews)
    corrections   = [r for r in reviews if r['action'] == 'corrected']
    confirmations = [r for r in reviews if r['action'] == 'confirmed']

    # Determine status
    new_status     = 'pending'
    grade_consensus = ''
    flagged        = False

    if review_count >= 3:
        correction_ratio = len(corrections) / review_count
        if correction_ratio >= 0.67:
            # Find most-suggested grade
            grade_counts: dict[str, int] = {}
            for r in corrections:
                g = r['suggested_grade']
                if g:
                    grade_counts[g] = grade_counts.get(g, 0) + 1
            if grade_counts:
                grade_consensus = max(grade_counts, key=grade_counts.get)
            new_status = 'flagged_for_admin_review'
            flagged    = True
        elif len(confirmations) / review_count >= 0.75:
            new_status = 'confirmed'

    update_payload: dict = {
        'grade_reviews':         reviews,
        'grade_review_count':    review_count,
        'grade_review_status':   new_status,
        'ai_assigned_condition': ai_assigned,
    }
    if grade_consensus:
        update_payload['grade_consensus'] = grade_consensus

    # Write admin flag if consensus disagrees with AI
    if flagged:
        db.collection('admin_grade_flags').document(coin_id).set({
            'user_email':        user_email,
            'coin_id':           coin_id,
            'ai_assigned_grade': ai_assigned,
            'community_grade':   grade_consensus,
            'review_count':      review_count,
            'flagged_at':        firestore.SERVER_TIMESTAMP,
            'resolved':          False,
            'year':              d.get('Year', ''),
            'mint_mark':         d.get('Mint Mark', ''),
            'program_series':    d.get('Program/Series', ''),
        }, merge=True)

    coin_ref.set(update_payload, merge=True)

    if action == 'confirmed':
        msg = '✓ Grade confirmed! Thank you for helping improve Numista.AI.'
    else:
        msg = f'Correction submitted — "{suggested_grade}" has been noted.'
        if flagged:
            msg += (' 🚩 Community consensus differs from the AI grade — '
                    'this coin has been flagged for admin review.')

    return {
        'status':       'ok',
        'message':      msg,
        'new_status':   new_status,
        'review_count': review_count,
        'flagged':      flagged,
    }


# ─── Admin: Grade Flag Dashboard ─────────────────────────────────────────────

@app.get("/api/admin/grade_flags")
def admin_grade_flags(resolved: bool = False, limit: int = 100):
    """
    Returns all coins flagged for admin grade review.
    resolved=false (default) → open flags only.
    resolved=true            → already-resolved flags.
    """
    try:
        q = (db.collection('admin_grade_flags')
               .where('resolved', '==', resolved)
               .order_by('flagged_at', direction=firestore.Query.DESCENDING)
               .limit(limit))
        docs = list(q.stream())
    except Exception:
        # Index may still be building — fall back to unordered
        docs = list(
            db.collection('admin_grade_flags')
              .where('resolved', '==', resolved)
              .limit(limit)
              .stream()
        )

    flags = []
    for doc in docs:
        d = doc.to_dict()
        # Fetch the coin's current image if available
        try:
            owner  = d.get('user_email', '')
            cid    = d.get('coin_id', doc.id)
            cdoc   = (db.collection('users').document(owner)
                        .collection('coins').document(cid).get())
            img    = cdoc.to_dict().get('image_url_obverse', '') if cdoc.exists else ''
            conf   = cdoc.to_dict().get('confidence_score', 0.0) if cdoc.exists else 0.0
            theme  = cdoc.to_dict().get('Theme/Subject', '') if cdoc.exists else ''
        except Exception:
            img = ''; conf = 0.0; theme = ''

        # Build review summary for display
        try:
            cdoc2  = (db.collection('users').document(d.get('user_email',''))
                        .collection('coins').document(doc.id).get())
            reviews = cdoc2.to_dict().get('grade_reviews', []) if cdoc2.exists else []
        except Exception:
            reviews = []

        grade_tally: dict = {}
        for rv in reviews:
            g = rv.get('suggested_grade', rv.get('action',''))
            if g and g != 'confirmed':
                grade_tally[g] = grade_tally.get(g, 0) + 1

        flags.append({
            'flag_id':         doc.id,
            'coin_id':         d.get('coin_id', doc.id),
            'user_email':      d.get('user_email', ''),
            'year':            d.get('year', ''),
            'mint_mark':       d.get('mint_mark', ''),
            'program_series':  d.get('program_series', ''),
            'theme_subject':   theme,
            'ai_grade':        d.get('ai_assigned_grade', ''),
            'community_grade': d.get('community_grade', ''),
            'review_count':    d.get('review_count', 0),
            'grade_tally':     grade_tally,
            'confidence_score': round(float(conf), 2),
            'image_url':       img,
            'flagged_at':      str(d.get('flagged_at', '')),
            'resolved':        d.get('resolved', False),
            'resolved_grade':  d.get('resolved_grade', ''),
            'resolved_by':     d.get('resolved_by', ''),
        })

    return {
        'status':  'ok',
        'results': flags,
        'count':   len(flags),
        'resolved': resolved,
    }


@app.post("/api/admin/grade_flags/{flag_id}/resolve")
async def resolve_grade_flag(
    flag_id:        str,
    admin_email:    str = Form(...),
    decision:       str = Form(...),   # 'accept_community' | 'keep_ai'
    resolved_grade: str = Form(''),
    notes:          str = Form(''),
):
    """
    Admin resolves a flagged coin grade.
    decision='accept_community' → updates coin Condition to community_grade
    decision='keep_ai'          → keeps existing AI grade, marks flag resolved
    """
    flag_ref = db.collection('admin_grade_flags').document(flag_id)
    flag_doc = flag_ref.get()
    if not flag_doc.exists:
        raise HTTPException(status_code=404, detail="Flag not found.")

    d          = flag_doc.to_dict()
    owner      = d.get('user_email', '')
    coin_id    = d.get('coin_id', flag_id)
    ai_grade   = d.get('ai_assigned_grade', '')
    comm_grade = d.get('community_grade', '')

    final_grade = comm_grade if decision == 'accept_community' else ai_grade
    if resolved_grade:
        final_grade = resolved_grade   # admin can also override both

    # Update the coin's Condition field
    if owner and coin_id:
        coin_ref = (db.collection('users').document(owner)
                      .collection('coins').document(coin_id))
        coin_ref.set({
            'Condition':           final_grade,
            'grade_review_status': 'admin_resolved',
            'admin_resolution': {
                'decision':    decision,
                'final_grade': final_grade,
                'resolved_by': admin_email,
                'notes':       notes,
            },
        }, merge=True)

    # Mark the flag resolved
    flag_ref.set({
        'resolved':      True,
        'resolved_grade': final_grade,
        'resolved_by':   admin_email,
        'resolved_at':   firestore.SERVER_TIMESTAMP,
        'resolution':    decision,
        'admin_notes':   notes,
    }, merge=True)

    action_desc = (f"Community grade '{comm_grade}' accepted"
                   if decision == 'accept_community'
                   else f"AI grade '{ai_grade}' kept")
    return {
        'status':      'ok',
        'message':     f'Resolved: {action_desc}. Coin updated to "{final_grade}".',
        'final_grade': final_grade,
    }


@app.get("/api/grade_review/stats")
def grade_review_stats(user_email: str):
    """Per-user grade review statistics for the Human AI Trainer dashboard."""
    coins_ref = db.collection('users').document(user_email).collection('coins')

    # Server-side filter — same two-query approach as queue endpoint
    seen_ids: set[str] = set()
    docs: list         = []
    try:
        for doc in coins_ref.where('source', 'in', list(AI_SOURCES)).stream():
            if doc.id not in seen_ids:
                seen_ids.add(doc.id)
                docs.append(doc)
    except Exception as e:
        print(f"[grade_review_stats] source query failed: {e}, falling back")
        docs     = list(coins_ref.stream())
        seen_ids = {d.id for d in docs}
    try:
        for doc in coins_ref.where('confidence_score', '<', 0.95).stream():
            if doc.id not in seen_ids:
                seen_ids.add(doc.id)
                docs.append(doc)
    except Exception:
        pass

    total_ai      = 0
    pending       = 0
    confirmed_ct  = 0
    flagged_ct    = 0
    reviewed_by_me = 0

    for doc in docs:
        d      = doc.to_dict()
        source = d.get('source', '')
        conf   = float(d.get('confidence_score', 1.0))
        is_ai  = source in AI_SOURCES or conf < 0.95
        if not is_ai:
            continue

        total_ai += 1
        status = d.get('grade_review_status', 'pending')
        if status == 'confirmed':
            confirmed_ct += 1
        elif status == 'flagged_for_admin_review':
            flagged_ct += 1
        else:
            pending += 1

        if any(r.get('reviewer') == user_email
               for r in d.get('grade_reviews', [])):
            reviewed_by_me += 1

    return {
        'total_ai_graded':  total_ai,
        'pending_review':   pending,
        'confirmed':        confirmed_ct,
        'flagged':          flagged_ct,
        'reviewed_by_me':   reviewed_by_me,
    }


@app.post("/api/process_invoice")
async def process_invoice(
    user_email:        str = Form(...),
    file:              UploadFile = File(...),
    import_session_id: str = Form(''),  # set by Bulk Import flow
    receipt_id:        str = Form(''),  # set by Bulk Import flow; links to receipts collection
    mask_pii:          bool = Form(False),
):
    """
    Uses GCP Document AI to scrape a PDF invoice, then heavily prompts Vertex AI 
    to filter out non-coin items (binders, sheets) and extract valid numismatic purchases.
    """
    contents = await file.read()
    
    # 1. Document AI Extraction (Standard Form Parser)
    try:
        doc_client = documentai.DocumentProcessorServiceClient()
        # In a generic environment, we can use vertex multimodal natively on the PDF if Document AI pipeline 
        # is too complex to setup for the generic endpoint here, so let's pass the raw PDF to Gemini 2.5 Pro Multimodal.
    except Exception as e:
        pass
        
    # Actually, Gemini 1.5/2.5 Pro Multimodal can read PDFs natively, performing both OCR and AI structuration in one pass!
    # This is *significantly* more robust than legacy DocumentAI.
    try:
        # Detect MIME type from extension — ignore browser fallback 'application/octet-stream'
        ext = (file.filename or "").rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else ""
        mime_map = {"pdf": "application/pdf", "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}
        reported_type = file.content_type or ""
        # Use reported type only if it's specific (not generic octet-stream)
        if reported_type and reported_type not in ("application/octet-stream", "binary/octet-stream", ""):
            mime_type = reported_type
        elif ext in mime_map:
            mime_type = mime_map[ext]
        else:
            # Magic byte sniff: PDFs start with %PDF (hex 25 50 44 46)
            mime_type = "application/pdf" if contents[:4] == b"%PDF" else "application/octet-stream"
        print(f"[process_invoice] filename={file.filename!r} reported={reported_type!r} → using mime={mime_type!r}")
        pdf_part = genai_types.Part.from_bytes(data=contents, mime_type=mime_type)


        # ─── Helper functions ─────────────────────────────────────────────────
        def _parse_cost(cost_str: str) -> float:
            """'$10.00' → 10.0. Returns 0.0 on any parse failure."""
            try:
                return float(str(cost_str).replace('$', '').replace(',', '').strip())
            except Exception:
                return 0.0

        def _apply_defaults(it: dict):
            """Apply schema defaults in-place."""
            it['deep_dive_status'] = 'PENDING'
            if not it.get('Program/Series'):
                it['Program/Series'] = (it.get('Country') or 'USA') + ' Invoice Import'
            if 'Condition' not in it:
                it['Condition'] = 'Ungraded'
            if 'Cost' not in it:
                it['Cost'] = '$0.00'
            # Auto-split combined Year+Mint (e.g. "2006D" → Year="2006", Mint Mark="D")
            import re as _re
            raw_year = str(it.get('Year', '')).strip()
            raw_mint = str(it.get('Mint Mark', '')).strip()
            if raw_year and not raw_mint:
                _ym = _re.match(r'^(\d{4}(?:-\d{4})?)\s*([A-WY-Z])$', raw_year, _re.IGNORECASE)
                if _ym:
                    it['Year'] = _ym.group(1)
                    it['Mint Mark'] = _ym.group(2).upper()

        pii_rule = ""
        if mask_pii:
            pii_rule = """
            CRITICAL SECURITY RULE (PII REDACTION):
            The user has requested to mask personal identifiable information (PII).
            Do NOT extract or include any customer name, customer phone number, customer email, customer shipping/billing address, credit card numbers, or other sensitive personal info in any extracted fields (e.g. in the "Personal Notes I", "Original Description from source", or "Retailer Name" fields). If these details are present, replace them with '[REDACTED]'.
            """

        extraction_prompt = f"""
        You are an expert numismatic accountant and collectibles specialist. Review this PDF invoice/receipt.
        Extract EVERY line item — coins, currency, stamps, medals, sets, supplies, and other collectibles.
        Classify each item by type and return a full, accurate record.
        {pii_rule}

        *** NEVER RETURN AN EMPTY LIST. If you can see any purchasable item with a dollar amount > $0
        in this invoice, you MUST extract it. An empty list [] is only acceptable when the document
        truly contains zero purchasable items (e.g. it is a blank page or a pure shipping notice). ***

        CRITICAL RULES:
        1. Ignore shipping, tax, discount, and subtotal rows — extract only purchasable line items.
        2. Extract ALL item types, not just coins. Use the item_type field to classify each.
        3. MULTI-LINE DESCRIPTIONS: Many invoices have item descriptions that span several lines within
           a single table row (e.g. the club name on line 1, coin name on line 2, grade/service on
           line 3, notation like "Taxable Item" on line 4). Treat all those lines TOGETHER as ONE item.
        4. RETAILER IDENTIFICATION — use these fingerprints even if the company name does NOT appear on the invoice:
           - Phone "1-800-645-3122" OR Customer# starting with "54" (5-8 digits) → "Littleton Coin Company"
           - Phone "1-800-546-2995" OR "littletoncoin.com" → "Littleton Coin Company"
           - "Washington Quarter Club" OR "Statehood Quarter Club" OR "Morgan Dollar Club" OR
             "Lincoln Cent Club" OR any "[Coin Type] Club Selection" heading → "Littleton Coin Company"
             (These are Littleton subscription club programs. Each invoice is ONE individual coin purchase.)
           - "shop.usmint.gov" OR "United States Mint" OR "usmint.gov" OR phone "1-800-872-6468" → "US Mint"
           - "APMEX" OR "apmex.com" → "APMEX"
           - "JM Bullion" OR "jmbullion.com" → "JM Bullion"
           - "SD Bullion" OR "sdbullion.com" → "SD Bullion"
           - "Provident Metals" OR "providentmetals.com" → "Provident Metals"
           - "BGASC" OR "bgasc.com" → "BGASC"
           - "MCM" OR "moderncoinmart.com" → "Modern Coin Mart"
           - "GovMint" OR "govmint.com" → "GovMint"
           - "American Mint" OR "americanmint.com" → "American Mint"
           - "PCS Coins" OR "PCS Stamps" OR "PCS Coins and Stamps" OR "pcscoins.com" → "PCS Stamps & Coins"
           - "JP Capital Collectibles" OR "JP CAPITAL COLLECTIBLES" → "JP Capital Collectibles LLC"
           - "Danbury Mint" OR "danburymint.com" → "The Danbury Mint"
           If you cannot determine the retailer, set "Retailer/Website" to "Unknown".

        CLUB/SUBSCRIPTION PROGRAM INVOICES:
          Littleton Coin Company and similar retailers sell coins through subscription clubs.
          When you see a heading like "WASHINGTON QUARTER CLUB SELECTION", "MORGAN DOLLAR CLUB",
          "STATE QUARTER SELECTION", etc., the ACTUAL COIN is described on the NEXT line(s).
          Example invoice layout:
            Qty: 1  Item: 2330A.XD  Description: WASHINGTON QUARTER CLUB SELECTION
                                                  1871 Liberty Seated Silver Quarter
                                                  ANACS
                                                  Taxable Item           Extremely Fi  $432.00
          → Extract as item_type "coin", Year "1871", Denomination "Liberty Seated Quarter",
            Grading Service "ANACS", Condition "Extremely Fine", Purchase Cost "$432.00".
          DO NOT skip these items. The coin IS purchasable — the "Club Selection" heading is just
          the program name, not a separate line item.

        TRUNCATED TEXT COMPLETION:
          Scanned invoices often cut off text at column boundaries. Complete using numismatic knowledge:
          - "Extremely Fi" → Condition: "Extremely Fine" (EF)
          - "Very Fi" → Condition: "Very Fine" (VF)
          - "Very Go" → Condition: "Very Good" (VG)
          - "Mint St" → Condition: "Mint State"
          - "Uncircula" or "Uncirc" → Condition: "Uncirculated"
          - "Brillian" → Condition: "Brilliant Uncirculated"
          - "About Un" → Condition: "About Uncirculated" (AU)
          - "Choice Un" → Condition: "Choice Uncirculated"
          - "Fine" alone → Condition: "Fine" (F-12)
          Always complete grade words; do not leave them truncated in the output.

        ITEM TYPE CLASSIFICATION — set item_type for every record:
          "coin"           → individual coin, bullion coin, or token
          "set"            → a named group of coins sold together (e.g. "1971-1978 Ike Set", "Lincoln Cent Collection")
                             MUST also populate set_contents listing each individual coin in the set
          "paper_currency" → banknote, Silver Certificate, Federal Reserve Note, Obsolete Note, Fractional Currency, Legal Tender Note
          "medal"          → commemorative medal, token, or non-monetary medallion
          "stamp"          → postage stamp or stamp block
          "supply"         → binder, coin page, holder, slab, capsule, album, magnifier, shipping supply
          "other"          → anything not covered above

        STAMP DISAMBIGUATION — this is CRITICAL:
          Postage stamps often appear on the SAME invoice as coins from retailers like Littleton.
          A line item is a STAMP (not a coin) if ANY of these are true:
            - The description contains the word "stamp" or "block of [N]"
            - It has a Scott catalog number (e.g. "#1234" or "Scott 1234")
            - The subject is clearly historical art/event (e.g. "Iwo Jima", "Lexington & Concord",
              "Military Academy West Point") AND the face value is a small postage amount (≤$1.00)
            - The quantity is listed as a "block" (e.g. "(15)" or "block of 4")
          EXAMPLE: "1937 5c Military Academy West Point (15)" = STAMP, not a Buffalo Nickel.
          EXAMPLE: "1990 25c Eisenhower" on a Littleton invoice alongside stamps = STAMP.
          EXAMPLE: "1945 Iwo Jima" at $0.XX = STAMP.
          NOTE: Pre-1900 US coins (1800s Liberty Seated, Bust, Draped Bust, Capped Bust series,
          Early American coins, Morgan Dollars, Barber coins, etc.) are always COINS, not stamps.

        FOR SETS — when item_type is "set":
          Enumerate the individual coins in set_contents. Use your numismatic knowledge to list
          each coin by year, mint mark, and denomination. Example for "1971-1978 Ike Set Unc & Proof":
          set_contents should list 1971-P, 1971-D, 1972-P, 1972-D ... through 1978.

        Return ONLY a JSON list of objects. Every object MUST include item_type.
        Schema (all fields apply to coins; use relevant fields for other types):
        [
          {
            "item_type": "coin | set | paper_currency | medal | stamp | supply | other",
            "Country": "Country of origin (USA for US items)",
            "Year": "numeric year or year range",
            "Mint Mark": "e.g. P, D, S, W — blank if none",
            "Denomination": "e.g. Lincoln Cent, Morgan Dollar, $1 Silver Certificate",
            "Quantity": 1,
            "Program/Series": "e.g. 50 State Quarters, American Women Quarters",
            "Theme/Subject": "Specific subject or design description",
            "Condition": "e.g. MS-65, Average Circ, Ch Proof-63",
            "Strike Type": "e.g. Business, Proof, Special Mint Set, Uncirculated",
            "Holder Type": "e.g. Raw, Slabs, Folder",
            "Grading Service": "e.g. PCGS, NGC, PMG, None",
            "Certification Number": "if present",
            "Metal Content": "e.g. 90% Silver, Cupro-Nickel, 35% Silver Wartime",
            "Purchase Cost": "formatted price like $10.00",
            "Purchase Date": "found on invoice",
            "Retailer/Website": "Identified retailer name (see RETAILER IDENTIFICATION rules)",
            "Retailer Item No.": "The specific stock/item number",
            "Retailer Invoice #": "The invoice ID",
            "Variety": "CRITICAL: Look for Double Die, Mint Error, Repunched Mint Mark, or errors",
            "Personal Notes I": "",
            "Personal Reference #": "",
            "Storage Location": "",
            "Original Description from source": "THE EXACT FULL LINE DESCRIPTION FROM THE INVOICE",
            "set_contents": []
          }
        ]

        NOTE: set_contents is ONLY populated when item_type is "set". It is an array of coin objects
        with at minimum: Year, Mint Mark, Denomination, Strike Type.

        DICTIONARY FOR MAPPING: """ + json.dumps(COIN_DICTIONARY) + """
        """
        
        # Try PRO model first; fall back to PRIMARY if it fails (e.g. model
        # deprecated, quota exhausted, or API error).
        try:
            response = genai_client.models.generate_content(
                model=PRO_MODEL,
                contents=[pdf_part, genai_types.Part.from_text(text=extraction_prompt)],
                config=genai_types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            print(f"[process_invoice] PRO model OK, filename={file.filename!r}")
        except Exception as pro_err:
            print(f"[process_invoice] PRO model failed ({pro_err!r}); retrying with PRIMARY")
            response = genai_client.models.generate_content(
                model=PRIMARY_MODEL,
                contents=[pdf_part, genai_types.Part.from_text(text=extraction_prompt)],
                config=genai_types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            print(f"[process_invoice] PRIMARY model OK, filename={file.filename!r}")

        raw_text = response.text or ""
        print(f"[process_invoice] raw_snippet={raw_text[:400]!r}")

        items = json.loads(raw_text) if raw_text.strip() else []
        if isinstance(items, dict):
            # Gemini sometimes wraps the list in an outer object —
            # try every known wrapper key before falling back to [the dict itself].
            for _key in ('items', 'coins', 'line_items', 'results', 'data',
                         'extracted_items', 'invoice_items', 'coin_items'):
                if _key in items and isinstance(items[_key], list):
                    items = items[_key]
                    break
            else:
                items = [items]   # treat the whole dict as one item record
        if not isinstance(items, list):
            items = []

        # ─── Retry pass: if first extraction returned nothing, try a simpler ──────
        # directive prompt focused purely on "find me the items with prices".
        if not items:
            print(f"[process_invoice] First pass empty — firing directive retry prompt")
            retry_prompt = """
            This is a coin/numismatic purchase invoice or receipt. I need you to extract every
            purchasable item that has a dollar amount > $0 associated with it.

            Look for ANY table row or line that contains:
            - A coin name (e.g. "1871 Liberty Seated Silver Quarter", "Morgan Dollar", "Lincoln Cent")
            - A currency note or collectible
            - A price/amount column with a non-zero value

            Rules:
            - If a description spans multiple lines in the same row, combine them into one item.
            - Complete truncated text: "Extremely Fi" → "Extremely Fine",
              "Very Fi" → "Very Fine", "About Un" → "About Uncirculated", etc.
            - For "Club Selection" invoices, the coin is on line 2 of the description block.
            - Ignore shipping, tax, and subtotal lines.
            - Pre-1900 coins (Liberty Seated, Barber, Morgan, etc.) are coins, not stamps.

            Return a JSON array with one object per item. Required fields:
            {
              "item_type": "coin",
              "Year": "year from description",
              "Denomination": "coin type (e.g. Liberty Seated Quarter, Morgan Dollar)",
              "Condition": "grade — complete any truncated words",
              "Grading Service": "PCGS / NGC / ANACS / ICG / or empty",
              "Purchase Cost": "dollar amount formatted like $432.00",
              "Retailer/Website": "seller name",
              "Retailer Item No.": "item or stock number if present",
              "Retailer Invoice #": "invoice number if present",
              "Original Description from source": "exact description text from invoice"
            }

            Even a single item is a valid result. Do NOT return [].
            """
            try:
                retry_response = genai_client.models.generate_content(
                    model=PRIMARY_MODEL,
                    contents=[pdf_part, genai_types.Part.from_text(text=retry_prompt)],
                    config=genai_types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                retry_text = retry_response.text or ""
                print(f"[process_invoice] retry_snippet={retry_text[:400]!r}")
                retry_items = json.loads(retry_text) if retry_text.strip() else []
                if isinstance(retry_items, dict):
                    for _key in ('items', 'coins', 'line_items', 'results', 'data',
                                 'extracted_items', 'invoice_items'):
                        if _key in retry_items and isinstance(retry_items[_key], list):
                            retry_items = retry_items[_key]
                            break
                    else:
                        retry_items = [retry_items]
                if isinstance(retry_items, list) and retry_items:
                    items = retry_items
                    print(f"[process_invoice] Retry succeeded: {len(items)} item(s) recovered")
                else:
                    print(f"[process_invoice] Retry also returned empty — genuinely nothing found")
            except Exception as retry_err:
                print(f"[process_invoice] Retry failed: {retry_err!r}")

        # ─── Route items by type ──────────────────────────────────────────────
        added_count    = 0   # coins, currency, medals, set-records → review_queue
        set_count      = 0   # number of set records
        set_coins_inside = 0 # total coins inside all sets
        pending_count  = 0   # stamps, other → pending_items
        supplies_count = 0   # supplies → supplies_log

        batch   = db.batch()
        col_ref = db.collection('users').document(user_email).collection('review_queue')
        pending_ref  = db.collection('users').document(user_email).collection('pending_items')
        supplies_ref = db.collection('users').document(user_email).collection('supplies_log')

        for item in items:
            if not isinstance(item, dict):
                continue

            item_type = str(item.get('item_type', 'coin')).lower().strip()
            item['source']      = 'PDF Invoice'
            item['source_file'] = file.filename
            item['created_at']  = firestore.SERVER_TIMESTAMP
            # Paper Trail back-references
            if import_session_id:
                item['import_session_id'] = import_session_id
            if receipt_id:
                item['receipt_id'] = receipt_id
                item['paper_trail'] = {
                    'receipt_id':  receipt_id,
                    'gcs_path':    f'receipts/{user_email}/{receipt_id}/original{("." + (file.filename or "pdf").rsplit(".", 1)[-1].lower()) if "." in (file.filename or "") else ".pdf"}',
                    'matched_at':  None,
                    'match_score': None,
                }
            _apply_defaults(item)

            if item_type == 'set':
                # Store as a single SET RECORD — user decides Break Up or Keep as Set
                set_id       = str(uuid.uuid4())
                set_contents = item.get('set_contents', [])
                if not isinstance(set_contents, list):
                    set_contents = []
                n_coins = max(len(set_contents), 1)
                item['set_id']         = set_id
                item['set_size']       = n_coins
                item['set_cost_label'] = f"{item.get('Purchase Cost', '$0.00')} total / {n_coins} coins"
                item['set_broken_up']  = False
                doc_ref = col_ref.document(set_id)
                batch.set(doc_ref, item)
                added_count      += 1
                set_count        += 1
                set_coins_inside += n_coins

            elif item_type in ('coin', 'paper_currency', 'medal', 'other', ''):
                # Numismatic items → review_queue
                doc_ref = col_ref.document(str(uuid.uuid4()))
                batch.set(doc_ref, item)
                added_count += 1

            elif item_type == 'stamp':
                # Stamps → pending_items (future Stamps module)
                doc_ref = pending_ref.document(str(uuid.uuid4()))
                batch.set(doc_ref, item)
                pending_count += 1

            elif item_type == 'supply':
                # Supplies → supplies_log (Inventory / expense tracking)
                doc_ref = supplies_ref.document(str(uuid.uuid4()))
                batch.set(doc_ref, item)
                supplies_count += 1

            else:
                # Unknown types → pending_items for safety
                doc_ref = pending_ref.document(str(uuid.uuid4()))
                batch.set(doc_ref, item)
                pending_count += 1

        batch.commit()

        # Strip non-serializable Firestore sentinels before returning
        response_items = [
            {k: v for k, v in it.items() if k != 'created_at'}
            for it in items if isinstance(it, dict)
        ]
        return {
            "status":           "success",
            "extracted_items":  added_count,
            "set_records":      set_count,
            "set_coins_inside": set_coins_inside,
            "pending_items":    pending_count,
            "supplies_logged":  supplies_count,
            "data":             response_items,
        }
        
    except Exception as e:
        print(f"Error extracting invoice: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mint_news")
def get_mint_news():
    """
    Aggregates numismatic news for the Numista.AI Market Intel feed.

    Priority:
      1. NewsAPI.org  — key from NEWSAPI_KEY env var or Firestore config/newsapi
      2. RSS fallback — CoinWorld + Numismatic News if key unavailable / API fails

    Each article: {title, source, published, summary, link}
    """
    import requests as req

    # ── 1. Resolve NewsAPI key ─────────────────────────────────────────────────
    news_api_key = os.environ.get("NEWSAPI_KEY", "").strip()
    if not news_api_key:
        try:
            # timeout=3 prevents indefinite hang if Firestore is slow
            cfg = db.collection("config").document("newsapi").get(timeout=3)
            if cfg.exists:
                news_api_key = cfg.to_dict().get("api_key", "")
        except Exception as e:
            print(f"[mint_news] Firestore key lookup failed: {e}")

    # ── 2. Try NewsAPI.org ─────────────────────────────────────────────────────
    if news_api_key:
        try:
            # Collector-focused query — specific enough to avoid commodity/finance noise.
            # Exclusions (-term) prevent astronomy (NGC=galaxy catalog), crypto, beer, fashion.
            # "American Eagle" alone matches Anheuser-Busch; use exact numismatic phrases.
            # NGC alone matches New General Catalogue (astronomy); remove standalone NGC.
            collector_query = (
                "numismatic OR "
                "\"coin collecting\" OR \"coin collector\" OR \"coin show\" OR "
                "\"proof set\" OR \"mint set\" OR \"coin dealer\" OR \"coin auction\" OR "
                "PCGS OR "
                "\"Morgan dollar\" OR \"Peace dollar\" OR \"American Eagle coin\" OR "
                "\"American Eagle bullion\" OR \"Walking Liberty\" OR \"Saint-Gaudens\" OR "
                "\"US Mint\" OR \"United States Mint\" OR "
                "\"uncirculated\" OR \"commemorative coin\" OR \"numismatics\""
                " -bitcoin -crypto -cryptocurrency -ethereum -blockchain -NFT"
                " -cluster -galaxy -beer -beauty -fashion -election -tariff"
            )
            params = {
                "q":        collector_query,
                "language": "en",
                "sortBy":   "publishedAt",
                "pageSize": 30,
                "apiKey":   news_api_key,
            }

            # Require a numismatic keyword in the article TITLE.
            # NewsAPI full-text search matches words buried anywhere in the article,
            # so politics/tech articles mentioning "coin" in passing sneak through.
            # Keywords that MUST appear in the title to keep the article
            _COIN_KW = {
                "numismatic", "numismatics", "coin", "coins", "mint", "minted",
                "pcgs", "proof set", "mint set", "bullion", "morgan dollar",
                "peace dollar", "american eagle coin", "american eagle bullion",
                "walking liberty", "saint-gaudens", "commemorative coin",
                "commemorative coins", "uncirculated", "coin show",
                "coin auction", "coin dealer",
            }
            # Keywords that cause immediate rejection even if a coin term appears
            _BLOCK_KW = {
                "bitcoin", "crypto", "cryptocurrency", "ethereum", "blockchain",
                "nft", "defi", "altcoin", "dogecoin", "litecoin", "ripple",
                "election", "senate", "congress", "parliament", "politics",
                "legislation", "tariff", "trade war", "policy",
            }
            # Block India-sourced articles (common source names from NewsAPI)
            _BLOCK_SOURCES = {
                "the hindu", "times of india", "hindustan times", "ndtv",
                "economic times", "mint",  # Indian financial paper, not US Mint
                "india today", "deccan chronicle", "business standard",
            }

            def _is_coin_title(t: str) -> bool:
                tl = t.lower()
                return any(kw in tl for kw in _COIN_KW)

            def _is_blocked(title: str, source_name: str) -> bool:
                tl = title.lower()
                sl = source_name.lower()
                if any(bk in tl for bk in _BLOCK_KW):
                    return True
                if any(bs in sl for bs in _BLOCK_SOURCES):
                    return True
                return False

            resp = req.get("https://newsapi.org/v2/everything", params=params, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                articles = data.get("articles", [])
                results = []
                for a in articles:
                    title       = a.get("title", "")
                    source_name = a.get("source", {}).get("name", "")
                    if not title or title == "[Removed]":
                        continue
                    # Must have a numismatic keyword in the title
                    if not _is_coin_title(title):
                        continue
                    # Hard-block crypto, politics, India-sourced
                    if _is_blocked(title, source_name):
                        continue
                    # Human-friendly relative date
                    raw_dt = a.get("publishedAt", "")
                    try:
                        from datetime import timezone
                        dt = datetime.fromisoformat(raw_dt.replace("Z", "+00:00"))
                        now = datetime.now(tz=timezone.utc)
                        delta = now - dt
                        if delta.days == 0:
                            hours = delta.seconds // 3600
                            pub_str = f"{hours}h ago" if hours > 0 else "Just now"
                        elif delta.days == 1:
                            pub_str = "Yesterday"
                        elif delta.days < 7:
                            pub_str = f"{delta.days}d ago"
                        else:
                            pub_str = dt.strftime("%b %d, %Y")
                    except Exception:
                        pub_str = raw_dt[:10]

                    desc = a.get("description") or a.get("content") or ""
                    desc = re.sub(r"<[^>]+?>", "", desc)
                    if len(desc) > 220:
                        desc = desc[:220].rsplit(" ", 1)[0] + "\u2026"

                    results.append({
                        "title":     title,
                        "source":    a.get("source", {}).get("name", "News"),
                        "published": pub_str,
                        "summary":   desc,
                        "link":      a.get("url", ""),
                    })
                if results:
                    return {"status": "ok", "source": "newsapi", "news": results}
        except Exception as e:
            print(f"[mint_news] NewsAPI call failed: {e}")

    # ── 3. RSS fallback — verified working feeds with per-feed timeout ─────────
    from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
    feeds = [
        # US Mint first — official government releases, always relevant
        ("https://www.usmint.gov/rss/news.xml",       "US Mint"),
        # Top collector trade publications
        ("https://coinweek.com/feed/",                "CoinWeek"),
        ("https://www.pcgs.com/rss/news",              "PCGS"),
        ("https://www.ngccoin.com/rss/news.ashx",      "NGC"),
        ("https://www.coinnews.net/feed/",             "CoinNews"),
        ("https://www.numismaticnews.net/feed",        "Numismatic News"),
    ]
    all_entries = []
    for url, label in feeds:
        try:
            with ThreadPoolExecutor(max_workers=1) as ex:
                future = ex.submit(feedparser.parse, url)
                feed = future.result(timeout=5)  # 5s max per feed
            for entry in feed.entries[:4]:
                summary = re.sub(r"<[^>]+?>", "", entry.get("summary", ""))
                if len(summary) > 220:
                    summary = summary[:220].rsplit(" ", 1)[0] + "\u2026"
                all_entries.append({
                    "title":     entry.get("title", ""),
                    "link":      entry.get("link", ""),
                    "published": entry.get("published", "")[:16],
                    "summary":   summary,
                    "source":    label,
                })
        except FuturesTimeout:
            print(f"[mint_news] RSS feed timed out ({url})")
        except Exception as e:
            print(f"[mint_news] RSS feed error ({url}): {e}")

    return {"status": "ok", "source": "rss", "news": all_entries}


# ── News curation: user dismissal endpoints ────────────────────────────────────

class DismissNewsRequest(BaseModel):
    user_email: str
    article_id: str   # SHA-1 hex of the article URL — computed client-side

@app.post("/api/dismiss_news")
def dismiss_news(req: DismissNewsRequest):
    """
    Records a user's 'Not Relevant' tap so the article never appears again.
    Stores up to 500 dismissed IDs per user (oldest pruned automatically).
    """
    try:
        import hashlib
        ref = db.collection("users").document(req.user_email) \
                  .collection("meta").document("dismissed_news")
        doc = ref.get()
        ids: list = doc.to_dict().get("ids", []) if doc.exists else []
        if req.article_id not in ids:
            ids.append(req.article_id)
        if len(ids) > 500:
            ids = ids[-500:]   # keep most recent 500
        ref.set({"ids": ids})
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dismissed_news/{user_email}")
def get_dismissed_news(user_email: str):
    """Returns the list of dismissed article IDs for a user."""
    try:
        ref = db.collection("users").document(user_email) \
                  .collection("meta").document("dismissed_news")
        doc = ref.get()
        ids = doc.to_dict().get("ids", []) if doc.exists else []
        return {"status": "ok", "ids": ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class DeepDiveRequest(BaseModel):
    user_email: str
    query: str
    # Optional fields sent by the Flutter app (Phase 3 Morgan Chat).
    # When collection_context is provided the backend skips its own Firestore
    # fetch — faster and avoids double-reading the same data.
    collection_context: str = ""
    user_name: str = ""

@app.post("/api/deep_dive")
async def deep_dive(request: DeepDiveRequest):
    """
    Morgan AI chat: answers questions about the user's coin collection.

    Two modes:
      • Flutter provides collection_context  → use it directly (faster, no extra Firestore read)
      • No collection_context provided       → fetch collection from Firestore (backward-compatible)

    Always responds as Morgan, Numista.AI's warm numismatic guide owl.
    """
    try:
        # ── 1. Resolve collection context ──────────────────────────────────────
        if request.collection_context and len(request.collection_context.strip()) > 50:
            # Flutter already built and sent the collection summary
            context = request.collection_context.strip()
        else:
            # Fallback: fetch directly from Firestore (keeps backward compatibility)
            col_ref = db.collection('users').document(request.user_email).collection('coins')
            docs = col_ref.stream()
            inventory_items = []
            for doc in docs:
                d = doc.to_dict()
                inventory_items.append({
                    "Year":      d.get("Year", ""),
                    "Denom":     d.get("Denomination", ""),
                    "Mint":      d.get("Mint Mark", ""),
                    "Condition": d.get("Condition", ""),
                    "Subject":   d.get("Theme/Subject", ""),
                    "Series":    d.get("Program/Series", ""),
                    "Value":     d.get("AI Estimated Value", "$0.00"),
                    "Cost":      d.get("Cost", "$0.00"),
                })
            if not inventory_items:
                context = "The user's collection is currently empty."
            else:
                context = json.dumps(inventory_items, default=str)

        # ── 2. Personalisation ─────────────────────────────────────────────────
        name = (request.user_name or "").strip()
        name_line = f"You are speaking with {name}." if name else ""

        # ── 3. RAG: look up coin knowledge base ────────────────────────────────
        knowledge_block = ""
        if MORGAN_KNOWLEDGE_AVAILABLE:
            try:
                kb_context = get_coin_context(db, request.query)
                if kb_context:
                    knowledge_block = f"\n\n{kb_context}"
            except Exception as kb_err:
                print(f"[deep_dive] Knowledge base lookup warning: {kb_err}")

        # ── 4. Build prompt ────────────────────────────────────────────────────
        prompt = f"""You are Morgan, the friendly AI numismatic guide owl for Numista.AI.
You are an enthusiastic, expert numismatic mentor — warm and patient like a trusted friend who happens to be a world-class coin expert.
You have encyclopedic knowledge of US coinage history, mint marks, designers, errors, and varieties.
{name_line}

Here is the user's current coin collection data:
{context}{knowledge_block}

User's Question: {request.query}

Instructions:
- Answer based on the collection data above whenever the question is about their specific coins.
- If NUMISMATIC REFERENCE DATA is provided above, use those verified facts to answer accurately. Cite design details, compositions, and historical context from that data.
- When asked for "most valuable", rank the collection by Value.
- Speak in plain, friendly English — explain any numismatic terms you use.
- Keep responses concise: 2–4 short paragraphs maximum (under 30 seconds of spoken length).
- If the question is about general numismatics (not their specific collection), answer as an expert using the reference data.
- If a coin they mention is NOT in their collection data, say you don't see it and suggest they add it.
- Do NOT invent or make up coin values — only reference what is in the data.
- Do NOT claim coins they don't own.
- If a coin is not in the reference database, say: 'I don't have that specific coin in my reference collection yet, but I'm constantly learning.'
"""

        # ── 5. Call Gemini ─────────────────────────────────────────────────────
        response = genai_client.models.generate_content(
            model=PRIMARY_MODEL,
            contents=[genai_types.Part.from_text(text=prompt)],
        )
        return {"status": "success", "response": response.text}

    except Exception as e:
        print(f"[deep_dive] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/review/commit")
async def commit_reviews(request: CommitReviewsRequest):
    """
    Moves items from review_queue to the primary collection with Duplicate Detection.
    A coin is only a true duplicate if Year, Mint, Denom, Invoice#, and Item# ALL match.
    """
    try:
        user_ref = db.collection('users').document(request.user_email)
        queue_ref = user_ref.collection('review_queue')
        coins_ref = user_ref.collection('coins')
        
        batch = db.batch()
        batch_op_count = 0
        committed_count = 0
        skipped_count = 0
        
        for doc_id in request.review_ids:
            doc_snapshot = queue_ref.document(doc_id).get()
            if doc_snapshot.exists:
                data = doc_snapshot.to_dict()
                
                # ── Hybrid Duplicate Detection ──────────────────────────────────────
                # Primary: invoice-based (if invoice# matches + item# matches → definite dupe)
                # Fallback: attribute-based (Year + Mint + normalized Denomination)
                inv_no  = (data.get('Retailer Invoice #') or '').strip()
                item_no = (data.get('Retailer Item No.')  or '').strip()
                is_dupe = False

                if inv_no:
                    try:
                        q = coins_ref \
                            .where('Retailer Invoice #', '==', inv_no) \
                            .where('Retailer Item No.',  '==', item_no) \
                            .limit(1).get()
                        is_dupe = len(q) > 0
                    except Exception:
                        pass  # Index may be missing — fall through to attribute check

                if not is_dupe:
                    # Attribute-based fallback: normalise denomination before compare
                    raw_d  = (data.get('Denomination') or '').strip()
                    norm_d = raw_d.lstrip('$').strip()   # "$5" → "5", "5" → "5"
                    denom_variants = list({raw_d, norm_d, f'${norm_d}'})
                    try:
                        q2 = coins_ref \
                            .where('Year',      '==', data.get('Year', '')) \
                            .where('Mint Mark', '==', data.get('Mint Mark', '')) \
                            .where('Denomination', 'in', denom_variants[:10]) \
                            .limit(1).get()
                        is_dupe = len(q2) > 0
                    except Exception:
                        pass

                if is_dupe:
                    batch.delete(queue_ref.document(doc_id))
                    skipped_count += 1
                    batch_op_count += 1
                else:
                    new_coin_ref = coins_ref.document(doc_id)
                    batch.set(new_coin_ref, data)
                    batch.delete(queue_ref.document(doc_id))
                    committed_count += 1
                    batch_op_count += 2
                    
                if batch_op_count >= 490:
                    batch.commit()
                    batch = db.batch()
                    batch_op_count = 0
        
        if batch_op_count > 0:
            batch.commit()
        return {
            "status": "success", 
            "message": f"Committed {committed_count} items. Skipped {skipped_count} duplicates.",
            "committed": committed_count,
            "skipped": skipped_count
        }
    except Exception as e:
        print(f"Commit error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/review/break_up_set")
async def break_up_set(request: Request):
    """
    Expands a set record in review_queue into individual coin records.
    Each coin gets set_id, set_name, set_cost_label, from_set=True.
    The original set record is then deleted.
    Request body: { user_email: str, set_doc_id: str }
    """
    try:
        body = await request.json()
        user_email  = body.get("user_email", "").strip()
        set_doc_id  = body.get("set_doc_id", "").strip()
        if not user_email or not set_doc_id:
            raise HTTPException(status_code=400, detail="user_email and set_doc_id are required")

        user_ref  = db.collection('users').document(user_email)
        queue_ref = user_ref.collection('review_queue')

        set_snap = queue_ref.document(set_doc_id).get()
        if not set_snap.exists:
            raise HTTPException(status_code=404, detail="Set document not found in review_queue")

        set_data     = set_snap.to_dict()
        set_contents = set_data.get('set_contents', [])
        if not isinstance(set_contents, list) or len(set_contents) == 0:
            raise HTTPException(status_code=422, detail="set_contents is empty — cannot break up")

        set_name       = set_data.get('Original Description from source', set_data.get('Theme/Subject', 'Unknown Set'))
        set_cost_label = set_data.get('set_cost_label', set_data.get('Purchase Cost', ''))
        n_coins        = len(set_contents)

        batch = db.batch()

        created = 0
        for coin in set_contents:
            if not isinstance(coin, dict):
                continue
            # Merge set-level fields with coin-level overrides
            expanded = {**set_data, **coin}
            expanded['item_type']      = 'coin'
            expanded['from_set']       = True
            expanded['set_id']         = set_doc_id
            expanded['set_name']       = set_name
            expanded['set_cost_label'] = set_cost_label
            expanded['set_size']       = n_coins
            # Clear set-specific fields that don't belong on individual coins
            expanded.pop('set_contents',  None)
            expanded.pop('set_broken_up', None)
            expanded['created_at'] = firestore.SERVER_TIMESTAMP

            new_doc = queue_ref.document(str(uuid.uuid4()))
            batch.set(new_doc, expanded)
            created += 1

        # Mark the original set as broken up (delete it)
        batch.delete(queue_ref.document(set_doc_id))

        batch.commit()
        return {
            "status":  "success",
            "set_id":  set_doc_id,
            "created": created,
            "message": f"Set broken up into {created} individual coin records.",
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"break_up_set error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/review/keep_set_as_is")
async def keep_set_as_is(request: Request):
    """
    Commits a set record from review_queue to the main 'coins' collection
    as a single set item (no expansion).
    The original review_queue doc is deleted after successful commit.
    Request body: { user_email: str, set_doc_id: str }
    """
    try:
        body = await request.json()
        user_email = body.get("user_email", "").strip()
        set_doc_id = body.get("set_doc_id", "").strip()
        if not user_email or not set_doc_id:
            raise HTTPException(status_code=400, detail="user_email and set_doc_id are required")

        user_ref  = db.collection('users').document(user_email)
        queue_ref = user_ref.collection('review_queue')
        coins_ref = user_ref.collection('coins')

        set_snap = queue_ref.document(set_doc_id).get()
        if not set_snap.exists:
            raise HTTPException(status_code=404, detail="Set document not found in review_queue")

        set_data = set_snap.to_dict()

        # Build the committed set record — keep set_contents for reference,
        # but mark it as committed and strip the queue-only flag.
        committed = {**set_data}
        committed['item_type']      = 'set'
        committed['kept_as_set']    = True
        committed['set_broken_up']  = False
        committed['committed_at']   = firestore.SERVER_TIMESTAMP

        batch = db.batch()
        # Write to main coins collection using the same doc ID for traceability
        batch.set(coins_ref.document(set_doc_id), committed)
        # Remove from review queue
        batch.delete(queue_ref.document(set_doc_id))
        batch.commit()

        set_name = set_data.get('Original Description from source',
                                set_data.get('Theme/Subject', 'Unknown Set'))
        return {
            "status":  "success",
            "set_id":  set_doc_id,
            "message": f"Set '{set_name}' committed to collection as a single set item.",
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"keep_set_as_is error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/review/bulk_update")
async def bulk_update_reviews(request: BulkUpdateRequest):
    """
    Applies shared metadata to multiple items in the review queue.
    """
    try:
        queue_ref = db.collection('users').document(request.user_email).collection('review_queue')
        batch = db.batch()
        batch_op_count = 0
        for doc_id in request.review_ids:
            batch.update(queue_ref.document(doc_id), request.updates)
            batch_op_count += 1
            if batch_op_count >= 490:
                batch.commit()
                batch = db.batch()
                batch_op_count = 0
        
        if batch_op_count > 0:
            batch.commit()
        return {"status": "success", "message": f"Updated {len(request.review_ids)} items"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _norm_date(raw: str) -> str:
    """Normalize a purchase date string to YYYY-MM-DD for key comparison.
    Handles: YYYY-MM-DD, MM/DD/YY, MM/DD/YYYY, M/D/YY, YYYY/MM/DD."""
    from datetime import datetime
    raw = str(raw).strip()
    if not raw:
        return ''
    for fmt in ('%Y-%m-%d', '%m/%d/%y', '%m/%d/%Y', '%-m/%-d/%y',
                '%Y/%m/%d', '%d-%m-%Y', '%B %d, %Y'):
        try:
            return datetime.strptime(raw, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    # Last resort: return as-is (still better than nothing)
    return raw


@app.post("/api/dedup_sweep")
async def dedup_sweep(user_email: str = Form(...)):
    """
    Scans a user's coins collection for potential duplicates.

    Match types (in order of confidence):
      - 'invoice'   : Same Invoice# AND Item# → near-certain re-import duplicate
      - 'attribute' : Same Year/Mint/Denom/Series/Theme/Condition/Date (normalized)
                      → same coin imported twice on the same date
      - 'possible'  : Same Year/Mint/Denom/Series/Theme/Condition but DIFFERENT dates
                      → flag for human review only; may be intentional multiples

    Coins that differ in Theme/Subject (e.g. different state/park quarters)
    are never grouped together.
    """
    try:
        coins_ref = db.collection('users').document(user_email).collection('coins')
        docs = coins_ref.stream()

        invoice_groups: dict  = {}   # invoice+item → list
        attr_groups: dict     = {}   # attribute key WITH date → list
        noddate_groups: dict  = {}   # attribute key WITHOUT date → list (for possible tier)

        for doc in docs:
            d = doc.to_dict()
            year    = str(d.get('Year', '')).strip()
            mint    = str(d.get('Mint Mark', '')).strip()
            denom   = str(d.get('Denomination', '')).strip().lstrip('$')
            series  = str(d.get('Program/Series', '')).strip().lower()
            theme   = str(d.get('Theme/Subject', '')).strip().lower()
            cond    = str(d.get('Condition', '')).strip().lower()
            inv_no  = str(d.get('Retailer Invoice #', '')).strip()
            item_no = str(d.get('Retailer Item No.', '')).strip()
            raw_date = str(d.get('Purchase Date', ''))
            norm_date = _norm_date(raw_date)

            snippet = {
                'id':      doc.id,
                'year':    year,
                'mint':    mint,
                'denom':   d.get('Denomination', ''),
                'series':  d.get('Program/Series', ''),
                'theme':   d.get('Theme/Subject', ''),
                'cond':    d.get('Condition', ''),
                'invoice': inv_no,
                'item_no': item_no,
                'date':    raw_date,
                'cost':    str(d.get('Cost', d.get('Purchase Cost', ''))),
            }

            # 1️⃣ Invoice key — only when BOTH invoice# AND item# are non-empty
            if inv_no and item_no:
                inv_key = f'inv::{inv_no}::{item_no}::{denom}'
                invoice_groups.setdefault(inv_key, []).append(snippet)
            else:
                # 2️⃣ Attribute key WITH normalized date — true duplicates
                #    (same coin imported twice on the same date)
                base_key  = f'{year}::{mint}::{denom}::{series}::{theme}::{cond}'
                attr_key  = f'attr::{base_key}::{norm_date}'
                attr_groups.setdefault(attr_key, []).append(snippet)

                # 3️⃣ No-date key — for possible-duplicate detection across dates
                #    We only promote to 'possible' if no attr group already covers it
                noddate_groups.setdefault(f'poss::{base_key}', []).append(snippet)

        # Collect definite duplicates (invoice + attribute)
        duplicates = []
        for k, v in invoice_groups.items():
            if len(v) > 1:
                duplicates.append({'key': k, 'match_type': 'invoice',
                                   'count': len(v), 'coins': v})
        for k, v in attr_groups.items():
            if len(v) > 1:
                duplicates.append({'key': k, 'match_type': 'attribute',
                                   'count': len(v), 'coins': v})

        # Collect possible duplicates — coins that share all attributes but have
        # DIFFERENT normalized dates.  Only include singleton-by-date coins so we
        # don't double-count coins already in an attribute-match group.
        for k, v in noddate_groups.items():
            if len(v) <= 1:
                continue
            # Bucket coins by their normalized date
            by_date: dict = {}
            for s in v:
                nd = _norm_date(s['date'])
                by_date.setdefault(nd, []).append(s)
            if len(by_date) <= 1:
                continue   # all same date → already in attr_groups, skip
            # Collect only the dates that have exactly ONE copy (true singletons).
            # Dates with 2+ copies are already surfaced in the attribute tier.
            singleton_coins = [coins[0] for coins in by_date.values() if len(coins) == 1]
            if len(singleton_coins) <= 1:
                continue   # not enough singletons to form a possible group
            duplicates.append({'key': k, 'match_type': 'possible',
                               'count': len(singleton_coins), 'coins': singleton_coins})

        # Sort: invoice → attribute → possible, then by count desc within each tier
        tier = {'invoice': 0, 'attribute': 1, 'possible': 2}
        duplicates.sort(key=lambda x: (tier.get(x['match_type'], 9), -x['count']))

        total = (sum(len(v) for v in invoice_groups.values()) +
                 sum(len(v) for v in attr_groups.values()))
        return {
            'status': 'success',
            'total_coins': total,
            'duplicate_groups': len(duplicates),
            'duplicates': duplicates,
        }
    except Exception as e:
        print(f'[dedup_sweep] Error: {e}')
        raise HTTPException(status_code=500, detail=str(e))




@app.post("/api/dedup_sweep/auto_clean")
async def dedup_auto_clean(user_email: str = Form(...)):
    """
    Automatically removes duplicates from INVOICE MATCH and ATTRIBUTE MATCH groups.

    - Invoice groups  (Invoice# + Item# + Denom):   keeps first, deletes the rest.
    - Attribute groups (Year/Mint/Denom/Series/Theme/Condition/Date-normalized):
      also keeps first, deletes the rest — same-date exact matches are
      just as safe as invoice matches for removing spreadsheet import duplicates.
    - Possible groups (same attributes, different dates): NEVER auto-deleted.

    Returns:
        groups_cleaned  : total groups processed
        coins_deleted   : total duplicate coins deleted
        coins_kept      : total coins retained (one per group)
    """
    try:
        coins_ref = db.collection('users').document(user_email).collection('coins')
        docs = list(coins_ref.stream())   # load all into memory

        invoice_groups: dict = {}
        attr_groups: dict    = {}

        for doc in docs:
            d = doc.to_dict()
            year    = str(d.get('Year', '')).strip()
            mint    = str(d.get('Mint Mark', '')).strip()
            denom   = str(d.get('Denomination', '')).strip().lstrip('$')
            series  = str(d.get('Program/Series', '')).strip().lower()
            theme   = str(d.get('Theme/Subject', '')).strip().lower()
            cond    = str(d.get('Condition', '')).strip().lower()
            inv_no  = str(d.get('Retailer Invoice #', '')).strip()
            item_no = str(d.get('Retailer Item No.', '')).strip()
            norm_date = _norm_date(str(d.get('Purchase Date', '')))

            if inv_no and item_no:
                key = f'inv::{inv_no}::{item_no}::{denom}'
                invoice_groups.setdefault(key, []).append(doc)
            else:
                attr_key = f'attr::{year}::{mint}::{denom}::{series}::{theme}::{cond}::{norm_date}'
                attr_groups.setdefault(attr_key, []).append(doc)

        groups_cleaned = 0
        coins_deleted  = 0
        coins_kept     = 0

        # Combine both group dicts for a single pass
        all_groups = list(invoice_groups.values()) + list(attr_groups.values())

        batch = db.batch()
        batch_count = 0

        for docs_in_group in all_groups:
            if len(docs_in_group) <= 1:
                continue
            groups_cleaned += 1
            coins_kept += 1
            for dup_doc in docs_in_group[1:]:
                batch.delete(coins_ref.document(dup_doc.id))
                coins_deleted += 1
                batch_count += 1
                if batch_count >= 490:
                    batch.commit()
                    batch = db.batch()
                    batch_count = 0


        if batch_count > 0:
            batch.commit()

        return {
            'status':         'success',
            'groups_cleaned': groups_cleaned,
            'coins_deleted':  coins_deleted,
            'coins_kept':     coins_kept,
        }
    except Exception as e:
        print(f'[dedup_auto_clean] Error: {e}')
        raise HTTPException(status_code=500, detail=str(e))






# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  PHASE 1: BINDER / HOLDER SCAN ENDPOINTS                                   ║
# ║  These endpoints power the "Add Coins by Holder Image" feature.             ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# ─── GCS helpers ─────────────────────────────────────────────────────────────

def _upload_to_gcs(file_bytes: bytes, dest_path: str, content_type: str = "image/jpeg") -> str:
    """
    Uploads bytes to the user-content GCS bucket.
    Returns the public gs:// URI.
    """
    bucket = gcs_client.bucket(USER_CONTENT_BUCKET)
    blob   = bucket.blob(dest_path)
    blob.upload_from_string(file_bytes, content_type=content_type)
    return f"gs://{USER_CONTENT_BUCKET}/{dest_path}"


def _bytes_to_b64(file_bytes: bytes) -> str:
    """Converts raw bytes to a base64 string for inline Gemini multimodal input."""
    return base64.b64encode(file_bytes).decode("utf-8")


# ─── The 50-State Quarters + DC/Territories master coin list ─────────────────
# Used to validate / cross-check AI output and fill in any gaps.
# Order matches physical binder layout (1999→2009).
STATE_QUARTER_PROGRAM = [
    # 1999
    {"year": "1999", "subject": "Delaware",          "abbr": "DE"},
    {"year": "1999", "subject": "Pennsylvania",       "abbr": "PA"},
    {"year": "1999", "subject": "New Jersey",         "abbr": "NJ"},
    {"year": "1999", "subject": "Georgia",            "abbr": "GA"},
    {"year": "1999", "subject": "Connecticut",        "abbr": "CT"},
    # 2000
    {"year": "2000", "subject": "Massachusetts",     "abbr": "MA"},
    {"year": "2000", "subject": "Maryland",           "abbr": "MD"},
    {"year": "2000", "subject": "South Carolina",     "abbr": "SC"},
    {"year": "2000", "subject": "New Hampshire",      "abbr": "NH"},
    {"year": "2000", "subject": "Virginia",           "abbr": "VA"},
    # 2001
    {"year": "2001", "subject": "New York",           "abbr": "NY"},
    {"year": "2001", "subject": "North Carolina",     "abbr": "NC"},
    {"year": "2001", "subject": "Rhode Island",       "abbr": "RI"},
    {"year": "2001", "subject": "Vermont",            "abbr": "VT"},
    {"year": "2001", "subject": "Kentucky",           "abbr": "KY"},
    # 2002
    {"year": "2002", "subject": "Tennessee",          "abbr": "TN"},
    {"year": "2002", "subject": "Ohio",               "abbr": "OH"},
    {"year": "2002", "subject": "Louisiana",          "abbr": "LA"},
    {"year": "2002", "subject": "Indiana",            "abbr": "IN"},
    {"year": "2002", "subject": "Mississippi",        "abbr": "MS"},
    # 2003
    {"year": "2003", "subject": "Illinois",           "abbr": "IL"},
    {"year": "2003", "subject": "Alabama",            "abbr": "AL"},
    {"year": "2003", "subject": "Maine",              "abbr": "ME"},
    {"year": "2003", "subject": "Missouri",           "abbr": "MO"},
    {"year": "2003", "subject": "Arkansas",           "abbr": "AR"},
    # 2004
    {"year": "2004", "subject": "Michigan",          "abbr": "MI"},
    {"year": "2004", "subject": "Florida",            "abbr": "FL"},
    {"year": "2004", "subject": "Texas",              "abbr": "TX"},
    {"year": "2004", "subject": "Iowa",               "abbr": "IA"},
    {"year": "2004", "subject": "Wisconsin",          "abbr": "WI"},
    # 2005
    {"year": "2005", "subject": "California",        "abbr": "CA"},
    {"year": "2005", "subject": "Minnesota",          "abbr": "MN"},
    {"year": "2005", "subject": "Oregon",             "abbr": "OR"},
    {"year": "2005", "subject": "Kansas",             "abbr": "KS"},
    {"year": "2005", "subject": "West Virginia",      "abbr": "WV"},
    # 2006
    {"year": "2006", "subject": "Nevada",             "abbr": "NV"},
    {"year": "2006", "subject": "Nebraska",           "abbr": "NE"},
    {"year": "2006", "subject": "Colorado",           "abbr": "CO"},
    {"year": "2006", "subject": "North Dakota",       "abbr": "ND"},
    {"year": "2006", "subject": "South Dakota",       "abbr": "SD"},
    # 2007
    {"year": "2007", "subject": "Montana",            "abbr": "MT"},
    {"year": "2007", "subject": "Washington",         "abbr": "WA"},
    {"year": "2007", "subject": "Idaho",              "abbr": "ID"},
    {"year": "2007", "subject": "Wyoming",            "abbr": "WY"},
    {"year": "2007", "subject": "Utah",               "abbr": "UT"},
    # 2008
    {"year": "2008", "subject": "Oklahoma",           "abbr": "OK"},
    {"year": "2008", "subject": "New Mexico",         "abbr": "NM"},
    {"year": "2008", "subject": "Arizona",            "abbr": "AZ"},
    {"year": "2008", "subject": "Alaska",             "abbr": "AK"},
    {"year": "2008", "subject": "Hawaii",             "abbr": "HI"},
    # 2009 DC & US Territories
    {"year": "2009", "subject": "District of Columbia", "abbr": "DC"},
    {"year": "2009", "subject": "Puerto Rico",        "abbr": "PR"},
    {"year": "2009", "subject": "Guam",               "abbr": "GU"},
    {"year": "2009", "subject": "American Samoa",     "abbr": "AS"},
    {"year": "2009", "subject": "U.S. Virgin Islands", "abbr": "VI"},
    {"year": "2009", "subject": "Northern Mariana Islands", "abbr": "MP"},
]

# Lookup by subject (case-insensitive)
_SQ_BY_SUBJECT = {c["subject"].lower(): c for c in STATE_QUARTER_PROGRAM}


# ─── The Spatial Analysis Prompt ─────────────────────────────────────────────

BINDER_SCAN_SYSTEM_PROMPT = """
You are an expert numismatic AI with advanced spatial reasoning capabilities.
You are analyzing photographs of a physical coin collection binder.

═══ YOUR TASK ═══
For every coin SLOT visible across ALL provided images, determine:
  1. Is a physical coin currently inserted in the slot? 
     - PRESENT = a coin is clearly visible (metallic disc, design visible)
     - ABSENT  = empty fabric/cardboard slot, hole, or placeholder visible
  2. Which coin belongs in this slot (year, subject/state, denomination)?
  3. What MINT MARK applies based on the page context?

═══ PAGE IDENTIFICATION RULES ═══
You will receive one or more images. Identify each page type:

  MAP PAGE (Main Collection Page):
  - Shows a geographic map of the United States with coin slots positioned 
    on their respective states
  - May also have slots for DC and non-contiguous territories (Hawaii, Alaska,
    Puerto Rico, Guam, US Virgin Islands, American Samoa, Northern Mariana Islands)
  - DEFAULT MINT MARK: Assign "P" (Philadelphia) to all coins on this page
    UNLESS the image text clearly states otherwise
  - The map page is typically the book's primary display page

  ALTERNATE MINT PAGE:
  - Usually labeled with text like "ALTERNATE MINT", "D", or similar
  - The header may say: "Use this space if you are collecting a complete set 
    of quarters from both the Philadelphia and Denver mints"
  - DEFAULT MINT MARK: Assign "D" (Denver) to ALL coins on this page
  - Layout is typically a grid of circular slots with year/state labels below

  CHECKLIST PAGE:
  - A printed list format (not a map) showing all coins in a program
  - May show check boxes, stamps, or handwritten marks indicating ownership

═══ SLOT OCCUPANCY DETECTION ═══
To determine if a coin is PRESENT vs ABSENT:
  PRESENT indicators:
    - Metallic/silver colored round disc visible
    - Coin design or portrait visible
    - The slot has a coin-colored object inside it
  ABSENT indicators:
    - You can see the fabric backing, cardboard, or foam insert material
    - The circular cutout is empty (showing material behind it)
    - The slot has a decorative placeholder or is clearly empty
    
  PARTIALLY VISIBLE: If a coin appears partially visible or obstructed,
  mark as PRESENT with "partially_visible": true

═══ OUTPUT FORMAT ═══
Return ONLY valid JSON matching this exact schema:
{
  "book_title": "string — detected title from any visible text, e.g. '50 State Commemorative Quarters Collector\'s Map'",
  "programs_detected": ["string", "..."],
  "page_count": integer,
  "pages": [
    {
      "page_index": 0,
      "page_type": "map_page | alternate_mint_page | checklist_page | unknown",
      "mint_assigned": "P | D | S | W | unknown",
      "mint_confidence": "high | medium | low",
      "mint_reasoning": "brief explanation of why this mint was assigned",
      "image_gcs_url": "to be filled server-side — leave as empty string",
      "slots_detected": integer
    }
  ],
  "coin_slots": [
    {
      "page_index": 0,
      "year": "string e.g. '1999'",
      "subject": "string e.g. 'Delaware'",
      "denomination": "Quarter",
      "program": "50 State Quarters | DC and US Territories",
      "mint": "P | D | S | W",
      "mint_uncertain": false,
      "present": true,
      "partially_visible": false,
      "slot_condition_note": "optional — any note about damage or ambiguity",
      "slot_bbox": {
        "x_pct": 0.25,
        "y_pct": 0.35,
        "w_pct": 0.05,
        "h_pct": 0.06
      }
    }
  ],
  "analysis_notes": "Any overall observations about the binder, image quality, or uncertainties",
  "mint_clarification_needed": false
}

═══ SLOT BOUNDING BOXES ═══
For each coin_slot, provide slot_bbox as PERCENTAGE coordinates (0.0–1.0) of the PAGE IMAGE:
  x_pct = left edge of the circular slot / image width
  y_pct = top edge of the circular slot / image height
  w_pct = diameter of the slot / image width
  h_pct = diameter of the slot / image height
Add a small margin (~20%) so the crop includes the slot label below the coin.
For map pages where slots are positioned geographically, estimate position as best you can.
If you genuinely cannot determine position, use: {"x_pct": 0, "y_pct": 0, "w_pct": 0, "h_pct": 0}

═══ IMPORTANT RULES ═══
- Report EVERY slot visible in the images, whether filled or empty
- Do NOT skip any slot, even if the coin is absent
- If reading the state label is ambiguous, use your best judgment and set
  mint_uncertain:true
- Cross-reference slot positions with expected program order 
  (50 states issued 1999-2008 in order of statehood; DC+territories in 2009)
- If an image is blurry or low quality, still attempt analysis and note it
- Set mint_clarification_needed:true if ANY coin's mint mark is ambiguous
"""


# ─── Coin Crop Endpoint ───────────────────────────────────────────────────────
# Dependencies: google-cloud-storage, Pillow (already in requirements.txt)
import base64, io as _io
from PIL import Image as _PILImage


@app.get("/api/coin_crop")
def get_coin_crop(coin_id: str, user_email: str):
    """
    Returns a base64-encoded JPEG crop of the specific coin's binder slot.

    Strategy:
    1. Load the coin doc → get scan_uuid, page_index, slot_bbox from Firestore.
    2. If slot_bbox exists (new scans): download the GCS page image, PIL crop, return.
    3. If slot_bbox is missing (old scans): return {"fallback": true} so Flutter
       displays the full binder page image instead (graceful degradation).
    """
    try:
        coin_ref = (db.collection('users').document(user_email)
                      .collection('coins').document(coin_id))
        coin_doc = coin_ref.get()
        if not coin_doc.exists:
            raise HTTPException(status_code=404, detail='Coin not found.')

        coin = coin_doc.to_dict()
        scan_uuid  = coin.get('scan_uuid', '')
        page_index = coin.get('page_index', 0)
        slot_bbox  = coin.get('slot_bbox', {})
        gcs_url    = coin.get('image_url_obverse', '')  # Full binder page URL

        # Graceful degradation for old coins without bbox
        if (not slot_bbox
                or slot_bbox.get('w_pct', 0) == 0
                or slot_bbox.get('h_pct', 0) == 0):
            return {
                'status':    'fallback',
                'message':   'No crop data for this coin — showing full binder page.',
                'image_url': gcs_url,
                'coin_id':   coin_id,
            }

        if not gcs_url:
            raise HTTPException(status_code=404, detail='No binder page image on file.')

        # Download the full binder page from GCS
        from google.cloud import storage as _gcs
        import re as _re

        # Parse GCS URL: could be gs:// or https://storage.googleapis.com/
        if gcs_url.startswith('gs://'):
            bucket_name, blob_name = gcs_url[5:].split('/', 1)
        elif 'storage.googleapis.com' in gcs_url:
            m = _re.match(
                r'https://storage\.googleapis\.com/([^/]+)/(.+)', gcs_url)
            if not m:
                raise HTTPException(status_code=400,
                    detail='Cannot parse GCS URL.')
            bucket_name, blob_name = m.group(1), m.group(2)
        else:
            # Not a GCS URL (could be Firebase Storage CDN URL)
            # Fall back to full-page display
            return {
                'status':    'fallback',
                'message':   'Image not in GCS — showing full binder page.',
                'image_url': gcs_url,
                'coin_id':   coin_id,
            }

        _gcs_client = _gcs.Client()
        bucket = _gcs_client.bucket(bucket_name)
        blob   = bucket.blob(blob_name)
        img_bytes = blob.download_as_bytes()

        # Open with PIL and crop using percentage coordinates
        img = _PILImage.open(_io.BytesIO(img_bytes)).convert('RGB')
        W, H = img.size

        x_pct = float(slot_bbox.get('x_pct', 0))
        y_pct = float(slot_bbox.get('y_pct', 0))
        w_pct = float(slot_bbox.get('w_pct', 0.1))
        h_pct = float(slot_bbox.get('h_pct', 0.1))

        # Add 25% margin so label below coin is included
        margin_x = w_pct * 0.25
        margin_y = h_pct * 0.25

        x1 = max(0, int((x_pct - margin_x) * W))
        y1 = max(0, int((y_pct - margin_y) * H))
        x2 = min(W, int((x_pct + w_pct + margin_x) * W))
        y2 = min(H, int((y_pct + h_pct + margin_y) * H))

        # Ensure minimum crop size (at least 80×80 px)
        if (x2 - x1) < 80 or (y2 - y1) < 80:
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            half = max(60, (x2 - x1) // 2, (y2 - y1) // 2)
            x1 = max(0, cx - half); x2 = min(W, cx + half)
            y1 = max(0, cy - half); y2 = min(H, cy + half)

        cropped = img.crop((x1, y1, x2, y2))

        # Encode as JPEG base64
        buf = _io.BytesIO()
        cropped.save(buf, format='JPEG', quality=88)
        b64 = base64.b64encode(buf.getvalue()).decode()

        return {
            'status':   'ok',
            'coin_id':  coin_id,
            'crop_b64': b64,
            'crop_size': [x2 - x1, y2 - y1],
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f'[coin_crop] Error: {e}')
        raise HTTPException(status_code=500,
            detail=f'Crop failed: {str(e)}')


@app.post("/api/analyze_binder_scan")
async def analyze_binder_scan(
    user_email:   str             = Form(...),
    binder_title: Optional[str]   = Form(None),
    images:       List[UploadFile] = File(...),
):
    """
    PHASE 1 — Main binder scan endpoint.

    Accepts 1-N photos of a coin collection binder/folder. Each image
    is uploaded to GCS and then sent to Gemini 1.5 Flash for spatial
    slot analysis. Returns a structured JSON payload describing every coin
    slot found (present or absent) and recommended metadata.

    Supports delta detection: if a prior binder_scan document already
    exists for this user+title, the response includes a 'new_coins' list
    containing only slots that changed from absent → present since the
    last scan.
    """
    if not images:
        raise HTTPException(status_code=400, detail="At least one image is required.")

    scan_uuid  = str(uuid.uuid4())
    gcs_urls   = []
    image_parts = []

    # ── 1. Upload each image to GCS and prepare multimodal parts ─────────────
    for idx, img_file in enumerate(images):
        raw_bytes   = await img_file.read()
        content_type = img_file.content_type or "image/jpeg"

        # Determine file extension for GCS path
        ext = img_file.filename.rsplit(".", 1)[-1].lower() if "." in img_file.filename else "jpg"

        gcs_path = f"users/{user_email}/binder_scans/{scan_uuid}/page_{idx:02d}.{ext}"
        gcs_url  = _upload_to_gcs(raw_bytes, gcs_path, content_type)
        gcs_urls.append(gcs_url)

        # Send inline (base64) to Gemini — faster than signed URL round-trip
        image_parts.append(genai_types.Part.from_bytes(data=raw_bytes, mime_type=content_type))
        image_parts.append(genai_types.Part.from_text(text=f"[Image {idx + 1} of {len(images)}: page_{idx:02d}.{ext}]"))

    # ── 2. Call Gemini 2.5 Flash with all images + system prompt ──────────────────
    try:
        prompt_parts = image_parts + [genai_types.Part.from_text(text=BINDER_SCAN_SYSTEM_PROMPT)]

        response = genai_client.models.generate_content(
            model=PRIMARY_MODEL,
            contents=prompt_parts,
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
                max_output_tokens=65536,
                thinking_config=genai_types.ThinkingConfig(thinking_budget=0),  # MINIMAL thinking
            ),
        )
        try:
            ai_result = json.loads(response.text)
        except json.JSONDecodeError as je:
            # If JSON is truncated, log and raise with detail
            print(f"[analyze_binder_scan] JSON parse error at char {je.pos}: {je.msg}")
            print(f"[analyze_binder_scan] Raw response tail: ...{response.text[-200:]}")
            raise HTTPException(
                status_code=500,
                detail=f"AI response was truncated or malformed: {je.msg} at position {je.pos}"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[analyze_binder_scan] Gemini error: {e}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {e}")

    # ── 3. Post-process: inject GCS URLs into page records ───────────────────
    for idx, page in enumerate(ai_result.get("pages", [])):
        if idx < len(gcs_urls):
            page["image_gcs_url"] = gcs_urls[idx]

    # Override book_title if user supplied one
    if binder_title:
        ai_result["book_title"] = binder_title

    book_title = ai_result.get("book_title", "Unknown Binder")

    # ── 4. Cross-reference with known program data ───────────────────────────
    # For each AI slot, verify it matches our master program list.
    # Fill in any subjects the AI may have missed based on slot order.
    validated_slots = _validate_and_enrich_slots(
        ai_result.get("coin_slots", []),
        ai_result.get("programs_detected", []),
    )
    ai_result["coin_slots"] = validated_slots

    # ── 5. Delta detection — compare to previous scan ────────────────────────
    new_coins     = []
    prior_scan_id = None

    try:
        binder_scans_ref = (
            db.collection("users")
              .document(user_email)
              .collection("binder_scans")
        )
        # Look for an existing scan with the same book title
        prior_query = (
            binder_scans_ref
            .where("title", "==", book_title)
            .order_by("last_scan_date", direction=firestore.Query.DESCENDING)
            .limit(1)
            .get()
        )

        if prior_query:
            prior_doc  = prior_query[0]
            prior_scan_id = prior_doc.id
            prior_data = prior_doc.to_dict()

            # Build a lookup of prior slot states: key = "year|subject|mint"
            prior_slots_lookup = {
                f"{s['year']}|{s['subject']}|{s['mint']}": s
                for s in prior_data.get("coin_slots", [])
            }

            for slot in validated_slots:
                slot_key = f"{slot['year']}|{slot['subject']}|{slot['mint']}"
                prior = prior_slots_lookup.get(slot_key)

                if slot.get("present") and (prior is None or not prior.get("present")):
                    # This slot is NOW present but was absent (or unknown) before
                    new_coins.append(slot)

    except Exception as e:
        print(f"[analyze_binder_scan] Delta detection warning: {e}")
        # Non-fatal — delta detection is best-effort

    is_first_scan = (prior_scan_id is None)
    present_coins = [s for s in validated_slots if s.get("present")]
    absent_coins  = [s for s in validated_slots if not s.get("present")]

    # ── 6. Save the raw scan result to Firestore ─────────────────────────────
    # This registers the scan for delta detection on future uploads.
    try:
        scan_doc = {
            "title":         book_title,
            "scan_uuid":     scan_uuid,
            "image_gcs_urls": gcs_urls,
            "programs":      ai_result.get("programs_detected", []),
            "last_scan_date": firestore.SERVER_TIMESTAMP,
            "coin_slots":    validated_slots,
            "pages":         ai_result.get("pages", []),
            "present_count": len(present_coins),
            "absent_count":  len(absent_coins),
            "total_slots":   len(validated_slots),
        }

        if prior_scan_id:
            # Update existing binder document
            binder_scans_ref.document(prior_scan_id).set(scan_doc, merge=True)
            binder_doc_id = prior_scan_id
        else:
            # Create new binder document
            new_ref = binder_scans_ref.document()
            new_ref.set(scan_doc)
            binder_doc_id = new_ref.id

    except Exception as e:
        print(f"[analyze_binder_scan] Firestore save warning: {e}")
        binder_doc_id = scan_uuid  # Use scan UUID as fallback

    # ── 7. Return full payload to Flutter ────────────────────────────────────
    return {
        "status":           "success",
        "binder_doc_id":    binder_doc_id,
        "scan_uuid":        scan_uuid,
        "book_title":       book_title,
        "programs_detected": ai_result.get("programs_detected", []),
        "image_gcs_urls":   gcs_urls,
        "pages":            ai_result.get("pages", []),
        "coin_slots":       validated_slots,
        "present_count":    len(present_coins),
        "absent_count":     len(absent_coins),
        "total_slots":      len(validated_slots),
        "is_first_scan":    is_first_scan,
        "new_coins":        new_coins,          # Empty list on first scan (all coins are "new")
        "mint_clarification_needed": ai_result.get("mint_clarification_needed", False),
        "analysis_notes":   ai_result.get("analysis_notes", ""),
    }


def _validate_and_enrich_slots(
    ai_slots: list,
    programs_detected: list,
) -> list:
    """
    Cross-references AI-detected slots against the known program master list.
    - Ensures denominations are standardized
    - Normalizes subject names
    - Flags any subjects not in our program master list
    """
    enriched = []
    for slot in ai_slots:
        subject_key = slot.get("subject", "").lower().strip()
        master = _SQ_BY_SUBJECT.get(subject_key)

        enriched_slot = dict(slot)
        enriched_slot["denomination"] = "Quarter"  # All 50-state programs are quarters

        if master:
            # Correct year if AI got it wrong (rare but possible)
            enriched_slot["subject"] = master["subject"]  # Normalize capitalization
            enriched_slot["program"] = (
                "DC and US Territories"
                if master["year"] == "2009" and master["abbr"] not in ["HI", "AK"]
                else "50 State Quarters"
            )
        else:
            # Subject not in master list — keep AI value, flag it
            enriched_slot["validation_warning"] = f"Subject '{slot.get('subject', '')}' not in program master list"

        enriched.append(enriched_slot)

    return enriched



# ─── Document AI Configuration ───────────────────────────────────────────────
# RECEIPT processor (DO NOT CHANGE): c113e9bb62be1554 — "Coin Receipts Data Extractor"
#   Used by invoice/receipt endpoints elsewhere in this file.
#
# CHECKLIST processor (new, dedicated): 7425afc720652ee4 — "Coin Checklist Extractor"
#   Created 2026-04-15. Trained on 650 synthetic Littleton checklist PDFs.
#   To retrain: Cloud Console → Document AI → Coin Checklist Extractor → Train
DOCUMENT_AI_PROCESSOR_PATH = (
    "projects/568985927038/locations/us/processors/261d6897c84ca28b"
    "/processorVersions/5d758c133d6114a0"  # littleton-v1 (fine-tuned 2026-04-17)
)

# Known checklist format signatures for Document AI routing.
# Key = format hint string, Value = descriptor for logging/UI display.
KNOWN_CHECKLIST_FORMATS = {
    "littleton":  "Littleton Coin Company",
    "whitman":    "Whitman / H.E. Harris",
    "numista":    "Numista.AI Export",
}

# ─── Series Name → Program Routing Table ─────────────────────────────────────
# Maps the `series_name` entity extracted by littleton-v1 → canonical program
# name and denomination used throughout the Firestore schema.
# Keys are lowercase for case-insensitive matching. Extend as new series are
# added to the Document AI training dataset.
SERIES_NAME_ROUTING = {
    # ── Silver Dollars ───────────────────────────────────────────────────────
    "morgan dollar":               {"program": "Morgan Silver Dollars",        "denomination": "Dollar"},
    "morgan silver dollar":        {"program": "Morgan Silver Dollars",        "denomination": "Dollar"},
    "peace dollar":                {"program": "Peace Silver Dollars",         "denomination": "Dollar"},
    "peace silver dollar":         {"program": "Peace Silver Dollars",         "denomination": "Dollar"},
    "eisenhower dollar":           {"program": "Eisenhower Dollars",           "denomination": "Dollar"},
    "susan b. anthony dollar":     {"program": "Susan B. Anthony Dollars",     "denomination": "Dollar"},
    "sacagawea dollar":            {"program": "Sacagawea Dollars",            "denomination": "Dollar"},
    # ── Half Dollars ─────────────────────────────────────────────────────────
    "liberty walking half dollar": {"program": "Walking Liberty Half Dollars", "denomination": "Half Dollar"},
    "walking liberty half dollar": {"program": "Walking Liberty Half Dollars", "denomination": "Half Dollar"},
    "franklin half dollar":        {"program": "Franklin Half Dollars",        "denomination": "Half Dollar"},
    "kennedy half dollar":         {"program": "Kennedy Half Dollars",         "denomination": "Half Dollar"},
    "barber half dollar":          {"program": "Barber Half Dollars",          "denomination": "Half Dollar"},
    "barber halves":               {"program": "Barber Half Dollars",          "denomination": "Half Dollar"},
    # ── Nickels ──────────────────────────────────────────────────────────────
    "liberty head nickel":         {"program": "Liberty Head Nickels",         "denomination": "Nickel"},
    "liberty head nickels":        {"program": "Liberty Head Nickels",         "denomination": "Nickel"},
    "buffalo nickel":              {"program": "Buffalo Nickels",              "denomination": "Nickel"},
    "buffalo nickels":             {"program": "Buffalo Nickels",              "denomination": "Nickel"},
    "jefferson nickel":            {"program": "Jefferson Nickels",            "denomination": "Nickel"},
    # ── Dimes ────────────────────────────────────────────────────────────────
    "barber dime":                 {"program": "Barber Dimes",                 "denomination": "Dime"},
    "barber dimes":                {"program": "Barber Dimes",                 "denomination": "Dime"},
    "mercury dime":                {"program": "Mercury Dimes",                "denomination": "Dime"},
    "winged liberty head dime":    {"program": "Mercury Dimes",                "denomination": "Dime"},
    "roosevelt dime":              {"program": "Roosevelt Dimes",              "denomination": "Dime"},
    "roosevelt dimes":             {"program": "Roosevelt Dimes",              "denomination": "Dime"},
    # ── Cents ────────────────────────────────────────────────────────────────
    "lincoln cent":                {"program": "Lincoln Cents",                "denomination": "Cent"},
    "lincoln cents":               {"program": "Lincoln Cents",                "denomination": "Cent"},
    "flying eagle cent":           {"program": "Flying Eagle & Indian Head Cents", "denomination": "Cent"},
    "indian head cent":            {"program": "Flying Eagle & Indian Head Cents", "denomination": "Cent"},
    # ── Proof & Special Sets ─────────────────────────────────────────────────
    "u.s. proof sets":             {"program": "U.S. Proof Sets",              "denomination": "Set"},
    "us proof sets":               {"program": "U.S. Proof Sets",              "denomination": "Set"},
    "proof sets":                  {"program": "U.S. Proof Sets",              "denomination": "Set"},
}


def _parse_coin_subject(subject: str) -> tuple:
    """
    Parses a v4 `coin_subject` string into (year, mint_mark).

    Handles formats produced by Littleton checklists:
      "1907"               → ("1907", "P")   plain Philadelphia year
      "1912-D"             → ("1912", "D")   Denver
      "1912-S"             → ("1912", "S")   San Francisco
      "1921-O"             → ("1921", "O")   New Orleans
      "1883 Without Cents" → ("1883", "P")   descriptive subject, no explicit mint
      "1955 Proof Set"     → ("1955", "S")   proof sets default to S mint

    Returns (year_str, mint_str). mint defaults to "P" when not explicit.
    """
    s = subject.strip()
    # "YYYY-M" or "YYYY-MM" e.g. "1912-D", "1921-O"
    m = re.match(r"(\d{4})-([A-Za-z]+)", s)
    if m:
        return m.group(1), m.group(2).upper()
    # Plain year at start: "1907", "1883 Without Cents", "1955 Proof Set"
    m = re.match(r"(\d{4})", s)
    if m:
        year = m.group(1)
        mint = "S" if "proof" in s.lower() else "P"
        return year, mint
    # No year detectable
    return "", "P"


def _detect_checklist_format(filename: str, content_type: str) -> str:
    """
    Attempts to detect the checklist format from filename/content-type hints.
    Returns a format key from KNOWN_CHECKLIST_FORMATS, or 'unknown'.

    This is a lightweight heuristic — the Flutter app can also pass format_hint
    directly to bypass detection.
    """
    name_lower = filename.lower()
    if "littleton" in name_lower:
        return "littleton"
    if "whitman" in name_lower or "harris" in name_lower:
        return "whitman"
    if "numista" in name_lower:
        return "numista"
    return "unknown"


def _analyze_checklist_with_document_ai(file_bytes: bytes, content_type: str) -> dict:
    """
    Sends a checklist PDF to the Document AI Custom Extraction Processor (littleton-v1).

    Schema v4 entities extracted:
      - series_name   (top-level)  → identifies the coin series (e.g. "Liberty Head Nickels")
      - coin_entry    (parent)     → one entity per checklist row
          - coin_subject  (child)  → e.g. "1907", "1912-D", "1955 Proof Set"
          - is_owned      (child)  → checkbox: True if circle is filled (owned)

    Returns:
      {
        "series_name": str,   # Raw extracted series name, or "" if not found
        "slots":       list,  # List of coin_slot dicts in standard binder_scan format
      }
    Falls back gracefully if the processor returns no useful data.
    """
    client = documentai.DocumentProcessorServiceClient(
        credentials=credentials,
        client_options={"api_endpoint": "us-documentai.googleapis.com"},
    )

    raw_doc = documentai.RawDocument(content=file_bytes, mime_type=content_type)
    request = documentai.ProcessRequest(
        name=DOCUMENT_AI_PROCESSOR_PATH,
        raw_document=raw_doc,
    )

    try:
        result = client.process_document(request=request)
        document = result.document
    except Exception as e:
        print(f"[Document AI] Processing error: {e}")
        return {"series_name": "", "slots": []}

    # ── 1. Extract top-level series_name ─────────────────────────────────────
    # series_name is a document-level entity (not nested inside coin_entry).
    # Used to resolve the canonical program name and denomination via SERIES_NAME_ROUTING.
    series_name = ""
    for entity in document.entities:
        if entity.type_.lower() == "series_name":
            series_name = entity.mention_text.strip()
            break  # Only one series_name per document

    routing      = SERIES_NAME_ROUTING.get(series_name.lower().strip(), {})
    program      = routing.get("program",      "Unknown Program")
    denomination = routing.get("denomination", "Unknown")
    print(f"[Document AI] series_name='{series_name}' → program='{program}'")

    # ── 2. Extract coin_entry entities (one per checklist row) ────────────────
    coin_slots = []
    for entity in document.entities:
        if entity.type_.lower() != "coin_entry":
            continue

        slot = {
            "page_index":          0,
            "year":                "",
            "subject":             "",
            "denomination":        denomination,
            "program":             program,
            "series_name":         series_name,
            "mint":                "P",
            "mint_uncertain":      True,
            "present":             False,   # Treat null/unlabeled as not owned
            "partially_visible":   False,
            "slot_condition_note": "",
            "source":              "document_ai",
        }

        for prop in entity.properties:
            ptype = prop.type_.lower()

            if ptype == "coin_subject":
                raw_subject    = prop.mention_text.strip()
                slot["subject"] = raw_subject
                year, mint     = _parse_coin_subject(raw_subject)
                slot["year"]   = year
                slot["mint"]   = mint
                slot["mint_uncertain"] = (mint == "P")  # P could mean unlabeled

            elif ptype == "is_owned":
                # Prefer the normalized boolean from checkbox fields when available.
                # Falls back to mention_text string comparison.
                try:
                    slot["present"] = prop.normalized_value.boolean_value
                except Exception:
                    raw = prop.mention_text.strip().lower()
                    slot["present"] = raw in ("true", "yes", "1", "checked", "owned", "filled")

        coin_slots.append(slot)

    return {"series_name": series_name, "slots": coin_slots}


@app.post("/api/analyze_checklist")
async def analyze_checklist(
    user_email:   str              = Form(...),
    binder_title: Optional[str]    = Form(None),
    format_hint:  Optional[str]    = Form(None),   # "littleton" | "whitman" | "numista" | "unknown"
    files:        List[UploadFile] = File(...),
):
    """
    Analyzes a printed coin program checklist (PDF or image scan).

    HYBRID ROUTING:
    1. If format is KNOWN → Document AI Custom Extractor (fast, 2-5s)
    2. If format is UNKNOWN or Document AI fails → Gemini 3-flash (flexible, ~15-20s)

    Supports:
    - Littleton Coin Company style PDF checklists (Document AI)
    - Whitman / H.E. Harris published checklists (Document AI)
    - Any unknown format, handwritten marks, image scans (Gemini fallback)

    Returns the same coin_slots structure as analyze_binder_scan.
    """
    scan_uuid    = str(uuid.uuid4())
    gcs_urls     = []
    all_raw_bytes = []  # Keep bytes for potential Gemini fallback

    for idx, f in enumerate(files):
        raw_bytes    = await f.read()
        content_type = f.content_type or "application/pdf"
        ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else "pdf"

        gcs_path = f"users/{user_email}/checklists/{scan_uuid}/page_{idx:02d}.{ext}"
        gcs_url  = _upload_to_gcs(raw_bytes, gcs_path, content_type)
        gcs_urls.append(gcs_url)
        all_raw_bytes.append((raw_bytes, content_type, f.filename))

    # ── Determine format and routing ─────────────────────────────────────────
    detected_format = format_hint or "unknown"
    if detected_format == "unknown" and all_raw_bytes:
        first_filename, first_ct = all_raw_bytes[0][2], all_raw_bytes[0][1]
        detected_format = _detect_checklist_format(first_filename, first_ct)

    use_document_ai = detected_format in KNOWN_CHECKLIST_FORMATS
    analysis_engine = "document_ai" if use_document_ai else "gemini"

    ai_result = None
    doc_ai_slots = []

    # ── Path A: Document AI (littleton-v1, schema v4) ────────────────────────
    doc_ai_series_name = ""
    if use_document_ai:
        print(f"[analyze_checklist] Using Document AI for format: {detected_format}")
        try:
            # Process each file — collect slots and the extracted series_name
            for raw_bytes, content_type, filename in all_raw_bytes:
                if content_type == "application/pdf":
                    result     = _analyze_checklist_with_document_ai(raw_bytes, content_type)
                    doc_ai_slots.extend(result["slots"])
                    # Use first non-empty series_name across all pages
                    if result["series_name"] and not doc_ai_series_name:
                        doc_ai_series_name = result["series_name"]

            if doc_ai_slots:
                # Resolve programs_detected from series routing
                programs = list({s.get("program", "Unknown") for s in doc_ai_slots})
                ai_result = {
                    "book_title": binder_title or doc_ai_series_name or f"{KNOWN_CHECKLIST_FORMATS[detected_format]} Checklist",
                    "programs_detected": programs,
                    "page_count": len(all_raw_bytes),
                    "pages": [
                        {
                            "page_index": i,
                            "page_type": "checklist_page",
                            "mint_assigned": "varies",
                            "mint_confidence": "high",
                            "mint_reasoning": f"Extracted by Document AI ({detected_format} format, series: {doc_ai_series_name})",
                            "image_gcs_url": gcs_urls[i] if i < len(gcs_urls) else "",
                            "slots_detected": len(doc_ai_slots),
                        }
                        for i in range(len(all_raw_bytes))
                    ],
                    "coin_slots": doc_ai_slots,
                    "analysis_notes": f"Processed by Document AI ({detected_format} processor). Series: {doc_ai_series_name or 'not detected'}.",
                    "mint_clarification_needed": any(s.get("mint_uncertain") for s in doc_ai_slots),
                }
                analysis_engine = "document_ai"
            else:
                print(f"[analyze_checklist] Document AI returned no entities — falling back to Gemini")
                use_document_ai = False  # Force fallback
        except Exception as e:
            print(f"[analyze_checklist] Document AI error, falling back to Gemini: {e}")
            use_document_ai = False

    # ── Path B: Gemini 3-flash fallback ────────────────────────────────────
    if not use_document_ai or ai_result is None:
        print(f"[analyze_checklist] Using Gemini {PRIMARY_MODEL} for checklist analysis")
        analysis_engine = "gemini"

        file_parts = []
        for raw_bytes, content_type, filename in all_raw_bytes:
            file_parts.append(genai_types.Part.from_bytes(data=raw_bytes, mime_type=content_type))
            file_parts.append(genai_types.Part.from_text(text=f"[File: {filename}]"))

        checklist_prompt = """
You are a numismatic AI analyzing a printed coin program checklist.

The user has uploaded scans of a printed checklist used by coin collectors to track
their collection. Common formats include:
  - Littleton Coin Company style: rows listing each coin with a checkbox/mark column
  - Whitman guide style: a grid or narrative list with check marks
  - Custom: any format where coins are listed and marks indicate ownership

For EACH coin entry on the checklist:
  1. Is this coin marked as OWNED? Look for: checkmarks ✓, X marks, stamps, stickers,
     handwritten letters ("Y", "yes", "have"), or any mark in the ownership column.
  2. What coin is this? (Year, Subject/State, Denomination, Mint Mark if listed)
  3. Is the mint mark explicitly listed, or is it a combined entry (both P and D)?

Return ONLY valid JSON using this schema:
{
  "book_title": "Program name detected from the checklist header",
  "programs_detected": ["string"],
  "page_count": integer,
  "pages": [{"page_index": 0, "page_type": "checklist_page", "mint_assigned": "varies",
              "mint_confidence": "high", "mint_reasoning": "...", "image_gcs_url": "",
              "slots_detected": integer}],
  "coin_slots": [
    {
      "page_index": 0,
      "year": "1999",
      "subject": "Delaware",
      "denomination": "Quarter",
      "program": "50 State Quarters",
      "mint": "P",
      "mint_uncertain": false,
      "present": true,
      "partially_visible": false,
      "slot_condition_note": ""
    }
  ],
  "analysis_notes": "",
  "mint_clarification_needed": false
}

IMPORTANT:
- If a checklist row lists the coin without a specific mint mark,
  create SEPARATE entries for both P and D mint with mint_uncertain:true
- If the checklist ONLY shows P mint entries, set those as mint:"P" with mint_uncertain:false
- Report ALL entries, marked or unmarked (set present:false for unmarked)
"""

        try:
            response = genai_client.models.generate_content(
                model=PRIMARY_MODEL,
                contents=file_parts + [genai_types.Part.from_text(text=checklist_prompt)],
                config=genai_types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                    max_output_tokens=65536,
                    thinking_config=genai_types.ThinkingConfig(thinking_budget=0),
                ),
            )
            try:
                ai_result = json.loads(response.text)
            except json.JSONDecodeError as je:
                print(f"[analyze_checklist] JSON parse error at char {je.pos}: {je.msg}")
                print(f"[analyze_checklist] Raw response tail: ...{response.text[-200:]}")
                raise HTTPException(
                    status_code=500,
                    detail=f"AI response was truncated or malformed: {je.msg} at position {je.pos}"
                )
        except HTTPException:
            raise
        except Exception as e:
            print(f"[analyze_checklist] Gemini error: {e}")
            raise HTTPException(status_code=500, detail=f"Checklist analysis failed: {e}")

        # Inject GCS URLs into page records
        for idx, page in enumerate(ai_result.get("pages", [])):
            if idx < len(gcs_urls):
                page["image_gcs_url"] = gcs_urls[idx]

    # ── Post-process: validate and enrich slots ──────────────────────────────
    if binder_title:
        ai_result["book_title"] = binder_title

    validated = _validate_and_enrich_slots(
        ai_result.get("coin_slots", []),
        ai_result.get("programs_detected", []),
    )

    present = [s for s in validated if s.get("present")]
    absent  = [s for s in validated if not s.get("present")]

    return {
        "status":            "success",
        "scan_uuid":         scan_uuid,
        "analysis_engine":   analysis_engine,       # "document_ai" | "gemini"
        "detected_format":   detected_format,        # "littleton" | "unknown" etc.
        "book_title":        ai_result.get("book_title", "Unknown Checklist"),
        "programs_detected": ai_result.get("programs_detected", []),
        "image_gcs_urls":    gcs_urls,
        "pages":             ai_result.get("pages", []),
        "coin_slots":        validated,
        "present_count":     len(present),
        "absent_count":      len(absent),
        "total_slots":       len(validated),
        "is_first_scan":     True,
        "new_coins":         present,
        "mint_clarification_needed": ai_result.get("mint_clarification_needed", False),
        "analysis_notes":    ai_result.get("analysis_notes", ""),
    }

class ConfirmBinderScanRequest(BaseModel):
    user_email:       str
    binder_doc_id:    str
    scan_uuid:        str
    book_title:       str
    storage_location: str          # Final user-confirmed storage location label
    purchase_cost:    Optional[str] = None
    purchase_date:    Optional[str] = None
    retailer:         Optional[str] = None
    personal_notes:   Optional[str] = None
    confirmed_coins:  list          # The user-confirmed subset of present coin_slots
    use_binder_image: bool = True   # If True, set image_url_obverse = binder page GCS URL
    primary_page_gcs_url: Optional[str] = None  # The main page image URL for the storage location


@app.post("/api/confirm_binder_scan")
async def confirm_binder_scan(request: ConfirmBinderScanRequest):
    """
    PHASE 1 — Confirmation endpoint.

    Takes the user-confirmed coin list from the Flutter review wizard
    and stages all coins into the review_queue for final commit.

    Key behaviors:
    - Sets Storage Location = request.storage_location on all coins
    - Sets image_url_obverse = the binder page GCS URL (if use_binder_image=True)
    - Performs duplicate detection: checks if same Year+Mint+Denomination already
      exists in coins collection with a DIFFERENT storage location — if so, returns
      that info for user confirmation rather than auto-creating a duplicate
    - Saves the confirmed state back to binder_scans/{binder_doc_id}.coin_slots
      (marks confirmed slots as having coinId references)
    """
    user_ref    = db.collection("users").document(request.user_email)
    queue_ref   = user_ref.collection("review_queue")
    coins_ref   = user_ref.collection("coins")
    binder_ref  = user_ref.collection("binder_scans").document(request.binder_doc_id)

    staged_count      = 0
    duplicate_prompts = []  # Coins that already exist elsewhere, needing user confirmation
    batch             = db.batch()

    for slot in request.confirmed_coins:
        year        = str(slot.get("year", ""))
        mint        = slot.get("mint", "")
        denomination = slot.get("denomination", "Quarter")
        subject     = slot.get("subject", "")
        program     = slot.get("program", "50 State Quarters")
        page_index  = slot.get("page_index", 0)

        # Determine the binder image URL for this coin's page
        coin_image_url = ""
        if request.use_binder_image and request.primary_page_gcs_url:
            coin_image_url = request.primary_page_gcs_url

        # ── Cross-location duplicate check ────────────────────────────────────
        # A coin is a duplicate ONLY if Year + Mint + Denomination match AND
        # it's stored in a DIFFERENT location. Same-location copies are allowed.
        try:
            existing = (
                coins_ref
                .where("Year",         "==", year)
                .where("Mint Mark",    "==", mint)
                .where("Denomination", "==", denomination)
                .get()
            )

            for existing_doc in existing:
                existing_data = existing_doc.to_dict()
                existing_location = existing_data.get("Storage Location", "")

                # Only flag if it's stored somewhere OTHER than this binder
                if (
                    existing_location and
                    existing_location.lower() != request.storage_location.lower()
                ):
                    duplicate_prompts.append({
                        "year":       year,
                        "mint":       mint,
                        "subject":    subject,
                        "denomination": denomination,
                        "existing_location": existing_location,
                        "new_location": request.storage_location,
                        "confirmation_message": (
                            f"Your {year}{mint} {subject} {denomination} is separate from "
                            f"the same coin stored in '{existing_location}', correct?"
                        ),
                    })
        except Exception as e:
            print(f"[confirm_binder_scan] Duplicate check warning for {year}{mint} {subject}: {e}")

        # ── Stage the coin in review_queue ────────────────────────────────────
        new_doc = {
            # Golden Schema fields
            "Year":                year,
            "Mint Mark":           mint,
            "Denomination":        denomination,
            "Program/Series":      program,
            "Theme/Subject":       subject,
            "Country":             "USA",
            "Condition":           slot.get("condition", "Ungraded"),
            "Strike Type":         "",
            "Holder Type":         "Binder",
            "Grading Service":     "",
            "Certification Number": "",
            "Metal Content":       "Cupro-Nickel Clad Copper",  # Standard for 1999-2009 quarters
            "Purchase Cost":       request.purchase_cost or "$0.00",
            "Purchase Date":       request.purchase_date or "",
            "Retailer/Website":    request.retailer or "",
            "Retailer Item No.":   "",
            "Retailer Invoice #":  "",
            "Variety":             slot.get("variant", ""),
            "Personal Notes I":    request.personal_notes or "",
            "Personal Reference #": "",
            "Storage Location":    request.storage_location,
            "Original Description from source": (
                f"Added via Binder Scan — {request.book_title}"
            ),

            # Image fields
            "image_url_obverse":   coin_image_url,    # Binder evidence photo
            "image_url_reverse":   "",

            # AI / valuation
            "AI Estimated Value":  "Pending",
            "Melt Value":          "N/A",
            "Is Silver":           False,

            # Internal tracking
            "source":              "Binder Scan",
            "source_file":         request.scan_uuid,
            "scan_uuid":           request.scan_uuid,           # For crop endpoint
            "binder_doc_id":       request.binder_doc_id,
            "binder_page_index":   page_index,
            "page_index":          page_index,                  # For crop endpoint
            "slot_bbox":           slot.get("slot_bbox", {}),   # For crop endpoint
            "deep_dive_status":    "PENDING",
            "created_at":          firestore.SERVER_TIMESTAMP,
            "confidence_score":    0.85,  # AI-identified, user-confirmed
        }

        doc_ref = queue_ref.document(str(uuid.uuid4()))
        batch.set(doc_ref, new_doc)
        staged_count += 1

        if staged_count % 400 == 0:  # Firestore batch limit is 500
            batch.commit()
            batch = db.batch()

    # Commit any remaining
    if staged_count % 400 != 0:
        batch.commit()

    # ── Update binder_scans doc to reflect confirmed state ────────────────────
    try:
        confirmed_keys = {
            f"{s.get('year')}|{s.get('subject')}|{s.get('mint')}"
            for s in request.confirmed_coins
        }
        binder_doc = binder_ref.get()
        if binder_doc.exists:
            updated_slots = []
            for slot in binder_doc.to_dict().get("coin_slots", []):
                slot_key = f"{slot.get('year')}|{slot.get('subject')}|{slot.get('mint')}"
                if slot_key in confirmed_keys:
                    slot["confirmed"] = True
                updated_slots.append(slot)
            binder_ref.update({
                "coin_slots":           updated_slots,
                "storage_location":     request.storage_location,
                "primary_image_url":    request.primary_page_gcs_url or "",
                "last_confirmed_date":  firestore.SERVER_TIMESTAMP,
            })
    except Exception as e:
        print(f"[confirm_binder_scan] Binder doc update warning: {e}")

    return {
        "status":            "success",
        "message":           f"Staged {staged_count} coins to Review Hub.",
        "staged_count":      staged_count,
        "duplicate_prompts": duplicate_prompts,
        "next_step":         "review_hub",
    }


@app.get("/api/binder_scans/{user_email}")
async def list_binder_scans(user_email: str):
    """
    Returns all binder_scan documents for a user.
    Used by the Storage Location viewer in My Collection to display
    the binder overview when a user clicks a Storage Location value.
    """
    try:
        docs = (
            db.collection("users")
              .document(user_email)
              .collection("binder_scans")
              .order_by("last_scan_date", direction=firestore.Query.DESCENDING)
              .get()
        )
        result = []
        for doc in docs:
            d = doc.to_dict()
            result.append({
                "id":              doc.id,
                "title":           d.get("title", "Unknown"),
                "storage_location": d.get("storage_location", d.get("title", "")),
                "present_count":   d.get("present_count", 0),
                "absent_count":    d.get("absent_count", 0),
                "total_slots":     d.get("total_slots", 0),
                "last_scan_date":  str(d.get("last_scan_date", "")),
                "primary_image_url": d.get("primary_image_url", ""),
                "image_gcs_urls":  d.get("image_gcs_urls", []),
                "programs":        d.get("programs", []),
            })
        return {"status": "success", "binder_scans": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/binder_scans/{user_email}/{binder_id}")
async def get_binder_detail(user_email: str, binder_id: str):
    """
    Returns the full detail of one binder scan, including all coin_slots.
    Used when a user clicks a Storage Location link in My Collection.
    """
    try:
        doc = (
            db.collection("users")
              .document(user_email)
              .collection("binder_scans")
              .document(binder_id)
              .get()
        )
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Binder scan not found.")
        d = doc.to_dict()
        return {
            "status":           "success",
            "id":               doc.id,
            "title":            d.get("title", ""),
            "storage_location": d.get("storage_location", ""),
            "programs":         d.get("programs", []),
            "pages":            d.get("pages", []),
            "coin_slots":       d.get("coin_slots", []),
            "image_gcs_urls":   d.get("image_gcs_urls", []),
            "primary_image_url": d.get("primary_image_url", ""),
            "present_count":    d.get("present_count", 0),
            "absent_count":     d.get("absent_count", 0),
            "total_slots":      d.get("total_slots", 0),
            "last_scan_date":   str(d.get("last_scan_date", "")),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  PCGS CERT LOOKUP — DIRECT API                                              ║
# ║  Calls api.pcgs.com/publicapi/coindetail/GetCoinFactsByCertNo/{certNo}      ║
# ║  using a bearer token stored in Firestore (config/pcgs → bearerToken).      ║
# ║                                                                              ║
# ║  ⚠️  Root cause of previous 404s: cert was passed as ?CertNo=X (query)     ║
# ║       instead of as a PATH parameter: /GetCoinFactsByCertNo/X               ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import requests as _requests

_PCGS_API_BASE = "https://api.pcgs.com/publicapi"

def _get_pcgs_token() -> Optional[str]:
    """Reads the PCGS bearer token from Firestore config/pcgs → bearerToken."""
    try:
        doc = db.collection("config").document("pcgs").get()
        token = doc.to_dict().get("bearerToken") if doc.exists else None
        return token or None
    except Exception as e:
        print(f"[PCGS] Could not read token from Firestore: {e}")
        return None

@app.get("/api/pcgs/cert/{cert_no}")
async def pcgs_cert_lookup(cert_no: str):
    """
    Looks up a PCGS certification number via the PCGS Public API.

    Endpoint: GET /publicapi/coindetail/GetCoinFactsByCertNo/{certNo}
              (certNo is a PATH parameter — not a query string)

    Bearer token is read from Firestore at: config/pcgs → bearerToken
    Stored there by admin via the app's Advanced token UI or directly in Firebase.
    """
    if not cert_no.isdigit() or not (6 <= len(cert_no) <= 9):
        raise HTTPException(status_code=400, detail="cert_no must be 6-9 digits.")

    # ── Fetch token ───────────────────────────────────────────────────────────
    token = _get_pcgs_token()
    if not token:
        raise HTTPException(
            status_code=503,
            detail="PCGS bearer token not configured. Add bearerToken to Firestore config/pcgs."
        )

    # ── Call PCGS API — cert as PATH param (not query string!) ───────────────
    url = f"{_PCGS_API_BASE}/coindetail/GetCoinFactsByCertNo/{cert_no}"
    params = {"retrieveAllData": "true"}
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    try:
        resp = _requests.get(url, params=params, headers=headers, timeout=15)
    except _requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="PCGS API timed out.")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Could not reach PCGS API: {e}")

    print(f"[PCGS Cert] cert={cert_no} status={resp.status_code} url={resp.url}")

    if resp.status_code == 401:
        raise HTTPException(status_code=401, detail="PCGS bearer token is invalid or expired. Generate a new one at pcgs.com/publicapi/documentation.")
    if resp.status_code == 429:
        raise HTTPException(status_code=429, detail="PCGS daily limit reached (1,000 calls/day). Try again tomorrow.")
    if resp.status_code == 404:
        return {"found": False, "certNo": cert_no}
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=f"PCGS API returned {resp.status_code}: {resp.text[:300]}")

    try:
        data = resp.json()
    except Exception:
        raise HTTPException(status_code=502, detail=f"PCGS returned non-JSON: {resp.text[:200]}")

    print(f"[PCGS Cert] raw response keys: {list(data.keys()) if isinstance(data, dict) else type(data).__name__}")

    # IsValidRequest=False means the cert exists in the DB but data retrieval failed
    if not data.get("IsValidRequest"):
        msg = data.get("ServerMessage", "Cert not found.")
        return {"found": False, "certNo": cert_no, "message": msg}

    # ── Normalise into our standard coinDetail shape ──────────────────────────
    coin_detail = {
        # Core identity
        "CertNo":       cert_no,
        "PCGSNo":       str(data.get("PCGSNo", "")),
        "CoinName":     data.get("Name", ""),
        "Grade":        data.get("Grade", ""),
        "Designation":  data.get("Designation", ""),
        # Date / mint
        "Year":         str(data.get("Year", "")),
        "MintMark":     data.get("MintMark", ""),
        "MintLocation": data.get("MintLocation", ""),
        # Physical
        "Denomination": data.get("Denomination", ""),
        "MetalContent": data.get("MetalContent", ""),
        "Country":      data.get("Country", ""),
        # Market / pop
        "PriceGuideValue": data.get("PriceGuideValue"),
        "Population":   str(data.get("Population", "")),
        "PopHigher":    str(data.get("PopHigher", "")),
        # Variety
        "MajorVariety": data.get("MajorVariety", ""),
        "MinorVariety": data.get("MinorVariety", ""),
        "DieVariety":   data.get("DieVariety", ""),
        "SeriesName":   data.get("SeriesName", ""),
        "Category":     data.get("Category", ""),
        # Authentication
        "IsNFCSecure":  data.get("IsNFCSecure", False),
        # Links
        "CoinFactsLink": data.get("CoinFactsLink", ""),
    }

    # Images (PCGS returns a list; take first obverse/reverse if present)
    images = data.get("Images") or []
    for img in images:
        if isinstance(img, dict):
            side = img.get("Side", "").lower()
            if side == "obverse" and "ObverseImageURL" not in coin_detail:
                coin_detail["ObverseImageURL"] = img.get("URL", "")
            elif side == "reverse" and "ReverseImageURL" not in coin_detail:
                coin_detail["ReverseImageURL"] = img.get("URL", "")

    grade_str = coin_detail["Grade"] or coin_detail["Designation"]
    print(f"[PCGS Cert] ✅ {coin_detail['CoinName']} | {grade_str} | NFC={coin_detail['IsNFCSecure']}")
    return {"found": True, "certNo": cert_no, "coinDetail": coin_detail}


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  AI PHOTO IDENTIFIER — POST /api/identify_coin_photo                        ║
# ║  Two-pass Gemini coin identification from user-uploaded obverse + reverse    ║
# ║  images. Identifies, grades, estimates value, detects errors/varieties.      ║
# ║  Saves coin + images to Firestore/GCS on confirmation.                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

PHOTO_ID_PASS1_PROMPT = """
You are a professional numismatist examining two coin images uploaded by a collector.
Image A and Image B are provided — the collector may have uploaded them in any order.

YOUR TASKS:
1. SIDE DETECTION: Determine which image is the OBVERSE (portrait/date side) and which is the REVERSE.
2. IDENTIFICATION: Identify the coin precisely — Year, Country, Denomination, Program/Series, Theme/Subject.
3. MINT MARK (critical): Examine the obverse extremely carefully for a mint mark letter.
   Common locations: below the date, near the portrait neck, near "IN GOD WE TRUST", along the lower rim.
   US Mint codes: P=Philadelphia, D=Denver, S=San Francisco, W=West Point, CC=Carson City, O=New Orleans.
   Report any visible letter, even faint. If genuinely absent, return "None (P)".
4. GRADE: Estimate the Sheldon scale grade (e.g. "G-4", "VF-30", "XF-45", "AU-55", "MS-63", "PR-65").
5. METAL COMPOSITION (apply these rules exactly):
   - Pre-1965 US dimes, quarters, halves = 90% Silver, 10% Copper
   - Half dollars 1965-1970 = 40% Silver, 60% Copper
   - Morgan/Peace Dollars, Walking Liberty, Franklin Half, Mercury Dime = 90% Silver
   - Indian Head $5 Half Eagle ($5 gold), $10 Eagle, $20 Double Eagle = 90% Gold, 10% Copper
   - American Gold Eagle = 91.67% Gold  |  American Silver Eagle = 99.9% Silver
   - Gold Buffalo, Platinum Eagle = 99.99% respective metal
   - Modern clad (post-1964 quarters, post-1970 halves) = NO silver, cupro-nickel
   - Set is_silver=true/false and is_gold=true/false accordingly.
6. NUMISMATIC REPORT: Write 2-4 sentences on the coin's historical significance and collectibility.
7. VARIETY NOTES: Note any obvious doubled dies, RPMs, off-center strikes, or other mint anomalies.

Return ONLY valid JSON — no markdown fences, no commentary:
{
  "obverse_image": "A" or "B",
  "year": integer,
  "country": string,
  "denomination": string,
  "program_series": string,
  "theme_subject": string,
  "mint_mark": string,
  "grade": string,
  "is_silver": boolean,
  "is_gold": boolean,
  "metal_content": string,
  "report": string,
  "variety_notes": string,
  "confidence": "HIGH", "MEDIUM", or "LOW"
}
"""

PHOTO_ID_PASS2_PROMPT_TEMPLATE = """
You are a senior grading expert performing a VERIFICATION PASS on a coin already identified as:
  Year: {year} | Country: {country} | Denomination: {denomination}
  Program/Series: {program_series} | Mint Mark: {mint_mark}
  Initial Grade: {grade} | Metal: {metal_content}

You are looking at the same two images (A and B) again.

YOUR TASKS:
1. VERIFY the identification — correct year, denomination, or series if wrong.
2. REFINE the grade to a precise Sheldon number (e.g. "VF-30", "MS-63", "PR-65").
3. CHECK for mint errors: doubled dies, repunched mint marks (RPM), off-center strikes,
   die cracks, cuds, lamination errors, rotated dies, or any other varieties.
4. ESTIMATE retail value in USD based on current market for this grade.
5. Write a brief condition note describing the coin's surfaces and strike quality.

Return ONLY valid JSON:
{{
  "identification_confirmed": boolean,
  "corrected_year": integer or null,
  "corrected_denomination": string or null,
  "corrected_series": string or null,
  "refined_grade": string,
  "errors_detected": [string],
  "estimated_value_usd": string,
  "condition_notes": string,
  "confidence": "HIGH", "MEDIUM", or "LOW"
}}
"""


@app.post("/api/identify_coin_photo")
async def identify_coin_photo(
    user_email:    str        = Form(...),
    image_a:       UploadFile = File(...),
    image_b:       UploadFile = File(...),
    save_to_collection: bool  = Form(False),
    # Optional user overrides sent from the review screen
    override_year:    Optional[str] = Form(None),
    override_denom:   Optional[str] = Form(None),
    override_series:  Optional[str] = Form(None),
    override_theme:   Optional[str] = Form(None),
    override_mint:    Optional[str] = Form(None),
    override_grade:   Optional[str] = Form(None),
    override_metal:   Optional[str] = Form(None),
    override_cost:    Optional[str] = Form(None),
    override_storage: Optional[str] = Form(None),
    override_notes:   Optional[str] = Form(None),
):
    """
    Two-pass Gemini AI coin identification from obverse + reverse photos.

    Pass 1  — Identification: determines which image is obverse/reverse,
              identifies year/denomination/series/mint mark/grade/metal.
    Pass 2  — Verification:   refines grade, checks for errors/varieties,
              estimates retail value, confirms or corrects identification.

    When save_to_collection=True, the identified coin (with any user overrides
    applied) is written directly to Firestore under users/{user_email}/coins
    and both images are uploaded to GCS.

    Returns the full coin document as JSON whether or not it was saved.
    """
    print(f"[identify_coin_photo] user={user_email} save={save_to_collection}")

    # ── 1. Read image bytes ───────────────────────────────────────────────────
    bytes_a      = await image_a.read()
    bytes_b      = await image_b.read()
    mime_a       = image_a.content_type or "image/jpeg"
    mime_b       = image_b.content_type or "image/jpeg"

    part_a_img   = genai_types.Part.from_bytes(data=bytes_a, mime_type=mime_a)
    part_b_img   = genai_types.Part.from_bytes(data=bytes_b, mime_type=mime_b)
    label_a      = genai_types.Part.from_text(text="[Image A]")
    label_b      = genai_types.Part.from_text(text="[Image B]")

    # ── 2. PASS 1 — Identification ────────────────────────────────────────────
    try:
        resp1 = genai_client.models.generate_content(
            model=PRIMARY_MODEL,
            contents=[
                label_a, part_a_img,
                label_b, part_b_img,
                genai_types.Part.from_text(text=PHOTO_ID_PASS1_PROMPT),
            ],
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
                thinking_config=genai_types.ThinkingConfig(thinking_budget=0),
            ),
        )
        raw1 = resp1.text.strip()
        if raw1.startswith("```"):
            raw1 = raw1.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        pass1: dict = json.loads(raw1)
        print(f"[identify_coin_photo] Pass 1 ✅ {pass1.get('year')} {pass1.get('denomination')} conf={pass1.get('confidence')}")
    except Exception as e:
        print(f"[identify_coin_photo] Pass 1 error: {e}")
        raise HTTPException(status_code=500, detail=f"AI identification failed: {e}")

    # ── 3. PASS 2 — Verification ──────────────────────────────────────────────
    pass2: dict = {}
    try:
        pass2_prompt = PHOTO_ID_PASS2_PROMPT_TEMPLATE.format(
            year          = pass1.get("year", ""),
            country       = pass1.get("country", ""),
            denomination  = pass1.get("denomination", ""),
            program_series= pass1.get("program_series", ""),
            mint_mark     = pass1.get("mint_mark", ""),
            grade         = pass1.get("grade", ""),
            metal_content = pass1.get("metal_content", ""),
        )
        resp2 = genai_client.models.generate_content(
            model=PRIMARY_MODEL,
            contents=[
                label_a, part_a_img,
                label_b, part_b_img,
                genai_types.Part.from_text(text=pass2_prompt),
            ],
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
                thinking_config=genai_types.ThinkingConfig(thinking_budget=0),
            ),
        )
        raw2 = resp2.text.strip()
        if raw2.startswith("```"):
            raw2 = raw2.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        pass2 = json.loads(raw2)
        print(f"[identify_coin_photo] Pass 2 ✅ grade={pass2.get('refined_grade')} val={pass2.get('estimated_value_usd')}")
    except Exception as e:
        # Non-fatal — continue with Pass 1 results only
        print(f"[identify_coin_photo] Pass 2 error (non-fatal): {e}")

    # ── 4. Merge Pass 1 + Pass 2 results ─────────────────────────────────────
    final_year   = str(pass2.get("corrected_year")  or pass1.get("year",  ""))
    final_denom  = pass2.get("corrected_denomination") or pass1.get("denomination", "")
    final_series = pass2.get("corrected_series")    or pass1.get("program_series", "")
    final_grade  = pass2.get("refined_grade")       or pass1.get("grade", "")
    final_conf   = pass2.get("confidence")          or pass1.get("confidence", "")
    errors       = pass2.get("errors_detected", []) or []
    variety_str  = "; ".join(errors) if errors else pass1.get("variety_notes", "")
    est_value    = pass2.get("estimated_value_usd", "Pending")
    cond_notes   = pass2.get("condition_notes", "")

    full_report  = pass1.get("report", "")
    if cond_notes:
        full_report += f"\n\nCondition: {cond_notes}"
    if errors:
        full_report += f"\n\nErrors/Varieties: {variety_str}"
    full_report += f"\n\n[AI Confidence: {final_conf}]"

    # Determine which image is obverse vs reverse
    obverse_is_a = str(pass1.get("obverse_image", "A")).upper() == "A"
    obv_bytes    = bytes_a if obverse_is_a else bytes_b
    rev_bytes    = bytes_b if obverse_is_a else bytes_a
    obv_mime     = mime_a  if obverse_is_a else mime_b
    rev_mime     = mime_b  if obverse_is_a else mime_a

    # Apply user overrides (from review screen)
    ai_coin = {
        "Year":           override_year    or final_year,
        "Country":        pass1.get("country", "USA"),
        "Denomination":   override_denom   or final_denom,
        "Program/Series": override_series  or final_series,
        "Theme/Subject":  override_theme   or pass1.get("theme_subject", ""),
        "Mint Mark":      override_mint    or pass1.get("mint_mark", ""),
        "Condition":      override_grade   or final_grade,
        "Metal Content":  override_metal   or pass1.get("metal_content", ""),
        "Variety":        variety_str,
        "AI Estimated Value": est_value,
        "Numismatic Report":  full_report,
        "Cost":           override_cost    or "$0.00",
        "Storage Location": override_storage or "",
        "Personal Notes": override_notes   or "",
        "Quantity":       1,
        "ai_confidence":  final_conf,
        "is_silver":      pass1.get("is_silver", False),
        "is_gold":        pass1.get("is_gold",   False),
        "source":         "AI Photo Identifier",
        "deep_dive_status": "PENDING",
    }

    # ── 5. Optionally save to Firestore + GCS ─────────────────────────────────
    coin_id      = str(uuid.uuid4())
    gcs_obv_uri  = ""
    gcs_rev_uri  = ""
    obv_b64      = ""
    rev_b64      = ""

    if save_to_collection:
        ts = int(__import__("time").time())
        try:
            gcs_obv_uri = _upload_to_gcs(
                obv_bytes,
                f"users/{user_email}/photo_id/{coin_id}_obverse_{ts}.jpg",
                obv_mime,
            )
            gcs_rev_uri = _upload_to_gcs(
                rev_bytes,
                f"users/{user_email}/photo_id/{coin_id}_reverse_{ts}.jpg",
                rev_mime,
            )
        except Exception as e:
            print(f"[identify_coin_photo] GCS upload warning: {e}")

        # Build base64 thumbnails for immediate Flutter display
        obv_b64 = f"data:{obv_mime};base64," + base64.b64encode(obv_bytes).decode()
        rev_b64 = f"data:{rev_mime};base64," + base64.b64encode(rev_bytes).decode()

        coin_doc = {
            **ai_coin,
            "id":                    coin_id,
            "imageUrlObverse":       obv_b64,
            "imageUrlReverse":       rev_b64,
            "imageUrlObverse_gcs":   gcs_obv_uri,
            "imageUrlReverse_gcs":   gcs_rev_uri,
            "Added":                 firestore.SERVER_TIMESTAMP,
        }

        db.collection(f"users/{user_email}/coins").document(coin_id).set(coin_doc)
        print(f"[identify_coin_photo] ✅ Saved coin {coin_id} for {user_email}")
    else:
        # Preview mode — return b64 images for the Flutter review screen
        obv_b64 = f"data:{obv_mime};base64," + base64.b64encode(obv_bytes).decode()
        rev_b64 = f"data:{rev_mime};base64," + base64.b64encode(rev_bytes).decode()

    return {
        "coin_id":        coin_id,
        "saved":          save_to_collection,
        "coin":           ai_coin,
        "obverse_b64":    obv_b64,
        "reverse_b64":    rev_b64,
        "gcs_obverse":    gcs_obv_uri,
        "gcs_reverse":    gcs_rev_uri,
    }


# ─── Text-Only Coin Valuation (Batch Estimator) ───────────────────────────────

class TextValuationRequest(BaseModel):
    year:           str
    denomination:   str
    mint_mark:      Optional[str] = ""
    condition:      Optional[str] = ""
    program_series: Optional[str] = ""
    metal_content:  Optional[str] = ""
    country:        Optional[str] = "USA"

TEXT_VALUATION_PROMPT = """\
You are a professional coin dealer with 30+ years experience pricing US and world coins.

A user has a coin with these details:
  Year:          {year}
  Denomination:  {denomination}
  Mint Mark:     {mint_mark}
  Grade/Condition: {condition}
  Program/Series:  {program_series}
  Metal Content:   {metal_content}
  Country:         {country}

Estimate the current retail market value range for this coin.
Return ONLY valid JSON with exactly these fields:
{{
  "estimated_value": "string — a price RANGE in USD, e.g. '$15 – $35' or '$1,200 – $1,800'. Never a single point value.",
  "confidence": "HIGH, MEDIUM, or LOW",
  "basis": "one sentence explaining your estimate (grade, series, metal content, demand)"
}}

Rules:
- Always return a RANGE (low – high), never a single number.
- If grade/condition is unknown, widen the range accordingly.
- If the coin is common and low-value, '$1 – $3' is a valid answer.
- If you cannot estimate (unknown coin, insufficient data), return estimated_value: 'Pending' and confidence: 'LOW'.
- Do NOT add any text outside the JSON object.
"""

@app.post("/api/estimate_value_text")
async def estimate_value_text(request: TextValuationRequest):
    """
    Text-only coin value estimation — no photos required.

    Used by the Flutter BatchValuationService to estimate values for coins
    imported via CSV, Excel, or PDF invoice that have no photos attached.

    Always returns a PRICE RANGE (not a point value) since condition cannot
    be visually confirmed without photos.  Sets needs_photo=True so the UI
    can prompt the user to upload images for a more precise estimate.
    """
    prompt = TEXT_VALUATION_PROMPT.format(
        year           = request.year           or "Unknown",
        denomination   = request.denomination   or "Unknown",
        mint_mark      = request.mint_mark      or "None",
        condition      = request.condition      or "Unknown",
        program_series = request.program_series or "Unknown",
        metal_content  = request.metal_content  or "Unknown",
        country        = request.country        or "USA",
    )
    try:
        resp = genai_client.models.generate_content(
            model=PRIMARY_MODEL,
            contents=[genai_types.Part.from_text(text=prompt)],
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
                thinking_config=genai_types.ThinkingConfig(thinking_budget=0),
            ),
        )
        raw = resp.text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        result: dict = json.loads(raw)

        estimated = result.get("estimated_value", "Pending")
        confidence = result.get("confidence", "LOW")
        basis      = result.get("basis", "")

        print(f"[estimate_value_text] {request.year} {request.denomination} "
              f"{request.mint_mark} → {estimated} ({confidence})")

        return {
            "estimated_value": estimated,
            "confidence":      confidence,
            "basis":           basis,
            "needs_photo":     True,   # always — text estimate cannot confirm grade visually
            "source":          "text_estimator",
        }
    except Exception as e:
        print(f"[estimate_value_text] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Valuation failed: {e}")



# ═══════════════════════════════════════════════════════════════════════════════
# BULK IMPORT & PAPER TRAIL  (Add Coins — unified tab)
# ═══════════════════════════════════════════════════════════════════════════════
#
# Three-step flow:
#   1. POST /api/import/start        → create session, return GCS signed upload URLs
#   2. Browser uploads files directly to GCS (no server in the loop)
#   3. POST /api/import/process      → orchestrate AI processing of all files
#      GET  /api/import/status/{id}  → live progress polling
#
# Paper Trail:
#   GET  /api/receipts/{email}                    → all receipts for a user
#   GET  /api/receipts/{email}/{id}/view_url      → fresh signed URL for original PDF
# ───────────────────────────────────────────────────────────────────────────────

import asyncio
import hashlib
import threading

IMPORT_BUCKET = USER_CONTENT_BUCKET  # reuse the existing bucket

# ── File type classifier ──────────────────────────────────────────────────────

def _classify_file(filename: str, first_bytes: bytes = b"") -> str:
    """Return 'spreadsheet' | 'invoice' | 'image' | 'other'."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext in ("xlsx", "xls", "csv", "ods"):
        return "spreadsheet"
    if ext == "pdf" or first_bytes[:4] == b"%PDF":
        return "invoice"
    if ext in ("jpg", "jpeg", "png", "webp", "heic", "bmp", "tiff", "tif"):
        return "image"
    return "other"


# ── Duplicate detection ───────────────────────────────────────────────────────

def _score_duplicate(new_coin: dict, existing_coin: dict) -> float:
    """
    Return a 0.0–1.0 duplicate confidence score.
    >= 0.90  → Strong duplicate (flag, don't add)
    0.60–0.89 → Possible duplicate (flag with warning, still add)
    < 0.60   → Unique
    """
    score = 0.0
    def _norm(v):
        return str(v or "").strip().lower()

    if _norm(new_coin.get("Program/Series")) == _norm(existing_coin.get("Program/Series")) \
            and _norm(new_coin.get("Program/Series")):
        score += 0.40
    if _norm(new_coin.get("Year")) == _norm(existing_coin.get("Year")) \
            and _norm(new_coin.get("Year")):
        score += 0.30
    if _norm(new_coin.get("Mint Mark")) == _norm(existing_coin.get("Mint Mark")):
        score += 0.10
    if _norm(new_coin.get("Condition")) == _norm(existing_coin.get("Condition")) \
            and _norm(new_coin.get("Condition")):
        score += 0.10
    # Purchase date + cost exact match adds a lot of confidence
    if _norm(new_coin.get("Purchase Date")) == _norm(existing_coin.get("Purchase Date")) \
            and _norm(new_coin.get("Purchase Date")):
        score += 0.05
    if _norm(new_coin.get("Cost")) == _norm(existing_coin.get("Cost")) \
            and _norm(new_coin.get("Cost")):
        score += 0.05
    return min(score, 1.0)


def _run_duplicate_sweep(user_email: str, session_id: str, new_coin_ids: list[str]) -> dict:
    """
    Compare every coin added in this session against the user's existing
    collection + review_queue (excluding coins in this very session).
    Updates the session doc with duplicate flags. Returns summary dict.
    """
    if not new_coin_ids:
        return {"strong": 0, "possible": 0}

    # Load existing coins (collection + review_queue minus this session)
    existing = []
    for coll_name in ("collection", "review_queue"):
        docs = db.collection("users").document(user_email).collection(coll_name)\
                 .where("import_session_id", "!=", session_id)\
                 .limit(2000).stream()
        for d in docs:
            existing.append((d.id, coll_name, d.to_dict()))

    strong_count = 0
    possible_count = 0
    flags = []

    session_ref = db.collection("users").document(user_email)\
                    .collection("import_sessions").document(session_id)

    for coin_id in new_coin_ids:
        # Load the new coin
        coin_doc = db.collection("users").document(user_email)\
                     .collection("review_queue").document(coin_id).get()
        if not coin_doc.exists:
            continue
        new_coin = coin_doc.to_dict()

        best_score = 0.0
        best_match = None
        for ex_id, ex_coll, ex_data in existing:
            s = _score_duplicate(new_coin, ex_data)
            if s > best_score:
                best_score = s
                best_match = (ex_id, ex_coll, ex_data)

        if best_score >= 0.90:
            strong_count += 1
            flags.append({
                "new_coin_id": coin_id,
                "match_id": best_match[0] if best_match else None,
                "match_collection": best_match[1] if best_match else None,
                "score": best_score,
                "level": "strong",
            })
            # Tag the new coin record
            db.collection("users").document(user_email)\
              .collection("review_queue").document(coin_id)\
              .update({"duplicate_flag": "strong", "duplicate_score": best_score})

        elif best_score >= 0.60:
            possible_count += 1
            flags.append({
                "new_coin_id": coin_id,
                "match_id": best_match[0] if best_match else None,
                "match_collection": best_match[1] if best_match else None,
                "score": best_score,
                "level": "possible",
            })
            db.collection("users").document(user_email)\
              .collection("review_queue").document(coin_id)\
              .update({"duplicate_flag": "possible", "duplicate_score": best_score})

    # Write flags to session
    session_ref.update({"duplicate_flags": flags})
    return {"strong": strong_count, "possible": possible_count}


# ── Receipt → Coin linker ─────────────────────────────────────────────────────

def _link_receipts_to_coins(user_email: str, session_id: str) -> dict:
    """
    After all files are processed, attempt to link each invoice line item
    to a coin record added in this session.

    Match tiers:
      EXACT  — retailer + invoice# + item# all agree → auto-link
      STRONG — year + mint + series all agree         → auto-link
      PARTIAL — series agrees, year/mint unclear      → AI suggestion (not auto-linked)
      NONE   — mark as unlinked_item
    """
    # Load all receipts for this session
    receipts = list(
        db.collection("users").document(user_email).collection("receipts")
          .where("session_id", "==", session_id).stream()
    )
    # Load all coins added in this session
    coins = list(
        db.collection("users").document(user_email).collection("review_queue")
          .where("import_session_id", "==", session_id).stream()
    )
    coin_data = [(c.id, c.to_dict()) for c in coins]

    linked_total = 0
    unlinked_total = 0

    for rec_snap in receipts:
        rec_id = rec_snap.id
        rec = rec_snap.to_dict()
        line_items = rec.get("line_items", [])
        if not line_items:
            continue

        linked_coin_ids = []
        unlinked_items = []

        for item in line_items:
            item_type = str(item.get("item_type", "coin")).lower()
            if item_type not in ("coin", "paper_currency", "medal", ""):
                unlinked_items.append(item)
                continue

            matched_coin_id = None
            match_tier = "none"

            retailer = str(rec.get("retailer", "")).lower().strip()
            inv_no   = str(rec.get("invoice_number", "")).lower().strip()
            item_no  = str(item.get("Retailer Item No.", "")).lower().strip()
            item_yr  = str(item.get("Year", "")).strip()
            item_mm  = str(item.get("Mint Mark", "")).strip().upper()
            item_ser = str(item.get("Program/Series", "") or item.get("Denomination", "")).lower().strip()

            for c_id, c_data in coin_data:
                c_retailer = str(c_data.get("Retailer Name", "")).lower().strip()
                c_inv      = str(c_data.get("Retailer Invoice #", "")).lower().strip()
                c_item_no  = str(c_data.get("Retailer Item No.", "")).lower().strip()
                c_yr       = str(c_data.get("Year", "")).strip()
                c_mm       = str(c_data.get("Mint Mark", "")).strip().upper()
                c_ser      = str(c_data.get("Program/Series", "")).lower().strip()

                # EXACT match
                if inv_no and c_inv == inv_no and retailer and c_retailer == retailer \
                        and item_no and c_item_no == item_no:
                    matched_coin_id = c_id
                    match_tier = "exact"
                    break

                # STRONG match
                if item_yr and c_yr == item_yr \
                        and c_mm == item_mm \
                        and item_ser and c_ser and item_ser in c_ser:
                    matched_coin_id = c_id
                    match_tier = "strong"
                    break

            if matched_coin_id:
                linked_coin_ids.append(matched_coin_id)
                linked_total += 1
                # Write paper_trail back to the coin record
                purchase_date = (
                    item.get("Purchase Date") or
                    item.get("Invoice Date") or
                    rec.get("invoice_date") or ""
                )
                purchase_price_raw = (
                    item.get("Purchase Cost") or
                    item.get("Cost") or
                    item.get("price") or "0"
                )
                try:
                    purchase_price = float(
                        str(purchase_price_raw).replace("$", "").replace(",", "").strip()
                    )
                except Exception:
                    purchase_price = 0.0

                db.collection("users").document(user_email)\
                  .collection("review_queue").document(matched_coin_id)\
                  .update({
                      "paper_trail": {
                          "receipt_id":       rec_id,
                          "receipt_filename": rec.get("original_filename", ""),
                          "retailer":         rec.get("retailer", ""),
                          "purchase_date":    purchase_date,
                          "purchase_price":   purchase_price,
                          "gcs_path":         rec.get("gcs_path", ""),
                          "match_tier":       match_tier,
                      },
                      "Purchase Date": purchase_date,
                  })
                # Also mark the line item as linked
                item["linked_coin_id"] = matched_coin_id
                item["match_tier"] = match_tier
            else:
                # Partial match suggestion (series only) — leave for user
                item["linked_coin_id"] = None
                item["match_tier"] = "none"
                unlinked_items.append(item)
                unlinked_total += 1

        # Update receipt with links
        db.collection("users").document(user_email).collection("receipts")\
          .document(rec_id).update({
              "linked_coin_ids": linked_coin_ids,
              "unlinked_items":  unlinked_items,
              "line_items":      line_items,
          })

    return {"linked": linked_total, "unlinked": unlinked_total}


# ── Helper: save original file to GCS (receipts/images) ──────────────────────

def _save_to_gcs(user_email: str, session_id: str, filename: str,
                 data: bytes, file_type: str) -> str:
    """
    Upload raw bytes to GCS under the user's import session path.
    Returns the gs:// path.
    """
    bucket = gcs_client.bucket(IMPORT_BUCKET)
    safe_name = filename.replace(" ", "_")
    blob_path = f"{user_email}/imports/{session_id}/raw/{safe_name}"
    blob = bucket.blob(blob_path)
    mime_map = {
        "invoice": "application/pdf",
        "image":   "image/jpeg",
        "spreadsheet": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }
    blob.upload_from_string(data, content_type=mime_map.get(file_type, "application/octet-stream"))
    return f"gs://{IMPORT_BUCKET}/{blob_path}"


# ── POST /api/import/start ─────────────────────────────────────────────────────

class ImportStartRequest(BaseModel):
    user_email:    str
    session_id:    str
    file_manifest: list[dict]   # [{name, size, mime}]

@app.post("/api/import/start")
def import_start(req: ImportStartRequest):
    """
    Create a Firestore session document and return one GCS signed upload URL
    per file. The browser uploads directly to GCS — no data passes through
    Cloud Run, keeping large batches fast.
    """
    session_ref = db.collection("users").document(req.user_email)\
                    .collection("import_sessions").document(req.session_id)
    session_ref.set({
        "started_at":   firestore.SERVER_TIMESTAMP,
        "status":       "uploading",
        "total_files":  len(req.file_manifest),
        "processed_files": 0,
        "per_file":     [
            {"name": f["name"], "type": _classify_file(f["name"]), "status": "pending"}
            for f in req.file_manifest
        ],
        "summary": {
            "coins_identified":   0,
            "receipts_parsed":    0,
            "duplicates_flagged": 0,
            "total_purchase_value": 0.0,
            "unlinked_receipts":  0,
        },
    })

    # Generate one signed URL per file (15-min write window)
    bucket = gcs_client.bucket(IMPORT_BUCKET)
    signed_urls = []
    for f in req.file_manifest:
        safe_name = f["name"].replace(" ", "_")
        blob_path = f"{req.user_email}/imports/{req.session_id}/raw/{safe_name}"
        blob = bucket.blob(blob_path)
        url = blob.generate_signed_url(
            version="v4",
            expiration=900,       # 15 minutes
            method="PUT",
            content_type=f.get("mime", "application/octet-stream"),
        )
        signed_urls.append({"name": f["name"], "upload_url": url, "gcs_path": f"gs://{IMPORT_BUCKET}/{blob_path}"})

    return {"status": "ok", "session_id": req.session_id, "files": signed_urls}


# ── GET /api/import/status/{session_id} ───────────────────────────────────────

@app.get("/api/import/status/{session_id}")
def import_status(session_id: str, user_email: str):
    """Live progress polling — called every 2 s by the browser progress bar."""
    doc = db.collection("users").document(user_email)\
            .collection("import_sessions").document(session_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Session not found")
    data = doc.to_dict()
    # Strip server timestamps for JSON serialisation
    data.pop("started_at", None)
    return data


# ── POST /api/import/process ───────────────────────────────────────────────────

class ImportProcessRequest(BaseModel):
    user_email: str
    session_id: str
    mask_pii:   bool = False

@app.post("/api/import/process")
async def import_process(req: ImportProcessRequest):
    """
    Orchestrates AI processing of every file in the session.
    Files must already be in GCS (uploaded by the browser via signed URLs).

    Processing runs synchronously here (Cloud Run timeout = 3600 s).
    For very large sessions the client polls /api/import/status for progress.
    """
    user_email = req.user_email
    session_id = req.session_id
    mask_pii   = req.mask_pii

    session_ref = db.collection("users").document(user_email)\
                    .collection("import_sessions").document(session_id)
    session_snap = session_ref.get()
    if not session_snap.exists:
        raise HTTPException(status_code=404, detail="Session not found")

    session_ref.update({"status": "processing"})
    per_file: list[dict] = session_snap.to_dict().get("per_file", [])

    bucket = gcs_client.bucket(IMPORT_BUCKET)
    summary = {
        "coins_identified":   0,
        "receipts_parsed":    0,
        "total_purchase_value": 0.0,
        "unlinked_receipts":  0,
    }
    new_coin_ids: list[str] = []

    # ── Pre-compute obverse/reverse image pairs ───────────────────────────────
    # Group image-type files by their filename stem (minus suffix keywords).
    # e.g. '1935_penny_obv.jpg' and '1935_penny_rev.jpg' share stem '1935_penny'.
    _IMG_SUFFIXES = (
        "_obv", "_rev", "_obverse", "_reverse", "_front", "_back",
        "_a", "_b", "_1", "_2",
    )
    def _img_stem(name: str) -> str:
        """Return filename stem with common obv/rev suffixes stripped."""
        base = name.rsplit(".", 1)[0].lower().rstrip("_")
        for sfx in _IMG_SUFFIXES:
            if base.endswith(sfx):
                return base[:-len(sfx)].rstrip("_")
        return base

    # Map: stem -> [per_file indices]
    _img_stem_map: dict[str, list[int]] = {}
    for _i, _fm in enumerate(per_file):
        if (_fm.get("type") or _classify_file(_fm["name"])) == "image":
            _s = _img_stem(_fm["name"])
            _img_stem_map.setdefault(_s, []).append(_i)
    # Set of indices already processed as part of a pair
    _paired_idx_done: set[int] = set()
    # ──────────────────────────────────────────────────────────────────────────

    for idx, file_meta in enumerate(per_file):
        fname     = file_meta["name"]
        ftype     = file_meta.get("type") or _classify_file(fname)
        safe_name = fname.replace(" ", "_")
        blob_path = f"{user_email}/imports/{session_id}/raw/{safe_name}"
        blob      = bucket.blob(blob_path)
        gcs_path  = f"gs://{IMPORT_BUCKET}/{blob_path}"

        # Update per-file status to "processing"
        per_file[idx]["status"] = "processing"
        session_ref.update({"per_file": per_file, "processed_files": idx})

        try:
            file_bytes = blob.download_as_bytes()
        except Exception as e:
            per_file[idx]["status"] = "error"
            per_file[idx]["error"]  = str(e)
            session_ref.update({"per_file": per_file})
            continue

        result_meta: dict = {}

        # ── Route by file type ─────────────────────────────────────────────────
        if ftype == "spreadsheet":
            try:
                ext = fname.rsplit(".", 1)[-1].lower() if "." in fname else ""
                df  = pd.read_csv(io.BytesIO(file_bytes)) if ext == "csv" \
                      else pd.read_excel(io.BytesIO(file_bytes))

                # Reuse existing column-mapping logic
                headers = list(df.columns)
                mapping_prompt = f"""You are an expert data migration agent for a numismatic app.
Golden Schema keys: ["Program/Series","Theme/Subject","Year","Country","Denomination",
"Mint Mark","Condition","Cost","Purchase Date","Retailer Name","Retailer Invoice #",
"Retailer Item No.","Storage Location","Notes"]
User spreadsheet headers: {headers}
Map each user header to the closest schema key.
Output ONLY a raw JSON object: {{"user_header": "schema_key"}}"""

                resp = genai_client.models.generate_content(
                    model=PRIMARY_MODEL,
                    contents=[genai_types.Part.from_text(text=mapping_prompt)],
                    config=genai_types.GenerateContentConfig(response_mime_type="application/json"),
                )
                mapping: dict = json.loads(resp.text)

                col_ref  = db.collection("users").document(user_email).collection("review_queue")
                batch    = db.batch()
                count    = 0
                for _, row in df.iterrows():
                    doc = {
                        "Program/Series": "", "Year": "", "Mint Mark": "",
                        "Denomination": "", "Condition": "Ungraded",
                        "Cost": "", "Purchase Date": "", "Country": "United States",
                        "deep_dive_status": "PENDING",
                        "upload_method":    "spreadsheet_import",
                        "source_file":      fname,
                        "import_session_id": session_id,
                        "source_type":      "spreadsheet",
                        "created_at":       firestore.SERVER_TIMESTAMP,
                    }
                    for uc, sc in mapping.items():
                        if uc in row and pd.notna(row[uc]):
                            doc[sc] = str(row[uc]).strip()
                    doc_ref = col_ref.document(str(uuid.uuid4()))
                    batch.set(doc_ref, doc)
                    new_coin_ids.append(doc_ref.id)
                    count += 1
                    if count % 490 == 0:
                        batch.commit()
                        batch = db.batch()
                if count % 490 != 0:
                    batch.commit()

                summary["coins_identified"] += count
                result_meta = {"coins_added": count}
                per_file[idx]["status"]      = "done"
                per_file[idx]["coins_added"] = count

            except Exception as e:
                per_file[idx]["status"] = "error"
                per_file[idx]["error"]  = str(e)
                print(f"[bulk_import] spreadsheet error ({fname}): {e}")

        elif ftype == "invoice":
            try:
                # Reuse existing process_invoice Gemini logic (inline)
                ext = fname.rsplit(".", 1)[-1].lower() if "." in fname else ""
                mime_map_local = {"pdf": "application/pdf", "png": "image/png",
                                  "jpg": "image/jpeg", "jpeg": "image/jpeg"}
                mime_type = mime_map_local.get(ext, "application/pdf")
                if file_bytes[:4] == b"%PDF":
                    mime_type = "application/pdf"

                pdf_part = genai_types.Part.from_bytes(data=file_bytes, mime_type=mime_type)

                pii_rule = ""
                if mask_pii:
                    pii_rule = """
                    CRITICAL SECURITY RULE (PII REDACTION):
                    The user has requested to mask personal identifiable information (PII).
                    Do NOT extract or include any customer name, customer phone number, customer email, customer shipping/billing address, credit card numbers, or other sensitive personal info in any extracted fields (e.g. in the "Personal Notes I", "Original Description from source", or "Retailer Name" fields). If these details are present, replace them with '[REDACTED]'.
                    """

                extraction_prompt = f"""You are an expert numismatic accountant.
Extract every purchasable line item from this invoice/receipt.
Return JSON array. Each object must include:
{{
  "item_type": "coin|set|stamp|supply|paper_currency|medal|other",
  "Program/Series": "...", "Year": "...", "Mint Mark": "...",
  "Denomination": "...", "Condition": "...",
  "Purchase Cost": "$0.00", "Purchase Date": "YYYY-MM-DD or as printed",
  "Retailer Name": "...", "Retailer Invoice #": "...", "Retailer Item No.": "..."
}}
Ignore shipping, tax, subtotal rows.
{pii_rule}"""

                try:
                    response = genai_client.models.generate_content(
                        model=PRO_MODEL,
                        contents=[pdf_part, genai_types.Part.from_text(text=extraction_prompt)],
                        config=genai_types.GenerateContentConfig(response_mime_type="application/json"),
                    )
                except Exception:
                    response = genai_client.models.generate_content(
                        model=PRIMARY_MODEL,
                        contents=[pdf_part, genai_types.Part.from_text(text=extraction_prompt)],
                        config=genai_types.GenerateContentConfig(response_mime_type="application/json"),
                    )

                raw = response.text or ""
                items = json.loads(raw) if raw.strip() else []
                if isinstance(items, dict):
                    for k in ("items", "coins", "line_items", "results"):
                        if k in items and isinstance(items[k], list):
                            items = items[k]; break
                    else:
                        items = [items]
                if not isinstance(items, list):
                    items = []

                # Derive receipt-level metadata from first item
                first_coin = next((i for i in items if isinstance(i, dict)
                                   and str(i.get("item_type", "coin")).lower()
                                   in ("coin", "paper_currency", "medal", "other", "")), {})
                retailer    = first_coin.get("Retailer Name", "Unknown Retailer")
                inv_no      = first_coin.get("Retailer Invoice #", "")
                inv_date    = first_coin.get("Purchase Date", "")

                total_val = 0.0
                line_items_out = []
                added_this_file = 0

                col_ref = db.collection("users").document(user_email).collection("review_queue")
                batch   = db.batch()

                for item in items:
                    if not isinstance(item, dict):
                        continue
                    item_type = str(item.get("item_type", "coin")).lower()
                    cost_str  = item.get("Purchase Cost") or item.get("Cost") or "0"
                    try:
                        cost_val = float(str(cost_str).replace("$", "").replace(",", "").strip())
                    except Exception:
                        cost_val = 0.0
                    total_val += cost_val

                    if item_type in ("coin", "paper_currency", "medal", "other", ""):
                        item["import_session_id"] = session_id
                        item["source_type"]       = "invoice_scan"
                        item["source_file"]       = fname
                        item["upload_method"]     = "invoice_scan"
                        item["deep_dive_status"]  = "PENDING"
                        item["created_at"]        = firestore.SERVER_TIMESTAMP
                        doc_ref = col_ref.document(str(uuid.uuid4()))
                        batch.set(doc_ref, item)
                        new_coin_ids.append(doc_ref.id)
                        line_items_out.append({**item, "coin_doc_id": doc_ref.id})
                        added_this_file += 1

                batch.commit()

                # Save original PDF to GCS (already there from upload, just record path)
                receipt_id  = str(uuid.uuid4())
                receipt_doc = {
                    "session_id":        session_id,
                    "original_filename": fname,
                    "gcs_path":          gcs_path,
                    "retailer":          retailer,
                    "invoice_number":    inv_no,
                    "invoice_date":      inv_date,
                    "total_amount":      total_val,
                    "line_items":        line_items_out,
                    "linked_coin_ids":   [],
                    "unlinked_items":    [],
                    "uploaded_at":       firestore.SERVER_TIMESTAMP,
                }
                db.collection("users").document(user_email)\
                  .collection("receipts").document(receipt_id).set(receipt_doc)

                summary["coins_identified"]     += added_this_file
                summary["receipts_parsed"]      += 1
                summary["total_purchase_value"] += total_val
                result_meta = {"coins_added": added_this_file, "receipt_id": receipt_id,
                               "total_value": total_val}
                per_file[idx]["status"]      = "done"
                per_file[idx]["coins_added"] = added_this_file
                per_file[idx]["receipt_id"]  = receipt_id

            except Exception as e:
                per_file[idx]["status"] = "error"
                per_file[idx]["error"]  = str(e)
                print(f"[bulk_import] invoice error ({fname}): {e}")

        elif ftype == "image":
            # Skip this image if it was already handled as part of a pair
            if idx in _paired_idx_done:
                per_file[idx]["status"] = "done"
                per_file[idx]["note"]   = "Processed as part of an obverse/reverse pair"
                session_ref.update({"per_file": per_file, "processed_files": idx + 1})
                continue

            try:
                ext_lower = fname.rsplit(".", 1)[-1].lower() if "." in fname else "jpg"
                mime_a    = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
                             "png": "image/png",  "webp": "image/webp",
                             "heic": "image/heic"}.get(ext_lower, "image/jpeg")
                bytes_a   = file_bytes

                # Check if there is a paired image (obverse + reverse)
                partner_bytes: bytes = file_bytes   # default: use same image for both passes
                partner_mime:  str   = mime_a
                partner_idx:   int | None = None
                stem = _img_stem(fname)
                companions = [i for i in _img_stem_map.get(stem, []) if i != idx]
                if companions:
                    partner_idx = companions[0]
                    _paired_idx_done.add(partner_idx)
                    partner_meta  = per_file[partner_idx]
                    partner_safe  = partner_meta["name"].replace(" ", "_")
                    partner_blob  = bucket.blob(
                        f"{user_email}/imports/{session_id}/raw/{partner_safe}"
                    )
                    try:
                        partner_bytes = partner_blob.download_as_bytes()
                        pext = partner_meta["name"].rsplit(".", 1)[-1].lower() if "." in partner_meta["name"] else "jpg"
                        partner_mime  = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
                                         "png": "image/png",  "webp": "image/webp",
                                         "heic": "image/heic"}.get(pext, "image/jpeg")
                    except Exception as pair_e:
                        print(f"[bulk_import] Could not load partner image: {pair_e}")
                        partner_bytes = bytes_a
                        partner_mime  = mime_a

                # ── Pass 1 — Full identification (mirrors identify_coin_photo) ──
                part_a = genai_types.Part.from_bytes(data=bytes_a,   mime_type=mime_a)
                part_b = genai_types.Part.from_bytes(data=partner_bytes, mime_type=partner_mime)

                resp1 = genai_client.models.generate_content(
                    model=PRIMARY_MODEL,
                    contents=[
                        genai_types.Part.from_text(text="[Image A]"), part_a,
                        genai_types.Part.from_text(text="[Image B]"), part_b,
                        genai_types.Part.from_text(text=PHOTO_ID_PASS1_PROMPT),
                    ],
                    config=genai_types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1,
                        thinking_config=genai_types.ThinkingConfig(thinking_budget=0),
                    ),
                )
                raw1 = resp1.text.strip()
                if raw1.startswith("```"):
                    raw1 = raw1.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                pass1: dict = json.loads(raw1)

                # ── Pass 2 — Verification (non-fatal) ────────────────────────
                pass2: dict = {}
                try:
                    pass2_prompt = PHOTO_ID_PASS2_PROMPT_TEMPLATE.format(
                        year          = pass1.get("year", ""),
                        country       = pass1.get("country", ""),
                        denomination  = pass1.get("denomination", ""),
                        program_series= pass1.get("program_series", ""),
                        mint_mark     = pass1.get("mint_mark", ""),
                        grade         = pass1.get("grade", ""),
                        metal_content = pass1.get("metal_content", ""),
                    )
                    resp2 = genai_client.models.generate_content(
                        model=PRIMARY_MODEL,
                        contents=[
                            genai_types.Part.from_text(text="[Image A]"), part_a,
                            genai_types.Part.from_text(text="[Image B]"), part_b,
                            genai_types.Part.from_text(text=pass2_prompt),
                        ],
                        config=genai_types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.1,
                            thinking_config=genai_types.ThinkingConfig(thinking_budget=0),
                        ),
                    )
                    raw2 = resp2.text.strip()
                    if raw2.startswith("```"):
                        raw2 = raw2.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                    pass2 = json.loads(raw2)
                except Exception as p2e:
                    print(f"[bulk_import] image pass2 non-fatal: {p2e}")

                # ── Merge results ─────────────────────────────────────────────
                final_year   = str(pass2.get("corrected_year")  or pass1.get("year",  ""))
                final_denom  = pass2.get("corrected_denomination") or pass1.get("denomination", "")
                final_series = pass2.get("corrected_series")    or pass1.get("program_series", "")
                final_grade  = pass2.get("refined_grade")       or pass1.get("grade", "")
                final_conf   = pass2.get("confidence")          or pass1.get("confidence", "")
                errors       = pass2.get("errors_detected", []) or []
                variety_str  = "; ".join(errors) if errors else pass1.get("variety_notes", "")
                est_value    = pass2.get("estimated_value_usd", "Pending")
                cond_notes   = pass2.get("condition_notes", "")
                full_report  = pass1.get("report", "")
                if cond_notes:
                    full_report += f"\n\nCondition: {cond_notes}"
                if errors:
                    full_report += f"\n\nErrors/Varieties: {variety_str}"
                full_report += f"\n\n[AI Confidence: {final_conf}]"

                gcs_path_img = f"gs://{IMPORT_BUCKET}/{user_email}/imports/{session_id}/raw/{safe_name}"

                coin_doc = {
                    "Year":              final_year,
                    "Country":           pass1.get("country", "USA"),
                    "Denomination":      final_denom,
                    "Program/Series":    final_series,
                    "Theme/Subject":     pass1.get("theme_subject", ""),
                    "Mint Mark":         pass1.get("mint_mark", ""),
                    "Condition":         final_grade,
                    "Metal Content":     pass1.get("metal_content", ""),
                    "Variety":           variety_str,
                    "AI Estimated Value": est_value,
                    "Numismatic Report": full_report,
                    "ai_confidence":     final_conf,
                    "is_silver":         pass1.get("is_silver", False),
                    "is_gold":           pass1.get("is_gold",   False),
                    "source":            "AI Photo Identifier",
                    "deep_dive_status":  "PENDING",
                    "import_session_id": session_id,
                    "source_type":       "image",
                    "source_file":       fname,
                    "upload_method":     "image_upload",
                    "gcs_image_path":    gcs_path_img,
                    "has_paired_image":  partner_idx is not None,
                    "created_at":        firestore.SERVER_TIMESTAMP,
                }

                col_ref = db.collection("users").document(user_email).collection("review_queue")
                doc_ref = col_ref.document(str(uuid.uuid4()))
                doc_ref.set(coin_doc)
                new_coin_ids.append(doc_ref.id)
                summary["coins_identified"] += 1
                per_file[idx]["status"]      = "done"
                per_file[idx]["coins_added"] = 1
                per_file[idx]["coin_doc_id"] = doc_ref.id
                print(f"[bulk_import] image identified: {final_year} {final_denom} "
                      f"conf={final_conf} pair={'yes' if partner_idx is not None else 'no'}")

            except Exception as e:
                per_file[idx]["status"] = "error"
                per_file[idx]["error"]  = str(e)
                print(f"[bulk_import] image error ({fname}): {e}")

        else:
            per_file[idx]["status"] = "skipped"
            per_file[idx]["note"]   = "File type not recognized"

        # Push progress after each file
        session_ref.update({
            "per_file":       per_file,
            "processed_files": idx + 1,
            "summary":        summary,
        })

    # ── Post-processing: duplicate sweep + receipt linking ────────────────────
    session_ref.update({"status": "linking"})

    dup_result  = _run_duplicate_sweep(user_email, session_id, new_coin_ids)
    link_result = _link_receipts_to_coins(user_email, session_id)

    summary["duplicates_flagged"]  = dup_result["strong"] + dup_result["possible"]
    summary["unlinked_receipts"]   = link_result["unlinked"]

    session_ref.update({
        "status":           "done",
        "processed_files":  len(per_file),
        "summary":          summary,
        "per_file":         per_file,
    })

    return {
        "status":       "done",
        "session_id":   session_id,
        "summary":      summary,
        "duplicates":   dup_result,
        "links":        link_result,
    }


# ── GET /api/receipts/{user_email} ────────────────────────────────────────────

@app.get("/api/receipts/{user_email}")
def list_receipts(user_email: str, session_id: str = None, limit: int = 100):
    """Return all receipts for a user, optionally filtered by session."""
    col = db.collection("users").document(user_email).collection("receipts")
    if session_id:
        col = col.where("session_id", "==", session_id)
    docs = col.order_by("uploaded_at", direction=firestore.Query.DESCENDING)\
              .limit(limit).stream()
    results = []
    for d in docs:
        data = d.to_dict()
        data["receipt_id"] = d.id
        data.pop("uploaded_at", None)
        results.append(data)
    return {"receipts": results}


# ── GET /api/receipts/{user_email}/{receipt_id}/view_url ──────────────────────

@app.get("/api/receipts/{user_email}/{receipt_id}/view_url")
def receipt_view_url(user_email: str, receipt_id: str):
    """
    Generate a fresh 24-hour signed GCS URL so the user can view the original
    invoice PDF directly in the browser (no download required).
    """
    rec_snap = db.collection("users").document(user_email)\
                 .collection("receipts").document(receipt_id).get()
    if not rec_snap.exists:
        raise HTTPException(status_code=404, detail="Receipt not found")

    gcs_path = rec_snap.to_dict().get("gcs_path", "")
    if not gcs_path.startswith("gs://"):
        raise HTTPException(status_code=400, detail="No GCS path recorded for this receipt")

    # Parse  gs://bucket/path/to/blob
    path_part = gcs_path[len("gs://"):]
    bucket_name, blob_name = path_part.split("/", 1)
    bucket = gcs_client.bucket(bucket_name)
    blob   = bucket.blob(blob_name)

    signed_url = blob.generate_signed_url(
        version="v4",
        expiration=86400,    # 24 hours
        method="GET",
    )
    return {
        "receipt_id":      receipt_id,
        "signed_url":      signed_url,
        "filename":        rec_snap.to_dict().get("original_filename", ""),
        "expires_seconds": 86400,
    }




# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  COLLECTION MANAGEMENT — BULK CLEAR                                         ║
# ║  Allows a user's entire coin collection to be wiped in one call.            ║
# ║  Protected by a mandatory confirm=DELETE guard.                             ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

class ClearCollectionRequest(BaseModel):
    user_email: str
    confirm: str          # must equal "DELETE" exactly


@app.get("/api/collection/count")
def collection_count(user_email: str):
    """
    Return the number of coins in a user's collection using Firestore's
    aggregation query (COUNT) — reads zero documents, billed as a single
    aggregation query.

    Returns:
        { "user_email": str, "coins": int }
    """
    try:
        coins_ref   = db.collection('users').document(user_email).collection('coins')
        agg_query   = coins_ref.count()
        result      = agg_query.get()
        # result is a list of AggregationResult; first item holds the count
        count = result[0][0].value if result and result[0] else 0
        return {"user_email": user_email, "coins": count}
    except Exception as e:
        print(f"[collection_count] Error for {user_email}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/collection/clear")
def collection_clear(req: ClearCollectionRequest):
    """
    Permanently delete ALL coins from a user's collection.

    Safety gate:
        req.confirm must be the exact string "DELETE" — the endpoint returns
        400 immediately if it is anything else.

    Only the `coins` sub-collection is affected.  All other user data
    (review_queue, import_sessions, receipts, binder_scans, etc.) is left
    untouched.

    Implementation:
        Streams document references in pages and deletes in Firestore batches
        of ≤ 490 writes (hard limit is 500).  Never loads the full collection
        into memory.

    Returns:
        { "status": "success", "user_email": str, "coins_deleted": int }
    """
    if req.confirm != "DELETE":
        raise HTTPException(
            status_code=400,
            detail="Safety check failed: 'confirm' must be the exact string 'DELETE'."
        )

    try:
        coins_ref     = db.collection('users').document(req.user_email).collection('coins')
        coins_deleted = 0
        BATCH_LIMIT   = 490  # Firestore max is 500 writes per batch

        while True:
            # Stream up to BATCH_LIMIT doc refs at a time (select() fetches only IDs)
            docs = list(coins_ref.limit(BATCH_LIMIT).stream())
            if not docs:
                break   # nothing left

            batch = db.batch()
            for doc in docs:
                batch.delete(coins_ref.document(doc.id))
                coins_deleted += 1
            batch.commit()

        print(f"[collection_clear] Deleted {coins_deleted} coins for {req.user_email}")
        return {
            "status":        "success",
            "user_email":    req.user_email,
            "coins_deleted": coins_deleted,
        }

    except Exception as e:
        print(f"[collection_clear] Error for {req.user_email}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
