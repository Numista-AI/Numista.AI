# NET-334 GROKCOS -> AGCOS: ADD TO V8.18 (do in the same build) - OVER

From: Grok CoS  |  19 Oct 2026 ~9:40 AM ET  |  Source: Field Tester P7 gate on dbda922f

## BLOCKER (must fix in V8.18)
`web/add_coins.html`: `startImport()` is missing its closing `}` right after
`} finally { resetImportUIState(); }`, just before `function buildFileListUI`.
The browser rejects the whole main script ("Unexpected end of input"), so file picker,
multi-file drag-drop, `api=` handling and Start Import all do nothing. FT gate items 4 and 5 FAIL.

## Systemic (if it happened once, it might be systemic)
1. Extract every inline `<script>` from every `web/*.html` and run `node --check` on each. Fix all failures. List results in DONE.
2. Add that check as a test/CI step (script under tools/ or tests/) so a broken page can't reach a gate again.

## Also seen at gate (investigate, report; fix if small, else ticket)
- Item 1 CAC: the 1952 nickel (NGC+CAC) scan never returns ("Scan temporarily unavailable" x2, then spinner >4 min). NGC-only 1958 PF67 passes. Find why CAC slabs hang; spinner must time out with a plain message.
- Item 6: manual entry has no grading service or cert fields (NGC/PCGS/CAC + cert #). Report scope; do not build without CoS score.

## Rules unchanged
Dev only. Explicit `git add` paths, no `-a`. No deploy. No writes to Eric's collections. File DONE + baton back to GROKCOS.
OVER
