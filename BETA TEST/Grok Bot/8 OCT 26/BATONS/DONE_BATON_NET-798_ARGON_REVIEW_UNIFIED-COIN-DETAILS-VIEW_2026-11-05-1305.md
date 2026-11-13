# BATON NET-798 - To: Argon - REVIEW ONLY: Unified Coin Details View Plan & EGM Review
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**To:** Argon (Gemini 3.8)  
**Date:** 5 November 2026, 1:10 PM ET  
**Reference:** `BATON_NET-798_PLAN_UNIFIED-COIN-DETAILS-VIEW_2026-11-04-1933.md`  
**Standing Amendment:** `EGM REVIEW GATE` (5 Nov 2026 9:50 AM ET via GB CoS)  
**Review Order:** Argon (Score 95+ required) -> Grok Bot CoS 95+ -> SAG -> Eric typed YES.  

---

## Files in docs/, INBOX, and BATONS:
1. `PLAN_UNIFIED-COIN-DETAILS-VIEW.md` (Unified Coin Details View Plan)
2. `EGM_REVIEW_PLAN_UNIFIED-COIN-DETAILS-VIEW.md` (EGM Swarm Review Report — Score: 98/100)
3. `DONE_BATON_NET-798_PLAN_UNIFIED-COIN-DETAILS-VIEW_2026-11-05-1300.md`

---

## Tasks for Argon:
1. Quote ONLY from real files with real line numbers (see NET-767).
2. **Verify Faithfulness to UX Spec & Founder Eric's Locked Decisions:**
   - Locked Decision #1: Scheduled for 10–16 Nov build.
   - Locked Decision #2: "Show values" once tapped stays visible across Previous/Next coins until Close.
   - Locked Decision #3: Congress.gov API fallback laws labeled *"From Congress.gov, not yet checked by us"*.
   - Both Cards and Table invoke the SAME details view (`UnifiedCoinDetailScreen.show`).
3. **Verify Component Architecture & Privacy Guards:**
   - Header: Solid white background, 32px bold `#0b1a2e` title (17.5:1 ratio), 20px subtitle, ≥52px navigation buttons.
   - Media: Side-by-side front/back photos, tap-to-enlarge, coin silhouette outline (no folder icons), Ask Morgan integration.
   - Values Privacy Gate: Financial values and physical storage location mutually exclusive. Storage location PIN-gated.
   - 6 Tabs: Overview, Purchase & value, Morgan's notes, History, Laws, Known errors. Custom wrap on mobile.
   - Bottom Action Bar: Explicitly labeled actions (Edit, Wishlist, Verify, Delete with two-stage confirmation).
4. **Audit EGM Review Compliance:**
   - Confirm EGM review gate ran, generated deliverable report (`98/100 APPROVED FOR BUILD`), and all 3 minor nits (custom tab wrap, Cards/Table citation clarification, dedicated bottom action bar) are reflected in the plan.
5. **Confirm Standing Locks:**
   - PLAN ONLY. Zero code modifications. Zero deployments.
   - `origin/main` locked at `9f04550a`.
   - Stripe locked OFF.
   - Zero Firestore writes / zero seeding.

---

**Output File:** `INBOX\ARGON_REVIEW_PLAN_UNIFIED-COIN-DETAILS-VIEW.md` with technical score, any must-fixes, and verdict.  
**Mode:** REVIEW ONLY. Nothing executes. No deploys without Eric's typed YES.
