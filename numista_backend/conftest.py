import os
import sys
from unittest.mock import MagicMock, patch

os.environ["DISABLE_PROXIES"] = "true"
# Allow monkeypatch-based legacy tests to bypass the default-deny auth middleware.
# ONLY active when K_SERVICE and ENVIRONMENT!=production are unset (i.e., local/CI only).
# Tests that validate the 401 behavior should use dependency_overrides or set K_SERVICE.
os.environ.setdefault("ALLOW_UNAUTHENTICATED", "1")

import google.auth
import google.cloud.firestore
import google.cloud.storage

# Patch google.auth.default before main import
mock_creds = MagicMock()
google.auth.default = MagicMock(return_value=(mock_creds, "studio-9101802118-8c9a8"))
google.cloud.firestore.Client = MagicMock()
google.cloud.storage.Client = MagicMock()

import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client_prod_mode():
    old_k = os.environ.get("K_SERVICE")
    old_allow = os.environ.get("ALLOW_UNAUTHENTICATED")
    os.environ["K_SERVICE"] = "numista-backend-test-prod"
    os.environ.pop("ALLOW_UNAUTHENTICATED", None)
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
    if old_k is None:
        os.environ.pop("K_SERVICE", None)
    else:
        os.environ["K_SERVICE"] = old_k
    if old_allow is not None:
        os.environ["ALLOW_UNAUTHENTICATED"] = old_allow

