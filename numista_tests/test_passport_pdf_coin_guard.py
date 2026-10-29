"""Plan.v2.1 §9 Gate 3b: Passport PDF & Melt Engine Coin Guard (`pytest numista_tests/test_passport_pdf_coin_guard.py -v`)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "numista_backend")))

from catalog_nac1 import KIND_TO_COLLECTION  # noqa: E402
from tests.test_catalog_collection_routing import (  # noqa: E402
    CWT_PRV,
    MEDAL,
    MORGAN,
    NOTE,
    FakeDb,
    add,
)


def test_passport_pdf_and_melt_engine_coin_subcollection_never_polluted_by_banknotes_or_medals():
    """
    Verifies Plan.v2.1 §3.1 invariant:
    Adding Bank Notes (`BN`), Medals (`MD`), Tokens (`TK`), or Private Medals (`CLASS=PRV`)
    writes exclusively to `currency` or `world_items` and NEVER writes a single document into
    `users/{uid}/coins`, preserving the Coin Passport PDF generator and melt-value calculator.
    """
    assert KIND_TO_COLLECTION["CN"] == "coins"
    assert KIND_TO_COLLECTION["BN"] == "currency"
    assert KIND_TO_COLLECTION["MD"] == "world_items"
    assert KIND_TO_COLLECTION["TK"] == "world_items"
    assert KIND_TO_COLLECTION["ST"] == "world_items"

    db = FakeDb()
    add(db, NOTE)
    add(db, MEDAL)
    add(db, CWT_PRV)

    coin_docs = [p for p in db.store if p.startswith("users/u1/coins/")]
    assert coin_docs == [], f"Non-coin items polluted users/u1/coins: {coin_docs}"

    # Adding an actual coin writes to users/u1/coins/ with valid specifications
    add(db, MORGAN)
    coin_docs_after = [p for p in db.store if p.startswith("users/u1/coins/")]
    assert len(coin_docs_after) == 1
    assert db.store[coin_docs_after[0]]["kind"] == "CN"
