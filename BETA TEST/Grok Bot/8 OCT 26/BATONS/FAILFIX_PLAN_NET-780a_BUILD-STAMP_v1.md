# FAILFIX PLAN v1: Build Stamp in /version.json (NET-780a)
**To:** Antigravity Desk, Grok Bot CoS, Argon (Gemini 3.8), Founder Eric  
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**Date:** 4 November 2026, 5:30 PM ET  
**Reference Baton:** `BATON_NET-780_FAILFIX_PLAN_NET-748-v5-FT_v1_2026-11-04-1658.md`  
**Partition:** Split Track A of NET-780 (per Founder Eric 4:58 PM ET split direction)  
**Status:** **PLAN ONLY** (Zero code changes, zero deployments, zero Firestore writes).  
**Standing Locks:** `origin/main` strictly locked at `9f04550a`; Stripe strictly locked OFF; Zero deployments without Eric's typed YES.

---

## 1. Defect & Requirements

### A. Defect Description
Field Tester reported that inspecting `https://numista-vault--p7-gate-8avtpz22.web.app/version.json` returned standard Flutter version info without build provenance:
```json
{"app_name":"numista_ai","version":"8.18.15","build_number":"81818","package_name":"numista_ai"}
```
There is no `git_commit` SHA or `build_time` timestamp. As a result, Field Tester and the test harness could not deterministically prove whether `p7-gate` was running the exact commit under review (`c294fd3c` vs older commits).

### B. Requirements
1. Every deployed build (preview channels and production) must serve `/version.json` with:
   - `git_commit`: Full or short 8-char git SHA (e.g., `c294fd3c`).
   - `build_time`: ISO 8601 UTC timestamp of the build (e.g., `2026-11-04T21:00:00Z`).
2. `/version.json` must be strictly un-cached so browser checks immediately reflect new channel deployments:
   - Verified in `numista_mobile/firebase.json:181-188`:
     ```json
     181:       {
     182:         "source": "/version.json",
     183:         "headers": [
     184:           {
     185:             "key": "Cache-Control",
     186:             "value": "no-cache, no-store, must-revalidate"
     187:           }
     188:         ]
     189:       },
     ```
3. Must integrate seamlessly with Flutter Web build output without dirtying git tracking.

---

## 2. Root Cause Analysis

Flutter's built-in web compiler generates `build/web/version.json` exclusively from `pubspec.yaml` version fields (`version: 8.18.15+81818`). It does not query git or embed build timestamps.
Currently, after `flutter build web --release` completes, deployment scripts immediately execute `firebase hosting:channel:deploy` without post-processing `build/web/version.json`.

---

## 3. Planned Implementation

### A. Post-Build Stamp Tool (`tools/stamp_build_version.py`)
Create a lightweight, hermetic Python post-build script `tools/stamp_build_version.py`:
```python
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

def stamp_version():
    web_dir = Path("build/web")
    version_file = web_dir / "version.json"
    if not version_file.exists():
        print(f"ERROR: {version_file} not found. Run flutter build web first.", file=sys.stderr)
        sys.exit(1)

    try:
        git_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip()
    except Exception as e:
        git_sha = "unknown"

    build_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with open(version_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["git_commit"] = git_sha
    data["build_time"] = build_time

    with open(version_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"[STAMP] Successfully injected into {version_file}:")
    print(f"        git_commit: {git_sha}")
    print(f"        build_time: {build_time}")

if __name__ == "__main__":
    stamp_version()
```

### B. Deployment Pipeline Integration
Update the deploy procedure in deployment documentation/scripts to mandate running `python tools/stamp_build_version.py` immediately after `flutter build web`:
```bash
cd numista_mobile
flutter build web --release
python ../tools/stamp_build_version.py
firebase hosting:channel:deploy p7-gate --expires 30d
```

### C. Example Output Served by Web Server
```json
{
  "app_name": "numista_ai",
  "version": "8.18.15",
  "build_number": "81818",
  "package_name": "numista_ai",
  "git_commit": "c294fd3cb9e4e6b123456789abcdef0123456789",
  "build_time": "2026-11-04T22:30:00Z"
}
```

---

## 4. Verification & Test Steps

1. Execute test dry run:
   ```bash
   python tools/stamp_build_version.py
   cat numista_mobile/build/web/version.json
   ```
2. Verify exit code is 0.
3. Verify JSON parses with `jq` or Python and contains both `git_commit` and `build_time`.
4. Deploy test to channel `p7-gate` (after Eric's typed YES).
5. In browser or via curl:
   ```bash
   curl -s -H "Cache-Control: no-cache" https://numista-vault--p7-gate-8avtpz22.web.app/version.json
   ```
6. Confirm response contains exact git commit and UTC build timestamp.

---

## 5. Review & Standing Locks
- **PLAN ONLY.** Zero code modifications committed, zero deployments executed.
- `origin/main` locked at `9f04550a`. Stripe locked OFF.
