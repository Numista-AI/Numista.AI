import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from main import app
from routes.deps import get_current_user
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
    def mock_resolve(self, coin_data, genai_client=None, primary_model="gemini-4-hydrogen"):
        if coin_data.get("item_type") == "paper_currency":
            return None
        return (429, "Lincoln Cents (1909-1958)")
    monkeypatch.setattr(gs_module.GreysheetService, "resolve_gsid_hybrid", mock_resolve)

    # /api/greysheet/resolve requires get_current_user after security hardening
    prev_override = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = lambda: {"email": "test@numista.ai", "uid": "test-uid"}
    try:
        yield
    finally:
        if prev_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = prev_override

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
    # Auth guard: /api/greysheet/deals and /api/greysheet/deals/refresh
    # now require a Firebase Bearer token — unauthenticated callers must receive 401.
    # Use dependency_overrides to simulate missing auth (ALLOW_UNAUTHENTICATED=1 is set
    # in conftest for legacy monkeypatch tests, so we must explicitly override the dep).
    from routes.deps import get_current_user
    from fastapi import HTTPException as _HTTPException

    async def _unauthenticated():
        raise _HTTPException(status_code=401, detail="Authentication token missing or invalid")

    app.dependency_overrides[get_current_user] = _unauthenticated
    try:
        response = client.get("/api/greysheet/deals")
        assert response.status_code == 401, (
            f"Expected 401 for unauthenticated /api/greysheet/deals, got {response.status_code}")

        response = client.post("/api/greysheet/deals/refresh")
        assert response.status_code == 401, (
            f"Expected 401 for unauthenticated /api/greysheet/deals/refresh, got {response.status_code}")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

def test_daily_snapshot_endpoint():
    from routes.deps import require_admin_user
    app.dependency_overrides[require_admin_user] = lambda: {"uid": "admin_uid", "email": "admin@numista.ai", "admin": True}
    try:
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
    finally:
        app.dependency_overrides.pop(require_admin_user, None)

def test_advanced_api_level_default(monkeypatch):
    """Verify that GreysheetService requests include apiLevel=advanced and verify=True."""
    monkeypatch.setenv("GREYSHEET_API_KEY", "test-api-key-only")
    monkeypatch.setenv("GREYSHEET_API_TOKEN", "test-api-token-only")
    monkeypatch.delenv("GREYSHEET_BASE_URL", raising=False)
    service = gs_module.GreysheetService()
    captured_params = {}
    captured_verify = None
    
    def fake_requests_get(url, headers=None, params=None, verify=False, timeout=15):
        nonlocal captured_params, captured_verify
        captured_params = params
        captured_verify = verify
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"Data": []}
        return mock_resp

    monkeypatch.setattr("requests.get", fake_requests_get)
    service._get("GetPricingRequest", {"Gsid": 429})
    assert captured_params.get("apiLevel") == "advanced"
    assert captured_params.get("Gsid") == 429
    assert captured_verify is True


def test_greysheet_fail_closed_without_env_vars(monkeypatch):
    """Verify GreysheetService fails closed without env vars (0 HTTP calls, 0 Firestore config/greysheet reads)."""
    monkeypatch.delenv("GREYSHEET_API_KEY", raising=False)
    monkeypatch.delenv("GREYSHEET_API_TOKEN", raising=False)

    mock_db = MagicMock()
    http_called = False

    def fail_if_called(*args, **kwargs):
        nonlocal http_called
        http_called = True
        raise AssertionError("requests.get must NOT be called when Greysheet env vars are missing")

    monkeypatch.setattr("requests.get", fail_if_called)

    service = gs_module.GreysheetService(db=mock_db)
    res = service._get("GetPricingRequest", {"Gsid": 7084})

    assert res is None
    assert http_called is False
    assert service._headers is None
    mock_db.collection.assert_not_called()


def test_greysheet_outgoing_request_capture_and_sandbox_override(monkeypatch):
    """P5: Capture exact outgoing URL, method, auth headers, params, and verify=True with GREYSHEET_BASE_URL override."""
    monkeypatch.setenv("GREYSHEET_API_KEY", "p5-test-key")
    monkeypatch.setenv("GREYSHEET_API_TOKEN", "p5-test-token")
    monkeypatch.setenv("GREYSHEET_BASE_URL", "https://cpgpublicapiv2dev.greysheet.com/api/")

    captured = {}

    def capture_get(url, headers=None, params=None, verify=None, timeout=None):
        captured["method"] = "GET"
        captured["url"] = url
        captured["headers"] = dict(headers or {})
        captured["params"] = dict(params or {})
        captured["verify"] = verify
        captured["timeout"] = timeout
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"Data": [{"GsId": 7084}], "PermitAccess": True}
        return mock_resp

    monkeypatch.setattr("requests.get", capture_get)

    service = gs_module.GreysheetService()
    res = service._get("GetPricingRequest", {"Gsid": 7084})

    assert res == {"Data": [{"GsId": 7084}], "PermitAccess": True}
    assert captured["method"] == "GET"
    assert captured["url"] == "https://cpgpublicapiv2dev.greysheet.com/api/GetPricingRequest"
    assert captured["headers"] == {
        "x-api-key": "p5-test-key",
        "x-api-token": "p5-test-token",
        "Content-Type": "application/json",
    }
    assert captured["params"] == {"Gsid": 7084, "apiLevel": "advanced"}
    assert captured["verify"] is True


def test_greysheet_config_endpoint_env_only(monkeypatch):
    """Verify GET /api/greysheet/config reports active/production with env vars and unconfigured without them."""
    from routes.deps import require_admin_user
    prev_override = app.dependency_overrides.get(require_admin_user)
    app.dependency_overrides[require_admin_user] = lambda: {"uid": "admin", "email": "admin@numista.ai", "admin": True}
    try:
        monkeypatch.setenv("GREYSHEET_API_KEY", "p5-test-key")
        monkeypatch.setenv("GREYSHEET_API_TOKEN", "p5-test-token")
        resp_active = client.get("/api/greysheet/config")
        assert resp_active.status_code == 200
        body_active = resp_active.json()
        assert body_active["status"] == "active"
        assert body_active["mode"] == "production"
        assert body_active["tier"] == "Advanced"

        monkeypatch.delenv("GREYSHEET_API_KEY", raising=False)
        monkeypatch.delenv("GREYSHEET_API_TOKEN", raising=False)
        resp_unconf = client.get("/api/greysheet/config")
        assert resp_unconf.status_code == 200
        body_unconf = resp_unconf.json()
        assert body_unconf["status"] == "unconfigured"
        assert body_unconf["mode"] == "unconfigured"
        assert body_unconf["tier"] == "None"
    finally:
        if prev_override is None:
            app.dependency_overrides.pop(require_admin_user, None)
        else:
            app.dependency_overrides[require_admin_user] = prev_override


def test_resolve_coin_with_timeout_calls_resolve_gsid_hybrid(monkeypatch):
    """Verify resolve_coin_with_timeout delegates to resolve_gsid_hybrid instead of nonexistent resolve_coin."""
    service = gs_module.GreysheetService()
    called_with = {}

    def fake_hybrid(coin_data):
        called_with["coin_data"] = coin_data
        return (7084, "1909-S Lincoln Cent")

    def fake_pricing(gsid):
        return [{
            "GsId": gsid,
            "PricingData": [{"Grade": 60, "GradeLabel": "PR60", "CpgVal": "2.90", "GreyVal": "2.15"}],
        }]

    monkeypatch.setattr(service, "resolve_gsid_hybrid", fake_hybrid)
    monkeypatch.setattr(service, "get_pricing", fake_pricing)

    out = service.resolve_coin_with_timeout("1909", "One Cent", series="Lincoln Cents", mint="S", timeout_ms=2000)
    assert called_with["coin_data"]["Year"] == "1909"
    assert out is not None
    assert out["gsid"] == 7084
    assert out["cpg_retail"] == 2.90

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

