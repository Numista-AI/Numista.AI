# PLAN (v3) — NET-816 Catalog Chunk 1 Fail-Fix A1/A2 (AG CoS v5)
Filed: 2026-11-10 15:20 EST by AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`).
Target Track: NET-816 Catalog Chunk 1 v2.2 Fail-Fix (A1 Blocker & A2 Major).
In response to: `BATON_NET-816_AGCOS-V5_REVISE_FAILFIX-A1A2_v2-to-v3_CoS87_20261110-1457.md` & `COS_SCORE_NET-816_FAILFIX-A1A2_v2_87_REVISE_20261110.md` (CoS Score 87/100 REVISE).
Attempt: **Track attempt 3 of 10; AG CoS v5 attempt 3 of 4** (official record corrected from v2).
Status: **STRICT PLAN ONLY — NO CODE, NO DEPLOYS, NO MERGES BEFORE GATED APPROVAL (CoS 95 + SAG 95 + Eric scoped typed YES)**.

---

## 1. Executive Summary & Defect Closure Matrix (v1 D1–D6 & v2 N1–N5)

Plan v3 builds upon the verified closures of D1, D2, and D3 from v2, and systematically closes all material deductions (N1–N5) identified in CoS Score 87:

| Defect | Area | Description in v2 | Resolution in v3 (§ reference) |
|---|---|---|---|
| **N1** | Correctness / Field Tester | False claim that `main.dart` routes `#/catalog` to catalog; `main.dart:155` checks `uri.path` only, while hash URLs have `uri.path == '/'` and route to home/login. | **Closed (§2.1 & §5):** Explicitly declare `#/catalog` out of scope for this fail-fix track with architectural explanation. Direct path routing (`/catalog` and `/catalog/<nac>`) is the canonical public catalog entry. FT-3 pass criteria aligned to verify HTTP 200 and clean front-door/home load without 404 or crash. |
| **N2** | Execution: tests | Unescaped `$` in test reason string (`$30` and `$1.09`) caused Dart compile error `missing_identifier`. | **Closed (§4 File 3):** Escaped all literal dollar signs (`\$30` and `\$1.09`). Syntax verified. |
| **N3** | Execution / permissions: rollback | Rollback Option A omitted `git checkout c547b7a0`; used invalid `git revert -m`; Option B channel deletion lacked authority rule; host execution omitted. | **Closed (§7.2):** Option A explicitly checks out `c547b7a0` before build; uses `git revert --no-edit <sha>` without `-m`; channel deletion explicitly prohibited without Eric's typed YES; stated that Firebase CLI commands run on host machine (EDS_Laptop). |
| **N4** | Correctness: new mis-map | Silver 5-cent fallback routed all 5-cent coins to half-dime weight (0.03617 oz), causing war nickels lacking "35%" text (e.g. `1942-P Jefferson Wartime Nickel`) to read 36% low. | **Closed (§4 Change 2.3, 2.4, 2.5):** Added wartime/war/nickel keyword detection for $0.05 silver coins routing them to `_ag35` (0.05626 oz) before half-dime lookup. Added test case for `'Silver Alloy'`, `'5 cents'`, series `'Jefferson Wartime Nickel'`. |
| **N5** | Execution: Field Tester | FT-2 used synthetic non-existent slug instead of real NAC code; FT-4 lacked test account specification and clashed with "Firestore UNTOUCHED". | **Closed (§5 FT-2 & FT-4):** FT-2 uses real catalog NAC code `NAC1.CN.US.H10C.SEATEDLIBE.1853.XX.BASE.2`. FT-4 specifies read-only demo/fixture state (`/demo` or pre-seeded test fixtures) with zero live Firestore writes. |

---

## 2. Root Cause Analysis & Architectural Boundaries

### 2.1 A1 BLOCKER: Missing `/catalog` Firebase Hosting Rewrites & Scope Boundary on `#/catalog`
* **Locations:** `numista_mobile/firebase.json` lines 49–133 (`hosting.rewrites`), `numista_mobile/lib/main.dart` lines 113–181.
* **Root Cause & Server-Side Rewrites:**
  - Firebase Hosting uses explicit static route rewrites rather than a blanket catch-all `**`.
  - While `/about`, `/pricing`, `/login`, etc., are explicitly rewritten to `/index.html`, `/catalog` and `/catalog/**` were omitted.
  - Adding `/catalog` and `/catalog/**` pointing to `/index.html` ensures direct browser requests and deep links return HTTP 200 with the SPA bundle.
* **Client-Side Routing Architecture at `c547b7a0`:**
  - In `main.dart:115–118`, the entry-point route inspects `uri.path`.
  - Lines 154–181 check `if (normalizedPath == '/catalog' || path.startsWith('/catalog/'))` to launch `CatalogBrowseScreen`.
  - In single-page web apps, browsers never send the hash fragment (`#...`) to the server. A request for `https://numista.ai/#/catalog` arrives at Firebase Hosting with `path == '/'`, which rewrites to `/index.html`.
  - In `main.dart:113–114`, the codebase explicitly documents:
    `// Hash-fragment URLs (e.g. /#/claim?...) have uri.path == '/' — they pass through to the normal app flow correctly.`
  - Therefore, `/#/catalog` evaluates `uri.path == '/'`, skipping line 155 and falling through to the Front Door / Login / Home flow.
* **Scope Boundary (N1 Resolution):**
  - Canonical public catalog access for Numista.AI is **path-based** (`/catalog` and `/catalog/<nac>`).
  - Modifying `main.dart` to inspect `uri.fragment` is explicitly **OUT OF SCOPE** for this fail-fix track to strictly maintain the 3-file surgical scope (`firebase.json`, `melt_value_service.dart`, `catalog_chunk1_face_value_and_card_test.dart`) and avoid unintended side-effects on existing front-door hash routing.
  - Field Tester check FT-3 will validate that `/#/catalog` returns HTTP 200 and loads the normal front-door flow cleanly without a 404 or crash.

### 2.2 A2 MAJOR & N4: Sub-Dollar Silver, War Nickel, and Half Dime Melt Logic
* **Locations:** `numista_mobile/lib/services/melt_value_service.dart` lines 11–17 (`_ag90`), 24–26 (`_ag35`), 189–202 (`compute()`), 230–238 (`_matchDenom`).
* **Root Causes:**
  1. `_ag90` table lacked `'half dime'`.
  2. `_matchDenom` only checked `'nickel'` for face value $0.05.
  3. Fallback `?? 0.77344` forced all unrecognized 90% silver coins to Morgan dollar weight.
  4. Line 201 `if (ag > 0) return ag * 0.77344 * count;` acted as an unconditional Morgan fallback for any coin containing "silver" without the "90%" keyword.
  5. In v2 plan, routing generic silver $0.05 coins to half dime (0.03617 oz) inadvertently caused War Nickels lacking "35%" text (e.g. `1942-P Jefferson Wartime Nickel` with metal "Silver Alloy") to read 36% low (0.03617 oz vs 0.05626 oz).
* **Fix Strategy:**
  - Route $0.05 silver coins containing `nickel`, `war`, or `wartime` in the combined text to `_ag35` (0.05626 oz).
  - Route other $0.05 silver coins (half dimes) to `_ag90['half dime']` (0.03617 oz).
  - Sub-dollar silver dimes, quarters, and halves resolve to their exact standard weights.
  - Morgan/Peace dollars (even with empty denom or denom "CC" with series "1$-Morgan dollar") safely resolve to 0.77344 oz.
  - Unmodeled silver tokens return `null` and never receive a Morgan weight.

---

## 3. Scope of Modifications (Strictly 3 Files)

This fail-fix track is strictly confined to 3 files:
1. `numista_mobile/firebase.json` (Hosting rewrites for `/catalog` and `/catalog/**`)
2. `numista_mobile/lib/services/melt_value_service.dart` (Melt valuation corrections)
3. `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart` (Unit and regression tests)

Zero modifications to `main.dart`, backend services, or database schemas.

---

## 4. Surgical Code Modification Specification (PLAN ONLY)

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
* **Effect:** Direct HTTP GET requests to `/catalog` and deep links like `/catalog/<nac_code>` return HTTP 200 with `/index.html`, allowing `main.dart` to mount `CatalogBrowseScreen`.

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

#### Change 2.3: Update 35% War Nickel Detection (lines 197–200)
Expand detection keywords to include `wartime`:
```dart
      if (combined.contains('35%') || combined.contains('war nickel') || combined.contains('wartime')) {
        final oz = _matchDenom(_ag35, denom) ?? 0.05626;
        return ag * oz * count;
      }
```

#### Change 2.4: Fix 90% Silver Block & Preserve Robust Dollar Fallback (lines 189–192)
```dart
      if (combined.contains('90%') || combined.contains('half dime') || combined.contains('half-dime') || combined.contains('morgan') || combined.contains('peace') || combined.contains('barber') || combined.contains('walking liberty') || combined.contains('standing liberty') || combined.contains('mercury')) {
        final fv = parseFaceValue(denom);
        final isDollar = fv == 1.00 || combined.contains('dollar') || combined.contains('morgan') || combined.contains('peace');
        final oz = _matchDenom(_ag90, denom) ?? (isDollar ? 0.77344 : null);
        if (oz != null) return ag * oz * count;
        return null;
      }
```

#### Change 2.5: Close Generic Silver Morgan Inflation Fallback (lines 201–202)
Replace `if (ag > 0) return ag * 0.77344 * count;` with denomination-aware lookup routing war nickels and standard denominations correctly:
```dart
      if (ag > 0) {
        final fv = parseFaceValue(denom);
        // N4: Route 5-cent wartime/war nickels without "35%" text to 35% war nickel weight
        if (fv == 0.05 && (combined.contains('nickel') || combined.contains('war') || combined.contains('wartime'))) {
          return ag * 0.05626 * count;
        }
        final isDollar = fv == 1.00 || combined.contains('dollar') || combined.contains('morgan') || combined.contains('peace');
        final oz = _matchDenom(_ag90, denom) ?? (isDollar ? 0.77344 : null);
        if (oz != null) return ag * oz * count;
        return null;
      }
```

---

### File 3: `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart`
**Location:** Inside `main()`, group `'NET-816 Chunk 1 — MeltValueService.parseFaceValue (#1 & NET-837 #2/#4/#5)'`:
Add the following comprehensive regression test suite (with all literal dollar signs cleanly escaped to ensure zero compile errors):
```dart
    test('NET-816 Fail-Fix A2 & D1-D3/N2/N4 regression: half dime, war nickel, sub-dollar silver, and Morgan dollars', () {
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

      // (d) N4: Wartime nickel with "Silver Alloy" and "Wartime Nickel" series (lacking "35%")
      expect(
        MeltValueService.compute(
          metalContent: 'Silver Alloy',
          denomination: '5 cents',
          programSeries: 'Jefferson Wartime Nickel',
          spotPrices: spot,
        ),
        closeTo(0.05626 * 30.0, 1e-4),
        reason: 'Jefferson Wartime Nickel in Silver Alloy must receive 0.05626 oz melt',
      );

      // (e) Half dime variants compute to 0.03617 oz * spot (~$1.0851 at $30/oz)
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
        equals(r'$1.09'),
        reason: 'Formatted melt value string at \$30/oz silver spot must round to \$1.09',
      );
    });
```

---

## 5. Bounded Field Tester Check (p7-gate Preview) (N1 & N5 Closure)

Following build and deploy to the preview channel `p7-gate`, the Field Tester will execute the following 4 bounded checks with explicit PASS/FAIL rules:

| Check # | Target URL / Flow | Test Procedure | PASS Criteria | FAIL Criteria |
|---|---|---|---|---|
| **FT-1** | Direct GET `/catalog` | Open `https://numista-vault--p7-gate-<hash>.web.app/catalog` in a clean browser session. | HTTP 200 returned. Page mounts Flutter SPA, displays "Public Coin Catalog" header, search input, type-photo cards, and face value chips. | HTTP 404, blank page, or Firebase Hosting "Page Not Found". |
| **FT-2** | Direct GET `/catalog/<nac>` | Open `https://numista-vault--p7-gate-<hash>.web.app/catalog/NAC1.CN.US.H10C.SEATEDLIBE.1853.XX.BASE.2` (Real catalog NAC code for 1853 Seated Liberty Half Dime). | HTTP 200 returned. Deep link mounts directly into catalog item view for the 1853 Half Dime. Zero 404 errors. | HTTP 404, infinite spinner, or router exception screen. |
| **FT-3** | Direct GET `#/catalog` | Open `https://numista-vault--p7-gate-<hash>.web.app/#/catalog` in a clean browser session. | HTTP 200 returned (via `/` rewrite). App mounts cleanly into front-door / login / home flow (as documented in `main.dart:113-114`) without crash or 404. | HTTP 404, blank screen, crash, or redirection loop. |
| **FT-4** | Half Dime Dashboard Melt Value | Inspect collection dashboard for a 90% silver Half Dime (e.g. 1853 Seated Liberty Half Dime) at ~$30.00/oz silver spot. Uses read-only pre-seeded test fixtures or client-side demo mode (`/demo`). **Zero live Firestore writes.** | Melt value displays approximately **$1.09** (`0.03617 oz * spot`). | Melt value displays **$23.20** (Morgan dollar weight), $0.00, or "N/A". |

---

## 6. Machine-Checkable Verification Gate

Upon receiving gated authorization (CoS 95 + SAG 95 + Eric scoped typed YES):
1. `cd numista_mobile`
2. `flutter test test/catalog_chunk1_face_value_and_card_test.dart` (Must exit code 0; all existing and new tests pass).
3. `flutter analyze lib/services/melt_value_service.dart test/catalog_chunk1_face_value_and_card_test.dart` (Must exit code 0 with 0 issues).
4. `python -c "import json; d = json.load(open('firebase.json')); rewrites = [r.get('source') for r in d['hosting']['rewrites']]; assert '/catalog' in rewrites, 'missing /catalog'; assert '/catalog/**' in rewrites, 'missing /catalog/**'; print('firebase.json rewrites VERIFIED')"` (Must exit code 0).

---

## 7. Base Commit, Build Identity & Rollback Procedures (N3 Closure)

### 7.1 Base Commit & Branch Identity
* **Base Branch:** `p7-v8.9`
* **Base Source Commit:** `c547b7a0` (Working tree source files in `numista_mobile/` are clean and identical to `c547b7a0`).
* **Built Commit Identity Requirement:**
  - Upon applying the surgical changes, a git commit will be created on `p7-v8.9`:
    `git commit -m "fix(catalog): add /catalog rewrites and correct half-dime melt value (NET-816 A1/A2)"`
  - The exact resulting commit SHA **MUST** be explicitly recorded in the `DONE_BATON_...` report.
  - Preview deploy to channel `p7-gate` will only proceed once Founder Eric provides a new scoped typed `YES` explicitly naming that built commit SHA.

### 7.2 Rollback Procedures (N3 Resolution)
1. **Source Code Rollback:**
   - If unit tests fail before commit:
     `git checkout c547b7a0 -- numista_mobile/firebase.json numista_mobile/lib/services/melt_value_service.dart numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart`
   - If already committed:
     `git revert --no-edit <built_commit_sha>` and push to `origin/p7-v8.9`.
2. **Hosting Channel `p7-gate` Rollback:**
   - **Host Machine Requirement:** All Firebase deployment commands must be executed on the host machine (`EDS_Laptop`) where valid Firebase credentials exist.
   - **Rollback to Known-Good Build:**
     On `EDS_Laptop`:
     ```bash
     git checkout c547b7a0
     cd numista_mobile
     flutter build web --release
     firebase hosting:channel:deploy p7-gate --only hosting
     ```
     Record deployed commit `c547b7a0` in the audit log.
   - **Channel Teardown Boundary:** Deleting the preview channel (`firebase hosting:channel:delete p7-gate -f`) is **STRICTLY PROHIBITED** without explicit prior typed `YES` from Founder Eric.

---

## 8. Invariant Protection & Scope Boundaries

1. **Strict PLAN ONLY:** Zero code files modified, zero git commits created, zero deploys executed prior to plan gate passage (CoS 95 + SAG 95 + Eric scoped typed YES).
2. **Pinned Repository Roots:** `origin/main` (`9f04550a45fa4da082ba8948c2d89a521a90fa45`) remains strictly pinned. Zero pushes or merges to `main`.
3. **Protected Infrastructure:** Live hosting (`numista.ai`), Cloud Firestore, and Stripe live mode remain strictly **OFF / UNTOUCHED**.
4. **Scope Isolation:** Changes are strictly confined to the 3 named files.
