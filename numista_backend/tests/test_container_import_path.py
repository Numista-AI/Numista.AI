import os
import sys
import subprocess
import pytest


def test_container_import_path():
    """Verify that under container runtime conditions (cwd=numista_backend,
    sys.path holding ONLY numista_backend, no repo root),
    importing main, importing services.duplicate_check, importing routes,
    and calling commit_reviews succeed without any ModuleNotFoundError.
    """
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    script = """
import sys
import os
import re
import asyncio
from unittest.mock import MagicMock

# Simulate container runtime: strip repo root and keep only backend directory
backend_dir = os.getcwd()
sys.path = [p for p in sys.path if os.path.abspath(p) != os.path.abspath(os.path.join(backend_dir, ".."))]
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# 1. Top-level 'numista_backend' is not in container sys.path
try:
    import numista_backend
    raise AssertionError("numista_backend should not exist in container sys.path")
except ModuleNotFoundError:
    pass

# 2. Main, routes, and services.duplicate_check must import cleanly
import main
import routes.import_routes
import routes.cert_routes
from services.duplicate_check import check_and_flag_duplicate
assert callable(check_and_flag_duplicate)

# 3. Verify no non-test backend source files have 'from numista_backend' or 'import numista_backend' statements
for root, dirs, files in os.walk(backend_dir):
    if "tests" in root or ".pytest_cache" in root or "__pycache__" in root:
        continue
    for file in files:
        if file.endswith(".py") and not file.startswith("test_"):
            with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                for line in f:
                    if re.match(r'^\\s*(from|import)\\s+numista_backend\\b', line):
                        raise ModuleNotFoundError(f"Container runtime failure: {file} imports numista_backend: {line.strip()}")

# 4. commit_reviews must execute dupe check cleanly without ModuleNotFoundError
from main import commit_reviews, CommitReviewsRequest

req = CommitReviewsRequest(user_email='grokbot@numista.ai', review_ids=['test_doc_1'])

mock_db = MagicMock()
mock_queue_doc = MagicMock()
mock_queue_doc.to_dict.return_value = {'Year': '2021', 'Mint': 'W', 'Denomination': 'Dollar'}
mock_queue_doc.id = 'test_doc_1'
mock_queue_doc.exists = True
mock_db.collection.return_value.document.return_value.get.return_value = mock_queue_doc

main.db = mock_db
res = asyncio.run(commit_reviews(req, _user={'email': 'grokbot@numista.ai'}))
print(f"COMMIT_SUCCESS: {res}")
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = ""
    res = subprocess.run(
        [sys.executable, "-c", script],
        cwd=backend_dir,
        env=env,
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        raise AssertionError(f"Container import test failed (exit code {res.returncode}):\n{res.stderr}\n{res.stdout}")
    assert "COMMIT_SUCCESS" in res.stdout
