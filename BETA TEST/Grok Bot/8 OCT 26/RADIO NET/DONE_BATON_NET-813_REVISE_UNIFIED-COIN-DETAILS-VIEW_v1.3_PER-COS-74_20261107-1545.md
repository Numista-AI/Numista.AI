# DONE BATON NET-813: REVISE UNIFIED COIN DETAILS VIEW v1.3 (PER CoS 74 MUST-FIXES)
**Date:** 7 November 2026, 3:45 PM ET  
**From:** Antigravity CoS v4 Work / Catalog Night Team (`ba2bfdb2`)  
**To:** Grok Bot CoS  
**Deliverable:** `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.3.md`  
**Forward Review Baton:** `BATON_NET-813_GROKCOS_REVIEW_UNIFIED-COIN-DETAILS-VIEW_v1.3_20261107-1545.md`  

## Resolution Status: ALL 7 MUST-FIXES RESOLVED
All 7 numbered blocking must-fixes from `COS_SCORE_NET-813_UNIFIED-COIN-DETAILS_v1.2_20261106.md` have been addressed and integrated in full in `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.3.md`:
1. MF-1 (Deterministic Rollback & Kill-Switch): Reverse-topological SHA revert; pre-deploy release ID clone restore; static remote JSON / query param kill-switch without Firestore writers.
2. MF-2 (Parent Identity & Navigation): Strict fail-closed on missing parent (`crw.isVirtualChild && parentDoc == null`); `UnifiedCoinNavigationContext`; Standalone Parent Mode when outside filtered list; full callback wiring.
3. MF-3 (Laws Provenance & URLs): Explicit `is_editorial_verified` schema binding; strict `isValidCongressUrl`; web semantic `<a>` anchor vs mobile `LaunchMode.externalApplication`; 4s bounded timeout.
4. MF-4 (Rich Content & Morgan Notes): Sandboxed MarkdownBody blocking outbound links & remote images; `"AI Analysis (Unverified Reference)"` label; theme-aware typography; strict `isOwnedStorageUrl` guard before any image fetch.
5. MF-5 (Value/Privacy Matrix & Public Catalog): Owner default-hidden / Show values reveal; Guest positive CPG retail always visible on Overview surface with gold "Valuation Pending" fallback; real `PublicCoinProjection` adapter for public `/catalog`.
6. MF-6 (Implementable Offline Test Suite): Complete authored `UnifiedCoinDetailHarness` test suite with 11 concrete unit/widget tests.
7. MF-7 (Standing Rules & Gates): Independent Founder YES gates for writes, rules, live deploy; US-only and zero-PII/zero-AJ-data; alerts only, never budget caps ($20/mo threshold); Catalog live target ~13 Nov $\rightarrow$ Details View preview 10–16 Nov.

Forward review baton is filed and waiting for Grok Bot CoS review.
