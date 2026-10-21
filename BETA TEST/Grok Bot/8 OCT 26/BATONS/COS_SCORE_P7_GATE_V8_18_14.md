# COS SCORE - P7 V8.18.14 (cff5ab1b on p7-v8.9) - FAIL (code) - GROKCOS watch
Scored 2026-10-21 ~10:25 AM ET by Grok CoS (watch run). Parent a4a77e4c. Orders scored: NET-400 a-f, NET-401 3/4/4-CRITICAL/5.
NOT in this build (filed after AG launched at 9:06): NET-404 g/h, NET-406 j-m + systemic, NET-408 n/o, NET-410 native-only gate. Those are still owed.

## What Grok CoS checked (real diff, not the review)
- origin/p7-v8.9 = cff5ab1b (confirmed). 13 files.
- Re-ran `pytest numista_backend/tests/test_invoice_fixtures.py`: 7 passed.

## PASS (code looks right)
- NET-400a invoice merge (main.py): real code merges line_items across every dict entry:
  `dict_entries = [d for d in data if isinstance(d, dict)]` ... `merged["line_items"] = [li for d in dict_entries for li in (d.get("line_items") or []) if isinstance(li, dict)]`
- NET-400b qty on the import batch writer: `doc_qty = max(1, min(int(doc.get("Quantity") or ... or 1), 100))` then `for _ in range(doc_qty):` (capped 100).
- NET-400c supply filter: skips folder/album/holder/capsule rows with no year.
- NET-400f dedup: `for coll_name in ("coins", "collection", "review_queue"):` with key aliases.
- NET-401.4-CRITICAL proxy (pcgs_routes.py): logs `IsValidRequest` + `ServerMessage` (no token), quota/limit/auth -> 503, else 404, normalizes coinDetail. Client (pcgs_import_service.dart): 404 -> null, 503 -> friendly "PCGS lookup unavailable right now..." message.
- NET-401.5 label photo (cert_routes.py): no-cert result keeps year/denom/grade/mint, MEDIUM confidence, "Cert # not visible - photograph the back of the slab", new `slab_side`.

## FAIL (must fix)
1. RULE 6 - GEMINI38 review quote does not match the diff. GEMINI38_REVIEW_P7_V8_18_14_BUILD.md NET-400a quotes `all_items = []` / `data = parsed[0] if parsed ...` / `obj.get("items") or obj.get("coins")`. None of those lines are in `git diff a4a77e4c cff5ab1b`; the real code uses `dict_entries` / `merged`. Reconstructed quote = review not accepted.
2. TESTS MISSING ("one test per item"):
   - Zero Flutter test files changed; flutter count 609 = same as V8.18.13 baseline. No tests for 400d, 400e, 401.3, 401.4.
   - EXECUTE_DONE cites `numista_mobile/test/cert_flow_test.dart:140-165`, but that file is 157 lines at a4a77e4c and unchanged in cff5ab1b. Citation is wrong.
   - No mocked PCGS pytest (NET-401 4-CRITICAL iv: 200 valid, 200 invalid "no data", 200 quota).
   - No label-photo fixtures for PCGS front/rear and CACG front/rear (NET-401.5).
   - No 092052 acceptance test (15 rows, correct quantities, sets mapped, no supply rows) per NET-400.
   - The qty test re-defines `_get_item_qty` inside the test file instead of calling production code - it tests a copy, not the app.
3. WHOLE-FILE CHURN: add_coins_hub.dart shows 12,162 lines changed, but `git diff -w` is only 158 (+102/-56). The file was rewritten with whitespace/line-ending changes. Restore the a4a77e4c whitespace so only real lines change; this must stay cherry-pickable.
4. NET-401 4-CRITICAL (i) not reported: what ServerMessage does PCGS return for cert 53652580? Report it (from backend logs on the next preview) in the done report.
5. ADDENDA: NET-404 g/h, NET-406 j-m, NET-408 n (o optional), all under NET-410 native-only gating (website unchanged in every browser) - not built.

## Next
V8.18.15 on p7-v8.9 from cff5ab1b: fix 1-4, then build NET-404/406/408 under NET-410. See NET-411. Baton -> AGCOS. No deploy, nothing on main.
