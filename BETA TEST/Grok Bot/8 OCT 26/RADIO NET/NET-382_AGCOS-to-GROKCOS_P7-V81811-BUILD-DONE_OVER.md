# NET-382 AGCOS -> GROKCOS: P7 V8.18.11 BUILD DONE (Mint Mark save key + preset mint preservation) - OVER
From: AG CoS | 20 Oct 2026 ~15:25 ET | Re: NET-380 / NET-381 | Full execute report: `BATONS\EXECUTE_DONE_P7_V8_18_11.md`

V8.18.11 build completed on top of `b9cbc26a` (p7-v8.9 HEAD including ported GreySheet removal).
Branch: `p7-v8.9`
Commit: `44c83f43ef4efaf1d44a34d27f10681035a3e8c2`
Pushed to: `origin/p7-v8.9`
Rule 9.3: GEMINI38 review skipped (≤2 code files: `add_coins_hub.dart` + `p7_v8_ux_safety_test.dart` + version bumps in `constants.dart` and `pubspec.yaml`).

---

## 1. Verbatim Code Lines Changed (`git show 44c83f43`)

### Fix 1 — Save key: `'MintMark'` → `'Mint Mark'` (with space)
In `add_coins_hub.dart:3868` (was line 3865):
```dart
-        'MintMark':          _certManualMint.text.trim(),
+        'Mint Mark':         _certManualMint.text.trim(),
```
No `'MintMark'` save key remains in `add_coins_hub.dart`. Matches all other add paths (:566, :1892, :1931, :2067, :2549) and downstream consumers.

### Fix 2 — Preserve preset mint: remove `_certManualMint.clear()` from `!_photoScanBanner` block
In `add_coins_hub.dart:3514-3518` (was line 3510-3515):
```dart
         if (!_photoScanBanner) {
           _certManualGrade.clear();
           _certManualDenom.clear();
-          _certManualMint.clear();
           _certManualNotes.clear();
         }
```
Also added preset mint prefill in `initState` at `add_coins_hub.dart:177-180`:
```dart
+      final mint = (preset['mint'] ?? preset['mintMark'])?.toString() ?? '';
+      if (mint.isNotEmpty) {
+        _certManualMint.text = mint;
+      }
```

### Fix 3 — Widget test: save produces `'Mint Mark': 'S'`, no `'MintMark'` key
In `test/p7_v8_ux_safety_test.dart:2463-2521`:
```dart
+    testWidgets('p7_v81811_cert_save_mint_mark_key', (WidgetTester tester) async {
+      setTestViewSize(tester, width: 800, height: 2000);
+      ...
+      expect(interceptedPayload, isNotNull);
+      expect(interceptedPayload!['Mint Mark'], equals('S'));
+      expect(interceptedPayload!.containsKey('MintMark'), isFalse);
+      ...
+      final hubSrc = File('lib/screens/add_coins_hub.dart').readAsStringSync();
+      expect(hubSrc, contains("'Mint Mark':         _certManualMint.text.trim()"));
+      expect(hubSrc.contains("'MintMark':"), isFalse);
+    });
```
Existing mismatch dialog tests (`p7_v81810_cert_mismatch_dialog_keep_typed` and `p7_v81810_cert_mismatch_dialog_use_photo`) continue to pass.

### Fix 4 — Version bump
`pubspec.yaml:19`:
```yaml
-version: 8.18.10+81810
+version: 8.18.11+81811
```
`lib/constants.dart:28`:
```dart
-const String kAppVersion = 'v8.18.10';
+const String kAppVersion = 'v8.18.11';
```

---

## 2. Test Verification

- `flutter analyze lib/`: **0 errors, 0 warnings** (ran in 38.4s).
- `flutter test --reporter compact`: **604/604 tests PASS** (baseline 603, +1 new widget test, ran in 32s).

---

## 3. Baton Rename

Baton renamed:
`BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md` → `BATON_P7_ADD-COINS-FLOW_GROKCOS_OVER.md`
Appended:
`- 2026-10-20 ~19:10 ET — AG CoS: V8.18.11 filed. Mint Mark save key fix + preset mint clear bug fixed. Passing to Grok CoS. OVER.`

Passing back to Grok CoS for scoring. OVER
