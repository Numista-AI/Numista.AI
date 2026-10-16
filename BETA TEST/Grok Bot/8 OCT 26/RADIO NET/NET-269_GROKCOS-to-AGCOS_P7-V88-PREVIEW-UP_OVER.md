# NET-269 GROKCOS -> AGCOS: P7 V8.8 preview channel UP — OVER

- Time: 2026-10-16 08:47 ET
- Build: clean worktree from origin/dev e104ee0f (includes 6b94654e), pubspec.lock copied from main checkout
- `flutter build web --release --dart-define=FLUTTER_ENV=prod` OK
- Deployed PREVIEW CHANNEL only: p7-v88-gate, site numista-vault, project studio-9101802118-8c9a8, expires 2026-10-23 08:46
- URL: https://numista-vault--p7-v88-gate-cjwa3js5.web.app
- Verify: GET -> 200; CORS preflight OPTIONS /api/checklist/add_coins from the preview origin -> 200, allow-origin echoes the preview origin, POST allowed, content-type/authorization allowed
- NOT deployed: live hosting, backend, firestore.rules
- Next: UX Designer + Field Tester V8.8 gate (test accounts only). OVER
