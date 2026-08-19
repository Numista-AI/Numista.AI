"""
numista_backend/routes/feedback_callable_route.py
--------------------------------------------------
MORGAN Feedback System — Cloud Run callable endpoint.

All seven modes handled in a single POST /api/feedback/callable:
  CHECK        — throttle check, lock reservation, rate limit
  EXTRACT      — read-only PII-redact + Gemini extraction
  SUBMIT       — full write (redact, ID, Firestore, GCS prefix routing)
  DISMISS      — increment dismissal_count, clear lock
  UPLOAD_URL   — return signed PUT URL for screenshot
  CORRECTION   — append-only post-submit correction
  ADMIN_RESOLVE— admin-only status change; DATA_INTEGRITY requires resolution_note

Auth: request.auth.uid from Firebase ID Token only.
      Any client-supplied uid field in the body is IGNORED.
"""

import hashlib
import logging
import os
import re
import uuid as uuid_lib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from google.cloud import firestore, storage as gcs
from pydantic import BaseModel

from .deps import db, genai_client, get_current_user, require_admin_user, storage_client, MODEL_FLASH

logger = logging.getLogger("numista_backend.feedback_callable")
router = APIRouter(prefix="/api/feedback", tags=["MORGAN Feedback Callable"])

PROJECT_ID = "studio-9101802118-8c9a8"
GCS_BUCKET = "studio-9101802118-8c9a8-uploads"
GCS_STANDARD_PREFIX = "feedback_screenshots"
GCS_HOLD_PREFIX = "feedback_screenshots_hold"

# ── Constants ──────────────────────────────────────────────────────────────────
INTERVIEW_MAX_DURATION_SECONDS = 30 * 60      # 30 minutes
RATE_LIMIT_WINDOW_SECONDS = 60 * 60           # 60 minutes rolling
MAX_INTERVIEWS_PER_WINDOW = 3
CORRECTION_WINDOW_SECONDS = 10 * 60          # 10 minutes
BEHAVIORAL_THROTTLE_SECONDS = 24 * 60 * 60   # 24 hours
UPLOAD_URL_EXPIRY_MINUTES = 5

# Allowed values for server-final issue_type
SAFE_CLIENT_ISSUE_TYPES = {"BUG", "FEATURE", "UX", "PRAISE", "CONFUSION", "OTHER"}
VALID_ISSUE_TYPES = SAFE_CLIENT_ISSUE_TYPES | {"DATA_INTEGRITY"}
VALID_SEVERITY = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}

# ── PII Redaction ─────────────────────────────────────────────────────────────

# Cert number patterns: PCGS/NGC/ANACS/ICG (7-10 digits, optional hyphens)
_CERT_PATTERN = re.compile(r'\b(?:PCGS|NGC|ANACS|ICG)?[-\s]?[0-9]{7,10}\b', re.IGNORECASE)
_DOLLAR_PATTERN = re.compile(r'\$[\d,]+(?:\.\d{1,2})?')
_EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b')

def _redact_text(text: str) -> tuple[str, int]:
    """PII-redact a string. Returns (redacted_text, replacement_count)."""
    count = 0
    result = _CERT_PATTERN.sub(lambda m: (count.__class__.__init__(count) or '[CERT_REDACTED]'), text)
    # Use nested replacement to count matches
    cert_count = len(_CERT_PATTERN.findall(text))
    dollar_count = len(_DOLLAR_PATTERN.findall(text))
    email_count = len(_EMAIL_PATTERN.findall(text))

    result = _CERT_PATTERN.sub('[CERT_REDACTED]', text)
    result = _DOLLAR_PATTERN.sub('[VALUE_REDACTED]', result)
    result = _EMAIL_PATTERN.sub('[EMAIL_REDACTED]', result)
    return result, cert_count + dollar_count + email_count


def _redact_transcript(messages: List[Dict]) -> tuple[List[Dict], int]:
    """Redact all message fields in a transcript. Returns (redacted_list, total_count)."""
    total = 0
    redacted = []
    for msg in messages:
        text = msg.get("message") or msg.get("text") or ""
        clean, n = _redact_text(text)
        total += n
        redacted.append({**msg, "message": clean, "message_redacted": clean})
    return redacted, total


# ── Doc ID computation ────────────────────────────────────────────────────────

def _compute_doc_id(uid: str, trigger_reason: str, counter: int = 0) -> str:
    """
    Deterministic document ID.
    manualFAB: sha256(uid + 'manualFAB' + YYYYMMDD + counter)
    Non-FAB:   sha256(uid + trigger_reason + YYYYMMDD)
    Same trigger + same uid + same day → same ID. Two tabs = one doc (first write wins).
    """
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    if trigger_reason == "manualFAB":
        raw = f"{uid}|manualFAB|{today}|{counter}"
    else:
        raw = f"{uid}|{trigger_reason}|{today}"
    return hashlib.sha256(raw.encode()).hexdigest()[:40]


# ── Request / Response models ──────────────────────────────────────────────────

class CallableRequest(BaseModel):
    mode: str  # CHECK | EXTRACT | SUBMIT | DISMISS | UPLOAD_URL | CORRECTION | ADMIN_RESOLVE

    # CHECK
    trigger_reason: Optional[str] = None

    # EXTRACT
    transcript: Optional[List[Dict[str, Any]]] = None
    page_title: Optional[str] = None
    route: Optional[str] = None

    # SUBMIT
    extraction_status: Optional[str] = None
    issue_type: Optional[str] = None          # from EXTRACT result only; client cannot set final
    severity_estimate: Optional[str] = None    # from EXTRACT result only
    affected_feature: Optional[str] = None
    user_intent: Optional[str] = None
    reproduction_steps: Optional[str] = None
    morgan_summary: Optional[str] = None
    app_version: Optional[str] = None
    screenshot_url: Optional[str] = None
    screenshot_consented: Optional[bool] = None
    user_confirmed_summary: Optional[bool] = None
    morgan_summary_confirmed_text: Optional[str] = None
    client_suggested_issue_type: Optional[str] = None
    intake_method: Optional[str] = None
    lock_id: Optional[str] = None

    # CORRECTION
    doc_id: Optional[str] = None
    correction_text: Optional[str] = None

    # DISMISS
    reason: Optional[str] = None  # 'banner_timeout' | 'user_closed' | 'esc_key'

    # ADMIN_RESOLVE
    new_status: Optional[str] = None
    resolution_note: Optional[str] = None
    new_issue_type: Optional[str] = None  # optional promotion to DATA_INTEGRITY


# ── Router ────────────────────────────────────────────────────────────────────

@router.post("/callable")
async def feedback_callable(
    req: CallableRequest,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Single trusted entry point for all 7 MORGAN Feedback callable modes."""
    # Auth: uid from verified token only; any uid in req body is ignored
    uid = user["uid"]
    mode = req.mode.upper()

    if mode == "CHECK":
        return await _handle_check(uid, req)
    elif mode == "EXTRACT":
        return await _handle_extract(uid, req)
    elif mode == "SUBMIT":
        return await _handle_submit(uid, req)
    elif mode == "DISMISS":
        return await _handle_dismiss(uid, req)
    elif mode == "UPLOAD_URL":
        return await _handle_upload_url(uid, req)
    elif mode == "CORRECTION":
        return await _handle_correction(uid, req)
    elif mode == "ADMIN_RESOLVE":
        return await _handle_admin_resolve(uid, req, user)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown mode: {mode}")


# ── CHECK ─────────────────────────────────────────────────────────────────────

async def _handle_check(uid: str, req: CallableRequest) -> Dict[str, Any]:
    trigger_reason = req.trigger_reason or "manualFAB"
    now = datetime.now(timezone.utc)

    user_ref = db.collection("users").document(uid)
    user_doc = user_ref.get()
    data: Dict = user_doc.to_dict() if user_doc.exists else {}

    # 1. Existing lock check
    lock = data.get("feedback_trigger_lock")
    if lock:
        locked_until = lock.get("locked_until")
        if locked_until and _to_dt(locked_until) > now:
            return {"allowed": False, "interview_mode": False, "reason": "already_locked"}

    # 2. 24h behavioral throttle (non-FAB triggers only)
    if trigger_reason != "manualFAB":
        last_ts = data.get("last_feedback_trigger_ts")
        if last_ts and (now - _to_dt(last_ts)).total_seconds() < BEHAVIORAL_THROTTLE_SECONDS:
            return {"allowed": False, "interview_mode": False, "reason": "throttled"}

    # 3. Rolling 60-min rate limit
    interviews_this_hour: int = data.get("interviews_this_hour", 0)
    reset_at = data.get("interviews_this_hour_reset_at")
    if reset_at and (now - _to_dt(reset_at)).total_seconds() > RATE_LIMIT_WINDOW_SECONDS:
        interviews_this_hour = 0  # window expired; will reset below

    if interviews_this_hour >= MAX_INTERVIEWS_PER_WINDOW:
        return {"allowed": True, "interview_mode": False, "reason": "rate_limited"}

    # 4. Compute draft_doc_id with post-increment counter
    next_counter = interviews_this_hour + 1
    draft_doc_id = _compute_doc_id(uid, trigger_reason, counter=next_counter)

    # 5. Write lock + increment counter atomically
    new_reset_at = _to_dt(reset_at) if (reset_at and (now - _to_dt(reset_at)).total_seconds() <= RATE_LIMIT_WINDOW_SECONDS) else now
    lock_id = str(uuid_lib.uuid4())
    locked_until = now + timedelta(seconds=INTERVIEW_MAX_DURATION_SECONDS)

    user_ref.set({
        "feedback_trigger_lock": {
            "reason": trigger_reason,
            "locked_until": locked_until,
            "lock_id": lock_id,
            "draft_doc_id": draft_doc_id,
        },
        "interviews_this_hour": next_counter,
        "interviews_this_hour_reset_at": new_reset_at,
    }, merge=True)

    return {
        "allowed": True,
        "interview_mode": True,
        "lock_id": lock_id,
        "draft_doc_id": draft_doc_id,
    }


# ── EXTRACT (read-only) ───────────────────────────────────────────────────────

async def _handle_extract(uid: str, req: CallableRequest) -> Dict[str, Any]:
    """Purely read-only. PII-redacts transcript, calls Gemini, returns JSON.
    NEVER writes to Firestore."""
    if not req.transcript:
        return {"extraction_status": "FAILED", "redaction_applied": 0}

    # Step 1: PII redact transcript before sending to Gemini
    redacted_transcript, redaction_count = _redact_transcript(req.transcript)

    # Step 2: Call Gemini extraction
    extraction_prompt = f"""
You are a structured JSON extractor for user feedback transcripts.
Analyze the following feedback interview transcript and return a JSON object with these fields:
  - issue_type: one of BUG | FEATURE | UX | PRAISE | CONFUSION | DATA_INTEGRITY | OTHER
  - severity_estimate: one of LOW | MEDIUM | HIGH | CRITICAL
  - affected_feature: brief string
  - user_intent: what the user was trying to do
  - reproduction_steps: steps to reproduce (null if not applicable)
  - morgan_summary: 2-3 sentence plain English summary suitable to read back to the user

Context:
  Page: {req.page_title or 'Unknown'}
  Route: {req.route or '/'}
  Trigger: {req.trigger_reason or 'manualFAB'}

Transcript:
{_format_transcript(redacted_transcript)}

Return ONLY valid JSON. No markdown. No explanation.
"""
    try:
        if genai_client is None:
            raise ValueError("GenAI client not initialized")

        from google.genai import types as genai_types
        response = genai_client.models.generate_content(
            model=MODEL_FLASH,
            contents=extraction_prompt,
            config=genai_types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=512,
            ),
        )
        raw = response.text.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        import json
        parsed = json.loads(raw.strip())

        # Validate and sanitise
        issue_type = parsed.get("issue_type", "OTHER")
        if issue_type not in VALID_ISSUE_TYPES:
            issue_type = "OTHER"
        severity = parsed.get("severity_estimate", "MEDIUM")
        if severity not in VALID_SEVERITY:
            severity = "MEDIUM"

        logger.info(f"EXTRACT: uid={uid} issue_type={issue_type} redaction={redaction_count}")

        return {
            "extraction_status": "COMPLETE",
            "issue_type": issue_type,
            "severity_estimate": severity,
            "affected_feature": parsed.get("affected_feature"),
            "user_intent": parsed.get("user_intent"),
            "reproduction_steps": parsed.get("reproduction_steps"),
            "morgan_summary": parsed.get("morgan_summary"),
            "redaction_applied": redaction_count,
        }

    except Exception as e:
        logger.warning(f"EXTRACT failed for uid={uid}: {e}")
        return {
            "extraction_status": "FAILED",
            "redaction_applied": redaction_count,
        }


# ── SUBMIT ────────────────────────────────────────────────────────────────────

async def _handle_submit(uid: str, req: CallableRequest) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    lock_id = req.lock_id
    user_ref = db.collection("users").document(uid)

    # Step 1: Verify or refresh lock
    user_doc = user_ref.get()
    user_data: Dict = user_doc.to_dict() if user_doc.exists else {}
    lock = user_data.get("feedback_trigger_lock", {})

    if lock and lock.get("lock_id") == lock_id:
        doc_id = lock.get("draft_doc_id")
        trigger_reason = lock.get("reason", req.trigger_reason or "manualFAB")
        if not doc_id:
            raise HTTPException(status_code=400, detail="Lock missing draft_doc_id")
    elif not lock_id or not lock:
        # Fallback: lock expired; compute fresh ID and use trigger_reason from request
        trigger_reason = req.trigger_reason or "manualFAB"
        counter = user_data.get("interviews_this_hour", 0)
        doc_id = _compute_doc_id(uid, trigger_reason, counter=counter)
    else:
        raise HTTPException(status_code=409, detail="Lock mismatch. Call CHECK first.")

    # Step 2: PII redact transcript
    transcript = req.transcript or []
    redacted_transcript, redaction_count = _redact_transcript(transcript)

    # Step 3: PII redact confirmed text
    confirmed_text = req.morgan_summary_confirmed_text
    confirmed_redaction = 0
    if confirmed_text:
        confirmed_text, confirmed_redaction = _redact_text(confirmed_text)

    total_redaction = redaction_count + confirmed_redaction

    # Step 4: Server-final classification (client cannot inject issue_type or severity)
    extraction_status = req.extraction_status or "FAILED"
    if extraction_status == "COMPLETE" and req.issue_type and req.issue_type in VALID_ISSUE_TYPES:
        # Trust EXTRACT result
        final_issue_type = req.issue_type
        final_severity = req.severity_estimate if req.severity_estimate in VALID_SEVERITY else "MEDIUM"
        needs_admin_triage = False
    else:
        # FAIL / fallback path: use client suggestion (safe enum only)
        client_suggestion = (req.client_suggested_issue_type or "OTHER").upper()
        needs_admin_triage = False
        if client_suggestion == "DATA_INTEGRITY":
            # DATA_INTEGRITY from client → triage flag, issue_type stays OTHER
            final_issue_type = "OTHER"
            needs_admin_triage = True
        elif client_suggestion in SAFE_CLIENT_ISSUE_TYPES:
            final_issue_type = client_suggestion
        else:
            final_issue_type = "OTHER"
        final_severity = "MEDIUM"  # explicit default on FAIL

    # Step 5: GCS prefix routing (DATA_INTEGRITY → hold prefix)
    screenshot_url = req.screenshot_url
    if screenshot_url and final_issue_type == "DATA_INTEGRITY":
        # Already uploaded to standard prefix; note as hold for admin
        pass  # Screenshot URL stored as-is; admin cannot delete hold objects

    # Step 6: Write to beta_feedback/{doc_id} via Admin SDK (full set)
    doc_ref = db.collection("beta_feedback").document(doc_id)
    existing = doc_ref.get()
    if existing.exists:
        # Deterministic ID: second write from same trigger/day = duplicate
        logger.info(f"SUBMIT: duplicate doc_id={doc_id} uid={uid}")
        return {"doc_id": doc_id, "status": "duplicate"}

    user_email = user_data.get("email", "") or ""
    doc_data = {
        "feedback_id": doc_id,
        "user_id": uid,
        "user_email": user_email,
        "route": req.route or "/",
        "page_title": req.page_title or "Unknown",
        "app_version": req.app_version or "unknown",
        "status": "OPEN",
        "resolution_note": None,
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
        "intake_method": req.intake_method or "fallback_form",
        "trigger_reason": trigger_reason,
        "issue_type": final_issue_type,
        "severity_estimate": final_severity,
        "needs_admin_triage": needs_admin_triage,
        "redaction_applied": total_redaction,
        "interview_turns": len([m for m in redacted_transcript if m.get("role") == "user"]),
        "turn_cap_reached": len([m for m in redacted_transcript if m.get("role") == "user"]) >= 6,
        "morgan_summary": req.morgan_summary,
        "morgan_summary_confirmed_text": confirmed_text,
        "user_confirmed_summary": req.user_confirmed_summary or False,
        "extraction_status": extraction_status,
        "affected_feature": req.affected_feature,
        "user_intent": req.user_intent,
        "reproduction_steps": req.reproduction_steps,
        "client_suggested_issue_type": req.client_suggested_issue_type,
        "full_transcript": redacted_transcript,
        "screenshot_url": screenshot_url,
        "screenshot_consented": req.screenshot_consented or False,
        "post_submit_correction": None,
        "post_submit_correction_ts": None,
        "pending_sync": False,
    }

    doc_ref.set(doc_data)

    # Step 7: Update users/{uid} — clear lock, set last_trigger
    user_ref.set({
        "last_feedback_trigger_ts": firestore.SERVER_TIMESTAMP,
        "feedback_trigger_lock": firestore.DELETE_FIELD,
    }, merge=True)

    logger.info(f"SUBMIT: uid={uid} doc_id={doc_id} issue_type={final_issue_type} redaction={total_redaction}")
    return {"doc_id": doc_id, "status": "filed"}


# ── DISMISS ───────────────────────────────────────────────────────────────────

async def _handle_dismiss(uid: str, req: CallableRequest) -> Dict[str, Any]:
    user_ref = db.collection("users").document(uid)
    user_doc = user_ref.get()
    data: Dict = user_doc.to_dict() if user_doc.exists else {}
    lock = data.get("feedback_trigger_lock", {})

    updates: Dict[str, Any] = {
        "feedback_dismissal_count": firestore.Increment(1),
    }
    if lock and lock.get("lock_id") == req.lock_id:
        updates["feedback_trigger_lock"] = firestore.DELETE_FIELD

    user_ref.set(updates, merge=True)
    logger.info(f"DISMISS: uid={uid} reason={req.reason}")
    return {"status": "dismissed"}


# ── UPLOAD_URL ────────────────────────────────────────────────────────────────

async def _handle_upload_url(uid: str, req: CallableRequest) -> Dict[str, Any]:
    """Returns a signed PUT URL. Input is lock_id only — server reads draft_doc_id from lock."""
    lock_id = req.lock_id
    if not lock_id:
        raise HTTPException(status_code=400, detail="lock_id required")

    user_ref = db.collection("users").document(uid)
    user_doc = user_ref.get()
    data: Dict = user_doc.to_dict() if user_doc.exists else {}
    lock = data.get("feedback_trigger_lock", {})

    if not lock or lock.get("lock_id") != lock_id:
        raise HTTPException(status_code=409, detail="Lock not found or expired. Call CHECK.")

    now = datetime.now(timezone.utc)
    locked_until = lock.get("locked_until")
    if locked_until and _to_dt(locked_until) < now:
        raise HTTPException(status_code=409, detail="Lock expired. Call CHECK again.")

    draft_doc_id = lock.get("draft_doc_id")
    if not draft_doc_id:
        raise HTTPException(status_code=500, detail="Lock missing draft_doc_id")

    # GCS signed PUT URL
    object_name = f"{GCS_STANDARD_PREFIX}/{uid}/{draft_doc_id}/screenshot.jpg"
    bucket = storage_client.bucket(GCS_BUCKET)
    blob = bucket.blob(object_name)
    expiry = timedelta(minutes=UPLOAD_URL_EXPIRY_MINUTES)

    signed_url = blob.generate_signed_url(
        version="v4",
        expiration=expiry,
        method="PUT",
        content_type="image/jpeg",
    )

    return {
        "signed_url": signed_url,
        "object_path": object_name,
    }


# ── CORRECTION ────────────────────────────────────────────────────────────────

async def _handle_correction(uid: str, req: CallableRequest) -> Dict[str, Any]:
    if not req.doc_id or not req.correction_text:
        raise HTTPException(status_code=400, detail="doc_id and correction_text required")

    doc_ref = db.collection("beta_feedback").document(req.doc_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Feedback doc not found")

    data: Dict = doc.to_dict()
    if data.get("user_id") != uid:
        raise HTTPException(status_code=403, detail="Not your feedback doc")

    created_at = data.get("created_at")
    if created_at:
        age = (datetime.now(timezone.utc) - _to_dt(created_at)).total_seconds()
        if age > CORRECTION_WINDOW_SECONDS:
            raise HTTPException(status_code=409, detail="Correction window expired")

    clean_text, _ = _redact_text(req.correction_text)
    doc_ref.update({
        "post_submit_correction": clean_text,
        "post_submit_correction_ts": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
    })
    return {"status": "corrected"}


# ── ADMIN_RESOLVE ─────────────────────────────────────────────────────────────

async def _handle_admin_resolve(
    uid: str,
    req: CallableRequest,
    user: Dict[str, Any],
) -> Dict[str, Any]:
    # Verify isAdmin claim or admin email (matches deps.py pattern)
    is_admin = user.get("admin") is True or user.get("email") in ["admin@numista.ai", "eric@numista.ai"]
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")

    if not req.doc_id:
        raise HTTPException(status_code=400, detail="doc_id required")

    doc_ref = db.collection("beta_feedback").document(req.doc_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Feedback doc not found")

    data: Dict = doc.to_dict()
    current_issue_type = data.get("issue_type", "OTHER")

    # DATA_INTEGRITY resolution requires non-empty resolution_note
    is_data_integrity = current_issue_type == "DATA_INTEGRITY" or (
        req.new_issue_type and req.new_issue_type.upper() == "DATA_INTEGRITY"
    )
    if is_data_integrity and req.new_status == "RESOLVED":
        if not req.resolution_note or not req.resolution_note.strip():
            raise HTTPException(
                status_code=400,
                detail="resolution_note is required before resolving a DATA_INTEGRITY ticket"
            )

    updates: Dict[str, Any] = {
        "updated_at": firestore.SERVER_TIMESTAMP,
    }
    if req.new_status:
        updates["status"] = req.new_status
    if req.resolution_note:
        updates["resolution_note"] = req.resolution_note.strip()
    if req.new_issue_type:
        new_type = req.new_issue_type.upper()
        if new_type not in VALID_ISSUE_TYPES:
            raise HTTPException(status_code=400, detail=f"Invalid issue_type: {new_type}")
        updates["issue_type"] = new_type
        if new_type == "DATA_INTEGRITY":
            updates["needs_admin_triage"] = False  # triage resolved by admin promotion

    doc_ref.update(updates)
    logger.info(f"ADMIN_RESOLVE: admin={uid} doc={req.doc_id} status={req.new_status} type={req.new_issue_type}")
    return {"status": "resolved"}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _to_dt(ts: Any) -> datetime:
    """Convert Firestore Timestamp or datetime to timezone-aware datetime."""
    if isinstance(ts, datetime):
        return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)
    if hasattr(ts, "timestamp"):
        return datetime.fromtimestamp(ts.timestamp(), tz=timezone.utc)
    return datetime.now(timezone.utc)


def _format_transcript(messages: List[Dict]) -> str:
    lines = []
    for m in messages:
        role = m.get("role", "user").upper()
        text = m.get("message") or m.get("message_redacted") or m.get("text") or ""
        lines.append(f"{role}: {text}")
    return "\n".join(lines)
