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

def test_pricing_endpoint():
    # Test fetching pricing details for a dummy/sample GSID
    # Since GSID 429 is a common Lincoln Cent, let's query it
    response = client.get("/api/greysheet/pricing/429")
    assert response.status_code == 200
    data = response.json()
    assert "pricing" in data
    # It should have matching grades or default list
    assert isinstance(data["pricing"], list)
