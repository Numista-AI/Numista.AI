"""
test_default_deny_auth.py
=========================
T1B REQ_031B: Default-deny auth middleware acceptance tests.

Verifies that every non-public API route returns HTTP 401 when called
without an Authorization header, and when called with an invalid/garbage token.
Also verifies that the PUBLIC_PATHS allowlist still responds (not 401),
CORS preflight passes, and every non-public route either has an auth dependency
or is in a reviewed handler-auth/non-guarded allowlist.

Tests use FastAPI's TestClient and patch firebase_auth.verify_id_token
so no real Firebase project is needed.
"""

import re
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
    mock_app = MagicMock()
    mock_fs = MagicMock()
    with patch("firebase_admin._apps", {"[DEFAULT]": mock_app, "default": mock_app}), \
         patch("firebase_admin.get_app", return_value=mock_app), \
         patch("firebase_admin.firestore.client", return_value=mock_fs), \
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


def test_all_routes_require_auth_no_token(client):
    """Walks all routes on app and asserts every non-public route returns 401 when called with no token."""
    import main as m

    tested = 0
    for route in m.app.routes:
        if not hasattr(route, "methods"):
            continue
        path = route.path
        if path in m._PUBLIC_PATHS or m._is_public(path) or path in ["/openapi.json", "/docs", "/redoc", "/docs/oauth2-redirect"]:
            continue

        methods = route.methods - {"OPTIONS", "HEAD"}
        if not methods:
            continue
        method = next(iter(methods))

        real_path = re.sub(r'\{[^}]+\}', 'test_param', path)
        resp = client.request(method, real_path)
        assert resp.status_code == 401, (
            f"Expected 401 for unauthenticated request to {method} {real_path} (from route {path}), got {resp.status_code}. "
            f"Body: {resp.text[:200]}"
        )
        tested += 1

    assert tested > 50, f"Expected to test > 50 non-public routes, only tested {tested}"


def test_all_routes_require_auth_garbage_token(client):
    """Walks all routes on app and asserts every non-public route returns 401 when called with Authorization: Bearer garbage."""
    import main as m

    tested = 0
    for route in m.app.routes:
        if not hasattr(route, "methods"):
            continue
        path = route.path
        if path in m._PUBLIC_PATHS or m._is_public(path) or path in ["/openapi.json", "/docs", "/redoc", "/docs/oauth2-redirect"]:
            continue

        methods = route.methods - {"OPTIONS", "HEAD"}
        if not methods:
            continue
        method = next(iter(methods))

        real_path = re.sub(r'\{[^}]+\}', 'test_param', path)
        resp = client.request(method, real_path, headers={"Authorization": "Bearer garbage_invalid_token_12345"})
        assert resp.status_code == 401, (
            f"Expected 401 for garbage token request to {method} {real_path} (from route {path}), got {resp.status_code}. "
            f"Body: {resp.text[:200]}"
        )
        tested += 1

    assert tested > 50, f"Expected to test > 50 non-public routes, only tested {tested}"


# Reviewed list of routes that do not have get_current_user / require_admin_user
# in their FastAPI dependency tree, but are protected by handler-auth (_authenticate_request / deep_dive)
# or are non-guarded routes protected exclusively by the default-deny outer gate.
REVIEWED_NON_GUARDED_ROUTES = {
    "/api/analyze/grade-coin",
    "/api/analyze_checklist",
    "/api/attorney/issue",
    "/api/attorney/revoke",
    "/api/attorney/snapshot",
    "/api/binder_scans/{user_email}",
    "/api/binder_scans/{user_email}/{binder_id}",
    "/api/coin_crop",
    "/api/collection/count",
    "/api/commit_group_photo",
    "/api/convert_heic",
    "/api/deep_dive",
    "/api/ebay/search",
    "/api/epn/normalize-search",
    "/api/estate/generate-appraisal-url",
    "/api/estimate_value_general",
    "/api/estimate_value_text",
    "/api/export/appraisal-pdf",
    "/api/greysheet/cac",
    "/api/greysheet/pricing/{gsid}",
    "/api/greysheet/quota",
    "/api/greysheet/refresh",
    "/api/greysheet/resolve",
    "/api/identify-world-item",
    "/api/identify_coin_photo",
    "/api/identify_group_photo",
    "/api/import/process",
    "/api/import/start",
    "/api/import/status/{session_id}",
    "/api/import/upload",
    "/api/ingestion/jobs",
    "/api/ingestion/status/{job_id}",
    "/api/mint_news",
    "/api/news/feed",
    "/api/nicknames",
    "/api/nicknames/stats",
    "/api/nicknames/submit",
    "/api/nicknames/{doc_id}/vote",
    "/api/portfolio/snapshot",
    "/api/preview_cost_split",
    "/api/process_invoice",
    "/api/receipts/{user_email}",
    "/api/receipts/{user_email}/{receipt_id}",
    "/api/receipts/{user_email}/{receipt_id}/stream",
    "/api/receipts/{user_email}/{receipt_id}/view_url",
    "/api/reference/db_update_check",
    "/api/reference/glossary",
    "/api/reference/grade/{grade_code}",
    "/api/reference/search",
    "/api/review/break_up_set",
    "/api/review/keep_set_as_is",
    "/api/stats/gaps",
    "/api/stripe/subscription-status",
    "/api/template",
    "/api/transfer/sell-direct",
    "/api/transfer/sold-items/{user_id}",
    "/api/transfer/undo-sale",
    "/api/v1/affiliate/search_url",
    "/api/v1/estate/attorney-report/{token}",
    "/api/v1/estate/attorney-report/{token}/pdf",
    "/api/v1/wishlist/reserve",
    "/api/variety/detect",
    "/api/wishlist/create-share",
    "/api/wishlist/deals/check",
    "/api/wishlist/deals/{user_email}",
    "/support/expire-grants",
    "/tickets/{ticket_id}/revoke",
}


def test_guarded_or_reviewed_routes():
    """Every non-public route must either have an auth dependency or be explicitly reviewed."""
    import main as m
    from routes.deps import get_current_user, require_admin_user

    def has_auth(dep):
        if dep.call in (get_current_user, require_admin_user):
            return True
        if hasattr(dep.call, "__name__") and dep.call.__name__ in (
            "get_current_user", "require_admin_user", "get_current_uid", "require_admin"
        ):
            return True
        for d in dep.dependencies:
            if has_auth(d):
                return True
        return False

    all_routes = []
    for r in m.app.routes:
        if type(r).__name__ == "_IncludedRouter" and hasattr(r, "original_router"):
            all_routes.extend(r.original_router.routes)
        else:
            all_routes.append(r)

    unaccounted_routes = []
    for route in all_routes:
        if not hasattr(route, "methods"):
            continue
        path = route.path
        if path in m._PUBLIC_PATHS or m._is_public(path) or path in ["/openapi.json", "/docs", "/redoc", "/docs/oauth2-redirect"]:
            continue

        is_guarded = hasattr(route, "dependant") and has_auth(route.dependant)
        if not is_guarded and path not in REVIEWED_NON_GUARDED_ROUTES:
            unaccounted_routes.append(path)

    assert not unaccounted_routes, (
        f"Found non-public routes with neither an auth dependency nor entry in REVIEWED_NON_GUARDED_ROUTES: "
        f"{unaccounted_routes}"
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
