# BATON — NET-827 Stripe fail-fix PLAN ONLY — attempt 4 of 10 (Carbon try 2 of 4)
From: Grok Bot CoS, 10 Nov 2026 ~6:55 PM ET. To: AG Gemini 4 Carbon.
Your v1.8 (65,130 B, SHA-256 BCC3F2D33B4799F2D4F8D4B17E0CAC226BDC223184248D3E75DE6E9C452A2E38) scored 85 REVISE.
Read the full score record first: C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\10 NOV 2026\Carbon\COS_SCORE_NET-827_FAILFIX-B1B5_v1.8_85_REVISE_20261110.md (18,288 B, SHA-256 CBF4FB6CD0F8C657825D033B31C08FABC5FF7638E68A4CD604AE025E3505EC02).
Keep everything v1.8 closed (N2, A1–A6, and all of Eric's decisions). Write v1.9 from v1.8.

## Must fix
1. (−6) Firestore rules: as written they would stop every user from listing their own collection on the LIVE app (list queries are rejected because existing coins lack the lock field and the app's queries are unfiltered). The rules deploy to production, which is frozen under hold 41b8bd5f. Either enforce the lock without breaking unfiltered owner list queries, or move locked-coin enforcement to the server or the app with a matching app change in the file list. Decide the add-coin rule. Add rules unit tests (emulator), the exact deploy command, a rollback that restores the current rules file by SHA, and mark the rules deploy explicitly as a PRODUCTION change that needs its own scoped Eric YES.
2. (−3) Dedupe migrated coins: email-keyed originals still exist after migration to the user-ID folder. Count and export each coin once (define the dedupe key). Lock coins only, not currency or wishlist items.
3. (−3) Use the real production bucket numista-uploads-studio-9101802118-8c9a8, not the invented numista-vault-user-content. Set the preview bucket in the preview deploy step, and make the guard block the real production bucket.
4. (−2) List and guard (or prove unreachable from the preview service) the remaining production connections: brain_processor.py, services/canon_sync_service.py, numista_scraper, the storage client in routes/deps.py, and the plain storage clients in main.py and estate_routes.py. Put them in the file list.
5. (−1) Restore v1.7's lock and CSV tests, including the one that rejects an unauthenticated CSV request.
Advisory: state who may use p7-gate during NET-827 (no real users), since its login and data stay on production while its API calls go to the preview backend.

## Limits
PLAN ONLY. No code, commits, deploys, rules deploys, Firestore, Stripe or Cloud Run. Holds 74611e05 and 41b8bd5f stand. Stop by 3 AM ET.
Save as PLAN_NET-827_FAILFIX-B1B5_STRIPE-CHECKOUT-PREVIEW_v1.9_AG-CARBON_20261110.md in the Carbon folder and reply with name, size and SHA-256 (Get-FileHash), plus how you closed each item.
