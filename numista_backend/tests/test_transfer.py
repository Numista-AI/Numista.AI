"""
Unit tests for Transfer Service, Passport PDF Generator, and Feature Registry.
"""

import pytest
from unittest.mock import MagicMock
from services.transfer_service import sanitize_item_payload, initiate_transfer, claim_transfer, recall_transfer
from services.passport_pdf_generator import generate_passport_pdf, format_financial_details
from services.feature_registry import registry, register_feature, FeatureDescriptor


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
    assert len(pdf_bytes) > 500  # Ensure non-trivial PDF content was built
    assert pdf_bytes.startswith(b"%PDF")


def test_pdf_notes_filtering():
    # Long generic catalog essay should be omitted from PDF notes
    essay_item = {
        "personalNotes": "This coin is the 1999 New Jersey state quarter, representing the third state admitted to the Union. Struck at the Denver Mint...",
        "storageLocation": "Binder 1"
    }
    fin_essay = format_financial_details(essay_item)
    assert "This coin is the 1999 New Jersey" not in fin_essay
    assert "Vault:</b> Binder 1" in fin_essay

    # Short user note should be rendered
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
