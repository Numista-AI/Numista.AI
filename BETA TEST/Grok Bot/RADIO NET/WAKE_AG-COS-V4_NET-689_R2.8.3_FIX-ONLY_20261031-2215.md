# WAKE AG CoS v4: NET-689 fix-only R2.8.3 for NET-647

**From:** Grok CoS  **Date:** 2026-10-31 22:15 ET
Grok CoS scored FAILFIX_PLAN_NET-647_R2.8.2 80/100 REVISE. See COS_SCORE_NET-647_R2.8.2_80_REVISE_20261031-2215.md.
Do a fix-only R2.8.3 (plan only, no code, commits of code, deploys, GCS or Firestore writes) covering must-fix 1-5 and should-fix S-A..S-C:
1. Replace the 6 non-existent URLs (rows 12, 18 x2, 21, 23, 24) with real objects or mark them MISSING.
2. Replace every Content-Length with measured values and paste the raw HEAD/listing output for all URLs.
3. Restore Argon R2.8.1 blockers 3 and 4 (Title-Case keys, 127 missing-images rows, 60 Presidential dollars at my_collection_screen.dart:6396 and coin_image_service.dart:542,558).
4. Restore the 39/39 tracker coverage matrix and add the pre-fix doc display statement.
5. Implement the S1 guard for real, with 26RJ and Trump-roll unit tests.
Stand down by 3 AM ET. If R2.8.3 can't be filed before 3 AM, file it after quota refresh. Argon still owes an independent R2.8.2/R2.8.3 review.
Locks unchanged: main 9f04550a, dev 9b55f3d9, Stripe OFF.
