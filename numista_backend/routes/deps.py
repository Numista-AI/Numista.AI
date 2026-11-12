"""
routes/deps.py
--------------
Centralized dependencies, shared database clients, logging, and authentication middleware
for all Numista.AI APIRouters.
"""

import os
import logging
from datetime import datetime, timezone
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
MODEL_FLASH = "gemini-3.8-flash"
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
    """Extracts Authorization Bearer token (or query token) and verifies via Firebase Admin SDK."""
    auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split("Bearer ")[1].strip()
    elif request.query_params.get("token"):
        token = request.query_params.get("token", "").strip()
    if not token:
        return None
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        logger.warning(f"Firebase token verification failed: {e}")
        return None

async def get_current_user(request: Request) -> Dict[str, Any]:
    """FastAPI dependency requiring a valid Firebase ID Token."""
    if hasattr(request.state, "user") and request.state.user:
        return request.state.user
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
    """FastAPI dependency requiring the Firebase custom claim 'admin': True.

    The email allowlist (eric@, admin@) has been intentionally removed — an unverified
    signup with those addresses would bypass this guard. Admin status is granted only
    by the bootstrap_admin_claim.py script via the Firebase Admin SDK.
    """
    if user.get("admin") is not True:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user


def check_and_increment_rate_cap(uid: str, endpoint: str, daily_limit: int, is_admin: bool = False) -> None:
    """Per-user daily cap helper storing counts in _rate_limits/{uid}/{endpoint}/{YYYY-MM-DD}.

    1. Reads Firestore _rate_limits/{uid}/{endpoint}/{today_date} doc
    2. If count >= daily_limit: raise HTTPException(429, "Daily limit reached")
    3. Else: increment count atomically (use Firestore Increment)
    4. If Firestore read fails: raise HTTPException(429) - fail closed
    Admin users are exempt.
    """
    if is_admin:
        return
    today_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    clean_uid = str(uid).strip()
    clean_endpoint = str(endpoint).strip().lstrip("/")
    doc_ref = db.collection("_rate_limits").document(clean_uid).collection(clean_endpoint).document(today_date)
    try:
        snap = doc_ref.get()
        current_count = 0
        if snap.exists:
            data = snap.to_dict() or {}
            current_count = data.get("count", 0)
        if current_count >= daily_limit:
            raise HTTPException(status_code=429, detail="Daily limit reached")
        doc_ref.set({"count": firestore.Increment(1)}, merge=True)
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Rate cap check failed for {clean_uid}/{clean_endpoint}: {e}")
        raise HTTPException(status_code=429, detail="Daily limit reached")


_check_and_increment_rate_cap = check_and_increment_rate_cap


MORGAN_WEB_LOOKUP_GLOBAL_DAILY_LIMIT = 50
MORGAN_WEB_LOOKUP_USER_DAILY_LIMIT = 3


def is_morgan_web_lookup_enabled() -> bool:
    """Returns True when M4 Morgan web lookup is enabled (default: true)."""
    return os.environ.get("M4_WEB_LOOKUP_ENABLED", "true").strip().lower() == "true"


def _safe_doc_count(snap) -> int:
    """Safely extracts a non-negative integer count from a Firestore DocumentSnapshot."""
    if snap is None or not getattr(snap, "exists", False):
        return 0
    raw = (snap.to_dict() or {}).get("count")
    try:
        return max(0, int(raw or 0))
    except (ValueError, TypeError):
        return 0


def _execute_dual_rate_cap_logic(
    get_fn,
    set_fn,
    user_ref,
    global_ref,
    per_user_limit: int,
    global_limit: int,
    is_admin: bool,
) -> Dict[str, int]:
    """Shared read-check-increment logic for both real Firestore transactions and unit tests."""
    global_count = _safe_doc_count(get_fn(global_ref))
    user_count = 0 if is_admin else _safe_doc_count(get_fn(user_ref))

    if global_count >= global_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Global daily Morgan web lookup limit reached ({global_limit}/day). Please try again tomorrow.",
        )

    if not is_admin and user_count >= per_user_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Your daily Morgan web lookup limit reached ({per_user_limit}/day). Please try again tomorrow.",
        )

    set_fn(
        global_ref,
        {"count": global_count + 1, "updated_at": firestore.SERVER_TIMESTAMP},
    )
    if not is_admin:
        set_fn(
            user_ref,
            {"count": user_count + 1, "updated_at": firestore.SERVER_TIMESTAMP},
        )

    return {
        "user_used": 0 if is_admin else user_count + 1,
        "user_limit": per_user_limit,
        "user_remaining": per_user_limit if is_admin else max(0, per_user_limit - (user_count + 1)),
        "global_used": global_count + 1,
        "global_limit": global_limit,
        "global_remaining": max(0, global_limit - (global_count + 1)),
    }


def check_and_increment_dual_rate_cap(
    uid: str,
    endpoint: str,
    per_user_limit: int = MORGAN_WEB_LOOKUP_USER_DAILY_LIMIT,
    global_limit: int = MORGAN_WEB_LOOKUP_GLOBAL_DAILY_LIMIT,
    is_admin: bool = False,
) -> Dict[str, int]:
    """Atomically enforces both a per-user daily cap and a global daily cap in one Firestore transaction."""
    if os.environ.get("M4_WEB_LOOKUP_RATE_LIMIT_ENABLED", "true").strip().lower() != "true":
        return {
            "user_used": 0,
            "user_limit": per_user_limit,
            "user_remaining": per_user_limit,
            "global_used": 0,
            "global_limit": global_limit,
            "global_remaining": global_limit,
        }

    clean_uid = str(uid or "").strip()
    clean_endpoint = str(endpoint or "").strip().lstrip("/")
    if not clean_uid or clean_uid == "_global" or not clean_endpoint:
        raise HTTPException(
            status_code=429,
            detail="Web lookup rate limit check unavailable. Please try again shortly.",
        )

    today_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    user_ref = (
        db.collection("_rate_limits")
        .document(clean_uid)
        .collection(clean_endpoint)
        .document(today_date)
    )
    global_ref = (
        db.collection("_rate_limits")
        .document("_global")
        .collection(clean_endpoint)
        .document(today_date)
    )

    try:
        transaction = db.transaction()

        @firestore.transactional
        def _txn_step(txn):
            return _execute_dual_rate_cap_logic(
                get_fn=lambda ref: ref.get(transaction=txn),
                set_fn=lambda ref, payload: txn.set(ref, payload, merge=True),
                user_ref=user_ref,
                global_ref=global_ref,
                per_user_limit=per_user_limit,
                global_limit=global_limit,
                is_admin=is_admin,
            )

        return _txn_step(transaction)
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Dual rate cap check failed for {clean_uid}/{clean_endpoint}: {e}")
        raise HTTPException(
            status_code=429,
            detail="Web lookup rate limit check unavailable. Please try again shortly.",
        )


def get_dual_rate_cap_quota(
    uid: str,
    endpoint: str = "morgan_web_lookup",
    per_user_limit: int = MORGAN_WEB_LOOKUP_USER_DAILY_LIMIT,
    global_limit: int = MORGAN_WEB_LOOKUP_GLOBAL_DAILY_LIMIT,
    is_admin: bool = False,
) -> Dict[str, Any]:
    """Read-only inspection of current per-user and global daily usage (0 writes)."""
    enabled = is_morgan_web_lookup_enabled()
    rate_limit_enabled = (
        os.environ.get("M4_WEB_LOOKUP_RATE_LIMIT_ENABLED", "true").strip().lower() == "true"
    )
    if not rate_limit_enabled:
        return {
            "enabled": enabled,
            "rate_limit_enabled": False,
            "user_used": 0,
            "user_limit": per_user_limit,
            "user_remaining": per_user_limit,
            "global_used": 0,
            "global_limit": global_limit,
            "global_remaining": global_limit,
        }

    clean_uid = str(uid or "").strip()
    clean_endpoint = str(endpoint or "").strip().lstrip("/")
    if not clean_uid or clean_uid == "_global" or not clean_endpoint:
        raise HTTPException(
            status_code=429,
            detail="Web lookup rate limit check unavailable. Please try again shortly.",
        )

    today_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    global_ref = (
        db.collection("_rate_limits")
        .document("_global")
        .collection(clean_endpoint)
        .document(today_date)
    )
    user_ref = (
        db.collection("_rate_limits")
        .document(clean_uid)
        .collection(clean_endpoint)
        .document(today_date)
    )

    try:
        global_used = _safe_doc_count(global_ref.get())
        user_used = 0 if is_admin else _safe_doc_count(user_ref.get())
    except Exception as e:
        logger.warning(f"Quota read failed for {clean_uid}/{clean_endpoint}: {e}")
        raise HTTPException(
            status_code=429,
            detail="Web lookup rate limit check unavailable. Please try again shortly.",
        )

    return {
        "enabled": enabled,
        "rate_limit_enabled": True,
        "user_used": user_used,
        "user_limit": per_user_limit,
        "user_remaining": per_user_limit if is_admin else max(0, per_user_limit - user_used),
        "global_used": global_used,
        "global_limit": global_limit,
        "global_remaining": max(0, global_limit - global_used),
    }


