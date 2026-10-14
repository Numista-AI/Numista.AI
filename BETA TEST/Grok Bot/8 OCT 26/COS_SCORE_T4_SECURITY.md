# COS_SCORE_T4_SECURITY - PASS
From: Grok CoS. 13 Oct 2026 10:13 PM ET. DEV ONLY. No Firestore / sync_canon / live deploy.

Scored: NET-066 (AGCOS) + GEMINI38_REVIEW_T4_SECURITY_BUILD.md + EXECUTE_DONE_T4_SECURITY.md + commit `c80f4122` against NET-065 item 3 (T4 SECURITY HOTFIX).

## Verdict: PASS

### What passes (Grok CoS verified on EDS_Laptop, `dev` @ `c80f4122` / tip `c902a676`)
- **P0-A Portfolio snapshot IDOR** at `main.py:11205-11216`: `Depends(get_current_user)` + caller uid/email/admin gate -> 403. Matches Gemini quotes verbatim (`git show c80f4122`).
- **P0-B Estate rules**: `/users/{email}/estate_reports/{reportId}` is owner-only read / write false (mobile + backend rules). Root `/estate_reports/{token}` requires authenticated read; writes server-only. `estate_routes.py` clamps `valid_days` to `[1, 30]`.
- **P1-A Valuation**: both `estimate_value_text` and `estimate_value_general` require auth, block anonymous (403), rate-cap 20/day via `_check_and_increment_rate_cap`.
- **P1-B CSV formula escape**: `backup_export_service.dart:cleanCsvCell` prefixes `=+-@\t\r`.
- **P1-C Deps**: `PyJWT==2.14.0`, `urllib3==2.8.0` in requirements.txt and requirements-dev.txt.
- **P2-A Admin nav**: `AuthService.isAdmin` + `base_layout` sidebar/route guards.
- **P2-B** `test_default_deny_auth` route walker expanded; reviewed allowlist updated.
- Gemini 3.8 BUILD review present with code quoted; header reads Gemini 3.8; commit SHA `c80f4122`.

### Grok CoS re-run (EDS_Laptop)
| Suite | Result | Notes |
|-------|--------|-------|
| `test_idor_fixes.py` + `test_valuation_cap.py` + `test_default_deny_auth.py` | **30/30 PASS** | Verified this watch |
| Full pytest (AG) | 511/511 | Accepted (scoped security tests re-verified) |
| Flutter test (AG) | 471/471 | Accepted |
| flutter analyze (AG) | 0 issues | Accepted |

### Residual (does not block T4 PASS)
NET-065 required a **systemic audit** of routes taking `user_id` / email from path/query. AG catalogued **39** routes (18 ownership/admin-guarded, **21 Category-2** still relying on outer default-deny without per-route token match). Snapshot (the named P0) is sealed. Category-2 cleanup is a follow-on track, not a reopen of this hotfix.

Live smoke this watch: `numista.ai/api/spot_prices` 200, `/api/collection` 401. OK.

## Next
T4 SECURITY HOTFIX is **PASS** on `dev` (`c80f4122`). Live / production deploy needs Eric typed **YES** (cherry-pick approved commits onto a branch from `main` — never a full `dev` merge). Passing baton to ERIC for that deploy decision.

Hard holds: no live data writes; Firestore rules deploy / Cloud Run deploy each need separate Eric typed YES.
