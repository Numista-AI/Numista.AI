"""
Unit tests for Generate-and-Select Verifier Services:
- Catalog Sanity-Check Verifier (catalog_verifier.py)
- OCR Balance & Structural Verifier (ocr_balance_verifier.py)
- Image Intake & Scraping Verifier (image_intake_verifier.py)
"""

import pytest
import struct
from services.catalog_verifier import (
    verify_coin_identification,
    parse_sheldon_grade
)
from services.ocr_balance_verifier import (
    verify_invoice_extraction,
    parse_currency
)
from services.image_intake_verifier import (
    verify_image_candidate,
    get_image_dimensions
)


# ==============================================================================
# 1. CATALOG VERIFIER TESTS (Technique 3)
# ==============================================================================

def test_catalog_verifier_valid_morgan_dollar():
    candidate = {
        "year": 1881,
        "program_series": "Morgan Dollar",
        "mint_mark": "S",
        "grade": "MS-64",
        "metal_content": "90% Silver, 10% Copper"
    }
    result = verify_coin_identification(candidate)
    assert result["is_valid"] is True
    assert len(result["errors"]) == 0


def test_catalog_verifier_catches_impossible_1921_o_morgan():
    # 1921 Morgan dollars were ONLY minted in Philadelphia, Denver, and San Francisco (NO New Orleans 'O')
    candidate = {
        "year": 1921,
        "program_series": "Morgan Dollar",
        "mint_mark": "O",
        "grade": "MS-63"
    }
    result = verify_coin_identification(candidate)
    assert result["is_valid"] is False
    assert any("Invalid mint mark 'O' for 1921 Morgan Dollar" in err for err in result["errors"])


def test_catalog_verifier_catches_invalid_sheldon_grade():
    # 59 is not a valid Sheldon grade number (standard skips from 58 to 60)
    candidate = {
        "year": 1943,
        "program_series": "Walking Liberty Half Dollar",
        "mint_mark": "D",
        "grade": "AU-59"
    }
    result = verify_coin_identification(candidate)
    assert result["is_valid"] is False
    assert any("Invalid Sheldon grade number '59'" in err for err in result["errors"])


def test_catalog_verifier_catches_pre_1965_clad_hallucination():
    # 1942 Washington Quarter cannot be clad copper-nickel
    candidate = {
        "year": 1942,
        "program_series": "Washington Quarter",
        "mint_mark": "P",
        "grade": "XF-40",
        "metal_content": "Copper-Nickel Clad"
    }
    result = verify_coin_identification(candidate)
    assert result["is_valid"] is False
    assert any("90% Silver, not Copper-Nickel" in err for err in result["errors"])


def test_parse_sheldon_grade_helper():
    assert parse_sheldon_grade("MS-65") == 65
    assert parse_sheldon_grade("AU58") == 58
    assert parse_sheldon_grade("Poor 1") == 1
    assert parse_sheldon_grade("PR-70DCAM") == 70
    assert parse_sheldon_grade("Ungraded") is None


# ==============================================================================
# 2. OCR BALANCE VERIFIER TESTS (Technique 4)
# ==============================================================================

def test_ocr_balance_verifier_balanced_receipt():
    extraction = {
        "grand_total": "125.00",
        "subtotal": "115.00",
        "tax": "5.00",
        "shipping": "5.00",
        "items": [
            {"description": "1921 Morgan Dollar MS63", "price": 45.00, "quantity": 1},
            {"description": "1943 Walking Liberty Half AU55", "price": 35.00, "quantity": 2}
        ]
    }
    result = verify_invoice_extraction(extraction)
    assert result["is_valid"] if "is_valid" in result else result["is_balanced"] is True
    assert len(result["errors"]) == 0
    assert result["feedback_prompt"] is None


def test_ocr_balance_verifier_catches_line_sum_mismatch():
    extraction = {
        "grand_total": "150.00",
        "subtotal": "150.00",
        "items": [
            {"description": "1889 Morgan Dollar MS64", "price": 85.00, "quantity": 1},
            # Missing 2nd item that accounted for remaining $65.00
        ]
    }
    result = verify_invoice_extraction(extraction)
    assert result["is_balanced"] is False
    assert len(result["errors"]) > 0
    assert result["feedback_prompt"] is not None
    assert "RECONCILIATION ERROR" in result["feedback_prompt"]
    assert "85.00" in result["feedback_prompt"]


def test_parse_currency_helper():
    assert parse_currency("$1,245.50") == 1245.50
    assert parse_currency("45.00") == 45.00
    assert parse_currency(None) == 0.0
    assert parse_currency("") == 0.0


# ==============================================================================
# 3. IMAGE INTAKE VERIFIER TESTS (Technique 5)
# ==============================================================================

def _make_mock_png(width: int, height: int) -> bytes:
    """Constructs minimal valid PNG header with width and height for testing."""
    signature = b'\x89PNG\r\n\x1a\n'
    # IHDR chunk: 13 bytes (length 13, type IHDR, width 4B, height 4B, bit depth 1B, color 1B, comp 1B, filt 1B, interlace 1B)
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr_chunk = struct.pack('>I', 13) + b'IHDR' + ihdr_data + b'\x00\x00\x00\x00'
    return signature + ihdr_chunk + b'\x00' * 50


def test_image_intake_verifier_valid_square_coin():
    mock_bytes = _make_mock_png(600, 600)
    result = verify_image_candidate(mock_bytes, metadata={"url": "https://upload.wikimedia.org/coin.png"})
    assert result["is_valid"] is True
    assert result["width"] == 600
    assert result["height"] == 600
    assert result["aspect_ratio"] == 1.0


def test_image_intake_verifier_catches_distorted_banner():
    # 1200x200 banner image is not a coin
    mock_bytes = _make_mock_png(1200, 200)
    result = verify_image_candidate(mock_bytes)
    assert result["is_valid"] is False
    assert any("Distorted aspect ratio" in err for err in result["errors"])


def test_image_intake_verifier_catches_low_res():
    # 150x150 is below 300x300 threshold
    mock_bytes = _make_mock_png(150, 150)
    result = verify_image_candidate(mock_bytes)
    assert result["is_valid"] is False
    assert any("Low resolution image" in err for err in result["errors"])


def test_image_intake_verifier_catches_empty_stream():
    result = verify_image_candidate(b'')
    assert result["is_valid"] is False
    assert "Image byte stream is empty" in result["errors"][0]
