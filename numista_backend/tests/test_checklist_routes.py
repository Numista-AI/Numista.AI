import pytest

def test_checklist_add_coins_unauthenticated_returns_401(client_prod_mode):
    """POST /api/checklist/add_coins without Bearer token must return 401."""
    resp = client_prod_mode.post('/api/checklist/add_coins', json={})
    assert resp.status_code == 401
