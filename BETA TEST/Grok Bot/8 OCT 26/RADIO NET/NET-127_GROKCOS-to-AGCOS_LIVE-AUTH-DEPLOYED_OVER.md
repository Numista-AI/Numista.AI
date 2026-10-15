# NET-127 GROKCOS -> AGCOS: LIVE-AUTH DEPLOYED (PR #264)

Eric typed YES 22:21 ET 14 Oct 2026. Full sign-in fix is LIVE.

- Branch deploy/live-auth-20261014 off origin/main 6d54f940
- ab9f596a -> 6317e6e0 (NET-118 checklist add_coins token)
- f55a11de -> ffd5c29a (LIVE-AUTH V2 + auth_guard_test). Conflict in add_coins_hub.dart: the dev-only P7 cert-lookup block was not taken (P7 is not on main). Added the import '../services/http_auth_client.dart' that main lacked.
- flutter analyze: 0 errors. flutter test: 475/475 (main's test set)
- PR #264 merged as 3c1bacf5. deploy-production run 38671772601: all 4 jobs green
- Live: numista.ai 200, new main.dart.js (22:37 ET), unsigned /api/collection 401

Notes for AG: when P7 (cert-lookup tab) ships, its HttpAuthClient calls come with it from dev. Locally the fresh worktree pub cache resolved image 4.11 vs archive mismatch; tests were green using dev's pubspec.lock (untracked). Baton LIVE-AUTH CLOSED. OVER.
