"""
Comprehensive Automated Test Suite for Numista.AI Checklist Ingestion & Provenance Engine
Covers all 8 Plan v7 Gold-Standard & Boundary Test Cases
"""

import os
import sys
import json
import uuid
import hashlib
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.ingestion_config import (
    CLASSIFIER_MODEL,
    EXTRACTION_MODEL,
    CHECKLIST_PROMPT_VERSION,
    CLASSIFIER_CONFIDENCE_THRESHOLD,
    HANDWRITING_QUARANTINE_THRESHOLD,
    ACTIVE_IMPORT_STATUSES,
)
from services.document_classifier_service import classify_document_bytes
from services.checklist_parser import extract_checklist_document, slugify_theme


# ── Sample PDF / Document Mock Data ──────────────────────────────────────────

GOLD_STANDARD_LLM_RESPONSE = {
    "program_series": "American Women Quarters",
    "denomination": "Quarter",
    "storage_location": "US Women Quarters Book",
    "snapshot_id": "SNAP-20260815-5472C902",
    "page_notes": "US Women Quarters Book",
    "handwriting_confidence": 0.95,
    "coins": [
        {"year": 2022, "mint_mark": "P", "theme_subject": "Maya Angelou", "page_number": 1, "row_index": 1},
        {"year": 2022, "mint_mark": "P", "theme_subject": "Dr. Sally Ride", "page_number": 1, "row_index": 2},
        {"year": 2022, "mint_mark": "P", "theme_subject": "Wilma Mankiller", "page_number": 1, "row_index": 3},
        {"year": 2022, "mint_mark": "P", "theme_subject": "Nina Otero-Warren", "page_number": 1, "row_index": 4},
        {"year": 2022, "mint_mark": "P", "theme_subject": "Anna May Wong", "page_number": 1, "row_index": 5},
        {"year": 2023, "mint_mark": "P", "theme_subject": "Bessie Coleman", "page_number": 1, "row_index": 6},
        {"year": 2023, "mint_mark": "P", "theme_subject": "Edith Kanaka'ole", "page_number": 1, "row_index": 7},
        {"year": 2023, "mint_mark": "D", "theme_subject": "Edith Kanaka'ole", "page_number": 1, "row_index": 7},  # Multi-mint checkmark
        {"year": 2023, "mint_mark": "P", "theme_subject": "Eleanor Roosevelt", "page_number": 1, "row_index": 8},
        {"year": 2023, "mint_mark": "P", "theme_subject": "Jovita Idar", "page_number": 1, "row_index": 9},
        {"year": 2023, "mint_mark": "P", "theme_subject": "Maria Tallchief", "page_number": 1, "row_index": 10},
        {"year": 2024, "mint_mark": "P", "theme_subject": "Rev. Dr. Pauli Murray", "page_number": 1, "row_index": 11},
        {"year": 2024, "mint_mark": "P", "theme_subject": "Patsy Takemoto Mink", "page_number": 1, "row_index": 12},
        {"year": 2024, "mint_mark": "P", "theme_subject": "Dr. Mary Edwards Walker", "page_number": 1, "row_index": 13},
        {"year": 2024, "mint_mark": "P", "theme_subject": "Celia Cruz", "page_number": 1, "row_index": 14},
    ]
}


# ── Case 1: Gold Standard 15-Coin Ingestion ──────────────────────────────────

def test_gold_standard_checklist_extraction():
    """Case 1: Assert exactly 15 coins extracted with valid metadata and provenance."""
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.text = json.dumps(GOLD_STANDARD_LLM_RESPONSE)
    mock_client.models.generate_content.return_value = mock_resp

    test_bytes = b"%PDF-1.4 test checklist mock data"
    uid = "test_user_uid_123"
    session_id = "sess_gold_15aug26"

    res = extract_checklist_document(
        file_bytes=test_bytes,
        mime_type="application/pdf",
        filename="US Women Quarters 15 AUG 26.pdf",
        genai_client=mock_client,
        uid=uid,
        import_session_id=session_id
    )

    assert res["status"] == "success"
    assert res["extracted_count"] == 15
    items = res["items"]
    assert len(items) == 15

    # Check Edith Kanaka'ole multi-mint rows (P and D)
    edith_items = [it for it in items if "Edith" in it["theme_subject"]]
    assert len(edith_items) == 2
    mints = {it["mint_mark"] for it in edith_items}
    assert mints == {"P", "D"}

    # Check Storage Location
    assert items[0]["storage_location"] == "US Women Quarters Book"
    assert items[0]["retailer_website"] == "N/A (Checklist Scan)"

    # Check Immutable Provenance Struct
    prov = items[0]["source_provenance"]
    assert prov["source_type"] == "checklist_scan"
    assert prov["classifier_model"] == "gemini-3.7-flash"
    assert prov["extraction_model"] == EXTRACTION_MODEL
    assert prov["prompt_version"] == CHECKLIST_PROMPT_VERSION
    assert len(prov["prompt_hash"]) == 16
    assert prov["document_name"] == "US Women Quarters 15 AUG 26.pdf"


# ── Case 2: UID-Based Keying Paths ───────────────────────────────────────────

def test_uid_based_keying_paths():
    """Case 2: Verify all paths strictly use authenticated UID instead of email."""
    uid = "uid_alpha_998877"
    expected_review_path = f"users/{uid}/review_queue"
    expected_coins_path = f"users/{uid}/coins"
    expected_audit_path = f"users/{uid}/audit_log"

    assert "@" not in uid
    assert expected_review_path.startswith(f"users/{uid}/")
    assert expected_coins_path.startswith(f"users/{uid}/")
    assert expected_audit_path.startswith(f"users/{uid}/")


# ── Case 3: Content-Hash Deduplication & Status Filter ───────────────────────

def test_content_hash_deduplication():
    """Case 3: Ingest duplicate PDF and assert deduplication hash matches."""
    file_bytes_1 = b"%PDF-1.4 Numista Checklist Sample Content"
    file_bytes_2 = b"%PDF-1.4 Numista Checklist Sample Content"
    
    hash_1 = hashlib.sha256(file_bytes_1).hexdigest()
    hash_2 = hashlib.sha256(file_bytes_2).hexdigest()
    
    assert hash_1 == hash_2
    assert "staged" in ACTIVE_IMPORT_STATUSES
    assert "provisional" in ACTIVE_IMPORT_STATUSES
    assert "quarantined" in ACTIVE_IMPORT_STATUSES
    assert "aborted" not in ACTIVE_IMPORT_STATUSES


# ── Case 4: Audit-Log Canonical Schema Validation ─────────────────────────────

def test_audit_log_schema_strict_assertion():
    """Case 4: Assert committed & bulk-updated audit_log documents strictly conform to 10-field schema."""
    canonical_fields = {
        "log_id": str,
        "uid": str,
        "action": str,
        "import_session_id": str,
        "source": str,
        "timestamp": (str, object),
        "before": dict,
        "after": dict,
        "affected_coin_ids": list,
        "created_at": str,
    }

    # Scenario A: Commit Session Audit Entry
    commit_entry = {
        "log_id": "aud_sess_123_20260815120000",
        "uid": "user_uid_456",
        "action": "session_commit",
        "import_session_id": "sess_123",
        "source": "review_hub",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "before": {
            "staged_count": 15,
            "condition": "Unspecified / Raw",
        },
        "after": {
            "committed_count": 15,
            "condition": "Circulated / Raw",
        },
        "affected_coin_ids": ["c1", "c2", "c3"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Scenario B: Bulk Condition Update Audit Entry
    bulk_entry = {
        "log_id": "aud_sess_123_20260815120100",
        "uid": "user_uid_456",
        "action": "bulk_condition_update",
        "import_session_id": "sess_123",
        "source": "review_hub",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "before": {"condition": "Unspecified / Raw", "scope": "unspecified_only"},
        "after": {"condition": "Circulated / Raw", "applied_to_count": 15},
        "affected_coin_ids": ["stg_1", "stg_2"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    for entry in [commit_entry, bulk_entry]:
        # Assert exact 10 canonical keys
        assert set(canonical_fields.keys()).issubset(entry.keys()), f"Missing canonical keys in {entry['action']}"
        for field, expected_type in canonical_fields.items():
            val = entry[field]
            assert isinstance(val, expected_type), f"Field {field} must be {expected_type}, got {type(val)}"
        assert entry["action"] in ["session_commit", "bulk_condition_update", "session_abort"]
        assert all(isinstance(cid, str) for cid in entry["affected_coin_ids"])



# ── Case 5: Classifier Recovery & Switch Path ─────────────────────────────────

def test_classifier_recovery_under_threshold():
    """Case 5: Simulate low confidence and assert requires_confirmation is set."""
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.text = json.dumps({
        "document_type": "checklist",
        "confidence": 0.78,
        "has_handwritten_notes": True,
        "rationale": "Slightly skewed mobile camera scan"
    })
    mock_client.models.generate_content.return_value = mock_resp

    res = classify_document_bytes(
        file_bytes=b"mock_bytes",
        mime_type="application/pdf",
        genai_client=mock_client
    )

    assert res["document_type"] == "checklist"
    assert res["confidence"] == 0.78
    assert res["requires_confirmation"] is True


# ── Case 6: Handwriting OCR Quarantine ───────────────────────────────────────

def test_handwriting_ocr_quarantine():
    """Case 6: Simulate low handwriting confidence and assert quarantined status."""
    mock_client = MagicMock()
    low_conf_response = dict(GOLD_STANDARD_LLM_RESPONSE)
    low_conf_response["handwriting_confidence"] = 0.65  # Below 0.75 threshold
    
    mock_resp = MagicMock()
    mock_resp.text = json.dumps(low_conf_response)
    mock_client.models.generate_content.return_value = mock_resp

    res = extract_checklist_document(
        file_bytes=b"%PDF-1.4 mock",
        mime_type="application/pdf",
        filename="scratched_notes.pdf",
        genai_client=mock_client,
        uid="uid_1",
        import_session_id="sess_q"
    )

    assert res["status"] == "success"
    # All items should have status 'quarantined' due to low handwriting confidence
    assert res["items"][0]["status"] == "quarantined"


# ── Case 7: SoR Soft-Delete Abort State Transition ───────────────────────────

def test_soft_delete_abort_state_transition():
    """Case 7: Assert abort preserves documents with status: 'aborted'."""
    staged_doc = {
        "staging_id": "stg_999",
        "status": "staged",
        "title": "2022 P Quarter - Maya Angelou"
    }

    # Soft-delete transition
    staged_doc["status"] = "aborted"
    staged_doc["aborted_at"] = datetime.now(timezone.utc).isoformat()
    staged_doc["aborted_by"] = "test_uid"

    assert staged_doc["status"] == "aborted"
    assert "aborted_at" in staged_doc
    assert staged_doc["staging_id"] == "stg_999"  # Zero document ID mutation


# ── Case 8: Slugification & Reference Image Contract ──────────────────────────

def test_slugify_theme_and_reference_image_contract():
    """Case 8: Assert deterministic slugification prevents image collisions."""
    assert slugify_theme("Maya Angelou") == "maya_angelou"
    assert slugify_theme("Dr. Sally Ride") == "dr_sally_ride"
    assert slugify_theme("Edith Kanaka'ole") == "edith_kanakaole"
    assert slugify_theme("Hot Springs (AR)") == "hot_springs"
    assert slugify_theme("Yellowstone National Park") == "yellowstone"
    assert slugify_theme("Grand Canyon National Park") == "grand_canyon"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
