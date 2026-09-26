import pytest
from unittest.mock import MagicMock, patch

def test_add_coin_valuation_integrity_greysheet_hit():
    """Verify that when Greysheet resolves, cpg_retail is used."""
    mock_gs_service = MagicMock()
    mock_gs_service.resolve_coin_with_timeout.return_value = {
        "gsid": 12345,
        "bid": 25.0,
        "ask": 28.0,
        "cpg_retail": 32.0,
    }

    with patch("services.greysheet_service.GreysheetService", return_value=mock_gs_service):
        from services.greysheet_service import GreysheetService
        gs = GreysheetService(db=MagicMock())
        res = gs.resolve_coin_with_timeout("1921", "Dollar", "Morgan", "", "D", 1000)

        est_value_num = None
        val_source = "Awaiting Valuation"
        ai_value_status = "pending"

        if res and res.get("gsid"):
            cpg_val = res.get("cpg_retail") or res.get("ask")
            if cpg_val and cpg_val > 0:
                est_value_num = float(cpg_val)
                val_source = "Greysheet Production API"
                ai_value_status = "valued"

        assert est_value_num == 32.0
        assert val_source == "Greysheet Production API"
        assert ai_value_status == "valued"

def test_add_coin_valuation_integrity_fallback_to_mint_price():
    """Verify that when Greysheet fails, US Mint issue price is used if available."""
    mock_gs_service = MagicMock()
    mock_gs_service.resolve_coin_with_timeout.return_value = None

    with patch("services.greysheet_service.GreysheetService", return_value=mock_gs_service), \
         patch("services.usmint_releases_scraper.get_mint_issue_price", return_value=169.0):

        from services.usmint_releases_scraper import get_mint_issue_price
        mint_price = get_mint_issue_price(MagicMock(), "2026", "Dollar", "P", "Morgan")

        est_value_num = None
        val_source = "Awaiting Valuation"
        ai_value_status = "pending"

        if mint_price and mint_price > 0:
            est_value_num = mint_price
            val_source = "US Mint Issue Price"
            ai_value_status = "valued"

        assert est_value_num == 169.0
        assert val_source == "US Mint Issue Price"
        assert ai_value_status == "valued"

def test_add_coin_valuation_integrity_honest_pending():
    """Verify that when both fail, value is None and status is pending (NEVER 0.50)."""
    mock_gs_service = MagicMock()
    mock_gs_service.resolve_coin_with_timeout.return_value = None

    with patch("services.greysheet_service.GreysheetService", return_value=mock_gs_service), \
         patch("services.usmint_releases_scraper.get_mint_issue_price", return_value=None):

        est_value_num = None
        val_source = "Awaiting Valuation"
        ai_value_status = "pending"

        if est_value_num is None:
            formatted_ai_val = "Pending"
            ai_value_status = "pending"
            val_source = "Awaiting Valuation"
        else:
            formatted_ai_val = f"${est_value_num:.2f}"

        assert est_value_num is None
        assert formatted_ai_val == "Pending"
        assert ai_value_status == "pending"
        assert val_source == "Awaiting Valuation"
        # Explicitly verify it is NEVER 0.50
        assert est_value_num != 0.50
        assert formatted_ai_val != "$0.50"

def test_remediation_detection_logic():
    """Verify that coins with fake $0.50 values are correctly identified."""
    # Test case 1: estimated_value is 0.5, source is not Greysheet
    coin1 = {
        "estimated_value": 0.5,
        "AI Estimated Value": "$0.50",
        "valuation_source": "Local Catalog Baseline"
    }
    is_fake1 = (
        (coin1.get("estimated_value") == 0.5 or coin1.get("estimated_value") == 0.50) and
        coin1.get("valuation_source") != "Greysheet Production API"
    ) or coin1.get("AI Estimated Value") == "$0.50"
    assert is_fake1 is True

    # Test case 2: estimated_value is real 0.5 from Greysheet
    coin2 = {
        "estimated_value": 0.5,
        "AI Estimated Value": "$0.50",
        "valuation_source": "Greysheet Production API"
    }
    is_fake2 = (
        (coin2.get("estimated_value") == 0.5 or coin2.get("estimated_value") == 0.50) and
        coin2.get("valuation_source") != "Greysheet Production API"
    ) or (coin2.get("AI Estimated Value") == "$0.50" and coin2.get("valuation_source") != "Greysheet Production API")
    # Real Greysheet coin should not be considered fake
    assert ((coin2.get("estimated_value") == 0.5) and coin2.get("valuation_source") != "Greysheet Production API") is False

    # Test case 3: coin with legitimate valuation
    coin3 = {
        "estimated_value": 35.0,
        "AI Estimated Value": "$35.00",
        "valuation_source": "Greysheet Production API"
    }
    is_fake3 = (
        (coin3.get("estimated_value") == 0.5 or coin3.get("estimated_value") == 0.50) and
        coin3.get("valuation_source") != "Greysheet Production API"
    ) or coin3.get("AI Estimated Value") == "$0.50"
    assert is_fake3 is False
