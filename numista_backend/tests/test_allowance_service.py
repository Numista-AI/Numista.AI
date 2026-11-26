"""Entitlement path for the claim-time lock + Transfer Document PDF (PLAN v1.2 sections 4.1, 4.5)."""
import os
import sys

import pytest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from tests.fakes_firestore import FakeDB, seed_item  # noqa: E402
from services import allowance_service  # noqa: E402
from services.transfer_service import initiate_transfer  # noqa: E402
from services.transfer_document_pdf import claim_url, generate_transfer_document_pdf  # noqa: E402

EMAIL = "seller@example.com"


def _pdf_text(pdf_bytes: bytes) -> str:
    pypdf = pytest.importorskip("pypdf")
    import io
    return "\n".join(p.extract_text() for p in pypdf.PdfReader(io.BytesIO(pdf_bytes)).pages)


# ---------------------------------------------------------------- real entitlement functions
def test_founding_beta_resolves_unlimited_through_uid_for_auth(monkeypatch):
    """Never gate on stripe_tier alone (F8): the date-based Founding Beta fact must be injected."""
    import tier_gatekeeper as tg
    seen = {}

    def fake_profile(identifier, uid_for_auth=None, sign_in_provider=None):
        seen.update(identifier=identifier, uid=uid_for_auth, provider=sign_in_provider)
        # what get_user_profile(uid_for_auth=...) injects for a signup before the 15 Dec 2026 cutoff
        return {"_auth_created_ms": tg.BETA_SIGNUP_CUTOFF_MS - 1000, "_auth_is_anonymous": False}

    monkeypatch.setattr(tg, "get_user_profile", fake_profile)
    assert allowance_service.resolve_coin_limit(uid="U1", email=EMAIL, sign_in_provider="password") is None
    assert seen == {"identifier": EMAIL, "uid": "U1", "provider": "password"}


def test_free_account_resolves_to_ten(monkeypatch):
    import tier_gatekeeper as tg
    monkeypatch.setattr(tg, "get_user_profile", lambda *a, **k: {"_auth_created_ms": tg.BETA_SIGNUP_CUTOFF_MS + 1000,
                                                                  "_auth_is_anonymous": False})
    assert allowance_service.resolve_coin_limit(uid="U2", email=EMAIL) == 10


def test_stripe_tier_alone_is_not_the_gate(monkeypatch):
    import tier_gatekeeper as tg
    profile = {"stripe_tier": "free", "_auth_created_ms": tg.BETA_SIGNUP_CUTOFF_MS - 1, "_auth_is_anonymous": False}
    monkeypatch.setattr(tg, "get_user_profile", lambda *a, **k: profile)
    assert allowance_service.resolve_coin_limit(uid="U3", email=EMAIL) is None


def test_auth_facts_unavailable_never_locks(monkeypatch):
    import tier_gatekeeper as tg

    def boom(*a, **k):
        raise tg.AuthFactsUnavailable("auth lookup failed")
    monkeypatch.setattr(tg, "get_user_profile", boom)
    d = FakeDB()
    for i in range(15):
        seed_item(d, EMAIL, f"k{i:02d}", created_at=f"2026-03-{i + 1:02d}T00:00:00+00:00")
    out = allowance_service.apply_free_overflow_lock(d, user_key=EMAIL, uid="U4")
    assert out["skipped"] == "entitlement_unavailable"
    assert not any(v.get("locked_pending_upgrade") for v in d.store.values())


def test_unlock_on_upgrade_uses_the_existing_helper(monkeypatch):
    import tier_gatekeeper as tg
    from tests.fakes_firestore import Col
    d = FakeDB()
    for i in range(12):
        seed_item(d, EMAIL, f"k{i:02d}", created_at=f"2026-03-{i + 1:02d}T00:00:00+00:00")
    allowance_service.apply_free_overflow_lock(d, user_key=EMAIL, uid="U5", limit_resolver=lambda: 10)
    assert sum(1 for v in d.store.values() if v.get("locked_pending_upgrade")) == 2
    # tier_gatekeeper.unlock_user_coins is what payment_routes.py calls on an upgrade payment
    _orig_where = Col.where
    monkeypatch.setattr(
        Col,
        "where",
        lambda self, field=None, op=None, value=None, *, filter=None: (
            _orig_where(self, filter.field_path, filter.op_string, filter.value)
            if filter is not None else _orig_where(self, field, op, value)
        ),
    )
    monkeypatch.setattr(tg, "_run_txn", lambda db, fn: fn(db.transaction()))
    tg.unlock_user_coins(d, "U5", EMAIL, None)
    assert not any(v.get("locked_pending_upgrade") for v in d.store.values())


def test_allowance_module_does_not_depend_on_the_lock_function_signature():
    """The NET-827 build changes lock_overflow_coins' signature; this module must not call it."""
    src = open(os.path.join(backend_dir, "services", "allowance_service.py"), encoding="utf-8").read()
    assert "lock_overflow_coins(" not in src.replace("tier_gatekeeper.lock_overflow_coins", "")


# ---------------------------------------------------------------- Transfer Document
@pytest.fixture
def doc_transfer():
    d = FakeDB()
    seed_item(d, EMAIL, "c1", Cost="$45.00", **{"Mint Mark": "S", "Condition": "MS-65", "Grading Service": "PCGS",
              "cert_number": "123456789"}, cpgRetail=150.0, greysheet_bid=123.45)
    return initiate_transfer(db=d, user_a_id=EMAIL, item_ids=["c1"], version=2, transfer_type="sale_ebay",
                             sender_display="A. Seller", sender_address="1 Main St, Springfield")


def test_pdf_has_item_claim_code_and_expiry_but_never_the_email(doc_transfer):
    text = _pdf_text(generate_transfer_document_pdf(doc_transfer, doc_transfer["claim_token"], doc_transfer["claim_code"]))
    assert "TRANSFER DOCUMENT" in text and "Sale (eBay)" in text
    assert "1921" in text and "PCGS" in text and "123456789" in text
    assert doc_transfer["claim_code"] in text
    assert doc_transfer["expires_at"][:10] in text
    assert "A. Seller" in text and "1 Main St" in text, "typed sender details print"
    assert "seller@example.com" not in text and "@" not in text
    assert doc_transfer["sender_ref"] in text


def test_pdf_never_shows_cost_cpg_or_wholesale(doc_transfer):
    text = _pdf_text(generate_transfer_document_pdf(doc_transfer, doc_transfer["claim_token"], doc_transfer["claim_code"]))
    for forbidden in ("45.00", "150", "123.45", "greysheet", "Greysheet", "CPG"):
        assert forbidden not in text, forbidden


def test_pdf_hides_address_when_the_seller_typed_none():
    d = FakeDB()
    seed_item(d, EMAIL, "c1")
    t = initiate_transfer(db=d, user_a_id=EMAIL, item_ids=["c1"], version=2, transfer_type="gift")
    text = _pdf_text(generate_transfer_document_pdf(t, t["claim_token"], t["claim_code"]))
    assert "Gift" in text and "Street" not in text and "St," not in text


def test_pdf_copy_without_secrets_says_how_to_reissue(doc_transfer):
    text = " ".join(_pdf_text(generate_transfer_document_pdf(doc_transfer)).split())
    assert doc_transfer["claim_code"] not in text and "Reissue code" in text


def test_claim_url_puts_the_token_in_the_fragment():
    assert claim_url("TOK") == "https://numista.ai/#/claim?t=TOK"


def test_pdf_price_only_when_seller_opts_in():
    d = FakeDB()
    seed_item(d, EMAIL, "c1")
    shown = initiate_transfer(db=d, user_a_id=EMAIL, item_ids=["c1"], version=2, transfer_type="sale_private",
                              show_price=True, sale_price_usd=250.0)
    assert "$250.00" in _pdf_text(generate_transfer_document_pdf(shown, shown["claim_token"], shown["claim_code"]))
    d2 = FakeDB()
    seed_item(d2, EMAIL, "c1")
    hidden = initiate_transfer(db=d2, user_a_id=EMAIL, item_ids=["c1"], version=2, transfer_type="sale_private",
                               sale_price_usd=250.0)
    assert "250" not in _pdf_text(generate_transfer_document_pdf(hidden, hidden["claim_token"], hidden["claim_code"]))
