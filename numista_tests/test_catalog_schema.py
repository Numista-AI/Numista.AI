"""Plan.v2.2 §9 Gate 2: Schema & Ingestion Gate (`pytest numista_tests/test_catalog_schema.py -v`)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "numista_backend")))

from tests.test_catalog_collection_routing import (  # noqa: F401, E402
    test_cc_era_year_agreement,
    test_citation_required_and_kind_and_cc_must_match_nac,
    test_every_fixture_row_is_a_valid_catalog_item,
    test_filter_by_state_facet_cc_and_facility,
    test_fineness_requires_precious_metal_type,
    test_mint_mark_consistency,
    test_public_catalog_and_snapshot_reject_user_pii,
    test_tier_a_mintage_validator_rejects_commercial_sources,
)
