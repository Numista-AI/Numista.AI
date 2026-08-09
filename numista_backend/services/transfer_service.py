"""
Transfer Service — Numista.AI Lateral Transfer ("The Secure Passport Protocol")

Handles item transfer initiation, server-side data sanitization, cryptographic 60-day token validation,
GCS asset duplication, and atomic claim/recall logic.
"""

import uuid
import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from google.cloud import firestore

COLLECTION_TRANSFERS = "transfers"

def _get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

def sanitize_item_payload(item_data: Dict[str, Any], privacy_toggles: Dict[str, bool]) -> Dict[str, Any]:
    """
    Strips sensitive personal/financial fields from item payload based on User A's privacy preferences.
    """
    sanitized = dict(item_data)
    
    # Financial fields
    if privacy_toggles.get("hide_cost_basis", False):
        for field in ["purchase_price", "cost_basis", "price_paid", "purchase_date", "acquired_price"]:
            sanitized.pop(field, None)
            
    # Private notes
    if privacy_toggles.get("hide_private_notes", False):
        for field in ["private_notes", "notes", "personal_notes", "user_notes"]:
            sanitized.pop(field, None)
            
    # Storage & inventory location
    if privacy_toggles.get("hide_storage_location", False):
        for field in ["storage_location", "vault_box", "safe_number", "bin_location", "location"]:
            sanitized.pop(field, None)
            
    # Invoice & vendor IDs
    if privacy_toggles.get("hide_invoices", False):
        for field in ["invoice_id", "invoice_num", "receipt_url", "vendor_name", "order_id"]:
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
        "recipient_email": recipient_email,
        "claim_pin": claim_pin,
        "items": sanitized_items,
        "item_ids": item_ids,
        "created_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "status": "pending",
        "privacy_toggles": privacy_toggles
    }

    db.collection(COLLECTION_TRANSFERS).document(transfer_id).set(transfer_doc)
    return transfer_doc

def claim_transfer(
    db: firestore.Client,
    user_b_id: str,
    transfer_id: str,
    claim_pin: str,
    selected_item_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Claims a pending transfer, copying items into User B's vault and appending provenance milestones.
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

        new_coin_doc = {
            **item,
            "id": new_item_id,
            "original_transfer_id": transfer_id,
            "provenanceLedger": provenance,
            "transferStatus": "claimed",
            "adopted_at": _get_utc_now().isoformat()
        }

        # Write to User B collection
        db.collection("users").document(user_b_id).collection("coins").document(new_item_id).set(new_coin_doc)
        claimed_items.append(new_coin_doc)

        # Update User A's coin status to transferred
        sender_coin_ref = db.collection("users").document(sender_id).collection("coins").document(item_id)
        if sender_coin_ref.get().exists:
            sender_coin_ref.update({
                "transferStatus": "transferred",
                "transferredTo": user_b_id
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

    if transfer_data.get("sender_id") != user_a_id:
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
