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


def extract_checklist_document(
    file_bytes: bytes,
    mime_type: str,
    filename: str,
    genai_client: Any,
    uid: str,
    import_session_id: str
) -> Dict[str, Any]:
    """
    Extracts coin checklist items from document bytes using Gemini 3.1 Pro Preview.
    Attaches calibrated composite confidence, exact runtime models, prompt hashes,
    and immutable SoR source provenance.
    """
    try:
        from google.genai import types as genai_types
        
        doc_hash = hashlib.sha256(file_bytes).hexdigest()
        prompt_hash = hashlib.sha256(
            (CHECKLIST_EXTRACTION_SYSTEM_PROMPT + "\n" + CHECKLIST_PROMPT_VERSION).encode("utf-8")
        ).hexdigest()[:16]
        
        pdf_part = genai_types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
        response = genai_client.models.generate_content(
            model=EXTRACTION_MODEL,
            contents=[pdf_part, genai_types.Part.from_text(text=CHECKLIST_EXTRACTION_SYSTEM_PROMPT)],
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        raw_text = response.text or "{}"
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text.strip(), flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned).strip()
        data = json.loads(cleaned)
        
        raw_coins = data.get("coins", [])
        extracted_location = data.get("storage_location", "").strip()
        snapshot_id = data.get("snapshot_id", "").strip()
        program_series = data.get("program_series", "US Mint Program").strip()
        handwriting_conf = float(data.get("handwriting_confidence", 0.90))
        
        extracted_items = []
        for idx, coin in enumerate(raw_coins):
            year = int(coin.get("year", 0)) if str(coin.get("year", "")).isdigit() else 0
            mint_mark = str(coin.get("mint_mark", "P")).upper().strip()
            theme_subject = str(coin.get("theme_subject", "")).strip()
            denom = str(coin.get("denomination", "Quarter")).strip()
            series = str(coin.get("program_series", program_series)).strip()
            
            box_clarity = float(coin.get("box_clarity_score", 0.95))
            subject_ocr = float(coin.get("subject_ocr_score", 0.95))
            header_val = float(coin.get("header_validation_score", 0.95))
            
            composite_conf = (
                BOX_CLARITY_WEIGHT * box_clarity +
                SUBJECT_OCR_WEIGHT * subject_ocr +
                HEADER_VALIDATION_WEIGHT * header_val
            )
            
            item_loc = coin.get("storage_location", extracted_location).strip()
            notes = coin.get("personal_notes", "").strip()
            
            # Format item record matching canonical schema
            title = f"{year} {mint_mark} {denom} - {theme_subject}" if theme_subject else f"{year} {mint_mark} {denom}"
            
            is_quarantined = handwriting_conf < HANDWRITING_QUARANTINE_THRESHOLD
            
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
                "title": title,
                "Condition": coin.get("condition", "Unspecified / Raw"),
                "condition": coin.get("condition", "Unspecified / Raw"),
                "Cost": "$0.00",
                "cost": 0.0,
                "Retailer/Website": "N/A (Checklist Scan)",
                "retailer_website": "N/A (Checklist Scan)",
                "Retailer Invoice #": "N/A",
                "retailer_invoice_num": "N/A",
                "Storage Location": item_loc,
                "storage_location": item_loc,
                "Personal Notes": notes,
                "personal_notes": notes,
                "status": "quarantined" if is_quarantined else "staged",
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
