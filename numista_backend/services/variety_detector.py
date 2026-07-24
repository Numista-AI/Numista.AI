# -*- coding: utf-8 -*-
"""
variety_detector.py
===================
2nd-Stage Gemini Vision Variety & Die-Error Detector.
Analyzes macro photo crops and USB microscope high-resolution frames
for curated high-value targets (e.g. 1955 DDO Lincoln, 1937-D 3-Legged Buffalo,
1942/1 Mercury Dime, Morgan VAMs, 1955-D RPM).
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Curated High-Value Variety Target Database
CURATED_VARIETY_CATALOG = {
    "1955_DDO_CENT": {
        "name": "1955 Doubled Die Obverse (DDO)",
        "denomination": "Cent",
        "key_markers": ["Strong doubling on date '1955'", "Dramatic doubling on 'LIBERTY' and 'IN GOD WE TRUST'"],
        "estimated_premium_multiplier": 50.0,
    },
    "1937_D_3_LEGGED_BUFFALO": {
        "name": "1937-D 3-Legged Buffalo Nickel",
        "denomination": "Five Cents",
        "key_markers": ["Back leg completely missing", "Thigh remains intact", "Pitted surface under belly"],
        "estimated_premium_multiplier": 30.0,
    },
    "1942_1_MERCURY_DIME": {
        "name": "1942/1 Overdate Mercury Dime",
        "denomination": "Dime",
        "key_markers": ["Clear '1' under the '2' in date 1942"],
        "estimated_premium_multiplier": 25.0,
    },
    "MORGAN_VAM_TOP_100": {
        "name": "Morgan Dollar Major VAM Variety",
        "denomination": "Dollar",
        "key_markers": ["Ear doubling", "Die gouges", "Re-punched mint mark", "Clashed dies"],
        "estimated_premium_multiplier": 5.0,
    },
    "1955_D_RPM_CENT": {
        "name": "1955-D Re-punched Mint Mark (RPM)",
        "denomination": "Cent",
        "key_markers": ["Clear D/D repunching south/east"],
        "estimated_premium_multiplier": 10.0,
    }
}

def analyze_variety_crop(base64_image: str, year: str = "", mint_mark: str = "", series: str = "") -> Dict[str, Any]:
    """
    Executes 2nd-stage Gemini Vision prompt targeted at variety detection.
    Enforces the 85% confidence threshold rule:
    If confidence < 85%, returns status 'possible_variety_detected' requiring HITL review.
    """
    try:
        from google import genai
        from google.genai import types
        from config import GEMINI_FLASH_MODEL

        client = genai.Client()
        prompt = f"""
        You are a master numismatic die-variety and error specialist.
        Analyze this macro image / USB microscope crop for coin: Year='{year}', Mint='{mint_mark}', Series='{series}'.

        Target varieties to inspect for:
        1. 1955 DDO Lincoln Cent (dramatic doubling on date & lettering)
        2. 1937-D 3-Legged Buffalo Nickel (missing front/rear leg)
        3. 1942/1 Overdate Mercury Dime (clear 1 under 2)
        4. Morgan Dollar VAM varieties (RPMs, die gouges, doubled dies)
        5. Re-punched mint marks (RPMs) or doubled dies.

        Return ONLY a JSON object with this exact structure:
        {{
            "variety_detected": true/false,
            "variety_name": "Name of variety or 'None'",
            "confidence_score": 0.0 to 100.0,
            "evidence_details": ["Key marker 1 seen", "Key marker 2 seen"],
            "recommended_action": "confirm" or "hitl_review"
        }}
        """

        image_bytes = base64_image
        if "," in image_bytes:
            image_bytes = image_bytes.split(",")[1]

        import base64
        raw_bytes = base64.b64decode(image_bytes)

        response = client.models.generate_content(
            model=GEMINI_FLASH_MODEL,
            contents=[
                types.Part.from_bytes(data=raw_bytes, mime_type="image/jpeg"),
                prompt
            ]
        )

        text_out = response.text.strip()
        if text_out.startswith("```json"):
            text_out = text_out.replace("```json", "").replace("```", "").strip()

        result = json.loads(text_out)
        score = float(result.get("confidence_score", 0.0))

        # Enforce 85% Rule
        if score < 85.0:
            result["status"] = "possible_variety_detected"
            result["requires_hitl"] = True
            result["recommended_action"] = "hitl_review"
        else:
            result["status"] = "variety_confirmed" if result.get("variety_detected") else "no_variety"
            result["requires_hitl"] = False

        return result

    except Exception as e:
        logger.exception("Variety analysis failed")
        return {
            "variety_detected": False,
            "variety_name": "None",
            "confidence_score": 0.0,
            "evidence_details": [f"Analysis error: {str(e)}"],
            "status": "error",
            "requires_hitl": True,
            "recommended_action": "hitl_review"
        }
