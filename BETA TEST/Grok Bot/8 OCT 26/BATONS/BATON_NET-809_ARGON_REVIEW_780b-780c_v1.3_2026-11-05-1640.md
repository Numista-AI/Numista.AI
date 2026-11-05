# BATON_NET-809_ARGON_REVIEW_780b-780c_v1.3_2026-11-05-1640

- **To:** Argon (Gemini 3.8 Auditor)
- **From:** AG CoS v4 Work (`ba2bfdb2`)
- **Date:** 5 November 2026 4:40 PM ET
- **Priority:** HIGH
- **Target Files:** `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.3.md`, `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.3.md`
- **Reference Scores:** `COS_SCORE_NET-805_780b-780c-v1.2_20261105.md` (86 FAIL), `SAG_SCORE_NET-805_780b-780c-v1.2_20261105.md` (72 FAIL)
- **Status:** PLAN ONLY (Zero code execution, zero deployments, zero Firestore writes/seeding).

### Verification Checklist for Argon Review:
1. [ ] **Rollback (both plans):** Confirm `git checkout 9f04550a -- <files>` is eliminated. Confirm rollback is pinned to pre-execute `p7-v8.9` commit `a5eeb19b` via `git revert` or `git checkout a5eeb19b`. Confirm GCS invariant that deactivated manifest keys are never served.
2. [ ] **Nickel Regex Boundary (780b §4.B & §5):** Confirm negative lookbehind `(?<!\d)5¢` is specified: `RegExp(r'(?:\b5c\b|(?<!\d)5¢|\bfive cents?\b|\bnickel\b)', caseSensitive: false)`. Confirm Test 3 fails `15¢` and `25c`, and passes `5¢`, `5c`, `five cents`, and `nickel`. Confirm line 433 real `¢` citation (no mojibake claim).
3. [ ] **Valuation Chip Logic (780b §4.C):** Confirm `fmt.format(valCpg)` is displayed whenever `valCpg > 0`. Confirm gold `'Valuation Pending'` chip is rendered strictly when `valCpg <= 0`. Confirm zero suppression of real price due to pending AI/enrichment status. Confirm zero AI/melt/cost in primary slot.
4. [ ] **Image Fallback Order (780c §3.1 & §4):** Confirm strict 4-step sequence: User photo $\rightarrow$ Allowlisted own-origin URL $\rightarrow$ `CoinImageService` reference library $\rightarrow$ SVG placeholder (null allowlist does not jump straight to placeholder; Card 2 nickel resolves).
5. [ ] **Census (780c §3.2):** Confirm unverified archive counts (8,836 / 109 / 8,945) are struck. Confirm master census = exactly 3,202 (2,354 Tier 1 / 639 Tier 2 / 181 Tier 3 / 1 Tier 4 / 27 Tier 5 Excluded).
6. [ ] **$0.00 Spend Cap & Tooling Label:** Confirm bulk mirroring is removed from this YES; confirm hard abort before any storage mutation call. Confirm `tools/verify_catalog_manifest_pii.py` is labeled "create, then run".
7. [ ] **Locks:** Confirm `origin/main` locked at `9f04550a`, Stripe OFF, zero deploys, zero Firestore writes.

Please review and score `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.3.md` and `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.3.md`.
Review chain: Argon (Gemini 3.8) -> Grok Bot CoS (>=95) -> Stand Alone Grok (SAG, >=95) -> Founder Eric typed YES.
