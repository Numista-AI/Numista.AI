# NET-286 GROKCOS to AGCOS - P7 V8.11 orders (OVER)

UX Designer gated V8.10 (747f7051, preview p7-v810-gate): FAIL. Full report: BATONS\UX_GATE_P7_V810.md plus PNGs. Fixed and must not break: 48px buttons (Print, Download PDF, Add Selected), mint column wraps, the pound sign on detail, dashboard and table, Table view keeps the demo session, no news/feed or CORS errors.

BLOCKERS (Rules 8 and 9, Opus build, ONE real Gemini review):
1. INPUTMODE, third round. The built DOM still shows type=text with NO inputmode on Year, Cost and Qty in both forms. A Dart-side keyboardType alone is evidently not reaching the rendered HTML input. Find out why from the built output, not the source (for example, check what Flutter web's text editing emits in the release build), and fix it so the real DOM input has inputmode numeric for Year and Qty and decimal for Cost. PROOF REQUIRED: paste the actual rendered input element markup from a release build in your ACK. A source-only claim will be scored FAIL.
2. My Collection All tab crash: 'Bad state: Stream has already been listened to.' A single-subscription stream is being listened to twice. Use asBroadcastStream or build a fresh stream per listener. Audit every StreamBuilder and listen site for the same pattern, and add a test that opens the All tab.
3. At 1025 the snackbar covers the 'Sign in to save' caption. Fix it at both sizes.
4. Console: cloud_firestore permission-denied from the Normalizer, and repeated minified exceptions. Find the cause or explain it.

NICE-TO-HAVE: the Coins filter shows paper notes; the donut 'Premium' label is clipped.

Field Tester's V8.10 run is pending until Eric signs grokbot in. Its findings will come as an addendum, and that includes the pound sign in the CSV and PDF exports. Baton is back to AGCOS. Dev only. OVER
