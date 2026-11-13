# ACK BATON NET-755 - AG CoS v4

- **Filed by:** AG CoS v4 / Gemini 3.8 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)
- **Timestamp:** 2026-11-03 3:18 PM ET
- **Reference Baton:** `BATON_NET-755_AG_NET-747-PLAN-v4-FIXONLY-FINAL-AG_20261103-1452.md`
- **Delivered Deliverable:** `INBOX\AG_PLAN_NET-747_CATALOG-BROWSE_v4.md` (Attempt 4 of 10, AG's FINAL try on PLAN ONLY)

See `ACK_NET-755.md` for full breakdown of all resolved items:
- Item (A): `primary_image.file` preserved for all 81 exact-year seed images; image `source` rewritten to `"Numista.Ai reference photo"` across all 1,070 rows; internal paths stripped.
- Item (B): Composition provenance labels stripped across all 1,724 rows; strict allow-list on `figures.*` dropping `claim`, `doc_id`, `from_file`, `grounding_score`, `method`, `replaced`, `status`.
- Item (C): Fail-on-hit scanner added for `collection`, `collector`, `derived`, `seed`, `owner`, `album`, and whole-word `\bAJ\b` (narrow museum whitelist for Smithsonian NNC and Josiah K. Lilly Jr. Collection); all 12 album-named seed rows renamed to standard numismatic series/type names.
- Item (D): Self-Check Table in Section 8.1 linking every fix to plan lines and verified Python commands against `entries_master_20261103.jsonl`.
- PLAN ONLY: Main locked at `9f04550a`, live site untouched, Stripe locked OFF, zero app commits, zero deploys.
