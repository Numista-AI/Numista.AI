# ACK BATON NET-755 - AG CoS v4

- **Filed by:** AG CoS v4 / Gemini 3.8 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)
- **Timestamp:** 2026-11-03 3:18 PM ET
- **Reference Baton:** `BATON_NET-755_AG_NET-747-PLAN-v4-FIXONLY-FINAL-AG_20261103-1452.md`
- **Delivered Deliverable:** `INBOX\AG_PLAN_NET-747_CATALOG-BROWSE_v4.md` (Attempt 4 of 10, AG's FINAL try on PLAN ONLY)

---

## Summary of Fix-Only Actions in Plan v4

All four required fixes from Baton NET-755 (addressing Argon's findings `MF-v3-A`, `MF-v3-B`, and `MF-v3-C` from `ARGON_REVIEW_NET-747_CATALOG-BROWSE_v3.md`) have been incorporated into `AG_PLAN_NET-747_CATALOG-BROWSE_v4.md` without any scope creep:

### 1. (A) IMAGE SOURCE
- **Preserved `primary_image.file`:** Retained `file` sub-key in `primary_image` for all 81 exact-year seed images so they reliably resolve and load from local asset paths (`assets/catalog/seed_images/<file>`).
- **Sanitized Image Source:** Rewrote `source` across all 1,070 records (81 `primary_image`, 966 `type_image`, 23 `secondary_image`) to `"Numista.Ai reference photo"`. Stripped internal file paths (`from_file`), image status (`image_status`, `status`), and internal collection references.

### 2. (B) FIGURES ALLOW-LIST & COMPOSITION PROVENANCE
- **Stripped Composition Provenance:** Removed `status: "COLLECTION_DERIVED"` and scrubbed `label: "collection-derived, needs primary source"` to `"Needs source"` across all 1,724 `figures.composition` rows.
- **Strict Allow-List for `figures.*`:** Restricted sub-keys strictly to `{value, unit, label, source_url}`. Dropped all internal RAG metadata keys: `claim`, `doc_id`, `from_file`, `grounding_score`, `method`, `replaced`, `status`.

### 3. (C) EXPANDED ZERO-TOLERANCE SCANNER & ALBUM RENAMING
- **Fail-on-Hit Scanner:** Added automated exit code 1 validator scanning all nested JSON fields and final built output for forbidden tokens: `collection`, `collector`, `derived`, `seed`, `owner`, and `album` (case-insensitive).
- **Narrow Museum Whitelist:** Allowed only verified public institution strings: `"National Numismatic Collection"`, `"Josiah K. Lilly Jr. Collection"`, `"herbarium collection"`, and museum source URLs (`americanhistory.si.edu`).
- **Whole-Word `\bAJ\b` Match:** Bounded collector identifier search to `\bAJ\b` to prevent false-positive flagging of dictionary words like "major".
- **12 Album-Named Seed Rows Renamed:** Replaced all third-party collector album names (e.g., "The U.S. Nickel Collection", "Kennedy Half Dollar Collection", etc.) with standardized numismatic type/series names (e.g., "Jefferson Five Cents", "Kennedy Half Dollar"), eliminating all collector album titles from `name` and `series`.

### 4. (D) SELF-CHECK TABLE
- Authored Section 8.1 in Plan v4 containing machine-executable Python one-liners directly runnable against `INBOX\NET-747_inputs\entries_master_20261103.jsonl` linking each fix to its exact plan lines and verifying assertions with exit code 0.

---

## Standing Guardrails
- **PLAN ONLY:** Zero app code written, zero commits to `p7-v8.9` or `dev`, zero deploys, zero spend.
- **Branch & Site Locks:** `origin/main` locked at `9f04550a`; live site untouched; Stripe locked OFF.
- **Firestore Guard:** Zero deployments of `firestore.rules` and zero Firestore writes without Founder Eric's explicit separate typed YES.
- **Preview Channel:** Phase 3 deploy YES covers preview channel `p7v12` only.
- **Precedence:** Catalog Browse never delays or diverts resources from the five 26 Nov must-ships.

---

## Handoff
- Deliverables synced to `BATONS/`, `RADIO NET/`, `For SAG/`, and `catalog_wt` (docs only).
- Turn passed to Argon for review from `RADIO NET`, followed by Grok CoS 95+, SAG, and Founder Eric's typed YES.
