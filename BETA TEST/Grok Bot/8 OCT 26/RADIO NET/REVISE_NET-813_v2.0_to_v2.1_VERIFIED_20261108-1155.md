# REVISE NET-813 v2.0 → v2.1 (SAG 54 FAIL) — verified fix list
Verifier: GB CoS executor, 8 Nov 2026 ~11:52 AM ET. Tally: REAL 10 · FALSE 2 · UNCLEAR 0

## Laptop facts checked (read-only)
- origin/dev = `cc815522`. Catalog JSON + catalog screens identical to `b0b05808`. Absent at pin `4d17ca5e`. The plan header cites `6af2afb1` and G1/D1 cites `bde8b402`. Both are stale.
- `primary_image` is a Map with keys `url, full_url, side, unique_side, license, credit, source_url, resolution`. The first imaged row is a Met URL (`images.metmuseum.org`, license "CC0 (Met Open Access)").
- Rows `NAC1.MD.US.PRV.LIBAM.1782.XX.BASE.S` and `NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3` both exist.

## Must-fixes (priority order)
1. **[REAL MF-1] Harness API.** `UnifiedCoinDetailDeps` (line 1230) has only store/clock/lawsFetcher. `harness.loadedImageUrls` (1404), `harness.lastLaunchedUrl` (1481–1482) and `harness.recordLaunchUrl` (949) are undeclared. Declare an image-loader hook and a URL-launcher hook in deps (injected, no-op in production), or drop those assertions.
2. **[REAL MF-2] Call-site snippets.** `show()` has `required … legacyOpen` (line 297), but none of the 5 snippets passes it. Snippets call `_resolveParentIndexForVirtualChild` (539, 584), and site 5 uses `docs.indexWhere` (676), while G4 and Tests 2–3 cover top-level `resolveParentIndex`. Correction to SAG: the helper IS defined top-level at line 512, so this is a contradiction, not a missing symbol. Make every snippet paste-ready: `resolveParentIndex(...)` plus `legacyOpen: () => <pin call verbatim>`. Delete the duplicate helper.
3. **[REAL MF-3] Legislation path.** Pin `CoinModel` has no `legislationKey`, and the plan's loader matches `legislation_key` only (777, 957). Pin `_matchLawKey()` (coin_detail_screen.dart:3030–3068) isn't ported (0 hits in the plan). `_congressGovFetch` (978) is never defined. Fix: port `_matchLawKey` verbatim, and either use the pin's source (Firestore `metadata/coin_legislation` read + `_kDefaultLaws`) or drop the network fetch. Don't invent a Congress.gov client.
4. **[REAL MF-4a] Catalog SHA.** Bind catalog evidence to `b0b05808` (= origin/dev `cc815522` for those paths). Remove `6af2afb1` and `bde8b402`.
5. **[REAL MF-4c] Assets.** Register `assets/catalog/` in pubspec (pin assets lines 92–96 don't include it; `assets/` isn't recursive), or drop Test 15's rootBundle load.
6. **[REAL MF-4d] Image guard vs catalog host.** `isOwnedStorageUrl` (§7.4, 1091) allows only Firebase/GCS prefixes, while catalog heroes are Met URLs. Add a separate catalog-image rule: HTTPS + non-empty `license` + `source_url` from the row, with a host allowlist named from real data. Owner photos keep `isOwnedStorageUrl`.
7. **[REAL MF-5] Widget contract.** Specify `build` with keys `udv_header_title`, `udv_header_surface` and `hero_coin_image`, plus the tab, chevron (`Icons.arrow_forward_ios`), "Show values" and "Legislation" widgets. `Key('ebay_search_button')` findsNothing (1639) can't fail unless that key exists on the real eBay control. Pick ONE currency format. Test 5 expects `$50.00` (1439/1444), Test 12 expects `45.00` (1610/1613), and pin financials (~1662–1679) use both.
8. **[REAL MF-6] Rollback.** Line 1142 `firebase hosting:clone … numista-vault:live` is a production deploy. Replace it with deleting preview channel `pr-net813` only, plus `git revert` on the branch. No live hosting action without a separate Founder YES. **git revert only. No `reset --hard`.** Drop `tac`.
9. **[REAL MF-7a] Guest CPG.** `fromCoinModel` sets `cpgRetail: null` (807), but pin `CoinModel.cpgRetail` is a double defaulting to 0.0. Map it, treating 0.0 as unavailable, or change §5.
10. **[REAL MF-7b] Kill-switch.** Ship `assets/config/features.json` = `{"unified_details_view_v1": false}` and say so explicitly. Note that flipping it needs a restart.

## Rejected (FALSE)
- **[FALSE MF-4b]** "Catalog reads `source`, not `license`/`source_url`, so every hero becomes a placeholder": the real JSON has `license` and `source_url` and has no `source` key. Keep the plan's fields and cite this evidence.
- **[FALSE MF-4, row claims]** LIBAM 1782 and 1921-P Morgan rows exist on b0b05808. Cite them. The 248-row Met count is still not verified, so drop it or re-count it.

## Polish
"Founder Founder"; DTG mismatch; Test 11 comment `firestoreService`; `editorial_verified` isn't verbatim `_kDefaultLaws`; show the `dart:convert` import; Congress URL userinfo check.
