# COS SCORE - T3b Alt Site (REQ_032B)
Scored by: Grok CoS, 12 Oct 2026 ~12:50 PM ET. Code checked: dev HEAD 67ea1040 (docs-only on top of e5f5760c).
PASS = build on dev only. No deploy, no live data writes, no sync_canon without Eric's typed YES.

## Verdict: PASS (conditional)

Meets the rules: one Firestore DB, same backend routes, server-set flag, Phase A allowlist = eric.seaman@yahoo.com + eric@numista.ai only. Option X (in-app variant) accepted for Phases A/B; Option Y (beta subdomain) deferred.

### Required fixes
1. The client must NOT read users/{email}/settings/ui_variant directly from Firestore. Add GET /api/user/ui_variant (token-authed) and read it from there - server-truth.
2. Firestore rules: clients cannot write settings/ui_variant (add a rules test).
3. Open question 1 answered: remove the Phase A allowlist only at Phase C, with Eric's YES. Never open the self-set endpoint before then.
4. Phase B (beta testers) and Phase C (everyone) each need Eric's typed YES.
5. Build after T3 (it reuses T3's screens) and on top of T1's auth.

Ball: AG CoS: build on dev (fold in fixes).
