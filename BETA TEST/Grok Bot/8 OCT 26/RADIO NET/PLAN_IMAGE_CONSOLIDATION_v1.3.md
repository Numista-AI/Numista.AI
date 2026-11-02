# PLAN_IMAGE_CONSOLIDATION_v1.3 (NET-676 / NET-727) - GB CoS authored - 1 Nov 2026, ~9:50 PM ET

v1.3 = FIX-ONLY round closing the 3 must-fixes in SAG_REVIEW_NET-676-v1.2_76_REVISE_20261101.md. Docs only; nothing run. A PASS still needs Eric's typed YES.
Status: PLAN + DRY-RUN ONLY. **v1.2 = FIX-ONLY round closing every must-fix in SAG_REVIEW_NET-676-v1.1_76_REVISE_20261101.md.** Everything not marked [v1.2] is v1.1 text unchanged.
Review cycle: SAG -> Eric typed YES (one per phase) -> EXECUTE. A SAG PASS is not approval.
Grounding: every code citation is from `git show 32d4b42e:<file>` (origin/dev tip, 1 Nov). Locks: main 9f04550a, dev 32d4b42e, Stripe OFF. No commits, deploys, GCS writes or Firestore writes were made for this plan. Never touch V3Tees (gen-lang-client-0504730428).
Tag legend: [v1] carried from v1; [FIX ...] v1.1 closure; [v1.2 Mn] closes SAG v1.1 must-fix n; [PROPOSED] needs Eric's YES.

## v1.3 closure table (SAG v1.2 must-fixes)
| # | SAG v1.2 must-fix | v1.3 fix | Where |
|---|---|---|---|
| S1 | G-718 pass criteria too loose | G-718 now names its pass criteria: NET-718 **R5** SEC-1 + SEC-2 + SEC-15 live, with staging tests green: (a) the person's name (anywhere on the page) and ship-to / bill-to / deliver-to address are found and burned on every receipt, invoice, packing slip and appraisal fixture, verified by independent re-OCR + libpostal of the stored object; (b) a document of an address-bearing type with no address found is **rejected and nothing is stored** (no object, no Firestore doc, no Document AI call); (c) the no-disk-write test passes; (d) soft delete is off on the user-content buckets. Tests: NET-718 R5 SEC-1 Test and SEC-2 Test (30-fixture set). | Sec 8 |
| S2 | P3 apply could write a user field | **P3 abort rule:** the apply script checks every row before any write and aborts the whole batch (writes nothing) if the old or new value matches `(^|/)users(/|%2F)`, or the Firestore doc path or field is under `receipts`, `invoices`, `appraisals`, `binder_scans`, `estate_reports`, or is an owner-photo / user-upload field (any field the Sec 5.2 scope table marks as user content; exact field names are re-listed from code at P0, not assumed here). | Sec 8 |
| S3 | Side guard not fail-closed | Side comes only from the clean-map `side` column (set at P0 from image_index.csv / verified folder rules), never from a filename guess. A row is **dropped (not written) and listed** if `side` is missing, empty, ambiguous (more than one value), or not one of `obverse, reverse, edge, privy_detail, ogp, detail`; if more than 0 rows are dropped, P3 apply stops for review. | Sec 8 |
| S4 | (NET-718 R5 impact) | NET-718 R5 turns soft delete **off** on the user-content buckets. This plan deletes no user-content object, so no change to P6 (reference buckets keep their 7-day soft delete as last resort). | Sec 8 |

## v1.2 closure table (SAG v1.1 must-fixes)
| # | SAG must-fix | v1.2 fix | Where |
|---|---|---|---|
| M1 | Receipt redaction missing / assumed | No redaction exists at 32d4b42e (verified: no image/document redaction code in numista_backend; Document AI at main.py:5008-5016 receives raw bytes). This plan **moves, copies or remaps no receipt, invoice, appraisal or binder-scan object** and **adds no receipt path**. New hard gate G-718: no phase that writes user-content objects (P2 for any `users/` key, P5) may start until NET-718 R4 SEC-1/SEC-2 (in-memory redaction, raw never stored, reject if not confident) is live and its tests pass on staging. | Sec 5.2, Sec 8 |
| M2 | Owner photos keep EXIF GPS; deferred without a gate | Gate G-718 also requires NET-718 R4 SEC-1 strip-before-write for **all** image formats (today only HEIC strips GPS, main.py:4269-4272). P5 (new owner-photo keys, promotion) is blocked by G-718. No phase of this plan copies an owner photo. Promotion (Sec 7d) re-encodes from pixels. | Sec 7c, Sec 8 |
| M3 | 2,184 vs 558 inconsistent | One P1 count: **1,626 rows** = 2,559 total − 375 (BETA TEST / CoS-to-AG) − 558 (outside `COIN IMAGES\`). Exact filter below in Sec 3 item 2. Byte total for the 1,626 is **not yet recounted** (the 1,367,270,043 figure is for the 2,184 set); P0 re-computes and reports it. | Sec 2, 3, 8 |
| M4 | P6 can delete live objects; soft delete not a safety net | P6 now re-runs the full P0 ref match (Firestore + code/JSON + relative-path + image_index + external URL) **immediately before** delete; any hit keeps that object. Delete only objects with zero hits on that fresh scan. Soft delete is listed as last resort only, not a gate. | Sec 4.2, Sec 8 |
| M5 | `^users/` regex misses full URLs | Regex is matched against the **full ref string** as stored (e.g. `gs://bucket/users/...`, `https://storage.googleapis.com/bucket/users/...`, `https://firebasestorage.googleapis.com/v0/b/<bucket>/o/users%2F...`, or bare `users/...`). Pattern: `(^\|/)users(/\|%2F)` case-insensitive. P0 must re-prove the 210 GCS delete candidates have zero hits under the new pattern; until then the 210 count is **provisional**. | Sec 3, Sec 8 |
| M6 | P3 stop ambiguous | P3 stops only on a **side mismatch in the apply diff**: any row where the new value's `side` (from the clean map) differs from the field being written (`obverse_image_url` vs `reverse_image_url`, and the same for edge/privy_detail/ogp keys). The 110 excluded side-guard groups are already out of the map and do not trigger a stop. | Sec 8 |

## 0. What changed from v1 (closure table)
| CoS item | Closed in | Summary |
|---|---|---|
| MF-1 LOCK-1 keep_copy_map | Sec 5.1 | 290 user rows stripped (recount; Argon said 287). 5 exact master_path collisions (recount; Argon said 10/13 by leaf name) get md5-suffixed names. Obverse/reverse same-md5 hard guard: 110 groups (recount). |
| MF-2 LOCK-2 filters | Sec 3, 4 | Regex extended. Laptop list 2,559 -> 2,184 (375 BETA TEST / CoS-to-AG rows removed), 1,367,270,043 bytes. Recounted 1 Nov. |
| MF-3 LOCK-3 grammar/enum | Sec 1, 6, 7 | One grammar, one 6-value enum. ownerPhotos compat covers both schemas actually present in code (Sec 7c). |
| CoS-4 code/JSON remap | Sec 5.3 | Branch off p7-v8.9, scripted from cleaned map, per-file diff CSV, tests green, git revert rollback. |
| CoS-5 scope table | Sec 5.2 | Every Firestore collection with image refs marked IN or OUT. Count typo fixed: 192 files = 153 .py + 30 .json + 9 .dart. |
| CoS-6 phase table | Sec 8 | P0-P5, each with its own YES, stop condition and rollback. |
| CoS-7 external URLs + versioning | Sec 4.2 | Versioning checked read-only 1 Nov: **NOT enabled** on any of the 4 image buckets; soft delete = 7 days. So GCS quarantine is copy-then-hold, never move. Public-URL check required. |
| Eric add (31 Oct) uploads + ranking | Sec 7c, 7d | Phone/webcam/microscope intake, ranking rule and collector toggle. |

## 1. Master locations and naming [FIX MF-3]
- Laptop master: `MyVertexProject\1 NUMISTA.AI\COIN IMAGES\` [v1]. Kept copies outside it go to `COIN IMAGES\_unsorted\` pending naming.
- GCS master: `gs://numista-reference-library/reference_library/master/` (new prefix; bucket already exists and already holds reference_library/*) [v1].
- **One grammar everywhere** (this section, Sec 6 intake, the Interim Rule 3 manifest): `{year}_{program}_{subject}_{side}[_{mintcode}][_{variant}].{ext}`, lowercase, `_` separators. Existing objects are NOT renamed; only new master copies follow it.
- **One `side` / `view_type` enum everywhere:** `obverse | reverse | edge | privy_detail | ogp | detail`.
- Relation to the existing index key (quoted, `numista_mobile/lib/services/coin_image_service.dart:9`):
  `/// Key format in Firestore: {year}[_{mint}][_{subject}]_{program}_{side}`
  The index key is unchanged (it is a lookup key, not a filename). [PROPOSED] `numista_backend/_scripts/build_image_index.py` maps master filenames to that key; mapping table goes in the P2 dry-run.

## 2. Duplicate proof (read-only, 31 Oct, recounted 1 Nov)
- Real buckets in project studio-9101802118-8c9a8 (from `buckets.txt`, read-only listing). Image buckets in scope: `numista-reference-library`, `us_mint_coin_images`. Protected user buckets: `numista-uploads-studio-9101802118-8c9a8`, `studio-9101802118-8c9a8-uploads`, `studio-9101802118-8c9a8.firebasestorage.app`. Not image stores, out of scope: all `gcf-*`, `run-sources-*`, `*_cloudbuild`, `vision-*`, `numista-firestore-exports`, `numista-estate-reports`, `numista-training-docs`, `coin_paper_currency_test`, `ai-studio-bucket-*`, `*-blueprint-config`, `*_import_document`, `cloud-ai-platform-*`, `studio-9101802118-8c9a8-source-bucket`.
- GCS: 22,085 image objects (24.25 GB), 0 without md5; 2,556 md5 groups, 12,610 extra copies, 16.20 GB redundant, of which 11,214 copies sit in numista-uploads (protected). Final candidates: **210 objects, 456,547,455 bytes** (179 us_mint_coin_images, 31 numista-reference-library); 0 match the v1.1 user regex (rechecked 1 Nov).
- Laptop: SHA256 over 8,945 images. After v1.1 filters: **2,184 candidates, 1,367,270,043 bytes** (was 2,559 / 1,457,426,527).
- Same name, different content: never auto-deleted (laptop 136 names; GCS 17,968 rows).
- Hash, never name, decides a duplicate.

## 3. Protection rules [FIX MF-2]
1. User regex in `1 NUMISTA.AI/Coin Images/_INDEX/consolidation_20261031/gcs_dedupe.ps1:4` (untracked working file; not in git at 32d4b42e) changes from `'uploads|user-content|user_contributed'` to `'(?i)uploads|user-content|user_contributed|firebasestorage\.app|(^|/)users(/|%2F)'` [v1.2 M5], matched against the full stored ref string (gs://, https://storage.googleapis.com/, firebasestorage download URL, or bare path). Reason: owner photos are written under `users/` in the default bucket (quoted, `numista_mobile/lib/screens/coin_detail_screen.dart:4402-4403`):
   ```dart
         final refCompressed = FirebaseStorage.instance
             .ref('users/$userEmail/coins/${coin.id}/owner_photo_$photoId.$ext');
   ```
   and the same at `my_collection_screen.dart:5440` and `:5444`. Default bucket (quoted, `numista_mobile/lib/firebase_options.dart:55`): `    storageBucket: 'studio-9101802118-8c9a8.firebasestorage.app',`
2. [v1.2 M3] Laptop P1 filter, applied in this order to the 2,559 duplicate-candidate rows: (a) drop rows whose full path contains `\BETA TEST\` or `\Grok CoS to Antigravity\` (375 rows -> 2,184); (b) keep only rows whose full path contains `\1 NUMISTA.AI\COIN IMAGES\` (case-insensitive), moving the other 558 (e.g. repo-root screenshots like `step6_modal_after_10sec_total.png`) to `review_not_coin_images.csv`, never quarantined. **P1 set = 1,626 rows.** P0 recomputes the count and bytes; if P0's count differs, P0's number is used and reported before YES P1.
3. Code protection [v1] by leaf name, plus [FIX] full-path match. A collided leaf (Sec 5.1) protects every copy sharing that leaf until resolved by hand.
4. Firestore protection [v1]: 7,422 images referenced by 5,959 user docs; 13 GCS candidates already removed.
5. [FIX] P0 re-scan (Firestore + code + user regex) runs immediately before any move. Any new hit drops that object from the list.

## 4. Quarantine and deletion (dry-run first)
### 4.1 Laptop [v1, filtered]
Move to `COIN IMAGES\_QUARANTINE_<date>\` keeping relative path + restore log. Hard delete after 30 days only with a separate Eric YES.
### 4.2 GCS [FIX CoS-7]
Read-only check, 1 Nov 2026 (`gcloud storage buckets describe`):
| Bucket | Versioning | Soft delete | Lifecycle |
|---|---|---|---|
| numista-reference-library | not enabled | 604,800 s (7 days) | none |
| us_mint_coin_images | not enabled | 7 days | none |
| numista-uploads-studio-9101802118-8c9a8 | not enabled | 7 days | none |
| studio-9101802118-8c9a8.firebasestorage.app | not enabled | 7 days | none |

v1 assumed versioning/lifecycle protection; it does not exist. So:
- **No GCS move or delete in P2.** P2 = copy kept object to `master/`, verify md5 equal, leave the original in place and readable for 30 days.
- [PROPOSED] External URL check before any later delete: for each of the 210, build the public `https://storage.googleapis.com/<bucket>/<name>` URL and search Research Posts, Buffer/X post exports, site HTML/JSON in the repo and `code_refs.csv`; plus a 30-day access check if usage logs are available. Any hit = keep.
- [v1.2 M4] Delete of the 210 (provisional count; see M5) only in P6 with its own YES, after 30 days, and only after a **fresh full ref scan run the same day as the delete** (Firestore image fields, code/JSON strings, relative paths against us_mint_coin_images, image_index.csv, external-URL search). Any hit on any scan keeps that object. Soft delete (7 days) is a last-resort restore, not a safety gate.
- [v1.2 SF] The external-URL check uses only URLs that already exist in the searched sources; no new public URLs are minted or objects made public for the check.
- Relative paths: `numista_mobile/lib/widgets/common/ref_image_widget.dart:57` builds URLs against us_mint_coin_images (quoted): `      : 'https://storage.googleapis.com/us_mint_coin_images/$path';` so any relative path in Firestore/JSON pointing at us_mint_coin_images protects the object (179 of the 210 live in that bucket). P0 matches relative paths against it.

## 5. Remap
### 5.1 Clean map [FIX MF-1]
From `gcs_keep_copy_map.csv` (2,556 rows):
- Strip 290 rows whose kept copy matches the v1.1 user regex -> 2,266 reference rows.
- 5 exact master_path collisions (different md5, same target name) get `_<md5first8>` suffix: 2010 Yellowstone ATB reverse; 2020 American Samoa ATB reverse; 2023 Native American $1 reverse; standing_liberty_quarter_type1_1917s_obverse.png; standing_liberty_quarter_type2_1924d_obverse.png. (Argon's list of 10-13 counted leaf names across folders; the semiq-* and 1999 SBA names collide only across user rows or across sides and are covered by the strip and the guard below.)
- Side guard: 110 md5 groups contain both an `obverse` and a `reverse` filename (e.g. `1907_err_fr91_pcblic_spelling_*`). The remap script must never write a `*_reverse` URL into an `*obverse*` field or vice versa; those 110 groups are excluded from remap and listed for human review.
- Output (dry-run): `gcs_keep_copy_map_clean.csv`, `remap_excluded_side_guard.csv`.
### 5.2 Firestore scope table [FIX CoS-5]
Fields from `firestore_image_refs_summary.txt` (read-only scan, 31 Oct).
| Collection | Ref fields | Decision | Reason |
|---|---|---|---|
| users/*/coins | image_url_obverse/_reverse, gcs_path | IN | User-facing cards |
| users/*/currency | image_url_obverse/_reverse | IN | Same |
| users/*/transferred_coins, transfers | image_url_* | IN | Same |
| users/*/review_queue, staging_area | gcs_path | IN, ref images only | Skip user-upload paths |
| users/*/receipts, binder_scans, import_sessions, estate_reports | gcs_path | OUT | User uploads; never remapped |
| users/*/wishlist | image ref | IN | Ref images |
| coin_image_index | obverse/reverse.public_url, gcs_path | IN, via rebuild of `numista_backend/_scripts/build_image_index.py`, not doc edits | Index is generated (`numista_backend/_scripts/build_image_index.py:45` `FIRESTORE_COLLECTION = "coin_image_index"`) |
| currency_image_index, coin_set_index | image refs | IN | Generated indexes |
| reference_library | gcs_url, gcs_path, filename | IN | Catalog of library objects |
| definitive_reference | image_url_obverse/_reverse | IN | Catalog |
| coins_reference | none found in scan | OUT (no refs) | Re-check in P0 |
| global_metadata | items[].images[] | IN | Site data |
| mint_errors | image refs | IN | Catalog |
| greysheet_cache | data[].FeaturedImageUrl (15,895) | OUT | Third-party URLs; not our objects |
| brain_knowledge_base, brain_suggestions | file_path, filename, source_filename | OUT | AI training text; filenames are history, not live display |
| scraper_reports, weekly_audits, ai_* queues | - | OUT | Logs |
Process [v1]: dry-run diff CSV per collection -> Firestore export to `gs://numista-firestore-exports/` -> batched writes <= 400 with old-value log -> FT on p7-gate -> rollback script from log.
### 5.3 Code/JSON remap [FIX CoS-4]
Scope: `code_bucket_refs_20261031.csv` = 25,748 strings in **192 files: 153 .py, 30 .json, 9 .dart** (v1 typo corrected).
1. Branch `img-remap-<date>` off p7-v8.9 (never main or dev).
2. Script reads only `gcs_keep_copy_map_clean.csv`; exact-string replace with URL/token boundaries (old value must be followed by a quote, whitespace, `?`, `#`, `)` or end of string), so a prefix of a longer URL is never changed; `code_remap_diff.csv` flags any partial hit for hand review.
3. Writes `code_remap_diff.csv` (file, line, old, new) for review before commit.
4. JSON data files copied to `_backup_<date>/` before change.
5. Gates: `flutter analyze`, `flutter test`, `pytest` green; FT on p7-gate.
6. Rollback: `git revert` of the single remap commit; restore JSON from backup.
7. `_legacy_quarantine/` and `_archive/` scripts: OUT (dead code), listed only.

## 6. Intake for Catalog Research and Research Posts [v1, enum fixed]
Upload only to `gs://numista-reference-library/reference_library/incoming/{bot}/` with metadata: source_url, license, year, view_type (Sec 1 enum), mint_code, found_by, date. Checks: md5 vs index; grammar; resolution floor; license present; year/side visual check; Morgan/Peace check; unique side for cards. Pass -> master/ + image_index.csv row; fail -> `incoming/_rejected/` with reason. No bot writes master/ directly.

## 7. Extra views [v1, enum fixed]
- view_type enum per Sec 1. Tag privy close-ups (26ea_d, 26xe_e, 26xl___d, 26gc_h) as `privy_detail`; box/case/COA (26XM/26XH composites, 26gc_a) as `ogp`.
- 7a Edge: `edge` required for Presidential $1 (2007+), Sacagawea/Native American $1 (2009+). Index flags coins missing one. Search order: master index -> buckets -> laptop -> museum/public domain -> verified uploads.
- Code today (quoted, `numista_mobile/lib/models/coin_model.dart:209-210`):
  ```dart
        imageUrlObverse: (data['image_url_obverse'] ?? data['imageUrlObverse'] ?? data['imageUrl'] ?? '').toString(),
        imageUrlReverse: (data['image_url_reverse'] ?? data['imageUrlReverse'] ?? '').toString(),
  ```
- [PROPOSED] optional `extra_images: [{url, view_type}]`, backward compatible; Coin Inspector Privy / OGP / Edge tabs hidden when empty; cards keep the unique side. Separate NET ticket (P5), about 1-2 dev days.

## 7c. User uploads: phone, webcam, microscope [FIX MF-3 compat + Eric scope]
What exists at 32d4b42e:
- Phone/webcam capture: `numista_mobile/lib/screens/add_coins_hub.dart:5201` `              title: const Text('Take Photo (Webcam / Phone)'),` and `numista_mobile/lib/screens/coin_detail_screen.dart:4357` `              onTap: () => Navigator.pop(context, ImageSource.camera),`
- Microscope: `numista_mobile/lib/screens/base_layout.dart:368-369` routes 'Microscope Scanner' to `MicroscopeScanScreen()`; USB microscope bridge described in `numista_mobile/lib/screens/desktop_agent_download_screen.dart:295`.
- Storage rule (quoted, `numista_backend/storage.rules:9-12`):
  ```
      match /users/{email}/{allPaths=**} {
        allow read, write: if request.auth != null
                           && request.auth.token.email == email;
      }
  ```
- Finding: "compressed" and "original" get the same bytes (`numista_mobile/lib/screens/coin_detail_screen.dart:4404` and `:4409` both `putData(uploadBytes, ...)`), so nothing is compressed and EXIF (incl. GPS) is kept in both copies. Fix belongs to NET-718 R4 SEC-1 (in-memory strip of all EXIF/GPS, every format, before the only write). [v1.2 M2] This plan copies no owner photo, and P5 is blocked by gate G-718 until that ships.
- **Two ownerPhotos schemas exist** (Argon cited only one). Doc comment (quoted, `numista_mobile/lib/models/coin_model.dart:40`): `  /// Each entry: {id, url, storage_path, original_storage_path, caption, uploaded_at, uploaded_by}`; written map (quoted, `numista_mobile/lib/screens/coin_detail_screen.dart:4412-4417`): `'id'`, `'url'`, `'original_url'`, `'caption'`, `'uploaded_at'`. Parsing is schema-free (`numista_mobile/lib/models/coin_model.dart:239-241` maps each entry to `Map<String, dynamic>`), so any new keys must be optional and readers must accept both shapes. No migration of existing entries.
Rules [v1 7c, kept]: per-user area, never merged into master by default; tag device (`phone | webcam | microscope`) and view_type (Sec 1 enum); microscope = `detail` or `privy_detail` only, never the primary card image; resolution + focus checks; EXIF GPS stripped in memory before write (NET-718 R4 SEC-1; gate G-718).
[PROPOSED] new optional keys on each owner_photos entry: `device`, `view_type`, `qc: {resolution, focus_score}`, `promotion_status: none|nominated|approved|rejected`.

## 7d. Image ranking and collector toggle [PROPOSED]
Today's tiers (quoted, `numista_backend/_scripts/build_image_index.py:52-60`): tier 1 = `"us_mint_coin_images"`, `"US Mint"`; tier 2 = `reference_library/bulk_programs/`; tier 3 = `wikimedia_uscoin/` "Wikimedia Commons / Public Domain".
Stock ranking (default card image):
1. Museum / official (US Mint, BEP, Treasury, NNC/Smithsonian, ANS) - tier 1, museum sources added at tier 1.
2. Public domain (Wikimedia Commons PD, today tier 3). [PROPOSED] Library items in `bulk_programs/` and `rare_uscoin/` (today tier 2) are re-tiered by their recorded source: official/museum -> rank 1, public domain -> rank 2, unknown licence -> below rank 2 until a licence is recorded.
3. Verified user upload - only if promoted: AI QC pass + human check + measurably better (higher resolution, in focus, correct side, correct year/mint) than the current stock image for that key. Promoted copies are re-encoded with EXIF stripped and carry no user id, email or name; credit "Collector photo" only.
Collector toggle: per coin `display_image_pref: stock | own` (default stock; the user's own photo shows only on their own views unless promoted). Stored on users/*/coins (new optional field). Shared/public views always use stock unless promoted.

## 8. Phase table with gates [FIX CoS-6]
| Phase | Action | Needs | Stop if | Rollback |
|---|---|---|---|---|
| P0 | Re-scan Firestore + code + user regex; rebuild clean map; dry-run reports only | Eric YES P0 | Any scan error; any new user hit | Nothing written |
| P1 | Laptop quarantine of 1,626 (P0 count governs), COIN IMAGES only | YES P1 | Restore log incomplete | Move back from log |
| P2 | GCS copy kept objects to master/, verify md5; originals untouched. No `users/` object is copied | YES P2 (includes filename-grammar -> index-key mapping table) | Any md5 mismatch; any source key matching the user regex | Delete the new master copies only |
| P3 | Firestore remap: dry-run diff -> YES -> export -> apply | YES P3 dry-run, YES P3 apply | [v1.3] Pre-write check over the whole batch, abort with zero writes on: (1) any old or new value matching `(^|/)users(/|%2F)`; (2) any doc path/field under receipts, invoices, appraisals, binder_scans, estate_reports or an owner-photo field (S2); (3) any row whose clean-map `side` is missing, ambiguous or outside the 6-value enum (S3, fail closed); (4) any side mismatch (new value's side != target field's side); any FT fail (FT = Flutter test suite on p7-gate) | Rollback script from old-value log; export restore |
| P4 | Code/JSON remap on branch | YES P4 | Any test red | git revert; JSON backup |
| P5 | Extra views + ranking + toggle ticket | YES P5 (separate NET) **and gate G-718 met** | G-718 not met | Feature flag off |
| P6 | Delete GCS originals (210, provisional) after 30 days | YES P6 | Any hit on the same-day fresh full ref scan (Sec 4.2) | None reliable; soft delete 7 days is last resort only |
**Gate G-718 [v1.3 S1]:** NET-718 R5 SEC-1, SEC-2 and SEC-15 live with staging tests green; pass = names (anywhere) and ship-to/bill-to addresses burned on every address-type fixture per independent re-OCR, address-type documents with no address found are rejected with nothing stored, no-disk-write test passes, soft delete off on user-content buckets. Required before P5 and before any phase that would write a user-content object. P0-P4 copy, move or delete only reference/stock image objects and laptop files (P3 may rewrite stock-image URL fields inside Firestore docs, never a user-upload field), and never touch receipts, invoices, appraisals, binder scans or owner photos.
No phase starts before NET-706 launch-critical work if Eric says so; P0 is read-only and can run anytime.

## 9. Privacy in reports [PROPOSED]
User object paths contain the account email (`users/$userEmail/...`). Every dry-run CSV replaces the email segment with `users/<redacted>/` (no hash; a short hash of an email is reversible against the user list) [v1.2 SF]. No names, emails, addresses or receipt contents in any report; receipts/binder_scans/estate paths are counted, never listed.

## Interim rules [v1, unchanged]
GCS and Firestore read only; stage at /workspace/image-intake/<bot>/ or COIN IMAGES\_INTAKE\<bot>\; MANIFEST.csv per batch; source order Mint/BEP/Treasury > museums > public domain > verified uploads; coins and notes first; Eric-YES'd plans exempt (no-clobber, no deletes); nothing in V3Tees; no secrets.

## 10. Lessons
- Index first; hash decides duplicates; protection lists before delete lists; inventories exclude repo folders. [v1]
- Verify safety nets, don't assume them: v1 relied on bucket versioning that was never turned on. [new]
- Recount reviewer numbers from the CSVs: Argon's 287 / 10-13 became 290 / 5; both counts are recorded. [new]
- Line numbers drift between branches: Argon's coin_detail 4364-4380 is 4402-4417 at 32d4b42e. Always cite the commit. [new]
- Read the model doc comment as well as the writer: ownerPhotos has two schemas. [new]
- Report files are themselves a data leak risk; hash user path segments. [new]

## v1.1 docs-only path fix (GB CoS, 2026-11-01, per Argon NET-726A)
Bare filenames replaced with full repo paths verified by `git ls-tree -r 32d4b42e`. `gcs_dedupe.ps1` is not tracked in git; its working path is given. No content or scope change.
