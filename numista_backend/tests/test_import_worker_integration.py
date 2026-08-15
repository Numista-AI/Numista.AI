"""
Numista.AI Ingestion Worker & Golden Fixture Integration Acceptance Test
Verifies byte-for-byte fidelity with us_women_quarters_15_aug_26_golden.json
"""

import os
import sys
import json
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.checklist_parser import extract_checklist_document, get_official_us_mint_title, normalize_storage_location


def test_golden_fixture_acceptance():
    """Assert checklist extraction reproduces the 15-coin golden fixture byte-for-byte."""
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "us_women_quarters_15_aug_26_golden.json")
    with open(fixture_path, "r", encoding="utf-8") as f:
        golden_data = json.load(f)

    assert len(golden_data) == 15

    # Build simulated Gemini extraction response from golden data
    llm_coins = []
    for idx, g in enumerate(golden_data):
        llm_coins.append({
            "year": g["year"],
            "mint_mark": g["mint_mark"],
            "theme_subject": g["theme_subject"],
            "denomination": "Quarter",
            "program_series": "American Women Quarters",
            "condition": "Unspecified / Raw",
            "storage_location": g["storage_location"],
            "page_number": 2,
            "row_index": idx + 1,
            "box_clarity_score": 0.98,
            "subject_ocr_score": 0.99,
            "header_validation_score": 1.0,
        })

    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.text = json.dumps({
        "program_series": "American Women Quarters",
        "denomination": "Quarter",
        "storage_location": "US Women Quarters Book",
        "snapshot_id": "SNAP-20260815-5472C902",
        "page_notes": "All Quarters Stored in the U.S. Women's Quarter Book",
        "handwriting_confidence": 0.95,
        "coins": llm_coins
    })
    mock_client.models.generate_content.return_value = mock_resp

    test_bytes = b"%PDF-1.4 test bytes"
    uid = "collector_uid_777"
    session_id = "sess_golden_acceptance"

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

    # Byte-for-byte field verification against golden fixture
    for idx, (extracted, golden) in enumerate(zip(items, golden_data)):
        assert extracted["year"] == golden["year"], f"Row {idx} year mismatch"
        assert extracted["mint_mark"] == golden["mint_mark"], f"Row {idx} mint_mark mismatch"
        assert extracted["theme_subject"] == golden["theme_subject"], f"Row {idx} theme_subject mismatch"
        assert extracted["official_us_mint_title"] == golden["official_us_mint_title"], f"Row {idx} official_us_mint_title mismatch"
        assert extracted["storage_location"] == golden["storage_location"], f"Row {idx} storage_location mismatch"
        assert extracted["source_type"] == golden["source_type"], f"Row {idx} source_type mismatch"
        assert extracted["status"] == "staged", f"Row {idx} should be staged"
        assert extracted["review_needed"] is False, f"Row {idx} should not need review"

    # Specific diacritic and multi-mint assertions
    zitkala = next(it for it in items if "Zitkala" in it["theme_subject"])
    assert zitkala["theme_subject"] == "Zitkala-Ša"
    assert "Š" in zitkala["theme_subject"]

    edith_records = [it for it in items if "Edith" in it["theme_subject"]]
    assert len(edith_records) == 2
    assert {it["mint_mark"] for it in edith_records} == {"P", "D"}

    patsy = next(it for it in items if "Patsy" in it["theme_subject"])
    assert patsy["theme_subject"] == "Patsy Mink"
    assert patsy["official_us_mint_title"] == "Patsy Takemoto Mink"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
