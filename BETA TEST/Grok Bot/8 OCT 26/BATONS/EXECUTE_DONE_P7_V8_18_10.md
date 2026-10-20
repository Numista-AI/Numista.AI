# EXECUTE DONE: P7 Add Coins Flow V8.18.10

**Date:** 2026-10-20 ~14:40 ET  
**Author:** AG CoS  
**Branch:** `p7-v8.9`  
**Commit SHA:** `89dc630526c51ba1a4b2a42d0e2bd48f128a60dc` (pushed to `origin/p7-v8.9`)  
**Parent Commit:** `8f28f7b1009ec9b9a4872d336bc2092293f9cf30`  
**Preceding Directives:** NET-375 / NET-378  

---

## 1. Test Verification Summary

- **`flutter analyze lib/`:** **0 issues found** (0 errors, 0 warnings).
- **`flutter test --reporter compact`:** **600/600 PASS** (baseline 599 + 1 net test increase from splitting mismatch test into keep_typed and use_photo).
- **`pytest tests/test_cert_lookup.py -v`:** **24/24 PASS** (baseline 24).

---

## 2. Items 1–7 Scope Checklist

| Item | Description | Status | Evidence in Diff |
|------|-------------|--------|------------------|
| **Item 1** | Cert # conflict: real `showDialog` presenting BOTH cert numbers, 18px text, two 56px tall full-width buttons ("Keep the number I typed", "Use the number on the photo"), safe default on dismiss, chosen cert # sent to `_pcgsSingleCtrl.text` and `_certPendingConfirm['certNo']`, label prefill either way | **PASS** | `add_coins_hub.dart:3266-3331` (real `showDialog<String>` with 18px text and two 56px buttons; amber warning banner removed from confirm card) |
| **Item 2** | Widget tests for both dialog choices (`p7_v81810_cert_mismatch_dialog_keep_typed` and `p7_v81810_cert_mismatch_dialog_use_photo`) replacing old banner test | **PASS** | `p7_v8_ux_safety_test.dart:2308-2462` (both widget tests pass and assert prefilled fields and cert text) |
| **Item 3** | Backend test actually asserts no Firestore write with `mock_db.collection.assert_not_called()` | **PASS** | `test_cert_lookup.py:686-693` (patches `routes.cert_routes.db` and asserts `assert_not_called()`) |
| **Item 4** | Photo mint visible on confirm screen: dedicated `_certManualMint` controller, rendered in 'Mint mark' field between Year and Grade, saved to `coinDoc['MintMark']`, visible even if coin name prefilled | **PASS** | `add_coins_hub.dart:102, 251, 3280, 3479, 3655, 3865, 3925` |
| **Item 5** | Do not claim `coin_name` unless extracted: removed synthetic string concatenation prefill from `_scanSlabPhoto` | **PASS** | `add_coins_hub.dart:3284` (removed `[photoYear, photoMint, photoDenom].join(' ')`) |
| **Item 6** | Version bump to `8.18.10+81810` in `pubspec.yaml` and `kAppVersion = 'v8.18.10'` in `constants.dart` | **PASS** | `pubspec.yaml:19`, `constants.dart:28` |
| **Item 7** | GEMINI38 build review filed with strict script-paste discipline from `git diff 8f28f7b1..89dc6305` | **PASS** | `GEMINI38_REVIEW_P7_V8_18_10_BUILD.md` filed in `BATONS\` |

---

## 3. Verbatim File:Line Citations from Commit Diff

1. **Item 1 (Cert # mismatch real dialog):**
   `numista_mobile/lib/screens/add_coins_hub.dart:3266`
   `+ final chosen = await showDialog<String>(`
2. **Item 2 (Widget tests):**
   `numista_mobile/test/p7_v8_ux_safety_test.dart:2308`
   `+ testWidgets('p7_v81810_cert_mismatch_dialog_keep_typed', (tester) async {`
   `numista_mobile/test/p7_v8_ux_safety_test.dart:2385`
   `+ testWidgets('p7_v81810_cert_mismatch_dialog_use_photo', (tester) async {`
3. **Item 3 (Backend test assertion):**
   `numista_backend/tests/test_cert_lookup.py:693`
   `+ mock_db.collection.assert_not_called()`
4. **Item 4 (Mint visible on confirm card):**
   `numista_mobile/lib/screens/add_coins_hub.dart:3655`
   `+ Expanded(child: _certManualField('Mint mark', _certManualMint, hint: 'e.g. S, D, CC')),`
5. **Item 5 (No coin_name synthetic claim):**
   `numista_mobile/lib/screens/add_coins_hub.dart:3284`
   `- _certManualCoinName.text = [photoYear, photoMint, photoDenom].where((s) => s.isNotEmpty).join(' ');`
6. **Item 6 (Version bump):**
   `numista_mobile/lib/constants.dart:28`
   `+ const String kAppVersion = 'v8.18.10';`
   `numista_mobile/pubspec.yaml:19`
   `+ version: 8.18.10+81810`

---

## 4. Deployment Safety

- Zero live deployments performed.
- `main` and `dev` branches strictly untouched during worktree build.
- All changes committed to branch `p7-v8.9` and pushed to `origin/p7-v8.9`.
