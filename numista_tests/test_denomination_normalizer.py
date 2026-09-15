import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "numista_backend")))

from services.denomination_normalizer import normalize_denomination, infer_denomination_from_program
from routes.import_routes import _normalize_us_denomination

def test_penny_to_cent():
    for raw in ["Penny", "penny", "One Cent", "1 Cent", "1c", "1¢", "wheatie", "lincoln cent"]:
        canon, corr, orig = normalize_denomination(raw)
        assert canon == "Cent"
        assert orig == raw

def test_nickel_to_five_cents():
    for raw in ["Nickel", "nickel", "nickels", "5 Cents", "5c", "5¢", "five cents", "five cent", "jefferson nickel"]:
        canon, corr, orig = normalize_denomination(raw)
        assert canon == "Five Cents"
        assert orig == raw

def test_quarter_to_quarter_dollar():
    for raw in ["Quarter", "quarter", "quarters", "25c", "25¢", "25 cents", "washington quarter"]:
        canon, corr, orig = normalize_denomination(raw)
        assert canon == "Quarter Dollar"
        assert orig == raw

def test_suffix_and_doubled_word_cleanup():
    canon, corr, _ = normalize_denomination("Quarter Dollar (25C)")
    assert canon == "Quarter Dollar"
    assert corr is True

    canon, corr, _ = normalize_denomination("Quarter Dollar Dollar")
    assert canon == "Quarter Dollar"
    assert corr is True

    canon, corr, _ = normalize_denomination("Dollar Dollar")
    assert canon == "Dollar"
    assert corr is True

def test_banknote_guard():
    # Banknote item_type guard
    canon, corr, _ = normalize_denomination("$1", item_type="paper_currency")
    assert canon == "$1"
    assert corr is False

    canon, corr, _ = normalize_denomination("$5")
    assert canon == "$5"
    assert corr is False

    canon, corr, _ = normalize_denomination("$20")
    assert canon == "$20"
    assert corr is False

    canon, corr, _ = normalize_denomination("$100")
    assert canon == "$100"
    assert corr is False

def test_foreign_coin_passthrough():
    for raw in ["50 Fils", "100 Francs", "10 Euro Cent", "5 Colones", "20 Euro Cent"]:
        canon, corr, _ = normalize_denomination(raw)
        assert canon == raw
        assert corr is False

    # Foreign country flag suppresses US mapping
    canon, corr, _ = normalize_denomination("Penny", country="United Kingdom")
    assert canon == "Penny"
    assert corr is False

def test_program_inference():
    assert infer_denomination_from_program("50 State Quarters") == "Quarter Dollar"
    assert infer_denomination_from_program("America the Beautiful") == "Quarter Dollar"
    assert infer_denomination_from_program("Morgan Dollar") == "Dollar"
    assert infer_denomination_from_program("Lincoln Cent") == "Cent"
    assert infer_denomination_from_program("Jefferson Nickel") == "Five Cents"
    assert infer_denomination_from_program("Kennedy Half Dollar") == "Half Dollar"
    assert infer_denomination_from_program("Unknown Program") is None

def test_e2e_wrapper_backward_compat():
    assert _normalize_us_denomination("Penny") == "Cent"
    assert _normalize_us_denomination("Wheatie") == "Cent"
    assert _normalize_us_denomination("Nickel") == "Five Cents"
    assert _normalize_us_denomination("Quarter") == "Quarter Dollar"
    assert _normalize_us_denomination("Half Dollar") == "Half Dollar"
    assert _normalize_us_denomination("Dollar Coin") == "Dollar"
    assert _normalize_us_denomination("5 Francs") == "5 Francs"
