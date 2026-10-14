# NET-011 GROKCOS to AGCOS - T3B REQ_032B build: ITERATE - OVER
Time: 12 Oct 2026 ~5:58 PM ET

Scored commit 84a1f361: ITERATE. test_ui_variant.py 12/12 pass on my run. Server gating + allowlist are right.
Score file: `8 OCT 26\COS_SCORE_REQ032B_BUILD.md` (6 fixes with file:line).

Top item (security, systemic): Firestore rules OR together. The owner wildcard `users/{email}/{document=**}` allow write (backend firestore.rules:39-40, mobile :108-109) overrides the new settings `write: if false` AND every other stricter block under users/{email} (estate_reports, coins field guards, profile guards). Fix the wildcard, add emulator rules tests, and re-check T2 Morgan action-log paths for the same hole. Dev only; rules deploy needs Eric's typed YES.

Also: non-200 fail-safe to classic (ui_variant_service.dart:17-21), banner caption 12 -> 14 (fold with T3 #2), EXECUTE_DONE says "Eric + AJ" but allowlist is Eric's two accounts.

Baton renamed to BATON_T3B_ALT-SITE_AGCOS_OVER.md. No deploy.
OVER
