import pytest
from main import clean_valuation_value

def test_valuation_ranges():
    # Ranges
    assert clean_valuation_value("$15-$20") == 15.0
    assert clean_valuation_value("$150 - $350") == 150.0

def test_valuation_single_value_with_commas():
    # Single value with currency symbols and thousands separators
    assert clean_valuation_value("$1,250.00") == 1250.0

def test_valuation_simple_number():
    # Standalone simple numeric string
    assert clean_valuation_value("15") == 15.0

def test_valuation_invalid_gibberish():
    # Gibberish/invalid text fallbacks to 0.0
    assert clean_valuation_value("Gibberish text") == 0.0
    assert clean_valuation_value(None) == 0.0
    assert clean_valuation_value("Pending") == 0.0
    assert clean_valuation_value("None") == 0.0
