# EGM REVIEW REPORT: Unified Coin Details View Plan (NET-798)

**Target Document:** `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW.md`  
**Reference Design Spec:** `1 NUMISTA.AI/UI UX DESIGN/2026-11-04/Unified Coin Details/Spec_Unified_Coin_Details_2026-11-04.md`  
**Reviewer:** EGM Synthesizer Persona (Swarm Multi-Lens Audit)  
**Recipient:** Antigravity CoS v4 Work (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**Date:** 5 November 2026, 1:00 PM ET  
**Status:** **PLAN AUDIT COMPLETE**  
**Overall Score:** **98 / 100**  
**Executive Verdict:** **APPROVED FOR BUILD** (with 3 Minor Pragmatic Advisories for the 10–16 Nov Sprint)

---

## Reviewer Status Matrix

| Auditing Lens Shortname | Focus Scope | Status | Score (/20) |
|---|---|---|---|
| `implementation_readiness` | Technical actionability, state persistence, Sprint build readiness | **completed** | 19 / 20 |
| `design_critic` | Faithfulness to UX Spec & Founder Eric's Locked Decisions | **completed** | 20 / 20 |
| `codebase_details` | Citation accuracy, legacy split deprecation, privacy gates | **completed** | 19 / 20 |
| `accessibility_contrast` | WCAG AAA conformance (17.5:1 / 18.9:1), touch targets ≥52px | **completed** | 20 / 20 |
| `defect_prevention` | Elimination of folder icons, 1.1:1 text, co-location privacy leak | **completed** | 20 / 20 |
| **Total** | **Comprehensive Swarm Audit** | **ALL RUN** | **98 / 100** |

---

## Executive Summary & Score Breakdown

The implementation plan `PLAN_UNIFIED-COIN-DETAILS-VIEW.md` is an **exemplary, production-grade technical and UX specification**. It rigorously resolves the long-standing architectural defect in Numista.AI (`p7-gate`) where Cards View and Table View presented bifurcated, conflicting detail modals.

Crucially, the plan strictly incorporates all three of **Founder Eric's Locked Decisions** from 4 Nov 2026, enforces the **mutual exclusivity privacy gate** between financial values and physical storage locations, eliminates the legacy **~1.1:1 white-on-white text defect** with measured WCAG AAA contrast ratios (up to 18.9:1), and permanently removes placeholder folder icons in favor of a branded coin silhouette outline with an "Add a photo" CTA.

There are **zero blockers (🔴)** and **zero major issues (🟡)**. Three minor advisories (🟢 Nits) were issued and folded directly into the v1.1 revision of the plan.

---

## Prioritized Findings (Blockers ➜ Majors ➜ Nits)

### 🔴 Blocker Findings
*None identified. The plan is structurally sound and fully compliant with governance rules.*

### 🟡 Major Findings
*None identified. All locked architectural and privacy boundaries are satisfied.*

### 🟢 Pragmatic Advisories (Nits Folded Into Plan)

#### Nit 1: Clarify Flutter `TabBar` Multi-Row Wrap Implementation
- **Reviewer Lens:** `implementation_readiness`
- **Resolution:** Plan Section 4 updated to specify that on narrow mobile screens (≤390px), tabs are implemented using a custom `Wrap` containing `FilterChip`/`InkWell` controls bound to the `TabController`.

#### Nit 2: Clarify Cards View Tap vs. Table Cell Tap Citation
- **Reviewer Lens:** `codebase_details`
- **Resolution:** Section 2.1 updated to cite both `my_collection_screen.dart:3042–3045` (Cards View card tap) and `my_collection_screen.dart:2736` (Table View row tap).

#### Nit 3: Add Dedicated `_BottomActionBar` Subsection in Section 3
- **Reviewer Lens:** `design_critic` / `implementation_readiness`
- **Resolution:** Section 3.5 added formalizing the bottom action bar with button order (Edit, Wishlist, Verify, Delete), minimum 52px height, and two-stage confirmation modal for Delete.

---

## Detailed Multi-Lens Audits

### 1. Implementation Readiness (Pragmatic Tech Lead) — 19/20
- **Actionability:** The 5-step implementation roadmap in Section 8 provides a logical progression: component scaffolding ➜ laws integration ➜ invocation redirection ➜ automated tests ➜ deprecation of legacy code.
- **Entry Point Signature:** `UnifiedCoinDetailScreen.show(...)` encapsulates all necessary inputs: `coin`, `coinList` (for Prev/Next navigation), `currentIndex`, `spotPrices`, AI chat routing, and refresh callbacks (`onEdited`, `onDeleted`).
- **State Management:** The plan correctly requires keeping `_showValues` in the modal's state so that as the user navigates via `Previous coin` / `Next coin`, valuation data remains revealed until modal dismissal (`Close`).

### 2. Design & UX Quality — 20/20
- **Founder Eric's Locked Decisions Compliance:**
  1. **Locked Decision #1 (Build Window):** Scheduled strictly for the **10–16 Nov sprint build** (Sections 1, 7, 8).
  2. **Locked Decision #2 (Show Values Persistence):** Values persist across Previous/Next navigation and reset to hidden upon Close (Sections 1, 3.4, 7).
  3. **Locked Decision #3 (Congress.gov Fallback):** Unchecked statutory data is clearly labeled *"From Congress.gov, not yet checked by us"*, while Numista.AI catalog legislation always takes precedence (Sections 1, 5, 7).
- **Tab Simplification:** Successfully consolidates 7 technical/confusing tabs down to 6 user-friendly tabs: Overview, Purchase & value, Morgan's notes, History, Laws, Known errors.
- **Ask Morgan Integration:** Well-placed branded owl tile adjacent to the coin photos preloading specific coin context.

### 3. Codebase Details & Hygiene — 19/20
- **Verbatim Citations Verified:**
  - `numista_mobile/lib/screens/my_collection_screen.dart:2750–2761`: Exact match for Table View info icon invoking `CoinDetailScreen.show`.
  - `numista_mobile/lib/screens/my_collection_screen.dart:3449–3454`: Exact match for `_showCoinInspectorDialog` definition.
  - `numista_mobile/lib/screens/coin_detail_screen.dart:758–766`: Exact match for legacy 7 tabs.
  - `numista_mobile/lib/screens/coin_detail_screen.dart:892–915`: Exact match for legacy `_kDark(context)` container with white text producing low contrast.
- **Commit Boundaries:** Strict adherence to "PLAN ONLY" protocol; zero code touched, zero Firestore writes.

### 4. Accessibility & Contrast (WCAG AAA) — 20/20
- **Empirical Contrast Auditing:**
  - **Coin Title:** `#0b1a2e` (Deep Navy) on `#ffffff` ➜ **17.5:1** (Exceeds WCAG AAA requirement of 7.0:1).
  - **Body Text:** `#111111` (Charcoal) on `#ffffff` ➜ **18.9:1** (Exceeds WCAG AAA).
  - **Spec Labels:** `#333333` on `#ffffff` ➜ **12.6:1** (Exceeds WCAG AAA).
  - **Buttons:** `#ffffff` on `#1d4f91` / `#1d4f91` on `#ffffff` ➜ **8.1:1** (Exceeds WCAG AAA).
  - **Active Tab:** `#0b3d7a` on `#e8f0fb` ➜ **9.3:1** (Exceeds WCAG AAA).
  - **Notice Banner:** `#3a2e00` on `#fff4c2` ➜ **12.1:1** (Exceeds WCAG AAA).
- **Physical Usability Safeguards:**
  - Every button is ≥52px in height (Tabs ≥56px).
  - Every button combines an explicit text label with an icon.
  - Elimination of hover-only interactions for full touch/keyboard parity.

### 5. Defect Prevention & Privacy Gates — 20/20
- **Defect #1 Fixed (1.1:1 Text):** White-on-light header text is replaced with solid white background and `#0b1a2e` Navy title.
- **Defect #2 Fixed (Folder Icon):** Generic folder icon placeholder is eliminated; replaced with a gold-outlined coin silhouette + "Add a photo" CTA.
- **Defect #3 Fixed (Privacy Breach):** Mutual exclusivity gate strictly enforced between valuation and safe location.

---

## Verdict & Recommendation

**VERDICT: APPROVED FOR BUILD (Score: 98/100)**

The implementation plan is technically sound, aesthetically aligned with senior numismatist accessibility requirements, and faithful to all executive decisions. It is ready for Argon (Gemini 3.8) evaluation, Grok CoS build scoring, and Founder Eric's deployment clearance for the 10–16 Nov sprint.
