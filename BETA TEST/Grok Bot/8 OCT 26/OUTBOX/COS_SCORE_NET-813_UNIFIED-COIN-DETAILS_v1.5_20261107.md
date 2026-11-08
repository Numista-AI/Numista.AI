# GB CoS score — NET-813 Unified Coin Details View v1.5

**81/100 — FAIL.** Pass requires 95+. Not ready for SAG, Eric YES or execution.
Reviewed Sat 7 Nov 2026, ~7:50–8:00 PM ET (America/New_York). Baton `BATON_NET-813_GROKCOS_REVIEW_UNIFIED-COIN-DETAILS-VIEW_v1.5_20261107-1945.md` (mtime 19:45:40 ET; stamp 19:45 ET — matches). Plan `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.5.md` (1,078 lines, 51,873 bytes, mtime 19:45 ET). Delivery commit on origin/dev **00957e85** (`docs(net-813): deliver Unified Coin Details View plan v1.5 and review baton`). Writer AG CoS v5 `cfe23a7a`, attempt **2/4**. Next if revised: **v1.6 attempt 3/4**.

## Evidence
All cites checked with `git show 4d17ca5e:<path>` (pin) on EDS_Laptop, not the working tree. Public entry checked at `git show origin/dev:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`. origin/main locked at 9f04550a. Stripe OFF. PLAN ONLY. No builds/tests run, no writes, no deploys, no messages.

## Prior CoS-86 must-fix closeout
| # | Must-fix | v1.5 verdict | Evidence |
|---|---|---|---|
| 1 | Real CoinModel / CollectionRow | **Closed** | `toSyntheticCoinModel()` now uses real fields (`themeSubject`, String `year`, `mintMark`, `imageUrlObverse/Reverse`, `personalNotes`, `metalContent`, `cpgRetail` double, `storageLocation`, String `purchaseCost`/`aiEstimatedValue`). Pin `coin_model.dart:81–` constructor: only `id` required, others defaulted — compiles. `CollectionRow` tests pass `data:` (pin `collection_row.dart` `required this.id, required this.data`). `showPublicWidget` gone; `.public(...)` constructor published. |
| 2 | Harness + assertions that can fail | **Not closed** | Closeout claims "injectable `fakeFirestoreService`, fake clock, image loader capture". The harness in §10 (P813–833) has only counters, `lastLaunchedUrl`, `isWeb`, `simulatedLatency`. No Firestore fake, no clock, no image capture. Test 11 still passes vacuously unless the widget calls `harness.recordWrite()` itself. Test 2/3 are static list math, not widget navigation. Test 5 passes `cachedCoinsDocs: []`, so `_stepNavigation` (P344–350) hits the cache-miss banner and never navigates — the test cannot pass. Test 8 has no timeout/fake-clock case. Test 9 calls `tester.element(find.byType(SizedBox).first)` without pumping any widget (throws), and its expected string is wrong: the link regex turns `![img](https://evil.com/pic.png)` into `!img` and `**Important**` is not stripped, so the result is not `'See Congress for details.  Important'`. Test 12 claims user-photo priority but asserts none. |
| 3 | Mid-nav parent identity + list rule | **Mostly closed** | `nextParentIndex >= 0 ? nextParentIndex : null` (P354–357) — never `targetIdx`. List-changes-while-open rule stated (P363–364). **Gap:** `onNavigate` handlers at both wire-up sites are empty stubs (P298–300, P312–314) and `coin` / `currentParentIndex` are `final` on the widget, so a second Next uses stale `widget.coin` / index. Navigation state must live in `State` (current coin, current index) or the caller must rebuild the sheet. |
| 4 | Kill-switch loader + revert loop | **Closed** | `rootBundle.loadString('assets/config/features.json')` with no `?v=` (P776); explicit `merge-base --is-ancestor` loop over `scratch/revert_shas_net813.txt` (P754–756). Note: pin `pubspec.yaml:92–96` declares `assets/`, `assets/data/`, `assets/fonts/`, `assets/mint_mark_diagrams/` only — `assets/config/` (and `assets/data/checked_legislation_manifest.json` is fine) must be added to the manifest/file list or the loader fail-closes forever. |
| 5 | Verbatim cites / defenses / unverified claims | **Partial (regression)** | **Closed:** §2.5 markdown `:2785–2806` now verbatim; header `:59`, `:892–893`, `:918–921`, `:925` verbatim; `imageBuilder → SizedBox.shrink()` + `onTapLink` no-op restored; `/studio-…-uploads/` dropped. **New regressions:** see must-fix 1 and 3 below (§2.1–§2.4 call-site quotes fabricated; manifest citations altered). |
| 6 | Handoff hygiene | **Mostly closed** | Stamp 19:45 = mtime; attempt 2/4 stated; closeout section cites now match headings. §12 says "Delivery Commit: To be recorded" though 00957e85 exists. |

## Numbered blocking must-fixes (v1.6)
1. **Re-quote all five call sites from `git show 4d17ca5e:numista_mobile/lib/screens/my_collection_screen.dart` — §2.1–§2.4 are not what the file says (v1.4's quotes were closer).**
   - §2.1: real `:2726` is `final row = vicinity.row;`, `:2729` `final crw = docs[row];`, `:2730` `final m = crw.data;`, `:2734` `final effectiveId = crw.isVirtualChild ? (crw.parentDocId ?? crw.id) : crw.id;`, `:2736` `void onTap() => _showCoinInspectorDialog(effectiveId, m);`. Plan shows `final row = crw.data;`, `effectiveId = crw.id`, `_showCoinInspectorDialog(effectiveId, row)` at 2734.
   - §2.2: real `:2754–2783` uses `_cachedCoinsDocs` (not `_allCoinsDocs`), returns early when parent is missing, and calls `CoinDetailScreen.show(context, coin: coin, spotPrices: _spotPrices, onNavigateToAiChat: …, onDeleted: …, onEdited: …)` (named args, pin `coin_detail_screen.dart:108–115`). Plan shows positional `CoinDetailScreen.show(context, CoinModel.fromMap(...), parentDoc)`.
   - §2.3: real card tap `:3042–3044` is `setState(() => _selectedCoinId = effectiveId); _showCoinInspectorDialog(effectiveId, m);` — **not** `CoinDetailScreen.show`. §1's site list (site 4 at `:3041`, site 5 at `:3118` as `CoinDetailScreen.show`) is wrong.
   - §2.4: real `:3118–3122` resolves `m['parent_set_id']` against `_cachedCoinsDocs` and calls `_showCoinInspectorDialog(parentDoc.id, parentDoc.data())`.
   - §2.7 laws: real `:3152` is `if ((law['congress_url'] ?? '').toString().isNotEmpty) ...[` and `:3153` `SizedBox(height: 16),` (non-const).
2. **Make the wire-up compile and keep existing behavior.** §3.4 uses `_allCoinsDocs` (0 occurrences at pin; real field `_cachedCoinsDocs` `:131`) and passes `_filteredRows` as a list, but `:787` is a method `List<CollectionRow> _filteredRows(List<CollectionRow> rows)`. Bind to the real `docs` list each builder already receives (`_buildDataTable(List<CollectionRow> docs…)` `:2557`, `_buildCardGrid(…)` `:2982`). Unified `show()` drops `spotPrices`, `onNavigateToAiChat`, `onDeleted`, `onEdited` from the real `CoinDetailScreen.show` — carry them or state the replacement (melt needs spot prices; delete/edit must refresh the list).
3. **Use the real `_kDefaultLaws` values in the manifest — no edits.** Pin `coin_detail_screen.dart:2973–3027`: `110-161` title is `District of Columbia and United States Territories Circulating Quarter Dollar Program Act`, citation `121 Stat. 2014 (31 U.S.C. § 5112(r))` (plan: shortened title, `121 Stat. 2018`, no USC); `116-330` citation `134 Stat. 5101 (31 U.S.C. § 5112(z))` (plan: `§ 5112(x)`). Copy values verbatim from the pin; keep `editorial_verified: false`.
4. **Finish the harness for real and fix the tests that cannot pass.** Add the injectable Firestore read/write fake, fake clock for the 4.0 s laws timeout, URL and image-loader capture actually consumed by the widget. Test 5 needs real cached docs (fake `DocumentSnapshot`s) so Next actually navigates; assert parent index after a virtual-child step. Test 9: pump a widget before `tester.element`, and fix the expected sanitizer output (or extend the sanitizer to strip `!`-image syntax and emphasis). Test 12: add an owner fixture with an accepted user photo and assert it outranks the reference image; add a guest test on the same fixture. Add a laws timeout test.
5. **Move navigation state into `State`.** `_UnifiedCoinDetailScreenState` must hold current coin + current parent index and update them on step; wire `onNavigate` to something real or remove it. Test two consecutive Next steps across a virtual-child group.
6. **Asset manifest + hygiene.** Add `assets/config/` (features.json) and the manifest path to the pubspec/file manifest. Record delivery commit in §12.

## Rubric
| Dimension | v1.4 | v1.5 |
|---|---:|---:|
| Standing locks / read-only / approval boundaries | 19 | 19/20 |
| Branch, rollback and feature gate | 13 | 14/15 |
| Five-site resolution / navigation identity | 14 | 9/15 |
| Laws, notes and outbound safety | 13 | 12/15 |
| Guest privacy / CPG / image precedence | 12 | 13/15 |
| Accessibility / low-click UX | 9 | 9/10 |
| Offline verification / field-test readiness | 6 | 5/10 |
| **Total** | **86** | **81/100 FAIL** |

MF-1 (real CoinModel), MF-4 (loader + revert loop), markdown/header verbatim cites and the restored Markdown defenses are real progress. The score drops because the ground-truth call-site section — the foundation of the five-site consolidation — no longer matches `git show`, the wire-up references a field that does not exist, the manifest altered real statute citations, and the closeout claims harness capabilities the code does not contain.

No AJ PII found in the plan. No authority granted. Sequence: CoS 95+ → SAG 95+ → Eric typed YES; separate code/preview/live gates. No messages sent, no Eric ping.
