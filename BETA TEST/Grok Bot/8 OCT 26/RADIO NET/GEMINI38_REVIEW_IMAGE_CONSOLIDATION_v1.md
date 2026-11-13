# GEMINI 3.8 (ARGON) TECHNICAL REVIEW — `PLAN_IMAGE_CONSOLIDATION_v1.md` (NET-676)

- **Reviewer:** Numista.Ai Argon (Gemini 3.8 Thinking / Planning & Review Gate)
- **Date / Time:** 2026-10-31 19:36 EDT
- **Track / Baton:** `WAKE_ARGON_NET-676_IMAGE-CONSOLIDATION-v1_20261031-1925.md`
- **Artifacts Audited:**
  - Plan: [`PLAN_IMAGE_CONSOLIDATION_v1.md`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/COIN%20IMAGES/_INDEX/consolidation_20261031/PLAN_IMAGE_CONSOLIDATION_v1.md) (`lines 1–75`)
  - Evidence Folder: `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\COIN IMAGES\_INDEX\consolidation_20261031\` (`gcs_dedupe_summary.txt`, `firestore_image_refs_summary.txt`, `gcs_delete_candidates_after_firestore.csv`, `gcs_delete_candidates_firestore_hits.csv`, `gcs_keep_copy_map.csv`, `laptop_delete_candidates.csv`, `laptop_samename_diffcontent.csv`, `protected_images.csv`, `code_bucket_refs_20261031.csv`, `gcs_dedupe.ps1`, `fs_scan.py`)
- **Mode:** **DOCS-ONLY (`NO EXECUTE`)** — Zero files moved, zero GCS mutations, zero Firestore writes.
- **Verdict:** **94 / 100 — CONDITIONAL GO**
  - **Phase 1 (Read-Only Inventory & 30-Day Non-Destructive Quarantine of the 210 GCS candidates):** **SAFE TO PROCEED** once Eric gives `YES` (with 2 minor filter refinements below).
  - **Phase 2 (Section 5 Firestore/Code Remap & Section 7 Schema Rollout):** **LOCK 3 ITEMS BELOW IN `v1.1` BEFORE DRY-RUN / APPLY.**

---

## 1. Score Breakdown & Executive Summary

| Check Item (from `WAKE_ARGON_NET-676`) | Weight | Score | Status |
| :--- | :---: | :---: | :--- |
| **(1) Zero Firestore/Code-referenced files quarantined or deleted** | 25 | **24 / 25** | **PASS (with `firebasestorage.app` & `BETA TEST` filter lock)** |
| **(2) Remap scope completeness (~6k user, ~8.6k catalog, JSON, ~40 scripts)** | 20 | **17 / 20** | **CONDITIONAL (`gcs_keep_copy_map.csv` needs user-filter + 13 collision fix)** |
| **(3) Rollback architecture & 30-day quarantine safety net** | 20 | **20 / 20** | **PASS** |
| **(4) Naming convention + mint code (`{year}_{program}_{subject}_{side}[_{mintcode}]`)** | 10 | **9 / 10** | **PASS (harmonize `[_{variant}]` with Interim Rule #3)** |
| **(5) Intake (§6 / Interim rules) & User uploads (§7c)** | 15 | **14 / 15** | **PASS (align `owner_photos` bucket/keys with `coin_detail_screen.dart`)** |
| **(6) Extra views: `edge`, `privy` (`privy_detail`), `ogp` (§7 & §7a)** | 10 | **10 / 10** | **PASS (standardize 6-value `view_type` enum across §§6–7c)** |
| **TOTAL** | **100** | **94 / 100** | **CONDITIONAL GO** |

---

## 2. Detailed Audit of the 6 Required Check Items

### Check (1): No File Referenced by Firestore or Code Is Ever Quarantined or Deleted (`24 / 25`)
- **What Verified Clean:**
  - **GCS Quarantine List (`gcs_delete_candidates_after_firestore.csv`, 210 objects, `456,547,455` bytes / `0.46 GB`):**
    - We audited all 210 rows (`179` in `gs://us_mint_coin_images`, `31` in `gs://numista-reference-library`).
    - Every one of the 210 objects has a verified bit-identical `md5` match (`kept_copy`) in `gs://numista-reference-library` or `gs://us_mint_coin_images`, **0 leaf-name collisions** among the 210 `kept_copy` targets, **0 user-upload objects**, **0 code references**, and **0 Firestore references** (`8` full-path hits + `5` filename hits were stripped out via `gcs_delete_candidates_firestore_hits.csv`, reducing `223 -> 210`).
  - **Same-Name / Different-Content Protection:**
    - `laptop_samename_diffcontent.csv` (`136` filenames, `1,009` rows) and `gcs_samename_diffcontent.csv` (`17,968` rows) are properly segregated and excluded from auto-quarantine.
- **2 Refinements to Lock (Why `-1 pt`):**
  1. **Add `firebasestorage.app` and `^users/` to `$user` protection regex in `gcs_dedupe.ps1:4`:**
     - Currently `gcs_dedupe.ps1:4` defines `$user='uploads|user-content|user_contributed'`.
     - However, Flutter's `StorageService` (`numista_mobile/lib/storage_service.dart:10-11`) and `_addOwnerPhoto` (`numista_mobile/lib/screens/coin_detail_screen.dart:4364-4372`) write user coin/set photos to `studio-9101802118-8c9a8.firebasestorage.app` under `users/$userEmail/coins/${coin.id}/owner_photo_$photoId.$ext` and `owner_photo_${photoId}_original.$ext` using identical `uploadBytes` (identical MD5!).
     - Lock `$user='uploads|user-content|user_contributed|firebasestorage\.app|^users/'` so future runs of `gcs_dedupe.ps1` never flag `owner_photo_*_original.jpg` in `firebasestorage.app` as an unprotected duplicate.
  2. **Exclude `BETA TEST` & `Grok CoS to Antigravity` from `laptop_delete_candidates.csv` (`375` of `2,559` rows):**
     - Grouping `laptop_delete_candidates.csv` by top folder shows `2,184` rows are genuine duplicate coin/scrape images (`Manual downloaded Coin Images\Kaggle` `1,160`, `1 NUMISTA.AI\INFO Folder` `354`, `Manual downloaded Coin Images\US Mint` `161`, `Numista_Brain_Inbox` `203`, `scratch\mint_2026_official` `66`, etc.), while **`375` rows** are mirrored test/baton screenshots (`1 NUMISTA.AI\BETA TEST` `335`, `BETA TEST\Grok Bot` `26`, `1 NUMISTA.AI\Grok CoS to Antigravity` `14`). Exclude those 3 test/baton doc trees from the laptop coin quarantine pass so historical audit trails stay in place.

---

### Check (2): Remap Scope Completeness (~6k User Docs, ~8.6k Catalog Docs, JSON Data Files, ~40 Backend Scripts) (`17 / 20`)
- **What Verified Clean:**
  - **Firestore Scan (`fs_scan.py:1-58` & `firestore_image_refs_summary.txt:1-9`):**
    - Scanned `54,676` total documents across top-level collections and `users/*`, `estate_reports/*`, and `tickets/*` subcollections.
    - Found `45,039` distinct image references across `15,681` docs:
      - **User-facing docs (`5,959` docs referencing `7,422` distinct protected images):** `users/*/coins` (`5,396`), `users/*/currency` (`317`), `users/*/review_queue` (`145`), `users/*/receipts` (`41`), `users/*/transferred_coins` (`31`), `users/*/import_sessions` (`15`), `users/*/binder_scans` (`8`), `users/*/wishlist` (`1`), `users/*/estate_reports` (`1`), plus top-level `transfers` (`2`) and `staging_area` (`2`).
      - **Catalog / Reference / System docs (`9,722` docs):** `reference_library` (`6,019`), `definitive_reference` (`1,564`), `coin_image_index` (`1,003`), `brain_suggestions` (`415`), `greysheet_cache` (`414`), `brain_knowledge_base` (`286`), `currency_image_index` (`10`), `mint_errors` (`7`), `coin_set_index` (`3`), `global_metadata` (`1`).
  - **Code & JSON Scan (`code_bucket_refs_20261031.csv`):**
    - `25,748` bucket/path matches across `192` files (`680` in ~40 backend `.py` scripts, `15` in Flutter `.dart` files, remainder in JSON data/seed/log files).
- **MUST-FIX in Section 5 Step 1 Before Any Remap Dry-Run (`-3 pts`):**
  - Section 5 line 26 states: *"1. Build `old_url -> master_url` from `gcs_keep_copy_map.csv`."*
  - Auditing `gcs_keep_copy_map.csv` (`2,556` rows) against `gcs_dedupe.ps1:10-11` uncovered **three issues** that must be fixed before building the remap table:
    1. **`287` User-Upload Rows Inside `gcs_keep_copy_map.csv`:** In `gcs_dedupe.ps1:10`, `$keep` is appended *before* the line 11 `$user` filter (`if($x.bucket -match $user ...){$prot++;continue}`). As a result, `287` of the `2,556` rows in `gcs_keep_copy_map.csv` have `kept` in `gs://numista-uploads-studio-9101802118-8c9a8/...` (including user currency photos `users/jseaman1204@gmail.com/currency/<uuid>/obverse.jpg` mapped to `master_path = gs://numista-reference-library/reference_library/master/obverse.jpg`). **Fix:** Strip all rows matching `$user` (`uploads|user-content|user_contributed|firebasestorage\.app|^users/`) from `gcs_keep_copy_map.csv`.
    2. **`13` `master_path` Leaf Collisions Across Distinct MD5 Groups:** Because `gcs_dedupe.ps1:10` computes `master_path` as `"gs://numista-reference-library/reference_library/master/"+(Split-Path $k.name -Leaf).ToLower()`, **13 `master_path` targets** (`10` reference coin filenames + `3` generic user filenames `obverse.jpg`, `reverse.jpg`, `front.jpg`) are claimed by **multiple different MD5 groups**! For example:
       - `gs://numista-reference-library/reference_library/master/2010-america-the-beautiful-quarters-coin-yellowstone-wyoming-uncirculated-reverse.jpg` is mapped from both `atb_quarters/...` (`md5=I8D7vwcAoyv3gT2gx76SOQ==`) and `bulk_programs/america_the_beautiful/...` (`md5=kr6M7AmodO5IX2i7twNm2w==`).
       - `gs://numista-reference-library/reference_library/master/2023-native-american-one-dollar-uncirculated-coin-reverse.jpg` is mapped from both `bulk_programs/american_women/...` (`md5=dSG3I/JPmbgYIJxrng3A+g==`) and `bulk_programs/native_american/...` (`md5=7vclo+SAlXmM16r2qVr7QQ==`).
       - **Fix:** Disambiguate colliding leaf names (or keep existing `reference_library/<program>/...` paths for distinct-MD5 files and only remap identical-MD5 duplicates to their canonical `kept` object).
    3. **Normalize Both `gs://`, `https://storage.googleapis.com/`, and Relative Bucket Paths:** Firestore holds `1,008` `gs://` refs, `32,827` `https://` refs, and `11,204` relative paths (`firestore_image_refs_summary.txt:8`; see also `RefImageWidget._buildGCSImage` at `numista_mobile/lib/widgets/common/ref_image_widget.dart:55-58` which prepends `https://storage.googleapis.com/us_mint_coin_images/`). Furthermore, in `gcs_delete_candidates_firestore_hits.csv:6`, `1907_err_fr91_pcblic_spelling_obverse.jpg` and `..._reverse.jpg` share MD5 `+GFCBxis4Qjp5nSgWZvb6A==` because an earlier upload put the same image on both sides — never remap an `_obverse` field to a `_reverse` filename even if their MD5s match!

---

### Check (3): Rollback and the 30-Day Quarantine (`20 / 20`)
- **Verified Complete:**
  - **Laptop (§4):** Moves duplicates to `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\COIN IMAGES\_QUARANTINE_20261031\` preserving relative path + restore log CSV; hard delete after 30 days requires a separate Eric `YES`.
  - **GCS (§4):** Copies kept object to `gs://numista-reference-library/reference_library/master/`, moves duplicate to `gs://numista-reference-library/_quarantine/20261031/{original_bucket}/{original_path}` with Object Versioning ON and 30-day lifecycle policy.
  - **Firestore (§5):** Full `gcloud firestore export` to `gs://numista-firestore-exports/pre_image_remap_20261031/` prior to any write, batched updates (`<= 400` writes/batch) recording `{doc_path, field_path, old_value, new_value}` for 1-command rollback, 30-day retention of old GCS URLs post-remap, and FT verification on `p7-gate` (`Eric's collection` first).

---

### Check (4): Naming Convention Plus Mint Code (`9 / 10`)
- **Verified Clean:**
  - Section 1 line 9 defines `{year}_{program}_{subject}_{side}[_{mintcode}].{ext}` (lowercase, e.g. `2026_aa_iowa_reverse_p.jpg`), and leaves existing referenced filenames untouched in place.
- **1 Minor Harmonization (`-1 pt`):**
  - Interim Rule #3 (line 56) includes `[_variant]`: `{year}_{program}_{subject}_{side}[_mintcode][_variant]` (e.g., `_proof`, `_revproof`, `_unc`, `_type1`), whereas Section 1 line 9 omits `[_{variant}]`. Update Section 1 line 9 to `{year}_{program}_{subject}_{side}[_{mintcode}][_{variant}].{ext}` so both sections match, and ensure `build_image_index.py` / `CoinImageService` (`numista_mobile/lib/services/coin_image_service.dart:9`, which keys `coin_image_index` as `{year}[_{mint}][_{subject}]_{program}_{side}`) supports the new canonical master filenames when rebuilding `coin_image_index`.

---

### Check (5): Intake (§6 / Interim Rules) and User Uploads (§7c) (`14 / 15`)
- **What Verified Clean:**
  - **Intake (§6 & Interim Rules):** Staging prefix `gs://numista-reference-library/reference_library/incoming/{bot}/`, laptop `COIN IMAGES\_INTAKE\<bot>\`, and workspace `/workspace/image-intake/<bot>/<subject>/` with required `MANIFEST.csv` (`filename,source_url,license,sha256,year,program,subject,side,mint_code,notes`) and SHA256/MD5 dedupe gate cleanly prevent future scatter across `scratch/`, `output/`, or ad-hoc buckets.
  - **User Uploads (§7c):** Strictly isolates user uploads from `reference_library/master/`, sets `image_verification_status: "unverified"`, and requires user opt-in + human/Grok approval before any promotion to `master/`.
- **1 Code-Alignment Item for Phase 2 (`-1 pt`):**
  - Section 7c line 70 states user photos are stored under `gs://numista-uploads-studio-9101802118-8c9a8/users/{uid}/coins/{coinId}/{view_type}_{timestamp}.{ext}` and line 72 states `owner_photos[]` entries have `{id, url, storage_path, view_type, caption, uploaded_at, verified_by}`.
  - In the live Flutter codebase (`numista_mobile/lib/screens/coin_detail_screen.dart:4364-4380`), `_addOwnerPhoto` currently uploads to the default Firebase Storage bucket (`studio-9101802118-8c9a8.firebasestorage.app`, per `firebase_options.dart:55` and `storage_service.dart:11`) at `users/$userEmail/coins/${coin.id}/owner_photo_$photoId.$ext` and writes `{id, url, original_url, caption, uploaded_at}` (without `storage_path`).
  - **Fix for Phase 2 (§7c):** Specify in §7c that Phase 2 will either keep `studio-9101802118-8c9a8.firebasestorage.app/users/{userEmail}/coins/{coinId}/` or migrate cleanly with backward-compatible readers for existing `{id, url, original_url, caption, uploaded_at}` entries on `CoinModel.ownerPhotos`.

---

### Check (6): Extra Views — `edge`, `privy` (`privy_detail`), `ogp` (§7 & §7a) (`10 / 10`)
- **Verified Complete:**
  - Keeps `image_url_obverse` and `image_url_reverse` untouched (`numista_mobile/lib/models/coin_model.dart:46-47, 209-210`) so zero existing collection cards, checklists, or detail screens break.
  - Adds optional `additional_images: [{view_type, url, gcs_path, caption, source, license}]` on catalog docs (`definitive_reference`, `reference_library`, `coin_image_index`) and `view_type` on user `owner_photos[]`, plus optional `edge_inscription` and `privy_mark` strings on catalog docs (§7a).
  - Directly supports 2026 Semiquincentennial "250" / Liberty Bell privy marks (`privy_detail`), incuse edge lettering (`edge`), and Mint packaging/COA (`ogp`).
  - **Editorial polish:** Standardize the `view_type` / `<side>` enum across §6 (line 33), §7 (line 37), §7a (line 63), and §7c (line 72) so every section lists the exact same 6 values: `obverse | reverse | edge | privy_detail | ogp | detail`.

---

## 3. Rule 6(a) Verbatim Code & Evidence Citations

Per `GEMINI.md` Rule 6(a), every file and line cited in this review is pasted verbatim below:

1. **`numista_mobile/lib/models/coin_model.dart:39-48`** (existing `ownerPhotos`, `imageUrlObverse`, `imageUrlReverse` fields on `CoinModel`):
```dart
  /// Owner photos attached to a set (estate/provenance).
  /// Each entry: {id, url, storage_path, original_storage_path, caption, uploaded_at, uploaded_by}
  final List<Map<String, dynamic>> ownerPhotos;
  
  // Internal tracking
  final String aiEstimatedValue;
  final String meltValue;
  final String imageUrlObverse;
  final String imageUrlReverse;
  final DateTime? timestamp;
```

2. **`numista_mobile/lib/models/coin_model.dart:61-63`** (existing `imageVerificationStatus` field on `CoinModel`):
```dart
  // Image QC / Verification status
  final String imageVerificationStatus; // 'unverified', 'grok_verified', 'human_verified', 'flagged'
  final String imageVerificationReason;
```

3. **`numista_mobile/lib/models/coin_model.dart:209-210` & `239-241`** (Firestore deserialization of `image_url_obverse`, `image_url_reverse`, and `owner_photos`):
```dart
      imageUrlObverse: (data['image_url_obverse'] ?? data['imageUrlObverse'] ?? data['imageUrl'] ?? '').toString(),
      imageUrlReverse: (data['image_url_reverse'] ?? data['imageUrlReverse'] ?? '').toString(),
```
```dart
      ownerPhotos: (data['owner_photos'] as List<dynamic>?)
          ?.map((e) => Map<String, dynamic>.from(e as Map))
          .toList() ?? [],
```

4. **`numista_mobile/lib/screens/coin_detail_screen.dart:4364-4380`** (actual `_addOwnerPhoto` upload path and Firestore map structure):
```dart
      final refCompressed = FirebaseStorage.instance
          .ref('users/$userEmail/coins/${coin.id}/owner_photo_$photoId.$ext');
      await refCompressed.putData(uploadBytes, SettableMetadata(contentType: 'image/$ext'));
      final compressedUrl = await refCompressed.getDownloadURL();

      final refOriginal = FirebaseStorage.instance
          .ref('users/$userEmail/coins/${coin.id}/owner_photo_${photoId}_original.$ext');
      await refOriginal.putData(uploadBytes, SettableMetadata(contentType: 'image/$ext'));
      final originalUrl = await refOriginal.getDownloadURL();

      final photoMap = {
        'id': photoId,
        'url': compressedUrl,
        'original_url': originalUrl,
        'caption': '',
        'uploaded_at': DateTime.now().toIso8601String(),
      };
```

5. **`numista_mobile/lib/storage_service.dart:9-11`** (Firebase Storage bucket binding):
```dart
  // Firebase Storage bucket — must match firebase_options.dart storageBucket exactly
  final FirebaseStorage _storage = FirebaseStorage.instanceFor(
      bucket: 'studio-9101802118-8c9a8.firebasestorage.app');
```

6. **`numista_mobile/lib/services/coin_image_service.dart:4-10`** (`coin_image_index` bucket sources and key grammar):
```dart
/// Looks up reference coin images from the Firestore coin_image_index collection,
/// which is built by build_image_index.py from the GCS buckets:
///   - gs://us_mint_coin_images        (Tier 1 — US Mint official images)
///   - gs://numista-reference-library  (Tier 2–5 — reference + Wikimedia)
///
/// Key format in Firestore: {year}[_{mint}][_{subject}]_{program}_{side}
/// where subject is the state/president/woman slug for series coins.
```

7. **`numista_mobile/lib/widgets/common/ref_image_widget.dart:51-60`** (relative path resolution against `gs://us_mint_coin_images`):
```dart
  Widget _buildGCSImage(String path) {
    // Assuming a standard base URL for the GCS bucket or Firebase Storage
    // In a real implementation, this would use FirebaseStorage.instance.ref(path).getDownloadURL()
    // For now, we construct a placeholder URL or use the path directly if it's a full URL
    final fullUrl = path.startsWith('http') 
      ? path 
      : 'https://storage.googleapis.com/us_mint_coin_images/$path';

    return _buildImage(fullUrl, isNetwork: true);
  }
```

8. **`1 NUMISTA.AI/COIN IMAGES/_INDEX/consolidation_20261031/gcs_dedupe.ps1:4-12`** (dedupe script showing `$user` regex and `$keep` population before `$user` filtering):
```powershell
$user='uploads|user-content|user_contributed'
$refs = Get-ChildItem C:\Users\ericd\Documents\MyVertexProject\numista_mobile\lib,C:\Users\ericd\Documents\MyVertexProject\numista_backend -Recurse -File -Include *.dart,*.py,*.json,*.csv -ea 0 | ?{$_.FullName -notmatch 'node_modules|\.venv|site-packages'} | Select-String -Pattern '[A-Za-z0-9_\-]+\.(jpe?g|png|webp)' -AllMatches | %{$_.Matches.Value} | sort -u
$rs=@{}; $refs|%{$rs[$_.ToLower()]=1}
$keep=@();$del=@();$prot=0
foreach($g in ($c|?{$_.md5}|group md5|?{$_.Count -gt 1})){
 $f=$g.Group|sort @{e={if($_.name -like 'reference_library/master/*'){0}elseif($_.bucket -eq 'numista-reference-library'){1}else{2}}},@{e={$_.name.Length}}
 $k=$f[0]; $keep+=[pscustomobject]@{md5=$g.Name;copies=$g.Count;kept="gs://$($k.bucket)/$($k.name)";master_path="gs://numista-reference-library/reference_library/master/"+(Split-Path $k.name -Leaf).ToLower()}
 foreach($x in $f[1..($f.Count-1)]){ $leaf=(Split-Path $x.name -Leaf).ToLower(); if($x.bucket -match $user -or $x.name -match $user -or $rs[$leaf]){$prot++;continue}; $del+=[pscustomobject]@{object="gs://$($x.bucket)/$($x.name)";size=$x.size;md5=$g.Name;kept_copy="gs://$($k.bucket)/$($k.name)";action='move_to_quarantine_prefix_30d'}}
}
```

9. **`1 NUMISTA.AI/COIN IMAGES/_INDEX/consolidation_20261031/fs_scan.py:15-22` & `32-39`** (read-only Firestore scanner across top collections and 2-level subcollections):
```python
USERC={"users","my_coin_collection","public_wishlists","review_queue","transfers","estate_reports","staging_area"}
def isuser(p): return p.split("/")[0] in USERC
def handle(d):
    p=d.reference.path; top=p.split("/")[0]; key=top if p.count("/")==1 else top+"/*/"+d.reference.parent.id; colcount[key]+=1
    out=[]; walk(d.to_dict() or {},"",out)
    if out: docs_with[key]+=1
    for f,v in out:
        r=refs[v.strip()]; (r["user"] if isuser(p) else r["other"]).add(p); r["fields"].add(f"{key}:{f}")
```
```python
for c in db.collections():
    scan(c); print(c.id,colcount[c.id],flush=True)
    if c.id in ("users","estate_reports","tickets"):
        for d in c.list_documents():
            for sc in d.collections():
                scan(sc)
                for d2 in sc.list_documents():
                    for sc2 in d2.collections(): scan(sc2)
```

---

## 4. Summary of 3 Lock Items for `v1.1` / Execution

1. **LOCK-1 (Section 5 Step 1 — Clean `gcs_keep_copy_map.csv` before remap):**
   - Filter out the `287` user-upload rows (`numista-uploads-studio-9101802118-8c9a8`, `firebasestorage.app`, `users/`) from `gcs_keep_copy_map.csv`.
   - Resolve the `10` reference `master_path` leaf collisions where two distinct MD5 groups share the same leaf filename across different folders (`2010-america-the-beautiful-quarters-coin-yellowstone-wyoming-uncirculated-reverse.jpg`, `2020-america-the-beautiful-quarters-coin-national-park-of-american-samoa-uncirculated-reverse.jpg`, `2023-native-american-one-dollar-uncirculated-coin-reverse.jpg`, `2022-national-purple-heart-hall-of-honor-commemorative-silver-coin-proof-colorized-obverse.jpg`, `1999-susan-b-anthony-dollar-obverse.jpg`, `1999-susan-b-anthony-dollar-reverse.jpg`, `standing_liberty_quarter_type1_1917s_obverse.png`, `standing_liberty_quarter_type1_1917s_reverse.png`, `semiq-penny-reverse-unc.jpg`, `semiq-nickel-obverse-unc-d.jpg`, `semiq-nickel-reverse-unc.jpg`).
   - Guard against remapping an `_obverse` field to a `_reverse` filename when an earlier bad upload gave both sides the same MD5 (e.g. `1907_err_fr91_pcblic_spelling_obverse.jpg` vs `_reverse.jpg`, MD5 `+GFCBxis4Qjp5nSgWZvb6A==`).
2. **LOCK-2 (Section 3 / Section 4 — Filter Refinements):**
   - Extend `$user` regex in `gcs_dedupe.ps1:4` to `'uploads|user-content|user_contributed|firebasestorage\.app|^users/'`.
   - Exclude the `375` test/baton screenshot rows under `1 NUMISTA.AI\BETA TEST`, `BETA TEST\Grok Bot`, and `1 NUMISTA.AI\Grok CoS to Antigravity` from `laptop_delete_candidates.csv` (`2,559 -> 2,184` coin image quarantine candidates).
3. **LOCK-3 (Sections 1, 6, 7, 7a, 7c — Naming & Enum Harmonization):**
   - Unify §1 line 9 naming grammar with Interim Rule #3 line 56: `{year}_{program}_{subject}_{side}[_{mintcode}][_{variant}].{ext}` (lowercase).
   - Unify the `view_type` / `<side>` enum across §§6, 7, 7a, 7c to: `obverse | reverse | edge | privy_detail | ogp | detail`.
   - Note backward compatibility in §7c for existing `CoinModel.ownerPhotos` entries (`{id, url, original_url, caption, uploaded_at}` in `studio-9101802118-8c9a8.firebasestorage.app`).
