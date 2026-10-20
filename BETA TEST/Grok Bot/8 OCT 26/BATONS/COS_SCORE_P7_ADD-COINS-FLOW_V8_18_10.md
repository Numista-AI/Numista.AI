# COS SCORE - P7 ADD-COINS-FLOW V8.18.10 BUILD
Scorer: Grok CoS | 2026-10-20 ~15:00 ET | Reviewed: code `89dc6305` on origin/p7-v8.9 (parent `8f28f7b1`, docs `0d3ccd51` on dev) + GEMINI38_REVIEW_P7_V8_18_10_BUILD.md + EXECUTE_DONE_P7_V8_18_10.md + NET-379. Independent re-run on Grok worktree `Temp\cos_wt_8189` checked out at 89dc6305.
Verdict: **FAIL (narrow, one data bug).** Items 1, 2, 3, 5, 6, 7 PASS. Item 4 shows the mint on screen but saves it under the wrong field name. Dev only. No deploys.

## Independent test re-run (Grok, 89dc6305)
- pytest tests/test_cert_lookup.py: **24 passed**
- flutter analyze lib/: **No issues found**
- flutter test --reporter compact: **600/600 All tests passed**

| # | NET-375 item | Score | Notes (independent, from `git show 89dc6305`) |
|---|-----------|-------|-------|
| 1 | Keep typed cert # until user chooses; dialog | **PASS** | `add_coins_hub.dart` scan handler: `final chosen = await showDialog<String>(` only when `typedCert.isNotEmpty && typedCert != certNum`. Title and body 18px; two `SizedBox(height: 56, width: double.infinity)` buttons `'Keep the number I typed ($typedCert)'` / `'Use the number on the photo ($certNum)'`. Dismiss: `chosenCert = chosen ?? typedCert;` (safe default). `_pcgsSingleCtrl.text = chosenCert;` and `_certPendingConfirm!['certNo'] = chosenCert;`. Label prefill runs either way. Amber "Using photo cert #" banner deleted. This is the truthfulness fix from V8.18.9 and it is real now. |
| 2 | Widget tests, both choices | **PASS** | `p7_v81810_cert_mismatch_dialog_keep_typed` taps keep, expects `find.widgetWithText(TextField, '1111111')`; `p7_v81810_cert_mismatch_dialog_use_photo` taps photo, expects `'8321797'`. Both assert 1881 / Morgan Dollar / MS-65 / S prefilled. Misnamed V8.18.9 test replaced. |
| 3 | Backend test really asserts no Firestore write | **PASS** | `patch("routes.cert_routes.db") as mock_db` + `mock_db.collection.assert_not_called()`. Patch target is real: `cert_routes.py:33 from routes.deps import ... db` and `db.collection(...)` at :68/:289/:332. |
| 4 | Photo mint visible on confirm screen | **FAIL (save key)** | Visible: PASS. New `_certManualMint` controller (declared, disposed, cleared on reset), `Expanded(child: _certManualField('Mint mark', _certManualMint, hint: 'e.g. S, D, CC'))` between Year and Grade, prefilled from `photoMint`, and from lookup `mint` when present. **Bug:** save writes `'MintMark': _certManualMint.text.trim(),` (add_coins_hub.dart ~:3865). Every other add path in the same file writes `'Mint Mark'` (with a space) at :562, :1888, :1927, :2063, :2545, and `coin_model.dart:251` writes `'Mint Mark'`. `coin_model.dart:173` reads MintMark only as a fallback, but raw-map readers use only `'Mint Mark'`: `backup_export_service.dart:256` (CSV export), `batch_valuation_service.dart:168`, `morgan_chat_context.dart:319`, `set_expansion_helper.dart:91/138/174`, and `coin_normalizer_service.dart:92-93` would treat these coins as missing a mint. So a cert-added 1881-S would export, value and show to Morgan with no mint. **Smaller bug:** in the lookup-not-found `else` branch, the new block sets `_certManualMint` from `initialCoinPreset['mint'/'mintMark']`, then the existing `if (!_photoScanBanner) { ... _certManualMint.clear(); }` wipes it, so a preset mint is lost when there is no photo scan. |
| 5 | No `coin_name` claim unless extracted | **PASS** | Synthetic `[photoYear, photoMint, photoDenom].join(' ')` prefill removed; coin name now only from lookup or user. NET-379/EXECUTE_DONE say the same. |
| 6 | Version bump | **PASS** | `pubspec.yaml version: 8.18.10+81810`; `constants.dart kAppVersion = 'v8.18.10'`. |
| 7 | GEMINI38 script-paste discipline | **PASS** | Checked all 362 code lines in the review against the real diff and source: 360 match verbatim; the 2 misses are emoji lines garbled by file encoding, not invented code. No fabricated blocks this time. Minor: used `git diff 8f28f7b1..89dc6305` instead of the ordered `b40d2355..`, acceptable because 89dc6305 is a single commit on top of 8f28f7b1. |
| 8 | p7-v8.9 only, explicit add, no deploy | **PASS** | 5 files only (test_cert_lookup.py, constants.dart, add_coins_hub.dart, pubspec.yaml, p7_v8_ux_safety_test.dart). main untouched at 3c1bacf5. No deploy. |

## Truthfulness
NET-379 and EXECUTE_DONE describe only code that the commit contains. Good. The `MintMark` key was simply not caught.

## Non-blocking notes (for UX gate, not this fix)
- `_photoScanTypedCert` is now dead (`// ignore: unused_field`); fine to delete.
- Year / Mint mark / Grade now share one row with three Expanded fields at 18px; UX Designer should check it at 360px phone width.
- Order deviation: NET-375 said GreySheet hotfix first. V8.18.10 landed 14:35, hotfix `1ddb1d1f` landed 14:45 on hotfix/greysheet-bid-display (8 files, +741/-523; home_dashboard.dart alone 605 lines, possible line-ending churn). NET-374 not filed yet, so the hotfix is not scored.

## Next (NET-380)
V8.18.11, small, `add_coins_hub.dart` + its test only (2 files, so GEMINI38 skipped per Rule 9.3):
1. Save key `'Mint Mark'` (with the space), same as every other add path. Do not also write `MintMark`.
2. Remove the `_certManualMint.clear()` inside the `if (!_photoScanBanner)` block so a preset mint survives.
3. Widget test: after keep-typed or use-photo plus Save, the saved coin map has `'Mint Mark': 'S'` and no `'MintMark'` key.
4. Bump 8.18.11+81811 / v8.18.11.
But first: file NET-374 for hotfix `1ddb1d1f` (Eric's priority), with tests and a `git diff --stat --ignore-all-space` so Grok can see whether home_dashboard.dart is real change or line endings.

Live smoke this watch (14:58 ET): numista.ai 200, numista-vault.web.app 200, /api/spot_prices 200, /api/collection 401 unauth, main.dart.js 200.
