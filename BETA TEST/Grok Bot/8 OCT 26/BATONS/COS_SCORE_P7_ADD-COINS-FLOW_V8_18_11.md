# COS SCORE - P7 ADD-COINS-FLOW V8.18.11 BUILD
Scorer: Grok CoS | 2026-10-20 ~15:35 ET | Reviewed: code `44c83f43` on origin/p7-v8.9 (parent `b9cbc26a`, docs `a8d5abd7` on dev) + EXECUTE_DONE_P7_V8_18_11.md + NET-382. GEMINI38 skipped per NET-380 / Rule 9.3 (2 code files + 2 version lines); Grok quotes the code below from `git show 44c83f43`. Independent re-run on Grok worktree `Temp\cos_wt_8189` checked out at 44c83f43.
Verdict: **PASS (code).** All 4 NET-380 items met. Dev only. No deploys.

## Independent test re-run (Grok, 44c83f43)
- flutter analyze lib/: **No issues found** (52.0s)
- flutter test --reporter compact: **604/604 All tests passed**
- flutter test --plain-name p7_v81811: **1/1 passed**
- Commit scope: 4 files, +68/-4 (constants.dart, add_coins_hub.dart, pubspec.yaml, p7_v8_ux_safety_test.dart). origin/main still 3c1bacf5.

| # | NET-380 item | Score | Evidence (from `git show 44c83f43`) |
|---|---|---|---|
| a | Save key `'Mint Mark'`, no `MintMark` | **PASS** | `-        'MintMark':          _certManualMint.text.trim(),` / `+        'Mint Mark':         _certManualMint.text.trim(),` in `coinDoc` (add_coins_hub.dart:3868). The same `coinDoc` goes to `/api/cert_save` (dup check, `..remove('Added')`) and to `FirebaseFirestore.instance.collection(AuthService.coinsPath).add(coinDoc)` at :3915-3917, so Firestore now gets `'Mint Mark'`. Grep of the file at 44c83f43: no `'MintMark':` write key left; remaining `MintMark` text is the PCGS API read at :4352 and a comment. Matches the other add paths (:566, :1892, :1931, :2067, :2549) and `coin_model.dart:251`. Backend `cert_routes.py:185` `coin_detail.get("MintMark")` reads the PCGS API payload, not our coin map, so unaffected. |
| b | Preset mint survives lookup-not-found | **PASS** | Removed `-          _certManualMint.clear();` from the trailing `if (!_photoScanBanner)` block (:3514-3518). The not-found branch still sets mint from `initialCoinPreset['mint'/'mintMark']` (:3509-3510) or clears it only when there is no preset and no photo scan (:3511-3512), so nothing stale is kept. Post-save reset still clears it (:3928). Bonus: `initState` now prefills `_certManualMint` from the preset (:177-180), same pattern as Year. |
| c | Widget test: `'Mint Mark': 'S'`, no `MintMark` | **PASS (note)** | `p7_v81811_cert_save_mint_mark_key` intercepts the real `/api/cert_save` body and asserts `interceptedPayload!['Mint Mark'], equals('S')` and `interceptedPayload!.containsKey('MintMark'), isFalse`, plus a source check. Re-run green. Note: it reaches Save through the preset path, not after the cert # dialog as NET-380 asked. Accepted because every cert/photo path saves through the one `coinDoc` map, so the key is proven either way. No test yet for the not-found branch keeping a preset mint; add it with the next P7 touch (non-blocking). |
| d | Version bump | **PASS** | `version: 8.18.11+81811`; `kAppVersion = 'v8.18.11'`. |
| e | Truthfulness / scope | **PASS** | NET-382 and EXECUTE_DONE quote only lines that are in the commit. Explicit add, p7-v8.9 only, no deploy, main untouched. Minor: AG's baton stamp "~19:10 ET" is UTC; real time ~15:18 ET. |

## Non-blocking notes (for the UX/FT gate)
- Year / Mint mark / Grade share one row (3 Expanded fields, 18px); UX Designer to check at 360px phone width (carried from V8.18.10).
- `_photoScanTypedCert` still dead (`// ignore: unused_field`); delete on next touch.
- FT must add one cert coin with a mint (e.g. an S-mint slab on the grokbot account) and confirm the mint shows in My Collection, CSV export and Morgan, not only on the card.

## Next
1. AG: GreySheet hotfix rev 2 now, per AG's own NET-382B plan (approved, see NET-382C). Report as NET-383.
2. P7 baton -> GROKCOS_WILCO (gate phase). After hotfix rev 2 is scored and ported to p7-v8.9, Grok CoS refreshes the p7-gate preview + tagged backend from p7-v8.9 HEAD, then UX Designer + Field Tester re-gate (HARD: invoice PDF import end to end, cert-photo scan under 30 s, mint saved as above). Then Eric's deploy YES (cherry-pick onto a branch from main).

Live smoke this watch (15:33 ET): numista.ai 200, numista-vault.web.app 200, /api/spot_prices 200, /api/collection 401 unauth, main.dart.js 200.