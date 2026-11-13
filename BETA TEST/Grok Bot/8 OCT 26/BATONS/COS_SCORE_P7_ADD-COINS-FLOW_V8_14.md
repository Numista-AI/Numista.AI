# COS SCORE - P7 ADD-COINS-FLOW V8.14 BUILD
Scorer: Grok CoS (watch) | 2026-10-17 18:05 ET | Reviewed: code `f48d15e3` on origin/p7-v8.9 (parent 86f646da) + EXECUTE_DONE_P7_V8_14.md + GEMINI38_REVIEW_P7_V8_14_BUILD.md + NET-306 + independent read of `git show f48d15e3` in worktree `C:\Users\ericd\AppData\Local\Temp\p7v89_build` (6 files: main.py, cert_routes.py, add_coins_hub.dart, settings_screen.dart, p7_v8_ux_safety_test.dart, add_coins.html).
Verdict: **PASS (code).** All 6 NET-299 MUST-FIXES are in. GEMINI38 hygiene PASS (spot-checked). Dev only. No deploys.

| # | Item (NET-299) | Score | Independent file:line (f48d15e3) |
|---|---|---|---|
| 1 | AI Photo ID: slab label wins, full image, no counterfeit accusation | **PASS (code)** | Prompt: `main.py:5466-5476` SLAB LABEL WINS + soft "Please confirm year" + dealer-sticker ignore; Pass2 `:5531-5534` never counterfeit from rotation. Persist: `:6331-6334` Grading Service / Certification Number with overrides. Flutter: `_picGradingService`/`_picCertNum` controllers; populate `:4640-4642`, overrides on confirm `:4717-4719`, editable fields `:5100-5107`. Upload sends raw `Uint8List` via `MultipartFile.fromBytes` (`:4596-4610`, `:4690-4701`) — display crop was never applied to bytes. ClipOval gone from camera picker. |
| 2 | Photo work area: full-width 200-280px, uncropped, 18px text | **PASS (code)** | `add_coins_hub.dart:4787-4790` BoxConstraints minHeight 200 / maxHeight 280 / minWidth infinity; `:4807-4831` ClipRRect + BoxFit.contain; prompt "Tap to take a photo or choose from your library" 18px. Both boxes in Expanded Row `:4951-4953`. Re-ran `p7_v814_take_photo_full_screen_routing_and_prompt`: **PASS**. |
| 3 | "Take a photo" -> AI Photo ID, not microscope | **PASS (code)** | `showCameraFullScreen` flag `:35`; dedicated Scaffold AppBar 'AI Photo Identification' `:633-641`; quick-add card pushes `AddCoinsHub(showCameraFullScreen: true)` `:663-677`. Microscope path untouched. Re-ran `p7_v814_quick_add_card_take_photo_and_cert_labels`: **PASS**. |
| 4 | Bulk Import: multi-file drop + folder traversal | **PASS (code)** | `web/add_coins.html` `extractFilesFromDataTransfer` + `webkitGetAsEntry` recursive; `handleFileList(..., append: true)` with size+name dedupe; Clear button. |
| 5 | Bulk Import: auth + 90s timeout + plain error + retry | **PASS (code); needs backend redeploy to test live** | Client: `getAuthHeader` Bearer on upload/process/status; `AbortController` 90s; Retry button + plain error; spinner cannot run forever. Backend: `@app.options("/api/import/upload")` `:6986-6990` (same pattern as identify_coin_photo `:5556-5569`); POST already `Depends(get_current_user)`. **Live "Failed to fetch" will stay until main backend (or the import host) is redeployed — Eric typed YES required; document only, no deploy this score.** |
| 6 | CACG/CAC systemic: cert + every add path + invoice PDF | **PASS (code)** | `cert_routes.py`: CACG auto-detect prefix, manual fallback (no public API), verify `cacgrading.com/cert-verify/{cert}`. Invoice prompts in `main.py` list CACG beside PCGS/NGC/CAC. Flutter: CACG chip, helper text, verify link; `settings_screen.dart:1950` allServices includes CACG. Re-ran `p7_v814_cacg_cert_chips_and_auto_detection`: **PASS**. |

## GEMINI38 hygiene: PASS
Spot-checked against `git show f48d15e3:<path>`: main.py 5466-5476 and 6331-6334; add_coins_hub 4787-4790 / 4640-4642 / 5100-5107; OPTIONS 6986-6990; CACG cert_routes + settings allServices. Lines and quotes match. One review per version (Rule 9.3) — good.

## Soft (not blocking; fold if cheap on next touch)
- OPTIONS preflight returns bare `FastAPIResponse(200)` and relies on CORSMiddleware to attach ACAO headers (matches identify_coin_photo). FT on preview after backend redeploy should confirm preflight; if browsers still fail, return explicit Access-Control-* headers on the OPTIONS response.
- V8.13 soft still open: share one payload builder between real export and the `mockCoins` test hook.

## Gates / Next
- Code PASS. Holder stays **GROKCOS_OVER**.
- Next for Grok CoS: ONE preview on fixed channel **p7-gate** (reuse, do not mint a new channel) built from f48d15e3 / p7-v8.9 tip, then UX Designer + Field Tester re-gate covering V8.10 through V8.14.
- Before FT can clear PDF / Bulk Import live: ask Eric for typed YES to redeploy scan_service (PDF CORS) and main backend (import OPTIONS + auth). Until then FT marks those BLOCKED-BY-DEPLOY, not FAIL.
- AG: Rule 9 stand-down (baton with GROKCOS). No parallel tracks. Queued P1/P4/P5/P6/P8/P9/P10 remain Rule 8 WAIT behind P7.
- No ERIC baton, no deploy YES for live site. Deploy later = cherry-pick approved commits onto a branch from main, only on Eric's typed YES.
