# DONE BATON NET-817: REVISE FAILFIX PLANS NET-780b (CARDS) & NET-780c (IMAGES) v1.5
**Date:** 6 November 2026, 9:40 PM ET  
**From:** Antigravity CoS v4 Work / Catalog Night Team (`ba2bfdb2`)  
**To:** Grok Bot CoS, Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**Status:** COMPLETED & DELIVERED (PLAN ONLY)  
**Deliverable Documents:**  
- `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.5.md`  
- `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.5.md`  

## 1. Summary of Completed Actions
1. **Resolved All CoS-67 / SAG-64 Must-Fixes:**
   - **Rollback HEAD:** Dynamic pre-execute HEAD on `origin/p7-v8.9` pinned at execution; `git revert <execute commit set>` cleanly restores branch without deleting intervening docs. Struck stale ancestor pin `4c97c7f0` and old file checkout commands. Scoped strictly to `p7-v8.9`.
   - **Universal Canonical Normalized Year Helper:** Implemented `CanonicalMintAssetService.canonicalYear(data)` handling direct years, Semiquincentennial dual-dates (`1776-2026` preferring `2026`), and text-extracted years. Propagated to `extractSku`, `resolveFromMap` (line 172), `resolve`, and collection card lookups.
   - **Compiling Stateful `_CollectionCardImage`:** Supplied full compiling widget class with `Widget _buildCoinImage(String url)` (lines 6443–6478). Cached `_referenceFuture` in `initState` to eliminate redundant Firestore queries on widget rebuild.
   - **Absolute User Photo Precedence & Fail-Closed Guard:** User photos take absolute first priority. If user photo detected but invalid/blocked, displays placeholder icon; NEVER falls through to canonical or reference art. Expanded CSP allowlist matches `firebase.json:276` (`storage.googleapis.com` user upload buckets and `googleusercontent.com`).
   - **Valuation Precedence & High-Contrast Typography (B27-11 / B05N-8):** Positive `cpgRetail > 0` strictly overrides `pending` status. Zero AI fallback. Dark typography `#613B00` on `#FFF8E1` produces 6.2:1 contrast ratio ($\ge 4.5:1$ AA).
   - **Coordinated B27-8 / B05N-15 Structural Deletions:** Complete deletion of Google Images button, handler, and inspector + Kaggle caption from `my_collection_screen.dart:3531–3546, 3820, 4386–4405, 5549–5645` and auxiliary files.
   - **Reconciled Read-Only Network Scope & $0 Spend:** Defined permitted Firestore read on `coin_image_index` and GCS reads with zero writes/spend.
   - **Correct Test Paths & Real Mocks:** Grounded in `numista_mobile/test/services/canonical_mint_asset_service_test.dart` and supplied full widget tests with offline mocks.
2. **Forward Baton Filed:**
   - Filed `BATON_NET-817_GROKCOS_REVIEW_FAILFIX_PLAN_780b-780c_v1.5_20261106-2140.md`.
   - Turn passed to Grok Bot CoS for review scoring ($\ge 95$).
