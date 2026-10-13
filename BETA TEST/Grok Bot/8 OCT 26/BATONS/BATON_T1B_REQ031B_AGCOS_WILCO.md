# BATON T1B_REQ031B - DEFAULT-DENY AUTH (URGENT, P0 holes live)
Holder: AGCOS  Proword: WILCO  Since: 12 Oct 2026 8:06 PM ET
Source: CR_REQ031_AUTH_ORDER.md (Code Reviewer). 48 write/scan/import/admin routes run with NO token on prod.
P0: config/greysheet-credentials (main.py:10350), config/usmint-cookies (:9344), dedup_sweep/auto_clean (:3492), estate generate-attorney-link (estate_routes.py:61), family/subaccounts POST/DELETE (subaccount_routes.py:55,:107).
TASK (top priority, above T2/T3/T3b; dev only):
1. Default-deny auth middleware in main.py: pass OPTIONS + explicit public allowlist (Stripe webhook w/ signature, public wishlist reserve, health, public pages); 401 everything else BEFORE routing/validation.
2. Keep per-route email-token 403 checks. Admin claim required on admin/config/brain/greysheet-batch/scraper. Cron via Cloud Scheduler OIDC or admin claim.
3. Acceptance test: walk app.routes; no token with empty AND valid body => 401 unless allowlisted. Full pytest.
4. Confirm Eric's admin:true claim exists before relying on it (report, don't change).
Then rename baton to BATON_T1B_REQ031B_GROKCOS_OVER.md. Deploy needs Eric typed YES.
## Log
- 8:06 PM ET GROKCOS issued.

- 13 Oct 8:31 AM ET GROKCOS: ADD rules fix: firestore.rules users/{email} must block owner writes to tier, stripe_tier, beta_tester (server-only); fix dead /profile guard; RUN emulator tests. Ship with T1B under one Eric YES. Then T2: strip real field names (AI Estimated Value, Purchase Cost, Melt Value, Price Paid) and test with real names. T3: PIN kept after email via keyboard; last 2 fonts <14.
