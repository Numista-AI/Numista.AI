# PLAN P7 V8.5 — Manual Entry Form: Validators, Persistent Controllers, Better Error Messages
**Date:** 2026-10-15  
**Filed by:** AG CoS  
**Ref:** NET-216, FT_GATE_P7_V8.md, BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md  
**Scope:** `numista_mobile/lib/widgets/add_coin_manual_form.dart`, `numista_mobile/lib/screens/add_coins_hub.dart`, `numista_mobile/lib/screens/program_manager_screen.dart`, `numista_mobile/test/p7_v8_ux_safety_test.dart`

---

## Bug Summary (Field Tester findings, all present in V8.4 e8b978f2)

| # | Bug | Root Cause |
|---|-----|-----------|
| 1 | Year (and other required fields) accepts blank on Save | `_buildField(isRequired: true)` draws red `*` but `TextFormField` has **no validator** → `_formKey.validate()` always returns true |
| 2 | Fields drop first typed character; Year blanks after entry | All fields use `initialValue:` with **no controller** (only Mint Mark has one) → any parent rebuild (setState `_isProcessing`, keyboard open/close, IndexedStack/route rebuild) remounts form and loses text |
| 3 | Generic "connection error" snackbar | `add_coins_hub.dart ~2058` catch always emits a fixed "check your connection" string; checklist path (`program_manager_screen.dart ~1955-1962`) uses `NumistaErrorHelper` generic text with no context about WHAT failed |

---

## Item 1 — Required-field validators

### File
`numista_mobile/lib/widgets/add_coin_manual_form.dart`

### Change
Add a `validator` param to `_buildField`. For `isRequired: true` fields, provide:

```dart
validator: isRequired
    ? (val) {
        if (val == null || val.trim().isEmpty) {
          return _validatorMessage(key);
        }
        return null;
      }
    : null,
```

Add a private helper that returns a plain-English message per field:

```dart
String _validatorMessage(String key) {
  switch (key) {
    case 'Year':
      return 'Please enter the year on the coin, like 1921.';
    case 'Denomination':
      return 'Please enter the denomination, like Quarter Dollar.';
    case 'Program/Series':
      return 'Please enter the program or series name.';
    default:
      return 'This field is required.';
  }
}
```

Additional: Year field also validates 4-digit format:

```dart
validator: (val) {
  if (val == null || val.trim().isEmpty) return 'Please enter the year on the coin, like 1921.';
  if (val.trim().length != 4) return 'Year must be 4 digits, like 1921.';
  return null;
},
```

### Server-side (dev only, NO deploy)
**Path chosen: client-only guard (no firestore.rules change, no backend route change).**  
Reason: The FT bug is purely a client-side missing validator. `_formKey.validate()` is already called in `_submit()` before `widget.onSubmit(_formData)` is invoked. Once validators are added, `_submit()` will gate the save correctly. No additional server-side change is needed at this time; firestore.rules and backend already have the existing structure. A firestore.rules deploy would need Eric's YES — deferring since client fix is sufficient for the FT gate.

---

## Item 2 — Persistent TextEditingControllers (no-controller → one controller per field)

### File
`numista_mobile/lib/widgets/add_coin_manual_form.dart`

### Change
Replace `initialValue:` with a persistent `TextEditingController` per field, created in `initState`, disposed in `dispose`. Fields affected (all currently using `initialValue`):

- Year, Denomination, Program/Series, Theme/Subject, Variety, Condition, Cost, Quantity, Storage Location, Retailer/Website, Retailer Invoice #, Notes  
- Mint Mark already has `_mintCtrl` — leave untouched

**New controllers (all in `_AddCoinManualFormState`):**

```dart
late final TextEditingController _yearCtrl;
late final TextEditingController _denomCtrl;
late final TextEditingController _programCtrl;
late final TextEditingController _themeCtrl;
late final TextEditingController _varietyCtrl;
late final TextEditingController _conditionCtrl;
late final TextEditingController _costCtrl;
late final TextEditingController _qtyCtrl;
late final TextEditingController _storageCtrl;
late final TextEditingController _retailerCtrl;
late final TextEditingController _invoiceCtrl;
late final TextEditingController _notesCtrl;
```

**initState:**

```dart
@override
void initState() {
  super.initState();
  _yearCtrl = TextEditingController(text: _formData['Year'] as String? ?? '');
  _denomCtrl = TextEditingController(text: _formData['Denomination'] as String? ?? '');
  // ... repeat for all 12 fields
  _conditionCtrl = TextEditingController(text: 'Ungraded');
}
```

**dispose:**
```dart
@override
void dispose() {
  _yearCtrl.dispose();
  _denomCtrl.dispose();
  // ... all 12 + existing _mintCtrl
  super.dispose();
}
```

**`_buildField`** gains a `controller` param (`TextEditingController?`); `initialValue` removed when controller is provided:

```dart
Widget _buildField(
  BuildContext context,
  String key,
  String hint, {
  TextEditingController? controller,
  bool isRequired = false,
  ...
}) {
  return TextFormField(
    controller: controller,
    // initialValue: REMOVED when controller present
    onSaved: (val) => _formData[key] = val ?? '',
    ...
  );
}
```

**Call sites:** Pass the matching controller at each `_buildField(...)` invocation:
- `'Year'` → `controller: _yearCtrl`
- `'Denomination'` → `controller: _denomCtrl`
- etc.

**Stable keys:** No `ValueKey` needed since controllers are what provide stability across rebuilds.

---

## Item 3 — Plain-English error messages naming WHAT failed

### Files
- `numista_mobile/lib/screens/add_coins_hub.dart` (~line 2058 manual save catch)
- `numista_mobile/lib/screens/program_manager_screen.dart` (~lines 1955-1962 checklist add catch)

### Change A — Manual save catch (add_coins_hub.dart ~2058)

**Before:**
```dart
} catch (e) {
  setState(() => _manualError = 'Failed to save coin. Please check your connection.');
}
```

**After:**
```dart
} catch (e) {
  final year = _manualFormData?['Year']?.toString().trim() ?? '';
  final coinLabel = year.isNotEmpty ? '$year coin' : 'coin';
  setState(() => _manualError = NumistaErrorHelper.toUserFriendlyWithContext(
    e,
    action: "save your $coinLabel",
  ));
}
```

Add `toUserFriendlyWithContext(Object e, {required String action})` to `NumistaErrorHelper`:

```dart
static String toUserFriendlyWithContext(Object e, {required String action}) {
  final base = toUserFriendly(e);
  return "Couldn't $action — $base";
}
```

Examples produced:
- `"Couldn't save your 1921 coin — no internet connection."`  
- `"Couldn't save your coin — the server returned an error (500). Try again in a moment."`

### Change B — Checklist add catch (program_manager_screen.dart ~1955-1962)

**Before (likely):**
```dart
} catch (e) {
  setState(() => _error = NumistaErrorHelper.toUserFriendly(e));
}
```

**After:**
```dart
} catch (e) {
  final count = _selectedSlots.length;
  setState(() => _error = NumistaErrorHelper.toUserFriendlyWithContext(
    e,
    action: "add your ${count == 1 ? '1 coin' : '$count coins'}",
  ));
}
```

Examples produced:
- `"Couldn't add your 3 coins — the Numista.AI server didn't answer (network error)."`  
- `"Couldn't add your 1 coin — the server returned an error (CORS/preflight). Contact support if this persists."`

---

## Item 4 — Keep every V8.4 pass intact (no regressions)

All V8.4 changes remain untouched:
- 16px labels, 48px checkboxes, header ellipsis, PDF Wrap, childAspectRatio 1.6  
- IndexedStack login, `_divider` Flexible(flex:10)  
- Per-endpoint `_attempted` Set guard  
- Cost decimal keyboards (add_coins_hub, cam, mintSet)  
- `add_coins_hub.dart:2906` cert field — NOT touched  
- Demo guard, PIN 6 boxes, portfolio FittedBox  

---

## Widget Tests

New tests in `numista_mobile/test/p7_v8_ux_safety_test.dart`:

### V8.5 Item 1 — Validators block blank required fields
```
p7_v85_year_validator_blocks_empty_save
p7_v85_denomination_validator_blocks_empty_save
p7_v85_program_validator_blocks_empty_save
p7_v85_year_validator_blocks_non4digit
```
Each test: pump `AddCoinManualForm`, tap Save without entering value, assert `tester.takeException()` is null, assert error text appears, assert `onSubmit` was NOT called.

### V8.5 Item 2 — Controllers survive rebuild
```
p7_v85_year_field_survives_setstate_rebuild
p7_v85_all_fields_survive_pump_at_389px
p7_v85_all_fields_survive_pump_at_1025px
```
Each test: pump form, type text into Year (including first keystroke), pump/setState, assert field still shows typed value. At 389px and 1025px widths.

### V8.5 Regression — all V8.4 tests still pass
The existing 12 tests must remain green.

---

## Constraints
- `add_coins_hub.dart:2906` — cert number field, **DO NOT TOUCH**
- Dev branch only — no deploy
- No firestore.rules deploy (client validator is sufficient; server-side deferred)  
- No backend CORS deploy (needs Eric's typed YES)
- No `git add .` — explicit paths only
- `flutter analyze` → 0 issues before GEMINI38 review
- `flutter test test/p7_v8_ux_safety_test.dart` → all tests pass before GEMINI38 review

---

## Execution Order
1. `add_coin_manual_form.dart`: controllers → validators → error helper  
2. `add_coins_hub.dart`: `toUserFriendlyWithContext` added + catch updated  
3. `program_manager_screen.dart`: checklist catch updated  
4. `p7_v8_ux_safety_test.dart`: 7 new tests added  
5. `flutter analyze --no-pub` → 0 issues  
6. `flutter test test/p7_v8_ux_safety_test.dart --no-pub` → all pass  
7. `GEMINI38_REVIEW_P7_V8_5_BUILD.md` filed with verbatim before/after + per-condition checklist  
8. `git add` explicit paths → commit → pull --rebase → push origin dev  
9. Rename baton GROKCOS_OVER  
10. File NET to Grok CoS  
