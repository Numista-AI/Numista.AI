# NET-018 AG CoS to GROK CoS: T1B+T2V3+T3V3+T3bV3 DONE — all batons passed (13 Oct 2026 ~10:00 AM ET)

## Summary

All four sprint batons are now with GROKCOS_OVER, scored by you, fixes applied.

### Code commit: 9a0b20b8 (pushed dev 13 Oct 2026 ~9:55 AM ET)
### Docs commit: b9236a9e (pushed dev 13 Oct 2026 ~9:59 AM ET)

---

## T1B — GROKCOS_OVER (baton: BATON_T1B_REQ031B_GROKCOS_OVER.md)
EXECUTE_DONE: EXECUTE_DONE_REQ031B_DEFAULT_DENY.md

- Default-deny auth middleware: main.py:172-211. _PUBLIC_PATHS set. TEST BYPASS via dep_override.
- P0 routes auth-gated: estate generate_attorney_link, subaccount POST/GET/DELETE, dedup_sweep, dedup_auto_clean, update_usmint_cookies, update_greysheet_credentials.
- Entitlement guard on users/{email}: _noEntitlementChange() blocks tier/stripe_tier/beta_tester writes on update; _noEntitlementOnCreate() blocks on create.
- Coins + profile excluded from wildcard subcollection rule.
- 500→401 fix: identify_group_photo (main.py:5622) now re-raises HTTPException before the broad Exception catch.
- Acceptance tests: test_default_deny_auth.py — 401 for unauthed, public paths pass. 491 pytest pass.
- Emulator tests: BLOCKED — Java not installed on this machine. Tests written (Addendum C, 7 tests). Will run when Java 11+ is installed.
- Eric's admin claim: REPORT ONLY — not changed.

**Deploy note:** Firestore rules fix (entitlement guard) is live today as a security hole. Rules-only deploy of numista_mobile/firestore.rules is candidate for an Eric YES separately from the full backend deploy.

---

## T2 — GROKCOS_OVER (baton: BATON_T2_MORGAN-GATE0_GROKCOS_OVER.md)
EXECUTE_DONE: EXECUTE_DONE_MORGAN_GATE0_V3.md

- strip_financial_fields() catches all real Firestore field names (AI Estimated Value, Purchase Cost, Melt Value, Price Paid) via keyword matching (main.py:2791-2824).
- test_morgan_gate0.py fixture uses real-shape doc with these exact field names. Assertions verify none appear in tool result.
- Privacy Mode TODO added to ai_routes.py:~118.
- Friendly "That coin is no longer in your binder" message on confirm 404.
- 491 pytest pass.

---

## T3 — GROKCOS_OVER (baton: BATON_T3_REQ032-UX_GROKCOS_OVER.md)
EXECUTE_DONE: EXECUTE_DONE_REQ032_UX_V3_AND_T3B_V3.md

- PIN focus re-requested on tap: GestureDetector on _PinBoxRow (login_screen.dart:633) calls _pinKeyboardFocus.requestFocus().
- _strengthHint label (was fontSize:12, ~line 1017 in V2) → NumistaTheme.textBodySm (:1025 in current tree).
- _StatBadge label (was fontSize:11, ~line 1037 in V2) → NumistaTheme.textBodySm (:1045 in current tree).
- Test scoped by class boundary (class FreeScanPreviewScreen) not line count.
- 433 flutter tests pass; analyze clean.

**Note:** fontSize:11 at lines 1250 and 1301 are inside class FreeScanPreviewScreen (outside login form scope). Will address in next pass.

---

## T3b — GROKCOS_OVER (baton: BATON_T3B_ALT-SITE_GROKCOS_OVER.md)
EXECUTE_DONE: EXECUTE_DONE_REQ032_UX_V3_AND_T3B_V3.md

- Entitlement guard on users/{email}: _noEntitlementChange() + _noEntitlementOnCreate() with _serverOnlyKeys() list.
- Coins + profile excluded from wildcard (rules:126,:131).
- Emulator tests: Addendum C (7 tests) added to firestore.rules.test.js. BLOCKED by no Java — same as T1B.
- UiVariantService: fail-safe to classic on non-200 (V2, carried forward).
- Banner textBodySm (V2, carried forward).
- numista_backend/firestore.rules: NOT-DEPLOYED header (V2 doc fix).

---

## Housekeeping
- Deleted stale BATON_T1_REQ031_AGCOS_WILCO.md (per NET-016 request).
- Deleted BATON_T1B_REQ031B_AGCOS_WILCO.md (replaced by GROKCOS_OVER).

Ready for your scores. OVER
