# NET-167 GROK CoS -> AG CoS: P7 V7 FAIL (UX + FT), V8 orders. Supersedes the NET-166 scope, which folds in here.
UX Designer (10:04 AM ET) report: screenshots in UX chat; FT report: BATONS\FT_GATE_P7_V7.md.
BLOCKERS (V8 must fix, Plan.v1 first, dev only):
1. SAFETY: Add Selected Coins POSTs with NO confirm, even in the signed-out demo. Add a confirm card listing the coins (Save/Cancel). Demo mode must never call write endpoints (client guard + a test). The backend default-deny already returns 401 for signed-out calls, so prove that with a test.
2. CORS: allow preview channels with a tight regex (see NET-166), plus a test. Explain why live spot_prices is CORS-blocked.
3. Phone layout: program cards one per row at full width; Set Collection Goal card not one character per line; check targets of 48px or more; labels 16px or larger and dark.
4. Manual entry: its own full screen, 18px dark labels, Mint Mark/Denomination not cut off, inputmode=numeric for Year/Cost/Qty, fix the Qty prefill bug (typing 1 gives 11), mark required fields, 56px Save, and the correct bottom-nav highlight.
5. Plain-English errors (no raw ClientException uri).
6. Smaller: '/assets/assets' 404 on the mint_mark_diagrams, the Firestore aggregation 403, the dashboard ',904.0|2' wrap, and the clipped 6th PIN box.
Re-gate: UX Designer + Field Tester on a new preview. Eric's YES before anything goes live.
OVER
