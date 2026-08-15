"""
Numista.AI Multi-Modal Document Classifier Service
Classifies uploaded documents (Checklist, Invoice/Receipt, Slab Certificate)
using Gemini 3.7 Flash and geometric/structural layout analysis.
"""

import json
import logging
import re
from typing import Dict, Any, Tuple
from config.ingestion_config import CLASSIFIER_MODEL, CLASSIFIER_CONFIDENCE_THRESHOLD

logger = logging.getLogger("numista_backend.document_classifier")

CLASSIFIER_PROMPT = """
You are an expert numismatic document analyst. Analyze this uploaded document image/PDF and classify its type.
Determine whether it is:
1. "checklist": A checklist, inventory grid, collection tally sheet, or coin program table (e.g. Numista.AI Program Checklist, Dansco page, Whitman checklist, Whitman table, table with Year/Subject/Mint Mark columns with checkmarks/handwriting).
2. "invoice": A commercial purchase receipt, store order confirmation, Littleton Coin invoice, APMEX receipt, US Mint order receipt, or dealer invoice with itemized prices and totals.
3. "certificate": A third-party grading service certificate, PCGS/NGC slab photo, or authenticity certificate.
4. "unknown": Document cannot be determined.

Return ONLY a JSON object with this exact schema:
{
  "document_type": "checklist" | "invoice" | "certificate" | "unknown",
  "confidence": 0.0 to 1.0,
  "detected_program_or_vendor": "Identified coin program (e.g. American Women Quarters) or Vendor (e.g. Littleton)",
  "page_count_estimated": 1,
  "has_handwritten_notes": true | false,
  "rationale": "Brief reason for classification"
}
"""

def classify_document_bytes(
    file_bytes: bytes,
    mime_type: str,
    genai_client: Any
) -> Dict[str, Any]:
    """
    Classifies document bytes using Gemini 3.7 Flash multimodal analysis.
    """
    try:
        from google.genai import types as genai_types
        part = genai_types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
        response = genai_client.models.generate_content(
            model=CLASSIFIER_MODEL,
            contents=[part, genai_types.Part.from_text(text=CLASSIFIER_PROMPT)],
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        raw_text = response.text or "{}"
        # Strip fences if present
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text.strip(), flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned).strip()
        data = json.loads(cleaned)
        
        doc_type = data.get("document_type", "unknown").lower()
        confidence = float(data.get("confidence", 0.5))
        
        requires_confirmation = confidence < CLASSIFIER_CONFIDENCE_THRESHOLD
        
        return {
            "document_type": doc_type,
            "confidence": confidence,
            "detected_program_or_vendor": data.get("detected_program_or_vendor", ""),
            "has_handwritten_notes": bool(data.get("has_handwritten_notes", False)),
            "requires_confirmation": requires_confirmation,
            "rationale": data.get("rationale", ""),
        }
    except Exception as e:
        logger.exception(f"Document classification failed: {e}")
        return {
            "document_type": "unknown",
            "confidence": 0.0,
            "detected_program_or_vendor": "",
            "has_handwritten_notes": False,
            "requires_confirmation": True,
            "rationale": f"Classifier error: {str(e)}",
        }
