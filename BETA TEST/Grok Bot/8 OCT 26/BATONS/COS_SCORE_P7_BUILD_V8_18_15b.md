# COS_SCORE P7 BUILD V8.18.15b (c0965740) | Grok CoS

**Scored:** 2026-10-22 ~15:45 ET | **Branch:** p7-v8.9 (dev only) | **Parent:** a7c83d7d | **Tier 1** (data-loss path)

## VERDICT: FAIL-FIX (small). Core Item 5 logic is right; not ready for UX/FT gate yet.

## What I re-ran myself (AG worktree p7v89_build at 184cd215 = c0965740 + docs)
- `pytest numista_backend/tests -q`: **606 passed** (matches AG).
- `flutter test test/p7_v8_ux_safety_test.dart` (WHOLE file, not --name filter): **+94 -2 FAILED**. Parent a7c83d7d: **94/94 pass**. So c0965740 broke 2 existing tests:
  1. `p7_v8188_cert_lookup_not_found_ngc_shows_honest_message` expects text "Direct NGC cert lookup is not supported" (found 0).
  2. `p7_v81815_401_4_ngc_not_found_amber_card_with_cert` expects "Cert #99999999 (NGC) was not found" (found 0).
  Cause: Item 2 copy change; old assertions not updated. AG ran only `--name "V8.18.15b"`, and GEMINI38 review did not catch it. Rule: run the full suite before EXECUTE_DONE.

## Item scores
- Item 1 tap targets 48px (base_layout.dart:958, 1033): PASS.
- Item 2 NGC copy (add_coins_hub.dart:3753): PASS on copy; FAIL on the 2 stale tests above. Note the new NGC text no longer shows the cert number; keep that (or show "Cert #... " on a second line) and assert it in the updated tests.
- Item 3 cert photo 1024 tokens / 25s / json_repair: PASS (pytest added, green).
- Item 4 U.S. Mint invoice parsing + 60s poll: PASS (fixture pytest green).
- Item 5 dedup (main.py:3557-3605, verified in code):
  - a. Year+Mint+Denom match now commits with `possible_duplicate=True` + `duplicate_flag`, never deletes: **PASS**.
  - b. Invoice#+Item No. definite dupe ignores matches whose id is in `request.review_ids` (coin doc id == queue doc id, so split Qty rows survive even across the 490-op batch flush): **PASS in code**. Test is weak: `test_review_commit_split_invoice_qty_both_committed` mocks both coin queries as empty AND `queue_ref.document(id).get()` returns an auto-MagicMock, not mock_doc1/2, so it would pass on the OLD code too. Rewrite so the invoice query returns an existing coin whose id is in review_ids (must commit) and one whose id is not (must skip).
  - c. Snackbars use server `committed`/`skipped`: PASS on numbers. **Copy is wrong for skipped rows:** definite dupes are DELETED from review_queue (main.py batch.delete), so "check them in Review" points to nothing. Fix: "Added N coins. M were already in your collection from the same invoice, so we didn't add them twice." Also tell the user about flagged rows: return `flagged` (possible_duplicate count) from the server and add "K might be coins you already have; look for the yellow 'Possible duplicate' tag." Widget test must cover the server-response path, not just a format helper.
  - d. Systemic audit (Eric rule): **MISSING**. Not in EXECUTE_DONE or review. Required: drop-vs-flag table for main.py execute_add_coin (~2700), duplicate scanner (~3885+), add_coins_hub.dart "Duplicates Skipped" (~4724), invoice/receipt import, CSV import.
  - e. Tests: same-YMD both saved PASS; split rows weak (see b); **true re-import of same invoice+item skipped-and-reported test MISSING**.
- GEMINI38_REVIEW with quoted code: present, PASS on form; missed the 2 failing tests.

## Orders (NET-432) for V8.18.15c on p7-v8.9, dev only
1. Update the 2 stale NGC tests; full `flutter test` must be all green (report count), plus `flutter analyze lib/` 0 and full pytest.
2. Fix the skipped-row snackbar copy as above; add `flagged` count to /api/review/commit response and snackbar; widget test on a mocked 200 response.
3. Rewrite the split-Qty test (b) and add the re-import skip test (e).
4. File the systemic dupe audit (d) as a table in EXECUTE_DONE.
5. GEMINI38_REVIEW (code quoted) of the c-delta only, EXECUTE_DONE_P7_V8_18_15c, NET-433, baton to GROKCOS.
Then Grok CoS refreshes p7-gate preview and sends to UX + FT. Live main still has the silent-drop bug (main.py:3479); hotfix to main only by cherry-pick on Eric's typed YES.

Rules: dev only, no data writes, no restores, no deploys, main untouched.