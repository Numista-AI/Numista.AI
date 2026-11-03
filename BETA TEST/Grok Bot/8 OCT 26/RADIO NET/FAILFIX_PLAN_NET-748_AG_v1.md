# FAILFIX PLAN NET-748 v1 (NET-746 FAILFIX: Image Pipeline + Add-by-SKU)
**Station:** AG CoS v4 / Gemini 3.8 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3` | `eric@numista.ai`)  
**Date:** 3 Nov 2026, 10:05 AM ET  
**Baton Ref:** `BATON_NET-748_AG_NET-746-FAILFIX-PLAN-ONLY_20261103-0950.md`  
**Target Channel:** `p7-gate` preview on branch `p7-v8.9`  
**Standing Locks:** `origin/main` locked at `9f04550a`; live production site untouched; Stripe locked OFF; NO EXECUTION / NO DEPLOY until Argon + CoS 95+ + SAG + Eric typed YES.

---

## 1. Executive Summary of Field Tester Failure & Direct Root Causes

Field Tester tested build `7c0eec8d` on preview channel `p7-gate` as user `grokbot@numista.ai` (`FT_RESULT_NET746_R2.8.19_7c0eec8d_FAIL.md`).
The report flagged 3 distinct failures:
1. **Broken-image icons in Collection:** Morgan Reverse Proof, Peace Reverse Proof, Morgan Enhanced Uncirculated, Polly Cooper, 2023S Set, and both Edith Kanaka'ole cards.
2. **Grey empty placeholders in Collection:** 2026P cent, 2026S Bicentennial nickel.
3. **Add-by-SKU "session expired" error:** Searching `26SQRP` displayed `"Your session expired or sign-in is required. Please sign in to continue."` while the user was actively signed in.

### Detailed Root Cause Analysis

#### A. Broken Images & Grey Placeholders
1. **Unwired Service in UI Rendering Pipeline:**
   - In Plan R2.8.19, `CanonicalMintAssetService` was implemented in `numista_mobile/lib/services/canonical_mint_asset_service.dart` with 45 unit tests, but **was never invoked anywhere in the UI**.
   - Specifically, in `numista_mobile/lib/screens/my_collection_screen.dart:6358-6364`:
     ```dart
     final obv = _cleanUrl(data[_F.imageObverse]);
     final rev = _cleanUrl(data[_F.imageReverse]);
     final directUrl = rev.isNotEmpty ? rev : obv;
     if (directUrl.isNotEmpty) {
       return _buildCoinImage(directUrl);
     }
     ```
     For users without stored direct URLs (such as `grokbot@numista.ai`), this fell through to:
     ```dart
     return FutureBuilder<CoinImageResult>(
       future: CoinImageService.fetchReferenceImages(...)
     ```
     Because `CanonicalMintAssetService.resolveFromMap(data)` was never called, none of the canonical mint image assets were provided to `_CollectionCardImage`.
2. **Firestore Float Year String (`2023.0` / `2026.0`):**
   - Inspection of `grokbot@numista.ai/coins` reveals imported CSV documents store `Year: 2023.0` and `Year: 2026.0`.
   - In `CanonicalMintAssetService:154`, year was read as `(data['year'] ?? data['Year'] ?? '').toString().trim()`.
   - The equality checks `if (cleanYear == '2023')` and `if (cleanYear == '2026')` evaluated to `false` because `"2023.0" != "2023"`. This broke resolution for both 2023 Edith Kanaka'ole cards and 2026 coins.
3. **Missing Canonical Mappings in `CanonicalMintAssetService`:**
   - `CanonicalMintAssetService` lacked mappings for:
     - 2026 Lincoln Cent (`2026_cent_collector-only_1776~2026_reverse.jpg`)
     - 2026 Jefferson Nickel (`2026_five_cents_1776~2026_dual_date_reverse.jpg`)
     - 2026 Native American Dollar - Polly Cooper (`2026_native_american_dollar_polly_cooper_reverse.jpg`)
   - `coin_image_index` in Firestore also lacked `2026_morgan-dollar_reverse`, and `CoinImageService` lacked `"polly cooper"` in `_subjectSlugMap`, causing steal-guard to suppress reverses and return empty/grey placeholders.

#### B. Add-by-SKU "Session Expired" Error
1. **Missing `firestore.rules` Permission for `global_metadata`:**
   - In `numista_mobile/lib/screens/add_coins_hub.dart:2589-2594`:
     ```dart
     snap = await FirebaseFirestore.instance
         .collection('global_metadata')
         .doc('usmint_sku_dictionary')
         .collection('skus')
         .doc(docId)
         .get();
     ```
   - In `numista_mobile/firestore.rules`, rules existed for `coin_image_index`, `coin_set_index`, and `mint_errors` (lines 189-208), but **`global_metadata` was completely missing**.
   - Any client read to `global_metadata` was caught by the default deny rule at line 335 (`match /{document=**} { allow read, write: if false; }`), throwing `FirebaseException(code: 'permission-denied')`.
   - In `numista_mobile/lib/utils/numista_error_helper.dart:81`:
     ```dart
     case 'permission-denied':
     case 'unauthenticated':
       return _signIn; // "Your session expired or sign-in is required. Please sign in to continue."
     ```
   - Thus, Firestore's rule denial masqueraded as a false "session expired" error.
2. **Missing SKU Document in Firestore:**
   - Live Firestore inspection confirmed `global_metadata/usmint_sku_dictionary/skus/26SQRP` did not exist.
3. **Absence of Client-Side Fallback Dictionary:**
   - `_lookupSku()` relied exclusively on network calls to Firestore, rather than checking known canonical SKUs in-memory first.

---

## 2. Gate-by-Gate Execution Plan (Plan Only - Awaiting Review & YES)

### Gate 1: Security Rules Patch (`firestore.rules`)
Add authenticated read access for `global_metadata` in `numista_mobile/firestore.rules` directly below `mint_errors`:
```text
    // ── Global metadata dictionaries (SKU dictionary, etc. — authenticated read) ──
    match /global_metadata/{document=**} {
      allow read: if isAuthenticated();
      allow write: if false;  // backend service account only
    }
```
**Verification:** Run `test_firestore_rules_audit.py` or unit tests ensuring authenticated clients can read `global_metadata` while writes remain blocked.

---

### Gate 2: Firestore SKU Seed for `26SQRP`
Deploy a seed script ensuring `global_metadata/usmint_sku_dictionary/skus/26SQRP` exists with canonical golden schema metadata:
```json
{
  "sku": "26SQRP",
  "name": "Donald J. Trump Semiquincentennial $1 Reverse Proof Coin",
  "description": "Donald J. Trump 45th & 47th President Semiquincentennial $1 Reverse Proof Coin",
  "year": "2026",
  "mint_mark": "",
  "denomination": "$1",
  "program": "Semiquincentennial",
  "program_series": "Semiquincentennial",
  "item_type": "coin",
  "implied_condition": "Reverse Proof",
  "retailer": "US Mint"
}
```

---

### Gate 3: Canonical Mint Asset Service Enhancements (`canonical_mint_asset_service.dart`)
1. **Normalize Year Strings:**
   Strip trailing `.0` from year inputs:
   ```dart
   final cleanYear = (year ?? '').trim().replaceAll(RegExp(r'\.0+$'), '');
   ```
2. **Add 2026 Lincoln Cent Mappings:**
   ```dart
   if (cleanYear == '2026' && (cleanTitle.contains('cent') || cleanTitle.contains('penny') || cleanDenom.contains('1c'))) {
     return const CanonicalMintAssetPair(
       sku: '2026-CENT-P',
       obverseUrl: '$_base/2026_series/2026_cent_collector-only_1776~2026_obverse.jpg',
       reverseUrl: '$_base/2026_series/2026_cent_collector-only_1776~2026_reverse.jpg',
       isGenuine2026: true,
     );
   }
   ```
3. **Add 2026 Jefferson Nickel (Bicentennial) Mappings:**
   ```dart
   if (cleanYear == '2026' && (cleanTitle.contains('nickel') || cleanTitle.contains('bicentennial') || cleanDenom.contains('5c') || cleanDenom.contains('5 cents'))) {
     return const CanonicalMintAssetPair(
       sku: '2026-NICKEL-S',
       obverseUrl: '$_base/2026_series/2026_five_cents_1776~2026_dual_date_obverse.jpg',
       reverseUrl: '$_base/2026_series/2026_five_cents_1776~2026_dual_date_reverse.jpg',
       isGenuine2026: true,
     );
   }
   ```
4. **Add 2026 Native American Dollar - Polly Cooper Mappings:**
   ```dart
   if (cleanYear == '2026' && (cleanTitle.contains('polly') || cleanTitle.contains('cooper') || cleanTitle.contains('oneida') || (cleanTitle.contains('native american') && cleanDenom.contains('dollar')))) {
     return const CanonicalMintAssetPair(
       sku: '2026-SAC-POLLY',
       obverseUrl: '$_base/2026_series/2026_native_american_dollar_polly_cooper_obverse.jpg',
       reverseUrl: '$_base/2026_series/2026_native_american_dollar_polly_cooper_reverse.jpg',
       isGenuine2026: true,
     );
   }
   ```
5. **In-Memory Canonical SKU Dictionary Helper:**
   Add `CanonicalMintAssetService.getKnownSkuData(String rawSku)` providing static golden schema dictionary maps for all 12 known US Mint SKUs (`26SQRP`, `26EA`, `26XE`, `26XL`, `26XH`, `26XF`, `26RJ`, `26GC`, `26RG`, `23RG`, `26RH`, `23RH`).

---

### Gate 4: Wire Image Resolution in UI Screens
1. **`numista_mobile/lib/screens/my_collection_screen.dart` (`_CollectionCardImage`):**
   Update lines 6358-6365:
   ```dart
   // 1. Check Canonical Mint Asset Service first (handles official 2026/2023 art & guards user uploads)
   final canonical = CanonicalMintAssetService.resolveFromMap(data);
   if (canonical != null) {
     final directUrl = canonical.reverseUrl.isNotEmpty ? canonical.reverseUrl : canonical.obverseUrl;
     if (directUrl.isNotEmpty) {
       return _buildCoinImage(directUrl);
     }
   }

   // 2. Stored direct URLs (if any)
   final obv = _cleanUrl(data[_F.imageObverse]);
   final rev = _cleanUrl(data[_F.imageReverse]);
   final directUrl = rev.isNotEmpty ? rev : obv;
   if (directUrl.isNotEmpty) {
     return _buildCoinImage(directUrl);
   }
   ```
2. **`my_collection_screen.dart` (`_showCoinInspectorDialog` & `_buildCoinFlipperDialog`):**
   Integrate `CanonicalMintAssetService.resolveFromMap(data)` so dialog views and inspection cards display obverse and reverse pairs seamlessly.
3. **`numista_mobile/lib/screens/add_coins_hub.dart` (`_lookupSku`):**
   In `_lookupSku()`:
   ```dart
   // Check local canonical dictionary first
   final localData = CanonicalMintAssetService.getKnownSkuData(rawSku);
   if (localData != null) {
     setState(() {
       _skuSearchResult = localData;
       _skuSearching = false;
       _skuError = '';
     });
     return;
   }
   ```
   This ensures `26SQRP` resolves instantly even if Firestore has latency or transient network issues.

---

### Gate 5: Verification, Tests & Build
1. **Unit Tests:**
   Update `test/services/canonical_mint_asset_service_test.dart` with test cases verifying:
   - Year `.0` stripping (`Year: 2023.0` -> matches Edith Kanaka'ole).
   - 2026 Lincoln Cent resolution.
   - 2026 Jefferson Nickel resolution.
   - 2026 Polly Cooper resolution.
   - `getKnownSkuData('26SQRP')` returns complete golden schema map.
   Run: `flutter test test/services/canonical_mint_asset_service_test.dart` -> 100% pass (expecting $\ge 50$ tests).
2. **Static Analysis:**
   Run: `flutter analyze` -> 0 issues.
3. **Deploy Scope:**
   Upon review completion and Eric's typed YES:
   - Build web release with version stamp.
   - Deploy strictly to preview channel `p7-gate` (`numista-vault--p7-gate-8avtpz22.web.app`).
   - Push code strictly to `origin/p7-v8.9`. Push docs strictly to `origin/dev`.

---

## 3. Review Checklist & Next Steps
- [x] Full root cause diagnosis covering all 3 Field Tester failure areas.
- [x] Verifiable code cites matching actual repo implementation.
- [x] Explicit plan for `firestore.rules`, `CanonicalMintAssetService`, and `add_coins_hub.dart`.
- [x] Zero code pushed / zero deploys executed.
- [x] Baton passed to Review Swarm (Argon / GB CoS / SAG) for review scoring ($\ge 95$).
