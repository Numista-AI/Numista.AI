"""
Extended unit tests for set_pricing.py

Covers the resolution logic NOT tested by the existing test_set_pricing.py fixture tests:
  - resolve_set_sku(): is_set detection, year resolution, product type branching,
    metal inference, SKU key construction, unvaluable error paths
  - get_set_valuation(): full pipeline including uncataloged SKU paths
  - load_set_catalog(): structure and version validation
  - Catalog JSON schema: all entries have required fields and valid value ranges

Run with:
  pytest numista_backend/tests/test_set_pricing_extended.py -v
"""

import json
import pytest
from pathlib import Path

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import set_pricing
from set_pricing import resolve_set_sku, get_set_valuation, load_set_catalog


# ── Helpers ───────────────────────────────────────────────────────────────────

def _set_doc(**kwargs):
    """Build a minimal set document with safe defaults."""
    return {
        "name": kwargs.get("name", "2002 Proof Set"),
        "item_type": kwargs.get("item_type", "set"),
        "Year": kwargs.get("year", "2002"),
        "Metal Content": kwargs.get("metal", "clad"),
        **{k: v for k, v in kwargs.items() if k not in ("name", "item_type", "year", "metal")}
    }


# ── resolve_set_sku: is_set detection ─────────────────────────────────────────

class TestIsSetDetection:
    def test_item_type_set_is_recognized(self):
        doc = _set_doc(item_type="set")
        sku, err = resolve_set_sku(doc)
        assert err is None or err.get("reason") != "not_a_set"

    def test_denomination_set_is_recognized(self):
        doc = {"name": "Proof Collection", "Denomination": "Set", "Year": "2002", "Metal Content": "clad"}
        sku, err = resolve_set_sku(doc)
        assert err is None or err.get("reason") != "not_a_set"

    def test_name_containing_set_is_recognized(self):
        doc = {"name": "2002 Silver Proof Set", "Year": "2002", "Metal Content": "silver"}
        sku, err = resolve_set_sku(doc)
        assert err is None or err.get("reason") != "not_a_set"

    def test_plain_coin_doc_is_not_a_set(self):
        doc = {"name": "1921 Morgan Dollar", "Year": "1921", "Metal Content": "silver",
               "Denomination": "Dollar", "item_type": "coin"}
        sku, err = resolve_set_sku(doc)
        assert sku is None
        assert err is not None
        assert err.get("reason") == "not_a_set"

    def test_program_containing_set_is_recognized(self):
        doc = {"name": "Annual Collection", "Program/Series": "Mint Set", "Year": "2002",
               "Metal Content": "clad"}
        sku, err = resolve_set_sku(doc)
        assert err is None or err.get("reason") != "not_a_set"


# ── resolve_set_sku: year resolution ──────────────────────────────────────────

class TestYearResolution:
    def test_year_from_year_field(self):
        sku, err = resolve_set_sku(_set_doc(year="2002"))
        assert err is None
        assert sku.startswith("2002_")

    def test_year_from_name_fallback(self):
        doc = {"name": "1999 Proof Set", "item_type": "set", "Metal Content": "clad"}
        sku, err = resolve_set_sku(doc)
        assert err is None
        assert sku.startswith("1999_")

    def test_year_from_program_fallback(self):
        doc = {"name": "Annual Collection", "Program/Series": "2004 Mint Set", "item_type": "set",
               "Metal Content": "clad"}
        sku, err = resolve_set_sku(doc)
        assert err is None
        assert sku.startswith("2004_")

    def test_year_only_first_4_chars_used(self):
        sku, err = resolve_set_sku(_set_doc(year="2002-01-01"))
        assert err is None
        assert sku.startswith("2002_")

    def test_no_year_returns_unvaluable(self):
        doc = {"name": "Proof Set", "item_type": "set", "Metal Content": "clad"}
        sku, err = resolve_set_sku(doc)
        assert sku is None
        assert err["status"] == "unvaluable"
        assert err["basis"] == "set_year_unspecified"

    def test_invalid_year_string_returns_unvaluable(self):
        # Name must NOT contain a year digit sequence so the name-fallback also fails
        doc = {"name": "Annual Proof Set", "item_type": "set", "Year": "unknown",
               "Metal Content": "clad"}
        sku, err = resolve_set_sku(doc)
        assert sku is None
        assert err is not None


# ── resolve_set_sku: product type detection ───────────────────────────────────

class TestProductTypeDetection:
    def test_quarter_proof_set_detected(self):
        doc = _set_doc(name="2002 50 State Quarters Proof Set")
        sku, err = resolve_set_sku(doc)
        assert err is None
        assert "quarter_proof_set" in sku
        assert "_5" in sku  # 5-coin quarter proof set

    def test_proof_set_detected(self):
        doc = _set_doc(name="2002 Proof Set")
        sku, err = resolve_set_sku(doc)
        assert err is None
        assert "proof_set" in sku
        assert "_10" in sku  # 10-coin standard proof

    def test_mint_set_detected(self):
        doc = _set_doc(name="2002 Mint Set Uncirculated")
        sku, err = resolve_set_sku(doc)
        assert err is None
        assert "mint_set" in sku
        assert "_20" in sku  # 20-coin P&D mint set

    def test_uncirculated_keyword_detected(self):
        doc = _set_doc(name="2002 Uncirculated Collection")
        sku, err = resolve_set_sku(doc)
        assert err is None
        assert "mint_set" in sku

    def test_ambiguous_set_defaults_to_proof(self):
        doc = _set_doc(name="2002 Annual Set", item_type="set")
        sku, err = resolve_set_sku(doc)
        assert err is None
        assert "proof_set" in sku  # fallback to proof_set


# ── resolve_set_sku: metal resolution ─────────────────────────────────────────

class TestMetalResolution:
    def test_silver_from_metal_content_field(self):
        doc = _set_doc(metal="silver")
        sku, err = resolve_set_sku(doc)
        assert err is None
        assert "_silver_" in sku

    def test_silver_from_name(self):
        doc = _set_doc(name="2002 Silver Proof Set", metal="")
        sku, err = resolve_set_sku(doc)
        assert err is None
        assert "_silver_" in sku

    def test_clad_from_cupronickel(self):
        doc = _set_doc(metal="cupronickel")
        sku, err = resolve_set_sku(doc)
        assert err is None
        assert "_clad_" in sku

    def test_clad_from_copper_nickel(self):
        doc = _set_doc(metal="copper-nickel")
        sku, err = resolve_set_sku(doc)
        assert err is None
        assert "_clad_" in sku

    def test_clad_keyword_in_name(self):
        doc = _set_doc(name="2002 Clad Proof Set", metal="")
        sku, err = resolve_set_sku(doc)
        assert err is None
        assert "_clad_" in sku

    def test_no_metal_returns_unvaluable(self):
        doc = {"name": "2002 Proof Set", "item_type": "set", "Year": "2002"}
        sku, err = resolve_set_sku(doc)
        assert sku is None
        assert err["status"] == "unvaluable"
        assert err["basis"] == "set_metal_unspecified"

    def test_unknown_metal_returns_unvaluable(self):
        doc = _set_doc(metal="unobtanium")
        sku, err = resolve_set_sku(doc)
        assert sku is None
        assert err["status"] == "unvaluable"
        assert err["basis"] == "set_metal_unrecognized"


# ── resolve_set_sku: SKU key construction ─────────────────────────────────────

class TestSkuKeyConstruction:
    def test_sku_key_format(self):
        doc = _set_doc(name="2002 Proof Set", year="2002", metal="clad")
        sku, err = resolve_set_sku(doc)
        assert err is None
        # Format: {year}_{product_type}_{metal}_{coin_count}
        parts = sku.split("_")
        assert parts[0] == "2002"
        assert parts[-1].isdigit()

    def test_clad_proof_set_sku(self):
        doc = _set_doc(name="2002 Proof Set", year="2002", metal="clad")
        sku, err = resolve_set_sku(doc)
        assert sku == "2002_proof_set_clad_10"

    def test_silver_proof_set_sku(self):
        doc = _set_doc(name="2002 Silver Proof Set", year="2002", metal="silver")
        sku, err = resolve_set_sku(doc)
        assert sku == "2002_proof_set_silver_10"


# ── get_set_valuation: full pipeline ──────────────────────────────────────────

class TestGetSetValuation:
    def test_cataloged_set_returns_valued_status(self):
        doc = _set_doc(name="2002 Proof Set", year="2002", metal="clad")
        result = get_set_valuation(doc)
        assert result["status"] == "valued"
        assert result["ai_value_status"] == "valued"

    def test_cataloged_set_has_price_fields(self):
        doc = _set_doc(name="2002 Proof Set", year="2002", metal="clad")
        result = get_set_valuation(doc)
        assert "estimated_value" in result
        assert "numeric_median" in result
        assert "low" in result
        assert "high" in result
        assert result["low"] <= result["numeric_median"] <= result["high"]

    def test_cataloged_set_has_basis(self):
        doc = _set_doc(name="2002 Proof Set", year="2002", metal="clad")
        result = get_set_valuation(doc)
        assert "basis" in result
        assert result["basis"]  # non-empty

    def test_cataloged_set_has_confidence(self):
        doc = _set_doc(name="2002 Proof Set", year="2002", metal="clad")
        result = get_set_valuation(doc)
        assert result["confidence"] in ("HIGH", "MEDIUM", "LOW")

    def test_uncataloged_set_returns_unvaluable(self):
        doc = _set_doc(name="1875 Proof Set", year="1875", metal="silver")
        result = get_set_valuation(doc)
        assert result["status"] == "unvaluable"
        assert "1875" in result["basis"]

    def test_not_a_set_returns_skipped(self):
        doc = {"name": "1921 Morgan Dollar", "item_type": "coin", "Year": "1921"}
        result = get_set_valuation(doc)
        assert result["status"] == "skipped"

    def test_silver_proof_set_higher_value_than_clad(self):
        clad_doc = _set_doc(name="2002 Proof Set", year="2002", metal="clad")
        silver_doc = _set_doc(name="2002 Silver Proof Set", year="2002", metal="silver")
        clad_result = get_set_valuation(clad_doc)
        silver_result = get_set_valuation(silver_doc)
        if clad_result["status"] == "valued" and silver_result["status"] == "valued":
            assert silver_result["numeric_median"] > clad_result["numeric_median"]


# ── Catalog JSON schema validation ────────────────────────────────────────────

class TestCatalogSchema:
    REQUIRED_FIELDS = {"year", "product_type", "metal", "coin_count", "low", "high",
                       "median", "display_range", "confidence", "basis", "as_of"}
    VALID_PRODUCT_TYPES = {"proof_set", "quarter_proof_set", "mint_set"}
    VALID_METALS = {"clad", "silver", "gold"}
    VALID_CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}

    def test_catalog_loads_successfully(self):
        catalog = load_set_catalog()
        assert isinstance(catalog, dict)
        assert len(catalog) > 0

    def test_catalog_has_2002_clad_proof(self):
        catalog = load_set_catalog()
        assert "2002_proof_set_clad_10" in catalog

    def test_all_entries_have_required_fields(self):
        catalog = load_set_catalog()
        for sku, data in catalog.items():
            missing = self.REQUIRED_FIELDS - set(data.keys())
            assert not missing, f"SKU '{sku}' missing fields: {missing}"

    def test_all_prices_are_positive(self):
        catalog = load_set_catalog()
        for sku, data in catalog.items():
            assert data["low"] > 0, f"SKU '{sku}': low price must be > 0"
            assert data["high"] > 0, f"SKU '{sku}': high price must be > 0"
            assert data["median"] > 0, f"SKU '{sku}': median must be > 0"

    def test_low_lte_median_lte_high_for_all(self):
        catalog = load_set_catalog()
        for sku, data in catalog.items():
            assert data["low"] <= data["median"], f"SKU '{sku}': low > median"
            assert data["median"] <= data["high"], f"SKU '{sku}': median > high"

    def test_all_confidence_values_are_valid(self):
        catalog = load_set_catalog()
        for sku, data in catalog.items():
            assert data["confidence"] in self.VALID_CONFIDENCE, (
                f"SKU '{sku}': confidence '{data['confidence']}' not in {self.VALID_CONFIDENCE}"
            )

    def test_display_range_contains_dollar_sign(self):
        catalog = load_set_catalog()
        for sku, data in catalog.items():
            assert "$" in data["display_range"], (
                f"SKU '{sku}': display_range '{data['display_range']}' missing '$'"
            )

    def test_sku_key_matches_year_in_data(self):
        catalog = load_set_catalog()
        for sku, data in catalog.items():
            year_from_key = int(sku.split("_")[0])
            assert year_from_key == data["year"], (
                f"SKU '{sku}': key year {year_from_key} != data year {data['year']}"
            )
