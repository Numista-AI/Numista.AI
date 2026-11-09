# CLOSURE MAP: RSI-CONTROLS Process Controls Specification v1.0 -> v1.1

**Document Version:** 1.1  
**Date:** Monday, 9 November 2026 16:20 ET (`2026-11-09 16:20:00 -05:00`)  
**Author:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
**Track:** RSI-CONTROLS (Process & Quality Controls Blueprint)  
**Target Document:** `docs/PLAN_RSI-CONTROLS_PROCESS-CONTROLS_v1.1.md` (SHA-256: `a41d273b4d1fd44290544479a108d77b76330e0b1f2fdb37bc7c61efe435b54a`, 373 lines)  
**Prior Document:** `docs/PLAN_RSI-CONTROLS_PROCESS-CONTROLS_v1.0.md` (SHA-256: `e3baac28299c9656356b7f60faa9e8d95b713e1b79c3fe9467b7499549d94009`, 332 lines, preserved byte-identical)  
**In Response To:** Grok Bot CoS G1 Disposition `COS_SCORE_RSI-CONTROLS_PROCESS-CONTROLS_v1.0_86_REVISE_G1_20261109.md` (86/100 REVISE; Deductions: 3+3+2+2+2+2 = 14) and `BATON_RSI-CONTROLS_AGCOS_REVISE_PROCESS-CONTROLS_v1.0-to-v1.1_20261109-1545.md`.

---

## Executive Summary of Revisions

This closure map provides an exact, line-by-line reconciliation of all six must-fix groups cited in Grok Bot CoS G1 evaluation. Plan v1.1 directly incorporates every required change, restores Founder Eric's verbatim language, eliminates reset and administrative loopholes, removes arbitrary policy overlays, establishes honest evidence provenance, and clarifies rollback boundaries.

---

## Must-Fix Group Reconciliation Matrix

| Group ID | Deduction | CoS Finding / Mandate | Resolution in v1.1 | v1.1 Location |
|---|---|---|---|---|
| **MF-1** | **-3** | **Lines 53–85, 253 — "still failing after 4 tries":**<br>- Preserve Eric's exact words: *"still failing after 4 tries"*.<br>- Do not substitute "4 consecutive FAIL" or allow reset bypass.<br>- CoS pass followed by SAG fail does not reset counter.<br>- Dedupe CoS/SAG multi-review on same packet (1 failure).<br>- Preserve per-writer history; retirement cannot be evaded by rename or withdrawal. | - Quoted Founder Eric's exact words verbatim in §3.1.<br>- Removed "4 consecutive FAIL" substitution.<br>- Replaced with non-resetting failure accumulation: 4 failed delivered unique attempts retire writer from track.<br>- Explicitly banned reset bypass from intermediate CoS pass.<br>- Clarified multi-review deduplication: dual review on same packet hash counts as at most 1 attempt/failure.<br>- Banned evasion via rename, re-badge, or withdrawal after delivery. Updated watch block (§8.2). | **§3.1, §3.2, §3.3, §8.2**<br>(Lines 52–100, 244–260) |
| **MF-2** | **-3** | **Lines 91–137, 256–257 — "If NO ONE gets it right by 10 total attempts":**<br>- Preserve Eric's exact words.<br>- Permit 10th attempt evaluation (do not halt review before scoring 10th).<br>- If still not right after 10th review, halt further monolithic revisions, notify Eric, propose split, and no 11th monolithic attempt.<br>- No automatic child-counter reset or blanket 4/10 budgets; inherit parent history; child budgets are an explicitly proposed scope awaiting Eric's typed YES. | - Quoted Founder Eric's exact words verbatim in §4.1.<br>- Permitted full evaluation of 10th delivered unique attempt.<br>- Established hard halt on monolithic revisions if still not right after 10th review; zero 11th monolithic attempts permitted.<br>- Mandated split proposal to Eric.<br>- Removed automatic 0/10 standing reset for child chunks.<br>- Established that child chunks inherit parent history in audit ledgers and chunk authoring budgets are explicitly proposed scopes awaiting Eric's typed YES. Updated watch block (§8.2). | **§4.1, §4.2, §8.2**<br>(Lines 102–148, 253–258) |
| **MF-3** | **-2** | **Lines 57, 73–85, 231–233 — count once on delivered unique packet:**<br>- Count once on delivered unique packet (SHA-256 / commit SHA).<br>- Pre-delivery working draft withdrawn = zero.<br>- Post-delivery withdrawal / relabeled BLOCKED does not erase history.<br>- Genuine external hold = zero, but a new hash fix is a new packet attempt.<br>- Denominator = unique delivered submissions, not reviews.<br>- No administrative-rejection loophole. | - Defined attempt identity strictly by delivered unique packet (commit SHA + document SHA-256).<br>- Explicitly codified that pre-delivery withdrawn draft = 0 attempts.<br>- Codified that post-delivery withdrawal or relabeling as BLOCKED retains attempt history.<br>- Codified that genuine external holds = 0 attempts, but any subsequent revision with a new document hash is a new packet attempt.<br>- Set denominator strictly to unique delivered submissions across all quality metrics.<br>- Closed administrative rejection loopholes in disposition table. | **§3.1, §3.2, §3.3, §7.3**<br>(Lines 56–99, 230–235) |
| **MF-4** | **-2** | **Lines 10, 23, 33–36, 134–137, 156–169, 319–328 — evidence receipts & honest provenance:**<br>- Cite existing receipts for baselines, budgets, and verified commands/paths.<br>- Label illustrative/unverified citations explicitly.<br>- Honest box-clock timestamps matching actual file creation/editing times.<br>- No invented commands or unauthorized operational checks; file normal-route evidence blockers for external dependencies (e.g. Task Master ledger). | - Labeled sprint log historical totals in §2.1 and §5.2 as `Illustrative / Unverified` pending Task Master ledger reconciliation (recorded as normal-route evidence blocker).<br>- Grounded all normative citations in verified on-disk receipts (EVD-01 through EVD-06, EVD-08).<br>- Pinned honest box-clock timestamps matching actual file creation/edit times (16:15 ET).<br>- Eliminated unverified forward DTG offsets.<br>- Confirmed zero unauthorized cloud queries or scraping executed. | **§1, §2.1, §5.1, §5.2, §11**<br>(Lines 4–11, 31–37, 150–178, 319–332) |
| **MF-5** | **-2** | **Lines 19–25, 173–208, 214–233, 276–291 — no exclusive policy overlays:**<br>- Remove exclusive p7-branch / all-test Stripe policy overlays.<br>- No extra ACK approval tier.<br>- Preserve each track's actual baseline and standing constraints (CoS $\ge 95$, SAG $\ge 95$, Eric typed YES).<br>- Remove universal 10-of-10 test threshold; track-specific tests govern.<br>- No generic automatic preview deploy.<br>- Case-appropriate empirical FT proof on authorized verified target (inspection $\ne$ submit; UI screenshots for UI, HTTP/JSON logs for backend/pricing).<br>- Prospective eligible versions only; no pilot restart of completed work. | - Added invariant §1.8 explicitly prohibiting exclusive policy overlays across unrelated tracks.<br>- Preserved standard 5 gates without adding an extra ACK approval tier.<br>- Replaced universal "10-of-10" test requirement with track-specific automated test suite passing 100% in Gate G-4.<br>- Removed automatic preview deploy claims; deploys require explicit authorization.<br>- Replaced mandatory universal UI screenshot requirement with case-appropriate empirical proof (UI captures for frontend; HTTP logs and JSON schema validation for backend/pricing).<br>- Confirmed pilot applies prospectively to eligible versions only without restarting completed work. | **§1.8, §6.1, §6.2, §6.3, §7.1, §7.3, §9.1, §9.2**<br>(Lines 27–28, 180–215, 217–235, 276–294) |
| **MF-6** | **-2** | **Lines 244–272, 295–315 — rollback / activation / pilot governance:**<br>- Proposed flags are configuration specifications, not implemented mechanical rollback.<br>- No instant restore claim without adapter evidence.<br>- Rollback cannot disable mandatory 4/10 safeguards under generic pilot permission.<br>- Exact activation text / saved routine version reviewable before Eric typed YES, with snapshot + rollback scope.<br>- Pilot approval is not permanent adoption.<br>- All insertions remain strictly UNAPPLIED. | - Clarified that proposed boolean flags are configuration schemas, not implemented rollback.<br>- Explicitly disclaimed instant restore claims pending adapter implementation under future authorized work.<br>- Mandated that rollback mechanisms cannot disable Founder Eric's 4/10 safeguards.<br>- Mandated that exact activation text, configuration snapshot, and rollback scope must be reviewable by Founder Eric prior to any typed YES.<br>- Clarified that 5-plan pilot approval is strictly pilot-scoped, not permanent sprint adoption.<br>- Retained prominent UNAPPLIED caution banner in §8.1. | **§8.1, §8.3, §10**<br>(Lines 237–243, 261–274, 296–316) |

---

## Detailed Line-by-Line Changes: v1.0 vs v1.1

### 1. Header & Authority
- **v1.0 (Lines 4, 10):** Date labeled `~15:45 ET`; baseline commit `9c940715`.
- **v1.1 (Lines 4, 10, 11):** Date labeled honestly at box clock `2026-11-09 16:15:00 -05:00`; baseline commit updated to `6fd0b7f329971ec6e01a88484a95842841cf5e14`; explicit reference to Grok Bot CoS G1 disposition `COS_SCORE_RSI-CONTROLS_PROCESS-CONTROLS_v1.0_86_REVISE_G1_20261109.md` and baton.

### 2. Operational Invariants (§1)
- **v1.0 (Lines 18–25):** Listed 7 invariants without explicit protection against cross-track policy overlays.
- **v1.1 (Lines 18–28):** Added Invariant 8 explicitly stating that this plan does not impose exclusive policy overlays on tracks with their own verified baselines and adds no extra approval tiers.

### 3. Historical Provenance (§2.1)
- **v1.0 (Line 33):** Cited raw historical attempt totals as asserted facts without qualification.
- **v1.1 (Lines 33–35):** Explicitly categorized historical sprint log counts as `Illustrative / Unverified` observations, noting that official Task Master ledger reconciliation is an external evidence blocker.

### 4. Scope A: Writer Replacement Policy (§3.1–3.3)
- **v1.0 (Lines 53–85):** Used "4 consecutive FAIL dispositions" and stated that PASS "resets consecutive writer failure streak".
- **v1.1 (Lines 53–100):** 
  - Restored Eric's exact words: *"If someone is still failing after 4 tries, somebody else take over."*
  - Replaced consecutive language with non-resetting failure accumulation: 4 failed unique delivered attempts retire the writer.
  - Eliminated the reset loophole: intermediate CoS pass does not reset failure accumulation if downstream gate fails.
  - Codified multi-review deduplication: dual scoring on same packet hash = 1 attempt / 1 failure.
  - Clarified disposition table: pre-delivery draft withdrawn = 0 attempts; post-delivery withdrawal / relabeled BLOCKED retains attempt history; genuine external hold = 0 attempts unless packet has a new hash fix.

### 5. Scope B: 10-Submission Trigger & Split Inheritance (§4.1–4.2)
- **v1.0 (Lines 91–137):** Stated that when `submissions >= 10`, reviews are halted immediately (which would block the 10th attempt review) and child chunks automatically start with fresh 0/10 and 1/4 counters.
- **v1.1 (Lines 102–148):**
  - Restored Eric's exact words: *"If NO ONE gets it right by 10 total attempts, you notify me and we break it down into smaller bite-size chunks."*
  - Explicitly permitted the 10th unique delivered attempt to complete its applicable review(s).
  - Enforced that if after the 10th review the workstream is still not right, monolithic revisions are hard-halted, Founder Eric is notified, a split proposal is filed, and zero 11th monolithic attempts are permitted.
  - Established that child chunks inherit parent history in audit ledgers and chunk authoring budgets/caps are an explicitly proposed scope awaiting Founder Eric's typed YES (no standing automatic reset).

### 6. Scope C: Evidence Manifest (§5.1–5.2)
- **v1.0 (Lines 151–169):** Included citations without explicitly distinguishing between verified disk receipts and unverified ledger counts.
- **v1.1 (Lines 150–178):** Created clear distinction in Evidence Table between verified disk/git receipts (EVD-01 to EVD-06, EVD-08) and unverified sprint log observations (EVD-07, labeled illustrative and recorded as an external evidence blocker). Box-clock timestamps strictly aligned.

### 7. Scope D: Operational Lifecycle & Gates (§6.1–6.3)
- **v1.0 (Lines 173–208):** Contained universal 10-of-10 test pass assertion and generic automatic preview deploy text.
- **v1.1 (Lines 180–215):** Preserved standard 5 gates without extra ACK tier; substituted track-specific test suites passing 100% for the universal 10-of-10 requirement; clarified that deploys require explicit authorization; established case-appropriate empirical proof requirements (inspection $\ne$ submit).

### 8. Scope E: 5-Plan Pilot Framework (§7.1–7.3)
- **v1.0 (Lines 214–233):** Did not explicitly restrict pilot to prospective versions or prevent restarting completed work.
- **v1.1 (Lines 217–235):** Explicitly restricted pilot candidates to prospective eligible versions; prohibited restarting completed authoring or superseded compositions; codified explicit denominators for historical vs. pilot rework rates.

### 9. Scope F: Proposed Watch Routine Blocks & Rollback Governance (§8.1–8.3)
- **v1.0 (Lines 244–272):** Watch block used consecutive failure text and halted review at $\ge 10$; claimed instant rollback via flags.
- **v1.1 (Lines 237–274):**
  - Updated proposed watch routine text to enforce "still failing after 4 tries" without consecutive loophole, and to permit 10th attempt evaluation before hard halt.
  - Clarified that proposed boolean flags are configuration schemas, not implemented mechanical rollback.
  - Explicitly disclaimed instant restore claims pending adapter implementation under future authorized work.
  - Prohibited using rollback to bypass 4/10 safeguards.
  - Mandated that exact activation text and configuration snapshot must be reviewable by Founder Eric prior to typed YES.
  - Reaffirmed that pilot approval is not permanent adoption.

### 10. Scope G: Field Tester Evidence (§9.1–9.3)
- **v1.0 (Lines 276–291):** Mandated universal browser screenshot requirements for all tracks.
- **v1.1 (Lines 276–294):** Clarified case-appropriate empirical proof: browser screenshots and console/network logs for UI/frontend tracks; empirical HTTP runner logs and JSON schema validation for backend/pricing tracks.

---

## Byte & Hash Verification

```powershell
# Document Byte & Hash Verification Log (Box clock: 2026-11-09 16:20 ET)
# Plan v1.0 (Preserved Byte-Identical)
Get-FileHash docs/PLAN_RSI-CONTROLS_PROCESS-CONTROLS_v1.0.md -Algorithm SHA256
# -> E3BAAC28299C9656356B7F60FAA9E8D95B713E1B79C3FE9467B7499549D94009 (332 lines)

# Plan v1.1 (Revised Plan)
Get-FileHash docs/PLAN_RSI-CONTROLS_PROCESS-CONTROLS_v1.1.md -Algorithm SHA256
# -> A41D273B4D1FD44290544479A108D77B76330E0B1F2FDB37BC7C61EFE435B54A (373 lines)
```

**Submitted by:**  
Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
Monday, 9 November 2026 16:20 ET (`2026-11-09 16:20:00 -05:00`). Strict PLAN ONLY.
