# GB CoS SCORE — NET-812 / FAILFIX_PLAN_NET-780b_CARDS_v1.4 + 780c_IMAGES_v1.4

- Scorer: Grok Bot Chief of Staff · 2026-11-05 ~8:00 PM ET (America/New_York)
- Repository inspected read-only: origin/p7-v8.9 @ a07cf9f231daff6fa1066978c3ad03d5bfe08529; origin/dev @ b0b058087f1492244a0c0b769e126b38ac1ba06c; origin/main @ 9f04550a45fa4da082ba8948c2d89a521a90fa45.
- Mode: SCORE ONLY. No app/repository code execution or code change; isolated Dart regex check only. No deploy, Firestore write/rules change, network lookup, main change, Stripe change, or external message.
- **CoS: 67 / 100 FAIL** (pass >=95).
- SAG: independent xAI API grok-4.7 review filed separately; CoS score not supplied to SAG.
- Cycle has no Argon. Eric YES gate: BLOCKED pending NET-817 revision and independent pass.

## 1. v1.3 must-fixes against actual code and proposed patches

| Check | Result | Real-code evidence / reason |
|---|---|---|
| Rollback to real pre-execute SHA | **FAIL / STALE** | v1.4 pins `4c97c7f0664d33862a5e0ed58f427edbdce27174`, but actual p7 HEAD is `a07cf9f231daff6fa1066978c3ad03d5bfe08529`. The pin is an ancestor 11 commits behind. Those are docs-only for lib/assets/firebase, but a whole execute-set revert back to the old pin still deletes intervening history. Record actual HEAD at execution and revert the execute set; use an old-file checkout only for a scoped pre-commit recovery of the actual pre-execute files, never as branch rollback. |
| Positive CDN retail overrides pending; no AI fallback | **PASS AS PROPOSED LOGIC** | Real defect is exactly line 3170 (`valueText == '—' || enrichment_status == 'pending'`) and real line 3023 falls back to AI value. Proposed `hasValidPrice = valCpg > 0` and `valueText = hasValidPrice ? fmt.format(valCpg) : ''` correctly remove both problems and retain non-null `_parseNumber` semantics. Tests still need to exist and run. |
| Nickel/cent regex | **PASS AS PROPOSED LOGIC** | Actual 2026-only branch uses trailing `\b` after non-word `¢` at lines 431–434. Proposed `(?<!\d)5¢` without trailing boundary handles `5¢` and blocks `15¢`; `\b5c\b` rejects `25c`. The cent correction is analogous. This is proposed, not executed. |
| 26EA year-from-text and canonical preservation | **PARTIAL / BLOCKING** | `extractSku` may infer `26EA`, but `resolveFromMap` separately recomputes year at real line 172 with only `_normYear(data['year'] ?? data['Year'])`. Later 2026 gates need that year. The proposed local `String year` fallback does not propagate to `resolveFromMap`. T-780b-1 therefore does not guarantee the claimed obverse/reverse resolution. `1776-2026` is only a note, not an implementation or test. |
| Real image API and full widget | **FAIL AS SUPPLIED PATCH** | The nonexistent `resolveReferenceAsset` is gone and `FutureBuilder<CoinImageResult>` uses the real method. However, the full replacement class ends at `}` after `build` and calls `_buildCoinImage` repeatedly without defining it. The real class supplies this method at 6443–6478; the proposed class omits it. A complete compilable class or explicit surgical insertion preserving the real method is required. |
| User photo precedence and allowlist | **PARTIAL / BLOCKING** | Correctly places user photos before canonical and adds real reference/uploads buckets, but accepts only the literal `/numista-uploads-studio-` prefix rather than a concrete verified user bucket/pattern. Other actual user paths (`/microscope/`, `/users/`, `/user_uploads/`) are recognized by the real guard but rejected by the new allowlist. Preserve real user images with an explicit authenticated path policy; do not invent wildcard matching. |
| $0 scope, census, no cloud writes | **CONTRADICTORY** | `docs/MISSING_IMAGES.csv` really has 3,202 data rows, and excluding bulk ingest/cloud writes is good. But the new build path calls `CoinImageService.fetchReferenceImages`, whose actual code performs Firestore reads and then loads GCS images. “Zero external API queries / zero external network calls” is false. Define the permitted read-only network boundary and no-write/no-spend test rather than denying required reads. |
| Actual tests | **FAIL / NOT SUPPLIED** | Existing canonical test is `test/services/canonical_mint_asset_service_test.dart`, not the plan’s `test/canonical_mint_asset_service_test.dart`. `collection_card_image_test.dart` and `my_collection_card_pricing_test.dart` do not exist. New tests may be proposed, but their test contents, mocks and assertions must be supplied and run before claiming verification. |

## 2. Verbatim real-code evidence

Actual `resolveFromMap` independently loses the year fallback:
```dart
final sku = extractSku(data);
// ...
final year = _normYear(data['year'] ?? data['Year']);
return resolve(
  sku: sku,
  title: primaryTitle,
  year: year,
  mintMark: mintMark,
  denomination: denom,
);
```

Actual 26EA resolution depends on the SKU switch and later year-gated logic. The proposed fallback changes only the local `year` in `extractSku`, not the later `resolveFromMap` input.

Actual `_CollectionCardImage` has the necessary method after `build`:
```dart
Widget _buildCoinImage(String url) {
  return Center(
    child: Container(
      // ...
      child: Image.network(
        url,
        fit: BoxFit.contain,
        errorBuilder: (context, error, stackTrace) => // placeholder
```

The plan’s complete `_CollectionCardImage` code ends without that method, so simply applying it causes an undefined-method build failure.

Actual `CoinImageService` is not a local-only resolver: its header says it looks up `coin_image_index` in Firestore, and lines 562–579 call `.collection(...).doc(...).get()`. This is compatible with read-only review and may be a legitimate app behavior, but it directly contradicts “zero external API queries/network calls.”

## 3. Related tracker and regression checks

- **B27-8 (+B05N-15): STILL OPEN / NOT COVERED.** Real p7 code still contains the Google Images button and `https://www.google.com/search?tbm=isch`, “Kaggle reference datasets” panel, microscope label, and ref-image/photo-sharing Kaggle paths. Neither v1.4 plan removes them. Required: complete removal, bounded terminal state, no off-site photo action, regression tests. This must be coordinated with NET-816, which also covers it; do not create conflicting implementations.
- **B27-11 (+B05N-12): STILL OPEN / NEW CARD REGRESSION.** Real `coin_detail_screen.dart` light `_kSurface` is white while h1/h2/strong are forced `Colors.white` at 2789–2792. Neither plan addresses this. Proposed pending text `#C9A227` over its alpha-gold background is approximately **2.24:1 on white** and **2.06:1 over #F5F5F0**. Positive 13px gold retail on white is also below normal-text AA. Require theme-aware dark gold/black text >=4.5:1 and automated plus Eric field-test contrast evidence.
- **B05N-7 / B27-5 uploaded image preservation:** conceptual user-first ordering is correct, but the supplied class omission and overly narrow accepted paths mean this is not a complete fix. Test real upload URLs and ensure canonical/fallback never steals a user photo.
- **B05N-8 / B27-5 valuation:** the primary-card AI-fallback and pending-status bug is correctly fixed as proposed. This does not establish CDN retail for the separate Cert Add/grade financial flow or prove no `$0.00` below face there; keep that scope explicit or include those real call paths.

## 4. NET-817 blocking must-fixes

1. Record current p7 HEAD at execution, not stale `4c97c7f0`; revert exactly the execute set without deleting intervening docs/work. Remove ambiguous old-SHA checkout language or tightly scope it to a pre-commit recovery.
2. Provide one canonical normalized year helper used by both `extractSku` and `resolveFromMap`/`resolve`. Test missing-year 26EA through the public `resolveFromMap`, including obverse/reverse, `1776-2026` preferring 2026, and no 2023 nickel becoming a 2026 commemorative.
3. Supply a complete compilable `_CollectionCardImage` including the real `_buildCoinImage`, or precise edits preserving it. Add concrete accepted user-upload paths and tests for user > canonical > own-origin > reference > placeholder, external-host rejection before fetch, and reference result allowlisting.
4. Reconcile the scope: reference lookup requires Firestore/network reads. State exactly which reads are permitted, with no writes/cloud mutations, timeouts/error fallback and zero unintended third-party image requests. Do not claim zero network.
5. Supply actual test files at correct paths with mocks/assertions, plus the required B27-8 removal coordination and B27-11 contrast fixes/tests. Verify both light and dark themes and real uploaded-photo/retail fixtures.

## 5. Scoring rubric

| Dimension | Score |
|---|---:|
| PII/redaction and standing locks | 19/20 |
| v1.3 must-fix closeout | 22/35 |
| Real API / implementability | 9/20 |
| Census, scope and no invention | 9/15 |
| Related tracker coverage and launch fit | 8/10 |
| **Total** | **67/100 FAIL** |

## 6. PII and locks

No AJ PII or credentials in this review. No code changes/deploys/Firestore writes/rules or external messages. origin/main unchanged at 9f04550a; Stripe unchanged OFF. SAG runs independently through xAI API grok-4.7 using plan text and real-code evidence only.