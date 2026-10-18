# NET-312 | GROKCOS to AGCOS | P7 V8.15: preview must reach test backends (small, dev only)
Filed 18 Oct 2026, 7:58 AM ET. Eric chose (in GROKCOS chat, 7:51 AM ET) to deploy scan_service and the main backend as HIDDEN no-traffic tagged test copies (tag `p7gate`) so live users are unaffected. Grok CoS does the Cloud Run deploys. The front end currently can't point at them.

Build V8.15 on `f48d15e3` (p7-v8.9):
1. `numista_mobile/lib/constants.dart`: change `kApiBaseUrl` and `kScanServiceUrl` to `const String.fromEnvironment('API_BASE_URL', defaultValue: <current live URL>)` and `SCAN_SERVICE_URL` the same way. Defaults must stay byte-identical to today's live URLs.
2. Replace the hard-coded live backend URL with `kApiBaseUrl` in `program_manager_screen.dart`, `family_subaccount_service.dart`, `market_news_service.dart`, `stripe_service.dart` and `upcoming_releases_service.dart`. Grep for any other copies, including `web/*.html` such as `add_coins.html` `API_BASE`. Standalone HTML pages can't read dart-define, so tell me how they'd reach the test backend (for example a `?api=` override allowed only for `*.run.app` hosts on preview origins, or a note that they stay on live).
3. Add a test proving the defaults equal the live URLs.
4. This touches more than two files, so it needs one GEMINI38 review with code quoted verbatim.
No deploys. Nothing goes on main. Use explicit-path commits only. Hand the baton back to GROKCOS when done.
OVER
