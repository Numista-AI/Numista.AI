# BATON: `BATON_NET-807_ARGON_REVIEW_SOFT404-PUBLIC-CATALOG-PRICING_v1.1_2026-11-05-1555.md`

- **From:** Antigravity CoS v4 Work (`ba2bfdb2`)
- **To:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Gemini 3.8 Code & Data Auditor)
- **Date / Time:** 2026-11-05 3:55 PM ET
- **Priority:** HIGH — Soft-404, Public Catalog Options A/B/C, and Pricing Plan Revision v1.1 Audit
- **Mode:** **REVIEW ONLY (`NO EXECUTE`)** — Zero code modifications, zero deployments, zero Firestore writes/seeding.
- **Reference Batons:**
  - `BATON_NET-807_REVISE_SOFT404-PUBLIC-CATALOG-PRICING_v1.1_PER-COS-78-SAG-52_2026-11-05-1455.md`
  - `COS_SCORE_NET-801_SOFT404-PUBLIC-CATALOG-PRICING_20261105.md` (CoS 95 PASS / SAG 68 FAIL on v1.0)
- **Target Files for Argon Review:**
  1. `docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.1.md` (mirrored across `INBOX/`, `BATONS/`, and `RADIO NET/`)
  2. `BETA TEST/Grok Bot/8 OCT 26/BATONS/DONE_BATON_NET-807_REVISE_SOFT404-PUBLIC-CATALOG-PRICING_v1.1_2026-11-05-1550.md`

---

## Instructions for Argon (Gemini 3.8):
1. Audit revised plan against the CoS 95 / SAG 68 must-fixes:
   - **Catalog Census:** 5,142 reconciled to 3,202 master entries matching `entries_master_20261103.jsonl` and `MISSING_IMAGES.csv`; "World" claims removed.
   - **Unsourced Claims:** Deleted 99.4% stat, 5,000+ indexable pages, advisory board, Sheldon grading, Passport Protocol.
   - **Public Pricing:** Sourced strictly from CDN CPG retail (`cpgRetail`); zero wholesale; zero user data; gold `'Valuation Pending'` chip for missing pricing.
   - **Images:** AI replicas strictly inside labeled `ai_replica_images`, never primary or index; own-origin allowlist; zero hotlinks.
   - **Options A/B/C:** Fully defined with explicit gate requiring Founder Eric's typed choice ("Option A", "Option B", or "Option C") and typed YES.
   - **Meta Scraper:** Static `<title>` and `<meta property="og:*">` tags for non-JS crawlers (`facebookexternalhit`).
   - **Anchors & AuthGate:** Semantic `Link` widget for footer/Pricing; AuthGate race condition resolved.
   - **Rollback & Safety:** Pinned rollback to `9f04550a`; preview channel gate; $25.00/$20.00 egress hard budget cap cited.
2. File review as `ARGON_REVIEW_PLAN_SOFT404-PUBLIC-CATALOG-PRICING_v1.1.md` in `INBOX/`, `BATONS/`, and `RADIO NET/`.
3. Next in chain: Grok Bot CoS (`>= 95`) -> Stand Alone Grok (SAG, `>= 95`) -> Founder Eric typed choice (Option A, B, or C) & typed YES.
