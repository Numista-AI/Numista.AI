# EXECUTE DONE: P7 Add Coins Flow V8.18.15

**Date:** 2026-10-21 ~13:58 ET  
**Author:** AG CoS  
**Branch:** `p7-v8.9`  
**Commit SHA:** `2aa65b50d3e9482c849be146e29667eec489074a` (pushed cleanly to `origin/p7-v8.9`)  
**Parent Commit:** `cff5ab1bb32097843bcdebf195f5ce4a7df79396`  
**Preceding Directives:** NET-400, NET-401, NET-404, NET-406, NET-408, NET-410, NET-411, NET-413  
**Rule 6 / Rule 9.3 Review Status:** Complete (`BETA TEST\Grok Bot\8 OCT 26\BATONS\GEMINI38_REVIEW_P7_V8_18_15_BUILD.md`)

---

## 1. Quality Gates & Test Verification

- **`flutter test test/p7_v8_ux_safety_test.dart --plain-name "p7_v81815"`**: **8/8 PASS** (100% green; covers 400d, 400e, 401.3, 401.4, 410, 408n, 413p, 413q).
- **`flutter analyze lib/`**: **0 issues found** (0 errors, 0 warnings; clean in 58.9s).
- **`pytest numista_backend/tests/test_invoice_fixtures.py numista_backend/tests/test_cert_lookup.py`**: **39/39 PASS** (100% green; includes mocked PCGS 200/404/503 routes, 4 label-photo fixtures, and 092052 acceptance test).
- **Line Ending Hygiene**: LF-only line endings strictly preserved in `numista_mobile/lib/screens/add_coins_hub.dart` (zero CRLF churn).
- **No live deploy performed**: Dev/p7 branches only. Nothing pushed to `main`. No direct writes to Firestore.

---

## 2. Requirement Verification Matrix

| Item | Requirement Description | Status | Exact file:line Implementation & Tests |
|---|---|---|---|
| **NET-400a** | **Invoice multi-object line_items merge:** Merge all `line_items` across list of dicts via production `normalize_and_validate_receipt`. | **PASS** | `numista_backend/main.py:7389-7402`<br>`numista_backend/tests/test_invoice_fixtures.py:135-156` |
| **NET-400b** | **Quantity support in invoice rows & import:** Expand items by `quantity` into separate coin docs in review queue and batches. | **PASS** | `numista_backend/main.py:7413-7421, 7545-7552`<br>`numista_backend/tests/test_invoice_fixtures.py:159-224` |
| **NET-400c** | **Supply filter & set normalization:** Skip supply/folder rows lacking 4-digit years; normalize "Unknown Cent/Nickel" to `Denomination="Cent"` and `Program/Series="Cent & Nickel Set"`. | **PASS** | `numista_backend/main.py:7442-7470`<br>`numista_backend/tests/test_invoice_fixtures.py:205-265` |
| **NET-400d** | **Manual cert entry dual keys:** Manual saves write `Year`, `certNo`, `cert_number`, `Certification Number`, `Cert #`, `grader`. | **PASS** | `numista_mobile/lib/screens/add_coins_hub.dart:3962-3977`<br>`numista_mobile/test/p7_v8_ux_safety_test.dart:2711-2761` |
| **NET-400e** | **Graded condition preservation:** Never overwrite graded coins to 'Ungraded'; manual additions save grade (e.g. MS65) and retain condition. | **PASS** | `numista_mobile/lib/screens/add_coins_hub.dart:562-598, 3960-3976`<br>`numista_mobile/test/p7_v8_ux_safety_test.dart:2763-2821` |
| **NET-400f** | **Duplicate sweep case/aliases & multi-collection:** `_score_duplicate` normalizes case & checks key aliases across `coins`, `collection`, `review_queue`. | **PASS** | `numista_backend/main.py:6891-6945`<br>`numista_backend/tests/test_invoice_fixtures.py:270-295` |
| **NET-401.3** | **Older-user sizing audit:** Button heights >= 48px; Scan Another & Cancel sized >= 48px; text wrapped with `FittedBox` scaleDown at 360dp width. | **PASS** | `numista_mobile/lib/screens/add_coins_hub.dart:5685-5705`<br>`numista_mobile/test/p7_v8_ux_safety_test.dart:2823-2852` |
| **NET-401.4** | **NGC friendly not-found card:** Amber card naming cert # and grader searched, explaining direct lookup unavailable, offering >=56px photo scan button and manual entry. | **PASS** | `numista_mobile/lib/screens/add_coins_hub.dart:3654-3690`<br>`numista_mobile/test/p7_v8_ux_safety_test.dart:2854-2905` |
| **NET-401.4-CRITICAL** | **PCGS cert lookup proxy & client fix:** Proxy logs `IsValidRequest` & `ServerMessage` safely (no tokens), returns 503 for quota, 404 for not found. Client handles 404 as null and 503 with friendly message. | **PASS** | `numista_backend/routes/pcgs_routes.py:71-105`<br>`numista_backend/tests/test_cert_lookup.py:703-757` |
| **NET-401.5** | **Slab photo OCR fallback:** 4 fixtures (PCGS front+rear, CACG front hint+rear); front of CACG slab returns hint to photo rear; pre-fills fields. | **PASS** | `numista_backend/routes/cert_routes.py:460-475`<br>`numista_backend/tests/test_cert_lookup.py:759-861` |
| **NET-404g** | **Android Take Photo greeter routing:** Morgan greeter tile routes to `Add New Coins` tab `camera` on phone, avoiding Microscope Scanner. | **PASS** | `numista_mobile/lib/widgets/morgan_greeter.dart:196-204` |
| **NET-404h** | **Microscope screen overflow & feedback button:** Screen padding responsive (88dp on phone); server offline text wrapped with `Flexible`; server banner hidden on native phone. | **PASS** | `numista_mobile/lib/screens/microscope_scan_screen.dart:224-232, 297-300, 319-370` |
| **NET-406j-m** | **Phone layout list #1:** Data-driven checklist count via `BetaChecklistService.allTasks.length`; DASHBOARD title wrapped in `FittedBox` scaleDown; single-column phone layout. | **PASS** | `numista_mobile/lib/screens/home_dashboard.dart:627-645`<br>`numista_mobile/lib/widgets/beta_welcome_dialog.dart:154-184` |
| **NET-408n** | **Portrait resolutions zero overflow:** Tested at 360x640, 412x892, 457x812dp with zero RenderFlex overflow. | **PASS** | `numista_mobile/test/p7_v8_ux_safety_test.dart:2947-2971` |
| **NET-410** | **Mobile native gating (`isNativePhone`):** `isNativePhone = !kIsWeb && (Platform.isAndroid || Platform.isIOS)` via conditional imports; web unconditionally returns `false`. | **PASS** | `numista_mobile/lib/utils/platform_gate.dart:1-8`<br>`numista_mobile/lib/utils/_platform_gate_io.dart:1-4`<br>`numista_mobile/lib/utils/_platform_gate_stub.dart:1`<br>`numista_mobile/test/p7_v8_ux_safety_test.dart:2907-2945` |
| **NET-413p** | **Landscape scroll & feedback button clamp:** Wrap entry cards in `SingleChildScrollView` with 88dp bottom padding on phone; feedback button clamped within safe area margins. | **PASS** | `numista_mobile/lib/screens/add_coins_hub.dart:824-836`<br>`numista_mobile/lib/widgets/beta_feedback_widget.dart:55-66`<br>`numista_mobile/test/p7_v8_ux_safety_test.dart:2973-3004` |
| **NET-413q** | **Low-RAM Android camera lost-data recovery:** `CameraRecoveryService.retrieveLostData()` called on initialization; memory reduced to 1600x1600 @ quality 75; byte reading protected. | **PASS** | `numista_mobile/lib/services/camera_recovery_service.dart:1-58`<br>`numista_mobile/lib/services/camera_capture_service_mobile.dart:6-28`<br>`numista_mobile/lib/screens/add_coins_hub.dart:169-189`<br>`numista_mobile/test/p7_v8_ux_safety_test.dart:3006-3040` |
| **Version** | **Release version bump to v8.18.15:** Updated across all 4 release files. | **PASS** | `numista_mobile/pubspec.yaml:23`<br>`numista_mobile/lib/constants.dart:28`<br>`numista_mobile/lib/screens/home_dashboard.dart:1736`<br>`RELEASE_NOTES.md:4` |

---

## 3. NET-410 KEEP-WEB / GATE-NATIVE Audit Table

Per NET-410 directives, every mobile phone change is gated behind `isNativePhone` so that `numista.ai` in any browser (desktop or mobile browser) remains 100% UNCHANGED:

| File & Line | Breakpoint / Change | Status | Rationale |
|---|---|---|---|
| `numista_mobile/lib/screens/add_coins_hub.dart:824-836` | `SingleChildScrollView` with 88dp bottom padding | **GATE-NATIVE** | Applies only when `isNativePhone` is true; web retains standard card layout. |
| `numista_mobile/lib/widgets/beta_feedback_widget.dart:58-66` | Clamped right/bottom within safe area | **GATE-NATIVE** | Prevents FAB from overlapping navigation bar or floating off-screen on phones. |
| `numista_mobile/lib/screens/home_dashboard.dart:627-645` | Single column DASHBOARD header + `FittedBox` | **GATE-NATIVE** | Web displays standard multi-column layout; phone displays single-column header. |
| `numista_mobile/lib/widgets/morgan_greeter.dart:196-204` | Route to 'Add New Coins' tab 'camera' | **GATE-NATIVE** | Phones route to native camera; web routes to Webcam / Camera Scanner. |
| `numista_mobile/lib/screens/microscope_scan_screen.dart:299` | Hide hardware server offline banner | **GATE-NATIVE** | Phones do not run localhost hardware server; web continues to display hardware status. |
| `numista_mobile/lib/screens/add_world_item_screen.dart:271` | Width < 700 responsive form layout | **KEEP-WEB** | Web UX responsive form layout for tablet/narrow browser windows. |
| `numista_mobile/lib/screens/program_manager_screen.dart:459, 583` | Width < 650 responsive tab layout | **KEEP-WEB** | Responsive tab and table display for narrow browser windows. |
| `numista_mobile/lib/screens/program_manager_screen.dart:967` | Width < 700 responsive modal card width | **KEEP-WEB** | Responsive modal width on web. |
| `numista_mobile/lib/screens/program_manager_screen.dart` | Font 13 -> 16px | **KEEP-WEB** | Eric's older-user legibility standard (all text >= 16/18px). |

---

## 4. NET-413 `image_picker` Call Sites Audit Table

Every `image_picker` call site across the codebase was audited for low-RAM stability, memory limits, and error handling:

| File & Line | Purpose | Max Dimensions & Quality | Error & Byte Handling | Status |
|---|---|---|---|---|
| `lib/services/camera_capture_service_mobile.dart:7-25` | Primary mobile camera photo capture | 1600x1600, quality 75 | Try/catch around `readAsBytes()`, friendly SnackBar on failure | **OPTIMIZED & PROTECTED** |
| `lib/services/camera_recovery_service.dart:18-55` | Android killed-activity lost data recovery | Native result | Safe byte read with `RecoveredCameraData`, logs errors safely | **ACTIVE (Android Only)** |
| `lib/screens/add_coins_hub.dart:169-188` | On-init check for recovered camera photo | Native result | Auto-routes recovered photo to AI camera tab with success toast | **ACTIVE & GATED** |
| `lib/screens/add_coins_hub.dart:3284-3320` | Slab label photo picker | 1600x1600 (phone) / 1920 (web), quality 75/85 | Try/catch around `readAsBytes()` with inline error message | **OPTIMIZED & PROTECTED** |
| `lib/screens/add_coins_hub.dart:5090` | Photo gallery upload fallback | Default (Gallery) | User selects existing file from gallery | **AUDITED** |
| `lib/screens/add_world_item_screen.dart:129` | World item image picker | Default | Standard gallery/camera picker | **AUDITED** |
| `lib/screens/ai_chat_screen.dart:233` | AI chat photo attachment | Default | Standard chat attachment picker | **AUDITED** |
| `lib/screens/coin_detail_screen.dart:4330` | Coin detail photo replacement | 2000x2000, quality 90 | Standard replacement picker | **AUDITED** |
| `lib/screens/my_collection_screen.dart:4973, 5438` | Collection screen photo edit | 2000x2000, quality 90 | Standard collection photo picker | **AUDITED** |
| `lib/screens/login_screen.dart:1104` | Login sample coin capture | Default | Standard onboarding photo picker | **AUDITED** |
| `lib/services/camera_capture_service_web.dart:166` | Web browser photo fallback | Default | Web-only file picker | **AUDITED (Web Only)** |

---

## 5. PCGS Cert 53652580 Real API Response

When querying cert number `53652580` via PCGS API, the raw API response received and logged by the proxy is:
```json
{
  "IsValidRequest": false,
  "ServerMessage": "No data found for this certification number."
}
```
- **Proxy Status**: Mapped cleanly to HTTP 404 Not Found with payload `{"detail": {"error": "not_found", "message": "No data found for this certification number."}}`.
- **Security Check**: API authentication tokens are NEVER logged in logs, tracebacks, or client responses.
- **Client Handling**: Mobile client receives 404, handles as `null` coin detail without crashing, and presents the friendly Amber NGC/PCGS not-found card with the 56px label photo button.

---

## 6. Open Hardware Checks (Pending Eric's USB Android Test Phone)

The following items are complete in code and verified in unit/widget tests, but remain open until verified on Eric's physical USB Android test phone (TCL T609C, Android 13):
1. **NET-404g**: Native phone 'Take Photo' opens the camera directly (verified in code via `morgan_greeter.dart` routing).
2. **NET-413q**: 5 camera photos in a row on low-RAM Android each reach the AI ID step without activity death or dropped images.

---

## 7. Commit Information
- **Commit:** `2aa65b50d3e9482c849be146e29667eec489074a`
- **Branch:** `p7-v8.9` (pushed cleanly to `origin/p7-v8.9`)
- **Message:** `fix(p7-v8.18.15): GEMINI38 redo, tests, LF restore, isNativePhone, camera recovery, phone layout, v8.18.15`

Baton is passed to GROKCOS for UX Gate V8.18.15 scoring.
