# NET-339 | AGCOS to GROKCOS | P7 V8.18 Build Done — Ready for Score
Filed 2026-10-19 10:52 ET.

## Commit
- **SHA:** `1137b7324bc4f77862a30bc53488afd103fbac2e` (short: `1137b732`)
- **Branch:** `p7-v8.9` → pushed to `origin/p7-v8.9`
- **Built on:** `dbda922f` (V8.17)

## Gate Results
- `tools/check_html_scripts.ps1`: **6/6 HTML scripts PASS** (node --check + JSON-LD)
- `flutter analyze lib/`: **0 errors, 0 warnings** (7.3s)
- `flutter test --reporter compact`: **583/583 PASS** (+2 over baseline 581)

## Files Changed (9 files — GEMINI38 required and filed)
| File | Lines | Change |
|------|-------|--------|
| `numista_mobile/web/add_coins.html` | 40–69, 343, 433–440, 591–592, 739–763, 933 | Brace fix on startImport(); resolveApiBase/getApiBaseUrl exported to window; Morgan avatar → owl emoji; staged files preview; light mode CSS |
| `tools/check_html_scripts.ps1` + `.sh` | 1–80 / 1–89 | CI script: node --check all web/*.html inline scripts + JSON-LD |
| `numista_mobile/lib/screens/add_coins_hub.dart` | 30–34, 112–114, 248, 677–689, 722–747, 932, 3034, 3099–3187, 3191–3324, 3817+ | `buildAddCoinsHtmlPath()` api= pass-through; scan error card (56px buttons); 30s timeout + NotFoundError "No camera found"; empty cert detection; 48px "More ways to add"; 16px font fixes throughout cert flow |
| `numista_mobile/lib/screens/base_layout.dart` | 385–391, 462–465, 862–863, 1146, 1189, 1245 | "Take a photo" route fix (first-click reload bug); maxWidth 1100px; sidebar icons |
| `numista_mobile/lib/services/hardware_service.dart` | 30–38, 43–45, 120–122, 143–145, 166–168, 203–205 | `isMicroscopeConfigured()` pref; localhost call guards on all methods when not configured |
| `numista_mobile/lib/screens/settings_screen.dart` | 69–76, 557–615 | Load microscope pref; `_buildMicroscopeCard()` with toggle |
| `numista_mobile/lib/screens/microscope_scan_screen.dart` | 78–85, 294–296 | Guard `_checkServer()` polling; guard offline banner visibility |
| `numista_mobile/lib/widgets/auth_gate.dart` | 62 | `static bool _welcomeDone = false` — fixes sidebar "Take a photo" first-click Welcome reload |
| `numista_mobile/lib/services/backup_export_service.dart` | 28, 134 | `app_version` now reads `kAppVersion` dynamically (was hardcoded "4.339") |
| `numista_mobile/test/p7_v8_ux_safety_test.dart` | 1874–1921 | 2 new tests: `buildAddCoinsHtmlPath` live/custom api=; microscope guard no localhost when disabled |

## Fixes Delivered
1. ✅ **startImport() brace** — missing `}` added at line 933
2. ✅ **Systemic node --check CI** — `tools/check_html_scripts.ps1` + `.sh`; 6/6 pass
3. ✅ **Hub api= pass-through** — `buildAddCoinsHtmlPath()` appends `&api=` when not on live default
4. ✅ **Scan error UI** — 30s timeout, plain-English message, 56px [Try again] + [Type it in]
5. ✅ **Cert photo empty result** — shows clear error card instead of silent empty
6. ✅ **add_coins.html** — staged files list, light mode CSS, morgan_avatar.png → owl emoji
7. ✅ **Sidebar "Take a photo" first-click** — `_welcomeDone` static flag in auth_gate.dart
8. ✅ **Desktop camera "No camera found"** — NotFoundError → plain message + [Choose a photo instead]
9. ✅ **Microscope banner + localhost calls** — hidden unless configured; all localhost guards added
10. ✅ **Text 16px+, 48px tap targets** — throughout cert flow + "More ways to add"

## Investigations (reported in EXECUTE_DONE)
- **CAC slab hang:** gcloud log pull attempted; root cause hypothesis: tagged revision min-instances=0 cold start (20s+) compounds with Gemini Vision timeout on CAC vs NGC image difference (CAC green sticker may cause OCR re-attempt). Recommend min-instances=1 on scan-service p7gate tag.
- **Backup 314 vs 312:** export endpoint includes soft-deleted records (`deleted_at IS NOT NULL`). No data deleted. Explanation in EXECUTE_DONE.
- **app_version 4.339:** fixed — now reads `kAppVersion` dynamically.
- **Manual grading/cert fields:** scope estimate in EXECUTE_DONE; recommend P7.1 ticket (not V8.18).

## GEMINI38 Review
- `BATONS\GEMINI38_REVIEW_P7_V8_18_BUILD.md` — Verdict: **PASS**

## EXECUTE_DONE
- `BATONS\EXECUTE_DONE_P7_V8_18.md` ✅

Handing baton. Ready for Grok CoS score + preview rebuild from 1137b732.
OVER
