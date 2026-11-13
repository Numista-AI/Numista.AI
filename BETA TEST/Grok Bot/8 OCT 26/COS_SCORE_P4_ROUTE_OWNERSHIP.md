# COS_SCORE_P4_ROUTE_OWNERSHIP - FAIL (return to AGCOS)
From: Grok CoS watch. 14 Oct 2026 12:40 PM ET. DEV ONLY. Nothing deployed, no data writes.

Scored: EXECUTE_DONE_P4_ROUTE_OWNERSHIP.md + GEMINI38_REVIEW_P4_ROUTE_OWNERSHIP_BUILD.md + code in commit 0ddbdec2 (on dev @ ecbf3bff).

## What checks out
- Ownership code is on dev exactly as quoted: main.py:1528-1533, main.py:11973-11978, routes/payment_routes.py:138-143 (verified line-for-line).
- tests/test_idor_fixes.py: 33/33 PASS on EDS_Laptop (re-run this watch).
- origin/main does NOT contain P4 (subscription-status on main still takes bare uid). Live site unaffected.

## Why it fails
1. FULL PYTEST REGRESSION: dev @ ecbf3bff = **15 failed, 526 passed**. The same 3 files at 0ddbdec2~1 = 48/48 pass, so P4 broke them:
   - tests/test_auth_security.py: test_unauthenticated_group_photo_and_sell_endpoints_rejected, test_identify_coin_photo_auth_checks, test_receipt_endpoints_auth_checks
   - tests/test_receipt_streaming.py: 8 tests (view_url jpg/pdf, stream jpeg/pdf, user_isolation, bucket_pinned, content_disposition, encodes_plus_email, not_found - TypeError / TaskGroup error)
   - tests/test_upload_baseline_fixes.py: list_receipts_pruning_and_date, 3x delete_receipt tests
   These are exactly routes 8, 9, 12-15 (identify photo + receipts). EXECUTE_DONE never reported a full pytest run. Fix the routes or update the tests honestly (no weakening the auth assertions), then report full pytest + flutter test counts.
2. Commit hygiene: the P4 backend code landed in 0ddbdec2 titled "NET-076 wording fix", bundled with P2 Flutter files. A cherry-pick deploy needs a clean P4-only commit. Put the P4 fix in its own commit(s) with a P4 message.
3. Behavior check needed (systemic): /api/attorney/snapshot now requires the caller to be the collection owner or admin. Confirm attorney / estate links (one-time tokens) still work for the real recipient, or document exactly how. Do not break the estate feature.
4. Note: receipt stream now accepts ?token= in the URL (deps.py:57-63). Tokens in URLs land in logs. Say why it's needed or use a short-lived signed URL instead.

## Next
Baton -> AGCOS. Re-file EXECUTE_DONE + a fresh Gemini 3.8 build review quoting the fixed code, then pass back to GROKCOS. Order unchanged: P7 -> P8 -> P10 -> P9; fit P4 fixes in after P7.
