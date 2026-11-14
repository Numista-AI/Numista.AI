"""Regression tests for Track #1: Security Route Baseline & Parity Checker (S1-01..S1-06)."""

from __future__ import annotations

import copy
import json

import main as backend_main
from scripts import assert_route_parity


def test_flattened_routes_have_no_included_router_wrappers_or_duplicates() -> None:
    """S1-01 / S1-03: _iter_effective_routes flattens all APIRouters with zero duplicate route keys."""
    routes, duplicates = assert_route_parity.inspect_app_routes(backend_main.app)

    assert duplicates == [], f"Found duplicate (path, methods) registrations: {duplicates}"
    assert len(routes) >= 190
    assert not any("_IncludedRouter" in r["path"] for r in routes)
    assert getattr(backend_main, "admin_grade_flags", None) is None
    assert getattr(backend_main, "resolve_grade_flag", None) is None

    # Verify _EffectiveRouteContext / APIRoute attribute contract assumed by inspect_app_routes()
    api_contexts = [
        r for r in assert_route_parity._iter_effective_routes(backend_main.app.routes)
        if type(r).__name__ in ("_EffectiveRouteContext", "APIRoute")
    ]
    assert api_contexts and all(
        hasattr(r, "path")
        and hasattr(r, "methods")
        and hasattr(r, "name")
        and hasattr(r, "tags")
        and hasattr(getattr(r, "dependant", None), "dependencies")
        for r in api_contexts
    )


def test_extract_dep_name_handles_callable_class_instance_deterministically() -> None:
    """S1-01: _extract_dep_name returns class name rather than memory-address str() for callable instances."""
    class CustomBearer:
        def __call__(self) -> None:
            return None

    class FakeDependant:
        def __init__(self, call_obj: object) -> None:
            self.call = call_obj

    def sample_guard() -> None:
        return None

    instance = CustomBearer()
    assert not hasattr(instance, "__name__")
    assert assert_route_parity._extract_dep_name(FakeDependant(instance)) == "CustomBearer"
    assert assert_route_parity._extract_dep_name(FakeDependant(sample_guard)) == "sample_guard"


def test_route_parity_matches_committed_baseline() -> None:
    """S1-04: Live FastAPI app matches route_snapshot_baseline.json across path, methods, name, tags, and dependencies."""
    baseline = json.loads(assert_route_parity.BASELINE_FILE.read_text(encoding="utf-8"))
    current, duplicates = assert_route_parity.inspect_app_routes(backend_main.app)
    errors = assert_route_parity.compare_routes(baseline, current, duplicates=duplicates)

    assert errors == [], "Route parity drift detected:\n" + "\n".join(errors)
    assert len(current) == len(baseline)


def test_compare_routes_detects_dependency_tag_name_and_duplicate_drift() -> None:
    """S1-02: compare_routes catches dropped auth Depends(), tag drift, name changes, missing/new routes, and duplicates."""
    baseline = [
        {
            "path": "/api/v1/photos/signed_url",
            "methods": ["POST"],
            "name": "create_signed_photo_urls",
            "tags": ["User Photo Signed URLs"],
            "dependencies": ["require_registered_user"],
        },
        {
            "path": "/api/v1/hardware/installer_url",
            "methods": ["GET"],
            "name": "get_hardware_installer_url",
            "tags": ["Hardware Agent"],
            "dependencies": ["require_registered_user"],
        },
    ]

    # 1. Dependency drop + tag drift
    mutated = copy.deepcopy(baseline)
    mutated[0]["dependencies"] = []
    mutated[1]["tags"] = []
    errors = assert_route_parity.compare_routes(baseline, mutated)
    joined = "\n".join(errors)
    assert "DEPENDENCIES MISMATCH for POST /api/v1/photos/signed_url" in joined
    assert "TAGS MISMATCH for GET /api/v1/hardware/installer_url" in joined

    # 2. Missing route + unexpected new route + duplicate key
    missing_and_extra = [
        {
            "path": "/api/v1/photos/signed_url",
            "methods": ["POST"],
            "name": "renamed_handler",
            "tags": ["User Photo Signed URLs"],
            "dependencies": ["require_registered_user"],
        },
        {
            "path": "/api/v1/new_unguarded",
            "methods": ["POST"],
            "name": "new_unguarded",
            "tags": [],
            "dependencies": [],
        },
    ]
    errors_2 = assert_route_parity.compare_routes(
        baseline,
        missing_and_extra,
        duplicates=[("/api/v1/photos/signed_url", "POST")],
    )
    joined_2 = "\n".join(errors_2)
    assert "DUPLICATE ROUTE KEY: POST /api/v1/photos/signed_url" in joined_2
    assert "MISSING ROUTE: GET /api/v1/hardware/installer_url" in joined_2
    assert "UNEXPECTED NEW ROUTE: POST /api/v1/new_unguarded" in joined_2
    assert "NAME MISMATCH for POST /api/v1/photos/signed_url" in joined_2


def test_hardened_baseline_records_security_dependencies() -> None:
    """S1-04: Regenerated baseline reflects post-hardening auth dependencies from cc97a8fd & 7c87a6eb."""
    baseline = json.loads(assert_route_parity.BASELINE_FILE.read_text(encoding="utf-8"))
    by_key = {(r["path"], ",".join(r["methods"])): r for r in baseline}

    assert by_key[("/api/v1/photos/signed_url", "POST")]["dependencies"] == ["require_registered_user"]
    assert by_key[("/api/v1/hardware/installer_url", "GET")]["dependencies"] == ["require_registered_user"]
    assert by_key[("/api/transfer/initiate", "POST")]["dependencies"] == ["require_registered_user"]
    assert by_key[("/api/transfer/claim", "POST")]["dependencies"] == ["require_registered_user"]
    assert by_key[("/api/transfer/recall", "POST")]["dependencies"] == ["require_registered_user"]
    assert by_key[("/api/import_spreadsheet", "POST")]["dependencies"] == ["get_current_user"]
    assert by_key[("/api/v1/import/get_upload_url", "POST")]["dependencies"] == ["get_current_user"]
    assert by_key[("/api/v1/import/commit_batch", "POST")]["dependencies"] == ["get_current_user"]
    assert by_key[("/api/admin/grade_flags", "GET")]["dependencies"] == ["require_admin_user"]
    assert by_key[("/api/admin/grade_flags/{flag_id}/resolve", "POST")]["dependencies"] == ["require_admin_user"]
    assert by_key[("/support/tickets", "GET")]["dependencies"] == ["require_admin"]

    # Removed stale baseline paths must stay absent
    assert ("/api/dismissed_news/{user_email}", "GET") not in by_key
    assert ("/api/v1/coa/parse", "POST") not in by_key
