# GB CoS score — NET-810 Mint Product Fields, Detail View v1.2

**73/100 — FAIL.** Pass bar 95+. Not ready for SAG, Eric YES or execution.
Reviewed Sat 7 Nov 2026, ~9:14–9:20 PM ET (America/New_York). Baton `BATON_NET-810_GROKCOS_REVIEW_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.2_20261107-2100.md` (mtime 20:46 ET, stamp 21:00). Plan `docs/PLAN_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.2.md` (1,236 lines, 55,060 bytes on disk / 53,736 UTF-8 chars, SHA-256 `0de9ae15ef8eea9eac7d50e29da9b77e7329f3996408f1622066ce04426322aa` matches the baton). Delivery commit origin/dev **843c1d59**. Writer AG CoS v5 `cfe23a7a`, attempt **2/4** (v1.1 was 56 FAIL; v1.0 was 58 FAIL). Next: **v1.3 attempt 3/4**.

## Evidence
Cites checked with `git show 4d17ca5e:<path>` and `git ls-tree` on EDS_Laptop; origin/dev `catalog_public_v1.json` parsed (3,202 records). origin/main `9f04550a` locked. Stripe OFF. PLAN ONLY. No builds/tests/writes/deploys/messages.

**Verified correct:** Public catalog on origin/dev is `numista_mobile/assets/catalog/catalog_public_v1.json` (5,895,259 bytes; 2,965 coins / 181 notes / 56 medals). origin/dev `pubspec.yaml:97` already lists `- assets/catalog/`; pin `pubspec.yaml:92-96` quote is verbatim (no catalog entry at the pin). `NAC1.CN.US.1D.MORGANSILV.1921.D.BASE.2` exists (1921-D Morgan Silver Dollars, Denver, `status_badge` "Needs source", `is_placeholder` false). Fugio example `NAC1.CN.US.1C.FUGIO.1787.XX.BASE.1` exists. `_DetailsTab` class at `coin_detail_screen.dart:1513-1570` and Notes at `:1541` match the quoted body. `_DetailsTab(` call-site body matches `:774-778` (inside `TabBarView` `:771`). `_DetailTile` body matches `:3268-3309` (`_kSubtext` is `:61`). Composite key fields `year` / `mint_facility` / `mint_mark_on_coin` / `denomination` / `series` (no top-level `variety`) match the public schema. CoinModel decoupling (no new fields, no `toPublicCatalogMap`) is the right design. UnifiedCoinDetailsModal dropped from R1/AC-3. Display/value-separation rules remain solid.

## Prior CoS-56 must-fix closeout
| # | Must-fix | v1.2 | Evidence |
|---|---|---|---|
| 1 | Name a source file that exists | **Mostly closed** | Phantom `catalog_master_3202.jsonl` discarded. Public catalog artifact verified. Overlay `mint_product_fields_v1.json` + `scripts/export_mint_product_fields.py` are new/planned (absent on origin/dev). Generation input is only "government public data feeds or official U.S. Mint schedule exports" — no concrete file or API. |
| 2 | Make the join actually match | **Partial** | Prefix fixed to `RegExp(r'^NAC1?\.')`. Composite fallback uses real keys and fails closed on 0 or >1. 1921-D example is real (and is the only 1921-D Morgan, so composite would uniquely match). But `NAC1.CN.US.1D.MORGANSILV.2024.W.PRF.1` is not in the public catalog (zero 2024 Morgan records). Eligible statuses `{PUBLISHED_ON_X, PREVIEW_DRAFT, PUBLISHED}` are not public `status_badge` values (real badges: Needs source 1724, Details coming 950, none 519, Pre-Federal 9). The verified 1921-D row is `status_badge: "Needs source"` — it would be dropped if badges are filtered through `kEligibleStatuses`. `record_status` is not a public-catalog key. Primary NAC path still reads user free-text `personalRef` (CoinModel has no `nac_code`). |
| 3 | Remove `toPublicCatalogMap` / drop CoinModel fields | **Closed** | Plan keeps CoinModel byte-identical to the pin. Private-key *test* is still a tautology (see must-fix 4). |
| 4 | Wire initialization | **Partial** | Intent is right (`ensureInitialized().then` + `setState` if mounted, fail closed). Cited lines and the surrounding `initState` body are wrong (see must-fix 1 below). |
| 5 | Drop or gate UnifiedCoinDetailsModal | **Closed** | R1/AC-3 scoped to `_DetailsTab` only. |
| 6 | Real style hook | **Mostly closed** | 3-tuple + `isMuted` + `_kSubtext` / `FontWeight.normal` is the right hook. Diff hunks are labeled `:1584-1620`, which is `_FinancialsTab`, not `_DetailTile` (`:3268-3309`). Applying those hunks as numbered would edit the wrong widget. |
| 7 | Tests that can fail for the right reason | **Partial** | Injected-metadata widget test is the right shape, but `_DetailsTab` is library-private so `test/mint_product_fields_test.dart` cannot name it unless exported (`@visibleForTesting`) or tested through a public surface. FakeFirestore is never injected (zero-writes test is a tautology). Private-key test only checks a hardcoded `publicKeys` list. Claimed GestureDetector ancestor check is not in the suite (and values already have a long-press copy `GestureDetector` at `:3299`). |

## Numbered blocking must-fixes (v1.3)
1. **Fix every file:line citation vs `git show 4d17ca5e`.** `_CoinDetailScreenState.initState` is `:183-193`, not `:111-125` (`:111-125` is `CoinDetailScreen.show`). Real `initState` calls `_loadInspectorMode()` — there is no `_checkWishlist()` or `_loadProvenance()` in this file. `_DetailsTab(` call site is `:774-778` inside `TabBarView` `:771`, not `:845-855` (845-855 is the edit-form "Personal Notes" field / hero-header comment). `_DetailTile` is `:3268-3309`, not `:1584-1620` (`:1588` starts `_FinancialsTab`). Optimistic `toFirestore()` uses are `:491` and `:683` (plan cites `:490` and `:682`, the `fromMap` lines). Rewrite the section 9 diffs with hunks that would apply at those real lines. Do not invent methods in the quoted baseline.
2. **Do not invent catalog records.** `NAC1.CN.US.1D.MORGANSILV.2024.W.PRF.1` / `status_badge: "Published"` / `$80.00` / `release_date: "2024-07-11"` is not in `catalog_public_v1.json`. Keep the verified 1921-D example. For a modern Mint-product demo, pick a NAC that actually exists, or clearly label overlay-only fixture data as not-in-catalog.
3. **Align the status allow-list with the artifact you bind to.** Public catalog has `status_badge` / `is_placeholder`, not `record_status`. None of `PUBLISHED_ON_X` / `PREVIEW_DRAFT` / `PUBLISHED` appear as badges. Show one real record that would survive the gate you specify (the 1921-D row would not, if badges must be in `kEligibleStatuses`). Overlay records may use overlay status fields — say which file each field comes from.
4. **Make the tests compile and actually fail for the right reason.** Export `_DetailsTab` for tests or pump a public surface. Inject `FakeFirebaseFirestore` into the lookup/render path (or drop the unused fake). Serialize `MintProductMetadata` / overlay JSON and assert the ten private collector keys are absent; do not assert against a hardcoded allow-list. If you claim no `GestureDetector` ancestors on Mint rows, test that — or drop the claim, because `:3299` already uses one for clipboard copy.
5. **Name the overlay's real input.** `scripts/export_mint_product_fields.py` reading unspecified "government public data feeds" is not a source file. Name the Mint/export file or API (and mark it to-be-acquired if it is not in repo yet).

## Rubric
| Dimension | v1.0 | v1.1 | v1.2 |
|---|---:|---:|---:|
| Schema fidelity / source of truth / ingestion | 9 | 6/20 | 14/20 |
| Display rules / zero-urgency / value separation | 14 | 17/20 | 18/20 |
| Code correctness against real APIs / line citations | 11 | 13/20 | 12/20 |
| Allow-list gate / persistence safety / operational locks | 11 | 9/20 | 16/20 |
| Tests / verification / handoff integrity | 13 | 11/20 | 13/20 |
| **Total** | **58** | **56** | **73/100 FAIL** |

Source binding, CoinModel decoupling, and dropping UnifiedCoinDetailsModal are real gains. The score stays well under 95 because surgical line labels would patch the wrong widgets (and invent two `initState` calls), the modern "demonstrable" NAC is not in the catalog, the status allow-list does not match public badges, and three tests cannot compile or cannot fail for the reason claimed.

No AJ identifying values reproduced. No approval granted. Route: CoS 95+ -> SAG 95+ -> Eric typed YES; separate gates for writes, publishing, rules and deploys. No messages sent, no Eric ping.
