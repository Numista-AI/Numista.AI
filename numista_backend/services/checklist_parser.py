"""
Numista.AI Checklist & Handwritten Notes Parser Service
Deterministic Multi-Modal & 2-Stage Parsing Pipeline
Extracts 100% of marked checklist rows/cells into canonical SoR coin schemas.
"""

import re
import json
import hashlib
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from config.ingestion_config import (
    EXTRACTION_MODEL,
    CHECKLIST_PROMPT_VERSION,
    BOX_CLARITY_WEIGHT,
    SUBJECT_OCR_WEIGHT,
    HEADER_VALIDATION_WEIGHT,
    HANDWRITING_QUARANTINE_THRESHOLD,
    MAX_ROWS_PER_EXTRACTION_CHUNK
)

logger = logging.getLogger("numista_backend.checklist_parser")

CHECKLIST_EXTRACTION_SYSTEM_PROMPT = """
You are Numista.AI's System of Record Checklist & Grid Inventory Extractor.
Your task is to analyze this coin checklist or inventory table and extract EVERY coin marked or checked by the collector.

CRITICAL EXTRACTION RULES:
1. Examine every table row and column grid cell (e.g. Year, Subject / Theme, and Mint Mark columns: P, D, S, W, Proof, Unc).
2. If a mint mark box (or check cell) is checked (with a checkmark, X, tick, ink dot, or circle), EXTRACT THAT COIN.
3. Multi-Mint Rows: If a row has checkmarks in multiple columns (e.g., both 'P' and 'D' checked for '2023 Edith Kanaka'ole'), you MUST extract TWO separate coin records (one for 'P', one for 'D').
4. Theme/Subject: You MUST extract the specific individual theme/subject name for each row (e.g. 'Maya Angelou', 'Dr. Sally Ride', 'Wilma Mankiller', 'Nina Otero-Warren', 'Anna May Wong', 'Bessie Coleman', 'Edith Kanaka'ole', 'Eleanor Roosevelt', 'Jovita Idar', 'Maria Tallchief', 'Rev. Dr. Pauli Murray', 'Patsy Takemoto Mink', 'Dr. Mary Edwards Walker', 'Celia Cruz', 'Zitkala-Sa'). NEVER return a blank Theme/Subject for recognized program coins!
5. Storage Location & Binder Notes: Look at the top header, margins, or footer for handwritten notes (e.g. 'US Women Quarters Book', '2x2 Box A', 'ATB-P tube'). Extract this string into "storage_location".
6. Personal Notes: Extract any row-specific handwritten annotations, variety notes, or numbers.
7. Document Provenance: Extract the Snapshot ID (e.g. SNAP-YYYYMMDD-XXXXXXXX) if present in the header/footer.
8. Denomination & Program: Infer denomination (e.g. 'Quarter' or 'Quarter Dollar') and Program Series (e.g. 'American Women Quarters', '50 State Quarters', 'America the Beautiful Quarters', 'Morgan Dollars').
9. Condition / Grade: If a grade is specified in the notes (e.g. 'MS65', 'BU', 'Proof'), extract it. Otherwise set to 'Unspecified / Raw'.

Return a JSON object with this exact structure:
{
  "program_series": "American Women Quarters",
  "denomination": "Quarter",
  "storage_location": "US Women Quarters Book",
  "snapshot_id": "SNAP-20260815-5472C902",
  "page_notes": "Extracted header/footer notes",
  "handwriting_confidence": 0.95,
  "coins": [
    {
      "year": 2022,
      "mint_mark": "P",
      "denomination": "Quarter",
      "program_series": "American Women Quarters",
      "theme_subject": "Maya Angelou",
      "condition": "Unspecified / Raw",
      "storage_location": "US Women Quarters Book",
      "personal_notes": "",
      "page_number": 1,
      "row_index": 1,
      "box_clarity_score": 0.98,
      "subject_ocr_score": 0.99,
      "header_validation_score": 1.0
    }
  ]
}
9. 2026 America250 / Semiquincentennial (CRITICAL FOR 2026 CHECKLISTS):
   - CIRCULATING REDESIGNS — assign Program/Series = "United States Semiquincentennial" for these coins when year == 2026:
     * "Emerging Liberty" or "Emerging Liberty Dime" → denomination = "10c" / "Dime"
     * "Enduring Liberty" or "Enduring Liberty Half Dollar" → denomination = "50c" / "Half Dollar"
     * "1776 ~ 2026" or "1776~2026" nickel → denomination = "5c" / "Nickel"
     * America250 quarters: "Mayflower Compact", "Revolutionary War", "Declaration of Independence",
       "U.S. Constitution", "Gettysburg Address" → denomination = "25c" / "Quarter"
   - DO NOT assign Semiquincentennial to pennies / cents — no 2026 cent redesign exists in circulation.
   - PRIVY BULLION COLLECTIBLES — keep parent series (do NOT assign Semiquincentennial):
     * American Silver Eagle with 250 privy → Program/Series = "American Silver Eagle"
     * American Gold Eagle with 250 privy → Program/Series = "American Gold Eagle"
     * American Buffalo Gold with 250 privy → Program/Series = "American Buffalo"
     * Morgan Dollar with 250 privy → Program/Series = "Morgan Dollar"
     * Peace Dollar with 250 privy → Program/Series = "Peace Dollar"
     * American Innovation $1 with 250 privy → Program/Series = "American Innovation Dollar"
   - NATIVE AMERICAN $1 (Valley Forge / Polly Cooper / Oneida Allies): assign Program/Series = "Native American $1" — NOT Semiquincentennial.
   - COMMEMORATIVE PRESIDENTIAL DOLLAR (Donald J. Trump 2026): assign Program/Series = "Commemorative Dollar".
   - The text "250th Anniversary", "America250", or "semiquincentennial" in a header or title is a strong signal these are 2026 Semiquincentennial circulating coins.
"""

def slugify_theme(theme_raw: str) -> str:
    """
    Deterministic theme slugification algorithm for canonical reference image keys.
    """
    if not theme_raw:
        return "unknown"
    s = theme_raw.lower().strip()
    s = re.sub(r"\(.*?\)", "", s).strip()
    s = re.sub(r"\b(national park & preserve|national park and preserve|national park|national historic site|national monument|national historical park|national forest|national memorial|state park)\b", "", s).strip()
    s = re.sub(r"[^\w\s-]", "", s)
    slug = re.sub(r"[\s-]+", "_", s).strip("_")
    return slug or "unknown"


def parse_checklist_notes(raw_notes: str) -> Dict[str, Any]:
    """
    Parses row-level annotations/notes from checklists for ownership, quantity,
    storage location, condition, and flags.
    """
    raw_str = (raw_notes or "").strip()
    if not raw_str:
        return {
            "is_owned": True,
            "quantity": 1,
            "condition": "Unspecified / Raw",
            "storage_location": "",
            "personal_notes": "",
            "confidence_score": 1.0,
            "flag": None,
        }

    lower = raw_str.lower()
    if lower in ("0", "have 0", "already have 0", "need", "missing", "none") or re.search(r"\b(?:have|has|already have)\s+0\b", lower):
        return {
            "is_owned": False,
            "quantity": 0,
            "condition": "Unspecified / Raw",
            "storage_location": "",
            "personal_notes": raw_str,
            "confidence_score": 1.0,
            "flag": "unselected_zero_ownership" if "already have 0" in lower else None,
        }

    is_owned = True
    quantity = 1
    condition = "Unspecified / Raw"
    storage_loc = ""
    personal_notes = raw_str
    flag = None

    qty_match = re.search(r"(?:qty|quantity)[:\s]+(\d+)", raw_str, re.IGNORECASE)
    if qty_match:
        quantity = int(qty_match.group(1))

    if re.search(r"\bproof\b", lower):
        condition = "Proof"
    elif re.search(r"\b(?:unc|uncirculated)\b", lower):
        condition = "Uncirculated"
    elif re.search(r"\b(ms\s*\d{2}|au\s*\d{2}|xf\s*\d{2}|vf\s*\d{2}|f\s*\d{2}|vg\s*\d{2}|g\s*\d{2}|ag\s*\d{2}|fr\s*\d{2}|pr\s*\d{2})\b", lower):
        cond_match = re.search(r"\b(ms\s*\d{2}|au\s*\d{2}|xf\s*\d{2}|vf\s*\d{2}|f\s*\d{2}|vg\s*\d{2}|g\s*\d{2}|ag\s*\d{2}|fr\s*\d{2}|pr\s*\d{2})\b", raw_str, re.IGNORECASE)
        if cond_match:
            condition = cond_match.group(1).upper().replace(" ", "")

    if re.match(r"^atb\s*-\s*([pd])\s*tube", raw_str, re.IGNORECASE):
        m = re.match(r"^atb\s*-\s*([pd])\s*tube", raw_str, re.IGNORECASE)
        storage_loc = f"ATB-{m.group(1).upper()} tube"
    elif "atb-p tube" in lower:
        storage_loc = "ATB-P tube"
    elif "atb-d tube" in lower:
        storage_loc = "ATB-D tube"
    elif "dansco album" in lower:
        storage_loc = raw_str
    elif "proof set box" in lower or ("proof set" in lower and "box" in lower):
        storage_loc = "Proof Set Box"
    elif "unc roll" in lower:
        storage_loc = "UNC Roll"
    elif re.search(r"(?:safe\s+box\s+\d+|box\s+\d+|album\s+[^\,]+|binder\s+[^\,]+|tube\s+[^\,]+|vault\s+[^\,]+)", raw_str, re.IGNORECASE):
        loc_match = re.search(r"(safe\s+box\s+\d+|box\s+\d+|album\s+[^\,]+|binder\s+[^\,]+|tube\s+[^\,]+|vault\s+[^\,]+)", raw_str, re.IGNORECASE)
        if loc_match:
            storage_loc = loc_match.group(1).strip()

    return {
        "is_owned": is_owned,
        "quantity": quantity,
        "condition": condition,
        "storage_location": storage_loc,
        "personal_notes": personal_notes,
        "confidence_score": 1.0,
        "flag": flag,
    }



US_WOMEN_QUARTERS_OFFICIAL_TITLES: Dict[tuple, str] = {
    (2022, "Maya Angelou"): "Maya Angelou",
    (2022, "Dr. Sally Ride"): "Dr. Sally Ride",
    (2022, "Wilma Mankiller"): "Wilma Mankiller",
    (2022, "Nina Otero-Warren"): "Nina Otero-Warren",
    (2022, "Anna May Wong"): "Anna May Wong",
    (2023, "Bessie Coleman"): "Bessie Coleman",
    (2023, "Edith Kanaka'ole"): "Edith Kanaka'ole",
    (2023, "Eleanor Roosevelt"): "Eleanor Roosevelt",
    (2023, "Jovita Idar"): "Jovita Idar",
    (2023, "Maria Tallchief"): "Maria Tallchief",
    (2024, "Dr. Pauli Murray"): "Rev. Dr. Pauli Murray",
    (2024, "Patsy Mink"): "Patsy Takemoto Mink",
    (2024, "Dr. Mary Edwards Walker"): "Dr. Mary Edwards Walker",
    (2024, "Celia Cruz"): "Celia Cruz",
    (2024, "Zitkala-Ša"): "Zitkala-Ša",
    (2024, "Zitkala-Sa"): "Zitkala-Ša",
    (2025, "Ida B. Wells"): "Ida B. Wells",
    (2025, "Juliette Gordon Low"): "Juliette Gordon Low",
    (2025, "Dr. Vera Rubin"): "Dr. Vera Rubin",
    (2025, "Stacey Milbern"): "Stacey Park Milbern",
    (2025, "Althea Gibson"): "Althea Gibson",
}


def get_official_us_mint_title(year: int, theme_subject: str) -> str:
    """
    Returns official US Mint catalog title for a known (year, theme_subject) pair.
    Preserves exact theme_subject if not in dictionary.
    """
    if not theme_subject:
        return ""
    key = (year, theme_subject.strip())
    if key in US_WOMEN_QUARTERS_OFFICIAL_TITLES:
        return US_WOMEN_QUARTERS_OFFICIAL_TITLES[key]
    norm_theme = theme_subject.strip().replace("Š", "S").replace("š", "s").replace("ʻ", "'").replace("’", "'")
    for (y, t), official in US_WOMEN_QUARTERS_OFFICIAL_TITLES.items():
        if y == year and (t == norm_theme or t.replace("Š", "S").replace("ʻ", "'") == norm_theme):
            return official
    return theme_subject.strip()


def normalize_storage_location(raw_text: str, default_location: str = "") -> str:
    """
    Normalizes handwritten notes/header text to clean canonical storage location.
    Handles 'All Quarters Stored in the U.S. Women's Quarter Book' -> 'US Women Quarters Book'.
    """
    if not raw_text:
        return default_location.strip().rstrip(".")
    cleaned = raw_text.strip().rstrip(".")
    lower = cleaned.lower()
    if "women" in lower and ("quarter" in lower or "book" in lower):
        return "US Women Quarters Book"
    if "all quarters stored in" in lower:
        match = re.search(r"all quarters stored in (?:the )?([^\.\n]+)", cleaned, re.IGNORECASE)
        if match:
            loc = match.group(1).strip().rstrip(".")
            return "US Women Quarters Book" if "women" in loc.lower() else loc
    return cleaned


def extract_checklist_document(
    file_bytes: bytes,
    mime_type: str,
    filename: str,
    genai_client: Any,
    uid: str,
    import_session_id: str,
    program_hint: str = "",
) -> Dict[str, Any]:
    """
    Extracts coin checklist items from document bytes using Gemini 3.1 Pro Preview.
    Attaches calibrated composite confidence, exact runtime models, prompt hashes,
    and immutable SoR source provenance.
    """
    try:
        from google.genai import types as genai_types

        doc_hash = hashlib.sha256(file_bytes).hexdigest()

        # Prepend the classifier's detected program/vendor as a hint when available
        effective_prompt = CHECKLIST_EXTRACTION_SYSTEM_PROMPT
        if program_hint:
            effective_prompt = (
                f"PROGRAM CONTEXT HINT: The classifier identified this document as belonging to the "
                f'"{program_hint}" program. Use this to inform program_series assignment when ambiguous.\n\n'
            ) + effective_prompt

        prompt_hash = hashlib.sha256(
            (effective_prompt + "\n" + CHECKLIST_PROMPT_VERSION).encode("utf-8")
        ).hexdigest()[:16]

        pdf_part = genai_types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
        response = genai_client.models.generate_content(
            model=EXTRACTION_MODEL,
            contents=[pdf_part, genai_types.Part.from_text(text=effective_prompt)],
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        raw_text = response.text or "{}"
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text.strip(), flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned).strip()
        data = json.loads(cleaned)
        
        raw_coins = data.get("coins", [])
        raw_location = data.get("storage_location", "").strip()
        page_notes = data.get("page_notes", "").strip()
        extracted_location = normalize_storage_location(page_notes or raw_location, default_location="US Women Quarters Book")
        
        snapshot_id = data.get("snapshot_id", "").strip()
        program_series = data.get("program_series", "American Women Quarters").strip()
        handwriting_conf = float(data.get("handwriting_confidence", 0.90))
        
        extracted_items = []
        for idx, coin in enumerate(raw_coins):
            year = int(coin.get("year", 0)) if str(coin.get("year", "")).isdigit() else 0
            mint_mark = str(coin.get("mint_mark", "P")).upper().strip()
            theme_subject = str(coin.get("theme_subject", "")).strip()
            denom = str(coin.get("denomination", "Quarter")).strip()
            series = str(coin.get("program_series", program_series)).strip()
            official_title = get_official_us_mint_title(year, theme_subject)
            
            box_clarity = float(coin.get("box_clarity_score", 0.95))
            subject_ocr = float(coin.get("subject_ocr_score", 0.95))
            header_val = float(coin.get("header_validation_score", 0.95))
            
            composite_conf = (
                BOX_CLARITY_WEIGHT * box_clarity +
                SUBJECT_OCR_WEIGHT * subject_ocr +
                HEADER_VALIDATION_WEIGHT * header_val
            )
            
            coin_loc = coin.get("storage_location", "").strip()
            item_loc = normalize_storage_location(coin_loc, default_location=extracted_location)
            notes = coin.get("personal_notes", "").strip()
            
            # Format item record matching canonical schema
            title = f"{year} {mint_mark} {denom} - {theme_subject}" if theme_subject else f"{year} {mint_mark} {denom}"
            
            # Fail-closed quarantine gating
            is_quarantined = (handwriting_conf < HANDWRITING_QUARANTINE_THRESHOLD) or (not theme_subject)
            review_needed = is_quarantined
            
            source_provenance = {
                "source_type": "checklist_scan",
                "document_name": filename,
                "document_hash": doc_hash,
                "snapshot_id": snapshot_id or f"SNAP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-SCAN",
                "classifier_model": "gemini-3.7-flash",
                "extraction_model": EXTRACTION_MODEL,
                "prompt_version": CHECKLIST_PROMPT_VERSION,
                "prompt_hash": prompt_hash,
                "page_number": int(coin.get("page_number", 1)),
                "row_index": int(coin.get("row_index", idx + 1)),
                "mint_mark": mint_mark,
                "composite_confidence": round(composite_conf, 3),
                "handwriting_confidence": round(handwriting_conf, 3),
                "extracted_at": datetime.now(timezone.utc).isoformat(),
            }
            
            item = {
                "item_type": "coin",
                "Country": "United States",
                "country": "United States",
                "is_foreign": False,
                "Year": year or "",
                "year": year,
                "Mint Mark": mint_mark,
                "mint_mark": mint_mark,
                "Denomination": denom,
                "denomination": denom,
                "Program/Series": series,
                "program_series": series,
                "Theme/Subject": theme_subject,
                "theme_subject": theme_subject,
                "Official US Mint Title": official_title,
                "official_us_mint_title": official_title,
                "title": title,
                "Condition": coin.get("condition", "Unspecified / Raw"),
                "condition": coin.get("condition", "Unspecified / Raw"),
                "Cost": "$0.00",
                "cost": 0.0,
                "Retailer/Website": "N/A (Checklist Scan)",
                "retailer_website": "N/A (Checklist Scan)",
                "source_type": "checklist_scan",
                "Retailer Invoice #": "N/A",
                "retailer_invoice_num": "N/A",
                "Storage Location": item_loc,
                "storage_location": item_loc,
                "Personal Notes": notes,
                "personal_notes": notes,
                "status": "quarantined" if is_quarantined else "staged",
                "review_needed": review_needed,
                "import_session_id": import_session_id,
                "doc_hash": doc_hash,
                "source_provenance": source_provenance,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            extracted_items.append(item)
            
        return {
            "status": "success",
            "extracted_count": len(extracted_items),
            "doc_hash": doc_hash,
            "prompt_hash": prompt_hash,
            "storage_location": extracted_location,
            "snapshot_id": snapshot_id,
            "items": extracted_items,
        }
    except Exception as e:
        logger.exception(f"Checklist extraction failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "items": []
        }
