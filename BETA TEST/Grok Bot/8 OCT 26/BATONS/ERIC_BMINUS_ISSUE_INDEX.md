# ERIC B− ISSUE INDEX — Personal Mint Invoice Live Review
**DTG:** 2026-10-27 ~12:16 PM ET (America/New_York)  
**Source:** `27_OCT_2026.docx` + SS_1…SS_10 in `/workspace/eric-bminus-27oct/`  
**Tester:** Eric (Founder) — personal account on **live** `https://numista.ai`  
**Baseline:** NET-595 live — main `449a9dcf` / Cloud Run `numista-backend-00494-rew` / Hosting release 27 Oct 2026 14:52:14 GMT  
**Grade:** B−  
**Recommended board id:** **NET-602** (next free after Desk NET-601 live-deploy rule)  
**Lane:** PLAN_REQUEST → AG CoS v2 `086b98b4-2340-4241-9f6a-08b8aaa8992c` Plan.v1 → Argon → GB CoS → Stand Alone Grok feedback → ONLY THEN EXECUTE (not build-ready yet)

---

## Severity key
| Sev | Meaning |
|-----|---------|
| **P0** | Blocks trust / data loss risk / wrong destructive action / must fix before next live Mint push |
| **P1** | Core workflow broken or misleading; ship in same FAIL-FIX wave |
| **P2** | Polish / clarity; same wave preferred if cheap |

**Type:** `F` = Functional · `U` = UX / copy / contrast · `F+U` = both

---

## Issue table

| ID | Sev | Type | Title | SS | Eric note (abbrev) | Acceptance sketch |
|----|-----|------|-------|----|--------------------|-------------------|
| **I-01** | P1 | U | Add screen confusion: Mint Set vs Upload Files vs Upload a list | SS_1 | Founder still confused which control for US Mint invoice / spreadsheet | Clear primary path for **Invoice (PDF)** and **Spreadsheet**; labels/help distinguish Mint Set product vs file upload vs handwritten/list; no overlapping meanings |
| **I-02** | P2 | U | Reduce clicks to upload invoice | SS_1 | Feels too many clicks; still worked | Fewer steps from Add → invoice in Review Hub (measurable click count drop); do not break multi-PDF |
| **I-03** | — | — | Multi-PDF upload + Storage Location | SS_2A/2B (context) | **PASS** — 2 PDFs <1 min; Storage Location OK | Regress-protect only |
| **I-04a** | P2 | U/F | “July 4th Privy eligible” on Trump $1 roll | SS_3 | Drop or clarify if only MIGHT be in roll | Copy either removed or explicit “may contain / not guaranteed”; no false certainty |
| **I-04b** | **P0** | F | Missed $9.95 S&H on Trump roll | SS_3 | Fee showed $0.00; S&H on invoice | Fee/S&H parsed and shown; matches invoice when present |
| **I-04c** | **P0** | F | Edit auto-saves to collection | (flow after SS_3) | Edit then auto-saved; stop until user commits | Edit updates draft/hub row only; **Commit/Add** required to vault; cancel leaves collection unchanged |
| **I-04d** | — | — | Innovation + 2023 Proof | — | **PASS** — no issues | Regress-protect |
| **I-05** | **P0** | F+U | Select All appears to start Delete | SS_4 | Select All for approve-all seemed to initiate Delete; backed out | Select All only selects; Delete requires explicit Delete control + confirm; no accidental delete path |
| **I-06** | **P0** | U | Commit Selected unreadable + ambiguous | SS_4 | Dark-on-red; unclear delete vs add | High-contrast label; wording = **add/commit to collection** (not delete); distinct from Delete Selected |
| **I-07** | **P0** | F | No images / valuations after add | SS_5, SS_6 | 3 new adds: placeholder + Valuation Pending / $0 | Post-commit path fills or queues images + est. values for just-added SKUs (or clear progress + retry) |
| **I-08** | P1 | F | Innovation grade Unspecified | SS_5 | Should be ≥ Uncirculated | Mint BU / roll / circulating modern $1 → Uncirculated (or product-correct grade), not Unspecified |
| **I-09** | P2 | U | Collection sort order | SS_5 | No rhyme or reason | Documented default sort (e.g. date added desc or year desc); UI shows active sort |
| **I-10** | P1 | U | Google Images button still present | SS_6 | Thought already removed | Button gone from Coin Inspector (and any clone surfaces) |
| **I-11** | P1 | F+U | Generate AI Report Now → estate/probate state | SS_7 | Wrong surface; hard to read (prefer gold/black over red/black) | Estate tax/probate jurisdiction **only** on Estate Planning; modal not from collection report CTA |
| **I-12** | **P0** | F | Replace Generate AI Report Now purpose | SS_5, SS_7 | Expected fill images + values for just-added coins | Collection CTA (rename OK) fills/queues **images + estimated values** for recent adds (or selected); not estate modal |
| **I-13** | P1 | U | Card/Table unreadable colors | SS_7, SS_8, SS_10 | White/light on cream; red/black hard | WCAG-ish contrast; Eric preference **gold/black** over red/black for primary CTAs where applicable |
| **I-14** | P1 | F+U | Card view missing Table sections | SS_8 | Financials, Provenance, AI Insights, History, Legislation, Known Errors should appear on card click | Same section tabs/content available in Card detail as Table |
| **I-15** | P1 | F+U | AI Insights gaps / unreadable | SS_9 | Large gaps in narrative (missing entities) | No empty placeholder holes in prose; entities filled or sentence omitted; readable contrast |
| **I-16** | P2 | F | Legislation Matched blank | SS_10 | Empty for Silver Proof Set | Match when data exists **or** honest empty-state (already partial); prefer real match for common US Mint sets if DB supports |

---

## P0 list (must in Plan.v1 Functional track)
1. **I-04b** — S&H / fee miss ($9.95)  
2. **I-04c** — Edit must not auto-save to collection  
3. **I-05** — Select All ≠ Delete  
4. **I-06** — Commit Selected contrast + add semantics  
5. **I-07** — Images + valuations after Mint add  
6. **I-12** — Collection CTA fills images/values (not estate dropdown)

## P1 (same wave preferred)
I-01, I-08, I-10, I-11, I-13, I-14, I-15

## P2 / polish
I-02, I-04a, I-09, I-16

## PASS / regress-only
I-03 multi-PDF + Storage Location · I-04d Innovation + 2023 Proof parse · eBay button (Eric #5 under collection notes)

## Ambiguities for Plan.v1 (AG must resolve in Plan, not guess in code)
1. **I-01 IA:** Collapse “Upload a list” vs “Upload Files” vs “Mint Set” — rename, regroup, or one-click “US Mint invoice”?  
2. **I-04a:** Product truth — is July 4 Privy a real SKU attribute or marketing hedge?  
3. **I-07 vs I-12:** Auto-enrich on commit vs explicit user CTA (or both)?  
4. **I-16:** Data gap vs UI bug — Congress.gov / DB coverage for “Silver Proof Set”?  
5. **Sort (I-09):** Eric did not pick preferred key — propose default in Plan.  
6. **Scope split:** Functional FAIL-FIX vs UX polish tracks (see PLAN_REQUEST) — Argon reviews both before EXECUTE.

## Artifact paths
- Review folder: `/workspace/eric-bminus-27oct/`  
- This index: `/workspace/eric-bminus-27oct/ERIC_BMINUS_ISSUE_INDEX.md`  
- Mirror: `/workspace/p7gate/net602/ERIC_BMINUS_ISSUE_INDEX.md`
