"""
numista_backend/tests/test_cors_auth.py
---------------------------------------
P7 V8.16 security & CORS regression tests:
1. 401 response carries CORS headers for allowed origins (CORS outermost)
2. Import process route returns 403 on email mismatch (import ownership)
3. Import start route returns 403 on email mismatch (import ownership)
4. Preview origin matching regex also gets CORS headers on 401
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from routes.deps import get_current_user


@pytest.fixture
def auth_client():
    app.dependency_overrides[get_current_user] = lambda: {
        "uid": "test_user_uid",
        "email": "user@example.com",
        "admin": False,
    }
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


# test (a): 401 carries CORS headers for an allowed origin
def test_401_response_carries_cors_headers(client_prod_mode):
    resp = client_prod_mode.get(
        '/api/collection',
        headers={'Origin': 'https://numista-vault.web.app'}
    )
    assert resp.status_code == 401
    assert 'access-control-allow-origin' in resp.headers
    assert resp.headers['access-control-allow-origin'] == 'https://numista-vault.web.app'


def test_401_response_carries_cors_headers_preview_origin(client_prod_mode):
    preview_origin = 'https://numista-vault--p7gate.web.app'
    resp = client_prod_mode.get(
        '/api/collection',
        headers={'Origin': preview_origin}
    )
    assert resp.status_code == 401
    assert 'access-control-allow-origin' in resp.headers
    assert resp.headers['access-control-allow-origin'] == preview_origin


# test (b): import process route returns 403 on email mismatch
def test_import_process_email_mismatch_returns_403(auth_client):
    resp = auth_client.post('/api/import/process', json={'user_email': 'other@example.com', 'import_id': 'fake'})
    assert resp.status_code == 403


def test_import_start_email_mismatch_returns_403(auth_client):
    resp = auth_client.post(
        '/api/import/start',
        json={
            'user_email': 'other@example.com',
            'session_id': 'sess_123',
            'file_manifest': [{'name': 'inv.pdf', 'size': 100, 'mime': 'application/pdf'}],
        }
    )
    assert resp.status_code == 403


def test_import_littleton_sync_email_mismatch_returns_403(auth_client):
    resp = auth_client.post(
        '/api/import/littleton_sync',
        json={
            'user_email': 'other@example.com',
            'orders': [],
        }
    )
    assert resp.status_code == 403

