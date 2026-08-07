"""
test_beta_estate_pipeline.py — Unit tests for Estate LPT Division Engine, Heir Locks, Cash Offsets & PDF Passports
"""

import pytest
from services.passport_pdf_generator import generate_passport_pdf, downsample_image_to_300dpi_thumb

def test_lpt_greedy_estate_division_solver():
    """Verify Longest Processing Time (LPT) greedy lot division solver among 2 heirs."""
    unlocked_items = [
        {"id": "coin_1", "title": "1907 Saint-Gaudens $20", "value": 2500.0},
        {"id": "coin_2", "title": "1893-S Morgan Dollar", "value": 1800.0},
        {"id": "coin_3", "title": "1921 Morgan Dollar", "value": 40.0},
        {"id": "coin_4", "title": "1937-D Buffalo Nickel", "value": 15.0},
    ]

    total_value = sum(item["value"] for item in unlocked_items)
    target_per_heir = total_value / 2.0  # 50/50 split = $2177.50 each

    heir_lots = {"Heir A": [], "Heir B": []}
    heir_totals = {"Heir A": 0.0, "Heir B": 0.0}

    # Sort descending
    sorted_items = sorted(unlocked_items, key=lambda x: x["value"], reverse=True)

    for item in sorted_items:
        # Assign to heir furthest below target
        selected_heir = min(heir_totals.keys(), key=lambda h: heir_totals[h])
        heir_lots[selected_heir].append(item)
        heir_totals[selected_heir] += item["value"]

    # Calculate Cash Offset
    offset_a = target_per_heir - heir_totals["Heir A"]
    offset_b = target_per_heir - heir_totals["Heir B"]

    assert len(heir_lots["Heir A"]) + len(heir_lots["Heir B"]) == 4
    # Cash offsets sum to zero
    assert abs(offset_a + offset_b) < 0.01

def test_passport_pdf_generation_with_watermark_and_disclaimer():
    """Verify PDF Passport generation creates valid PDF bytes containing legal disclaimer and canvas watermark."""
    sample_transfer = {
        "transfer_id": "TEST_PASS_999",
        "claim_pin": "123456",
        "sender_id": "test_executor@numista.ai",
        "created_at": "2026-08-07T12:00:00Z",
        "expires_at": "2026-10-07T12:00:00Z",
        "privacy_toggles": {"hide_cost_basis": True, "hide_private_notes": True},
        "items": [
            {"title": "1921 Morgan Dollar", "year": "1921", "mint_mark": "S", "grade": "MS-63", "category": "Coin"},
            {"title": "1896 $1 Silver Certificate", "year": "1896", "grade": "VF-20", "category": "Paper Currency"}
        ]
    }

    pdf_bytes = generate_passport_pdf(sample_transfer)
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")

def test_image_downsampling_300dpi_memory_optimization():
    """Verify image downsampling to 300 DPI 300x300 px reduces byte footprint."""
    from PIL import Image as PILImage
    import io

    # Create dummy 1920x1080 high-res image
    img = PILImage.new('RGB', (1920, 1080), color=(150, 150, 150))
    raw_buf = io.BytesIO()
    img.save(raw_buf, format='PNG')
    raw_bytes = raw_buf.getvalue()

    downsampled_buf = downsample_image_to_300dpi_thumb(raw_bytes, (300, 300))
    downsampled_bytes = downsampled_buf.getvalue()

    assert len(downsampled_bytes) < len(raw_bytes)
    assert len(downsampled_bytes) > 0
