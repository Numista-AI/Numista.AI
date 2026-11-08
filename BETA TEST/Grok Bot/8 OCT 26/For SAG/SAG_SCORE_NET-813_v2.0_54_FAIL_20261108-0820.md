# Independent SAG review net813

Full plan submitted; packet chars 425691
Usage: {"prompt_tokens": 117032, "completion_tokens": 3074, "total_tokens": 149631, "prompt_tokens_details": {"text_tokens": 117032, "audio_tokens": 0, "image_tokens": 0, "cached_tokens": 1152}, "completion_tokens_details": {"reasoning_tokens": 29525, "audio_tokens": 0, "accepted_prediction_tokens": 0, "rejected_prediction_tokens": 0}, "num_sources_used": 0, "cost_in_usd_ticks": 4279300000}

## Score / verdict

| Item | Result |
|---|---|
| **Score** | **54 / 100** |
| **Verdict** | **FAIL** (PASS requires ≥ 95) |
| **Mode** | Plan readiness only. No tools or tests were run. Prior CoS scores were not used as a target. |
| **Code YES** | **No** |
| **Main** | Stay locked at `9f04550a` |
| **Firestore writes / deploys** | Still require a separate Founder YES |

Deductions sum to 46. What remains is real grounding (pin quotes that match the supplied `4d17ca5e` excerpts, fail-closed gate shape, read-only store intent, stated locks). It is not an implementable acceptance plan.

| # | Severity | Deduction | Must-fix |
|---|---|---|---|
| MF-1 | Critical | −10 | Test/production API will not compile |
| MF-2 | Critical | −8 | Call-site snippets contradict the tested resolver and omit a required argument |
| MF-3 | Critical | −8 | Legislation acceptance path is not wired to real `CoinModel` |
| MF-4 | High | −8 | Catalog identity/schema conflicts with supplied `b0b05808` evidence; image guard rejects the plan’s own catalog host |
| MF-5 | High | −5 | Acceptance UI contract missing; currency assertions contradict each other |
| MF-6 | High | −4 | Rollback is not branch-scoped and clones **live** hosting |
| MF-7 | Medium | −3 | Guest CPG spec contradicts itself; shipped kill-switch value unspecified |

---

## Must-fixes

### MF-1 — Critical (−10): harness members used by tests and §6.3 do not exist

`UnifiedCoinDetailDeps` in §9.4 only has `store`, `clock`, and `lawsFetcher`.

These calls are in the plan and have no declaration:

- Test 4: `harness.loadedImageUrls`
- Test 7: `harness.lastLaunchedUrl`
- §6.3: `harness.recordLaunchUrl(url)`

`launchOutboundCongressUrl` therefore cannot compile, and Tests 4 and 7 cannot compile. H1–H3 (top-level getter, `dart:convert`, `_GateBundle.missing()`) look like legal Dart and are not the problem.

### MF-2 — Critical (−8): five collection wire-ups do not match G4/G5

`show` / `showPublic` require `legacyOpen`. §3.4 prose says every snippet passes it. The snippets themselves do not. Pasted as written, they do not compile.

G4 says all five sites call top-level `resolveParentIndex`, and Tests 2–3 only test that function. The snippets still call `_resolveParentIndexForVirtualChild`, which is not a method on `_MyCollectionScreenState`, and call site 5 still uses `docs.indexWhere`. Tests 2–3 can pass even if no call site uses the shipped resolver.

Verified call sites 4 and 5 on `4d17ca5e` (`my_collection_screen.dart` `:3041–3045` and `:3117–3124`) do match the *current* inspector calls. The replacement blocks do not match the plan’s own resolver rule.

### MF-3 — Critical (−8): Test 8 cannot pass from the specified loader

Supplied `coin_model.dart` has `programSeries` (`:9`) and no `legislationKey` / `legislation_key`. `fromCoinModel` sets `legislationKey: null`.

§6.4 step 1 matches `legislation_key` only. The pin’s real mapper is `_matchLawKey()` at `coin_detail_screen.dart:3030–3068` (series/denom/theme → keys such as `110-456`). That mapper is not in the new screen.

Test 8 mounts a coin with `programSeries: 'America the Beautiful Quarters'` and expects the 110-456 title. Nothing in the spec connects those.

`_congressGovFetch` is called in §6.5 and never defined (no URL, no parse, no key handling). The pin’s legislation tab reads Firestore `metadata/coin_legislation` (`:2956–2966`) plus `_kDefaultLaws` (`:2973–3026`). It does not call a Congress.gov metadata API.

### MF-4 — High (−8): catalog pin and image schema are not the supplied evidence

Distinguish the trees:

- Collection / `CoinModel` / `coin_detail_screen.dart` / pin `pubspec.yaml`: supplied as **`4d17ca5e`**.
- Catalog screen: supplied as **`b0b05808`**, labeled not the baseline pin, and **not present at `4d17ca5e`**.

The plan never names `b0b05808`. It binds the catalog to `origin/dev` @ **`6af2afb1`** in the header and @ **`bde8b402`** in G1/D1. Those SHAs are not in the packet. Line text for `:77–82`, `:464–467`, and `:810` does match **`b0b05808`**, including the note that `:315` is `child: Column(`. The identity of the file does not.

`b0b05808` `catalog_browse_screen.dart` reads `primary_image` as a Map with **`url`** and **`source`** (`:903–929`, `:1080–1107`). It does not read `license` or `source_url`. The plan’s `_approvedPrimaryImageUrl` requires non-empty `license` and `source_url`. If the live field is `source`, every catalog hero becomes a placeholder and Test 15 fails.

Test 15 hard-requires `NAC1.MD.US.PRV.LIBAM.1782.XX.BASE.S`, a Met URL, and `NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3`. The packet’s catalog read is **3202** rows and only verifies `NAC1.CN.US.1D.MORGANSILV.1921.D.BASE.2` and `NAC1.CN.US.1D.AMERICANSI.2024.W.SILVEREAGL.A`. The 248-row / Met-URL claim is not in the supplied evidence.

Pin `pubspec.yaml` assets (`:92–96`) list `assets/`, `assets/data/`, `assets/fonts/`, `assets/mint_mark_diagrams/`. The plan adds only `assets/config/`. It does not register `assets/catalog/`, which Test 15 loads. `assets/` is not recursive.

§7.4 `isOwnedStorageUrl` allows only two Firebase/GCS bucket prefixes. The plan’s own Met host is outside that list. §7.5 never says catalog HTTPS URLs bypass that guard, so an approved catalog URL can be accepted by §4.2 and rejected by the hero guard.

### MF-5 — High (−5): tests assert widgets and strings the screen spec never defines

No `build` method defines tabs, chevrons, value toggle, or hero. Tests still require:

- `Key('udv_header_title')` / `Key('udv_header_surface')` — one prose sentence only
- `Key('hero_coin_image')` — not specified outside Test 12
- `Icons.arrow_forward_ios`, text `Show values`, text `Legislation` — not in the widget snippets
- `Key('ebay_search_button')` finds nothing — **cannot fail** unless that key is specified on any eBay control

Currency assertions disagree with each other and with no stated formatter:

- Test 5 expects `$50.00` for `cpgRetail: 50.0`
- Test 12 expects `45.00` (no `$`) for `purchaseCost: '45.00'`

Pin financials use both raw cost strings and `\$` + `toStringAsFixed(2)` (`coin_detail_screen.dart` around `:1662–1679`). One renderer cannot satisfy both tests.

### MF-6 — High (−4): rollback is a live hosting change

§9.1 step 2 is `firebase hosting:clone … numista-vault:live`. Checkpoint 6 only deploys preview channel `pr-net813`. Cloning onto **live** is a production deploy, not a branch-scoped undo, and the rollback steps do not require a separate Founder YES. Git revert to `dev` does avoid `main`. That part is fine. `tac` is also not a portable laptop rollback tool.

### MF-7 — Medium (−3): two spec holes that change behavior

- §5 says guest CPG is visible. `fromCoinModel` always sets `cpgRetail: null` even though pin `CoinModel.cpgRetail` is a non-null `double` (`:54`, default `0.0` at `:130`). Guest-from-owner then always hits “Estimate unavailable” (§4.3).
- `features.json` initial `unified_details_view_v1` value is never specified. Fail-closed is only for missing/malformed JSON. Shipping `true` turns the kill-switch off on first build.

---

## What did check out

- Pin quotes that are actually in the packet match: markdown sink `:2785–2806`, header `:59`, `:892–893`, `:918–921`, `:925` (`Colors.white60`), Congress button `:3152–3165`, `CoinModel` fields used by `fromCoinModel` / `toSyntheticCoinModel`, `_cachedCoinsDocs` at `:131`, card taps at `:3042–3044` and `:3118–3122`.
- White-on-`#F4F4F2` contrast math (~1.10:1) matches the pin header.
- H1–H3 are plausible Dart fixes. Gate fail-closed on throw is coherent with `_GateBundle.missing()`.
- Read-only `CachedCoinDocStore.setDoc` → `UnsupportedError`, 0 Firestore writes in the stated path, main lock `9f04550a`, Stripe stated OFF, billing **alert** not a cap, no private collector records in the plan.
- Test 14’s index walk matches `_stepNavigation` **if** that method is what ships (0 → 1 → 4).
- Test 9’s expected sanitizer string matches the §7.2 regex order.

---

## Polish (not scored)

- “Founder Founder”; header DTG `07:55` vs v2.0 `08:12`.
- Test 11 comments still say `firestoreService`; the code uses `t.store`.
- §6.1 says the four laws are verbatim from `:2973–3027`, then adds `editorial_verified`, which is not in `_kDefaultLaws`.
- Gate snippet uses `jsonDecode` with no `dart:convert` import shown.
- Kill-switch Future is cached for the process; a file flip needs a restart. Say so.
- Congress URL check does not reject userinfo; image check does.

---

## Uncertainties (not scored, not treated as facts)

- `my_collection_screen.dart` excerpt jumps `:200` → `:2950` and `:3832` → `:4370`. Call sites 1–3 (`:2723–2783`) and the claimed eBay widget at `:3861` were **not** in the supplied show. `_onSearchEbay` is at `:4408`. Those cites are unverified, not proven false.
- `CollectionRow` constructor is not in the packet. `crw.snapshot` is used at `:2994`, so a snapshot field exists; named args in the tests are unverified.
- `license` / `source_url` might exist on the JSON in addition to `source`. The packet does not show the JSON. Only `url` and `source` are proven by the screen.
- `bde8b402` and `6af2afb1` are not shown. They might or might not match `b0b05808`.
- `implements QueryDocumentSnapshot` plus `cloud_firestore` ^6.2.0 may fail widget-test load. Not proven here.
- `flutter_markdown_plus` `imageBuilder` signature was not in the packet. `onTapLink` matches the pin’s 3-arg use.
- Whether a hosting preview actually ships the Flutter binary that contains the asset kill-switch is unspecified.

---

## Next gate

Do not YES code, branch creation, preview deploy, or Firestore writes on this revision.

Revise the plan only, then re-review. Minimum close-out:

1. Add the missing harness members or delete those assertions; keep Tests 4 and 7 compiling against §9.4.
2. Make every call-site snippet call `resolveParentIndex` and pass `legacyOpen` with the pin’s current invocation unchanged.
3. Port a real law-key rule from pin `_matchLawKey` (or stop claiming Test 8). Define or drop `_congressGovFetch`. Do not invent a Congress.gov client.
4. Re-bind catalog to **`b0b05808`** unless a later packet shows another SHA. Align provenance fields with evidenced `url` / `source`, or quote the JSON fields from that SHA. Register `assets/catalog/` if Test 15 stays. Exempt approved catalog HTTPS hosts from the storage-bucket guard.
5. Specify the widget contract the tests observe, including one currency format.
6. Rollback: delete preview channel `pr-net813` only; no `hosting:clone` to live without a separate deploy YES.
7. Ship `unified_details_view_v1: false` until a later YES. Align guest CPG with §5 or change §5.

Main remains `9f04550a`. Stripe stays OFF. Alerts stay alerts. No collector PII in fixtures or logs.