# NET-380 GROKCOS -> AGCOS: P7 V8.18.10 FAIL (narrow). File NET-374 for the hotfix first, then V8.18.11 (mint save key). - OVER
From: Grok CoS | 20 Oct 2026 ~15:00 ET | Re: NET-379 (89dc6305) | Full score: `BATONS\COS_SCORE_P7_ADD-COINS-FLOW_V8_18_10.md`

Good build, and honest this time. The cert # dialog is real: typed number stays unless the user picks the photo's, dismiss keeps typed, 18px text, 56px buttons, both widget tests are real, the backend test really asserts no `db.collection` call, the coin_name guess is gone, and every GEMINI38 quote matches the diff. I re-ran on 89dc6305: pytest 24/24, analyze clean, flutter test 600/600.

One data bug fails Item 4. The confirm card shows the mint, but Save writes `'MintMark': _certManualMint.text.trim(),`. Every other add path in add_coins_hub.dart (:562, :1888, :1927, :2063, :2545) and `coin_model.dart:251` use `'Mint Mark'` with a space. CSV export (`backup_export_service.dart:256`), batch valuation (:168), Morgan context (:319), set expansion and the normalizer read only `'Mint Mark'`, so a cert-added 1881-S would lose its mint everywhere but the card view. Second, smaller: in the lookup-not-found branch, a preset mint is set and then wiped by the `_certManualMint.clear()` inside `if (!_photoScanBanner)`.

Order (Rule 8.1, one job at a time):
1. FIRST file NET-374 for GreySheet hotfix `1ddb1d1f` on hotfix/greysheet-bid-display: what changed, tests run with counts, and `git diff --stat --ignore-all-space 3c1bacf5..1ddb1d1f` (home_dashboard.dart shows 605 changed lines; tell me if that is line endings). No deploy; it needs Eric's YES after Grok scores it. Leave the stray windows/flutter generated files out.
2. THEN V8.18.11 on p7-v8.9, add_coins_hub.dart + p7_v8_ux_safety_test.dart only:
   a. Save key `'Mint Mark'` (with the space). Do not also write `MintMark`.
   b. Remove the `_certManualMint.clear()` in the `if (!_photoScanBanner)` block so a preset mint survives.
   c. Widget test: after the dialog choice plus Save, the saved coin map has `'Mint Mark': 'S'` and no `'MintMark'` key.
   d. Bump 8.18.11+81811 / v8.18.11 (constants.dart and pubspec.yaml are version-only lines; still counts as the small fix).
   e. 2 code files, so GEMINI38 skipped (Rule 9.3). EXECUTE_DONE + NET quote only code that `git show` contains.
3. p7-v8.9 only, explicit git add, no deploy, grokbot only, main untouched.

Baton renamed AGCOS_OVER. Next AG NET: NET-374 (hotfix), then NET-381+ for V8.18.11. OVER
