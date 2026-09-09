"""
test_repair_26rj_ghosts.py
==========================
Unit tests for repair_26rj_ghosts.py script auditing and repairing
ghost USMC children in 2026 Uncirculated Coin Set (26RJ) parent documents.
"""

from unittest.mock import MagicMock, patch
import pytest

from scripts.repair_26rj_ghosts import (
    matches_26rj_in_code_filter,
    is_cent_entry,
    extract_mint_mark,
    get_canonical_denomination_category,
    evaluate_ghost,
    audit_parent_set,
    repair_parent_set,
    BACKUP_FIELD_NAME,
    RETAILER_ITEM_STAMP,
)


class TestRepair26RJInCodeFilter:
    """Step 1: Test tightened in-code filter for 26RJ parent sets."""

    def test_matches_theme_uncirculated_coin_set(self):
        data = {"Theme/Subject": "250th Anniversary Uncirculated Coin Set"}
        matched, reasons = matches_26rj_in_code_filter(data)
        assert matched is True
        assert any("Uncirculated Coin Set" in r for r in reasons)

    def test_matches_set_type_uncirculated(self):
        data = {"set_type": "uncirculated"}
        matched, reasons = matches_26rj_in_code_filter(data)
        assert matched is True
        assert any("set_type == 'uncirculated'" in r for r in reasons)

    def test_matches_name_26rj(self):
        data = {"name": "2026 US Mint Set 26RJ"}
        matched, reasons = matches_26rj_in_code_filter(data)
        assert matched is True
        assert any("26RJ" in r for r in reasons)

    def test_matches_program_series_uncirculated(self):
        data = {"Program/Series": "Uncirculated Sets"}
        matched, reasons = matches_26rj_in_code_filter(data)
        assert matched is True
        assert any("Program/Series" in r for r in reasons)

    def test_matches_retailer_item_no(self):
        data = {"Retailer Item No.": "26RJ"}
        matched, reasons = matches_26rj_in_code_filter(data)
        assert matched is True
        assert any("Retailer Item No." in r for r in reasons)

    def test_rejects_unrelated_set(self):
        data = {
            "Theme/Subject": "Morgan Dollar Tribute",
            "name": "Silver Proof Set",
            "set_type": "proof",
            "Program/Series": "Proof Sets",
            "Retailer Item No.": "26RF"
        }
        matched, reasons = matches_26rj_in_code_filter(data)
        assert matched is False
        assert len(reasons) == 0


class TestCentSafetyRules:
    """Safety: Test protection for all cent entries."""

    @pytest.mark.parametrize("denom", [
        "1 Cent", "One Cent", "Lincoln Cent", "Cent", "cent", "penny", "1c", "0.01"
    ])
    def test_is_cent_entry_positive(self, denom):
        assert is_cent_entry(denom) is True

    @pytest.mark.parametrize("denom", [
        "Nickel", "Dime", "Quarter", "Half Dollar", "Dollar", "Medal", "Stamp"
    ])
    def test_is_cent_entry_negative(self, denom):
        assert is_cent_entry(denom) is False

    def test_cent_entry_never_flagged_as_ghost_even_with_usmc_theme(self):
        # Even if theme mistakenly contains USMC patterns, safety rule protects cents
        is_ghost, reason = evaluate_ghost(
            denomination="Lincoln Cent",
            theme="Marine Corps 250 Years Honor Courage",
            name="2026 Cent"
        )
        assert is_ghost is False
        assert "SAFETY PROTECTED" in reason
        assert "cent" in reason

    def test_parent_doc_never_flagged_as_ghost(self):
        # A doc matching parent ID is never flagged as ghost child
        is_ghost, reason = evaluate_ghost(
            denomination="Set",
            theme="Uncirculated Set",
            doc_id="parent_123",
            parent_doc_id="parent_123"
        )
        assert is_ghost is False
        assert "SAFETY PROTECTED" in reason
        assert "parent set document" in reason


class TestGhostEvaluation:
    """Step 2: Ghost patterns and canonical checks."""

    @pytest.mark.parametrize("pattern", [
        "marine", "usmc", "1775-2025", "1775~2025", "250 years", "honor, courage", "honor courage"
    ])
    def test_usmc_ghost_patterns_detected(self, pattern):
        is_ghost, reason = evaluate_ghost(
            denomination="Half Dollar",
            theme=f"Commemorative {pattern} Coin"
        )
        assert is_ghost is True
        assert "Matches USMC ghost pattern" in reason

    def test_non_canonical_entry_flagged_as_ghost(self):
        is_ghost, reason = evaluate_ghost(
            denomination="Commemorative Bronze Medal",
            theme="General Washington"
        )
        assert is_ghost is True
        assert "Non-canonical denomination/theme" in reason

    def test_canonical_coins_not_flagged(self):
        canonical_test_cases = [
            ("1 Cent", "Lincoln Cent"),
            ("5 Cents", "Jefferson Nickel"),
            ("10 Cents", "Emerging Liberty Dime"),
            ("25 Cents", "Semiquincentennial Quarter"),
            ("50 Cents", "Enduring Liberty Half Dollar"),
            ("1 Dollar", "Native American Dollar"),
        ]
        for denom, theme in canonical_test_cases:
            is_ghost, reason = evaluate_ghost(denomination=denom, theme=theme)
            assert is_ghost is False, f"Expected canonical for {denom} - {theme}, got: {reason}"


class TestAuditParentSet:
    """Step 2 & 3: Auditing Path A (set_contents) and Path B (real children)."""

    def test_audit_inline_dict_set_contents_with_ghost(self):
        parent_id = "parent_test_1"
        parent_snap = MagicMock()
        parent_snap.id = parent_id
        parent_snap.to_dict.return_value = {
            "name": "2026 United States Mint Uncirculated Coin Set",
            "set_contents": [
                {"Denomination": "1 Cent", "Theme/Subject": "Lincoln Cent", "Mint Mark": "P"},
                {"Denomination": "1 Cent", "Theme/Subject": "Lincoln Cent", "Mint Mark": "D"},
                {"Denomination": "50 Cents", "Theme/Subject": "Marine Corps 250th Commemorative", "Mint Mark": "P"},  # Ghost
            ]
        }

        mock_coins_ref = MagicMock()
        mock_coins_ref.where.return_value.stream.return_value = []

        audit = audit_parent_set(parent_snap, mock_coins_ref)

        assert audit["path_a"]["count"] == 3
        assert audit["path_a"]["type_desc"] == "list of dicts (inline objects)"
        assert len(audit["path_a"]["ghost_indices"]) == 1
        assert audit["path_a"]["ghost_indices"] == [2]
        assert audit["canonical_summary"]["p_cent_present"] is True
        assert audit["canonical_summary"]["d_cent_present"] is True

    def test_audit_doc_id_string_set_contents(self):
        parent_id = "parent_test_2"
        parent_snap = MagicMock()
        parent_snap.id = parent_id
        parent_snap.to_dict.return_value = {
            "name": "2026 United States Mint Uncirculated Coin Set",
            "set_contents": ["doc_cent_p", "doc_usmc_ghost"]
        }

        mock_coins_ref = MagicMock()
        mock_coins_ref.where.return_value.stream.return_value = []

        # Mock child doc resolution
        snap_cent = MagicMock()
        snap_cent.exists = True
        snap_cent.to_dict.return_value = {
            "Denomination": "1 Cent",
            "Theme/Subject": "Lincoln Cent",
            "Mint Mark": "P"
        }

        snap_ghost = MagicMock()
        snap_ghost.exists = True
        snap_ghost.to_dict.return_value = {
            "Denomination": "Dollar",
            "Theme/Subject": "USMC 250 Years Honor, Courage",
            "Mint Mark": "P"
        }

        def mock_document(doc_id):
            doc_ref = MagicMock()
            if doc_id == "doc_cent_p":
                doc_ref.get.return_value = snap_cent
            elif doc_id == "doc_usmc_ghost":
                doc_ref.get.return_value = snap_ghost
            else:
                missing = MagicMock()
                missing.exists = False
                doc_ref.get.return_value = missing
            return doc_ref

        mock_coins_ref.document.side_effect = mock_document

        audit = audit_parent_set(parent_snap, mock_coins_ref)

        assert audit["path_a"]["count"] == 2
        assert audit["path_a"]["type_desc"] == "list of strings (doc IDs)"
        assert audit["path_a"]["ghost_indices"] == [1]
        assert audit["canonical_summary"]["p_cent_present"] is True
        assert audit["canonical_summary"]["d_cent_present"] is False


class TestRepairParentSet:
    """Phase 2: Transactional repair, pruning, backup, and safety."""

    def test_repair_prunes_ghosts_writes_backup_and_stamps_retailer(self):
        parent_id = "parent_rep_1"
        original_contents = [
            {"Denomination": "1 Cent", "Theme/Subject": "Lincoln Cent", "Mint Mark": "P"},
            {"Denomination": "5 Cents", "Theme/Subject": "Jefferson Nickel", "Mint Mark": "P"},
            {"Denomination": "50 Cents", "Theme/Subject": "Marine Corps 1775-2025", "Mint Mark": "P"},  # Ghost at idx 2
        ]

        audit_data = {
            "parent_id": parent_id,
            "path_a": {
                "count": 3,
                "raw_contents": original_contents,
                "ghost_indices": [2],
                "ghost_entries": [
                    {"index": 2, "denomination": "50 Cents", "theme": "Marine Corps 1775-2025", "doc_id": None}
                ]
            },
            "path_b": {
                "count": 1,
                "children": [],
                "usmc_children": [
                    {
                        "doc_id": "child_usmc_doc",
                        "denomination": "Dollar",
                        "theme": "USMC Commemorative",
                        "is_ghost": True
                    }
                ]
            },
            "canonical_summary": {
                "p_cent_present": True,
                "d_cent_present": False
            }
        }

        mock_db = MagicMock()
        mock_txn = MagicMock()
        # Ensure transaction context runner executes callback
        mock_db.transaction.return_value = mock_txn

        mock_coins_ref = MagicMock()
        parent_doc_ref = MagicMock()
        parent_doc_ref.id = parent_id
        child_doc_ref = MagicMock()
        child_doc_ref.id = "child_usmc_doc"

        # Mock post-repair get on parent
        post_repair_snap = MagicMock()
        post_repair_snap.to_dict.return_value = {
            "Retailer Item No.": RETAILER_ITEM_STAMP,
            BACKUP_FIELD_NAME: original_contents,
            "set_contents": original_contents[:2]
        }
        parent_doc_ref.get.return_value = post_repair_snap

        def mock_document_lookup(did):
            if did == parent_id:
                return parent_doc_ref
            elif did == "child_usmc_doc":
                return child_doc_ref
            return MagicMock()

        mock_coins_ref.document.side_effect = mock_document_lookup

        result = repair_parent_set(mock_db, mock_coins_ref, audit_data)

        assert result["parent_id"] == parent_id
        assert result["backup_written"] is True
        assert result["retailer_stamped"] is True
        assert result["original_set_contents_len"] == 3
        assert result["pruned_set_contents_len"] == 2
        assert result["deleted_child_count"] == 1
        assert "child_usmc_doc" in result["deleted_child_ids"]

        # Verify transaction update call contains expected fields
        parent_doc_ref.get.assert_called()
        mock_txn.update.assert_called_once()
        update_args = mock_txn.update.call_args[0]
        assert update_args[0] == parent_doc_ref
        assert update_args[1]["Retailer Item No."] == "26RJ"
        assert update_args[1][BACKUP_FIELD_NAME] == original_contents
        assert len(update_args[1]["set_contents"]) == 2

        # Verify deletion was called for ghost child
        mock_txn.delete.assert_called_once_with(child_doc_ref)
