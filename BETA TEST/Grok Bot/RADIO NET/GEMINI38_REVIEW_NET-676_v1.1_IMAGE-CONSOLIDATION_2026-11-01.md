# GEMINI 3.8 TECHNICAL REVIEW — `PLAN_IMAGE_CONSOLIDATION_v1.1.md` (`NET-676` / `NET-727`)

**Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer & SAG Auditor)  
**Target Plan:** [`PLAN_IMAGE_CONSOLIDATION_v1.1.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/PLAN_IMAGE_CONSOLIDATION_v1.1.md)  
**Author Reviewed:** GB CoS (Grok CoS, per Eric's 6:25 PM ET directive)  
**Prior v1 Scores:** Grok CoS `84/100 REVISE` | Argon `94/100 CONDITIONAL GO`  
**Date / Time:** 2026-11-01 18:50 ET  
**Score:** **98 / 100 — PASS (Cleared for SAG Review)**  
**Execution Lock:** **NO EXECUTE** — Plan + Dry-Run Review Only. Zero code changes, zero deploys, zero pushes.

---

## 1. Executive Summary & Scoring Breakdown

`PLAN_IMAGE_CONSOLIDATION_v1.1.md` resolves every `MF-1` through `MF-3`, `CoS-4` through `CoS-7`, and Eric's 31 Oct scope additions (phone/webcam/microscope intake, 3-tier stock ranking, and collector `stock | own` toggle). We independently verified **both** every `32d4b42e` (`origin/dev`) code citation **and** every CSV row/byte count in `1 NUMISTA.AI\Coin Images\_INDEX\consolidation_20261031\`, confirming **100% mathematical and textual accuracy**.

| Category | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **1. CSV & Bucket Inventory Accuracy** | 30 | **30 / 30** | Independently verified: `2,556` `gcs_keep_copy_map.csv` rows $\rightarrow$ `290` user rows stripped $\rightarrow$ `2,266` reference rows; `5` exact `master_path` collisions; `2,559` $\rightarrow$ `2,184` laptop candidates (`1,367,270,043` bytes); `25,748` strings across `192` files (`153 .py + 30 .json + 9 .dart`). |
| **2. Safety Gates, Versioning & Rollback (`CoS-6`, `CoS-7`)** | 25 | **25 / 25** | Verified read-only that bucket versioning is `not enabled` (7-day soft delete only), replacing `v1`'s move with copy-then-hold in `P2` + 30-day external URL check (`P6`) + per-phase `YES` gates (`P0–P6`). |
| **3. Rule 6(a) `32d4b42e` Code Citations** | 20 | **19 / 20** | All 11 code quotes match `git show 32d4b42e:<path>` verbatim (`-1` minor note: 3 filenames in prose omit their subdirectory prefix, full paths documented in Section 2.2 below). |
| **4. User Upload, Ranking & Toggle Design (`Sec 7c, 7d`)** | 15 | **15 / 15** | Dual `ownerPhotos` schema compatibility (`coin_model.dart:40` vs `coin_detail_screen.dart:4412-4417`), 3-tier ranking, and privacy-preserving promotion (`"Collector photo"`, zero PII). |
| **5. Privacy in Reports & Scope Hygiene (`Sec 9`)** | 10 | **9 / 10** | Replaces `users/$userEmail/...` with `users/<sha256-first8>/` in all dry-run CSVs and never lists receipt/binder_scan/estate paths. |
| **TOTAL** | **100** | **98 / 100** | **PASS — Ready for SAG Review** |

---

## 2. Independent Verification of CSV Counts & `32d4b42e` Code Citations (Rule 6(a))

### 2.1 Independent Verification of `consolidation_20261031` CSV Data
We executed a read-only verification script against `1 NUMISTA.AI\Coin Images\_INDEX\consolidation_20261031\`:
1. **`gcs_keep_copy_map.csv` (`Sec 0, 5.1`):**
   - Total rows: **`2,556`** (`['md5', 'copies', 'kept', 'master_path']`).
   - Rows matching v1.1 user regex (`uploads|user-content|user_contributed|firebasestorage\.app|^users/`): **`290`** $\rightarrow$ leaves **`2,266`** reference rows.
   - Exact `master_path` collisions among the `2,266` reference rows: **`5`** (`2010-america-the-beautiful-quarters-coin-yellowstone-wyoming-uncirculated-reverse.jpg`, `2020-america-the-beautiful-quarters-coin-national-park-of-american-samoa-uncirculated-reverse.jpg`, `2023-native-american-one-dollar-uncirculated-coin-reverse.jpg`, `standing_liberty_quarter_type1_1917s_obverse.png`, `standing_liberty_quarter_type2_1924d_obverse.png`).
2. **`laptop_delete_candidates.csv` (`Sec 0, 2, 3`):**
   - Total rows: **`2,559`**.
   - After excluding `\BETA TEST\` and `\Grok CoS to Antigravity\` (`375` rows): **`2,184` candidates**, **`1,367,270,043` bytes** — matches `v1.1` to the exact byte.
3. **`code_bucket_refs_20261031.csv` (`Sec 0, 5.3`):**
   - Total rows: **`25,748`** across **`192` unique files**: **`153` `.py`**, **`30` `.json`**, **`9` `.dart`** — matches `v1.1` to the exact file count.

### 2.2 Verbatim Verification of Every `32d4b42e` Code Citation (`Rule 6(a)`)

1. **[`numista_mobile/lib/services/coin_image_service.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/coin_image_service.dart#L9) (`32d4b42e` line `9`, `Sec 1`):**
   ```dart
   9: /// Key format in Firestore: {year}[_{mint}][_{subject}]_{program}_{side}
   ```
2. **[`numista_mobile/lib/screens/coin_detail_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/coin_detail_screen.dart#L4357-L4418) (`32d4b42e` lines `4357, 4402–4418`, `Sec 3 & 7c`):**
   ```dart
   4357:               onTap: () => Navigator.pop(context, ImageSource.camera),
   ...
   4402:       final refCompressed = FirebaseStorage.instance
   4403:           .ref('users/$userEmail/coins/${coin.id}/owner_photo_$photoId.$ext');
   4404:       await refCompressed.putData(uploadBytes, SettableMetadata(contentType: 'image/$ext'));
   4405:       final compressedUrl = await refCompressed.getDownloadURL();
   4406: 
   4407:       final refOriginal = FirebaseStorage.instance
   4408:           .ref('users/$userEmail/coins/${coin.id}/owner_photo_${photoId}_original.$ext');
   4409:       await refOriginal.putData(uploadBytes, SettableMetadata(contentType: 'image/$ext'));
   4410:       final originalUrl = await refOriginal.getDownloadURL();
   4411: 
   4412:       final photoMap = {
   4413:         'id': photoId,
   4414:         'url': compressedUrl,
   4415:         'original_url': originalUrl,
   4416:         'caption': '',
   4417:         'uploaded_at': DateTime.now().toIso8601String(),
   4418:       };
   ```
3. **[`numista_mobile/lib/screens/my_collection_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L5440-L5445) (`32d4b42e` lines `5440–5445`, `Sec 3`):**
   ```dart
   5440:       final refCompressed = FirebaseStorage.instance.ref('users/$userEmail/coins/$coinId/owner_photo_$photoId.$ext');
   5441:       await refCompressed.putData(uploadBytes, SettableMetadata(contentType: 'image/$ext'));
   5442:       final compressedUrl = await refCompressed.getDownloadURL();
   5443:       
   5444:       final refOriginal = FirebaseStorage.instance.ref('users/$userEmail/coins/$coinId/owner_photo_${photoId}_original.$ext');
   5445:       await refOriginal.putData(uploadBytes, SettableMetadata(contentType: 'image/$ext'));
   ```
4. **[`numista_mobile/lib/firebase_options.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/firebase_options.dart#L55) (`32d4b42e` line `55`, `Sec 3`):**
   ```dart
   55:     storageBucket: 'studio-9101802118-8c9a8.firebasestorage.app',
   ```
5. **[`numista_mobile/lib/widgets/common/ref_image_widget.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/widgets/common/ref_image_widget.dart#L55-L57) (`32d4b42e` lines `55–57`, cited in `Sec 4.2` as `ref_image_widget.dart:57`):**
   ```dart
   55:     final fullUrl = path.startsWith('http') 
   56:       ? path 
   57:       : 'https://storage.googleapis.com/us_mint_coin_images/$path';
   ```
6. **[`numista_backend/_scripts/build_image_index.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/_scripts/build_image_index.py#L45-L64) (`32d4b42e` lines `45, 52–64`, cited in `Sec 5.2 & 7d` as `build_image_index.py:45, 52-60`):**
   ```python
   45: FIRESTORE_COLLECTION = "coin_image_index"
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
   ```
7. **[`numista_mobile/lib/models/coin_model.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/models/coin_model.dart#L40-L41) (`32d4b42e` lines `40–41, 209–210, 239–241`, `Sec 7 & 7c`):**
   ```dart
    40:   /// Each entry: {id, url, storage_path, original_storage_path, caption, uploaded_at, uploaded_by}
    41:   final List<Map<String, dynamic>> ownerPhotos;
   ...
   209:       imageUrlObverse: (data['image_url_obverse'] ?? data['imageUrlObverse'] ?? data['imageUrl'] ?? '').toString(),
   210:       imageUrlReverse: (data['image_url_reverse'] ?? data['imageUrlReverse'] ?? '').toString(),
   ...
   239:       ownerPhotos: (data['owner_photos'] as List<dynamic>?)
   240:           ?.map((e) => Map<String, dynamic>.from(e as Map))
   241:           .toList() ?? [],
   ```
8. **[`numista_mobile/lib/screens/add_coins_hub.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/add_coins_hub.dart#L5201) (`32d4b42e` line `5201`, `Sec 7c`):**
   ```dart
   5201:               title: const Text('Take Photo (Webcam / Phone)'),
   ```
9. **[`numista_mobile/lib/screens/base_layout.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/base_layout.dart#L368-L369) (`32d4b42e` lines `368–369`, `Sec 7c`):**
   ```dart
   368:       case 'Microscope Scanner':
   369:         return const MicroscopeScanScreen();
   ```
10. **[`numista_mobile/lib/screens/desktop_agent_download_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/desktop_agent_download_screen.dart#L295) (`32d4b42e` line `295`, `Sec 7c`):**
    ```dart
    295:             'The local hardware bridge between your USB microscope and numista.ai.\n'
    ```
11. **[`numista_backend/storage.rules`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/storage.rules#L9-L12) (`32d4b42e` lines `9–12`, `Sec 7c`):**
    ```javascript
     9:     match /users/{email}/{allPaths=**} {
    10:       allow read, write: if request.auth != null
    11:                          && request.auth.token.email == email;
    12:     }
    ```

---

## 3. Verdict

**98 / 100 — PASS.** Cleared for SAG Review and mirrored to `For SAG` and `1 NUMISTA.AI\Coin Images\_INDEX\consolidation_20261031\`.
