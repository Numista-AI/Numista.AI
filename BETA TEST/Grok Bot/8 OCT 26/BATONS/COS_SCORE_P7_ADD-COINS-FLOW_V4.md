# COS SCORE - P7 ADD-COINS-FLOW V4
Scorer: Grok CoS | 2026-10-14 ~17:15 ET | Reviewed: 65711b71 on dev vs a016e1c4 (V3)
Verdict: **PASS V4 (code)**. GATE PENDING: UX Designer + Field Tester before Eric deploy YES.

Tests re-run by Grok CoS: `pytest tests/test_cert_lookup.py` -> **17 passed** in 7.37s.

| # | Item | Score | Evidence |
|---|------|-------|----------|
| 3b-i | NGC verify link numeric grade | **PASS** | Button (tap-time) and stored verify_link both use `replaceAll(RegExp(r'[^0-9]'), '')`. Cert 8321797-003 + PF67 -> `https://www.ngccoin.com/certlookup/8321797-003/67/`. `test_ngc_verify_url_numeric_grade` asserts PF67/MS64/PR65. |
| 3b-ii | Slab photo-read Vertex AI + ADC | **PASS** | `_genai.Client(vertexai=True, project=..., location=...)`. No GOOGLE_API_KEY / GEMINI_API_KEY / google.generativeai. Dead `/scan_cert_number` stub deleted. 3 mocked upload tests + URL test. |
| Prior | Double-write, eric_emails, add-another | PASS (V3) | Unchanged; still good. |
| Gate | UX Designer + Field Tester | **PENDING** | Grok CoS arranging. No ERIC deploy YES until gate PASS. |

## Quoted code (HEAD after 65711b71)

### Verify button (add_coins_hub.dart)
```dart
case 'NGC':
  final tapGrade = _certManualGrade.text.trim();
  final numericGrade = tapGrade.replaceAll(RegExp(r'[^0-9]'), '');
  final gradeSegment = numericGrade.isNotEmpty ? numericGrade : tapGrade;
  verifyUrl = 'https://www.ngccoin.com/certlookup/$certNo/$gradeSegment/';
```

### Stored verify_link (add_coins_hub.dart)
```dart
case 'NGC':
  final numericGrade = grade.replaceAll(RegExp(r'[^0-9]'), '');
  final gradeSegment = numericGrade.isNotEmpty ? numericGrade : grade;
  verifyLink = 'https://www.ngccoin.com/certlookup/$certNo/$gradeSegment/';
```

### Slab scan (cert_routes.py)
```python
from google import genai as _genai
from google.genai import types as _genai_types
# ...
_scan_client = _genai.Client(
    vertexai=True,
    project=_SCAN_PROJECT_ID,
    location=_SCAN_LOCATION,
)
```

## Next
1. Grok CoS: UX Designer review + Field Tester (grokbot) walkthrough on dev.
2. AG CoS: **WAIT** — do not start P5 until Grok files gate PASS / NET release (Rule 8: finish P7 through gate first).
3. After gate PASS: baton -> ERIC for cherry-pick deploy YES. No full dev merge. No collection writes.
