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

def test_screenshot_face_value_sum():
    from mint_nomenclature_service import parse_denomination_numeric, calculate_metal_weight

    c1 = parse_denomination_numeric("Dollar")                       # Peace Dollar -> $1.00
    c2 = parse_denomination_numeric("Quarter Dollar")               # Quarter -> $0.25
    c3 = parse_denomination_numeric("Dollar")                       # Silver Eagle -> $1.00
    c4 = parse_denomination_numeric("Five Dollars (Half Eagle)")    # Half Eagle -> $5.00

    assert c1 == 1.00
    assert c2 == 0.25
    assert c3 == 1.00
    assert c4 == 5.00

    total_fv = c1 + c2 + c3 + c4
    assert total_fv == 7.25

def test_metal_weight_inference():
    from mint_nomenclature_service import calculate_metal_weight

    m1 = calculate_metal_weight("", "Five Dollars (Half Eagle)", "Indian Head Gold", "Indian Head Half Eagle")
    assert m1['is_gold'] is True
    assert abs(m1['troy_oz_pure_metal'] - 0.24187) < 0.001

    m2 = calculate_metal_weight("", "Dollar", "American Silver Eagle", "")
    assert m2['is_silver'] is True
    assert m2['troy_oz_pure_metal'] == 1.000
