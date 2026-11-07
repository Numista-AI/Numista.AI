# FAILFIX PLAN v1.9: Broken Images & Storage URL Security Guard (NET-780c)
**To:** Grok Bot CoS, Stand Alone Grok (SAG, grok-4.7), Antigravity Desk, Founder Eric  
**From:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`) — Attempt 1/4 on NET-817  
**Date:** 7 November 2026, 15:39 ET (Observed Wall-Clock DTG: `2026-11-07 15:39 ET`)  
**Reference Batons & Scores:**  
- `BATON_NET-780_FAILFIX_PLAN_NET-748-v5-FT_v1_2026-11-04-1658.md`  
- `COS_SCORE_NET-817_CARDS_IMAGES_v1.8_20261107.md` (Images 76/100 FAIL, Cards 70/100 FAIL, Combined 73/100 FAIL)  
- `RADIO_NET-832_GROKCOS_WRITER-ASSIGN_REVISE-817-v1.9_20261107.md`  
- `RADIO_NET-835_GROKCOS-to-DESK_ASSIGN-817-v1.9_20261107.md`  
- `BATON_NET-817_REVISE_CARDS-IMAGES_v1.9_TO-AGCOS-V5_cfe23a7a_ATTEMPT1_20261107.md`  
**Directives & Audit Authority:**  
- `GB CoS SCORE v1.8` & `RADIO_NET-832`: Narrow delta resolving `MF-B1'`, `MF-B2'`, `MF-B3'`, `MF-I3'`, `MF-I6`, `MF-I7`, and `MF-I5'` while preserving every item marked **Closed** in `COS_SCORE_NET-817_CARDS_IMAGES_v1.8_20261107.md`.  
- `PROTOCOL UPDATE: ARGON DROPPED ENTIRELY`: Founder Eric typed YES. Review sequence is strictly: AG CoS v5 Plan $\rightarrow$ Grok Bot CoS ($\ge 95$) $\rightarrow$ Stand Alone Grok ($\ge 95$) $\rightarrow$ Founder Eric typed YES.  
**Status:** **PLAN ONLY** (Zero code changes, zero test execution, zero builds, zero deployments, zero Firestore writes/seeding).  
**Explicit Standing Locks & Clearances:**  
1. `origin/main` strictly locked at `9f04550a`.  
2. Stripe strictly locked OFF across all code and configurations.  
3. Execution strictly scoped to branch `p7-v8.9` against verified code baseline commit `4d17ca5e` (`c294fd3c`, the last code commit touching `numista_mobile/` on `p7-v8.9`; branch `dev` @ `b0b05808` lacks `canonical_mint_asset_service.dart`).  
4. Founder Eric's typed YES to this plan is strictly for code execution on `p7-v8.9` and preview channel deployment — it is NOT an approval for Firestore database writes, seeding, or security rules changes. Separate scoped Eric typed YES is required for any database writes.  
5. Zero deployments to live production `numista-vault.web.app` or `numista.ai` without prior Firebase Preview Channel sign-off and Eric's separate, explicit typed approval. Target is **p7-gate preview** (`preview-catalog`) only.  
6. **Alerts only, NEVER budget caps:** all spending caps (including $25 limit and hard $0.00 spend cap) are permanently eliminated per Eric's standing rule; billing alerts set at $20/mo.  
7. Zero AJ PII across all plans, logs, mocks, and code.  

---

## 1. Executive Summary & Itemized Must-Fix Closeout Table (v1.8 $\rightarrow$ v1.9 Delta)

Plan v1.9 preserves every item marked **Closed** in `COS_SCORE_NET-817_CARDS_IMAGES_v1.8_20261107.md` (`MF-B2`, `MF-B3` apply order, `MF-I1`, `MF-I2`, `MF-I4`) and resolves all open cross-plan and Images must-fixes (`MF-B1'`, `MF-B2'`, `MF-B3'`, `MF-I3'`, `MF-I6`, `MF-I7`, `MF-I5'`) with verbatim `git show 4d17ca5e:...` evidence:

| Must-Fix # | Must-Fix Description | Plan v1.9 Resolution & Verbatim Grounding at `4d17ca5e` | Plan Section |
| :--- | :--- | :--- | :--- |
| **MF-B1'** | **Resolve Orphaned Kaggle/Google Inspector Deletions & Correct Verbatim Quotes:** Do not point at parked NET-816 v1.11 as active owner. Fix stale quotes for `:3531–3548`, `:4387–4406`, and `:4408–4426`. | **Explicit Re-Homing / Self-Contained Gate:** Records that NET-816 v1.11 is **PARKED** and Catalog Chunk 1 (`9bbe20e4`) is scoped strictly to 2 catalog items (`catalog_service.dart` / `catalog_browse_screen.dart`), NOT `my_collection_screen.dart`. NET-817's card/image changes (`:3017–3023`, `:3167–3192`, `:6356–6479`) are **100% independent** of the inspector/Google-button lines and do not touch them by default (or, if explicitly assigned by CoS at execution gate, delete all 7 spans atomically in Step 1). All quotes corrected verbatim from `git show 4d17ca5e:numista_mobile/lib/screens/my_collection_screen.dart`. | §2.A, §4.B |
| **MF-B2'** | **Pin Code Commit (`4d17ca5e`), Not Docs HEAD (`ebf1eed8`), & Honest DTG:** Pre-flight must check `git diff --quiet 4d17ca5e HEAD -- numista_mobile/` and stamp real wall-clock filing time. | Pre-flight gate (§4.A) pins `4d17ca5e` via `git diff --quiet 4d17ca5e HEAD -- numista_mobile/` so docs-only commits on `p7-v8.9` never invalidate the code baseline while any unexpected code drift aborts immediately. DTG stamped from observed wall-clock (`2026-11-07 15:39 ET`). | Header, §4.A |
| **MF-B3'** | **Include Required Imports in `my_collection_screen.dart` Diff:** Add `collection_card_valuation_row.dart` and `collection_card_image.dart` imports. | §3.D includes the exact verbatim import block from `my_collection_screen.dart:42–45` at `4d17ca5e` and adds `import '../widgets/collection_card_image.dart';` immediately after `import '../widgets/collection_card_valuation_row.dart';` landed in Step 1. | §3.D |
| **MF-I3'** | **Declare Image Precedence Policy Honestly (Canonical vs User Photo):** Shipped `_CollectionCardImage` (`:6369–6383`) checks `CanonicalMintAssetService.resolveFromMap(data)` (`:6369`) before direct user URLs (`:6377`), where `resolveFromMap` (`:156`) yields to user uploads via `hasUserUploadedPhotos(data)` (`:27–50`) EXCEPT when `getDownloadURL()` URL-encodes `/users/` as `users%2F`. Do not falsely call an inversion "restored". | **Preserves Shipped Order (`Canonical -> Direct User URL -> Reference Service`) + Fixes `hasUserUploadedPhotos` URL-Encoding Gap:** Quotes `my_collection_screen.dart:6369–6383` and `canonical_mint_asset_service.dart:27–50, 153–158` verbatim. Keeps the exact shipped evaluation order (`CanonicalMintAssetService.resolveFromMap(widget.data)` first, then direct user photo `revUserUrl`/`obvUserUrl`, then `CoinImageService.fetchReferenceImages`) AND patches `hasUserUploadedPhotos` at `canonical_mint_asset_service.dart:39` to match both `s.contains('/users/')` and `s.contains('users%2f')` (plus `imageUrlObverse`, `imageUrlReverse`, `obverse_image_url`, `reverse_image_url`, `obverseUrl`, `reverseUrl`). Documents the exact set of affected cards: 2026 canonical SKU coins where a collector uploaded their own photo via `FirebaseStorage.ref('users/$email/coins/...').getDownloadURL()` (`:5489`), which now properly yield in `hasUserUploadedPhotos` (`:156`) and render the collector's photo while non-user URLs on 2026 SKUs continue to use canonical Mint assets. | §2.C, §3.C, §6.2 |
| **MF-I6** | **Preserve Shipped `_cleanUrl` Semantics in `extractUserPhoto` (`http(s)://` Only vs Non-URL Junk):** Shipped `_cleanUrl` (`:6360–6365`) only treats strings starting with `https://` or `http://` as URLs; non-URL junk (`'N/A'`, `'pending'`, `'none'`, `'null'`, local filenames `'coin.jpg'`) returns `''` so the card falls through to canonical/reference instead of failing closed to a dead placeholder! | Restores shipped `_cleanUrl` semantics in `lib/utils/collection_image_utils.dart` (`extractUserPhoto`): a field value is returned as a candidate URL **only** if it starts with `https://`, `http://`, or a valid same-origin asset path `/assets/` (or protocol-relative `//` / `/\` so malicious URL-like strings still hit the fail-closed guard). Non-URL sentinel strings (`'N/A'`, `'pending'`, `'none'`, `'null'`, `'—'`, `'gs://...'`, or bare filenames `'IMG_001.jpg'`) return `''`, allowing the card to fall through cleanly to `CanonicalMintAssetService` or `CoinImageService`! Meanwhile, any `http://` or unowned `https://` URL (e.g., `https://evil.firebasestorage.app/x.jpg` or `http://storage.googleapis.com/...`) is returned by `extractUserPhoto`, rejected by `isOwnedStorageUrl`, and fails closed to placeholder. Tested explicitly in §6.2! | §2.C, §3.B, §6.2 |
| **MF-I7** | **Prove Firestore Reference-Index `public_url` Forms Against `isOwnedStorageUrl`:** Cite the index builder/seeder code that populates `reference_images` and `currency_reference_images` and prove every emitted `public_url` matches `isOwnedStorageUrl`. | Quotes `git show 4d17ca5e:numista_backend/scripts/reference_library/build_image_index.py` (`:46, :53–105, :303`), `build_currency_image_index.py` (`:40–42, :267`), and `promote_user_photos.py` (`:35, :130`) verbatim, proving 100% of Firestore `public_url` entries are constructed as `f"{PUBLIC_URL_BASE}/{bucket}/{path}"` where `PUBLIC_URL_BASE = "https://storage.googleapis.com"` and `bucket` is exclusively `us_mint_coin_images`, `numista-reference-library`, or `numista-uploads-studio-9101802118-8c9a8` — all three of which are explicitly permitted in `isOwnedStorageUrl`. Includes one sanitized fixture per form in `owned_storage_url_test.dart` (§6.1). | §2.B, §6.1 |
| **MF-I5'** | **Prove `didUpdateWidget` Refresh on Same `_CollectionCardImageState` Instance & Fix `ref_image_widget.dart` Path:** Pass stable `ValueKey('card')` across both `pumpWidget` calls and assert `identical(stateBefore, stateAfter)`. Fix path citation to `numista_mobile/lib/widgets/common/ref_image_widget.dart:57`. | In §6.2 (`collection_card_image_test.dart` Case 7), passes `key: const ValueKey('card')` to `CollectionCardImage` on both `pumpWidget` calls, captures `final stateBefore = tester.state(find.byKey(const ValueKey('card')));` before update and `stateAfter` after update, and asserts `expect(identical(stateBefore, stateAfter), isTrue)` alongside `expect(fetchCount, 2)`. Updates path citation in §2.B to `numista_mobile/lib/widgets/common/ref_image_widget.dart:57`. | §2.B, §6.2 |

---

## 2. Root Cause Analysis & Verbatim Grounding (`git show 4d17ca5e:...`)

### A. Kaggle & Google Images Structural Deletion Ownership & Correct Quotes (MF-B1')
Verifying `git show 4d17ca5e:numista_mobile/lib/screens/my_collection_screen.dart`:
- **State variables at lines 150–151:**
  ```dart
  150:   List<ReferenceImage> _inspectorSimilar = [];
  151:   bool _loadingInspectorSimilar = false;
  ```
- **Call site at line 3454:**
  ```dart
  3454:     _fetchInspectorSimilar(data);
  ```
- **Google Images button at lines 3531–3548 (`OutlinedButton.icon` calling `_onSearchGoogle(data)`):**
  ```dart
  3531:                     // Google Images search — only shown when no photo is active
  3532:                     if (!hasActive && refFuture != null) ...[
  3533:                       Tooltip(
  3534:                         message: 'Opens Google Images: searches for this coin',
  3535:                         child: OutlinedButton.icon(
  3536:                           onPressed: () => _onSearchGoogle(data),
  3537:                           icon: Icon(Icons.image_search, size: 15),
  3538:                           label: Text('Google Images'),
  ...
  3547:                       SizedBox(width: 8),
  3548:                     ],
  ```
- **UI call at line 3820:**
  ```dart
  3820:                           _buildSimilarCoinsInspector(),
  ```
- **Google Images handler at lines 4387–4406 (`void _onSearchGoogle(Map<String, dynamic> data) async`):**
  ```dart
  4387:   void _onSearchGoogle(Map<String, dynamic> data) async {
  4388:     final year  = data[_F.year]?.toString().replaceAll(RegExp(r'\.0$'), '') ?? '';
  ...
  4406:   }
  ```
- **Outbound eBay SOLD search at lines 4408–4426 (MUST BE PRESERVED):**
  ```dart
  4408:   /// Opens eBay SOLD listings in the browser using an EPN affiliate link
  4409:   /// so Numista.AI earns commission on any resulting purchase.
  4410:   void _onSearchEbay(Map<String, dynamic> data) async {
  4411:     try {
  4412:       final coin = CoinModel.fromMap(data, _selectedCoinId ?? '');
  4413:       final url  = await EpnService.generateSearchUrl(coin, soldOnly: true);
  ```
- **Inspector loader (`:5252–5278`) and UI/dialog (`:5549–5684`):**
  ```dart
  5252:   Future<void> _fetchInspectorSimilar(Map<String, dynamic> data) async {
  ...
  5278:   }
  ...
  5549:   Widget _buildSimilarCoinsInspector() {
  ...
  5647:   void _showRefImageDialog(BuildContext ctx, ReferenceImage img) {
  ...
  5684:   }
  ```
**Ownership Boundary (`MF-B1'`):** Identical to `FAILFIX_PLAN_NET-780b_CARDS_v1.9.md` §2.A and §4.B: NET-816 v1.11 is **PARKED**, and Catalog Chunk 1 (`9bbe20e4`) does not own `my_collection_screen.dart`. NET-817's card and image changes (`:3017–3023`, `:3167–3192`, `:6356–6479`) are 100% independent of the inspector/Google-button lines and leave them untouched by default pending CoS re-homing (or, if explicitly directed by CoS at execution gate, remove all 7 spans atomically in Step 1 while preserving `_onSearchEbay` at `:4408–4426`).

---

### B. Real Storage Bucket URLs & Firestore Reference-Index `public_url` Proof (MF-I1, MF-I5', MF-I7)
Verifying all storage URL emitters across `numista_mobile/` and `numista_backend/` at commit `4d17ca5e`:

1. **Real Project Storage Bucket (`numista_mobile/lib/firebase_options.dart:55, 64, 73` & `.firebaserc`):**
   ```dart
   55:     storageBucket: 'studio-9101802118-8c9a8.firebasestorage.app',
   ```
2. **Real User Upload Download URLs (`numista_mobile/lib/screens/my_collection_screen.dart:5015, 5489`):**
   ```dart
   5015:       final url = await snap.ref.getDownloadURL();
   ...
   5489:       final ref = FirebaseStorage.instance.ref('users/$userEmail/coins/${coinId}_${side}_$ts.jpg');
   ```
   Yields Form A: `https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2F...`
3. **Real Official Mint Tier-1 Reference Widget (`numista_mobile/lib/widgets/common/ref_image_widget.dart:55–57` — exact path verified per `MF-I5'`):**
   ```dart
   55:     final fullUrl = path.startsWith('http') 
   56:       ? path 
   57:       : 'https://storage.googleapis.com/us_mint_coin_images/$path';
   ```
4. **Real Canonical Mint & Wikimedia Reference Service (`numista_mobile/lib/services/canonical_mint_asset_service.dart:52–55`):**
   ```dart
   52:   static const String _base =
   53:       'https://storage.googleapis.com/numista-reference-library/reference_library';
   54:   static const String _mintBase = '$_base/us_mint_official';
   55:   static const String _wikiBase = '$_base/wikimedia_uscoin';
   ```
5. **Real Direct Upload Buckets (`numista_mobile/lib/services/canonical_mint_asset_service.dart:37–38`):**
   ```dart
   37:              s.contains('studio-9101802118-8c9a8-uploads') ||
   38:              s.contains('numista-uploads-studio-') ||
   ```
6. **Proof of Firestore `reference_images` and `currency_reference_images` Index `public_url` Forms (`MF-I7`):**
   - In `git show 4d17ca5e:numista_backend/scripts/reference_library/build_image_index.py` lines 46, 53–105, and 302–304:
     ```python
     46: PUBLIC_URL_BASE = "https://storage.googleapis.com"
     ...
     55:     {
     56:         "tier": 1,
     57:         "source": "us_mint_direct",
     58:         "bucket": "us_mint_coin_images",
     ...
     65:     {
     66:         "tier": 1,
     67:         "source": "us_mint_official",
     68:         "bucket": "numista-reference-library",
     69:         "prefix": "reference_library/us_mint_official/",
     ...
     302:         "gcs_uri": f"gs://{bucket}/{path}",
     303:         "public_url": f"{PUBLIC_URL_BASE}/{bucket}/{path}",
     ```
     Every single source in `SOURCES` (`:53–105`: `us_mint_direct`, `us_mint_official`, `wikimedia_uscoin`, `pcgs_coinfacts`, `ngc_coin_explorer`, `heritage_auctions`, `kaggle_us_coins`) writes to either `"bucket": "us_mint_coin_images"` or `"bucket": "numista-reference-library"`.
   - In `git show 4d17ca5e:numista_backend/scripts/reference_library/build_currency_image_index.py` lines 40–42 and 266–268:
     ```python
     40: BUCKET_NAME = "numista-reference-library"
     41: CURRENCY_PREFIX = "reference_library/wikimedia_uscurrency/"
     42: PUBLIC_URL_BASE = "https://storage.googleapis.com"
     ...
     266:         "gcs_uri": f"gs://{BUCKET_NAME}/{path}",
     267:         "public_url": f"{PUBLIC_URL_BASE}/{BUCKET_NAME}/{path}",
     ```
   - In `git show 4d17ca5e:numista_backend/scripts/reference_library/promote_user_photos.py` lines 35 and 130:
     ```python
     35: UPLOADS_BUCKET = "numista-uploads-studio-9101802118-8c9a8"
     ...
     130:         "public_url": f"https://storage.googleapis.com/{REF_BUCKET}/{dest_blob_Path}",
     ```
   - And in `git show 4d17ca5e:numista_mobile/lib/services/coin_image_service.dart` line 404:
     ```dart
     404:     final url = data['public_url'] as String?;
     ```
   **Conclusion (`MF-I7`):** 100% of `public_url` values stored in Firestore `reference_images` and `currency_reference_images` and returned by `CoinImageService.fetchReferenceImages` start with `https://storage.googleapis.com/us_mint_coin_images/` or `https://storage.googleapis.com/numista-reference-library/` (or `https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/`), all of which pass `isOwnedStorageUrl`!

---

### C. Shipped `_CollectionCardImage` Precedence, `_cleanUrl` Semantics, & Steal-Guard (MF-I3', MF-I6)
In `git show 4d17ca5e:numista_mobile/lib/screens/my_collection_screen.dart`, lines 6356–6420 read verbatim:
```dart
6356: class _CollectionCardImage extends StatelessWidget {
6357:   final Map<String, dynamic> data;
6358:   const _CollectionCardImage({required this.data});
6359: 
6360:   static String _cleanUrl(dynamic val) {
6361:     if (val == null) return '';
6362:     final s = val.toString().trim();
6363:     if (s.startsWith('https://') || s.startsWith('http://')) return s;
6364:     return '';
6365:   }
6366: 
6367:   @override
6368:   Widget build(BuildContext context) {
6369:     final canon = CanonicalMintAssetService.resolveFromMap(data);
6370:     if (canon != null) {
6371:       final canonUrl = canon.reverseUrl.isNotEmpty ? canon.reverseUrl : canon.obverseUrl;
6372:       if (canonUrl.isNotEmpty) {
6373:         return _buildNetworkImage(canonUrl);
6374:       }
6375:     }
6376: 
6377:     final obv = _cleanUrl(data[_F.imageObverse] ?? data['imageObverse'] ?? data['obverse_url']);
6378:     final rev = _cleanUrl(data[_F.imageReverse] ?? data['imageReverse'] ?? data['reverse_url']);
6379:     final directUrl = rev.isNotEmpty ? rev : obv; // Prefer reverse (distinct design)
6380: 
6381:     if (directUrl.isNotEmpty) {
6382:       return _buildNetworkImage(directUrl);
6383:     }
...
6409:         // MF-V3-3: When subject is known and reverse is null (steal-guard
6410:         // correctly blocked a generic reverse), show placeholder instead of
6411:         // falling back to generic obverse. Keeps obverse fallback for coins
6412:         // without a subject (e.g. generic Morgan/Peace).
6413:         final refUrl = (ref?.reverseUrl?.isNotEmpty == true)
6414:             ? ref!.reverseUrl!
6415:             : (subject.isEmpty && ref?.obverseUrl?.isNotEmpty == true)
6416:                 ? ref!.obverseUrl!
6417:                 : '';
```

**Why Precedence and `_cleanUrl` Matter (`MF-I3'` & `MF-I6`):**
1. **Precedence Order (`MF-I3'`):**
   - Shipped `_CollectionCardImage` evaluates `CanonicalMintAssetService.resolveFromMap(data)` (`:6369`) **first**, and direct user URLs (`:6377`) **second**.
   - Inside `CanonicalMintAssetService.resolveFromMap(data)` (`canonical_mint_asset_service.dart:156`), `if (hasUserUploadedPhotos(data)) return null;` is intended to yield to real user uploads so collector-uploaded photos take precedence over canonical Mint stock art.
   - However, `hasUserUploadedPhotos` (`:39`) only checked `s.contains('/users/')`, missing Firebase Storage download URLs (`getDownloadURL()` at `my_collection_screen.dart:5015, 5489`) where `/users/` is URL-encoded as `users%2F` (`.../o/users%2F...`)!
   - **v1.9 Fix (`MF-I3'`):** We keep the exact shipped evaluation order in `CollectionCardImage` (`1. CanonicalMintAssetService.resolveFromMap(widget.data)` $\rightarrow$ `2. Direct User URL (rev preferred over obv)` $\rightarrow$ `3. CoinImageService.fetchReferenceImages`) AND patch `hasUserUploadedPhotos` in `canonical_mint_asset_service.dart:39–50` to also detect `s.contains('users%2f')` and all user photo field aliases (`imageUrlObverse`, `imageUrlReverse`, `obverse_image_url`, `reverse_image_url`, `obverseUrl`, `reverseUrl`).
   - **Affected Cards Documented:** For any 2026 canonical SKU coin where a user has uploaded a real photo via Firebase Storage (`users%2F...`), `hasUserUploadedPhotos` now returns `true` so `resolveFromMap` yields (`null`) and Step 2 renders the collector's own uploaded photo. For any 2026 canonical SKU coin whose `image_url_obverse`/`reverse` contains a non-user URL or stale reference URL, Step 1 (`resolveFromMap`) continues to render the authoritative canonical Mint asset just as in shipped `:6369–6375`.
2. **`_cleanUrl` Non-URL Junk Fallthrough (`MF-I6`):**
   - Shipped `_cleanUrl` (`:6360–6365`) returns `''` for anything that does not start with `https://` or `http://`.
   - In v1.8, `extractUserPhoto` returned any non-empty string other than `'null'`, `'None'`, or `'gs://'`. Consequently, a legacy Firestore doc with `image_url_obverse: 'N/A'`, `'pending'`, `'none'`, `'—'`, or a bare filename `'IMG_1234.JPG'` caused `extractUserPhoto` to return a non-empty string, which then failed `isOwnedStorageUrl` and locked the card onto a dead placeholder instead of falling through to `CanonicalMintAssetService` or `CoinImageService`!
   - **v1.9 Fix (`MF-I6`):** `extractUserPhoto` strictly filters candidate strings so only URL-shaped strings (`https://...`, `http://...`, `/assets/...`, or protocol-relative `//...` / `/\...` attack strings) are returned as candidate URLs. All non-URL sentinels (`'N/A'`, `'pending'`, `'none'`, `'null'`, `'—'`, `'gs://...'`, bare filenames `'coin.jpg'`) return `''` so the card falls through cleanly to canonical/reference! Meanwhile, any `http://...`, `//evil.com`, `/\evil.com`, or unowned `https://...` URL is returned by `extractUserPhoto`, rejected by `isOwnedStorageUrl`, and fails closed to placeholder without triggering a network reference fetch.

---

### D. Verbatim Content-Security-Policy Analysis (MF-I4 — Closed, Preserved)
In `git show 4d17ca5e:numista_mobile/firebase.json` line 276, the CSP header reads verbatim:
```json
276: "value": "default-src 'self' https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseapp.com https://*.firebase.com https://storage.googleapis.com https://*.run.app; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://apis.google.com https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.run.app; worker-src blob: 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.gstatic.com; font-src 'self' https://fonts.gstatic.com https://*.gstatic.com data:; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseio.com wss://*.firebaseio.com https://firestore.googleapis.com https://identitytoolkit.googleapis.com https://accounts.google.com https://*.run.app https://numista-backend-568985927038.us-central1.run.app https://localhost:5000; frame-src 'self' https://apis.google.com https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.run.app"
```
Adding `https://firebasestorage.googleapis.com` to `img-src` allows Form A (`getDownloadURL()`) user photos to load under browser CSP.

---

## 3. Targeted Production Code Implementation

### A. Public Top-Level Storage Guard: `numista_mobile/lib/utils/owned_storage_url.dart` (MF-I1, MF-I2 — Closed, Preserved)
```dart
/// Public top-level security guard for image URLs rendered in Numista.AI.
/// Admits only verified first-party and official Google Cloud / Firebase storage URLs.
/// Blocks unowned third-party storage, wildcards, and protocol-relative bypasses.
bool isOwnedStorageUrl(String? url) {
  if (url == null) return false;
  final trimmed = url.trim();
  if (trimmed.isEmpty) return false;

  // 1. Relative same-origin paths: must start with single '/', not '//', and no backslashes
  if (trimmed.startsWith('/') && !trimmed.startsWith('//') && !trimmed.contains(r'\')) {
    return true;
  }

  // 2. Strict HTTPS parsing
  final uri = Uri.tryParse(trimmed);
  if (uri == null || uri.scheme != 'https') return false;

  final host = uri.host.toLowerCase();
  final path = uri.path;

  // 3. Form A: Firebase Storage download URL for real project bucket (studio-9101802118-8c9a8)
  if (host == 'firebasestorage.googleapis.com') {
    return path.startsWith('/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/');
  }

  // 4. Form B: Google Cloud Storage with exact permitted bucket roots
  if (host == 'storage.googleapis.com') {
    return path.startsWith('/us_mint_coin_images/') ||
           path.startsWith('/numista-reference-library/') ||
           path.startsWith('/studio-9101802118-8c9a8-uploads/') ||
           path.startsWith('/numista-uploads-studio-9101802118-8c9a8/') ||
           path.startsWith('/studio-9101802118-8c9a8.firebasestorage.app/');
  }

  return false;
}
```

---

### B. User Photo Helper with Shipped `_cleanUrl` Semantics: `numista_mobile/lib/utils/collection_image_utils.dart` (MF-I2, MF-I6)
```dart
/// Extracts cleaned direct user photo URL candidate from coin document map.
///
/// MF-I6: Preserves shipped `_cleanUrl` (`my_collection_screen.dart:6360-6365`)
/// semantics so non-URL sentinel values ('N/A', 'pending', 'none', 'null', '—',
/// 'gs://...', or bare filenames like 'IMG_001.jpg') return '' and fall through
/// cleanly to CanonicalMintAssetService / CoinImageService.
///
/// Returns non-empty string ONLY when the field contains an explicit HTTP(S) URL,
/// a same-origin '/' path, or a protocol-relative '//' / '/\' URL candidate
/// (which is then validated fail-closed by `isOwnedStorageUrl`).
String extractUserPhoto(Map<String, dynamic> data, {bool isObverse = true}) {
  final keys = isObverse
      ? const <String>[
          'image_url_obverse',
          'imageUrlObverse',
          'obverse_image_url',
          'obverse_url',
          'imageObverse',
          'image_obverse',
          'obverseUrl',
          'photo_obverse',
        ]
      : const <String>[
          'image_url_reverse',
          'imageUrlReverse',
          'reverse_image_url',
          'reverse_url',
          'imageReverse',
          'image_reverse',
          'reverseUrl',
          'photo_reverse',
        ];

  for (final k in keys) {
    final val = data[k];
    if (val != null) {
      final s = val.toString().trim();
      if (s.isEmpty) continue;
      final lower = s.toLowerCase();
      if (lower == 'null' ||
          lower == 'none' ||
          lower == 'n/a' ||
          lower == 'na' ||
          lower == 'pending' ||
          lower == '—' ||
          lower == '-' ||
          lower.startsWith('gs://')) {
        continue;
      }
      // Match shipped _cleanUrl (:6363) + relative/protocol-relative path candidates
      if (lower.startsWith('https://') ||
          lower.startsWith('http://') ||
          s.startsWith('/')) {
        return s;
      }
    }
  }
  return '';
}
```

---

### C. Patch `hasUserUploadedPhotos` in `canonical_mint_asset_service.dart:31–50` & Public `CollectionCardImage` Widget (MF-I2, MF-I3', MF-I6)

#### 1. Surgical Patch to `hasUserUploadedPhotos` in `numista_mobile/lib/services/canonical_mint_asset_service.dart:31–50` (MF-I3')
In `git show 4d17ca5e:numista_mobile/lib/services/canonical_mint_asset_service.dart`, lines 31–50 read verbatim:
```dart
31:     bool isUserUrl(dynamic val) {
32:       if (val == null) return false;
33:       final s = val.toString().trim().toLowerCase();
34:       if (s.isEmpty) return false;
35:       if (s.contains('/reference_images/') || s.contains('reference_library')) return false;
36:       return s.contains('/microscope/') ||
37:              s.contains('studio-9101802118-8c9a8-uploads') ||
38:              s.contains('numista-uploads-studio-') ||
39:              s.contains('/users/') ||
40:              s.contains('/user_uploads/') ||
41:              s.contains('user_upload');
42:     }
43: 
44:     return isUserUrl(data['image_url_obverse']) ||
45:            isUserUrl(data['image_url_reverse']) ||
46:            isUserUrl(data['imageObverse']) ||
47:            isUserUrl(data['imageReverse']) ||
48:            isUserUrl(data['stored_obv']) ||
49:            isUserUrl(data['stored_rev']);
50:   }
```
Exact surgical replacement so `getDownloadURL()` URLs containing `users%2f` (URL-encoded `/users/`) are recognized as user uploads:
```dart
<<<<
      return s.contains('/microscope/') ||
             s.contains('studio-9101802118-8c9a8-uploads') ||
             s.contains('numista-uploads-studio-') ||
             s.contains('/users/') ||
             s.contains('/user_uploads/') ||
             s.contains('user_upload');
    }

    return isUserUrl(data['image_url_obverse']) ||
           isUserUrl(data['image_url_reverse']) ||
           isUserUrl(data['imageObverse']) ||
           isUserUrl(data['imageReverse']) ||
           isUserUrl(data['stored_obv']) ||
           isUserUrl(data['stored_rev']);
  }
====
      return s.contains('/microscope/') ||
             s.contains('studio-9101802118-8c9a8-uploads') ||
             s.contains('numista-uploads-studio-') ||
             s.contains('/users/') ||
             s.contains('users%2f') ||
             s.contains('/user_uploads/') ||
             s.contains('user_upload');
    }

    return isUserUrl(data['image_url_obverse']) ||
           isUserUrl(data['image_url_reverse']) ||
           isUserUrl(data['imageUrlObverse']) ||
           isUserUrl(data['imageUrlReverse']) ||
           isUserUrl(data['obverse_image_url']) ||
           isUserUrl(data['reverse_image_url']) ||
           isUserUrl(data['obverse_url']) ||
           isUserUrl(data['reverse_url']) ||
           isUserUrl(data['imageObverse']) ||
           isUserUrl(data['imageReverse']) ||
           isUserUrl(data['obverseUrl']) ||
           isUserUrl(data['reverseUrl']) ||
           isUserUrl(data['stored_obv']) ||
           isUserUrl(data['stored_rev']);
  }
>>>>
```

#### 2. Public Production Widget: `numista_mobile/lib/widgets/collection_card_image.dart` (MF-I2, MF-I3', MF-I6)
Preserves the exact shipped precedence order (`1. CanonicalMintAssetService.resolveFromMap(widget.data)` [which yields via `hasUserUploadedPhotos` when the collector uploaded their own photo] $\rightarrow$ `2. Direct User URL (reverse preferred over obverse)` $\rightarrow$ `3. CoinImageService.fetchReferenceImages`), while failing closed if a user photo field holds an unowned/malicious URL:
```dart
import 'package:flutter/material.dart';
import 'package:numista_ai/services/canonical_mint_asset_service.dart';
import 'package:numista_ai/services/coin_image_service.dart';
import 'package:numista_ai/utils/collection_image_utils.dart';
import 'package:numista_ai/utils/owned_storage_url.dart';

/// Semantic request key for memoizing reference image fetches.
/// Uses CanonicalMintAssetService.canonicalYear to normalize year representation.
@immutable
class CollectionCardImageRequestKey {
  final String year;
  final String mint;
  final String denomination;
  final String series;
  final String subject;

  const CollectionCardImageRequestKey({
    required this.year,
    required this.mint,
    required this.denomination,
    required this.series,
    required this.subject,
  });

  factory CollectionCardImageRequestKey.fromData(Map<String, dynamic> data) {
    String read(String snakeKey, String legacyKey) {
      final s = data[snakeKey]?.toString();
      if (s != null && s.trim().isNotEmpty && s.trim() != 'None' && s.trim() != 'null') return s.trim();
      final l = data[legacyKey]?.toString();
      if (l != null && l.trim().isNotEmpty && l.trim() != 'None' && l.trim() != 'null') return l.trim();
      return '';
    }

    final canonYear = CanonicalMintAssetService.canonicalYear(data);
    final year = canonYear.isNotEmpty ? canonYear : read('year', 'Year').replaceAll(RegExp(r'\.0$'), '');
    final mint = read('mint_mark', 'Mint Mark');
    final denom = read('denomination', 'Denomination');
    final series = read('program_series', 'Program/Series');
    final subject = read('theme_subject', 'Theme/Subject');

    return CollectionCardImageRequestKey(
      year: year,
      mint: mint,
      denomination: denom,
      series: series,
      subject: subject,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is CollectionCardImageRequestKey &&
          runtimeType == other.runtimeType &&
          year == other.year &&
          mint == other.mint &&
          denomination == other.denomination &&
          series == other.series &&
          subject == other.subject;

  @override
  int get hashCode =>
      year.hashCode ^
      mint.hashCode ^
      denomination.hashCode ^
      series.hashCode ^
      subject.hashCode;
}

typedef ImageFetcherFn = Future<CoinImageResult> Function({
  required String year,
  String? mint,
  String? denomination,
  String? series,
  String? subject,
});

/// Production collection card image widget with lifecycle caching, fail-closed
/// storage validation, shipped precedence (`Canonical -> Direct URL -> Reference`),
/// reverse-preference display policy, and MF-V3-3 steal-guard.
class CollectionCardImage extends StatefulWidget {
  final Map<String, dynamic> data;
  final ImageFetcherFn? imageFetcher;

  const CollectionCardImage({
    super.key,
    required this.data,
    this.imageFetcher,
  });

  @override
  State<CollectionCardImage> createState() => _CollectionCardImageState();
}

class _CollectionCardImageState extends State<CollectionCardImage> {
  Future<CoinImageResult>? _refFuture;
  CollectionCardImageRequestKey? _lastKey;

  @override
  void initState() {
    super.initState();
    _checkAndInitFetch();
  }

  @override
  void didUpdateWidget(covariant CollectionCardImage oldWidget) {
    super.didUpdateWidget(oldWidget);
    final newKey = CollectionCardImageRequestKey.fromData(widget.data);
    if (newKey != _lastKey) {
      _checkAndInitFetch();
    }
  }

  void _checkAndInitFetch() {
    _lastKey = CollectionCardImageRequestKey.fromData(widget.data);

    final revUserUrl = extractUserPhoto(widget.data, isObverse: false);
    final obvUserUrl = extractUserPhoto(widget.data, isObverse: true);
    final directUrl = revUserUrl.isNotEmpty ? revUserUrl : obvUserUrl;

    // Fail-closed pre-check: if a direct URL candidate is present but unowned,
    // do not initiate a reference fetch.
    if (directUrl.isNotEmpty && !isOwnedStorageUrl(directUrl)) {
      _refFuture = null;
      return;
    }

    // 1. Shipped Step 1 (my_collection_screen.dart:6369): Canonical Mint asset pair.
    // Note: resolveFromMap (:156) checks hasUserUploadedPhotos(widget.data) and
    // returns null whenever the collector uploaded their own photo (including users%2F).
    final canon = CanonicalMintAssetService.resolveFromMap(widget.data);
    if (canon != null) {
      final canonUrl = canon.reverseUrl.isNotEmpty ? canon.reverseUrl : canon.obverseUrl;
      if (canonUrl.isNotEmpty) {
        _refFuture = null; // Bypasses network reference fetch completely
        return;
      }
    }

    // 2. Shipped Step 2 (my_collection_screen.dart:6377-6383): Direct user photo URL
    // (prefer reverse, support reverse-only).
    if (directUrl.isNotEmpty) {
      _refFuture = null; // Bypasses network reference fetch completely
      return;
    }

    // 3. Shipped Step 3 (my_collection_screen.dart:6385+): Fallback to reference service with 5s timeout.
    final fetcher = widget.imageFetcher ?? CoinImageService.fetchReferenceImages;
    _refFuture = fetcher(
      year: _lastKey!.year,
      mint: _lastKey!.mint.isEmpty ? null : _lastKey!.mint,
      denomination: _lastKey!.denomination.isEmpty ? null : _lastKey!.denomination,
      series: _lastKey!.series.isEmpty ? null : _lastKey!.series,
      subject: _lastKey!.subject.isEmpty ? null : _lastKey!.subject,
    ).timeout(
      const Duration(seconds: 5),
      onTimeout: () => const CoinImageResult(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final revUserUrl = extractUserPhoto(widget.data, isObverse: false);
    final obvUserUrl = extractUserPhoto(widget.data, isObverse: true);

    // Fail-closed security guard on any explicit unowned direct URL candidate
    if (revUserUrl.isNotEmpty && !isOwnedStorageUrl(revUserUrl)) {
      return _buildPlaceholder();
    }
    if (obvUserUrl.isNotEmpty && !isOwnedStorageUrl(obvUserUrl)) {
      return _buildPlaceholder();
    }

    // 1. Shipped Step 1 (:6369-6375): Canonical Mint asset check
    // (automatically yields to collector uploads via hasUserUploadedPhotos at :156)
    final canon = CanonicalMintAssetService.resolveFromMap(widget.data);
    if (canon != null) {
      final canonUrl = canon.reverseUrl.isNotEmpty ? canon.reverseUrl : canon.obverseUrl;
      if (canonUrl.isNotEmpty && isOwnedStorageUrl(canonUrl)) {
        return _buildCoinImage(canonUrl);
      }
    }

    // 2. Shipped Step 2 (:6377-6383): Direct user photo check with reverse preference
    final directUrl = revUserUrl.isNotEmpty ? revUserUrl : obvUserUrl;
    if (directUrl.isNotEmpty) {
      if (isOwnedStorageUrl(directUrl)) {
        return _buildCoinImage(directUrl);
      }
      return _buildPlaceholder();
    }

    // 3. Shipped Step 3 (:6385+): Render reference fetch future
    if (_refFuture == null) {
      return _buildPlaceholder();
    }

    return FutureBuilder<CoinImageResult>(
      future: _refFuture,
      builder: (context, snapshot) {
        final ref = snapshot.data;

        // MF-V3-3 Steal-Guard (:6409-6417): When subject is known and reverse is null,
        // show placeholder instead of falling back to generic obverse.
        final refUrl = (ref?.reverseUrl?.isNotEmpty == true)
            ? ref!.reverseUrl!
            : (_lastKey!.subject.isEmpty && ref?.obverseUrl?.isNotEmpty == true)
                ? ref!.obverseUrl!
                : '';

        if (refUrl.isNotEmpty && isOwnedStorageUrl(refUrl)) {
          return _buildCoinImage(refUrl);
        }

        if (snapshot.connectionState == ConnectionState.waiting) {
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
        }

        return _buildPlaceholder();
      },
    );
  }

  Widget _buildPlaceholder() {
    return const Center(
      child: Icon(Icons.image_not_supported_outlined, size: 36, color: Color(0xFF8B92B4)),
    );
  }

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
          fit: BoxFit.contain, // Prevents coin edge cropping
          errorBuilder: (context, error, stackTrace) => _buildPlaceholder(),
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
}
```

---

### D. Required Import & Delegation Diff in `numista_mobile/lib/screens/my_collection_screen.dart` (MF-B3')
1. **Import Addition (`my_collection_screen.dart:43–46`, immediately after Step 1 Cards import):**
```dart
<<<<
import '../constants.dart';
import '../constants/denomination_canon.dart';
import '../widgets/collection_card_valuation_row.dart';
====
import '../constants.dart';
import '../constants/denomination_canon.dart';
import '../widgets/collection_card_valuation_row.dart';
import '../widgets/collection_card_image.dart';
>>>>
```
2. **Widget Delegation (`my_collection_screen.dart:6356–6479`):**
```dart
<<<<
6356: class _CollectionCardImage extends StatelessWidget {
...
6479: }
====
6356: // Delegated to production widget CollectionCardImage (NET-780c v1.9)
6357: class _CollectionCardImage extends StatelessWidget {
6358:   final Map<String, dynamic> data;
6359:   const _CollectionCardImage({required this.data});
6360:   @override
6361:   Widget build(BuildContext context) => CollectionCardImage(data: data);
6362: }
>>>>
```

---

### E. Surgical CSP Patch in `numista_mobile/firebase.json:276` (MF-I4 — Closed, Preserved)
```json
<<<<
"value": "default-src 'self' https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseapp.com https://*.firebase.com https://storage.googleapis.com https://*.run.app; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://apis.google.com https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.run.app; worker-src blob: 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.gstatic.com; font-src 'self' https://fonts.gstatic.com https://*.gstatic.com data:; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseio.com wss://*.firebaseio.com https://firestore.googleapis.com https://identitytoolkit.googleapis.com https://accounts.google.com https://*.run.app https://numista-backend-568985927038.us-central1.run.app https://localhost:5000; frame-src 'self' https://apis.google.com https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.run.app"
====
"value": "default-src 'self' https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseapp.com https://*.firebase.com https://storage.googleapis.com https://*.run.app; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://apis.google.com https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.run.app; worker-src blob: 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.gstatic.com; font-src 'self' https://fonts.gstatic.com https://*.gstatic.com data:; img-src 'self' data: blob: https://storage.googleapis.com https://firebasestorage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseio.com wss://*.firebaseio.com https://firestore.googleapis.com https://identitytoolkit.googleapis.com https://accounts.google.com https://*.run.app https://numista-backend-568985927038.us-central1.run.app https://localhost:5000; frame-src 'self' https://apis.google.com https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.run.app"
>>>>
```

---

## 4. Execution Gates & Apply Ordering

### A. Pre-Flight Verification Against Code Pin `4d17ca5e` (MF-B2')
Before executing any file modifications on branch `p7-v8.9` (only after CoS $\ge 95$, SAG $\ge 95$, and Founder Eric's explicit typed YES):
```bash
git status
git diff --quiet 4d17ca5e HEAD -- numista_mobile/
```
- **Why `git diff --quiet 4d17ca5e HEAD -- numista_mobile/`:** Commit `4d17ca5e` (`c294fd3c`) is the verified code baseline on `p7-v8.9`. Subsequent commits on `p7-v8.9` are documentation/baton commits under `docs/` and `BETA TEST/`. Checking `git diff --quiet 4d17ca5e HEAD -- numista_mobile/` (prior to Step 1) guarantees zero unreviewed code drift under `numista_mobile/`.
- `origin/main` remains strictly locked at `9f04550a`. Stripe remains locked OFF.

### B. Kaggle & Google Inspector Deletions Boundary (MF-B1')
- NET-816 v1.11 is **PARKED**, and Catalog Chunk 1 (`9bbe20e4`) is scoped exclusively to 2 catalog items (`catalog_service.dart` / `catalog_browse_screen.dart`).
- NET-817's card and image changes (`:3017–3023`, `:3167–3192`, `:6356–6479`) have **zero overlap** with the inspector/Google-button lines (`:150–151`, `:3454`, `:3531–3548`, `:3820`, `:4387–4406`, `:5252–5278`, `:5549–5684`). By default, NET-817 leaves those lines untouched pending CoS re-homing to a dedicated inspector cleanup track (or, if explicitly directed by CoS at execution gate, removes all 7 verified spans atomically in Step 1 while preserving `_onSearchEbay` at `:4408–4426`).

### C. Stated Apply Ordering (MF-B3 — Closed, Preserved)
1. **Step 1 (Cards Plan NET-780b v1.9):** Lands `canonicalYear` at line 77 and denomination regex fixes at lines 431–435 of `canonical_mint_asset_service.dart`, updates `melt_value_service.dart:76–88`, creates `collection_card_valuation_row.dart`, and wires `my_collection_screen.dart`.
2. **Step 2 (Images Plan NET-780c v1.9):** Lands `owned_storage_url.dart`, `collection_image_utils.dart`, `collection_card_image.dart` (calling `CanonicalMintAssetService.canonicalYear`), patches `hasUserUploadedPhotos` at `canonical_mint_asset_service.dart:39`, wires `my_collection_screen.dart`, and updates `firebase.json:276`.

### D. Rollback Protocol
If any post-apply check or test fails:
```bash
git checkout p7-v8.9
git revert --no-edit <Images-commit-hash>
git push origin p7-v8.9
```

---

## 5. Security, Rules & Standing Boundaries
- **No Argon:** Cycle has zero Argon reviews per Founder Eric's typed YES.
- **PLAN ONLY:** Zero code execution, zero deployments, zero Firestore writes without Founder Eric's explicit typed YES.
- **Alerts Only, Never Budget Caps:** Hard spending caps are permanently eliminated; billing alerts set at $20/mo.
- **No AJ PII:** Zero user emails or private credentials in plans, tests, or fixtures.
- **Nightly Stand-Down:** Standing 3:00 AM ET stand-down observed.

---

## 6. Real Automated Test Suites

### 6.1 `numista_mobile/test/utils/owned_storage_url_test.dart` (MF-I1, MF-I2, MF-I7)
Verifies public top-level `isOwnedStorageUrl` against real accepted bucket forms, sanitized Firestore index `public_url` fixtures from `build_image_index.py`, `build_currency_image_index.py`, and `promote_user_photos.py` (`MF-I7`), and malicious/unowned rejected forms:
```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/utils/owned_storage_url.dart';

void main() {
  group('isOwnedStorageUrl Real Allowlist & Index public_url Verification (MF-I1, MF-I7)', () {
    test('Accepts Form A: Real Firebase Storage download URL for project bucket', () {
      const realUserUrl = 'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fanon_user_1%2Fcoins%2F123.jpg?alt=media';
      expect(isOwnedStorageUrl(realUserUrl), isTrue);
    });

    test('MF-I7: Accepts all Firestore reference_images & currency_reference_images public_url forms', () {
      // 1. build_image_index.py:58 (tier 1 us_mint_direct -> us_mint_coin_images)
      const tier1DirectIndexUrl = 'https://storage.googleapis.com/us_mint_coin_images/2024-america-the-beautiful-quarters-coin-proof.jpg';
      // 2. build_image_index.py:68 (tier 1 us_mint_official -> numista-reference-library)
      const tier1OfficialIndexUrl = 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026/2026-CENT-P_reverse.jpg';
      // 3. build_image_index.py:76 (tier 2 wikimedia_uscoin -> numista-reference-library)
      const tier2WikiCoinIndexUrl = 'https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/Kennedy_half_dollar_reverse.png';
      // 4. build_currency_image_index.py:40-42 (currency_reference_images -> numista-reference-library)
      const currencyIndexUrl = 'https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscurrency/US-1-FRN-2017-Obv.jpg';
      // 5. promote_user_photos.py:35 (promoted user uploads bucket)
      const promotedUploadUrl = 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/coins/sample_obv.jpg';

      expect(isOwnedStorageUrl(tier1DirectIndexUrl), isTrue);
      expect(isOwnedStorageUrl(tier1OfficialIndexUrl), isTrue);
      expect(isOwnedStorageUrl(tier2WikiCoinIndexUrl), isTrue);
      expect(isOwnedStorageUrl(currencyIndexUrl), isTrue);
      expect(isOwnedStorageUrl(promotedUploadUrl), isTrue);
    });

    test('Accepts Form B: Real direct upload bucket roots', () {
      const upload1 = 'https://storage.googleapis.com/studio-9101802118-8c9a8-uploads/user_abc/front.jpg';
      const gcsFb = 'https://storage.googleapis.com/studio-9101802118-8c9a8.firebasestorage.app/o/photo.png';
      expect(isOwnedStorageUrl(upload1), isTrue);
      expect(isOwnedStorageUrl(gcsFb), isTrue);
    });

    test('Accepts relative same-origin path', () {
      expect(isOwnedStorageUrl('/assets/images/placeholder.png'), isTrue);
    });

    test('Rejects fabricated buckets', () {
      expect(isOwnedStorageUrl('https://storage.googleapis.com/numista-vault.firebasestorage.app/coin.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://storage.googleapis.com/numista-ai-images/coin.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://storage.googleapis.com/numista-catalog-assets/coin.jpg'), isFalse);
    });

    test('Rejects attacker-registrable wildcards and open prefixes', () {
      expect(isOwnedStorageUrl('https://evil.firebasestorage.app/coin.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://evil.web.app/coin.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://storage.googleapis.com/numista-uploads-studio-evil/coin.jpg'), isFalse);
    });

    test('Rejects protocol-relative backslash and double-slash attacks', () {
      expect(isOwnedStorageUrl(r'/\evil.com/coin.jpg'), isFalse);
      expect(isOwnedStorageUrl('//evil.com/coin.jpg'), isFalse);
    });

    test('Rejects non-HTTPS schemes and empty strings', () {
      expect(isOwnedStorageUrl('http://storage.googleapis.com/us_mint_coin_images/penny.jpg'), isFalse);
      expect(isOwnedStorageUrl(''), isFalse);
      expect(isOwnedStorageUrl(null), isFalse);
    });
  });
}
```

---

### 6.2 `numista_mobile/test/widgets/collection_card_image_test.dart` (MF-I2, MF-I3', MF-I5', MF-I6)
Pumps the production `CollectionCardImage` widget with an injectable fetcher, proving:
1. User-uploaded photo (`users%2F...`) yields in `CanonicalMintAssetService.resolveFromMap` (`MF-I3'`), renders the collector's photo, and bypasses network reference fetch even on a 2026 canonical SKU coin.
2. Reverse-only user photo renders reverse and bypasses network fetch.
3. Unowned/malicious HTTP(S) URL fails closed to placeholder without network fetch.
4. **Non-URL sentinel junk (`'N/A'`, `'pending'`, `'none'`, `'null'`, bare filename `'coin.jpg'`) in `image_url_obverse` returns `''` from `extractUserPhoto` (`MF-I6`) and falls through cleanly to `CanonicalMintAssetService` / `CoinImageService` instead of locking onto placeholder!**
5. 1964 Kennedy Half Dollar reference fallback (`resolveFromMap` proven `isNull`, `fetchCount == 1`).
6. MF-V3-3 Steal-Guard (`subject` populated + `reverseUrl == null` displays placeholder).
7. **Same-State instance `didUpdateWidget` refresh proof (`MF-I5'`):** Uses `key: const ValueKey('card')` across both `pumpWidget` calls and asserts `expect(identical(stateBefore, stateAfter), isTrue)` and `expect(fetchCount, 2)`.

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/canonical_mint_asset_service.dart';
import 'package:numista_ai/services/coin_image_service.dart';
import 'package:numista_ai/utils/collection_image_utils.dart';
import 'package:numista_ai/widgets/collection_card_image.dart';

void main() {
  group('CollectionCardImage Production Widget Tests (MF-I2, MF-I3\', MF-I5\', MF-I6)', () {
    testWidgets('Case 1 (MF-I3\'): User-uploaded Firebase Storage photo (users%2F) yields in resolveFromMap, renders user photo, and bypasses network fetch even on 2026 SKU', (tester) async {
      int fetchCount = 0;
      const userUrl = 'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fanon%2Fcoins%2Fobv.jpg';
      final data = {
        'image_url_obverse': userUrl,
        'Year': '2026',
        'mint_mark': 'P',
        'denomination': '1¢',
        'title': '2026 Lincoln Cent',
      };

      // Prove hasUserUploadedPhotos recognizes URL-encoded users%2F so resolveFromMap returns null
      expect(CanonicalMintAssetService.hasUserUploadedPhotos(data), isTrue);
      expect(CanonicalMintAssetService.resolveFromMap(data), isNull);

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardImage(
              data: data,
              imageFetcher: ({required year, mint, denomination, series, subject}) async {
                fetchCount++;
                return const CoinImageResult();
              },
            ),
          ),
        ),
      );

      expect(fetchCount, 0, reason: 'Valid user photo must bypass network reference fetch');
      final img = tester.widget<Image>(find.byType(Image));
      expect((img.image as NetworkImage).url, equals(userUrl));
    });

    testWidgets('Case 2: Reverse-only user photo renders reverse and bypasses network fetch', (tester) async {
      int fetchCount = 0;
      const revUrl = 'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fanon%2Fcoins%2Frev.jpg';
      final data = {
        'image_url_reverse': revUrl,
        'Year': '1964',
        'denomination': 'Half Dollar',
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardImage(
              data: data,
              imageFetcher: ({required year, mint, denomination, series, subject}) async {
                fetchCount++;
                return const CoinImageResult();
              },
            ),
          ),
        ),
      );

      expect(fetchCount, 0, reason: 'Valid reverse-only user photo must bypass network fetch');
      final img = tester.widget<Image>(find.byType(Image));
      expect((img.image as NetworkImage).url, equals(revUrl));
    });

    testWidgets('Case 3: Unowned/malicious HTTP(S) user photo fails closed without network fetch', (tester) async {
      int fetchCount = 0;
      final data = {
        'image_url_obverse': 'https://evil.firebasestorage.app/malicious.jpg',
        'Year': '1964',
        'denomination': 'Half Dollar',
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardImage(
              data: data,
              imageFetcher: ({required year, mint, denomination, series, subject}) async {
                fetchCount++;
                return const CoinImageResult();
              },
            ),
          ),
        ),
      );

      expect(fetchCount, 0, reason: 'Unowned user photo must fail closed without network fetch');
      expect(find.byIcon(Icons.image_not_supported_outlined), findsOneWidget);
    });

    testWidgets('Case 4 (MF-I6): Non-URL sentinel strings ("N/A", "pending", "none", bare filename) return "" from extractUserPhoto and fall through to reference/canonical', (tester) async {
      for (final junk in const ['N/A', 'pending', 'none', 'null', '—', 'gs://bucket/file.jpg', 'IMG_001.jpg']) {
        final data = {
          'image_url_obverse': junk,
          'Year': '1964',
          'mint_mark': 'D',
          'denomination': 'Half Dollar',
        };

        expect(extractUserPhoto(data, isObverse: true), isEmpty, reason: 'Junk "$junk" must be ignored by extractUserPhoto');

        int fetchCount = 0;
        await tester.pumpWidget(
          MaterialApp(
            home: Scaffold(
              body: CollectionCardImage(
                key: ValueKey('junk_$junk'),
                data: data,
                imageFetcher: ({required year, mint, denomination, series, subject}) async {
                  fetchCount++;
                  return const CoinImageResult(
                    reverseUrl: 'https://storage.googleapis.com/us_mint_coin_images/kennedy/1964_rev.jpg',
                  );
                },
              ),
            ),
          ),
        );
        await tester.pump();

        expect(fetchCount, 1, reason: 'Card with non-URL junk "$junk" must fall through to reference fetcher');
        expect(find.byType(Image), findsOneWidget);
      }
    });

    testWidgets('Case 5: Reference fetch triggered when no user photo and no canonical asset (1964 Kennedy)', (tester) async {
      final data = {
        'Year': '1964',
        'mint_mark': 'D',
        'denomination': 'Half Dollar',
        'program_series': 'Kennedy Half Dollar',
      };

      expect(CanonicalMintAssetService.resolveFromMap(data), isNull);

      int fetchCount = 0;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardImage(
              data: data,
              imageFetcher: ({required year, mint, denomination, series, subject}) async {
                fetchCount++;
                return const CoinImageResult(
                  reverseUrl: 'https://storage.googleapis.com/us_mint_coin_images/kennedy/1964_rev.jpg',
                );
              },
            ),
          ),
        ),
      );
      await tester.pump();

      expect(fetchCount, 1, reason: 'Reference fetcher must be called exactly once');
      expect(find.byType(Image), findsOneWidget);
    });

    testWidgets('Case 6: MF-V3-3 Steal-Guard: Subject known + reverse null displays placeholder (no obverse fallback)', (tester) async {
      int fetchCount = 0;
      final data = {
        'Year': '1964',
        'denomination': 'Half Dollar',
        'theme_subject': 'Specific Commemorative Subject',
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardImage(
              data: data,
              imageFetcher: ({required year, mint, denomination, series, subject}) async {
                fetchCount++;
                return const CoinImageResult(
                  obverseUrl: 'https://storage.googleapis.com/us_mint_coin_images/generic_obv.jpg',
                  reverseUrl: null,
                );
              },
            ),
          ),
        ),
      );
      await tester.pump();

      expect(fetchCount, 1);
      expect(find.byIcon(Icons.image_not_supported_outlined), findsOneWidget);
    });

    testWidgets('Case 7 (MF-I5\'): Semantic RequestKey refresh on the SAME State instance triggers second fetch when Year changes from "" to "1964"', (tester) async {
      int fetchCount = 0;
      const cardKey = ValueKey('card');
      final dataInitial = {
        'Year': '',
        'denomination': 'Half Dollar',
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardImage(
              key: cardKey,
              data: dataInitial,
              imageFetcher: ({required year, mint, denomination, series, subject}) async {
                fetchCount++;
                return const CoinImageResult();
              },
            ),
          ),
        ),
      );
      await tester.pump();
      final stateBefore = tester.state(find.byKey(cardKey));
      expect(fetchCount, 1);

      final dataUpdated = {
        'Year': '1964',
        'denomination': 'Half Dollar',
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardImage(
              key: cardKey,
              data: dataUpdated,
              imageFetcher: ({required year, mint, denomination, series, subject}) async {
                fetchCount++;
                return const CoinImageResult();
              },
            ),
          ),
        ),
      );
      await tester.pump();
      final stateAfter = tester.state(find.byKey(cardKey));

      expect(identical(stateBefore, stateAfter), isTrue, reason: 'Must update the exact same State instance via didUpdateWidget');
      expect(fetchCount, 2, reason: 'Mutating Year must invalidate RequestKey and trigger second fetch');
    });
  });
}
```

---

## 7. Delivery & Sign-Off Requirements
- **Verification Command (Post-Approval Execution Only):**
  `flutter test test/utils/owned_storage_url_test.dart test/widgets/collection_card_image_test.dart`
- **Review Gate:** Requires independent score $\ge 95$ from Grok Bot CoS and Stand Alone Grok (SAG, grok-4.7) on **both** `FAILFIX_PLAN_NET-780b_CARDS_v1.9.md` and `FAILFIX_PLAN_NET-780c_IMAGES_v1.9.md` prior to Founder Eric's typed YES.
