# COS SCORE - P11 SCAN-AUTH-578b374a V1 (77abbf9c)
Scored by Grok CoS, 15 Oct 2026 ~8:25 AM ET (day watch). Ref: NET-150, NET-153, GEMINI38_REVIEW_P11_SCAN_AUTH_BUILD.md.

## Result: PASS (code). Tier 1. GEMINI38_REVIEW present with code quoted (Rule 6 met).

## Checked independently (not taken from AG's report)
1. Net code diff 8391bdfa (pre-578b374a) -> 77abbf9c, main.py + routes/cert_routes.py only: the ONLY surviving changes are
   - _authenticate_request: current_user equal to dev_guest@numista.ai is discarded (falls through to strict Bearer check); is_dev_guest owner-match bypass removed from that function.
   - cert_routes.py scan_cert_number_upload: model "gemini-2.0-flash-002" -> MODEL_FLASH (routes/deps.py:36 = "gemini-3.8-flash"); import added.
   identify_coin_photo is byte-identical to pre-578b374a: unconditional `owner_key = _authenticate_request(authorization, user_email, current_user=_user)` at main.py:6125. The NET-150 skip-auth is gone.
2. `git grep _call_authenticate_request` on 77abbf9c in numista_backend: 0 hits. Wrapper fully removed.
3. GEMINI38 quotes spot-checked against the tree: main.py:6125 and 3060-3078 match.
4. Tests re-run by Grok CoS on dev 77abbf9c: pytest tests -> 558 passed (20.9s). Auth suites (test_auth_security, test_idor_fixes, test_default_deny_auth) -> 85 passed. Matches AG.
5. Prod safety: routes/deps.py get_current_user only returns dev_guest when NOT K_SERVICE/production AND ALLOW_UNAUTHENTICATED=1, so dev_guest can never reach Cloud Run. The _authenticate_request change is defense-in-depth with no live behavior change.

## Not blocking (later batch)
- N1 SYSTEMIC: 12 handlers in main.py still carry their own inline `is_dev_guest` owner-match bypass (lines ~1532, 1711, 1979, 4296, 4912, 5312, 5357, 6956, 7099, 11460, 11980). Unreachable on Cloud Run (see 5) but now inconsistent with _authenticate_request. Remove them in one pass with a test, next time main.py auth is touched.
- N2 PROCESS: project-scanner runs must commit docs/report files ONLY (explicit paths). Any code change found during a scan gets its own baton + GEMINI38_REVIEW + COS_SCORE before it lands on dev. 578b374a broke this.
- N3 cert OCR now uses gemini-3.8-flash. Not exercised live. Check one slab photo scan on the next preview channel before deploy.

## Deploy
Not urgent and no standalone deploy: live already enforces default-deny and never had 578b374a. 578b374a and 77abbf9c are now cleared to ride in the NEXT approved cherry-pick bundle, and must always be picked TOGETHER (578b374a alone re-opens the identify_coin_photo skip-auth). Deploy only on Eric's typed YES, cherry-pick onto a branch from main, never a full dev merge.
