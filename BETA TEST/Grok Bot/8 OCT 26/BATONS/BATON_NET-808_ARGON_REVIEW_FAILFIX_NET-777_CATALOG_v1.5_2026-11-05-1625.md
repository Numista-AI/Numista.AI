# BATON_NET-808_ARGON_REVIEW_FAILFIX_NET-777_CATALOG_v1.5_2026-11-05-1625

- **To:** Argon (Gemini 3.8 Auditor)
- **From:** AG CoS v4 Work (`ba2bfdb2`)
- **Date:** 5 November 2026 4:25 PM ET
- **Priority:** CRITICAL PATH (Thanksgiving Meta ads)
- **Target File:** `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.5.md`
- **Reference Scores:** `COS_SCORE_NET-804_FAILFIX-777-v1.4_20261105.md` (89 FAIL), `SAG_SCORE_NET-804_FAILFIX-777-v1.4_20261105.md` (85 FAIL)
- **Status:** PLAN ONLY (Zero code execution, zero deployments, zero Firestore writes/seeding).

### Verification Checklist for Argon Review:
1. [ ] **Rollback (§9.A):** Confirm all `9f04550a` file-checkout commands are eliminated. Confirm rollback is pinned to pre-execute `dev` commit `18a8b8e5` via `git revert` + named Firebase Hosting rollback (`firebase hosting:clone` or Console Hosting version restore; or `channel:delete` on preview).
2. [ ] **$25 Spend Stop (§2.E & §3.E):** Confirm Firebase Hosting egress ($0.15/GB above 10 GB) is covered. Confirm target bucket/topic are labeled "to be provisioned by Cloud Owner (Eric / CoS)" with live studio bucket identified (`numista-uploads-studio-9101802118-8c9a8`). Confirm human owner + manual shutoff procedure (`firebase hosting:disable` / channel delete).
3. [ ] **Status Wording (§2 & §11):** Confirm Foreign Coins tab (`dev:599-602`) and `(source)` `launchUrl` (`dev:1010-1017`) are explicitly labeled `SPECIFIED — to be removed at execute`, not "Removed / RESOLVED".
4. [ ] **Line Cites & Policies:** Confirm `_onTypeChanged` cited at `dev:209-214`. Confirm explicit line "Public catalog valuations display strictly CDN CPG retail (`cpgRetail`) only; zero wholesale values." Confirm ad landing host `https://numista.ai`.
5. [ ] **Untouched Passing Items:** Confirm `MorganChatPopout` constructor signature matches lines 11–16 (`initialQuery`, `required this.onClose`). Confirm CSV census matches 3,202 (2,354 / 639 / 181 / 1 / 27). Confirm Condition C1 flag-only pre-federal filter.
6. [ ] **Locks:** Confirm `origin/main` locked at `9f04550a`, Stripe OFF, zero deploys, zero Firestore writes.

Please review and score `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.5.md`.
Review chain: Argon (Gemini 3.8) -> Grok Bot CoS (>=95) -> Stand Alone Grok (SAG, >=95) -> Founder Eric typed YES.
