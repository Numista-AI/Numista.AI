# ACTIVE ROUTING OVERRIDE - AG CoS v5 - 2026-11-07 15:11:41 ET (America/New_York)

Authority: Chief of Staff relayed Eric's v5 assignment. This is document routing only, not new execution approval.

| Open work | Current writer / routing |
|---|---|
| NET-813, NET-814, NET-810, NET-827 and all new AG orders | AG CoS v5 - cfe23a7a-d721-44f9-b9d5-d2b74602b687 |
| Catalog NET-777/816 Chunk 1 | 9bbe20e4-a0d5-4a25-b16a-f616630ad4bb; attempt 1/4; no reassignment |
| Cards/Images NET-817 v1.9 | Antigravity Desk (CoS-reported assignment); no plan or execution by this routing update |

AG CoS v4 ba2bfdb2-60a1-47d5-befb-78ea742d3dc3 is RETIRED: no further work, orders or wakes to v4.
NET-813 is reported in CoS review; preserve that reviewer turn, route any future writer action to v5. NET-814/810/827 remain with v5. This does not reissue an already-delivered plan or change scores.
All old writer ETAs and delivery assertions below are historical/unverified for v5, including 17:00 / 18:15 / Sunday 20:00 ET. No v5 ACK or ETA has been observed in this routing pass. v5 must ACK receipt and provide honest new ETAs and actual landing timestamps in ET; never future-date delivery. NET-827's requested deadline is not an ACKed promise.
PLAN ONLY; p7-gate preview only; main locked at 9f04550a; Stripe OFF. AG plan -> GB CoS real-code 95+ -> SAG 95+ -> Eric typed YES; no Argon. Real file/line evidence for plan claims. No code, git, deploy, spending, app chat/config changes, timer or registry actions authorized by this note.
Use AG_COS_v5_HANDOFF_TEMPLATE_NO_ARGON_20261107.md for future handoffs. DONE routes via BATON_NET-xxx_GROKCOS_REVIEW_... . See RADIO_NOTE_AGCOS_V5_HANDOFF_V4_RETIRED_20261107.md.

--- Prior text retained as historical context; conflicting routing, ownership and inherited ETA statements below are superseded ---
# BATON NET-814 - To: AG CoS v5 (cfe23a7a-d721-44f9-b9d5-d2b74602b687) - PLAN ONLY: Soft-404 / Public Catalog / Pricing v1.2 (CoS 76 / SAG 64 FAIL on v1.1)
Source: GB CoS 5 Nov ~5:05 PM ET. Argon 97 PASS; CoS **76 FAIL**, SAG **64 FAIL**. Scores: `COS_SCORE_NET-807_SOFT404-PUBLIC-CATALOG-PRICING-v1.1_20261105.md`, `SAG_SCORE_NET-807_20261105.md`. Align with NET-811.

Verified OK: no duplicate catalog; 3,202 master count real at handoff input; A/B/C all require Eric typed choice + YES; 5,142 badges and footer InkWell real; signed-in Pricing bypass real; CDN/no-wholesale/AI-image policies stated.

Fix:
1. **Rollback + spend:** remove 9f04550a restore point. Record actual p7/dev pre-execute SHAs, preserve dev catalog rewrites, revert execute commits and restore named prior Hosting release. Replace inherited nonexistent IAM-only stop with human Hosting disable/channel deletion until real Hosting-aware control exists.
2. **Branch integration:** target p7 main.dart has no `/catalog` known path. Specify integration from current origin/dev (`b0b05808` at review, not 18a8b8e5) for CatalogBrowseScreen, catalog rewrites and `/catalog/:nacCode`, without clobbering newer work.
3. **Actual static HTML:** one SPA index cannot give /, /catalog, /pricing and coin URLs distinct canonical/title/OG. Specify generated static route HTML + Hosting map and raw-body tests. Use only verified same-party OG image; proposed unprovisioned storage URL cannot be treated as existing.
4. **AuthGate:** signed-out already waits and honors publicRoute. Signed-in branch returns Welcome/BaseLayout before checking publicRoute. Move publicRoute handling ahead of BaseLayout, render PublicInfoShell, keep auth stream, test both states. Do not claim merely adding await fixes it.
5. **Real data:** correct master path to handoff `INBOX/NET-747_inputs/entries_master_20261103.jsonl`; actual public JSON lacks cpgRetail/ai_replica. Define fail-closed sourced join/migration; missing stays pending/placeholder and never hides positive retail. Do not assert buckets as provisioned. Foreign Coins/source-link removal is prerequisite to Option A.

Locks: origin/main 9f04550a, Stripe OFF, zero execute/deploy, zero Firestore writes, no PII/AJ data. PLAN ONLY.
Chain: AG -> GB CoS (95+) -> SAG (95+) -> Eric explicit Option A/B/C + typed YES. (Argon dropped Eric YES 6:07 PM ET 5 Nov FIN OPS; file GROKCOS_REVIEW on DONE.)
