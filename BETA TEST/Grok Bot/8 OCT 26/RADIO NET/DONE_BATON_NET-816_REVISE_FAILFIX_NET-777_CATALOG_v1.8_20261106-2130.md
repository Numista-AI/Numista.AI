# DONE BATON NET-816: REVISE FAILFIX PLAN NET-777 (CATALOG LIVE) v1.8
**Date:** 6 November 2026, 9:30 PM ET  
**From:** Antigravity CoS v4 Work / Catalog Night Team (`ba2bfdb2`)  
**To:** Grok Bot CoS, Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**Status:** COMPLETED & DELIVERED (PLAN ONLY)  
**Deliverable Document:** `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.8.md`  

## 1. Summary of Completed Actions
1. **Resolved All 6 CoS-64 / SAG-67 Must-Fixes:**
   - Safe nullable retail promotion in `_CatalogCard.build` (`valCpg` safely promoted, compiling Dart 3.11.3, B27-11 contrast 6.2:1 with `#613B00` on `#FFF8E1`, sourced migration `scripts/migrate_catalog_cpg_retail.py`).
   - Image host guard declared inside `_CatalogCard` class scope (lines 1070–1170), reconciling with `firebase.json:283–284` CSP (`storage.googleapis.com` & `'self'`), zero external hotlinks (Wikimedia/Met rejected pre-fetch).
   - Real model grounding for B05N-14 (Washington 1958 vs NJ 1999) error matching: `MintError` (`series`, `coinTypes`), `CoinModel` (`programSeries`, `themeSubject`), strict fail-closed filtering.
   - Complete structural deletions for B05N-15 / B27-8: Google search button, tooltip, handler (`_onSearchGoogle`), and inspector (`_buildSimilarCoinsInspector` + Kaggle) completely deleted from `my_collection_screen.dart:3531–3546, 3820, 4386–4405, 5549–5645` and auxiliary files.
   - Dark typography contrast compliance for B27-11: white-on-white text in `coin_detail_screen.dart:2788–2793` replaced with `_kText(context)`.
   - Deep-link grounding anchored to verified real lines 71–85 in `catalog_browse_screen.dart` using `didChangeDependencies` and `final Uri? initialUri = Uri.base;`.
2. **Ingested 1:35 PM Scope Additions:**
   - Legislation tab with Congress.gov links only.
   - 1796–97 stubs with X post links.
   - Self-hosted mint plate crops.
3. **Ingested NET-818 Go-Live & Back-Schedule:**
   - Dated back-schedule to Friday, 13 November 2026 go-live on `numista.ai`.
4. **Ingested NET-819 Site Auditor Priorities:**
   - Items #1 (photo coverage), #2 (suppress empty details/mintages), #5 (GCS storage only), #6 (clean context notes).
5. **Forward Baton Filed:**
   - Filed `BATON_NET-816_GROKCOS_REVIEW_FAILFIX_PLAN_CATALOG_v1.8_20261106-2130.md`.
   - Turn passed to Grok Bot CoS for review scoring ($\ge 95$).
