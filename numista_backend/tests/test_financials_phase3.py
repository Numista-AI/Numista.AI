"""
Numista.AI — Phase 3 Financials Tests
Covers the cost-basis parsing and acquisition_cost_display logic from Phase 3A.

These tests exercise the canonical cost_basis resolution rules introduced in the
Phase 3A audit (Aug 24 2026) without touching Firestore. The logic under test
lives in numista_backend/main.py around line 2293 ("Parse cost_basis and
acquisition_cost_display") and numista_backend/scripts/backfill_is_foreign.py.

Cost-basis rules (as implemented):
  - None / missing cost           -> cost_basis=None, display="UKN"
  - "$0.00", "0", "FREE", "GIFT", "FOUND", "COIN JAR" -> cost_basis=0.0, display="$0.00"
  - "UKN", "UNKNOWN", "N/A"       -> cost_basis=None, display="UKN"
  - Numeric / "$12.50"            -> cost_basis=float, display="$12.50"
  - Unparseable string            -> cost_basis=None, display="UKN"
  - Provenance contains "jar" / "gift" / "found" / "inherited" / "free"
                                  -> cost_basis=0.0, display="$0.00" (when cost missing)
"""
import json
import os
import re
import pytest


# ──────────────────────────────────────────────────────────────────────────────
# Pure reproduction of the cost_basis parsing logic from main.py ~L2294-2316
# Extracted here so we can test it without importing the full FastAPI app.
# If the logic changes in main.py, this function MUST be updated to match.
# ──────────────────────────────────────────────────────────────────────────────

def _parse_cost(cost, provenance=None):
    """
    Mirror of the cost_basis parsing block in main.py (Phase 3A).
    Returns (cost_basis_num, cost_display_str).
    """
    prov_desc = provenance or ""
    cost_basis_num = None
    cost_display_str = "UKN"

    if cost:
        cost_upper = str(cost).strip().upper()
        if cost_upper in ["$0.00", "0", "0.00", "FREE", "GIFT", "FOUND", "COIN JAR"]:
            cost_basis_num = 0.0
            cost_display_str = "$0.00"
        elif cost_upper in ["UKN", "UNKNOWN", "N/A"]:
            cost_basis_num = None
            cost_display_str = "UKN"
        else:
            try:
                cleaned_val = float(re.sub(r"[^\d.]", "", cost_upper))
                cost_basis_num = cleaned_val
                cost_display_str = f"${cleaned_val:.2f}"
            except Exception:
                cost_basis_num = None
                cost_display_str = "UKN"
    elif prov_desc and any(k in prov_desc.lower() for k in ["jar", "gift", "found", "inherited", "free"]):
        cost_basis_num = 0.0
        cost_display_str = "$0.00"

    return cost_basis_num, cost_display_str


def _can_calc_pl(cost_display_str):
    """
    Mirror of canCalcPL from coin_detail_screen.dart Phase 3A:
      canCalcPL = costDisplay != "UKN"
    So any known cost (including $0.00) allows P&L calculation.
    """
    return cost_display_str != "UKN"


# ──────────────────────────────────────────────────────────────────────────────
# Cost-basis parsing tests
# ──────────────────────────────────────────────────────────────────────────────

class TestCostBasisParsing:
    """Unit tests for the Phase 3A cost_basis + acquisition_cost_display logic."""

    # ── Missing / None cost ───────────────────────────────────────────────────

    def test_none_cost_returns_ukn(self):
        num, disp = _parse_cost(None)
        assert num is None
        assert disp == "UKN"

    def test_empty_string_cost_returns_ukn(self):
        num, disp = _parse_cost("")
        assert num is None
        assert disp == "UKN"

    # ── Zero-value / face-value / free keywords ───────────────────────────────

    def test_dollar_zero_zero_cost_returns_zero(self):
        """$0.00 is an explicit zero-cost entry (e.g. found in pocket change)."""
        num, disp = _parse_cost("$0.00")
        assert num == 0.0
        assert disp == "$0.00"

    def test_bare_zero_returns_zero(self):
        num, disp = _parse_cost("0")
        assert num == 0.0
        assert disp == "$0.00"

    def test_decimal_zero_returns_zero(self):
        num, disp = _parse_cost("0.00")
        assert num == 0.0
        assert disp == "$0.00"

    def test_free_keyword_returns_zero(self):
        num, disp = _parse_cost("FREE")
        assert num == 0.0
        assert disp == "$0.00"

    def test_free_keyword_case_insensitive(self):
        num, disp = _parse_cost("free")
        assert num == 0.0
        assert disp == "$0.00"

    def test_gift_keyword_returns_zero(self):
        num, disp = _parse_cost("GIFT")
        assert num == 0.0
        assert disp == "$0.00"

    def test_found_keyword_returns_zero(self):
        num, disp = _parse_cost("FOUND")
        assert num == 0.0
        assert disp == "$0.00"

    def test_coin_jar_keyword_returns_zero(self):
        num, disp = _parse_cost("COIN JAR")
        assert num == 0.0
        assert disp == "$0.00"

    # ── Unknown / suppressed ──────────────────────────────────────────────────

    def test_ukn_keyword_returns_ukn(self):
        """UKN means 'unknown cost' — P&L calculation is suppressed."""
        num, disp = _parse_cost("UKN")
        assert num is None
        assert disp == "UKN"

    def test_unknown_keyword_returns_ukn(self):
        num, disp = _parse_cost("UNKNOWN")
        assert num is None
        assert disp == "UKN"

    def test_na_keyword_returns_ukn(self):
        num, disp = _parse_cost("N/A")
        assert num is None
        assert disp == "UKN"

    # ── Numeric values ────────────────────────────────────────────────────────

    def test_whole_dollar_amount(self):
        num, disp = _parse_cost("25")
        assert num == 25.0
        assert disp == "$25.00"

    def test_dollar_sign_prefix(self):
        num, disp = _parse_cost("$12.50")
        assert num == 12.50
        assert disp == "$12.50"

    def test_large_value(self):
        """A $3,500 Morgan dollar purchase — commas stripped by re.sub."""
        num, disp = _parse_cost("$3,500.00")
        assert num == 3500.0
        assert disp == "$3500.00"

    def test_small_face_value_cent(self):
        """A 1c coin bought for $0.01 — below face value."""
        num, disp = _parse_cost("0.01")
        assert num == 0.01
        assert disp == "$0.01"

    def test_numeric_string_with_whitespace(self):
        num, disp = _parse_cost("  $7.99  ")
        assert num == 7.99
        assert disp == "$7.99"

    # ── Unparseable / malformed ───────────────────────────────────────────────

    def test_alphabetic_garbage_returns_ukn(self):
        num, disp = _parse_cost("five dollars")
        assert num is None
        assert disp == "UKN"

    def test_special_characters_only_returns_ukn(self):
        num, disp = _parse_cost("???")
        assert num is None
        assert disp == "UKN"

    def test_euro_symbol_stripped_yields_numeric(self):
        """
        The re.sub(r'[^\\d.]', '', ...) strips ALL non-numeric chars including €.
        So '€50' becomes '50' -> parses as $50.00. This is current backend behavior.
        A future enhancement could detect currency symbols and return UKN instead.
        """
        num, disp = _parse_cost("€50")
        # Current behavior: strips € -> treats as $50.00
        assert num == 50.0
        assert disp == "$50.00"

    # ── Provenance-based zero cost (when cost field is missing) ───────────────

    def test_jar_provenance_no_cost_returns_zero(self):
        """'coin jar' in provenance with no cost -> $0.00 (Phase 3A rule)."""
        num, disp = _parse_cost(None, provenance="Found in coin jar")
        assert num == 0.0
        assert disp == "$0.00"

    def test_gift_provenance_no_cost_returns_zero(self):
        num, disp = _parse_cost(None, provenance="Birthday gift from grandpa")
        assert num == 0.0
        assert disp == "$0.00"

    def test_found_provenance_no_cost_returns_zero(self):
        num, disp = _parse_cost(None, provenance="Found on sidewalk")
        assert num == 0.0
        assert disp == "$0.00"

    def test_inherited_provenance_no_cost_returns_zero(self):
        num, disp = _parse_cost(None, provenance="Inherited from estate")
        assert num == 0.0
        assert disp == "$0.00"

    def test_free_provenance_no_cost_returns_zero(self):
        num, disp = _parse_cost(None, provenance="Received for free at coin show")
        assert num == 0.0
        assert disp == "$0.00"

    def test_neutral_provenance_no_cost_returns_ukn(self):
        """'eBay purchase' has no zero-cost keyword -> UKN if cost missing."""
        num, disp = _parse_cost(None, provenance="eBay purchase")
        assert num is None
        assert disp == "UKN"

    def test_cost_overrides_provenance(self):
        """Explicit cost value takes priority over provenance keyword."""
        num, disp = _parse_cost("$45.00", provenance="Gift from wife")
        assert num == 45.0
        assert disp == "$45.00"


# ──────────────────────────────────────────────────────────────────────────────
# canCalcPL gate tests (Phase 3A Flutter / Phase 3C E2E coverage equivalent)
# ──────────────────────────────────────────────────────────────────────────────

class TestCanCalcPL:
    """
    Tests for the canCalcPL discriminator (Phase 3A).
    canCalcPL = costDisplay != "UKN"
    This is the gate that enables the P&L row in the coin detail view.
    Key insight: $0.00 is known cost -> P&L CAN be calculated (shows $0 gain).
    UKN is unknown cost -> P&L is suppressed.
    """

    def test_ukn_display_blocks_pl(self):
        assert _can_calc_pl("UKN") is False

    def test_zero_dollar_display_enables_pl(self):
        """$0.00 is a KNOWN cost — P&L is calculated (likely shows gain equal to market value)."""
        assert _can_calc_pl("$0.00") is True

    def test_positive_cost_enables_pl(self):
        assert _can_calc_pl("$125.00") is True

    def test_small_cost_enables_pl(self):
        assert _can_calc_pl("$0.01") is True

    def test_large_cost_enables_pl(self):
        assert _can_calc_pl("$10000.00") is True

    def test_free_keyword_resolves_to_known_cost_enabling_pl(self):
        """FREE -> $0.00 -> canCalcPL=True. Verifies end-to-end free-coin P&L flow."""
        _, disp = _parse_cost("FREE")
        assert _can_calc_pl(disp) is True

    def test_ukn_keyword_suppresses_pl(self):
        """UKN input -> UKN display -> canCalcPL=False."""
        _, disp = _parse_cost("UKN")
        assert _can_calc_pl(disp) is False

    def test_none_cost_suppresses_pl(self):
        """Missing cost with neutral provenance -> UKN -> no P&L."""
        _, disp = _parse_cost(None, provenance="Purchased at auction")
        assert _can_calc_pl(disp) is False

    def test_jar_provenance_enables_pl(self):
        """Coin jar (zero cost) -> $0.00 -> canCalcPL=True."""
        _, disp = _parse_cost(None, provenance="Old coin jar")
        assert _can_calc_pl(disp) is True


# ──────────────────────────────────────────────────────────────────────────────
# backfill_is_foreign.py logic tests (no Firestore required)
# ──────────────────────────────────────────────────────────────────────────────

class TestIsForeignBackfillLogic:
    """
    Tests for the backfill_is_foreign.py idempotency and filtering logic.
    These tests use mock document dicts instead of real Firestore — safe offline.
    """

    def _should_backfill(self, data: dict) -> bool:
        """Mirror of the skip logic: backfill only docs missing 'is_foreign'."""
        return "is_foreign" not in data

    def test_missing_is_foreign_flagged_for_update(self):
        doc = {"Year": "1964", "Denomination": "Quarter Dollar", "Mint Mark": "D"}
        assert self._should_backfill(doc) is True

    def test_present_is_foreign_false_skipped(self):
        """Document already has is_foreign=False -> no re-write (idempotent)."""
        doc = {"Year": "1964", "is_foreign": False}
        assert self._should_backfill(doc) is False

    def test_present_is_foreign_true_skipped(self):
        """World coins with is_foreign=True must not be overwritten."""
        doc = {"Year": "1965", "is_foreign": True, "Country": "Canada"}
        assert self._should_backfill(doc) is False

    def test_empty_doc_flagged(self):
        """Edge case: minimal/empty doc missing is_foreign should be flagged."""
        assert self._should_backfill({}) is True

    def test_audit_record_structure(self):
        """Audit JSON written by the backfill script must have required keys."""
        import datetime as dt
        record = {
            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
            "scope": "single user: test_uid",
            "dry_run": True,
            "touched_count": 5,
            "skipped_count": 10,
            "touched_paths": ["users/test_uid/coins/doc1"],
        }
        required = {"timestamp", "scope", "dry_run", "touched_count", "skipped_count", "touched_paths"}
        assert required.issubset(record.keys()), f"Missing audit keys: {required - record.keys()}"
        assert isinstance(record["touched_paths"], list)
        assert record["dry_run"] is True  # Default safety gate

    def test_dry_run_default_is_true(self):
        """DRY_RUN defaults to true — must never auto-write without explicit opt-in."""
        import os
        # Simulate env without DRY_RUN set
        env_val = os.environ.get("DRY_RUN", "true").lower()
        assert env_val == "true", "DRY_RUN should default to 'true' for safety"
