# GB CoS SCORE - PLAN_IMAGE_CONSOLIDATION_v1 (NET-676) - 20261031-1945 ET
Mode: READ-ONLY. Nothing quarantined, deleted, moved or remapped. Scorer: GB CoS.
Inputs: PLAN_IMAGE_CONSOLIDATION_v1.md; GEMINI38_REVIEW_IMAGE_CONSOLIDATION_v1.md + NET-677 (Argon 94 CONDITIONAL GO); gcs_dedupe_summary.txt; firestore_image_refs_summary.txt.

## Verdict: 84 / 100 - REVISE (gate 95). Fix-only v1.1; no new scope.
Argon's 94 = Phase 1 safe. CoS weights the remap/rollback and phasing more heavily, so CoS is lower.

| Area | Wt | Score | Why |
|---|---|---|---|
| No referenced file ever quarantined/deleted | 30 | 26 | Firestore + code + user-bucket protection is real (7,422 protected, 13 Firestore hits pulled, 210 final GCS candidates with 0 hits). Gaps: user regex misses firebasestorage.app and ^users/ (LOCK-2); 375 BETA TEST/baton screenshots in laptop list (LOCK-2); code protection is leaf-name match, so leaf collisions (LOCK-1) can mis-protect; no fresh re-scan right before the move. |
| Remap whole scope + rollback | 30 | 24 | Firestore path (map, dry-run diff, export, batched <=400 with old-value log, rollback script, FT on p7-gate) is good. Gaps: keep_copy_map dirty (LOCK-1); JSON/code remap (192 files, ~40 scripts) has no process or rollback; greysheet_cache FeaturedImageUrl (15,895 refs), brain_*, definitive_reference, coins_reference not explicitly in/out of scope; count typo '680 .py ... 15 .dart in 192 files'. |
| Naming + mint code, intake, user uploads | 20 | 18 | Convention, incoming/ -> master/ promotion, _rejected, manifest and 7c upload rules are solid. Grammar mismatch Sec 1 vs Interim #3, enum drift, ownerPhotos compat (LOCK-3). |
| Extra views (edge/privy/OGP) + phasing | 20 | 16 | Views + edge list + 1-2 dev-day ticket are fine. No explicit phase table with gates/YES per phase; GCS 'move to _quarantine' breaks any public https URL outside Firestore/code (e.g. Research Posts, X posts) - needs copy-then-hold or 404 check; bucket versioning/lifecycle not verified as enabled. |
| **Total** | 100 | **84** | |

## MUST-FIX for v1.1 (fix-only)
1. **LOCK-1 (Argon):** Clean gcs_keep_copy_map.csv - strip 287 user-upload rows; resolve the 10 reference (+3 user) master_path leaf collisions (e.g. folder-qualified or md5-suffixed names); hard guard: never remap an _obverse field to a _reverse file (1907_err_fr91 same-md5 case).
2. **LOCK-2 (Argon):** user regex = 'uploads|user-content|user_contributed|firebasestorage\.app|^users/'; drop 375 BETA TEST / Grok CoS to Antigravity rows from laptop list (2,559 -> 2,184). Re-publish counts.
3. **LOCK-3 (Argon):** One grammar {year}_{program}_{subject}_{side}[_{mintcode}][_{variant}].{ext} lowercase everywhere; one enum obverse|reverse|edge|privy_detail|ogp|detail in Sec 6/7/7a/7c; ownerPhotos {id,url,original_url,caption,uploaded_at} stays backward compatible.
4. **CoS-4 Code/JSON remap process:** dedicated branch off p7-v8.9 (never main/dev), scripted find/replace from the cleaned map, diff CSV per file, analyze + flutter test + pytest green, rollback = git revert; JSON data files backed up before change.
5. **CoS-5 Scope table:** list every Firestore collection/field with refs as IN (remap) or OUT (leave, reason) - incl. greysheet_cache, brain_*, definitive_reference, coins_reference, reference_library, coin_image_index; fix the '680 .py / 192 files' count.
6. **CoS-6 Phase table with gates:** P0 re-scan (Firestore+code) immediately before any move; P1 laptop quarantine; P2 GCS quarantine (copy-to-master first, verify, then hold); P3 Firestore remap dry-run -> Eric YES -> apply; P4 code/JSON remap; P5 extra-views NET ticket. Each phase: own Eric YES, stop condition, rollback.
7. **CoS-7 External URL safety:** before GCS quarantine, check the 210 objects' public URLs against Research Posts/X/site content (or keep originals readable during 30 days); verify versioning/lifecycle on numista-reference-library actually enabled (read-only gsutil check) and record it.

Execute nothing until v1.1 >= 95 (Argon + CoS), SAG pass, Eric typed YES.
