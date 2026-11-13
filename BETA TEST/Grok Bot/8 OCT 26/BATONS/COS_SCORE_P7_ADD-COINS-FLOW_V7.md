# COS SCORE - P7 ADD-COINS-FLOW V7
Scorer: Grok CoS | 2026-10-14 ~20:00 ET | Reviewed: ec34ab69 on dev (vs V6 ae2b87bd), code read directly (not AG summary)
Verdict: **PASS V7 (code).** Next: preview deploy, then UX Designer (rendered) + Field Tester gates.

Re-run by Grok CoS on EDS_Laptop: `flutter test test/p7_v5_ux_fixes_test.dart` -> 9/9 passed; `flutter test test/p7_cert_lookup_test.dart` -> 20/20 passed.
`flutter analyze` -> 2 issues, both in `lib/screens/program_manager_screen.dart` (unused import `http_auth_client.dart`, line 5), which is an UNCOMMITTED local edit, not part of ec34ab69 (likely NET-118 work in progress). Committed V7 code is clean. AG must leave analyze at 0 when that file is committed.

| # | NET-116 item | Score | Evidence |
|---|------|-------|----------|
| 1 | Empty-cert guard in `_saveManualCertEntry` | **PASS** | add_coins_hub.dart:3277-3285: `if (certNo.trim().isEmpty)` -> SnackBar + return, before `_certManualSaving = true` (3286), so no write and no flag to reset. |
| 1b | Refuse empty `certClean` (`123/`) | **PASS** | 3016-3025: SnackBar + return before `_certPendingConfirm` is set. Minor: if `123/` auto-detects as PCGS it goes to `_lookupSingleCert` with the raw text (3008-3011); not a write risk. |
| 2 | Empty guard must not set `_pcgsLookupError` | **PASS** | 2991-2999: SnackBar only, setState removed. |
| 3 | Fallback 18px dark, plain words, no CSV tip; badge 16px | **PASS** | 3735-3745: header 18 #92400E "Lookup not available right now", body 18 #78350F, jargon gone; button 16 (3766); CSV tip block deleted. Grader badge 16 (3073). |
| 4 | Tests | **PASS (weak)** | `find.text('NGC'), findsNothing` added. `blocker1EmptyLookupNoFallbackCard` is good. `blocker1SaveManualCertEmptyRefused` only taps Look Up with an empty box, the same path as blocker1EmptyCertRefused; it does not call the save. The guard is plainly in the code, so not a blocker. Carry as a P7 follow-up: a real save-path test (e.g. `123/` NGC input). |
| 5 | Gemini38 BUILD review + NET | **PASS** | GEMINI38_REVIEW_P7_ADD_COINS_FLOW_V7_BUILD.md + NET-117 (V7-done) filed. |

## Next
Code PASS. Baton stays GROKCOS_OVER, awaiting preview. Grok CoS does the Firebase re-login with Eric in the morning and deploys channel `p7-v7-gate` (project studio-9101802118-8c9a8, site numista-vault, FLUTTER_ENV=prod -> numista-qc). Then UX Designer (rendered) + Field Tester gates. No live deploy without Eric's YES.
