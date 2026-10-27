import pytest
from fastapi.testclient import TestClient
from main import app
from services.deal_spotter_service import DealSpotterService

client = TestClient(app)

def test_deal_spotter_service_arbitrage_math():
    service = DealSpotterService()
    # CPG retail: $100. Listing price: $70. Shipping: $5. Total cost = $75. Net margin = $25. Margin % = 33.3%
    result = service.calculate_arbitrage(listing_price=70.0, shipping=5.0, benchmark_val=100.0)
    assert result["total_cost"] == 75.0
    assert result["net_margin"] == 25.0
    assert result["margin_percent"] == 33.3
    assert result["is_arbitrage_deal"] is True

def test_deal_spotter_wishlist_matching():
    service = DealSpotterService()
    # Must use cpgRetail — bid-only items are now skipped
    items = [
        {"Year": "1909", "MintMark": "S", "ProgramSeries": "Lincoln Cents", "cpgRetail": 150.0}
    ]
    deals = service.match_wishlist_items(items)
    assert len(deals) == 1
    assert "deal_badge" in deals[0]
    assert deals[0]["cpg_retail"] == 150.0
    assert "greysheet_bid" not in deals[0]

def test_wishlist_deals_endpoints():
    res1 = client.get("/api/wishlist/deals/test@numista.ai")
    assert res1.status_code == 200
    data1 = res1.json()
    assert "deals" in data1
    # The mock fixture doc has cpgRetail: 120.0 — deals endpoint should return >= 1
    assert data1["count"] >= 1

    payload = {
        "user_email": "test@numista.ai",
        "wishlist_items": [
            # Must have cpg_retail — bid-only items yield 0 deals now
            {"year": "1881", "mint": "S", "series": "Morgan Dollars", "cpg_retail": 120.0}
        ]
    }
    res2 = client.post("/api/wishlist/deals/check", json=payload)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["status"] == "success"
    assert data2["count"] == 1
