# COS_SCORE - P7 ADD-COINS-FLOW V8.18.6
Scorer: Grok CoS | 19 Oct 2026 ~4:35 PM ET | Commit 4c42d1f5 on p7-v8.9 (parent 4531f45d) | Order: NET-357

## VERDICT: PASS (code) - go to preview refresh + UX/FT re-gate

Diff 4531f45d..4c42d1f5 touches 3 backend files only (main.py +96/-18, cert_routes.py 1 line, test_cert_lookup.py +142). Flutter code is unchanged from 4531f45d (595/0 re-run at V8.18.5 still stands). Grok CoS re-ran `pytest tests/test_cert_lookup.py` on 4c42d1f5 = 20 passed.

| # | NET-357 item | Grade | Evidence |
|---|---|---|---|
| 2a | Shared reader runs concurrently, inside budget | PASS | main:6247-6254 `cert_task = asyncio.create_task(_extract_cert_with_budget(bytes_a, mime_type=mime_a, timeout=_cert_budget_a))` started before pass 1; helper uses `asyncio.wait_for(asyncio.to_thread(extract_cert_from_image, ...), timeout=timeout)` (event loop not blocked). Task cancelled on all 3 pass-1 error branches. Await at merge uses `asyncio.wait_for(cert_task, timeout=_rem_cert_budget)`. |
| 2b | Image B only with >= 3 s left | PASS | `if not cert_read.get("cert_number") and not single_image_mode and bytes_b:` then `_rem_b >= 3.0` check, timeout = `_rem_b`. |
| 2c | Shared reader cert wins | PASS | `if shared_cert: final_cert = shared_cert; final_service = shared_service or pass_service` else pass2/pass1 fallback. Old `if not final_cert:` synchronous block deleted. |
| 2d | Friendly message, no raw exception | PASS | cert_routes:454 `"Scan failed — please enter cert # manually."`; bonus: pass-1 500 detail is now "AI identification failed. Please try again." (no `{e}`). Exceptions logged server-side only. |
| T-a | pytest pass1 X vs shared Y | PASS | `test_shared_cert_reader_wins_over_pass1`: both `/api/scan_cert_number_upload` and `/api/identify_coin_photo` return 53652580 / PCGS over pass-1 PASS1-CERT-11111. |
| T-b | pytest reader sleeps past budget | PARTIAL (test is vacuous) | `test_shared_cert_reader_budget_timeout_no_500` sets budget 0.4 s, but the task only starts `if _cert_budget_a > 0.5`, so slow_extract is never called (Grok CoS scratch run: 0 calls). The test passes without touching the timeout path. |
| V | Grok CoS behavior proof (scratch, not committed) | PASS | Budget 1.2 s, reader blocks 3.0 s, pass-1 returns cert P1X. In one event loop (httpx ASGITransport): response 200 in 1.22 s, reader called once, cert falls back to P1X, log "Shared cert reader await non-fatal error". So the budget really holds in production code. (Note: the same check via TestClient measured 3.2 s only because TestClient's loop shutdown joins the still-sleeping worker thread; not a server-side delay.) |
| R | GEMINI38 quotes real lines | PASS | Spot-checked main:6249-6253 and cert_routes:454 against `git diff 4531f45d 4c42d1f5`: verbatim. Gemini did not catch the vacuous T-b test. |
| H | Hygiene | PASS | EXECUTE_DONE_P7_V8_18_6.md filed. Pushed to origin/p7-v8.9 only. No main touch, no deploy. |

## P7.1 tickets (no work now)
1. Fix T-b: use a budget above 0.5 s (e.g. 1.2 s) with a reader that sleeps longer, assert the reader was called once and the response came back near the budget (measure with httpx AsyncClient + ASGITransport, not TestClient).
2. Cost: two-photo raw (no-slab) coins now make up to 2 extra Gemini cert calls (A, then B). Consider skipping B when pass 1 says grading_service None.
3. Carry-overs: no-camera error-card layout nit (V8.18.5), 314 vs 312 count gap (V8.18.2).

## Next
Baton GROKCOS_WILCO. AG stands down (Rule 9.1). Grok CoS refreshes the p7-gate preview (one fixed channel) + tagged backend from 4c42d1f5, then UX Designer + Field Tester re-gate on grokbot. HARD items: invoice PDFs end-to-end, camera on the preview with camera=(self), cert-photo scan under 30 s, preview console shows no localhost:8443 on hub load. Live deploy only by cherry-pick onto a branch from main, on Eric's typed YES.