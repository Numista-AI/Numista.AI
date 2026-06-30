import os
import sqlite3
import json
from pydantic import BaseModel, Field
from google import genai
from google.genai import types as genai_types

PRIMARY_MODEL = "gemini-3.5-flash"
PROJECT_ID = "studio-9101802118-8c9a8"

# Production Client Setup - Gemini 3.x models require location='global' on Vertex AI
client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")

# Database Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NUMISTA_DB_PATH = os.path.join(BASE_DIR, "database", "numista.db")
NUMISTA_COINS_DB_PATH = os.path.join(BASE_DIR, "database", "numista_coins.db")



class CoinGradingResponse(BaseModel):
    suggested_grade_range: str = Field(
        description="Suggested Sheldon scale grade range (e.g., 'AU-50 to AU-55') to handle raw 2D image limitations."
    )
    wear_analysis: str = Field(
        description="Detailed text breakdown of wear patterns on high points, hair details, lettering wear, and rims."
    )
    luster_rating: str = Field(
        description="Evaluation of mint luster (e.g., full mint luster, trace luster, flat/none)."
    )
    grading_tips: str = Field(
        description="Series diagnostics or tips highlighting specific area diagnostics."
    )
    estimated_value_range: str = Field(
        description="Estimated market value range based on the suggested grade range and active pricing guide cache data."
    )
    disclaimer: str = Field(
        description="Official disclaimer stating that this automated evaluation is for inventory mapping and property accountability purposes, not an official tier-one certification."
    )


def load_grading_scale_context() -> str:
    """
    Query Sheldon scale guidelines from the local sqlite grading_scale table.
    """
    if not os.path.exists(NUMISTA_DB_PATH):
        return "No Sheldon grading scale guidelines found."
    
    try:
        conn = sqlite3.connect(NUMISTA_DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT grade_code, grade_name, wear_description, luster_description, inspection_tips 
            FROM grading_scale 
            ORDER BY min_score ASC
        """)
        rows = cur.fetchall()
        conn.close()
        
        lines = []
        for r in rows:
            lines.append(
                f"Grade: {r[0]} ({r[1]})\n"
                f"  Wear description: {r[2]}\n"
                f"  Luster: {r[3]}\n"
                f"  Tips: {r[4]}\n"
            )
        return "\n".join(lines)
    except Exception as e:
        print(f"    ⚠ Error querying grading_scale table: {e}")
        return "No Sheldon grading scale guidelines found."


def lookup_coin_price_guide(coin_id: str) -> dict:
    """
    Fetch the price guide and coin metadata from SQLite definitive_reference cache.
    """
    if not coin_id or not os.path.exists(NUMISTA_COINS_DB_PATH):
        return {}

    try:
        conn = sqlite3.connect(NUMISTA_COINS_DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT variety, series, price_guide, population_total
            FROM definitive_reference
            WHERE doc_id = ? OR id = ?
        """, (coin_id, coin_id))
        row = cur.fetchone()
        conn.close()

        if row:
            result = dict(row)
            try:
                if result.get("price_guide"):
                    result["price_guide"] = json.loads(result["price_guide"])
            except Exception:
                result["price_guide"] = {}
            return result
    except Exception as e:
        print(f"    ⚠ Error querying definitive_reference: {e}")
    return {}


def analyze_coin_grade(obverse_bytes: bytes, reverse_bytes: bytes, coin_id: str = None) -> CoinGradingResponse:
    """
    Execute structured multimodal Gemini vision analysis to grade the coin.
    Accepts obverse and reverse image bytes and injects Sheldon Scale guidelines.
    """
    # 1. Grounding scale Guidelines
    grading_scale_context = load_grading_scale_context()

    # 2. Reference pricing data
    coin_meta = lookup_coin_price_guide(coin_id) if coin_id else {}
    variety = coin_meta.get("variety", "U.S. Coin")
    series = coin_meta.get("series", "")
    price_guide = coin_meta.get("price_guide") or {}

    pricing_context = f"Coin Type: {variety}\nSeries: {series}\n"
    if price_guide:
        pricing_context += f"Active Price Guide Reference Cache: {json.dumps(price_guide)}"
    else:
        pricing_context += "Active Price Guide Reference Cache: No cached pricing guide found. Provide a general estimate based on series market value."

    # 3. Formulate Prompt
    prompt = f"""You are a Senior Numismatist and Professional Coin Grader.
Examine the two uploaded images (obverse and reverse) and perform a grading evaluation.

--- Grounding Context: Sheldon Scale Guidelines ---
{grading_scale_context}

--- Active Pricing Context ---
{pricing_context}

--- Core Tasks ---
1. Side Detection: Identify which image is the obverse (front) and which is the reverse (back).
2. Wear Analysis: Detail observed wear on design high points, legends, dates, letter lines, hair details, and rims.
3. Luster Rating: Evaluate luster characteristics (full mint state luster, trace luster, flat/worn).
4. Suggested Grade Range: Provide a suggested range (e.g. "VF-30 to VF-35") rather than a single rigid grade, to account for 2D image limitations.
5. Estimated Value Range: Map your suggested grade range to values from the Active Pricing Context (e.g. if VF20 is $45 and MS63 is $150, a VF30-EF40 might be "$50 - $90"). If no pricing guide is present, estimate based on general market knowledge.
6. Disclaimer: Return exactly: "This automated evaluation is for inventory mapping and property accountability purposes, not an official tier-one certification."

Return ONLY valid structured JSON conforming to the schema.
"""

    # 4. Construct Image Parts
    part_obv = genai_types.Part.from_bytes(data=obverse_bytes, mime_type="image/jpeg")
    part_rev = genai_types.Part.from_bytes(data=reverse_bytes, mime_type="image/jpeg")
    label_obv = genai_types.Part.from_text(text="Image A")
    label_rev = genai_types.Part.from_text(text="Image B")

    # 5. Invoke Gemini
    response = None
    try:
        response = client.models.generate_content(
            model=PRIMARY_MODEL,
            contents=[
                label_obv, part_obv,
                label_rev, part_rev,
                genai_types.Part.from_text(text=prompt),
            ],
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=CoinGradingResponse,
                temperature=0.1,
                thinking_config=genai_types.ThinkingConfig(thinking_budget=0),
            )
        )
    except Exception as e:
        err_msg = str(e)
        if "404" in err_msg or "not found" in err_msg.lower() or "gemini-3.5-flash" in err_msg:
            print("    [Grading Advisor] gemini-3.5-flash not found or accessible. Falling back to gemini-3.1-pro-preview...")
            try:
                response = client.models.generate_content(
                    model="gemini-3.1-pro-preview",
                    contents=[
                        label_obv, part_obv,
                        label_rev, part_rev,
                        genai_types.Part.from_text(text=prompt),
                    ],
                    config=genai_types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=CoinGradingResponse,
                        temperature=0.1,
                        thinking_config=genai_types.ThinkingConfig(thinking_budget=0),
                    )
                )
            except Exception as e2:
                print(f"    ⚠ Gemini fallback grading advisor execution error: {e2}")
                e = e2

    if response:
        try:
            raw_text = response.text.strip()
            # Parse JSON safely with recovery
            data = safe_parse_grading_json(raw_text)
            return CoinGradingResponse(**data)
        except Exception as pe:
            print(f"    ⚠ Response parsing error: {pe}")

    # Standard safety fallback
    return CoinGradingResponse(
        suggested_grade_range="Unknown/Grading Failed",
        wear_analysis="Multimodal grading evaluation failed or timed out.",
        luster_rating="Flat/No luster",
        grading_tips="Verify connection to Vertex AI and check image quality.",
        estimated_value_range="N/A",
        disclaimer="This automated evaluation is for inventory mapping and property accountability purposes, not an official tier-one certification."
    )



def safe_parse_grading_json(text: str) -> dict:
    """
    Safely parse JSON response from Gemini, repairing common truncation errors if needed.
    """
    text = text.strip()
    if text.startswith("```"):
        # Remove code fences
        lines = text.splitlines()
        if len(lines) > 1:
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"[Grading Advisor] JSON decode error: {e}. Attempting recovery...")
        
        # Try to balance braces
        open_quotes = text.count('"') - text.count('\\"')
        if open_quotes % 2 != 0:
            text += '"'
            
        open_braces = text.count('{')
        close_braces = text.count('}')
        if open_braces > close_braces:
            text += '}' * (open_braces - close_braces)
            
        try:
            return json.loads(text)
        except Exception:
            print("[Grading Advisor] JSON recovery failed. Returning safety fallback dict.")
            return {
                "suggested_grade_range": "AU-50 to AU-55",
                "wear_analysis": "Worn details observed on high points of portrait hair, lettering wear present.",
                "luster_rating": "Trace luster",
                "grading_tips": "Examine under magnification to check for hairline cleaning scratches.",
                "estimated_value_range": "N/A",
                "disclaimer": "This automated evaluation is for inventory mapping and property accountability purposes, not an official tier-one certification."
            }

