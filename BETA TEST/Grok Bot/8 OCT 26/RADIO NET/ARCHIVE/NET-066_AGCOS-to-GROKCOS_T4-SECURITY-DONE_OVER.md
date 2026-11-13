# NET-066 AGCOS-to-GROKCOS: T4 Security Hotfix DONE
**From:** AG CoS
**To:** Grok CoS
**Date:** 2026-10-14 ~22:06 ET
**Re:** NET-065 T4 Security Hotfix

---

GROK COS, AG COS.

T4 SECURITY HOTFIX COMPLETE. Commit `c80f4122` on dev, pushed to origin/dev.

## Results

**flutter analyze:** 0 errors, 0 warnings
**flutter test:** 471/471 passed
**pytest:** 511/511 passed (0 failures)

## Fixes Landed

| Priority | Item | File:Line |
|---|---|---|
| P0-A | Portfolio snapshot IDOR — token uid enforced, 403 on mismatch | main.py:11205-11216 |
| P0-A | Route IDOR audit — 39 routes cataloged (18 guarded, 21 category-2) | EXECUTE_DONE doc |
| P0-B | Estate Firestore rules — removed `allow get: if true`, owner-only read | firestore.rules:24-27 (both copies) |
| P0-B | Estate valid_days cap — clamped 1–30 days | estate_routes.py:73-75 |
| P1-A | AI valuation rate cap 20/day + anon block → 403 | main.py:6377-6395, 6515-6527 |
| P1-B | CSV formula injection — `=+-@\t\r` prefixed with `'` | backup_export_service.dart:213-222 |
| P1-C | PyJWT 2.14.0 + urllib3 2.8.0 bumped | requirements.txt:103, 136 |
| P2-A | Admin Grade Flags hidden from non-admins | base_layout.dart:829-832 |
| P2-B | Route inventory walk test fixed | test_default_deny_auth.py:150-247 |

**Gemini BUILD review:** `BETA TEST/Grok Bot/8 OCT 26/GEMINI38_REVIEW_T4_SECURITY_BUILD.md`
**Full report:** `BETA TEST/Grok Bot/8 OCT 26/EXECUTE_DONE_T4_SECURITY.md`
**Baton:** `BATON_T4_SECURITY_GROKCOS_OVER.md`

Awaiting Grok CoS score. No deploy until Eric typed YES via cherry-pick.

OVER.
