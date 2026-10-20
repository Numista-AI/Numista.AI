# EXECUTE DONE: P7 Add Coins Flow V8.18.9

**Date:** 2026-10-20 ~10:45 ET  
**Author:** AG CoS  
**Branch:** `p7-v8.9`  
**Commit SHA:** `8f28f7b1009ec9b9a4872d336bc2092293f9cf30` (pushed to `origin/p7-v8.9`)  
**Parent:** `b40d2355`  
**Preceding Directives:** `NET-369` / `COS_SCORE_P7_ADD-COINS-FLOW_V8_18_8.md`  

---

## 1. Summary of Delivered Work

1. **"Take a photo of the label" Button & OCR Prefill:**
   - Renamed button in `numista_mobile/lib/screens/add_coins_hub.dart` (`_buildManualCertEntryCard`) to `"Take a photo of the label"` (height 56px, font size 18px, key `cert_lookup_scan_slab_button`).
   - Extended `ScanCertResponse` and `extract_cert_from_image` in `numista_backend/routes/cert_routes.py` to extract printed label fields: `year`, `denomination`, `grade`, `mint`, `variety`, and `coin_name`.
   - On photo scan, prefills those fields into `_certManualYear`, `_certManualDenom`, `_certManualGrade`, `_certManualCoinName`, and `_certManualNotes`.
   - Shows 18px banner: `"📷 Read from your slab photo - please check before saving"`.
   - Tags source as `source: "photo_scan"`, NEVER `"api"`.
   - Nothing is saved to Firestore or cached until user explicitly taps "Confirm & Add to My Collection".
   - Cert # conflict handling: if photo cert differs from typed cert, a modal dialog (`showDialog`) asks user whether to use the photo cert or keep the typed cert, and an amber warning banner highlights the difference.

2. **Backend Logging Hygiene:**
   - In `numista_backend/main.py`: `global_exception_handler` now logs `request.url.path` rather than full `request.url` with query parameters.

3. **Version Bump:**
   - `numista_mobile/pubspec.yaml` bumped to `8.18.9+8189`.
   - `numista_mobile/lib/constants.dart` `kAppVersion` bumped to `v8.18.9`.

4. **Testing Evidence:**
   - `flutter analyze lib/`: **0 issues** (clean).
   - `flutter test --reporter compact`: **599/599 passed**.
     - `test/p7_v8_ux_safety_test.dart` includes `p7_v8189_photo_scan_prefills_label_fields_and_shows_banner` and `p7_v8189_photo_scan_cert_mismatch_shows_dialog_and_resolves`.
   - `pytest tests/test_cert_lookup.py -s -v`: **24/24 passed**.
     - Includes `test_scan_cert_number_upload_returns_label_fields_not_api_source` verifying `source != "api"`, label fields returned, and zero Firestore writes.

5. **Review:**
   - `GEMINI38_REVIEW_P7_V8_18_9_BUILD.md` filed with exact verbatim diff lines from `git show 8f28f7b1`.

6. **Deploy Status:**
   - Zero deploys, `main` branch untouched.
