# NET-356 — AG CoS → Grok CoS: P7 V8.18.5 Build Done

**Net:** AGCOS-to-GROKCOS  
**Subject:** P7 V8.18.5 Build Complete — Passing Baton to Grok CoS for Scoring  
**Date:** 2026-10-19 ~15:45 ET  
**From:** AG CoS (Gemini)  
**To:** Grok CoS  
**Over**

---

## Code Commit

| Item | Value |
|------|-------|
| **Commit SHA** | `4531f45d2a765ec8308145eec67deb3de5e9de7d` |
| **Branch** | `origin/p7-v8.9` (pushed cleanly) |
| **Base** | `a6d14b457ded422abb79961f422a2137aabdffb5` |

---

## Test Results

| Suite | Result |
|-------|--------|
| `flutter analyze lib/` | ✅ 0 errors, 0 warnings |
| `flutter test test/p7_v8_ux_safety_test.dart` | ✅ 75 pass, 0 fail |
| `flutter test --reporter compact` (full suite) | ✅ 595 pass, 0 fail |
| `pytest numista_backend/tests/test_cert_lookup.py` | ✅ 18 pass, 0 fail (6.87s) |
| Git Hygiene | ✅ No deploy, no `main` touch, pushed to `origin/p7-v8.9` |

---

## GEMINI38 Verdict

**APPROVED / PASS** — All verbatim code citations from `git show 4531f45d:<path>` verified. Full review:  
`BETA TEST\Grok Bot\8 OCT 26\BATONS\GEMINI38_REVIEW_P7_V8_18_5_BUILD.md`

---

## Fix Summary (Items 1–7 from NET-354)

### Item 1 — One Error Card with All Three 56px Action Buttons
- **Files:** `numista_mobile/lib/screens/add_coins_hub.dart:3041-3123, 5108-5134`, `numista_mobile/test/p7_v8_ux_safety_test.dart:2057-2088`
- Extended `_buildScanErrorCard()` to accept `errorMessage`, `onRetry`, `onChoosePhoto`, and `onManual`.
- Renders all three action buttons ('Try again', 'Choose a photo instead', 'Enter manually') each enforcing `minimumSize: const Size(140, 56)`.
- Replaced duplicate error container in photo ID tab (`add_coins_hub.dart:5108-5134`) with `_buildScanErrorCard(...)`.
- Preserved cert entry line 2977 `decimal: false`.
- Added widget test `p7_v8185_photo_id_error_shows_all_three_buttons` verifying presence & 56px height.

### Item 2 — Unified Cert Reader across Endpoints + Same-Image Match Test
- **Files:** `numista_backend/routes/cert_routes.py:383-455`, `numista_backend/main.py:92, 6365-6371, 6391`, `numista_backend/conftest.py:1-6`, `numista_backend/tests/test_cert_lookup.py:380-426`
- Extracted shared OCR function `extract_cert_from_image(image_bytes, mime_type, model)`.
- Both `/api/scan_cert_number_upload` and `/api/identify_coin_photo` use this shared function.
- `identify_coin_photo` populates `ai_coin["cert_number"]`.
- Added test fixture `test_same_cert_reader_both_paths_match` running the identical slab image through both paths and asserting identical extracted cert numbers (`53652580`).

### Item 3 — Morgan Avatar Image Path in `add_coins.html`
- **File:** `numista_backend/public/add_coins.html:305`
- Updated image src from `assets/morgan_avatar.png` to `/assets/assets/morgan_avatar.png`.
- Resolves 200 OK on Firebase Hosting structure.

### Item 4 — ValueKey Finders for Form Fields in Flutter Tests
- **Files:** `numista_mobile/lib/widgets/add_coin_manual_form.dart:435`, `numista_mobile/test/p7_v8_ux_safety_test.dart:117-119, 703-715, 813-824, 848-863, 919-921`
- Added `key: const ValueKey('manual_field_Mint Mark')` to `_buildMintMarkField`.
- Replaced all brittle `fields.at(n)` index finders with `find.byKey(const ValueKey('manual_field_<label>'))`.

### Item 5 — Permissions-Policy Camera Header in `firebase.json`
- **File:** `numista_mobile/firebase.json:236-237`
- Updated Permissions-Policy to `"camera=(self), microphone=(), geolocation=(), payment=()"`.
- Committed to branch only; no production deploy.

### Item 6 — Localhost Caller Proof with `HttpOverrides`
- **Files:** `numista_mobile/test/p7_v8_ux_safety_test.dart:2092-2144`
- Implemented `_LocalhostTrackerHttpOverrides` interceptor.
- Added test `p7_v8185_localhost_proof_zero_requests_on_hub_load` proving exactly 0 HTTP requests to `localhost` or `127.0.0.1` on hub load and with microscope disabled.

### Item 7 — Glob All `web/**/*.html` with `firebaseConfig` for Web Credentials
- **File:** `numista_mobile/test/p7_v8_ux_safety_test.dart:1963-1986`
- Dynamically parses `lib/firebase_options.dart` web configuration.
- Recursively globs `Directory('web')` for `*.html` and verifies web apiKey/appId and complete absence of Android keys.

---

## Baton Handoff

Baton renamed and updated:  
`BETA TEST\Grok Bot\8 OCT 26\BATONS\BATON_P7_ADD-COINS-FLOW_GROKCOS_OVER.md`

Standing by for Grok CoS Scoring.

**OVER**
