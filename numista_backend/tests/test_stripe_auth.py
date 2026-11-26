"""
test_stripe_auth.py
--------------------
Tests for:
  MUST 1  — Stripe Checkout IDOR fix: checkout session uses token identity, not request body
  MUST 2  — Stripe Portal IDOR test: portal uses token identity, no user_email query accepted
  MUST 4  — passport-pdf allow claimer by uid (in addition to sender and recipient email)

Uses app.dependency_overrides (the correct FastAPI pattern) to inject fake auth.
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from unittest.mock import patch, MagicMock
from main import app
from routes.deps import get_current_user
from fastapi import HTTPException

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from routes.deps import get_current_user

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _make_user(uid, email):
    async def _fake():
        return {'uid': uid, 'email': email}
    return _fake

def _no_token():
    async def _raise():
        raise HTTPException(status_code=401, detail='Unauthorized')
    return _raise


# ─── MUST 1: Stripe Checkout IDOR ─────────────────────────────────────────────

def test_stripe_checkout_idor():
    """Token for user A with body user_email=B → session uses A's identity."""
    app.dependency_overrides[get_current_user] = _make_user('uidA', 'userA@numista.ai')
    try:
        with patch('routes.payment_routes.stripe.api_key', 'sk_test_dummy'), \
             patch('routes.payment_routes.load_stripe_keys', return_value={'secret_key': 'sk_test_dummy'}), \
             patch('routes.payment_routes.stripe.checkout.Session.create') as mock_create:
            mock_session = MagicMock()
            mock_session.url = 'https://checkout.stripe.com/pay/mock'
            mock_session.id = 'sess_mock123'
            mock_create.return_value = mock_session

            client = TestClient(app)
            response = client.post(
                '/api/stripe/create-checkout-session',
                json={'user_email': 'userB@numista.ai', 'tier': 'pro'},
            )
            assert response.status_code == 200, response.text

            mock_create.assert_called_once()
            kwargs = mock_create.call_args.kwargs
            # Must use token email (userA), NOT body email (userB)
            assert kwargs['customer_email'] == 'usera@numista.ai', \
                f"Expected usera@numista.ai, got {kwargs['customer_email']}"
            assert kwargs['client_reference_id'] == 'uidA', \
                f"Expected uidA, got {kwargs['client_reference_id']}"
    finally:
        app.dependency_overrides.clear()


def test_stripe_checkout_no_token():
    """No token → 401."""
    app.dependency_overrides[get_current_user] = _no_token()
    try:
        client = TestClient(app)
        response = client.post(
            '/api/stripe/create-checkout-session',
            json={'user_email': 'someone@numista.ai', 'tier': 'pro'},
        )
        assert response.status_code == 401, response.text
    finally:
        app.dependency_overrides.clear()


# ─── MUST 2: Stripe Portal IDOR ───────────────────────────────────────────────

def test_stripe_portal_idor():
    """Token A + query user_email=B with no entitlements -> 404 no_billing_account, no Stripe calls."""
    app.dependency_overrides[get_current_user] = _make_user('uidA', 'userA@numista.ai')
    try:
        with patch('routes.payment_routes.stripe.api_key', 'sk_test_dummy'), \
             patch('routes.payment_routes.load_stripe_keys', return_value={'secret_key': 'sk_test_dummy'}), \
             patch('routes.payment_routes.stripe.Customer.list') as mock_list, \
             patch('routes.payment_routes.stripe.Customer.create') as mock_create_cust, \
             patch('routes.payment_routes.stripe.billing_portal.Session.create') as mock_portal, \
             patch('routes.payment_routes.db') as mock_db:

            mock_doc = MagicMock()
            mock_doc.exists = False
            mock_doc.to_dict.return_value = {}
            mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

            client = TestClient(app)
            response = client.post(
                '/api/stripe/create-customer-portal?user_email=userB@numista.ai'
            )
            assert response.status_code == 404, response.text
            assert response.json()['detail']['error'] == 'no_billing_account'
            mock_list.assert_not_called()
            mock_create_cust.assert_not_called()
            mock_portal.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_stripe_portal_idor_verified_map_uses_own_cus():
    """Token A + query user_email=B with A's verified map -> portal called with A's cus_ and return_url."""
    app.dependency_overrides[get_current_user] = _make_user('uidA', 'userA@numista.ai')
    try:
        with patch('routes.payment_routes.stripe.api_key', 'sk_test_dummy'), \
             patch('routes.payment_routes.load_stripe_keys', return_value={'secret_key': 'sk_test_dummy'}), \
             patch('routes.payment_routes.stripe.Customer.list') as mock_list, \
             patch('routes.payment_routes.stripe.Customer.create') as mock_create_cust, \
             patch('routes.payment_routes.stripe.billing_portal.Session.create') as mock_portal, \
             patch('routes.payment_routes.db') as mock_db:

            ent_doc = MagicMock()
            ent_doc.exists = True
            ent_doc.to_dict.return_value = {'stripe_customer_id': 'cus_A'}
            cust_doc = MagicMock()
            cust_doc.exists = True
            cust_doc.to_dict.return_value = {'uid': 'uidA'}

            def _col(name):
                c = MagicMock()
                if name == 'entitlements':
                    c.document.return_value.get.return_value = ent_doc
                elif name == 'stripe_customers':
                    c.document.return_value.get.return_value = cust_doc
                return c

            mock_db.collection.side_effect = _col

            mock_portal_sess = MagicMock()
            mock_portal_sess.url = 'https://billing.stripe.com/mock'
            mock_portal.return_value = mock_portal_sess

            client = TestClient(app)
            response = client.post(
                '/api/stripe/create-customer-portal?user_email=userB@numista.ai'
            )
            assert response.status_code == 200, response.text
            assert response.json()['portal_url'] == 'https://billing.stripe.com/mock'
            mock_list.assert_not_called()
            mock_create_cust.assert_not_called()
            mock_portal.assert_called_once_with(
                customer='cus_A',
                return_url='https://numista.ai/#/settings',
            )
    finally:
        app.dependency_overrides.clear()


def test_stripe_portal_no_token():
    """No token → 401."""
    app.dependency_overrides[get_current_user] = _no_token()
    try:
        client = TestClient(app)
        response = client.post('/api/stripe/create-customer-portal')
        assert response.status_code == 401, response.text
    finally:
        app.dependency_overrides.clear()


# ─── MUST 4: Passport PDF — sender, claimer, stranger, no-token ───────────────

PASSPORT_URL = '/api/transfer/passport-pdf/transfer123'


def _transfer_doc(user_a_id='sender@numista.ai', user_b_id='claimer@numista.ai',
                  recipient_email='recipient@numista.ai', items=None):
    """Build a fake Firestore transfer document."""
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        'user_a_id': user_a_id,
        'user_b_id': user_b_id,
        'recipient_email': recipient_email,
        'items': items or [{'title': 'Morgan Dollar', 'grade': 'MS65'}],
    }
    return mock_doc


def test_passport_pdf_no_token():
    """No token → 401."""
    app.dependency_overrides[get_current_user] = _no_token()
    try:
        client = TestClient(app)
        response = client.get(PASSPORT_URL)
        assert response.status_code == 401, response.text
    finally:
        app.dependency_overrides.clear()


def test_passport_pdf_stranger():
    """Caller who is neither sender, claimer, nor recipient → 403."""
    app.dependency_overrides[get_current_user] = _make_user('strangerUID', 'stranger@numista.ai')
    try:
        with patch('main.db') as mock_db:
            mock_db.collection.return_value.document.return_value.get.return_value = _transfer_doc()
            client = TestClient(app)
            response = client.get(PASSPORT_URL)
            assert response.status_code == 403, response.text
    finally:
        app.dependency_overrides.clear()


def test_passport_pdf_sender():
    """Sender (caller uid == user_a_id) → passes auth guard (200 or 500 from PDF gen, never 403)."""
    app.dependency_overrides[get_current_user] = _make_user('senderUID', 'sender@numista.ai')
    try:
        with patch('main.db') as mock_db, \
             patch('services.passport_pdf_generator.generate_passport_pdf') as mock_gen:
            mock_db.collection.return_value.document.return_value.get.return_value = _transfer_doc()
            mock_gen.return_value = b'%PDF-fake'  # minimal fake PDF bytes
            client = TestClient(app)
            response = client.get(PASSPORT_URL)
            # Must NOT be 403 (auth guard) or 401 — PDF generation may raise other codes
            assert response.status_code == 200, \
                f"Sender got auth-blocked: {response.status_code} {response.text}"
    finally:
        app.dependency_overrides.clear()


def test_passport_pdf_claimer():
    """Claimer (caller uid == user_b_id) → passes auth guard (200 or 500, never 403)."""
    app.dependency_overrides[get_current_user] = _make_user('claimerUID', 'claimer@numista.ai')
    try:
        with patch('main.db') as mock_db, \
             patch('services.passport_pdf_generator.generate_passport_pdf') as mock_gen:
            mock_db.collection.return_value.document.return_value.get.return_value = _transfer_doc()
            mock_gen.return_value = b'%PDF-fake'
            client = TestClient(app)
            response = client.get(PASSPORT_URL)
            assert response.status_code == 200, \
                f"Claimer got auth-blocked: {response.status_code} {response.text}"
    finally:
        app.dependency_overrides.clear()


def test_passport_pdf_recipient_by_email():
    """Recipient matched by email (different uid) → passes auth guard."""
    app.dependency_overrides[get_current_user] = _make_user(
        'recipientUID', 'recipient@numista.ai'
    )
    try:
        with patch('main.db') as mock_db, \
             patch('services.passport_pdf_generator.generate_passport_pdf') as mock_gen:
            mock_db.collection.return_value.document.return_value.get.return_value = _transfer_doc()
            mock_gen.return_value = b'%PDF-fake'
            client = TestClient(app)
            response = client.get(PASSPORT_URL)
            assert response.status_code == 200, \
                f"Recipient got auth-blocked: {response.status_code} {response.text}"
    finally:
        app.dependency_overrides.clear()
