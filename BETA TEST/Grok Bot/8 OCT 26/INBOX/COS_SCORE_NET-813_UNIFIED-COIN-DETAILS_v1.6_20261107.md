# COS_SCORE — NET-813 Unified Coin Details View v1.6
- **Track:** NET-813
- **Artifact:** `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.6.md` (also `BETA TEST/.../PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.6.md`)
- **Review baton:** `BATON_NET-813_GROKCOS_REVIEW_UNIFIED-COIN-DETAILS-VIEW_v1.6_20261107-2030.md`
- **Scorer:** Grok Bot CoS (GROKCOS)
- **DTG:** 2026-11-07 ~8:55 PM ET (America/New_York)
- **Pin:** `git show 4d17ca5e` (not the dirty p7-v8.9 worktree). Public catalog cites vs `git show origin/dev`.
- **Attempt:** 3/4
- **Prior:** v1.4 **86** FAIL; v1.5 **81** FAIL
- **Result:** **89 / 100 FAIL** (pass threshold 95)

## Rubric
1. Standing locks and Eric rules — **19 / 20**
2. Branch, rollback and feature gate — **14 / 15** (`assets/config/` added next to existing pubspec assets; §12 still says "Delivery Commit: To be recorded" even though origin/dev already has `2dbb525e`)
3. Five-site resolution and navigation identity — **13 / 15**
4. Laws, notes and outbound-link safety — **14 / 15**
5. Guest privacy, CPG, and image precedence — **12 / 15**
6. Accessibility and keyboard — **9 / 10**
7. Offline verification (harness + tests) — **8 / 10**

**Total: 89 / 100 FAIL**

## What closed vs CoS-81
- **MF-1 largely CLOSED.** §2.1–§2.4 and the §1 site list now match `git show 4d17ca5e:numista_mobile/lib/screens/collection/collection_screen.dart`: Site 1 `:2736` `_showCoinInspectorDialog(effectiveId, m)`; Sites 2/3 `:2761` / `:2773` named `CoinDetailScreen.show`; Site 4 `:3042–3044` setState + inspector; Site 5 `:3117–3124` `parent_set_id` + `_showCoinInspectorDialog(parentDoc.id, parentDoc.data())`. §2.5 markdown `:2785–2806` matches including `onTapLink`. §2.7 laws `:3152–3165` match (non-const `SizedBox`).
- **MF-2 CLOSED.** Wire-up no longer invents `_allCoinsDocs` (only mentioned in the closeout as removed). Uses `_cachedCoinsDocs` `:131`; binds `docs` from `_buildDataTable` `:2557` and `_buildCardGrid` `:2982`; carries `spotPrices`, `onNavigateToAiChat`, `onDeleted`, `onEdited`. Constructor maps `coin` / `snapshot` / `currentParentIndex` onto `initial*` fields so existing `CoinDetailScreen.show(...)` named args compile.
- **MF-3 CLOSED.** §6.1 `_kDefaultLaws` matches pin `:2973–3027`, including the full 110-161 title and citations `121 Stat. 2014 (31 U.S.C. § 5112(r))` and `134 Stat. 5101 (31 U.S.C. § 5112(z))`. `editorial_verified: false` kept. "121 Stat. 2018" / "5112(x)" appear only as descriptions of the prior fail.
- **MF-5 mostly CLOSED.** Nav state lives in `_UnifiedCoinDetailScreenState` (`_currentCoin`, `_currentSnapshot`, `_currentParentIndex`). `_stepNavigation` uses `parentIndex >= 0 ? parentIndex : null` (never `targetIdx`). The list is captured for the session.
- **MF-6 mostly CLOSED.** `assets/config/` is added next to existing pubspec assets; attempt 3/4 and prior commit `00957e85` are recorded.
- **Test 5** now supplies real cached docs and asserts in-state Next plus values reveal.
- **Test 9** expected `'See Congress for details.  **Important**'` matches the §7.2 regex (images stripped, link labels kept, bold kept) and pumps a widget before reading the stylesheet.

## Must-fixes for v1.7 (attempt 4/4 — last try)
1. **Re-quote §2.6 header subtitle `:925` verbatim.** Pin is `style: const TextStyle(color: Colors.white60, fontSize: 12)`. v1.6 invented `Colors.white.withAlpha(180)` (a regression; v1.5 had `:925` right). `:59`, `:892–893`, `:918–921` already match.
2. **§4.1 public call site is not `catalog_browse_screen.dart:315`.** On `git show origin/dev:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`, line 315 is `child: Column(` under the Morgan owl header. The real open path is card `onTap: () => _showItemDetailModal(item)` at `:466`, plus `_showItemDetailModal` at `:810` (and the initial-NAC path at `:80`). Quote those sites from `git show origin/dev` and write the `UnifiedCoinDetailScreen.showPublic(...)` replacement against them. Do not present a proposed `showPublic` at `:315` as if it already exists.
3. **Test 14 must perform two consecutive Next steps that both succeed.** Today's fixture starts on the parent set; one Next already lands on `c2` (skipping virtual children), so a second Next has nowhere to go. Add a coin *before* the set (or a third coin after) so the test can Next onto the set and Next again onto the coin after the virtual-child group. Assert `_currentParentIndex` after each step.
4. **Test 13 must advance `FakeClock` during an in-flight request.** Advancing 5s *before* `pumpWidget` does not simulate a mid-request 4.0s timeout; elapsed at fetch start is already +5s and the widget never has to consult `harness.clock` while work is in flight. The widget must read `harness.clock` in the laws loader; advance after pump, while the request is outstanding, then assert the offline-manifest path.
5. **Test 11 must be able to fail.** The widget implementation has to perform Firestore reads/writes through `harness.firestoreService`. A test that never mounts a widget which uses that service can pass vacuously (`writeCount == 0` even if production code writes through a different client).
6. **Test 12 must use the same owner fixture for guest/public.** Build one owner coin that has an accepted user photo *and* a reference image (plus private fields). Owner view: user photo wins (`Key('hero_coin_image')` / `NetworkImage` as specified in the widget, not only in the test). Guest/public view of *that same fixture*: private strings (`storageLocation`, notes, purchase cost) are absent *because they were redacted*, not because the projection never received them. Today's guest `PublicCoinProjection` uses a different invented NAC (`NAC-1921-MORGAN`) with no private fields, so `findsNothing` cannot fail.
7. **Record delivery commit `2dbb525e`** in §12 (origin/dev already has the v1.6 plan + review baton). Stop leaving "Delivery Commit: To be recorded" after the commit exists.

## Notes (not blocking alone)
- Site 5 comment dash (`parent missing — skip` vs pin en-dash) is a nit if the code quote itself stays verbatim.
- Constructor `coin:` → `initialCoin` mapping is the right compatibility shim; keep it.

## Boundaries
PLAN ONLY. `origin/main` locked `9f04550a`. Stripe OFF. Alerts only, never caps. No Argon. No code/deploy/Firestore/main. Pin `4d17ca5e` via `git show` / `git ls-tree`. Path: CoS 95+ → SAG 95+ → Eric typed YES. No Eric ping.
