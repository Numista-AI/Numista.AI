# BATON NET-808 - To: AG CoS v4 - PLAN ONLY: FAILFIX NET-777 Catalog v1.5 (CoS 89 / SAG 85 FAIL on v1.4)
Source: GB CoS ~4:00 PM ET 5 Nov. Argon 98 PASS; CoS **89 FAIL**, SAG **85 FAIL** after real-repo checks. Eric YES blocked.
Score files: `COS_SCORE_NET-804_FAILFIX-777-v1.4_20261105.md`, `SAG_SCORE_NET-804_FAILFIX-777-v1.4_20261105.md`. **Priority: CRITICAL PATH (Thanksgiving Meta ads). Take first.**

Verified OK (do not touch): MorganChatPopout 11-16 snippet; tier table = CSV (2,354/639/181/1/27); mint_mark tokens clean; C1 flag-only (9 records).

File `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.5.md`. Fix:
1. **Rollback (§9.A):** `catalog_public_v1.json` / `catalog_browse_screen.dart` do not exist at `9f04550a`, and `git checkout 9f04550a -- numista_mobile/firebase.json` strips dev's catalog hosting lines. Replace with `git revert <execute SHA>` pinned to pre-execute dev SHA (now `18a8b8e5`) + named prior Firebase Hosting release restore (`hosting:clone`/console). No `9f04550a` file checkouts.
2. **$25 stop (§2.E):** `gs://numista-catalog-assets` and `projects/numista-ai/topics/billing-budget-alerts` are unverified. Use verified ids or label "to be created" with owner; name a human owner + manual shutoff (disable public access / take channel down); cover Firebase Hosting egress, not only bucket IAM. Invent no ids.
3. **Status wording:** Foreign Coins tab (dev 599-602) and `(source)` launchUrl (dev 1010-1017) are still live on dev. Mark "SPECIFIED — removed at execute", not "Removed/RESOLVED".
4. Cite `_onTypeChanged` 209-214; add "public values CDN CPG retail only, no wholesale"; confirm landing host `numista.ai`.
**Locks:** origin/main `9f04550a`, Stripe OFF, zero deploys, zero Firestore writes, no PII/AJ data, outbound links only Congress.gov (Laws tab). PLAN ONLY.
**Chain:** AG → Argon → GB CoS (95+) → SAG (95+) → Eric typed YES.
