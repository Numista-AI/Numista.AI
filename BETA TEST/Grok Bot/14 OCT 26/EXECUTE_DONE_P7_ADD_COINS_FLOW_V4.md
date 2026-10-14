# EXECUTE_DONE — P7 Add-Coins Flow V4
**Date:** 2026-10-14 ~17:05 ET  
**Agent:** AG CoS (Antigravity / Gemini 3.8)  
**Commit:** `65711b71` on `dev`  
**Branch:** dev (pushed, confirmed dev → dev)

---

## What was fixed (V4 — from NET-104 / COS_SCORE_P7_ADD-COINS-FLOW_V3.md)

### FAIL 3b-i — NGC verify URL must use numeric grade only

**Root cause (V3):** Stored `verify_link` used `gradeSlug = grade.replaceAll(' ', '').toUpperCase()` → produced `/PF67/`. Button had no grade at all → produced `/certlookup/{certNo}/`.

**Fix:**
- `add_coins_hub.dart:3060-3065` (`_saveManualCertEntry`): `grade.replaceAll(RegExp(r'[^0-9]'), '')` → `PF67→67`, `MS64→64`, `PR65→65`. Stored `verify_link` = `https://www.ngccoin.com/certlookup/8321797-003/67/` ✅
- `add_coins_hub.dart:2921-2962` (`_buildManualCertEntryCard` verify button): Grade now read from `_certManualGrade.text` at **tap time** (not build time), same regex. Button URL = `https://www.ngccoin.com/certlookup/8321797-003/67/` ✅
- Both paths produce the same URL format. Consistent.

### FAIL 3b-ii — Slab scan must use Vertex AI + ADC, not GOOGLE_API_KEY

**Root cause (V3):** `scan_cert_number_upload` imported `google.generativeai`, read `GOOGLE_API_KEY`/`GEMINI_API_KEY` from env, called `genai.configure(api_key=...)`.

**Fix:**
- `cert_routes.py:35-37`: Module-level import: `from google import genai as _genai` / `from google.genai import types as _genai_types` (same `google-genai` SDK used in `main.py`)
- `cert_routes.py:399-404`: Client: `_genai.Client(vertexai=True, project=_SCAN_PROJECT_ID, location=_SCAN_LOCATION)` — ADC, no API key
- `cert_routes.py:420-428`: Call: `_scan_client.models.generate_content(model="gemini-2.0-flash-002", contents=[prompt, image_part], config=GenerateContentConfig(...))` — matches `main.py` pattern exactly
- Dead stub `/scan_cert_number` (405 raise) deleted entirely. Only `/scan_cert_number_upload` remains.
- No `GOOGLE_API_KEY`, `GEMINI_API_KEY`, `genai.configure`, or `google.generativeai` anywhere in file.

---

## Test results

| Suite | Result |
|-------|--------|
| `pytest test_cert_lookup.py` | **17/17 passed** (13 prior + 4 new) |
| Full pytest | **543 passed, 15 failed** (15 = pre-existing baseline: receipt_streaming, upload_baseline_fixes, auth_security) |
| `flutter analyze lib/screens/add_coins_hub.dart` | **No issues found** (32.5s) |
| `flutter test --reporter compact` | **500/500 passed** |

---

## 4 new tests added

1. `test_scan_cert_number_upload_returns_cert` — mocks Vertex AI client, asserts cert/grader/confidence returned
2. `test_scan_cert_number_upload_ngc_cert` — NGC cert with dash suffix (8321797-003)
3. `test_scan_cert_number_upload_no_cert_found` — null cert → LOW confidence message
4. `test_ngc_verify_url_numeric_grade` — asserts Grok CoS test case: PF67→67, MS64→64, PR65→65, plain 67 passthrough

---

## GEMINI38 BUILD REVIEW

Filed: `BETA TEST/Grok Bot/14 OCT 26/GEMINI38_REVIEW_P7_ADD_COINS_FLOW_V4_BUILD.md`  
Verdict: All 8 checks PASS. Recommends PASS.

---

## Gate status

- [x] FAIL 3b-i NGC URL: FIXED
- [x] FAIL 3b-ii Vertex AI ADC: FIXED
- [x] Dead stub deleted
- [x] pytest cert: 17/17 pass
- [x] Full pytest: 543 pass (15 baseline)
- [x] flutter analyze: 0 issues
- [x] flutter test: 500/500 pass
- [x] Gemini BUILD review filed (verbatim code lines included)
- [ ] UX Designer review — still outstanding (gate req, arranged by Grok CoS)
- [ ] Field Tester walkthrough — still outstanding (gate req, arranged by Grok CoS)

Passing to Grok CoS for score. After PASS + gate: P5 rebuild.
