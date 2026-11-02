# RADIO OVER NET-730 — AG CoS v4 to ALL — NET-647 R2.8.11 MINT FAIL-FIX PLAN FILED
**Date / Time:** 2026-11-01 19:55 EST  
**Station:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3` | `eric@numista.ai` | PAYG `numista-qc`)  
**Baton:** [`BATON_NET-730_GROKCOS-ARGON_NET-647-R2.8.11-REVIEW_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/BATONS/BATON_NET-730_GROKCOS-ARGON_NET-647-R2.8.11-REVIEW_20261101.md)  

1. **Plan Filed:** [`FAILFIX_PLAN_NET-647_R2.8.11_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.11_20261101.md) (~166 KB, 1,570 lines).
2. **All Must-Fixes (`MF-A` through `MF-D`), Should-Fixes (`SF-A` through `SF-D`, Should-Fix 5, 6, 7), and Nits Surgically Resolved:**
   - **MF-A (Section 7 Verbatim Citations against `origin/dev 32d4b42e`):**
     - 7.1: [`numista_mobile/lib/screens/my_collection_screen.dart:6320-6366`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L6320-L6366) matches 100% verbatim.
     - 7.2: [`numista_mobile/lib/screens/my_collection_screen.dart:3016-3023`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L3016-L3023) matches 100% verbatim.
     - 7.3: [`numista_mobile/lib/services/coin_image_service.dart:535-571`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/coin_image_service.dart#L535-L571) matches 100% verbatim (closing brace included).
     - 7.4: [`numista_mobile/lib/screens/review_hub_screen.dart:2282-2290`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/review_hub_screen.dart#L2282-L2290) matches 100% verbatim with multi-qty calculation clearly labeled `[PROPOSED EXTENSION]`.
     - 7.5: [`numista_backend/main.py:8369-8376`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L8369-L8376) matches 100% verbatim.
   - **MF-B (Row 10 Microscope User Photo Guard):**
     - Row 10 doc `0172d0ee64284a12a8aa269ce805ec07` has `scan_source: microscope` and stored URLs under `studio-9101802118-8c9a8-uploads/microscope/eric@numista.ai/...`.
     - Implemented `hasUserUploadedPhotos(data)` guard returning `null` in `resolveFromMap` so user-uploaded photos are never overwritten.
     - Standalone test updated to assert `expect(CanonicalMintAssetService.hasUserUploadedPhotos(doc), isTrue)` and `expect(pair, isNull)` (non-destructive preservation), plus companion negative test.
   - **MF-C (Gate 4 Verification Script):**
     - Gate 4 updated with executable Python verification script asserting HTTP 200 OK, `Content-Type: image/webp`, exact byte length, and `x-goog-hash` MD5 match for all 4 staged files (`26ea_b.webp`, `26xe_b.webp`, `23rh_b.webp`, `23rh_c.webp`).
   - **MF-D (Matrix & 4.1.1 Reconciliations):**
     - Line 29 dime reverse hex MD5 corrected to `8533943d7d88a011adaf372476bfe1f3`.
     - Row 10 doc ID in matrix updated to `0172d0ee64284a12a8aa269ce805ec07`.
     - Section 4.1.1 updated to live Row 11 doc `8f2197d5d03a428db24486b4ee375a5e` (2026-D "250th Anniversary of American Independence" Half Dollar) with live MD5s `ef82afd24a5c4eeb74947958b0552e91` and `cceb4ab85d398347792d8929fb11bed0`.
     - Row 03 test fixture updated with `'Retailer Item No.': '26XL'`, `'Variety': 'Reverse Proof'` from live dump.
     - 23RH primary URLs set to live HTTP 200 composites (`2023_american_women_quarters_five_honorees_composite.jpg` and `2023_american_innovation_four_states_composite.jpg`) with staged files held behind Gate 4.
   - **Should-Fixes & Nits:**
     - SF-A: Reference library paths harmonized (108 total, 104 live 200, 4 staged in 9.1). Staging local source directory specified: `c:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\Coin Images\staged_mint_images\`.
     - SF-B: Dev tip documented as `32d4b42e` (catalog `9b55f3d9`); preview channel branch documented as `p7-v8.9` strictly.
     - SF-C: Row 4 table title updated to live title: `"2026 United States Mint Uncirculated Coin Set"`.
     - SF-D: Timestamps updated to `2026-11-01 19:55 EST`.
     - Should-Fix 5: Added `'Program / Series'` key handling (with spaces) + unit test.
     - Should-Fix 6: Removed stray ````dart` code fence at line 61.
     - Should-Fix 7: Expanded citation 7.3 to lines 535-571.
     - Nit 1: Documented Row 18 fallback obverse (`2002_Penny_Proof_Obv.png`) as a proof-for-business-strike last resort fallback.
     - Footer: Verified as `**END PLAN R2.8.11**`.
3. **Standalone Unit Test Suite:** Full suite of **43/43 PASSED (100%)** (`flutter test scratch/canonical_mint_asset_service_test.dart`). Output verbatim embedded in Section 3.2.
4. **Turn:** Baton handed to Grok CoS and Argon for re-score (`BATON_NET-730`). Threshold: $\ge 95/100$ PASS required for SAG concurrence and Gate 3 Founder Eric typed `YES`.
5. **Operating Mode:** DOCS-ONLY (`NO EXECUTE`). Zero code edits, zero builds, zero deployments. Locks: `origin/main 9f04550a`, `origin/dev 32d4b42e`, Stripe OFF. Live site HTTP 200 OK.
6. **Next in AG Queue:** NET-705 (US Catalog Site Plan).

OVER.
