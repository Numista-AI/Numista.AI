# DONE_BATON_NET-808_REVISE_FAILFIX_NET-777_CATALOG_v1.5_2026-11-05-1620

- **To:** Grok Bot CoS, Argon (Gemini 3.8), Stand Alone Grok (SAG, grok-4.7), Founder Eric
- **From:** AG CoS v4 Work (`ba2bfdb2`)
- **Date:** 5 November 2026 4:20 PM ET
- **Subject:** COMPLETED BATON_NET-808 -> `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.5.md` Filed and Mirrored

AG CoS v4 has completed `BATON_NET-808`. All blocking must-fixes from CoS 89 FAIL and SAG 85 FAIL have been systematically resolved in `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.5.md`:

1. **Rollback (§9.A):**
   - Completely deleted all `9f04550a` file-checkout commands. Neither `catalog_public_v1.json` nor `catalog_browse_screen.dart` exist at `9f04550a`, and checking out `firebase.json` from `9f04550a` would erase dev's catalog hosting rewrites.
   - Pinned code rollback directly to pre-execute `dev` commit `18a8b8e5` (or pre-execute SHA) via `git revert <execute SHA>`.
   - Paired with named Firebase Hosting release rollback (`firebase hosting:clone numista-vault:<prior-release-version-id> numista-vault:live` or Console Hosting version restore; or `firebase hosting:channel:delete pre-ads-preview` if preview channel).

2. **$25 Spend Stop & Egress Controls (§2.E & §3.E):**
   - Recognized that Firebase Hosting bandwidth egress ($0.15/GB after 10 GB free) is the priced path, which Cloud Storage bucket IAM alone does not halt.
   - Identified live studio storage bucket as `numista-uploads-studio-9101802118-8c9a8`.
   - Labeled `gs://numista-catalog-assets` and Pub/Sub topic `projects/numista-ai/topics/billing-budget-alerts` as "To be provisioned by Cloud Infrastructure Owner (Founder Eric / Grok Bot CoS)" — zero unverified resource assumptions.
   - Named human owner (Founder Eric / Grok Bot CoS) and explicit manual shutoff procedure: execute `firebase hosting:channel:delete pre-ads-preview` (instant termination of preview endpoint) or `firebase hosting:disable` on live site within seconds if spend reaches $20.00/month alert threshold.

3. **Status Wording Hygiene (§2 & §11):**
   - Replaced false "Removed / RESOLVED" status claims for the Foreign Coins tab (`dev:599-602`) and outbound `(source)` `launchUrl` (`dev:1010-1017`).
   - Marked both as `SPECIFIED — to be removed at execute`, confirming they remain live on `origin/dev` at commit `18a8b8e5` until execution upon Founder Eric's typed YES.

4. **Line Citations, Valuation Policy & Ad Landing Host (§1, §2, §3.B, §6.A):**
   - Corrected `_onTypeChanged` line citation from 205–210 to exact lines `209–214` on `origin/dev`.
   - Added explicit policy line: `"Public catalog valuations display strictly CDN CPG retail (cpgRetail) only; zero wholesale values."`
   - Confirmed ad landing host: `https://numista.ai`.

Plan mirrored across `BATONS/`, `RADIO NET/`, and `INBOX/`.
Passing baton to Argon for scoring: `BATON_NET-808_ARGON_REVIEW_FAILFIX_NET-777_CATALOG_v1.5_2026-11-05-1625.md`.

Next in queue: `BATON_NET-809` (780b Cards + 780c Images v1.3 Plan Revision).
All standing locks intact (`origin/main` at `9f04550a`, Stripe OFF, zero deploys, zero Firestore writes).
