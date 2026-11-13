# EXECUTE DONE: P7 Add Coins Flow V8.18.11

**Date:** 2026-10-20 ~15:20 ET  
**Author:** AG CoS  
**Branch:** `p7-v8.9`  
**Commit SHA:** `44c83f43ef4efaf1d44a34d27f10681035a3e8c2` (pushed to `origin/p7-v8.9`)  
**Parent Commit:** `b9cbc26a2ecec78c4ec3749cbce8d9dda9a4dc70`  
**Preceding Directives:** NET-380 / COS_SCORE V8.18.10  
**Rule 9.3 Review Status:** Skipped (surgical fix: ≤2 code files changed — only 1 application code file `add_coins_hub.dart` + 1 test file `p7_v8_ux_safety_test.dart` + version bumps in `pubspec.yaml` and `constants.dart`)

---

## 1. Test Verification Summary

- **`flutter analyze lib/`:** **0 issues found** (0 errors, 0 warnings). Ran in 38.4s.
- **`flutter test --reporter compact`:** **604/604 PASS** (baseline 603 + 1 new widget test `p7_v81811_cert_save_mint_mark_key`). Ran in 32s.

---

## 2. Fix Verification Matrix

| Fix | Description | Status | Verbatim Evidence in Commit Diff |
|---|---|---|---|
| **Fix 1** | Save key: `'MintMark'` → `'Mint Mark'` (with space). Remove `'MintMark'` save key completely. | **PASS** | `add_coins_hub.dart:3865` changed to `add_coins_hub.dart:3868` |
| **Fix 2** | Preserve preset mint: remove `_certManualMint.clear()` from `!_photoScanBanner` block; also initialize `_certManualMint` from `preset['mint']` / `preset['mintMark']` in `initState`. | **PASS** | `add_coins_hub.dart:3513` deleted; `add_coins_hub.dart:177-180` added |
| **Fix 3** | Widget test: `p7_v81811_cert_save_mint_mark_key` verifies save produces `'Mint Mark': 'S'`, no `'MintMark'` key, and source code assertion. | **PASS** | `p7_v8_ux_safety_test.dart:2463-2521` |
| **Fix 4** | Version bump to `8.18.11+81811` in `pubspec.yaml` and `kAppVersion = 'v8.18.11'` in `constants.dart`. | **PASS** | `pubspec.yaml:19`, `constants.dart:28` |

---

## 3. Verbatim File:Line Citations (Before → After from `git show 44c83f43`)

### Fix 1: Save key `'MintMark'` → `'Mint Mark'`
- **File:** `numista_mobile/lib/screens/add_coins_hub.dart`
- **Before (`b9cbc26a:3865`):**
```dart
        'MintMark':          _certManualMint.text.trim(),
```
- **After (`44c83f43:3868`):**
```dart
        'Mint Mark':         _certManualMint.text.trim(),
```

### Fix 2: Remove `_certManualMint.clear()` from `!_photoScanBanner` block & prefill in `initState`
- **File:** `numista_mobile/lib/screens/add_coins_hub.dart`
- **Before (`b9cbc26a:3510-3515`):**
```dart
        if (!_photoScanBanner) {
          _certManualGrade.clear();
          _certManualDenom.clear();
          _certManualMint.clear();
          _certManualNotes.clear();
        }
```
- **After (`44c83f43:3514-3518`):**
```dart
        if (!_photoScanBanner) {
          _certManualGrade.clear();
          _certManualDenom.clear();
          _certManualNotes.clear();
        }
```
- **InitState prefill added (`44c83f43:177-180`):**
```dart
      final mint = (preset['mint'] ?? preset['mintMark'])?.toString() ?? '';
      if (mint.isNotEmpty) {
        _certManualMint.text = mint;
      }
```

### Fix 3: Widget test for save producing `'Mint Mark': 'S'` and no `'MintMark'`
- **File:** `numista_mobile/test/p7_v8_ux_safety_test.dart`
- **Lines (`44c83f43:2463-2521`):**
```dart
    testWidgets('p7_v81811_cert_save_mint_mark_key', (WidgetTester tester) async {
      setTestViewSize(tester, width: 800, height: 2000);

      Map<String, dynamic>? interceptedPayload;

      final prevOverride = HttpAuthClient.httpClientOverride;
      HttpAuthClient.httpClientOverride = MockClient.streaming((request, bodyStream) async {
        if (request.url.path == '/api/cert_save') {
          final bodyBytes = await bodyStream.toBytes();
          final jsonMap = jsonDecode(utf8.decode(bodyBytes)) as Map<String, dynamic>;
          interceptedPayload = jsonMap['coin_data'] as Map<String, dynamic>?;
          return http.StreamedResponse(
            Stream.value(utf8.encode(jsonEncode({'status': 'ok'}))),
            200,
            headers: {'content-type': 'application/json'},
          );
        }
        return http.StreamedResponse(Stream.value(utf8.encode('{"detail":"not found"}')), 404);
      });
      addTearDown(() {
        HttpAuthClient.httpClientOverride = prevOverride;
      });

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(
            showCertFullScreen: true,
            initialCoinPreset: {
              'name': 'Morgan Dollar',
              'year': '1881',
              'mint': 'S',
              'certNo': '8321797',
              'grader': 'NGC',
            },
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Ensure 'S' is populated in the mint mark field
      expect(find.widgetWithText(TextField, 'S'), findsOneWidget);

      // Trigger save
      final saveBtn = find.text('Confirm & Add to My Collection');
      expect(saveBtn, findsOneWidget);
      await tester.ensureVisible(saveBtn);
      await tester.tap(saveBtn);
      await tester.pumpAndSettle();

      // Assert: the coin map contains 'Mint Mark': 'S'
      expect(interceptedPayload, isNotNull);
      expect(interceptedPayload!['Mint Mark'], equals('S'));
      // Assert: the coin map does NOT contain key 'MintMark' (no space variant)
      expect(interceptedPayload!.containsKey('MintMark'), isFalse);

      // Static source assertion confirming save block writes 'Mint Mark' and not 'MintMark'
      final hubSrc = File('lib/screens/add_coins_hub.dart').readAsStringSync();
      expect(hubSrc, contains("'Mint Mark':         _certManualMint.text.trim()"));
      expect(hubSrc.contains("'MintMark':"), isFalse);
    });
```

### Fix 4: Version bump
- **File:** `numista_mobile/pubspec.yaml:19`
- **Before:**
```yaml
version: 8.18.10+81810
```
- **After:**
```yaml
version: 8.18.11+81811
```
- **File:** `numista_mobile/lib/constants.dart:28`
- **Before:**
```dart
const String kAppVersion = 'v8.18.10';
```
- **After:**
```dart
const String kAppVersion = 'v8.18.11';
```

---

## 4. Confirmation of Zero `'MintMark'` Save Key

Grepping the entire `numista_mobile/lib/screens/add_coins_hub.dart` in commit `44c83f43` confirms:
- **`'MintMark':`** (save key dictionary assignment): **0 occurrences**
- Only non-save references remain: line 3508 reading preset key `widget.initialCoinPreset?['mintMark']`, and line 4352 reading external third-party API payload `data['MintMark']`.

---

## 5. Deployment Safety

- Zero live deployments performed.
- `main` strictly untouched.
- Work committed and pushed only to branch `p7-v8.9`.
