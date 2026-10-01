"""
test_grade_flag_resolve.py
---------------------------
Tests for MUST 3 (REQ_027F): admin grade-flag resolve endpoint.

Acceptance:
  - Admin token + JSON {decision, resolved_grade, notes} → 200 (flag exists) or 404 (missing)
  - Form-encoded body → 422 (route expects JSON Pydantic body)
  - Non-admin token → 403
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient

from main import app
from routes.deps import get_current_user, require_admin_user


def _admin_user():
    async def _dep():
        return {'uid': 'adminUID', 'email': 'admin@numista.ai', 'admin': True}
    return _dep


def _non_admin_user():
    async def _dep():
        return {'uid': 'userUID', 'email': 'user@numista.ai'}
    return _dep


def _require_admin_ok():
    async def _dep():
        return {'uid': 'adminUID', 'email': 'admin@numista.ai', 'admin': True}
    return _dep


def _require_admin_forbidden():
    async def _dep():
        raise HTTPException(status_code=403, detail='Admin required')
    return _dep


def _require_admin_unauthed():
    async def _dep():
        raise HTTPException(status_code=401, detail='Unauthorized')
    return _dep


RESOLVE_URL = '/api/admin/grade_flags/flag123/resolve'
RESOLVE_MISSING_URL = '/api/admin/grade_flags/missing-flag/resolve'
VALID_JSON = {'decision': 'accept_ai', 'resolved_grade': '', 'notes': 'Test note'}


def test_resolve_flag_admin_success():
    """Admin + JSON body + existing flag → 200."""
    app.dependency_overrides[get_current_user] = _admin_user()
    app.dependency_overrides[require_admin_user] = _require_admin_ok()
    try:
        with patch('routes.grade_review_routes.db') as mock_db:
            mock_doc = MagicMock()
            mock_doc.exists = True
            mock_doc.to_dict.return_value = {
                'flag_id': 'flag123',
                'coin_id': 'coin_abc',
                'user_email': 'user@numista.ai',
                'ai_grade': 'MS65',
                'user_grade': 'MS64',
                'status': 'open',
            }
            mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

            client = TestClient(app)
            response = client.post(RESOLVE_URL, json=VALID_JSON)
            assert response.status_code == 200, \
                f"Expected 200, got {response.status_code}: {response.text}"
    finally:
        app.dependency_overrides.clear()


def test_resolve_flag_not_found():
    """Admin + JSON body + non-existent flag → 404."""
    app.dependency_overrides[get_current_user] = _admin_user()
    app.dependency_overrides[require_admin_user] = _require_admin_ok()
    try:
        with patch('routes.grade_review_routes.db') as mock_db:
            mock_doc = MagicMock()
            mock_doc.exists = False
            mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

            client = TestClient(app)
            response = client.post(RESOLVE_MISSING_URL, json=VALID_JSON)
            assert response.status_code == 404, \
                f"Expected 404, got {response.status_code}: {response.text}"
    finally:
        app.dependency_overrides.clear()


def test_resolve_flag_form_encoded():
    """Form-encoded body (not JSON) → 422 Unprocessable Entity.
    The route uses AdminResolveFlagRequest (Pydantic JSON body) so form data is rejected.
    """
    app.dependency_overrides[get_current_user] = _admin_user()
    app.dependency_overrides[require_admin_user] = _require_admin_ok()
    try:
        client = TestClient(app)
        response = client.post(
            RESOLVE_URL,
            data={'decision': 'accept_ai', 'resolved_grade': '', 'notes': ''},
        )
        assert response.status_code == 422, \
            f"Expected 422 for form-encoded body, got {response.status_code}: {response.text}"
    finally:
        app.dependency_overrides.clear()


def test_resolve_flag_non_admin():
    """Valid token but no admin claim → 403."""
    app.dependency_overrides[get_current_user] = _non_admin_user()
    app.dependency_overrides[require_admin_user] = _require_admin_forbidden()
    try:
        client = TestClient(app)
        response = client.post(RESOLVE_URL, json=VALID_JSON)
        assert response.status_code == 403, \
            f"Expected 403 for non-admin, got {response.status_code}: {response.text}"
    finally:
        app.dependency_overrides.clear()


def test_resolve_flag_no_token():
    """No token at all → 401."""
    app.dependency_overrides[get_current_user] = _require_admin_unauthed()
    app.dependency_overrides[require_admin_user] = _require_admin_unauthed()
    try:
        client = TestClient(app)
        response = client.post(RESOLVE_URL, json=VALID_JSON)
        assert response.status_code == 401, \
            f"Expected 401 for unauthenticated request, got {response.status_code}: {response.text}"
    finally:
        app.dependency_overrides.clear()
