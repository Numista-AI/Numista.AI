# SAG PACKET - PLAN_IMAGE_CONSOLIDATION_v1 (NET-676) - 20261031-1945 ET
Status: Argon 94 CONDITIONAL GO; GB CoS 84 REVISE (v1.1 fix-only pending). Read-only review; nothing executed.

## Upload these files
1. PLAN_IMAGE_CONSOLIDATION_v1.md
2. GEMINI38_REVIEW_IMAGE_CONSOLIDATION_v1.md
3. RADIO_OVER_NET-677_ARGON-to-ALL_IMAGE-CONSOLIDATION-v1-REVIEW_20261031.md
4. COS_SCORE_IMAGE_CONSOLIDATION_v1_84_REVISE_20261031-1945.md
5. gcs_dedupe_summary.txt
6. firestore_image_refs_summary.txt
7. gcs_delete_candidates_after_firestore.csv (210 rows)
8. gcs_delete_candidates_firestore_hits.csv
9. gcs_dedupe.ps1 and fs_scan.py
(Large CSVs - gcs_keep_copy_map, protected_images, code_bucket_refs - sample only if size limit.)
Folder: C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\COIN IMAGES\_INDEX\consolidation_20261031\

## Questions for SAG
1. Can any of the 210 GCS candidates still be referenced by a path the scans miss (public https URL in posts/site, signed URL, relative filename in JSON)? Is leaf-name code protection safe given the 13 leaf collisions?
2. Is the Firestore remap rollback (export + per-write old-value log + rollback script) sufficient, and what is the equivalent safe process for the ~192 code/JSON files?
3. Which Firestore collections should be OUT of remap scope (greysheet_cache 15,895 third-party URLs, brain_*, scraper_reports) and why?
4. Is 'move to _quarantine' safe for GCS, or should it be copy-to-master + keep original readable for 30 days?
5. Is the unified grammar {year}_{program}_{subject}_{side}[_{mintcode}][_{variant}] and enum obverse|reverse|edge|privy_detail|ogp|detail complete (bank notes, medals, sets)?
6. Is the proposed phase order (re-scan -> laptop -> GCS -> Firestore -> code -> extra-views ticket) correct, each with its own Eric YES?
