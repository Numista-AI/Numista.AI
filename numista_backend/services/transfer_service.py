"""
Transfer Service — Numista.AI Lateral Transfer ("The Secure Passport Protocol")

Handles item transfer initiation, server-side data sanitization, cryptographic 60-day token validation,
recipient email authorization locking, email notification dispatching with audit logging,
atomic claim/recall logic, and sender coin deletion on successful claim.
"""

import uuid
import random
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from google.cloud import firestore

COLLECTION_TRANSFERS = "transfers"
logger = logging.getLogger("numista_backend.transfer_service")


def _get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


def sanitize_item_payload(item_data: Dict[str, Any], privacy_toggles: Dict[str, bool]) -> Dict[str, Any]:
    """
    Strips sensitive personal/financial fields from item payload based on User A's privacy preferences.
    """
    sanitized = dict(item_data)
    
    # Financial fields
    if privacy_toggles.get("hide_cost_basis", False):
        for field in ["purchase_price", "cost_basis", "price_paid", "purchase_date", "acquired_price", "Purchase Cost"]:
            sanitized.pop(field, None)
            
    # Private notes
    if privacy_toggles.get("hide_private_notes", False):
        for field in ["private_notes", "notes", "personal_notes", "user_notes", "Personal Notes I"]:
            sanitized.pop(field, None)
            
    # Storage & inventory location
    if privacy_toggles.get("hide_storage_location", False):
        for field in ["storage_location", "vault_box", "safe_number", "bin_location", "location", "Storage Location"]:
            sanitized.pop(field, None)
            
    # Invoice & vendor IDs
    if privacy_toggles.get("hide_invoices", False):
        for field in ["invoice_id", "invoice_num", "receipt_url", "vendor_name", "order_id", "Retailer Invoice #"]:
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


def initiate_transfer(
    db: firestore.Client,
    user_a_id: str,
    item_ids: List[str],
    recipient_email: Optional[str] = None,
    privacy_toggles: Optional[Dict[str, bool]] = None
) -> Dict[str, Any]:
    """
    Initiates a lateral transfer for one or more items.
    Immediately locks items to transferStatus = 'pending' on sender's collection.
    Generates Passport Certificate PDF and dispatches email if recipient_email is provided.
    Appends audit trail to transfers/{transfer_id}/email_audit in Firestore.
    """
    clean_user_a_id = user_a_id.strip().lower() if "@" in user_a_id else user_a_id.strip()

    if not privacy_toggles:
        privacy_toggles = {
            "hide_cost_basis": False,
            "hide_private_notes": False,
            "hide_storage_location": False,
            "hide_invoices": False
        }

    now = _get_utc_now()
    expires_at = now + timedelta(days=60)
    transfer_id = uuid.uuid4().hex
    claim_pin = f"{random.randint(100000, 999999)}"

    sanitized_items = []
    
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

        # Disallow initiating transfer on items that are already pending or transferred
        curr_status = item_data.get("transferStatus", "")
        if curr_status in ["pending", "transferred", "claimed"]:
            raise ValueError(f"Item {item_id} is already in state '{curr_status}' and cannot be transferred again.")

        # Sanitize item payload
        clean_item = sanitize_item_payload(item_data, privacy_toggles)
        sanitized_items.append(clean_item)

        # Move copy to transferred_coins archive
        db.collection("users").document(clean_user_a_id).collection("transferred_coins").document(item_id).set({
            **item_data,
            "archived_at": now.isoformat(),
            "transfer_id": transfer_id,
            "transfer_status": "pending"
        })

        # Lock active item status to pending immediately
        coin_ref.update({
            "transferStatus": "pending",
            "transferId": transfer_id
        })

    transfer_doc = {
        "transfer_id": transfer_id,
        "sender_id": clean_user_a_id,
        "recipient_email": recipient_email.strip().lower() if recipient_email else None,
        "claim_pin": claim_pin.strip(),
        "items": sanitized_items,
        "item_ids": item_ids,
        "created_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "status": "pending",
        "privacy_toggles": privacy_toggles,
        "email_sent": False
    }

    transfer_ref = db.collection(COLLECTION_TRANSFERS).document(transfer_id)
    transfer_ref.set(transfer_doc)

    # Automated Email Dispatch & Audit Trail
    if recipient_email and recipient_email.strip():
        clean_recipient = recipient_email.strip().lower()
        try:
            from services.passport_pdf_generator import generate_passport_pdf
            from services.email_service import send_passport_transfer_email

            pdf_bytes = generate_passport_pdf(transfer_doc)
            email_res = send_passport_transfer_email(
                recipient_email=clean_recipient,
                transfer_data=transfer_doc,
                pdf_bytes=pdf_bytes
            )

            is_sent = email_res.get("status") == "sent"
            transfer_ref.update({"email_sent": is_sent})
            transfer_doc["email_sent"] = is_sent

            audit_entry = {
                "timestamp": now.isoformat(),
                "recipient_email": clean_recipient,
                "status": email_res.get("status", "unknown"),
                "provider": email_res.get("provider", "none"),
                "message_id": email_res.get("message_id", "")
            }
            transfer_ref.collection("email_audit").add(audit_entry)

        except Exception as ee:
            logger.warning(f"Failed to dispatch transfer email / write audit log: {ee}")

    return transfer_doc


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

    items = transfer_data.get("items", [])
    if not items:
        raise ValueError("Transfer payload contains no items to claim.")

    # Pre-fetch all sender items inside transaction to satisfy Firestore transactional rules
    sender_item_snaps = []
    for item in items:
        item_id = item.get("id")
        if selected_item_ids and item_id not in selected_item_ids:
            continue

        sender_ref = resolve_item_collections(item, clean_sender_id, db).document(item_id)
        sender_snap = sender_ref.get(transaction=transaction)
        if not sender_snap.exists and clean_sender_id != sender_id:
            sender_ref = resolve_item_collections(item, sender_id, db).document(item_id)
            sender_snap = sender_ref.get(transaction=transaction)

        sender_item_snaps.append((item, sender_ref, sender_snap))

    # 2. WRITE OPERATIONS NEXT
    claimed_items = []
    now_iso = _get_utc_now().isoformat()

    for item, sender_ref, sender_snap in sender_item_snaps:
        item_id = item.get("id")
        new_item_id = uuid.uuid4().hex

        provenance = list(item.get("provenanceLedger", []))
        provenance.append({
            "event": "Lateral Transfer (Passport Protocol)",
            "date": now_iso,
            "from_user": clean_sender_id,
            "to_user": clean_user_b_id,
            "transfer_id": transfer_ref.id
        })

        denom = item.get("Denomination") or item.get("denomination") or ""
        year_str = item.get("Year") or item.get("year") or ""
        mint_str = item.get("Mint Mark") or item.get("mintMark") or ""

        new_coin_doc = {
            **item,
            "id": new_item_id,
            "Denomination": str(denom).strip() if str(denom).strip() else "N/A",
            "Year": str(year_str).strip(),
            "Mint Mark": str(mint_str).strip(),
            "original_transfer_id": transfer_ref.id,
            "provenanceLedger": provenance,
            "transferStatus": "active",
            "adopted_at": now_iso,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
            "timestamp": firestore.SERVER_TIMESTAMP
        }

        # Write active document to recipient's collection
        recipient_ref = resolve_item_collections(item, clean_user_b_id, db).document(new_item_id)
        transaction.set(recipient_ref, new_coin_doc)
        claimed_items.append(new_coin_doc)

        # Archive copy in sender's transferred_coins subcollection
        sender_archive_ref = db.collection("users").document(clean_sender_id).collection("transferred_coins").document(item_id)
        transaction.set(sender_archive_ref, {
            **item,
            "transferStatus": "transferred",
            "transferredTo": clean_user_b_id,
            "claimed_at": now_iso
        }, merge=True)

        # Delete active document from sender's active collection
        if sender_snap.exists:
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
        "items_claimed_count": len(claimed_items),
        "claimed_items": claimed_items
    }


def claim_transfer(
    db: firestore.Client,
    user_b_id: str,
    transfer_id: str,
    claim_pin: str,
    selected_item_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Claims a pending transfer atomically using execute_claim_transaction.
    """
    clean_transfer_id = transfer_id.strip()
    clean_pin = claim_pin.strip()
    clean_user_b_id = user_b_id.strip().lower() if "@" in user_b_id else user_b_id.strip()

    transfer_ref = db.collection(COLLECTION_TRANSFERS).document(clean_transfer_id)
    transfer_snap = transfer_ref.get()

    if not transfer_snap.exists:
        raise ValueError("Transfer not found")

    transfer_data = transfer_snap.to_dict() or {}

    if transfer_data.get("status") != "pending":
        raise ValueError(f"Transfer cannot be claimed (status: {transfer_data.get('status')})")

    stored_pin = str(transfer_data.get("claim_pin") or "").strip()
    if stored_pin != clean_pin:
        raise ValueError("Invalid claim PIN code")

    # Recipient Authorization Locking
    locked_email = transfer_data.get("recipient_email")
    if locked_email and locked_email.strip():
        clean_locked = locked_email.strip().lower()
        if "@" in clean_user_b_id and clean_user_b_id != clean_locked:
            raise ValueError(f"Transfer is locked exclusively to recipient account '{clean_locked}'. Active user '{clean_user_b_id}' is not authorized to claim.")

    # Execute inside atomic Firestore transaction
    transaction = db.transaction()
    return execute_claim_transaction(
        transaction=transaction,
        db=db,
        transfer_ref=transfer_ref,
        clean_user_b_id=clean_user_b_id,
        selected_item_ids=selected_item_ids
    )


def recall_transfer(
    db: firestore.Client,
    user_a_id: str,
    transfer_id: str
) -> Dict[str, Any]:
    """
    Recalls an unclaimed pending transfer by User A.
    Restores items in User A's active collection to transferStatus = 'none'.
    """
    transfer_ref = db.collection(COLLECTION_TRANSFERS).document(transfer_id)
    transfer_snap = transfer_ref.get()

    if not transfer_snap.exists:
        raise ValueError("Transfer not found")

    transfer_data = transfer_snap.to_dict()

    if transfer_data.get("sender_id") != user_a_id and transfer_data.get("sender_id").lower() != user_a_id.lower():
        raise ValueError("Only the transfer sender can recall this transaction")

    if transfer_data.get("status") != "pending":
        raise ValueError(f"Cannot recall transfer in status '{transfer_data.get('status')}'")

    # Restore User A's items
    for item_id in transfer_data.get("item_ids", []):
        coin_ref = db.collection("users").document(user_a_id).collection("coins").document(item_id)
        if coin_ref.get().exists:
            coin_ref.update({
                "transferStatus": "none",
                "transferId": firestore.DELETE_FIELD
            })

    transfer_ref.update({
        "status": "recalled",
        "recalled_at": _get_utc_now().isoformat()
    })

    return {"transfer_id": transfer_id, "status": "recalled"}
