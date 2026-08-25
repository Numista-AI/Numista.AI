# support_routes.py
#
# Scoped Consent Support Access — FastAPI router for Numista.AI Cloud Run backend.
#
# Privacy contract (server-enforced, not client-trusted):
#  - Coin data is ALWAYS re-fetched live from users/{identifier}/coins/{coin_id}.
#  - The stored diagnostic_package is reference metadata only; its coin field
#    values are never returned to support.
#  - Grant consent is proven by the user pressing "Grant Access" while authenticated.
#    No cryptographic token is required — the server-side grant_active flag is the
#    authority. Admin can only view tickets where grant_active == True AND not expired.
#  - ALWAYS_REDACTED fields are stripped on every support view regardless of what
#    the client submitted.

import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

import firebase_admin.auth
from fastapi import APIRouter, Header, HTTPException, Depends
from google.cloud import firestore
from google.api_core.exceptions import FailedPrecondition

from logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["support"])

# ── Firestore client (shared with main app) ─────────────────────────────────
_db: Optional[firestore.Client] = None
_auth_client = None  # firebase_admin.auth module reference


def _get_db() -> firestore.Client:
    global _db
    if _db is None:
        _db = firestore.Client()
    return _db


def _get_auth():
    """Returns firebase_admin.auth — lazy import avoids circular init issues."""
    return firebase_admin.auth


# ── Constants ───────────────────────────────────────────────────────────────

MAX_GRANT_HOURS = 48

# Fields that are ALWAYS stripped from the support view, regardless of user choices.
# This set is authoritative and lives server-side only.
ALWAYS_REDACTED = frozenset({
    "purchase_cost", "cost", "personal_notes", "notes",
    "storage_location", "ai_estimated_value", "greysheet_value",
    "melt_value", "purchase_price", "insurance_value",
    # PascalCase aliases that may exist in legacy coin documents
    "AI Estimated Value", "Purchase Cost", "Personal Notes",
    "Storage Location", "Insurance Value",
})

# Fields the support portal is permitted to see (PascalCase = legacy schema).
# The dual-key lookup below handles both legacy PascalCase and normalized snake_case.
KEY_MAP = {
    "Denomination":    "denomination",
    "Year":            "year",
    "Program/Series":  "program_series",
    "Grade":           "grade",
    "Mint Mark":       "mint_mark",
    "Variety":         "variety",
    "obverse_image_url": "obverse_image_url",   # already snake_case
    "reverse_image_url": "reverse_image_url",   # already snake_case
    "Country":         "country",
    "Composition":     "composition",
}

VALID_CATEGORIES = {
    "bug_report", "scan_camera", "import_pcgs_excel_invoice", "pcgs_data",
    "coin_display_images", "checklist", "ai_chat_morgan", "ai_trainer_grading",
    "pricing_valuation", "wishlist", "estate_planning", "currency_collection",
    "supplies", "settings_backup", "account_login", "other",
}

VALID_STATUSES = {"open", "in_progress", "waiting_on_user", "resolved", "closed"}


# ── Auth dependencies ────────────────────────────────────────────────────────

async def get_current_uid(authorization: str = Header(...)) -> str:
    """Validates Firebase ID token. Returns UID. Raises 401 on failure."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    id_token = authorization[len("Bearer "):]
    try:
        decoded = firebase_admin.auth.verify_id_token(id_token, check_revoked=True)
        return decoded["uid"]
    except Exception as e:
        logger.warning(f"[support] Auth failure: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def require_admin(authorization: str = Header(...)) -> str:
    """Validates Firebase ID token AND requires admin == true custom claim.
    Raises 401 if token invalid, 403 if not admin."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    id_token = authorization[len("Bearer "):]
    try:
        decoded = firebase_admin.auth.verify_id_token(id_token, check_revoked=True)
    except Exception as e:
        logger.warning(f"[support] Admin auth failure: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if decoded.get("admin") is not True:
        raise HTTPException(status_code=403, detail="Admin access required")
    return decoded["uid"]


# ── Internal helpers ─────────────────────────────────────────────────────────

def _generate_ticket_id() -> str:
    """28-character crypto-random ticket ID (matches existing _generateId() style)."""
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(secrets.choice(chars) for _ in range(28))


def _grant_is_active(ticket: dict) -> bool:
    """Returns True if grant_active is set and has not expired.
    This is the sole gate for admin support-view access — no token required.
    The same function is used by the scheduled expiry job so it cannot drift."""
    if not ticket.get("grant_active"):
        return False
    expires_at = ticket.get("expires_at")
    if expires_at is None:
        return False
    # Firestore Timestamps are returned as datetime objects by the Admin SDK
    if hasattr(expires_at, "timestamp"):
        expires_dt = expires_at.replace(tzinfo=timezone.utc) if expires_at.tzinfo is None else expires_at
    else:
        expires_dt = expires_at
    return datetime.now(timezone.utc) < expires_dt


def _get_user_identifier(ticket_user_id: str) -> str:
    """Returns the email-based Firestore path key for the given Firebase UID.
    TODO(uid-migration): replace with direct UID lookup once users/{uid} migration lands.
    """
    try:
        user_record = firebase_admin.auth.get_user(ticket_user_id)
        return user_record.email.strip().lower()
    except firebase_admin.auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User account not found")
    except Exception as e:
        logger.error(f"[support] get_user failed for uid={ticket_user_id}: {e}")
        raise HTTPException(status_code=403, detail="Unable to resolve user identity")


def _verify_coin_ownership(db: firestore.Client, ticket_user_id: str, coin_ids: list) -> str:
    """Verifies every coin_id belongs to the ticket owner. Returns identifier.
    Runs on grant creation AND every support view (defense in depth)."""
    identifier = _get_user_identifier(ticket_user_id)
    for coin_id in coin_ids:
        ref = db.collection("users").document(identifier).collection("coins").document(coin_id)
        if not ref.get().exists:
            raise HTTPException(
                status_code=422,
                detail=f"coin_id '{coin_id}' not found in your collection"
            )
    return identifier


def _build_support_view(db: firestore.Client, ticket_user_id: str, private_doc: dict) -> dict:
    """Server-side re-fetch and re-redact. Ignores client-submitted coin values.
    Returns only server-authorized snake_case coin fields + redacted_fields_applied list."""
    grant = private_doc.get("support_grant", {})
    diag = private_doc.get("diagnostic_package", {})

    # Read redacted_fields from diagnostic_package — NOT from support_grant.
    user_redacted = set(diag.get("redacted_fields", []))

    identifier = _get_user_identifier(ticket_user_id)
    coins = []
    for coin_id in grant.get("allowed_coin_ids", []):
        ref = db.collection("users").document(identifier).collection("coins").document(coin_id)
        doc = ref.get()
        if not doc.exists:
            continue
        raw = doc.to_dict() or {}

        visible = {}
        for raw_key, output_key in KEY_MAP.items():
            if raw_key in ALWAYS_REDACTED or raw_key in user_redacted:
                continue
            # Dual-key lookup: check PascalCase first (legacy), then snake_case (normalized).
            if raw_key in raw:
                visible[output_key] = raw[raw_key]
            elif output_key in raw:
                visible[output_key] = raw[output_key]
        visible["coin_id"] = coin_id
        coins.append(visible)

    redacted_fields_applied = sorted(
        user_redacted | {k for k in ALWAYS_REDACTED if k in KEY_MAP}
    )

    return {
        "coins": coins,
        "redacted_fields_applied": redacted_fields_applied,
    }


def _write_audit_log(db: firestore.Client, ticket_id: str, user_id: str,
                     support_agent_id: str, action: str, resource_path: str = None):
    """Writes an immutable audit entry to support_access_logs via Admin SDK."""
    try:
        log_ref = db.collection("support_access_logs").document()
        log_ref.set({
            "log_id": log_ref.id,
            "ticket_id": ticket_id,
            "user_id": user_id,
            "support_agent_id": support_agent_id,
            "action": action,
            "resource_path": resource_path,
            "timestamp": datetime.now(timezone.utc),
        })
    except Exception as e:
        logger.error(f"[support] Failed to write audit log action={action}: {e}")


# ── User endpoints ───────────────────────────────────────────────────────────

@router.post("/tickets", status_code=201)
async def create_ticket(body: dict, uid: str = Depends(get_current_uid)):
    """Create a new help ticket. Does NOT accept supportGrant from client."""
    db = _get_db()

    # Validate required fields
    subject = (body.get("subject") or "").strip()
    description = (body.get("description") or "").strip()
    category = (body.get("category") or "").strip()

    if not subject:
        raise HTTPException(400, "subject is required")
    if not description:
        raise HTTPException(400, "description is required")
    if category not in VALID_CATEGORIES:
        raise HTTPException(400, f"invalid category. Valid: {sorted(VALID_CATEGORIES)}")

    ticket_id = _generate_ticket_id()
    now = datetime.now(timezone.utc)

    # Base document — no sensitive data here
    ticket_ref = db.collection("tickets").document(ticket_id)
    ticket_ref.set({
        "ticket_id": ticket_id,
        "user_id": uid,
        "created_at": now,
        "updated_at": now,
        "status": "open",
        "subject": subject,
        "description": description,
        "category": category,
        "platform": "web",          # always set by backend
        "app_version": body.get("app_version", ""),
        "assigned_to": None,
        "resolution_notes": None,
        "closed_at": None,
        "grant_active": False,
    })

    # Optional diagnostic package → goes in private sub-document
    diag = body.get("diagnostic_package")
    if diag and isinstance(diag, dict):
        # Strip any coin field values from client submission; keep only safe metadata
        safe_diag = {
            "generated_at": now,
            "app_version": diag.get("app_version", ""),
            "platform": "web",
            "device_info": diag.get("device_info", {}),
            "error_logs": diag.get("error_logs", [])[:50],   # cap at 50 entries
            "collection_stats": diag.get("collection_stats", {}),
            "redacted_fields": diag.get("redacted_fields", []),
            "selected_coin_ids": diag.get("selected_coin_ids", []),
        }
        private_ref = ticket_ref.collection("private").document("grant_and_diag")
        private_ref.set({"diagnostic_package": safe_diag, "support_grant": None})

    logger.info(f"[support] Ticket created ticket_id={ticket_id} uid={uid}")
    return {"ticket_id": ticket_id}


@router.get("/tickets")
async def list_my_tickets(uid: str = Depends(get_current_uid)):
    """List the caller's own tickets, newest first."""
    db = _get_db()
    query = (
        db.collection("tickets")
        .where("user_id", "==", uid)
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(50)
    )
    try:
        docs = query.stream()
        tickets = []
        for doc in docs:
            d = doc.to_dict()
            # Never expose resolution_notes to the user
            d.pop("resolution_notes", None)
            tickets.append(d)
        return {"tickets": tickets}
    except FailedPrecondition:
        logger.warning("[support] list_my_tickets: Firestore index still building — returning 503")
        raise HTTPException(
            status_code=503,
            detail="Ticket index is still being built. Please wait a moment and try again.",
        )


@router.post("/tickets/{ticket_id}/grant", status_code=201)
async def create_grant(ticket_id: str, body: dict, uid: str = Depends(get_current_uid)):
    """Create a support access grant for an owned ticket.
    Consent is proven by the authenticated user calling this endpoint.
    No token is generated or returned — grant_active flag is the authority."""
    db = _get_db()

    ticket_ref = db.collection("tickets").document(ticket_id)
    ticket_doc = ticket_ref.get()
    if not ticket_doc.exists:
        raise HTTPException(404, "Ticket not found")

    ticket = ticket_doc.to_dict()
    if ticket["user_id"] != uid:
        raise HTTPException(403, "You do not own this ticket")
    if ticket.get("grant_active"):
        raise HTTPException(409, "A grant is already active for this ticket. Revoke it first.")

    # Parse and clamp duration
    requested_hours = int(body.get("duration_hours", MAX_GRANT_HOURS))
    duration_hours = max(1, min(requested_hours, MAX_GRANT_HOURS))

    allowed_coin_ids = body.get("allowed_coin_ids", [])
    redacted_fields = body.get("redacted_fields", [])

    # Verify coin ownership server-side
    if allowed_coin_ids:
        _verify_coin_ownership(db, uid, allowed_coin_ids)

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=duration_hours)

    grant = {
        "created_at": now,
        "expires_at": expires_at,
        "duration_hours": duration_hours,
        "scopes": ["read:selected_coins", "read:error_state", "read:collection_stats"],
        "allowed_coin_ids": allowed_coin_ids,
        "revoked": False,
        "revoked_at": None,
    }

    # Write private sub-document (grant + diagnostic metadata)
    private_ref = ticket_ref.collection("private").document("grant_and_diag")
    priv_doc = private_ref.get()
    if priv_doc.exists:
        private_ref.update({"support_grant": grant})
    else:
        private_ref.set({
            "support_grant": grant,
            "diagnostic_package": {
                "redacted_fields": redacted_fields,
                "selected_coin_ids": allowed_coin_ids,
            },
        })

    # Set grant_active + expires_at on base document (used by _grant_is_active)
    ticket_ref.update({
        "grant_active": True,
        "expires_at": expires_at,
        "updated_at": now,
    })

    _write_audit_log(db, ticket_id, uid, uid, "grant_created")
    logger.info(f"[support] Grant created ticket_id={ticket_id} uid={uid} hours={duration_hours}")

    return {
        "expires_at": expires_at.isoformat(),
        "duration_hours": duration_hours,
        "allowed_coin_ids": allowed_coin_ids,
    }


@router.post("/tickets/{ticket_id}/revoke")
async def revoke_grant(
    ticket_id: str,
    authorization: str = Header(...),
):
    """Revoke an active support grant. Callable by ticket owner OR admin.
    Verifies caller is the ticket owner or has admin == true custom claim."""
    db = _get_db()

    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing Bearer token")
    id_token = authorization[len("Bearer "):]
    try:
        decoded = firebase_admin.auth.verify_id_token(id_token, check_revoked=True)
    except Exception:
        raise HTTPException(401, "Invalid or expired token")

    caller_uid = decoded["uid"]
    caller_is_admin = decoded.get("admin") is True

    ticket_ref = db.collection("tickets").document(ticket_id)
    ticket_doc = ticket_ref.get()
    if not ticket_doc.exists:
        raise HTTPException(404, "Ticket not found")

    ticket = ticket_doc.to_dict()
    if ticket["user_id"] != caller_uid and not caller_is_admin:
        raise HTTPException(403, "Not authorized to revoke this grant")

    now = datetime.now(timezone.utc)
    private_ref = ticket_ref.collection("private").document("grant_and_diag")
    if private_ref.get().exists:
        private_ref.update({
            "support_grant.revoked": True,
            "support_grant.revoked_at": now,
        })
    ticket_ref.update({"grant_active": False, "updated_at": now})

    _write_audit_log(db, ticket_id, ticket["user_id"], caller_uid, "grant_revoked")
    logger.info(f"[support] Grant revoked ticket_id={ticket_id} by uid={caller_uid}")
    return {"revoked": True}


@router.patch("/tickets/{ticket_id}")
async def update_ticket(ticket_id: str, body: dict, uid: str = Depends(get_current_uid)):
    """Update ticket subject/description/status. Blocks scope expansion while grant active."""
    db = _get_db()

    ticket_ref = db.collection("tickets").document(ticket_id)
    ticket_doc = ticket_ref.get()
    if not ticket_doc.exists:
        raise HTTPException(404, "Ticket not found")

    ticket = ticket_doc.to_dict()
    if ticket["user_id"] != uid:
        raise HTTPException(403, "You do not own this ticket")

    # Freeze guard: block scope expansion while a grant is live
    if ticket.get("grant_active"):
        private_ref = ticket_ref.collection("private").document("grant_and_diag")
        private_doc = private_ref.get()
        if private_doc.exists:
            grant = (private_doc.to_dict() or {}).get("support_grant", {})
            if grant and _grant_is_valid(grant):
                forbidden = {"allowed_coin_ids", "diagnostic_package", "selected_coin_ids"}
                if forbidden & set(body.keys()):
                    raise HTTPException(423, "Cannot expand scope while a support grant is active")

    # Only allow safe fields to be updated by client
    allowed_update_keys = {"subject", "description", "status"}
    updates = {k: v for k, v in body.items() if k in allowed_update_keys}

    if "status" in updates and updates["status"] not in VALID_STATUSES:
        raise HTTPException(400, f"Invalid status. Valid: {sorted(VALID_STATUSES)}")

    updates["updated_at"] = datetime.now(timezone.utc)
    ticket_ref.update(updates)
    return {"updated": True}


@router.post("/tickets/{ticket_id}/messages", status_code=201)
async def post_message(ticket_id: str, body: dict, uid: str = Depends(get_current_uid)):
    """Add a message to a ticket thread (user side)."""
    db = _get_db()

    ticket_ref = db.collection("tickets").document(ticket_id)
    ticket_doc = ticket_ref.get()
    if not ticket_doc.exists:
        raise HTTPException(404, "Ticket not found")

    ticket = ticket_doc.to_dict()
    if ticket["user_id"] != uid:
        raise HTTPException(403, "You do not own this ticket")

    msg_body = (body.get("body") or "").strip()
    if not msg_body:
        raise HTTPException(400, "Message body is required")

    msg_ref = ticket_ref.collection("messages").document()
    now = datetime.now(timezone.utc)
    msg_ref.set({
        "message_id": msg_ref.id,
        "sender": "user",
        "sender_id": uid,
        "body": msg_body,
        "created_at": now,
    })
    ticket_ref.update({"updated_at": now})
    return {"message_id": msg_ref.id}


# ── Support / Admin endpoints ────────────────────────────────────────────────

@router.get("/support/tickets")
async def list_support_tickets(admin_uid: str = Depends(require_admin)):
    """List open/in_progress tickets for the support queue. Admin only."""
    db = _get_db()
    _write_audit_log(db, "", "", admin_uid, "portal_opened")

    query = (
        db.collection("tickets")
        .where("status", "in", ["open", "in_progress", "waiting_on_user"])
        .order_by("updated_at", direction=firestore.Query.DESCENDING)
        .limit(100)
    )
    try:
        docs = list(query.stream())
        tickets = [doc.to_dict() for doc in docs]
        return {"tickets": tickets}
    except FailedPrecondition:
        logger.warning("[support] list_support_tickets: Firestore index still building — returning 503")
        raise HTTPException(
            status_code=503,
            detail="Ticket index is still being built. Please wait a moment and try again.",
        )


@router.get("/support/tickets/{ticket_id}")
async def get_support_ticket_view(
    ticket_id: str,
    admin_uid: str = Depends(require_admin),
):
    """Redacted support view of a ticket. Requires admin claim + active user consent grant.
    Never reads private sub-document directly from Firestore client — this endpoint
    is the only path through which support sees coin data."""
    db = _get_db()

    ticket_ref = db.collection("tickets").document(ticket_id)
    ticket_doc = ticket_ref.get()
    if not ticket_doc.exists:
        raise HTTPException(404, "Ticket not found")

    ticket = ticket_doc.to_dict()
    ticket_user_id = ticket["user_id"]

    # Validate consent flag — user must have actively granted access and not expired
    if not _grant_is_active(ticket):
        raise HTTPException(403, "No active grant. The user has not granted support access for this ticket.")

    # Load private sub-document via Admin SDK (bypasses Firestore rules)
    private_ref = ticket_ref.collection("private").document("grant_and_diag")
    private_doc = private_ref.get()
    if not private_doc.exists:
        raise HTTPException(403, "No support grant data exists for this ticket")

    private_data = private_doc.to_dict() or {}
    grant = private_data.get("support_grant") or {}

    # Ownership verification on every support view (defense in depth)
    allowed_coin_ids = grant.get("allowed_coin_ids", [])
    if allowed_coin_ids:
        _verify_coin_ownership(db, ticket_user_id, allowed_coin_ids)

    # Build server-side redacted view
    coin_view = _build_support_view(db, ticket_user_id, private_data)

    # Load messages via Admin SDK
    msgs_query = (
        ticket_ref.collection("messages")
        .order_by("created_at")
        .limit(200)
    )
    messages = [m.to_dict() for m in msgs_query.stream()]

    diag = private_data.get("diagnostic_package", {})

    _write_audit_log(db, ticket_id, ticket_user_id, admin_uid, "document_read",
                     resource_path=f"tickets/{ticket_id}")

    return {
        "ticket_id": ticket_id,
        "status": ticket["status"],
        "subject": ticket["subject"],
        "description": ticket["description"],
        "category": ticket["category"],
        "platform": ticket["platform"],
        "app_version": ticket["app_version"],
        "created_at": ticket["created_at"],
        "grant_expires_at": ticket.get("expires_at"),
        # Safe diagnostic metadata (no financial coin data)
        "device_info": diag.get("device_info", {}),
        "error_logs": diag.get("error_logs", []),
        "collection_stats": diag.get("collection_stats", {}),
        # Server-re-fetched and re-redacted coin view
        "coins": coin_view["coins"],
        "redacted_fields_applied": coin_view["redacted_fields_applied"],
        "messages": messages,
    }


@router.post("/support/tickets/{ticket_id}/messages", status_code=201)
async def support_post_message(
    ticket_id: str,
    body: dict,
    admin_uid: str = Depends(require_admin),
):
    """Support agent posts a message. Requires admin claim + active user grant."""
    db = _get_db()

    ticket_ref = db.collection("tickets").document(ticket_id)
    ticket_doc = ticket_ref.get()
    if not ticket_doc.exists:
        raise HTTPException(404, "Ticket not found")

    ticket = ticket_doc.to_dict()

    # Validate active grant flag
    if not _grant_is_active(ticket):
        raise HTTPException(403, "No active grant. The user has not granted support access.")

    msg_body = (body.get("body") or "").strip()
    if not msg_body:
        raise HTTPException(400, "Message body is required")

    msg_ref = ticket_ref.collection("messages").document()
    now = datetime.now(timezone.utc)
    msg_ref.set({
        "message_id": msg_ref.id,
        "sender": "support",
        "sender_id": admin_uid,
        "body": msg_body,
        "created_at": now,
    })
    ticket_ref.update({"updated_at": now})
    _write_audit_log(db, ticket_id, ticket["user_id"], admin_uid, "message_sent",
                     resource_path=f"tickets/{ticket_id}/messages/{msg_ref.id}")
    return {"message_id": msg_ref.id}


@router.patch("/support/tickets/{ticket_id}/status")
async def support_update_status(
    ticket_id: str,
    body: dict,
    admin_uid: str = Depends(require_admin),
):
    """Support agent updates ticket status. Admin only. No grant token required for status change."""
    db = _get_db()

    new_status = (body.get("status") or "").strip()
    if new_status not in VALID_STATUSES:
        raise HTTPException(400, f"Invalid status. Valid: {sorted(VALID_STATUSES)}")

    ticket_ref = db.collection("tickets").document(ticket_id)
    if not ticket_ref.get().exists:
        raise HTTPException(404, "Ticket not found")

    now = datetime.now(timezone.utc)
    updates = {"status": new_status, "updated_at": now}
    if new_status == "closed":
        updates["closed_at"] = now
        # Auto-revoke grant on close
        ticket_ref.update(updates)
        private_ref = ticket_ref.collection("private").document("grant_and_diag")
        if private_ref.get().exists:
            private_ref.update({
                "support_grant.revoked": True,
                "support_grant.revoked_at": now,
            })
        ticket_ref.update({"grant_active": False})
    else:
        ticket_ref.update(updates)

    return {"status": new_status}


# ── Scheduled expiry endpoint ────────────────────────────────────────────────

@router.get("/support/expire-grants")
async def expire_grants():
    """Called by Cloud Scheduler every 30 minutes.
    Uses the same _grant_is_valid() helper as all support endpoints — cannot drift."""
    db = _get_db()
    now = datetime.now(timezone.utc)

    # Find all tickets with grant_active == True
    query = db.collection("tickets").where("grant_active", "==", True).stream()
    expired_count = 0

    for ticket_doc in query:
        ticket = ticket_doc.to_dict()
        ticket_id = ticket["ticket_id"]

        # _grant_is_active reads expires_at directly from the ticket document
        if not _grant_is_active(ticket):
            # Grant has expired — clear the flag
            ticket_doc.reference.update({"grant_active": False, "updated_at": now})
            _write_audit_log(db, ticket_id, ticket.get("user_id", ""), "", "grant_expired")
            expired_count += 1

    logger.info(f"[support] expire-grants: expired {expired_count} grant(s)")
    return {"expired": expired_count}


# ── Stub helper (for revoke endpoint — admin path) ──────────────────────────

async def _get_id_token_for_uid(uid: str) -> str:
    """Stub: admin revoke uses Depends(get_current_uid) which already verified the token.
    The actual verification happened in the Depends chain. This is not called at runtime."""
    raise NotImplementedError("Use Depends(require_admin) for admin-originated revoke")
