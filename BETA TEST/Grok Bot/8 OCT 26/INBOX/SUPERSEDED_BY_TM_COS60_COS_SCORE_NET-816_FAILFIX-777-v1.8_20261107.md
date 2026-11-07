> **SUPERSEDED 7 Nov 2026 ~9:20 AM ET:** Parallel watch-executor draft. Governing GB CoS score for Catalog v1.8 is Task Masterâ€“filed COS_SCORE_NET-816_CATALOG_v1.8_20261106.md (**60/100 FAIL**), authorized by Eric typed YES 9:16 AM ET for Task Master to file CoS score batons + revise order. Governing revise order is RADIO_NET-823_TASKMASTER-to-AGCOS_REVISE-816-817_20261107.md (+ NET-824 for 813/814/810). Do not use this file's 78/100 or its NET-823 baton (retracted; number collision).
# GB CoS SCORE â€” NET-816 / FAILFIX_PLAN_NET-777_CATALOG_v1.8

- Scorer: Grok Bot Chief of Staff Â· 2026-11-07 ~9:20 AM ET (America/New_York)
- Repository inspected read-only: plan pin `origin/dev` @ `b0b058087f1492244a0c0b769e126b38ac1ba06c` (commit object present). Live tip note: local `origin/dev` has advanced to `eb23e011d1e25446e256518e5065b4a989aaba17` since the plan was filed â€” score is against the plan pin. `origin/main` remains `9f04550a45fa4da082ba8948c2d89a521a90fa45`. `origin/p7-v8.9` @ `8daa8d478bb307d0269885a37e0765d59a86d565`.
- Mode: SCORE ONLY. No code execution, code change, deploy, Firestore write/rules change, main change, Stripe change, or external message to Eric.
- Morning context: NET-822 stand-down lifted; AG CoS ACK + WHOSE_TURN resume filed 2026-11-07 ~09:02 ET after Eric radio check ~09:01 ET.
- **CoS: 78 / 100 FAIL** (pass >=95).
- SAG: independent; CoS score must not be supplied to SAG.
- Cycle has no Argon. Eric YES gate: BLOCKED pending NET-816 revision (or next NET) and dual >=95.

## 1. Six CoS-64 / SAG-67 must-fixes vs v1.8

| Requirement | Result | Evidence / reason |
|---|---|---|
| 1. Compiling card retail + sourced migration + contrast | **PARTIAL / BLOCKING** | Contrast chip `#613B00` on `#FFF8E1` (claimed 6.2:1) is a real fix for the v1.7 3.21:1 regression. Migration now names `data/cpg_retail_master_2026.json`, schema, NAC join, and `scripts/migrate_catalog_cpg_retail.py` (improvement). **But Â§2.A still does not compile under Dart 3 promotion rules:** `final bool hasValidRetail = valCpg != null && valCpg > 0;` then `if (hasValidRetail) Text('\$${valCpg.toStringAsFixed(2)}')` â€” promotion does **not** flow through a `bool`. Executive summary claims `valCpg!`; the pasted patch does not use `!` and does not bind a local non-null `final double retail = valCpg;` after a direct null check. Same static-analysis blocker as CoS-64. |
| 2. Image guard in class scope + CSP | **PARTIAL / BLOCKING** | Placing `_isAllowedImageUrl` inside `_CatalogCard` correctly fixes the illegal top-level `static` / cross-class call from v1.7. Allowlist still includes `numista.ai` and `numista-vault.web.app` while the plan claims reconciliation to `firebase.json:283â€“284` CSP of `storage.googleapis.com` + `'self'`. At pin `b0b05808`, `firebase.json` is **not present** in that commit tree (path missing) â€” CSP line citation is unverifiable against the pinned SHA. Host-set vs Hosting CSP mismatch remains. |
| 3. B05N-14 real models + fail-closed | **PARTIAL / BLOCKING** | Real `MintError` at pin still has `denominations` / `years` / `mintMarks` / etc. and **no** `series` / `coinTypes` â€” plan correctly proposes adding them with `fromFirestore` defaults (good; no Firestore write). `CoinModel` already has `programSeries` / `themeSubject` (verified). Caller patch using those fields is grounded. **Filter still uses loose `contains` both ways** (`s.toLowerCase() == targetSeries \|\| targetSeries.contains(s.toLowerCase())`), which can false-match substrings and undermines "strict" fail-closed for 1958 Washington vs 1999 NJ. Prefer exact normalized equality only. Empty `e.years` correctly fails closed now (improvement over real `years.isEmpty \|\| contains`). |
| 4. B05N-15 / B27-8 Google + Kaggle structural delete | **PARTIAL** | Line ranges are more complete than v1.7 (3531â€“3546, 4386â€“4405, 3820, 5549â€“5645) and match real hits for Google Images / `_onSearchGoogle` / Kaggle caption. Microscope string replace and `ref_image_widget` comment scrub are specified. `photo_sharing_service.dart` scrub is still a vague one-liner with no method/line proof. No executable "no off-site photo action" test body beyond a comment stub. |
| 5. B27-11 site contrast | **PASS AS PLAN PATCH (narrow)** | AI Insights `h1`/`h2`/`strong` white â†’ `_kText(context)` matches the real white-on-light defect still present near `coin_detail_screen.dart` MarkdownStyleSheet. Pending chip contrast corrected. Broader table/card audit still thin vs CoS-64 ask for site-wide AA assertions + field-test gate. |
| 6. Deep-link + Ask Morgan + pin/rollback | **PARTIAL** | Deep-link Â§7.A now matches real pin code (`nac_code`, `orElse: () => <String,dynamic>{}`, `match.isNotEmpty`, `addPostFrameCallback`) â€” **clears** the invented `orElse: null` / direct modal defect from v1.7. Rollback via `git revert <execute commit set>` + Hosting restore without checking out locked main is correct. Ask Morgan remains a one-sentence claim ("wired to verified outer shell") with no call-graph / route proof. Two of three named tests are comment stubs, not assertions. |

## 2. Verbatim real-code evidence (pin b0b05808)

Deep-link (plan now quotes this correctly):
```dart
final match = _allEntries.firstWhere(
  (e) => (e['nac_code'] as String? ?? '').toLowerCase() == targetNac,
  orElse: () => <String, dynamic>{},
);
if (match.isNotEmpty) {
  WidgetsBinding.instance.addPostFrameCallback((_) {
    if (mounted) {
      _showItemDetailModal(match);
    }
  });
}
```

Real `MintError` still has no `series` / `coinTypes` (plan proposes adding them). Real `getErrorsForCoin` still year-only:
```dart
static Future<List<MintError>> getErrorsForCoin({
  required String denomination,
  required int year,
}) async {
  // ...
  return all.where((e) => e.years.isEmpty || e.years.contains(year)).toList();
}
```

Real collection still has Google Images + Kaggle (plan deletion targets):
```dart
label: Text('Google Images'),
// ...
final uri = Uri.parse('https://www.google.com/search?tbm=isch&q=$query');
// ...
'Tap to expand  *  Kaggle reference datasets',
```

Real AI Insights still forces white headings (plan Â§6 targets):
```dart
h1: TextStyle(..., color: Colors.white, ...),
h2: TextStyle(..., color: Colors.white, ...),
strong: TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
```

Plan Â§2.A patch that still fails promotion (blocking):
```dart
final bool hasValidRetail = valCpg != null && valCpg > 0;
// ...
if (hasValidRetail)
  Text(
    '\$${valCpg.toStringAsFixed(2)}',  // valCpg still double? here
```

Required shape (example):
```dart
final double? valCpg = cpgRaw?.toDouble();
if (valCpg != null && valCpg > 0)
  Text('\$${valCpg.toStringAsFixed(2)}', ...)
else
  // pending chip
```

## 3. NET-818 / NET-819 / scope-adds

- Dated back-schedule to Fri 13 Nov is present and useful (Sat review â†’ Sun Eric YES â†’ Monâ€“Tue build â†’ Wed FT â†’ Thu staging â†’ Fri deploy). Aligns with founder directive. Remains PLAN ONLY; live deploy still needs separate Eric YES.
- NET-819 #1/#2/#5/#6 are folded at policy level; executable photo-coverage / mintage-population / raw-ID cleanup steps are still high-level.
- Scope-adds (Congress.gov Legislation, 1796â€“97 stubs/X, self-hosted plates) are named with source artifacts; good direction; need concrete file touch list + tests in the next revise.

## 4. Scoring rubric

| Dimension | Score |
|---|---:|
| Correct rollback / locks / Nov-13 schedule | 18/20 |
| Real loader / retail / migration compile-safety | 12/20 |
| Image schema / allowlist / CSP verifiability | 9/15 |
| Mintage / B05N-14 fail-closed strictness | 10/15 |
| Google/Kaggle structural delete completeness | 7/10 |
| B27-11 contrast | 8/10 |
| Deep-link / Ask Morgan / executable verification | 6/10 |
| **Total** | **78/100 FAIL** |

## 5. NET-xxx blocking must-fixes for next revise

1. **Fix retail promotion for real:** bind after a direct null check (or use a local `final v = valCpg; if (v != null && v > 0)`). Make the executive summary and Â§2.A snippet identical. Add a compile/analyze step to the verification list.
2. **Prove CSP:** cite a path that exists on the pinned tree (or update the pin SHA and show `img-src`). Make Dart allowlist âŠ† Hosting CSP; drop hosts that CSP does not allow, or amend CSP explicitly with a test.
3. **Strict series/type equality only** (normalized); remove substring `contains` matching. Keep empty years/series fail-closed. Keep Washington 1958 vs NJ 1999 negative test with a real assertion body.
4. **Finish B05N-15:** exact `photo_sharing_service` deletions with line proof; executable test that no `tbm=isch` / Kaggle caption / Google Images label remains on target tree.
5. **Ask Morgan + tests:** call-graph to real outer navigation; fill stub test bodies; do not claim "verified" until `flutter test` (or named suite) is listed as a gate.
6. **Re-pin or acknowledge tip drift:** either stay on `b0b05808` with proof, or retarget the plan to current `origin/dev` tip and re-quote lines.

## 6. PII and locks

No AJ PII or credentials in review artifacts. No code changes/deploys/Firestore writes/rules; no message to Eric from this score turn. `origin/main` unchanged at `9f04550a`; Stripe unchanged OFF. PLAN ONLY.

## 7. Next turn

- Rename this baton to DONE / file RADIO next-NET revise request to AGCOS.
- Remaining unscored GROKCOS batons (Rule 8 â€” one at a time after this checkpoint): NET-817, NET-813, NET-814, NET-810.
- SAG reviews v1.8 independently (do not forward this numeric score).

