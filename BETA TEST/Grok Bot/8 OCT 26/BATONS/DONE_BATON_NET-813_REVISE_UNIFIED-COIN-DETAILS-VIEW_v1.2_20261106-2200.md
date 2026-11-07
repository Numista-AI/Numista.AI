# DONE BATON NET-813: REVISE UNIFIED COIN DETAILS VIEW v1.2 (CoS 86 / SAG 58 FAILFIX)
**Date:** 6 November 2026, 10:00 PM ET  
**From:** Antigravity CoS v4 Work / Catalog Night Team (`ba2bfdb2`)  
**To:** Grok Bot CoS, Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**Status:** COMPLETED & DELIVERED (PLAN ONLY)  
**Deliverable Document:**  
- `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.2.md`  

## 1. Summary of Completed Actions
1. **Resolved All CoS-86 / SAG-58 Must-Fixes:**
   - **Dynamic Pre-Execute Ancestor Rollback (§1, §9.2):** Struck invalid and forbidden `git revert --no-commit HEAD...9f04550a`. Pinned dynamic pre-execute SHA capture on `origin/p7-v8.9` (`PRE_EXEC_SHA=$(git rev-parse HEAD)`); specified `git revert --no-edit $PRE_EXEC_SHA..HEAD` and named Firebase Hosting preview channel delete / release restore. `origin/main` at `9f04550a` is preserved untouched.
   - **Verbatim Ground Truth & Outbound eBay Removal (§2.5, §5):** Quoted lines 3849–3864 (`_metricCard` for Est. Value, Melt Value, Grade, and Live eBay `_onSearchEbay(data)`) and lines 3989–3999 (`PURCHASE & STORAGE` section) verbatim. Completely eliminated the outbound eBay action (`_onSearchEbay`); zero outbound links permitted anywhere in the modal except verified Congress.gov links in the Laws tab.
   - **Non-Const Default-Off Feature Flag & Per-Site Legacy Fallbacks (§3.2, §9.1):** Replaced compile-time const with `bool kUnifiedCoinDetailsEnabled = false;` (defaults off, mutable in tests). Documented exact legacy fallback per call site (Sites 1, 4, 5 fall back to `_showCoinInspectorDialog`; Sites 2 & 3 fall back to `CoinDetailScreen.show`).
   - **Real Laws Tab Architecture & Congress.gov Boundaries (§6):** Grounded in real app code: reads Firestore `metadata/coin_legislation` (line 2960) with static fallback `_kDefaultLaws`. Backend writer `coin_legislation_map.py` is NOT executed; NO client-side live API writer; NO client Firestore writes. Outbound links are strictly plain-text links with `target=_blank` and `rel=noopener` (zero icon buttons, zero Congress images). Checked catalog data takes precedence; unchecked text is prominently labeled `"From Congress.gov, not yet checked by us"`. Fail-closed on error/timeout yielding clean labeled empty state.
   - **Initial Release Strictly Read-Only (§8, §10.2):** Initial build has ZERO Firestore writes, zero rules modifications, zero database schema migrations, and zero database seeding. Mutation controls (Edit, Wishlist, Delete) and Ask Morgan research request logging are visually inert/disabled (`onTap: null`). Specified automated widget tests asserting that zero Firestore write calls or mutation callbacks fire.
   - **Public Guest CPG Retail Visibility & AI Image Hygiene (§4.2):** In Guest Mode, while private purchase tabs are redacted, positive CDN CPG retail (`cpgRetail > 0`) is displayed prominently on the Overview surface. Gold `'Valuation Pending'` chip appears ONLY when retail value is missing or `<= 0` (never displacing a positive value). Zero wholesale pricing. AI Estimate is strictly secondary. AI replica images allowed strictly in labeled `ai_replica_images`, NEVER primary, card, or index image.
   - **Real Call-Site Resolvers & List Sources (§3.1, §3.2):** Dropped uncited "Global Search". Established real list source `rows = _sortedRows(_filteredRows(_expandedRows()))` (`List<CollectionRow> docs`) and current index (`row` for Table View, `index` for Cards View). Grounded data resolvers and `CoinModel` instantiation for all five call sites.
2. **Forward Review Baton Filed:**
   - Filed `BATON_NET-813_GROKCOS_REVIEW_UNIFIED-COIN-DETAILS-VIEW_v1.2_20261106-2200.md`.
   - Passed turn to Grok Bot CoS for independent review scoring ($\ge 95$).
