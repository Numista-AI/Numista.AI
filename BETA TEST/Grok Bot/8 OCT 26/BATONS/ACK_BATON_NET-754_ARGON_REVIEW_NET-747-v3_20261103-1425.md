# ACK: BATON_NET-754_ARGON_REVIEW_NET-747-v3_20261103-1425

- **Station:** Argon (`31035602` — Independent Technical Reviewer / Gemini 3.8 Code & Data Auditor)
- **Timestamp:** 2026-11-03 14:33 ET
- **Status:** COMPLETE (`88 / 100 — REVISE TO v4`)
- **Deliverables Filed:**
  - `RADIO NET\ARGON_REVIEW_NET-747_CATALOG-BROWSE_v3.md`
  - `INBOX\ARGON_REVIEW_NET-747_CATALOG-BROWSE_v3.md`
  - `RADIO NET\GEMINI38_REVIEW_NET-747_CATALOG-BROWSE_v3_2026-11-03.md`
  - Synced to both `31 OCT 2026\For SAG` and `8 OCT 26\For SAG`
- **Summary of 6 `BATON_NET-754` Checks:**
  1. **Check #1 (Positive Field Allow-List + Nested Sub-Fields): FAIL (`MF-v3-A`, `MF-v3-B`)**
     - `v3` lines 132–133 allow-list `source` inside `type_image` (`966` rows) and `secondary_image` (`23` rows), where every single row in `entries_master_20261103.jsonl` contains `"source": "collection photo, owner removed"`. Remove `source` and `status` from `primary_image`, `type_image`, and `secondary_image`.
     - `v3` line 131 omits `file` from `primary_image`, stripping the image path from all `81` exact-year seed `primary_image` objects (`file: "NAC1-....jpg"`, no `url` key).
     - `v3` line 138 lists `figures: {mintage, weight_g, diameter_mm, fineness, composition}` without restricting sub-keys to `{value, unit, label, source_url}` (leaking internal RAG sub-keys `claim`, `doc_id`, `from_file: "EXTRACT_retry.json"`, `grounding_score`, `method`, `replaced`, `status`) and without scrubbing `figures.composition` (`1,724` rows, all `status: "COLLECTION_DERIVED"`, `label: "collection-derived, needs primary source"`).
  2. **Check #2 (Strip List + Nested Scrub + Scan FAILS on Any Hit Including Plain `"collection"`): FAIL (`MF-v3-C`)**
     - Confirmed `BATON_NET-754`'s flag: `v3` line 158 scans for `"collection-derived"` and `"collection-seed"`, NOT plain `"collection"` or plain `"derived"`.
     - Furthermore, `v3` line 154 exempts `"The U.S. Nickel Collection"`, which is one of **12 `fold_source == "seed_images"` rows** where third-party collector-album titles (`"The U.S. Nickel Collection"`, `"The World War II U.S. Coin Collection"`, `"Modern Morgan and Peace Silver Dollar Collection"`, `"The Ultimate Modern Morgan and Peace Silver Dollar Collection"`, `"Celebrating America Coin Collection"`) were ingested into `name` and `series` from user collection albums.
     - Fix: `pii_gate_validator.py` must scan case-insensitively for plain `collection`, plain `derived`, and plain `seed` (allowing only exact museum provenance strings `"National Numismatic Collection"`, `"Josiah K. Lilly Jr. Collection"`, `"herbarium collection"`, and museum URLs `metmuseum.org/art/collection/`, `numismatics.org/collectionimages/`, `si.edu/collection/`), and normalize the 12 collector-album `name`/`series` rows.
  3. **Check #3 (Exact Counts & 4 Sourced Mintages): PASS** (`3,202` total = `2,965` coins + `181` notes + `56` medals; `4` sourced mintages vs `3,198` `"Needs source"`; `951` placeholders; plus non-blocking data flag `N-v3-1` noting that 2 of the 4 `EXTRACT_retry.json` mintages matched El Salvador 5 centavos on Row 1022 and 1854-S Type 1 on Row 223).
  4. **Check #4 (Newest Entries Honest File-Date Disclosure + Seed Exclusion): PASS** (`3 Nov 2026` file date with visible UI note + `fold_source == "seed_images"` excluded).
  5. **Check #5 (Ask Morgan Filled Navy Button): PASS** (`#0B2545` background, `#FFFFFF` text, `2px solid #0B2545`, `36x36` owl icon).
  6. **Check #6 (Firestore Rules Guard + Preview-Only Deploy YES): PASS** (`firestore.rules` deploy & Firestore writes gated behind Eric's separate typed YES; Phase 3 deploy strictly `p7v12` preview only).
- **Turn:** Grok CoS (`GB CoS`) / AG CoS v4 (`v4` surgical revision on Checks #1 & #2).
