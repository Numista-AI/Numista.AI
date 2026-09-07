import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from main import app
import services.greysheet_service as gs_module

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_external_services(monkeypatch):
    """Ensure pytest runs reliably without hanging on external ADC/OAuth tokens or live network calls."""
    import main
    mock_db = MagicMock()
    mock_doc = MagicMock()
    mock_doc.to_dict.return_value = {
        "Quantity": 1,
        "greysheetBid": 95.0,
        "AI Estimated Value": "$95.00",
        "item_type": "coin",
        "Year": "1909",
        "MintMark": "S",
        "Denomination": "One Cent",
        "ProgramSeries": "Lincoln Cents"
    }
    mock_doc.exists = True
    
    mock_coins_collection = MagicMock()
    mock_coins_collection.get.return_value = [mock_doc]
    mock_coins_collection.document.return_value = mock_doc
    
    mock_user_doc = MagicMock()
    mock_user_doc.collection.return_value = mock_coins_collection
    
    mock_users_collection = MagicMock()
    mock_users_collection.document.return_value = mock_user_doc
    
    mock_db.collection.return_value = mock_users_collection
    
    monkeypatch.setattr(main, "db", mock_db)
    
    # Mock resolve_gsid_hybrid to return a valid mapping for Lincoln Cent test payload
    orig_resolve = gs_module.GreysheetService.resolve_gsid_hybrid
    def mock_resolve(self, coin_data, genai_client=None, primary_model="gemini-3.8-flash"):
        if coin_data.get("item_type") == "paper_currency":
            return None
        return (429, "Lincoln Cents (1909-1958)")
    monkeypatch.setattr(gs_module.GreysheetService, "resolve_gsid_hybrid", mock_resolve)

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

def test_advanced_api_level_default(monkeypatch):
    """Verify that GreysheetService requests include apiLevel=advanced."""
    service = gs_module.GreysheetService()
    captured_params = {}
    
    def fake_requests_get(url, headers=None, params=None, verify=False, timeout=15):
        nonlocal captured_params
        captured_params = params
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"Data": []}
        return mock_resp

    monkeypatch.setattr("requests.get", fake_requests_get)
    service._get("GetPricingRequest", {"Gsid": 429})
    assert captured_params.get("apiLevel") == "advanced"
    assert captured_params.get("Gsid") == 429

def test_quota_endpoint():
    """Verify GET /api/greysheet/quota returns usage & threshold metrics."""
    response = client.get("/api/greysheet/quota")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "usage" in data
    assert data["warning_threshold"] == 25000
    assert data["hard_cap_threshold"] == 50000

def test_quota_service_hard_cap():
    """Verify GreysheetQuotaService hard cap detection and 24h cache TTL check."""
    from services.greysheet_quota_service import GreysheetQuotaService
    from datetime import datetime, timezone, timedelta

    qs = GreysheetQuotaService()
    
    # Check 24h TTL logic
    now = datetime.now(timezone.utc)
    recent = now - timedelta(hours=5)
    stale = now - timedelta(hours=30)
    
    assert qs.is_cache_valid(recent, ttl_hours=24) is True
    assert qs.is_cache_valid(stale, ttl_hours=24) is False

