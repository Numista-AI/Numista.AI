# EXECUTE_DONE — REQ_032B Alt Site Phase A (T3b)
Filed by: Antigravity CoS  
Date: 2026-10-12 ~5:46 PM ET  
Commit: `84a1f361` on `dev` (rebased on T1+T2+T3)

## Result: DONE — Phase A built, 468 pytest + 432 Flutter tests pass, analyze clean

| Item | Description | File:Line |
|---|---|---|
| Backend: `GET /api/user/ui_variant` | Token-authed; reads Firestore setting; Phase A allowlist gating | main.py:220-272 |
| Backend: `POST /api/admin/set_ui_variant` | Admin-claim only; sets/clears `users/{email}/settings/ui_variant` | main.py:220-272 |
| Backend: Phase A allowlist | `{'eric.seaman@yahoo.com', 'eric@numista.ai'}` — hardcoded server-side | main.py:247 |
| Firestore rules | Client write to `settings/ui_variant` blocked (`allow write: if false`) | numista_backend/firestore.rules:30-34, numista_mobile/firestore.rules:92-96 |
| `UiVariantService` | Fetches from API, falls back to classic on error, `reset()` on sign-out | ui_variant_service.dart:1-28 |
| Sign-in refresh | `UiVariantService.refresh()` called after all sign-in flows | auth_service.dart:92-167, auth_gate.dart:98-118 |
| Sign-out reset | `UiVariantService.reset()` on sign-out | base_layout.dart:1309-1317 |
| `_buildBodyForRoute()` | Extracted from `_buildBody()` to enable variant wrapping | base_layout.dart:324-446 |
| Phase A banner injection | Alt variant wraps Home Dashboard in `_AltSiteBanner` | base_layout.dart:309-322 |
| `_AltSiteBanner` widget | Thin colored bar: "Alt site variant — Phase A (admin preview)" | base_layout.dart:1324-1345 |
| Backend tests | 12 tests: 401/403/400/200 for both endpoints, allowlist gating | test_ui_variant.py |
| Flutter tests | 5 tests: default, refresh alt/classic, error fallback, reset | ui_variant_service_test.dart |

## Counts
- Pytest: **468 passed, 0 failed** (T1 baseline 447 → +21 total across all tracks)
- Flutter test: **432 passed, 0 failed** (T3 baseline 427 → +5)
- flutter analyze: **0 errors, 0 warnings**
- Pubspec: 4.403.0+403 (unchanged)

## Phase gating summary
- **Phase A** (built): Eric + AJ only; server-enforced allowlist; alt shows a banner, no screen changes yet
- **Phase B** (NOT built): beta testers by creation timestamp — needs Eric's typed YES
- **Phase C** (NOT built): all users — needs Eric's typed YES
- Client NEVER writes `settings/ui_variant` directly — Firestore rules block it

## What's next
Grok CoS scores this build. Then Eric decides when to deploy T1 backend (separate from Flutter).
