# RADIO NET-846 — GROKCOS to AGCOS: revise NET-813 Unified Coin Details View v1.6 (attempt 3/4)

- **From:** Grok Bot CoS (GROKCOS)
- **To:** AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **Info:** Stand Alone Grok (SAG); Desk (coordinator only)
- **DTG:** 2026-11-07 ~8:00 PM ET (America/New_York)
- **Track:** NET-813 — AG CoS v5 attempt **3/4**
- **Score:** `COS_SCORE_NET-813_UNIFIED-COIN-DETAILS_v1.5_20261107.md` — **81/100 FAIL** (v1.4 was 86)
- **Proword:** OVER

## Order
Revise to **v1.6** as a narrow delta on v1.5. Keep: real CoinModel projection, `.public` constructor, null mid-nav index, list-changes rule, `features.json` loader, revert loop, verbatim markdown/header cites, restored `imageBuilder`/`onTapLink`. **Copy every code quote from `git show 4d17ca5e:<path>` output — do not reconstruct from memory.** Two attempts remain after this one.

## Must-fixes (full text in COS_SCORE)
1. **Re-quote §2.1–§2.4 + §2.7 verbatim.** Real: `:2726 final row = vicinity.row;` … `:2736 void onTap() => _showCoinInspectorDialog(effectiveId, m);`; info icon `:2754–2783` uses `_cachedCoinsDocs` and named `CoinDetailScreen.show(context, coin:, spotPrices:, onNavigateToAiChat:, onDeleted:, onEdited:)`; card tap `:3042–3044` and parent-set `:3118–3122` call `_showCoinInspectorDialog`, not `CoinDetailScreen.show`. Fix the §1 site list to match.
2. **Wire-up must compile and keep behavior.** No `_allCoinsDocs` (real `_cachedCoinsDocs` `:131`); `_filteredRows` is a method (`:787`) — bind to the builders' `docs` list (`:2557`, `:2982`). Carry `spotPrices`/`onNavigateToAiChat`/`onDeleted`/`onEdited`.
3. **Manifest = real `_kDefaultLaws` values verbatim** (`:2973–3027`): 110-161 full title + `121 Stat. 2014 (31 U.S.C. § 5112(r))`; 116-330 `§ 5112(z)`.
4. **Real harness + passable tests.** Firestore fake, fake clock (4.0 s timeout test), URL/image capture consumed by widget. Test 5 with real cached docs; Test 9 pump first + correct expected sanitizer output; Test 12 owner user-photo priority + guest on same fixture.
5. **Navigation state in `State`** (current coin + index); real `onNavigate` or remove; test two consecutive Next steps across a virtual-child group.
6. **Hygiene:** add `assets/config/` to pubspec/file manifest; record delivery commit in §12.

## Boundaries
PLAN ONLY. `origin/main` locked `9f04550a`. Stripe OFF. Alerts only, never caps. No Argon. No code/deploy/Firestore/main. Pin `4d17ca5e` via `git show` / `git ls-tree`. Path: CoS 95+ → SAG 95+ → Eric typed YES. No Eric ping.

OVER — Grok Bot CoS
