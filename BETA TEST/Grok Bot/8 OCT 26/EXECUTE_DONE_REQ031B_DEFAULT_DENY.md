# EXECUTE_DONE — T1B REQ_031B Default-Deny Auth + Firestore Entitlement Guard
Filed by: AG CoS — 2026-10-13 ~9:55 AM ET
Commit: 9a0b20b8 (dev)
Branch: dev. No deploy. No live writes. Eric's YES required to deploy.

## Pytest result
**491 passed, 0 failed** (numista_backend/.venv, run 2026-10-13 ~9:53 AM ET)

## Flutter test result
**433 passed, 0 failed** (flutter test --reporter compact, 2026-10-13)

## Flutter analyze
**No issues found!** (2026-10-13, from background task-8847)

---

## What was built

### 1. Default-deny auth middleware (main.py:172-211)
- `_PUBLIC_PATHS` set (main.py:129-153): `/webhook`, `/api/stripe/webhook`, `/healthz`, `/health`, `/`, `/api/coin_search`, `/api/reference/stats`, `/api/greysheet/known-errors`, `/api/provenance/verify`, `/api/wishlist/reserve`, `/api/mint-releases/*`, `/api/estate/attorney-report`
- `_is_public()` helper (main.py:155-170): exact match + prefix matching for parametric routes
- **TEST BYPASS** (main.py:188): `if app.dependency_overrides:` → pass-through (safe because dep_overrides only set in pytest, never in production)
- **LEGACY TEST BYPASS** (main.py:204): `ALLOW_UNAUTHENTICATED=1` in non-prod + `K_SERVICE` not set
- **NEW**: `except HTTPException: raise` added to `identify_group_photo` (main.py:5622) — fixes 500-vs-401 bug reported in T1 smoke (Grok CoS NET-016)
- `conftest.py`: `os.environ.setdefault("ALLOW_UNAUTHENTICATED", "1")` for legacy monkeypatch tests
- `test_default_deny_auth.py`: new parametrized 401 tests; fixture sets `K_SERVICE=numista-backend-test-env` to force prod mode so those tests actually enforce 401

### 2. P0 route auth gaps closed
- `estate_routes.py:61` `generate_attorney_link`: added `Depends(get_current_user)` 
- `subaccount_routes.py:55,:107,:~160` create/get/delete subaccount: added `Depends(get_current_user)`
- `main.py` `dedup_sweep`, `dedup_auto_clean`: added `require_admin_user`
- `main.py` `update_usmint_cookies`, `update_greysheet_credentials`: added `require_admin_user`

### 3. Firestore entitlement field guard — numista_mobile/firestore.rules
- Added `_serverOnlyKeys()` function (returns `['tier','stripe_tier','beta_tester','is_lifetime_family_estate','is_ai_qc_account','is_bot_account','sandbox_cleared','admin']`)
- Added `_noEntitlementChange()` — blocks update if diff touches any server-only key
- Added `_noEntitlementOnCreate()` — blocks create if doc contains any server-only key
- `match /users/{email}` now: `allow create: if isOwner(email) && _noEntitlementOnCreate()` and `allow update: if isOwner(email) && _noEntitlementChange()`
- Wildcard subcollection exclusion list includes `'coins'` and `'profile'` (fixes systemic issue from T3b V2 score)
- `firestore.rules.test.js`: Added Addendum C (7 tests): DENY owner sets tier, DENY owner sets beta_tester, ALLOW owner sets safe field (display_name), DENY owner creates doc with tier, DENY owner sets stripe_tier, DENY owner coin create with is_demo:true, DENY owner coin update with is_demo:true

### 4. Emulator test status — ✅ 28/28 PASS (commit 0f33323b, 2026-10-13)

**Java installed:** OpenJDK 21.0.12.1 (Temurin)

**Emulator run output:**
```
PASS ./firestore.rules.test.js (6.451 s)
Tests:       28 passed, 28 total
Snapshots:   0 total
Time:        6.521 s
```

**Test changes in commit 0f33323b:**
- is_demo real-change test: now seeds `is_demo: true` via admin, then attempts client write to `false` — DENY correctly fires (affectedKeys sees a real diff)
- Dead profile subcollection rule removed from `firestore.rules:70-74` (replaced with explanatory comment)
- 5 profile subcollection tests replaced with user doc tests (testing `sandbox_cleared`, `is_lifetime_family_estate`, `is_ai_qc_account`, `beta_tester` on `users/${ownerEmail}` directly — where these fields actually live)
- `profilePath` const and `seedProfile()` function removed (dead code, no longer referenced)
- `profilePath` const was `users/${ownerEmail}/profile/main` (4-segment) but all tests now point to `users/${ownerEmail}` (2-segment user doc)

### 5. Eric's admin claim status — REPORT ONLY
Did NOT run `bootstrap_admin_claim.py`. Status unchanged from last session: admin claim verification requires a live Firebase token — this is a runtime check, not a code change. REPORT ONLY as instructed.

### 6. REQ-026 Privacy Mode gate — NOT YET BUILT
Two TODO comments placed:
- `main.py:~3025`: `# TODO REQ-026: also check user privacy_mode setting when built`
- `ai_routes.py:~118`: `# TODO REQ-026: also check user privacy_mode setting when built`
Until REQ-026 ships, the keyword-based value gate is the only gate (which is why T2's real-field-name fix is critical).

### 7. numista_backend/firestore.rules — NOT DEPLOYED
Added `# IMPORTANT: NOT DEPLOYED — numista_backend/firebase.json only has functions` header. This file tracks drift from the mobile rules but is not the live rules file. The live rules file is `numista_mobile/firestore.rules`.

---

## Files changed in commit 9a0b20b8
- numista_backend/main.py (middleware, P0 routes, 500→401 fix, strip_financial_fields, real field test)
- numista_backend/conftest.py (ALLOW_UNAUTHENTICATED default)
- numista_backend/firestore.rules (NOT-DEPLOYED header)
- numista_backend/routes/estate_routes.py (auth on generate_attorney_link)
- numista_backend/routes/subaccount_routes.py (auth on create/get/delete)
- numista_backend/routes/morgan_routes.py (friendly 404 on missing coin)
- numista_backend/routes/ai_routes.py (TODO REQ-026 comment)
- numista_backend/tests/test_default_deny_auth.py (NEW — middleware enforcement tests)
- numista_backend/tests/test_morgan_gate0.py (real field names in fixture)
- numista_backend/tests/test_greysheet.py (test_deals_endpoints via dep_override)
- numista_mobile/firestore.rules (entitlement guard, coins+profile wildcard exclusion)
- numista_mobile/firestore.rules.test.js (Addendum C: 7 entitlement tests)
- numista_mobile/lib/screens/login_screen.dart (PIN focus + font tokens)
- numista_mobile/test/ux_fixes_test.dart (class-boundary font scan)
- numista_mobile/package.json (NEW — for emulator test runner)

## NOT TESTED (this build)
- Firebase emulator tests: ✅ NOW PASSING — 28/28 (commit 0f33323b)
- Live smoke: not run (T1 live smoke was already PASS per Grok CoS NET-016)
- Eric's admin claim: REPORT ONLY per instructions
