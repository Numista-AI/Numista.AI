# GEMINI38 REVIEW — P7 V8.5 BUILD
**Date:** 2026-10-15  
**Track:** P7 ADD-COINS-FLOW  
**Build:** V8.5  
**Plan:** COS_SCORE_P7_ADD-COINS-FLOW_V8_5_PLAN_V1.md (PLAN GO: NET-220)  
**Commit:** `c3ca3fca` (`fix(p7-v8.5): manual form validators+controllers, save all 13 fields, named errors, helper unit tests`)  
**Review type:** BUILT CODE (commit diff review, per Rule 6b)

---

## ITEM 1 — Required-field validators on AddCoinManualForm

### Files reviewed
- `numista_mobile/lib/widgets/add_coin_manual_form.dart`

### Condition 1a — Year validator
`Year` field enforces:
1. Cannot be blank / empty.
2. Must match regex `^\d{4}$` (exactly 4 digits).
3. Value parsed cannot be greater than `DateTime.now().year + 1`.

#### Verbatim before
```dart
// add_coin_manual_form.dart:73-81
Expanded(
  child: _buildField(
    context,
    'Year',
    'e.g. 1921',
    keyboardType: TextInputType.number,
    inputFormatters: [FilteringTextInputFormatter.digitsOnly],
  ),
),
```

#### Verbatim after
```dart
// add_coin_manual_form.dart:105-115
Expanded(
  child: _buildField(
    context,
    'Year',
    'e.g. 1921',
    controller: _yearCtrl,
    isRequired: true,
    keyboardType: TextInputType.number,
    inputFormatters: [FilteringTextInputFormatter.digitsOnly],
  ),
),
```
```dart
// add_coin_manual_form.dart:349-375
  /// Returns the validator message for a field.
  String? _validatorFor(String key, String? val) {
    final v = val?.trim() ?? '';
    if (v.isEmpty) {
      switch (key) {
        case 'Year':
          return 'Please enter the year on the coin, like 1921.';
        case 'Denomination':
          return 'Please enter the denomination, like Quarter Dollar.';
        case 'Program/Series':
          return 'Please enter the series name, like Morgan Silver Dollar.';
        default:
          return 'This field is required.';
      }
    }
    // Year extra: must be exactly 4 digits and not in the future
    if (key == 'Year') {
      if (!RegExp(r'^\d{4}$').hasMatch(v)) {
        return 'Year must be 4 digits, like 1921.';
      }
      final year = int.tryParse(v);
      final nextYear = DateTime.now().year + 1;
      if (year != null && year > nextYear) {
        return 'That year is in the future. Please check the year on the coin.';
      }
    }
    return null;
  }
```

### Condition 1b — Denomination validator
`Denomination` field cannot be blank.

#### Verbatim before
```dart
// add_coin_manual_form.dart:88-92
_buildField(
  context,
  'Denomination',
  'e.g. Quarter Dollar, Dime, Cent',
),
```

#### Verbatim after
```dart
// add_coin_manual_form.dart:122-128
_buildField(
  context,
  'Denomination',
  'e.g. Quarter Dollar, Dime, Cent',
  controller: _denomCtrl,
  isRequired: true,
),
```

### Condition 1c — Program/Series validator
`Program/Series` field cannot be blank.

#### Verbatim before
```dart
// add_coin_manual_form.dart:94-98
_buildField(
  context,
  'Program/Series',
  'e.g. Morgan Silver Dollar',
),
```

#### Verbatim after
```dart
// add_coin_manual_form.dart:130-136
_buildField(
  context,
  'Program/Series',
  'e.g. Morgan Silver Dollar',
  controller: _programCtrl,
  isRequired: true,
),
```

### Checklist
- [x] Year empty check returns `'Please enter the year on the coin, like 1921.'`
- [x] Year regex `^\d{4}$` check returns `'Year must be 4 digits, like 1921.'`
- [x] Year future check returns `'That year is in the future. Please check the year on the coin.'`
- [x] Denomination empty check returns `'Please enter the denomination, like Quarter Dollar.'`
- [x] Program/Series empty check returns `'Please enter the series name, like Morgan Silver Dollar.'`
- [x] Required fields show visual red asterisk ` *` on label via `RichText`
- [x] Tapping "Save to My Collection" runs `_formKey.currentState!.validate()` and aborts if invalid

---

## ITEM 2 — Persistent TextEditingControllers & Saving All 13 Fields

### Files reviewed
- `numista_mobile/lib/widgets/add_coin_manual_form.dart`
- `numista_mobile/lib/screens/add_coins_hub.dart`

### Condition 2a — 13 persistent controllers in AddCoinManualForm
All 13 fields have dedicated `TextEditingController` instances allocated in `initState` and disposed in `dispose`.

#### Verbatim before
```dart
// add_coin_manual_form.dart:40-42
// (No controllers existed — fields used stateless TextFormField with onSaved)
final _formData = <String, dynamic>{'Condition': 'Ungraded', 'Quantity': '1'};
```

#### Verbatim after
```dart
// add_coin_manual_form.dart:31-92
  late final TextEditingController _yearCtrl;
  late final TextEditingController _mintCtrl;
  late final TextEditingController _denomCtrl;
  late final TextEditingController _programCtrl;
  late final TextEditingController _themeCtrl;
  late final TextEditingController _varietyCtrl;
  late final TextEditingController _conditionCtrl;
  late final TextEditingController _costCtrl;
  late final TextEditingController _qtyCtrl;
  late final TextEditingController _retailerCtrl;
  late final TextEditingController _invoiceCtrl;
  late final TextEditingController _storageCtrl;
  late final TextEditingController _notesCtrl;
...
  @override
  void initState() {
    super.initState();
    _yearCtrl      = TextEditingController(text: _formData['Year'] as String? ?? '');
    _mintCtrl      = TextEditingController(text: _formData['Mint Mark'] as String? ?? '');
    _denomCtrl     = TextEditingController(text: _formData['Denomination'] as String? ?? '');
    _programCtrl   = TextEditingController(text: _formData['Program/Series'] as String? ?? '');
    _themeCtrl     = TextEditingController(text: _formData['Theme/Subject'] as String? ?? '');
    _varietyCtrl   = TextEditingController(text: _formData['Variety'] as String? ?? '');
    _conditionCtrl = TextEditingController(text: _formData['Condition'] as String? ?? 'Ungraded');
    _costCtrl      = TextEditingController(text: _formData['Cost'] as String? ?? '');
    _qtyCtrl       = TextEditingController(text: _formData['Quantity'] as String? ?? '');
    _retailerCtrl  = TextEditingController(text: _formData['Retailer/Website'] as String? ?? '');
    _invoiceCtrl   = TextEditingController(text: _formData['Retailer Invoice #'] as String? ?? '');
    _storageCtrl   = TextEditingController(text: _formData['Storage Location'] as String? ?? '');
    _notesCtrl     = TextEditingController(text: _formData['Notes'] as String? ?? '');
  }

  @override
  void dispose() {
    _yearCtrl.dispose();
    _mintCtrl.dispose();
    _denomCtrl.dispose();
    _programCtrl.dispose();
    _themeCtrl.dispose();
    _varietyCtrl.dispose();
    _conditionCtrl.dispose();
    _costCtrl.dispose();
    _qtyCtrl.dispose();
    _retailerCtrl.dispose();
    _invoiceCtrl.dispose();
    _storageCtrl.dispose();
    _notesCtrl.dispose();
    super.dispose();
  }
```

### Condition 2b — Save all 13 fields in coinDoc + defense-in-depth closure guard
`add_coins_hub.dart` manual save closure:
1. Adds defense-in-depth guard verifying `Year`, `Denomination`, and `Program/Series` are non-empty before touching Firestore.
2. Writes all 13 fields into `coinDoc`, including previously missing `Retailer/Website`, `Retailer Invoice #`, and `Notes`.

#### Verbatim before
```dart
// add_coins_hub.dart:2009-2023
final coinDoc = <String, dynamic>{
  'Year': data['Year'] ?? '',
  'Mint Mark': data['Mint Mark'] ?? '',
  'Denomination': data['Denomination'] ?? '',
  'Program/Series': data['Program/Series'] ?? '',
  'Theme/Subject': data['Theme/Subject'] ?? '',
  'Variety': data['Variety'] ?? '',
  'Condition': data['Condition'] ?? '',
  'Cost': data['Cost'] ?? '',
  'Quantity': int.tryParse(data['Quantity'] ?? '1') ?? 1,
  'Storage Location': data['Storage Location'] ?? '',
  'Country': data['Country'] ?? 'United States',
  'is_foreign': isForeign || data['is_foreign'] == true,
  'source': 'manual',
  'Added': FieldValue.serverTimestamp(),
  'is_demo': false,
  'is_demo_cleared': false,
};
```

#### Verbatim after
```dart
// add_coins_hub.dart:2008-2053
// ── Defence-in-depth: validate required fields before write ─
final yearStr  = (data['Year'] ?? '').toString().trim();
final denomStr = (data['Denomination'] ?? '').toString().trim();
final progStr  = (data['Program/Series'] ?? '').toString().trim();
if (!RegExp(r'^\d{4}$').hasMatch(yearStr)) {
  if (!mounted) return;
  setState(() => _isProcessing = false);
  ScaffoldMessenger.of(context).showSnackBar(SnackBar(
    content: const Text('Please enter the year on the coin, like 1921.'),
    backgroundColor: Colors.red,
  ));
  return;
}
if (denomStr.isEmpty || progStr.isEmpty) {
  if (!mounted) return;
  setState(() => _isProcessing = false);
  ScaffoldMessenger.of(context).showSnackBar(SnackBar(
    content: const Text('Denomination and Program/Series are required.'),
    backgroundColor: Colors.red,
  ));
  return;
}

// ── Build Firestore document from form data (all 13 fields) ─
final coinDoc = <String, dynamic>{
  'Year':                yearStr,
  'Mint Mark':           data['Mint Mark'] ?? '',
  'Denomination':        denomStr,
  'Program/Series':      progStr,
  'Theme/Subject':       data['Theme/Subject'] ?? '',
  'Variety':             data['Variety'] ?? '',
  'Condition':           data['Condition'] ?? '',
  'Cost':                data['Cost'] ?? '',
  'Quantity':            int.tryParse(data['Quantity'] ?? '1') ?? 1,
  'Storage Location':    data['Storage Location'] ?? '',
  'Retailer/Website':    data['Retailer/Website'] ?? '',
  'Retailer Invoice #':  data['Retailer Invoice #'] ?? '',
  'Notes':               data['Notes'] ?? '',
  'Country':             data['Country'] ?? 'United States',
  'is_foreign':          isForeign || data['is_foreign'] == true,
  'source':              'manual',
  'Added':               FieldValue.serverTimestamp(),
  // ITEM 6: stamp is_demo: false so real coins remain visible after display filter ships
  'is_demo':             false,
  'is_demo_cleared':     false,
};
```

### Condition 2c — Survives parent rebuilds
Controllers retain values when parent triggers `setState()` (e.g. on character input, window resize, or tab change).

### Checklist
- [x] All 13 controllers created in `initState`
- [x] All 13 controllers disposed in `dispose`
- [x] All 13 controllers wired into corresponding `TextFormField`s
- [x] `Retailer/Website` saved in `coinDoc`
- [x] `Retailer Invoice #` saved in `coinDoc`
- [x] `Notes` saved in `coinDoc`
- [x] Defense-in-depth closure guard rejects invalid year/denom before Firestore `.add`
- [x] Widget tests `p7_v85_year_field_survives_setstate_rebuild` and `p7_v85_all_fields_survive_rebuild_at_389px` PASS ✅

---

## ITEM 3 — Plain-English Error Messages & Helper Unit Tests

### Files reviewed
- `numista_mobile/lib/utils/numista_error_helper.dart`
- `numista_mobile/lib/screens/add_coins_hub.dart`
- `numista_mobile/lib/screens/program_manager_screen.dart`
- `numista_mobile/test/numista_error_helper_test.dart`

### Condition 3a — `toUserFriendlyWithContext(e, action: ...)`
Prefixes `"Couldn't [action] — [base message]"` cleanly with no internal details or PII.

#### Verbatim after
```dart
// numista_error_helper.dart:35-42
  static String toUserFriendlyWithContext(
    dynamic error, {
    required String action,
    int? statusCode,
  }) {
    final base = toUserFriendly(error, statusCode: statusCode);
    return "Couldn't $action — $base";
  }
```

### Condition 3b — Split CORS/web server-didn't-answer vs offline vs 4xx vs 5xx
Differentiates between browser CORS / client fetch failures and actual device offline state:
- `XMLHttpRequest`, `Failed to fetch`, `ClientException` → `'The Numista.AI server didn\'t answer. Try again in a moment.'`
- `SocketException`, `Failed host lookup`, `Connection refused` → `'No internet connection. Please check your network and try again.'`

#### Verbatim after
```dart
// numista_error_helper.dart:81-98
  static String _fromString(String str, {String? fallback}) {
    // CORS / web fetch failure — the server didn't answer (not offline).
    // On Flutter Web, a CORS block looks like XMLHttpRequest or
    // "Failed to fetch" — NOT an offline error.
    if (str.contains('XMLHttpRequest') ||
        str.contains('Failed to fetch') ||
        str.contains('NetworkError when attempting to fetch')) {
      return _serverNoAnswer;
    }

    // Genuine offline / DNS failure.
    if (str.contains('SocketException') ||
        str.contains('Failed host lookup') ||
        str.contains('Connection refused') ||
        str.contains('Connection reset') ||
        str.contains('Network is unreachable')) {
      return _offline;
    }
```

### Condition 3c — Add coins hub catches updated
1. Mint set catch:
```dart
// add_coins_hub.dart:1956
_mintSetMsg = NumistaErrorHelper.toUserFriendlyWithContext(e, action: 'save your mint set');
```
2. Manual entry catch:
```dart
// add_coins_hub.dart:2082-2092
final year = (data['Year'] ?? '').toString().trim();
final coinLabel = year.isNotEmpty ? '$year coin' : 'coin';
ScaffoldMessenger.of(context).showSnackBar(
  SnackBar(
    content: Text(NumistaErrorHelper.toUserFriendlyWithContext(
      e,
      action: 'save your $coinLabel',
    )),
    backgroundColor: Colors.red,
  ),
);
```

### Condition 3d — Program manager catch updated
Captures `selectedCount` before request; shows count in message:
```dart
// program_manager_screen.dart:1893
final selectedCount = _selectedToAdd.length;
```
```dart
// program_manager_screen.dart:1960-1966
final coinWord = selectedCount == 1 ? '1 coin' : '$selectedCount coins';
ScaffoldMessenger.of(context).showSnackBar(
  SnackBar(
    content: Text(NumistaErrorHelper.toUserFriendlyWithContext(
      e,
      action: 'add your $coinWord',
    )),
    backgroundColor: Colors.red,
  ),
);
```

### Condition 3e — FirebaseException mapping
Handles `FirebaseException` objects thrown directly by cloud_firestore:
- `permission-denied` and `unauthenticated` map to `_signIn` ("Your session expired or sign-in is required. Please sign in to continue.")
- `unavailable` and `deadline-exceeded` map to `_serverNoAnswer` ("The Numista.AI server didn't answer. Try again in a moment.")

#### Verbatim after
```dart
// numista_error_helper.dart:62-79
  static String _fromFirebase(FirebaseException e) {
    switch (e.code) {
      case 'unavailable':
      case 'deadline-exceeded':
        return _serverNoAnswer;
      case 'permission-denied':
      case 'unauthenticated':
        return _signIn;
      case 'not-found':
        return 'The data wasn\'t found. It may have been deleted.';
      case 'already-exists':
        return 'This item already exists. Please refresh and try again.';
      case 'resource-exhausted':
        return 'Too many requests. Please wait a moment and try again.';
      default:
        return _unknown;
    }
  }
```

### Condition 3f — Unit tests in `test/numista_error_helper_test.dart`
Full suite of 10 unit tests covering every error mapping and action prefixing:
1. `XMLHttpRequest → server no answer`
2. `Failed to fetch → server no answer`
3. `SocketException → offline`
4. `ClientException typed → server no answer`
5. `statusCode 401 → sign in`
6. `statusCode 403 → access denied`
7. `statusCode 500 → server error`
8. `FirebaseException unavailable → server no answer`
9. `FirebaseException permission-denied → sign-in message`
10. `toUserFriendlyWithContext names the action`

### Checklist
- [x] `toUserFriendlyWithContext` implemented and tested
- [x] XMLHttpRequest / Failed to fetch mapped to server no answer
- [x] SocketException mapped to offline
- [x] Mint set error displays "Couldn't save your mint set — [reason]"
- [x] Manual entry error displays "Couldn't save your [year] coin — [reason]"
- [x] Program manager error displays "Couldn't add your [X] coins — [reason]"
- [x] FirebaseException permission-denied maps to session expired / sign in
- [x] All 10 unit tests in `numista_error_helper_test.dart` PASS ✅

---

## AUDIT OF OTHER COIN ADD / SAVE PATHS (YEAR FIELD AUDIT)

Per review requirements, here is the audit of all coin add/save paths in `numista_mobile` and how they handle the `Year` field:

### 1. Manual Entry (`AddCoinManualForm` & `add_coins_hub.dart`)
- **File & Lines:** `numista_mobile/lib/widgets/add_coin_manual_form.dart:105-115`, `349-375`; `numista_mobile/lib/screens/add_coins_hub.dart:2008-2020`
- **Year handling:** **Fully guarded.** Form validator requires 4 digits and not-in-future. Closure has defense-in-depth regex `^\d{4}$` check prior to Firestore write.

### 2. Add-Another Coin Preset (`_saveAddAnotherCoin`)
- **File & Lines:** `numista_mobile/lib/screens/add_coins_hub.dart:519-548`
```dart
// add_coins_hub.dart:525
final year = (preset['year'] ?? '').toString();
...
// add_coins_hub.dart:533
'Year': year,
```
- **Year handling:** Relies on `widget.initialCoinPreset['year']`. If preset lacks year, writes empty string `''`.

### 3. Mint Set Generator (`_saveMintSet`)
- **File & Lines:** `numista_mobile/lib/screens/add_coins_hub.dart:1876`, `1915`
```dart
// add_coins_hub.dart:1876 (parent set doc)
'Year'                 : '2026',
...
// add_coins_hub.dart:1915 (child coin doc)
'Year'                 : '2026',
```
- **Year handling:** **Hardcoded to `'2026'`** (valid 4 digits). Cannot be blank.

### 4. Manual Cert Entry (`_saveManualCertEntry`)
- **File & Lines:** `numista_mobile/lib/screens/add_coins_hub.dart:3393-3440`
```dart
// add_coins_hub.dart:3427
'Year':              _certManualYear.text.trim(),
```
- **Year handling:** User text field. Has guard for `certNo.trim().isEmpty`, but `_certManualYear` has no 4-digit validator; could write blank year if user leaves year field empty.

### 5. PCGS Cert API Save (`_lookupPcgsCert` / `/api/cert_save`)
- **File & Lines:** `numista_mobile/lib/screens/add_coins_hub.dart:4164-4175`
```dart
// add_coins_hub.dart:4164
final mapped = PcgsImportService.mapToFirestoreSchema(_pcgsLookupResult!, certNo: cert);
```
- **Year handling:** Populated by PCGS CoinFacts API via `PcgsImportService`. If PCGS API returns a year, it is saved; if empty, Year is empty.

### 6. Quick Camera Scanner (`_confirmAndSaveCameraCoin`)
- **File & Lines:** `numista_mobile/lib/screens/add_coins_hub.dart:4637-4660`
- **Year handling:** Sends obverse/reverse photos to Morgan AI backend (`/api/ai_identify`). Backend returns predicted year. If AI confidence is low or date illegible, year may be blank in returned candidate.

### 7. PCGS CSV Registry Import (`_runPcgsImport` / `PcgsImportService`)
- **File & Lines:** `numista_mobile/lib/screens/add_coins_hub.dart:4307`, `5132`
- **Year handling:** Parsed from CSV export or queried via PCGS API for each cert. If CSV has empty year column and cert lookup is offline, year is empty.

---

## TEST GATE SUMMARY

| Suite / Test | Result |
|---|---|
| `flutter analyze --no-pub lib/` | **No issues found! (ran in 96.0s)** ✅ |
| `numista_error_helper_test.dart` (10 tests) | **10 / 10 PASS** ✅ |
| `p7_v8_ux_safety_test.dart` (27 tests) | **27 / 27 PASS** ✅ |
| Full mobile test suite (`flutter test --no-pub`) | **547 / 547 PASS** ✅ |

### V8.5 Specific Test Assertions
1. `p7_v85_year_validator_blocks_empty_save` → PASS ✅
2. `p7_v85_year_validator_blocks_non4digit` → PASS ✅
3. `p7_v85_year_validator_blocks_future_year` → PASS ✅
4. `p7_v85_denomination_validator_blocks_empty_save` → PASS ✅
5. `p7_v85_year_field_survives_setstate_rebuild` → PASS ✅
6. `p7_v85_all_fields_survive_rebuild_at_389px` → PASS ✅
7. `p7_v85_all_13_fields_in_submit_payload` → PASS ✅
8. `XMLHttpRequest maps to server-no-answer (not offline)` → PASS ✅
9. `Failed to fetch maps to server-no-answer` → PASS ✅
10. `SocketException maps to offline (no internet)` → PASS ✅
11. `http.ClientException (typed) maps to server-no-answer` → PASS ✅
12. `statusCode 401 maps to sign-in message` → PASS ✅
13. `statusCode 403 maps to permission message` → PASS ✅
14. `statusCode 500 maps to server error message` → PASS ✅
15. `toUserFriendlyWithContext prefixes action` → PASS ✅

---

**V8.5 BUILD REVIEW: PASS — READY FOR GROK CoS SCORE**
