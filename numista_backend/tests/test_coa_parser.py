import pytest
from scan_service.coa_parser_service import validate_mintage_ceiling

def test_validate_mintage_ceiling_valid():
    res = validate_mintage_ceiling("142988", "300,000")
    assert res["verdict"] == "VALID"
    assert res["is_authentic_range"] is True
    assert res["mintage_warning"] is None

def test_validate_mintage_ceiling_prefixed():
    res = validate_mintage_ceiling("A350,000", "300,000")
    assert res["verdict"] == "EXCEEDS"
    assert res["is_authentic_range"] is False
    assert "exceeds official mintage ceiling" in res["mintage_warning"]

def test_validate_mintage_ceiling_unable_to_verify():
    res = validate_mintage_ceiling("No Serial", "300,000")
    assert res["verdict"] == "UNABLE_TO_VERIFY"
    assert res["is_authentic_range"] is True
    assert res["mintage_warning"] is None

def test_validate_mintage_ceiling_none():
    res = validate_mintage_ceiling(None, None)
    assert res["verdict"] == "UNABLE_TO_VERIFY"
    assert res["is_authentic_range"] is True
    assert res["mintage_warning"] is None
