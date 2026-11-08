# GB CoS score — NET-810 Mint Product Fields, Detail View v1.1

**56/100 — FAIL.** Pass bar 95+. Not ready for SAG, Eric YES or execution.
Reviewed Sat 7 Nov 2026, ~7:52–8:00 PM ET (America/New_York). Baton `BATON_NET-810_GROKCOS_REVIEW_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.1_20261107-1940.md` (mtime 19:39:16 ET, stamp 19:40). Plan `docs/PLAN_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.1.md` (1,065 lines, 50,689 bytes, mtime 19:34 ET). Delivery commit origin/dev **97e0b35e**. Desk note `DESK_NOTE_NET-810_v1.1_GROKCOS_REVIEW_20261107-1941.md` read. Writer AG CoS v5 `cfe23a7a`, attempt **1/4** (v1.0 was 58 FAIL). Next: **v1.2 attempt 2/4**.

## Evidence
Cites checked with `git show 4d17ca5e:<path>` and `git ls-tree` on EDS_Laptop; origin/dev asset tree via `git ls-tree origin/dev -- numista_mobile/assets`; box `/workspace/catalog-preview/schema.json` + `entries.jsonl` (327 records). origin/main 9f04550a locked. Stripe OFF. PLAN ONLY. No builds/tests/writes/deploys/messages.

**Verified correct:** `toFirestore()` quote (P493–542) is verbatim vs pin `coin_model.dart:248–297`, zero-arg signature preserved. `_DetailsTab` is `StatelessWidget` at `coin_detail_screen.dart:1513`, `fields` opens at 1526, Notes at 1541. Neutral status copy, enum allow-list, ISO `release_date` validator with round-trip check, `release_time_et` pairing, NaN/negative handling and the 30-day freshness rule are well specified. Real test path `numista_mobile/test/`, marked To be authored. Revert via `$PRE_EXEC_SHA..HEAD`, main lock kept.

## Prior CoS-58 must-fix closeout
| # | Must-fix | v1.1 | Evidence |
|---|---|---|---|
| 1 | Source of truth / ingestion | **Not closed** | See must-fix 1–2 below. |
| 2 | `release_date` spec | **Mostly closed** | §5 formal ISO spec + fail-closed rules. But §4.2 lists `release_date` and `mint_product_as_of` as defined in `schema.json` 544–575; box schema has only `product_price_usd` (544), `mint_schedule_status` (551), `release_time_et` (~563), `product_availability` (~570). State them as proposed additions. |
| 3 | `toFirestore` / allow-list placement | **Partial (new defect)** | Signature preserved — good. But `toPublicCatalogMap()` starts from `toFirestore()` (P557), which emits `Purchase Cost`, `Purchase Date`, `Retailer/Website`, `Retailer Invoice #`, `Storage Location`, `Personal Notes I`, `Personal Reference #`, `owner_photos`, `provenanceLedger`, `transferId`… A "public catalog map" built from a private user coin is a PII leak path (AJ rule). The prior must-fix said the allow-list belongs in the catalog export/publish pipeline, not on `CoinModel`. |
| 4 | Real APIs / fail-closed gaps | **Partial** | Parsing/NaN fixed; helper paths named (`lib/helpers/mint_product_helper.dart`, `lib/services/mint_product_lookup_service.dart`). But `ensureInitialized()` is never called anywhere in the plan; `_DetailsTab` (StatelessWidget) calls sync `lookupForCoin`, which returns `null` while `_cacheByNac == null` — fields never render. |
| 5 | UnifiedCoinDetailsModal | **Not closed** | R1 (P589) and AC-3 (P985) still require rendering in `UnifiedCoinDetailsModal`, which does not exist at the pin and whose plan (NET-813) is FAIL. Limit v1 to `_DetailsTab` or declare an explicit dependency. |
| 6 | Neutral copy / style / value separation | **Mostly closed** | Copy, allow-list, freshness, value separation good. Styling still prose only: rows are `(String,String)` tuples rendered by the shared row (P697–723); no per-row style hook exists to apply `onSurfaceVariant`. |
| 7 | Tests | **Partial** | `testWidgets` added, but: (a) "Detail tab renders exact issue price label" pumps `CoinDetailScreen` with no injected lookup/fake asset and the asset does not exist → label never appears; real `CoinDetailScreen` also needs Firebase setup. (b) Card/browse test renders a `ListTile` it built itself — tautology. (c) "Zero buy links" never checks InkWell/url_launcher. (d) The claimed "zero Firestore writes via mock counter" test is absent (no mock/counter in §9). |
| 8 | Acceptance / manifest / rollback / timeline | **Mostly closed** | 10-point AC, file manifest, revert, 13 Nov fit present. Manifest omits the catalog asset itself and the pubspec `assets/catalog/` registration. |

## Numbered blocking must-fixes (v1.2)
1. **Name a source file that exists.** `assets/catalog/catalog_master_3202.jsonl` is absent at the pin (`git ls-tree 4d17ca5e` — no match) and at origin/dev (only `numista_mobile/assets/catalog/catalog_public_v1.json`), and was not found anywhere under the laptop's Documents. Pin `pubspec.yaml:92–96` does not declare `assets/catalog/`. The quoted SHA-256 `FBA6C66A…` matches an earlier CoS census of the master handoff file, which found **all 3,202 records proposal-status / not Mint-verified** — so "3,202 verified master entries" is not true. Do not bundle an unpublished master into the public web build. Bind to the published catalog artifact (or a dedicated, privacy-cleared Mint-fields artifact), state how it gets there, and register it in pubspec.
2. **Make the join actually match.** NAC codes are `NAC1.CN.US.…` (box entries, e.g. `NAC1.CN.US.1C.FUGIO.1787.XX.BASE.1`), but `lookupForCoin` only tries `coin.personalRef` starting with `NAC-` (P400–401) — a user free-text field and the wrong prefix. Composite fallback reads `mint_mark` and `variety`, but entries carry `mint_mark_on_coin` (bool) and no `variety` key, so the key collapses to year|''|denom|'' and is ambiguous or wrong. Quarantine checks `record_status` for `PROPOSAL`/`UNVETTED`; real values are `PREVIEW_DRAFT` (306), `PUBLISHED_ON_X` (13), `DRAFT_POST` (7), `PLACEHOLDER` (1) — none quarantined. 0 of 327 box entries carry `product_price_usd`. Define the real key mapping, the eligible status allow-list, and show at least one real record that would render.
3. **Remove `toPublicCatalogMap` from `CoinModel`** (or build it from an explicit allow-list of public catalog keys, never `toFirestore()`). Add a test that private keys (Purchase*, Retailer*, Storage Location, Personal Notes I, Personal Reference #, owner_photos, provenanceLedger, transfer*) are absent. Drop the 5 `CoinModel` fields if the lookup returns `MintProductMetadata` directly — they are otherwise dead or a persistence hazard.
4. **Wire initialization.** Call/await `ensureInitialized()` (e.g. FutureBuilder or a parent State) before `_DetailsTab` builds; specify rebuild after load. Fail closed if load fails.
5. **Drop or gate the `UnifiedCoinDetailsModal` requirement** in R1/AC-3 (NET-813 not approved).
6. **Real style hook.** Show the code change that lets Mint rows render muted values (e.g. a 3-tuple or a `muted` set checked in the row builder) with exact lines.
7. **Tests that can fail for the right reason.** Inject a fake lookup (or fake asset bundle) into the detail-tab test; render real card/browse widgets for absence tests; assert no `InkWell`/`GestureDetector`/`Link` ancestors on Mint rows; add the zero-writes test with a real fake Firestore; add the private-key-absence test from #3.

## Rubric
| Dimension | v1.0 | v1.1 |
|---|---:|---:|
| Schema fidelity / source of truth / ingestion | 9 | 6/20 |
| Display rules / zero-urgency / value separation | 14 | 17/20 |
| Code correctness against real APIs / line citations | 11 | 13/20 |
| Allow-list gate / persistence safety / operational locks | 11 | 9/20 |
| Tests / verification / handoff integrity | 13 | 11/20 |
| **Total** | **58** | **56/100 FAIL** |

Display rules, date validation, the preserved `toFirestore` signature and the rollback/acceptance sections are solid. The score stays below 58 because the source file does not exist in the repo, the join cannot match real NAC codes or keys, the lookup is never initialized, and the new public serializer would carry private collection fields.

No AJ identifying values reproduced. No approval granted. Route: CoS 95+ → SAG 95+ → Eric typed YES; separate gates for writes, publishing, rules and deploys. No messages sent, no Eric ping.
