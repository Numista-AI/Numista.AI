import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from main import app
from routes.deps import get_current_user
import services.greysheet_service as gs_module
import main

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_external_services(monkeypatch):
    """Ensure tests run offline with mocked Firestore and Greysheet API."""
    mock_db = MagicMock()
    mock_doc = MagicMock()
    mock_doc.to_dict.return_value = {
        "Quantity": 1,
        "greysheetGsid": "429",
        "greysheetBid": 95.0,
        "greysheetAsk": 110.0,
        "cpgRetail": 120.0,
        "AI Estimated Value": "$120.00",
        "item_type": "coin",
        "Year": "1881",
        "MintMark": "S",
        "Denomination": "Morgan Dollar",
        "ProgramSeries": "Morgan Dollars",
        "Condition": "MS-64",
    }
    mock_doc.exists = True
    mock_doc.get.return_value = mock_doc

    mock_coins_collection = MagicMock()
    mock_coins_collection.document.return_value = mock_doc
    mock_coins_collection.get.return_value = [mock_doc]

    mock_user_doc = MagicMock()
    mock_user_doc.collection.return_value = mock_coins_collection

    mock_users_collection = MagicMock()
    mock_users_collection.document.return_value = mock_user_doc

    mock_db.collection.return_value = mock_users_collection
    monkeypatch.setattr(main, "db", mock_db)

    # Mock Greysheet pricing response
    def mock_get_pricing(self, gsid):
        return [{
            "CollectableId": 429,
            "PricingData": [
                {
                    "Grade": 64,
                    "GradeLabel": "MS-64",
                    "CpgVal": "120.00",
                    "GreyVal": "95.00",
                    "GreyAskVal": "110.00",
                    "PcgsVal": "125.00",
                    "NgcVal": "120.00",
                    "BlueBookVal": "80.00",
                    "IsCac": False
                }
            ]
        }]
    monkeypatch.setattr(gs_module.GreysheetService, "get_pricing", mock_get_pricing)

    # Mock _authenticate_request
    monkeypatch.setattr(main, "_authenticate_request", lambda auth, body_email=None, current_user=None: "test_user@numista.ai")


def test_greysheet_lookup_response_contains_no_bid_fields():
    """Verify that /api/greysheet/refresh returns CPG/retail fields and strips bid/ask."""
    payload = {
        "user_id": "test_user@numista.ai",
        "coin_id": "test-coin-123"
    }
    prev_override = main.app.dependency_overrides.get(main.get_current_user)
    main.app.dependency_overrides[main.get_current_user] = lambda: {
        "email": "test_user@numista.ai",
        "uid": "test-uid",
    }
    try:
        response = client.post("/api/greysheet/refresh", json=payload)
    finally:
        if prev_override is None:
            main.app.dependency_overrides.pop(main.get_current_user, None)
        else:
            main.app.dependency_overrides[main.get_current_user] = prev_override
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

    # Must contain retail guide benchmark
    assert "cpgRetail" in data or "cpg_retail" in data

    # Assert bid / ask / net_margin fields are completely absent
    for forbidden_key in ["greysheet_bid", "greysheetBid", "greysheet_ask", "greysheetAsk", "gs_ask", "net_margin"]:
        assert forbidden_key not in data, f"Forbidden key '{forbidden_key}' found in response!"


def test_deals_endpoint_contains_no_bid_fields():
    """Verify that /api/greysheet/deals returns deals with CPG benchmark and no bid/net_margin."""
    app.dependency_overrides[get_current_user] = lambda: {"uid": "test_user", "email": "test@numista.ai"}
    try:
        response = client.get("/api/greysheet/deals")
        assert response.status_code == 200
        data = response.json()
        assert "deals" in data
        assert len(data["deals"]) > 0

        for deal in data["deals"]:
            # CPG Retail benchmark should be present
            assert "cpg_retail" in deal
            assert "margin_percent" in deal
            # Forbidden bid & net_margin fields must not be exposed
            assert "greysheet_bid" not in deal, "Found 'greysheet_bid' in deal!"
            assert "greysheetBid" not in deal, "Found 'greysheetBid' in deal!"
            assert "net_margin" not in deal, "Found 'net_margin' in deal!"
            assert "gs_ask" not in deal, "Found 'gs_ask' in deal!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_refresh_deals_endpoint_contains_no_bid_fields():
    """Verify that /api/greysheet/deals/refresh returns deals with no bid/net_margin."""
    app.dependency_overrides[get_current_user] = lambda: {"uid": "test_user", "email": "test@numista.ai"}
    try:
        response = client.post("/api/greysheet/deals/refresh")
        assert response.status_code == 200

        # Now check GET /api/greysheet/deals after refresh
        get_resp = client.get("/api/greysheet/deals")
        assert get_resp.status_code == 200
        deals = get_resp.json().get("deals", [])
        assert len(deals) > 0
        for deal in deals:
            assert "cpg_retail" in deal
            assert "greysheet_bid" not in deal
            assert "net_margin" not in deal
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_invoice_cost_split_contains_no_bid_fields():
    """Verify that /api/preview_cost_split details omit bid values."""
    payload = {
        "cost_total": "$100.00",
        "coins": [
            {"year": "1881", "mint_mark": "S", "denomination": "Morgan Dollar"},
            {"year": "1921", "mint_mark": "", "denomination": "Morgan Dollar"}
        ]
    }
    response = client.post("/api/preview_cost_split", json=payload, headers={"Authorization": "Bearer mock-token"})
    assert response.status_code == 200
    data = response.json()
    assert "split_details" in data
    for detail in data["split_details"]:
        assert "greysheet_bid" not in detail
        assert "share_pct" in detail
        assert "cost" in detail


# --- DealSpotterService rev 2 tests (hotfix: CPG-only, no bid fallback, no fake $95) ---

from services.deal_spotter_service import DealSpotterService


def test_deal_spotter_bid_only_item_yields_no_deal():
    """An item with only greysheetBid and no CPG must yield no deal (not relabeled as cpg_retail)."""
    service = DealSpotterService()
    items = [{"Year": "1881", "mint": "S", "series": "Morgan Dollars", "greysheetBid": 120.0}]
    deals = service.match_wishlist_items(items)
    assert deals == [], f"Expected no deals for bid-only item, got: {deals}"
    # Confirm no cpg_retail == 120.0 sneaking through
    for deal in deals:
        assert deal.get("cpg_retail") != 120.0


def test_deal_spotter_empty_item_yields_no_deal():
    """An item with no pricing values at all must yield no deal (not a fake $95 deal)."""
    service = DealSpotterService()
    items = [{"Year": "1921", "mint": "", "series": "Morgan Dollars"}]
    deals = service.match_wishlist_items(items)
    assert deals == [], f"Expected no deals for empty item, got: {deals}"


def test_deal_spotter_real_cpg_item_yields_deal():
    """An item with a real cpgRetail value must still produce a deal (regression guard)."""
    service = DealSpotterService()
    items = [{"Year": "1881", "mint": "S", "series": "Morgan Dollars", "cpgRetail": 150.0}]
    deals = service.match_wishlist_items(items)
    assert len(deals) == 1, f"Expected 1 deal for CPG item, got: {deals}"
    assert deals[0]["cpg_retail"] == 150.0
    assert "greysheet_bid" not in deals[0]
    assert "net_margin" not in deals[0]


_FORBIDDEN_WHOLESALE_KEYS_LOWER = {
    "greyval",
    "greyaskval",
    "greyval1",
    "greyaskval1",
    "greyask",
    "greysheet_bid",
    "greysheetbid",
    "greysheet_ask",
    "greysheetask",
    "bid",
    "ask",
    "wholesale",
    "net_margin",
    "gs_ask",
}


def _assert_no_wholesale_recursive(obj, forbidden_values=()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            assert str(k).lower() not in _FORBIDDEN_WHOLESALE_KEYS_LOWER, f"Wholesale key leaked: {k!r}"
            _assert_no_wholesale_recursive(v, forbidden_values)
    elif isinstance(obj, list):
        for item in obj:
            _assert_no_wholesale_recursive(item, forbidden_values)
    elif forbidden_values and obj is not None:
        assert str(obj) not in forbidden_values, f"Wholesale value leaked: {obj!r}"


def test_pricing_endpoint_strips_greyval_and_all_wholesale():
    """P5: GET /api/greysheet/pricing/{gsid} returns retail-only fields and strips GreyVal/GreyAskVal."""
    resp = client.get("/api/greysheet/pricing/429")
    assert resp.status_code == 200
    data = resp.json()
    assert data["gsid"] == 429
    assert len(data["pricing"]) == 1
    row = data["pricing"][0]["PricingData"][0]
    assert row["CpgVal"] == "120.00"
    assert row["PcgsVal"] == "125.00"
    assert row["NgcVal"] == "120.00"
    assert row["BlueBookVal"] == "80.00"
    _assert_no_wholesale_recursive(data, forbidden_values=("95.00", "110.00"))


def test_sibling_greysheet_endpoints_never_leak_greyval(monkeypatch):
    """P5: Verify sibling Greysheet endpoints never return GreyVal/GreyAskVal or wholesale bid/ask."""
    monkeypatch.setattr(
        gs_module.GreysheetService,
        "resolve_gsid_hybrid",
        lambda self, coin_data, genai_client=None, primary_model="gemini-4-hydrogen": (429, "1881-S Morgan Dollar"),
    )
    prev_override = main.app.dependency_overrides.get(get_current_user)
    main.app.dependency_overrides[get_current_user] = lambda: {
        "email": "test_user@numista.ai",
        "uid": "test-uid",
    }
    try:
        r_resolve = client.post(
            "/api/greysheet/resolve",
            json={"year": "1881", "mint_mark": "S", "denomination": "Morgan Dollar", "program_series": "Morgan Dollars"},
        )
        assert r_resolve.status_code == 200
        _assert_no_wholesale_recursive(r_resolve.json())

        r_refresh = client.post(
            "/api/greysheet/refresh",
            json={"user_id": "test_user@numista.ai", "coin_id": "test-coin-123"},
        )
        assert r_refresh.status_code == 200
        _assert_no_wholesale_recursive(r_refresh.json(), forbidden_values=("95.00", "110.00"))

        r_deals = client.get("/api/greysheet/deals")
        assert r_deals.status_code == 200
        _assert_no_wholesale_recursive(r_deals.json())

        r_cac = client.get("/api/greysheet/cac")
        assert r_cac.status_code == 200
        _assert_no_wholesale_recursive(r_cac.json())
    finally:
        if prev_override is None:
            main.app.dependency_overrides.pop(get_current_user, None)
        else:
            main.app.dependency_overrides[get_current_user] = prev_override
