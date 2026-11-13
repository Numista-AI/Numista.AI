# ARGON TECHNICAL REVIEW: `FAILFIX_PLAN_NET-748_CoS_v4.md`

- **Reviewer:** Argon (`31035602` — Gemini 3.8 Code & Data Auditor, Review-Only)
- **Baton:** `BATON_NET-761_ARGON_REVIEW_NET-748-CoS-v4_20261104-0937.md`
- **Target Plan:** `1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\FAILFIX_PLAN_NET-748_CoS_v4.md`
  - **Lines:** `368`
  - **MD5 Verified:** `2431496EC015E7092D8B5D7BA0E5297F` (matches `BATON_NET-761` line 3)
- **Attempt Counter:** CoS v4 / Overall Attempt 11 (Fix-Only Scope per Eric's 4 Nov 2026 9:25 AM ET decision: address Argon's 3 `v3` must-fixes only, zero new scope)
- **Date:** 2026-11-04 10:42 ET
- **Score:** **98 / 100 — PASS (0 Must-Fixes)**

---

## 1. Executive Summary & Rubric Breakdown

| Category | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **1. `MF-v3-1` Resolution (Firestore Rules File Path, `/global_metadata/` Prefix, Step 1b Isolation)** | 30 | **30 / 30** | Exact file `numista_mobile/firestore.rules` (339 lines), exact `/global_metadata/...` paths matching `add_coins_hub.dart:2589-2601`, and isolated Step 1b (`firebase deploy --only firestore:rules`) requiring a separate typed YES from Eric. |
| **2. `MF-v3-2` Resolution (`resolve()` Empty-SKU Inference & 3 Detail/Modal Call-Sites)** | 30 | **30 / 30** | `canonical_mint_asset_service.dart:182` infers `cleanSku` via `extractSku(...)` when `sku` is empty; `CanonicalMintAssetService.resolveFromMap(...)` is wired ahead of `CoinImageService.fetchReferenceImages` at `my_collection_screen.dart:3467`, `my_collection_screen.dart:4452`, and `coin_detail_screen.dart:1052`; Test 20 (`line 348`) covers `resolve()` with no `sku`. |
| **3. `MF-v3-3` Resolution (Multi-Field Join in `extractSku` & `26EA` Proof Token Removal)** | 25 | **25 / 25** | `extractSku` (`canonical_mint_asset_service.dart:104`) joins all non-null `Condition`/`Variety`/`Strike Type`/`Denomination` fields instead of short-circuiting with `??`; `26EA` drops the `proof` token requirement while preserving `!RegExp(r'\b(gold|platinum|palladium)\b').hasMatch(combined)`; Test 3 (`line 331`) tests both regressions. |
| **4. Verbatim Line-Number Accuracy & Zero Scope Creep** | 15 | **13 / 15** | All Dart and Firestore rules line citations match the current `dev` workspace. (-2 non-blocking: `inventory_gallery.dart` on line 286 is inherited from `v2`/`v3` and already flagged on line 20 as non-existent in `numista_mobile/lib/`, so the implementer skips it). |
| **TOTAL** | **100** | **98 / 100** | **PASS — Ready for SAG / GB CoS Gate & Eric's Typed YES** |

---

## 2. Verification of Argon's 3 `v3` Must-Fixes (`MF-v3-1`, `MF-v3-2`, `MF-v3-3`)

### 2.1 `MF-v3-1`: Firestore Rules File Path, `/global_metadata/` Collection Prefix, and Step 1b Deploy Gate — **FIXED (`PASS`)**

1. **Plan Citations (`INBOX/FAILFIX_PLAN_NET-748_CoS_v4.md`):**
   - `FAILFIX_PLAN_NET-748_CoS_v4.md:41`:
     ```markdown
     - **File:** `numista_mobile/firestore.rules` (the repo has no root `firestore.rules`; `firebase.json` points to `numista_mobile/firestore.rules`, 339 lines, deny-all catch-all at lines 335–337).
     ```
   - `FAILFIX_PLAN_NET-748_CoS_v4.md:48-55`:
     ```javascript
     match /global_metadata/usmint_sku_dictionary/skus/{skuId} {
       allow read: if isAuthenticated();
       allow write: if false;
     }
     match /global_metadata/littleton_sku_dictionary/skus/{skuId} {
       allow read: if isAuthenticated();
       allow write: if false;
     }
     ```
   - `FAILFIX_PLAN_NET-748_CoS_v4.md:63`:
     ```markdown
     - **Step 1b — LIVE rules deploy (separate gate, requires its own typed YES from Eric):** `firebase deploy --only firestore:rules` from `numista_mobile/`. Before running: snapshot current `numista_mobile/firestore.rules` and confirm diff shows only the two `/global_metadata/*_sku_dictionary/skus/{skuId}` blocks above. No backend/Cloud Run deploy is part of Step 1b.
     ```

2. **Codebase Verification (`numista_mobile/firestore.rules` & `numista_mobile/lib/screens/add_coins_hub.dart`):**
   - `numista_mobile/firestore.rules:8-10`:
     ```javascript
         function isAuthenticated() {
           return request.auth != null;
         }
     ```
   - `numista_mobile/firestore.rules:335-337`:
     ```javascript
         match /{document=**} {
           allow read, write: if false;
         }
     ```
   - `numista_mobile/lib/screens/add_coins_hub.dart:2589-2601`:
     ```dart
           final dictDoc = _skuRetailer == 'usmint'
               ? 'usmint_sku_dictionary'
               : 'littleton_sku_dictionary';

           final docSnap = await FirebaseFirestore.instance
               .collection('global_metadata')
               .doc(dictDoc)
               .collection('skus')
               .doc(rawSku)
               .get();
     ```
   - **Verdict:** Exact match. Both dictionary paths include `/global_metadata/...`, `isAuthenticated()` is defined at lines 8–10 of `numista_mobile/firestore.rules`, and Step 1b is cleanly isolated as a separate gated step.

---

### 2.2 `MF-v3-2`: Empty-SKU Inference Inside `resolve()` & Wiring the 3 Detail/Inspector Call-Sites — **FIXED (`PASS`)**

1. **Plan Citations (`INBOX/FAILFIX_PLAN_NET-748_CoS_v4.md`):**
   - `FAILFIX_PLAN_NET-748_CoS_v4.md:190-203`:
     ```dart
     var cleanSku = (sku ?? '').trim().toUpperCase();
     if (cleanSku.isEmpty) {
       cleanSku = extractSku(<String, dynamic>{
             'year': cleanYear,
             'title': cleanTitle,
             'denomination': cleanDenom,
             'mint_mark': cleanMint,
           }) ??
           '';
     }
     ```
   - `FAILFIX_PLAN_NET-748_CoS_v4.md:287-288`:
     ```markdown
     - `numista_mobile/lib/screens/my_collection_screen.dart` — **3 call-sites:** `_CollectionCardImage` (around line 6381, already uses `resolveFromMap` — verify `obverse_image`/`reverse_image` keys are checked first), `_showCoinInspectorDialog` (around line 3467 — wire `CanonicalMintAssetService.resolveFromMap(data)` before `CoinImageService.fetchReferenceImages`), and Vault detail view (around line 4452 — wire `CanonicalMintAssetService.resolveFromMap(data)` before `CoinImageService.fetchReferenceImages`).
     - `numista_mobile/lib/screens/coin_detail_screen.dart` — `_CoinImagePairState` (around line 1052 — wire `CanonicalMintAssetService.resolveFromMap(widget.coin)` before `CoinImageService.fetchReferenceImages` at line 1071).
     ```
   - `FAILFIX_PLAN_NET-748_CoS_v4.md:348`:
     ```markdown
     20. Direct `CanonicalMintAssetService.resolve(year: 2026, title: ...)` with **no `sku` argument** for (a) Morgan Dollar, (b) Peace Dollar, (c) American Silver Eagle, (d) `26SQRP`, and (e) a set title ("2026 Congratulations Set") — first four return non-null `CanonicalMintPair`; (e) returns a set-level pair (or null) and never a single-coin pair (`MF-v3-2`).
     ```

2. **Codebase Verification (`canonical_mint_asset_service.dart`, `my_collection_screen.dart`, `coin_detail_screen.dart`):**
   - `numista_mobile/lib/services/canonical_mint_asset_service.dart:182-186`:
     ```dart
         final cleanSku = (sku ?? '').trim().toUpperCase();
         final cleanYear = year ?? _extractYear(title) ?? _extractYear(series);
         final cleanTitle = (title ?? '').trim();
         final cleanSeries = (series ?? '').trim();
         final cleanDenom = (denomination ?? '').trim();
     ```
   - `numista_mobile/lib/screens/my_collection_screen.dart:3467-3476` (Coin Inspector Dialog):
     ```dart
         final hasUserPhoto = frontUrl != null && frontUrl.isNotEmpty;
         Future<CoinImageResult?>? refImageFuture;
         if (!hasUserPhoto) {
           refImageFuture = CoinImageService.fetchReferenceImages(
             title: title,
             year: year?.toString(),
             denomination: denom,
             mintMark: mintMark,
           );
         }
     ```
   - `numista_mobile/lib/screens/my_collection_screen.dart:4452-4465` (Vault Detail View):
     ```dart
                         Builder(builder: (context) {
                           final frontUrl = d['frontImageUrl'] as String?;
                           final backUrl = d['backImageUrl'] as String?;
                           final hasPhoto = frontUrl != null && frontUrl.isNotEmpty;

                           if (!hasPhoto) {
                             return FutureBuilder<CoinImageResult?>(
                               future: CoinImageService.fetchReferenceImages(
                                 title: title,
                                 year: year,
                                 denomination: denom,
                                 mintMark: mint,
                               ),
     ```
   - `numista_mobile/lib/screens/coin_detail_screen.dart:1051-1075` (`_CoinImagePairState`):
     ```dart
       void initState() {
         super.initState();
         _obvUrl = widget.obvUrl;
         _revUrl = widget.revUrl;

         // When at least one image is missing, try tiered discovery
         if (!_hasValidUrl(_obvUrl) || !_hasValidUrl(_revUrl)) {
           _discoverImages();
         }
       }
     ...
           final result = await CoinImageService.fetchReferenceImages(
             title: widget.coinTitle,
             year: widget.year,
             denomination: widget.denomination,
             mintMark: widget.mintMark,
           );
     ```
   - **Verdict:** All 3 call-sites and `resolve()` line numbers match the Dart source verbatim, and the empty-SKU gap is completely closed.

---

### 2.3 `MF-v3-3`: Multi-Field `combined` Join in `extractSku` & Removal of `proof` Requirement on `26EA` — **FIXED (`PASS`)**

1. **Plan Citations (`INBOX/FAILFIX_PLAN_NET-748_CoS_v4.md`):**
   - `FAILFIX_PLAN_NET-748_CoS_v4.md:96-105`:
     ```dart
     final extraFields = <Object?>[
       data['Condition'], data['condition'],
       data['Variety'], data['variety'],
       data['Strike Type'], data['strike_type'],
       data['Denomination'], data['denomination'],
     ].where((v) => v != null).map((v) => v.toString().toLowerCase()).join(' ');
     final combined = '$title $series $extraFields'.toLowerCase();
     ```
   - `FAILFIX_PLAN_NET-748_CoS_v4.md:109-115`:
     ```dart
     if (combined.contains('silver eagle') &&
         !RegExp(r'\b(gold|platinum|palladium)\b').hasMatch(combined)) {
       return '26EA';
     }
     ```
   - `FAILFIX_PLAN_NET-748_CoS_v4.md:331`:
     ```markdown
     3. "2026-W American Silver Eagle Proof" → `26EA`; ungraded "2026-W American Silver Eagle" (no "Proof" in title) → `26EA`; doc with `Condition: "Ungraded"` + `Variety: "Reverse Proof"` + "2026 Quarter" → `26SQRP` (`MF-v3-3`).
     ```

2. **Codebase Verification (`numista_mobile/lib/services/canonical_mint_asset_service.dart`):**
   - `numista_mobile/lib/services/canonical_mint_asset_service.dart:100-105`:
     ```dart
         final year = data['Year'] ?? data['year'] ?? _extractYear(title);
         if (year != 2026 && year != '2026') return null;

         final combined = '$title $series'.toLowerCase();
     ```
   - **Verdict:** Joining all non-null `Condition`/`Variety`/`Strike Type`/`Denomination` entries prevents `Condition: "Ungraded"` from masking `Variety: "Reverse Proof"`, and dropping the `proof` token requirement on `26EA` preserves ungraded 2026 Silver Eagle resolution.

---

## 3. Additional Line-Number Checks Across `FAILFIX_PLAN_NET-748_CoS_v4.md`

- `numista_mobile/lib/screens/add_coins_hub.dart:127-129` (cited in `CoS_v4` Section 2.1, line 75):
  ```dart
    String _skuRetailer = 'usmint'; // 'usmint' or 'littleton'
    bool _skuSearching = false;
    Map<String, dynamic>? _skuSearchResult;
  ```
- `numista_mobile/lib/screens/add_coins_hub.dart:2638-2647` (cited in `CoS_v4` Section 5.1, line 274):
  ```dart
        final coinDoc = <String, dynamic>{
          'name': title,
          'Title': title,
          'Year': _skuSearchResult!['year'],
          'Denomination': _skuSearchResult!['denomination'] ?? '',
          'Series': _skuSearchResult!['series'] ?? '',
          'Mint Mark': _skuSearchResult!['mint_mark'] ?? '',
          'Composition': _skuSearchResult!['composition'] ?? '',
          'Condition': 'Uncirculated',
  ```
- `numista_mobile/lib/services/canonical_mint_asset_service.dart:314-352` (cited in `CoS_v4` Section 3.4, lines 135–138):
  ```dart
        if (cleanYear == 2026 && cleanTitle.isNotEmpty) {
          final lower = cleanTitle.toLowerCase();
          if (lower.contains('dime') || cleanDenom.toLowerCase().contains('10c') || cleanDenom.toLowerCase().contains('dime')) {
  ...
          if (lower.contains('half dollar') || cleanDenom.toLowerCase().contains('50c') || cleanDenom.toLowerCase().contains('half')) {
  ```
- `numista_mobile/lib/services/coin_image_service.dart:618-631` (cited in `CoS_v4` Section 4.1, lines 209–211):
  ```dart
  class CoinImageResult {
    final String? obverseUrl;
    final String? reverseUrl;
    final String source; // 'canonical_mint' | 'curated_gcs' | 'wikimedia_commons'

    const CoinImageResult({
      this.obverseUrl,
      this.reverseUrl,
      required this.source,
    });
  ```

---

## 4. Final Recommendation

- **Verdict:** **98 / 100 (`PASS`)** — Zero Must-Fixes.
- All three `v3` Must-Fixes (`MF-v3-1`, `MF-v3-2`, `MF-v3-3`) are completely resolved with zero scope creep, and all source line numbers are verified against `dev`.
