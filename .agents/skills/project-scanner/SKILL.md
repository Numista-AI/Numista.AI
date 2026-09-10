---
name: project-scanner
description: >
  Nightly 360° system audit for Numista.AI. Validates backend, frontend, models,
  security, and live probes. Generates SCAN_REPORT.md in the project root.
---

# project-scanner — Honesty & Reporting Policy

This document governs how the `project-scanner` sidecar generates
`SCAN_REPORT.md` and associated artifacts. All rules are **mandatory**.

---

## 1. Header Status Tiers

The Executive Summary status line MUST use exactly one of:

| Status | Meaning | When to use |
|--------|---------|------------|
| `🟢 PASS` | All suites exit 0, zero warnings | Every gate green, zero lint |
| `🟢 PASS WITH WARNINGS` | All suites exit 0, lint/non-fatal warnings only | `dart analyze` has warnings but no test failures |
| `🟡 PASS WITH HOLDS` | At least one suite exits non-zero | `flutter test` fails, `dart analyze` exit 1, etc. |
| `🔴 FAIL` | Critical failure | Backend down, compilation error, security alert |

**Never** use `🟢 PASS WITH WARNINGS` when any test suite has failures.

---

## 2. N-of-M Playwright Labeling

- **Smoke only:** If only `auth.setup.js` + `01-homepage.spec.js` ran, report:
  ```
  Playwright Smoke: 8/8 passed in 40.0s (auth.setup + 01-homepage only)
  Master suite: NOT RUN this session
  ```
- **Full suite:** If the full master suite ran, report the actual stats from
  `test-results.json` with test count and duration.
- **NEVER** recycle a prior run's master-suite stats (e.g., "172 passed / 39.0m")
  unless the full suite was actually executed in THIS session and
  `test-results.json` reflects it.

### How to detect smoke vs full
Check `test-results.json` → `stats.expected`. If ≤ 10, it was smoke-only.
Cross-reference with the project list in the config — if only `setup` and
`chromium` projects are present, it was smoke.

---

## 3. Pytest Artifact Sync

- When SCAN_REPORT claims a pytest count (e.g., "303 passed"),
  `numista_tests/reports/pytest-output.txt` MUST contain the matching summary
  line from the same run session.
- If pytest was NOT re-run this session, the report MUST state:
  ```
  Backend Pytest: NOT RUN this session (last run: <date>, <count> passed)
  ```
- **NEVER** claim a pytest count that doesn't match the on-disk artifact.

---

## 4. Flutter Test Reporting

- Report the actual exit code and pass/fail counts from `flutter test`.
- If any test fails, the header MUST be `🟡 PASS WITH HOLDS` or worse.
- Cite the specific failing test file and line number.

---

## 5. Live QC Account Policy

- Default test account: `grokbot@numista.ai`
- **Forbidden accounts** (per `numista_qc/SUITE_MANIFEST.json`):
  - `ericdcman@gmail.com`
  - `eric.seaman@yahoo.com`
  - `jseaman1204@gmail.com`
- The Test Isolation section MUST name the account used:
  ```
  Test Isolation: E2E tests target grokbot@numista.ai (QC bot account).
  ```
- If a forbidden account was used (emergency fallback), flag explicitly:
  ```
  ⚠️ Test Isolation: E2E tests fell back to <account> (FORBIDDEN — grokbot unavailable).
  ```

---

## 6. Model & Program Registry

- **Primary flash model:** `gemini-3.8-flash`
- **Pro model:** `gemini-3.1-pro-preview`
- **Lite model:** `gemini-3.5-flash-lite`
- **Image model:** `gemini-3.1-flash-image`
- **Embedding model:** `gemini-embedding-2`
- **Program count:** 35 official US Mint & Treasury programs
  (source: `master_coin_programs.json`)

Update this section when models or programs change.

---

## 7. Report Generation (`generate_report.js`)

If `numista_tests/generate_report.js` is used to produce the Playwright
section of the report, it MUST:
- Dynamically detect whether smoke-only or full-suite ran (based on
  `test-results.json` stats)
- Never echo hardcoded master-suite baseline stats
- Label smoke runs as `Smoke Suite: N/N passed` (not `Master Suite`)

---

## 8. Safety Constraints

- Scanner runs on `dev` branch only
- Never push to `main`
- Never mutate production Firestore (`--execute` on real collections)
- Respect `SUITE_MANIFEST.json` `forbidden_accounts` and `protected_files`
