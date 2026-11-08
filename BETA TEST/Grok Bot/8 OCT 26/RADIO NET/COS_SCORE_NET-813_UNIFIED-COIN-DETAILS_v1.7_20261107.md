# COS_SCORE — NET-813 Unified Coin Details View v1.7
- **Track:** NET-813
- **Artifact:** `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.7.md` (also `BETA TEST/.../PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.7.md`)
- **SHA256:** `51d04618f5a84615bc2a2f2db68ea201b57d3aefd6c998659c5f4c350a8f8069` (72,413 bytes) — matches baton
- **Review baton:** `BATON_NET-813_GROKCOS_REVIEW_UNIFIED-COIN-DETAILS-VIEW_v1.7_20261107-2130.md`
- **Scorer:** Grok Bot CoS (GROKCOS)
- **DTG:** 2026-11-07 ~9:52 PM ET (America/New_York)
- **Pin:** `git show 4d17ca5e` (not the dirty p7-v8.9 worktree). Public catalog cites vs `git show origin/dev`.
- **Attempt:** 4/4 LAST TRY
- **Prior:** v1.3 **76** FAIL; v1.4 **86** FAIL; v1.5 **81** FAIL; v1.6 **89** FAIL
- **Result:** **92 / 100 FAIL** (pass threshold 95)
- **Revision attempts:** **EXHAUSTED.** No v1.8 revise wake. Hold for morning / Eric. No Eric ping.

## Rubric
1. Standing locks and Eric rules — **19 / 20**
2. Branch, rollback and feature gate — **15 / 15** (`2dbb525e` now recorded in §12; v1.7 delivered on `dev` as `334b8221`)
3. Five-site resolution and navigation identity — **14 / 15** (real public open path identified; quoted line prefixes in §4.1 are off-by-two for the card and initial-NAC blocks)
4. Laws, notes and outbound-link safety — **14 / 15**
5. Guest privacy, CPG, and image precedence — **13 / 15** (same owner fixture now, but `fromCoinModel` / Test 12 invent CoinModel fields; `toSyntheticCoinModel` writes `storageLocation: 'Public Catalog'`)
6. Accessibility and keyboard — **9 / 10**
7. Offline verification (harness + tests) — **8 / 10** (Test 13 order is right but the widget never reads `harness.clock`; Test 11 still cannot fail for the claimed reason and does not compile against the harness API; Test 14 has no public `currentParentIndex` getter)

**Total: 92 / 100 FAIL**

## What closed vs CoS-89
- **MF-1 CLOSED.** §2.6 line 925 is now quoted verbatim from `git show 4d17ca5e:numista_mobile/lib/screens/coin_detail_screen.dart`: `style: const TextStyle(color: Colors.white60, fontSize: 12)),`. `:59`, `:892-893`, `:918-921` match. The v1.6 `Colors.white.withAlpha(180)` regression is gone.
- **MF-2 largely CLOSED.** The plan correctly states that origin/dev `:315` is `child: Column(` (Morgan owl header) and is not an open site. Real sites exist: card `onTap: () => _showItemDetailModal(item)` at **`:466`**, `_showItemDetailModal` definition at **`:810`**, and initial-NAC `_showItemDetailModal(match)` at **`:80`**. Replacement is correctly described as swapping the body of `_showItemDetailModal` at `:810`. Remaining: the numbered quote block in §4.1 labels `return _CatalogCard(` as `:466` (actual `:464`; onTap is `:466`) and labels `WidgetsBinding.instance.addPostFrameCallback` as `:80` (actual `:78`; the call is `:80`). `:810` is exact.
- **MF-3 design CLOSED.** Test 14 now starts on non-virtual parent `c0` (1881-S Morgan), then two successful Next steps `c0 -> set_1 -> c2` with asserted indices `0 -> 1 -> 4` across `[row0, setRow, childRow1, childRow2, regularRow]`. That is the right fixture. Remaining compile hole: the State field is `_currentParentIndex` with no public/`@visibleForTesting` getter, but the test reads `state.currentParentIndex`.
- **MF-4 structure improved, not fully closed.** Test 13 now `pumpWidget`s, `pumpAndSettle`s, taps Legislation, `pump()`s one frame, advances `harness.clock` 5s, then `pumpAndSettle`s. That is the right order (no longer advancing before mount). Remaining: the widget implementation never reads `harness.clock` (no laws-loader citation of the clock); §6.4 says a timeout shows `"Founding legislation details pending verification."` while Test 13 expects the ATB Act-of-2008 manifest title; a coin that matches the checked manifest first may never take the in-flight online path.
- **MF-5 NOT closed.** Test 11 calls `harness.firestoreService.seedDocument` and `getDocument`, but the harness interface only defines `setDoc` / `getDoc`. The test itself performs the read after mount; the widget is given `cachedCoinsDocs` and is never shown querying through `harness.firestoreService`. `writeCount == 0` still passes vacuously if production code writes through a different client.
- **MF-6 partially closed.** Owner and guest now share one fixture (good). Owner fields `purchaseCost: '45.00'`, `storageLocation: 'Safe Box 3'`, `personalNotes: 'Private note: bought at ANA convention'` plus an accepted user photo are present; guest is `PublicCoinProjection.fromCoinModel(ownerCoin, referenceImageUrl: refPhoto)`. Remaining: `CoinModel` at pin `4d17ca5e` has no `nacCode`, `composition`, `weight`, or `diameter` (`fromCoinModel` and the Test 12 constructor use those invented names; real fields are `personalRef` / `metalContent`). `toSyntheticCoinModel()` sets `storageLocation: 'Public Catalog'`, which injects a storage location into the guest/public surface. `PublicCoinProjection` still has no private-field slots, so `findsNothing` for the owner private strings cannot fail because of a missed redaction.
- **MF-7 CLOSED.** §12 records delivery commit `2dbb525e` (and notes v1.7 delivered on branch `dev`). "Delivery Commit: To be recorded" is gone.

## Remaining defects (4/4 exhausted — recorded, not a revise order)
1. **§4.1 quote labels must match `git show origin/dev`.** Actual lines: `:464` `return _CatalogCard(`, `:465` `item: item,`, `:466` `onTap: () => _showItemDetailModal(item),`; `:77` `if (match.isNotEmpty) {`, `:78` `WidgetsBinding.instance.addPostFrameCallback((_) {`, `:79` `if (mounted) {`, `:80` `_showItemDetailModal(match);`. `:810` is already correct.
2. **Test 11 must compile against the harness and exercise the widget path.** Use `setDoc`/`getDoc` (or add matching methods to the interface). The mounted widget, not the test body, must read/write through `harness.firestoreService` so `writeCount == 0` can fail.
3. **Test 12 / `fromCoinModel` must use real `CoinModel` fields** from `git show 4d17ca5e:numista_mobile/lib/models/coin_model.dart` (no `nacCode` / `composition` / `weight` / `diameter`). Do not write `storageLocation: 'Public Catalog'` onto a guest synthetic coin. Guest redaction must be able to fail if private strings leak.
4. **Test 13 widget must read `harness.clock` during an in-flight laws fetch**, and the asserted fallback text must match the specified timeout path (manifest vs `"Founding legislation details pending verification."`).
5. **Test 14 must expose a testable `currentParentIndex`** (`@visibleForTesting int? get currentParentIndex => _currentParentIndex;`) so the 0→1→4 assertions compile.

## Notes (not blocking alone)
- Site list, `_cachedCoinsDocs` wire-up, constructor `coin:`/`snapshot:`/`currentParentIndex:` mapping, and `_kDefaultLaws` remain as previously closed.
- v1.7 delivery commit on origin/dev is `334b8221`; §12 records `2dbb525e` as requested for the prior delivery.

## Boundaries
PLAN ONLY. `origin/main` locked `9f04550a`. Stripe OFF. Alerts only, never caps. No Argon. No code/deploy/Firestore/main. Pin `4d17ca5e` via `git show` / `git ls-tree`. Path: CoS 95+ → SAG 95+ → Eric typed YES. Attempt 4/4 exhausted — no further revise wake. No Eric ping.
