# BATON: `BATON_NET-806_ARGON_REVIEW_UNIFIED-COIN-DETAILS-VIEW_v1.1_2026-11-05-1555.md`

- **From:** Antigravity CoS v4 Work (`ba2bfdb2`)
- **To:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Gemini 3.8 Code & Data Auditor)
- **Date / Time:** 2026-11-05 3:55 PM ET
- **Priority:** HIGH — Unified Coin Details View Plan Revision v1.1 Audit
- **Mode:** **REVIEW ONLY (`NO EXECUTE`)** — Zero code modifications, zero deployments, zero Firestore writes/seeding.
- **Reference Batons:**
  - `BATON_NET-806_REVISE_UNIFIED-COIN-DETAILS-VIEW_v1.1_PER-COS-86-SAG-61_2026-11-05-1455.md`
  - `AMEND_BATON_NET-806_CONGRESS-GOV-ONLY_LAWS-TAB_2026-11-05-1444.md` (Eric Typed AMEND: Congress.gov links approved)
  - `COS_SCORE_NET-798_UNIFIED-COIN-DETAILS-VIEW_20261105.md` (CoS 86 FAIL / SAG 61 FAIL on v1.0)
- **Target Files for Argon Review:**
  1. `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.1.md` (mirrored across `INBOX/`, `BATONS/`, and `RADIO NET/`)
  2. `BETA TEST/Grok Bot/8 OCT 26/BATONS/DONE_BATON_NET-806_REVISE_UNIFIED-COIN-DETAILS-VIEW_v1.1_2026-11-05-1550.md`

---

## Instructions for Argon (Gemini 3.8):
1. Audit revised plan against the CoS 86 / SAG 61 must-fixes:
   - **Storage PIN:** Dropped `StorageLocationPinService`; storage strictly hidden until a separate PIN design gets Eric's typed YES.
   - **Call Sites:** All five call sites in `my_collection_screen.dart` correctly cited and re-routed: 2736, 2761, 2773, 3044 (preserving 3043 `setState`), and 3122.
   - **Guest Hide-List:** Strict public/guest mode hide-list suppresses purchase, cost, retailer, invoice, storage, personal notes, private "Show values" toggle, and ownership actions.
   - **Pricing Hygiene:** Sourced strictly from CDN CPG retail (`cpgRetail`); zero wholesale; AI values labeled as `"AI Estimate (Experimental)"`; Live eBay dropped.
   - **Laws Tab (Eric AMEND):** Outbound links to Congress.gov ONLY via plain `<a href>` text links (`target=_blank`, `rel=noopener`); zero PCGS/NGC links; zero external images; catalog legislation wins; unchecked Congress.gov text labeled `"From Congress.gov, not yet checked by us"`; US-only scope; $0.00 spend cap.
   - **Rollback & Safety:** Feature flag `kUnifiedCoinDetailsEnabled`; legacy views preserved in 10–16 Nov build; baseline rollback pinned to `9f04550a`; code freeze before 26 Nov 2026.
   - **Firestore Writes:** Edit, Wishlist, Delete, and research logging segregated to a separate typed YES.
2. File review as `ARGON_REVIEW_PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.1.md` in `INBOX/`, `BATONS/`, and `RADIO NET/`.
3. Next in chain: Grok Bot CoS (`>= 95`) -> Stand Alone Grok (SAG, `>= 95`) -> Founder Eric typed YES.
