import yfinance as yf
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
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

# AI SDK
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
import feedparser
import re

app = FastAPI(title="Numista.AI Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
# Source: https://cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versions
# Verified: April 15, 2026
#
# Current stable Vertex AI lineup (NOT before Oct 16, 2026 retirement):
#   gemini-2.5-flash   — Primary workhorse. Fast, multimodal, structured JSON.
#   gemini-2.5-pro     — Complex document analysis. Higher quality, higher cost.
#   gemini-2.5-flash-lite — Cheapest option for simple tasks.
#
# Gemini 3.x models: NOT YET available on Vertex AI as of April 2026.
# They exist in AI Studio docs index but have not launched in Vertex AI.
# When Gemini 3.x lands on Vertex AI, update PRIMARY_MODEL below.
# The new thinking API (thinking_level="MINIMAL"|"HIGH") requires the
# google-genai SDK (successor to vertexai SDK). Migration note is documented
# inline at each generate_content() call.
PRIMARY_MODEL = "gemini-2.5-flash"
PRO_MODEL     = "gemini-2.5-pro"

vertexai.init(project=PROJECT_ID, location=LOCATION)
model        = GenerativeModel(PRIMARY_MODEL)   # All general endpoints
binder_model = GenerativeModel(PRIMARY_MODEL)   # Binder / checklist analysis


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

@app.post("/api/import_spreadsheet")
async def import_spreadsheet(
    user_email:  str = Form(...),
    file:        UploadFile = File(...),
    import_name: str = Form(''),   # optional label e.g. "Aunt's Access DB - Jan 2026"
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
        resp = model.generate_content(
            mapping_prompt,
            generation_config=GenerationConfig(response_mime_type="application/json"),
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
        new_doc['upload_method'] = 'spreadsheet_import'
        new_doc['source_file']   = file.filename
        new_doc['import_name']   = import_name or file.filename
        new_doc['created_at']    = firestore.SERVER_TIMESTAMP

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
                fb_resp = model.generate_content(
                    fallback_prompt,
                    generation_config=GenerationConfig(response_mime_type="application/json"),
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
        "Year,Mint Mark,Denomination,Program/Series,Theme/Subject,"
        "Condition,Cost,Purchase Date,Retailer Name,Retailer Invoice #,"
        "Retailer Item No.,Storage Location,Notes\n"
    )
    example_row = (
        '1921,D,Dollar,Morgan Silver Dollar,Morgan Dollar,'
        'VF-30,42.00,1995-06-15,Local Coin Shop,,,'
        'Safe Deposit Box,Rim nick at 3 o\'clock\n'
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

    docs = list(col.order_by('submitted_at', direction=firestore.Query.DESCENDING)
                   .limit(limit + offset).stream())
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
    docs      = list(coins_ref.stream())

    results = []
    for doc in docs:
        d      = doc.to_dict()
        source = d.get('source', '')
        conf   = float(d.get('confidence_score', 1.0))

        # Only AI-processed coins
        is_ai = source in AI_SOURCES or conf < 0.95
        if not is_ai:
            continue

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


@app.get("/api/grade_review/stats")
def grade_review_stats(user_email: str):
    """Per-user grade review statistics for the Human AI Trainer dashboard."""
    coins_ref = db.collection('users').document(user_email).collection('coins')
    docs      = list(coins_ref.stream())

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
async def process_invoice(user_email: str = Form(...), file: UploadFile = File(...)):
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
        from vertexai.generative_models import Part
        pdf_part = Part.from_data(data=contents, mime_type="application/pdf")
        
        extraction_prompt = """
        You are an expert coin collector's robotic accountant. Review this PDF invoice/receipt.
        Extract line items representing actual numismatic purchases (Coins, Bullion, Currency).
        
        CRITICAL RULES:
        1. Ignore shipping, tax, or discount rows.
        2. EXCLUDE all non-currency supplies such as: "Binders", "Coin Holders", "Slabs", "Magnifiers", "Pages", "Capsules".
        3. If an item is a foreign coin, ensure Country is accurate.
        
        Return ONLY a JSON list of objects matching this precise schema (23 columns):
        [
          {
            "Country": "Country of origin",
            "Year": "numeric year",
            "Mint Mark": "e.g. P, D, S, W",
            "Denomination": "e.g. Lincoln Cent, Morgan Dollar",
            "Quantity": 1,
            "Program/Series": "e.g. 50 State Quarters",
            "Theme/Subject": "Specific description",
            "Condition": "e.g. MS-65, Average Circ",
            "Strike Type": "e.g. Business, Proof, Special Mint Set",
            "Holder Type": "e.g. Raw, Slabs, Folder",
            "Grading Service": "e.g. PCGS, NGC, None",
            "Certification Number": "if present",
            "Metal Content": "e.g. 90% Silver, Cupro-Nickel, 35% Silver Wartime",
            "Purchase Cost": "formatted price like $10.00",
            "Purchase Date": "found on invoice top",
            "Retailer/Website": "e.g. Littleton Coin Company",
            "Retailer Item No.": "The specific stock number (e.g. 214.AC)",
            "Retailer Invoice #": "The invoice ID (e.g. 67000001)",
            "Variety": "CRITICAL: Lookout for 'Double Die', 'Mint Error', 'Repunched Mint Mark', or specific errors in description",
            "Personal Notes I": "",
            "Personal Reference #": "",
            "Storage Location": "inferred or blank",
            "Original Description from source": "THE EXACT FULL LINE DESCRIPTION FROM THE INVOICE"
          }
        ]
        
        DICTIONARY FOR MAPPING: {json.dumps(COIN_DICTIONARY)}
        """
        
        pro_model = GenerativeModel(PRO_MODEL)
        response = pro_model.generate_content(
            [pdf_part, extraction_prompt],
            generation_config=GenerationConfig(response_mime_type="application/json")
        )
        items = json.loads(response.text)
        
        # Save to Firestore (Review Queue)
        added_count = 0
        batch = db.batch()
        col_ref = db.collection('users').document(user_email).collection('review_queue')
        
        for item in items:
             # Apply defaults to pass schema rules
             item['deep_dive_status'] = 'PENDING'
             if not item.get('Program/Series'):  # preserve AI-extracted value
                 item['Program/Series'] = (item.get('Country') or 'USA') + ' Invoice Import'
             if 'Condition' not in item: item['Condition'] = 'Ungraded'
             if 'Cost' not in item: item['Cost'] = '$0.00'
             
             item['source'] = 'PDF Invoice'
             # ── Split combined Year+Mint (e.g. "2006D" → Year="2006", Mint Mark="D") ──
             import re as _re
             raw_year = str(item.get('Year', '')).strip()
             raw_mint = str(item.get('Mint Mark', '')).strip()
             if raw_year and not raw_mint:
                 _ym = _re.match(r'^(\d{4}(?:-\d{4})?)\s*([A-WY-Z])$', raw_year, _re.IGNORECASE)
                 if _ym:
                     item['Year'] = _ym.group(1)
                     item['Mint Mark'] = _ym.group(2).upper()
             item['source_file'] = file.filename
             item['created_at'] = firestore.SERVER_TIMESTAMP
             
             doc_ref = col_ref.document(str(uuid.uuid4()))
             batch.set(doc_ref, item)
             added_count += 1
             
        batch.commit()
        return {"status": "success", "extracted_items": added_count, "data": items}
        
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
                " -bitcoin -crypto -cluster -galaxy -beer -beauty -fashion -cluster"
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
            _COIN_KW = {
                "numismatic", "numismatics", "coin", "coins", "mint", "minted",
                "pcgs", "proof set", "mint set", "bullion", "morgan dollar",
                "peace dollar", "american eagle coin", "american eagle bullion",
                "walking liberty", "saint-gaudens", "commemorative coin",
                "commemorative coins", "uncirculated", "coin show",
                "coin auction", "coin dealer",
            }

            def _is_coin_title(t: str) -> bool:
                tl = t.lower()
                return any(kw in tl for kw in _COIN_KW)

            resp = req.get("https://newsapi.org/v2/everything", params=params, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                articles = data.get("articles", [])
                results = []
                for a in articles:
                    title = a.get("title", "")
                    if not title or title == "[Removed]":
                        continue
                    # Skip articles not about coins/numismatics at the title level
                    if not _is_coin_title(title):
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
        ("https://www.usmint.gov/rss/news.xml",       "US Mint"),
        ("https://www.pcgs.com/rss/news",              "PCGS"),
        ("https://www.ngccoin.com/rss/news.ashx",      "NGC"),
        ("https://www.coinnews.net/feed/",             "CoinNews"),
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


class DeepDiveRequest(BaseModel):
    user_email: str
    query: str

@app.post("/api/deep_dive")
async def deep_dive(request: DeepDiveRequest):
    """
    Grounded AI search: Fetches the user's specific collection from Firestore 
    and answers questions using Gemini 2.5 Flash as an expert numismatist.
    """
    try:
        # 1. Fetch Collection
        col_ref = db.collection('users').document(request.user_email).collection('coins')
        docs = col_ref.stream()
        
        inventory_items = []
        for doc in docs:
            d = doc.to_dict()
            # Reduce token size by only sending relevant searchable fields
            inventory_items.append({
                "Year": d.get("Year", ""),
                "Denom": d.get("Denomination", ""),
                "Mint": d.get("Mint Mark", ""),
                "Condition": d.get("Condition", ""),
                "Subject": d.get("Theme/Subject", ""),
                "Value": d.get("AI Estimated Value", "$0.00")
            })
            
        if not inventory_items:
            context = "The user's collection is currently empty."
        else:
            context = json.dumps(inventory_items, default=str)
            
        # 2. Call Gemini
        prompt = f"""
        You are 'Numista AI', a professional, expert numismatic advisor.
        You are looking at the user's private coin collection data:
        {context}
        
        User's Question: {request.query}
        
        Instructions:
        - Be accurate based ONLY on the provided data when possible.
        - If the question is general numismatics, answer as an expert.
        - Be concise but professional.
        - If they ask for 'most valuable', sort the provided JSON data by the Value field.
        """
        
        response = model.generate_content(prompt)
        return {"status": "success", "response": response.text}
        
    except Exception as e:
        print(f"Deep dive error: {e}")
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
                    continue

                new_coin_ref = coins_ref.document(doc_id)
                batch.set(new_coin_ref, data)
                batch.delete(queue_ref.document(doc_id))
                committed_count += 1
        
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

@app.post("/api/review/bulk_update")
async def bulk_update_reviews(request: BulkUpdateRequest):
    """
    Applies shared metadata to multiple items in the review queue.
    """
    try:
        queue_ref = db.collection('users').document(request.user_email).collection('review_queue')
        batch = db.batch()
        for doc_id in request.review_ids:
            batch.update(queue_ref.document(doc_id), request.updates)
        
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
      "slot_condition_note": "optional — any note about damage or ambiguity"
    }
  ],
  "analysis_notes": "Any overall observations about the binder, image quality, or uncertainties",
  "mint_clarification_needed": false
}

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

    from vertexai.generative_models import Part, GenerationConfig as GC

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
        image_parts.append(Part.from_data(data=raw_bytes, mime_type=content_type))
        image_parts.append(Part.from_text(f"[Image {idx + 1} of {len(images)}: page_{idx:02d}.{ext}]"))

    # ── 2. Call Gemini 2.5 Flash with all images + system prompt ──────────────────
    try:
        prompt_parts = image_parts + [Part.from_text(BINDER_SCAN_SYSTEM_PROMPT)]

        response = binder_model.generate_content(
            prompt_parts,
            generation_config=GC(
                response_mime_type="application/json",
                temperature=0.1,
                max_output_tokens=65536,
                # NOTE: thinking_level="MINIMAL" would be set here once we migrate
                # from vertexai SDK to the newer google-genai SDK (see deprecation plan)
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
    from vertexai.generative_models import Part, GenerationConfig as GC

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
            file_parts.append(Part.from_data(data=raw_bytes, mime_type=content_type))
            file_parts.append(Part.from_text(f"[File: {filename}]"))

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
            response = binder_model.generate_content(
                file_parts + [Part.from_text(checklist_prompt)],
                generation_config=GC(
                    response_mime_type="application/json",
                    temperature=0.1,
                    max_output_tokens=65536,
                    # NOTE: thinking_level="MINIMAL" pending google-genai SDK migration
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
            "binder_doc_id":       request.binder_doc_id,
            "binder_page_index":   page_index,
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


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)