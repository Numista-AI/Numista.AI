# BATON: `BATON_NET-804_ARGON_REVIEW_FAILFIX_NET-777_CATALOG_v1.4_2026-11-05-1515.md`

- **From:** Antigravity CoS v4 Work (`ba2bfdb2`)
- **To:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Gemini 3.8 Code & Data Auditor)
- **Date / Time:** 2026-11-05 3:15 PM ET
- **Priority:** CRITICAL PATH — Public Catalog Ad Landing Failfix Revision v1.4 (Thanksgiving Ad Launch 26 Nov)
- **Mode:** **REVIEW ONLY (`NO EXECUTE`)** — Zero code modifications, zero deployments, zero Firestore writes/seeding.
- **Reference Batons:**
  - `BATON_NET-804_REVISE_FAILFIX_NET-777_CATALOG_v1.4_PER-COS-85-SAG-70_2026-11-05-1455.md`
  - `BETA TEST/Grok Bot/8 OCT 26/BATONS/COS_SCORE_NET-803_FAILFIX-777-v1.3_20261105.md` (CoS 97 PASS, Argon 98 PASS, SAG 92 FAIL)
- **Target Files for Argon Review:**
  1. `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.4.md` (mirrored in `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/` and `BETA TEST/Grok Bot/8 OCT 26/BATONS/`)
  2. `docs/MISSING_IMAGES.csv` (scrubbed, verified 100% clean, mirrored across all 3 directories)
  3. `BETA TEST/Grok Bot/8 OCT 26/BATONS/DONE_BATON_NET-804_REVISE_FAILFIX_NET-777_CATALOG_v1.4_2026-11-05-1510.md`

---

## Instructions for Argon (Gemini 3.8):
1. Audit `FAILFIX_PLAN_NET-777_CATALOG_v1.4.md` against SAG's two blocking must-fixes and non-blocking refinements:
   - **SAG Must-Fix 1 (§2.D & CSV):** §2.D tier table synchronized to exact live CSV counts: 2,354 Tier 1 / 639 Tier 2 / 181 Tier 3 / 1 Tier 4 / 27 Tier 5 = 3,202 total.
   - **SAG Must-Fix 2 & CoS EX-v1.3-1 (§5.C):** `MorganChatPopout` code snippet verified against `numista_mobile/lib/widgets/morgan_chat_popout.dart:11-16` using `initialQuery`, required `onClose: () => Navigator.of(dialogCtx).pop()`, and centered `Dialog` wrapper.
   - **CSV Scrubbing Verification:** 147 dirty facility strings cleaned from `mint_mark` into valid tokens in `{'', 'P', 'D', 'S', 'W', 'O', 'CC'}`; 27 post-1929 private medals reclassified to `Tier 5` (`In Copyright (Private Mint / Post-1929 - Excluded from PD Ingestion until Licensed)`); 13 official US Mint medals dated 1982–2023 corrected to `Public Domain (US Govt Work)`.
   - **Programmatic Hard Stop (§2.E):** Cloud Billing budget Pub/Sub alert + Cloud Function `stop-public-egress` at $25.00/mo hard cap.
   - **Strict Condition C1 Filter (§7.B):** Flag-only check for pre-federal era (`item['is_pre_federal'] == true || item['pre_federal'] == true`).
   - **Outbound Link & Tab Cleanup (§2 & §8.A):** Verbatim citations on `dev:catalog_browse_screen.dart` lines 1010–1017 (removal of `launchUrl` outbound link) and lines 598–603 (removal of `Foreign Coins` tab).
   - **Pinned Rollback Targets (§9.A):** Revert commands pinned to baseline commit `9f04550a`.
   - **Field Tester Preview Checklist (§9.B):** Added Condition C1 pre-federal flags, zero AI replicas in primary slots, and zero `href`/`src` rendering of internal acquisition notes.
2. File your review as `ARGON_REVIEW_FAILFIX_PLAN_CATALOG_v1.4.md` in `INBOX/`, `BATONS/`, and `RADIO NET/`.
3. Next in chain: Grok Bot CoS (`>= 95`) -> Stand Alone Grok (SAG, `>= 95`) -> Founder Eric typed YES.
