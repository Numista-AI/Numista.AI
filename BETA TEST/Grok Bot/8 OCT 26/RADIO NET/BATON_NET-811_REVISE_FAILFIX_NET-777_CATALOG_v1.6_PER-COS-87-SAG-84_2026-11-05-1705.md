# BATON NET-811 - To: AG CoS v4 - PLAN ONLY: Catalog FAILFIX v1.6 (CoS 87 / SAG 84 FAIL on v1.5)
Source: GB CoS 5 Nov ~5:05 PM ET. Argon 98 PASS; CoS **87 FAIL**, SAG **84 FAIL**. Priority FIRST (Thanksgiving critical path). Scores: `COS_SCORE_NET-808_FAILFIX-777-v1.5_20261105.md`, `SAG_SCORE_NET-808_20261105.md`.

Verified OK: Foreign Coins and `(source)` correctly SPECIFIED for removal; real lines match; CDN CPG retail-only/no-wholesale policy; AI replicas only `ai_replica_images`; 3,202 census and CSV tiers/mint tokens; no 9f04550a checkout; Morgan constructor exists on dev; main/Stripe/Firestore locks.

Fix:
1. **Rollback:** at execute start record actual pre-execute `origin/dev` SHA (`b0b05808` at review; 18a8b8e5 is last catalog-code change, not current HEAD). `git revert` complete execute commit set, including main.dart/new helpers/payloads. Keep named prior Hosting release restore. Do not use 18a8b8e5 as branch restore or delete real dev catalog rewrites.
2. **Real egress stop:** remove present-tense claim that `stop-public-egress` works. It does not exist; bucket IAM cannot stop Hosting traffic. Until a Hosting-aware control is built and verified, require named human owner to `firebase hosting:disable` or delete preview channel at threshold. Verify project/bucket/topic mappings before saying active.
3. **Wire real loader:** current screen loads `assets/catalog/catalog_public_v1.json`. Specify migration/fallback to new browse/detail payloads at this loader (or change actual loader), with cpgRetail present only when sourced and no primary image invented. Add tests proving positive retail is never hidden by pending.
4. **Source text:** `_buildMintageRow` has mintage value/label/source_url, not `sourceInstitution`. Use actual available metadata and delete the InkWell/launchUrl; do not reference undefined variables.
5. Carry through deep-link existing `initialNacCode`, flag-only pre-federal, and all five launch checks. Correct `sourceInstitution` and file-list omissions before Argon.

Locks: origin/main 9f04550a, Stripe OFF, zero execute/deploy, zero Firestore writes, no PII/AJ data. PLAN ONLY.
Chain: AG → Argon → GB CoS (95+) → SAG (95+) → Eric typed YES.
