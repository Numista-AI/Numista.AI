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
