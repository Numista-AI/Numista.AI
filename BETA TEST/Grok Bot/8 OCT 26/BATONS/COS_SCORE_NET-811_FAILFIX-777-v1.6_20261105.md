# GB CoS SCORE — NET-811 / FAILFIX_PLAN_NET-777_CATALOG_v1.6

- Scorer: Grok Bot Chief of Staff · 2026-11-05 ~6:00 PM ET (America/New_York)
- Repo checked read-only: p7-v8.9 @ 71852bf9; origin/dev @ b0b058087f1492244a0c0b769e126b38ac1ba06c; origin/main @ 9f04550a
- Mode: SCORE ONLY; no execute, deploy, Firestore write, rules change, main change, or Stripe change
- **CoS: 64 / 100 FAIL** (pass >=95)
- Argon: 99 PASS; not treated as repository evidence
- SAG: independent xAI grok-4.7 result filed separately
- Eric YES gate: BLOCKED pending revision and independent pass

## 1. Prior four blocking must-fixes

| Check | Result | Real repository evidence |
|---|---|---|
| Rollback | **PASS** | `git rev-parse origin/dev` returns `b0b058087f1492244a0c0b769e126b38ac1ba06c`; it is still dev HEAD. The plan now specifies `git revert <execute commit set>` and Hosting release/channel restoration rather than an old-file checkout. |
| Hosting egress shutoff | **PARTIAL / BLOCKING** | The manual `firebase hosting:disable` / preview channel deletion is the correct billed-path mechanism, and the false active Cloud Function claim is gone. But the plan asserts an automated $20 alert while labeling its Pub/Sub topic unbuilt. No verified alert, single accountable operator/backup, or pre-launch runbook test establishes that a human will be notified before the cap. |
| Loader and retail precedence | **FAIL** | The loader exists and runs on dev, but the retail rule is not attached to the real card. `_loadCatalog()` decodes the JSON into `_allEntries`; the grid calls `_CatalogCard(item: item)`. Actual `_CatalogCard.build` at 1079–1150 reads only image, badge, year, denomination and name. The screen contains no `cpgRetail`, `valCpg`, `fmt`, or `Valuation Pending`. The plan’s isolated pseudocode never patches this renderer or supplies a concrete migration/fallback. |
| Mintage variables/link | **PASS AS PROPOSED** | Actual dev `_buildMintageRow` at 987–1023 contains `val`, `label`, `sourceUrl` and outbound `InkWell` / `launchUrl`. The proposed replacement removes `sourceUrl`, the InkWell and launchUrl and uses plain text. Correctly treated as plan work, not as already executed. |

### Live-code quotations

Actual loader, origin/dev lines 58–61:
```dart
Future<void> _loadCatalog() async {
  try {
    final jsonString = await rootBundle.loadString(
      'assets/catalog/catalog_public_v1.json');
    final List<dynamic> raw = json.decode(jsonString);
```

Actual card input and rendering, origin/dev lines 1079–1087 and 1136–1150:
```dart
Widget build(BuildContext context) {
  final primaryImg = item['primary_image'] as Map?;
  final typeImg = item['type_image'] as Map?;
  final imgMap = primaryImg ?? typeImg;
  final badge = item['status_badge'] as String?;
  final year = item['year']?.toString() ?? 'Undated';
  final denom = item['denomination']?.toString() ?? '';
  // ... title and metadata only; no valuation branch.
  Text([year, denom].where((s) => s.isNotEmpty).join(' · '));
```

Actual outbound mintage action, origin/dev lines 1010–1016:
```dart
InkWell(
  onTap: () async {
    final uri = Uri.tryParse(sourceUrl);
    if (uri != null) await launchUrl(uri);
  },
  child: const Text('(source)', ...),
),
```

## 2. Additional repo-grounded blockers

### A. B05N-14 is absent and the real filter is too broad

Tracker: error examples must match the same coin type and series. The plan never mentions B05N-14 or Known Errors.

Real `mint_error_service.dart:79–98`:
```dart
static Future<List<MintError>> getErrorsForCoin({
  required String denomination,
  required int year,
}) async {
  final normalized = _normalizeDenomination(denomination);
  // Firestore filter: denominations contains normalized
  return all.where((e) => e.years.isEmpty || e.years.contains(year)).toList();
}
```
There is no series or type argument. `_KnownErrorsTab` also passes only denomination/year to library and Greysheet requests. Empty error years explicitly match any year, allowing the reported 1999 NJ example on a 1958 Washington quarter.

### B. B05N-15 is absent and both offending UI paths remain

Real `my_collection_screen.dart:3531–3538`:
```dart
// Google Images search — only shown when no photo is active
if (!hasActive && refFuture != null) ...[
  // ...
  onPressed: () => _onSearchGoogle(data),
  label: Text('Google Images'),
```

Real `my_collection_screen.dart:4391–4394`:
```dart
final uri = Uri.parse('https://www.google.com/search?tbm=isch&q=$query');
if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
```

The same file at 5560–5639 still renders “Similar in Reference Library” and “Tap to expand * Kaggle reference datasets.” Additional Kaggle text/fallback remains at `microscope_scan_screen.dart:1335` and `ref_image_widget.dart:47`. The plan has no removal specification or regression tests.

### C. Actual JSON contradicts the claimed closed image perimeter

The real dev JSON has exactly 3,202 records, **zero `cpgRetail` keys**, and **167 external primary-image URLs**: 155 `upload.wikimedia.org`, 10 `thumb.wikimedia.org`, 1 `images.metmuseum.org`, and 1 `numismatics.org`.

Actual card code, origin/dev lines 1105–1109:
```dart
imgMap != null && imgMap['url'] != null
  ? Image.network(
      imgMap['url'] as String,
      fit: BoxFit.contain,
      errorBuilder: (c, e, s) => _buildPlaceholder(),
    )
```

No migration or pre-fetch allowlist guard is specified for those 167 URLs. The plan instead cites nonexistent `primary_image_url`; actual data uses `primary_image` / `type_image` maps. The claimed SVG is also not what the real `_buildPlaceholder()` renders (“No photo yet”). The plan cites `firebase.json:275–276` as Content-Security-Policy; those lines are actually `Strict-Transport-Security`. The real CSP begins at 283–284 and excludes the external image hosts, so these URLs fail rather than becoming allowed sources.

### D. Branch integration remains ambiguous

The catalog screen does not exist in p7-v8.9. Its `main.dart:119–148` known-path list lacks `/catalog` and sends unknown paths to `NotFoundScreen`. Origin/dev has the catalog screen and `/catalog` + `/catalog/**` Hosting rewrites. The plan allows dev “or active feature branch p7-v8.9” without specifying how b0b05808 is integrated into p7 while preserving newer work.

## 3. Scoring rubric

| Dimension | Score |
|---|---:|
| Correct rollback and execution locks | 20/20 |
| Real loader / retail implementation | 8/20 |
| Image schema / no-hotlink implementation | 6/15 |
| Mintage and preserved catalog fixes | 15/15 |
| Real Hosting spend readiness | 8/10 |
| B05N-14 / B05N-15 tracker coverage | 0/10 |
| Branch integration / launch verification | 7/10 |
| **Total** | **64/100 FAIL** |

## 4. Blocking must-fixes for next revision

1. Bind retail precedence directly to `_CatalogCard.build`; define the sourced JSON migration and exact fallback. Add positive/zero/missing/string-price and pending-flag tests. Never invent prices.
2. Specify fail-closed migration/guard for all 167 external primary URLs using the real `primary_image` / `type_image` schema. Reject external URLs before any fetch; use verified internal images or the real placeholder. Remove the `primary_image_url` assumption.
3. Implement B05N-14 same type AND series matching in both library and Greysheet paths, including unknown-series fail-closed behavior and 1958 Washington versus 1999 NJ regression tests.
4. Implement B05N-15 removal of Google Images and all Kaggle reference UI/fallback paths, including the external search callback. Add tests that no off-site photo action remains.
5. Turn the $20 alert into a verified pre-launch runbook: provision and test the alert, assign one accountable human and backup, and document monitoring and shutoff verification. Until then label it unverified, not an established hard cap.
6. Specify the exact dev-b0b05808 → p7-v8.9 integration. Preserve the now-correct rollback and proposed mintage deletion.

## 5. PII and locks

No AJ PII or credentials in the reviewed plan/evidence. No code executed or deployed. origin/main remains 9f04550a; Stripe OFF. No Firestore writes/rules. External messages: none.
