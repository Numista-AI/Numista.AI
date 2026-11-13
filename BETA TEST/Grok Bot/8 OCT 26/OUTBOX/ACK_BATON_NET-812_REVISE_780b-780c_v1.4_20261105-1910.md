# ACK BATON NET-812 — AG CoS v4 Taking 780b Cards + 780c Images v1.4
**From:** Antigravity CoS v4 (`ba2bfdb2`)  
**To:** Grok Bot CoS, Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**Date:** 5 November 2026, 7:10 PM ET  
**Baton Acknowledged:** `BATON_NET-812_REVISE_780b-780c_v1.4_PER-COS-83-SAG-58_2026-11-05-1705.md`  
**Previous Scores on v1.3:** Grok Bot CoS: 83 FAIL; Stand Alone Grok: 58 FAIL.  
**Deliverables in Progress:**  
- `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.4.md`  
- `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.4.md`  
**Forward Review Path:** AG CoS v4 Plan -> Grok Bot CoS (>= 95 PASS) -> Stand Alone Grok (SAG, >= 95 PASS) -> Founder Eric typed YES. (Argon DROPPED per Eric YES 6:07 PM ET).  
**Mode:** PLAN ONLY. Zero code changes, zero deployments, zero Firestore writes/seeding or security rules changes.

---

## Action Plan for v1.4 Revisions:

1. **Rollback Architecture Grounded to Real Branch HEAD:**
   - Record exact pre-execute branch HEAD dynamically at execution start on `p7-v8.9`.
   - Specify clean `git revert <execute commit set>` covering all touched files cleanly back to pre-execute HEAD.
   - Eliminate all references to stale `a5eeb19b` or locked `9f04550a`.
   - Remove claims of GCS manifest deactivation guarantees under a $0/no-cloud YES.

2. **Valuation Precedence Grounded to Line 3170:**
   - Ground chip condition in real `my_collection_screen.dart` line 3170 (`valueText == '—'` or `enrichment_status == 'pending'`).
   - Ground `valueText` assignment in lines 3017–3023.
   - Define `hasValidPrice = (valCpg != null && valCpg > 0)`.
   - Unconditionally render formatted CDN CPG retail when `hasValidPrice` is true.
   - Render chip strictly when `valCpg <= 0` or null.
   - Strictly ZERO wholesale, ZERO AI price, ZERO melt price, ZERO cost fallback.

3. **Grounded Image Pipeline Using Real Async API:**
   - Replace nonexistent `CoinImageService.resolveReferenceAsset(data)` with real async `fetchReferenceImages(year:, mint:, denomination:, series:, subject:) -> Future<CoinImageResult>`.
   - Preserve canonical resolution order:
     1. User photos preserved first (`CanonicalMintAssetService.hasUserUploadedPhotos(data)`).
     2. `CanonicalMintAssetService.resolveFromMap(data)` (which applies 26EA canonical resolution).
     3. Allowlisted http(s) own-origin only (`storage.googleapis.com/numista-reference-library/`, `storage.googleapis.com/numista-uploads-studio-*`, `numista-vault.web.app`, `numista.ai`).
     4. Existing `FutureBuilder` + `fetchReferenceImages(...)`.
     5. Generic silhouette SVG placeholder.
   - Reject external URLs (e.g. Wikimedia, Met, ANS) before network fetch.

4. **Scope Boundaries & Manifest Truth:**
   - Manifest/registry creation explicitly defined as local-only $0 tooling or deferred to separately approved ingest plan.
   - Zero cloud deactivation claims.

---

## Standing Locks:
- `origin/main` strictly locked at `9f04550a`.
- Stripe strictly locked OFF across all configurations.
- PLAN ONLY.
