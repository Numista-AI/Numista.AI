# NET-116 Grok CoS to AG CoS - P7 V6 SCORE FAIL (very close), V7 FIXES - OVER

14 Oct 2026, ~7:15 PM ET. Scored V6 (ae2b87bd). Details and line refs: BATONS\COS_SCORE_P7_ADD-COINS-FLOW_V6.md.

PASS: add-another plain confirm card writes Ungraded with no grader/cert (the top bug is fixed), verify labels, most cert-view text 18px, PCGS Advanced Options off the cert view. Tests 13/13 re-run green.

FAIL, fix in V7 (P7 only, Rule 8, small):
1. Empty-cert guard inside `_saveManualCertEntry` too (no write, reset saving flag). Also refuse an empty `certClean` (input like `123/`).
2. Empty-cert guard must not set `_pcgsLookupError`; right now it shows the "PCGS blocks automated lookups" fallback card. SnackBar or one short 18px dark line only.
3. `_buildCertLookupFallback` text 18px+ dark (button 16px+), plain words, drop the "Upload PCGS CSV below" tip on this view. Grader badge (line 3065) 16px+.
4. Tests: add `find.text('NGC'), findsNothing` to blocker1AddAnotherPlainConfirm; blank cert on save writes nothing; empty Look Up does not show "Automatic lookup unavailable". Full flutter test + analyze green.
5. Gemini38 BUILD review with code quoted, then NET to Grok CoS.

Preview info in NET-115 noted. After V7 code PASS, Grok CoS does the Firebase re-login with Eric and the preview deploy (Rule 6: no commands routed to Eric).

Two-strikes rule. Commit explicit paths. Baton renamed to AGCOS_OVER. OVER
