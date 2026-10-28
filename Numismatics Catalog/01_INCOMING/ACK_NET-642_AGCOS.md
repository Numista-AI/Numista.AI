# ACK_NET-642_AGCOS: Plan.v1 US Numismatics Catalog Site Integration Filed

**Date:** 28 OCT 2026 11:37 EDT  
**Station From:** AG CoS / Argon (`086b98b4`)  
**Station To:** Desk (Eric Seaman, Founder) / Grok CoS (`5bc1e74f`) / Catalog Research (`aabd65de`)  
**Ref Baton:** `NET-642_DESK-to-AG-COS-ARGON_CATALOG-SITE-INTEGRATION-PLAN-V1.md`  
**Artifact Filed:** `ARGON_PLAN_V1_US_NUMISMATICS_CATALOG_2026-10-28.md` (and mirrored to `Numismatics Catalog/01_INCOMING/`, `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/`, and `RADIO NET/`)

---

## 1. Action Summary
1. **Acknowledged:** Received direct founder brief from Eric Seaman and radio baton `NET-642`.
2. **Delivered Plan.v1:** Authored comprehensive architectural plan covering:
   - Scope: 1776 – 28 OCT 2026 (Semiquincentennial 250 years) spanning coins, bank notes, and medals used on US territory.
   - 6 Core Dimensions: Data ingestion path (staging → GCP → app), UI catalog surfaces & search/filter/sort, Auth/gates, Preview vs Main isolation, Relationship to existing Mint catalog & coin cards/checklists, and Black Friday cut (P0 coins/notes before cut vs P1 medals after cut).
   - Missing Asset Standard: Strict dual-sided placeholder architecture (`PlaceholderCoinCard` with obverse and reverse ghost silhouettes) retaining 100% metadata.
   - Universal Identifier Grammar: Full crosswalk integration with Catalog Research's `NAC1.<KIND>.<CC>.<CLASS>.<SERIES>.<DATE>.<FAC>.<VAR>.<CHK>`.
3. **Budget & Execution Discipline:**
   - **Cost on this baton:** **$0.00**. No Discovery Engine / Agent Builder credits or API spend incurred.
   - **Execution Status:** **PLAN ONLY**. Zero production files modified, zero live database writes, `origin/main` strictly locked.
   - **Priority Protection:** Mint track `p7-gate` FAIL-FIX remains Day #1 priority (`NET-641`); Catalog plan operates strictly in parallel without stealing execution resources.

---

## 2. Four Direct Clarifying Questions for Eric Seaman (Founder)
1. **Pre-Federal Colonial/State Coinage (1776–1792):** Should pre-1792 state issues (e.g., Massachusetts, Connecticut, New Jersey coppers, Continental Dollars) be grouped under their issuing state/colony or displayed as a unified chronological "Pre-Federal / Continental" category?
2. **Circulating Foreign Specie:** Spanish-American 8 Reales (pieces of eight) and fractional silver circulated as legal tender in the US until the Coinage Act of 1857. Should we include major foreign legal-tender circulating specie, or restrict scope strictly to American-authorized issues?
3. **Placeholder Style & Community Ingestion:** For records with placeholder images, should we provide a "Submit Image / Request Verification" community ingestion hook for collectors, or keep image ingestion strictly authoritative/internal?
4. **Access Tiering & Paywall Gates:** Should `/catalog` browsing and basic search be 100% public (maximizing SEO and top-of-funnel acquisition), reserving tier gates (Pro/Subscriber) strictly for high-res AI visual match and valuation analytics?

---

**Standing By for Founder Guidance and Grok CoS Review.**  
`OVER`
