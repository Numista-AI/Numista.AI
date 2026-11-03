# GEMINI 3.8 REVIEW — `FAILFIX_PLAN_NET-748_AG_v2.md` Against `BATON_NET-750`

- **Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer / Gemini 3.8 Code & Build Auditor)
- **Timestamp:** `2026-11-03T11:06:00-05:00` (ET)
- **Plan Under Review:** [`FAILFIX_PLAN_NET-748_AG_v2.md`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/FAILFIX_PLAN_NET-748_AG_v2.md) (written `10:42:20 AM ET`, 3 minutes *before* [`BATON_NET-750_AG_NET-748-FIXONLY-v2_FINAL-AG-TRY_20261103-1045.md`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/BATON_NET-750_AG_NET-748-FIXONLY-v2_FINAL-AG-TRY_20261103-1045.md) was posted at `10:45 AM ET`)
- **Authorizing Batons:** [`BATON_NET-749_ARGON_REVIEW_NET-748-FAILFIX-v1_20261103-1022.md`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/BATON_NET-749_ARGON_REVIEW_NET-748-FAILFIX-v1_20261103-1022.md) & [`BATON_NET-750_AG_NET-748-FIXONLY-v2_FINAL-AG-TRY_20261103-1045.md`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/BATON_NET-750_AG_NET-748-FIXONLY-v2_FINAL-AG-TRY_20261103-1045.md)
- **Score:** **86 / 100 — UPDATE `FAILFIX_PLAN_NET-748_AG_v2.md` IN-PLACE TO SATISFY `BATON_NET-750` (4 Surgical Fixes Below)**

---

## 1. Timing Note: Why `AG CoS v4` Should Update `FAILFIX_PLAN_NET-748_AG_v2.md` In-Place for `BATON_NET-750`

`AG CoS v4` wrote `FAILFIX_PLAN_NET-748_AG_v2.md` at `10:42:20 AM ET` in response to Argon's `10:19 AM ET` review (`GEMINI38_REVIEW_NET-748_AG_v1_2026-11-03.md`), **before** `BATON_NET-750_AG_NET-748-FIXONLY-v2_FINAL-AG-TRY_20261103-1045.md` (`10:45 AM ET`) added Grok CoS's 4 mandatory `v2` constraints.

All 5 substantive architectural fixes from Argon's `v1` review (`MF-1` through `MF-5`) are present in `v2`. However, auditing `FAILFIX_PLAN_NET-748_AG_v2.md` against `BATON_NET-750` and `flutter analyze` / `flutter test` reveals **4 surgical defects (`F2-1` through `F2-4`)** that `AG CoS v4` must patch in `FAILFIX_PLAN_NET-748_AG_v2.md` before Grok CoS and SAG score `v2` under `BATON_NET-750`:

1. **`F2-1` (`BATON_NET-749` #1 & `BATON_NET-750` #4 — `firestore.rules` Must Use Named Docs with No `{document=**}` Wildcard, and Must Be in Its Own Separate Step Gated Behind Eric's Separate Explicit YES):**
   - `FAILFIX_PLAN_NET-748_AG_v2.md:99-102` uses a recursive wildcard:
     ```javascript
     match /global_metadata/{document=**} {
       allow read:  if request.auth != null;
       allow write: if false;  // backend admin SDK only
     }
     ```
     And `FAILFIX_PLAN_NET-748_AG_v2.md:515-516` bundles `firebase deploy --only firestore:rules` directly into Gate 5 alongside the preview deploy.
   - Per `BATON_NET-749` line 5 (*"The firestore.rules change for global_metadata is READ-ONLY and as narrow as possible (named docs, no wildcard), with no path to user data"*) and `BATON_NET-750` line 9 (*"Put the firestore.rules change in its OWN separate step. Rules are project-wide and reach the LIVE site, so that step needs Eric's separate explicit YES. It is NOT preview-only. Keep it read-only and narrow"*):
     - Replace the wildcard in Gate 1 with named-document rules using the existing `isAuthenticated()` helper (`numista_mobile/firestore.rules:8-10`):
       ```javascript
       // ── Global Metadata SKU Dictionaries (Read-Only, Named Docs, No Wildcard) ──
       match /global_metadata/usmint_sku_dictionary/skus/{skuId} {
         allow get: if isAuthenticated();
         allow list, write: if false;
       }
       match /global_metadata/littleton_sku_dictionary/skus/{skuId} {
         allow get: if isAuthenticated();
         allow list, write: if false;
       }
       ```
     - Move `firebase deploy --only firestore:rules --project studio-9101802118-8c9a8` out of the `p7-gate` preview deploy into a **separate, standalone step requiring Founder Eric's separate explicit YES** (noting that `p7-gate` works immediately even *before* `firestore.rules` is deployed because `_lookupSku` falls back to `_kFallbackUsMintSkus[docId]` in `catch (e)`).

2. **`F2-2` (`flutter analyze` Compile Error in `FAILFIX_PLAN_NET-748_AG_v2.md` Gate 4F Lines 480–481 & 491–492 and Gate 4B Lines 397 & 407):**
   - **In Gate 4F (`FAILFIX_PLAN_NET-748_AG_v2.md:476-497`), `v2` writes:**
     ```dart
          setState(() {
            _skuResult = fallback;
            _skuLoading = false;
          });
     ```
     Look at the verbatim state variables in [`numista_mobile/lib/screens/add_coins_hub.dart:2578-2626`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/add_coins_hub.dart#L2578-L2626):
     ```dart
    setState(() {
      _skuSearching = true;
      _skuSearchResult = null;
      _skuError = '';
    });
    ...
      setState(() {
        _skuSearchResult = snap.data();
        _skuSearching = false;
      });
    } catch (e) {
      setState(() {
        _skuError = NumistaErrorHelper.toUserFriendly(e);
        _skuSearching = false;
      });
    }
     ```
     The state fields in `add_coins_hub.dart` are **`_skuSearchResult`** and **`_skuSearching`** (NOT `_skuResult` and `_skuLoading`), and the fallback must also check `_skuRetailer == 'US Mint'`! Using `_skuResult` / `_skuLoading` will fail `flutter analyze` with `Undefined name '_skuResult'` and `Undefined name '_skuLoading'`.
   - **In Gate 4B (`FAILFIX_PLAN_NET-748_AG_v2.md:383-416`), `v2` writes:**
     `color: AppTheme.textSecondary.withOpacity(0.5)`
     Look at the verbatim `_buildCoinImage` in [`numista_mobile/lib/screens/my_collection_screen.dart:6424-6460`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L6424-L6460):
     ```dart
  Widget _buildCoinImage(String url) {
    return Center(
      child: Container(
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          boxShadow: [
            BoxShadow(
              color: const Color(0xFFC9A227).withAlpha(40),
              blurRadius: 14,
              spreadRadius: 1,
            ),
          ],
        ),
        child: Image.network(
          url,
          fit: BoxFit.contain,
          errorBuilder: (context, error, stackTrace) => const Center(
            child: Icon(Icons.image_not_supported_outlined, size: 36, color: Color(0xFF8B92B4)),
          ),
          loadingBuilder: (context, child, progress) {
            if (progress == null) return child;
            return const Center(
              child: SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Color(0xFFC9A227),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
     ```
     Preserve the existing circular `Container` decoration and `const Icon(Icons.image_not_supported_outlined, size: 36, color: Color(0xFF8B92B4))` (do not introduce `AppTheme.textSecondary.withOpacity(0.5)`, which triggers a `deprecated_member_use` warning in `flutter analyze`).

3. **`F2-3` (Unit Test Regression in `FAILFIX_PLAN_NET-748_AG_v2.md` Gate 3E Lines 278–288 — Do Not Overwrite R2.8.19 `mayflower` Block at `canonical_mint_asset_service.dart:353-369`):**
   - In `FAILFIX_PLAN_NET-748_AG_v2.md:278-288`, `v2` replaces the existing `if (cleanTitle.contains('mayflower'))` block with `sku: '2026-QTR-MAYFLOWER'` and `fallbackObverseUrl: null`.
   - Look at the verbatim `R2.8.19` code in [`numista_mobile/lib/services/canonical_mint_asset_service.dart:353-369`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/canonical_mint_asset_service.dart#L353-L369):
     ```dart
      if (cleanTitle.contains('mayflower')) {
        final effMint = (cleanMint.isEmpty || cleanMint == 'P') ? 'P' : cleanMint;
        final obvUrl = effMint == 'D'
            ? '$_base/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Mayflower-Obverse-Unc-D.jpg'
            : '$_base/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg';
        return CanonicalMintAssetPair(
          sku: '2026-MAYFLOWER-$effMint',
          obverseUrl: obvUrl,
          reverseUrl:
              '$_base/2026_series/2026_quarter_dollar_mayflower_compact_reverse.jpg',
          fallbackObverseUrl: effMint == 'D'
              ? '$_base/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg'
              : null,
          fallbackReverseUrl: null,
          isGenuine2026: true,
        );
      }
     ```
     And look at the verbatim unit test in [`numista_mobile/test/services/canonical_mint_asset_service_test.dart:146-164`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/canonical_mint_asset_service_test.dart#L146-L164):
     ```dart
    test('Row 10 D-mint Path (R2.8.19, SAG 93 must-fix): 2026-MAYFLOWER-D fallbackObverseUrl is fully qualified with $_base', () {
      ...
      expect(pair!.sku, equals('2026-MAYFLOWER-D'));
      expect(pair.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Mayflower-Obverse-Unc-D.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_quarter_dollar_mayflower_compact_reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg'));
     ```
     Overwriting `mayflower` with `sku: '2026-QTR-MAYFLOWER'` would break test #11 (`Row 10 D-mint Path`)! Keep `canonical_mint_asset_service.dart:353-369` (`mayflower`) **100% unchanged**, and add the 4 new quarters (`declaration`, `gettysburg`, `revolutionary`, `constitution`) and `polly cooper` immediately after line 369.

4. **`F2-4` (`BATON_NET-750` #2 & #3 — Wrong `26SQRP` Image Path in Gate 2 Line 115 + Explicit Source Citations Table + `v1`-to-`v2` Change List):**
   - In `FAILFIX_PLAN_NET-748_AG_v2.md:115`, `v2` writes:
     `image: "https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/MASTER_SEMIQDJT_image_1.jpg"`
     In `canonical_mint_asset_service.dart:272`, `MASTER_SEMIQDJT_image_1.jpg` is in **`us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg`** (NOT `2026_series/`):
     ```dart
      case '26SQRP':
        return const CanonicalMintAssetPair(
          sku: '26SQRP',
          obverseUrl: '$_mintBase/2026_products/MASTER_SEMIQDJT_image_1.jpg',
          reverseUrl: '$_mintBase/2026_products/26sqrp_b.webp',
          fallbackObverseUrl: '$_mintBase/2026_products/MASTER_SEMIQDJT_image_2.jpg',
          fallbackReverseUrl: null,
          isSet: true,
          isGenuine2026: true,
        );
     ```
   - Also per `BATON_NET-750` #3 (*"Cite a source for every SKU (incl. 26SQRP) and every image mapping. Nothing invented"*), include an explicit **SKU & Asset Source Provenance Table** in Gate 2 / Gate 3 citing:
     - `numista_backend/main.py:2189-2200` (US Mint Packing Slip & Invoice Rules for `26XL`, `26EA`, `26XE`, `26SQRP`),
     - `numista_mobile/lib/services/canonical_mint_asset_service.dart:197-311` (verified R2.8.19 GCS bucket paths in `gs://numista-reference-library/reference_library/us_mint_official/2026_products/` and `2023_series/`), and
     - `gs://numista-reference-library/reference_library/2026_series/` (official U.S. Mint 2026 Semiquincentennial circulating & Native American `$1` high-res assets: `2026_one_cent_obverse/reverse.jpg`, `2026_five_cent_obverse/reverse.jpg`, `2026_quarter_dollar_{mayflower_compact,declaration_of_independence,gettysburg_address,revolutionary_war,us_constitution}_obverse/reverse.jpg`, `2026_american_innovation_obverse.jpg`, `2026_american_innovation_oneida_indian_nation_reverse.jpg` — all verified live `HTTP 200`, `2000x2000` RGB JPEG).

---

## 2. Rubric Breakdown

| Category | Max | Score | Notes |
| :--- | :---: | :---: | :--- |
| **Closure of Argon `v1` Must-Fixes (`MF-1`–`MF-5`)** | 40 | 38 | All 5 `v1` must-fixes incorporated; minus 2 for overwriting `R2.8.19` `mayflower` D-mint block (`F2-3`). |
| **`BATON_NET-750` Rule #4 (`firestore.rules` Narrow + Separate Step)** | 20 | 12 | Must replace `{document=**}` wildcard with named SKU dictionary paths (`allow get: if isAuthenticated(); allow list, write: if false;`) and isolate `firestore:rules` deploy in its own step requiring Eric's separate explicit YES (`F2-1`). |
| **Compile & Test Cleanliness (`flutter analyze` / `flutter test`)** | 20 | 16 | Must replace `_skuResult` / `_skuLoading` with `_skuSearchResult` / `_skuSearching` in `add_coins_hub.dart` and preserve `_buildCoinImage` styling in `my_collection_screen.dart` (`F2-2`). |
| **`BATON_NET-750` Rule #2 & #3 (Provenance Citations & `26SQRP` Path)** | 20 | 20 | Fix `26SQRP` path in Gate 2 line 115 to `us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg` and include provenance citations (`F2-4`). |
| **TOTAL** | **100** | **86** | **UPDATE `FAILFIX_PLAN_NET-748_AG_v2.md` IN-PLACE WITH `F2-1`..`F2-4` FOR 100/100 PASS** |
