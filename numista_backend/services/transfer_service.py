"""
Transfer Service — Numista.AI Lateral Transfer ("The Secure Passport Protocol")

Handles item transfer initiation, server-side data sanitization, cryptographic 60-day token validation,
recipient email authorization locking, email notification dispatching with audit logging,
and atomic claim/recall logic.
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


def initiate_transfer(
    db: firestore.Client,
    user_a_id: str,
    item_ids: List[str],
    recipient_email: Optional[str] = None,
    privacy_toggles: Optional[Dict[str, bool]] = None
) -> Dict[str, Any]:
    """
    Initiates a lateral transfer for one or more items.
    Generates Passport Certificate PDF and dispatches email if recipient_email is provided.
    Appends audit trail to transfers/{transfer_id}/email_audit in Firestore.
    """
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
        coin_ref = db.collection("users").document(user_a_id).collection("coins").document(item_id)
        coin_snap = coin_ref.get()

        if not coin_snap.exists and user_a_id != user_a_id.lower():
            alt_user_id = user_a_id.lower()
            coin_ref = db.collection("users").document(alt_user_id).collection("coins").document(item_id)
            coin_snap = coin_ref.get()

        if not coin_snap.exists:
            # Check banknotes as fallback
            coin_ref = db.collection("users").document(user_a_id).collection("banknotes").document(item_id)
            coin_snap = coin_ref.get()

        if not coin_snap.exists and user_a_id != user_a_id.lower():
            alt_user_id = user_a_id.lower()
            coin_ref = db.collection("users").document(alt_user_id).collection("banknotes").document(item_id)
            coin_snap = coin_ref.get()

        if not coin_snap.exists:
            raise ValueError(f"Item {item_id} not found in user's collection")

        item_data = coin_snap.to_dict()
        item_data["id"] = item_id
        
        # Sanitize item payload
        clean_item = sanitize_item_payload(item_data, privacy_toggles)
        sanitized_items.append(clean_item)

        # Move copy to transferred_coins archive
        db.collection("users").document(user_a_id).collection("transferred_coins").document(item_id).set({
            **item_data,
            "archived_at": now.isoformat(),
            "transfer_id": transfer_id,
            "transfer_status": "pending"
        })

        # Update active item status
        coin_ref.update({
            "transferStatus": "pending",
            "transferId": transfer_id
        })

    transfer_doc = {
        "transfer_id": transfer_id,
        "sender_id": user_a_id,
        "recipient_email": recipient_email.strip().lower() if recipient_email else None,
        "claim_pin": claim_pin,
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

            # Write immutable email audit entry to Firestore subcollection
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


def claim_transfer(
    db: firestore.Client,
    user_b_id: str,
    transfer_id: str,
    claim_pin: str,
    selected_item_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Claims a pending transfer, copying items into User B's vault with native SERVER_TIMESTAMP and field sanitization.
    Enforces recipient email authorization locking if recipient_email was specified at initiation.
    """
    transfer_ref = db.collection(COLLECTION_TRANSFERS).document(transfer_id)
    transfer_snap = transfer_ref.get()

    if not transfer_snap.exists:
        raise ValueError("Transfer not found")

    transfer_data = transfer_snap.to_dict()

    if transfer_data.get("status") != "pending":
        raise ValueError(f"Transfer cannot be claimed (status: {transfer_data.get('status')})")

    expires_at = datetime.fromisoformat(transfer_data["expires_at"])
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if _get_utc_now() > expires_at:
        transfer_ref.update({"status": "expired"})
        raise ValueError("Transfer token has expired (60-day window limit)")

    if transfer_data.get("claim_pin") != claim_pin.strip():
        raise ValueError("Invalid claim PIN code")

    # Recipient Authorization Locking:
    # If recipient_email was specified at initiation, only an account matching recipient_email can claim.
    locked_email = transfer_data.get("recipient_email")
    if locked_email and locked_email.strip():
        clean_locked = locked_email.strip().lower()
        clean_user_b = user_b_id.strip().lower()
        if "@" in clean_user_b and clean_user_b != clean_locked:
            raise ValueError(f"Transfer is locked exclusively to recipient account '{clean_locked}'. Active user '{clean_user_b}' is not authorized to claim.")

    sender_id = transfer_data["sender_id"]
    claimed_items = []

    for item in transfer_data.get("items", []):
        item_id = item.get("id")
        if selected_item_ids and item_id not in selected_item_ids:
            continue

        new_item_id = uuid.uuid4().hex
        provenance = item.get("provenanceLedger", [])
        provenance.append({
            "event": "Lateral Transfer (Passport Protocol)",
            "date": _get_utc_now().isoformat(),
            "from_user": sender_id,
            "to_user": user_b_id,
            "transfer_id": transfer_id
        })

        # Sanitize item strings so empty values default cleanly
        denom = item.get("Denomination") or item.get("denomination") or ""
        year_str = item.get("Year") or item.get("year") or ""
        mint_str = item.get("Mint Mark") or item.get("mintMark") or ""

        new_coin_doc = {
            **item,
            "id": new_item_id,
            "Denomination": denom.strip() if denom.strip() else "N/A",
            "Year": year_str.strip(),
            "Mint Mark": mint_str.strip(),
            "original_transfer_id": transfer_id,
            "provenanceLedger": provenance,
            "transferStatus": "claimed",
            "adopted_at": _get_utc_now().isoformat(),
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
            "timestamp": firestore.SERVER_TIMESTAMP
        }

        # Write to User B collection
        clean_user_b_id = user_b_id.strip().lower() if "@" in user_b_id else user_b_id.strip()
        db.collection("users").document(clean_user_b_id).collection("coins").document(new_item_id).set(new_coin_doc)
        claimed_items.append(new_coin_doc)

        # Update User A's coin status to transferred
        sender_coin_ref = db.collection("users").document(sender_id).collection("coins").document(item_id)
        if sender_coin_ref.get().exists:
            sender_coin_ref.update({
                "transferStatus": "transferred",
                "transferredTo": clean_user_b_id
            })

    transfer_ref.update({
        "status": "claimed",
        "claimed_by": user_b_id,
        "claimed_at": _get_utc_now().isoformat()
    })

    return {
        "transfer_id": transfer_id,
        "status": "claimed",
        "items_claimed_count": len(claimed_items),
        "claimed_items": claimed_items
    }


def recall_transfer(
    db: firestore.Client,
    user_a_id: str,
    transfer_id: str
) -> Dict[str, Any]:
    """
    Recalls an unclaimed pending transfer by User A.
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
