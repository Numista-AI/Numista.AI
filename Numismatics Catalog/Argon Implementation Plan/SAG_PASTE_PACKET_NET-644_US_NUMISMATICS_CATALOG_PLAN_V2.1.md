# Stand Alone Grok — Paste Packet: NET-644 Argon Catalog Site Plan.v2.1

**One-line ask:** Independently review and score Argon's **Plan.v2.1** for the U.S. Numismatics Master Catalog site integration. Maintain full independence from any GB CoS review — **do not ask for or assume any prior CoS scores**.

**DTG Packet:** 2026-10-29 ~09:15 AM ET • **Status:** PLAN ONLY — NO EXECUTE / NO FOLD / $0 UNAPPROVED SPEND • **Your Role:** Independent architecture, security, schema, and Black Friday cut grill.

---

## Board Constraints (Strictly Maintained)

- `origin/main` **LOCKED**. Mint FAIL-FIX / **NET-641** Day #1 priority on `p7-gate` — catalog work runs decoupled on `dev` and **never** touches Mint files.
- Production fold **HOLD** stack: **586 + 588 + 589 + 590**.
- **NET-640** = Phase I afternoon ≤$60 Discovery-only on `numista-morgan-pilot`, owned exclusively by Catalog Research — **separate track**; **$0** unapproved spend on this catalog planning desk.
- **Plan-Only Cycle:** Plan.v2.1 filed for review. **No code execution or fold permitted** until Mint FAIL-FIX clears or Founder explicitly gives parallel typed YES.

---

## Condensed Plan.v2.1 Summary

**Title:** Numista.AI — U.S. Numismatics Master Catalog (1776–2026) — Argon Plan.v2.1  
**Architect:** Argon (AG System Architect / Lead Engineer) • **Filed:** 2026-10-29  
**Source Plan:** `US_NUMISMATICS_CATALOG_IMPLEMENTATION_PLAN_V2.1.md`  
**Mockup:** `us_numismatics_catalog_mockup.html`

### What's New & Fixed in Plan.v2.1:
1. **Mobile Scope Alignments (Founder Confirmed):**
   - Catalog browsing, multi-faceted filtering, and deep archival inspection are engineered for **Desktop & Tablet Web** (`≥1280px` primary grid + 4-col sticky inspector).
   - Mobile application is strictly a **focused companion (~90% web / ~10% app)** for phone-only physical tasks: adding coins with camera, scanning certified slabs, and capturing purchase receipts.
2. **Founder Confirmed Decisions Sealed (Eric Seaman, Oct 29, 2026):**
   - **Q1 (Pre-1792):** Interleaved into the unified 1776–2026 timeline with a `"Pre-Federal"` badge and State Filter (`CONTINENTAL`, `CT`, `MA`, `NJ`, `NY`, `VT`).
   - **Q2 (Foreign Legal Tender):** Spanish 8 Reales and circulating foreign specie kept out of main US federal circulating series, but **given a dedicated Foreign Coins section** (`1776–1857`, `CC="FS"`).
   - **Q3 (Images):** Strict hierarchy: Museum preferred (Smithsonian NNC CC0) → Public Domain OK (US Mint/BEP/NARA) → Verified Collector Uploads (AI quality pre-screen + human Catalog Registrar sign-off + CC0 release) **only** when higher quality than existing. In personal collections, users can toggle between their own uploaded specimen photos and catalog stock photos.
   - **Q4 (Access & Gatekeeping):** Public browse and search (with guest rate limits and **NO image download**); Paid for adding coins, exports, Morgan AI, and visual match.
3. **Polity Code Split (`CC`):**
   - Split overloaded `PF`: Colonial / Pre-Federal becomes **`CO`**; U.S.-Philippines Territorial remains **`PF`**; Foreign Specie circulating in early America becomes **`FS`**.
   - BNF: `cc ::= "US" | "CO" | "PF" | "CS" | "FS"`.
4. **Common Private Medals in Scope:**
   - In addition to official U.S. Mint medals, **common private medals & historic tokens (`CLASS="PRV"`)** are formally confirmed in scope for Phase 2.
5. **Universal Checksum & Test Vectors:**
   - 13 canonical test vectors 100% verified with Crockford-32 checksum algorithm (`(h * 33 + b) % 37 % 32`).

---

## Complete Verbatim Plan.v2.1 Text for Independent Review

[Insert full contents of US_NUMISMATICS_CATALOG_IMPLEMENTATION_PLAN_V2.1.md here for standalone paste into Grok]
