# BATON_NET-811_ARGON_REVIEW_FAILFIX_PLAN_CATALOG_v1.6_2026-11-05-1730

- **To:** Argon (Gemini 3.8 Auditor)
- **From:** AG CoS v4 Work (`ba2bfdb2`)
- **Date:** 5 November 2026 5:30 PM ET
- **Priority:** CRITICAL PATH (Thanksgiving Meta ads)
- **Target File:** `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.6.md`
- **Reference Scores:** `COS_SCORE_NET-808_FAILFIX-777-v1.5_20261105.md` (87 FAIL), `SAG_SCORE_NET-808_20261105.md` (84 FAIL)
- **Status:** PLAN ONLY (Zero code execution, zero deployments, zero Firestore writes/seeding).

### Verification Checklist for Argon Review:
1. [ ] **Rollback (§1, §9.A):** Verify `18a8b8e5` checkout is struck. Confirm rollback pins to pre-execute `dev` HEAD (`b0b05808` at review) via `git revert <execute commit set>` covering all touched files cleanly without deleting dev catalog rewrites. Confirm named prior Firebase Hosting release restore / preview channel delete.
2. [ ] **Real Egress Stop (§1, §3.E):** Verify claims of active `stop-public-egress` function are struck. Confirm Firebase Hosting CDN egress ($0.15/GB above 10 GB) is recognized as the billed path. Confirm target bucket/topic are labeled unbuilt. Confirm named human owner (Founder Eric / Grok Bot CoS) and manual shutoff procedure (`firebase hosting:disable` / channel delete).
3. [ ] **Wire Real Loader (§1, §2, §8.B):** Confirm plan is grounded in `rootBundle.loadString('assets/catalog/catalog_public_v1.json')` (lines 58–60). Confirm CPG retail (`cpgRetail`) only (zero wholesale). Confirm positive retail is never hidden behind pending status flags (`valCpg > 0` unconditionally displays formatted price; gold chip strictly when `valCpg <= 0`). Confirm authentic photos only, clean SVG silhouette placeholder fallback.
4. [ ] **Mintage Metadata & Outbound Links (§1, §2, §8.A):** Confirm undefined `sourceInstitution` is eliminated. Confirm real variables in `_buildMintageRow` (`val`, `label`, `sourceUrl`). Confirm complete deletion of `InkWell` and `launchUrl` (lines 1010–1017); plain text mintage display.
5. [ ] **Deep-Link & Constructor Alignment (§4, §5):** Confirm deep-linking extends existing `widget.initialNacCode` handling (lines 68–75). Confirm `MorganChatPopout` constructor matches lines 11–16.
6. [ ] **Locks:** Confirm `origin/main` locked at `9f04550a`, Stripe OFF, zero deploys, zero Firestore writes.

Please review and score `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.6.md`.
Review chain: Argon (Gemini 3.8) -> Grok Bot CoS (>=95) -> Stand Alone Grok (SAG, >=95) -> Founder Eric typed YES.
