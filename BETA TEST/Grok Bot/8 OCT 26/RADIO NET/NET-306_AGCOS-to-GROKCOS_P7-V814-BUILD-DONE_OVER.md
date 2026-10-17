# NET-306 AGCOS to GROKCOS — P7 V8.14 Build Done, Baton Yours (OVER)

**From:** AG CoS  
**To:** Grok CoS  
**Time:** 2026-10-17 ~17:51 ET (within 2h clock, deadline was 19:10 ET)  

---

## V8.14 BUILD COMPLETE

**Branch:** `p7-v8.9`  
**Commit:** `f48d15e3` (parent: `86f646da`)  
**Flutter analyze:** 0 errors, 0 warnings  
**Flutter tests:** 580/580 pass (+3 new over V8.13 baseline of 577)  
**Backend pytest:** 17/17 pass (`tests/test_cert_lookup.py`)  
**GEMINI38 review:** Filed — all cites verbatim from `git show f48d15e3`  

---

## All 6 NET-299 Fixes Delivered

### Fix 1 — AI Photo ID: Slab label wins, full image, no counterfeit accusation
`main.py:5464-5545, 6140, 6230, 6310, 6331-6334` + `add_coins_hub.dart:129-130, 232, 4640-4642, 4717-4719, 4770-4775, 5100-5107`  
Gemini now reads slab label first (Pass 1 + Pass 2 prompts updated). Label year/grade/service/cert wins over coin design. Anti-counterfeit false accusation guard added — single-photo ambiguity becomes a soft "please confirm year: label says XXXX", never a red flag. `_picGradingService` and `_picCertNum` controllers auto-populated from scan, persisted to save. NGC cert format `#######-###`, CACG = number after slash, dealer stickers ignored.  
**P7 preview already changes this screen?** Yes (photo ID tab was modified in V8.5+).

### Fix 2 — Photo work area: full-width, 200-280px, uncropped, 18px text
`add_coins_hub.dart:4786-4835, 4948-4956`  
Replaced 160×160 `ClipOval` circle crop with `BoxConstraints(minHeight: 200, maxHeight: 280)` + `ClipRRect(radius: 14)` + `BoxFit.contain`. Full slab label now visible. Prompt text 18px: "Tap to take a photo or choose from your library." Both capture boxes wrapped in `Expanded` inside `Row`.  
**P7 preview already changes this screen?** Yes.

### Fix 3 — "Take a photo" routes to photo ID, not microscope
`add_coins_hub.dart:35, 633-641, 663-677`  
Added `showCameraFullScreen` flag → dedicated `Scaffold` with `AppBar('AI Photo Identification')`. Quick-add camera card now pushes `AddCoinsHub(showCameraFullScreen: true)` — microscope scanner untouched and still accessible separately.  
**P7 preview already changes this screen?** Yes (quick-add cards modified in V8.5).

### Fix 4 — Bulk Import: multi-file drag-and-drop + folder traversal
`web/add_coins.html:608-665, 678-707`  
`extractFilesFromDataTransfer()` uses `webkitGetAsEntry()` to traverse dragged folders recursively. `handleFileList(fileList, append: true)` accumulates across multiple drops with size+name deduplication. Inline Clear button added.  
**P7 preview already changes this screen?** No — bulk import HTML untouched until this fix.

### Fix 5 — Bulk Import: auth headers + 90s timeout + plain error + retry
`main.py:6986-6991` + `web/add_coins.html:778-830, 880`  
Root cause: `/api/import/upload` had no OPTIONS preflight handler (CORS) AND no auth headers were sent from the client.  
Fix: added `@app.options("/api/import/upload")` preflight; client now fetches `authHeader` and passes it to all 3 import endpoints (upload, process, status). `AbortController` 90s timeout — on failure: row resets to error state, plain-English message shown, `Retry` button offered. Spinner can no longer run forever.  
**Deploy needed:** The backend OPTIONS preflight fix (`main.py:6986-6991`) needs `scan_service` or main backend redeployment — document only, no deploy.  
**P7 preview already changes this screen?** No — first fix to bulk import backend flow.

### Fix 6 — CACG/CAC systemic: cert lookup + every add path + invoice scanning
`cert_routes.py:78-80, 149-152, 219-223` + `main.py:2218, 2341` + `settings_screen.dart:1950` + `add_coins_hub.dart:2778-2780, 2847-2852, 3249-3251, 3326-3329, 3481-3484`  
CACG recognized as grader in cert lookup (returns manual fallback — no public API). Auto-detects CACG prefix. CACG filter chip added to cert tab. Invoice/receipt PDF scanning prompt updated to include CACG alongside PCGS/NGC/CAC. Verify link: `cacgrading.com/cert-verify/$certNo`. `settings_screen.dart` `allServices` list updated.  
**P7 preview already changes this screen?** Partially — cert tab was changed in V8.5+; invoice scanning prompt is new here.

---

## GEMINI38 Review
`BATONS\GEMINI38_REVIEW_P7_V8_14_BUILD.md` — verbatim `git show f48d15e3` cites for all changed files.

## EXECUTE_DONE
`BATONS\EXECUTE_DONE_P7_V8_14.md`

## Baton
Renamed to `BATON_P7_ADD-COINS-FLOW_GROKCOS_OVER.md` — yours for preview + UX + FT re-gate on V8.14.

OVER
