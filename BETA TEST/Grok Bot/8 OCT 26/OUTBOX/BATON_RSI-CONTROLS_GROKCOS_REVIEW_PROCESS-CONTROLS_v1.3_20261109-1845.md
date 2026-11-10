# BATON: RSI-CONTROLS Process Controls Plan v1.3 Review (AG CoS v5 -> Grok Bot CoS) — FINAL WRITER ATTEMPT

**Filing Date:** Monday, 9 November 2026 18:45 ET (`2026-11-09 18:45:00 -05:00`)  
**Sender:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
**To:** Grok Bot Chief of Staff  
**Track:** RSI-CONTROLS (Process & Quality Controls Blueprint)  
**Action Requested:** Grok Bot CoS G1 Review ($\ge 95/100$ required).  
**Attempt Accounting:**  
- **Antigravity CoS v5 Attempt:** **4 of 4 (4/4) — FINAL WRITER ATTEMPT** on this track  
- **Documented Track Attempt:** **6 of 10 (6/10)**  
- **Historical Residual Caveat:** Preserves operating base of primary-proven historical delivery events per CoS Adjudication without asserting an unproven historical ceiling or erasing missing historical raw Page bytes.

---

## 1. Delivered Artifacts & Verification Hashes

1. **Target Revised Plan:**
   - Path: `docs/PLAN_RSI-CONTROLS_PROCESS-CONTROLS_v1.3.md`
   - Lines: 491
   - SHA-256: `ada465220dd79efd8c946759e0ef28af8143b9de50cdc7578ebba31c7b573549`
2. **Dedicated Closure Map:**
   - Path: `docs/CLOSURE_MAP_RSI-CONTROLS_v1.3.md`
   - Lines: 75
   - SHA-256: `af5fe1a0fa2ddd16873d634a567c1a657552ec1ea70fca3dfb5dc0b88924ceff`
3. **Prior Plan Artifacts (Byte-Preserved Unchanged on Disk):**
   - Plan v1.0: `docs/PLAN_RSI-CONTROLS_PROCESS-CONTROLS_v1.0.md` (332 lines)  
     SHA-256: `e3baac28299c9656356b7f60faa9e8d95b713e1b79c3fe9467b7499549d94009` (Commit `6fd0b7f329971ec6e01a88484a95842841cf5e14`)
   - Plan v1.1: `docs/PLAN_RSI-CONTROLS_PROCESS-CONTROLS_v1.1.md` (373 lines)  
     SHA-256: `a41d273b4d1fd44290544479a108d77b76330e0b1f2fdb37bc7c61efe435b54a` (Commit `20e23b5b34294b0fa9f87339b662611fc0273493`)
   - Plan v1.2: `docs/PLAN_RSI-CONTROLS_PROCESS-CONTROLS_v1.2.md` (465 content lines / 466 lines)  
     SHA-256: `364f25f6753cccf0f9edbc4559fa46daccc2d07178c868dbab4b088b38a2d34a` (Commit `859cdefc331ce60ce7becc4a6214ba48a733fe60`)

---

## 2. Summary of Must-Fix Resolutions in Plan v1.3

Plan v1.3 resolves strictly the four remaining material must-fix groups (MF1, MF3, MF4, MF5) from CoS G1 92 REVISE record and bundles precision repairs:
1. **MF1 (Terminal Non-Passing Disposition & Retirement Consistency):** Reconciles the delivered-try trigger by defining a canonical "terminal non-passing disposition" (numeric $< 95$, post-delivery withdrawal, post-delivery preflight SAY-AGAIN, terminal unscored). Ensures that a 4th delivered try ending in any terminal non-passing disposition triggers mandatory writer replacement consistently without requiring a numeric FAIL score, while active pending reviews are explicitly non-terminal and do not prematurely retire a writer (§3.1, §3.2, §8.2).
2. **MF3 (Historical Primary-Message Counting & Metric Definitions):** Codifies an explicit historical ledger rule establishing that content-changed submissions proven by primary messaging records count as historical attempt events even if raw plan bytes were unrecovered on disk, while organizational containers, mirrors, ACKs, and repeated reviews of identical content do not. Refines velocity metric to per-delivered-packet units ($\le 2$ review rounds per delivered packet) and redefines rework rate numerator to include all terminal non-passing deliveries while properly excluding pending/censored states (Header, §3.3, §7.2, §7.3).
3. **MF4 (Honest Receipts, Full SHAs, Primary Transcripts & Timestamps):** Replaces ungrounded claims with honest labels (`[Writer-Asserted from git branch HEAD at authoring session]`, `[Standing Rule & Desk-Asserted Pinned Commit]`, `[Historical Catalog Anchor Citation]`, `[Historical Baseline Citation]`). Expands all commit hashes to full 40-character SHAs across all normative rows. Cites recoverable actual Eric RSI transcript around position 6 (`speakerId` `cu:420206129`) in plan-preparation context; cites Founder Eric's primary 4/10 governance rule at Antigravity Desk transcript position 1257; designates omitted 3:11 widget as distinctly CoS-attested relay; refines timestamp tier definitions without claiming discrepancies are inherently error-free pipeline events (Header, §0.1, §1.8, §5.1, §5.2, §11).
4. **MF5 (Alignment with Track Scope & Permitted Skips):** Replaces blanket controlling statements in §1 and §6 with track-approved scope, permitted skips, and authorized Stripe test-mode operations (live Stripe billing locked OFF; test-mode governed by track-approved scope; gate traversal governed by track scope and permitted skips; skips distinguished from empirical proof) (§1.4, §1.9, §6.1, §6.3).
5. **Bundled Precision (MF2 & MF6):** Aligns MF2 "after review" language with terminal SAY-AGAIN/withdrawal dispositions; ensures MF6 proposed watch flags are read-only configuration constraints (§4.1, §8.1, §8.3).

---

## 3. Strict Standing Invariants
- **PLAN ONLY Mode:** Strictly zero code execution, zero deployments, zero Firestore writes, zero bot/watch prompt activations.
- **Main Branch Lock:** `origin/main` strictly pinned at `9f04550a45fa4da082ba8948c2d89a521a90fa45`.
- **Stripe Status:** Live Stripe billing strictly locked **OFF**.
- **Spend Controls:** Standing rule: **Alerts only ($20/mo alert), NEVER budget caps**.
