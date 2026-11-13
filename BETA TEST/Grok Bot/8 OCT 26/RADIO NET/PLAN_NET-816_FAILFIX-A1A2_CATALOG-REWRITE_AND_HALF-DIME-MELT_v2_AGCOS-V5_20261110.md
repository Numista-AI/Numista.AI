# PLAN (v2) — NET-816 Catalog Chunk 1 Fail-Fix A1/A2 (AG CoS v5)
Filed: 2026-11-10 14:55 EST by AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`).
Target Track: NET-816 Catalog Chunk 1 v2.2 Fail-Fix (A1 Blocker & A2 Major).
In response to: `BATON_NET-816_AGCOS-V5_REVISE_FAILFIX-A1A2_v1-to-v2_CoS79_20261110-1400.md` & `COS_SCORE_NET-816_FAILFIX-A1A2_v1_79_REVISE_20261110.md` (CoS Score 79/100 REVISE).
Attempt: Track attempt 1/10; AG CoS v5 attempt 2/4.
Status: **STRICT PLAN ONLY — NO CODE, NO DEPLOYS, NO MERGES BEFORE GATED APPROVAL (CoS 95 + SAG 95 + Eric scoped typed YES)**.

---

## 1. Executive Summary & Defect Closure Matrix

Plan v2 comprehensively addresses all six material deductions (D1–D6) identified in the designated CoS score of v1:

| Defect | Area | Description in v1 | Resolution in v2 (§ reference) |
|---|---|---|---|
| **D1** | Correctness | Line 201 generic silver fallback (`if (ag > 0) return ag * 0.77344 * count;`) inflated sub-dollar silver lacking "90%" text (14 dimes, 22 quarters, 62 halves, 28 89.24% pieces). | **Closed (§2.2 Change 2.4):** Generic silver block now checks `_matchDenom(_ag90, denom)` and strict dollar criteria. Sub-dollar silver gets correct denom oz; unmodeled silver returns `null`. Line 201 Morgan fallback removed. |
| **D2** | Correctness (regression) | Fallback keyed solely on `denom.contains('dollar')`, dropping Morgan/Peace coins with empty denom or denom `CC` (series `1$-Morgan dollar`). | **Closed (§2.2 Change 2.3 & 2.4):** Dollar fallback keyed on `fv == 1.00 || combined.contains('dollar') || combined.contains('morgan') || combined.contains('peace')`. Preserves all dollar variants. |
| **D3** | Execution: test coverage | Missing unit tests for removed fallback, kept dollar fallback, regression on standard denoms, and half dime variants. | **Closed (§2.3 & §3):** Added regression tests (a)–(d) to `catalog_chunk1_face_value_and_card_test.dart` covering all specified scenarios with exact float bounds. |
| **D4** | Execution: Field Tester | Missing bounded Field Tester check with explicit pass/fail criteria for preview. | **Closed (§4):** Added bounded 4-step Field Tester test suite (`/catalog`, `/catalog/<nac>`, `#/catalog`, and half dime collection dashboard melt value) with strict PASS/FAIL rules. |
| **D5** | Correctness: scope | Omitted explanation of `#/catalog` hash handling. | **Closed (§1.1 & §4):** Explained SPA client-side hash routing via root `/` rewrite (`index.html`) vs server-side path rewrites. Explicitly included in scope and Field Tester check. |
| **D6** | Execution: rollback & build identity | Base commit/branch unnamed, built SHA logging omitted, rollback steps undefined. | **Closed (§5 & §6):** Explicitly named base branch `p7-v8.9`, base commit `c547b7a0`, mandated logging built SHA in DONE report, and defined exact rollback procedures for both code and hosting channel. |

---

## 2. Root Cause Analysis & Technical Specifications

### 1.1 A1 BLOCKER: Missing `/catalog` Firebase Hosting Rewrites & `#/catalog` Architecture
* **Locations:** `numista_mobile/firebase.json` lines 49–133 (`hosting.rewrites`).
* **Symptom:** Direct browser HTTP requests to `/catalog` or `/catalog/**` (e.g. `https://numista-vault--p7-gate-<hash>.web.app/catalog` or `https://numista.ai/catalog`) return HTTP 404 from Firebase Hosting CDN.
* **Root Cause:** Firebase Hosting is configured for explicit static route rewrites rather than a blanket catch-all `**`. While `/about`, `/pricing`, `/login`, etc., are explicitly rewritten to `/index.html`, `/catalog` and `/catalog/**` were omitted.
* **`#/catalog` vs `/catalog` Architecture:**
  - In Single-Page Applications (SPAs), the browser **never** sends the fragment identifier (`#...`) across the wire to the web server. A request for `https://numista.ai/#/catalog` arrives at Firebase Hosting as an HTTP GET for path `/`.
  - Path `/` is already rewritten to `/index.html` by line 106–107 (`{"source": "/", "destination": "/index.html"}`).
  - Once `/index.html` is served, the Flutter web engine boots and resolves `#/catalog` via Flutter's client-side router (`main.dart` maps `catalog` to `CatalogBrowseScreen`).
  - However, path-based routing (`/catalog` and `/catalog/<nac>`) sends the literal path to Firebase Hosting, requiring explicit server-side rewrite rules. Adding explicit rewrites for `/catalog` and `/catalog/**` guarantees that both path URLs and hash URLs work seamlessly.

### 1.2 A2 MAJOR & D1/D2 DEFECTS: Sub-Dollar Silver & Half Dime Melt Value Inflation
* **Locations:** `numista_mobile/lib/services/melt_value_service.dart` lines 11–17 (`_ag90`), 189–202 (`compute()`), 230–238 (`_matchDenom`).
* **Root Causes:**
  1. `_ag90` table lacked `'half dime'`.
  2. `_matchDenom` only checked `'nickel'` for face value $0.05. Since `_ag90` has no `'nickel'`, `_matchDenom` returned `null`.
  3. In line 190, the fallback `?? 0.77344` forced all unrecognized 90% silver coins (including Half Dimes) to Morgan dollar weight.
  4. In line 201, `if (ag > 0) return ag * 0.77344 * count;` acted as an unconditional Morgan fallback for any coin containing "silver" without the "90%" keyword (inflating 14 "Silver" dimes, 22 "Silver" quarters, 62 "Silver" halves, 28 "89.24% Silver" pieces, and 5c/3c/10c silver coins by 4.3× to 10.7×).
  5. In v1 plan, replacing the fallback with `denom.contains('dollar')` created regression risk D2 on Morgan/Peace dollars where denomination is empty or "CC" with series "1$-Morgan dollar".

---

## 3. Surgical Code Modification Specification (PLAN ONLY)

### File 1: `numista_mobile/firebase.json`
**Location:** Inside `hosting.rewrites` array (immediately following line 72 `/terms` rewrite, preceding line 73 `/about`):
```json
      {
        "source": "/catalog",
        "destination": "/index.html"
      },
      {
        "source": "/catalog/**",
        "destination": "/index.html"
      },
```
* **Effect:** Direct HTTP GET requests to `/catalog` and deep links like `/catalog/<nac_code>` return HTTP 200 with `/index.html`, allowing Flutter web's router to display `CatalogBrowseScreen`. Hash URLs (`#/catalog`) continue to be served via `/` rewrite (lines 106–107).

---

### File 2: `numista_mobile/lib/services/melt_value_service.dart`

#### Change 2.1: Add `'half dime'` to `_ag90` table (lines 11–17)
```dart
  static const _ag90 = {
    'half dime':   0.03617,   // Nominal 1.25g (1853+ 1.24g) × 90% ÷ 31.1035
    'dime':        0.07234,   // 2.5g × 90% = 2.25g Ag ÷ 31.1035
    'quarter':     0.18084,   // 6.25g × 90% = 5.625g Ag ÷ 31.1035
    'half':        0.36169,   // 12.5g × 90% = 11.25g Ag ÷ 31.1035
    'half dollar': 0.36169,
    'dollar':      0.77344,   // Morgan / Peace: 26.73g × 90% ÷ 31.1035
  };
```

#### Change 2.2: Update `_matchDenom` for $0.05 face value (lines 230–238)
```dart
  static double? _matchDenom(Map<String, double> table, String rawDenom) {
    final fv = parseFaceValue(rawDenom);
    if (fv == 1.00 && table.containsKey('dollar')) return table['dollar'];
    if (fv == 0.50 && table.containsKey('half')) return table['half'];
    if (fv == 0.25 && table.containsKey('quarter')) return table['quarter'];
    if (fv == 0.10 && table.containsKey('dime')) return table['dime'];
    if (fv == 0.05) {
      if (table.containsKey('half dime')) return table['half dime'];
      if (table.containsKey('nickel')) return table['nickel'];
    }
    return null;
  }
```

#### Change 2.3: Fix 90% Silver Block & Preserve Robust Dollar Fallback (lines 189–192)
```dart
      if (combined.contains('90%') || combined.contains('half dime') || combined.contains('half-dime') || combined.contains('morgan') || combined.contains('peace') || combined.contains('barber') || combined.contains('walking liberty') || combined.contains('standing liberty') || combined.contains('mercury')) {
        final fv = parseFaceValue(denom);
        final isDollar = fv == 1.00 || combined.contains('dollar') || combined.contains('morgan') || combined.contains('peace');
        final oz = _matchDenom(_ag90, denom) ?? (isDollar ? 0.77344 : null);
        if (oz != null) return ag * oz * count;
        return null;
      }
```

#### Change 2.4: Close Generic Silver Morgan Inflation Fallback (lines 201–202)
Replace the dangerous `if (ag > 0) return ag * 0.77344 * count;` with denomination-aware lookup:
```dart
      if (ag > 0) {
        final fv = parseFaceValue(denom);
        final isDollar = fv == 1.00 || combined.contains('dollar') || combined.contains('morgan') || combined.contains('peace');
        final oz = _matchDenom(_ag90, denom) ?? (isDollar ? 0.77344 : null);
        if (oz != null) return ag * oz * count;
        return null;
      }
```
* **Effect & Truthful Behavior Statement:**
  1. Any sub-dollar silver coin without "90%" text (such as catalog rows marked "Silver" Dime, "Silver" Quarter, "Silver" Half Dollar, "89.24% Silver" pieces, or "Silver / Half dime") now correctly resolves to its proper denomination melt weight (0.07234, 0.18084, 0.36169, 0.03617 oz) instead of 0.77344 oz.
  2. Morgan and Peace dollars without "dollar" in the denomination (e.g. denomination "CC", empty denomination, or series "1$-Morgan dollar") continue to safely resolve to 0.77344 oz.
  3. Unmodeled or unrecognized silver tokens (e.g. "Twenty Cent", medals, non-legal-tender planchets) return `null` and will **NEVER** silently receive a Morgan dollar melt weight.

---

### File 3: `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart`
**Location:** Inside `main()`, group `'NET-816 Chunk 1 — MeltValueService.parseFaceValue (#1 & NET-837 #2/#4/#5)'`:
Add the following regression test cases (a)–(d) to close D3:
```dart
    test('NET-816 Fail-Fix A2 & D1-D3 regression: half dime, sub-dollar silver fallbacks, and Morgan dollars', () {
      const spot = <String, double>{'Gold': 3000.0, 'Silver': 30.0};

      // (a) Removed fallback: unlisted 90% sub-dollar returns null, NOT 0.77344
      final unlistedTwentyCent = MeltValueService.compute(
        metalContent: '90% Silver',
        denomination: 'Twenty Cent',
        spotPrices: spot,
      );
      expect(unlistedTwentyCent, isNull,
          reason: 'Unlisted sub-dollar silver must return null, never 0.77344');

      // (b) Dollar fallback preserved for Morgan/Peace without "dollar" in denomination
      final morganCC = MeltValueService.compute(
        metalContent: 'Silver',
        denomination: 'CC',
        programSeries: '1\$-Morgan dollar',
        spotPrices: spot,
      );
      expect(morganCC, closeTo(0.77344 * 30.0, 1e-4),
          reason: 'Morgan with denom CC must receive 0.77344 dollar melt');

      final morganNoDenom = MeltValueService.compute(
        metalContent: 'Silver',
        denomination: '',
        programSeries: 'Morgan',
        spotPrices: spot,
      );
      expect(morganNoDenom, closeTo(0.77344 * 30.0, 1e-4),
          reason: 'Morgan with empty denom must receive 0.77344 dollar melt');

      // (c) Standard denominations preserved unchanged:
      // 90% Dime (0.07234 oz -> $2.1702 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '90% Silver', denomination: 'Dime', spotPrices: spot),
        closeTo(0.07234 * 30.0, 1e-4),
      );
      // 90% Quarter (0.18084 oz -> $5.4252 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '90% Silver', denomination: 'Quarter', spotPrices: spot),
        closeTo(0.18084 * 30.0, 1e-4),
      );
      // 90% Half Dollar (0.36169 oz -> $10.8507 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '90% Silver', denomination: 'Half dollar', spotPrices: spot),
        closeTo(0.36169 * 30.0, 1e-4),
      );
      // 90% Dollar (0.77344 oz -> $23.2032 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '90% Silver', denomination: 'Dollar', spotPrices: spot),
        closeTo(0.77344 * 30.0, 1e-4),
      );
      // 40% Half Dollar (0.14792 oz -> $4.4376 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '40% Silver', denomination: 'Half dollar', spotPrices: spot),
        closeTo(0.14792 * 30.0, 1e-4),
      );
      // 35% War Nickel (0.05626 oz -> $1.6878 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '35% Silver', denomination: 'Nickel', spotPrices: spot),
        closeTo(0.05626 * 30.0, 1e-4),
      );

      // (d) Half dime variants compute to 0.03617 oz * spot (~$1.0851 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: 'Silver (90%)', denomination: 'Half Dime', spotPrices: spot),
        closeTo(0.03617 * 30.0, 1e-4),
        reason: 'Silver (90%) Half Dime must equal 0.03617 oz',
      );
      expect(
        MeltValueService.compute(metalContent: 'Silver', denomination: 'Half dime', spotPrices: spot),
        closeTo(0.03617 * 30.0, 1e-4),
        reason: 'Generic "Silver" Half dime must equal 0.03617 oz',
      );
      expect(
        MeltValueService.compute(metalContent: '90% Silver', denomination: 'Half-dime', spotPrices: spot),
        closeTo(0.03617 * 30.0, 1e-4),
        reason: '"90% Silver" Half-dime must equal 0.03617 oz',
      );
      expect(
        MeltValueService.format(metalContent: '90% Silver', denomination: 'Half Dime', spotPrices: spot),
        equals('\$1.09'),
        reason: 'Formatted melt value string at $30/oz silver spot must round to $1.09',
      );
    });
```

---

## 4. Bounded Field Tester Check (p7-gate Preview) (D4 Closure)

Following build and deploy to the preview channel `p7-gate`, the Field Tester must execute the following 4 bounded checks with explicit PASS/FAIL rules:

| Check # | Target URL / Flow | Test Procedure | PASS Criteria | FAIL Criteria |
|---|---|---|---|---|
| **FT-1** | Direct GET `/catalog` | Open `https://numista-vault--p7-gate-<hash>.web.app/catalog` in a clean browser session (or curl/HTTP GET). | HTTP 200 returned. Page loads Flutter SPA, displays "Public Coin Catalog" header, search input field, type-photo cards, and face value chips. | HTTP 404, blank page, or Firebase Hosting "Page Not Found" screen. |
| **FT-2** | Direct GET `/catalog/<nac>` | Open `https://numista-vault--p7-gate-<hash>.web.app/catalog/1842-liberty-seated-dollar` (or any valid catalog item path). | HTTP 200 returned. Renders specific coin card or catalog item view. Zero 404 errors in browser network panel. | HTTP 404, infinite spinner, or router exception screen. |
| **FT-3** | Direct GET `#/catalog` | Open `https://numista-vault--p7-gate-<hash>.web.app/#/catalog` in a clean browser session. | HTTP 200 returned (via `/` rewrite). Browser URL loads `CatalogBrowseScreen` without redirection loop or console errors. | HTTP 404, crash, or redirection failure. |
| **FT-4** | Half Dime Collection Dashboard Melt Value | Navigate to user collection containing a 90% silver Half Dime (e.g. 1853 Seated Liberty Half Dime) with silver spot at ~$30.00/oz. | Melt value card/chip displays approximately **$1.09** (`0.03617 oz * spot`). | Melt value displays **$23.20** (Morgan dollar weight 0.77344 oz), $0.00, or "N/A". |

---

## 5. Machine-Checkable Verification Gate

Upon receiving gated authorization (CoS 95 + SAG 95 + Eric scoped typed YES):
1. `cd numista_mobile`
2. `flutter test test/catalog_chunk1_face_value_and_card_test.dart` (Must exit code 0; all existing and new tests pass).
3. `flutter analyze lib/services/melt_value_service.dart test/catalog_chunk1_face_value_and_card_test.dart` (0 issues).
4. `python -c "import json; d = json.load(open('firebase.json')); rewrites = [r.get('source') for r in d['hosting']['rewrites']]; assert '/catalog' in rewrites, 'missing /catalog'; assert '/catalog/**' in rewrites, 'missing /catalog/**'; print('firebase.json rewrites VERIFIED')"` (Exit code 0).

---

## 6. Base Commit, Build Identity & Rollback Procedures (D6 Closure)

### 6.1 Base Commit & Branch Identity
* **Base Branch:** `p7-v8.9`
* **Base Source Commit:** `c547b7a0` (Note: git HEAD `999daf14` is ahead of `c547b7a0` exclusively by documentation/governance artifacts in `BETA TEST/` and `1 NUMISTA.AI/`; the working tree code files in `numista_mobile/` are clean and identical to `c547b7a0`).
* **Built Commit Identity Requirement:**
  - Upon applying the surgical changes to the 3 target files, a new git commit will be created on `p7-v8.9`:
    `git commit -m "fix(catalog): add /catalog rewrites and correct half-dime melt value (NET-816 A1/A2)"`
  - The exact resulting commit SHA (e.g. `<built_commit_sha>`) **MUST** be explicitly recorded in the `DONE_BATON_...` report.
  - Preview deploy to channel `p7-gate` will only proceed once Founder Eric provides a new scoped typed `YES` explicitly naming that built commit SHA.

### 6.2 Rollback Procedures
1. **Source Code Rollback:**
   - If unit tests or build verification fails, revert working tree files immediately:
     `git checkout c547b7a0 -- numista_mobile/firebase.json numista_mobile/lib/services/melt_value_service.dart numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart`
   - If already committed:
     `git revert <built_commit_sha> -m "revert: NET-816 fail-fix A1/A2"` and push to `origin/p7-v8.9`.
2. **Hosting Channel `p7-gate` Rollback:**
   - If the preview deployment fails any step of the Field Tester check:
     Option A (Re-deploy prior build): Rebuild from commit `c547b7a0` and re-deploy:
     `cd numista_mobile && flutter build web --release && firebase hosting:channel:deploy p7-gate --only hosting`
     Option B (Teardown preview channel): Delete the preview channel cleanly:
     `firebase hosting:channel:delete p7-gate -f`

---

## 7. Invariant Protection & Scope Boundaries

1. **Strict PLAN ONLY:** Zero code files modified, zero git commits created, zero deploys executed prior to plan gate passage (CoS 95 + SAG 95 + Eric scoped typed YES).
2. **Pinned Repository Roots:** `origin/main` (`9f04550a45fa4da082ba8948c2d89a521a90fa45`) remains strictly pinned. Zero pushes or merges to `main`.
3. **Protected Infrastructure:** Live hosting (`numista.ai`), Cloud Firestore, and Stripe live mode remain strictly **OFF / UNTOUCHED**.
4. **Scope Isolation:** Changes are strictly confined to the 3 named files (`firebase.json`, `melt_value_service.dart`, `catalog_chunk1_face_value_and_card_test.dart`). All other components remain untouched.
