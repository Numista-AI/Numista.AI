# PLAN — NET-816 Catalog Chunk 1 Fail-Fix A1/A2 (AG CoS v5)
Filed: 2026-11-10 13:50 EST by AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`).
Target Track: NET-816 Catalog Chunk 1 v2.2 Fail-Fix (A1 Blocker & A2 Major).
In response to: `RADIO_NET-880_STALL_GROKCOS-to-AGCOS-V5_NET-816-A1A2-FAILFIX-PLAN_20261110-1342.md`
Status: **STRICT PLAN ONLY — NO CODE, NO DEPLOYS, NO MERGES BEFORE GATED APPROVAL (CoS 95 + SAG 95 + Eric typed YES)**.

---

## 1. Problem Definition & Root Cause Analysis

### A1 BLOCKER: Missing `/catalog` Firebase Hosting Rewrites
* **Location:** `numista_mobile/firebase.json` lines 49–115 (`hosting.rewrites`).
* **Symptom:** Direct browser requests or deep-links to `/catalog` or `/catalog/**` (e.g. `https://p7-gate--numista-vault.web.app/catalog` or `https://numista.ai/catalog`) return HTTP 404 from Firebase Hosting because Firebase Hosting does not rewrite `/catalog` to `/index.html` (unlike `/about`, `/pricing`, `/login`, etc.).
* **Root Cause:** When the catalog browse route was added to Flutter web routes, corresponding static route rewrites were omitted from `firebase.json`.

### A2 MAJOR: 90% Silver Half Dime Melt Value Uses Morgan Dollar Weight (~21.4× Inflated)
* **Location:** `numista_mobile/lib/services/melt_value_service.dart` lines 11–17, 190, 230–238.
* **Symptom:** A 90% silver Half Dime (e.g. Seated Liberty Half Dime, face value $0.05) computes silver melt value using 0.77344 troy oz pure Ag (the Morgan dollar weight) rather than the half dime specification (~0.03617 troy oz pure Ag). On collection dashboards, silver melt value is overvalued by ~21.4× (~10× to 20× inflation).
* **Root Cause:**
  1. In `_ag90` table (lines 11–17), keys are `'dime'`, `'quarter'`, `'half'`, `'half dollar'`, `'dollar'`. There is no key for `'half dime'`.
  2. In `_matchDenom` (lines 230–238), face value $0.05 is checked via:
     ```dart
     if (fv == 0.05 && table.containsKey('nickel')) return table['nickel'];
     ```
     Because `_ag90` contains no `'nickel'` key, `_matchDenom(_ag90, denom)` returns `null`.
  3. In `compute()` (line 190):
     ```dart
     final oz = _matchDenom(_ag90, denom) ?? 0.77344;
     ```
     The `null` return triggers the fallback `?? 0.77344` (Morgan dollar weight).

---

## 2. Surgical Code Modification Specification (PLAN ONLY)

### File 1: `numista_mobile/firebase.json`
**Location:** Inside `hosting.rewrites` array (immediately following line 73 `/terms` rewrite):
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
* **Effect:** Direct HTTP GET requests to `/catalog` and `/catalog/<id>` serve `/index.html`, allowing the Flutter web client router to resolve the route.

---

### File 2: `numista_mobile/lib/services/melt_value_service.dart`

#### Change 2.1: Add `'half dime'` to `_ag90` table (lines 11–17)
```dart
  static const _ag90 = {
    'half dime':   0.03617,   // 1.25g × 90% = 1.125g Ag ÷ 31.1035 (exactly 0.07234 ÷ 2)
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

#### Change 2.3: Remove dangerous dollar fallback for sub-dollar coins (line 190)
In `compute()` silver section:
```dart
      if (combined.contains('90%') || combined.contains('morgan') || combined.contains('peace') || combined.contains('barber') || combined.contains('walking liberty') || combined.contains('standing liberty') || combined.contains('mercury') || combined.contains('half dime')) {
        final oz = _matchDenom(_ag90, denom) ?? (denom.contains('dollar') ? 0.77344 : 0.0);
        if (oz <= 0.0) return null;
        return ag * oz * count;
      }
```
* **Effect:** If denomination is unrecognized, it will NOT silently assign a 1-dollar Morgan melt weight to an unrecognized coin.

---

### File 3: `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart`
**Location:** Inside `main()` test group:
Add comprehensive unit test verifying:
1. `MeltValueService.compute(metalContent: 'Silver (90%)', denomination: 'Half Dime', spotPrices: {'Silver': 30.0})`:
   - Must equal `30.0 * 0.03617` (~$1.085).
   - Must NEVER equal `30.0 * 0.77344` ($23.20).
2. `MeltValueService.format(...)` returns accurate formatted string for half dimes.

---

## 3. Machine-Checkable Verification Gate
Upon receiving typed authorization to apply:
1. `cd numista_mobile`
2. `flutter test test/catalog_chunk1_face_value_and_card_test.dart` (Exit code 0).
3. `flutter analyze lib/services/melt_value_service.dart` (0 issues).
4. `python -c "import json; d = json.load(open('firebase.json')); assert any(r.get('source') == '/catalog' for r in d['hosting']['rewrites']); assert any(r.get('source') == '/catalog/**' for r in d['hosting']['rewrites']); print('firebase.json rewrites OK')"`

---

## 4. Invariant Protection & Gated Execution Order
1. **This document is PLAN ONLY.** No code will be written until CoS 95 + SAG 95 + Founder Eric typed `YES`.
2. **Preview Deploy Authorization:** The prior preview deploy authorization (`t2455s9467`) applied to commit `c547b7a0` only. Re-issuing preview deploy to `p7-gate` requires Eric's new scoped typed `YES` on the A1/A2-fixed commit.
3. **Standing Boundaries:** `origin/main` (`9f04550a`) strictly pinned; live hosting (`numista.ai`), Firestore, and Stripe live mode remain strictly **UNTOUCHED**.
