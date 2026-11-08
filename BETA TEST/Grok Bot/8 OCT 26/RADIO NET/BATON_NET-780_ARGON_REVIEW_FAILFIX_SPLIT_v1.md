# BATON NET-780 - ARGON REVIEW (Gemini 3.8) - Split Failfix Plans v1
**To:** Argon (Gemini 3.8 Reviewer)  
**From:** AG CoS v4  
**Date:** 2026-11-04 17:36 ET  
**Track:** NET-780 Split Failfix Plans Review (NET-780a, NET-780b, NET-780c, NET-780d)  
**Status:** READY FOR REVIEW - PLAN ONLY  

---

## 1. Review Objectives
Please review the four surgical fail-fix plans authored under Founder Eric's 4:58 PM split amendment:
1. `FAILFIX_PLAN_NET-780a_BUILD-STAMP_v1.md`: Injecting `git_commit` and `build_time` into `version.json`.
2. `FAILFIX_PLAN_NET-780b_CARDS_v1.md`: Resolving the 2 broken cards (`26EA`, `2023-NICKEL-D/P`) and AE 'Pending' price fallback.
3. `FAILFIX_PLAN_NET-780c_IMAGES_v1.md`: Eric's 4-tier image source order (own scrubbed first, mirror remainder, real counts 28/2, PII gate, CSP fix).
4. `FAILFIX_PLAN_NET-780d_SPLASH_v1.md`: Decoupling Cloud Run network wait & asset optimization to drop splash latency from ~40s to < 1.5s.

---

## 2. Review Criteria (Rule 6 Compliance)
1. Verify each citation contains verbatim code matching real repo files and line numbers.
2. Confirm strict PLAN ONLY adherence (zero code changes, zero deploys, `origin/main` locked at `9f04550a`).
3. Confirm Step 1b live Firestore rules deploy and SKU dictionary seed remain on strict HOLD.
4. Verify machine-checkable Rule 8 commands are specified.

Output file: `ARGON_REVIEW_NET-780_FAILFIX_SPLIT_v1.md`.
