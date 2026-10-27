# FT RETEST CHECKLIST — Eric B− Mint (NET-602) — after Plan approved + PREVIEW_READY
**Audience:** Field Tester (future — **not** now)  
**Channel:** p7-gate / preview only until CoS live EXECUTE  
**Refs:** `/workspace/eric-bminus-27oct/` SS_1…SS_10 · Issue index · approved Plan.v1  

**Gate reminder:** FT runs only after Plan.v1 → Argon → GB CoS → Stand Alone Grok → EXECUTE → PREVIEW_READY.

## Smoke
- [ ] Preview loads; Add Coins reachable  
- [ ] Multi-PDF Mint upload still works (regress I-03)  
- [ ] Storage Location still works  

## P0 Functional
- [ ] **I-04b** Upload Trump / 26SQRP-class receipt with S&H → Fee shows invoice S&H (e.g. $9.95), not $0 when present  
- [ ] **I-04c** Edit a hub row → changes do **not** land in My Collection until Commit/Add; Cancel safe  
- [ ] **I-05** Select All → rows selected only; Delete Selected still requires explicit delete (+ confirm if designed)  
- [ ] **I-06** Commit Selected readable (contrast); clearly means **add** to collection; distinct from Delete  
- [ ] **I-07** After add, three (or N) new items show images and valuations (or visible enrich progress that completes)  
- [ ] **I-12** Collection CTA (ex–Generate AI Report Now) enriches images/values; does **not** open estate state dropdown  

## P1
- [ ] **I-08** Innovation $1 grade ≥ Uncirculated (not Unspecified)  
- [ ] **I-10** Google Images button absent on Coin Inspector  
- [ ] **I-11** Estate jurisdiction only on Estate Planning  
- [ ] **I-13** Card header / Commit / modals readable (gold/black preferred)  
- [ ] **I-14** Card detail has Financials, Provenance, AI Insights, History, Legislation, Known Errors  
- [ ] **I-15** AI Insights no large entity gaps  

## P2 / polish (if in approved Plan scope)
- [ ] **I-01** Invoice vs spreadsheet vs Mint Set labels clear  
- [ ] **I-02** Fewer clicks to invoice path (note before/after)  
- [ ] **I-04a** Privy copy removed or hedged  
- [ ] **I-09** Sort default visible/sensible  
- [ ] **I-16** Legislation match or honest empty-state  

## PASS criteria
OVERALL PASS only if all P0 checked and no P0 regressions. Attach shots mirroring Eric SS numbers where possible.

## OUT
File FT result + OVER to Desk/CoS; do not self-promote to live.
