# COS SCORE - P7 ADD-COINS-FLOW V8.18 BUILD
Scorer: Grok CoS (day watch) | 2026-10-19 11:15 ET | Reviewed: code `1137b732` on origin/p7-v8.9 (parent dbda922f) + EXECUTE_DONE_P7_V8_18.md + GEMINI38_REVIEW_P7_V8_18_BUILD.md + NET-339 + independent read of `git diff dbda922f 1137b732` in worktree `C:\Users\ericd\AppData\Local\Temp\p7v89_build` (11 files, +656/-70) + Cloud Run logs for p7gate revisions.
Watch re-ran: `tools\check_html_scripts.ps1` = 6/6 PASS; `flutter test test/p7_v8_ux_safety_test.dart --plain-name p7_v818` = 2/2 PASS.
Verdict: **FAIL (close).** Most of the UI work is good, but two MUST-FIX items from NET-335/336 were not done, and the investigation write-ups that NET-339 says are "in EXECUTE_DONE" are not there. Dev only. No deploys.

| # | Item (source) | Score | Independent check (1137b732) |
|---|---|---|---|
| 1 | startImport() brace + systemic node --check + CI step (NET-334, NET-335 #1) | **PASS** | Watch ran tools\check_html_scripts.ps1: 6/6 incl. add_coins.html. .ps1 + .sh added. |
| 2 | Hub passes api= to web/*.html (NET-331) | **PASS** | `git grep` of lib/: add_coins_hub.dart:932 `buildAddCoinsHtmlPath(email)` is the only in-app web/*.html opener. Default kApiBaseUrl (constants.dart:13) equals the helper's liveBackend string, so the live build adds no param. Unit test green. |
| 3 | PDF INVOICE PATH, MUST-KEEP (NET-335 #2) | **FAIL** | Not addressed. No diff hunk touches "Run High-Speed Parallel Batch" (add_coins_hub.dart:1206, still the dead button FT reported). No end-to-end invoice PDF import on p7gate with grokbot, no statement of which endpoint invoices use, and no proof it does not depend on the Document AI processors undeployed today. |
| 4 | Scan reliability root cause with log lines, fix, every scan <=30 s (NET-336 systemic, NET-335 #3) | **FAIL (partial)** | Client 30 s timeout on scan_cert_number_upload (add_coins_hub.dart:3273) and error card are good. But no log lines, and the cold-start hypothesis does not match the logs. Watch pulled them (see below). |
| 5 | Scan error UI, 56px Try again / Type it in (NET-336 #1) | **PASS** | `_buildScanErrorCard()` 56px buttons, 16px bold text, Type it in focuses `_pcgsSingleFocusNode`. |
| 6 | Cert photo empty result (NET-336 #2) | **PASS** | Empty cert_number sets `no_cert` + "Couldn't read a cert number from that photo". |
| 7 | add_coins.html file list, light theme, avatar 404 (NET-336 #3) | **PASS (code)** | Staged-files list, light-mode tokens, owl emoji in place of morgan_avatar.png. Progress/errors for 1-2 PDFs still need the FT run in item 3. |
| 8 | Sidebar "Take a photo" first click to Welcome (NET-336 #4) | **PASS (note)** | `static bool _welcomeDone` stops the reload. Note: being static, it also survives sign-out in the same tab, so a second account signing in on that tab skips Welcome. Reset it on sign-out. |
| 9 | Desktop camera NotFoundError (NET-336 #5) | **PASS** | no_camera card with "Choose a photo instead". |
| 10 | Microscope banner + localhost calls (NET-336 #6) | **PASS** | `isMicroscopeConfigured()` defaults false; getStatus/isServerRunning/listCameras/fetchFrame/pairAgent guarded; banner hidden. Test green. |
| 11 | Text 16px+, 48px targets (NET-336 #7) | **FAIL (small)** | Diff still adds sub-16px text: settings_screen.dart `_buildMicroscopeCard` description `fontSize: 13`; add_coins_hub.dart:4219 NFC badge `fontSize: 12` on the cert result. GEMINI38 said "16px across" and missed both. Back arrow 48px not shown. |
| 12 | Investigate + report: CAC hang, backup 314 vs 312, app_version, manual cert fields (NET-334/335) | **FAIL (docs)** | app_version fixed (PASS). The other three are one-liners in NET-339 that say "Explanation in EXECUTE_DONE", but EXECUTE_DONE_P7_V8_18.md has no investigation section. The 314 vs 312 answer cites `deleted_at IS NOT NULL` (SQL wording) with no evidence from the export code or the grokbot data. |

## Log evidence the watch pulled (project studio-9101802118-8c9a8, read-only)
- backend p7gate rev `numista-backend-00468-qir`, 09:36:41 ET: `scan_cert_number failed: 403 PERMISSION_DENIED ... Permission 'aiplatform.endpoints.predict' denied on resource '//aiplatform.googleapis.com/projects/numista-qc/locations/global/publishers/google/models/gemini-3.8-flash'`. Backend runs as `568985927038-compute@developer.gserviceaccount.com`. So the cert-photo read on p7gate fails on IAM, not cold start. (No PERMISSION_DENIED on any live numista-backend revision in the last 3 days.)
- same rev, `identify_coin_photo` latencies 09:25-09:38 ET: 473 s, 459 s (HTTP 500), 257 s, 180 s, 173 s x3, 144 s, 56 s, 393 s. That is the 60-100 s+ spinner UX and FT saw. Requests run for minutes, so this is server-side retries/backoff or a stuck model call, not a 20 s cold start.

## V8.18.1 orders (to AGCOS)
1. MUST-FIX invoice PDF path: make "Run High-Speed Parallel Batch" work or remove it and route to the working path; state which endpoint invoice PDFs use and show it does not need the undeployed Document AI processors; run 1-2 invoice PDFs end-to-end on p7gate with grokbot (file list, progress, result). Screenshots to `1 NUMISTA.AI\BETA TEST\Grok Bot\19 OCT 26\`.
2. MUST-FIX scan root cause, using the log lines above: (a) cert-photo 403: find why the p7gate backend calls Vertex in project numista-qc with an identity that lacks `aiplatform.endpoints.predict`. Propose the fix (code config or IAM). Any IAM grant or Cloud Run setting change is infra: write it up for Grok CoS, do not apply it. (b) identify_coin_photo 56-473 s: find what blocks (retries, model name, timeouts) and cap server-side so the backend answers in 30 s or less with a clear error. Add a mocked pytest for the timeout path.
3. Text: the two sub-16px strings above to 16px+ (and plain words for the microscope description); confirm back arrow 48px with the line quoted.
4. Docs: put the CAC, 314 vs 312 (with the export code lines and grokbot counts; no deletes) and manual cert-field scope write-ups in EXECUTE_DONE.
5. Reset `_welcomeDone` on sign-out.
Rule 9.3: more than 2 files means one GEMINI38_REVIEW with code quoted, and it must check font sizes in the diff, not just assert them.

## Gates / Next
Baton to **AGCOS** for V8.18.1. After code PASS, Grok CoS rebuilds the fixed p7-gate preview from the new tip, then UX Designer + Field Tester re-gate on grokbot. No ERIC baton. Live deploy later = cherry-pick approved commits onto a branch from main, only on Eric's typed YES.