# EXECUTE_DONE: P7 V8.14 Build

**Date:** 2026-10-17 17:48 ET  
**Author:** AG CoS  
**Branch:** `p7-v8.9`  
**Commit SHA:** `f48d15e3f8be8f82ae97000cd017be6dae688d38` (short: `f48d15e3`)  
**Git Push Target:** `origin/p7-v8.9` (pushed `86f646da..f48d15e3`)  
**Flutter Analyze:** 0 errors, 0 warnings (`No issues found! (ran in 6.3s)`)  
**Flutter Test:** 580/580 passed (+3 new tests over baseline 577)  
**Backend Pytest:** 17/17 passed (`test_cert_lookup.py`)  

---

## 1. Summary of Changes & Fixes (NET-299 / Exhibits 1–7)

| Item (NET-299) | Description | Verbatim File & Line Cites (`git show f48d15e3`) | Verification |
|---|---|---|---|
| **Fix 1: AI Photo ID Slab Label Precedence & Anti-Counterfeit Guard** | Slab label wins over visual coin design impression; prevents false counterfeit/holder mismatch accusations on single/inverted photos; extracts and saves `Grading Service` and `Certification Number` with review screen editable fields and user overrides. | `numista_backend/main.py:5464-5545, 6140-6334`<br>`numista_mobile/lib/screens/add_coins_hub.dart:129-130, 232, 4640-4642, 4717-4719, 4770-4775, 5100-5107` | **PASS (code + backend + Flutter test)** |
| **Fix 2: Photo Work Area Expanded & Uncropped Preview** | Replaced 160x160 circular crop (`ClipOval`) with rounded rectangle `minHeight: 200, maxHeight: 280, minWidth: double.infinity` with `BoxFit.contain` and 18px prompt text: "Tap to take a photo or choose from your library". | `numista_mobile/lib/screens/add_coins_hub.dart:4786-4835, 4948-4956` | **PASS (widget test)**<br>Tested in `p7_v814_take_photo_full_screen_routing_and_prompt` |
| **Fix 3: "Take a photo" Direct Routing** | "Take a photo" card now routes directly to full-screen AI Photo ID screen with AppBar, BackButton, and uncropped capture area instead of Microscope Scanner. | `numista_mobile/lib/screens/add_coins_hub.dart:35, 633-641, 663-677` | **PASS (widget test)**<br>Tested in `p7_v814_quick_add_card_take_photo_and_cert_labels` |
| **Fix 4: Bulk Import Multi-File Drop & Directory Traversal** | Supported multi-file drop, recursive folder ingestion via `webkitGetAsEntry()`, deduplication, and added "Clear" button to badge. | `numista_mobile/web/add_coins.html:608-665, 678-707` | **PASS (code audit)** |
| **Fix 5: Bulk Import Auth Headers, 90s Timeout & Error Reset** | Added `Authorization: Bearer <token>` via `getAuthHeader()`, 90s `AbortController` timeout, `@app.options("/api/import/upload")` preflight handler, and retry button on upload failure. | `numista_backend/main.py:6986-6991`<br>`numista_mobile/web/add_coins.html:778-830, 880` | **PASS (code audit)** |
| **Fix 6: CACG (Rebranded CAC) Systemic Support** | Added CACG to cert auto-detection, cert lookup API and manual fallback, invoice extraction prompts, settings preferred services, and cert lookup chips & verify link (`cacgrading.com/cert-verify/$certNo`). | `numista_backend/routes/cert_routes.py:78-80, 149-152, 219-223`<br>`numista_backend/main.py:2218, 2341`<br>`numista_mobile/lib/screens/settings_screen.dart:1950`<br>`numista_mobile/lib/screens/add_coins_hub.dart:2778-2780, 2847-2852, 3249-3251, 3326-3329, 3481-3484` | **PASS (pytest + Flutter test)**<br>Tested in `p7_v814_cacg_cert_chips_and_auto_detection` |

---

## 2. Verification Commands & Outputs

1. **`flutter analyze lib/`**
   ```
   Analyzing lib...
   No issues found! (ran in 6.3s)
   ```
   0 errors, 0 warnings.

2. **`flutter test --reporter compact`**
   ```
   00:22 +580: All tests passed!
   ```
   Baseline: 577 -> 580 (+3 new automated tests). 100% passed.

3. **`pytest tests/test_cert_lookup.py`**
   ```
   ====================== 17 passed, 250 warnings in 8.05s =======================
   ```
   100% passed.

4. **`git push origin p7-v8.9`**
   ```
   To https://github.com/Numista-AI/Numista.AI.git
      86f646da..f48d15e3  p7-v8.9 -> p7-v8.9
   ```

---

## 3. Scope and Policy
- Files modified in worktree: `numista_backend/main.py`, `numista_backend/routes/cert_routes.py`, `numista_mobile/lib/screens/add_coins_hub.dart`, `numista_mobile/lib/screens/settings_screen.dart`, `numista_mobile/test/p7_v8_ux_safety_test.dart`, `numista_mobile/web/add_coins.html`.
- No generated files or untracked DB files committed.
- Branch `p7-v8.9` pushed cleanly to origin.
- Baton renaming reserved for parent AG CoS.
