# FT RETEST CHECKLIST — Eric B− Mint (NET-602 / NET-616) — after Plan approved + PREVIEW_READY
**Audience:** Field Tester (future — **not** now)  
**Channel:** p7-gate / preview only until CoS live EXECUTE  
**Refs:** `/workspace/eric-bminus-27oct/` morning SS_1…SS_10 · `1351hrs-test/` · Issue index · approved Plan.vN · NET-616 PM-01…07  

**Gate reminder:** FT runs only after Plan.vN → Argon → GB CoS → Stand Alone Grok → EXECUTE → PREVIEW_READY.

**Standing rule (Eric 23 Oct FT gate):** Before FT, AG must show screenshot proof of basics. After PREVIEW, FT asserts pass/fail on every P0 below — these are the “simple things” Eric asked FT to catch without waiting for founder beta.

## Smoke
- [ ] Preview loads; Add Coins reachable  
- [ ] Multi-PDF Mint upload still works  
- [ ] Storage Location still works  
- [ ] Invoice # captured on Review Hub + Paper Trail when present on PDF  

## P0 Functional (FT must FAIL the build if any miss)
- [ ] **I-04b / fee** Upload Trump / 26SQRP-class (or any pack/roll) receipt with S&H → Fee shows invoice S&H (e.g. $9.95), not $0 when present  
- [ ] **I-04c** Edit a hub row → changes do **not** land in My Collection until Commit/Add; Cancel safe  
- [ ] **I-05** Select All → rows selected only; Delete Selected still requires explicit delete (+ confirm if designed)  
- [ ] **I-06** Commit Selected readable (contrast); clearly means **add** to collection; distinct from Delete  
- [ ] **I-07 / PM-01** After Add/Commit, new Mint items show **images** (reference or product art OK) and **valuations** (not stuck “Valuation Pending” / blank / $0 with no source). If enrich is async, progress visible and completes within FT wait window.  
- [ ] **I-08 / PM-02** Re-upload same Mint Item # with a **different Invoice/Order #** (Eric 1351hrs: second **26RJ**) → **Duplicates Flagged ≥ 1** or amber POSSIBLE DUPLICATE before commit; do not silently treat as brand-new only.  
- [ ] **I-12 / CTA** Collection CTA (ex–Generate AI Report Now) either enriches images/values or is clearly labeled as collection summary — does **not** open estate state dropdown on My Collection  

## P1
- [ ] **I-08 grade** Innovation $1 / Unc products: grade ≥ Uncirculated (not Unspecified) when invoice implies Unc/Proof  
- [ ] **PM-04** Two identical SKUs distinguishable on Cards + detail (Invoice # and/or purchase date and/or cost visible without digging)  
- [ ] **PM-05** Same Item # stamps Theme/Subject consistently across uploads (26RJ: 250th / catalog theme both times)  
- [ ] **I-10** Google Images button absent (or demoted) on Coin Inspector  
- [ ] **I-11** Estate jurisdiction only on Estate Planning  
- [ ] **I-13 / PM-06** Card header / Commit / modals / AI Insights readable in Light mode (no white-on-cream); gold/black preferred where applicable; modal content not cut off  
- [ ] **I-14** Card detail has Financials, Provenance, AI Insights, History, Legislation, Known Errors  
- [ ] **I-15** AI Insights no large entity gaps  

## P2 / polish (if in approved Plan scope)
- [ ] **I-01** Invoice vs spreadsheet vs Mint Set labels clear  
- [ ] **I-02** Fewer clicks to invoice path (note before/after)  
- [ ] **I-04a** Privy copy removed or hedged  
- [ ] **I-09** Sort default visible/sensible  
- [ ] **I-16** Legislation match or honest empty-state  

## PASS criteria
OVERALL PASS only if all P0 checked and no P0 regressions. Attach shots mirroring Eric SS numbers where possible (include 1351hrs duplicate + post-commit images/vals).

## OUT
File FT result + OVER to Desk/CoS; do not self-promote to live.
