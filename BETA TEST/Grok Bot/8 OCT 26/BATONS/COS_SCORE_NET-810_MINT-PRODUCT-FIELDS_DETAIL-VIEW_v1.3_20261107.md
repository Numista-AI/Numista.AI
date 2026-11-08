# GB CoS score — NET-810 Mint Product Fields, Detail View v1.3

**88/100 — FAIL.** Pass bar 95+. Not ready for SAG, Eric YES or execution.
Reviewed Sat 7 Nov 2026, ~9:45–9:52 PM ET (America/New_York). Baton `BATON_NET-810_GROKCOS_REVIEW_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.3_20261107-2200.md` (mtime 21:35 ET, stamp 22:00). Plan `docs/PLAN_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.3.md` (58,651 bytes, SHA-256 `f0dba9076450e80fc6ce96212b9c75494fe23002f4e350f62cc3640251debd1d` matches the baton). Delivery commit origin/dev **62f68439**. Writer AG CoS v5 `cfe23a7a`, attempt **3/4** (v1.2 was 73 FAIL; v1.1 was 56 FAIL; v1.0 was 58 FAIL). Next: **v1.4 attempt 4/4**.

## Evidence
Cites checked with `git show 4d17ca5e:<path>` and `git ls-tree` on EDS_Laptop; origin/dev `catalog_public_v1.json` parsed (3,202 records). origin/main `9f04550a` locked. Stripe OFF. PLAN ONLY. No builds/tests/writes/deploys/messages.

**Verified correct:** Public catalog on origin/dev is `numista_mobile/assets/catalog/catalog_public_v1.json` (2,965 coins / 181 notes / 56 medals). `is_placeholder`: false **2,251** / true **951** (Details coming 950 are all `is_placeholder: true`; Needs source 1,724 / none 519 / Pre-Federal 8 are non-placeholder, plus 1 Pre-Federal placeholder). `NAC1.CN.US.1D.MORGANSILV.1921.D.BASE.2` exists (1921-D Morgan Silver Dollars, Denver, Dollar, `status_badge` "Needs source", `is_placeholder` false, `mint_mark_on_coin` true). `NAC1.CN.US.1D.AMERICANSI.2024.W.SILVEREAGL.A` exists (2024-W American Silver Eagle, West Point, Silver, Dollar, `status_badge` "Needs source", `is_placeholder` false, `mint_mark_on_coin` true). Invented `NAC1.CN.US.1D.MORGANSILV.2024.W.PRF.1` is absent (correctly discarded). `_DetailsTab` call site `:774-778` inside `TabBarView` `:771`, `_DetailTile` `:3268-3309` (`GestureDetector` clipboard at `:3299`), `initState` `:183-193` calling `_loadInspectorMode()` at **`:192`** (line 193 is the closing `}`), optimistic `toFirestore()` spreads at `:491` and `:683` (wrappers are `CoinModel.fromMap({...}, _coin.id)` at `:494` / `:686`). CoinModel decoupling and dropped UnifiedCoinDetailsModal remain correct. Display/value-separation rules remain solid. Overlay input named `data/usmint/usmint_product_schedule_2024.json` STATUS: TO-BE-ACQUIRED / PLANNED.

## Prior CoS-73 must-fix closeout
| # | Must-fix | v1.3 | Evidence |
|---|---|---|---|
| 1 | Fix every file:line citation vs `git show 4d17ca5e` | **Mostly closed** | `initState` range `:183-193` and `_loadInspectorMode()` are correct (no `_checkWishlist` / `_loadProvenance`). Call site `:774-778` / `TabBarView` `:771` and `_DetailTile` `:3268-3309` match; section 9 hunks target those lines and add `typedef _DetailsTab = DetailsTab`. Remaining: the plan says `_loadInspectorMode()` is "at line 193" (it is `:192`). The `toFirestore()` wrapper quotes omit the pin's `, _coin.id` argument (`:494` and `:686`). |
| 2 | Do not invent catalog records | **Closed** | Invented 2024 Morgan NAC discarded. Modern demo is the verified 2024-W ASE NAC above. Overlay-only fields (`product_price_usd` 80.00, `release_date` "2024-07-11") are placed in planned `mint_product_fields_v1.json`, not claimed as public-catalog columns. 1921-D retained. |
| 3 | Align the status allow-list | **Closed** | Public gate is `is_placeholder == false` (2,251 pass / 951 stubs). `record_status` and `{PUBLISHED_ON_X, PREVIEW_DRAFT, PUBLISHED}` are gone as the live filter. Both demo records survive. Public schema vs overlay fields are tabulated. |
| 4 | Tests that compile and fail for the right reason | **Partial** | `@visibleForTesting class DetailsTab` plus `typedef _DetailsTab = DetailsTab` is the right export. Commerce-button absence assertions replace the impossible `GestureDetector` ban. `MintProductMetadata.toJson()` private-key checks are the right shape for the overlay. Remaining: `FakeFirebaseFirestore` is still never injected (created, then `MintProductLookupService.forTesting(entries: ...)` runs without it — collection length stays 0 vacuously). The "public catalog record" half of the serializer test is a handmade map that never contained private keys. Test imports use `package:numista_mobile/...` but pin `pubspec.yaml` is `name: numista_ai`. |
| 5 | Name the overlay's real input | **Closed** | `data/usmint/usmint_product_schedule_2024.json`, marked `STATUS: TO-BE-ACQUIRED / PLANNED`. |

## Numbered blocking must-fixes (v1.4 — attempt 4/4 last try)
1. **Inject `FakeFirebaseFirestore` into the lookup/render path, or drop the unused fake.** Today's zero-writes test constructs `fakeFs`, looks up via `MintProductLookupService.forTesting` without passing `fakeFs`, then asserts `fakeFs.collection('coins')` is still empty. That cannot fail if production code writes through a real client.
2. **Use the real package name in tests:** `package:numista_ai/...` (pin `numista_mobile/pubspec.yaml` line 1 is `name: numista_ai`), not `package:numista_mobile/...`.
3. **Serialize a real public catalog record** (load `NAC1.CN.US.1D.AMERICANSI.2024.W.SILVEREAGL.A` from `catalog_public_v1.json`, or serialize the overlay JSON the script would emit) and assert the ten forbidden private collector keys are absent. Do not assert against a handmade map that never had those keys.
4. **Finish the pin quotes.** `toFirestore()` wrapper lines are `:490-494` and `:682-686` and include `, _coin.id`. `_loadInspectorMode();` is **line 192**, not 193 (193 is `}`).

## Rubric
| Dimension | v1.0 | v1.1 | v1.2 | v1.3 |
|---|---:|---:|---:|---:|
| Schema fidelity / source of truth / ingestion | 9 | 6/20 | 14/20 | **18/20** |
| Display rules / zero-urgency / value separation | 14 | 17/20 | 18/20 | **18/20** |
| Code correctness against real APIs / line citations | 11 | 13/20 | 12/20 | **17/20** |
| Allow-list gate / persistence safety / operational locks | 11 | 9/20 | 16/20 | **19/20** |
| Tests / verification / handoff integrity | 13 | 11/20 | 13/20 | **16/20** |
| **Total** | **58** | **56** | **73** | **88/100 FAIL** |

Real NAC binding, the `is_placeholder` gate, named overlay input, and corrected widget line ranges are genuine gains. The score stays under 95 because the zero-writes test is still a tautology, the test package imports would not resolve, the public-record privacy assertion is still handmade, and the `toFirestore()` quotes dropped `, _coin.id`.

No AJ identifying values reproduced. No approval granted. Route: CoS 95+ -> SAG 95+ -> Eric typed YES; separate gates for writes, publishing, rules and deploys. No messages sent, no Eric ping.
