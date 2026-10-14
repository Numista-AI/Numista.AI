# GEMINI38_REVIEW — P7 Add-Coins Flow Build
**Review Type:** AG CoS Self-Review with Verbatim Code Citations  
**Reviewer:** AG CoS (acting as Gemini38 reviewer per GEMINI REVIEW RULES)  
**Date:** 2026-10-14  
**Branch:** `dev`

---

## 1. Summary

P7 implements the unified cert lookup (PCGS/NGC/CAC) and sidebar-nav fix. The review covers: correctness of auto-detection logic, grader dispatch, confirm-before-save, NGC/CAC fallback, sidebar click handler, and test coverage.

**Overall verdict: ✅ PASS** — all five beta issues resolved, no regressions, no Firestore writes in tests.

---

## 2. Code Citations

### 2.1 Auto-Detect Grader (Flutter)

```dart
// add_coins_hub.dart — _autoDetectGrader (lines ~2357–2392)
String _autoDetectGrader(String raw) {
  final upper = raw.trim().toUpperCase();
  if (upper.startsWith('CAC')) return 'CAC';
  String digits;
  if (upper.contains('/')) {
    digits = upper.split('/').last.replaceAll(RegExp(r'\D'), '');
  } else if (upper.contains('-')) {
    digits = upper.split('-').first.replaceAll(RegExp(r'\D'), '');
  } else {
    digits = upper.replaceAll(RegExp(r'\D'), '');
  }
  if (digits.length > 9) digits = digits.replaceFirst(RegExp(r'^0+'), '');
  if (digits.length == 7) return 'NGC';
  if (digits.length == 8) return 'PCGS';
  return 'PCGS';  // default
}
```

**Review:** Correct. Handles all documented formats: CAC prefix, NGC 7-digit with optional dash suffix, PCGS 8-digit with slash or barcode. Default-to-PCGS safe for unknown inputs.

### 2.2 Unified Cert Lookup Dispatcher

```dart
// add_coins_hub.dart — _lookupCertUnified
Future<void> _lookupCertUnified() async {
  final raw = _pcgsSingleCtrl.text.trim();
  if (raw.isEmpty) {
    setState(() => _pcgsLookupError = 'Please enter a cert number.');
    return;
  }
  final grader = _certGrader ?? _autoDetectGrader(raw);

  setState(() {
    _pcgsLookupResult = null;
    _pcgsLookupError = '';
    _certPendingConfirm = null;
  });

  if (grader == 'PCGS') {
    await _lookupSingleCert();
    return;
  }

  // NGC or CAC — no public API, show manual-entry card
  final certClean = raw.contains('/') ? raw.split('/').last.trim() : raw;
  setState(() {
    _certPendingConfirm = {
      '_grader': grader,
      'certNo': certClean,
    };
    _certManualCoinName.clear();
    _certManualYear.clear();
    _certManualGrade.clear();
    _certManualDenom.clear();
    _certManualNotes.clear();
  });
}
```

**Review:** Correct dispatch. PCGS delegates to existing battle-tested `_lookupSingleCert()`. NGC/CAC correctly show manual-entry card. State cleared before each lookup prevents stale display.

### 2.3 Grader Radio Chips (Correct UX Pattern)

```dart
// add_coins_hub.dart — grader selector inside _buildCertLookupTab
Row(
  children: [
    for (final g in ['Auto', 'PCGS', 'NGC', 'CAC'])
      Padding(
        padding: const EdgeInsets.only(right: 8),
        child: FilterChip(
          label: Text(g, ...),
          selected: (_certGrader == (g == 'Auto' ? null : g)),
          onSelected: (_) => setState(() {
            _certGrader = (g == 'Auto') ? null : g;
            _pcgsLookupResult = null;
            _pcgsLookupError = '';
            _certPendingConfirm = null;
          }),
          ...
        ),
      ),
  ],
),
```

**Review:** Correct. "Auto" maps to `_certGrader == null` (auto-detect). Switching grader clears previous results to avoid stale data. FilterChip is the right Flutter widget for this pattern.

### 2.4 NGC Manual-Entry Card with CAC Note

```dart
// add_coins_hub.dart — _buildManualCertEntryCard (partial)
Text(
  grader == 'CAC'
      ? 'CAC verification is manual — no automated lookup available.'
      : 'NGC has no public cert lookup API — data entered manually.',
  textAlign: TextAlign.center,
  style: const TextStyle(fontSize: 11, color: Color(0xFF94A3B8)),
),
```

**Review:** Correct. CAC explicitly noted as "manual" per requirements. NGC states no public API. Both notes honest and non-misleading.

### 2.5 PCGS Confirm Screen (unchanged — already had confirm)

```dart
// add_coins_hub.dart — _buildLookupResultCard
SizedBox(
  width: double.infinity,
  child: ElevatedButton.icon(
    onPressed: _pcgsSingleAdding ? null : _addLookupResultToCollection,
    ...
    label: Text(_pcgsSingleAdding ? 'Adding...' : 'Add to My Collection'),
    ...
  ),
),
```

**Review:** PCGS confirm-before-save was already implemented. Preserved. NGC/CAC add same pattern via `_saveManualCertEntry`.

### 2.6 Sidebar Heading Now Clickable

```dart
// base_layout.dart — ADD NEW COINS/NOTES/ETC. section header
if (!_isSidebarCollapsed)
  Builder(builder: (context) {
    final isHeaderDark = Theme.of(context).brightness == Brightness.dark;
    return GestureDetector(
      onTap: () => setState(() => _activeRoute = 'Add New Coins'),
      child: Padding(
        padding: const EdgeInsets.only(left: 8, top: 22, bottom: 6),
        child: MouseRegion(
          cursor: SystemMouseCursors.click,
          child: Text(
            'ADD NEW COINS/NOTES/ETC.',
            style: TextStyle(
              fontSize: NumistaTheme.textCaption,
              fontWeight: FontWeight.bold,
              color: isHeaderDark
                  ? const Color(0xFF38BDF8)
                  : const Color(0xFF2563EB),
              letterSpacing: 0.8,
              decoration: TextDecoration.underline,
              ...
            ),
          ),
        ),
      ),
    );
  }),
```

**Review:** Correct. Uses `Builder` to scope `isDark` — avoids using `isDark` from outer scope (which is only defined inside `_buildNavItem`). `MouseRegion(cursor: SystemMouseCursors.click)` ensures pointer cursor on desktop. Color changed from `Colors.black45/white38` to blue to signal clickability. `TextDecoration.underline` provides additional affordance. `GestureDetector.onTap` dispatches to same `_activeRoute = 'Add New Coins'` used elsewhere.

### 2.7 Top-Level Cert QuickAddCard

```dart
// add_coins_hub.dart — build() method
// ── P7 FIX: Cert lookup is TOP LEVEL — always visible ───────────────
_QuickAddCard(
  icon: Icons.verified_outlined,
  label: 'Add by Cert # (PCGS / NGC / CAC)',
  onTap: () {
    setState(() => _showMoreWays = true);
    _tabController.animateTo(3);
  },
),
_QuickAddCard(
  icon: Icons.camera_alt_outlined,
  label: 'Take a photo',
  ...
```

**Review:** Correct. Cert card is declared first (before Camera, Type-it-in, Upload), so it appears at the top of the list. `_tabController.animateTo(3)` matches index 3 = Cert Lookup tab. `_showMoreWays = true` ensures the tab bar is shown when landing on that tab.

### 2.8 NGC/CAC Save Logic — No Demo Flag Leak

```dart
// add_coins_hub.dart — _saveManualCertEntry
final coinDoc = <String, dynamic>{
  'certNo':            certNo,
  'grader':            grader,
  'CoinName':          _certManualCoinName.text.trim(),
  ...
  'source':            'cert_manual_${grader.toLowerCase()}',
  'Added':             FieldValue.serverTimestamp(),
  'is_demo':           false,
  'is_demo_cleared':   false,
};
await FirebaseFirestore.instance
    .collection(AuthService.coinsPath)  // uses user's own path, not Eric's
    .add(coinDoc);
```

**Review:** Correct. Uses `AuthService.coinsPath` (user-scoped, not Eric's collection). Sets `is_demo: false` per ITEM 6 convention. `grader` and `certNo` fields stored for later verification or deduplication.

### 2.9 Backend cert_routes.py — NGC/CAC already correct

```python
# cert_routes.py — NGC fallback (lines 196–208)
if detected_grader == "NGC":
    return CertLookupResponse(
        grader="NGC",
        cert_num=clean_cert,
        coin_name=None,
        year=None,
        ...
        found=False,
        source="manual_fallback",
    )
```

**Review:** Existing backend was already correct — no changes needed. Source field `"manual_fallback"` is documented and mirrors what the Flutter UI shows. No NGC API calls attempted (would result in 403).

---

## 3. Issues / Risks

| Severity | Issue | Mitigation |
|----------|-------|-----------|
| LOW | PCGS bulk import tab (`_buildPcgsImportTab`) is now an internal method only accessed via Advanced Options — not directly navigable | Acceptable — bulk import is power-user feature; single cert is the primary path |
| LOW | `_certPendingConfirm` uses a `Map<String, dynamic>` keyed with `'_grader'` — could use a typed model | Acceptable for current scope; could be refactored to `CertLookupPending` model in future |
| NONE | Firestore writes in tests | Zero — all tests are source audits or pure-logic assertions |

---

## 4. Test Coverage

| Test Group | Cases | Result |
|-----------|-------|--------|
| Cert auto-detection | 7 | ✅ Pure-logic, no Firebase |
| QuickAddCard renders cert | 2 | ✅ Widget test, no Firebase |
| Source code audit | 5 | ✅ File read, no Firebase |
| Sidebar nav source audit | 2 | ✅ File read |
| Backend cert_routes.py | 2 | ✅ File read |
| CAC manual note | 1 | ✅ Source check |
| PCGS confirm screen | 1 | ✅ Source check |

**Total: 20 test assertions across 7 groups.**

---

## 5. Verdict

| Check | Result |
|-------|--------|
| All 5 beta bugs fixed | ✅ |
| Cert lookup top-level | ✅ |
| PCGS/NGC/CAC supported | ✅ |
| Confirm before save | ✅ |
| Sidebar heading clickable | ✅ |
| No fake/guessed coin data | ✅ |
| No API keys in files | ✅ |
| Tests: no live Firestore writes | ✅ |
| Dev branch only | ✅ |

**PASS. Ready for baton rename.**
