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

## 2026-11-02 8:30 PM ET - AG CoS v4's turn: EXECUTE NET-647 R2.8.19 (NET-746), p7-gate only
SAG scored R2.8.18 93 REVISE (line 444 $_base, Row 10 display, no D-path test). GB CoS filed FAILFIX_PLAN_NET-647_R2.8.19_CoS_20261102.md (MD5 A67C1FD567877D7991A7CBED720330AF), attempt 7 of 10, with only those fixes.
Eric typed 2 Nov 8:14 PM ET: "Make those specific fixes, and you have my Yes to execute. We can test it tomorrow. Keep making progress."
TURN: AG CoS v4 (BATON EXECUTE_GB-COS_NET-746_NET-647-R2.8.19_20261102-2030.md). p7-v8.9 / p7-gate only; main 9f04550a and live locked; Stripe OFF; 45/45 tests required; AG stand-down 3 AM ET; test tomorrow.
## 2026-11-02 6:15 PM ET - SAG / Gemini 3.8's turn on NET-647 R2.8.18 Review (NET-745)
Eric rule (2 Nov 5:56/5:58 PM ET): writer gets 4 tries, then someone else; 10 total tries then notify Eric and break into chunks. NET-647 moved to GB CoS (2 tries tonight), reviewed by SAG + Gemini 3.8. AG CoS v4 is off the pen; BATON_NET-744 / WAKE_AGCOS_NET-744 VOID.
GB CoS FILED FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md (1,735 lines, MD5 2A7805A7DC3C85EBCEE22574BE84BA6D) in INBOX and BATONS, attempt 6 of 10. Five fix-only changes from COS_SCORE R2.8.17 90 REVISE.
TURN: SAG + GEMINI 3.8 (BATON_NET-745). 95+ needed; then Eric's typed YES before any EXECUTE.

# WHOSE_TURN - updated 2026-10-29 ~9:30 AM ET

## NET-644 - Plan.v2.1 DELIVERED
- **Status:** Argon (AG CoS) authored and delivered `US_NUMISMATICS_CATALOG_IMPLEMENTATION_PLAN_V2.1.md` + `SAG_PASTE_PACKET_NET-644_US_NUMISMATICS_CATALOG_PLAN_V2.1.md`.
- **Folded:** Mobile 90/10 companion rewrite, Founder Q1–Q4 sealed, `CO`/`PF`/`FS` polity split, common private medals Phase 2 confirmed, guest rate-limits + NO image download, personal collection photo toggle.
- **Constraints:** PLAN ONLY / no execute / no fold / $0 unapproved spend.
- **Turn:** GB CoS + Stand Alone Grok review Plan.v2.1. No execute until Mint clear or Eric typed parallel-YES.

## OTHER
- Mint FAIL-FIX / NET-641: Day #1 priority on `p7-gate`. `origin/main` LOCKED.
- NET-640 Phase I: Concluded by Catalog Research (`EXECUTE_DONE` filed 28 Oct; 22 docs indexed in `morgan-docs`, total 136; $0.00 spend).
- FOLD: HOLD 586/588/589/590.
