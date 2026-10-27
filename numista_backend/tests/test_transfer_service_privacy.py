"""
Unit tests for Lateral Transfer Privacy & Archive Integrity (Target B: Bugs B1, B2, B3)
in numista_backend/services/transfer_service.py.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import pytest

from services.transfer_service import (
    COLLECTION_TRANSFERS,
    claim_transfer,
    execute_claim_transaction,
    initiate_transfer,
    sanitize_item_payload,
)


# ── In-memory Fake Firestore for Transactional & Subcollection Testing ───────


class _FakeSnapshot:
    def __init__(self, doc_id: str, data: Optional[Dict[str, Any]]):
        self.id = doc_id
        self._data = dict(data) if data is not None else None

    @property
    def exists(self) -> bool:
        return self._data is not None

    def to_dict(self) -> Optional[Dict[str, Any]]:
        return dict(self._data) if self._data is not None else None


class _FakeDocRef:
    def __init__(self, store: Dict[str, Dict[str, Any]], path: str):
        self._store = store
        self.path = path
        self.id = path.split("/")[-1]

    def get(self, transaction: Any = None) -> _FakeSnapshot:
        return _FakeSnapshot(self.id, self._store.get(self.path))

    def set(self, data: Dict[str, Any], merge: bool = False) -> None:
        if merge and self.path in self._store:
            merged = dict(self._store[self.path])
            merged.update(data)
            self._store[self.path] = merged
        else:
            self._store[self.path] = dict(data)

    def update(self, data: Dict[str, Any]) -> None:
        if self.path not in self._store:
            raise KeyError(f"Document {self.path} does not exist")
        doc = dict(self._store[self.path])
        for k, v in data.items():
            if getattr(v, "__class__", None).__name__ == "Sentinel" or str(v) == "Sentinel: Value used to delete a field in a document.":
                doc.pop(k, None)
            else:
                doc[k] = v
        self._store[self.path] = doc

    def delete(self) -> None:
        self._store.pop(self.path, None)

    def collection(self, name: str) -> "_FakeColRef":
        return _FakeColRef(self._store, f"{self.path}/{name}")


class _FakeColRef:
    def __init__(self, store: Dict[str, Dict[str, Any]], path: str):
        self._store = store
        self.path = path

    def document(self, doc_id: str) -> _FakeDocRef:
        return _FakeDocRef(self._store, f"{self.path}/{doc_id}")

    def add(self, data: Dict[str, Any]) -> None:
        self._store[f"{self.path}/auto_{len(self._store)}"] = dict(data)


class _FakeTransaction:
    def __init__(self) -> None:
        self._read_only = False
        self._max_attempts = 1
        self._id = b"fake_txn"

    def set(self, ref: _FakeDocRef, data: Dict[str, Any], merge: bool = False) -> None:
        ref.set(data, merge=merge)

    def update(self, ref: _FakeDocRef, data: Dict[str, Any]) -> None:
        ref.update(data)

    def delete(self, ref: _FakeDocRef) -> None:
        ref.delete()


class _FakeDB:
    def __init__(self) -> None:
        self.store: Dict[str, Dict[str, Any]] = {}

    def collection(self, name: str) -> _FakeColRef:
        return _FakeColRef(self.store, name)

    def transaction(self) -> _FakeTransaction:
        return _FakeTransaction()


# ── Bug B1: Golden Schema & paper_trail Sanitization ─────────────────────────


def test_sanitize_item_payload_strips_golden_schema_and_paper_trail():
    raw_coin = {
        "id": "coin-1",
        "Year": "1909",
        "Mint Mark": "S",
        "Variety": "VDB",
        "Denomination": "$0.01",
        "Cost": "$1,450.00",
        "Purchase Cost": 1450.0,
        "Purchase Date": "2025-11-12",
        "cost": 1450.0,
        "set_cost_label": "$1,450.00 (Set)",
        "Personal Notes": "Bought from estate auction, secret reserve",
        "Personal Notes I": "Legacy private note",
        "Storage Location": "Bank Box #42",
        "Retailer/Website": "Heritage Auctions",
        "Retailer/Dealer": "HA.com",
        "Retailer Invoice #": "INV-99881",
        "Retailer Item No.": "LOT-4421",
        "receipt_id": "rcpt_123",
        "receipt_gcs_path": "gs://numista-vault/receipts/rcpt_123.pdf",
        "paper_trail": {
            "receipt_id": "rcpt_123",
            "receipt_filename": "heritage_invoice.pdf",
            "purchase_date": "2025-11-12",
            "purchase_price": "$1,450.00",
            "retailer": "Heritage Auctions",
            "gcs_path": "gs://numista-vault/receipts/rcpt_123.pdf",
        },
    }

    clean = sanitize_item_payload(
        raw_coin,
        {
            "hide_cost_basis": True,
            "hide_private_notes": True,
            "hide_storage_location": True,
            "hide_invoices": True,
            "hide_owner_photos": True,
        },
    )

    # Public numismatic identity preserved
    assert clean["Year"] == "1909"
    assert clean["Mint Mark"] == "S"
    assert clean["Variety"] == "VDB"

    # All Golden Schema & legacy private fields stripped
    for forbidden_key in [
        "Cost",
        "Purchase Cost",
        "Purchase Date",
        "cost",
        "set_cost_label",
        "Personal Notes",
        "Personal Notes I",
        "Storage Location",
        "Retailer/Website",
        "Retailer/Dealer",
        "Retailer Invoice #",
        "Retailer Item No.",
        "receipt_id",
        "receipt_gcs_path",
        "paper_trail",
    ]:
        assert forbidden_key not in clean, f"Expected {forbidden_key} to be stripped"


def test_sanitize_item_payload_partial_paper_trail_when_only_cost_hidden():
    raw_coin = {
        "id": "coin-2",
        "Cost": "$85.00",
        "Purchase Date": "2026-01-15",
        "Retailer/Website": "US Mint",
        "paper_trail": {
            "receipt_id": "rcpt_77",
            "retailer": "US Mint",
            "purchase_price": "$85.00",
            "purchase_date": "2026-01-15",
        },
    }

    clean = sanitize_item_payload(
        raw_coin,
        {
            "hide_cost_basis": True,
            "hide_private_notes": False,
            "hide_storage_location": False,
            "hide_invoices": False,
        },
    )

    assert "Cost" not in clean
    assert "Purchase Date" not in clean
    assert clean["Retailer/Website"] == "US Mint"
    assert "paper_trail" in clean
    assert "purchase_price" not in clean["paper_trail"]
    assert "purchase_date" not in clean["paper_trail"]
    assert clean["paper_trail"]["retailer"] == "US Mint"


# ── Bugs B2 & B3: Partial Claim Ghost Cleanup + Sender Archive Integrity ─────


def test_partial_claim_deletes_unselected_ghost_archive_and_preserves_sender_private_data():
    db = _FakeDB()
    sender = "alice@numista.ai"
    recipient = "bob@numista.ai"

    # Seed two coins in Alice's active collection
    db.collection("users").document(sender).collection("coins").document("coin-claimed").set({
        "id": "coin-claimed",
        "Year": "1921",
        "Mint Mark": "D",
        "Denomination": "$1",
        "Quantity": 1,
        "Cost": "$95.00",
        "Personal Notes": "Keep cost private from Bob",
        "Storage Location": "Safe Row 2",
        "Retailer/Website": "APMEX",
        "paper_trail": {
            "receipt_id": "r-1",
            "purchase_price": "$95.00",
            "retailer": "APMEX",
        },
    })
    db.collection("users").document(sender).collection("coins").document("coin-unselected").set({
        "id": "coin-unselected",
        "Year": "1964",
        "Mint Mark": "P",
        "Denomination": "$0.50",
        "Quantity": 1,
        "Cost": "$18.00",
    })

    # Initiate transfer of both coins with all privacy switches ON
    transfer_doc = initiate_transfer(
        db=db,
        user_a_id=sender,
        item_ids=["coin-claimed", "coin-unselected"],
        privacy_toggles={
            "hide_cost_basis": True,
            "hide_private_notes": True,
            "hide_storage_location": True,
            "hide_invoices": True,
            "hide_owner_photos": True,
        },
    )
    transfer_id = transfer_doc["transfer_id"]

    # Both items initially have pending archive docs in Alice's transferred_coins
    assert f"users/{sender}/transferred_coins/coin-claimed" in db.store
    assert f"users/{sender}/transferred_coins/coin-unselected" in db.store

    # Bob claims ONLY "coin-claimed" (partial claim) via claim_transfer
    result = claim_transfer(
        db=db,
        user_b_id=recipient,
        transfer_id=transfer_id,
        claim_pin=transfer_doc["claim_pin"],
        selected_item_ids=["coin-claimed"],
    )

    assert result["status"] == "claimed"
    assert result["items_claimed_count"] == 1

    # 1. Bug B1 verification: Bob's new coin doc has NO leaked Cost, Notes, Storage, or paper_trail
    bob_coin = result["claimed_items"][0]
    assert "Cost" not in bob_coin
    assert "Personal Notes" not in bob_coin
    assert "Storage Location" not in bob_coin
    assert "Retailer/Website" not in bob_coin
    assert "paper_trail" not in bob_coin

    # 2. Bug B2 verification: Unselected coin's active doc is unlocked AND its pending ghost archive is deleted
    unselected_active = db.store[f"users/{sender}/coins/coin-unselected"]
    assert unselected_active["transferStatus"] == "none"
    assert f"users/{sender}/transferred_coins/coin-unselected" not in db.store

    # 3. Bug B3 verification: Alice's archive doc for "coin-claimed" retains her private Cost, Notes, and paper_trail
    alice_archive = db.store[f"users/{sender}/transferred_coins/coin-claimed"]
    assert alice_archive["transferStatus"] == "transferred"
    assert alice_archive["transfer_status"] == "transferred"
    assert alice_archive["Cost"] == "$95.00"
    assert alice_archive["Personal Notes"] == "Keep cost private from Bob"
    assert alice_archive["Storage Location"] == "Safe Row 2"
    assert alice_archive["paper_trail"]["purchase_price"] == "$95.00"
    assert alice_archive["historical_valuation_at_transfer"] == "$95.00"
