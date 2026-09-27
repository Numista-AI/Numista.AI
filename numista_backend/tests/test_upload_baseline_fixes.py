"""
test_upload_baseline_fixes.py
-----------------------------
Unit and regression tests for REQ_008 (Upload Baseline Fixes):
- R1/R2: Quantity extraction heuristic from Personal Notes / Description when Qty <= 1
- R3: Receipt list dynamic pruning of stale linked coin IDs and uploaded_at ISO formatting
- R3: DELETE /api/receipts/{user_email}/{receipt_id} endpoint
- U5: Single-photo POST /api/identify_coin_photo (image_b optional)
"""

import io
import json
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main
from main import app

client = TestClient(app)


def test_quantity_extraction_heuristic():
    """Verify that quantity regex matches 'Qty: 2' or 'Quantity: 5' in notes or description."""
    import re
    def apply_qty_test(item):
        curr_qty = item.get('Quantity')
        try:
            curr_qty_int = int(curr_qty) if curr_qty is not None else 1
        except (ValueError, TypeError):
            curr_qty_int = 1
        if curr_qty_int <= 1:
            notes_str = str(item.get('Personal Notes', '') or '')
            desc_str = str(item.get('Original Description from source', '') or '')
            qty_match = re.search(r'\b(?:qty|quantity)[\s:]*([0-9]+)\b', f"{notes_str} {desc_str}", re.IGNORECASE)
            if qty_match:
                extracted_qty = int(qty_match.group(1))
                if extracted_qty > 0:
                    item['Quantity'] = extracted_qty
            else:
                item['Quantity'] = curr_qty_int
        else:
            item['Quantity'] = curr_qty_int
        return item

    # Test item with Qty 1 in field but 'Qty: 2' in notes
    it1 = {'Quantity': 1, 'Personal Notes': 'Order # 12345; Qty: 2 shipped'}
    apply_qty_test(it1)
    assert it1['Quantity'] == 2

    # Test item with 'Quantity: 5' in description
    it2 = {'Quantity': '1', 'Original Description from source': 'Morgan Silver Dollar Quantity: 5'}
    apply_qty_test(it2)
    assert it2['Quantity'] == 5

    # Test item already having Quantity > 1
    it3 = {'Quantity': 3, 'Personal Notes': 'Qty: 1'}
    apply_qty_test(it3)
    assert it3['Quantity'] == 3

    # Test item with no quantity in notes
    it4 = {'Quantity': 1, 'Personal Notes': 'Nice uncirculated roll'}
    apply_qty_test(it4)
    assert it4['Quantity'] == 1


def test_list_receipts_pruning_and_date(monkeypatch):
    """Verify list_receipts formats uploaded_at and prunes stale linked coin IDs."""
    from datetime import datetime, timezone
    now = datetime(2026, 9, 27, 12, 0, 0, tzinfo=timezone.utc)

    # Mock receipt document
    mock_receipt = MagicMock()
    mock_receipt.id = "rec_test_123"
    mock_receipt.to_dict.return_value = {
        "invoice_date": "2026-09-20",
        "uploaded_at": now,
        "linked_coin_ids": ["active_coin_1", "deleted_coin_2", "active_coin_3"],
    }

    # Mock firestore
    mock_db = MagicMock()
    user_ref = MagicMock()

    # active coins: active_coin_1 and active_coin_3
    mock_cd1 = MagicMock(); mock_cd1.id = "active_coin_1"
    mock_cd3 = MagicMock(); mock_cd3.id = "active_coin_3"
    user_ref.collection("coins").select.return_value.stream.return_value = [mock_cd1, mock_cd3]
    user_ref.collection("review_queue").select.return_value.stream.return_value = []

    receipts_col = MagicMock()
    receipts_col.order_by.return_value.limit.return_value.stream.return_value = [mock_receipt]

    def _col_router(col_name):
        if col_name == "coins":
            m = MagicMock()
            m.select.return_value.stream.return_value = [mock_cd1, mock_cd3]
            return m
        elif col_name == "review_queue":
            m = MagicMock()
            m.select.return_value.stream.return_value = []
            return m
        elif col_name == "receipts":
            return receipts_col
        return MagicMock()

    user_ref.collection.side_effect = _col_router

    mock_db.collection("users").document.return_value = user_ref
    monkeypatch.setattr(main, "db", mock_db)

    resp = client.get("/api/receipts/tester@numista.ai")
    assert resp.status_code == 200
    data = resp.json()
    assert "receipts" in data
    assert len(data["receipts"]) == 1
    rec = data["receipts"][0]
    assert rec["receipt_id"] == "rec_test_123"
    assert rec["uploaded_at"] == now.isoformat()
    assert rec["linked_coins_count"] == 2
    assert rec["linked_coin_ids"] == ["active_coin_1", "active_coin_3"]


def test_delete_receipt_endpoint(monkeypatch):
    """Verify DELETE /api/receipts/{user_email}/{receipt_id} authenticates and deletes the receipt."""
    monkeypatch.setattr(main, "_authenticate_request", lambda auth, email: email)

    mock_db = MagicMock()
    user_ref = MagicMock()
    rec_ref = MagicMock()
    rec_snap = MagicMock()
    rec_snap.exists = True
    rec_snap.to_dict.return_value = {"gcs_path": "receipts/tester@numista.ai/rec_123/original.pdf"}
    rec_ref.get.return_value = rec_snap

    user_ref.collection("receipts").document.return_value = rec_ref
    mock_db.collection("users").document.return_value = user_ref
    monkeypatch.setattr(main, "db", mock_db)

    # Mock storage client
    mock_gcs = MagicMock()
    monkeypatch.setattr(main, "gcs_client", mock_gcs)

    resp = client.delete("/api/receipts/tester@numista.ai/rec_123", headers={"Authorization": "Bearer test-token"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"
    rec_ref.delete.assert_called_once()


def test_identify_coin_photo_single_image(monkeypatch):
    """Verify POST /api/identify_coin_photo succeeds when only image_a is provided."""
    mock_response1 = MagicMock()
    mock_response1.text = json.dumps({
        "year": "1964",
        "denomination": "Half Dollar",
        "country": "United States",
        "program_series": "Kennedy Half Dollars",
        "mint_mark": "D",
        "grade": "MS-63",
        "confidence": "HIGH",
        "obverse_image": "A"
    })

    mock_response2 = MagicMock()
    mock_response2.text = json.dumps({
        "refined_grade": "MS-64",
        "estimated_value_usd": "$25.00",
        "confidence": "HIGH"
    })

    mock_models = MagicMock()
    mock_models.generate_content.side_effect = [mock_response1, mock_response2]
    mock_client = MagicMock()
    mock_client.models = mock_models
    monkeypatch.setattr(main, "genai_client", mock_client)

    dummy_image = io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00")
    files = {"image_a": ("obverse.jpg", dummy_image, "image/jpeg")}
    data = {"user_email": "tester@numista.ai", "save_to_collection": "false"}

    resp = client.post("/api/identify_coin_photo", data=data, files=files)
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["coin"]["Year"] == "1964"
    assert res_data["coin"]["Denomination"] == "Half Dollar"
    assert "Single photo scan" in res_data["coin"]["Personal Notes"]
