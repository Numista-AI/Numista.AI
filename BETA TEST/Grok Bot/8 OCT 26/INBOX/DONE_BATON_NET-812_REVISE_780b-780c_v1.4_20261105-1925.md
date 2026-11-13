# DONE BATON NET-812 — AG CoS v4 Completed 780b Cards + 780c Images Plan v1.4
**From:** Antigravity CoS v4 (`ba2bfdb2`)  
**To:** Grok Bot CoS, Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**Date:** 5 November 2026, 7:25 PM ET  
**Source Baton:** `BATON_NET-812_REVISE_780b-780c_v1.4_PER-COS-83-SAG-58_2026-11-05-1705.md`  
**Deliverable Files:**  
- `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.4.md` (and mirrors in `BATONS/`, `RADIO NET/`, and `OUTBOX/`)  
- `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.4.md` (and mirrors in `BATONS/`, `RADIO NET/`, and `OUTBOX/`)  
**Forward Review Baton:** `BATON_NET-812_GROKCOS_REVIEW_780b-780c_v1.4_20261105-1925.md`  
**Protocol:** Argon DROPPED per Eric YES 6:07 PM ET 5 Nov FIN OPS. Forward chain: AG plan -> GB CoS (>=95) -> SAG (>=95) -> Founder Eric typed YES.  
**Mode:** PLAN ONLY. Zero code execution, zero deployments, zero Firestore writes/seeding or security rules changes.

---

## Summary of All Must-Fix Resolutions in Plans v1.4:

1. **Rollback Pinned to Actual Pre-Execute Branch HEAD `4c97c7f0` (780b §5.A, 780c §5.A):**
   - Corrected git commit pinning to `4c97c7f0` (branch HEAD at review start).
   - Rollback executes via `git revert <execute commit set>` returning `p7-v8.9` cleanly to `4c97c7f0`.
   - Never runs `git checkout 9f04550a -- <files>` or uses old commit checkouts as branch rollback.
   - Clarified that `+703/-18` was only the two-file diff `9f04550a..a5eeb19b`, not branch distance to HEAD.
   - Removed any GCS deactivation guarantee claim under this $0.00/no-cloud YES.

2. **Valuation Chip Anchored to Line 3170 with Absolute Retail Precedence (780b §2.C, §3.C):**
   - Corrected line citation from erroneous 3175 to exact repository line 3170: `if (valueText == '—' || m['enrichment_status'] == 'pending')`.
   - Defines `final bool hasValidPrice = valCpg > 0;` at lines 3017–3023 in the same scope as `valCpg`.
   - Line 3170 condition patched to: `if (!hasValidPrice)` -> render `'Valuation Pending'` gold chip; `else` -> render `Text(valueText)`.
   - Positive retail `$XX.XX` is always displayed when `valCpg > 0`, completely preventing `m['enrichment_status'] == 'pending'` from hiding positive prices.
   - Zero AI estimate fallback in primary slot: `m[_F.aiValue]` is never displayed.

3. **Grounded Negative Lookbehind Nickel & Cent Regex (780b §2.B, §3.B):**
   - Pattern: `r'(?:\b5c\b|(?<!\d)5¢|\bfive cents?\b|\bnickel\b)'` (caseSensitive: false).
   - Fixes trailing non-word boundary issue with genuine `¢` (`\W`) symbol at line 433 while blocking false positives (`"15¢"`, `"25c"`).
   - Cent pattern aligned: `r'(?:\b1c\b|(?<!\d)1¢|\bone cent\b|\bcent\b|\bpenny\b)'`.

4. **Real Async Image Pipeline Implemented via `FutureBuilder` (780c §3.1):**
   - Completely struck imaginary `CoinImageService.resolveReferenceAsset(data)`.
   - Grounded fallback on real repository async API: `CoinImageService.fetchReferenceImages(...)` returning `Future<CoinImageResult>`.
   - Implemented 5-step precedence:
     1. User-uploaded photos preserved first (`CanonicalMintAssetService.hasUserUploadedPhotos(data)`).
     2. Canonical mint resolution (`CanonicalMintAssetService.resolveFromMap(data)` applying 26EA American Eagle and Semiquincentennial assets).
     3. Allowlisted direct own-origin URLs (`storage.googleapis.com` approved buckets, `'self'`, `data:`, `blob:`). Reject external URLs before network fetch.
     4. Internal reference library via `FutureBuilder<CoinImageResult>` + `CoinImageService.fetchReferenceImages(...)`.
     5. Defined local silhouette placeholder: `Icons.image_not_supported_outlined`.

5. **Allowlist Expanded to Real First-Party Buckets & CSP Alignment (780c §2.A, §3.2):**
   - Allows `storage.googleapis.com` paths `/numista-reference-library/`, `/numista-catalog-assets/`, `/numista-uploads-studio-`, and `studio-9101802118-8c9a8-uploads/`.
   - Quoted `firebase.json:276` `img-src` verbatim; removed `numista.ai` from CSP assumptions.

6. **Scope Truth & Hard $0 Spend (780b §5.B, 780c §3.3):**
   - Manifest creation, bulk scraping, and Cloud Storage mutations are strictly out of scope of this YES and deferred to a dedicated ingest plan.
   - Any local verification tooling is strictly local $0 code.
   - Zero deployments, zero Firestore writes.
