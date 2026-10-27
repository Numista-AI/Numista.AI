"""
test_cors_public_paths.py — T1C HOTFIX: CORS + public path regression tests.

Tests:
1. /api/spot_prices returns 200 without auth (P0 fix — was missing from _PUBLIC_PATHS)
2. OPTIONS preflight on a protected route returns 200 (not 401)
3. OPTIONS preflight has CORS headers
4. Protected route still requires auth (regression)
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app

client = TestClient(app, raise_server_exceptions=False)


# ── 1. /api/spot_prices is public (P0 fix) ────────────────────────────────────
def test_spot_prices_no_auth_returns_200():
    """P0 fix: /api/spot_prices must be on _PUBLIC_PATHS — returns 200 without auth.
    Root cause: home_dashboard.dart:249 calls http.get('/api/spot_prices') with no
    auth header. Default-deny middleware was returning 401 before the fix.
    Fix: main.py _PUBLIC_PATHS added '/api/spot_prices'.
    """
    resp = client.get("/api/spot_prices")
    assert resp.status_code == 200, (
        f"/api/spot_prices returned {resp.status_code} — must be public (no auth required). "
        "Added to _PUBLIC_PATHS at main.py:~152"
    )


def test_spot_prices_returns_expected_keys():
    """Spot prices response must include Gold, Silver, Platinum, Palladium."""
    resp = client.get("/api/spot_prices")
    assert resp.status_code == 200
    data = resp.json()
    for key in ("Gold", "Silver", "Platinum", "Palladium"):
        assert key in data, f"Missing key '{key}' in /api/spot_prices response"


# ── 2. OPTIONS preflight always passes ────────────────────────────────────────
def test_options_preflight_protected_route_returns_200():
    """OPTIONS preflight on a protected route must return 200, not 401.
    main.py:179 — 'if request.method == "OPTIONS": return await call_next(request)'
    """
    resp = client.options(
        "/api/collection_inventory",
        headers={
            "Origin": "https://numista.ai",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        },
    )
    assert resp.status_code == 200, (
        f"OPTIONS preflight returned {resp.status_code} — must be 200. "
        "main.py:179 must pass OPTIONS before auth check."
    )


def test_options_preflight_has_cors_headers():
    """OPTIONS response must include Access-Control-Allow-Origin."""
    resp = client.options(
        "/api/collection_inventory",
        headers={
            "Origin": "https://numista.ai",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        },
    )
    cors = resp.headers.get("access-control-allow-origin", "")
    assert cors, (
        "OPTIONS response missing Access-Control-Allow-Origin header. "
        "CORSMiddleware (main.py:60-66) must run."
    )


def test_options_preflight_spot_prices_returns_200():
    """OPTIONS on /api/spot_prices must succeed."""
    resp = client.options(
        "/api/spot_prices",
        headers={"Origin": "https://numista.ai", "Access-Control-Request-Method": "GET"},
    )
    assert resp.status_code == 200


# ── 3. Default-deny: verify _PUBLIC_PATHS does NOT include protected routes ───
def test_spot_prices_in_public_paths():
    """Verify /api/spot_prices is in _PUBLIC_PATHS (main.py:129-155).
    This directly tests the fix rather than relying on middleware side effects
    that TestClient bypasses via dependency_overrides.
    """
    from main import _PUBLIC_PATHS
    assert "/api/spot_prices" in _PUBLIC_PATHS, (
        "/api/spot_prices must be in _PUBLIC_PATHS (main.py:~152). "
        "Without it, default-deny middleware returns 401 on the home dashboard."
    )


def test_protected_routes_not_in_public_paths():
    """Regression: sensitive routes must NOT be in _PUBLIC_PATHS."""
    from main import _PUBLIC_PATHS
    protected = [
        "/api/collection_inventory",
        "/api/coins",
        "/api/deep_dive",
        "/api/morgan/confirm",
        "/api/programs",
        "/api/admin/grade_flags",
    ]
    for route in protected:
        assert route not in _PUBLIC_PATHS, (
            f"Protected route '{route}' is incorrectly in _PUBLIC_PATHS — "
            "it must require auth"
        )


# ── 4. P7 V8 CORS preview regex & negative origin tests ──────────────────────
def test_cors_preview_origin_allowed(client_prod_mode):
    """Preview channels get allow-origin header."""
    preview_origin = "https://numista-vault--p7-v7-gate-o3flke1i.web.app"
    resp = client_prod_mode.options(
        "/api/spot_prices",
        headers={
            "Origin": preview_origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp.status_code in (200, 204)
    assert resp.headers.get("access-control-allow-origin") == preview_origin


def test_cors_preview_channel_get_spot_prices(client_prod_mode):
    """GET /api/spot_prices from preview channel returns 200 with matching CORS origin."""
    preview_origin = "https://numista-vault--p7-v7-gate-o3flke1i.web.app"
    resp = client_prod_mode.get(
        "/api/spot_prices",
        headers={"Origin": preview_origin},
    )
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == preview_origin


@pytest.mark.parametrize("evil_origin", [
    "https://numista-vault--x.web.app.evil.com",
    "https://evil-numista-vault--x.web.app",
    "http://numista-vault--x.web.app",
    "https://other-site--x.web.app",
])
def test_cors_evil_origins_rejected(client_prod_mode, evil_origin):
    """Evil origins mimicking preview pattern must not get allow-origin."""
    from main import _is_allowed_origin
    assert not _is_allowed_origin(evil_origin), f"Evil origin was allowed: {evil_origin}"

    resp = client_prod_mode.options(
        "/api/spot_prices",
        headers={
            "Origin": evil_origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    allow_origin = resp.headers.get("access-control-allow-origin")
    assert allow_origin != evil_origin, f"Disallowed origin {evil_origin} received allow-origin header"


# ── 5. Safety: Checklist add_coins default-deny 401 test ─────────────────────
def test_checklist_add_coins_unauthenticated_returns_401(client_prod_mode):
    """POST /api/checklist/add_coins without Bearer token must return 401."""
    resp = client_prod_mode.post(
        "/api/checklist/add_coins",
        json={
            "idempotency_key": "test-key-123",
            "program_id": "morgan_dollars",
            "program_name": "Morgan Dollars",
            "user_email": "anonymous@test.com",
            "slots": [],
        },
    )
    assert resp.status_code == 401, (
        f"Expected 401 for unauthenticated checklist add_coins, got {resp.status_code}"
    )



