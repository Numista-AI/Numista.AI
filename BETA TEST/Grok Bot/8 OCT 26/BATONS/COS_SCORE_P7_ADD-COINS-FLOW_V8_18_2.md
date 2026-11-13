# COS SCORE - P7 ADD-COINS-FLOW V8.18.2 BUILD
Scorer: Grok CoS (day watch) | 2026-10-19 12:50 ET | Reviewed: code `0e3c13b2` on origin/p7-v8.9 (parent 0f2f06e0) + EXECUTE_DONE_P7_V8_18_2.md + GEMINI38_REVIEW_P7_V8_18_2_BUILD.md + NET-345 + independent read of `git diff 0f2f06e0 0e3c13b2` in worktree `C:\Users\ericd\AppData\Local\Temp\p7v89_build` (3 files, +143/-44, worktree clean at 0e3c13b2).
Watch re-ran: `pytest numista_backend/tests/test_identify_timeout.py` = 4/4 PASS.
Verdict: **PASS (code).** Both code orders are done the way asked. The 314 vs 312 count item is only half explained; it moves to a P7.1 ticket and does not block the gate. Dev only. No deploys.

| # | Order (COS_SCORE V8.18.1) | Score | Independent check (0e3c13b2) |
|---|---|---|---|
| 1 | cert_routes.py project resolves like main.py, never numista-qc, pytest | **PASS** | `routes/cert_routes.py:373-379` now `os.environ.get("FIREBASE_PROJECT_ID") or os.environ.get("GOOGLE_CLOUD_PROJECT") or "studio-9101802118-8c9a8"`. Matches main.py:311 default (`studio-9101802118-8c9a8`). `test_cert_routes_project_id_never_defaults_to_numista_qc` unsets both vars, reloads the module, asserts not numista-qc. Code only, no Cloud Run/IAM change. |
| 2 | identify_coin_photo whole request 30 s or less, pass-2 test | **PASS (one note)** | `_req_start = time.monotonic()` right after auth; pass 1 `wait_for(..., GEMINI_IDENTIFY_PASS1_TIMEOUT=20)`; pass 2 gets `GEMINI_IDENTIFY_BUDGET(28) - elapsed`, skipped under 3 s, capped at `min(_pass2_budget, 10.0)`. Worst case 28 s from auth. `time` imported (main.py:28). New test sets budget 0 and proves pass 2 is skipped and pass-1 result returns 200. Note: the test covers the skip path, not a pass-2 `wait_for` that actually times out; the timeout branch is unchanged and already non-fatal, so accepted. |
| 3 | 314 vs 312: name the dropped grokbot docs (read-only) | **PARTIAL, moved to P7.1** | Named 3 set-parent docs (`Q4EOOUkUBDvBAyRB3Hmi`, `jbyU6PAR8N4OkhJLZxu4`, `myrK4XUCRnRuQwJujXna`, all 2026 Silver Proof Set, `set_contents` of 10, no item_type / is_set_parent). Read-only, no writes. But EXECUTE_DONE line 147-149 admits the math does not add up (311 + 30 = 341, not 312). Root cause of the 2-coin gap is still open. Not a code item: P7.1 ticket "grokbot count audit (getCoinQuantity + set expansion)". |
| 9.3 | GEMINI38 review with code quoted (3 files) | **PASS** | GEMINI38_REVIEW quotes before/after for cert_routes.py:374 and main.py pass-1/pass-2 blocks verbatim. |

## Gates / Next (owner Grok CoS)
1. Refresh the fixed p7-gate preview (https://numista-vault--p7-gate-8avtpz22.web.app) from tip 0e3c13b2, and the p7gate tagged backend revision with no traffic change (live stays on 00465-xx7).
2. UX Designer + Field Tester re-gate on grokbot. HARD FT items: 1-2 invoice PDFs end-to-end through "Open Invoice Importer" (file list, progress, result rows, screenshots to `19 OCT 26\`), and a CAC/PCGS cert-photo scan that answers in 30 s or less with no 403.
3. AG CoS: stand down (Rule 9.1, no timer while GROKCOS holds). No new build orders.
4. No ERIC baton yet. Live deploy later = cherry-pick approved commits onto a branch from main, only on Eric's typed YES.