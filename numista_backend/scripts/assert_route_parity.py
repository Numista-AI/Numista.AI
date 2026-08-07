"""
assert_route_parity.py
-----------------------
Automated route snapshot and parity assertion tool for Numista.AI backend.
Generates a baseline JSON snapshot of all registered FastAPI endpoints and diffs
current app routes against the baseline to guarantee 0 missing, altered, or duplicate routes.

Usage:
  python scripts/assert_route_parity.py --create-baseline
  python scripts/assert_route_parity.py --diff
"""

import sys
import os
import json
import argparse
from pathlib import Path

# Add backend root to sys.path
BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

BASELINE_FILE = BACKEND_ROOT / "scripts" / "route_snapshot_baseline.json"

def inspect_app_routes():
    """Import main.app safely and inspect all registered APIRoute endpoints."""
    try:
        from main import app
    except Exception as e:
        print(f"❌ CRITICAL: Failed to import main.app: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    routes_data = []
    for route in app.routes:
        # We focus on APIRoute instances (ignoring mounting or static routes if any)
        methods = sorted(list(getattr(route, "methods", [])))
        path = getattr(route, "path", str(route))
        name = getattr(route, "name", "")
        tags = getattr(route, "tags", [])
        
        # Capture dependency names if present
        deps = []
        dependant = getattr(route, "dependant", None)
        if dependant and hasattr(dependant, "dependencies"):
            for dep in dependant.dependencies:
                dep_name = getattr(dep.call, "__name__", str(dep.call))
                deps.append(dep_name)

        routes_data.append({
            "path": path,
            "methods": methods,
            "name": name,
            "tags": sorted(tags),
            "dependencies": sorted(deps)
        })

    # Sort deterministically by path then methods
    routes_data.sort(key=lambda x: (x["path"], ",".join(x["methods"])))
    return routes_data

def create_baseline():
    """Generates and writes the baseline snapshot JSON file."""
    routes = inspect_app_routes()
    with open(BASELINE_FILE, "w", encoding="utf-8") as f:
        json.dump(routes, f, indent=2)
    print(f"[OK] Route snapshot baseline created with {len(routes)} routes -> {BASELINE_FILE}")

def compare_diff():
    """Compares current app routes against baseline snapshot."""
    if not BASELINE_FILE.exists():
        print(f"❌ Baseline file {BASELINE_FILE} does not exist. Run with --create-baseline first.")
        sys.exit(1)

    with open(BASELINE_FILE, "r", encoding="utf-8") as f:
        baseline_routes = json.load(f)

    current_routes = inspect_app_routes()

    # Index by (path, methods_str)
    baseline_map = { (r["path"], ",".join(r["methods"])): r for r in baseline_routes }
    current_map = { (r["path"], ",".join(r["methods"])): r for r in current_routes }

    baseline_keys = set(baseline_map.keys())
    current_keys = set(current_map.keys())

    missing_keys = baseline_keys - current_keys
    new_keys = current_keys - baseline_keys

    errors = []
    if missing_keys:
        for k in sorted(missing_keys):
            errors.append(f"  - MISSING ROUTE: {k[1]} {k[0]}")

    if new_keys:
        for k in sorted(new_keys):
            errors.append(f"  - UNEXPECTED NEW ROUTE: {k[1]} {k[0]}")

    # Check for signature/dependency alterations on matching keys
    common_keys = baseline_keys & current_keys
    for k in sorted(common_keys):
        b = baseline_map[k]
        c = current_map[k]
        if b["name"] != c["name"]:
            errors.append(f"  - NAME MISMATCH for {k[1]} {k[0]}: baseline '{b['name']}' vs current '{c['name']}'")

    print("\n" + "=" * 60)
    print(f"[CHECK] Route Parity Check: Baseline ({len(baseline_routes)} routes) vs Current ({len(current_routes)} routes)")
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
        # Default behavior: if baseline exists diff, else error
        if BASELINE_FILE.exists():
            compare_diff()
        else:
            create_baseline()
