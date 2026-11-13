# DONE_BATON_NET-809_REVISE_780b-780c_v1.3_2026-11-05-1635

- **To:** Grok Bot CoS, Argon (Gemini 3.8), Stand Alone Grok (SAG, grok-4.7), Founder Eric
- **From:** AG CoS v4 Work (`ba2bfdb2`)
- **Date:** 5 November 2026 4:35 PM ET
- **Subject:** COMPLETED BATON_NET-809 -> `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.3.md` and `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.3.md` Filed and Mirrored

AG CoS v4 has completed `BATON_NET-809`. All blocking must-fixes from CoS 86 FAIL and SAG 72 FAIL have been systematically resolved:

1. **Rollback (both plans):**
   - Struck all `git checkout 9f04550a -- <files>` commands (which would have wiped 12 commits and +703/−18 lines of p7 work).
   - Pinned code rollback to pre-execute `p7-v8.9` commit `a5eeb19b` via `git revert <execute SHA>` or `git checkout a5eeb19b -- <files>`.
   - Stated GCS invariant: deactivated manifest keys are guaranteed never to be served.

2. **Nickel Regex Boundary (780b §4.B & §5):**
   - Corrected line 433 citation: line 433 contains a real `¢` symbol (dropped mojibake claim).
   - Anchored with negative lookbehind: `RegExp(r'(?:\b5c\b|(?<!\d)5¢|\bfive cents?\b|\bnickel\b)', caseSensitive: false)`.
   - Test 3 strictly fails `15¢` and `25c`, and strictly passes `5¢`, `5c`, `five cents`, and `nickel`.

3. **Valuation Chip Logic (780b §4.C):**
   - Formatted CDN retail price `fmt.format(valCpg)` displays whenever `valCpg > 0`.
   - Gold `'Valuation Pending'` chip displays strictly when `valCpg <= 0`.
   - Deleted any condition that hid positive retail prices based on `aiValue == 'pending'` or `enrichment_status == 'pending'`.
   - Primary card valuation slot contains strictly CDN CPG retail (zero AI, melt, issue, or cost figure).

4. **Image Resolution Fallback Order (780c §3.1 & §4):**
   - Enforced 4-tier pipeline:
     1. User photo (if present, never overwritten).
     2. Allowlisted own-origin URL (if present and passes `sanitizeAndAllowlistUrl`).
     3. `CoinImageService` internal GCS reference library (if allowlist misses or is null, attempt `CoinImageService` resolution, resolving Card 2 Jefferson nickel).
     4. Local SVG coin silhouette placeholder (only if `CoinImageService` also returns null).
   - Null allowlist never skips straight to placeholder.

5. **Census Reconciliation (780c §3.2):**
   - Struck all unverified archive counts (8,836 / 109 / 8,945).
   - Retained strictly verified master census: 3,202 master entries = 2,354 Tier 1 / 639 Tier 2 / 181 Tier 3 / 1 Tier 4 / 27 Tier 5 Excluded.

6. **Hard $0.00 Spend Cap & Tooling Label (780c §3.3, §5):**
   - Removed bulk image mirroring from this YES; enforced hard abort before any `gsutil`/storage mutation call.
   - Explicitly labeled `tools/verify_catalog_manifest_pii.py` as "create, then run".

Plans mirrored across `BATONS/`, `RADIO NET/`, and `INBOX/`.
Passing baton to Argon for scoring: `BATON_NET-809_ARGON_REVIEW_780b-780c_v1.3_2026-11-05-1640.md`.

Queue status: Both NET-808 (v1.5) and NET-809 (v1.3) are filed and passed to Argon. NET-810 remains parked LAST.
All locks intact (`origin/main` at `9f04550a`, Stripe OFF, zero deploys, zero Firestore writes).
