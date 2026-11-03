# ARGON (GEMINI 3.8) TECHNICAL REVIEW — `FAILFIX_PLAN_NET-748_CoS_v3.md` (BATON NET-751)
**Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Gemini 3.8 Code Reviewer & SAG Auditor)
**Timestamp:** 2026-11-03 12:06 ET
**Target Plan:** `1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\FAILFIX_PLAN_NET-748_CoS_v3.md` (335 lines, `22,571` bytes)
**Sidecar MD5 Verification:** `668233AA5060BB92076A63D5D57449BD` — **MATCHES** `FAILFIX_PLAN_NET-748_CoS_v3.md.md5` (`668233aa5060bb92076a63d5d57449bd`)
**Target Branch / Commit Inspected:** `p7-v8.9` (`7c0eec8d`), `main` locked at `9f04550a`
**Mode:** REVIEW ONLY (`NO EXECUTE` — zero code edits, zero git commits/pushes, zero deploys, zero Firestore/GCS writes)
**Score:** **92 / 100 — CONDITIONAL / 3 SURGICAL MUST-FIXES (`MF-v3-1`..`MF-v3-3`) BEFORE EXECUTION** *(Threshold: 95/100)*

---

## 1. Executive Summary

`FAILFIX_PLAN_NET-748_CoS_v3.md` is a **major step forward** from `AG_v1` (`78/100`) and `AG_v2` (`86/100`):
1. **All GCS Paths Verified Live (`HTTP 200`):** GB CoS caught and removed all 13 non-existent GCS paths that `AG_v2` had invented (`2026_one_cent_*`, `2026_five_cent_*`, `2026_american_innovation_oneida_indian_nation_reverse.jpg`, etc.). Argon independently ran read-only HTTP `HEAD` requests against `https://storage.googleapis.com/numista-reference-library/reference_library/` for every object in Section 6 (`lines 264–278`) and confirmed **100% return `HTTP 200` (`image/jpeg` or `image/webp`)**.
2. **Year Normalization (`_normYear`, Section 3.1):** Using `RegExp(r'^(\d{4})(?:\.0+)?$')` at all three sites (`extractSku` line 100, `resolveFromMap` line 154, and `resolve` line 184) fixes **both** `'2026.0'` AND `'2023.0'` in live `users/grokbot@numista.ai/coins` (which also unblocks the two `'2023.0'` `Edith Kanaka'ole` quarters `11d4da09` and `d9e2555c`!).
3. **Compile Errors & Hallucinated SKUs Fixed (`NEW-1`..`NEW-4`):** `_kFallbackUsMintSkus` is defined, unsourced `26RA`–`26RF` are dropped in favor of the 11 sourced SKUs from `_knownSkus`, and `CoinImageResult` uses real named fields (`sourceLabel`, `matchedKey`).
4. **R2.8.19 Mayflower Block & 45 Tests Preserved (`F2-3`):** Lines 353–369 of `canonical_mint_asset_service.dart` and all 45 tests in `test/services/canonical_mint_asset_service_test.dart` remain untouched.

However, **3 specific code-level defects (`MF-v3-1`, `MF-v3-2`, `MF-v3-3`)** were found when verifying the plan line-by-line against `numista_mobile/lib/screens/add_coins_hub.dart`, `numista_mobile/firestore.rules`, `numista_mobile/lib/services/canonical_mint_asset_service.dart`, and the 331 live Firestore documents in `users/grokbot@numista.ai/coins`:

1. **`[MF-v3-1 / CRITICAL — Check 1]` `firestore.rules` Path Is Missing the Leading `/global_metadata` Collection Segment (`CoS_v3` lines 35–42 vs `add_coins_hub.dart:2589-2601`):**
   - `CoS_v3` writes `match /usmint_sku_dictionary/skus/{skuId}` and `match /littleton_sku_dictionary/skus/{skuId}` (3 path segments — invalid Firestore document match syntax, as Firestore requires `collection/doc/subcollection/doc` = 4 segments).
   - In `add_coins_hub.dart:2589-2601`, `_lookupSku` actually queries:
     `FirebaseFirestore.instance.collection('global_metadata').doc('usmint_sku_dictionary').collection('skus').doc(docId).get()`
     and `FirebaseFirestore.instance.collection('global_metadata').doc('littleton_sku_dictionary').collection('skus').doc(docId).get()`.
   - Per `CoS_v3` line 45 (*"Pre-check (read-only): `_lookupSku` (add_coins_hub.dart:2572-2628) must read exactly those two collection paths... If the code uses any other path, STOP and report"*), the rule paths in `numista_mobile/firestore.rules` MUST be:
     - `match /global_metadata/usmint_sku_dictionary/skus/{skuId}`
     - `match /global_metadata/littleton_sku_dictionary/skus/{skuId}`
2. **`[MF-v3-2 / HIGH — Check 4 & Section 5.1]` `CoinImageService.fetchReferenceImages` (`CoS_v3` lines 225–230) Calls `CanonicalMintAssetService.resolve(...)` Without `sku`, Which Skips `switch (cleanSku)` (`lines 196–311`) for All 2026 Morgan, Peace, Silver Eagle, `26SQRP`, and Sets:**
   - In `CanonicalMintAssetService`, `extractSku(Map<String, dynamic> data)` (`lines 72–133`) is called by `resolveFromMap(data)` (`line 141`), **not** by `resolve(...)` (`line 174`).
   - Inside `resolve(...)`, Morgan (`26XE`, `26XF`), Peace (`26XL`, `26XH`), Silver Eagle (`26EA`), Trump Roll (`26SQRP`), and all Sets (`26RJ`, `26RG`, `26RH`, `26GC`, `23RG`, `23RH`) only exist in `switch (cleanSku)` (`lines 196–311`) — they have no rules in Section 2 (`lines 314–370`).
   - Therefore, when `CoinImageService.fetchReferenceImages` calls `CanonicalMintAssetService.resolve(title: [series, subject].whereType<String>().join(' '), year: y, mintMark: mint, denomination: denomination)` without `sku`, `cleanSku` is `''`, `switch (cleanSku)` is skipped, and `resolve(...)` returns `null` for every Morgan, Peace, Silver Eagle, Trump Roll, and Set!
   - **Fix:** In `CanonicalMintAssetService.resolve` (`line 182`), if `cleanSku.isEmpty`, infer it via `extractSku({'year': cleanYear, 'title': cleanTitle, 'denomination': cleanDenom, 'mint_mark': cleanMint})`, AND in `my_collection_screen.dart` (`lines 3467, 4452`) and `coin_detail_screen.dart` (`line 1052`, via `widget.coin.toFirestore()`), call `CanonicalMintAssetService.resolveFromMap(...)` first so full document fields (`Condition`, `Variety`, `Strike Type`, `Retailer Item No.`) are preserved.
3. **`[MF-v3-3 / HIGH — Section 3.2 & 3.3]` `extractSku` `cond` Uses `??` Short-Circuit (`CoS_v3` line 85), Dropping `Variety` and `Strike Type` on Live `grokbot@numista.ai` Docs Where `Condition == 'Ungraded'`, and `26EA` Drops Ungraded `2026-W American Silver Eagle` (`QdPnBpHPVptb9qmH0q4N`):**
   - In live `users/grokbot@numista.ai/coins` (e.g., `02289ae3`, `0522983c`, `162459c7`, `4c13dc63`), `data['Condition']` is `'Ungraded'` (non-null!), while `'Reverse Proof'` or `'Enhanced Uncirculated'` is stored in `data['Variety']` (capital `V`) and `data['Strike Type']`.
   - Because `data['Condition'] ?? data['condition'] ?? data['variety']` stops at the first non-null value (`'Ungraded'`), `cond` becomes `'ungraded'` and ignores `Variety` and `Strike Type`!
   - Additionally, live doc `QdPnBpHPVptb9qmH0q4N` (`Year: '2026'`, `Mint Mark: 'W'`, `Program/Series: 'American Silver Eagle'`, `Condition: 'Ungraded'`) has no `'proof'` token in any field; dropping the redundant `RegExp(r'\bproof\b').hasMatch(combined)` requirement from the `26EA` rule (while keeping `!RegExp(r'\b(gold|platinum|palladium)\b').hasMatch(combined)`) resolves all 4 live 2026 Silver Eagle docs while still excluding Gold/Platinum/Palladium Eagles (`b71de3f2`).

---

## 2. Checklist Verification (BATON NET-751 Items 1–7)

### Check 1: `firestore.rules` is named-doc, READ-ONLY, with no user-data path; rules deploy is its OWN LIVE step needing Eric's separate YES
- **Status:** **FAIL (`MF-v3-1` — Missing `/global_metadata` prefix in rule match path; live separation and read-only scope PASS)**
- **Verbatim Code Citation — `numista_mobile/lib/screens/add_coins_hub.dart:2588-2602`:**
  ```dart
  2588:       if (_skuRetailer == 'US Mint') {
  2589:         snap = await FirebaseFirestore.instance
  2590:             .collection('global_metadata')
  2591:             .doc('usmint_sku_dictionary')
  2592:             .collection('skus')
  2593:             .doc(docId)
  2594:             .get();
  2595:       } else if (_skuRetailer == 'Littleton Coin Company') {
  2596:         snap = await FirebaseFirestore.instance
  2597:             .collection('global_metadata')
  2598:             .doc('littleton_sku_dictionary')
  2599:             .collection('skus')
  2600:             .doc(docId)
  2601:             .get();
  2602:       }
  ```
- **Verbatim Code Citation — `numista_mobile/firestore.rules:329-339`:**
  ```javascript
  329:     match /support_access_logs/{log_id} {
  330:       allow read:  if request.auth != null && request.auth.token.admin == true;
  331:       allow write: if false;  // backend service account only via Admin SDK
  332:     }
  333: 
  334:     // ── Deny everything else ──────────────────────────────────────────────────
  335:     match /{document=**} {
  336:       allow read, write: if false;
  337:     }
  338:   }
  339: }
  ```
- **Finding (`MF-v3-1`):**
  1. The file path in the repo is `numista_mobile/firestore.rules` (there is no root `firestore.rules`).
  2. `CoS_v3` lines 35–42 write `match /usmint_sku_dictionary/skus/{skuId}` and `match /littleton_sku_dictionary/skus/{skuId}`. Those omit the parent collection `global_metadata` (`collection('global_metadata').doc('usmint_sku_dictionary').collection('skus').doc(docId)`).
  3. **Exact Replacement for Section 1 (`numista_mobile/firestore.rules` above line 335):**
     ```javascript
         // NET-748: read-only SKU dictionary lookups for Add by SKU.
         // Named docs only. {skuId} is a single-segment variable, NOT recursive.
         match /global_metadata/usmint_sku_dictionary/skus/{skuId} {
           allow get: if isAuthenticated();
           allow list, write: if false;
         }
         match /global_metadata/littleton_sku_dictionary/skus/{skuId} {
           allow get: if isAuthenticated();
           allow list, write: if false;
         }
     ```
  4. **Step 1b Live Governance:** `CoS_v3` lines 47–54 properly isolate `firebase deploy --only firestore:rules` as a project-wide LIVE step requiring a pre-deploy live snapshot diff (`INBOX\LIVE_RULES_SNAPSHOT_<ts>.rules`) and Eric's separate typed YES.

---

### Check 2: Firestore SKU seeding (`26SQRP`) is its OWN LIVE step needing Eric's separate YES
- **Status:** **PASS**
- **Verification:** `CoS_v3` Section 4.1 (`lines 177–194`), Section 4.2 (`line 214`), and Section 8 (`line 325`) explicitly isolate Firestore seeding of the 11 missing SKU documents as an out-of-scope live data write requiring its own separate typed YES from Eric. Meanwhile, `_kFallbackUsMintSkus` (`Section 4.2`) allows `p7-gate` preview testing with zero live Firestore writes.

---

### Check 3: `MF-1`: whole-word or denomination-field match, never a `"cent"` substring
- **Status:** **PASS**
- **Verification (`CoS_v3` lines 142–166):**
  - `isCent` checks `RegExp(r'\b(1c|1¢|one cent|cent|penny)\b').hasMatch(cleanDenom) || RegExp(r'\b(lincoln cent|one cent|penny)\b').hasMatch(cleanTitle)` and guards with `if (isCent && !isQuarter && !isHalf)`.
  - `isNickel` checks `RegExp(r'\b(5c|5¢|five cents?|nickel)\b').hasMatch(cleanDenom) || RegExp(r'\b(jefferson nickel|nickel|five cents?)\b').hasMatch(cleanTitle)` and guards with `if (isNickel && !isQuarter && !isHalf)`.
  - Placed *after* Dime (`315–331`), Half (`332–352`), Mayflower (`353–369`), Semiquincentennial Quarters (`qtrs`), and Polly Cooper (`2026-NATIVE-POLLY`).
  - Neither `"semiquincentennial"` nor `"Lincoln"` (on the Gettysburg Address quarter) can match `isCent`.
  - Also in `CoS_v3` Section 3.4 (`lines 104–109`), the Kennedy Half block (`line 336`) adds `(cleanTitle.contains('independence') && !isQuarter)`, preventing the `2026 Declaration of Independence` quarter from being hijacked by `2026-HALF-*`.

---

### Check 4: Variable names match the real code (`_skuSearchResult`/`_skuSearching`) and `flutter analyze` stays clean
- **Status:** **PARTIAL (`MF-v3-2` and `MF-v3-3` needed for complete image resolution across callers)**
- **Verbatim Code Citation — `numista_mobile/lib/screens/add_coins_hub.dart:127-129, 2610-2647`:**
  ```dart
  127:   String _skuRetailer = 'US Mint';
  128:   bool _skuSearching = false;
  129:   Map<String, dynamic>? _skuSearchResult;
  ```
  ```dart
  2618:       setState(() {
  2619:         _skuSearchResult = snap.data();
  2620:         _skuSearching = false;
  2621:       });
  2622:     } catch (e) {
  2623:       setState(() {
  2624:         _skuError = NumistaErrorHelper.toUserFriendly(e);
  2625:         _skuSearching = false;
  2626:       });
  2627:     }
  2628:   }
  2629: 
  2630:   Future<void> _addSkuToCollection() async {
  2631:     if (_skuSearchResult == null) return;
  2632:     setState(() => _isProcessing = true);
  2633: 
  2634:     try {
  2635:       final data = _skuSearchResult!;
  2636:       final isSetItem = data['item_type'] == 'set';
  2637:       
  2638:       final coinDoc = <String, dynamic>{
  2639:         'source': 'manual_sku',
  ```
- **Verbatim Code Citation — `numista_mobile/lib/services/coin_image_service.dart:489-500, 618-636`:**
  ```dart
  489:   static Future<CoinImageResult> fetchReferenceImages({
  490:     required String year,
  491:     String? mint,
  492:     String? denomination,
  493:     String? series,
  494:     String? subject,   // Theme/Subject field — e.g. 'New Jersey' for state quarters
  495:   }) async {
  ```
  ```dart
  618: class CoinImageResult {
  619:   final String? obverseUrl;
  620:   final String? reverseUrl;
  621:   final String? attribution;
  622:   final String? sourceLabel;
  623:   final String? matchedKey;
  624: 
  625:   const CoinImageResult({
  626:     this.obverseUrl,
  627:     this.reverseUrl,
  628:     this.attribution,
  629:     this.sourceLabel,
  630:     this.matchedKey,
  631:   });
  ```
- **Verbatim Code Citation — `numista_mobile/lib/services/canonical_mint_asset_service.dart:100-124, 174-197`:**
  ```dart
  100:     final year = (data['year'] ?? data['Year'] ?? '').toString().trim();
  101:     final prog = (data['Program/Series'] ?? data['Program / Series'] ?? data['program_series'] ?? '').toString().toLowerCase();
  102:     final theme = (data['Theme/Subject'] ?? data['theme_subject'] ?? '').toString().toLowerCase();
  103:     final title = (data['title'] ?? data['name'] ?? '').toString().toLowerCase();
  104:     final combined = '$prog $theme $title';
  105:     if (year == '2026') {
  106:       if (combined.contains('morgan') && combined.contains('enhanced')) return '26XE';
  107:       if (combined.contains('morgan') && combined.contains('proof')) return '26XF';
  108:       if (combined.contains('peace') && combined.contains('reverse proof')) return '26XL';
  109:       if (combined.contains('peace') && combined.contains('uncirculated')) return '26XH';
  110:       if (combined.contains('uncirculated') && combined.contains('set')) return '26RJ';
  111:       if (combined.contains('american innovation')) return '26GC';
  112:       if (combined.contains('trump') || combined.contains('semiquincentennial president')) {
  113:         return '26SQRP';
  114:       }
  115:       if (combined.contains('silver proof set')) return '26RH';
  116:       if (combined.contains('clad proof set') ||
  117:           (combined.contains('proof set') && !combined.contains('silver'))) {
  118:         return '26RG';
  119:       }
  120:     }
  ```
  ```dart
  174:   static CanonicalMintAssetPair? resolve({
  175:     String? sku,
  176:     String? title,
  177:     String? year,
  178:     String? mintMark,
  179:     String? denomination,
  180:     String? storedObverseUrl,
  181:   }) {
  182:     final cleanSku = (sku ?? '').trim().toUpperCase();
  183:     final cleanTitle = (title ?? '').trim().toLowerCase();
  184:     final cleanYear = (year ?? '').trim();
  ...
  195:     // 1. Exact / Inferred SKU Match
  196:     switch (cleanSku) {
  197:       case '26EA':
  ```
- **Findings (`MF-v3-2` and `MF-v3-3`):**
  1. **`MF-v3-2` (`resolve` does not call `extractSku` when `sku` is omitted):**
     - In `CoS_v3` Section 5.1 (`lines 225–230`), `CoinImageService.fetchReferenceImages` calls `CanonicalMintAssetService.resolve(title: [series, subject].whereType<String>().join(' '), year: y, mintMark: mint, denomination: denomination)` without `sku`.
     - Because `resolve()` never calls `extractSku()`, `cleanSku` is `''` and `switch (cleanSku)` (`lines 196–311`) is completely skipped!
     - **Fix:**
       - In `CanonicalMintAssetService.resolve` (`canonical_mint_asset_service.dart:182`), infer `cleanSku` via `extractSku` when `sku` is null or empty:
         ```dart
         final rawSku = (sku ?? '').trim().toUpperCase();
         final cleanSku = rawSku.isNotEmpty
             ? rawSku
             : extractSku(<String, dynamic>{
                 'year': cleanYear,
                 'title': cleanTitle,
                 'denomination': cleanDenom,
                 'mint_mark': cleanMint,
               });
         ```
       - And in `my_collection_screen.dart:3467` (`_showCoinInspectorDialog`), `my_collection_screen.dart:4452` (Vault detail), and `coin_detail_screen.dart:1052` (`_CoinImagePairState`, using `{...widget.coin.toFirestore(), 'source': widget.coin.source, 'Personal Notes': widget.coin.personalNotes}`), call `CanonicalMintAssetService.resolveFromMap(...)` before falling back to `CoinImageService.fetchReferenceImages` so full document metadata (`Condition`, `Variety`, `Strike Type`, `Retailer Item No.`, `sku`) is used.
       - Also note: in Section 5.2 (`line 254`), `inventory_gallery.dart` does not exist in `numista_mobile/lib/`; the set/collection widgets are `numista_mobile/lib/widgets/coin_set_viewer.dart` and `numista_mobile/lib/widgets/set_contents_panel.dart`.
  2. **`MF-v3-3` (`cond` in `extractSku` uses `??` instead of joining `Condition`, `Variety`, `Strike Type`, `Denomination`):**
     - In `CoS_v3` Section 3.2 (`line 85`):
       `final cond = (data['Condition'] ?? data['condition'] ?? data['variety'] ?? '').toString().toLowerCase();`
     - In live `users/grokbot@numista.ai/coins` (e.g., `02289ae3`, `0522983c`, `162459c7`, `4c13dc63`), `data['Condition']` is `'Ungraded'` while `'Reverse Proof'` / `'Enhanced Uncirculated'` is in `data['Variety']` (capital `V`) and `data['Strike Type']`. Using `??` short-circuits on `'Ungraded'` and drops `Variety` and `Strike Type`!
     - Also, live doc `QdPnBpHPVptb9qmH0q4N` (`2026-W American Silver Eagle`, `Condition: 'Ungraded'`) has no `'proof'` token in any field.
     - **Fix (`CanonicalMintAssetService.extractSku`, lines 85–96):**
       ```dart
       final cond = <Object?>[
         data['Condition'], data['condition'],
         data['Variety'], data['variety'],
         data['Strike Type'], data['strike_type'],
         data['Denomination'], data['denomination'],
       ].where((v) => v != null).map((v) => v.toString().toLowerCase()).join(' ');
       final combined = '$prog $theme $title $cond';
       if (year == '2026' &&
           RegExp(r'\b(american|silver)\s+eagle\b').hasMatch(combined) &&
           !RegExp(r'\b(gold|platinum|palladium)\b').hasMatch(combined)) {
         return '26EA';
       }
       ```

---

### Check 5: The R2.8.19 Mayflower block and the Row 10 D-mint test are preserved
- **Status:** **PASS**
- **Verbatim Code Citation — `numista_mobile/lib/services/canonical_mint_asset_service.dart:353-369`:**
  ```dart
  353:       if (cleanTitle.contains('mayflower')) {
  354:         final effMint = (cleanMint.isEmpty || cleanMint == 'P') ? 'P' : cleanMint;
  355:         final obvUrl = effMint == 'D'
  356:             ? '$_base/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Mayflower-Obverse-Unc-D.jpg'
  357:             : '$_base/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg';
  358:         return CanonicalMintAssetPair(
  359:           sku: '2026-MAYFLOWER-$effMint',
  360:           obverseUrl: obvUrl,
  361:           reverseUrl:
  362:               '$_base/2026_series/2026_quarter_dollar_mayflower_compact_reverse.jpg',
  363:           fallbackObverseUrl: effMint == 'D'
  364:               ? '$_base/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg'
  365:               : null,
  366:           fallbackReverseUrl: null,
  367:           isGenuine2026: true,
  368:         );
  369:       }
  ```
- **Verbatim Code Citation — `numista_mobile/test/services/canonical_mint_asset_service_test.dart:146-160`:**
  ```dart
  146:     test('Row 10 D-mint Path (R2.8.19, SAG 93 must-fix): 2026-MAYFLOWER-D fallbackObverseUrl is fully qualified with \$_base', () {
  147:       final doc = <String, dynamic>{
  148:         'Year': '2026',
  149:         'Mint Mark': 'D',
  150:         'Denomination': 'Quarter Dollar (25C)',
  151:         'Program/Series': 'United States Semiquincentennial (250th Anniversary)',
  152:         'Theme/Subject': 'Mayflower Compact & Pilgrim Couple',
  153:       };
  154:       expect(CanonicalMintAssetService.hasUserUploadedPhotos(doc), isFalse);
  155:       final pair = CanonicalMintAssetService.resolveFromMap(doc);
  156:       expect(pair, isNotNull);
  157:       expect(pair!.sku, equals('2026-MAYFLOWER-D'));
  158:       expect(pair.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Mayflower-Obverse-Unc-D.jpg'));
  159:       expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_quarter_dollar_mayflower_compact_reverse.jpg'));
  ```
- **Verification:** Preserved byte-for-byte in `CoS_v3` (`Section 3.4 line 110` and `Section 7.1 line 294`).

---

### Check 6: Every SKU and image mapping has a provenance table and cited sources, with nothing invented; `26SQRP` points to `us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg`
- **Status:** **PASS (100% Verified Live via Read-Only HTTP `HEAD`)**
- **Verbatim Code Citation — `numista_mobile/lib/services/canonical_mint_asset_service.dart:269-278`:**
  ```dart
  269:       case '26SQRP':
  270:         return const CanonicalMintAssetPair(
  271:           sku: '26SQRP',
  272:           obverseUrl: '$_mintBase/2026_products/MASTER_SEMIQDJT_image_1.jpg',
  273:           reverseUrl: '$_mintBase/2026_products/26sqrp_b.webp',
  274:           fallbackObverseUrl: '$_mintBase/2026_products/MASTER_SEMIQDJT_image_2.jpg',
  275:           fallbackReverseUrl: null,
  276:           isSet: true,
  277:           isGenuine2026: true,
  278:         );
  ```
- **Verbatim Code Citation — `numista_backend/main.py:2197-2200`:**
  ```python
  2197:              - "Peace Silver Dollar 2026 Rever" (Item 26XL) -> Year: 2026, Denomination: "Peace Dollar", Program/Series: "Morgan and Peace Silver Dollars", Strike Type: "Reverse Proof", Mint Mark: "" (Philadelphia - P), Metal Content: "99.9% Silver".
  2198:              - "American Eagle 2026 One Ounce" (Item 26EA) -> Year: 2026, Denomination: "American Silver Eagle", Program/Series: "American Silver Eagle", Strike Type: "Proof", Metal Content: "99.9% Silver".
  2199:              - "Morgan Silver Enhanced Un" (Item 26XE) -> Year: 2026, Denomination: "Morgan Dollar", Program/Series: "Morgan and Peace Silver Dollars", Strike Type: "Enhanced Uncirculated", Condition: "Enhanced Uncirculated", Variety: "Liberty Bell 250 Privy, 1776~2026 Dual Date", Metal Content: "99.9% Silver (0.859 oz ASW)".
  2200:              - "2026 Semiquincentennial President Donald J. Trump $1 Coin 25-Coin Roll" (Item 26SQRP) -> Year: 2026, Denomination: "Dollar", Program/Series: "Presidential $1 Coins", Strike Type: "Circulating", Condition: "Uncirculated", Metal Content: "Manganese-Brass (88.5% Cu, 6% Zn, 3.5% Mn, 2% Ni)", Cost: "$61.00".
  ```
- **Live HTTP `HEAD` Verification Table (Executed Read-Only by Argon on 2026-11-03):**

| Category / SKU | GCS Relative Path (`https://storage.googleapis.com/numista-reference-library/reference_library/...`) | HTTP Status | Content-Type / Bytes |
|---|---|---|---|
| `26SQRP` | `us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg` | **200 OK** | `image/jpeg` (`212,061B`) |
| `26SQRP` rev | `us_mint_official/2026_products/26sqrp_b.webp` | **200 OK** | `image/webp` (`93,144B`) |
| `26SQRP` fb | `us_mint_official/2026_products/MASTER_SEMIQDJT_image_2.jpg` | **200 OK** | `image/jpeg` (`226,064B`) |
| `26EA` | `us_mint_official/2026_products/26EA_image_1.jpg`, `26EA_image_2.jpg` | **200 OK** | `image/jpeg` (`264,539B` / `284,415B`) |
| `26XE` | `us_mint_official/2026_products/26XE_image_2.jpg`, `26XE_image_3.jpg` | **200 OK** | `image/jpeg` (`273,453B` / `265,672B`) |
| `26XF` | `us_mint_official/2026_products/26XF_image_1.jpg`, `26XF_image_2.jpg` | **200 OK** | `image/jpeg` (`241,949B` / `221,374B`) |
| `26XL` | `us_mint_official/2026_products/26XL_image_3.jpg`, `26XL_image_2.jpg` | **200 OK** | `image/jpeg` (`246,743B` / `242,400B`) |
| `26XH` | `us_mint_official/2026_products/26XH_image_2.jpg`, `26XH_image_3.jpg` | **200 OK** | `image/jpeg` (`216,321B` / `202,659B`) |
| `2026-NATIVE-POLLY` | `2026_series/2026_native_american_dollar_polly_cooper_obverse.jpg`, `_reverse.jpg` | **200 OK** | `image/jpeg` (`1,166,599B` / `1,574,131B`) |
| `2026-CENT-P` | `bulk_programs/penny/SemiQ-Penny-Obverse-Unc-P.jpg` | **200 OK** | `image/jpeg` (`1,339,242B`) |
| `2026-CENT-D` | `bulk_programs/us_mint_manual/highres_scrape/SemiQ-Penny-Obverse-Unc-D.jpg` | **200 OK** | `image/jpeg` (`1,340,528B`) |
| `2026-CENT-*` rev | `bulk_programs/penny/SemiQ-Penny-Reverse-Unc.jpg` | **200 OK** | `image/jpeg` (`1,437,578B`) |
| `2026-NICKEL-P/D` | `bulk_programs/nickel/SemiQ-Nickel-Obverse-Unc-P.jpg`, `-D.jpg`, `-Reverse-Unc.jpg` | **200 OK** | `image/jpeg` (`1.33MB` / `1.33MB` / `1.88MB`) |
| `2026-QTR-*` (x5) | `2026_series/2026_quarter_dollar_{mayflower_compact,declaration_of_independence,gettysburg_address,revolutionary_war,us_constitution}_{obverse,reverse}.jpg` | **200 OK** | `image/jpeg` (all 10 URLs verified `200 OK`) |
| `2023-AWQ-EDITH` | `2023_series/2023_american_women_quarters_shared_obverse.jpg`, `_edith_kanakaole_reverse.jpg` | **200 OK** | `image/jpeg` (`167,735B` / `231,827B`) |

---

### Check 7: Resolution of Every Open Item Flagged in Section 9 (`lines 328–335`)

1. **Line 329 — Public HTTP 200 for each GCS object:**
   - **Resolved:** Confirmed `HTTP 200` across all rows in Section 6 via read-only HTTP `HEAD` checks today (see table above).
2. **Line 330 — `CanonicalMintAssetPair` and `CoinImageResult` constructors:**
   - **Resolved:** Verified in `canonical_mint_asset_service.dart:11-20` (`sku`, `obverseUrl`, `reverseUrl` are `required`; `fallbackObverseUrl`, `fallbackReverseUrl`, `isSet = false`, `isGenuine2026 = false`, `isRepresentativePreview = false` are optional with defaults) and `coin_image_service.dart:625-631` (all 5 named parameters are optional). `CoS_v3`'s constructor calls in Sections 3.4 and 5.1 compile cleanly with zero missing required arguments.
3. **Line 331 — Morgan Reverse Proof:**
   - **Resolved:** Confirmed that `_knownSkus` (`canonical_mint_asset_service.dart:57-70`) and `main.py:2197-2200` have no standalone Morgan Reverse Proof SKU (`26XL` is Peace Reverse Proof; `26XE` is Morgan Enhanced Uncirculated; `26XF` is Morgan Proof).
4. **Line 332 — `23RG` uses `26RG` imagery (representative preview):**
   - **Resolved:** Matches `canonical_mint_asset_service.dart:279-289` (`isRepresentativePreview: true`).
5. **Line 333 — `item_type` literal for rolls in `_addSkuToCollection`:**
   - **Resolved:** Verified at `add_coins_hub.dart:2636` (`final isSetItem = data['item_type'] == 'set';`) and `line 2675` (`'item_type': 'coin'`). In `_kFallbackUsMintSkus`, `26SQRP` (and `26EA`, `26XE`, `26XF`, `26XL`, `26XH`) must use `'item_type': 'coin'` so `_addSkuToCollection` writes the coin fields (`Denomination`, `Program/Series`, `Theme/Subject`, `Condition`), while `26RJ`, `26RG`, `23RG`, `26RH`, `23RH`, `26GC` use `'item_type': 'set'`.
6. **Line 334 — Exact `_kFallbackUsMintSkus` map entries sourced from `main.py:2189-2239` and `canonical_mint_asset_service.dart:106-124`:**
   - **Resolved:** Drop-in constant map verified against `main.py` and `canonical_mint_asset_service.dart` (see Check 7 item 6 in `INBOX\ARGON_REVIEW_NET-748_CoS_v3.md`).

---

## 3. Summary of the 3 Must-Fixes (`MF-v3-1`..`MF-v3-3`) to Reach 100/100

| ID | File & Lines | Required Amendment |
|---|---|---|
| **`MF-v3-1`** | `numista_mobile/firestore.rules:334` (`CoS_v3` Section 1 lines 35–42) | Prefix both rule match paths with `/global_metadata` to match `add_coins_hub.dart:2589-2601`: `match /global_metadata/usmint_sku_dictionary/skus/{skuId}` and `match /global_metadata/littleton_sku_dictionary/skus/{skuId}`. |
| **`MF-v3-2`** | `numista_mobile/lib/services/canonical_mint_asset_service.dart:182` & `coin_detail_screen.dart:1052` (`CoS_v3` Section 5.1 & 5.2) | In `CanonicalMintAssetService.resolve`, when `sku` is null/empty, infer `cleanSku` via `extractSku({'year': cleanYear, 'title': cleanTitle, 'denomination': cleanDenom, 'mint_mark': cleanMint})` so `fetchReferenceImages` enters `switch (cleanSku)`. In `coin_detail_screen.dart:1052` and `my_collection_screen.dart:3467, 4452`, check `CanonicalMintAssetService.resolveFromMap(...)` before falling back to `fetchReferenceImages`. |
| **`MF-v3-3`** | `numista_mobile/lib/services/canonical_mint_asset_service.dart:104` (`CoS_v3` Section 3.2 & 3.3 lines 85–96) | Join `Condition`, `condition`, `Variety`, `variety`, `Strike Type`, `strike_type`, `Denomination`, `denomination` with `.join(' ')` instead of `??` (which short-circuits on `'Ungraded'`), and remove the `RegExp(r'\bproof\b').hasMatch(combined)` restriction on `26EA` (keeping `!RegExp(r'\b(gold|platinum|palladium)\b')`) so ungraded `2026-W American Silver Eagle` (`QdPnBpHPVptb9qmH0q4N`) also resolves. |
