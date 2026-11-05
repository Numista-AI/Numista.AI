# BATON: `BATON_NET-803_ARGON_REVIEW_FAILFIX_NET-777_CATALOG_v1.3_2026-11-05-1405.md`

- **From:** Antigravity CoS v4 Work (`ba2bfdb2`)
- **To:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Gemini 3.8 Code & Data Auditor)
- **Date / Time:** 2026-11-05 1:55 PM ET
- **Priority:** HIGH — Public Catalog Ad Landing Failfix Revision v1.3
- **Mode:** **REVIEW ONLY (`NO EXECUTE`)** — Zero code modifications, zero deployments, zero Firestore writes/seeding.
- **Reference Batons:**
  - `BATON_NET-803_REVISE_FAILFIX_NET-777_CATALOG_v1.3_PER-SAG-75_2026-11-05-1342.md`
  - `1 NUMISTA.AI/Grok CoS to Antigravity/OUTBOX/COS_SCORE_NET-788_FAILFIX-777-v1.2_20261105.md` (CoS 96 PASS, Argon 96 PASS, SAG 75 FAIL)
- **Target Files for Argon Review:**
  1. `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.3.md` (also in `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/` and `BETA TEST/Grok Bot/8 OCT 26/BATONS/`)
  2. `docs/MISSING_IMAGES.csv` (scrubbed, verified 100% clean)
  3. `BETA TEST/Grok Bot/8 OCT 26/BATONS/DONE_BATON_NET-803_REVISE_FAILFIX_NET-777_CATALOG_v1.3_2026-11-05-1400.md`

---

## Instructions for Argon (Gemini 3.8):
1. Audit `FAILFIX_PLAN_NET-777_CATALOG_v1.3.md` against the 5 SAG must-fixes and Argon's prior advisories:
   - **SAG Must-Fix 1:** Binding catalog-first AI rule in §2.B & §7.B (`ai_replica_images` only; never primary/card/index).
   - **SAG Must-Fix 2:** Dedicated rollback commands (§8.A) and mandatory Preview Channel gate (§8.B) before production.
   - **SAG Must-Fix 3:** CSV hygiene verified (81 blank-source rows reclassified, mint marks extracted, album titles scrubbed, `$0.00` restored, unproven match claims dropped).
   - **SAG Must-Fix 4:** Hard monthly $ cap ($25.00/mo) and automated Cloud Monitoring billing alert ($20.00/mo) covering GCS + CDN egress under Meta ads (§2.E). Tier 4 studio photography is strictly existing owned photos ($0.00).
   - **SAG Must-Fix 5:** Fix 3 signed-in path rewritten using native `MorganChatPopout` dialog from `lib/widgets/morgan_chat_popout.dart` (§4.C).
   - **Non-blocking & EX-1..EX-4:** Deep link modal close uses `window.history.back()` / handles `popstate` (§3.C); versioned catalog JSON filenames (`catalog_index_v{timestamp}.json`, §7.C); candidate source URLs strictly internal acquisition notes (§2.C); softened signed-out Morgan copy (§4.C); branch guard on `dev` (§9); explicit statement that Eric's YES is for code/GCS assets on dev/preview, NOT Firestore writes/rules.
2. File your review as `ARGON_REVIEW_FAILFIX_PLAN_CATALOG_v1.3.md` in `INBOX/`, `BATONS/`, and `RADIO NET/`.
3. Next in chain: Grok Bot CoS (`>= 95`) -> Stand Alone Grok (SAG, `>= 95`) -> Founder Eric typed YES.
