# GB CoS SCORE — NET-815 / FAILFIX_PLAN_NET-777_CATALOG_v1.7

- Scorer: Grok Bot Chief of Staff · 2026-11-05 ~7:10 PM ET (America/New_York)
- Repository inspected read-only: origin/dev @ b0b058087f1492244a0c0b769e126b38ac1ba06c; origin/p7-v8.9 reviewed at e364fd07 (docs staging refreshed to 605a22c9); origin/main remains 9f04550a45fa4da082ba8948c2d89a521a90fa45.
- Mode: SCORE ONLY. No code execution, code change, deploy, Firestore write/rules change, main change, Stripe change, or external message.
- **CoS: 64 / 100 FAIL** (pass >=95).
- SAG: independent xAI API grok-4.7 review filed separately; CoS score was not supplied to SAG.
- Cycle has no Argon. Eric YES gate: BLOCKED pending NET-816 revision and independent pass.

## 1. Six v1.6 must-fixes against the real code and the proposed patches

| Requirement | Result | Evidence / reason |
|---|---|---|
| 1. Retail on real card, sourced migration, fallback | **PARTIAL / BLOCKING** | v1.7 now targets the real `_CatalogCard.build` and reads `item['cpgRetail']`. But `valCpg` is nullable and `hasValidRetail` does not promote it, so `valCpg.toStringAsFixed(2)` fails static analysis. The migration names a script but no source file, input schema, NAC join, or verified-price provenance. Actual dev JSON has 3,202 entries and zero `cpgRetail`. No positive, string-price, missing/zero, or no-fallback test is supplied. The new pending-chip colors also regress contrast (below). |
| 2. Close real image path and correct CSP | **PARTIAL / BLOCKING** | The real schema (`primary_image` / `type_image`) and real CSP location (283–284) are now correct. But §3.B declares `static const _allowedImageHosts` and `_isAllowedImageUrl()` without a valid class scope; `static` is illegal at top level. `_CatalogCard` is a separate class and its proposed call to `_isAllowedImageUrl()` is therefore undefined. The real card still directly passes `imgMap['url']` to `Image.network`; 167 external primary URLs remain in actual data. |
| 3. B05N-14 same type AND series, fail closed | **FAIL** | Proposed code references nonexistent `MintError.series` and `MintError.coinTypes`, and nonexistent `CoinModel.series` / `CoinModel.type` instead of `programSeries`. No model/parser migration is specified. Its year-first branch can still return a year-only match when error series/type are empty. Caller/helper signatures are not consistently updated. Greysheet merely adds query parameters with no server-side filter verification. No real regression test is supplied. |
| 4. B05N-15 Google Images + Kaggle removal | **FAIL** | The defects remain on both real branches. Plan’s line-range deletion is not a valid patch: the widget continues past 3538, so “DELETE 3531–3538” leaves syntax behind. The proposed terminal text is unreachable because `_buildSimilarCoinsInspector` already returns `SizedBox.shrink()` when not loading and empty. No timeout/finally clears loading on fetch failure. `ref_image_widget.dart` header still names `assets/kaggle/`; `photo_sharing_service.dart` also retains Kaggle ingestion. Pinned dev execution does not include the needed p7 collection fixes in its integration list. |
| 5. Spend readiness / real Hosting shutoff | **PASS AS PLAN RUNBOOK; execution evidence still required** | Plan honestly labels the $20 automated email unbuilt and does not pretend to have executed shutoff. Manual preview deletion / Hosting disable, test notification, hourly checks and accountable primary/backup are now specified. Treat as a proposed runbook, not a live cap: before ad activation the human operator must verify project/budget mapping, test delivery and command outcome. Backup must be a human with access, not an agent acting as Eric. No shutoff was run in this review. |
| 6. Pin real branch and clean revert | **PASS FOR ROLLBACK; integration needs precision** | `git rev-parse origin/dev` still returns b0b058087f1492244a0c0b769e126b38ac1ba06c. `git revert <execute commit set>` plus Hosting release/channel restore is correct and does not check out stale main. Actual p7 still has no catalog screen or `/catalog` known route, so restricting execution to dev is correct. However, integration must be a tested complete commit set, not a loose list of individual files that would drop imports, asset registration and the other fixes. |

## 2. Verbatim real-code evidence

Actual dev loader, lines 58–66, loads the bundled JSON into `_allEntries`:
```dart
Future<void> _loadCatalog() async {
  try {
    final jsonString = await rootBundle.loadString('assets/catalog/catalog_public_v1.json');
    final List<dynamic> raw = json.decode(jsonString);
    final List<Map<String, dynamic>> entries = raw.map((e) => Map<String, dynamic>.from(e as Map)).toList();
    // setState -> _allEntries = entries
```

Actual dev card, lines 1105–1110, still has no host guard:
```dart
child: imgMap != null && imgMap['url'] != null
    ? Image.network(
        imgMap['url'] as String,
        fit: BoxFit.contain,
        errorBuilder: (c, e, s) => _buildPlaceholder(),
```

Actual `MintError` model has `denominations`, `years`, `mintMarks`, `datasets`, `relatedCoinIds` and other fields, but no `series` or `coinTypes`. Actual `CoinModel` exposes `programSeries` and `themeSubject`, not `series` or `type`.

Actual library match at `mint_error_service.dart:79–98` remains:
```dart
static Future<List<MintError>> getErrorsForCoin({
  required String denomination,
  required int year,
}) async {
  // ...
  return all.where((e) => e.years.isEmpty || e.years.contains(year)).toList();
}
```

Actual p7 collection still has:
```dart
onPressed: () => _onSearchGoogle(data),
label: Text('Google Images'),
```
and `https://www.google.com/search?tbm=isch&q=$query`, plus `Tap to expand * Kaggle reference datasets`.

The proposed mintage replacement correctly drops real `sourceUrl`, `InkWell` and `launchUrl` and retains plain `val` / `label`. Preserve that change.

## 3. B27-8 / B27-11 regression checks

- **B27-8 (+B05N-15): REGRESSED / STILL OPEN.** Google Images action, Kaggle caption, microscope text and reference-widget comments are still present in real code. Proposed line deletion and dead empty-state do not solve the spinner or complete the removal. Add executable tests for the whole inspector/clone surfaces and an error/timeout terminal state.
- **B27-11 (+B05N-12): STILL OPEN AND NEW REGRESSION INTRODUCED.** v1.7 never addresses site-wide contrast. On p7, `coin_detail_screen.dart:2769` gives AI Insights a white `_kSurface` in light mode while lines 2789, 2790 and 2792 force white h1/h2/strong text. The new 11px pending chip uses `#B78103` on `#FFF8E1`, measured at **3.21:1**, below WCAG AA’s 4.5:1 for normal text. White on `#F5F5F5` is 1.09:1. Replace with theme-aware dark text and add contrast assertions plus Eric field-test evidence.

## 4. Other launch blockers

1. **Deep-link quote is not the actual file.** Real dev lines 71–82 match only `nac_code`, return `<String,dynamic>{}` from `orElse`, check `match.isNotEmpty`, and defer the modal using `addPostFrameCallback`. Plan invents `id` fallback, `orElse: () => null` and a direct modal call. `orElse: null` would be a type error. `window.history.pushState` / `popstate` is JavaScript, not a Dart implementation; use the project’s actual web interop and lifecycle tests.
2. **Ask Morgan remains ungrounded in routing.** The new `_openAskMorganForCoin` is not wired to the existing `_openAskMorgan` callers, and its `pushNamed('/collection')` occurs inside a catalog `MaterialApp` without registered routes. Guest sign-in/signup redirects need the verified outer-navigation path and return-to-catalog behavior.
3. **Verification is not executable yet.** Actual repo test is `test/catalog_browse_test.dart`; the three plan-named test files are absent. It is valid to propose new files, but the plan supplies neither test contents/assertions nor fixture schemas. “Verified tests” must not be claimed until they run.
4. **Image guard must reconcile CSP and allowlist.** `numista.ai` and `numista-vault.web.app` are allowed by the proposed Dart set but are not explicit `img-src` entries. Either use approved `storage.googleapis.com` / relative same-origin assets or specify an exact CSP change and test. The Dart host check cannot replace a correct Hosting policy.

## 5. Scoring rubric

| Dimension | Score |
|---|---:|
| Correct rollback and execution locks | 19/20 |
| Real loader / retail implementation | 11/20 |
| Image schema / no-hotlink implementation | 7/15 |
| Mintage and preserved catalog fixes | 13/15 |
| Real Hosting spend readiness | 8/10 |
| B05N-14 / B05N-15 and B27 regressions | 1/10 |
| Branch integration / launch verification | 5/10 |
| **Total** | **64/100 FAIL** |

## 6. NET-816 blocking must-fixes

1. Supply compiling, class-correct card and image code: promote nullable retail safely; specify verified CPG source, input schema, NAC join and tests; put the image guard in a valid accessible scope and align allowlist/CSP. Test all external primary/type URLs fail before fetch and valid internal/relative assets still render.
2. Rewrite B05N-14 against the real models. Define canonical series/type fields and parsing/read migration without any Firestore write under this approval; use actual `programSeries` (or a documented normalization), consistent caller/helper signatures and a verified Greysheet server filter. Every result must require both known/matching series AND type AND applicable year; blank metadata fails closed. Supply the 1958 Washington vs 1999 NJ negative and same-series positive tests.
3. Give complete structural deletions for Google Images and Kaggle, not partial line numbers. Add timeout/error/finally terminal handling, remove the entire Similar/Kaggle surface as requested, cover microscope/ref-image/photo-sharing references, and port the fixes to the actual target tree. Tests must prove no off-site photo action remains (Congress.gov Laws only).
4. Add B27-11: replace white-on-white Markdown and audit table/card/detail surfaces for WCAG AA; use theme-aware dark text. Correct the pending chip to at least 4.5:1. Include automated contrast checks and a field-test gate.
5. Correct the deep-link and Ask Morgan implementations to the actual source and navigation structure, and provide the real test files with assertions before calling verification complete. Preserve the real dev SHA and full-set revert, and make any later p7 integration a tested complete change set.

## 7. PII and locks

No AJ PII or credentials in the review artifacts. Public institutional attribution is not treated as private PII. No code changes/deploys/Firestore writes/rules; no external messages; origin/main unchanged at 9f04550a; Stripe unchanged OFF. SAG ran independently through xAI grok-4.7 with plan + real code only.