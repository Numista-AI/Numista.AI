"""
attorney_routes.py — ITEM B (P2 Closeout)
==========================================
Attorney portal token issuance and snapshot access.

Security model
--------------
- Tokens are minted with secrets.token_hex(32) (256-bit random).
- Only the SHA-256 hash of the raw token is stored in Firestore
  (collection: attorney_tokens/{sha256_hex}).
- Raw token is returned ONCE to the authenticated owner via POST /issue.
- Raw token MUST NOT appear in any log output (B-ADD-3).
- Snapshot GET validates the hash, checks expiry/revocation, then:
  (1) reads coins, (2) builds snapshot dict, (3) serializes to JSON,
  (4) sends 200, (5) writes redeemed_at — B-ADD-2 ordering.
- Field allow-list enforced server-side; no private notes or storage
  locations are included in the attorney snapshot.

Routes
------
  POST /api/attorney/issue          JWT-auth, owner only
  GET  /api/attorney/snapshot       public, raw-token param
  POST /api/attorney/revoke         JWT-auth, owner only
"""

from __future__ import annotations

import datetime
import hashlib
import secrets
from datetime import timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from routes.deps import db, logger

router = APIRouter(prefix="/api/attorney", tags=["Attorney Portal"])

# ── Constants ─────────────────────────────────────────────────────────────────

TOKEN_TTL_HOURS = 72  # 72-hour expiry per plan B2

# Fields the attorney snapshot is ALLOWED to expose (plan B4 allow-list).
# Any field not in this set is excluded from the response body.
SNAPSHOT_ALLOW = frozenset([
    "coin_id",
    "coin_name",
    "year",
    "mint_mark",
    "country",
    "is_foreign",
    "greysheet_value",
    "melt_value",
    "estimated_value",
    "purchase_price",
    "condition",
    "sheldon_grade",
    "variety_error",
    "obverse_image_url",
    "reverse_image_url",
    "program_series",
    "theme_subject",
    "is_silver",
    "is_gold",
    "weight_grams",
    "purity",
    "is_demo",
])

# ── Helpers ───────────────────────────────────────────────────────────────────

def _sha256(raw: str) -> str:
    """SHA-256 hex digest of a raw token string."""
    return hashlib.sha256(raw.encode()).hexdigest()


def _now_utc() -> datetime.datetime:
    return datetime.datetime.now(timezone.utc)


def _filter_coin(data: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of a coin document with only SNAPSHOT_ALLOW fields."""
    return {k: v for k, v in data.items() if k in SNAPSHOT_ALLOW}


def _resolve_uid_from_request(request: Request) -> str:
    """
    Extract Firebase Auth uid from the Authorization header.
    Expects: Authorization: Bearer <Firebase ID token>
    Returns the uid claim from the verified token.
    Raises 401 if missing or invalid.
    """
    import firebase_admin
    from firebase_admin import auth as fb_auth

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header.")
    id_token = auth_header.split("Bearer ", 1)[1].strip()
    try:
        decoded = fb_auth.verify_id_token(id_token)
        return decoded["uid"]
    except Exception as exc:
        logger.warning(f"[attorney] JWT verification failed: {exc}")
        raise HTTPException(status_code=401, detail="Invalid or expired Firebase ID token.")


# ── Schemas ───────────────────────────────────────────────────────────────────

class RevokeRequest(BaseModel):
    token_hash: str   # SHA-256 hex of the raw token to revoke


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/issue")
async def issue_attorney_token(request: Request):
    """
    POST /api/attorney/issue
    JWT-authenticated, owner only.

    Mints a new 256-bit random token, stores only its SHA-256 hash in
    attorney_tokens/{hash}, and returns the raw token URL ONCE.

    B-ADD-3: token_url (containing the raw token) MUST NOT be logged at
    any level. It is treated as a secret equivalent to a PCGS bearer token.
    """
    owner_uid = _resolve_uid_from_request(request)

    raw_token = secrets.token_hex(32)  # 256-bit
    token_hash = _sha256(raw_token)

    now = _now_utc()
    expires_at = now + datetime.timedelta(hours=TOKEN_TTL_HOURS)

    doc = {
        "token_id": token_hash,          # document ID == hash; stored for self-reference
        "uid": owner_uid,                 # Firebase Auth opaque uid — NEVER email
        "created_at": now,
        "expires_at": expires_at,
        "is_one_time": True,
        "redeemed_at": None,
        "is_revoked": False,
    }

    try:
        db.collection("attorney_tokens").document(token_hash).set(doc)
    except Exception as exc:
        logger.error(f"[attorney/issue] Firestore write failed for uid={owner_uid}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to create attorney token.")

    # B-ADD-3: do NOT log token_url or raw_token at any level.
    # Return the raw token to the caller exactly once — it is never stored.
    token_url = f"https://numista.ai/attorney?uid={owner_uid}&token={raw_token}"
    logger.info(f"[attorney/issue] Token issued for uid={owner_uid} expires={expires_at.isoformat()}")
    # ↑ uid and expiry only — raw token and token_url intentionally omitted from log.

    return {
        "token_url": token_url,
        "expires_at": expires_at.isoformat(),
        "is_one_time": True,
    }


@router.get("/snapshot")
async def get_attorney_snapshot(uid: str, token: str, request: Request):
    """
    GET /api/attorney/snapshot?uid=<firebase_uid>&token=<raw_32_hex>
    Public endpoint — no Firebase Auth required on the attorney side.

    Validates the token hash, checks expiry and revocation, applies the
    field allow-list, and returns the scoped collection snapshot.

    B-ADD-2 write-ordering:
      (1) Read coins
      (2) Build snapshot dict
      (3) Serialize to JSON (implicit in FastAPI response)
      (4) Send 200 with body          ← HTTP response leaves the server
      (5) Write redeemed_at           ← background task after send

    Because steps 4 and 5 are not atomic, a network timeout on step 4
    leaves redeemed_at=null. The attorney can retry; the token is still
    valid. This is correct for one-time-use: only a SUCCESSFUL delivery
    consumes the token.
    """
    # Guard: empty params → dead-end, no Firestore query
    if not uid or not token:
        raise HTTPException(
            status_code=400,
            detail="Attorney access requires a valid link from the collection owner.",
        )

    token_hash = _sha256(token)

    # Look up the token document by hash
    token_ref = db.collection("attorney_tokens").document(token_hash)
    snap = token_ref.get()
    if not snap.exists:
        raise HTTPException(status_code=410, detail="This link is invalid or has expired.")

    data = snap.to_dict() or {}

    # Verify uid matches
    if data.get("uid") != uid:
        raise HTTPException(
            status_code=403,
            detail="This link is not valid for this account.",
        )

    # Check revocation
    if data.get("is_revoked"):
        raise HTTPException(status_code=410, detail="This link has been revoked.")

    # Check expiry
    expires_at = data.get("expires_at")
    if expires_at:
        if isinstance(expires_at, datetime.datetime):
            exp_dt = expires_at if expires_at.tzinfo else expires_at.replace(tzinfo=timezone.utc)
        else:
            exp_dt = datetime.datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
            if not exp_dt.tzinfo:
                exp_dt = exp_dt.replace(tzinfo=timezone.utc)
        if _now_utc() > exp_dt:
            raise HTTPException(status_code=410, detail="This link has expired. Please request a new one from the collection owner.")

    # Check one-time redemption
    if data.get("is_one_time") and data.get("redeemed_at") is not None:
        raise HTTPException(
            status_code=410,
            detail="This link has already been used. Please request a new one from the collection owner.",
        )

    # ── Step 1: Read coins ───────────────────────────────────────────────────
    try:
        coins_snap = db.collection("users").document(uid).collection("coins").stream()
        coins = []
        total_value = 0.0
        for coin_doc in coins_snap:
            coin_data = coin_doc.to_dict() or {}
            filtered = _filter_coin(coin_data)
            filtered["coin_id"] = coin_doc.id   # always include doc ID
            coins.append(filtered)
            # Valuation ladder: greysheet_value → melt_value → purchase_price
            val = (
                coin_data.get("greysheet_value")
                or coin_data.get("melt_value")
                or coin_data.get("purchase_price")
                or 0.0
            )
            try:
                total_value += float(val)
            except (TypeError, ValueError):
                pass
    except Exception as exc:
        logger.error(f"[attorney/snapshot] Failed to read coins for uid={uid}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to read collection data.")

    # ── Step 2: Build snapshot dict ──────────────────────────────────────────
    snapshot = {
        "uid": uid,
        "total_coins": len(coins),
        "total_estimated_value": round(total_value, 2),
        "coins": coins,
        "generated_at": _now_utc().isoformat(),
    }

    # ── Steps 3+4: FastAPI serializes and sends the response ─────────────────
    # ── Step 5: Write redeemed_at AFTER response is built ────────────────────
    # We use a BackgroundTask pattern here: mark redeemed only after the
    # response object is constructed. FastAPI sends the response body, then
    # any background tasks fire. This satisfies B-ADD-2.
    from fastapi.background import BackgroundTasks
    background = BackgroundTasks()

    def _mark_redeemed():
        try:
            token_ref.update({"redeemed_at": _now_utc()})
            logger.info(f"[attorney/snapshot] Token redeemed for uid={uid}")
        except Exception as exc:
            logger.warning(f"[attorney/snapshot] Could not mark redeemed_at for uid={uid}: {exc}")

    background.add_task(_mark_redeemed)

    from fastapi.responses import JSONResponse
    return JSONResponse(content=snapshot, background=background)


@router.post("/revoke")
async def revoke_attorney_token(req: RevokeRequest, request: Request):
    """
    POST /api/attorney/revoke
    JWT-authenticated. Owner may revoke their own token by hash.
    """
    owner_uid = _resolve_uid_from_request(request)

    token_ref = db.collection("attorney_tokens").document(req.token_hash)
    snap = token_ref.get()
    if not snap.exists:
        raise HTTPException(status_code=404, detail="Token not found.")

    data = snap.to_dict() or {}
    if data.get("uid") != owner_uid:
        raise HTTPException(status_code=403, detail="Unauthorized: you do not own this token.")

    try:
        token_ref.update({
            "is_revoked": True,
            "revoked_at": _now_utc(),
        })
    except Exception as exc:
        logger.error(f"[attorney/revoke] Update failed for uid={owner_uid}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to revoke token.")

    logger.info(f"[attorney/revoke] Token revoked for uid={owner_uid}")
    return {"status": "revoked", "token_hash": req.token_hash}
