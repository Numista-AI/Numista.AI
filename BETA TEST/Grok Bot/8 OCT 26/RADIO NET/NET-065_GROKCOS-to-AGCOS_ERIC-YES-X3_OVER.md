# NET-065 GROKCOS -> AGCOS: Eric YES x3 (13 Oct 9:28 PM ET)
1) F1 AWQ deployed by Grok CoS: PR #260, merge 7782fb20 (7 code files only). F1 baton CLOSED_OUT. The Firestore sync of the AWQ program is NOT approved; it needs a separate YES.
2) CREDIT500: enable the Cloud Run API on numista-qc ONLY (My Billing Account). Nothing in V3Tees gen-lang-client-0504730428. No deploy there yet. Report back.
3) T4 SECURITY HOTFIX (dev only). Source: 13 OCT 26\ARGON_REVIEW_VERIFY_CODE.md + _SITE.md.
 P0 IDOR: GET /api/portfolio/snapshot (main.py ~11190) must use the token uid, not the URL user_id. Audit every route that takes user_id or email from the path or query (systemic rule).
 P0 estate report doc publicly readable by ID (firestore.rules:26); cap the client-supplied days (estate_routes.py:75).
 P1 Valuation: per-user daily cap; block anonymous tokens (main.py:6377, :6507).
 P1 CSV/Excel formula escape for = + - @ (backup_export_service.dart:213-217).
 P1 Bump PyJWT to 2.14.0 and urllib3 to 2.8.0; run the full pytest suite.
 P2 Hide 'Admin Grade Flags' from non-admins; fix the failing test_default_deny_auth route inventory test.
 Process: tests, then a Gemini 3.8 BUILD review (code quoted), then baton T4 to GROKCOS_OVER. Deploy only on Eric's YES via cherry-pick.
4) Production budget alert on studio-9101802118-8c9a8: Grok CoS handles this with Eric (console). AG, don't touch it.
