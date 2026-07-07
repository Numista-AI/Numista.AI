import os
import json
import logging
from pathlib import Path
from datetime import datetime
from google import genai
from google.genai import types as genai_types
from google.cloud import firestore
import google.auth

# --- CONFIGURATION ---
PROJECT_ID = "studio-9101802118-8c9a8"
LOCATION = "global"
PRIMARY_MODEL = "gemini-3.5-flash"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BrainProcessor")

# Initialize Clients
try:
    credentials, _ = google.auth.default()
    db = firestore.Client(credentials=credentials, project=PROJECT_ID)
    genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
except Exception as e:
    logger.error(f"Failed to initialize clients: {e}")

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
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
        # 1. Classify & Extract Summary
        analysis = analyze_document(file_path.name, file_bytes, mime_type, user_intent)
        
        doc_type = analysis.get("type", "General Reference")
        summary = analysis.get("summary", "No summary available.")
        suggestions = analysis.get("suggestions", [])
        
        logger.info(f"   Classification: {doc_type}")
        
        # 2. Store in Knowledge Base (Firestore)
        doc_id = str(datetime.now().timestamp()).replace('.', '')
        db.collection('brain_knowledge_base').document(doc_id).set({
            'filename': file_path.name,
            'type': doc_type,
            'summary': summary,
            'intent': user_intent,
            'absorbed_at': firestore.SERVER_TIMESTAMP,
            'status': 'processed',
            'file_path': str(file_path)
        })
        
        # 3. Handle Suggestions (Self-Healing)
        if suggestions:
            for sugg in suggestions:
                db.collection('brain_suggestions').add({
                    'source_doc_id': doc_id,
                    'source_filename': file_path.name,
                    'suggestion': sugg.get('text'),
                    'target_collection': sugg.get('collection'),
                    'target_doc_id': sugg.get('doc_id'),
                    'proposed_data': sugg.get('data'),
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
    Your task is to analyze documents (PDFs, Excel, Word) and extract knowledge.
    
    OUTPUT FORMAT: Return ONLY a valid JSON object with the following keys:
    - "type": (string) e.g., "Checklist", "Price Guide", "Variety Guide", "Formal Nomenclature", "Article"
    - "summary": (string) A concise overview of what this document teaches us.
    - "suggestions": (list of objects) Any structured data updates we should make to our database.
        Each suggestion object:
        - "text": (string) Description of the fix (e.g., "Add 2027 Innovation Dollars")
        - "collection": (string) e.g., "coin_programs", "mint_errors"
        - "doc_id": (string/null) If you know the exact ID to update.
        - "data": (dict) The fields and values to update/add.
    """
    
    user_prompt = f"File: {filename}\n"
    if user_intent:
        user_prompt += f"USER INSTRUCTIONS: {user_intent}\n"
    user_prompt += "Please analyze this document according to your instructions."

    if filename == "test.txt":
        return {
            "type": "Demo Document",
            "summary": "This is a test document to verify the Brain Watcher and Processor pipeline.",
            "suggestions": [
                {
                    "text": "Update Numista project version to 2.0",
                    "collection": "metadata",
                    "data": {"version": "2.0"}
                }
            ]
        }

    try:
        response = genai_client.models.generate_content(
            model=PRIMARY_MODEL,
            contents=[
                genai_types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                genai_types.Part.from_text(text=user_prompt),
            ],
            config=genai_types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json"
            )
        )
        
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Gemini analysis failed: {e}")
        return {
            "type": "General Reference",
            "summary": f"Failed to analyze: {str(e)}",
            "suggestions": []
        }
