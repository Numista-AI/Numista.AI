import os
import json
import logging
import io
import pandas as pd
from pathlib import Path
from datetime import datetime
from google import genai
from google.genai import types as genai_types
from google.cloud import firestore
import google.auth

from config import GEMINI_FLASH_MODEL

# --- CONFIGURATION ---
PROJECT_ID = "studio-9101802118-8c9a8"
LOCATION = "global"
PRIMARY_MODEL = GEMINI_FLASH_MODEL

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BrainProcessor")

# Initialize Clients
db = None
genai_client = None
try:
    credentials, _ = google.auth.default()
    db = firestore.Client(credentials=credentials, project=PROJECT_ID)
    genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    logger.info("BrainProcessor clients initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize clients: {e}")
    raise RuntimeError(f"BrainProcessor cannot start — auth/client init failed: {e}") from e

def absorb_document(file_path: Path, user_intent: str = None):
    """
    The core 'Absorption' pipeline.
    """
    logger.info(f"🧠 Starting absorption for: {file_path.name}")
    
    try:
        # Read file bytes
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        
        mime_type = "application/pdf"
        if file_path.suffix.lower() == ".docx":
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif file_path.suffix.lower() in [".xlsx", ".xls"]:
            # Gemini 3.5 Flash doesn't support Excel directly, convert to CSV
            try:
                logger.info(f"   Converting Excel to CSV for Gemini: {file_path.name}")
                df = pd.read_excel(io.BytesIO(file_bytes))
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                file_bytes = csv_buffer.getvalue().encode('utf-8')
                mime_type = "text/csv"
            except Exception as excel_err:
                logger.error(f"   Excel conversion failed: {excel_err}")
                # Fallback to binary if conversion fails (though it will likely fail in Gemini too)
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif file_path.suffix.lower() in [".png", ".jpg", ".jpeg"]:
            mime_type = f"image/{file_path.suffix.lower()[1:]}"
            if mime_type == "image/jpg": mime_type = "image/jpeg"
            
        # 1. Classify & Extract Summary
        analysis = analyze_document(file_path.name, file_bytes, mime_type, user_intent)
        
        doc_type = analysis.get("type", analysis.get("classification", "General Reference"))
        summary = analysis.get("summary", "No summary available.")
        suggestions = analysis.get("suggestions", [])
        
        logger.info(f"   Classification: {doc_type}")
        
        # 2. Store in Knowledge Base (Firestore)
        # Use filename as part of ID for easier tracking
        doc_id = f"{file_path.stem}_{int(datetime.now().timestamp())}"
        
        # Clean up previous "Failed" entries for this same filename if we just succeeded
        try:
            failed_docs = db.collection('brain_knowledge_base').where('filename', '==', file_path.name).stream()
            for fd in failed_docs:
                fdata = fd.to_dict()
                # If the previous one was a failure, delete it to keep the dashboard clean
                if "Failed to analyze" in fdata.get('summary', '') or "Analysis failed" in fdata.get('summary', ''):
                    logger.info(f"   🗑 Cleaning up previous failed record: {fd.id}")
                    db.collection('brain_knowledge_base').document(fd.id).delete()
        except Exception as clean_err:
            logger.warning(f"   ⚠ Could not clean up old failure records: {clean_err}")

        db.collection('brain_knowledge_base').document(doc_id).set({
            'filename': file_path.name,
            'type': doc_type,
            'summary': summary,
            'intent': user_intent,
            'absorbed_at': firestore.SERVER_TIMESTAMP,
            'status': 'processed',
            'file_path': str(file_path),
            'source_dir': str(file_path.parent)
        })
        
        # 3. Handle Suggestions (Self-Healing)
        if suggestions:
            for sugg in suggestions:
                # Support both naming conventions (Gemini output is inconsistent)
                sug_text = sugg.get('text') or sugg.get('action')
                sug_coll = sugg.get('collection') or sugg.get('target') or "General"
                
                # If both are missing, use a generic description based on the type
                if not sug_text:
                    sug_type = sugg.get('type') or "Update"
                    sug_text = f"{sug_type.replace('_', ' ').title()} for {sug_coll}"
                
                sug_data = sugg.get('data') or sugg
                
                confidence_raw = sugg.get('confidence')
                try:
                    confidence = float(confidence_raw) if confidence_raw is not None else None
                    # Clamp to valid range
                    if confidence is not None:
                        confidence = max(0.0, min(1.0, confidence))
                except (TypeError, ValueError):
                    confidence = None

                db.collection('brain_suggestions').add({
                    'source_doc_id': doc_id,
                    'source_filename': file_path.name,
                    'suggestion': sug_text,
                    'target_collection': sug_coll,
                    'target_doc_id': sugg.get('doc_id'),
                    'proposed_data': sug_data,
                    'confidence': confidence,
                    'status': 'pending',
                    'created_at': firestore.SERVER_TIMESTAMP
                })
            logger.info(f"   Created {len(suggestions)} self-healing suggestions.")
            
        logger.info(f"✅ Document absorbed into Knowledge Base.")
        
    except Exception as e:
        logger.error(f"❌ Failed to absorb document {file_path.name}: {e}")
        raise

def analyze_document(filename: str, file_bytes: bytes, mime_type: str, user_intent: str = None) -> dict:
    """Uses Gemini 3.5 Flash to analyze the document with user intent."""
    
    system_instruction = """
    You are the 'Numista Brain', the core intelligence for a world-class numismatic platform.
    Your task is to analyze documents (PDFs, Excel, Word, Images) and extract knowledge.
    
    OUTPUT FORMAT: Return ONLY a valid JSON object with the following keys:
    - "classification": (string) e.g., "Checklist", "Price Guide", "Variety Guide", "Formal Nomenclature", "Article"
    - "summary": (string) A concise overview of what this document teaches us.
    - "suggestions": (list of objects) Any structured data updates we should make to our database.
        Each suggestion object:
        - "text": (string) Description of the fix (e.g., "Add 2027 Innovation Dollars")
        - "collection": (string) e.g., "coin_programs", "mint_errors"
        - "data": (dict) The fields and values to update/add.
        - "confidence": (float, 0.0 to 1.0) Your confidence that this suggestion is accurate and
          should be applied. Use these guidelines:
          - 0.93–1.00: Directly stated in the source document with no ambiguity.
          - 0.85–0.92: Strongly implied or consistent with well-known numismatic standards.
          - 0.00–0.84: Inferred, ambiguous, or requires cross-referencing another source.
    """
    
    user_prompt = f"""
        Analyze the following document content and provide structured numismatic knowledge.
        
        MISSION BRIEFING: {user_intent or 'Extract any useful numismatic data for the knowledge base.'}
        
        CRITICAL INSTRUCTIONS:
        1. CLASSIFY: Determine if this is a 'Variety Guide', 'Mintage Report', 'Checklist', 'Historical Reference', or 'Transaction Record'.
        2. CONTEXTUALIZE: If this is a 'Transaction Record' or has pricing, label them as 'Historical Observations' with the source and date. DO NOT use as current market value.
        3. EXTRACT DATE: Look for a document date or publication date.
        4. SELF-HEALING: If you find data that expands our database (e.g., a new variety), generate a suggestion.
        
        OUTPUT FORMAT (Strict JSON):
        {{
          "classification": "...",
          "summary": "...",
          "suggestions": [...]
        }}
        """

    # Handle .xlsx conversion to CSV if needed
    if mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        try:
            import pandas as pd
            import io
            print(f"📊 Converting Excel to CSV for AI analysis...")
            df = pd.read_excel(io.BytesIO(file_bytes))
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            file_bytes = csv_buffer.getvalue().encode('utf-8')
            mime_type = "text/csv"
        except Exception as conv_err:
            print(f"⚠ Excel conversion failed: {conv_err}. Attempting raw text fallback.")

    # Handle .docx conversion to text if needed
    if mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            from docx import Document
            import io
            print(f"📝 Converting Word (.docx) to text for AI analysis...")
            doc = Document(io.BytesIO(file_bytes))
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            file_bytes = "\n".join(full_text).encode('utf-8')
            mime_type = "text/plain"
        except Exception as conv_err:
            print(f"⚠ Word conversion failed: {conv_err}. Attempting raw text fallback.")

    try:
        # Use plain strings for text parts and from_bytes for blobs
        # This avoids the "Part.from_text() takes 1 positional argument but 2 were given" error
        # In the new SDK, strings are passed directly as strings, not as Parts.
        response = genai_client.models.generate_content(
            model=PRIMARY_MODEL,
            contents=[
                genai_types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                user_prompt,
            ],
            config=genai_types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json"
            )
        )
        
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Gemini analysis failed for {filename}: {e}")
        return {
            "classification": "General Reference",
            "summary": f"Analysis failed: {str(e)}",
            "suggestions": []
        }
