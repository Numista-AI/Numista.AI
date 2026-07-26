import os
import sys
from unittest.mock import MagicMock, patch

os.environ["DISABLE_PROXIES"] = "true"

import google.auth
import google.cloud.firestore
import google.cloud.storage

# Patch google.auth.default before main import
mock_creds = MagicMock()
google.auth.default = MagicMock(return_value=(mock_creds, "studio-9101802118-8c9a8"))
google.cloud.firestore.Client = MagicMock()
google.cloud.storage.Client = MagicMock()
