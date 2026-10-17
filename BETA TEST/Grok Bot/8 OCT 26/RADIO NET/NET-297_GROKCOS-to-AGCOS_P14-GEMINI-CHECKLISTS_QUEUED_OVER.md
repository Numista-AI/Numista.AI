# NET-297 | GROKCOS to AGCOS | P14 QUEUED (behind P7, do not start yet)
Filed 17 Oct 2026, 1:10 PM ET, on Eric's order.

## P14: Numista.Ai checklists optimized for Gemini scanning
- Eric approved turning off the always-on Document AI "Coin Checklist Extractor" (processor 261d6897c84ca28b). Checklist scans then use the existing Gemini fallback (main.py about lines 4951 to 5000).
- Goal: redesign Numista.Ai's own Coin Program checklist PDFs so Gemini reads checked boxes accurately, for example with large, clearly separated boxes, a printed slot ID beside each box, high contrast, a header code naming the program and page, and an ink-saver light layout.
- Rule: no Littleton or Whitman names anywhere users can see them (site, checklists, marketing, Morgan replies). They are competitors. Code can still accept scans of any checklist.
- Must keep: invoice and receipt PDF scanning (Gemini, unchanged). Treat this as systemic: the checklist PDF printout, the scanner, and the on-screen checklist must all match.
- Acceptance: a test set of filled checklists (dense, partly filled, pencil marks) scored for Gemini accuracy against known answers, with misses listed.
- Plan.v1 first. Nothing deploys without Eric's YES.
OUT
