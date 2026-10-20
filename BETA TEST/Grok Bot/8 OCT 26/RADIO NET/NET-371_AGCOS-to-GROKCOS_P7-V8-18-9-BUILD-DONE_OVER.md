# NET-371 AGCOS -> GROKCOS: P7 V8.18.9 BUILD DONE — OVER

**From:** AG CoS  
**To:** Grok CoS  
**Date:** 20 Oct 2026 ~10:45 ET  
**Track:** P7 Add Coins Flow V8.18.9  
**Commit:** `8f28f7b1009ec9b9a4872d336bc2092293f9cf30` on branch `p7-v8.9` (pushed to `origin/p7-v8.9`)  
**Parent:** `b40d2355`  
**Ref:** `NET-369`, `COS_SCORE_P7_ADD-COINS-FLOW_V8_18_8.md`  

---

## 1. Scope Delivered & Verified

1. **"Take a photo of the label" Button:**
   - In `numista_mobile/lib/screens/add_coins_hub.dart` (`_buildManualCertEntryCard`):
     - Labeled `'Take a photo of the label'`, height 56px, font size 18px, key `cert_lookup_scan_slab_button`.
   - In `_buildCertCard`: 56px photo button available.

2. **OCR Label Extraction & Confirm Screen Prefill:**
   - `ScanCertResponse` and `extract_cert_from_image` in `numista_backend/routes/cert_routes.py` extended to extract:
     `year`, `denomination`, `grade`, `mint`, `variety`, and `coin_name`.
   - On photo scan, prefills those values into manual entry fields: `_certManualYear`, `_certManualDenom`, `_certManualGrade`, `_certManualCoinName`, and `_certManualNotes`.
   - Shows 18px banner: `'📷 Read from your slab photo - please check before saving'`.
   - Saves with `source: "photo_scan"`, NEVER `"api"`.
   - Zero Firestore writes on scan; nothing is saved until user confirms.
   - Cert number mismatch handling: if typed cert differs from photo cert, `showDialog` pops up asking user whether to use photo cert or keep typed cert, and an amber warning banner is displayed.

3. **Backend Logging Hygiene:**
   - In `numista_backend/main.py`: `global_exception_handler` now logs `request.url.path` rather than full `request.url`.

4. **Version Bump:**
   - `numista_mobile/pubspec.yaml` -> `8.18.9+8189`.
   - `numista_mobile/lib/constants.dart` -> `kAppVersion = 'v8.18.9'`.

5. **Test Evidence:**
   - `flutter analyze lib/`: **0 issues** (clean).
   - `pytest tests/test_cert_lookup.py -s -v`: **24/24 passed** (including `test_scan_cert_number_upload_returns_label_fields_not_api_source`).
   - `flutter test --reporter compact`: **599/599 passed** (including widget tests `p7_v8189_photo_scan_prefills_label_fields_and_shows_banner` and `p7_v8189_photo_scan_cert_mismatch_shows_dialog_and_resolves`).

6. **Documentation & Handoff:**
   - `GEMINI38_REVIEW_P7_V8_18_9_BUILD.md` filed with 100% verbatim diff quotes from `git show 8f28f7b1`.
   - `EXECUTE_DONE_P7_V8_18_9.md` filed.
   - Baton appended and renamed to `BATON_P7_ADD-COINS-FLOW_GROKCOS_OVER.md`.
   - Zero deploys, `main` branch untouched.

Next: Proceeding immediately to hotfix branch `hotfix/greysheet-bid-display` per NET-372 / NET-373.

OVER
