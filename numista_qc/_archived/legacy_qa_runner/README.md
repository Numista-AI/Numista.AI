# Legacy QA Runner — Archived Scripts
Archived: 2026-08-25 during QC Consolidation (conv 723bb504). Replaced by `numista_qc/` suite.

| File | Reason Retired | Date |
|------|---------------|------|
| qa_account_auditor.py | 10/12 scorecard metrics hardcoded to PASS — produced false green reports | 2026-08-25 |
| run_full_beta_test_suite.py | Executive summary always wrote ✅ PASS regardless of actual results | 2026-08-25 |
| auth.probe2.json | Coordinate-based auth probe, superseded by signInAndWait() helper | 2026-08-25 |
| auth.probe3.json | Coordinate-based auth probe, superseded by signInAndWait() helper | 2026-08-25 |
| auth.probe7.js | Coordinate-based auth probe, superseded by signInAndWait() helper | 2026-08-25 |
| auth.probe8.js | Coordinate-based auth probe, superseded by signInAndWait() helper | 2026-08-25 |
| auth.probe9.js | Coordinate-based auth probe, superseded by signInAndWait() helper | 2026-08-25 |
| auth.probe10.js | Coordinate-based auth probe, superseded by signInAndWait() helper | 2026-08-25 |
| daily_feedback_dynamic.spec.js | 83 screenshot-only tests, zero real assertions — replaced by Layer 1 visual guards | 2026-08-25 |

**Do NOT delete these files from archive. Do NOT modify `run_overnight_tests.py` (it is NOT archived).**
