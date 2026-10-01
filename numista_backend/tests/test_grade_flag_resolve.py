import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_resolve_flag_admin_success(client):
    with patch('routes.deps.get_current_user') as mock_user, \
         patch('routes.deps.require_admin_user') as mock_admin, \
         patch('routes.grade_review_routes.db') as mock_db:
        
        mock_user.return_value = {'uid': 'admin1', 'email': 'admin@numista.ai'}
        mock_admin.return_value = {'uid': 'admin1', 'email': 'admin@numista.ai'}
        
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        response = client.post(
            "/api/admin/grade-flags/flag123/resolve",
            json={"decision": "accept_ai", "resolved_grade": "", "notes": ""}
        )
        assert response.status_code == 200

def test_resolve_flag_not_found(client):
    with patch('routes.deps.get_current_user') as mock_user, \
         patch('routes.deps.require_admin_user') as mock_admin, \
         patch('routes.grade_review_routes.db') as mock_db:
        
        mock_user.return_value = {'uid': 'admin1', 'email': 'admin@numista.ai'}
        mock_admin.return_value = {'uid': 'admin1', 'email': 'admin@numista.ai'}
        
        mock_doc = MagicMock()
        mock_doc.exists = False
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        response = client.post(
            "/api/admin/grade-flags/missing-flag/resolve",
            json={"decision": "accept_ai", "resolved_grade": "", "notes": ""}
        )
        assert response.status_code == 404

def test_resolve_flag_form_encoded(client):
    with patch('routes.deps.get_current_user') as mock_user, \
         patch('routes.deps.require_admin_user') as mock_admin:
        
        mock_user.return_value = {'uid': 'admin1', 'email': 'admin@numista.ai'}
        mock_admin.return_value = {'uid': 'admin1', 'email': 'admin@numista.ai'}
        
        response = client.post(
            "/api/admin/grade_flags/flag123/resolve",
            data={"decision": "accept_ai", "resolved_grade": "", "notes": ""}
        )
        assert response.status_code == 422

def test_resolve_flag_non_admin(client):
    with patch('routes.deps.get_current_user') as mock_user, \
         patch('routes.deps.require_admin_user') as mock_admin:
        
        from fastapi import HTTPException
        mock_user.return_value = {'uid': 'user1', 'email': 'user@numista.ai'}
        mock_admin.side_effect = HTTPException(status_code=403, detail="Admin required")
        
        response = client.post(
            "/api/admin/grade_flags/flag123/resolve",
            json={"decision": "accept_ai", "resolved_grade": "", "notes": ""}
        )
        assert response.status_code == 403
