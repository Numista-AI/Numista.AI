# PLAN_IMAGE_CONSOLIDATION_v1 (31 Oct 2026, GB CoS) - PLAN + DRY-RUN ONLY
Review Cycle: AG -> Argon -> CoS >=95 -> SAG -> Eric typed YES -> EXECUTE. Nothing deleted/moved/uploaded; no Firestore/site writes. Never touch V3Tees (gen-lang-client-0504730428).

## 1. Master locations
- Laptop: `MyVertexProject\1 NUMISTA.AI\COIN IMAGES\` (exists, convention-named). Kept copies outside it go to `COIN IMAGES\_unsorted\` pending naming.
- GCS: `gs://numista-reference-library/reference_library/master/` (new prefix in the bucket that already holds us_mint_official/2026_series; avoids cross-bucket URL churn).
- Naming: `{year}_{program}_{subject}_{side}[_{mintcode}].{ext}`, lowercase. Existing names are NOT renamed; only new master copies follow it.

## 2. Duplicate proof
- Laptop: full SHA256 (inventory_20261031.csv). 8,945 images; 1,786 hash groups with 2,579 extra copies (1.46 GB). After protecting 20 copies inside code/repo folders: **2,559 quarantine candidates, 1,457,426,527 bytes**.
- Same name, different content: 136 names (laptop_samename_diffcontent.csv) - NOT duplicates, never auto-deleted.
- GCS (done 31 Oct, read-only): 22,085 image objects (24.25 GB), 0 without md5. 2,556 identical-md5 groups, 12,610 extra copies, 16.20 GB redundant - but 11,214 of those copies sit in the user uploads bucket and are protected. After user/code/Firestore protection: **210 quarantine candidates, 0.46 GB** (us_mint_coin_images + numista-reference-library). See gcs_dedupe_summary.txt, gcs_delete_candidates_after_firestore.csv.

## 3. Protection rules (excluded from deletion)
- User upload buckets/prefixes (`*-uploads`, `numista-user-content`, `user_contributed/`) - excluded entirely.
- Any object whose file name appears in app code/backend (grep) - protected. Code grep found ~51k URL refs (mostly storage.googleapis.com, 3,207 to the uploads bucket, 77 to numista-reference-library).
- Firestore (scanned 31 Oct, read-only, 54k docs incl. all users/* subcollections): 45,039 distinct image refs in 15,681 docs. **7,422 images protected** (referenced by 5,959 user docs: users/*/coins 5,396, currency 317, review_queue 145, transferred_coins 31, receipts 41, etc.; also transfers, staging_area). Main fields: image_url_obverse/_reverse, gcs_path, gcs_url, coin_image_index obverse/reverse.public_url/gcs_path. 13 GCS candidates removed because Firestore references them. Files: protected_images.csv, firestore_image_refs.csv, firestore_image_refs_summary.txt.
- Code refs re-run 31 Oct (code_bucket_refs_20261031.csv): 25,748 bucket/path strings in 192 files (680 .py, 15 .dart, rest JSON data). By bucket: numista-uploads 18,216; reference_library/ 2,688; numista-reference-library 2,214; studio-uploads 2,190; us_mint_coin_images 415. Remap must update JSON data files and ~40 backend scripts, not just Firestore.

## 4. Quarantine and deletion
- Laptop: move candidates to `COIN IMAGES\_QUARANTINE_20261031\` preserving relative path + restore log; hard delete after 30 days only with Eric YES.
- GCS: copy kept object to master/, move duplicates to `gs://numista-reference-library/_quarantine/20261031/...`; object versioning/lifecycle delete at 30 days. Rollback = move back from quarantine.

## 5. Firestore remap process
1. Map table old_url -> master_url (from gcs_keep_copy_map.csv).
2. Read-only scan of coins/, catalog, review items, users/*/coins; dry-run diff CSV with affected doc count per collection.
3. Export Firestore (numista-firestore-exports) as backup; batched apply (<=400 writes/batch), each write logs old value.
4. Field Tester checks on p7-gate preview (cards show unique side, inspector, set panels); Eric's own collection first.
5. Old objects kept 30 days; rollback script restores old values from the log.

## 6. Intake for Catalog Research and Research Posts
- Upload only to `gs://numista-reference-library/reference_library/incoming/{bot}/`, with object metadata: source_url, license, year, side/view_type, mint_code, found_by, date.
- Auto checks: md5 dedupe against index; naming convention; resolution floor; license present; year/side visual check (SAG or Gemini); Morgan/Peace verification (Morgan obverse vs Peace confusion); unique side for cards.
- Pass -> promote to master/ + append row to image_index.csv; fail -> `incoming/_rejected/` with reason. No bot writes to master/ directly.

## 7. Extra views (Eric YES 6:06 PM, plan only)
- New index column `view_type`: obverse | reverse | privy_detail | ogp (box/case/COA).
- Naming: side=`privy_detail` or `ogp`, e.g. `2026_american_silver_eagle_proof_privy_detail_26ea.jpg`.
- Tag known privy close-ups: 26ea_d, 26xe_e, 26xl___d, 26gc_h. Tag box/case/COA shots (incl. 26XM/26XH composites, 26gc_a) as ogp.
- Cards keep showing only the unique side.
- Code finding: `coin_model.dart` has fixed `imageUrlObverse`/`imageUrlReverse` strings (Firestore `image_url_obverse/_reverse`) plus a list `ownerPhotos` (owner photos only). No general views list. Coin detail uses a TabBar (Details, Financials, ...).
- Effort estimate: add optional `extra_images: [{url, view_type}]` field (model + fromMap/toMap, backward compatible), populate from index, add a Privy and an OGP tab or a swipe gallery in the Coin Inspector hiding empty tabs - about 1-2 dev days + tests + FT check. Separate NET ticket after the Mint fail-fix.

## 7b. Real-number impact (31 Oct)
- Space saved by GCS dedupe is small (0.46 GB); the value is one home, not storage cost. The 16 GB of user-upload duplicates stay until the remap proves each is unreferenced (separate later pass).
- Remap scope: ~6,000 user docs + ~8,600 catalog/index docs + JSON/code files.

## Interim rules (until Eric YES; mirrors INTERIM_IMAGE_STORAGE_RULES_20261031-1848)
1. GCS and Firestore READ ONLY: no uploads, renames, moves, deletes or Firestore writes.
2. Stage new images at /workspace/image-intake/<bot>/<subject>/ (laptop COIN IMAGES\_INTAKE\<bot>\), never in live buckets.
3. Every batch has MANIFEST.csv (proposed_name, side, unique_side, category, source_page_url, image_url, license, credit, accession_or_sku, resolution, sha256, added_by, date, status=PROPOSAL); send path to GB CoS.
4. Source order: Mint/BEP/Treasury > museums (NNC, ANS) > public domain > verified user uploads; search numista-reference-library and Eric's photos first; licensed use only.
5. Scope: coins and bank notes first, medals lower priority.
6. Exemption: items in an Eric-YES'd plan (e.g. NET-647 R2.6's 7 uploads to 2026_products) proceed no-clobber, no deletes.
7. Nothing in V3Tees; no secrets in files or chat.

## 8. Lessons
- Index first: no bot proposes a stand-in image until index/master is searched.
- Hash, never name, decides duplicates.
- Protection lists (users, code, Firestore) come before any delete list.
- Inventories must exclude repo folders or flag them protected.

## 7a. Edge view (Eric 31 Oct 2026, 6:09 PM, via Argon)
- Add view_type 'edge' (side=edge in filenames). Required for coins whose date/mint mark is lettered on the edge: Presidential $1 (2007+), Sacagawea/Native American $1 (2009+), and any others found.
- Search order for edge images: master index -> Cloud buckets -> Eric's laptop folders -> museum/public domain -> verified uploads.
- Coin Inspector extra-views ticket adds an Edge tab alongside Privy and OGP. Cards still show the unique side (e.g. the president).
- Index flags coins needing an edge image but lacking one.


## 7c. User-uploaded photos (phone, webcam, microscope) - added by GB CoS 31 Oct 7:25 PM
- Uploads stay in a per-user area and are never merged into the master library by default.
- Tag each upload with device (phone, webcam or microscope) and view (obverse, reverse, edge, privy, ogp or detail).
- Microscope shots are detail or privy views only, never the primary card image.
- Run minimum resolution and focus checks, and strip EXIF GPS on ingest.
- Promotion to the master library needs both an AI and a human check, and the image must beat the current one. Collectors can toggle between their own photo and the stock photo.
