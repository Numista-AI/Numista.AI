# CLOSURE MAP: RSI-CONTROLS Process Controls Specification v1.1 -> v1.2

**Document Version:** 1.2  
**Timestamp Provenance (Declarations & Meanings):**  
- **Artifact Header DTG (Box-Clock Authoring):** Monday, 9 November 2026 17:20 ET (`2026-11-09 17:20:00 -05:00`)  
- **Box-Copy Filesystem mtime:** Recorded on disk at container/box write time  
- **Watch-Reported Delivery Time:** Recorded by Task Master / watcher on container detection  
- **Actual Filing Time:** Formal baton delivery and git push timestamp  
*(Note: Timestamp differences between header DTG, box-copy mtime, watch detection, and baton filing reflect distinct procedural pipeline events, not clock fabrication or data errors).*  
**Author:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
**Track:** RSI-CONTROLS (Process & Quality Controls Blueprint)  
**Target Document:** `docs/PLAN_RSI-CONTROLS_PROCESS-CONTROLS_v1.2.md` (SHA-256: `364f25f6753cccf0f9edbc4559fa46daccc2d07178c868dbab4b088b38a2d34a`, 466 lines)  
**Prior Documents (Byte-Preserved Unchanged):**  
- `docs/PLAN_RSI-CONTROLS_PROCESS-CONTROLS_v1.0.md` (SHA-256: `e3baac28299c9656356b7f60faa9e8d95b713e1b79c3fe9467b7499549d94009`, 332 lines)  
- `docs/PLAN_RSI-CONTROLS_PROCESS-CONTROLS_v1.1.md` (SHA-256: `a41d273b4d1fd44290544479a108d77b76330e0b1f2fdb37bc7c61efe435b54a`, 373 lines)  
**In Response To:**  
1. Grok Bot CoS G1 Disposition `COS_SCORE_RSI-CONTROLS_PROCESS-CONTROLS_v1.1_89_REVISE_G1_HOLD-COUNT_20261109.md` (89/100 REVISE; Deductions: 3+1+2+2+2+1 = 11).  
2. Grok Bot CoS Adjudication `COS_ADJUDICATION_RSI-CONTROLS_ATTEMPT-COUNT_20261109.md` (Recorded 2026-11-09 04:54:45 PM EST) resolving count hold.  
**Attempt Accounting:**  
- **Antigravity CoS v5 Attempt:** **3 of 4 (3/4)**  
- **Documented Track Attempt:** **5 of 10 (5/10)**  
- **Historical Residual Caveat:** Reconciles operating base of 4 documented track submissions (2 RSI Engineer + 2 AG CoS v5) from recovered primary delivery messages without asserting an unproven historical ceiling or erasing missing historical raw Page bytes.

---

## Executive Summary of Revisions

This closure map provides an exhaustive, line-by-line reconciliation of all six must-fix groups (MF1 through MF6) and bundled precision repairs from Grok Bot CoS G1 evaluation (89 REVISE) and the CoS Adjudication. Plan v1.2 strictly resolves every finding:
1. Enforces retirement strictly as *"4 delivered tries still not right"*, closing post-delivery withdrawal, unscored packets, and SAY-AGAIN loopholes (MF1).
2. Distinguishes plan-quality review passes (CoS $\ge 95$ + SAG $\ge 95$) from Founder Eric execution authorization; permits 10th attempt evaluation then hard halt; mandates explicit proposed child budgets (MF2).
3. Reconciles packet identity with document-only watch routines using immutable packet hash/manifest with commit metadata; defines velocity and rework rate metrics (MF3).
4. Grounds all claims in verified disk receipts; establishes 4-tier timestamp provenance; preserves approval-relay caveat requiring Founder Eric's OWN typed YES (MF4).
5. Eliminates contradictory policy overlays, defers to track-approved scope, provides domain-specific FT proof, and bans reopening superseded repair plans (MF5).
6. Establishes non-toggleable 4/10 safeguards, restores override audit trail, clarifies schema vs mechanical rollback, and preserves UNAPPLIED boundaries (MF6).
7. Incorporates explicit Section 0.1 with full 40-character SHAs and verbatim Rule 6a code quotes; eliminates placeholders.

---

## Must-Fix Group Reconciliation Matrix

| Group ID | Deduction | CoS G1 Finding / Mandate | Resolution in Plan v1.2 | Plan v1.2 Location |
|---|---|---|---|---|
| **MF-1** | **-3** | **L60–68 / 85–89 / 273–280 — Retirement condition & anti-evasion loopholes:**<br>- Retirement must be after "4 delivered tries still not right", not merely 4 scored failures.<br>- Close loopholes: post-delivery withdrawal-before-score, unscored packets, and SAY-AGAIN must not evade failure trigger.<br>- Count delivered unique packets once.<br>- No extra count for external waiting or same-packet multi-review. | - Codified retirement strictly as *"4 delivered tries still not right"* (failure to achieve required plan-quality pass: CoS $\ge 95$ AND SAG $\ge 95$).<br>- Explicitly closed anti-evasion loopholes in §3.1 and §3.2: post-delivery withdrawal-before-score, unscored packets, and SAY-AGAIN returns all count as delivered non-passing attempts.<br>- Enforced single packet counting via immutable hash/manifest.<br>- Prohibited extra counts for external waiting or multi-reviewer dual-scoring on the same packet hash.<br>- Updated proposed watch block in §8.2. | **§3.1, §3.2, §3.3, §8.2** |
| **MF-2** | **-1** | **L111 — Conflation of review quality with Eric authorization:**<br>- Distinguish plan-quality reviews (CoS $\ge 95$ + SAG $\ge 95$) from Eric execution authorization.<br>- Passing both required reviews while waiting/declining for non-plan reasons is NOT a plan failure or new attempt.<br>- Permit 10th attempt review, then hard halt (no 11th monolithic attempt).<br>- Explicit proposed child budgets. | - Clarified in §4.1 that achieving CoS $\ge 95$ and SAG $\ge 95$ successfully completes planning phase; waiting for or declining execution for business/schedule reasons is NOT a plan failure and does NOT increment attempt ledgers.<br>- Reaffirmed that 10th unique delivered attempt is fully evaluated; if still not passing, hard halt with zero 11th monolithic revisions.<br>- Mandated split proposal with explicit proposed child budgets (chunk submission caps and writer caps) awaiting Eric's typed YES in §4.2. | **§4.1, §4.2, §8.2** |
| **MF-3** | **-2** | **L60 / 92 / 246 / 256 — Watch reconciliation & metric definitions:**<br>- Commit + doc identity conflicts with document-only watch; use immutable packet hash/manifest, commit metadata only.<br>- L246 review-round velocity metric undefined.<br>- L256 rework rate numerator undefined. | - Reconciled packet identity for document-only watch environments in §3.1 and §5.1: established packet identity via immutable packet hash/manifest utilizing commit metadata only (document SHA-256 + commit SHA header metadata).<br>- Defined L246 review-round velocity metric explicitly in §7.2: $\text{Review Rounds to Pass} = \text{Count of review cycles (CoS + SAG) per delivered packet to reach } \ge 95$.<br>- Defined L256 rework rate numerator and denominator explicitly in §7.3: Numerator is count of delivered unique packets scoring $< 95$; Denominator is total delivered unique packets evaluated. | **§3.1, §5.1, §7.2, §7.3, §8.2** |
| **MF-4** | **-2** | **L24 / 177–184 / 360–368 — Verified disk receipts & timestamp provenance:**<br>- Unreceipted claims / path-exists does not prove pinned bytes / ref lock.<br>- Header DTG vs watch-reported delivery: define timestamp provenance (header vs box mtime vs watch delivery vs filing time).<br>- Ground claims in verified disk receipts; label unverified citations illustrative; zero invented checks; no clock fabrication/malice inference.<br>- Preserve approval-relay caveat; CoS confirmed primary 3:11 Eric directive. | - Added explicit Timestamp Provenance declarations in document header and §5.1 distinguishing header DTG, box mtime, watch delivery, and actual filing time.<br>- Reaffirmed no clock fabrication; discrepancies reflect pipeline stages.<br>- Grounded all code and ref citations in verified on-disk receipts in Section 0.1 and §5.2.<br>- Retained explicit `Illustrative / Unverified` labeling for external unverified sprint log observations (EVD-07).<br>- Retained approval-relay caveat requiring Founder Eric's OWN typed YES in §1.8. | **Header, §0.1, §1.8, §5.1, §5.2, §11** |
| **MF-5** | **-2** | **L23 / 191 / 223 vs L27 / 227 — Elimination of contradictory policy overlays:**<br>- Remove all-test Stripe overlay, universal 5-gate/FT overlay, and 100% test overlay contradicting track-approved scope.<br>- Defer to track-approved scope including permitted skips.<br>- Domain-specific FT proof (not a universal browser checklist).<br>- Prohibit reopening superseded repair plans. | - Eliminated contradictory overlays in §1.9 and §6.3; explicitly codified that gates defer to track-approved scope including permitted skips and branch definitions.<br>- Removed universal browser checklist requirement; replaced with domain-appropriate FT empirical proof in §6.2, §6.3, and §9.2 (screenshots for UI; curl/HTTP logs and JSON validation for backend/pricing/data).<br>- Explicitly prohibited reopening or recursively re-auditing superseded repair plans in §6.3. | **§1.9, §6.2, §6.3, §9.2** |
| **MF-6** | **-1** | **L292–302 — Non-toggleable 4/10 safeguards & rollback governance:**<br>- Make 4/10 safeguards non-toggleable absent a new Eric directive.<br>- Restore override audit trail.<br>- Clarify schema vs mechanical rollback; disclaim instant restore without adapter proof.<br>- Preserve UNAPPLIED boundary. | - Codified in §8.3 that 4-try writer retirement and 10-attempt split triggers are strictly non-toggleable; configuration flags cannot disable them absent a new Founder Eric directive.<br>- Restored emergency override audit trail requirement (`RADIO_OVERRIDE_ERIC_<track>_<DTG>.md`) in §8.3.<br>- Reaffirmed that configuration flags are schema specifications only, not implemented mechanical rollback, and disclaimed instant restore without adapter evidence.<br>- Preserved prominent UNAPPLIED caution banner in §8.1. | **§8.1, §8.3** |
| **Precision Repairs** | **Bundled** | **Placeholders, Section 0.1, Eric OWN YES, Pilot eligibility, Attempt count labels:**<br>- Eliminate placeholders; insert actual v1.0 and v1.1 hashes.<br>- Add Section 0.1 with full 40-char SHAs and verbatim Rule 6a quotes.<br>- Eric OWN typed YES required.<br>- Pilot next legitimately authorized versions only.<br>- Label AGv5 try 3/4 and documented track try 5/10 with historical residual caveat. | - Eliminated placeholders; cited exact v1.0 SHA `e3baac28...` (332 lines) and v1.1 SHA `a41d273b...` (373 lines).<br>- Created dedicated Section 0.1 at document start with full 40-character SHAs and verbatim quoted lines (lines 450, 230, 133).<br>- Enforced Founder Eric's OWN typed YES in §1.8 and §6.2.<br>- Restricted pilot candidates to prospective next-eligible versions in §7.1.<br>- Labeled document header and metadata as AG CoS v5 Attempt 3/4 and Documented Track Attempt 5/10 with historical residual caveat per CoS Adjudication. | **Header, §0.1, §1.8, §5.2, §7.1** |

---

## Detailed Line-by-Line Changes: v1.1 vs v1.2

### 1. Document Header & Metadata
- **v1.1:** Labeled Attempt 2 for AG CoS v5; header DTG `16:15 ET`. Did not define timestamp provenance tiers.
- **v1.2:** Labeled **AG CoS v5 Attempt 3 of 4 (3/4)** and **Documented Track Attempt 5 of 10 (5/10)** with explicit **Historical Residual Caveat** citing CoS Adjudication. Added explicit 4-tier Timestamp Provenance declaration (header DTG, box mtime, watch delivery, actual filing). Cited CoS Adjudication and G1 89 REVISE records. Updated baseline commit to `1832543445104103ff3bbf17e7a271233f9f2207`.

### 2. Normative Evidence Citations & Pinned References (§0.1)
- **v1.1:** Lacked dedicated Section 0.1; citations embedded in §5.2 and §11.
- **v1.2:** Added prominent **Section 0.1** at top of plan containing full 40-character SHAs, repository paths, line numbers, and verbatim source lines for `build_image_index.py:450`, `build_currency_image_index.py:230`, and `promote_user_photos.py:133`, plus verified non-existence of `scripts/reference_library` and byte hashes of v1.0 and v1.1.

### 3. Operational Constraints & Standing Boundaries (§1)
- **v1.1:** Contained general Invariant 8.
- **v1.2:** Added Invariant 8 requiring Founder Eric's **OWN typed YES** (relays alone unmet); added Invariant 9 explicitly eliminating contradictory policy overlays (no all-test Stripe overlay, no universal FT overlay on tracks with approved skips, no universal 100% test overlay contradicting approved scopes, prohibition on reopening superseded repair plans).

### 4. Scope A: Writer Replacement & Anti-Evasion Policy (§3.1–3.3)
- **v1.1:** Defined retirement after 4 failed attempts; did not explicitly close post-delivery withdrawal, unscored packets, or SAY-AGAIN loopholes.
- **v1.2:** Codified retirement strictly as *"still failing after 4 tries"* / *"4 delivered tries still not right"*. Closed anti-evasion loopholes: post-delivery withdrawal-before-score, unscored packets, and SAY-AGAIN returns all count as delivered non-passing attempts. Reconciled packet identity for document-only watch routines using immutable packet hash/manifest with commit metadata only.

### 5. Scope B: 10-Submission Trigger & Split Inheritance (§4.1–4.2)
- **v1.1:** L111 conflated plan-quality pass with Eric execution authorization.
- **v1.2:** Explicitly decoupled plan-quality pass (CoS $\ge 95$ + SAG $\ge 95$) from Founder Eric execution authorization (G-3). Codified that waiting for or declining execution for business/schedule reasons is NOT a plan failure or new attempt. Reaffirmed 10th attempt evaluation then hard halt (zero 11th monolithic attempts). Required explicit proposed child budgets in split proposals.

### 6. Scope C: Evidence Manifest & Watch Reconciliation (§5.1–5.2)
- **v1.1:** Did not explain reconciliation between git commit identity and document-only watch routines.
- **v1.2:** Codified that packet identity is established via immutable packet hash/manifest utilizing commit metadata only, enabling document-only watch routines to operate reliably without local git binaries. Grounded all entries in verified disk receipts; added EVD-09 and EVD-10 for v1.0 and v1.1 byte digests.

### 7. Scope D: Operational Lifecycle & Gates (§6.1–6.3)
- **v1.1:** Contained generic test and FT language that could be misread as contradictory overlays.
- **v1.2:** Explicitly codified that gates defer to track-approved scope, including permitted skips and target branch definitions. Specified domain-appropriate FT empirical proof (screenshots for UI; HTTP runner logs/JSON validation for backend/pricing/data). Explicitly prohibited reopening superseded repair plans.

### 8. Scope E: 5-Plan Pilot Framework (§7.1–7.3)
- **v1.1:** Review-round velocity metric and rework rate numerator were informally stated.
- **v1.2:** Formulated exact mathematical definitions for Review-Round Velocity Metric ($\le 2$ review rounds per track) and Rework Rate Numerator (delivered unique packets scoring $< 95$) and Denominator (total unique delivered packets evaluated). Restricted candidates strictly to prospective next-eligible versions.

### 9. Scope F: Proposed Watch Routine Blocks & Rollback Governance (§8.1–8.3)
- **v1.1:** Allowed boolean flags without explicitly stating that 4/10 safeguards are non-toggleable.
- **v1.2:** Updated proposed watch routine block for `ag-plan-handoff-watch` in §8.2 with all MF1–MF6 fixes. Codified in §8.3 that 4/10 safeguards are strictly non-toggleable absent a new Founder Eric directive. Restored emergency override audit trail requirement (`RADIO_OVERRIDE_ERIC_<track>_<DTG>.md`). Reaffirmed configuration schema status and disclaimed instant restore without adapter proof.

### 10. Scope G: Field Tester Evidence (§9.1–9.3)
- **v1.1:** Focused primarily on UI and API distinctions.
- **v1.2:** Expanded domain-appropriate verification categories (UI vs Backend/Pricing/API vs Data/Indexing), confirming empirical receipts are domain-appropriate rather than imposing a universal browser checklist across non-UI tracks.

---

## Byte & Hash Verification

```powershell
# Document Byte & Hash Verification Log (Box clock: 2026-11-09 17:20 ET)
# Plan v1.0 (Preserved Byte-Identical)
Get-FileHash docs/PLAN_RSI-CONTROLS_PROCESS-CONTROLS_v1.0.md -Algorithm SHA256
# -> E3BAAC28299C9656356B7F60FAA9E8D95B713E1B79C3FE9467B7499549D94009 (332 lines)

# Plan v1.1 (Preserved Byte-Identical)
Get-FileHash docs/PLAN_RSI-CONTROLS_PROCESS-CONTROLS_v1.1.md -Algorithm SHA256
# -> A41D273B4D1FD44290544479A108D77B76330E0B1F2FDB37BC7C61EFE435B54A (373 lines)

# Plan v1.2 (Revised Plan)
Get-FileHash docs/PLAN_RSI-CONTROLS_PROCESS-CONTROLS_v1.2.md -Algorithm SHA256
# -> 364F25F6753CCCF0F9EDBC4559FA46DACCC2D07178C868DBAB4B088B38A2D34A (466 lines)
```

**Submitted by:**  
Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
Monday, 9 November 2026 17:20 ET (`2026-11-09 17:20:00 -05:00`). Strict PLAN ONLY.
