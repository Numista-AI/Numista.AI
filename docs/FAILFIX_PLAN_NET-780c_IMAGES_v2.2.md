# FAILFIX PLAN v2.2: Broken Images & Storage URL Security Guard (NET-780c)
**To:** Grok Bot CoS, Stand Alone Grok (SAG, grok-4.7), Antigravity Desk, Founder Eric  
**From:** GB CoS fresh writer (v2.1; closes SAG must-fixes from `SAG_API_RESPONSE_20261108-072843.md`, Images 69 FAIL). v2.0 and earlier: Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`).  
**Date:** 8 November 2026, ~07:55 ET  
**Pin:** `4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235`.  
**Reference Batons & Scores:**  
- `BATON_NET-780_FAILFIX_PLAN_NET-748-v5-FT_v1_2026-11-04-1658.md`  
- `COS_SCORE_NET-817_CARDS_IMAGES_v1.9_20261107.md` (Cards 95/100 PASS, Images 78/100 FAIL, Combined 86/100 FAIL)  
- `RADIO_NET-838_GROKCOS-to-AGCOS_REVISE-817-v2.0_20261107.md`  
- `BATON_NET-817_REVISE_CARDS-IMAGES_v2.0_TO-AGCOS-V5_cfe23a7a_ATTEMPT2_PER-COS-86_20261107.md`  
**Directives & Audit Authority:**  
- `GB CoS SCORE v1.9` & `RADIO_NET-838`: Narrow delta resolving the single open item **`MF-I7'`** with verbatim `git show 4d17ca5e:...` quotes from `numista_backend/_scripts/build_image_index.py`, `numista_backend/_scripts/build_currency_image_index.py`, `numista_backend/_scripts/promote_user_photos.py`, and `numista_mobile/lib/services/coin_image_service.dart`, while preserving every item marked **Closed** in `COS_SCORE_NET-817_CARDS_IMAGES_v1.9_20261107.md`.  
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

## 0a. v2.2 Close-Out of CoS-94 Must-Fix (round 3, 08:12 ET; ONLY this item changed)

| # | CoS-94 must-fix | v2.2 change | Evidence |
|---|---|---|---|
| **MF-SAG-I3 (raw-dot)** | Literal `.`/`..` were only checked after `Uri.tryParse`, whose default implementation normalizes them away | `isOwnedStorageUrl` now checks the **raw trimmed string** before parsing: strip `?`/`#` suffix, split on `/`, reject any segment exactly `.` or `..`. Encoded checks and post-parse decoded-segment checks retained. §6.1 adds in-allowlist cases (`us_mint_coin_images/a/../x.jpg`, `./x.jpg`, cross-allowed-root `us_mint_coin_images/../numista-reference-library/x.jpg`) plus a positive that `%20` still passes. | https://api.dart.dev/dart-core/Uri/normalizePath.html (per CoS). No Dart test run. |

## 0. v2.1 Close-Out of SAG Must-Fixes (ONLY these items changed)

| # | SAG must-fix | v2.1 change | Evidence (`git show 4d17ca5e:…`) |
| :--- | :--- | :--- | :--- |
| **MF-SAG-I1** | Unowned URL in either photo field suppressed canonical and the other valid side | `build` and `_checkAndInitFetch` share one `_select()` decision: (a) if `CanonicalMintAssetService.hasUserUploadedPhotos(data)` (pin `:27`, after the `users%2f` patch) → render the **selected** owned side (reverse, else obverse); if that selected URL is unowned → placeholder; never fall to canonical; the non-selected side is ignored. (b) otherwise unowned/non-URL fields are treated as **absent**: owned canonical (`resolveFromMap`) → owned direct (reverse-preferred, unowned side skipped) → reference. An unowned URL is never rendered. Case 3 split into 3a (non-user unowned URL ignored, reference proceeds) and 3b (confirmed user upload, unowned → placeholder); Cases 8/9 added. Case 8 asserts against `resolveFromMap`'s own output rather than a hardcoded canonical URL. | Shipped order `my_collection_screen.dart:6369–6383` (canonical → direct → reference). |
| **MF-SAG-I2** | §2.C quote invented alias reads and `_buildNetworkImage` | §2.C `:6369–6383` re-quoted verbatim: two-field read `_cleanUrl(data[_F.imageObverse])` / `_cleanUrl(data[_F.imageReverse])` and `_buildCoinImage(...)` at `:6373` / `:6382`. Alias expansion in `extractUserPhoto` is labeled **new behavior**, and it must include `_F.imageObverse` / `_F.imageReverse` (constant values not re-read here — stated honestly). | `:6377 final obv = _cleanUrl(data[_F.imageObverse]);` `:6378 final rev = _cleanUrl(data[_F.imageReverse]);` `:6379 final directUrl = rev.isNotEmpty ? rev : obv;  // Prefer reverse (distinct design)` `:6382 return _buildCoinImage(directUrl);` |
| **MF-SAG-I3** | Prefix allowlist had no traversal normalization | `isOwnedStorageUrl` rejects backslash, userinfo, port, raw-lowercase `%2e`, `%5c`, and `%2f..`; rejects any decoded path segment (also split on `/` after decoding) equal to `.`/`..` or empty, then re-checks the bucket root on the validated segments. `%20` (emitter `:302` shape) still accepted. Relative paths: single `/`, no `//`, no `..`. New negative cases in §6.1. | — |
| **MF-SAG-I4** | 5 s `timeout` called "Shipped Step 3" | Timeout **removed**; reference fetch behaves as shipped `:6399–6406` (no timeout). | Pin `:6399 return FutureBuilder<CoinImageResult>(` … `:6406 ),` — no `.timeout`. |
| **MF-SAG-I5** | Stale reference lookup after photo change | `didUpdateWidget` re-runs `_checkAndInitFetch` when the RequestKey **or** the selection signature (`hasUserUploadedPhotos`, selected direct URL, its owned-ness) changes. Case 10: clearing the user URL on the same State starts a reference fetch. | — |
| **MF-SAG-I6** | Rollback hole | §4.D: assert `p7-v8.9`, clean tree, preflight; revert Images (it is applied after Cards, so it reverts first); push `p7-v8.9` only after success; never main. | — |
| **MF-SAG-I7** | balabaskar coverage claimed but not asserted | Fixture `…/reference_library/balabaskar_coins/…` added and asserted in §6.1. | Pin `build_image_index.py:84` `"reference_library/balabaskar_coins/",` (quoted in §2.B). |

## 1. Executive Summary & Itemized Must-Fix Closeout Table (v1.9 $\rightarrow$ v2.0 Delta)

Plan v2.0 preserves every item marked **Closed** in `COS_SCORE_NET-817_CARDS_IMAGES_v1.9_20261107.md` (`MF-B1'`, `MF-B2'`, `MF-B3'`, `MF-I1`, `MF-I2`, `MF-I3'`, `MF-I4`, `MF-I5'`, `MF-I6`) and closes the sole remaining blocking item **`MF-I7'`** with verbatim `git show 4d17ca5e:...` quotes:

| Must-Fix # | Must-Fix Description | Plan v2.0 Resolution & Verbatim Grounding at `4d17ca5e` | Plan Section |
| :--- | :--- | :--- | :--- |
| **MF-I7'** | **BLOCKING — Re-Quote Real Index Emitters from `git show 4d17ca5e`:** Use real paths `numista_backend/_scripts/build_image_index.py` (`SCAN_TARGETS`, `FIRESTORE_COLLECTION = "coin_image_index"`, `public_url = f"{PUBLIC_URL_BASE}/{bucket}/{encoded_path}"`), `numista_backend/_scripts/build_currency_image_index.py` (`FIRESTORE_COLLECTION = "currency_image_index"`, `REFERENCE_BUCKET = "numista-reference-library"`, `GCS_PREFIX = "reference_library/us_banknotes/"`, `public_url = f"{PUBLIC_URL_BASE}/{REFERENCE_BUCKET}/{blob.name}"`), `numista_backend/_scripts/promote_user_photos.py` (`BUCKET_NAME = "numista-uploads-studio-9101802118-8c9a8"`, `REF_PREFIX = "reference"`, `PUBLIC_BASE = "https://storage.googleapis.com"`, `return f"{PUBLIC_BASE}/{BUCKET_NAME}/{dest_path}"`), and `numista_mobile/lib/services/coin_image_service.dart` (`static const _collection = 'coin_image_index';`, `bestObvUrl = d['public_url'] as String?;` at `:567`, `bestRevUrl = d['public_url'] as String?;` at `:583`). Align test fixtures to real emitted path shapes. | Drops all references to nonexistent `scripts/reference_library/`, `SOURCES`, `CURRENCY_PREFIX`, `UPLOADS_BUCKET`, `REF_BUCKET`, `reference_images`, and `currency_reference_images`. Quotes the exact verbatim lines from `git show 4d17ca5e:numista_backend/_scripts/build_image_index.py` (`:44–103`, `:301–316`), `git show 4d17ca5e:numista_backend/_scripts/build_currency_image_index.py` (`:38–42`, `:267–281`), `git show 4d17ca5e:numista_backend/_scripts/promote_user_photos.py` (`:16–18`, `:34–37`, `:125–130`), and `git show 4d17ca5e:numista_mobile/lib/services/coin_image_service.dart` (`:16–18`, `:561–589`). Updates `owned_storage_url_test.dart` (§6.1) with sanitized fixtures matching every real emitted path shape (`Numista_Attributed_Coins%20(1)/...`, `reference_library/bulk_programs/...`, `reference_library/wikimedia_uscoin/...`, `reference_library/rare_uscoin/...`, `reference_library/balabaskar_coins/...`, `reference_library/2026_series/...`, `reference_library/user_contributed/...`, `reference_library/us_banknotes/...`, and `reference/{program_slug}/{year}_{program_slug}_{side}.jpg`). | §2.B, §6.1 |
| **MF-B1'** | **Orphaned Kaggle/Google Inspector Deletions & Verbatim Quotes (CLOSED — Preserved):** | Preserved verbatim from v1.9 (§2.A, §4.B). | §2.A, §4.B |
| **MF-B2'** | **Pin Code Commit (`4d17ca5e`) & Honest DTG (CLOSED — Preserved):** | Pre-flight `git diff --quiet 4d17ca5e HEAD -- numista_mobile/`; honest observed wall-clock DTG (`2026-11-07 16:37 ET`). | Header, §4.A |
| **MF-B3'** | **Include Required Imports in `my_collection_screen.dart` Diff (CLOSED — Preserved):** | Preserved verbatim from v1.9 (§3.D). | §3.D |
| **MF-I3'** | **Honest Image Precedence (`Canonical -> Direct URL -> Reference`) + `users%2f` Fix (CLOSED — Preserved):** | Preserved verbatim from v1.9 (§2.C, §3.C, §6.2). | §2.C, §3.C, §6.2 |
| **MF-I6** | **Preserve Shipped `_cleanUrl` Semantics in `extractUserPhoto` (CLOSED — Preserved):** | Preserved verbatim from v1.9 (§2.C, §3.B, §6.2). | §2.C, §3.B, §6.2 |
| **MF-I5'** | **Same-State Instance Refresh Proof & `ref_image_widget.dart` Path Fix (CLOSED — Preserved):** | Preserved verbatim from v1.9 (§2.B, §6.2). | §2.B, §6.2 |

---

## 2. Root Cause Analysis & Verbatim Grounding (`git show 4d17ca5e:...`)

### A. Kaggle & Google Images Structural Deletion Ownership & Correct Quotes (MF-B1' — Closed, Preserved)
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
**Ownership Boundary (`MF-B1'`):** NET-816 v1.11 is **PARKED**, and Catalog Chunk 1 (`9bbe20e4`) does not own `my_collection_screen.dart`. NET-817's card and image changes (`:3017–3023`, `:3167–3192`, `:6356–6479`) are 100% independent of the inspector/Google-button lines and leave them untouched by default pending CoS re-homing (or, if explicitly directed by CoS at execution gate, remove all 7 spans atomically in Step 1 while preserving `_onSearchEbay` at `:4408–4426`).

---

### B. Real Storage Bucket URLs & Verbatim Firestore Index `public_url` Proof (MF-I1, MF-I5', MF-I7')
Verifying all storage URL emitters across `numista_mobile/` and `numista_backend/_scripts/` via `git show 4d17ca5e:...`:

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
6. **Verbatim Proof of Firestore `coin_image_index` and `currency_image_index` Emitters (`MF-I7'`):**
   - **`git show 4d17ca5e:numista_backend/_scripts/build_image_index.py` lines 44–103 and 301–316:**
     ```python
     44: PROJECT = "studio-9101802118-8c9a8"
     45: FIRESTORE_COLLECTION = "coin_image_index"
     46: PUBLIC_URL_BASE = "https://storage.googleapis.com"
     ...
     52: # Buckets to scan: (bucket_name, gcs_prefix, source_tier, source_label, attribution)
     53: SCAN_TARGETS = [
     54:     (
     55:         "us_mint_coin_images",
     56:         "Numista_Attributed_Coins (1)/",
     57:         1,
     58:         "US Mint",
     59:         "United States Mint image",
     60:     ),
     61:     (
     62:         "numista-reference-library",
     63:         "reference_library/bulk_programs/",
     64:         2,
     65:         "Numista Reference Library",
     66:         "",
     67:     ),
     68:     (
     69:         "numista-reference-library",
     70:         "reference_library/wikimedia_uscoin/",
     71:         3,
     72:         "Wikimedia Commons",
     73:         "Wikimedia Commons / Public Domain",
     74:     ),
     75:     (
     76:         "numista-reference-library",
     77:         "reference_library/rare_uscoin/",
     78:         2,
     79:         "Numista Reference Library (Rare)",
     80:         "",
     81:     ),
     82:     (
     83:         "numista-reference-library",
     84:         "reference_library/balabaskar_coins/",
     85:         2,
     86:         "Numista Reference Library",
     87:         "",
     88:     ),
     89:     (
     90:         "numista-reference-library",
     91:         "reference_library/2026_series/",
     92:         2,
     93:         "Numista Reference Library (2026)",
     94:         "",
     95:     ),
     96:     (
     97:         "numista-reference-library",
     98:         "reference_library/user_contributed/",
     99:         5,
     100:         "User Contributed",
     101:         "",  # pulled from per-folder MANIFEST.json
     102:     ),
     103: ]
     ...
     301:     # Build public URL
     302:     encoded_path = blob_name.replace(" ", "%20")
     303:     public_url = f"{PUBLIC_URL_BASE}/{bucket}/{encoded_path}"
     304: 
     305:     return {
     306:         "canonical_key": canonical_key,
     307:         "year":          year,
     308:         "mint":          mint,
     309:         "subject":       subject,
     310:         "program":       program,
     311:         "side":          side,
     312:         "gcs_path":      f"gs://{bucket}/{blob_name}",
     313:         "public_url":    public_url,
     314:         "filename":      filename,
     315:         "source_tier":   source_tier,
     316:     }
     ```
     Every tuple in `SCAN_TARGETS` (`:53–103`) uses `bucket_name` `"us_mint_coin_images"` or `"numista-reference-library"`, and line 303 constructs `public_url = f"{PUBLIC_URL_BASE}/{bucket}/{encoded_path}"` where `PUBLIC_URL_BASE = "https://storage.googleapis.com"`.
   - **`git show 4d17ca5e:numista_backend/_scripts/build_currency_image_index.py` lines 38–42 and 267–281:**
     ```python
     38: PROJECT_ID = "studio-9101802118-8c9a8"
     39: FIRESTORE_COLLECTION = "currency_image_index"
     40: REFERENCE_BUCKET = "numista-reference-library"
     41: GCS_PREFIX = "reference_library/us_banknotes/"
     42: PUBLIC_URL_BASE = "https://storage.googleapis.com"
     ...
     267:         public_url = f"{PUBLIC_URL_BASE}/{REFERENCE_BUCKET}/{blob.name}"
     268:         now_iso = datetime.now(timezone.utc).isoformat()
     269: 
     270:         doc_data = {
     271:             "catalog_key": catalog_key,
     ...
     280:             "gcs_path": f"gs://{REFERENCE_BUCKET}/{blob.name}",
     281:             "public_url": public_url,
     ```
   - **`git show 4d17ca5e:numista_backend/_scripts/promote_user_photos.py` lines 16–18, 34–37, and 125–130:**
     ```python
     16:   • Copies the user photo to gs://numista-uploads-studio-9101802118-8c9a8/reference/
     17:     at path: reference/{program_slug}/{year}_{program_slug}_{side}.jpg
     18:   • Marks the coin_image_index doc with source_tier=1, attribution='User Contribution'
     ...
     34: PROJECT       = "studio-9101802118-8c9a8"
     35: BUCKET_NAME   = "numista-uploads-studio-9101802118-8c9a8"
     36: REF_PREFIX    = "reference"    # destination path prefix inside the bucket
     37: PUBLIC_BASE   = "https://storage.googleapis.com"
     ...
     125:     dest_blob = gcs.bucket(BUCKET_NAME).blob(dest_path)
     126:     content_type = src_blob.content_type or "image/jpeg"
     127:     dest_blob.upload_from_string(img_bytes, content_type=content_type)
     128:     dest_blob.make_public()
     129:     
     130:     return f"{PUBLIC_BASE}/{BUCKET_NAME}/{dest_path}"
     ```
   - **`git show 4d17ca5e:numista_mobile/lib/services/coin_image_service.dart` lines 16–18 and 561–589:**
     ```dart
     16: class CoinImageService {
     17:   static const _collection = 'coin_image_index';
     ...
     561:         if (needsObv && (!hasSubject || isSubjectBase)) {
     562:           final obvDoc = await db.collection(_collection)
     563:               .doc('${base}_obverse').get();
     564:           if (obvDoc.exists) {
     565:             final d = obvDoc.data()!['obverse'] as Map<String, dynamic>?;
     566:             if (d != null) {
     567:               bestObvUrl = d['public_url'] as String?;
     568:               bestAttr  ??= d['attribution'] as String?;
     569:               bestLabel ??= d['source_label'] as String?;
     570:               bestKey   ??= base;
     571:             }
     572:           }
     573:         }
     574: 
     575:         // STEAL-GUARD: only accept reverse from subject-containing bases
     576:         // when a subject is known. Generic reverse = honest placeholder.
     577:         if (needsRev && (!hasSubject || isSubjectBase)) {
     578:           final revDoc = await db.collection(_collection)
     579:               .doc('${base}_reverse').get();
     580:           if (revDoc.exists) {
     581:             final d = revDoc.data()!['reverse'] as Map<String, dynamic>?;
     582:             if (d != null) {
     583:               bestRevUrl = d['public_url'] as String?;
     584:               bestAttr  ??= d['attribution'] as String?;
     585:               bestLabel ??= d['source_label'] as String?;
     586:               bestKey   ??= base;
     587:             }
     588:           }
     589:         }
     ```
   **Conclusion (`MF-I7'`):** 100% of `public_url` values written to Firestore `coin_image_index` and `currency_image_index` (and read at `coin_image_service.dart:567, 583`) begin with `https://storage.googleapis.com/us_mint_coin_images/`, `https://storage.googleapis.com/numista-reference-library/`, or `https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/`, all three of which are explicitly permitted by `isOwnedStorageUrl`!

---

### C. Shipped `_CollectionCardImage` Precedence, `_cleanUrl` Semantics, & Steal-Guard (MF-I3', MF-I6 — Closed, Preserved)
In `git show 4d17ca5e:numista_mobile/lib/screens/my_collection_screen.dart`, lines 6356–6420 read verbatim:
```dart
6356: class _CollectionCardImage extends StatelessWidget {
6357:   final Map<String, dynamic> data;
6358:   const _CollectionCardImage({required this.data});
6359: 
6360:   static String _cleanUrl(dynamic val) {
6361:     if (val == null) return '';
6362:     final s = val.toString().trim();
6363:     if (s.isEmpty || s.startsWith('gs://') || !s.startsWith('http')) return '';
6364:     return s;
6365:   }
6366: 
6367:   @override
6368:   Widget build(BuildContext context) {
6369:     final canon = CanonicalMintAssetService.resolveFromMap(data);
6370:     if (canon != null) {
6371:       final canonUrl = canon.reverseUrl.isNotEmpty ? canon.reverseUrl : canon.obverseUrl;
6372:       if (canonUrl.isNotEmpty) {
6373:         return _buildCoinImage(canonUrl);
6374:       }
6375:     }
6376: 
6377:     final obv = _cleanUrl(data[_F.imageObverse]);
6378:     final rev = _cleanUrl(data[_F.imageReverse]);
6379:     final directUrl = rev.isNotEmpty ? rev : obv;  // Prefer reverse (distinct design)
6380: 
6381:     if (directUrl.isNotEmpty) {
6382:       return _buildCoinImage(directUrl);
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
  if (trimmed.isEmpty || trimmed.contains(r'\')) return false;
  final lower = trimmed.toLowerCase();
  // v2.1 MF-SAG-I3: encoded dot / backslash / encoded-slash-dot traversal rejected before parsing
  if (lower.contains('%2e') || lower.contains('%5c') || lower.contains('%2f.')) return false;
  // v2.2: raw literal dot segments rejected BEFORE Uri.tryParse (Dart Uri normalizes them away)
  if (trimmed.split(RegExp(r'[?#]')).first.split('/').any((p) => p == '.' || p == '..')) return false;

  bool badSegs(Iterable<String> segs) =>
      segs.expand((p) => p.split('/')).any((p) => p == '.' || p == '..');

  // 1. Relative same-origin paths: single leading '/', no '//', no dot segments
  if (trimmed.startsWith('/')) {
    if (trimmed.startsWith('//')) return false;
    final segs = trimmed.substring(1).split('/');
    return !segs.any((p) => p.isEmpty || p == '.' || p == '..');
  }

  // 2. Strict HTTPS parsing
  final uri = Uri.tryParse(trimmed);
  if (uri == null || uri.scheme != 'https') return false;
  if (uri.userInfo.isNotEmpty || uri.hasPort) return false;

  final host = uri.host.toLowerCase();
  final segs = uri.pathSegments; // decoded
  if (segs.isEmpty || segs.any((p) => p.isEmpty) || badSegs(segs)) return false;

  // 3. Form A: Firebase Storage download URL for the real project bucket
  if (host == 'firebasestorage.googleapis.com') {
    return segs.length >= 4 && segs[0] == 'v0' && segs[1] == 'b' &&
        segs[2] == 'studio-9101802118-8c9a8.firebasestorage.app' && segs[3] == 'o';
  }

  // 4. Form B: Google Cloud Storage, exact bucket root (first decoded segment), re-checked after validation
  if (host == 'storage.googleapis.com') {
    const roots = {
      'us_mint_coin_images',
      'numista-reference-library',
      'studio-9101802118-8c9a8-uploads',
      'numista-uploads-studio-9101802118-8c9a8',
      'studio-9101802118-8c9a8.firebasestorage.app',
    };
    return segs.length >= 2 && roots.contains(segs.first);
  }

  return false;
}
```

---

### B. User Photo Helper with Shipped `_cleanUrl` Semantics: `numista_mobile/lib/utils/collection_image_utils.dart` (MF-I2, MF-I6 — Closed, Preserved)
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

### C. Patch `hasUserUploadedPhotos` in `canonical_mint_asset_service.dart:31–50` & Public `CollectionCardImage` Widget (MF-I2, MF-I3', MF-I6 — Closed, Preserved)

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

/// v2.1: result of the shared precedence decision.
class _Selection {
  final String? url;
  final bool needsReference;
  final String signature;
  const _Selection.image(String this.url, this.signature) : needsReference = false;
  const _Selection.placeholder(this.signature) : url = null, needsReference = false;
  const _Selection.reference(this.signature) : url = null, needsReference = true;
}

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

  String? _lastSelSig;

  @override
  void didUpdateWidget(covariant CollectionCardImage oldWidget) {
    super.didUpdateWidget(oldWidget);
    final newKey = CollectionCardImageRequestKey.fromData(widget.data);
    // v2.1 MF-SAG-I5: also refresh when the photo selection changes (cleared/added/changed URL)
    if (newKey != _lastKey || _select().signature != _lastSelSig) {
      _checkAndInitFetch();
    }
  }

  /// v2.1 MF-SAG-I1: ONE precedence decision shared by build() and _checkAndInitFetch().
  _Selection _select() {
    final data = widget.data;
    final rev = extractUserPhoto(data, isObverse: false);
    final obv = extractUserPhoto(data, isObverse: true);
    final userUploaded = CanonicalMintAssetService.hasUserUploadedPhotos(data); // pin :27 (+users%2f patch)

    if (userUploaded) {
      final selected = rev.isNotEmpty ? rev : obv;             // preferred side only
      if (selected.isNotEmpty && isOwnedStorageUrl(selected)) return _Selection.image(selected, 'U|$selected');
      return const _Selection.placeholder('U|unowned');         // never fall through to canonical
    }

    // Not a confirmed user upload: unowned / non-URL fields are treated as ABSENT.
    final canon = CanonicalMintAssetService.resolveFromMap(data);
    if (canon != null) {
      final c = canon.reverseUrl.isNotEmpty ? canon.reverseUrl : canon.obverseUrl;
      if (c.isNotEmpty && isOwnedStorageUrl(c)) return _Selection.image(c, 'C|$c');
    }
    final ownedRev = (rev.isNotEmpty && isOwnedStorageUrl(rev)) ? rev : '';
    final ownedObv = (obv.isNotEmpty && isOwnedStorageUrl(obv)) ? obv : '';
    final direct = ownedRev.isNotEmpty ? ownedRev : ownedObv;
    if (direct.isNotEmpty) return _Selection.image(direct, 'D|$direct');
    return const _Selection.reference('R');
  }

  void _checkAndInitFetch() {
    _lastKey = CollectionCardImageRequestKey.fromData(widget.data);
    final sel = _select();
    _lastSelSig = sel.signature;
    if (!sel.needsReference) {
      _refFuture = null;
      return;
    }
    // Reference step: same call shape as shipped :6399-6406. v2.1 MF-SAG-I4: NO timeout (shipped has none).
    final fetcher = widget.imageFetcher ?? CoinImageService.fetchReferenceImages;
    _refFuture = fetcher(
      year: _lastKey!.year,
      mint: _lastKey!.mint.isEmpty ? null : _lastKey!.mint,
      denomination: _lastKey!.denomination.isEmpty ? null : _lastKey!.denomination,
      series: _lastKey!.series.isEmpty ? null : _lastKey!.series,
      subject: _lastKey!.subject.isEmpty ? null : _lastKey!.subject,
    );
  }

  @override
  Widget build(BuildContext context) {
    final sel = _select();
    if (sel.url != null) return _buildCoinImage(sel.url!);
    if (!sel.needsReference || _refFuture == null) return _buildPlaceholder();

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
6356: // Delegated to production widget CollectionCardImage (NET-780c v2.0)
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
- `origin/main` remains strictly locked at `9f04550a`. Stripe remains locked OFF.

### B. Kaggle & Google Inspector Deletions Boundary (MF-B1')
- NET-816 v1.11 is **PARKED**, and Catalog Chunk 1 (`9bbe20e4`) is scoped exclusively to 2 catalog items (`catalog_service.dart` / `catalog_browse_screen.dart`).
- NET-817's card and image changes (`:3017–3023`, `:3167–3192`, `:6356–6479`) have **zero overlap** with the inspector/Google-button lines (`:150–151`, `:3454`, `:3531–3548`, `:3820`, `:4387–4406`, `:5252–5278`, `:5549–5684`). By default, NET-817 leaves those lines untouched pending CoS re-homing to a dedicated inspector cleanup track.

### C. Stated Apply Ordering (MF-B3 — Closed, Preserved)
1. **Step 1 (Cards Plan NET-780b v2.0):** Lands `canonicalYear` at line 77 and denomination regex fixes at lines 431–435 of `canonical_mint_asset_service.dart`, updates `melt_value_service.dart:76–88`, creates `collection_card_valuation_row.dart`, and wires `my_collection_screen.dart`.
2. **Step 2 (Images Plan NET-780c v2.0):** Lands `owned_storage_url.dart`, `collection_image_utils.dart`, `collection_card_image.dart` (calling `CanonicalMintAssetService.canonicalYear`), patches `hasUserUploadedPhotos` at `canonical_mint_asset_service.dart:39`, wires `my_collection_screen.dart`, and updates `firebase.json:276`.

### D. Rollback Protocol
If any post-apply check or test fails:
```bash
#!/usr/bin/env bash
set -euo pipefail
IMAGES=<Images-commit-hash>        # recorded at apply time
BR=$(git rev-parse --abbrev-ref HEAD)
[ "$BR" = "p7-v8.9" ] || { echo "ABORT: HEAD is '$BR', not p7-v8.9"; exit 1; }
git diff --quiet && git diff --cached --quiet || { echo "ABORT: dirty tree"; exit 1; }
git cat-file -e "$IMAGES^{commit}" && git merge-base --is-ancestor "$IMAGES" HEAD || { echo "ABORT: $IMAGES missing"; exit 1; }
# Images was applied after Cards, so it reverts first. If Cards must also go, run the Cards §4.D script AFTER this one.
git revert --no-edit "$IMAGES" || { git revert --abort || true; exit 1; }
git push origin p7-v8.9            # only branch ever pushed; never main (locked 9f04550a)
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

### 6.1 `numista_mobile/test/utils/owned_storage_url_test.dart` (MF-I1, MF-I2, MF-I7')
Verifies public top-level `isOwnedStorageUrl` against real accepted bucket forms and one sanitized fixture per **real** emitted path shape from `numista_backend/_scripts/build_image_index.py` (`SCAN_TARGETS` $\rightarrow$ `coin_image_index`), `numista_backend/_scripts/build_currency_image_index.py` (`GCS_PREFIX = "reference_library/us_banknotes/"` $\rightarrow$ `currency_image_index`), and `numista_backend/_scripts/promote_user_photos.py` (`reference/{program_slug}/{year}_{program_slug}_{side}.jpg`):
```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/utils/owned_storage_url.dart';

void main() {
  group('isOwnedStorageUrl Real Allowlist & Index public_url Verification (MF-I1, MF-I7\')', () {
    test('Accepts Form A: Real Firebase Storage download URL for project bucket', () {
      const realUserUrl = 'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fanon_user_1%2Fcoins%2F123.jpg?alt=media';
      expect(isOwnedStorageUrl(realUserUrl), isTrue);
    });

    test('MF-I7\': Accepts every real emitted public_url shape from _scripts/build_image_index.py, build_currency_image_index.py, and promote_user_photos.py', () {
      // 1. _scripts/build_image_index.py:55-56 (SCAN_TARGETS Tier 1: us_mint_coin_images / Numista_Attributed_Coins (1)/ with space encoded as %20 at :302)
      const scanTargetMintUrl = 'https://storage.googleapis.com/us_mint_coin_images/Numista_Attributed_Coins%20(1)/2024_america-the-beautiful_reverse.jpg';
      // 2. _scripts/build_image_index.py:62-63 (SCAN_TARGETS Tier 2: numista-reference-library / reference_library/bulk_programs/)
      const scanTargetBulkUrl = 'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/1999_new-jersey_50-state-quarters_reverse.jpg';
      // 3. _scripts/build_image_index.py:69-70 (SCAN_TARGETS Tier 3: numista-reference-library / reference_library/wikimedia_uscoin/)
      const scanTargetWikiUrl = 'https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/1964_kennedy-half-dollar_reverse.png';
      // 4. _scripts/build_image_index.py:76-98 (SCAN_TARGETS Tier 2/5: rare_uscoin, balabaskar_coins, 2026_series, user_contributed)
      const scanTargetRareUrl = 'https://storage.googleapis.com/numista-reference-library/reference_library/rare_uscoin/1909_s_vdb_lincoln-cent_obverse.jpg';
      const scanTarget2026Url = 'https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026-CENT-P_reverse.jpg';
      const scanTargetContribUrl = 'https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/1921_morgan-dollar_obverse.jpg';
      // 5. _scripts/build_currency_image_index.py:40-41, 267 (REFERENCE_BUCKET = numista-reference-library, GCS_PREFIX = reference_library/us_banknotes/)
      const currencyBanknoteUrl = 'https://storage.googleapis.com/numista-reference-library/reference_library/us_banknotes/fr_1613_n_star_obv.jpg';
      // 6. _scripts/promote_user_photos.py:16-17, 35-37, 130 (BUCKET_NAME = numista-uploads-studio-9101802118-8c9a8, reference/{program_slug}/{year}_{program_slug}_{side}.jpg)
      const promotedUserRefUrl = 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference/morgan-dollar/1881_morgan-dollar_obverse.jpg';

      expect(isOwnedStorageUrl(scanTargetMintUrl), isTrue);
      expect(isOwnedStorageUrl(scanTargetBulkUrl), isTrue);
      expect(isOwnedStorageUrl(scanTargetWikiUrl), isTrue);
      expect(isOwnedStorageUrl(scanTargetRareUrl), isTrue);
      expect(isOwnedStorageUrl(scanTarget2026Url), isTrue);
      expect(isOwnedStorageUrl(scanTargetContribUrl), isTrue);
      expect(isOwnedStorageUrl(currencyBanknoteUrl), isTrue);
      expect(isOwnedStorageUrl(promotedUserRefUrl), isTrue);
      // v2.1 MF-SAG-I7: balabaskar prefix (build_image_index.py:84)
      const balabaskarUrl = 'https://storage.googleapis.com/numista-reference-library/reference_library/balabaskar_coins/fixture_coin_obverse.jpg';
      expect(isOwnedStorageUrl(balabaskarUrl), isTrue);
    });

    test('v2.1 MF-SAG-I3: rejects traversal, encoded dots, userinfo and port', () {
      expect(isOwnedStorageUrl('https://storage.googleapis.com/us_mint_coin_images/%2E%2E/other-bucket/x.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://storage.googleapis.com/us_mint_coin_images/../other-bucket/x.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://storage.googleapis.com/us_mint_coin_images/a%2f..%2fb/x.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2F..%2Fx.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://user:pw@storage.googleapis.com/us_mint_coin_images/x.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://storage.googleapis.com:8443/us_mint_coin_images/x.jpg'), isFalse);
      expect(isOwnedStorageUrl('/assets/../secret.png'), isFalse);
    });

    test('v2.2 MF-SAG-I3: raw dot segments inside an allowed root are rejected pre-normalization', () {
      expect(isOwnedStorageUrl('https://storage.googleapis.com/us_mint_coin_images/a/../x.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://storage.googleapis.com/us_mint_coin_images/./x.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://storage.googleapis.com/us_mint_coin_images/../numista-reference-library/x.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://storage.googleapis.com/us_mint_coin_images/a%20b/x.jpg'), isTrue); // %20 still allowed
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

    // v2.1 MF-SAG-I1: Case 3 split. (3a) unowned URL with NO user-upload signal is treated as absent:
    // never rendered, precedence continues to reference (matches shipped :6369-6406 + hasUserUploadedPhotos :27).
    testWidgets('Case 3a: unowned non-user URL is never rendered; reference fetch proceeds', (tester) async {
      int fetchCount = 0;
      final data = {'image_url_obverse': 'https://evil.firebasestorage.app/malicious.jpg', 'Year': '1964', 'denomination': 'Half Dollar'};
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: CollectionCardImage(data: data,
          imageFetcher: ({required year, mint, denomination, series, subject}) async { fetchCount++; return const CoinImageResult(); }))));
      await tester.pump();
      expect(fetchCount, 1);
      expect(find.byWidgetPredicate((w) => w is Image && w.image is NetworkImage &&
          (w.image as NetworkImage).url.contains('evil')), findsNothing);
    });

    // (3b) confirmed user upload (isUserUrl matches '/users/') whose selected URL is unowned -> placeholder, no fetch, no canonical.
    testWidgets('Case 3b: confirmed user upload with unowned selected URL fails closed', (tester) async {
      int fetchCount = 0;
      final data = {'image_url_obverse': 'https://evil.example/users/x.jpg', 'Year': '1964', 'denomination': 'Half Dollar'};
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: CollectionCardImage(data: data,
          imageFetcher: ({required year, mint, denomination, series, subject}) async { fetchCount++; return const CoinImageResult(); }))));
      expect(fetchCount, 0);
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
                    reverseUrl: 'https://storage.googleapis.com/us_mint_coin_images/Numista_Attributed_Coins%20(1)/1964_kennedy_rev.jpg',
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
                  reverseUrl: 'https://storage.googleapis.com/us_mint_coin_images/Numista_Attributed_Coins%20(1)/1964_kennedy_rev.jpg',
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
                  obverseUrl: 'https://storage.googleapis.com/us_mint_coin_images/Numista_Attributed_Coins%20(1)/generic_obv.jpg',
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

    // v2.1 MF-SAG-I1
    testWidgets('Case 8: 2026 cent with canonical match + unowned URL in photo field still shows canonical', (tester) async {
      final data = {'Year': '2026', 'denomination': 'Cent', 'mint_mark': 'P', 'title': '2026 Coin',
                    'image_url_obverse': 'https://evil.example/x.jpg'};
      final canon = CanonicalMintAssetService.resolveFromMap(data)!;
      final expected = canon.reverseUrl.isNotEmpty ? canon.reverseUrl : canon.obverseUrl;
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: CollectionCardImage(data: data,
          imageFetcher: ({required year, mint, denomination, series, subject}) async => fail('no fetch')))));
      expect((tester.widget<Image>(find.byType(Image)).image as NetworkImage).url, equals(expected));
    });

    testWidgets('Case 9: owned user reverse + unowned obverse renders the reverse', (tester) async {
      const rev = 'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fanon_user_1%2Fcoins%2Frev.jpg?alt=media';
      final data = {'image_url_reverse': rev, 'image_url_obverse': 'https://evil.example/x.jpg'};
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: CollectionCardImage(data: data))));
      expect((tester.widget<Image>(find.byType(Image)).image as NetworkImage).url, equals(rev));
    });

    // v2.1 MF-SAG-I5
    testWidgets('Case 10: clearing the user photo on the same State starts a reference fetch', (tester) async {
      var fetchCount = 0;
      Future<CoinImageResult> f({required year, mint, denomination, series, subject}) async { fetchCount++; return const CoinImageResult(); }
      const key = Key('c10');
      const rev = 'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fanon_user_1%2Fcoins%2Frev.jpg?alt=media';
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: CollectionCardImage(key: key, imageFetcher: f,
          data: const {'Year': '1964', 'denomination': 'Half Dollar', 'image_url_reverse': rev}))));
      expect(fetchCount, 0);
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: CollectionCardImage(key: key, imageFetcher: f,
          data: const {'Year': '1964', 'denomination': 'Half Dollar'}))));
      await tester.pump();
      expect(fetchCount, 1);
    });
  });
}
```

---

## 7. Delivery & Sign-Off Requirements
- **Verification Command (Post-Approval Execution Only):**
  `flutter test test/utils/owned_storage_url_test.dart test/widgets/collection_card_image_test.dart`
- **Review Gate:** Requires independent score $\ge 95$ from Grok Bot CoS and Stand Alone Grok (SAG, grok-4.7) on **both** `FAILFIX_PLAN_NET-780b_CARDS_v2.0.md` and `FAILFIX_PLAN_NET-780c_IMAGES_v2.0.md` prior to Founder Eric's typed YES.
