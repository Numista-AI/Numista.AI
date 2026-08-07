"""
Vision AI, Binder Scan, Auto-Capture Ingestion, and COA Parsing Routes
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Depends, Request
from pydantic import BaseModel, Field

from config import DEFAULT_VISION_MODEL, FALLBACK_VISION_MODEL
from routes.deps import genai_client, genai_types, get_current_user_email

logger = logging.getLogger("numista_backend.scan_routes")

router = APIRouter(prefix="/api", tags=["Vision AI & Binder Scans"])

# ── Schemas ───────────────────────────────────────────────────────────────────

class GcsVisionIdentifyRequest(BaseModel):
    user_email: str
    gcs_obverse_uri: Optional[str] = None
    gcs_reverse_uri: Optional[str] = None
    base64_obverse: Optional[str] = None
    base64_reverse: Optional[str] = None
    save_to_collection: bool = False

class CoaExtractionResponse(BaseModel):
    cert_number: str = ""
    grading_service: str = "PCGS"
    year: Optional[int] = None
    denomination: str = ""
    series: str = ""
    grade_alias: str = ""
    metal_type: str = "Silver"
    purity: float = 0.999
    weight_grams: float = 31.103
    mintage_limit: Optional[int] = None
    issue_price: Optional[float] = None

# ── Helper for Vision Model Call with Resilient Fallback ──────────

def call_vision_model_with_fallback(contents: List[Any], prompt_text: str) -> dict:
    """Invokes Gemini 3.6 Flash with automatic fallback to Gemini 3.5 Flash."""
    if not genai_client:
        raise HTTPException(status_code=500, detail="Vertex AI Client unavailable")

    models_to_try = [DEFAULT_VISION_MODEL, FALLBACK_VISION_MODEL]
    last_err = None

    for model_id in models_to_try:
        try:
            logger.info(f"Invoking vision model: {model_id}")
            resp = genai_client.models.generate_content(
                model=model_id,
                contents=contents + [genai_types.Part.from_text(text=prompt_text)],
                config=genai_types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                ),
            )
            raw = resp.text.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            return json.loads(raw)
        except Exception as e:
            logger.warning(f"Vision model {model_id} failed: {e}")
            last_err = e

    raise HTTPException(status_code=500, detail=f"Vision identification failed on all models: {last_err}")


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("/identify_coin_photo")
async def identify_coin_photo(
    user_email: str = Form(...),
    image_a: Optional[UploadFile] = File(None),
    image_b: Optional[UploadFile] = File(None),
    gcs_obverse_uri: Optional[str] = Form(None),
    gcs_reverse_uri: Optional[str] = Form(None),
    save_to_collection: bool = Form(False),
):
    """
    Multimodal coin identification from obverse + reverse photos.
    Supports direct GCS bucket URIs (gs://...) via zero-copy Part.from_uri() or direct file uploads.
    """
    parts = []

    # 1. Build image parts (GCS URI vs File Bytes)
    if gcs_obverse_uri and gcs_obverse_uri.startswith("gs://"):
        parts.append(genai_types.Part.from_text(text="[Obverse Image]"))
        parts.append(genai_types.Part.from_uri(file_uri=gcs_obverse_uri, mime_type="image/jpeg"))
    elif image_a:
        bytes_a = await image_a.read()
        mime_a = image_a.content_type or "image/jpeg"
        parts.append(genai_types.Part.from_text(text="[Obverse Image]"))
        parts.append(genai_types.Part.from_bytes(data=bytes_a, mime_type=mime_a))

    if gcs_reverse_uri and gcs_reverse_uri.startswith("gs://"):
        parts.append(genai_types.Part.from_text(text="[Reverse Image]"))
        parts.append(genai_types.Part.from_uri(file_uri=gcs_reverse_uri, mime_type="image/jpeg"))
    elif image_b:
        bytes_b = await image_b.read()
        mime_b = image_b.content_type or "image/jpeg"
        parts.append(genai_types.Part.from_text(text="[Reverse Image]"))
        parts.append(genai_types.Part.from_bytes(data=bytes_b, mime_type=mime_b))

    if not parts:
        raise HTTPException(status_code=400, detail="Must provide obverse and reverse images (via upload or GCS URIs)")

    prompt = """
    Identify the coin in the provided obverse/reverse images. Return JSON matching:
    {
        "year": 1921,
        "denomination": "Dollar",
        "series": "Morgan Silver Dollar",
        "mint_mark": "S",
        "grade": "MS-63",
        "estimated_value": 75.0,
        "confidence": 0.95,
        "slang_mapped": true
    }
    """

    result = call_vision_model_with_fallback(parts, prompt)

    # Normalize integer year and canonical denomination
    try:
        if "year" in result and result["year"]:
            result["year"] = int(result["year"])
    except (ValueError, TypeError):
        pass

    return {
        "status": "success",
        "coin": result,
        "saved": save_to_collection
    }


@router.post("/v1/coa/parse", response_model=CoaExtractionResponse)
async def api_parse_coa(file: UploadFile = File(...)):
    """Parse scanned US Mint / PCGS / NGC COA card and extract typed serial numbers and specs."""
    content = await file.read()
    filename = file.filename or "coa_scan.jpg"
    mime_type = file.content_type or "image/jpeg"

    if genai_client:
        try:
            part_img = genai_types.Part.from_bytes(data=content, mime_type=mime_type)
            prompt = """
            Extract metadata from this Certificate of Authenticity (COA) card into JSON:
            {
                "cert_number": "12345678",
                "grading_service": "PCGS",
                "year": 2026,
                "denomination": "$1",
                "series": "American Silver Eagle",
                "grade_alias": "MS-70",
                "metal_type": "Silver",
                "purity": 0.999,
                "weight_grams": 31.103,
                "mintage_limit": 50000,
                "issue_price": 75.00
            }
            """
            data = call_vision_model_with_fallback([part_img], prompt)
            return CoaExtractionResponse(**data)
        except Exception as e:
            logger.warning(f"COA Gemini parsing fallback: {e}")

    # Return default empty structured schema if parsing fails
    return CoaExtractionResponse(
        cert_number="UNKNOWN",
        grading_service="US Mint",
        series="Commemorative",
    )
