# Independent SAG review net810

Full plan submitted; packet chars 292780
Usage: {"prompt_tokens": 82971, "completion_tokens": 2448, "total_tokens": 110160, "prompt_tokens_details": {"text_tokens": 82971, "audio_tokens": 0, "image_tokens": 0, "cached_tokens": 1152}, "completion_tokens_details": {"reasoning_tokens": 24741, "audio_tokens": 0, "accepted_prediction_tokens": 0, "rejected_prediction_tokens": 0}, "num_sources_used": 0, "cost_in_usd_ticks": 3273480000}

## Score / verdict

| Item | Result |
| :--- | :--- |
| Plan | NET-810 v1.6 (plan readiness only; not implemented behavior) |
| Verdict | **FAIL** |
| Score | **64 / 100** |
| Pass bar | >= 95 |
| Tools / tests run by this review | **None** |

| Criterion | Deduction | Notes |
| :--- | ---: | :--- |
| Baseline: `4d17ca5e` vs catalog at `b0b05808` | −10 | Code quotes match the pin; catalog is not on that pin |
| Contradictory executable spec | −8 | §5.1 vs §7.1; stale Firestore matrix; initState swallows errors |
| Unsourced Mint facts / provenance | −6 | Example prices can be read as shippable; model has no provenance |
| Screen diff will not compile as written | −3 | Missing imports |
| US-only + blank mint fail-open | −4 | Charter US-only; pin default `mintMark` is `''` |
| Rollback not safe / not portable | −3 | Unconditional push; `tac`; second branch |
| Tests assert unverified fields / wrong reason | −2 | `status_badge`; placeholder test |
| **Total** | **−36** | **64** |

## What the pin evidence does support

Supplied `git show 4d17ca5e` matches the plan’s quotes for `coin_model.dart` lines 1–28 and `toFirestore()` 248–297; `coin_detail_screen.dart` `initState` 182–193 (`_loadInspectorMode();` at 192, `}` at 193), TabBarView 770–786, `fromMap` wrappers 490–494 and 682–686 including `, _coin.id`, `_DetailsTab` 1513–1544, and `_DetailTile` 3268–3309. `pubspec.yaml` line 1 is `name: numista_ai`; assets are lines 92–96 with no `assets/catalog/`; `firebase_core` is line 39 and `cloud_firestore` is line 40; dev deps do not include `fake_cloud_firestore`.

`CoinModel` is correctly left unmodified. §7.1’s eligible-index rule (`is_placeholder == false` only, both joins, unique composite, overlay-only return) is internally coherent. Main lock prefix `9f04550a`, Stripe OFF, alert-not-cap, no Firestore field on the new service, and NET-813 exclusion match the standing boundaries. Those strengths do not clear the blockers below.

Catalog rows were read from **`b0b05808`, not `4d17ca5e`**. Verified public columns there: both cited NAC rows exist, `is_placeholder` false, and year / `mint_facility` / denomination / series / type match the plan’s join examples. **`status_badge` is not in that verified column list.** The plan never names `b0b05808`.

## Must-fixes

**MF-1 — Blocker (−10). Execution tree is three SHAs, and the catalog is not on the pin.**  
Plan pins code to `4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235` and says those citations are the target tree, but also targets `origin/dev` (claimed `bde8b402`, not in this packet) and depends on `numista_mobile/assets/catalog/catalog_public_v1.json`. Supplied evidence: that public catalog was read from **`b0b05808` and is not present at `4d17ca5e`**. Registering `assets/catalog/` on the pin tree does not create the file; a missing asset directory fails asset bundling, and the privacy test’s `rootBundle.loadString('assets/catalog/catalog_public_v1.json')` cannot pass on the pin. Byte size `5,895,259`, type split 2,965/181/56, and status-badge counts are not in the supplied evidence.  
**Required plan change:** one execution SHA; name catalog blob source `b0b05808` separately from code pin `4d17ca5e`; preflight that cited line numbers still match that tree and that the catalog path exists before the pubspec diff; do not apply a duplicate `assets/catalog/` line if it is already present; drop or mark unverified any catalog statistic not re-checked on that SHA.

**MF-2 — Blocker (−8). Two current join specs disagree; old Firestore spec is still written as executable.**  
§5.1 still returns on `_byNacCode!.containsKey(ref)` and does not apply the placeholder gate. §7.1 returns null when the NAC is missing or not explicitly `is_placeholder == false`, and does not fall through to composite. §2’s carried-forward MF-1 still says inject `FakeFirebaseFirestore`, which §2.1/§7.1 removed. §7.1 says non-asset exceptions must not be swallowed; §7.2 `ensureInitialized().catchError((_) {})` swallows them on the only production wiring, including a FlutterFire `[core/no-app]` failure.  
**Required plan change:** delete or replace §5.1 with the §7.1 algorithm; mark the v1.3→v1.4 matrix historical/non-executable; remove the blanket `catchError` or limit it to the same two tolerated types and surface anything else.

**MF-3 — High (−6). Unsourced Mint values can still be shipped as facts.**  
§4.2 and the file-manifest description present concrete overlay prices/dates as the new asset. §5.5 still specifies production rendering of those values. `MintProductMetadata` has no `source_url` or `retrieved_at`, so the §2.0 MF-4 provenance rule is not representable. `scripts/export_mint_product_fields.py` has no contract. `displayStatus` hardcodes `"Available from U.S. Mint (as of Nov 2026)"` and ignores `mint_product_as_of`.  
**Required plan change:** committed `mint_product_fields_v1.json` is `{}` until `data/usmint/usmint_product_schedule_2024.json` is acquired; exporter is local-file-in/local-file-out only (no network, no Firestore, omit any field without provenance); synthetic values stay in tests only; as-of text comes from `asOfDate` or is omitted.

**MF-4 — High (−3). Screen diff is not compilable as written.**  
§7.2 and §9 reference `MintProductLookupService` and `MintProductMetadata`. Pin imports in `coin_detail_screen.dart` (lines 16–45) do not include them, and no import hunk is specified. `@visibleForTesting` is fine via `material.dart`.  
**Required plan change:** add the two relative imports to the surgical diff.

**MF-5 — High (−4). Not US-only; blank mint mark fail-open.**  
Lookup never requires US country, NAC `.US.`, or `type == coin`. Pin `CoinModel` defaults `mintMark` to `''` (line 84) and `country` to `'USA'` (line 109). §5.2/§7.1 map `''` to `'Philadelphia'`, and §10 locks that in. An unfilled mint mark can attach a Philadelphia Mint row.  
**Required plan change:** fail closed unless the coin is US and the catalog row is `type == coin` (or NAC segment `.US.`); blank/unknown mint mark must not become Philadelphia.

**MF-6 — High (−3). Rollback is not safe or branch-scoped for this environment.**  
§11.3 asserts only the local name `dev`, then unconditionally `git push origin dev` (remote write, no Founder YES). It needs `tac` and bash process substitution while AC-R2 is PowerShell. An empty list still reaches push. Target text also says synced to `origin/p7-v8.9`, which the script does not revert. It never checks upstream `origin/dev` or that HEAD is not main `9f04550a`.  
**Required plan change:** local reverts only until a separate Founder YES; abort on empty list, dirty tree, non-`dev`, wrong upstream, or main; PowerShell-native reverse or `git rev-list` with no `tac`; no push to `p7-v8.9` unless that branch is in scope with its own SHA list.

**MF-7 — Medium (−2). Acceptance tests are not evidence-tight.**  
Privacy test expects `realRecord['status_badge'] == 'Needs source'`, which this packet does not verify. The “Quarantined placeholder” coin omits `programSeries`, so §7.1 returns null on empty series before the placeholder row matters. It does not fail for the stated reason.  
**Required plan change:** assert only packet-verified public fields unless `status_badge` is re-verified; give the placeholder composite case full year/facility/denomination/series keys so null is caused by `is_placeholder: true`.

## Polish (no deduction)

- AC-4 says `facilityToMintMark`; code maps mint mark to facility.
- `release_time_et` is parsed and never displayed.
- Schedule status and product availability can render the same sentence twice (tests expect that).
- §2.1 “carried forward unchanged” is stale after the §7/§10/§11 edits.
- AC-7 pin line numbers for `_DetailTile` will shift after earlier insertions.
- Half-dime and nickel both normalize toward `5c` if those strings appear.
- Financial exclusion is by not editing `_FinancialsTab`, not by a test.

## Uncertainties (no deduction; not treated as facts)

- Full SHA expansion and `origin/dev` = `bde8b402` are plan claims; this packet only labels `git show 4d17ca5e` and catalog-from-`b0b05808`.
- Packet does not quote the catalog blob path or whether the root JSON value is an array.
- Whether `b0b05808` is an ancestor of `origin/dev` is unknown. That is why MF-1 is a preflight, not an assumption that `origin/dev` is already safe.
- `[core/no-app]` on `FirebaseFirestore.instance` was not re-verified here.
- `rootBundle.loadString` inside `tester.runAsync` may be zone-sensitive; not executed.
- Exact composite hit rate against real `programSeries` strings is unknown. Fail-closed on non-unique match is the right default.

## Next gate

Plan revision only. Do not patch code, run tests, write Firestore, seed, deploy, or push. Close MF-1..MF-7 in the plan text, then re-review. Firestore writes and any deploy/push still need a separate Founder YES after a passing plan. Main stays locked at `9f04550a`. Stripe stays OFF. Billing stays alert-only. Promo material stays out. No private collector fields in the public catalog or overlay.