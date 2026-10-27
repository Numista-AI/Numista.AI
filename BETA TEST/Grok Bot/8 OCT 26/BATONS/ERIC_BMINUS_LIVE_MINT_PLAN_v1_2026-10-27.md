# ERIC B− PERSONAL MINT LIVE REVIEW — REMEDIATION PLAN (v1)
**Document ID:** `ERIC_BMINUS_LIVE_MINT_PLAN_v1_2026-10-27`  
**Board ID:** `NET-602`  
**Date:** 2026-10-27 12:47 PM ET  
**Author:** Antigravity CoS v2 (`086b98b4-2340-4241-9f6a-08b8aaa8992c`)  
**Target Review Chain (Locked):** AG Plan.v1 → Argon → Grok Bot CoS (GB) → Stand Alone Grok → CoS/Desk EXECUTE  
**Iteration Cap:** ≤4 rounds (v1–v4). If not fully agreed after v4, partial-ship ready IDs only.  
**State:** **PLAN ONLY — ZERO CODE STARTED / ZERO PREVIEW OR LIVE DEPLOY**  

---

## 1. Executive Summary & Problem Statement

On 27 Oct 2026, Eric tested the live U.S. Mint invoice upload workflow on personal `numista.ai` following the NET-595 cherry-pick release (Hosting 14:52:14 GMT, Cloud Run `numista-backend-00494-rew`, commit `449a9dcf`). Eric awarded the overall experience a **B−**, identifying key functional friction points (data loss fears, unreadable action buttons, missing S&H, and silent pending valuations) and UX ambiguities.

Eric authorized: address the notes → test on preview (`p7-gate`) → deploy to live once verified working.

This Plan.v1 establishes a clear, decoupled two-track remediation roadmap:
- **Track A (Functional FAIL-FIX):** Resolves critical workflow blockers, data safety hazards (auto-save on edit, destructive select-all), parsing gaps (Trump roll $9.95 S&H), and missing post-add enrichment.
- **Track B (UX Polish & Information Architecture):** Eliminates visual debt, corrects contrast issues (gold/black over red/black), resolves Add screen confusion, and streamlines invoice navigation.

---

## 2. Scope & Track Partitioning

### Track A: Functional FAIL-FIX (P0 / P1 Priority)

| ID | Sev | Core Issue & User Impact | Evidence Ref | Target Codebase / Component | Acceptance Criteria |
|---|---|---|---|---|---|
| **I-04b** | **P0** | **Missing S&H on Trump Roll:** Invoice fee showed $0.00 instead of $9.95. | `SS_3` | `numista_backend/services/parsers/mint_invoice_parser.py` | Invoice shipping/handling fee parsed and populated into Hub Review row `fee` field; never silently defaults to $0.00 when present on invoice. |
| **I-04c** | **P0** | **Edit Auto-Saves to Collection:** Modifying a field in the review modal writes directly to the vault database. | Review Modal Flow | `ReviewTable.tsx`, `UploadHub.tsx`, `useCollectionStore.ts` | Edit strictly modifies the draft row in the temporary review state. No vault database writes occur until user clicks explicit "Commit/Add". Cancel or modal dismiss leaves user's collection 100% untouched. |
| **I-05** | **P0** | **Select All Initiates Delete:** Toggling "Select All" erroneously triggers or primes destructive deletion. | `SS_4` | `ReviewTable.tsx`, `ReviewActions.tsx` | "Select All" only updates row selection checkboxes (`selectedIds`). "Delete Selected" is a completely separate button requiring explicit user confirmation modal before removal from draft queue. |
| **I-06** | **P0** | **Commit Selected Unreadable & Ambiguous:** Red background with dark text; ambiguous action semantics. | `SS_4` | `ReviewActions.tsx`, Tailwind styling | Button re-styled to high-contrast brand styling (Gold/Black `#D4AF37` / `#1A1A1A`). Clearly labeled "Commit Selected to Collection" (or "Add Selected to Vault"); visually and semantically distinct from Delete. |
| **I-07** | **P0** | **Post-Add Zero Images & Values:** Newly added items remain with placeholder images and "$0 / Valuation Pending" indefinitely. | `SS_5`, `SS_6` | `collection_enrichment.py`, `CoinCard.tsx`, `enrichment_service.py` | Newly committed items automatically trigger a background enrichment worker with visible UI status badge ("Enriching: [Valuation / Image]"). Once complete, display estimated market value and authentic obverse/reverse imagery. |
| **I-12** | **P0** | **Repurpose "Generate AI Report Now" CTA:** Button opens inappropriate Estate Tax / Probate state modal from collection header. | `SS_5`, `SS_7` | `CollectionHeader.tsx`, `EnrichmentQueueModal.tsx` | Replace this CTA with "Fetch Values & Images" / "Enrich Collection". Clicking it dispatches immediate background valuation & image enrichment for all pending items in the active view. |
| **I-08** | **P1** | **Innovation Grade "Unspecified":** 2026 American Innovation $1 shows grade "Unspecified". | `SS_5` | `mint_invoice_parser.py`, `coin_normalizer.py` | Modern Mint sets and unopened rolls automatically default to "Uncirculated" (UNC) rather than "Unspecified" unless slabbed/graded otherwise. |
| **I-10** | **P1** | **Remove Dead "Google Images" Button:** Broken / unhelpful search button in Coin Inspector. | `SS_6` | `CoinInspectorModal.tsx` | Dead "Google Images" button completely removed from Inspector action row. |
| **I-11** | **P1** | **Move Estate Jurisdiction UI:** Estate tax & probate jurisdiction dropdown appears on collection main screen. | `SS_7` | `CollectionHeader.tsx`, `EstatePlanningView.tsx` | Relocate jurisdiction selector strictly to the dedicated Estate Planning tab / view. |
| **I-14** | **P1** | **Card Detail Exposes Table Sections:** Card click view lacks sections available in Table view. | `SS_8` | `CoinCardModal.tsx`, `CoinDetailTabs.tsx` | Card detail modal incorporates full parity with Table view: Financials, Provenance, AI Insights, History, Statutory Legislation, and Known Errors. |
| **I-15** | **P1** | **AI Insights Prose Gaps:** Narrative contains blank missing-entity placeholders or syntax gaps. | `SS_9` | `insights_generator.py`, prompt template | Ensure fallback template sanitization so generated AI Insights prose contains no template token leaks, undefined placeholders, or jarring sentence fragments. |

---

### Track B: UX Polish & Information Architecture (P1 / P2 Priority)

| ID | Sev | Requirement & UX Goal | Evidence Ref | Target Component | Acceptance Criteria |
|---|---|---|---|---|---|
| **I-01** | **P1** | **Clarify Add Screen Entrypoints:** Confusion between Mint Set, Upload Files, and Upload a list. | `SS_1` | `AddCoinsModal.tsx`, `ImportHubView.tsx` | Clear 3-card selection: (1) "U.S. Mint Invoice (PDF)" [Recommended primary], (2) "Spreadsheet Import (CSV/Excel)", (3) "Single Coin / Mint Set (Manual/Direct)". |
| **I-02** | **P2** | **Reduce Upload Clicks:** Streamline invoice upload flow from 4+ clicks down to 2. | `SS_1` | `AddCoinsModal.tsx` | Direct drag-and-drop target on the first modal view; clicking "U.S. Mint Invoice" immediately launches system file picker. Preserves multi-PDF upload support. |
| **I-04a** | **P2** | **Hedge "July 4th Privy Eligible" Copy:** Current copy asserts definitive eligibility, creating false collector expectation. | `SS_3` | `mint_invoice_parser.py`, Hub UI | Updated to honest, hedged language: "Unopened Roll — Eligible for randomly inserted July 4th Privy Mark (U.S. Mint lottery)". |
| **I-09** | **P2** | **Define Default Collection Sort Order:** Sorting order is currently ambiguous or unstated upon initial load. | `SS_5` | `CollectionControls.tsx`, `useCollectionStore.ts` | Default sort explicitly set to `Date Added (Newest First)`. Dropdown visibly displays current sort mode. |
| **I-13** | **P1** | **Color & Contrast Remediation:** Dark text on red badges, cream-on-white modal headers, illegible action buttons. | `SS_7`, `SS_8`, `SS_10` | Global Tailwind theme, `badges.css`, `Button.tsx` | Primary action CTAs standardize to Numista Gold (`#D4AF37`) on Dark Charcoal (`#1A1A1A`) with WCAG AAA contrast ratio. Red strictly reserved for destructive "Delete" actions. |
| **I-16** | **P2** | **Legislation Match vs. Clean Empty State:** Empty legislation card looks broken. | `SS_10` | `LegislationSection.tsx` | If statutory authority exists (e.g. Public Law 115-197 for Innovation $1), display full citation; if not indexed, display clean empty state: "Statutory authority not yet indexed for this series." |

---

### Regress-Protect (PASS Baseline Today — Must Not Regress)
1. **Multi-PDF Upload & Storage Location (`I-03`):** Simultaneous ingestion of multiple invoice PDFs with batch storage location assignment must remain fully functional.
2. **Innovation & 2023 Proof Extraction (`I-04d`):** Regex/NLP parsing accuracy on American Innovation and 2023 Proof sets must be preserved.
3. **eBay Quick Search Button:** Direct valuation search link on collection items must continue to function.

---

## 3. Ambiguity Decisions & Recommendations

Per Standing Order, the following ambiguities from `ERIC_BMINUS_ISSUE_INDEX.md` are resolved with concrete recommendations:

1. **`I-01` Add Screen Information Architecture:**
   - *Recommendation:* Replace the overlapping tiles with a distinct 3-card action panel:
     - **Card 1 (Hero / Primary):** `U.S. Mint Order Invoices (PDF)` with subtext "Upload one or more official receipts or packing slips".
     - **Card 2:** `Spreadsheets & Inventories (CSV, XLSX)` with subtext "Bulk import existing collections or dealer exports".
     - **Card 3:** `Manual Catalog Lookup` with subtext "Search U.S. Mint catalog or raw coin database".
2. **`I-04a` July 4th Privy Mark Copy:**
   - *Recommendation:* Do not drop the feature, but remove false certainty. Display:
     `"Unopened Roll — May contain randomly inserted July 4th Privy Mark (Mint distribution)"`.
3. **`I-07` vs. `I-12` Enrichment Triggers:**
   - *Recommendation:* Hybrid execution. 
     - Automatic: Immediately upon clicking "Commit Selected", enqueue items in a lightweight background valuation + image lookup worker (`status: "enriching"`).
     - Manual / On-Demand (`I-12`): The collection top-level CTA is renamed `"Fetch Values & AI Images"`. Clicking it forces a refresh/re-try on any items currently in `pending` or `$0.00` valuation status.
4. **`I-09` Default Sort Order:**
   - *Recommendation:* Default to `Date Added (Newest First)`. This ensures that newly committed Mint items immediately appear at the top of the user's screen upon returning to My Collection.
5. **`I-16` Legislation Empty State:**
   - *Recommendation:* Link known modern acts (e.g., *American Innovation $1 Coin Act*, Pub. L. 115-197; *Circulating Collectible Coin Redesign Act of 2020*, Pub. L. 116-330). If a coin does not map to an indexed statute, display an honest informational badge: `"Statutory authority record pending"`.

---

## 4. Technical Implementation Approach & Blast Radius

### Component Blast Radius
1. **Frontend / UI (`numista_web/src/`):**
   - `components/modals/AddCoinsModal.tsx` & `components/upload/UploadHub.tsx`: Entrypoint IA redesign, click reduction, drag-and-drop file staging.
   - `components/upload/ReviewTable.tsx` & `components/upload/ReviewActions.tsx`: Decouple edit modal from vault DB; fix "Select All" logic; re-theme Commit button (Gold/Black).
   - `components/collection/CollectionHeader.tsx`: Move estate tax state selector to Estate Planning; repurpose AI Report CTA to "Fetch Values & AI Images".
   - `components/collection/CoinCard.tsx` & `components/collection/CoinCardModal.tsx`: Add full tab parity (Financials, History, Legislation, Errors); add enrichment pending indicators.
   - `components/inspector/CoinInspectorModal.tsx`: Delete dead "Google Images" link.
   - `components/collection/LegislationSection.tsx`: Add fallback empty-state handling.
2. **Backend / Parsers (`numista_backend/`):**
   - `services/parsers/mint_invoice_parser.py`: Enhance regex parser to extract shipping & handling line items (e.g., `Shipping & Handling: $9.95`) and map to `fee`. Default modern uncirculated coin grade to `Uncirculated` (UNC) instead of `Unspecified`.
   - `services/enrichment/enrichment_service.py`: Ensure modern mint set SKU pricing fallback pulls Mint issue price if live auction comps are scarce.
   - `services/ai/insights_generator.py`: Add validation filter to strip placeholder tags (`<MISSING>`, `None`) before returning AI narrative text.

---

## 5. Preview Deployment & Field Tester Verification Plan

### Preview Channel (`p7-gate`)
- Code will be developed exclusively on `dev`.
- Build verified with `flutter analyze` / `npm run build` and unit tests before any deploy.
- Deployed exclusively to Firebase Hosting channel `p7-gate` and Cloud Run test revision.
- **ZERO writes to production `main` or live hosting (`numista-vault.web.app`).**

### Field Tester Verification Protocol
Field Tester will execute the 16 checks outlined in `FT_RETEST_CHECKLIST_NET602.md`:
1. **Invoice Upload & S&H:** Upload Trump 26SQRP receipt -> verify $9.95 fee is captured.
2. **Edit Isolation:** Edit item in Hub -> cancel -> verify zero rows added to Vault; commit -> verify row added.
3. **Select All Safety:** Click Select All -> verify rows are highlighted only, no delete confirmation triggered.
4. **Button Legibility:** Verify Gold/Black styling on Commit button; clear contrast.
5. **Post-Add Enrichment:** Verify committed coins display image and non-$0 valuation within enrichment timeout.
6. **CTA Repurposing:** Verify "Fetch Values & AI Images" triggers queue; no estate dropdown appears.
7. **Parity & Cleanup:** Verify Card Detail modal exhibits all 6 metadata sections; verify Google Images button is gone.

---

## 6. Live Promotion Gate (Cherry-Pick Release Policy)

Live promotion will strictly adhere to NET-601 and Eric's standing deploy-if-works authorization:
1. **Prerequisite:** Field Tester files full `FT_PASS_NET602.md` with screenshot proofs on preview `p7-gate`.
2. **CoS Clearance:** Grok CoS files `EXECUTE_LIVE_NET602.md`.
3. **Execution Pattern:** Clean cherry-pick of the squashed feature commit onto `main` via PR, followed by production Firebase Hosting release and Cloud Run deployment.
4. **Rollback Plan:** If any regression occurs, instant rollback to Hosting release `27 Oct 2026 14:52:14 GMT` and Cloud Run revision `numista-backend-00494-rew`.

---

## 7. Explicit Non-Goals
- **Catalog / Brain Merge (Stack 586+588+589+590):** Strictly on HOLD; zero touches to Catalog or Brain synchronization engines.
- **Database Schema Migrations:** No destructive schema alterations to live Firestore or SQLite vault collections.
- **Unrelated Refactorings:** No changes to authentication, stripe billing, or mobile Flutter shell outside the targeted Mint invoice and collection review modules.

---

## 8. Review Chain Status & Next Baton
- **AG CoS v2:** Plan.v1 completed and filed. Zero code started.
- **Next Baton:** **Argon** for Plan.v1 review and scorecard.
- **Following Steps:** GB CoS -> Stand Alone Grok -> EXECUTE.
