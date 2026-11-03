## 2026-11-03 3:18 PM ET - AG CoS v4 Completed BATON NET-755: Filed `AG_PLAN_NET-747_CATALOG-BROWSE_v4.md` (FIX-ONLY FINAL PLAN v4)
AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`) completed `BATON_NET-755_AG_NET-747-PLAN-v4-FIXONLY-FINAL-AG_20261103-1452.md` (Attempt 4 of 10, AG's FINAL try on PLAN ONLY), authoring `INBOX\AG_PLAN_NET-747_CATALOG-BROWSE_v4.md`, `ACK_NET-755.md`, and `ACK_BATON_NET-755_AG_20261103.md` across `INBOX`, `BATONS`, `RADIO NET`, `For SAG`, and `catalog_wt`.
- **Summary of Surgical Fixes in v4 (Items A–D resolving MF-v3-A..MF-v3-C):**
  1. **Item (A) IMAGE SOURCE:**
     - Preserved `primary_image.file` for all 81 exact-year seed images so local asset paths (`assets/catalog/seed_images/<file>`) resolve cleanly.
     - Rewrote image `source` across all 1,070 rows (81 `primary_image`, 966 `type_image`, 23 `secondary_image`) to `"Numista.Ai reference photo"`. Stripped internal paths (`from_file`), `image_status`, and internal collection references.
  2. **Item (B) FIGURES:**
     - Stripped composition provenance: removed `status: "COLLECTION_DERIVED"` and scrubbed `label` to `"Needs source"` across all 1,724 `figures.composition` rows.
     - Enforced strict allow-list on `figures.<metric>`: sub-keys restricted strictly to `{value, unit, label, source_url}`. Dropped all internal RAG metadata keys (`claim`, `doc_id`, `from_file`, `grounding_score`, `method`, `replaced`, `status`).
  3. **Item (C) SCANNER & ALBUM RENAMING:**
     - Automated fail-on-hit (exit code 1) validator scanning all nested JSON fields and built output for `collection`, `collector`, `derived`, `seed`, `owner`, and `album` (case-insensitive).
     - Bounded collector identifier search to `\bAJ\b` to prevent false-positives on words like "major".
     - Narrow museum whitelist allowed only for verified public institutions (`"National Numismatic Collection"`, `"Josiah K. Lilly Jr. Collection"`, `"herbarium collection"`, and museum URLs).
     - Renamed all 12 third-party collector album seed rows to standardized numismatic series/type names (e.g. "Jefferson Five Cents", "Kennedy Half Dollar").
  4. **Item (D) SELF-CHECK TABLE:**
     - Section 8.1 maps every fix to exact plan lines with machine-executable Python one-liners verified against `INBOX\NET-747_inputs\entries_master_20261103.jsonl` (exit code 0).
- **Standing Guardrails:** PLAN ONLY. Zero code/app commits, zero deploys, zero spend. `origin/main` stays `9f04550a`, live site untouched, Stripe locked OFF. `firestore.rules` and Firestore writes require Eric's separate typed YES. Phase 3 deploy YES covers preview channel `p7v12` only. Precedence behind five 26 Nov must-ships strictly maintained.
- **TURN NET-747:** Argon (review from RADIO NET) -> Grok CoS 95+ -> SAG -> Founder Eric's typed YES.
- **TURN NET-748:** SAG (`SAG_REVIEW_NET-748_CoS_v3.md`) / GB CoS -> FOUNDER ERIC TYPED YES.

