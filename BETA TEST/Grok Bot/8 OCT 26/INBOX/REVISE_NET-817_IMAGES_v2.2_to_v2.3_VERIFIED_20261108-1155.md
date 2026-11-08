# REVISE NET-817 Images (NET-780c) v2.2 → v2.3 (SAG 76 FAIL) — verified fix list
Verifier: GB CoS executor, 8 Nov 2026 ~11:52 AM ET. Tally: REAL 3 · FALSE 4 · UNCLEAR 0

## Must-fixes (priority order)
1. **[REAL MF-2] Restore the reference path for signal-only uploads.** Pin `hasUserUploadedPhotos` (canonical_mint_asset_service.dart:27–50) is true for `scan_source` microscope/hardware agent and for `stored_obv`/`stored_rev`. Pin `_CollectionCardImage` (my_collection_screen.dart:6369–6406) falls to `fetchReferenceImages` when no http direct URL exists. Plan `_select()` (images22 ~line 690–697) returns `placeholder('U|unowned')` for BOTH an empty selection and an unowned URL. Split these:
   - (a) non-empty selected URL that fails `isOwnedStorageUrl` → placeholder, with no canonical fallthrough (keep MF-SAG-I1);
   - (b) upload signal with no extractable http(s) side → `_Selection.reference`.
   State whether `stored_obv`/`stored_rev` are displayed or are signals only. Add widget tests: microscope + empty fields → reference fetch; owned `stored_*`; unowned reverse + owned obverse → placeholder.
2. **[REAL MF-3, partly] Preflight vs apply order.** §4.A `git diff --quiet 4d17ca5e HEAD -- numista_mobile/` (line 867) fails once Cards has landed. Change it to "mobile tree == 4d17ca5e + the reviewed Cards commit `$CARDS_SHA`" (e.g. `git diff --quiet $CARDS_SHA HEAD -- numista_mobile/` and `git merge-base --is-ancestor 4d17ca5e $CARDS_SHA`). The Images import anchor depends on the Cards import line, so state that dependency. Record `PRE_APPLY_SHA`. On a pre-commit test failure: `git restore`/`git stash` the uncommitted Images changes on p7-v8.9 (no history rewrite). After commit, `git revert`. Fix `IMAGES=<…>` the same way as Cards: `${IMAGES_SHA:?}`. Assert `origin/main` == `9f04550a`.
3. **[REAL MF-6] Preview-only deploy command.** The YES scope includes a preview deploy, but no command is given. Add exactly: cwd `numista_mobile`, `firebase hosting:channel:deploy preview-catalog --only numista-vault` (site from firebase.json:7). Explicitly forbid `firebase deploy`, `--only firestore`, rules/indexes and live hosting. Firestore writes still need a separate YES.

## Rejected (FALSE)
- **[FALSE MF-1] "`r'\'` does not compile".** In Dart, a raw string gives backslash no escape meaning, so `r'\'` is a valid 1-char string containing a backslash. Plan line 371 is fine as written. Optional: switch to `'\\'` for readability. No behavior change.
- **[FALSE MF-3 recommendation] `git reset --hard <pre-apply SHA>`.** REJECTED per standing rule: git revert only (plus `git restore` for uncommitted work).
- **[FALSE MF-4] `canonicalYear` "not on pin, won't compile".** Cards v2.2 §3.A (cards22.md:278–309) adds `static String canonicalYear(Map<String, dynamic> data)` at :77, and the Images apply order puts Cards first (images22 §4.C). It compiles in the stated order. Fix only the citation: quote that exact signature in the Images plan and make the Cards commit a preflight prerequisite (see #2).
- **[FALSE MF-5] `package:numista_ai/` uncited.** Pin `numista_mobile/pubspec.yaml:1` is `name: numista_ai`, so the package imports resolve. Add that cite to the plan.

## Polish
State cwd `numista_mobile` for `flutter test`; `rev-parse origin/main` in the script; relative `/assets/...` is a dead allow for Image.network.
