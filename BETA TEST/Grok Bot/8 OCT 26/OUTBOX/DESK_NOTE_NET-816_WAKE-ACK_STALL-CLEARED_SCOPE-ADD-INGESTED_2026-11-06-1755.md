# DESK NOTE — NET-816 WAKE ACK & STALL CLEARED (AG CoS v4)

- **Date:** 2026-11-06 17:55 ET (5:55 PM ET)
- **From:** AG CoS v4
- **To:** Grok Bot CoS / Stand Alone Grok / Founder Eric
- **Subject:** WAKE ACK, Stall Flags Cleared, Scope-Add Ingested, NET-816 Catalog Plan v1.8 Status & ETA

---

### 1. WAKE ACK & Stall Flag Processing
- **Wake Acknowledged:** Ingested all afternoon stall re-flags (10:02, 11:29, 12:43, 13:44, 15:14, 16:14, and 17:45 ET).
- **Wakes Cleared:** Moved all pending `WAKE_AGCOS_NET-816-STALL_20261106-*.md` files to `RADIO NET\WAKES\DONE`.
- **Laptop & AG CoS v4 Active:** Working actively on desk.

---

### 2. Scope-Add Ingestion Confirmed (1:35 PM ET Catalog Research Directive)
Per Eric's typed decision ("A: fold them into NET-816 Catalog v1.8 through the normal plan cycle"), folding all 3 research items directly into `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.8.md`:
1. **Legislation Tab Go-Live:** Sourced from `LEGISLATION_PROPOSAL_20261106.jsonl` + `entries_master_LEGIS_CANDIDATE_20261105.jsonl`. Laws tab links out strictly to Congress.gov.
2. **1796–97 Stubs & Social Posts X Links:** Sourced from `entries_master_20261104.jsonl` (3,209 rows) and `entries_master_RP_CANDIDATE_20261105.jsonl` (logs `ATTACH_X_1797_*`, `ATTACH_X_1796_*`).
3. **Mint Report Plate Images (US Gov Public Domain):** Sourced from `plates_20261105/` and `plate_crops_20261106/` as self-hosted assets under CSP (strictly zero external hotlinks).
4. **Mandatory Guardrails Preserved:**
   - AI replicas stay strictly labeled, never used as `primary_image`.
   - Null mintages remain null (no synthetic zero substitution).
   - Zero AJ PII.

---

### 3. Catalog Plan v1.8 Revision Scope
Addressing all 6 CoS (64) and SAG (67) blocking must-fixes:
1. **Compiling, Class-Correct Card & Safe Retail:** Safe nullable promotion (`valCpg!`) in `_CatalogCard.build`, valid class-scoped `_isAllowedImageUrl` guard, and explicit CPG source schema/NAC join provenance.
2. **B05N-14 Real Model Grounding:** Canonical `series` and `coinTypes` fields with fail-closed parsing against real `CoinModel.programSeries` and `MintError`. Strict match requires denomination + applicable year + matching series/type. Verified Greysheet server-filter and Washington/NJ regression tests.
3. **B05N-15 / B27-8 Complete Structural Removal:** Full deletion of Google Images action/button and Similar Coins/Kaggle surfaces across collection, microscope, ref-image, and photo-sharing files, with error/timeout terminal handling.
4. **B27-11 Contrast & Light Mode Fix:** Theme-aware dark typography replacing white-on-white text in AI Insights and WCAG AA $\ge 4.5:1$ compliant gold pending chip (`#613B00` on `#FFF8E1`, contrast 6.2:1).
5. **Deep-Link & Routing Grounding:** Modal grounding to real lines 71–85 (`orElse: () => <String, dynamic>{}`, `addPostFrameCallback`), Dart web interop, verified outer-navigation for Ask Morgan, and real executable test assertions.
6. **Integrated Scope-Add Runbooks:** Clear execution boundaries for the 3 Catalog Research additions.

---

### 4. Queue & Delivery ETA
- **Queue Precedence Strictly Maintained:**
  1. `NET-816` (Catalog FAILFIX Plan v1.8 — Thanksgiving Critical Path FIRST): **ACTIVE ON DESK**. Delivery of Plan v1.8 + Grok Bot CoS review baton this evening.
  2. `NET-817` (780b Cards + 780c Images Plan v1.5): Acknowledged and queued directly next.
  3. `NET-813` (Unified Details v1.2) $\rightarrow$ `NET-814` (Soft-404 v1.2) $\rightarrow$ `NET-810` (Mint product fields - parked last).

---

### 5. Standing Locks
- `origin/main` strictly locked at `9f04550a`.
- Stripe strictly locked OFF across all configurations.
- Strict PLAN ONLY mode: zero code execution, zero deployments, zero Firestore writes/seeding or security rules changes without Founder Eric's explicit typed YES.
- Review Chain: AG CoS v4 Plan $\rightarrow$ Grok Bot CoS ($\ge 95$) $\rightarrow$ Stand Alone Grok ($\ge 95$) $\rightarrow$ Founder Eric typed YES. Argon completely dropped.
