# ACK BATON NET-753 - AG CoS v4

- **Filed by:** AG CoS v4 / Gemini 3.8 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)
- **Timestamp:** 2026-11-03 2:16 PM ET
- **Reference Baton:** `BATON_NET-753_AG_NET-747-PLAN-v3_20261103-1353.md`
- **Delivered Deliverable:** `INBOX\AG_PLAN_NET-747_CATALOG-BROWSE_v3.md` (Attempt 3 of 10, PLAN ONLY)

## Summary of Completed Actions
1. **Allow-List & Schema Overhaul (`MF-1`):**
   - Completely rebuilt the allow-list against real master keys in `entries_master_20261103.jsonl`: `nac_code`, `name`, `type`, `denomination`, `year`, `series`, `mint_facility`, `mint_mark_on_coin`, `composition`, `era`, `designer`, `weight_g`, `diameter_mm`, `mintage`, `history`, `sources`, `figures`, `primary_image`, `type_image`, `secondary_image`, `extra_images`, `varieties`, `pre_federal`, `pre_federal_state`, `display_label`, `note_size`, `social_posts`.
   - Enumerated every permitted nested sub-field (`primary_image`, `type_image`, `secondary_image`, `extra_images`, `varieties`, `sources`, `mintage`, `figures`).
   - Removed inaccurate claim from v2 regarding previous schema alignment.
2. **Complete Strip & Scrub Pipeline (`MF-2`):**
   - Added `seed_status` (1,724 entries), `fold_source`, `record_status`, `needs_fact_check`, `published_on_x`, `program`, `measurement_note`, `reused_from`, `image_status`, `seed_type`, `proposal_status`, `product_code`, `doc_id`, `method`, `grounding_score`, `release_date` to strict deny-by-default strip list.
   - Built offline scrub rules for nested fields: purge `collection-derived` sources, strip internal file/manifest paths (`/workspace/...`, `gs://`), and filter internal status strings.
   - Mandated automated zero-tolerance scan across 100% of records in `catalog_public_v1.json` for forbidden tokens (`"seed"`, `"collection-derived"`, `"user-scoped"`, etc.) with exit code 1 failure.
3. **Accurate Counts & Nothing-Invented Rule (`MF-3`):**
   - Verified and locked master counts: **3,202 total** = **2,965 coins**, **181 notes**, **56 medals**.
   - Locked sourced mintages to exactly **4 records** (1796 Draped Bust cent, 1820 Capped Bust, 1854 Indian head Ty2, 1925 5 Cents). Show sourced mintage with source URL where one exists; remaining 3,198 show `"Needs source"`.
4. **Newest Entries Fallback & Seed Isolation (`MF-4`):**
   - Acknowledged lack of `created_at` / `date_added`; established fallback to Catalog Research file date (`entries_master_20261103.jsonl` timestamp: 3 Nov 2026).
   - Specified visible UI note: *"Entries sorted by Catalog Research file date (3 Nov 2026)."*
   - Specified seed exclusion mechanism (`is_interleaved_checklist_only: true` for `fold_source == "seed_images"` records). Newest strictly populated from original preview records.
5. **Filled Navy Ask Morgan Button (`MF-5`):**
   - Updated Ask Morgan button to filled navy (`#0B2545` background / `#FFFFFF` text / `border: 2px solid #0B2545`).
6. **Firestore & Rules Deploy Guard (`MF-6`):**
   - Specified that deploying `firestore.rules` or writing intake records to Firestore requires Founder Eric's explicit separate typed YES (due to project-wide live impact).
   - Confirmed that Phase 3 deploy authorization covers the **p7v12 preview channel only**, never live production.
7. **Non-Blocking Notes (N-a to N-e):**
   - Verified badge contrast numbers verbatim from UX file (15.39:1 / 12.63:1 text; 6.37:1 / 5.33:1 outline).
   - Confirmed SPA + `noindex` (strictly no Cloud Run).
   - Made era intervals half-open.
   - Confirmed 9 Morgan weight-conflict rejects are excluded and absent from placeholders.
   - Form captcha/rate-limiting collects zero PII.

## Next Steps
- Deliver v3 plan and ACKs across `BATONS/`, `RADIO NET/`, `For SAG/`.
- Docs committed and pushed to `origin/dev` via `catalog_wt`.
- Hand off to Argon for review from `RADIO NET`, followed by Grok CoS 95+, SAG, and Founder Eric's typed YES.
