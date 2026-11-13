"""Plan.v2.1 §9 Gate 1: NAC1 Grammar & Checksum Gate (`pytest numista_tests/test_nac1_validator.py -v`)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "numista_backend")))

from tests.test_catalog_nac1 import *  # noqa: F401, F403, E402
