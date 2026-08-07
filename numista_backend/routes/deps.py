"""
routes/deps.py
--------------
Centralized dependencies, shared database clients, logging, and authentication middleware
for all Numista.AI APIRouters.
"""

import os
import logging
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, Depends
from google.cloud import firestore, storage as gcs
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from google import genai
from google.genai import types as genai_types

logger = logging.getLogger("numista_backend.deps")

PROJECT_ID = "studio-9101802118-8c9a8"

# ── 1. Firestore & Storage Singletons ─────────────────────────────────────────
db = firestore.Client(project=PROJECT_ID)
storage_client = gcs.Client(project=PROJECT_ID)

# ── 2. Google GenAI Client (google-genai==1.71.0 Vertex AI standard) ───────────
try:
    genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")
    logger.info("Successfully initialized Vertex AI Google GenAI Client.")
except Exception as ge:
    logger.warning(f"Failed to initialize Vertex AI GenAI Client: {ge}")
    genai_client = None

# Model Constants (Rule 6 compliant)
MODEL_FLASH = "gemini-3.6-flash"
MODEL_PRO = "gemini-3.1-pro-preview"

# ── 3. Firebase Admin SDK Initialization ──────────────────────────────────────
if not firebase_admin._apps:
    sa_path = os.path.join(os.path.dirname(__file__), "..", "serviceAccountKey.json")
    if not os.path.exists(sa_path):
        sa_path = os.path.join(os.path.dirname(__file__), "..", "serviceAccountKey.json.json")
    if os.path.exists(sa_path):
        cred = credentials.Certificate(sa_path)
        firebase_admin.initialize_app(cred, {'projectId': PROJECT_ID})
    else:
        firebase_admin.initialize_app(options={'projectId': PROJECT_ID})

# ── 4. Authentication Middleware Dependencies ─────────────────────────────────

def verify_firebase_bearer_token(request: Request) -> Optional[Dict[str, Any]]:
    """Extracts Authorization Bearer token and verifies via Firebase Admin SDK."""
    auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split("Bearer ")[1].strip()
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        logger.warning(f"Firebase token verification failed: {e}")
        return None

async def get_current_user(request: Request) -> Dict[str, Any]:
    """FastAPI dependency requiring a valid Firebase ID Token."""
    is_prod = os.environ.get("K_SERVICE") or os.environ.get("ENVIRONMENT") == "production"
    decoded = verify_firebase_bearer_token(request)
    if not decoded:
        if not is_prod and os.environ.get("ALLOW_UNAUTHENTICATED") == "1":
            return {"email": "dev_guest@numista.ai", "uid": "dev_guest_uid", "admin": False}
        raise HTTPException(status_code=401, detail="Authentication token missing or invalid")
    return decoded

async def get_current_user_email(request: Request, user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """FastAPI dependency returning verified user email from token."""
    email = user.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="User email not present in authentication token")
    return email

async def require_admin_user(request: Request, user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """FastAPI dependency requiring custom claim ('admin': True) or designated admin email."""
    is_admin = user.get("admin") is True or user.get("email") in ["admin@numista.ai", "eric@numista.ai"]
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user
