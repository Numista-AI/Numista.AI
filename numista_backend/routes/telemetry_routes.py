"""
telemetry_routes.py
ITEM 4 — Numista.AI Beta Sprint

POST /api/telemetry/silent-error
Receives silent error telemetry from the Flutter client (ErrorMessageService Path 1b).
Writes to Firestore beta_feedback/{auto_id} using the Admin SDK (server-side write).

Firestore rules for beta_feedback: client create = false (unchanged).
This endpoint is the only write path — client never calls .add() directly.
"""

from datetime import datetime, timezone
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from routes.deps import db, logger, get_current_user

router = APIRouter(prefix="/api/telemetry", tags=["Beta Telemetry"])


class SilentErrorPayload(BaseModel):
    context: str = Field(..., description="screen.action label, e.g. 'add_coins_hub.import'")
    error_type: str = Field("", description="Exception class name (no stack trace, no message)")
    has_stack: bool = Field(False, description="Whether a stack trace was available")


@router.post("/silent-error", status_code=204)
async def silent_error(
    payload: SilentErrorPayload,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    ITEM 4 — Path 1(b): Receives silent error telemetry from Flutter ErrorMessageService.
    Writes to Firestore beta_feedback/{auto_id} via Admin SDK.
    Requires valid Firebase JWT. Returns 204 No Content on success.
    Never surfaces error details back to the client.
    """
    uid = current_user.get("uid", "unknown")
    email = current_user.get("email", "unknown")

    try:
        doc = {
            "type":        "silent_error",
            "context":     payload.context[:200],        # truncate to prevent abuse
            "error_type":  payload.error_type[:100],
            "has_stack":   payload.has_stack,
            "uid":         uid,
            "email":       email,
            "created_at":  datetime.now(timezone.utc).isoformat(),
            "source":      "flutter_error_message_service",
        }
        db.collection("beta_feedback").add(doc)
    except Exception as e:
        # Log server-side but never propagate to client.
        logger.warning(f"Telemetry write failed for uid={uid}: {e}")

    # Always return 204 — client does not need a response body.
    return None
