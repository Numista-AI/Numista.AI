# DONE BATON NET-798 - AG CoS v4: Unified Coin Details View Plan & EGM Review
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**To:** Grok Bot CoS, Argon (Gemini 3.8), Founder Eric  
**Date:** 5 November 2026, 1:10 PM ET  
**Original Baton:** `BATON_NET-798_PLAN_UNIFIED-COIN-DETAILS-VIEW_2026-11-04-1933.md`  
**Standing Amendment:** `EGM REVIEW GATE` (5 Nov 2026 9:50 AM ET via GB CoS)  
**Status:** **PLAN & EGM REVIEW COMPLETE** (Zero code changes, zero deployments, zero Firestore writes).

---

## 1. Summary of Deliverables
All requirements from `BATON_NET-798` and UX Spec (`Spec_Unified_Coin_Details_2026-11-04.md`) have been drafted, audited, and finalized:
1. `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW.md` (Unified Coin Details View Plan)
2. `docs/EGM_REVIEW_PLAN_UNIFIED-COIN-DETAILS-VIEW.md` (Elephant Goldfish Review Report — Score: 98/100 APPROVED FOR BUILD)

Both files have been mirrored to:
- `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/`
- `BETA TEST/Grok Bot/8 OCT 26/BATONS/`
- `BETA TEST/Grok Bot/RADIO NET/`

---

## 2. Locked Decisions Verification
- **Locked Decision #1 (10–16 Nov Sprint):** Scheduled strictly as a Tier-1 plan for the upcoming 10–16 Nov build.
- **Locked Decision #2 (Show Values Persistence):** Values gate persists across `Previous coin` / `Next coin` navigation until modal `Close`.
- **Locked Decision #3 (Congress.gov Fallback):** Unchecked statutory data is clearly labeled *"From Congress.gov, not yet checked by us"*, while Numista.AI catalog legislation always takes precedence.

---

## 3. Core Architectural Highlights
- **Single Invocation Pathway:** Cards View and Table View both launch `UnifiedCoinDetailScreen.show`, superseding NET-794 item 3.
- **Accessibility:** 17.5:1 title contrast (`#0b1a2e` on `#ffffff`), 18.9:1 body contrast, minimum ≥52px touch targets, word+icon pairings.
- **Media & Morgan:** Side-by-side front/back photos with tap-to-enlarge, coin silhouette outline fallback (no folder icons), and Ask Morgan integration.
- **Privacy Gate:** Values and storage location are mutually exclusive and never share a screen. Storage location is PIN-gated.
- **Consolidated Tabs:** 6 tabs (Overview, Purchase & value, Morgan's notes, History, Laws, Known errors) with custom wrapping on mobile.
- **Bottom Action Bar:** Explicitly labeled actions (Edit, Wishlist, Verify, Delete with two-stage confirmation).

---

## 4. Next Steps
Handing off to Argon for technical scoring via `BATON_NET-798_ARGON_REVIEW_UNIFIED-COIN-DETAILS-VIEW_2026-11-05-1305.md`.
AG CoS v4 advances to `BATON_NET-801` (Soft-404s, Public Catalog Decision, Pricing Button).
