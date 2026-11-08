# REVISE NET-810 v1.6 → v1.7 (SAG 64 FAIL) — verified fix list
Verifier: GB CoS executor, 8 Nov 2026 ~11:52 AM ET. Box files /workspace/sag-r2/ + read-only `git` on EDS_Laptop (no checkout/write).
Tally: REAL 7 · FALSE 1 · UNCLEAR 1

## Laptop facts checked (read-only)
- `origin/dev` is now `cc815522…` (NOT `bde8b402` as the plan says). `b0b05808` is an ancestor of origin/dev; pin `4d17ca5e` is NOT.
- `numista_mobile/assets/catalog/catalog_public_v1.json`: present on origin/dev, ABSENT at `4d17ca5e`. Catalog dir + catalog screens identical between `b0b05808` and `cc815522`. 3,202 rows.
- Row `NAC1.CN.US.1D.AMERICANSI.2024.W.SILVEREAGL.A` has `status_badge: "Needs source"` (b0b05808). Columns include `status_badge`, `is_placeholder`, `mint_facility`.

## Must-fixes (priority order)
1. **[REAL MF-1] One execution tree.** Name the code pin `4d17ca5e` and catalog source `b0b05808` (= current origin/dev `cc815522` for catalog paths) separately. Fix the stale `bde8b402` claim. Add preflight: catalog asset path exists, cited line numbers match the tree. Do not add a duplicate `assets/catalog/` pubspec line. Drop the catalog stats you didn't re-check (5,895,259 bytes, badge counts).
2. **[REAL MF-2] One join spec.** Plan line 388 (§5.1) still does `_byNacCode!.containsKey(ref)` with no placeholder gate. Delete §5.1 or replace it with the §7.1 algorithm (line 725). Mark the old FakeFirebaseFirestore matrix (lines 35, 68, 1412) as historical. Replace `.catchError((_) {})` at line 797 with a catch for the two tolerated asset errors only, and surface everything else.
3. **[REAL MF-3] Provenance.** Commit `mint_product_fields_v1.json` as `{}` until `data/usmint/usmint_product_schedule_2024.json` is acquired. Add `source_url` and `retrieved_at` to `MintProductMetadata`. Exporter is local-file-in/local-file-out only and omits any field without provenance. Hardcoded `'Available from U.S. Mint (as of Nov 2026)'` (line 601) must come from `asOfDate`, or be omitted.
4. **[REAL MF-4] Screen imports.** The `coin_detail_screen.dart` hunk needs `import '../services/mint_product_lookup_service.dart';` and `import '../models/mint_product_metadata.dart';`. Those imports exist in the service file (lines 652–653), but they aren't in the screen diff.
5. **[REAL MF-5a] US-only gate.** Lookup must fail closed unless the coin's country is US (pin default `'USA'`, coin_model:109; detail screen also treats `'United States'`) AND the row's `type == 'coin'` / NAC has `.US.`. No country check exists in the plan.
6. **[REAL MF-6] Rollback.** Lines 1398–1399 use `tac` + process substitution and then do an unconditional `git push origin dev`. Fix: local `git revert` only, with the push behind a separate Founder YES. Abort on empty list, dirty tree, wrong branch/upstream, or HEAD == `9f04550a`. Use PowerShell-native order (or `git rev-list`). **git revert only. No `reset --hard`.**
7. **[REAL MF-7b] Placeholder test.** "Quarantined placeholder" (line 1093) omits `series`, so it returns null for the wrong reason. Give it full year/facility/denomination/series keys so `is_placeholder: true` is the only cause.

## Decision needed (UNCLEAR)
- **[UNCLEAR MF-5b] Blank mint mark → Philadelphia (line 758).** No mint mark does conventionally mean Philadelphia for most US coins. But the pin `CoinModel.mintMark` defaults to `''` (coin_model:84), so blank also means "not entered". Recommended v1.7 rule: blank maps to Philadelphia only when the composite match is unique AND the catalog row's `mint_mark_on_coin` is null/blank. Otherwise return null. Flag this for CoS/Eric.

## Rejected (FALSE)
- **[FALSE MF-7a]** "`status_badge` unverified": it was verified on b0b05808 as "Needs source" for the cited row. Cite this evidence in the plan and keep the assertion.

## Polish (carry if cheap)
AC-4 name `facilityToMintMark`; unused `release_time_et`; duplicate status sentence; stale "carried forward unchanged" text; AC-7 line shifts.
