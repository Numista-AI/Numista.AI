import pytest
import time
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_list_ingestion_jobs():
    response = client.get("/api/ingestion/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert len(data["jobs"]) >= 1

def test_start_parallel_batch_and_poll_status():
    payload = {
        "user_email": "test_parallel@numista.ai",
        "concurrency_limit": 2,
        "items": [
            {"name": "1909-S VDB Lincoln Cent", "year": "1909", "mint": "S", "denomination": "Cent"},
            {"name": "1881-S Morgan Dollar", "year": "1881", "mint": "S", "denomination": "Dollar"}
        ]
    }
    response = client.post("/api/ingestion/batch_async", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "started"
    assert "job_id" in data
    
    job_id = data["job_id"]
    
    # Poll status endpoint
    status_res = client.get(f"/api/ingestion/status/{job_id}")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["job_id"] == job_id
    assert status_data["total_items"] == 2
