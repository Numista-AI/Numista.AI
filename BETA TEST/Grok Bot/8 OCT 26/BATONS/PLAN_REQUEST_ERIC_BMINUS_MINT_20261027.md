# PLAN REQUEST — Eric B− Personal Mint Live Review (27 Oct 2026)
**FROM:** Grok CoS (packet for Antigravity Desk)  
**TO:** AG CoS v2 only — conversation **`086b98b4-2340-4241-9f6a-08b8aaa8992c`** (title: AG CoS v2)  
**INFO:** Argon (Plan review), GB CoS, Stand Alone Grok (feedback), Field Tester (later), FinOps (FYI spend), Eric  
**DATE:** 2026-10-27 ~12:16 PM ET (America/New_York)  
**BOARD ID (recommended):** **NET-602**  
**PATTERN:** **PLAN_REQUEST only.** Review chain (Eric-locked):
1. AG CoS v2 writes **Plan.v1**
2. **Argon** reviews Plan.v1
3. **GB CoS** reviews
4. **Stand Alone Grok** feedback
5. **ONLY THEN** CoS/Desk may file EXECUTE

**Iteration cap (Eric-locked 27 Oct):** This AG→Argon→GB CoS→Stand Alone Grok cycle may run **up to 4 times** (Plan **v1–v4**). If still not fully ready after **v4**, **partial-ship**: EXECUTE only the ready issue IDs (preview→FT→live per YES rules); keep iterating the not-ready parts on a follow-on plan.

**DO NOT EXECUTE** from this packet or any draft until that full chain completes.  
**DO NOT** start coding, preview deploy, live deploy, or cherry-pick from this packet. **DO NOT EXECUTE** until Argon → GB CoS → Stand Alone Grok feedback complete.

---

## BLUF
Eric graded live Mint invoice add **B−** on personal `numista.ai` after NET-595. He authorized: address notes → test → deploy if they work (typed YES standing for live after FT PASS; any AG CoS thread OK after typed YES — NET-601).  

**This packet is not EXECUTE.** Produce a Plan.v1 that splits **Functional FAIL-FIX** vs **UX polish**, with acceptance criteria tied to SS refs, preview/p7-gate first, FT, then live only after FT PASS + existing Eric deploy-if-works YES. Gate: **AG Plan.v1 → Argon → GB CoS → Stand Alone Grok feedback → ONLY THEN EXECUTE.**

---

## Context locked
| Item | Value |
|------|--------|
| Live baseline | NET-595 — Hosting release Tue 27 Oct 2026 14:52:14 GMT; Run `numista-backend-00494-rew`; main `449a9dcf` (PR #268) |
| Live/main | **re-LOCKED** until this FAIL-FIX wave ships via proper Plan→Argon→CoS→EXECUTE |
| Catalog / Brain merge | HOLD |
| Old ~9M AG CoS chat | DO NOT USE |
| Model matrix | Gemini **3.8 Pro** heavy / Plan; **3.6 Flash** fast checks; **Claude dropdown dead — do not use** |
| Review artifacts | `/workspace/eric-bminus-27oct/` — `27_OCT_2026.docx`, `SS_1.png`…`SS_10.png` (+ SS_2A/2B) |
| Issue index | `/workspace/eric-bminus-27oct/ERIC_BMINUS_ISSUE_INDEX.md` (mirror `p7gate/net602/`) |

---

## What AG CoS v2 must produce
1. **Plan.v1** markdown (file under RADIO/BATONS or agreed path Desk names) covering:
   - Track A — **Functional** (P0 + P1 functional)
   - Track B — **UX polish** (copy, contrast, IA, sort)
   - Dependencies / order of work
   - Preview channel: **p7-gate** only until FT PASS
   - Explicit non-goals (catalog/Brain, unrelated refactors)
   - Test plan outline for Field Tester
   - Live cherry-pick plan (Hosting + Cloud Run) **gated** on FT PASS + Eric YES already on file for deploy-if-works
2. Call out **ambiguities** from the issue index and recommend a pick (do not leave as “TBD” without a default).
3. Estimate blast radius (Review Hub, Add Coins, My Collection Card/Table, Coin Inspector, report CTA, fee parse).
4. **Do not** file PREVIEW_READY or EXECUTE_DONE from this request.

---

## Requirements by track

### Track A — Functional (priority)
| ID | Sev | Requirement | SS | Acceptance |
|----|-----|-------------|----|------------|
| I-04b | P0 | Parse/show Mint S&H when present (Trump roll missed **$9.95**; fee showed $0.00) | SS_3 | Hub card Fee matches invoice S&H; not silently $0 when invoice has S&H |
| I-04c | P0 | **Stop auto-save to collection on Edit** | flow | Edit updates draft/hub only; vault write only on explicit Commit/Add; Cancel/back leaves collection unchanged |
| I-05 | P0 | Select All must not initiate Delete | SS_4 | Select All = selection only; Delete needs Delete control + confirm |
| I-06 | P0 | Commit Selected = add semantics + readable | SS_4 | Contrast readable; label clear “add/commit to collection”; visually distinct from Delete Selected |
| I-07 | P0 | Just-added Mint items get images + valuations | SS_5, SS_6 | After add, cards show image (or explicit enrich progress) and non-pending est. value when data available; no silent forever-pending for these SKUs |
| I-12 | P0 | Replace/repurpose **Generate AI Report Now** | SS_5, SS_7 | CTA fills/queues **images + estimated values** for just-added (or selected) coins; does **not** open estate tax/probate state dropdown |
| I-08 | P1 | 2026 Innovation grade not Unspecified | SS_5 | At least **Uncirculated** (or product-correct) |
| I-11 | P1 | Estate jurisdiction UI off collection CTA | SS_7 | State/probate selector lives on **Estate Planning** only |
| I-14 | P1 | Card detail exposes same sections as Table | SS_8 | Financials, Provenance, AI Insights, History, Legislation, Known Errors reachable from Card |
| I-15 | P1 | AI Insights no large gaps | SS_9 | No missing-entity holes in prose; readable |
| I-10 | P1 | Remove Google Images button | SS_6 | Gone from Coin Inspector |

### Track B — UX polish
| ID | Sev | Requirement | SS | Acceptance |
|----|-----|-------------|----|------------|
| I-01 | P1 | Clarify Add screen: Mint Set vs Upload Files vs Upload a list; define spreadsheet + invoice paths | SS_1 | Founder-testable: obvious control for US Mint PDF invoice and for spreadsheet |
| I-02 | P2 | Reduce clicks to upload invoice | SS_1 | Plan proposes click-count target; keep multi-PDF |
| I-04a | P2 | July 4th Privy eligible — drop or “might” clarify | SS_3 | No false certainty |
| I-09 | P2 | Collection sort has a defined default + visible control | SS_5 | Documented default |
| I-13 | P1 | Fix unreadable Card/Table/header/modal colors; prefer gold/black over red/black for primary CTAs where it fits brand | SS_7, SS_8, SS_10 | Header/title readable; Commit/modals readable |
| I-16 | P2 | Legislation empty-state vs match | SS_10 | Honest empty or real match for common sets |

### Regress-protect (PASS today)
- Multi-PDF upload + Storage Location (I-03)  
- Innovation + 2023 Proof extraction (I-04d)  
- eBay button  

---

## Constraints (non-negotiable)
1. **Plan only** from this packet — no code until EXECUTE after full chain: Argon → GB CoS → Stand Alone Grok feedback.  
2. **Preview first** — p7-gate / preview channel; **not** live.  
3. **FT** on preview after PREVIEW_READY (future EXECUTE).  
4. **Live cherry-pick** only after FT PASS + Eric’s deploy-if-works authorization (already given for this review wave; Desk/CoS still gate the EXECUTE live step).  
5. Live/main stay locked until that live step.  
6. No catalog/Brain merge.  
7. Thread: **AG CoS v2 only** (`086b98b4…`).  
8. Separate Functional vs UX in Plan so Argon can PASS/CONDITIONAL per track.
9. **≤4 plan passes** (v1–v4); after v4 **partial-ship** ready IDs only; continue the rest.

---

## Suggested Plan.v1 outline (AG may improve)
1. Problem statement + grade B− summary  
2. Track A scope / Track B scope / Out of scope  
3. Ambiguity decisions (I-01 IA, I-04a, I-07 vs I-12 enrich trigger, I-09 sort, I-16)  
4. Implementation approach per ID (files/areas — high level)  
5. Preview deploy notes  
6. FT checklist reference (see companion `FT_RETEST_CHECKLIST.md`)  
7. Live promote notes (Hosting + Run; no force-push; cherry-pick pattern like NET-595)  
8. Rollback  

---

## Owe back (this PLAN_REQUEST)
- Plan.v1 path + short BLUF  
- List of ambiguity picks  
- Confirmation: no code started  

Desk: wake AG CoS v2 with this file; do **not** lift live lock; do **not** treat `DRAFT_AFTER_ARGON_ONLY.md` as executable until Argon + GB CoS + Stand Alone Grok feedback all clear.

GROKCOS / PACKET OUT
