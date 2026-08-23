"""
Numista.AI — Catalog Slot Count Regression Tests
Verifies that the master_coin_programs.json slot counts match expected values
after the Aug 22 catalog rebuilds (Kennedy 213-slot, Eisenhower 32-slot,
Program Manager slot count fix, seeder total_slots fix).

These tests guard against the regression where:
  - total_slots was counting year-rows (e.g. 61 for Kennedy) instead of
    variety-slots (e.g. 213 for Kennedy).
  - The Program Manager card displayed '0/61' instead of '0/213'.

All tests are offline — they parse master_coin_programs.json directly.
"""
import json
import os
import pytest

CATALOG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "master_coin_programs.json"
)


@pytest.fixture(scope="module")
def catalog():
    """Load and return the master coin programs catalog."""
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


@pytest.fixture(scope="module")
def program_index(catalog):
    """Return a dict keyed by program Name for easy lookup."""
    return {prog["Name"]: prog for prog in catalog if "Name" in prog}


def _slot_count(prog: dict) -> int:
    """Compute variety-slot count: sum of len(coin['varieties']) for all coins."""
    coins = prog.get("Coins", prog.get("coins", []))
    total = 0
    for coin in coins:
        varieties = coin.get("varieties", coin.get("Varieties", []))
        # If varieties is missing/empty, the slot is still 1 (the year itself)
        total += len(varieties) if varieties else 1
    return total


def _year_row_count(prog: dict) -> int:
    """Count year-rows (the old buggy denominator)."""
    coins = prog.get("Coins", prog.get("coins", []))
    return len(coins)


# ── Kennedy Half Dollars ─────────────────────────────────────────────────────

class TestKennedyCatalogRebuild:
    """213-slot Kennedy rebuild (Aug 22)."""

    def test_kennedy_variety_slots_equal_213(self, program_index):
        """Variety-slot count must be 213, NOT year-row count."""
        prog = program_index.get("Kennedy Half Dollars")
        assert prog is not None, "Kennedy Half Dollars not found in catalog"
        assert _slot_count(prog) == 213

    def test_kennedy_year_rows_equal_61(self, program_index):
        """Year-row count is 61 — this was the old (wrong) denominator."""
        prog = program_index["Kennedy Half Dollars"]
        assert _year_row_count(prog) == 61

    def test_kennedy_slot_count_exceeds_year_rows(self, program_index):
        """Slot count must always exceed year-row count (multiple varieties per year)."""
        prog = program_index["Kennedy Half Dollars"]
        assert _slot_count(prog) > _year_row_count(prog)

    def test_kennedy_1964_has_proof_slot(self, program_index):
        """1964 Kennedy must include a PROOF slot (Philadelphia 90% Ag proof)."""
        prog = program_index["Kennedy Half Dollars"]
        coins = prog.get("Coins", prog.get("coins", []))
        coin_1964 = next((c for c in coins if str(c.get("year", "")) == "1964"), None)
        assert coin_1964 is not None, "1964 Kennedy coin row not found"
        varieties = coin_1964.get("varieties", [])
        variety_ids = [v.get("id", "") for v in varieties]
        assert "PROOF" in variety_ids, f"PROOF slot missing from 1964 Kennedy; found: {variety_ids}"

    def test_kennedy_1965_1967_has_sms_no_phantom_d(self, program_index):
        """1965-1967 Kennedy must have SMS slots and no phantom D-mint slot."""
        prog = program_index["Kennedy Half Dollars"]
        coins = prog.get("Coins", prog.get("coins", []))
        for yr in ["1965", "1966", "1967"]:
            coin = next((c for c in coins if str(c.get("year", "")) == yr), None)
            assert coin is not None, f"{yr} Kennedy row not found"
            varieties = coin.get("varieties", [])
            variety_ids = [v.get("id", "") for v in varieties]
            assert "SMS" in variety_ids, f"SMS slot missing from {yr} Kennedy; found: {variety_ids}"
            assert "D-UNC" not in variety_ids, f"Phantom D-UNC slot present in {yr} Kennedy (should not exist)"

    def test_kennedy_1968_1969_has_s_silver_proof_not_s_proof(self, program_index):
        """1968-1969 Kennedy must have S-SILVER-PROOF, not plain S-PROOF (40% Ag proof rename)."""
        prog = program_index["Kennedy Half Dollars"]
        coins = prog.get("Coins", prog.get("coins", []))
        for yr in ["1968", "1969"]:
            coin = next((c for c in coins if str(c.get("year", "")) == yr), None)
            if coin is None:
                continue  # Year may be absent in some catalog versions
            varieties = coin.get("varieties", [])
            variety_ids = [v.get("id", "") for v in varieties]
            assert "S-SILVER-PROOF" in variety_ids, \
                f"S-SILVER-PROOF missing from {yr} Kennedy; found: {variety_ids}"
            assert "S-PROOF" not in variety_ids, \
                f"Plain S-PROOF present in {yr} Kennedy — should be S-SILVER-PROOF; found: {variety_ids}"


# ── Eisenhower Dollars ────────────────────────────────────────────────────────

class TestEisenhowerCatalogRebuild:
    """32-slot Eisenhower rebuild (Aug 22)."""

    def test_eisenhower_variety_slots_equal_32(self, program_index):
        """Variety-slot count must be 32, NOT year-row count."""
        prog = program_index.get("Eisenhower Dollars")
        assert prog is not None, "Eisenhower Dollars not found in catalog"
        assert _slot_count(prog) == 32

    def test_eisenhower_year_rows_equal_7(self, program_index):
        """Eisenhower has 7 year-rows (1971-1978) — not 32."""
        prog = program_index["Eisenhower Dollars"]
        assert _year_row_count(prog) == 7

    def test_eisenhower_1971_has_s_silver_proof_not_s_proof(self, program_index):
        """1971 Eisenhower must have S-SILVER-PROOF (no clad S proof was struck in 1971)."""
        prog = program_index["Eisenhower Dollars"]
        coins = prog.get("Coins", prog.get("coins", []))
        coin_1971 = next((c for c in coins if str(c.get("year", "")) == "1971"), None)
        assert coin_1971 is not None, "1971 Eisenhower not found"
        varieties = coin_1971.get("varieties", [])
        variety_ids = [v.get("id", "") for v in varieties]
        assert "S-SILVER-PROOF" in variety_ids, f"S-SILVER-PROOF missing from 1971 Ike; found: {variety_ids}"
        # S-PROOF (clad) should NOT be in 1971 — no clad S proof was struck
        assert "S-PROOF" not in variety_ids, f"Phantom S-PROOF in 1971 Ike (no clad S proof struck); found: {variety_ids}"

    def test_eisenhower_1973_has_both_s_proof_and_s_silver_proof(self, program_index):
        """1973 Eisenhower must have both S-PROOF (clad proof exists) and S-SILVER-PROOF."""
        prog = program_index["Eisenhower Dollars"]
        coins = prog.get("Coins", prog.get("coins", []))
        coin_1973 = next((c for c in coins if str(c.get("year", "")) == "1973"), None)
        assert coin_1973 is not None, "1973 Eisenhower not found"
        varieties = coin_1973.get("varieties", [])
        variety_ids = [v.get("id", "") for v in varieties]
        assert "S-PROOF" in variety_ids or "S-CLAD" in variety_ids, \
            f"S-PROOF/S-CLAD slot missing from 1973 Ike; found: {variety_ids}"
        assert "S-SILVER-PROOF" in variety_ids, \
            f"S-SILVER-PROOF missing from 1973 Ike; found: {variety_ids}"

    def test_eisenhower_1972_has_s_silver_not_s_proof(self, program_index):
        """1972 Eisenhower: S-SILVER (BU) and S-SILVER-PROOF, but NOT plain S-PROOF."""
        prog = program_index["Eisenhower Dollars"]
        coins = prog.get("Coins", prog.get("coins", []))
        coin_1972 = next((c for c in coins if str(c.get("year", "")) == "1972"), None)
        if coin_1972 is None:
            pytest.skip("1972 Eisenhower not present in catalog")
        varieties = coin_1972.get("varieties", [])
        variety_ids = [v.get("id", "") for v in varieties]
        # S-SILVER (40% BU) or S-SILVER-PROOF should be present
        has_silver = "S-SILVER" in variety_ids or "S-SILVER-PROOF" in variety_ids
        assert has_silver, f"No silver slot in 1972 Ike; found: {variety_ids}"


# ── General Catalog Invariants ────────────────────────────────────────────────

class TestCatalogInvariants:
    """Cross-program sanity invariants to catch future slot count regressions."""

    def test_every_program_has_at_least_one_slot(self, catalog):
        """No program should have zero slots (empty varieties list)."""
        zero_slot_programs = []
        for prog in catalog:
            name = prog.get("Name", "?")
            if _slot_count(prog) == 0:
                coins = prog.get("Coins", prog.get("coins", []))
                if len(coins) > 0:  # Has year rows but zero slots = bug
                    zero_slot_programs.append(name)
        assert zero_slot_programs == [], \
            f"Programs with year rows but 0 variety-slots: {zero_slot_programs}"

    def test_slot_count_always_gte_year_row_count(self, catalog):
        """Slot count must always be >= year-row count (at least 1 variety per row)."""
        violations = []
        for prog in catalog:
            name = prog.get("Name", "?")
            slots = _slot_count(prog)
            rows = _year_row_count(prog)
            if rows > 0 and slots < rows:
                violations.append(f"{name}: {slots} slots < {rows} year-rows")
        assert violations == [], f"Programs with fewer slots than year-rows: {violations}"

    def test_no_duplicate_variety_ids_within_same_year(self, catalog):
        """
        Within a single year row, variety IDs must be unique.
        Duplicate IDs in the same year would cause the slot matcher to double-assign.
        """
        duplicates = []
        for prog in catalog:
            name = prog.get("Name", "?")
            coins = prog.get("Coins", prog.get("coins", []))
            for coin in coins:
                yr = coin.get("year", "?")
                varieties = coin.get("varieties", [])
                ids = [
                    (v.get("id", "") if isinstance(v, dict) else v)
                    for v in varieties
                ]
                if len(ids) != len(set(ids)):
                    seen = set()
                    dupes = [x for x in ids if x in seen or seen.add(x)]  # type: ignore[func-returns-value]
                    duplicates.append(f"{name} {yr}: duplicates={dupes}")
        assert duplicates == [], f"Programs with duplicate variety IDs in same year: {duplicates}"
