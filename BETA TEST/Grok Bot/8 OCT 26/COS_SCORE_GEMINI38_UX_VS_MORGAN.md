# CoS SCORE: GEMINI38_REVIEW_UX_VS_MORGAN_2026-10-08.md
Grade: **PASS (accepted)**. Grok and Gemini independently agree on the order and the phased hybrid.

Spot-check at dev e5f5760c: 16 of 16 of Gemini's new file:line citations matched the code (main.py:122, 2746-2750 INTERNAL_UNDO, 2804-2805; scan_routes 84/215/240/273/359; import_routes 76/234; ai_routes 237-238).
Minor: line 2805 shows client collection_context going into the prompt. The chat_history half of that claim wasn't verified at that line, so re-check it in the Gate 0 plan.

## Accepted additions to Gate 0 (for the Opus 4.6 Thinking Plan.v1)
1. INTERNAL_UNDO:<id> (main.py:2746) must delete only coins Morgan just added for this user, with soft delete.
2. Treat client-sent collection_context and chat_history as untrusted. Use server-side inventory only.
3. Treat coin notes and OCR text as data, never instructions (prompt-injection guard). No writes without a user Confirm tap.
4. Values and cost are stripped from Morgan's prompt by default. Privacy Mode (REQ_026) means zero financial figures, ever.
5. Add the scan_routes review/*, import_routes and /api/ai/essay routes to the REQ_031 route inventory and the usage caps.
6. Voice input (speech-to-text on mobile) is required before Phase 2.

UX fixes 1-5 proceed as Plan.v1 under REQ_032 (Sonnet 4.6 Thinking). Dev only. No deploy without Eric's YES.
