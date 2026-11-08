# GB CoS SCORE — NET-809 / FAILFIX_PLAN_NET-780b_CARDS_v1.3 + 780c_IMAGES_v1.3

- Scorer: Grok Bot Chief of Staff · 2026-11-05 ~5:00 PM ET (America/New_York)
- Repo checked read-only: p7-v8.9 @ 4c97c7f0; origin/dev @ b0b05808; origin/main @ 9f04550a
- Mode: SCORE ONLY; no execute, deploy, Firestore write, rules change, main change, or Stripe change
- **CoS: 83 / 100 FAIL** (pass >=95)
- Argon: see corresponding Argon review; not treated as repo evidence
- SAG: independent xAI grok-4.7 result filed separately
- Eric YES gate: BLOCKED pending revision and independent pass

## 1. Real-code verification

| Check | Result | Evidence |
|---|---|---|
| Rollback | **PASS** | No 9f04550a checkout. Uses git revert and a5eeb19b only for uncommitted work; the +703/-18 warning matches git. |
| Nickel regex | **PASS** | Proposed (?<!\d)5¢ has no trailing word-boundary and Test 3 explicitly rejects 15¢ and 25c. Current line 433 has a genuine ¢. |
| Valuation chip | **PASS** | Proposed hasValidPrice = valCpg > 0 takes absolute precedence; chip only when false. Real defect is line 3170 (plan calls 3175). |
| Image order | **CONCEPT PASS / CODE FAIL** | Correct conceptual order user -> own-origin -> internal reference -> SVG, but calls CoinImageService.resolveReferenceAsset(data), which does not exist. Actual async API is fetchReferenceImages(year,mint,denomination,series,subject) returning CoinImageResult. |
| Own-origin allowlist | **FAIL** | Allows only numista-catalog-assets on storage.googleapis.com, but real canonical assets use numista-reference-library and user uploads use numista-uploads-studio-*. Existing user uploads would be rejected before the reference fallback. |
| Scope / census | **PARTIAL** | Correct 3202 census and no bulk GCS in this YES. Yet creation of manifest tooling is still included while storage mutations are said to be outside scope, and GCS manifest rollback is asserted without implementation. |

## 2. Breakdown

- PII/redaction & locks: 20/20
- Prior must-fix closeout: 29/35
- Real API / implementability: 9/20
- Census & no invention: 15/15
- Launch fit: 10/10
- **Total: 83/100 FAIL**

## 3. Blocking must-fixes

1. Record the actual pre-execute p7-v8.9 SHA and revert the complete execute commit set; do not use stale a5eeb19b as a branch restore or treat +703/-18 as its distance to HEAD.
2. Replace the imaginary resolveReferenceAsset call with the real async fetchReferenceImages path and map CoinImageResult obverse/reverse plus loading/error states. Keep user photos first and CanonicalMintAssetService ordering explicit.
3. Extend the allowlist to the actual approved numista-reference-library and numista-uploads-studio-* buckets before fetch; retain strict host/path validation and reject external URLs without fetching them.
4. Move manifest/registry work to its separate approved ingest plan or explain the $0 local-only boundary. Remove the guaranteed manifest-deactivation claim until that behavior is implemented and tested. Correct chip citation to line 3170.

## 4. PII and locks

No AJ PII found in the plan or supplied excerpts. origin/main remains 9f04550a; Stripe OFF. No execution or deployment performed.
