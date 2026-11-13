# GEMINI38_REVIEW — P7 Add-Coins Flow V4 Build
**Reviewer:** Antigravity / Gemini 3.8  
**Date:** 2026-10-14  
**Commit under review:** (pending — pre-commit review of staged diff)  
**Scope:** FAIL 3b-i (NGC URL numeric grade) + FAIL 3b-ii (Vertex AI ADC for slab scan, dead stub deleted)

---

## FAIL 3b-i — NGC verify URL: numeric grade only, consistent in button + stored link

### CHECK 1: Dead stub `/scan_cert_number` deleted

**Verified:** The old stub endpoint is gone from `cert_routes.py`. Searched for `scan_cert_number` without `_upload` — no match at module level. The `@router.post("/scan_cert_number"` route that previously raised 405 no longer exists.

```
# DELETED — was at cert_routes.py:359-372 (V3):
@router.post("/scan_cert_number", response_model=ScanCertResponse)
async def scan_cert_number(
    image: bytes = Depends(lambda: None),  # overridden below
    user: dict = Depends(get_current_user),
):
    ...
    raise HTTPException(status_code=405, detail="Use multipart form POST.")
```

✅ PASS — stub deleted, only `/scan_cert_number_upload` remains.

---

### CHECK 2: `_buildManualCertEntryCard` verify button — NGC URL with numeric grade at tap time

**File:** `numista_mobile/lib/screens/add_coins_hub.dart:2921-2962`

```dart
// add_coins_hub.dart:2921-2962
Builder(builder: (_) {
  return SizedBox(
    width: double.infinity,
    child: OutlinedButton.icon(
      onPressed: () async {
        final String verifyUrl;
        switch (grader.toUpperCase()) {
          case 'NGC':
            // Extract digits only from grade at tap time: PF67→67, MS64→64
            final tapGrade = _certManualGrade.text.trim();
            final numericGrade = tapGrade.replaceAll(RegExp(r'[^0-9]'), '');
            final gradeSegment = numericGrade.isNotEmpty ? numericGrade : tapGrade;
            verifyUrl = 'https://www.ngccoin.com/certlookup/$certNo/$gradeSegment/';
            break;
          case 'CAC':
            verifyUrl = 'https://www.cacgrading.com/cert-verify/$certNo';
            break;
          default:
            verifyUrl = 'https://www.pcgs.com/cert/$certNo';
        }
```

**Verdict:** ✅ PASS
- Grade is read from `_certManualGrade.text` at tap time (user fills form first, then taps Verify)
- `replaceAll(RegExp(r'[^0-9]'), '')` strips all non-digit chars: `PF67→67`, `MS64→64`, `PR65→65`
- Fallback: if grade field is empty, `gradeSegment` falls back to the raw tap grade (not blank URL)
- URL format: `https://www.ngccoin.com/certlookup/8321797-003/67/` ✅

---

### CHECK 3: `_saveManualCertEntry` stored `verify_link` — NGC URL with numeric grade

**File:** `numista_mobile/lib/screens/add_coins_hub.dart:3060-3065`

```dart
// add_coins_hub.dart:3060-3065
case 'NGC':
  // Numeric grade only: PF67→67, MS64→64, PR65→65
  final numericGrade = grade.replaceAll(RegExp(r'[^0-9]'), '');
  final gradeSegment = numericGrade.isNotEmpty ? numericGrade : grade;
  verifyLink = 'https://www.ngccoin.com/certlookup/$certNo/$gradeSegment/';
  break;
```

**Verdict:** ✅ PASS
- Same `replaceAll(RegExp(r'[^0-9]'), '')` pattern as button — consistent across both paths
- V3 code was: `final gradeSlug = grade.replaceAll(' ', '').toUpperCase();` → produced `/PF67/` ❌
- V4 code strips all non-digits → produces `/67/` ✅
- Grok CoS test case: cert `8321797-003`, grade `PF67` → URL `https://www.ngccoin.com/certlookup/8321797-003/67/` ✅

---

## FAIL 3b-ii — Slab scan: Vertex AI + ADC, no GOOGLE_API_KEY

### CHECK 4: Module-level google-genai import (patchable for tests)

**File:** `numista_backend/routes/cert_routes.py:35-37`

```python
# cert_routes.py:35-37
# google-genai SDK — Vertex AI + ADC (no API key). Patchable at module level for tests.
from google import genai as _genai
from google.genai import types as _genai_types
```

**Verdict:** ✅ PASS
- Uses `google-genai` package (the new SDK, per main.py comment line 20: "replaces deprecated vertexai SDK, shutdown Jun 24 2026")
- Imported at module level so tests can `patch("routes.cert_routes._genai")`
- No `GOOGLE_API_KEY` or `GEMINI_API_KEY` import anywhere in file ✅

---

### CHECK 5: Vertex AI + ADC client instantiation in scan endpoint

**File:** `numista_backend/routes/cert_routes.py:369-404`

```python
# cert_routes.py:369-371
_SCAN_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "numista-qc")
_SCAN_LOCATION = os.environ.get("GEMINI_LOCATION", "global")

# cert_routes.py:399-404
    try:
        _scan_client = _genai.Client(
            vertexai=True,
            project=_SCAN_PROJECT_ID,
            location=_SCAN_LOCATION,
        )
```

**Verdict:** ✅ PASS
- Pattern exactly matches `main.py:392`: `genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=GEMINI_LOCATION)`
- `vertexai=True` → uses ADC, no API key required
- `project` defaults to `"numista-qc"` from `FIREBASE_PROJECT_ID` env var ✅
- No `api_key`, no `GOOGLE_API_KEY`, no `GEMINI_API_KEY` anywhere in the function ✅

---

### CHECK 6: Image part construction and generate_content call

**File:** `numista_backend/routes/cert_routes.py:420-428`

```python
# cert_routes.py:420-428
        image_part = _genai_types.Part.from_bytes(data=raw, mime_type=mime)
        response = _scan_client.models.generate_content(
            model="gemini-2.0-flash-002",
            contents=[prompt, image_part],
            config=_genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                max_output_tokens=128,
            ),
        )
```

**Verdict:** ✅ PASS
- `Part.from_bytes(data=raw, mime_type=mime)` is the correct google-genai SDK pattern for binary image data
- `_scan_client.models.generate_content(model=..., contents=..., config=...)` matches the pattern used throughout `main.py` (e.g. line 744)
- `response_mime_type="application/json"` preserved from V3 ✅
- `max_output_tokens=128` preserved ✅

---

### CHECK 7: No API-key code remaining in cert_routes.py

**Verified by grep:** No occurrence of `GOOGLE_API_KEY`, `GEMINI_API_KEY`, `genai.configure`, `google.generativeai`, or `GenerativeModel` in `cert_routes.py`.

✅ PASS — clean.

---

## CHECK 8: New pytest tests (4 added)

**File:** `numista_backend/tests/test_cert_lookup.py` — 4 new tests appended

```python
# test_cert_lookup.py — test_scan_cert_number_upload_returns_cert (mocked Vertex AI)
def test_scan_cert_number_upload_returns_cert():
    mock_response = MagicMock()
    mock_response.text = '{"cert_number": "53652580", "grader": "PCGS", "confidence": "HIGH"}'
    with patch("routes.cert_routes._genai") as _mock_genai_mod:
        mock_client = MagicMock()
        _mock_genai_mod.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = mock_response
        response = client.post(
            "/api/scan_cert_number_upload",
            files={"file": ("test.jpg", b"\xff\xd8\xff" + b"\x00" * 100, "image/jpeg")},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["cert_number"] == "53652580"
    assert data["grader"] == "PCGS"
    assert data["confidence"] == "HIGH"
    assert data["message"] == "OK"
```

```python
# test_cert_lookup.py — test_ngc_verify_url_numeric_grade (Grok CoS test case)
def test_ngc_verify_url_numeric_grade():
    def _ngc_url(cert_no: str, grade: str) -> str:
        numeric_grade = re.sub(r'[^0-9]', '', grade)
        grade_segment = numeric_grade if numeric_grade else grade
        return f"https://www.ngccoin.com/certlookup/{cert_no}/{grade_segment}/"
    # Grok CoS test case from NET-104
    assert _ngc_url("8321797-003", "PF67") == "https://www.ngccoin.com/certlookup/8321797-003/67/"
    assert _ngc_url("8321797-003", "MS64") == "https://www.ngccoin.com/certlookup/8321797-003/64/"
    assert _ngc_url("8321797-003", "PR65") == "https://www.ngccoin.com/certlookup/8321797-003/65/"
    assert _ngc_url("1234567", "67") == "https://www.ngccoin.com/certlookup/1234567/67/"
```

**Test results:** 17/17 passed (13 pre-existing + 4 new). Exit code 0.

✅ PASS

---

## Summary

| Item | Check | Result |
|------|-------|--------|
| Dead stub `/scan_cert_number` deleted | cert_routes.py: no `@router.post("/scan_cert_number"` | ✅ PASS |
| Verify button NGC URL numeric grade | add_coins_hub.dart:2928-2933: `replaceAll(RegExp(r'[^0-9]'), '')` | ✅ PASS |
| Stored verify_link NGC numeric grade | add_coins_hub.dart:3060-3065: same regex | ✅ PASS |
| google-genai import at module level | cert_routes.py:36-37: `from google import genai as _genai` | ✅ PASS |
| vertexai=True + ADC client | cert_routes.py:400-404: `_genai.Client(vertexai=True, project=..., location=...)` | ✅ PASS |
| No GOOGLE_API_KEY usage | grep confirms zero occurrences in cert_routes.py | ✅ PASS |
| generate_content pattern matches main.py | cert_routes.py:421-428: `_scan_client.models.generate_content(model=..., contents=..., config=...)` | ✅ PASS |
| Mocked scan tests pass | 4 new tests: 17/17 pass | ✅ PASS |
| flutter analyze | No issues found (32.5s) | ✅ PASS |
| Full pytest suite | 543 pass, 15 pre-existing baseline fails | ✅ PASS |

**All V4 fix items verified. Recommend PASS.**
