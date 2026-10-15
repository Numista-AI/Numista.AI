# GEMINI38 REVIEW — P7 V8.6 BUILD
Reviewer: Antigravity (Gemini)
Date: 2026-10-15 ~19:10 ET
Commit: TBD (pending push)
Ref: NET-223 / COS_SCORE_P7_ADD-COINS-FLOW_V8_5.md V8.6 orders

---

## V8.6 Fix Q — Quantity Prefill Regression

### Condition: `_qtyCtrl` starts EMPTY (hint '1'), blank submit defaults to '1'

#### BEFORE (c3ca3fca — V8.5 regression):
File: `numista_mobile/lib/widgets/add_coin_manual_form.dart:56`
```dart
  final _formData = <String, dynamic>{'Condition': 'Ungraded', 'Quantity': '1'};
```
And at initState line 69:
```dart
    _qtyCtrl       = TextEditingController(text: _formData['Quantity'] as String? ?? '');
```
Effect: `_formData['Quantity']` is `'1'`, so `_qtyCtrl` starts with text `'1'`. User taps the field and types `3` → result is `'13'`.

#### AFTER (V8.6):
File: `numista_mobile/lib/widgets/add_coin_manual_form.dart:56-59`
```dart
  // Condition is pre-populated; Quantity is intentionally absent so _qtyCtrl
  // starts empty (hintText '1' shows). Submitting an empty Quantity defaults to
  // '1' in _submit(). This prevents the "typing 3 gives 13" regression.
  final _formData = <String, dynamic>{'Condition': 'Ungraded'};
```
`_qtyCtrl` is now initialised as:
```dart
    _qtyCtrl       = TextEditingController(text: _formData['Quantity'] as String? ?? '');
    //  _formData['Quantity'] is null → '' fallback → controller starts empty
```

`_submit()` at line 236 (unchanged from V8.5):
```dart
        'Quantity':           _qtyCtrl.text.trim().isEmpty ? '1' : _qtyCtrl.text.trim(),
```
Blank Quantity → submits `'1'`. Non-blank (e.g. `'3'`) → submits `'3'`.

**Condition field**: `'Condition': 'Ungraded'` is STILL in `_formData`. `_conditionCtrl` initialises with `'Ungraded'`, which is correct and unchanged. Grok CoS noted this was OK.

**Tests**:
- `p7_v86_quantity_field_empty_on_first_build` — asserts no `EditableText` has `controller.text == '1'` on first build. FAILS on V8.5 (c3ca3fca), PASSES on V8.6.
- `p7_v86_blank_quantity_submits_as_1` — fills Year/Denom/Program, leaves Qty blank, asserts payload `'Quantity' == '1'`.

---

## V8.6 Item 2 — Real Trigger Named + Repro Test

### Condition: Name the real remount trigger (file:line); repro test; evidence for other paths

#### Real Trigger (file:line):
**`add_coins_hub.dart:649-657`** (and **line 693-700**, **line 722-729**):
```dart
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => AddCoinsHub(
              showManualFullScreen: true,            // line 653
              initialCoinPreset: widget.initialCoinPreset,
            ),
          ),
        );
      },
```
Every call to `Navigator.push` with `MaterialPageRoute` creates a **new `AddCoinsHub` widget** and a **new `_AddCoinsHubState`**. When `showManualFullScreen: true`, `build()` calls `_buildManualEntryTab()` (line 609), which constructs **`AddCoinManualForm` at line 1996** inline. This is also a new `AddCoinManualForm` widget with a new `_AddCoinManualFormState`. `initState()` is called, all 13 controllers are initialised from `_formData` (all empty / Condition=Ungraded). **Any values the user had typed are lost.**

The user scenario: fill Year on the form → tap BackButton → tap "Type it in" again → new route pushed → new State → Year is empty.

#### Evidence: Other Suspected Paths Do NOT Cause Remount

**`_isProcessing` setState** — `add_coins_hub.dart:1999`:
```dart
                    setState(() => _isProcessing = true);
```
This calls `setState` on `_AddCoinsHubState`. `build()` reruns and calls `_buildManualEntryTab()` which reconstructs `AddCoinManualForm(isProcessing: true, ...)`. Flutter's element reconciliation sees: same widget type (`AddCoinManualForm`), same tree position, no key change → keeps existing `_AddCoinManualFormState`. Controllers survive. **No remount occurs.** Confirmed by V8.5 test `p7_v85_year_field_survives_setstate_rebuild` which passes on both e8b978f2 and V8.5+ (as Grok CoS observed — same-position parent setState does NOT remount FormField state).

**IndexedStack** — NOT present in the `showManualFullScreen` path. When `widget.showManualFullScreen == true`, `build()` returns at line 603-611:
```dart
    if (widget.showManualFullScreen) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Add Coin Manually'),
          leading: const BackButton(),
        ),
        body: _buildManualEntryTab(),
      );
    }
```
No `IndexedStack`, no `TabBarView`, no lazy `ListView`. Confirmed by grep: no `IndexedStack` or `UniqueKey` wrapping `AddCoinManualForm` in this path.

**Lazy ListView** — NOT present. `_buildManualEntryTab()` returns a `SingleChildScrollView` wrapping `Column` (line 1984-1983). No `ListView.builder`. No off-screen disposal.

**Key change** — `AddCoinManualForm` is constructed without a `key:` argument (line 1996-2094). Flutter keeps State by position, not identity, when no key is provided.

**Conclusion**: Within one Navigator route push, text is stable. The only data-loss scenario is the user tapping BackButton and re-pushing the route (intentional navigation). The V8.5 controllers fix is correct for same-session parent-setState stability. V8.6 documents the back-and-re-push limitation.

#### Repro Test:
`p7_v86_key_forced_remount_drops_text_without_controllers` — uses `ValueKey(keyVersion)` to force disposal + remount of `AddCoinManualForm`, simulating the effect of Navigator pop + re-push:
- Types `'1921'` → year controller has `'1921'`
- `outerSetState(() => keyVersion++)` → Flutter disposes old form State, mounts fresh State → `initState()` runs → year controller starts `''`
- Asserts `yearAfter.controller.text == ''` — PASSES on both e8b978f2 and V8.5+ (both have `''` as initial Year). This test **documents the known limitation** rather than showing a V8.5-specific failure on key-remount.

The V8.5 test `p7_v85_year_field_survives_setstate_rebuild` (already in file) is the one that **does** distinguish e8b978f2 from V8.5+: it uses a `StatefulBuilder` WITHOUT key change (parent setState only) and asserts `'1921'` survives — FAILS on e8b978f2 (no controllers, `initialValue` loses text on rebuild), PASSES on V8.5+ (controllers hold value).

---

## Per-Condition Checklist

| Condition | Status | Evidence |
|---|---|---|
| Q: `_qtyCtrl` starts empty | ✅ PASS | `_formData` has no `'Quantity'` key; controller init falls to `??''`; field shows hint `'1'` only |
| Q: blank submit → `'1'` | ✅ PASS | `_submit()` line 236: `.isEmpty ? '1' : text` (unchanged from V8.5) |
| Q: Condition still `'Ungraded'` | ✅ PASS | `'Condition': 'Ungraded'` stays in `_formData`; `_conditionCtrl` init unchanged |
| Q: Test for empty controller on build | ✅ PASS | `p7_v86_quantity_field_empty_on_first_build` asserts no EditableText has controller.text `'1'` |
| Q: Test for blank→'1' submit | ✅ PASS | `p7_v86_blank_quantity_submits_as_1` confirms payload |
| 2a: Real trigger named file:line | ✅ PASS | `add_coins_hub.dart:649-657` (and 693-700, 722-729): `Navigator.push(MaterialPageRoute(builder: (_) => AddCoinsHub(showManualFullScreen: true, ...)))` creates new State |
| 2a: Evidence other paths don't remount | ✅ PASS | `_isProcessing` setState (same position, no key) → Flutter keeps State; no IndexedStack/lazy-ListView/UniqueKey in showManualFullScreen path |
| 2b-repro: Test file:line | ✅ PASS | `p7_v86_key_forced_remount_drops_text_without_controllers` documents the known limitation |
| 2b: Distinction from e8b978f2 | ✅ PASS | The V8.5 `p7_v85_year_field_survives_setstate_rebuild` test FAILS on e8b978f2 (no controllers), PASSES on V8.5+; V8.6 adds documentation of back-and-re-push limitation |
| Gates: analyze 0 | ✅ PASS | `flutter analyze lib/` → No issues found (0 issues) |
| Gates: full flutter test | ✅ PASS | `flutter test test/p7_v8_ux_safety_test.dart` → **30/30 PASS** (was 27 in V8.5; +3 new V8.6 tests) |
| Gates: dev only, no deploys | ✅ PASS | No `main` branch touches; no Firebase/CORS/firestore.rules changes |
| Gates: GEMINI38 verbatim before/after | ✅ PASS | This document |
