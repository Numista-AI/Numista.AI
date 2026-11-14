"""
assert_route_parity.py
-----------------------
Automated route snapshot and parity assertion tool for Numista.AI backend.
Generates a baseline JSON snapshot of all registered FastAPI endpoints (flattening
FastAPI 0.141+ _IncludedRouter entries) and diffs current app routes—including
auth dependencies and tags—against the baseline to guarantee 0 missing, added,
altered, or duplicate routes.

Usage:
  python scripts/assert_route_parity.py --create-baseline
  python scripts/assert_route_parity.py --diff
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

# Add backend root to sys.path
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

BASELINE_FILE = BACKEND_ROOT / "scripts" / "route_snapshot_baseline.json"


def _has_local_gcp_credentials() -> bool:
    """Return True if explicit local service account credentials exist on disk."""
    gac = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if gac and Path(gac).is_file():
        return True
    return (
        (BACKEND_ROOT / "serviceAccountKey.json").is_file()
        or (BACKEND_ROOT / "serviceAccountKey.json.json").is_file()
    )


def _ensure_offline_gcp_stubs() -> None:
    """Stub GCP clients before importing main when running offline or in CI without credentials."""
    os.environ.setdefault("DISABLE_PROXIES", "true")
    force_offline = os.environ.get("ASSERT_ROUTE_PARITY_OFFLINE", "").strip() == "1"
    if not force_offline and _has_local_gcp_credentials():
        return

    import google.auth
    import google.cloud.firestore
    import google.cloud.storage

    # Only replace real client constructors if not already mocked (e.g. by conftest.py)
    if not isinstance(google.auth.default, MagicMock):
        google.auth.default = MagicMock(return_value=(MagicMock(), "studio-9101802118-8c9a8"))
    if not isinstance(google.cloud.firestore.Client, MagicMock):
        google.cloud.firestore.Client = MagicMock()
    if not isinstance(google.cloud.storage.Client, MagicMock):
        google.cloud.storage.Client = MagicMock()


def _iter_effective_routes(routes: list[Any]):
    """Recursively flatten FastAPI _IncludedRouter objects into leaf route/context entries."""
    for route in routes:
        eff_fn = getattr(route, "effective_route_contexts", None)
        if callable(eff_fn):
            yield from eff_fn()
        elif type(route).__name__ == "_IncludedRouter" and hasattr(route, "original_router"):
            yield from _iter_effective_routes(route.original_router.routes)
        else:
            yield route


def _extract_dep_name(dep: Any) -> str:
    """Return deterministic callable name for a FastAPI Dependant entry."""
    call = getattr(dep, "call", dep)
    name = getattr(call, "__name__", None)
    if name:
        return str(name)
    cls = getattr(call, "__class__", None)
    if cls is not None and getattr(cls, "__name__", None):
        return str(cls.__name__)
    return str(call)


def inspect_app_routes(app_instance: Any | None = None) -> tuple[list[dict[str, Any]], list[tuple[str, str]]]:
    """Import main.app safely and inspect all registered endpoints + duplicate route keys."""
    if app_instance is None:
        _ensure_offline_gcp_stubs()
        try:
            from main import app as app_instance
        except Exception as e:
            print(f"[CRITICAL] Failed to import main.app: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    routes_data: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str]] = set()
    duplicates: list[tuple[str, str]] = []

    # _EffectiveRouteContext (FastAPI >=0.141) and APIRoute both expose:
    # .path, .methods, .name, .tags, .dependant.dependencies
    # If a future FastAPI changes this contract, the AttributeError will surface here.
    for route in _iter_effective_routes(app_instance.routes):
        methods = sorted(list(getattr(route, "methods", None) or []))
        path = getattr(route, "path", str(route))
        name = getattr(route, "name", "") or ""
        tags = sorted(str(t) for t in (getattr(route, "tags", None) or []))

        deps: list[str] = []
        dependant = getattr(route, "dependant", None)
        if dependant and hasattr(dependant, "dependencies"):
            for dep in dependant.dependencies:
                deps.append(_extract_dep_name(dep))

        key = (path, ",".join(methods))
        # Both copies are retained in routes_data so callers can inspect them;
        # duplicates list is the authoritative signal. create_baseline refuses to write if non-empty.
        if key in seen_keys:
            duplicates.append(key)
        else:
            seen_keys.add(key)

        routes_data.append({
            "path": path,
            "methods": methods,
            "name": name,
            "tags": tags,
            "dependencies": sorted(deps),
        })

    # Sort deterministically by path then methods
    routes_data.sort(key=lambda x: (x["path"], ",".join(x["methods"])))
    duplicates.sort()
    return routes_data, duplicates


def compare_routes(
    baseline_routes: list[dict[str, Any]],
    current_routes: list[dict[str, Any]],
    duplicates: list[tuple[str, str]] | None = None,
) -> list[str]:
    """Compare current flattened routes against baseline, checking routes, duplicates, names, tags, and dependencies."""
    errors: list[str] = []

    for path, methods_str in (duplicates or []):
        errors.append(f"  - DUPLICATE ROUTE KEY: {methods_str} {path}")

    baseline_map = {(r["path"], ",".join(r.get("methods", []))): r for r in baseline_routes}
    current_map = {(r["path"], ",".join(r.get("methods", []))): r for r in current_routes}

    baseline_keys = set(baseline_map.keys())
    current_keys = set(current_map.keys())

    for k in sorted(baseline_keys - current_keys):
        errors.append(f"  - MISSING ROUTE: {k[1]} {k[0]}")

    for k in sorted(current_keys - baseline_keys):
        errors.append(f"  - UNEXPECTED NEW ROUTE: {k[1]} {k[0]}")

    for k in sorted(baseline_keys & current_keys):
        b = baseline_map[k]
        c = current_map[k]
        if b.get("name", "") != c.get("name", ""):
            errors.append(
                f"  - NAME MISMATCH for {k[1]} {k[0]}: baseline '{b.get('name', '')}' vs current '{c.get('name', '')}'"
            )
        b_deps = sorted(b.get("dependencies", []))
        c_deps = sorted(c.get("dependencies", []))
        if b_deps != c_deps:
            errors.append(
                f"  - DEPENDENCIES MISMATCH for {k[1]} {k[0]}: baseline {b_deps} vs current {c_deps}"
            )
        b_tags = sorted(b.get("tags", []))
        c_tags = sorted(c.get("tags", []))
        if b_tags != c_tags:
            errors.append(
                f"  - TAGS MISMATCH for {k[1]} {k[0]}: baseline {b_tags} vs current {c_tags}"
            )

    return errors


def create_baseline() -> None:
    """Generate and write the baseline snapshot JSON file (refuses if duplicate routes exist)."""
    routes, duplicates = inspect_app_routes()
    if duplicates:
        print(f"[CRITICAL] Refusing to write baseline: found {len(duplicates)} duplicate route key(s):")
        for path, methods_str in duplicates:
            print(f"  - DUPLICATE ROUTE KEY: {methods_str} {path}")
        sys.exit(1)

    with open(BASELINE_FILE, "w", encoding="utf-8") as f:
        json.dump(routes, f, indent=2)
        f.write("\n")
    print(f"[OK] Route snapshot baseline created with {len(routes)} routes -> {BASELINE_FILE}")


def compare_diff() -> None:
    """Compare current app routes against baseline snapshot."""
    if not BASELINE_FILE.exists():
        print(f"[ERROR] Baseline file {BASELINE_FILE} does not exist. Run with --create-baseline first.")
        sys.exit(1)

    with open(BASELINE_FILE, "r", encoding="utf-8") as f:
        baseline_routes = json.load(f)

    current_routes, duplicates = inspect_app_routes()
    errors = compare_routes(baseline_routes, current_routes, duplicates=duplicates)

    print("\n" + "=" * 60)
    print(
        f"[CHECK] Route Parity Check: Baseline ({len(baseline_routes)} routes) "
        f"vs Current ({len(current_routes)} routes)"
    )
    print("=" * 60)

    if errors:
        print(f"[FAIL] PARITY FAILURE: Found {len(errors)} route discrepancy(ies):")
        for err in errors:
            print(err)
        sys.exit(1)
    else:
        print(f"[SUCCESS] PARITY SUCCESS: 100% route parity verified across all {len(current_routes)} endpoints!")
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assert FastAPI route parity against baseline snapshot.")
    parser.add_argument("--create-baseline", action="store_true", help="Create baseline snapshot JSON")
    parser.add_argument("--diff", action="store_true", help="Compare current routes against baseline")
    args = parser.parse_args()

    if args.create_baseline:
        create_baseline()
    elif args.diff:
        compare_diff()
    else:
        if BASELINE_FILE.exists():
            compare_diff()
        else:
            create_baseline()
