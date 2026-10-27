# SAG Paste Packet — FAIL-FIX Plan.v1 (NET-629) Round 1

**Paste this whole note into Stand Alone Grok.** Reply here with score /100 and GO | CONDITIONAL GO | HOLD.

---

## Ask Stand Alone Grok

You are scoring **FAIL-FIX Plan.v1** for Numista.Ai Mint B− after FT NET-627 OVERALL FAIL on preview `p7-gate` (SHA `751a4305`). Locked chain: AG Plan.v1 → Argon **71/100 CONDITIONAL GO** → GB CoS **91/100 PASS WITH EDITS** → **you (SAG)** → Eric typed YES → EXECUTE preview only.

**Treat Argon Must-Fix 1–5 + GB FF-1..3 as mandatory coding / EXECUTE-brief folds (not optional polish).** Say GO / CONDITIONAL GO / HOLD and a /100. Prefer locking IGs into EXECUTE over Plan.v2 unless a P0 remains uncovered.

### Plan
`ERIC_BMINUS_FAILFIX_PLAN_v1_2026-10-27.md` (docs commit `68b1ef65` on origin/dev). Scope: only I-07/PM-01 (26RJ image+val after Commit) and I-04b (26SQRP Fee $0 vs S&H $9.95).

### Prior SAG lock (88 CG on FAIL brief) — still in force
Commit re-enrich + issue_price baseline + async kick; sets/rolls catalog images+issue price first (don’t wait on Greysheet); 26RJ catalog URLs must exist+copy; 26SQRP Hub Fee $9.95 without breaking 26RJ Fee $9.95; no regress IG-1 dup / contrast / wrap.

### What Plan.v1 got right (Argon+GB concur)
- I-07: `keep_set_as_is` skips enrich **CONFIRMED**; commit stamps snake_case vals but misses PascalCase `AI Estimated Value` that the grid reads → Valuation Pending **CONFIRMED**. FT path was **Commit** (not Keep-as-Set); keep_set fix still mandatory as second path.
- Catalog **has** 26RJ image URLs (`us_mint_catalog_service.py:200-202`); problem is copy/wiring + UI dual-read.
- I-04b: `pack_expanded` zero at `main.py:7718-7719` **CONFIRMED**.

### Argon Must-Fix P0 (mandatory IGs for EXECUTE) — Plan.v1 incomplete without these
1. **Also patch `main.py:7589–7590`** — blanket `allocated_fee = 0` for any invoice containing 26SQRP. Fixing only `:7718` leaves USM24086141 at Fee $0.
2. **Clarify fee on parent roll lot vs children** — Hub roll row carries $9.95; don’t multiply full S&H onto every pack-expanded child; preserve 26RJ Fee $9.95.
3. **Wire real BackgroundTasks / async enrich kick** on `commit_reviews` (not vibes — name function/signature).
4. **Dual-write PascalCase `AI Estimated Value`** (and `ai_estimated_value`) on the **Commit** path too.
5. **Prove catalog image copy for 26RJ** on Commit (Theme stamped but images empty in FT) — Firestore dump gate.

### GB FF folds (also mandatory)
- **FF-1:** Catalog URLs exist (Argon confirmed) — still prove copy onto vault before persist + FT screenshot.
- **FF-2:** Same as Argon #2 (parent vs children fee).
- **FF-3:** Baseline fill-missing-only (don’t overwrite non-blank Greysheet/collector vals); log enrich errors (no bare `except: pass`); sets/rolls skip Greysheet overwrite in async worker.

### Retest proofs before founder (unchanged)
(a) Commit new 26RJ → image + non-zero val (baseline OK if Greysheet N/A)  
(b) 26SQRP Hub Fee = $9.95  
(c) Prior PASS green: dup amber, 26RJ Fee $9.95, contrast, wrap  
+ Firestore dumps of committed 26RJ + 26SQRP Hub row in FT package

### What we need from you
1. Score /100 and GO | CONDITIONAL GO | HOLD  
2. Confirm Argon Must-Fix 1–5 + GB FF-1..3 as mandatory EXECUTE folds (amend with pinpoint text if needed)  
3. Confirm no Plan.v2 required if those IGs are locked into the coding brief  
4. Explicit: **NO EXECUTE / NO founder retest** until Eric typed YES after your GO. origin/main LOCKED. Preview `p7-gate` only.

**Fallback (Eric locked, not this round):** if next FT still misses a P0 → Argon writes plan → GB+SAG review → Claude/3.8 EXECUTE only. Finish this AG cycle first.
