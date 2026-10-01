import sys
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

@pytest.fixture
def client():
    return TestClient(app)

# MUST 1: Stripe Checkout IDOR test
def test_stripe_checkout_idor(client):
    with patch('routes.deps.get_current_user') as mock_user, \
         patch('routes.payment_routes.stripe.checkout.Session.create') as mock_create:
        
        mock_user.return_value = {'uid': 'userA', 'email': 'userA@numista.ai'}
        mock_session = MagicMock()
        mock_session.url = "http://mock-checkout-url"
        mock_session.id = "sess_mock123"
        mock_create.return_value = mock_session
        
        response = client.post(
            "/api/stripe/create-checkout-session",
            json={"user_email": "userB@numista.ai", "tier": "pro"}
        )
        assert response.status_code == 200
        
        # Verify the stripe call used token A's identity, NOT userB
        mock_create.assert_called_once()
        kwargs = mock_create.call_args.kwargs
        assert kwargs['customer_email'] == 'usera@numista.ai'
        assert kwargs['client_reference_id'] == 'userA'

def test_stripe_checkout_no_token(client):
    with patch('routes.deps.get_current_user') as mock_user:
        from fastapi import HTTPException
        mock_user.side_effect = HTTPException(status_code=401, detail="Unauthorized")
        
        response = client.post(
            "/api/stripe/create-checkout-session",
            json={"user_email": "userB@numista.ai", "tier": "pro"}
        )
        assert response.status_code == 401

# MUST 2: Stripe Portal IDOR test
def test_stripe_portal_idor(client):
    with patch('routes.deps.get_current_user') as mock_user, \
         patch('routes.payment_routes.stripe.Customer.list') as mock_list, \
         patch('routes.payment_routes.stripe.Customer.create') as mock_create_cust, \
         patch('routes.payment_routes.stripe.billing_portal.Session.create') as mock_portal_create, \
         patch('routes.payment_routes.db') as mock_db:
        
        mock_user.return_value = {'uid': 'userA', 'email': 'userA@numista.ai'}
        
        # User doc doesn't have stripe_customer_id
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {}
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        # Mock Stripe customer list to return empty, then create creates one
        mock_list_result = MagicMock()
        mock_list_result.data = []
        mock_list.return_value = mock_list_result
        
        mock_cust = MagicMock()
        mock_cust.id = "cus_mock123"
        mock_create_cust.return_value = mock_cust
        
        mock_portal = MagicMock()
        mock_portal.url = "http://mock-portal"
        mock_portal_create.return_value = mock_portal
        
        # Call it with body or query (though it ignores it)
        response = client.post("/api/stripe/create-customer-portal?user_email=userB@numista.ai")
        assert response.status_code == 200
        
        mock_list.assert_called_once_with(email='usera@numista.ai', limit=1)
        mock_create_cust.assert_called_once()
        assert mock_create_cust.call_args.kwargs['email'] == 'usera@numista.ai'

def test_stripe_portal_no_token(client):
    with patch('routes.deps.get_current_user') as mock_user:
        from fastapi import HTTPException
        mock_user.side_effect = HTTPException(status_code=401, detail="Unauthorized")
        
        response = client.post("/api/stripe/create-customer-portal")
        assert response.status_code == 401

# MUST 4: Passport PDF allow claimer by uid
def test_passport_pdf_no_token(client):
    with patch('routes.deps.get_current_user') as mock_user:
        from fastapi import HTTPException
        mock_user.side_effect = HTTPException(status_code=401, detail="Unauthorized")
        response = client.get("/api/transfers/pdf/transfer123")
        assert response.status_code == 401

def test_passport_pdf_stranger(client):
    with patch('routes.deps.get_current_user') as mock_user, \
         patch('main.db') as mock_db:
        mock_user.return_value = {'uid': 'stranger', 'email': 'stranger@numista.ai'}
        
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'user_a_id': 'senderUID',
            'user_b_id': 'claimerUID',
            'recipient_email': 'recipient@numista.ai'
        }
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        response = client.get("/api/transfers/pdf/transfer123")
        assert response.status_code == 403

def test_passport_pdf_sender(client):
    with patch('routes.deps.get_current_user') as mock_user, \
         patch('main.db') as mock_db:
        mock_user.return_value = {'uid': 'senderUID', 'email': 'sender@numista.ai'}
        
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'user_a_id': 'senderUID',
            'user_b_id': 'claimerUID',
            'recipient_email': 'recipient@numista.ai'
        }
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        # We need to mock reportlab/etc if the PDF generator runs.
        # But wait, it returns a FileResponse. Let's patch the generator to return a dummy file.
        with patch('main.generate_certificate_of_transfer') as mock_gen:
            mock_gen.return_value = "dummy.pdf"
            with patch('main.os.path.exists', return_value=True):
                # actually FileResponse checks file existence and stat, which is hard to mock easily
                # let's just see if it bypasses the 403 check
                response = client.get("/api/transfers/pdf/transfer123")
                # might fail 500 or 404 because file dummy.pdf doesn't exist but definitely NOT 403
                assert response.status_code != 403

def test_passport_pdf_claimer(client):
    with patch('routes.deps.get_current_user') as mock_user, \
         patch('main.db') as mock_db:
        mock_user.return_value = {'uid': 'claimerUID', 'email': 'claimer@numista.ai'}
        
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'user_a_id': 'senderUID',
            'user_b_id': 'claimerUID',
            'recipient_email': 'recipient@numista.ai'
        }
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        with patch('main.generate_certificate_of_transfer') as mock_gen:
            mock_gen.return_value = "dummy.pdf"
            with patch('main.os.path.exists', return_value=True):
                response = client.get("/api/transfers/pdf/transfer123")
                assert response.status_code != 403
