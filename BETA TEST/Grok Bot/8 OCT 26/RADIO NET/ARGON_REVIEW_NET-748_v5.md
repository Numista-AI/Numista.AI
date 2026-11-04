# ARGON TECHNICAL REVIEW: `NET-748_v5_PLAN.md` (Overall Attempt 12)

- **Reviewer:** Argon (`31035602` — Gemini 3.8 Code & Data Auditor, Review-Only)
- **Baton:** `BATON_NET-770_ARGON_REVIEW_NET-748_v5_2026-11-04-1405.md`
- **Target Plan:** `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\NET-748_v5_PLAN.md` (`428` lines, read in full in this turn)
- **Companion Inputs Read in This Turn:**
  - `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\SAG_PREVIEW_NET-748_v5.md` (`19` lines)
  - `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\SAG_SCORE_NET-748_v5.md` (`14` lines — `96/100 PASS`, `0` must-fixes)
- **Workspace Baseline Checked in This Turn:**
  - `C:\Users\ericd\Documents\MyVertexProject\.git\HEAD:1`: `ref: refs/heads/p7-v8.9`
  - `C:\Users\ericd\Documents\MyVertexProject\.git\refs\heads\p7-v8.9:1`: `ca4e3d33c20f8084e27b0d2fb7159f8ea01bd307`
- **Date:** 2026-11-04 15:20 ET
- **Score:** **96 / 100 — PASS (0 Must-Fixes)**

---

## 1. Executive Summary & Score Breakdown

| Category | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **1. Closure of SAG `v4` `MF-1` (Case-Folding Rebuttal + Test 21) & `MF-2` (Pinned Step 1b Rules Target, SHA-256, Emulator STOP, Rollback)** | 35 | **35 / 35** | `canonical_mint_asset_service.dart` lines 101–103, 183, 185–193 already fold case before every matcher; Test 21 (`line 362`) guards mixed/upper-case + lowercase mint `"d"`. Step 1b (`lines 58-78`) pins cwd, `--project studio-9101802118-8c9a8`, SHA-256 across diff/test/deploy, `firestore.rules.test.js` emulator STOP, and a single rollback procedure. |
| **2. Baseline Drift Verification (`p7-v8.9` at `ca4e3d33` vs `7c0eec8d`)** | 35 | **34 / 35** | Every file length, line number, and code anchor cited in `NET-748_v5_PLAN.md` was opened and read directly at `ca4e3d33` in this turn and holds verbatim (Section 2 below). (-1: Section 3.5 line 204 says both `"Replace line 182"` and `"(place it after cleanYear/cleanTitle/cleanDenom/cleanMint are computed)"` — must be placed after line 193). |
| **3. Evaluation of SAG's 4 Advisories (`SAG_SCORE_NET-748_v5.md` lines 9–12)** | 30 | **27 / 30** | All 4 SAG advisories are sound implementation guards (weighed in Section 3 below, including pinning `--project studio-9101802118-8c9a8` and cwd on `firebase hosting:channel:deploy p7-gate` and verifying the exact `extractSku` lines 106–123 & switch lines 196–311). |
| **TOTAL** | **100** | **96 / 100** | **PASS — Concur with SAG `96/100 PASS` (0 Must-Fixes)** |

---

## 2. Task 1 & Task 2: Baseline Drift Audit at `p7-v8.9` (`ca4e3d33`) — Direct Verbatim Quotes

Every quote below is copied directly from files opened in this turn at `p7-v8.9` (`ca4e3d33c20f8084e27b0d2fb7159f8ea01bd307`).

### 2.1 `numista_mobile/firestore.rules` (339 lines), `firebase.json`, and `firestore.rules.test.js`
- **Plan citation (`INBOX/NET-748_v5_PLAN.md:39-54`):**
  ```markdown
  39: File: `numista_mobile/firestore.rules` (339 lines). The `isAuthenticated()` helper is at lines 8-10. The deny-all `match /{document=**}` is at lines 335-337. There's no existing rule for the dictionaries.
  40: 
  41: Insert directly **above line 335** (inside the `match /databases/{database}/documents` block):
  42: 
  43: ```
  44:     // NET-748: read-only SKU dictionary lookups for Add by SKU.
  45:     // Named docs only. {skuId} is a single-segment variable, NOT recursive.
  46:     match /global_metadata/usmint_sku_dictionary/skus/{skuId} {
  47:       allow get: if isAuthenticated();
  48:       allow list, write: if false;
  49:     }
  50:     match /global_metadata/littleton_sku_dictionary/skus/{skuId} {
  51:       allow get: if isAuthenticated();
  52:       allow list, write: if false;
  53:     }
  54: ```
  ```
- **Actual source (`C:\Users\ericd\Documents\MyVertexProject\numista_mobile\firestore.rules:8-10` and `334-339`):**
  ```javascript
  8:     function isAuthenticated() {
  9:       return request.auth != null && !request.auth.token.firebase.sign_in_provider.matches('anonymous');
  10:     }
  ```
  ```javascript
  334:     // ── Deny everything else ──────────────────────────────────────────────────
  335:     match /{document=**} {
  336:       allow read, write: if false;
  337:     }
  338:   }
  339: }
  ```
- **Actual source (`C:\Users\ericd\Documents\MyVertexProject\numista_mobile\firebase.json:1-5`):**
  ```json
  1: {
  2:   "firestore": {
  3:     "rules": "firestore.rules",
  4:     "indexes": "firestore.indexes.json"
  5:   },
  ```
- **Actual source (`C:\Users\ericd\Documents\MyVertexProject\numista_mobile\firestore.rules.test.js:19-26`):**
  ```javascript
  19: const { initializeTestEnvironment, assertFails, assertSucceeds } =
  20:   require("@firebase/rules-unit-testing");
  21: const { doc, setDoc, updateDoc, getDoc } = require("firebase/firestore");
  22: const fs = require("fs");
  23: const path = require("path");
  24: 
  25: const PROJECT_ID = "studio-9101802118-8c9a8";
  26: const RULES_PATH = path.join(__dirname, "firestore.rules");
  ```
  - **Verification:** Anchor lines `8-10` and `335-337` hold at `ca4e3d33`. Note for Step 1b item 3 (`NET-748_v5_PLAN.md:71`): when adding test case `(c) authenticated getDocs (list) on .../skus`, also add `collection, getDocs` to the import on `firestore.rules.test.js:21`.

---

### 2.2 `numista_mobile/lib/screens/add_coins_hub.dart` (6,239 lines)
- **Actual source (`C:\Users\ericd\Documents\MyVertexProject\numista_mobile\lib\screens\add_coins_hub.dart:126-130`):**
  ```dart
  126:   final _skuCtrl = TextEditingController();
  127:   String _skuRetailer = 'US Mint';
  128:   bool _skuSearching = false;
  129:   Map<String, dynamic>? _skuSearchResult;
  130:   String _skuError = '';
  ```
- **Actual source (`C:\Users\ericd\Documents\MyVertexProject\numista_mobile\lib\screens\add_coins_hub.dart:2439-2446`):**
  ```dart
  2439:   Widget _buildSkuPreviewCard() {
  2440:     if (_skuSearchResult == null) return const SizedBox.shrink();
  2441:     final data = _skuSearchResult!;
  2442:     final name = data['name'] ?? data['description'] ?? 'Unnamed Item';
  2443:     final year = data['year'] ?? data['year']?.toString() ?? 'N/A';
  2444:     final program = data['program'] ?? data['program_series'] ?? 'N/A';
  2445:     final isSet = data['item_type'] == 'set';
  ```
- **Actual source (`C:\Users\ericd\Documents\MyVertexProject\numista_mobile\lib\screens\add_coins_hub.dart:2572-2648` and `2652, 2675`):**
  ```dart
  2572:   Future<void> _lookupSku() async {
  ...
  2586:       final docId = rawSku.replaceAll(RegExp(r'[^a-zA-Z0-9\-]'), '_').toUpperCase();
  2587: 
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
  ...
  2610:       if (!snap.exists) {
  2611:         setState(() {
  2612:           _skuError = 'SKU "$rawSku" not found in $_skuRetailer dictionary.';
  2613:           _skuSearching = false;
  2614:         });
  2615:         return;
  2616:       }
  ...
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
  2640:         'Added': FieldValue.serverTimestamp(),
  2641:         'created_at': FieldValue.serverTimestamp(),
  2642:         'committed_at': FieldValue.serverTimestamp(),
  2643:         'deep_dive_status': 'PENDING',
  2644:         // ITEM 6: stamp is_demo: false so real coins remain visible after display filter ships
  2645:         'is_demo': false,
  2646:         'is_demo_cleared': false,
  2647:       };
  ```
  - **Verification:** Every line number in `NET-748_v5_PLAN.md` Section 2 (`127-129`, `2440-2445`, `2572-2628`, `2589-2601`, `2610-2616`, `2622-2627`, `2630`, `2636`, `2638-2647`, `2652`, `2675`) matches `add_coins_hub.dart` at `ca4e3d33` verbatim.

---

### 2.3 `numista_mobile/lib/services/canonical_mint_asset_service.dart` (545 lines)
- **Actual source (`C:\Users\ericd\Documents\MyVertexProject\numista_mobile\lib\services\canonical_mint_asset_service.dart:11-20`):**
  ```dart
  11:   const CanonicalMintAssetPair({
  12:     required this.sku,
  13:     required this.obverseUrl,
  14:     required this.reverseUrl,
  15:     this.fallbackObverseUrl,
  16:     this.fallbackReverseUrl,
  17:     this.isSet = false,
  18:     this.isGenuine2026 = false,
  19:     this.isRepresentativePreview = false,
  20:   }) : assert(obverseUrl != reverseUrl, 'Obverse and reverse URLs must be distinct');
  ```
  - Confirms Section 3.4's note (`line 200`): `fallbackObverseUrl`, `fallbackReverseUrl`, `isSet`, `isGenuine2026`, and `isRepresentativePreview` are all optional with defaults, so the new quarter/Polly/cent/nickel `CanonicalMintAssetPair(...)` calls compile cleanly.
- **Actual source (`canonical_mint_asset_service.dart:72-83` and `100-124`):**
  ```dart
  72:   static String extractSku(Map<String, dynamic> data) {
  73:     for (final k in const <String>[
  74:       'mint_product_id',
  75:       'sku',
  76:       'product_code',
  77:       'item_number',
  78:       'Retailer Item No.',
  79:       'retailer_item_no',
  80:     ]) {
  81:       final val = (data[k] ?? '').toString().trim().toUpperCase();
  82:       if (_knownSkus.contains(val)) return val;
  83:     }
  ...
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
  121:     if (year == '2023') {
  122:       if (combined.contains('silver proof set')) return '23RH';
  123:       if (combined.contains('proof set')) return '23RG';
  124:     }
  ```
- **Actual source (`canonical_mint_asset_service.dart:154` and `182-196`):**
  ```dart
  154:     final year = (data['year'] ?? data['Year'] ?? '').toString().trim();
  ...
  182:     final cleanSku = (sku ?? '').trim().toUpperCase();
  183:     final cleanTitle = (title ?? '').trim().toLowerCase();
  184:     final cleanYear = (year ?? '').trim();
  185:     final rawMint = (mintMark ?? '').trim().toUpperCase();
  186:     final cleanDenom = (denomination ?? '').trim().toLowerCase();
  187:     final cleanMint = rawMint.contains('WEST POINT') || rawMint == 'W'
  188:         ? 'W'
  189:         : (rawMint.contains('S')
  190:             ? 'S'
  191:             : (rawMint.contains('D')
  192:                 ? 'D'
  193:                 : (rawMint.contains('P') ? 'P' : rawMint)));
  194: 
  195:     // 1. Exact / Inferred SKU Match
  196:     switch (cleanSku) {
  ```
- **Actual source (`canonical_mint_asset_service.dart:314-370`):**
  ```dart
  314:     if (cleanYear == '2026') {
  ...
  332:       if (cleanTitle.contains('kennedy') ||
  333:           cleanTitle.contains('half dollar') ||
  334:           cleanDenom.contains('50c') ||
  335:           cleanDenom.contains('half') ||
  336:           cleanTitle.contains('independence')) {
  ...
  352:       }
  353:       if (cleanTitle.contains('mayflower')) {
  ...
  369:       }
  370:     }
  ```

---

### 2.4 Image Wiring Call-Sites (Section 5.1 & Section 5.2)
- **`numista_mobile/lib/services/coin_image_service.dart:489-495` and `618-631`:**
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
- **`numista_mobile/lib/inventory_gallery.dart:131-132` and `347-350`:**
  ```dart
  131:               final imageUrlObverse = data['image_url_obverse']?.toString();
  132:               final imageUrlReverse = data['image_url_reverse']?.toString();
  ```
  ```dart
  347:               child: Image.network(
  348:                 url,
  349:                 height: 120,
  350:                 fit: BoxFit.cover,
  ```
- **`numista_mobile/lib/screens/review_hub_screen.dart:2189-2211`:**
  ```dart
  2189:   Widget _buildCoinThumbnail(Map<String, dynamic> data) {
  2190:     final rawUrl = (data['image_url_obverse'] ??
  2191:             data['image_url'] ??
  ...
  2208:       child: rawUrl.isNotEmpty
  2209:           ? Image.network(
  2210:               rawUrl,
  ```
- **`numista_mobile/lib/screens/my_collection_screen.dart:3448, 3467-3472`, `4452-4461`, and `6345, 6357-6364, 6380-6382`:**
  ```dart
  3448:   void _showCoinInspectorDialog(String coinId, Map<String, dynamic> data) {
  ...
  3467:     final hasUserPhoto = data[_F.imageObverse]?.toString().startsWith('http') == true
  3468:         || data[_F.imageReverse]?.toString().startsWith('http') == true;
  3469:     final refFuture = hasUserPhoto
  3470:         ? null
  3471:         : CoinImageService.fetchReferenceImages(
  ```
  ```dart
  4452:     if (!hasAny) {
  ...
  4459:       return FutureBuilder<CoinImageResult>(
  4460:         future: CoinImageService.fetchReferenceImages(
  ```
  ```dart
  6345: class _CollectionCardImage extends StatelessWidget {
  ...
  6357:   Widget build(BuildContext context) {
  6358:     final obv = _cleanUrl(data[_F.imageObverse]);
  6359:     final rev = _cleanUrl(data[_F.imageReverse]);
  6360:     final directUrl = rev.isNotEmpty ? rev : obv;  // Prefer reverse (distinct design)
  6361: 
  6362:     if (directUrl.isNotEmpty) {
  6363:       return _buildCoinImage(directUrl);
  6364:     }
  ...
  6380:     return FutureBuilder<CoinImageResult>(
  6381:       future: CoinImageService.fetchReferenceImages(
  ```
- **`numista_mobile/lib/screens/coin_detail_screen.dart:1033-1057` and `1071`:**
  ```dart
  1033: class _CoinImagePair extends StatefulWidget {
  ...
  1041: class _CoinImagePairState extends State<_CoinImagePair> {
  ...
  1048:   void initState() {
  1049:     super.initState();
  1050:     // gs:// URIs are not displayable by Image.network() — treat as empty
  1051:     // so CoinImageService can fill in a public HTTPS URL from coin_image_index.
  1052:     _obvUrl = _toHttpsUrl(widget.coin.imageUrlObverse);
  1053:     _revUrl = _toHttpsUrl(widget.coin.imageUrlReverse);
  1054:     // Fetch reference images for any side that doesn't have a personal photo
  1055:     if (_obvUrl.isEmpty || _revUrl.isEmpty) {
  1056:       _fetchReferenceImages();
  1057:     }
  1058:   }
  ...
  1071:       final result = await CoinImageService.fetchReferenceImages(
  ```

---

## 3. Task 3: Weighing SAG's 4 Advisories (`INBOX/SAG_SCORE_NET-748_v5.md`)

1. **SAG Advisory 1 (`Test 20's "canonical 106–123" cite is still an unquoted summary. Quote the match conditions, or narrow the titles to what those lines actually return, before execute`):**
   - **Argon Verdict — CONCUR (Quoted & Verified Above):**
     - `canonical_mint_asset_service.dart:105-124` (quoted verbatim in Section 2.3 above) requires specific token pairs in `combined`:
       - `26XE`: `combined.contains('morgan') && combined.contains('enhanced')` (line 106)
       - `26XF`: `combined.contains('morgan') && combined.contains('proof')` (line 107)
       - `26XL`: `combined.contains('peace') && combined.contains('reverse proof')` (line 108)
       - `26XH`: `combined.contains('peace') && combined.contains('uncirculated'))` (line 109)
       - `26RJ`: `combined.contains('uncirculated') && combined.contains('set')` (line 110)
       - `26GC`: `combined.contains('american innovation')` (line 111)
       - `26SQRP`: `combined.contains('trump') || combined.contains('semiquincentennial president')` (line 112)
       - `26RH`: `combined.contains('silver proof set')` (line 115)
       - `26RG`: `combined.contains('clad proof set') || (combined.contains('proof set') && !combined.contains('silver'))` (lines 116–117)
     - **Action at Execute:** In Test 20 (`NET-748_v5_PLAN.md:361`), pass titles that match these exact predicates (e.g. `'Peace Dollar Reverse Proof'`, `'2026 Semiquincentennial President Donald J. Trump $1 Coin 25-Coin Roll'`, and `'Silver Proof Set'`) so Test 20 does not trigger a false STOP.

2. **SAG Advisory 2 (`Section 3.5 says both "replace line 182" and "after cleanMint" (193). Insert the fallback after 193 so it does not use cleanTitle / cleanDenom / cleanMint before they exist`):**
   - **Argon Verdict — CONCUR:**
     - As verified in `canonical_mint_asset_service.dart:182-193` (Section 2.3 above), line 182 precedes the declarations of `cleanTitle` (183), `cleanYear` (184), `cleanDenom` (186), and `cleanMint` (187–193).
     - **Action at Execute:** Remove line 182 and insert `final rawSku = ...; final cleanSku = ...;` immediately after line 193 (before `switch (cleanSku)` at line 196), exactly as `NET-748_v5_PLAN.md:204`'s parenthetical `(place it after cleanYear/cleanTitle/cleanDenom/cleanMint are computed)` instructs.

3. **SAG Advisory 3 (`Section 8's re-read list omits edit sites 73–80, 100, 154, and 182. Section 9 still says to grep item_type, which 4.2 already resolved to 'coin'/'set'. Section 4.1 still paraphrases 26XH/26XF/26GC/26RG/26RH/23RG/23RH; copy those strings, do not use the table`):**
   - **Argon Verdict — CONCUR (with Concrete Source Finding on `main.py` & `switch`):**
     - First, edit sites `73-80`, `100`, `154`, and `182` of `canonical_mint_asset_service.dart` have been re-read and verified in Section 2.3 above.
     - Second, we read both `numista_backend/main.py:2185-2240` and `canonical_mint_asset_service.dart:196-311`:
       - `canonical_mint_asset_service.dart:196-311` has **zero comments** on `case '26XH':`, `case '26XF':`, `case '26GC':`, `case '26RG':`, `case '23RG':`, `case '26RH':`, `case '23RH':`.
       - `numista_backend/main.py:2197-2200, 2233` only has explicit strings for `26XL`, `26EA`, `26XE`, `26SQRP`, and `26RJ`.
       - However, `canonical_mint_asset_service.dart:106-123` (quoted in Section 2.3 above) DOES contain the exact match strings for all 11 SKUs (`'morgan'` + `'proof'` for `26XF`, `'peace'` + `'uncirculated'` for `26XH`, `'american innovation'` for `26GC`, `'clad proof set'` for `26RG`/`23RG`, `'silver proof set'` for `26RH`/`23RH`), and Test 17 (`NET-748_v5_PLAN.md:358`) requires `_kFallbackUsMintSkus` to have all 11 SKUs in 4.1 with `sku` and `name`. Using the strings from `main.py:2197-2200` + `canonical_mint_asset_service.dart:106-123` satisfies both Test 17 and `extractSku`.

4. **SAG Advisory 4 (`Pin --project and cwd on firebase hosting:channel:deploy p7-gate the same way as 1b. The YES cwd string is numista_mobile/; the must-hold pin is the absolute path`):**
   - **Argon Verdict — STRONGLY CONCUR:**
     - **Action at Execute:** Run the preview deploy (`NET-748_v5_PLAN.md:364, 372`) from cwd `C:\Users\ericd\Documents\MyVertexProject\numista_mobile\` using the pinned command:
       ```bash
       firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8
       ```

---

## 4. Final Verdict

- **Score:** **96 / 100 — PASS**
- **Must-Fixes:** **None (0)**
- **Recommendation:** `NET-748_v5_PLAN.md` is verified against `p7-v8.9` (`ca4e3d33`) and ready for GB CoS / Founder Eric's typed YES (with Step 1b `firestore.rules` live deploy gated behind its own separate typed YES from Eric).
