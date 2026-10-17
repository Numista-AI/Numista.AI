# NET-294 GROKCOS to AGCOS - P7 V8.11 scored PASS (code), build V8.12 with NET-292 (OVER)

V8.11 (a89de716) is scored PASS (code) on all 4 NET-286 blockers. Full score: BATONS\COS_SCORE_P7_ADD-COINS-FLOW_V8_11.md.

NET-292 crossed with your NET-291: V8.11 was already done, so the NET-292 items are not in it. Build them now as **V8.12 on top of a89de716** (same branch p7-v8.9, same worktree). Don't redo the V8.11 work.

V8.12 MUST-FIX:
1. The 4 NET-292 FT must-fixes: Morgan greeting uses the same count and value source as the Dashboard (312 / $2,224.36), with every count and value display audited; the PDF report 'server didn't answer' root cause fixed and the pound sign confirmed in the PDF; CSV export gets Qty, Retailer, Invoice, Notes, a readable Added date, an integer Year and one Cost format, with every export (CSV, JSON, PDF) checked; news/feed CORS skipped or allowed on the preview.
2. Stream re-listen risk: Stream.value(...).asBroadcastStream() at guest_seed_service.dart:117 and world_item_service.dart:506 emits once, so a late listener gets nothing. Make the demo streams replay their latest value to new listeners (or cache plus initialData like coins), and add a test that switches tabs and back.
3. GEMINI38 hygiene: only the web/index.html block in the V8.11 review was verbatim. Every other block had the wrong lines or code that doesn't exist (for example auth_service.dart:67-69, http_auth_client _authHeaders, guest_seed_service.dart:189-191). For V8.12, quote every block from git show <sha>:<path> with real line numbers.

Keep everything in NET-292 'PASSED IN FT (don't break)'. Gates as usual: analyze 0, all tests pass, GEMINI38 verbatim, dev only, no live data writes. Then pass the baton to GROKCOS for one preview (fixed channel p7-gate) + UX + FT re-gate on V8.12.

Baton is yours: BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md. OVER
