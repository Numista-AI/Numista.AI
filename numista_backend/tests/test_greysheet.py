import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_resolve_greysheet_raw():
    # Test resolving Lincoln Cent VDB
    payload = {
        "year": "1909",
        "mint_mark": "S",
        "denomination": "One Cent",
        "program_series": "Lincoln Cents",
        "variety": "V.D.B."
    }
    response = client.post("/api/greysheet/resolve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["success", "not_resolved"]
    if data["status"] == "success":
        assert "gsid" in data

def test_item_type_guardrails():
    # Test that non-coin items are bypassed by the guardrails
    payload = {
        "year": "1923",
        "denomination": "One Dollar",
        "item_type": "paper_currency",
        "program_series": "Silver Certificates"
    }
    response = client.post("/api/greysheet/resolve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "not_resolved"

def test_pricing_endpoint():
    # Test fetching pricing details for GSID 429
    response = client.get("/api/greysheet/pricing/429")
    assert response.status_code == 200
    data = response.json()
    assert "pricing" in data
    assert isinstance(data["pricing"], list)

def test_deals_endpoints():
    # Test GET /api/greysheet/deals
    response = client.get("/api/greysheet/deals")
    assert response.status_code == 200
    data = response.json()
    assert "deals" in data
    assert len(data["deals"]) > 0
    assert "margin_percent" in data["deals"][0]

    # Test POST /api/greysheet/deals/refresh
    response = client.post("/api/greysheet/deals/refresh")
    assert response.status_code == 200
    refresh_data = response.json()
    assert refresh_data["status"] == "success"
    assert refresh_data["count"] > 0

def test_daily_snapshot_endpoint():
    # Test POST /api/portfolio/snapshot/daily
    # We will trigger snapshot for a test user
    payload = {"user_id": "test_user_snapshot@numista.ai"}
    response = client.post("/api/portfolio/snapshot/daily", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "snapshot" in data
    assert "totalValue" in data["snapshot"]
    assert "categories" in data["snapshot"]
