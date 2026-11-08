# GB CoS score — NET-810 Mint Product Fields, Detail View v1.4

**93/100 — FAIL.** Pass bar 95+. Not ready for SAG, Eric YES or execution. Revision attempts are **exhausted (4/4)**. No v1.5 revise order tonight.
Reviewed Sat 7 Nov 2026, ~10:14–10:25 PM ET (America/New_York). Baton `BATON_NET-810_GROKCOS_REVIEW_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.4_20261107-2230.md` (mtime 22:09 ET, stamp 22:30). Plan `docs/PLAN_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.4.md` (62,772 bytes, 1,340 lines, SHA-256 `79bab214362a6f24f4f961950e8b4d8f5a8201ed102a288f45d5e93759f8526c` matches the baton). Delivery commit origin/dev **43e44ce1**. Writer AG CoS v5 `cfe23a7a`, attempt **4/4 LAST TRY** (v1.3 was 88 FAIL; v1.2 was 73 FAIL; v1.1 was 56 FAIL; v1.0 was 58 FAIL). Next: hold for morning / Eric. No v1.5 wake.

## Evidence
Cites checked with `git show 4d17ca5e:<path>` and `git ls-tree` on EDS_Laptop; origin/dev plan hash matches the on-disk file. origin/main `9f04550a` locked. Stripe OFF. PLAN ONLY. Alerts only, never caps. No Argon. No builds/tests/writes/deploys/messages.

**Verified correct:** Public catalog on origin/dev is `numista_mobile/assets/catalog/catalog_public_v1.json` (2,965 coins / 181 notes / 56 medals). `is_placeholder`: false **2,251** / true **951**. `NAC1.CN.US.1D.MORGANSILV.1921.D.BASE.2` and `NAC1.CN.US.1D.AMERICANSI.2024.W.SILVEREAGL.A` exist (both `status_badge` "Needs source", `is_placeholder` false). Invented `NAC1.CN.US.1D.MORGANSILV.2024.W.PRF.1` remains discarded. `_DetailsTab` call site `:774-778` inside `TabBarView` `:771`, `_DetailTile` `:3268-3309` (`GestureDetector` clipboard at `:3299`), `initState` `:183-193` calling `_loadInspectorMode()` at **`:192`** (line 193 is `}`), optimistic `toFirestore()` wrappers are `CoinModel.fromMap({...}, _coin.id)` at `:490-494` / `:682-686` (uses at `:491` / `:683`). Pin `numista_mobile/pubspec.yaml` line 1 is `name: numista_ai`. CoinModel decoupling, dropped UnifiedCoinDetailsModal, display/value-separation rules, and named overlay input `data/usmint/usmint_product_schedule_2024.json` STATUS: TO-BE-ACQUIRED / PLANNED remain correct.

## Prior CoS-88 must-fix closeout
| # | Must-fix | v1.4 | Evidence |
|---|---|---|---|
| 1 | Inject `FakeFirebaseFirestore` into the lookup/render path, or drop the unused fake | **Closed (residual)** | `forTesting` now accepts `firestore:` (:652-658). Zero-writes `testWidgets` (:1170-1226) constructs `fakeFs`, passes `firestore: fakeFs`, looks up, pumps `DetailsTab` with resolved metadata, taps `\$80.00`, and asserts `coins` and `users` stay empty. Residual: `_firestore` is stored (:646, :658) but never read by `ensureInitialized` or `lookupForCoin`; `DetailsTab` does not receive the client. A write through `FirebaseFirestore.instance` would still go uncaught. |
| 2 | Use `package:numista_ai/...` in tests | **Closed** | Test imports at :978-981 are `package:numista_ai/models/coin_model.dart`, `.../mint_product_metadata.dart`, `.../mint_product_lookup_service.dart`, `.../coin_detail_screen.dart`. No leftover `package:numista_mobile/` imports (filesystem paths under `numista_mobile/` remain correct). |
| 3 | Serialize a real public catalog record and assert the ten forbidden private collector keys are absent | **Closed** | Privacy test (:1228-1279) loads `NAC1.CN.US.1D.AMERICANSI.2024.W.SILVEREAGL.A` from `assets/catalog/catalog_public_v1.json` (File, with `rootBundle` fallback), asserts `status_badge: 'Needs source'` and `is_placeholder: false`, then checks the forbidden keys against both `MintProductMetadata.toJson()` and the real record. Handmade public-catalog map is gone. Residual: `File('assets/catalog/...')` is CWD-relative; the `rootBundle` fallback sits in a plain `test()` rather than `testWidgets`. |
| 4 | Finish the pin quotes (`toFirestore` wrappers including `, _coin.id`; `_loadInspectorMode();` is line 192) | **Closed** | Section 3.2 quotes `:490-494` and `:682-686` verbatim including `, _coin.id` (matches `git show 4d17ca5e`). Notice at :174 correctly cites `_loadInspectorMode();` at **line 192** and line 193 as `}`. Residual: the initState fence (:161-172) includes `@override` which is pin `:182` under a "lines 183–193" heading. Section 3.2 labels the TabBarView excerpt "768–782"; pin `Expanded(` is `:770`, `TabBarView` `:771` (call site `:774-778` is correct in §7.2). |

## Remaining defects (recorded for morning; not a new attempt)
1. **Document identity:** H1 and `Document Version` still say **v1.3** / `RADIO_NET-851` / DTG 22:00 ET, while the filename, §12, and the review baton say v1.4 / 22:30 / `RADIO_NET-855`. Leftover v1.2→v1.3 must-fix rows after a broken `---` separator at :53-59 collide with the new MF-1..MF-4 numbers.
2. **`_firestore` is accepted and stored but never used.** The zero-writes test now injects `fakeFs` (the v1.3 tautology of asserting on an uninjected client is gone) but still cannot observe writes that bypass the unused field.
3. Minor citation range labels: initState fence includes `@override` (`:182`); TabBarView excerpt start labeled 768 vs pin `Expanded` at `:770`.
4. Privacy-test file load depends on CWD; `rootBundle` fallback is not inside `testWidgets`.

## Rubric
| Dimension | v1.0 | v1.1 | v1.2 | v1.3 | v1.4 |
|---|---:|---:|---:|---:|---:|
| Schema fidelity / source of truth / ingestion | 9 | 6/20 | 14/20 | 18/20 | **18/20** |
| Display rules / zero-urgency / value separation | 14 | 17/20 | 18/20 | 18/20 | **18/20** |
| Code correctness against real APIs / line citations | 11 | 13/20 | 12/20 | 17/20 | **19/20** |
| Allow-list gate / persistence safety / operational locks | 11 | 9/20 | 16/20 | 19/20 | **19/20** |
| Tests / verification / handoff integrity | 13 | 11/20 | 13/20 | 16/20 | **19/20** |
| **Total** | **58** | **56** | **73** | **88** | **93/100 FAIL** |

The four numbered CoS-88 must-fixes are addressed in the plan text (injection + `package:numista_ai` + real catalog privacy load + pin quotes with `, _coin.id` and line 192). The score stays under 95 because the document header is still labeled v1.3, `_firestore` is still unread dead weight, and a few excerpt ranges remain off by one or two lines.

No AJ identifying values reproduced. No approval granted. Route: CoS 95+ -> SAG 95+ -> Eric typed YES; separate gates for writes, publishing, rules and deploys. No messages sent, no Eric ping.
