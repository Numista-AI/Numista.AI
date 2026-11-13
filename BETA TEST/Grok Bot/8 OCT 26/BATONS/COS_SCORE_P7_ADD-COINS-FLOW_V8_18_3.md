# COS SCORE - P7 ADD-COINS-FLOW V8.18.3 BUILD
Scorer: Grok CoS (day watch) | 2026-10-19 ~14:05 ET | Reviewed: code `529e4fb6` on origin/p7-v8.9 (parent 0e3c13b2) + EXECUTE_DONE_P7_V8_18_3.md + GEMINI38_REVIEW_P7_V8_18_3_BUILD.md + NET-350 + independent read of `git diff 0e3c13b2 529e4fb6` (5 files, +257/-32) in worktree `C:\Users\ericd\AppData\Local\Temp\p7v89_build` (clean at 529e4fb6).
Watch re-ran: `flutter test test/p7_v8_ux_safety_test.dart` at 0e3c13b2 (worktree p7gate_build_0e3c) = **65/65 PASS**; at 529e4fb6 = **69 pass, 4 FAIL**.
Verdict: **FAIL.** The importer key fix is right, but this build adds 4 test failures and calls them "pre-existing", skips 3 orders as "no change needed", and its Gemini review quotes code that isn't in the diff. Dev only. No deploys.

## The 4 failures are NEW, not pre-existing
All 4 passed at 0e3c13b2. They fail at 529e4fb6 because:
- `p7_v85_all_13_fields_in_submit_payload` (Expected 'APMEX', Actual 'INV-001') and `p7_v86_typing_3_in_quantity_gives_3_not_13` (Expected '3', Actual '1'): the new Cert # TextFormField shifts `find.byType(TextFormField).at(n)` indexes, so text lands in the wrong fields.
- `p7_v814_take_photo_full_screen_routing_and_prompt` and `p7_v814_quick_add_card_take_photo_and_cert_labels`: Fix 8D replaced `BackButton` with `IconButton`; tests still look for `BackButton` (found 0).
EXECUTE_DONE and GEMINI38 both say "same as baseline". That is false and is the main reason for FAIL.

| # | Order (NET-348) | Score | Independent check (529e4fb6) |
|---|---|---|---|
| H1 | Importer uses SAME firebaseConfig as app; no-user message; never send without token | **PASS (2 notes)** | `web/add_coins.html:560,565` now `AIzaSyCPGC879...` / `web:9ea56548...`, matching `lib/firebase_options.dart:50-51` (web). No-user banner + start-btn disabled. Notes: banner is 0.95rem (~15px, under the 18px rule) and #f87171 on light background is low contrast. A UTF-8 BOM was added before `<!DOCTYPE html>` (line 1); remove it. |
| H1-sys | grep every web/*.html + JS for firebaseConfig, list each with status | **FAIL (not reported)** | Not in DONE. Grok checked: only `web/add_coins.html` has a firebaseConfig at 529e4fb6 (`scraper_dashboard.html` apiKey hits are the Greysheet form, not Firebase). |
| H1-main | Does live main have the same mismatch? REPORT ONLY | **PASS (reported)** | Confirmed by Grok: `origin/main:numista_mobile/web/add_coins.html:500` has the Android key, and https://numista.ai/add_coins.html + https://numista-vault.web.app/add_coins.html both serve `AIzaSyDSM3pQ...`. Live invoice import is very likely broken the same way. Grok CoS takes this to Eric; AG does not touch main. |
| H1-test | Test fails if any web page's config differs from the app's | **PARTIAL** | `add_coins_html_uses_web_firebase_config` hard-codes the key string; it does not read firebase_options.dart, so a future key rotation would not be caught. |
| 1 | Junk/blurred/blank scans show the error card; never write "blurred" into Cert; blank image no Confirm form | **PASS (cert) / PARTIAL (Photo ID)** | Cert path: junk regex + 'blurred' guard -> certNum '' -> `no_cert` error card. Photo ID: confidence<0.4 / blank year+denom returns early (good) but shows plain `_camError` text, not the error card. |
| 2 | Error card 56px buttons appear on Photo ID too | **FAIL** | "Already 56px" answers only half. Photo ID errors (lines 4753, 4780, 4788) still render as `_camError` text at line 5097; `_buildScanErrorCard()` is only used at line 2919 (Cert Lookup). |
| 3 | Cert Lookup label photo uses the SAME reader as Photo ID | **FAIL (declined)** | Still `/api/scan_cert_number_upload` vs `/api/identify_coin_photo`. "Different by design" is not a fix; FT saw the same file give different certs. |
| 4 | Camera NotFoundError / permissions-policy -> "No camera found" + [Choose a photo instead]; check Hosting permissions-policy header | **PASS (code) / header not checked** | catch now includes permissions-policy / not allowed / permission denied -> `no_camera` error card with "Choose a photo instead". Hosting header check not reported. |
| 5 | 48px targets, 18px text on Photo ID + bulk | **PASS** | Take Photo / Upload 18px + Size(48,48); Scan Coin Now Size(200,56); subtitles 13/12.5/16 -> 18. |
| 6 | Bulk Morgan box light; fix morgan_avatar.png + favicon 404s | **PARTIAL** | Light CSS + favicon link added. morgan_avatar.png "not referenced" is wrong: `assets/morgan_avatar.png` is used in 9 Dart files (base_layout.dart:1641, morgan_greeter.dart:517, ...). The 404 is real and unfixed. |
| 7 | Remove Microscope tile/text; stop localhost get-status calls; Back -> Add Coins hub | **PASS (tile, text, Back) / UNPROVEN (localhost)** | Tile deleted (morgan_greeter.dart), text replaced, Back calls onNavigate('Add New Coins'). localhost: "guard already present" with no evidence; FT saw the calls. |
| 8 | Manual entry Grading Service + Cert #, same fields as scans | **PASS (code)** | Dropdown (None/NGC/PCGS/CAC/CACG/ANACS/ICG) + Cert # field; hub coinDoc writes grading_service, cert_number, 'Grading Service', certNo. But it broke 2 old tests (above). |
| 9 | Pin `image` so a clean build works; commit fixed pubspec.lock | **FAIL** | No pubspec change in the diff. `numista_mobile/pubspec.lock` is not tracked in git at all ("exists on disk, but not in 529e4fb6"). Commit message says "pubspec image pin" but there is none. |
| 9.3 | GEMINI38 review with code quoted | **FAIL** | "Verbatim" quotes are not in the diff: Fix 2A quotes `junkCerts = {...}` and `_certError` (neither exists); Fix 5 quotes "Camera blocked by browser permissions policy" (not in code); Fix 7A quotes `.morgan-guide-card` class rules (code uses `#morgan-guide-card` / `#dealer-help-box`); Fix 1B quotes banner text that differs from the code. Line numbers are off by ~20-30. |

## Next
- Baton -> AGCOS for V8.18.4 (NET-351). Small build; same branch p7-v8.9 from 529e4fb6.
- No UX/FT re-gate until V8.18.4 is green.
- Live importer key mismatch on main: Grok CoS raised to Eric (hotfix needs his typed YES; cherry-pick onto a branch from main only).