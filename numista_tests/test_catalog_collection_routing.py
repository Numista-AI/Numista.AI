"""Plan.v2.1 §9 Gate 3a: Collection Routing & Transactional Integrity Gate (`pytest numista_tests/test_catalog_collection_routing.py -v`)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "numista_backend")))

from tests.test_catalog_collection_routing import *  # noqa: F401, F403, E402
