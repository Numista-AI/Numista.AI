# _archived/ — Numista QC Legacy Test Files
Files moved here from numista_tests/ during QC consolidation (24 AUG 26).
These are preserved for historical reference. Do not execute.

## Archive contents (populated during Phase 5 cleanup)
- auth.probe1-10.js — coordinate-based auth probes, superseded by signInAndWait()
- 21-aug12-ui-scrollbar-contrast.spec.js — screenshot-only, zero assertions
- master_ui_e2e.spec.ts — dead code, skip guard prevented it from ever running
- run_full_beta_test_suite.py — hardcoded PASS in executive summary
- run_full_e2e_qa.py — superseded by run_qc.ps1
- check_highlight.py, find_blobs.py, find_button.py, find_coords_*.py — coordinate finders, no assertions
- crop_sidebar.py — screenshot utility only

Files are moved here before deletion to preserve the historical test vector record.
Delete only after one full review cycle confirms no regression.
