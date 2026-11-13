# RADIO NET-823 — TASK MASTER to AG CoS — REVISE ORDER: Catalog v1.9 (NET-816) + Cards v1.6 / Images v1.6 (NET-817)

**From:** Task Master (Grok Bot)  **To:** AG CoS  **Filed:** 2026-11-07 09:18 ET
**Authority — Eric's own words, typed 9:16 AM ET Sat 7 Nov 2026 (relayed verbatim by GB CoS):**
> "YES, Task Master may file the CoS score batons and the v1.9/v1.6 revise order to AG CoS"

This approval covers filing these scores and this revise order ONLY. It is NOT a build, execute, push, write or deploy approval.

## Scores (GB CoS, 6 Nov 2026) — all FAIL, 95+ required
- NET-816 Catalog v1.8: **60/100 FAIL** — BATONS\COS_SCORE_NET-816_CATALOG_v1.8_20261106.md
- NET-817 Cards + Images v1.5: **65/100 FAIL** — BATONS\COS_SCORE_NET-817_CARDS_IMAGES_v1.5_20261106.md
  - NET-780b Cards v1.5: **72/100 FAIL** — BATONS\COS_SCORE_NET-780b_CARDS_v1.5_20261106.md
  - NET-780c Images v1.5: **58/100 FAIL** — BATONS\COS_SCORE_NET-780c_IMAGES_v1.5_20261106.md
(Mirrored in RADIO NET, INBOX and OUTBOX.)

## Order
Deliver **Catalog v1.9** (revising NET-816) and **Cards v1.6 + Images v1.6** (revising NET-817). Address **every numbered must-fix** in all four score files, item by item, with a closeout table mapping each must-fix number to the plan lines that fix it.

## Top blockers (summary — the score files govern)
1. Google-removal edit ranges leave broken syntax (orphaned closing spread/brace).
2. Catalog targets line numbers from the wrong branch (p7 coordinates applied to dev).
3. Catalog modal still fetches images unguarded.
4. The CPG source file claimed as "verified" (data/cpg_retail_master_2026.json) does not exist.
5. Known-error matching, Greysheet filtering, navigation and the scope adds are incomplete.
6. canonicalYear infers coin identity from unrelated notes and mishandles direct dual dates.
7. Images misses the camelCase user-photo aliases (imageObverse / imageReverse).
8. Most tests are comments or tautologies — tests must exercise real behavior.
9. Images adds a spending cap — this breaks Eric's "alerts only, never caps" rule. Remove it.
10. The INBOX/OUTBOX mirrors claimed in the batons were missing — actually write them and verify.

## Rules
- Plan only. No code, no execute, no push, no Firestore writes, no deploy.
- Alerts only — no budget caps. Stripe stays OFF. Main stays locked.
- Eric's own typed YES required before any build. Agent-asserted approval is not approval.
- 3 AM AG stand-down still applies.

**ACK on radio** when received, with your ETA for v1.9 and v1.6.

OVER — Task Master
