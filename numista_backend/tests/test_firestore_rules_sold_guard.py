"""Static checks for the Sold / pending read-only rules (PLAN v1.2 G1, F14).

The Firestore emulator needs node + java + firebase-tools, which are not part of the pytest environment, so
these tests parse the rules text itself. They assert the properties that matter and that are easy to break:
overlapping `match` rules are OR-ed, so a collection with its own guarded block MUST also be excluded from
the wildcard rule, in BOTH rules files, which must stay identical for these collections.
"""
import os
import re

import pytest

BACKEND = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RULE_FILES = {
    "mobile": os.path.join(BACKEND, "..", "numista_mobile", "firestore.rules"),
    "backend": os.path.join(BACKEND, "firestore.rules"),
}
GUARD = "resource.data.get('status', 'active') != 'sold' && resource.data.get('transferStatus', 'none') != 'pending'"


def _text(name):
    with open(RULE_FILES[name], encoding="utf-8") as fh:
        return fh.read()


def _flat(s):
    return re.sub(r"\s+", " ", s)


def _block(text, header):
    start = text.index(header)
    return text[start:text.index("\n    }\n", start)]


@pytest.mark.parametrize("name", ["mobile", "backend"])
@pytest.mark.parametrize("sub", ["coins", "banknotes", "currency"])
def test_each_item_collection_is_excluded_from_the_wildcard(name, sub):
    wildcard = [m for m in re.findall(r"!\(sub in \[(.*?)\]\)", _text(name), flags=re.S)]
    assert len(wildcard) == 2, "the doc rule and the nested-doc rule both carry the exclusion list"
    for lst in wildcard:
        assert f"'{sub}'" in lst, f"{sub} must be excluded from the wildcard, or the wildcard re-grants write access"


@pytest.mark.parametrize("name", ["mobile", "backend"])
def test_coins_update_and_delete_are_blocked_for_sold_and_pending(name):
    blk = _flat(_block(_text(name), "match /users/{email}/coins/{coinId} {"))
    assert f"allow delete: if isOwner(email) && {GUARD};" in blk
    assert GUARD in blk.split("allow update:")[1]
    assert "request.resource.data.is_demo == false" in blk, "existing create rule must be intact"


@pytest.mark.parametrize("name", ["mobile", "backend"])
@pytest.mark.parametrize("sub", ["banknotes", "currency"])
def test_paper_money_blocks_guard_sold_and_pending_and_keep_create(name, sub):
    blk = _flat(_block(_text(name), f"match /users/{{email}}/{sub}/{{docId}} {{"))
    assert "allow read, create: if isOwner(email);" in blk
    assert f"allow update, delete: if isOwner(email) && {GUARD};" in blk


def test_the_two_rules_files_agree_on_the_guarded_collections():
    for sub in ("banknotes", "currency"):
        header = f"match /users/{{email}}/{sub}/{{docId}} {{"
        assert _flat(_block(_text("mobile"), header)) == _flat(_block(_text("backend"), header))
    assert _flat(_block(_text("mobile"), "match /users/{email}/coins/{coinId} {")) == \
        _flat(_block(_text("backend"), "match /users/{email}/coins/{coinId} {"))


@pytest.mark.parametrize("name", ["mobile", "backend"])
def test_transfers_and_claim_lookups_have_no_client_rule_so_default_deny_applies(name):
    text = _text(name)
    assert "match /transfers/" not in text and "match /transfer_claims/" not in text
    assert "match /{document=**} {\n      allow read, write: if false;" in text, "default deny must remain"
