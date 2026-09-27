"""
Unit tests for Transfer Service, Passport PDF Generator, Feature Registry,
and Lateral Transfer Phase 1 (TC-1 to TC-7, TC-11, TC-12).
"""

import os
import sys

scan_service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scan_service"))
if scan_service_dir not in sys.path:
    sys.path.insert(0, scan_service_dir)

import pytest
import secrets
from unittest.mock import MagicMock
from services.transfer_service import (
    sanitize_item_payload,
    initiate_transfer,
    claim_transfer,
    recall_transfer,
    record_direct_sale,
    undo_sale,
    get_sold_inventory,
)
from services.passport_pdf_generator import generate_passport_pdf, format_financial_details
from services.feature_registry import registry, register_feature, FeatureDescriptor


# ─────────────────────────────────────────────────────────────────────────────
# In-Memory Firestore Mock for Test Automation
# ─────────────────────────────────────────────────────────────────────────────

class FakeSnapshot:
    def __init__(self, doc_id: str, data: dict = None, exists: bool = True):
        self.id = doc_id
        self._data = dict(data) if data is not None else None
        self.exists = exists

    def to_dict(self):
        return dict(self._data) if self._data is not None else None


class FakeDocRef:
    def __init__(self, doc_id: str, path: str, store: dict):
        self.id = doc_id
        self.path = path
        self._store = store

    def get(self, transaction=None):
        if self.path in self._store:
            return FakeSnapshot(self.id, self._store[self.path], exists=True)
        return FakeSnapshot(self.id, None, exists=False)

    def set(self, data, merge: bool = False):
        if merge and self.path in self._store:
            self._store[self.path].update(data)
        else:
            self._store[self.path] = dict(data)

    def update(self, data):
        if self.path not in self._store:
            raise ValueError(f"Document {self.path} does not exist to update")
        from google.cloud import firestore
        for k, v in data.items():
            if v == firestore.DELETE_FIELD:
                self._store[self.path].pop(k, None)
            else:
                self._store[self.path][k] = v

    def delete(self):
        self._store.pop(self.path, None)

    def collection(self, subcol_name: str):
        return FakeCollection(f"{self.path}/{subcol_name}", self._store)


class FakeCollection:
    def __init__(self, path: str, store: dict):
        self.path = path
        self._store = store

    def document(self, doc_id: str = None):
        if doc_id is None:
            import uuid
            doc_id = uuid.uuid4().hex[:12]
        return FakeDocRef(doc_id, f"{self.path}/{doc_id}", self._store)

    def stream(self):
        prefix = f"{self.path}/"
        for p, d in list(self._store.items()):
            if p.startswith(prefix):
                suffix = p[len(prefix):]
                if "/" not in suffix:
                    yield FakeSnapshot(suffix, d, exists=True)

    def get(self):
        return list(self.stream())

    def add(self, data):
        doc_ref = self.document()
        doc_ref.set(data)
        return None, doc_ref


class FakeTransaction:
    def __init__(self, store: dict):
        self._store = store

    def get(self, ref):
        return ref.get(transaction=self)

    def update(self, ref, data):
        ref.update(data)

    def set(self, ref, data, merge: bool = False):
        ref.set(data, merge=merge)

    def delete(self, ref):
        ref.delete()


class FakeBatch:
    def __init__(self, store: dict):
        self._store = store
        self._ops = []

    def set(self, ref, data, merge: bool = False):
        self._ops.append(("set", ref, data, merge))

    def update(self, ref, data):
        self._ops.append(("update", ref, data))

    def delete(self, ref):
        self._ops.append(("delete", ref))

    def commit(self):
        for op in self._ops:
            if op[0] == "set":
                op[1].set(op[2], merge=op[3])
            elif op[0] == "update":
                op[1].update(op[2])
            elif op[0] == "delete":
                op[1].delete()
        self._ops.clear()


class FakeFirestore:
    def __init__(self):
        self._store = {}

    def collection(self, col_name: str):
        return FakeCollection(col_name, self._store)

    def transaction(self):
        return FakeTransaction(self._store)

    def batch(self):
        return FakeBatch(self._store)


# ─────────────────────────────────────────────────────────────────────────────
# Baseline Existing Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_sanitize_item_payload():
    raw_item = {
        "id": "coin_123",
        "title": "1921 Morgan Silver Dollar",
        "grade": "MS-65",
        "purchase_price": 1250.0,
        "private_notes": "Inherited from grandfather",
        "storage_location": "Safe Box #4",
        "invoice_id": "INV-998822"
    }

    toggles = {
        "hide_cost_basis": True,
        "hide_private_notes": True,
        "hide_storage_location": True,
        "hide_invoices": True
    }

    sanitized = sanitize_item_payload(raw_item, toggles)

    assert "purchase_price" not in sanitized
    assert "private_notes" not in sanitized
    assert "storage_location" not in sanitized
    assert "invoice_id" not in sanitized
    assert sanitized["title"] == "1921 Morgan Silver Dollar"
    assert sanitized["grade"] == "MS-65"


def test_generate_passport_pdf():
    mock_transfer_data = {
        "transfer_id": "tf_test_9988",
        "claim_pin": "654321",
        "sender_id": "test_sender@numista.ai",
        "created_at": "2026-07-23T15:00:00Z",
        "expires_at": "2026-09-21T15:00:00Z",
        "items": [
            {
                "title": "1881-S Morgan Dollar",
                "year": "1881",
                "mint_mark": "S",
                "grade": "MS66",
                "category": "Coin"
            }
        ]
    }

    pdf_bytes = generate_passport_pdf(mock_transfer_data)

    assert pdf_bytes is not None
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")


def test_pdf_notes_filtering():
    essay_item = {
        "personalNotes": "This coin is the 1999 New Jersey state quarter, representing the third state admitted to the Union. Struck at the Denver Mint...",
        "storageLocation": "Binder 1"
    }
    fin_essay = format_financial_details(essay_item)
    assert "This coin is the 1999 New Jersey" not in fin_essay
    assert "Vault:</b> Binder 1" in fin_essay

    short_user_item = {
        "personalNotes": "bad condition, reverse scratch",
        "storageLocation": "Safe Box #2"
    }
    fin_user = format_financial_details(short_user_item)
    assert "Notes:</b> bad condition, reverse scratch" in fin_user


def test_feature_registry_registration():
    @register_feature(
        name="Test Capability",
        description="A test feature descriptor",
        keywords=["test", "capability"],
        synonyms=["check"],
        instructions="Run test capability",
        enabled=True
    )
    def dummy_func():
        pass

    feat = registry.get_feature("Test Capability")
    assert feat is not None
    assert feat.name == "Test Capability"
    assert "test" in feat.keywords

    prompt_context = registry.build_morgan_prompt_context()
    assert "Lateral Transfer" in prompt_context
    assert "Test Capability" in prompt_context


# ─────────────────────────────────────────────────────────────────────────────
# Phase 1 Test Cases: TC-1 to TC-7, TC-11, TC-12
# ─────────────────────────────────────────────────────────────────────────────

def test_tc1_mode3_direct_sale_partial_quantity_integer_cents():
    """
    TC-1: Mode 3 Sold Outside Numista (Addendum 2 G1, G2, Lock L1).
    2026 Morgan Proof 26XE (Qty 2, unit cost $169.00). Sell 1 unit at $250.00 with $15.00 fees.
    Expected: Kept coin Qty = 1, unit cost = $169.00. Archive shows profit $66.00 in integer cents.
    """
    db = FakeFirestore()
    user_id = "grokbot@numista.ai"
    coin_id = "coin_26xe_test"

    db.collection("users").document(user_id).collection("coins").document(coin_id).set({
        "title": "2026-W Morgan Silver Dollar Proof",
        "denomination": "Dollar",
        "Quantity": 2,
        "Cost": "$169.00",
        "Purchase Cost": "$169.00",
        "retailerItemNo": "26XE",
        "provenanceLedger": []
    })

    res = record_direct_sale(
        db=db,
        user_id=user_id,
        coin_id=coin_id,
        qty_sold=1,
        sale_price_usd=250.0,
        fees_usd=15.0,
        sales_venue="eBay",
        buyer_reference="EBAY-ORD-991"
    )

    # Return dictionary assertions
    assert res["status"] == "success"
    assert res["qty_sold"] == 1
    assert res["remaining_qty"] == 1
    assert res["unit_cost_basis"] == 169.0
    assert res["allocated_cost_basis"] == 169.0
    assert res["gross_sale_price"] == 250.0
    assert res["fees"] == 15.0
    assert res["realized_profit"] == 66.0  # $250 - $15 - $169 = $66.00

    # Active coin doc assertions (Gate 0 & Lock L1)
    active_snap = db.collection("users").document(user_id).collection("coins").document(coin_id).get()
    assert active_snap.exists is True
    active_coin = active_snap.to_dict()
    assert active_coin["Quantity"] == 1
    assert active_coin["retailerItemNo"] == "26XE"
    assert len(active_coin["provenanceLedger"]) == 1
    assert active_coin["provenanceLedger"][0]["event"] == "Direct Sale (Outside Numista.AI)"

    # Archive record assertions (G2 integer cents math)
    archive_id = res["sale_archive_id"]
    arch_snap = db.collection("users").document(user_id).collection("transferred_coins").document(archive_id).get()
    assert arch_snap.exists is True
    arch_data = arch_snap.to_dict()
    assert arch_data["status"] == "sold"
    assert arch_data["mode"] == "sold_outside"
    assert arch_data["unit_cost_basis_cents"] == 16900
    assert arch_data["allocated_cost_basis_cents"] == 16900
    assert arch_data["sale_price_cents"] == 25000
    assert arch_data["fees_cents"] == 1500
    assert arch_data["net_proceeds_cents"] == 23500
    assert arch_data["realized_profit_cents"] == 6600
    assert arch_data["realized_profit_usd"] == 66.0
    assert arch_data["retailerItemNo"] == "26XE"


def test_tc2_mode1_partial_transfer_and_claim():
    """
    TC-2: Mode 1 Partial Quantity Transfer & Claim (G1).
    Sender transfers 1 of 2 coins. On claim, sender retains 1 coin; recipient receives 1 coin.
    """
    db = FakeFirestore()
    sender_id = "grokbot@numista.ai"
    recipient_id = "test_recipient@numista.ai"
    coin_id = "coin_26xe_mode1"

    db.collection("users").document(sender_id).collection("coins").document(coin_id).set({
        "title": "2026-W Morgan Silver Dollar Proof",
        "denomination": "Dollar",
        "Quantity": 2,
        "Cost": "$169.00",
        "retailerItemNo": "26XE",
        "owner_photos": ["https://storage/private.jpg"],
        "provenanceLedger": []
    })

    # Initiate partial transfer
    init_res = initiate_transfer(
        db=db,
        user_a_id=sender_id,
        item_ids=[coin_id],
        recipient_email=recipient_id,
        item_quantities={coin_id: 1}
    )
    transfer_id = init_res["transfer_id"]
    claim_pin = init_res["claim_pin"]

    # Verify pending lock on sender
    sender_coin = db.collection("users").document(sender_id).collection("coins").document(coin_id).get().to_dict()
    assert sender_coin["pendingTransferQty"] == 1
    assert sender_coin["transferStatus"] == "pending"

    # Execute claim
    claim_res = claim_transfer(
        db=db,
        user_b_id=recipient_id,
        transfer_id=transfer_id,
        claim_pin=claim_pin,
        selected_item_ids=[coin_id]
    )
    assert claim_res["status"] == "claimed"

    # Sender retained coin
    updated_sender = db.collection("users").document(sender_id).collection("coins").document(coin_id).get().to_dict()
    assert updated_sender["Quantity"] == 1
    assert updated_sender.get("pendingTransferQty") is None

    # Recipient adopted coin
    rec_coins = list(db.collection("users").document(recipient_id).collection("coins").stream())
    assert len(rec_coins) == 1
    rec_coin = rec_coins[0].to_dict()
    assert rec_coin["Quantity"] == 1
    assert rec_coin["retailerItemNo"] == "26XE"
    assert "owner_photos" not in rec_coin


def test_tc3_mode1_recall_partial_transfer():
    """
    TC-3: Mode 1 Recall Partial Transfer (Bug B1 & G1).
    Recall restores pendingTransferQty back to active vault and clears archive ghost copy.
    """
    db = FakeFirestore()
    sender_id = "grokbot@numista.ai"
    coin_id = "coin_recall_test"

    db.collection("users").document(sender_id).collection("coins").document(coin_id).set({
        "title": "1921 Morgan Dollar",
        "Quantity": 2,
        "Cost": "$45.00"
    })

    init_res = initiate_transfer(
        db=db,
        user_a_id=sender_id,
        item_ids=[coin_id],
        item_quantities={coin_id: 1}
    )
    transfer_id = init_res["transfer_id"]

    recall_res = recall_transfer(db=db, user_id=sender_id, transfer_id=transfer_id)
    assert recall_res["status"] == "recalled"

    # Sender inventory restored to full available quantity
    active_coin = db.collection("users").document(sender_id).collection("coins").document(coin_id).get().to_dict()
    assert active_coin["transferStatus"] == "none"
    assert active_coin.get("pendingTransferQty") is None


def test_tc4_banknote_transfer_and_recall_b1():
    """
    TC-4: Bug B1 Banknote Collection Restoration and Case-Insensitive UID.
    """
    db = FakeFirestore()
    sender_id = "grokbot@numista.ai"
    note_id = "banknote_1896_test"

    db.collection("users").document(sender_id).collection("banknotes").document(note_id).set({
        "title": "1896 $1 Silver Certificate",
        "item_type": "banknote",
        "Quantity": 1
    })

    init_res = initiate_transfer(db=db, user_a_id=sender_id, item_ids=[note_id])
    transfer_id = init_res["transfer_id"]

    # Call recall with UPPERCASE email
    recall_res = recall_transfer(db=db, user_id="GROKBOT@NUMISTA.AI", transfer_id=transfer_id)
    assert recall_res["status"] == "recalled"

    restored_note = db.collection("users").document(sender_id).collection("banknotes").document(note_id).get().to_dict()
    assert restored_note["transferStatus"] == "none"


def test_tc5_partial_claim_unselected_release_b2():
    """
    TC-5: Bug B2 Partial Claim releases unselected items back to sender.
    """
    db = FakeFirestore()
    sender_id = "grokbot@numista.ai"
    recipient_id = "test_recipient@numista.ai"
    coin_a = "coin_a"
    coin_b = "coin_b"

    db.collection("users").document(sender_id).collection("coins").document(coin_a).set({
        "title": "Coin A", "Quantity": 1
    })
    db.collection("users").document(sender_id).collection("coins").document(coin_b).set({
        "title": "Coin B", "Quantity": 1
    })

    init_res = initiate_transfer(db=db, user_a_id=sender_id, item_ids=[coin_a, coin_b])
    transfer_id = init_res["transfer_id"]
    pin = init_res["claim_pin"]

    claim_res = claim_transfer(
        db=db,
        user_b_id=recipient_id,
        transfer_id=transfer_id,
        claim_pin=pin,
        selected_item_ids=[coin_a]
    )
    assert claim_res["status"] == "claimed"

    # coin_a adopted by recipient, deleted from sender
    assert db.collection("users").document(sender_id).collection("coins").document(coin_a).get().exists is False
    assert len(list(db.collection("users").document(recipient_id).collection("coins").stream())) == 1

    # coin_b unlocked and restored to sender
    released_b = db.collection("users").document(sender_id).collection("coins").document(coin_b).get().to_dict()
    assert released_b["transferStatus"] == "none"


def test_tc6_pin_entropy_secrets_b3():
    """
    TC-6: Bug B3 Cryptographic PIN Entropy via secrets module.
    """
    db = FakeFirestore()
    pins = set()
    for _ in range(10):
        res = initiate_transfer(db=db, user_a_id="grokbot@numista.ai", item_ids=[])
        pin = res["claim_pin"]
        assert len(pin) == 6
        assert pin.isdigit()
        pin_int = int(pin)
        assert 100000 <= pin_int <= 999999
        pins.add(pin)
    assert len(pins) >= 9


def test_tc7_privacy_sanitization_b4():
    """
    TC-7: Bug B4 Privacy sanitization scrubs owner photos and financials.
    """
    raw_item = {
        "id": "coin_privacy",
        "title": "2026-W Morgan Silver Dollar",
        "owner_photos": ["https://storage/private1.jpg"],
        "user_photos": ["https://storage/private2.jpg"],
        "images_user": ["https://storage/private3.jpg"],
        "storage_location": "Safe Box #9",
        "purchase_price": 169.0,
        "private_notes": "Bought at release"
    }
    sanitized = sanitize_item_payload(raw_item, {
        "hide_owner_photos": True,
        "hide_cost_basis": True,
        "hide_storage_location": True,
        "hide_private_notes": True
    })
    assert "owner_photos" not in sanitized
    assert "user_photos" not in sanitized
    assert "images_user" not in sanitized
    assert "storage_location" not in sanitized
    assert "purchase_price" not in sanitized
    assert "private_notes" not in sanitized
    assert sanitized["title"] == "2026-W Morgan Silver Dollar"


def test_tc11_undo_mode3_sale_l3():
    """
    TC-11: CoS Lock L3 Undo Sale.
    Restores Quantity and cost basis, marks archive status = 'voided' (not deleted),
    and appends provenance entry.
    """
    db = FakeFirestore()
    user_id = "grokbot@numista.ai"
    coin_id = "coin_26xe_undo"

    db.collection("users").document(user_id).collection("coins").document(coin_id).set({
        "title": "2026-W Morgan Silver Dollar",
        "Quantity": 2,
        "Cost": "$169.00",
        "retailerItemNo": "26XE",
        "provenanceLedger": []
    })

    # Sell 1 of 2
    sale_res = record_direct_sale(
        db=db,
        user_id=user_id,
        coin_id=coin_id,
        qty_sold=1,
        sale_price_usd=250.0,
        fees_usd=15.0
    )
    sale_archive_id = sale_res["sale_archive_id"]

    # Undo the sale
    undo_res = undo_sale(db=db, user_id=user_id, sale_archive_id=sale_archive_id)
    assert undo_res["status"] == "success"
    assert undo_res["restored_qty"] == 1

    # Active coin quantity restored back to 2
    active_coin = db.collection("users").document(user_id).collection("coins").document(coin_id).get().to_dict()
    assert active_coin["Quantity"] == 2
    last_prov = active_coin["provenanceLedger"][-1]
    assert last_prov["event"] == "Sale Voided / Undone"

    # Archive record is NOT deleted; marked status = voided (Lock L3)
    arch_doc = db.collection("users").document(user_id).collection("transferred_coins").document(sale_archive_id).get().to_dict()
    assert arch_doc["status"] == "voided"
    assert arch_doc["transfer_status"] == "voided"
    assert "voided_at" in arch_doc


def test_tc12_estate_report_wording_l4():
    """
    TC-12: CoS Lock L4 Estate Report Disposed Section Wording & Void Exclusion.
    Must render exact wording:
    "The owner recorded these items as sold or given away. Dates and details are as the owner entered them. If you find one of these items, it may not have left the collection."
    Strictly excludes voided sales.
    """
    from scan_service.estate_report_generator import fetch_sold_items
    from scan_service.estate_pdf_builder import _sold_disposed_section, _styles

    db = FakeFirestore()
    user_id = "grokbot@numista.ai"

    # Active sold coin
    db.collection("users").document(user_id).collection("transferred_coins").document("sale_active").set({
        "title": "2026-W Morgan Silver Dollar Proof (26XE)",
        "status": "sold",
        "sale_date": "2026-09-27",
        "sales_venue": "eBay",
        "sold_qty": 1,
        "sale_price_usd": 250.0
    })

    # Voided / undone sale (must be strictly excluded per Lock L4)
    db.collection("users").document(user_id).collection("transferred_coins").document("sale_voided").set({
        "title": "1881-S Morgan Dollar (Voided)",
        "status": "voided",
        "transfer_status": "voided",
        "sale_date": "2026-09-25",
        "sold_qty": 1,
        "sale_price_usd": 150.0
    })

    # Recalled transfer (must also be excluded)
    db.collection("users").document(user_id).collection("transferred_coins").document("sale_recalled").set({
        "title": "1921 Morgan Dollar (Recalled)",
        "status": "recalled",
        "transfer_status": "recalled",
        "sold_qty": 1
    })

    sold_items = fetch_sold_items(db, user_id)
    assert len(sold_items) == 1
    assert sold_items[0]["title"] == "2026-W Morgan Silver Dollar Proof (26XE)"

    st = _styles()
    ctx = {"sold_items": sold_items}
    story = _sold_disposed_section(ctx, st)
    assert len(story) > 0

    all_texts = []
    for flowable in story:
        if hasattr(flowable, "text"):
            all_texts.append(flowable.text)
        elif hasattr(flowable, "_cellvalues"):
            for row in flowable._cellvalues:
                for cell in row:
                    if hasattr(cell, "text"):
                        all_texts.append(cell.text)

    combined_text = " ".join(all_texts)
    exact_required_phrase = (
        "The owner recorded these items as sold or given away. "
        "Dates and details are as the owner entered them. "
        "If you find one of these items, it may not have left the collection."
    )
    assert exact_required_phrase in combined_text
    assert "2026-W Morgan Silver Dollar Proof (26XE)" in combined_text
    assert "1881-S Morgan Dollar (Voided)" not in combined_text


def test_tc13_undo_mode3_full_sale_resurrection_sf1_sf7():
    """
    TC-13: Full Sale Undo (Resurrection), SF1 (unit cost basis restoration) & SF7 (Quantity in archive).
    - Checks archive doc sets Quantity == sold_qty (SF7).
    - Checks full sale removes active coin.
    - Checks undo resurrects coin with original unit cost_basis (not total allocated) and original created_at (SF1).
    """
    db = FakeFirestore()
    user_id = "grokbot@numista.ai"
    coin_id = "coin_multi_qty_full_sale"
    orig_created_at = "2026-01-15T08:30:00Z"

    db.collection("users").document(user_id).collection("coins").document(coin_id).set({
        "title": "1921 Morgan Silver Dollar",
        "Quantity": 3,
        "Cost": "$45.00",
        "cost_basis": 45.0,
        "created_at": orig_created_at,
        "provenanceLedger": []
    })

    # Record full sale of all 3 units at $60 each ($180 total)
    sale_res = record_direct_sale(
        db=db,
        user_id=user_id,
        coin_id=coin_id,
        qty_sold=3,
        sale_price_usd=180.0,
        fees_usd=10.0,
        sales_venue="eBay"
    )
    sale_archive_id = sale_res["sale_archive_id"]

    # Active coin should be deleted
    assert db.collection("users").document(user_id).collection("coins").document(coin_id).get().exists is False

    # Archive document inspection (SF7 & SF1)
    arch_doc = db.collection("users").document(user_id).collection("transferred_coins").document(sale_archive_id).get().to_dict()
    assert arch_doc["Quantity"] == 3  # SF7: matches sold_qty, not stale pre-sale count
    assert arch_doc["sold_qty"] == 3
    assert arch_doc["cost_basis"] == 135.0  # 3 * $45 allocated cost basis for the sale
    assert arch_doc["original_cost_basis"] == 45.0  # SF1: stored original unit cost basis
    assert arch_doc["original_created_at"] == orig_created_at  # SF1: stored original creation timestamp

    # Undo full sale
    undo_res = undo_sale(db=db, user_id=user_id, sale_archive_id=sale_archive_id)
    assert undo_res["status"] == "success"
    assert undo_res["restored_qty"] == 3

    # Active coin must be resurrected with unit cost basis and original created_at
    resurrected_coin = db.collection("users").document(user_id).collection("coins").document(coin_id).get().to_dict()
    assert resurrected_coin is not None
    assert resurrected_coin["Quantity"] == 3
    assert resurrected_coin["Cost"] == "$45.00"
    assert resurrected_coin["cost_basis"] == 45.0  # SF1: unit cost, NOT $135
    assert resurrected_coin["created_at"] == orig_created_at  # SF1: preserved original created_at
    assert resurrected_coin["transferStatus"] == "none"

    # Archive marked voided
    arch_updated = db.collection("users").document(user_id).collection("transferred_coins").document(sale_archive_id).get().to_dict()
    assert arch_updated["status"] == "voided"
    assert arch_updated["transfer_status"] == "voided"

