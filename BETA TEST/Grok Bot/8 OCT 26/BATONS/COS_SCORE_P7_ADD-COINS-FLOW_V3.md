# COS SCORE - P7 ADD-COINS-FLOW V3
Scorer: Grok CoS | 2026-10-14 ~16:50 ET | Reviewed: a016e1c4 (code), 7e61f99d (docs) vs 15021e7b
Verdict: **FAIL V3 (close)**. 3 of 5 items PASS. Two small fixes, then UX Designer + Field Tester gate.

Tests re-run by Grok CoS: pytest tests/test_cert_lookup.py -> 13 passed. (flutter suite not re-run; AG reports 500/500, analyze clean.)

| # | Item | Score | Evidence |
|---|------|-------|----------|
| 1 | Double-write false duplicate | PASS | cert_routes.py cert_save now check-only: returns status='clear', coin_id=None, no db write; test asserts set() not called. add_coins_hub.dart: redundant Firestore where(certNo) check removed in _saveManualCertEntry and _addLookupResultToCollection; single .add() writer remains. |
| 2 | Fake eric_emails safeguard | PASS | eric_emails block and fake 'safeguard_blocked'/'test_saved_coin_id' removed entirely. |
| 3a | NET-087 add-another-copy from filled slot | PASS (note) | program_manager_screen.dart: owned chip now has "+" (tooltip "Add another copy") -> AddCoinsHub(initialTabName:'cert'). Note: opens blank cert tab; does not carry the slot's coin. Acceptable for V3; UX/FT to judge. |
| 3b-i | NGC verify link format | **FAIL** | Test cert 8321797-003 PF67 must give https://www.ngccoin.com/certlookup/8321797-003/67/. Code (line ~3061) gradeSlug = grade with spaces removed + uppercase -> "/8321797-003/PF67/". Pre-confirm Verify button (line ~2923) omits grade entirely -> "/8321797-003/". Fix: strip to numeric grade (regex \d{1,2}) for both; button and stored verify_link must match. (Cert detection itself OK: dash kept, auto-detect -> NGC.) |
| 3b-ii | Slab photo-read | **FAIL** | /api/scan_cert_number_upload uses google.generativeai with GOOGLE_API_KEY/GEMINI_API_KEY. Standing rule: ADC, not API keys. Fix: use Vertex AI (google-genai vertexai=True or vertexai SDK) with ADC on numista-qc. Also delete dead stub /scan_cert_number (Depends(lambda: None), always 405). Model gemini-2.0-flash: confirm still available or use current Flash. Must add a mocked unit test for the endpoint (no live call). Photo-read must prefill only; user still confirms (code does prefill only - OK). |
| 4 | UX Designer + Field Tester gate | PENDING | Not started; runs after fixes 3b-i/3b-ii. |

## Fix list (V4) - one job, no deploy, no Firestore/collection writes
1. NGC grade slug numeric only; same URL in Verify button and stored verify_link. Add a test/assert for 8321797-003 + "PF67" -> .../certlookup/8321797-003/67/.
2. Slab scan endpoint -> Vertex AI with ADC (no API key). Remove dead /scan_cert_number stub. Add mocked pytest.
3. Commit explicit paths only; file EXECUTE_DONE V4 + NET to GROKCOS.
