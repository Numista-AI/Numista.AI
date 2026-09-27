"""
Transfer Service — Numista.AI Lateral Transfer ("The Secure Passport Protocol")

Handles item transfer initiation, server-side data sanitization, cryptographic 60-day token validation,
recipient email authorization locking, email notification dispatching with audit logging,
atomic claim/recall logic, and sender coin deletion on successful claim.
"""

import uuid
import random
import secrets
import re
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

    # Owner & user photos (Bug B4)
    if privacy_toggles.get("hide_owner_photos", True):
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


def initiate_transfer(
    db: firestore.Client,
    user_a_id: str,
    item_ids: List[str],
    recipient_email: Optional[str] = None,
    privacy_toggles: Optional[Dict[str, bool]] = None,
    item_quantities: Optional[Dict[str, int]] = None
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
            "hide_invoices": False,
            "hide_owner_photos": True
        }

    now = _get_utc_now()
    expires_at = now + timedelta(days=60)
    transfer_id = uuid.uuid4().hex
    claim_pin = f"{secrets.randbelow(900000) + 100000}"

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

        curr_qty = int(item_data.get("Quantity") or item_data.get("qty") or 1)
        transfer_qty = 1
        if item_quantities and item_id in item_quantities:
            transfer_qty = max(1, min(curr_qty, int(item_quantities[item_id])))

        # Sanitize item payload
        clean_item = sanitize_item_payload(item_data, privacy_toggles)
        clean_item["transfer_qty"] = transfer_qty
        sanitized_items.append(clean_item)

        # Move copy to proper transferred archive subcollection
        item_type = str(item_data.get("item_type") or item_data.get("category") or "").lower()
        is_paper_money = item_type in ["paper_currency", "banknote", "currency", "paper_money", "note"] or "FR-" in str(item_data.get("Variety", ""))
        archive_subcol = "transferred_currency" if is_paper_money else "transferred_coins"

        db.collection("users").document(clean_user_a_id).collection(archive_subcol).document(item_id).set({
            **item_data,
            "archived_at": now.isoformat(),
            "transfer_id": transfer_id,
            "transfer_status": "pending",
            "transfer_qty": transfer_qty
        })

        # Lock active item status to pending immediately
        coin_ref.update({
            "transferStatus": "pending",
            "transferId": transfer_id,
            "pendingTransferQty": transfer_qty
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

    # Release unselected items back to sender (Bug B2)
    for item, sender_ref, sender_snap in unselected_item_snaps:
        if sender_snap.exists:
            transaction.update(sender_ref, {
                "transferStatus": "none",
                "transferId": firestore.DELETE_FIELD,
                "pendingTransferQty": firestore.DELETE_FIELD
            })

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
            "from_user": clean_sender_id,
            "to_user": clean_user_b_id,
            "transfer_id": transfer_ref.id,
            "quantity": transfer_qty
        })

        denom = item.get("Denomination") or item.get("denomination") or ""
        year_str = item.get("Year") or item.get("year") or ""
        mint_str = item.get("Mint Mark") or item.get("mintMark") or ""

        new_coin_doc = {
            **item,
            "id": new_item_id,
            "Quantity": transfer_qty,
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

        # Determine proper archive subcollection ('transferred_currency' vs 'transferred_coins')
        item_type = str(item.get("item_type") or item.get("category") or "").lower()
        is_paper_money = item_type in ["paper_currency", "banknote", "currency", "paper_money", "note"] or "FR-" in str(item.get("Variety", ""))
        archive_subcol = "transferred_currency" if is_paper_money else "transferred_coins"

        # Archive copy in sender's transferred_coins/transferred_currency subcollection with legal provenance
        sender_archive_ref = db.collection("users").document(clean_sender_id).collection(archive_subcol).document(item_id)
        transaction.set(sender_archive_ref, {
            **item,
            "original_item_id": item_id,
            "transfer_transaction_id": transfer_ref.id,
            "sender_email": clean_sender_id,
            "receiver_email": clean_user_b_id,
            "transfer_timestamp": now_iso,
            "historical_valuation_at_transfer": item.get("AI Estimated Value") or item.get("estimated_value") or item.get("Cost") or 0.0,
            "transferStatus": "transferred",
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
    txn_fn = getattr(execute_claim_transaction, 'to_wrap', execute_claim_transaction) if not hasattr(transaction, '_clean_up') else execute_claim_transaction
    return txn_fn(
        transaction=transaction,
        db=db,
        transfer_ref=transfer_ref,
        clean_user_b_id=clean_user_b_id,
        selected_item_ids=selected_item_ids
    )


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
    for item_id in transfer_data.get("item_ids", []):
        for subcol in ["coins", "banknotes", "currency"]:
            item_ref = db.collection("users").document(clean_user_a_id).collection(subcol).document(item_id)
            if item_ref.get().exists:
                item_ref.update({
                    "transferStatus": "none",
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

    return {"transfer_id": transfer_id, "status": "recalled"}


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

    # Active record mutation (G1 partial quantity)
    if qty_to_sell < current_qty:
        new_qty = current_qty - qty_to_sell
        coin_ref.update({
            "Quantity": new_qty,
            "provenanceLedger": provenance,
            "updated_at": firestore.SERVER_TIMESTAMP
        })
    else:
        # Full sale: remove from active inventory
        coin_ref.delete()

    # Determine proper archive subcollection
    archive_subcol = "transferred_currency" if active_subcol in ["banknotes", "currency"] else "transferred_coins"

    archive_doc = {
        **item_data,
        "id": sale_archive_id,
        "original_coin_id": coin_id,
        "original_subcollection": active_subcol,
        "mode": "sold_outside",
        "status": "sold",
        "transfer_status": "sold",
        "sold_qty": qty_to_sell,
        "remaining_qty": current_qty - qty_to_sell,
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

    db.collection("users").document(clean_user_id).collection(archive_subcol).document(sale_archive_id).set(archive_doc)

    return {
        "status": "success",
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

    if active_snap.exists:
        active_data = active_snap.to_dict() or {}
        curr_qty = int(active_data.get("Quantity") or active_data.get("qty") or 1)
        restored_qty = curr_qty + sold_qty
        prov = list(active_data.get("provenanceLedger", []))
        prov.append(void_prov_entry)
        active_ref.update({
            "Quantity": restored_qty,
            "provenanceLedger": prov,
            "updated_at": firestore.SERVER_TIMESTAMP
        })
    else:
        # Full sale was deleted — resurrect original document
        resurrected_data = dict(arch_doc)
        for k in ["id", "original_coin_id", "original_subcollection", "mode", "status", "transfer_status",
                 "sold_qty", "remaining_qty", "unit_cost_basis_cents", "allocated_cost_basis_cents",
                 "sale_price_cents", "sale_price_usd", "fees_cents", "fees_usd", "net_proceeds_cents",
                 "net_proceeds_usd", "realized_profit_cents", "realized_profit_usd", "sale_date",
                 "sales_venue", "buyer_reference", "sold_at"]:
            resurrected_data.pop(k, None)
        prov = list(resurrected_data.get("provenanceLedger", []))
        prov.append(void_prov_entry)
        resurrected_data["id"] = orig_coin_id
        resurrected_data["Quantity"] = sold_qty
        resurrected_data["transferStatus"] = "none"
        resurrected_data["provenanceLedger"] = prov
        resurrected_data["updated_at"] = firestore.SERVER_TIMESTAMP
        active_ref.set(resurrected_data)

    # Mark archive document status = voided (Lock L3)
    arch_ref.update({
        "status": "voided",
        "transfer_status": "voided",
        "voided_at": now_iso
    })

    return {
        "status": "success",
        "message": f"Sale {sale_archive_id} successfully voided. Restored {sold_qty} unit(s).",
        "coin_id": orig_coin_id,
        "restored_qty": sold_qty
    }


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
