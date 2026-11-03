# BATON NET-755 - AG: NET-747 Catalog Browse PLAN v4 FIX-ONLY (PLAN ONLY) - attempt 4 of 10, AG's FINAL try
Filed by Antigravity Desk, 3 Nov 2026 2:52 PM ET, on GB CoS's direction. Source: INBOX\ARGON_REVIEW_NET-747_CATALOG-BROWSE_v3.md (88 REVISE).

Write INBOX\AG_PLAN_NET-747_CATALOG-BROWSE_v4.md. Make it fix-only against v3: no new scope, plus a change list. If v4 misses, GB CoS writes v5.

(A) IMAGE SOURCE
   - Rewrite the image source as a fixed public credit with no 'collection' or 'owner' wording (e.g. 'Numista.Ai reference photo').
   - KEEP primary_image.file, so the 81 exact-year images still load.
(B) FIGURES
   - Strip the composition provenance labels (COLLECTION_DERIVED / 'collection-derived').
   - Make figures.* an allow-list: keep value, unit and source citation only. Drop claim, doc_id, from_file and grounding_score.
(C) SCANNER
   - FAIL on any hit for collection, collector, derived, seed, owner or album (case-insensitive), across every nested field AND the built output.
   - For AJ, match the whole word only (\bAJ\b), so words like 'major' don't false-flag.
   - Rename the 12 album-named rows (e.g. 'The U.S. Nickel Collection') to the generic coin or set name, or exclude them from the seed rows.
(D) SELF-CHECK TABLE: for each fix, give the plan line it's at and the command that proves it, run against INBOX\NET-747_inputs\entries_master_20261103.jsonl.

PLAN ONLY: no code, no app commits, no deploys, no spend. Main stays 9f04550a. The live site stays untouched. Stripe stays OFF.
When it's filed, write ACK_NET-755 in INBOX. Argon reviews it from RADIO NET, then CoS 95+, then SAG, then Eric's typed YES.
