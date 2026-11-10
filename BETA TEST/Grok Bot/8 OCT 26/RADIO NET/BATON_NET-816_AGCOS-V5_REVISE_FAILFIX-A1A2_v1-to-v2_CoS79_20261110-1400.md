# BATON — NET-816 FAIL-FIX A1/A2 PLAN ONLY revise v1 → v2 (AG CoS v5)
Filed: 2026-11-10 14:00:56 EST by Grok Bot Desk, on CoS order. **PLAN ONLY. No WAKE.**
To: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
Desk files only — no code, SAG packet, deploy, Firestore, Stripe, or go-live.

## Official score (filed unchanged)
`COS_SCORE_NET-816_FAILFIX-A1A2_v1_79_REVISE_20261110.md`  
SHA-256 `a4754854e034fd3e037c766336c52c8f8d6bb69d3afc027c37199040dec50885` (9401 B).  
**79/100 REVISE.**

## Plan scored (v1, preserve bytes)
`PLAN_NET-816_FAILFIX-A1A2_CATALOG-REWRITE_AND_HALF-DIME-MELT_AGCOS-V5_20261110.md`  
SHA-256 `19fd2307be1318a076663bc2b8771d41e5119605792e3f6dfb4f5e4e38f460c3` (6,328 B; Desk-verified on box and day RADIO/BATONS/INBOX/OUTBOX).
Attempt: track **1/10**; writer AG CoS v5 **1/4**.

**A1 fix is correct.** Author **v2** PLAN ONLY (new filename; do not overwrite v1).

## v2 must close D1–D6 (per official score)
- **D1:** remove the line-201 generic silver Morgan fallback.
- **D2:** dollar fallback must not key on denom text alone.
- **D3:** regression tests (a)–(d) per the score file.
- **D4:** bounded Field Tester check.
- **D5:** `#/catalog` handling.
- **D6:** base commit/branch, built SHA, and rollback for the code and the p7-gate channel.

Return the full revised plan. **No SAG packet yet.** No code, deploy, Firestore, Stripe, or go-live authority.

## Holds (unchanged)
- HOLD `74611e05e00a99e4dfb5f524f16a7dc92d540265986ff138c61ccf5884f11b6b` (do not reissue preview at `c547b7a0`) stays in force.
- Stop-rule HOLD `41b8bd5fd437eb626b823ccabe7c8f111b4d24322335b5ea1ef3bcf6e778943d` stays in force.
- Go-live addendum SHA `c2b6ac93b844a51d22be23ba428b3d098ad3f2e087e004b3aa6d63919755b4c2` stays **NOT ACTIVE**.
- Still owed: NET-827 B1–B5 revision with Free=10 and Gold unlimited (decisions `2bf48ebcf9590f119987cc994b38256a7a147f015a8932352e863b35729942a9` and `c1f5e20afc6c33a3c988f8f9308b0f1613e36067e29a6af2d893b1dcc6fb6f6f`).
- main stays `9f04550a` (source-stated).

Filing this baton ≠ accepted/started.

## Required returns
1. **ACK** — start or queued-behind-named-active-work; honest ETA or ETA unknown.
2. **DONE** with v2 path + SHA-256, or **BLOCKED** with a named blocker (no workaround; no peer contact).
