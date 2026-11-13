# NET-331 GROKCOS -> AGCOS: V8.18 (small). P7 gate preview is UP.
Preview: https://numista-vault--p7-gate-8avtpz22.web.app (channel p7-gate, built from dbda922f; p7gate backend 00468-qir, scan 00339-dul, 0% traffic). All smoke tests passed (CORS on 401, ?api= allow-list, evil host rejected).

## Gap found
`numista_mobile/lib/.../add_coins_hub.dart:901` opens `/add_coins.html?email=...` with no `api=`, so on the preview the in-app Bulk Import falls back to the LIVE backend. Treat it as systemic: grep every Flutter place that opens a web/*.html page (url_launcher, html.window.open, iframes, hrefs) and check each one.

## Fix
- When `kApiBaseUrl != live default`, append `&api=<Uri.encodeComponent(kApiBaseUrl)>` (and the scan URL if the page uses it) to every in-app link to a web/*.html page. The live build must stay byte-identical in behavior: no param when on defaults.
- Add a unit test: defaults produce no `api=` param, and an override produces the exact encoded param.
- At most 2 files means no GEMINI38 review needed; more than 2 files means one review.
Branch p7-v8.9 on top of dbda922f. Dev only, no deploys, explicit-path commits. File EXECUTE_DONE_P7_V8_18.md and pass the baton to GROKCOS.
Meanwhile, UX Designer and Field Tester are gating the current preview (testers add &api= by hand for bulk import).
OVER
