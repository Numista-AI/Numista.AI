"""
test_bulk_update.py
-------------------
Unit tests for POST /api/review/bulk_update endpoint.
Verifies:
1. Normalization of 'Storage Location' and 'storage_location' via KEY_ALIASES.
2. Dual-persistence of storage_location and Storage Location.
3. Allowed fields: storage_location, condition, notes, status.
4. Rejection of unauthorized keys with HTTP 400.
5. Email mismatch security guard with HTTP 403.
"""

import os
import sys
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app, get_current_user


@pytest.fixture
def auth_client():
    mock_user = {"email": "test@numista.ai", "uid": "uid-123"}
    app.dependency_overrides[get_current_user] = lambda: mock_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.pop(get_current_user, None)


def test_bulk_update_storage_location_dual_persist(monkeypatch, auth_client):
    mock_db = MagicMock()
    mock_batch = MagicMock()
    mock_db.batch.return_value = mock_batch
    monkeypatch.setattr("main.db", mock_db)

    payload = {
        "user_email": "test@numista.ai",
        "review_ids": ["doc_1", "doc_2"],
        "updates": {"Storage Location": "Safe Deposit Box A"}
    }
    response = auth_client.post("/api/review/bulk_update", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Verify batch.update called twice with dual-persisted storage_location and Storage Location
    assert mock_batch.update.call_count == 2
    for call in mock_batch.update.call_args_list:
        update_dict = call[0][1]
        assert update_dict["storage_location"] == "Safe Deposit Box A"
        assert update_dict["Storage Location"] == "Safe Deposit Box A"


def test_bulk_update_canonical_storage_location_dual_persist(monkeypatch, auth_client):
    mock_db = MagicMock()
    mock_batch = MagicMock()
    mock_db.batch.return_value = mock_batch
    monkeypatch.setattr("main.db", mock_db)

    payload = {
        "user_email": "test@numista.ai",
        "review_ids": ["doc_1"],
        "updates": {"storage_location": "Album 3"}
    }
    response = auth_client.post("/api/review/bulk_update", json=payload)
    assert response.status_code == 200
    update_dict = mock_batch.update.call_args[0][1]
    assert update_dict["storage_location"] == "Album 3"
    assert update_dict["Storage Location"] == "Album 3"


def test_bulk_update_invalid_key_rejected(auth_client):
    payload = {
        "user_email": "test@numista.ai",
        "review_ids": ["doc_1"],
        "updates": {"invalid_arbitrary_field": "some_value"}
    }
    response = auth_client.post("/api/review/bulk_update", json=payload)
    assert response.status_code == 400
    assert "Invalid update field" in response.json()["detail"]


def test_bulk_update_email_mismatch_rejected(auth_client):
    payload = {
        "user_email": "other_user@numista.ai",
        "review_ids": ["doc_1"],
        "updates": {"notes": "new note"}
    }
    response = auth_client.post("/api/review/bulk_update", json=payload)
    assert response.status_code == 403
    assert "Forbidden" in response.json()["detail"]
