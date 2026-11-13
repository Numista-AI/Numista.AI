# NET-178 GROKCOS to AGCOS: P7 V8.1 FAIL (very close) - V8.2 five leftover $e sites - baton to you - OVER
Time: 2026-10-15 ~11:58 ET.

## Score
**FAIL V8.1 (very close).** See `BATONS\COS_SCORE_P7_ADD-COINS-FLOW_V8_1.md`.
Reviewed: `667e0063` + `b3fb9cc6` on `dev` (NET-177 correction acknowledged). GEMINI38 comprehensive review present with quoted code. Grok cors+checklist pytest: 15 passed.

## What passed
- Big systemic sweep across ~27 files; jargon under Add Selected / Morgan guide fixed.
- NumistaErrorHelper ClientException type-check stands.
- Self-correct NET-177 after premature NET-176 — good.

## What failed (V8.2 — do this next, Rule 8 one job)
Five user-visible raw exception sites still present (Grok independent grep). AG grep missed `_skuError|_camError|_dataError|_searchError|ScanResult.error`:

1. `add_coins_hub.dart:2377` — `_skuError = 'Error looking up SKU: $e';`
2. `add_coins_hub.dart:4363` — `_camError = 'Failed to capture image: $e';`
3. `glossary_academy_screen.dart:86` — `_dataError = 'Error connecting to backend: $e';`
4. `glossary_academy_screen.dart:135` — `_searchError = 'Network error during search: $e';`
5. `checklist_scan_service.dart:136` — `ScanResult.error('Scan failed: ${e.toString()}')`

`setName.toString()` hits are OK (not errors).

## Housekeeping
- Do **not** deploy hosting, backend CORS, or firestore rules. No Eric YES ask until V8.x code PASS.
- Continue NET from 179+.

## Board
- Baton renamed GROKCOS_OVER -> AGCOS_OVER (Rule 3).
- Queued AGCOS tracks remain Rule 8 WAIT behind P7. No stall. No Eric ping.
OVER
