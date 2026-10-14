"""
numista_backend/tests/test_p2_coin_count_single_source.py
---------------------------------------------------------
Unit tests verifying the P2 Coin Count Single Source of Truth:
- expand_collection_inventory expands set child coins
- count_coins_and_lots counts only physical coins (loose + set children)
- Set parents, supplies, and paper currency are excluded from total_coins
- Replicates the exact 284 lots -> 311 physical coins (+ 2 currency = 313 items) scenario
"""

from unittest.mock import MagicMock
import pytest

from scan_service.collection_inventory import (
    expand_collection_inventory,
    count_coins_and_lots,
    is_physical_coin,
    is_set_parent,
)


def _make_mock_doc(doc_id: str, data: dict):
    doc = MagicMock()
    doc.id = doc_id
    doc.to_dict.return_value = data
    return doc


def test_coin_count_exact_mismatch_scenario():
    """
    Simulates the exact user collection scenario:
    - 280 loose coins (lots)
    - 4 sets containing a total of 31 physical coins (4 lots)
    - Total lots in Firestore = 280 + 4 = 284
    - Total physical coins = 280 + 31 = 311
    - 2 paper currency items (banknotes)
    - 1 supply item
    Verifies that total_coins is 311, NOT 284 (unexpanded), NOT 313 (coins + currency), NOT 314.
    """
    docs = []

    # 1. 280 loose coins
    for i in range(280):
        docs.append(_make_mock_doc(f"loose_coin_{i}", {
            "Year": "1964",
            "Denomination": "Quarter Dollar",
            "item_type": "coin",
            "AI Estimated Value": "$10.00",
        }))

    # 2. 4 sets with 31 total child coins
    # Set 1: 5-coin silver proof set
    docs.append(_make_mock_doc("set_1", {
        "Theme/Subject": "1999 Silver Proof Set",
        "item_type": "set",
        "set_contents": [
            {"Denomination": "Cent", "Year": "1999", "item_type": "coin"},
            {"Denomination": "Nickel", "Year": "1999", "item_type": "coin"},
            {"Denomination": "Dime", "Year": "1999", "item_type": "coin"},
            {"Denomination": "Quarter", "Year": "1999", "item_type": "coin"},
            {"Denomination": "Half Dollar", "Year": "1999", "item_type": "coin"},
        ],
        "AI Estimated Value": "$35.00",
    }))

    # Set 2: 6-coin set
    docs.append(_make_mock_doc("set_2", {
        "Theme/Subject": "2000 Mint Set",
        "item_type": "set",
        "set_contents": [
            {"Denomination": "Cent", "Year": "2000", "item_type": "coin"},
            {"Denomination": "Nickel", "Year": "2000", "item_type": "coin"},
            {"Denomination": "Dime", "Year": "2000", "item_type": "coin"},
            {"Denomination": "Quarter", "Year": "2000", "item_type": "coin"},
            {"Denomination": "Half Dollar", "Year": "2000", "item_type": "coin"},
            {"Denomination": "Dollar", "Year": "2000", "item_type": "coin"},
        ],
        "AI Estimated Value": "$20.00",
    }))

    # Set 3: 10-coin state quarters set
    docs.append(_make_mock_doc("set_3", {
        "Theme/Subject": "State Quarters Set",
        "item_type": "set",
        "set_contents": [
            {"Denomination": "Quarter", "Year": "2004", "item_type": "coin"} for _ in range(10)
        ],
        "AI Estimated Value": "$50.00",
    }))

    # Set 4: 10-coin proof set
    docs.append(_make_mock_doc("set_4", {
        "Theme/Subject": "2007 Proof Set",
        "item_type": "set",
        "set_contents": [
            {"Denomination": "Quarter", "Year": "2007", "item_type": "coin"} for _ in range(10)
        ],
        "AI Estimated Value": "$45.00",
    }))

    # Total set children = 5 + 6 + 10 + 10 = 31

    # 3. 2 paper currency items
    docs.append(_make_mock_doc("curr_1", {
        "Denomination": "Five Dollars",
        "Year": "1953",
        "item_type": "paper_currency",
        "AI Estimated Value": "$15.00",
    }))
    docs.append(_make_mock_doc("curr_2", {
        "Denomination": "Two Dollars",
        "Year": "1976",
        "item_type": "paper_currency",
        "AI Estimated Value": "$4.00",
    }))

    # 4. 1 supply item
    docs.append(_make_mock_doc("sup_1", {
        "item_type": "supply",
        "is_supply": True,
        "Original Description from source": "Coin albums",
    }))

    # Expand inventory
    inventory, stats = expand_collection_inventory(docs, include_financial=True)
    counts = count_coins_and_lots(inventory)

    # Assertions:
    # 284 parent lots in Firestore (280 loose + 4 sets). Supplies and currency are also in docs (287 docs total).
    assert stats["sets"] == 4

    # Physical coins count MUST be 311:
    # 280 loose + 31 set children = 311
    # Paper currency (2), supplies (1), and set parents (4) MUST NOT be counted as physical coins!
    assert counts["total_coins"] == 311

    # Total lots = 280 loose + 4 sets + 2 currency + 1 supply = 287 parent docs
    assert counts["set_count"] == 4


def test_is_physical_coin_rules():
    """Verify individual counting rules for different item types."""
    assert is_physical_coin({"item_type": "coin", "is_set_parent": False}) is True
    assert is_physical_coin({"item_type": "", "is_set_parent": False}) is True
    assert is_physical_coin({"item_type": "set", "is_set_parent": True}) is False
    assert is_physical_coin({"item_type": "coin", "is_set_parent": True}) is False
    assert is_physical_coin({"item_type": "paper_currency", "is_set_parent": False}) is False
    assert is_physical_coin({"item_type": "supply", "is_set_parent": False}) is False
    assert is_physical_coin({"item_type": "medal", "is_set_parent": False}) is False
