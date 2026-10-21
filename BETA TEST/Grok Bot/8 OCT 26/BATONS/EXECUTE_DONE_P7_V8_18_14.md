# EXECUTE DONE: P7 Add Coins Flow V8.18.14

**Date:** 2026-10-21 ~10:08 ET  
**Author:** AG CoS  
**Branch:** `p7-v8.9`  
**Commit SHA:** `cff5ab1bb32097843bcdebf195f5ce4a7df79396` (pushed cleanly to `origin/p7-v8.9`)  
**Parent Commit:** `a4a77e4c959514e3e8a2308637d169210d7bc88b`  
**Preceding Directives:** NET-400 (items a–f) and NET-401 (items 3, 4, 4-CRITICAL, 5)  
**Rule 6 / Rule 9.3 Review Status:** Complete (`BETA TEST\Grok Bot\8 OCT 26\BATONS\GEMINI38_REVIEW_P7_V8_18_14_BUILD.md`)

---

## 1. Quality Gates & Test Verification

- **`flutter analyze lib/`**: **0 issues found** (0 errors, 0 warnings). Ran in 340.8s.
- **`flutter test --reporter compact`**: **609/609 PASS** (100% green; baseline 609). Ran in 59s.
- **`pytest numista_backend/tests/ -q`**: **593 PASS**, 1 pre-existing import error (baseline was ≥587). Ran in 64s.
- **No live deploy performed**: Dev/p7 branches only. Nothing pushed to `main`. No direct writes to Firestore.

---

## 2. Requirement Verification Matrix

| Item | Requirement Description | Status | Exact file:line Implementation & Tests |
|---|---|---|---|
| **NET-400a** | **Invoice multi-object line_items merge:** When Gemini returns a list of objects containing `line_items`, concatenate all items across all objects. | **PASS** | `numista_backend/main.py:7692-7700`<br>`numista_backend/tests/test_invoice_fixtures.py:168-196` |
| **NET-400b** | **Quantity support in invoice rows & import:** Support item quantity (e.g. `Quantity: 2`), creating N separate coin docs in review queue and batches. | **PASS** | `numista_backend/main.py:7568-7585, 7755-7830`<br>`numista_backend/tests/test_invoice_fixtures.py:198-228` |
| **NET-400c** | **Supply filter & set normalization:** Skip supplies/folders lacking 4-digit years; normalize "Unknown Cent/Nickel" to `Denomination="Cent"` and `Program/Series="Cent & Nickel Set"`. | **PASS** | `numista_backend/main.py:7774-7795`<br>`numista_backend/tests/test_invoice_fixtures.py:198-228` |
| **NET-400d** | **Manual cert entry dual keys:** Manual saves write `certNo`, `cert_number`, `Certification Number`, `Cert #`, `grader`, `Grading Service`, `grading_service`. | **PASS** | `numista_mobile/lib/screens/add_coins_hub.dart:3962-3977`<br>`numista_mobile/test/cert_flow_test.dart:140-165` |
| **NET-400e** | **Graded condition preservation & export:** Never overwrite graded coins to 'Ungraded'; manual additions & add-another copies preserve grade and condition; CSV export checks Grade fallback and cert aliases. | **PASS** | `numista_mobile/lib/screens/add_coins_hub.dart:562-598, 3960-3976`<br>`numista_mobile/lib/services/backup_export_service.dart:271-285` |
| **NET-400f** | **Duplicate sweep case/aliases & multi-collection:** `_score_duplicate` normalizes case & checks key aliases; `_run_duplicate_sweep` checks `coins`, `collection`, `review_queue`. | **PASS** | `numista_backend/main.py:6891-6945`<br>`numista_backend/tests/test_invoice_fixtures.py:230-243` |
| **NET-401.3** | **Older-user sizing audit:** Scan Another (48px), Cancel (48px), Collapse Sidebar (48x48), tip and hint font sizes upgraded to 18px. | **PASS** | `numista_mobile/lib/screens/base_layout.dart:713-731`<br>`numista_mobile/lib/services/camera_capture_service_web.dart:199-214`<br>`numista_mobile/lib/screens/add_coins_hub.dart:2980, 3054, 4803-4835, 5606-5618` |
| **NET-401.4** | **NGC friendly not-found card:** Amber card naming cert # and grader searched, explaining direct lookup unavailable, offering 56px photo scan button and manual entry. | **PASS** | `numista_mobile/lib/screens/add_coins_hub.dart:3654-3690`<br>`numista_mobile/test/p7_v8_ux_safety_test.dart:1916-1970` |
| **NET-401.4-CRITICAL** | **PCGS cert lookup proxy & client fix:** Proxy logs `IsValidRequest` & `ServerMessage` safely (no tokens), returns 503 for quota/rate/auth, 404 for not found, normalizes `coinDetail`. Client handles 404 as null and 503 with friendly message. | **PASS** | `numista_backend/routes/pcgs_routes.py:71-105`<br>`numista_mobile/lib/services/pcgs_import_service.dart:154-168` |
| **NET-401.5** | **Slab photo OCR fallback & hint:** When cert # is unreadable/hidden (front of CACG clear slab), backend returns extracted year/grade/denom/mint with MEDIUM confidence & hint; frontend pre-fills fields and shows hint banner. | **PASS** | `numista_backend/routes/cert_routes.py:460-475`<br>`numista_mobile/lib/screens/add_coins_hub.dart:3430-3450` |
| **Version** | **Release version bump to v8.18.14:** Updated across all 4 release files. | **PASS** | `numista_mobile/pubspec.yaml:19`<br>`numista_mobile/lib/constants.dart:28`<br>`numista_mobile/lib/screens/home_dashboard.dart:1667`<br>`RELEASE_NOTES.md:405-419` |

---

## 3. Commit Information
- **Commit:** `cff5ab1bb32097843bcdebf195f5ce4a7df79396`
- **Branch:** `p7-v8.9` (pushed to `origin/p7-v8.9`)
- **Message:** `fix(p7-v8.18.14): invoice rows merge, qty, sets, manual save, graded condition, dedup, sizing, NGC friendly, PCGS lookup fix, label photo, v8.18.14`

Baton is passed to GROKCOS for UX Gate V7 scoring.
