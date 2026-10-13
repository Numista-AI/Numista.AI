"""
test_default_deny_auth.py
=========================
T1B REQ_031B: Default-deny auth middleware acceptance tests.

Verifies that every non-public API route returns HTTP 401 when called
without an Authorization header, and that the PUBLIC_PATHS allowlist
still responds (not 401).

Tests use FastAPI's TestClient and patch firebase_auth.verify_id_token
so no real Firebase project is needed.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    """Spin up the app with Firebase mocked out.

    We set K_SERVICE so the middleware treats this as a production environment,
    which disables the ALLOW_UNAUTHENTICATED=1 bypass set in conftest.py for
    legacy monkeypatch-based tests. This ensures 401 enforcement is actually tested.
    """
    import os as _os
    _old_k = _os.environ.get("K_SERVICE")
    _os.environ["K_SERVICE"] = "numista-backend-test-env"
    # Patch firebase_admin.initialize_app to avoid real credential loading
    with patch("firebase_admin._apps", {"default": MagicMock()}), \
         patch("firebase_admin.auth.verify_id_token", side_effect=Exception("no token")), \
         patch("firebase_admin.credentials.Certificate", MagicMock()), \
         patch("firebase_admin.initialize_app", MagicMock()), \
         patch("google.cloud.firestore.Client", MagicMock()), \
         patch("google.cloud.storage.Client", MagicMock()), \
         patch("google.genai.Client", MagicMock()), \
         patch("stripe.api_key", "sk_test_dummy"):
        import main as _main_module
        yield TestClient(_main_module.app, raise_server_exceptions=False)
    # Restore K_SERVICE
    if _old_k is None:
        _os.environ.pop("K_SERVICE", None)
    else:
        _os.environ["K_SERVICE"] = _old_k


@pytest.mark.parametrize("method,path,body", [
    # P0 routes that were completely unauthenticated before T1B
    ("POST", "/api/dedup_sweep", {"user_email": "test@test.com"}),
    ("POST", "/api/dedup_sweep/auto_clean", {"user_email": "test@test.com"}),
    ("POST", "/api/config/usmint-cookies", {"cookie_string": "test"}),
    ("POST", "/api/config/greysheet-credentials", {"api_key": "k", "api_token": "t"}),
    # Subaccount routes
    ("POST", "/api/v1/family/subaccounts", {"parent_email": "test@test.com", "child_alias": "kid",
                                             "relationship": "child", "permission_level": "read",
                                             "bequest_percentage": 0}),
    ("GET",  "/api/v1/family/subaccounts?parent_email=test@test.com", None),
    ("DELETE", "/api/v1/family/subaccounts/sub_123?parent_email=test@test.com", None),
    # Estate route
    ("POST", "/api/v1/estate/generate-attorney-link",
     {"owner_uid": "uid123", "valid_days": 7, "owner_email": "test@test.com"}),
    # Other authenticated routes (sample)
    ("POST", "/api/v1/rag/query", {"query": "test"}),
    ("GET",  "/api/collection/count?user_email=test@test.com", None),
    ("GET",  "/api/greysheet/deals", None),
])
def test_unauthenticated_request_returns_401(client, method, path, body):
    """No-token request to a protected route must return 401."""
    if method == "POST":
        resp = client.post(path, json=body)
    elif method == "GET":
        resp = client.get(path)
    elif method == "DELETE":
        resp = client.delete(path)
    else:
        pytest.skip(f"Method {method} not handled in this test")

    assert resp.status_code == 401, (
        f"{method} {path} returned {resp.status_code} (expected 401). "
        f"Body: {resp.text[:200]}"
    )


@pytest.mark.parametrize("path", [
    "/api/coin_search?q=morgan",
    "/api/reference/stats",
    "/api/mint-releases/upcoming",
    "/api/mint-releases/all",
    "/api/provenance/verify/fake_token",
])
def test_public_paths_not_blocked(client, path):
    """Public allowlist routes must NOT return 401 (they may return 200, 404, 422, etc.)."""
    resp = client.get(path)
    assert resp.status_code != 401, (
        f"GET {path} returned 401 — it should be on the public allowlist. "
        f"Body: {resp.text[:200]}"
    )


def test_options_preflight_not_blocked(client):
    """OPTIONS requests (CORS preflight) must never return 401."""
    resp = client.options("/api/v1/rag/query")
    assert resp.status_code != 401, (
        f"OPTIONS returned 401 — CORS preflight is broken. Body: {resp.text[:200]}"
    )
