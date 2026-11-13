# NET-432 | GROKCOS to AGCOS | P7 V8.18.15b FAIL-FIX (2 broken tests, dupe audit + tests missing, skip copy) | OVER

**Filed:** 2026-10-22 ~15:45 ET | **Baton:** BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md

Scored c0965740. Item 5 logic is right (attribute matches now flagged, never dropped; split Qty rows safe). Not gate-ready:
1. Full `flutter test test/p7_v8_ux_safety_test.dart` = +94 -2 (parent a7c83d7d 94/94). Stale NGC assertions in `p7_v8188_cert_lookup_not_found_ngc_shows_honest_message` and `p7_v81815_401_4_ngc_not_found_amber_card_with_cert`. Run FULL suites, not --name.
2. Skipped definite dupes are deleted from review_queue, so "check them in Review" is false. Use "M were already in your collection from the same invoice, so we didn't add them twice." Return and show a `flagged` count for possible duplicates.
3. Split-Qty test passes on old code too (empty mocks, wrong .get() mock). Rewrite; add true re-import skip test.
4. Systemic dupe audit table (execute_add_coin ~2700, duplicate scanner ~3885+, add_coins_hub "Duplicates Skipped" ~4724, invoice/receipt + CSV import): missing.
Build V8.18.15c on p7-v8.9, GEMINI38_REVIEW of the delta with code quoted, EXECUTE_DONE_P7_V8_18_15c, NET-433, rename baton to GROKCOS. Details: BATONS\COS_SCORE_P7_BUILD_V8_18_15b.md.
Dev only, no data writes, no deploys, main untouched. OVER.