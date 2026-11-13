"""Tests for Review 04 Two-Field Mint Consistency (M4-03, M4-04)."""

from unittest.mock import MagicMock

from numista_backend.services.mint_helpers import (
    query_docs_by_mint_mark,
    read_mint_mark,
)
from numista_backend.services.greysheet_service import GreysheetService
from numista_backend.services.transfer_service import execute_claim_transaction


class _FakeDoc:
    def __init__(self, doc_id: str, data: dict):
        self.id = doc_id
        self._data = data

    def to_dict(self):
        return dict(self._data)


class _FakeQuery:
    def __init__(self, docs, filters=None, limit_n=None):
        self._docs = docs
        self._filters = list(filters or [])
        self._limit_n = limit_n

    def where(self, field, op, value):
        assert op == "=="
        return _FakeQuery(self._docs, self._filters + [(field, value)], self._limit_n)

    def limit(self, n):
        return _FakeQuery(self._docs, self._filters, n)

    def get(self):
        matched = []
        for doc in self._docs:
            data = doc.to_dict()
            ok = True
            for field, val in self._filters:
                if val is None:
                    if data.get(field) is not None:
                        ok = False
                        break
                else:
                    if data.get(field) != val:
                        ok = False
                        break
            if ok:
                matched.append(doc)
        if self._limit_n is not None:
            return matched[: self._limit_n]
        return matched


def test_query_docs_by_mint_mark_canonical_and_legacy_fallback():
    docs = [
        _FakeDoc("c1", {"Year": "2024", "mint_mark": "D"}),
        _FakeDoc("l1", {"Year": "2024", "Mint Mark": "S"}),
    ]
    base = _FakeQuery(docs)

    res_d = query_docs_by_mint_mark(base, "D")
    assert [d.id for d in res_d] == ["c1"]

    res_s = query_docs_by_mint_mark(base, "S")
    assert [d.id for d in res_s] == ["l1"]


def test_query_docs_by_mint_mark_empty_handles_blank_and_none_and_dedups():
    docs = [
        _FakeDoc("n1", {"Year": "2026", "mint_mark": ""}),
        _FakeDoc("n2", {"Year": "2026", "mint_mark": None, "Mint Mark": ""}),
        _FakeDoc("n3", {"Year": "2026", "Mint Mark": None}),
    ]
    res = query_docs_by_mint_mark(_FakeQuery(docs), "")
    assert [d.id for d in res] == ["n1", "n2", "n3"]


def test_read_mint_mark_post_prune():
    assert read_mint_mark({"mint_mark": "W"}) == "W"
    assert read_mint_mark({"mint": "Philadelphia", "mint_mark": ""}) == ""


def test_greysheet_validate_match_reads_post_prune_mint_mark():
    svc = GreysheetService(db=None)
    ok, reason = svc.validate_match(
        "1921-S Morgan Dollar",
        {"Year": "1921", "mint_mark": "S", "Program/Series": "Morgan Dollar", "Denomination": "$1"},
    )
    assert ok is True, reason


def test_claim_transfer_preserves_modern_and_dual_writes_legacy():
    claim_fn = getattr(execute_claim_transaction, "__wrapped__", execute_claim_transaction)

    def _run_claim(item_data):
        db = MagicMock()
        tx = MagicMock()
        transfer_doc = MagicMock()
        transfer_doc.exists = True
        transfer_doc.to_dict.return_value = {
            "status": "pending",
            "sender_id": "alice@example.com",
            "sender_name": "Alice",
            "items": [{"id": "orig-1", **item_data}],
            "provenanceLedger": [],
        }
        transfer_ref = MagicMock()
        transfer_ref.id = "t-1"
        transfer_ref.get.return_value = transfer_doc

        sender_coin_doc = MagicMock()
        sender_coin_doc.exists = False
        db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = sender_coin_doc

        written_docs = []
        tx.set.side_effect = lambda ref, d, **kwargs: written_docs.append(d)

        res = claim_fn(tx, db, transfer_ref, "bob@example.com")
        assert res["status"] == "claimed"
        # First tx.set is the recipient coin doc (second is archive)
        return written_docs[0]

    # Case 1: modern item with manual override preserved
    modern = _run_claim({
        "Year": "2026",
        "mint": "Custom Mint",
        "mint_mark": "P",
        "Denomination": "$1",
    })
    assert modern["mint"] == "Custom Mint"
    assert modern["mint_mark"] == "P"
    assert modern["Mint Mark"] == "P"

    # Case 2: post-prune item with only mint_mark dual-writes all 3 fields
    post_prune = _run_claim({
        "Year": "2024",
        "mint_mark": "D",
        "Denomination": "Quarter",
        "Program/Series": "American Women Quarters",
    })
    assert post_prune["mint"] == "Denver"
    assert post_prune["mint_mark"] == "D"
    assert post_prune["Mint Mark"] == "D"
