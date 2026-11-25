"""
Transfer Service — Numista.AI Lateral Transfer ("The Secure Passport Protocol")

Handles item transfer initiation, server-side data sanitization, cryptographic 60-day token validation,
recipient email authorization locking, email notification dispatching with audit logging,
atomic claim/recall logic, and sender coin deletion on successful claim.
"""

import hmac
import uuid
import random
import secrets
import re
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from google.cloud import firestore

try:
    from services.mint_helpers import (
        build_mint_write_fields,
        read_mint_facility,
        read_mint_mark,
    )
except ImportError:
    from .mint_helpers import (
        build_mint_write_fields,
        read_mint_facility,
        read_mint_mark,
    )

COLLECTION_TRANSFERS = "transfers"
logger = logging.getLogger("numista_backend.transfer_service")

# ── v2 claim scheme helpers (PLAN v1.2 sections 4.2, 7.3, 6.3) ──────────────────
import hashlib
import os

COLLECTION_CLAIM_LOOKUPS = "transfer_claims"
CLAIM_CODE_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"  # Crockford base32: no I, L, O, U
CLAIM_CODE_LENGTH = 10                                       # 10 x 5 bits = 50 bits
CLAIM_FAIL_LIMIT_UID = 10                                    # failed lookups per hour per uid
CLAIM_FAIL_LIMIT_IP = 30                                     # failed lookups per hour per hashed IP
ALLOWED_TRANSFER_TYPES = ("sale_ebay", "sale_private", "gift", "lateral")
ALLOWED_EXPIRY_DAYS = (7, 30, 60)
NOT_FOUND_MESSAGE = "Code not found or expired"
RATE_LIMITED_MESSAGE = "Too many attempts. Please try again later."

# Licensed pricing data (Greysheet / CPG) must not be copied into archives or transfers (F15, R5).
_LICENSED_PRICING_EXACT = {"cpgretail", "cpg_retail", "pricelastupdated", "price_last_updated"}
# Seller-side state that must never travel to a recipient's copy of an item.
_V2_RECIPIENT_STRIP = (
    "status", "sold_at", "sold_qty", "sale_archive_id", "locked_pending_upgrade", "ebay_listing",
    "transferId", "pendingTransferQty", "claimed_by_ref", "claimed_at",
    "AI Estimated Value", "ai_estimated_value", "estimated_value",
)


class ClaimRateLimited(ValueError):
    """Too many failed claim lookups, or the limiter itself failed (fail closed)."""


def _pepper() -> str:
    return os.environ.get("TRANSFER_CLAIM_PEPPER", "")


def _hash_secret(value: str) -> str:
    """Hash for a claim token or code. HMAC with a server pepper when configured."""
    pepper = _pepper()
    if pepper:
        return hmac.new(pepper.encode("utf-8"), value.encode("utf-8"), hashlib.sha256).hexdigest()
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_legacy_pin(pin: str, salt: str) -> str:
    """Salted (and peppered when configured) hash used to replace a plaintext legacy PIN."""
    return hmac.new((_pepper() + salt).encode("utf-8"), pin.encode("utf-8"), hashlib.sha256).hexdigest()


def generate_claim_token() -> str:
    return secrets.token_urlsafe(16)  # 128 bits


def generate_claim_code() -> str:
    """10 Crockford-base32 characters (50 bits), shown as XXXXX-XXXXX."""
    raw = "".join(secrets.choice(CLAIM_CODE_ALPHABET) for _ in range(CLAIM_CODE_LENGTH))
    return f"{raw[:5]}-{raw[5:]}"


def normalize_claim_code(code: str) -> str:
    """Upper-case, drop separators, map look-alikes (O->0, I/L->1). Raises on anything invalid."""
    cleaned = re.sub(r"[\s\-]", "", str(code or "")).upper().replace("O", "0").replace("I", "1").replace("L", "1")
    if len(cleaned) != CLAIM_CODE_LENGTH or any(ch not in CLAIM_CODE_ALPHABET for ch in cleaned):
        raise ValueError(NOT_FOUND_MESSAGE)
    return cleaned


def pseudonym(user_id: str) -> str:
    """Stable anonymous collector reference. Never reveals the e-mail."""
    digest = hashlib.sha256((_pepper() + "ref:" + str(user_id or "").strip().lower()).encode("utf-8")).hexdigest()
    return "NUM-" + digest[:6].upper()


def strip_licensed_pricing_fields(item: Dict[str, Any]) -> Dict[str, Any]:
    """Copy of `item` without CPG / Greysheet fields (archive rows and transfer payloads)."""
    clean = {}
    for key, value in item.items():
        low = str(key).lower()
        if low.startswith("greysheet") or low in _LICENSED_PRICING_EXACT:
            continue
        clean[key] = value
    return clean


def _json_safe_item(doc: Dict[str, Any]) -> Dict[str, Any]:
    """API-safe copy of a claimed item: Firestore write sentinels (SERVER_TIMESTAMP) and datetimes
    cannot be JSON-encoded. Without this the claim route returned HTTP 500 after the claim had
    already committed."""
    safe: Dict[str, Any] = {}
    for key, value in doc.items():
        if type(value).__name__ == "Sentinel":
            continue
        if isinstance(value, datetime):
            safe[key] = value.isoformat()
        else:
            safe[key] = value
    return safe


def _item_title(item: Dict[str, Any]) -> str:
    year = str(item.get("Year") or item.get("year") or "").strip()
    mint = str(item.get("Mint Mark") or item.get("mint_mark") or "").strip()
    series = str(item.get("Program/Series") or item.get("series") or "").strip()
    denom = str(item.get("Denomination") or item.get("denomination") or "").strip()
    head = f"{year}{('-' + mint) if mint else ''}".strip()
    parts = [p for p in (head, series or denom) if p]
    return " ".join(parts) if parts else "Numismatic item"


def _limiter_ref(db, scope: str, identifier: str, now: datetime):
    ident_hash = hashlib.sha256(str(identifier).encode("utf-8")).hexdigest()[:32]
    return (
        db.collection("_rate_limits").document(f"{scope}_{ident_hash}")
        .collection("claim_attempt").document(now.strftime("%Y-%m-%dT%H"))
    )


def _limiter_scopes(uid: Optional[str], client_ip: Optional[str]):
    return (("uid", uid, CLAIM_FAIL_LIMIT_UID), ("ip", client_ip, CLAIM_FAIL_LIMIT_IP))


def check_claim_attempts(db, *, uid: Optional[str], client_ip: Optional[str], now: Optional[datetime] = None) -> None:
    """Deny when a caller already used its failed-lookup budget. FAILS CLOSED on any limiter error."""
    now = now or _get_utc_now()
    for scope, ident, limit in _limiter_scopes(uid, client_ip):
        if not ident:
            continue
        try:
            snap = _limiter_ref(db, scope, ident, now).get()
            count = int((snap.to_dict() or {}).get("count", 0)) if snap.exists else 0
        except Exception as exc:
            logger.warning("claim limiter read failed (%s): denying", type(exc).__name__)
            raise ClaimRateLimited(RATE_LIMITED_MESSAGE)
        if count >= limit:
            raise ClaimRateLimited(RATE_LIMITED_MESSAGE)


def record_claim_failure(db, *, uid: Optional[str], client_ip: Optional[str], now: Optional[datetime] = None) -> None:
    now = now or _get_utc_now()
    for scope, ident, _limit in _limiter_scopes(uid, client_ip):
        if not ident:
            continue
        try:
            _limiter_ref(db, scope, ident, now).set({"count": firestore.Increment(1)}, merge=True)
        except Exception as exc:
            logger.warning("claim limiter write failed (%s): denying", type(exc).__name__)
            raise ClaimRateLimited(RATE_LIMITED_MESSAGE)


def _write_claim_lookups(db, transfer_id: str, token_hash: str, code_hash: str, expires_at_iso: str) -> None:
    for kind, h in (("token", token_hash), ("code", code_hash)):
        db.collection(COLLECTION_CLAIM_LOOKUPS).document(h).set(
            {"transfer_id": transfer_id, "kind": kind, "expires_at": expires_at_iso}
        )


def _delete_claim_lookups(db, transfer_data: Dict[str, Any]) -> None:
    for h in transfer_data.get("claim_lookup_ids") or []:
        try:
            db.collection(COLLECTION_CLAIM_LOOKUPS).document(h).delete()
        except Exception as exc:
            logger.warning("claim lookup cleanup failed (%s)", type(exc).__name__)


def _resolve_claim_lookup(db, *, claim_token: Optional[str] = None, claim_code: Optional[str] = None) -> str:
    """token/code -> transfer_id. One uniform error for unknown, malformed and expired."""
    if claim_token:
        secret = str(claim_token).strip()
    else:
        secret = normalize_claim_code(claim_code or "")
    snap = db.collection(COLLECTION_CLAIM_LOOKUPS).document(_hash_secret(secret)).get()
    if not snap.exists:
        raise ValueError(NOT_FOUND_MESSAGE)
    data = snap.to_dict() or {}
    exp = data.get("expires_at")
    if exp:
        try:
            when = datetime.fromisoformat(str(exp))
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            if _get_utc_now() > when:
                raise ValueError(NOT_FOUND_MESSAGE)
        except ValueError:
            raise ValueError(NOT_FOUND_MESSAGE)
    transfer_id = str(data.get("transfer_id") or "")
    if not transfer_id:
        raise ValueError(NOT_FOUND_MESSAGE)
    return transfer_id


def public_transfer_view(transfer_doc: Dict[str, Any]) -> Dict[str, Any]:
    """API-safe copy: no hashes, no lookup ids, no typed sender address."""
    hidden = {"claim_token_hash", "claim_code_hash", "claim_lookup_ids", "claim_pin_hash",
              "claim_pin_salt", "sender_address", "sender_id"}
    return {k: v for k, v in transfer_doc.items() if k not in hidden}



def _get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


def sanitize_item_payload(
    item_data: Dict[str, Any],
    privacy_toggles: Optional[Dict[str, bool]] = None,
    **kwargs: bool,
) -> Dict[str, Any]:
    """
    Strips sensitive personal/financial fields from item payload based on User A's privacy preferences.
    Covers legacy snake_case keys, Golden Schema keys, and nested paper_trail metadata.
    """
    toggles: Dict[str, bool] = dict(privacy_toggles or {})
    toggles.update(kwargs)

    sanitized = dict(item_data)
    paper_trail = dict(sanitized["paper_trail"]) if isinstance(sanitized.get("paper_trail"), dict) else None

    # Financial fields
    if toggles.get("hide_cost_basis", False):
        for field in [
            "purchase_price",
            "cost_basis",
            "price_paid",
            "purchase_date",
            "acquired_price",
            "Purchase Cost",
            "Cost",
            "Purchase Date",
            "cost",
            "set_cost_label",
            "unit_cost_basis_cents",
            "allocated_cost_basis_cents",
            "original_cost_basis",
        ]:
            sanitized.pop(field, None)
        if paper_trail is not None:
            for pt_field in ["purchase_price", "purchase_date", "cost", "price_paid"]:
                paper_trail.pop(pt_field, None)

    # Private notes
    if toggles.get("hide_private_notes", False):
        for field in [
            "private_notes",
            "notes",
            "personal_notes",
            "user_notes",
            "Personal Notes I",
            "Personal Notes",
        ]:
            sanitized.pop(field, None)

    # Storage & inventory location
    if toggles.get("hide_storage_location", False):
        for field in [
            "storage_location",
            "vault_box",
            "vault_id",
            "safe_number",
            "safe_location",
            "bin_location",
            "box_number",
            "location",
            "Storage Location",
        ]:
            sanitized.pop(field, None)

    # Invoice & vendor IDs
    if toggles.get("hide_invoices", False):
        for field in [
            "invoice_id",
            "invoice_num",
            "receipt_url",
            "vendor_name",
            "order_id",
            "Retailer Invoice #",
            "Retailer/Website",
            "Retailer/Dealer",
            "Retailer Item No.",
            "receipt_id",
            "receipt_gcs_path",
        ]:
            sanitized.pop(field, None)
        if paper_trail is not None:
            for pt_field in [
                "receipt_id",
                "receipt_filename",
                "retailer",
                "gcs_path",
                "invoice_id",
                "order_id",
                "receipt_url",
            ]:
                paper_trail.pop(pt_field, None)

    if paper_trail is not None:
        if paper_trail:
            sanitized["paper_trail"] = paper_trail
        else:
            sanitized.pop("paper_trail", None)

    # Owner & user photos (Bug B4)
    if toggles.get("hide_owner_photos", True):
        for field in ["owner_photos", "user_photos", "images_user", "custom_images", "user_images"]:
            sanitized.pop(field, None)

    return sanitized


def resolve_item_collections(item_data: dict, uid: str, db: firestore.Client):
    """
    Dynamically resolves the target subcollection reference for an item.
    Primary canonical name for paper money is 'banknotes', with fallback check for legacy 'currency' subcollection.
    """
    clean_uid = uid.strip().lower() if "@" in uid else uid.strip()
    item_type = str(item_data.get("item_type") or item_data.get("category") or "").lower()

    is_paper_money = item_type in ["paper_currency", "banknote", "currency", "paper_money", "note"] or "FR-" in str(item_data.get("Variety", ""))

    subcollection = "banknotes" if is_paper_money else "coins"
    ref = db.collection("users").document(clean_uid).collection(subcollection)

    # Fallback lookup for legacy accounts that might hold paper money under 'currency'
    if is_paper_money and "id" in item_data:
        item_id = item_data["id"]
        try:
            if not ref.document(item_id).get().exists:
                legacy_ref = db.collection("users").document(clean_uid).collection("currency")
                if legacy_ref.document(item_id).get().exists:
                    return legacy_ref
        except Exception:
            pass

    return ref


def _extract_seller_photo_urls(item_data: Dict[str, Any]) -> List[str]:
    """Collect candidate seller-uploaded storage URLs from an item doc (owner_photos first)."""
    urls: List[str] = []
    seen = set()

    def _add(u: Any) -> None:
        if isinstance(u, str):
            s = u.strip()
            if s and s not in seen:
                seen.add(s)
                urls.append(s)

    owner_photos = item_data.get("owner_photos")
    if isinstance(owner_photos, list):
        for entry in owner_photos:
            if isinstance(entry, dict):
                _add(entry.get("compressed_url") or entry.get("url") or entry.get("original_url"))
            elif isinstance(entry, str):
                _add(entry)
    _add(item_data.get("image_url_obverse"))
    _add(item_data.get("image_url_reverse"))
    return urls


def _load_seller_photo_bytes_for_pdf(
    raw_items_by_id: Dict[str, Dict[str, Any]],
    allowed_owners: set,
    *,
    storage_client: Any = None,
    max_per_item: int = 2,
    max_total: int = 8,
) -> Dict[str, List[bytes]]:
    """Fetch EXIF-stripped JPEG bytes for seller's own photos only (validated via coin_image_service).

    Never fetches external/unvalidated URLs or another seller's photos. Fails soft per photo.
    """
    from services.coin_image_service import load_sanitized_coin_image, parse_and_validate_storage_url

    client = storage_client
    if client is None:
        try:
            from google.cloud import storage as gcs_storage
            client = gcs_storage.Client()
        except Exception as e:
            logger.warning(f"Storage client unavailable for transfer PDF photos: {type(e).__name__}")
            return {}

    out: Dict[str, List[bytes]] = {}
    total = 0
    for item_id, item_data in raw_items_by_id.items():
        if total >= max_total:
            break
        imgs: List[bytes] = []
        for url in _extract_seller_photo_urls(item_data):
            if len(imgs) >= max_per_item or total >= max_total:
                break
            try:
                bucket_name, blob_name = parse_and_validate_storage_url(url, allowed_owners)
                img_bytes, _ = load_sanitized_coin_image(
                    client, bucket_name, blob_name, max_edge=600, quality=80
                )
                imgs.append(img_bytes)
                total += 1
            except Exception as pe:
                logger.info(f"Skipping transfer PDF photo for item {item_id}: {type(pe).__name__}")
                continue
        if imgs:
            out[item_id] = imgs
    return out


def initiate_transfer(
    db: firestore.Client,
    user_a_id: str,
    item_ids: List[str],
    recipient_email: Optional[str] = None,
    privacy_toggles: Optional[Dict[str, bool]] = None,
    item_quantities: Optional[Dict[str, int]] = None,
    *,
    version: int = 1,
    transfer_type: str = "lateral",
    expires_days: Optional[int] = None,
    source: str = "active",
    sender_display: Optional[str] = None,
    sender_address: Optional[str] = None,
    show_price: bool = False,
    sale_price_usd: Optional[float] = None,
    include_photos: bool = False,
    storage_client: Any = None,
) -> Dict[str, Any]:
    """
    Initiates a lateral transfer for one or more items.
    Immediately locks items to transferStatus = 'pending' on sender's collection.

    version=1 (default) keeps the legacy PIN behavior byte-for-byte.
    version=2 (PLAN v1.2): 128-bit token + 50-bit short code, stored only as hashes, hide-all privacy
    defaults, pseudonymous sender, no plaintext PIN, optional `source="sold_item"` for the buyer of a
    sale. The raw token/code are returned ONCE in the result and are never stored.
    """
    clean_user_a_id = user_a_id.strip().lower() if "@" in user_a_id else user_a_id.strip()
    is_v2 = int(version) >= 2

    if is_v2:
        if transfer_type not in ALLOWED_TRANSFER_TYPES:
            raise ValueError(f"transfer_type must be one of {ALLOWED_TRANSFER_TYPES}")
        if source not in ("active", "sold_item"):
            raise ValueError("source must be 'active' or 'sold_item'")
        days = 60 if expires_days is None else int(expires_days)
        if days not in ALLOWED_EXPIRY_DAYS:
            raise ValueError(f"expires_days must be one of {ALLOWED_EXPIRY_DAYS}")
        defaults = {
            "hide_cost_basis": True,
            "hide_private_notes": True,
            "hide_storage_location": True,
            "hide_invoices": True,
            "hide_owner_photos": True,
        }
        privacy_toggles = {**defaults, **(privacy_toggles or {})}
    else:
        if source != "active":
            raise ValueError("source 'sold_item' requires a v2 transfer")
        days = 60
        if not privacy_toggles:
            privacy_toggles = {
                "hide_cost_basis": False,
                "hide_private_notes": False,
                "hide_storage_location": False,
                "hide_invoices": False,
                "hide_owner_photos": True
            }

    now = _get_utc_now()
    expires_at = now + timedelta(days=days)
    transfer_id = uuid.uuid4().hex
    claim_pin = f"{secrets.randbelow(900000) + 100000}"

    sanitized_items = []
    raw_items_by_id: Dict[str, Dict[str, Any]] = {}
    pending_locks = []  # (coin_ref, update_payload) applied only after every item passed the guards
    pending_archives = []

    for item_id in item_ids:
        # Check coins collection first
        coin_ref = db.collection("users").document(clean_user_a_id).collection("coins").document(item_id)
        coin_snap = coin_ref.get()

        if not coin_snap.exists:
            # Check banknotes as fallback
            coin_ref = db.collection("users").document(clean_user_a_id).collection("banknotes").document(item_id)
            coin_snap = coin_ref.get()

        if not coin_snap.exists:
            # Check legacy currency as fallback
            coin_ref = db.collection("users").document(clean_user_a_id).collection("currency").document(item_id)
            coin_snap = coin_ref.get()

        if not coin_snap.exists:
            raise ValueError(f"Item {item_id} not found in user's collection")

        item_data = coin_snap.to_dict()
        item_data["id"] = item_id
        if include_photos:
            raw_items_by_id[item_id] = dict(item_data)

        # Guards (F9): demo, Sold, locked and listed items cannot start a transfer.
        if item_data.get("is_demo") is True or item_data.get("is_demo_cleared") is True:
            raise ValueError(f"Item {item_id} is a demo item and cannot be transferred.")
        is_sold = item_data.get("status") == "sold"
        if source == "sold_item":
            if not is_sold:
                raise ValueError(f"Item {item_id} is not marked Sold; use a regular transfer.")
        elif is_sold:
            raise ValueError(f"Item {item_id} is marked Sold; create the transfer for the buyer instead.")
        if item_data.get("locked_pending_upgrade") is True:
            raise ValueError(f"Item {item_id} is locked until you upgrade and cannot be transferred.")
        listing_state = (item_data.get("ebay_listing") or {}).get("status")
        if listing_state in ("approved", "published"):
            raise ValueError(f"Item {item_id} has an active eBay listing and cannot be transferred.")

        # Disallow initiating transfer on items that are already pending or transferred
        curr_status = item_data.get("transferStatus", "")
        if curr_status in ["pending", "transferred", "claimed"]:
            raise ValueError(f"Item {item_id} is already in state '{curr_status}' and cannot be transferred again.")

        curr_qty = int(item_data.get("Quantity") or item_data.get("qty") or 1)
        transfer_qty = 1
        if source == "sold_item":
            transfer_qty = max(1, min(curr_qty, int(item_data.get("sold_qty") or curr_qty)))
        elif item_quantities and item_id in item_quantities:
            transfer_qty = max(1, min(curr_qty, int(item_quantities[item_id])))

        # Sanitize item payload
        clean_item = sanitize_item_payload(item_data, privacy_toggles)
        if is_v2:
            clean_item = strip_licensed_pricing_fields(clean_item)
            for k in _V2_RECIPIENT_STRIP:
                clean_item.pop(k, None)
        clean_item["transfer_qty"] = transfer_qty
        sanitized_items.append(clean_item)

        # Move copy to proper transferred archive subcollection (not for sold_item: its sale row already exists)
        item_type = str(item_data.get("item_type") or item_data.get("category") or "").lower()
        is_paper_money = item_type in ["paper_currency", "banknote", "currency", "paper_money", "note"] or "FR-" in str(item_data.get("Variety", ""))
        archive_subcol = "transferred_currency" if is_paper_money else "transferred_coins"

        if source != "sold_item":
            archive_payload = strip_licensed_pricing_fields(item_data) if is_v2 else item_data
            pending_archives.append((archive_subcol, item_id, {
                **archive_payload,
                "archived_at": now.isoformat(),
                "transfer_id": transfer_id,
                "transfer_status": "pending",
                "transfer_qty": transfer_qty
            }))

        # Lock active item status to pending (status stays "sold" for a sold_item transfer)
        pending_locks.append((coin_ref, {
            "transferStatus": "pending",
            "transferId": transfer_id,
            "pendingTransferQty": transfer_qty
        }))

    # Every item passed its guards: now write.
    for archive_subcol, item_id, payload in pending_archives:
        db.collection("users").document(clean_user_a_id).collection(archive_subcol).document(item_id).set(payload)
    for coin_ref, payload in pending_locks:
        coin_ref.update(payload)

    transfer_doc = {
        "transfer_id": transfer_id,
        "sender_id": clean_user_a_id,
        "recipient_email": recipient_email.strip().lower() if recipient_email else None,
        "items": sanitized_items,
        "item_ids": item_ids,
        "created_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "status": "pending",
        "privacy_toggles": privacy_toggles,
        "email_sent": False
    }

    raw_token = raw_code = None
    if is_v2:
        raw_token = generate_claim_token()
        raw_code = generate_claim_code()
        token_hash = _hash_secret(raw_token)
        code_hash = _hash_secret(normalize_claim_code(raw_code))
        transfer_doc.update({
            "version": 2,
            "transfer_type": transfer_type,
            "source": source,
            "expires_days": days,
            "sender_ref": pseudonym(clean_user_a_id),
            "sender_display": (sender_display or "").strip() or None,
            "sender_address": (sender_address or "").strip() or None,
            "show_price": bool(show_price),
            "include_photos": bool(include_photos),
            "sale_price_usd": float(sale_price_usd) if (show_price and sale_price_usd is not None) else None,
            "claim_token_hash": token_hash,
            "claim_code_hash": code_hash,
            "claim_lookup_ids": [token_hash, code_hash],
        })
    else:
        transfer_doc["claim_pin"] = claim_pin.strip()

    transfer_ref = db.collection(COLLECTION_TRANSFERS).document(transfer_id)
    transfer_ref.set(transfer_doc)
    if is_v2:
        _write_claim_lookups(db, transfer_id, transfer_doc["claim_token_hash"], transfer_doc["claim_code_hash"],
                             expires_at.isoformat())

    result = dict(transfer_doc)
    if is_v2:
        result["claim_token"] = raw_token
        result["claim_code"] = raw_code
        try:
            from services.transfer_document_pdf import generate_transfer_document_pdf
            import base64
            pdf_photos = None
            if include_photos and raw_items_by_id:
                allowed_owners = {clean_user_a_id, user_a_id.strip()}
                pdf_photos = _load_seller_photo_bytes_for_pdf(
                    raw_items_by_id,
                    allowed_owners,
                    storage_client=storage_client,
                )
            result["document_pdf_b64"] = base64.b64encode(
                generate_transfer_document_pdf(
                    transfer_doc,
                    claim_token=raw_token,
                    claim_code=raw_code,
                    item_photos=pdf_photos,
                )
            ).decode("ascii")
        except Exception as pe:
            logger.warning(f"Transfer Document generation failed: {type(pe).__name__}")

    # Automated Email Dispatch & Audit Trail
    if recipient_email and recipient_email.strip():
        clean_recipient = recipient_email.strip().lower()
        try:
            from services.passport_pdf_generator import generate_passport_pdf
            from services.email_service import send_passport_transfer_email

            if is_v2:
                import base64
                pdf_bytes = base64.b64decode(result.get("document_pdf_b64") or "") or generate_passport_pdf(transfer_doc)
                email_payload = {**transfer_doc, "claim_pin": raw_code}
            else:
                pdf_bytes = generate_passport_pdf(transfer_doc)
                email_payload = transfer_doc
            email_res = send_passport_transfer_email(
                recipient_email=clean_recipient,
                transfer_data=email_payload,
                pdf_bytes=pdf_bytes
            )

            is_sent = email_res.get("status") == "sent"
            transfer_ref.update({"email_sent": is_sent})
            transfer_doc["email_sent"] = is_sent
            result["email_sent"] = is_sent

            audit_entry = {
                "timestamp": now.isoformat(),
                "recipient_email": clean_recipient,
                "status": email_res.get("status", "unknown"),
                "provider": email_res.get("provider", "none"),
                "message_id": email_res.get("message_id", "")
            }
            transfer_ref.collection("email_audit").add(audit_entry)

        except Exception as ee:
            logger.warning(f"Failed to dispatch transfer email / write audit log: {type(ee).__name__}")

    return result if is_v2 else transfer_doc


@firestore.transactional
def execute_claim_transaction(
    transaction: firestore.Transaction,
    db: firestore.Client,
    transfer_ref: firestore.DocumentReference,
    clean_user_b_id: str,
    selected_item_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Atomic Firestore Transaction context for claiming transfers.
    Enforces strict read-before-write ordering and atomic rollback on error.
    """
    # 1. READ OPERATIONS FIRST
    transfer_snap = transfer_ref.get(transaction=transaction)
    if not transfer_snap.exists:
        raise ValueError("Transfer not found")

    transfer_data = transfer_snap.to_dict() or {}
    if transfer_data.get("status") != "pending":
        raise ValueError(f"Transfer cannot be claimed (status: {transfer_data.get('status')})")

    expires_at_str = transfer_data.get("expires_at", "")
    if expires_at_str:
        expires_at = datetime.fromisoformat(expires_at_str)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if _get_utc_now() > expires_at:
            transaction.update(transfer_ref, {"status": "expired"})
            raise ValueError("Transfer token has expired (60-day window limit)")

    sender_id = (transfer_data.get("sender_id") or "").strip()
    clean_sender_id = sender_id.lower() if "@" in sender_id else sender_id
    is_v2 = int(transfer_data.get("version") or 1) >= 2
    is_sold_item = transfer_data.get("source") == "sold_item"
    from_ref = transfer_data.get("sender_ref") if is_v2 else clean_sender_id
    to_ref = pseudonym(clean_user_b_id) if is_v2 else clean_user_b_id

    items = transfer_data.get("items", [])
    if not items:
        raise ValueError("Transfer payload contains no items to claim.")

    # Pre-fetch all sender items inside transaction to satisfy Firestore transactional rules
    sender_item_snaps = []
    unselected_item_snaps = []
    for item in items:
        item_id = item.get("id")
        sender_ref = resolve_item_collections(item, clean_sender_id, db).document(item_id)
        sender_snap = sender_ref.get(transaction=transaction)
        if not sender_snap.exists and clean_sender_id != sender_id:
            sender_ref = resolve_item_collections(item, sender_id, db).document(item_id)
            sender_snap = sender_ref.get(transaction=transaction)

        if selected_item_ids and item_id not in selected_item_ids:
            unselected_item_snaps.append((item, sender_ref, sender_snap))
        else:
            sender_item_snaps.append((item, sender_ref, sender_snap))

    # 2. WRITE OPERATIONS NEXT
    claimed_items = []
    now_iso = _get_utc_now().isoformat()

    # Release unselected items back to sender and remove their pending ghost archives (Bug B2)
    for item, sender_ref, sender_snap in unselected_item_snaps:
        if sender_snap.exists:
            transaction.update(sender_ref, {
                "transferStatus": "sold" if is_sold_item else "none",
                "transferId": firestore.DELETE_FIELD,
                "pendingTransferQty": firestore.DELETE_FIELD
            })
        unselected_id = item.get("id") or item.get("item_id")
        if unselected_id:
            unselected_type = str(item.get("item_type") or item.get("category") or "").lower()
            unselected_is_paper = (
                unselected_type in ["paper_currency", "banknote", "currency", "paper_money", "note"]
                or "FR-" in str(item.get("Variety", ""))
            )
            unselected_arch_col = "transferred_currency" if unselected_is_paper else "transferred_coins"
            unselected_arch_ref = (
                db.collection("users")
                .document(clean_sender_id)
                .collection(unselected_arch_col)
                .document(unselected_id)
            )
            transaction.delete(unselected_arch_ref)

    for item, sender_ref, sender_snap in sender_item_snaps:
        item_id = item.get("id")
        new_item_id = uuid.uuid4().hex

        transfer_qty = int(item.get("transfer_qty") or 1)
        sender_data = sender_snap.to_dict() if sender_snap.exists else {}
        sender_current_qty = int(sender_data.get("Quantity") or sender_data.get("qty") or 1)

        provenance = list(item.get("provenanceLedger", []))
        provenance.append({
            "event": "Lateral Transfer (Passport Protocol)",
            "date": now_iso,
            "from_user": from_ref,
            "to_user": to_ref,
            "transfer_id": transfer_ref.id,
            "quantity": transfer_qty
        })

        denom = item.get("Denomination") or item.get("denomination") or ""
        year_str = item.get("Year") or item.get("year") or ""
        if "mint" in item and "mint_mark" in item:
            preserved_mint = str(item.get("mint") or "").strip()
            preserved_mark = read_mint_mark(item)
            mint_fields = {
                "mint": preserved_mint,
                "mint_mark": preserved_mark,
                "Mint Mark": preserved_mark,
            }
        else:
            mint_fields = build_mint_write_fields(
                read_mint_mark(item),
                raw_mint=read_mint_facility(item),
                year=str(year_str).strip(),
                series=str(item.get("Program/Series") or item.get("series") or "").strip(),
                denomination=str(denom).strip(),
                country=str(item.get("Country") or item.get("country") or "United States").strip(),
                variety=str(item.get("Variety") or item.get("variety") or "").strip(),
            )

        new_coin_doc = {
            **item,
            "id": new_item_id,
            "Quantity": transfer_qty,
            "Denomination": str(denom).strip() if str(denom).strip() else "N/A",
            "Year": str(year_str).strip(),
            **mint_fields,
            "original_transfer_id": transfer_ref.id,
            "provenanceLedger": provenance,
            "transferStatus": "active",
            "adopted_at": now_iso,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
            "timestamp": firestore.SERVER_TIMESTAMP
        }
        if is_v2:
            for k in _V2_RECIPIENT_STRIP:
                new_coin_doc.pop(k, None)
            new_coin_doc["is_demo"] = False
            new_coin_doc["is_demo_cleared"] = False

        # Write active document to recipient's collection
        recipient_ref = resolve_item_collections(item, clean_user_b_id, db).document(new_item_id)
        transaction.set(recipient_ref, new_coin_doc)
        claimed_items.append(new_coin_doc)

        # Determine proper archive subcollection ('transferred_currency' vs 'transferred_coins')
        item_type = str(item.get("item_type") or item.get("category") or "").lower()
        is_paper_money = item_type in ["paper_currency", "banknote", "currency", "paper_money", "note"] or "FR-" in str(item.get("Variety", ""))
        archive_subcol = "transferred_currency" if is_paper_money else "transferred_coins"

        if is_sold_item:
            # Buyer of a Sold item: the sender's doc stays Sold and the sale row (and its gain/loss) is untouched.
            if sender_snap.exists:
                transaction.update(sender_ref, {
                    "transferStatus": "sold",
                    "transferId": firestore.DELETE_FIELD,
                    "pendingTransferQty": firestore.DELETE_FIELD,
                    "claimed_at": now_iso,
                    "claimed_by_ref": to_ref,
                })
            continue

        # Archive copy in sender's transferred_coins/transferred_currency subcollection with legal provenance.
        # Merge sender_data after item so privacy-stripped fields (Cost, Personal Notes, paper_trail, etc.)
        # remain intact in the sender's private archive while staying stripped from recipient_ref.
        sender_archive_ref = db.collection("users").document(clean_sender_id).collection(archive_subcol).document(item_id)
        transaction.set(sender_archive_ref, {
            **item,
            **sender_data,
            "original_item_id": item_id,
            "transfer_transaction_id": transfer_ref.id,
            "sender_email": clean_sender_id,
            "receiver_email": clean_user_b_id,
            "transfer_timestamp": now_iso,
            "historical_valuation_at_transfer": (
                item.get("AI Estimated Value")
                or item.get("estimated_value")
                or sender_data.get("AI Estimated Value")
                or sender_data.get("estimated_value")
                or sender_data.get("Cost")
                or sender_data.get("Purchase Cost")
                or item.get("Cost")
                or 0.0
            ),
            "transferStatus": "transferred",
            "transfer_status": "transferred",
            "transferredTo": clean_user_b_id,
            "claimed_at": now_iso,
            "transferred_qty": transfer_qty
        }, merge=True)

        # Update or delete sender active doc (G1 partial quantity)
        if sender_snap.exists and sender_current_qty > transfer_qty:
            remaining_qty = sender_current_qty - transfer_qty
            transaction.update(sender_ref, {
                "Quantity": remaining_qty,
                "transferStatus": "none",
                "transferId": firestore.DELETE_FIELD,
                "pendingTransferQty": firestore.DELETE_FIELD
            })
        else:
            # Unconditionally delete active document if whole record transferred
            transaction.delete(sender_ref)

    # Update transfer document status to claimed
    transaction.update(transfer_ref, {
        "status": "claimed",
        "claimed_by": clean_user_b_id,
        "claimed_at": now_iso
    })

    return {
        "transfer_id": transfer_ref.id,
        "status": "claimed",
        "version": 2 if is_v2 else 1,
        "items_claimed_count": len(claimed_items),
        "claimed_items": [_json_safe_item(c) for c in claimed_items]
    }


def claim_transfer(
    db: firestore.Client,
    user_b_id: str,
    transfer_id: Optional[str] = None,
    claim_pin: Optional[str] = None,
    selected_item_ids: Optional[List[str]] = None,
    *,
    claim_token: Optional[str] = None,
    claim_code: Optional[str] = None,
    client_ip: Optional[str] = None,
    uid: Optional[str] = None,
    sign_in_provider: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Claims a pending transfer atomically using execute_claim_transaction.

    Three ways in: v2 `claim_token` (QR), v2 `claim_code` (typed), or legacy `transfer_id` + PIN.
    Token/code lookups are rate-limited per uid and per hashed IP and FAIL CLOSED. After the claim
    commits, the FIFO overflow lock runs for Free recipients (the claim itself always succeeds).
    """
    clean_user_b_id = user_b_id.strip().lower() if "@" in user_b_id else user_b_id.strip()
    limiter_uid = uid or clean_user_b_id
    uses_secret = bool(claim_token or claim_code)

    if uses_secret:
        check_claim_attempts(db, uid=limiter_uid, client_ip=client_ip)
        try:
            clean_transfer_id = _resolve_claim_lookup(db, claim_token=claim_token, claim_code=claim_code)
            transfer_ref = db.collection(COLLECTION_TRANSFERS).document(clean_transfer_id)
            transfer_snap = transfer_ref.get()
            if not transfer_snap.exists:
                raise ValueError(NOT_FOUND_MESSAGE)
        except ValueError:
            record_claim_failure(db, uid=limiter_uid, client_ip=client_ip)
            raise
        clean_pin = ""
    else:
        if not (transfer_id or "").strip() or claim_pin is None:
            raise ValueError("A claim token, a claim code, or a Transfer ID with PIN is required")
        clean_transfer_id = transfer_id.strip()
        clean_pin = claim_pin.strip()
        transfer_ref = db.collection(COLLECTION_TRANSFERS).document(clean_transfer_id)
        transfer_snap = transfer_ref.get()
        if not transfer_snap.exists:
            raise ValueError("Transfer not found")

    transfer_data = transfer_snap.to_dict() or {}

    if transfer_data.get("status") != "pending":
        raise ValueError(f"Transfer cannot be claimed (status: {transfer_data.get('status')})")

    # ── Recipient Authorization Guard — FIRST, before PIN checks ────────────
    # A non-recipient cannot burn the 5 PIN tries and lock out the real recipient.
    locked_email = transfer_data.get("recipient_email")
    if locked_email and locked_email.strip():
        clean_locked = locked_email.strip().lower()
        if clean_user_b_id != clean_locked:
            raise ValueError(
                "This transfer is locked to a different account. "
                "Please sign in with the correct recipient account."
            )

    if not uses_secret:
        # ── Legacy PIN brute-force lockout ───────────────────────────────────
        # After 5 wrong attempts the transfer document is soft-locked for 15 minutes.
        PIN_MAX_ATTEMPTS = 5
        PIN_LOCKOUT_MINUTES = 15

        pin_fail_count = int(transfer_data.get("pin_fail_count", 0))
        pin_locked_until_str = transfer_data.get("pin_locked_until")
        now = _get_utc_now()

        if pin_locked_until_str:
            try:
                locked_until = datetime.fromisoformat(pin_locked_until_str)
                if locked_until.tzinfo is None:
                    locked_until = locked_until.replace(tzinfo=timezone.utc)
                if now < locked_until:
                    raise ValueError(
                        "Too many incorrect PIN attempts. Please wait 15 minutes before trying again."
                    )
                else:
                    # Lockout period has expired — reset counters
                    pin_fail_count = 0
                    transfer_ref.update({"pin_fail_count": 0, "pin_locked_until": firestore.DELETE_FIELD})
            except ValueError as ve:
                if "Too many incorrect" in str(ve):
                    raise
                pass  # fromisoformat parse error — ignore and proceed

        stored_pin = str(transfer_data.get("claim_pin") or "").strip()
        stored_hash = transfer_data.get("claim_pin_hash")
        if stored_hash:
            pin_ok = hmac.compare_digest(
                str(stored_hash), hash_legacy_pin(clean_pin, str(transfer_data.get("claim_pin_salt") or ""))
            )
        elif stored_pin:
            pin_ok = hmac.compare_digest(stored_pin, clean_pin)
        else:
            pin_ok = False  # v2 transfers have no PIN: only the token or code can claim them
        if not pin_ok:
            # Atomic increment so concurrent wrong guesses can't race past the threshold
            new_count = pin_fail_count + 1
            update_data: Dict[str, Any] = {"pin_fail_count": firestore.Increment(1)}
            if new_count >= PIN_MAX_ATTEMPTS:
                update_data["pin_locked_until"] = (
                    now + timedelta(minutes=PIN_LOCKOUT_MINUTES)
                ).isoformat()
                transfer_ref.update(update_data)
                raise ValueError(
                    "Too many incorrect PIN attempts. Please wait 15 minutes before trying again."
                )
            transfer_ref.update(update_data)
            raise ValueError("Invalid claim PIN code")

        # Successful auth — clear any accumulated failure count
        if pin_fail_count > 0:
            transfer_ref.update({"pin_fail_count": 0})

    # Execute inside atomic Firestore transaction
    transaction = db.transaction()
    txn_fn = getattr(execute_claim_transaction, 'to_wrap', execute_claim_transaction) if not hasattr(transaction, '_clean_up') else execute_claim_transaction
    result = txn_fn(
        transaction=transaction,
        db=db,
        transfer_ref=transfer_ref,
        clean_user_b_id=clean_user_b_id,
        selected_item_ids=selected_item_ids
    )

    # One-time use: the lookup docs die with the claim.
    _delete_claim_lookups(db, transfer_data)

    # Free recipients: keep the oldest items open, lock the newest. The claim already succeeded.
    result["locked"] = False
    if uid:
        try:
            from services.allowance_service import apply_free_overflow_lock, LOCKED_CLAIM_MESSAGE
            lock_res = apply_free_overflow_lock(
                db, user_key=clean_user_b_id, uid=uid, email=clean_user_b_id, sign_in_provider=sign_in_provider
            )
            claimed_ids = {c.get("id") for c in result.get("claimed_items", [])}
            if claimed_ids & set(lock_res.get("locked_ids", [])):
                result["locked"] = True
                result["message"] = LOCKED_CLAIM_MESSAGE
        except Exception as exc:  # the claim is committed; never fail it because of the lock step
            logger.warning("post-claim overflow lock failed (%s)", type(exc).__name__)
    return result


def recall_transfer(
    db: firestore.Client,
    user_a_id: Optional[str] = None,
    transfer_id: str = "",
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Recalls an unclaimed pending transfer by User A (Bug B1 fix).
    Restores items in User A's active collections (coins, banknotes, currency) to transferStatus = 'none'.
    Updates ghost archive copy in transferred_coins / transferred_currency to status = 'recalled'.
    """
    effective_id = user_a_id or user_id or ""
    clean_user_a_id = effective_id.strip().lower() if "@" in effective_id else effective_id.strip()

    transfer_ref = db.collection(COLLECTION_TRANSFERS).document(transfer_id)
    transfer_snap = transfer_ref.get()

    if not transfer_snap.exists:
        raise ValueError("Transfer not found")

    transfer_data = transfer_snap.to_dict() or {}

    sender_id = (transfer_data.get("sender_id") or "").strip().lower()
    if sender_id != clean_user_a_id:
        raise ValueError("Only the transfer sender can recall this transaction")

    if transfer_data.get("status") != "pending":
        raise ValueError(f"Cannot recall transfer in status '{transfer_data.get('status')}'")

    now_iso = _get_utc_now().isoformat()

    # Restore User A's items across coins, banknotes, and legacy currency subcollections (Bug B1)
    restore_status = "sold" if transfer_data.get("source") == "sold_item" else "none"
    for item_id in transfer_data.get("item_ids", []):
        for subcol in ["coins", "banknotes", "currency"]:
            item_ref = db.collection("users").document(clean_user_a_id).collection(subcol).document(item_id)
            if item_ref.get().exists:
                item_ref.update({
                    "transferStatus": restore_status,
                    "transferId": firestore.DELETE_FIELD,
                    "pendingTransferQty": firestore.DELETE_FIELD
                })

        # Clean up ghost archive in transferred_coins / transferred_currency (Bug B1)
        for archive_col in ["transferred_coins", "transferred_currency"]:
            arch_ref = db.collection("users").document(clean_user_a_id).collection(archive_col).document(item_id)
            if arch_ref.get().exists:
                arch_ref.update({
                    "transfer_status": "recalled",
                    "status": "recalled",
                    "recalled_at": now_iso
                })

    transfer_ref.update({
        "status": "recalled",
        "recalled_at": now_iso
    })
    _delete_claim_lookups(db, transfer_data)  # the QR and the code die at once

    return {"transfer_id": transfer_id, "status": "recalled"}


def preview_transfer(
    db: firestore.Client,
    user_id: str,
    *,
    claim_token: Optional[str] = None,
    claim_code: Optional[str] = None,
    client_ip: Optional[str] = None,
    uid: Optional[str] = None,
) -> Dict[str, Any]:
    """Authenticated preview: item TITLES only. No sender, address, cost, notes, photos or price."""
    clean_user = user_id.strip().lower() if "@" in user_id else user_id.strip()
    limiter_uid = uid or clean_user
    check_claim_attempts(db, uid=limiter_uid, client_ip=client_ip)
    try:
        transfer_id = _resolve_claim_lookup(db, claim_token=claim_token, claim_code=claim_code)
        snap = db.collection(COLLECTION_TRANSFERS).document(transfer_id).get()
        if not snap.exists:
            raise ValueError(NOT_FOUND_MESSAGE)
    except ValueError:
        record_claim_failure(db, uid=limiter_uid, client_ip=client_ip)
        raise
    data = snap.to_dict() or {}
    if data.get("status") != "pending":
        raise ValueError(NOT_FOUND_MESSAGE)
    locked_email = (data.get("recipient_email") or "").strip().lower()
    if locked_email and locked_email != clean_user:
        raise ValueError(NOT_FOUND_MESSAGE)
    return {
        "items": [{"title": _item_title(i), "quantity": int(i.get("transfer_qty") or 1)} for i in data.get("items", [])],
        "expires_at": data.get("expires_at"),
    }


def rotate_claim_code(db: firestore.Client, user_a_id: str, transfer_id: str) -> Dict[str, Any]:
    """Sender reissues a pending transfer's token and code (also upgrades a legacy PIN transfer)."""
    clean_user_a_id = user_a_id.strip().lower() if "@" in user_a_id else user_a_id.strip()
    transfer_ref = db.collection(COLLECTION_TRANSFERS).document(transfer_id)
    snap = transfer_ref.get()
    if not snap.exists:
        raise ValueError("Transfer not found")
    data = snap.to_dict() or {}
    if (data.get("sender_id") or "").strip().lower() != clean_user_a_id:
        raise ValueError("Only the transfer sender can reissue this code")
    if data.get("status") != "pending":
        raise ValueError(f"Cannot reissue a transfer in status '{data.get('status')}'")
    expires_str = data.get("expires_at") or ""
    if expires_str:
        exp = datetime.fromisoformat(expires_str)
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if _get_utc_now() > exp:
            raise ValueError("Transfer has expired")

    _delete_claim_lookups(db, data)
    raw_token = generate_claim_token()
    raw_code = generate_claim_code()
    token_hash = _hash_secret(raw_token)
    code_hash = _hash_secret(normalize_claim_code(raw_code))
    updates = {
        "version": 2,
        "claim_token_hash": token_hash,
        "claim_code_hash": code_hash,
        "claim_lookup_ids": [token_hash, code_hash],
        "claim_pin": firestore.DELETE_FIELD,
        "claim_pin_hash": firestore.DELETE_FIELD,
        "claim_pin_salt": firestore.DELETE_FIELD,
        "pin_fail_count": firestore.DELETE_FIELD,
        "pin_locked_until": firestore.DELETE_FIELD,
        "rotated_at": _get_utc_now().isoformat(),
    }
    if not data.get("sender_ref"):
        updates["sender_ref"] = pseudonym(clean_user_a_id)
    transfer_ref.update(updates)
    _write_claim_lookups(db, transfer_id, token_hash, code_hash, expires_str)

    merged = {**data, **{k: v for k, v in updates.items() if v is not firestore.DELETE_FIELD}}
    merged.pop("claim_pin", None)
    result = {"transfer_id": transfer_id, "claim_token": raw_token, "claim_code": raw_code, "expires_at": expires_str}
    try:
        from services.transfer_document_pdf import generate_transfer_document_pdf
        import base64
        result["document_pdf_b64"] = base64.b64encode(
            generate_transfer_document_pdf(merged, claim_token=raw_token, claim_code=raw_code)
        ).decode("ascii")
    except Exception as pe:
        logger.warning(f"Transfer Document generation failed: {type(pe).__name__}")
    return result


# ── MODE 3: DIRECT SALE & DISPOSITION ENGINE (PHASE 1) ────────────────────────

def record_direct_sale(
    db: firestore.Client,
    user_id: str,
    coin_id: str,
    qty_sold: int,
    sale_price_usd: float,
    fees_usd: float = 0.0,
    sale_date: Optional[str] = None,
    sales_venue: str = "Outside Numista.AI",
    buyer_reference: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Mode 3: Records a direct sale outside Numista.AI (CoS Addendum 2 G1-G3, Phase 1).
    - Decrements Quantity by qty_sold if qty_sold < current_qty, or deletes from active collection if qty_sold == current_qty.
    - Preserves exact US Mint item code (e.g. '26XE') without suffix.
    - Computes financials in integer cents (Lock L1 & G2):
        allocated_cost_basis_cents = unit_cost_cents * qty_sold
        net_proceeds_cents = sale_price_cents - fees_cents
        realized_profit_cents = net_proceeds_cents - allocated_cost_basis_cents
    - Archives record in users/{user_id}/transferred_coins/{sale_archive_id} with status = 'sold'.
    - Stored strictly on sender's private archive, never in any recipient payload.
    """
    clean_user_id = user_id.strip().lower() if "@" in user_id else user_id.strip()

    coin_ref = None
    active_subcol = "coins"
    for subcol in ["coins", "banknotes", "currency"]:
        ref = db.collection("users").document(clean_user_id).collection(subcol).document(coin_id)
        if ref.get().exists:
            coin_ref = ref
            active_subcol = subcol
            break

    if not coin_ref:
        raise ValueError(f"Item {coin_id} not found in user's active collection")

    item_data = coin_ref.get().to_dict() or {}
    item_data["id"] = coin_id

    if item_data.get("status") == "sold":
        raise ValueError(f"Item {coin_id} is already marked Sold")
    if item_data.get("transferStatus") == "pending":
        raise ValueError(f"Item {coin_id} has a pending transfer; cancel it before recording a sale")

    current_qty = int(item_data.get("Quantity") or item_data.get("qty") or 1)
    qty_to_sell = int(qty_sold)
    if qty_to_sell < 1:
        raise ValueError(f"Quantity to sell must be at least 1, got {qty_to_sell}")
    if qty_to_sell > current_qty:
        raise ValueError(f"Cannot sell {qty_to_sell} units; only {current_qty} available in vault")

    # Financial math in integer cents (Lock L1 & G2)
    raw_cost_str = str(item_data.get("Cost") or item_data.get("Purchase Cost") or item_data.get("cost_basis") or "0")
    clean_cost_num = float(re.sub(r'[^\d.]', '', raw_cost_str) or 0.0)
    unit_cost_cents = round(clean_cost_num * 100)
    allocated_cost_basis_cents = unit_cost_cents * qty_to_sell

    sale_price_cents = round(float(sale_price_usd) * 100)
    fees_cents = round(float(fees_usd) * 100)
    net_proceeds_cents = sale_price_cents - fees_cents
    realized_profit_cents = net_proceeds_cents - allocated_cost_basis_cents

    now = _get_utc_now()
    now_iso = now.isoformat()
    sale_archive_id = f"sale_{uuid.uuid4().hex[:12]}"
    effective_sale_date = sale_date or now_iso[:10]

    # Provenance entry
    provenance = list(item_data.get("provenanceLedger", []))
    provenance.append({
        "event": "Direct Sale (Outside Numista.AI)",
        "date": effective_sale_date,
        "qty_sold": qty_to_sell,
        "sale_price": f"${sale_price_cents / 100:.2f}",
        "sales_venue": sales_venue,
        "sale_archive_id": sale_archive_id,
        "timestamp": now_iso
    })

    # Determine proper archive subcollection
    archive_subcol = "transferred_currency" if active_subcol in ["banknotes", "currency"] else "transferred_coins"

    archive_doc = {
        **strip_licensed_pricing_fields(item_data),  # F15: no CPG / Greysheet data in long-lived archive rows
        "id": sale_archive_id,
        "original_coin_id": coin_id,
        "original_subcollection": active_subcol,
        "mode": "sold_outside",
        "status": "sold",
        "transfer_status": "sold",
        "Quantity": qty_to_sell,  # SF7: archive quantity equals sold quantity
        "sold_qty": qty_to_sell,
        "remaining_qty": current_qty - qty_to_sell,
        "original_cost_basis": float(item_data.get("cost_basis") if item_data.get("cost_basis") is not None else clean_cost_num),  # SF1: preserve unit cost_basis
        "original_created_at": item_data.get("created_at"),  # SF1: preserve creation timestamp
        "unit_cost_basis_cents": unit_cost_cents,
        "allocated_cost_basis_cents": allocated_cost_basis_cents,
        "cost_basis": allocated_cost_basis_cents / 100.0,
        "sale_price_cents": sale_price_cents,
        "sale_price_usd": sale_price_cents / 100.0,
        "fees_cents": fees_cents,
        "fees_usd": fees_cents / 100.0,
        "net_proceeds_cents": net_proceeds_cents,
        "net_proceeds_usd": net_proceeds_cents / 100.0,
        "realized_profit_cents": realized_profit_cents,
        "realized_profit_usd": realized_profit_cents / 100.0,
        "sale_date": effective_sale_date,
        "sales_venue": sales_venue,
        "buyer_reference": buyer_reference or "",
        "notes": notes or "",
        "sold_at": now_iso,
        "created_at": firestore.SERVER_TIMESTAMP,
        "provenanceLedger": provenance,
    }

    archive_ref = db.collection("users").document(clean_user_id).collection(archive_subcol).document(sale_archive_id)

    # R3: status is the Sold marker (never changes while Sold); transferStatus is the transfer sub-state.
    sold_marker = {
        "status": "sold",
        "transferStatus": "sold",
        "sold_at": now_iso,
        "sold_qty": qty_to_sell,
        "sale_archive_id": sale_archive_id,
        "provenanceLedger": provenance,
        "updated_at": firestore.SERVER_TIMESTAMP,
    }

    # MF3: Atomic batch write (write archive + delete/decrement coin in single commit)
    if hasattr(db, "batch"):
        batch = db.batch()
        batch.set(archive_ref, archive_doc)
        if qty_to_sell < current_qty:
            new_qty = current_qty - qty_to_sell
            batch.update(coin_ref, {
                "Quantity": new_qty,
                "provenanceLedger": provenance,
                "updated_at": firestore.SERVER_TIMESTAMP
            })
        else:
            # Full sale: Mark Sold, never delete (R3). The doc stays, read-only, with status "sold".
            batch.update(coin_ref, sold_marker)
        batch.commit()
    else:
        archive_ref.set(archive_doc)
        if qty_to_sell < current_qty:
            new_qty = current_qty - qty_to_sell
            coin_ref.update({
                "Quantity": new_qty,
                "provenanceLedger": provenance,
                "updated_at": firestore.SERVER_TIMESTAMP
            })
        else:
            coin_ref.update(sold_marker)

    return {
        "status": "success",
        "item_kept_as_sold": qty_to_sell == current_qty,
        "sale_archive_id": sale_archive_id,
        "coin_id": coin_id,
        "qty_sold": qty_to_sell,
        "remaining_qty": current_qty - qty_to_sell,
        "unit_cost_basis": unit_cost_cents / 100.0,
        "allocated_cost_basis": allocated_cost_basis_cents / 100.0,
        "gross_sale_price": sale_price_cents / 100.0,
        "fees": fees_cents / 100.0,
        "realized_profit": realized_profit_cents / 100.0,
        "sale_date": effective_sale_date,
        "sales_venue": sales_venue
    }


def undo_sale(
    db: firestore.Client,
    user_id: str,
    sale_archive_id: str
) -> Dict[str, Any]:
    """
    Undo Mode 3 Sale (CoS Lock L3).
    - Restores Quantity and cost basis to active coin.
    - If active coin was deleted (whole sale), recreates active document.
    - Marks archive entry status = 'voided', transfer_status = 'voided' (NOT deleted).
    - Appends provenance event: 'Sale voided/undone by owner on [Date]'.
    - Excludes voided sales from Estate Report.
    """
    clean_user_id = user_id.strip().lower() if "@" in user_id else user_id.strip()

    arch_ref = None
    arch_doc = None
    arch_subcol = "transferred_coins"
    for col in ["transferred_coins", "transferred_currency"]:
        candidate = db.collection("users").document(clean_user_id).collection(col).document(sale_archive_id)
        snap = candidate.get()
        if snap.exists:
            arch_ref = candidate
            arch_doc = snap.to_dict()
            arch_subcol = col
            break

    if not arch_ref or not arch_doc:
        raise ValueError(f"Sale record '{sale_archive_id}' not found in archive")

    if arch_doc.get("status") == "voided" or arch_doc.get("transfer_status") == "voided":
        raise ValueError(f"Sale '{sale_archive_id}' is already voided")

    orig_coin_id = arch_doc.get("original_coin_id") or arch_doc.get("id")
    target_subcol = arch_doc.get("original_subcollection") or ("banknotes" if "currency" in arch_subcol else "coins")
    sold_qty = int(arch_doc.get("sold_qty") or arch_doc.get("quantity_sold") or 1)
    now_iso = _get_utc_now().isoformat()

    active_ref = db.collection("users").document(clean_user_id).collection(target_subcol).document(orig_coin_id)
    active_snap = active_ref.get()

    void_prov_entry = {
        "event": "Sale Voided / Undone",
        "date": now_iso[:10],
        "details": f"Sale of {sold_qty} unit(s) voided by owner. Restored to vault.",
        "sale_archive_id": sale_archive_id,
        "timestamp": now_iso
    }

    # MF3: Atomic batch execution (resurrect/increment coin + void archive in single commit)
    batch = db.batch() if hasattr(db, "batch") else None

    peek = (active_snap.to_dict() or {}) if active_snap.exists else {}
    if active_snap.exists and peek.get("status") == "sold" and peek.get("sale_archive_id") == sale_archive_id:
        # R3: the Sold doc was kept. Flip it back to active.
        if peek.get("transferStatus") == "pending":
            raise ValueError("Cancel the pending transfer before undoing this sale")
        if peek.get("claimed_by_ref"):
            raise ValueError("This item was already transferred to the buyer and cannot be restored")
        prov = list(peek.get("provenanceLedger", []))
        prov.append(void_prov_entry)
        restore_payload = {
            "status": firestore.DELETE_FIELD,
            "sold_at": firestore.DELETE_FIELD,
            "sold_qty": firestore.DELETE_FIELD,
            "sale_archive_id": firestore.DELETE_FIELD,
            "transferStatus": "none",
            "provenanceLedger": prov,
            "updated_at": firestore.SERVER_TIMESTAMP,
        }
        if batch:
            batch.update(active_ref, restore_payload)
        else:
            active_ref.update(restore_payload)
    elif active_snap.exists:
        active_data = active_snap.to_dict() or {}
        curr_qty = int(active_data.get("Quantity") or active_data.get("qty") or 1)
        restored_qty = curr_qty + sold_qty
        prov = list(active_data.get("provenanceLedger", []))
        prov.append(void_prov_entry)
        update_payload = {
            "Quantity": restored_qty,
            "provenanceLedger": prov,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        if batch:
            batch.update(active_ref, update_payload)
        else:
            active_ref.update(update_payload)
    else:
        # Full sale was deleted — resurrect original document (SF1)
        resurrected_data = dict(arch_doc)
        for k in ["id", "original_coin_id", "original_subcollection", "mode", "status", "transfer_status",
                 "sold_qty", "remaining_qty", "unit_cost_basis_cents", "allocated_cost_basis_cents",
                 "sale_price_cents", "sale_price_usd", "fees_cents", "fees_usd", "net_proceeds_cents",
                 "net_proceeds_usd", "realized_profit_cents", "realized_profit_usd", "sale_date",
                 "sales_venue", "buyer_reference", "sold_at", "voided_at",
                 "original_cost_basis", "original_created_at"]:
            resurrected_data.pop(k, None)
        prov = list(resurrected_data.get("provenanceLedger", []))
        prov.append(void_prov_entry)
        resurrected_data["id"] = orig_coin_id
        resurrected_data["Quantity"] = sold_qty
        resurrected_data["transferStatus"] = "none"
        resurrected_data["provenanceLedger"] = prov
        resurrected_data["updated_at"] = firestore.SERVER_TIMESTAMP

        # SF1: Restore original unit cost_basis
        orig_cb = arch_doc.get("original_cost_basis")
        if orig_cb is not None:
            resurrected_data["cost_basis"] = float(orig_cb)
        elif arch_doc.get("unit_cost_basis_cents") is not None:
            resurrected_data["cost_basis"] = float(arch_doc["unit_cost_basis_cents"]) / 100.0

        # SF1: Restore original created_at
        orig_created = arch_doc.get("original_created_at")
        if orig_created is not None:
            resurrected_data["created_at"] = orig_created

        if batch:
            batch.set(active_ref, resurrected_data)
        else:
            active_ref.set(resurrected_data)

    # Mark archive document status = voided (Lock L3)
    void_payload = {
        "status": "voided",
        "transfer_status": "voided",
        "voided_at": now_iso
    }
    if batch:
        batch.update(arch_ref, void_payload)
        batch.commit()
    else:
        arch_ref.update(void_payload)

    return {
        "status": "success",
        "message": f"Sale {sale_archive_id} successfully voided. Restored {sold_qty} unit(s).",
        "coin_id": orig_coin_id,
        "restored_qty": sold_qty
    }


def list_pending_transfers(db: firestore.Client, user_a_id: str) -> List[Dict[str, Any]]:
    """Returns the sender's pending transfers with safe summary fields only (no hashes, PINs or address)."""
    clean_user_a_id = user_a_id.strip().lower() if "@" in user_a_id else user_a_id.strip()
    now = _get_utc_now()
    docs = db.collection(COLLECTION_TRANSFERS).where("sender_id", "==", clean_user_a_id).stream()
    rows: List[Dict[str, Any]] = []
    for snap in docs:
        data = snap.to_dict() or {}
        if data.get("status") != "pending":
            continue
        expires_str = str(data.get("expires_at") or "")
        is_expired = False
        if expires_str:
            try:
                exp = datetime.fromisoformat(expires_str)
                if exp.tzinfo is None:
                    exp = exp.replace(tzinfo=timezone.utc)
                is_expired = now > exp
            except ValueError:
                pass
        items = data.get("items") or []
        rows.append({
            "transfer_id": data.get("transfer_id") or snap.id,
            "status": "pending",
            "version": int(data.get("version") or 1),
            "transfer_type": data.get("transfer_type") or "lateral",
            "source": data.get("source") or "active",
            "created_at": data.get("created_at"),
            "expires_at": expires_str or None,
            "is_expired": is_expired,
            "item_count": len(items),
            "item_titles": [_item_title(i) for i in items],
            "recipient_email": data.get("recipient_email"),
        })
    rows.sort(key=lambda r: str(r.get("created_at") or ""), reverse=True)
    return rows


def get_sold_inventory(db: firestore.Client, user_id: str) -> List[Dict[str, Any]]:
    """
    Returns list of sold/transferred items for user, including active sales and voided sales for audit.
    """
    clean_user_id = user_id.strip().lower() if "@" in user_id else user_id.strip()
    records = []

    for subcol in ["transferred_coins", "transferred_currency"]:
        docs = db.collection("users").document(clean_user_id).collection(subcol).stream()
        for doc in docs:
            d = doc.to_dict()
            d["doc_id"] = doc.id
            d["subcollection"] = subcol
            records.append(d)

    # Sort by sale_date or archived_at descending
    records.sort(key=lambda r: str(r.get("sale_date") or r.get("sold_at") or r.get("archived_at") or ""), reverse=True)
    return records


def harden_legacy_pins(db: firestore.Client, apply: bool = False) -> Dict[str, Any]:
    """N4 (PLAN v1.2 section 6.3): replace plaintext PINs on pending legacy transfers with salted hashes.

    DRY RUN by default: with apply=False nothing is written. A live run needs its own DEPLOY card
    (the CLI wrapper refuses to apply without one). v2 transfers have no PIN and are skipped.
    """
    stats = {"scanned": 0, "eligible": 0, "hardened": 0, "applied": bool(apply)}
    for snap in db.collection(COLLECTION_TRANSFERS).stream():
        stats["scanned"] += 1
        data = snap.to_dict() or {}
        if data.get("status") != "pending" or not data.get("claim_pin") or data.get("claim_pin_hash"):
            continue
        stats["eligible"] += 1
        if not apply:
            continue
        salt = secrets.token_hex(8)
        db.collection(COLLECTION_TRANSFERS).document(snap.id).update({
            "claim_pin_hash": hash_legacy_pin(str(data["claim_pin"]).strip(), salt),
            "claim_pin_salt": salt,
            "claim_pin": firestore.DELETE_FIELD,
        })
        stats["hardened"] += 1
    return stats
