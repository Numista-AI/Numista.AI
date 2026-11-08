# BATON NET-805 - To: AG CoS v4 - PLAN ONLY: 780b Cards + 780c Images v1.2 (CoS 82 / SAG 67 FAIL on v1.1)
Source: GB CoS ~2:55 PM ET 5 Nov. Argon 96/96 PASS; CoS **82 FAIL**, SAG **67 FAIL**. Score file: `COS_SCORE_NET-791_FAILFIX-780b-780c-v1.1_20261105.md`. **Take after NET-804.**

Fix:
1. 780b nickel regex: trailing `\b` after `¢` never matches "5¢" — fix pattern + Test 3.
2. 780b: CDN CPG retail only on cards; missing → gold "Valuation Pending" chip; no unlabeled AI-value fallback (Eric 5 Nov 10:36 AM).
3. 780b: redact NGC cert `[cert no. redacted]` and demo $ figures from the plan.
4. 780c: census must match `docs/MISSING_IMAGES.csv` (2,354 / 666 / 181 / 1; all rows still missing) — delete 1,420 / 1,180 / 602 / "0 unmapped".
5. 780c: own-origin **allowlist** image guard (no denylist).
6. 780c: anchored folder-prefix excludes (bare `eric` hits 578 "American" paths); keep list in local config, not a pushed doc.
7. 780c: `tools/verify_catalog_manifest_pii.py` and `assets/catalog_image_manifest.json` are to-be-created; use `NAC1.…` keys.
8. Both: rollback section; one line each on AI-only-in-`ai_replica_images`, US-only, $0 cap, no wholesale.
**Plan A caps apply.** Locks unchanged: `origin/main` `9f04550a`, Stripe OFF, zero deploys, zero Firestore writes, no PII, no AJ data. PLAN ONLY — no execute/deploy/merge without Eric's separate YES.
**Chain:** AG files revision → Argon → GB CoS (95+) → SAG (95+) → Eric typed YES.
