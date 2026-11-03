# BATON NET-756 - ARGON (Gemini 3.8): review NET-747 Catalog Browse PLAN v4 FIX-ONLY (attempt 4 of 10, AG's FINAL try)
Filed by Antigravity Desk, 3 Nov 2026 3:25 PM ET.

Plan to review: AG_PLAN_NET-747_CATALOG-BROWSE_v4.md (RADIO NET / INBOX, filed 3:11 PM by AG CoS v4; ACK NET-755 at 3:15).
What v4 had to fix: your v3 review (88 REVISE, MF-v3-A..C) and BATON_NET-755 items A-D (now in PROCESSED).
Check every claim against INBOX\NET-747_inputs\entries_master_20261103.jsonl.

Please check especially:
1. Fix-only: no new scope versus v3; change list present.
2. (A) Image source is the fixed credit "Numista.Ai reference photo" on all 81 primary / 966 type / 23 secondary rows, and primary_image.file is kept so the 81 exact-year images load.
3. (B) figures.* allow-list is value, unit, label, source_url only; claim, doc_id, from_file, grounding_score, method, replaced, status dropped; all 1,724 composition rows lose COLLECTION_DERIVED.
4. (C) Scanner FAILS (exit 1) on collection, collector, derived, seed, owner, album (case-insensitive) across nested fields AND built output; \bAJ\b whole-word; museum whitelist stays narrow; the 12 album-named rows (1250, 1251, 1252, 1659, 1920, 1996, 3081, 3082, 3084, 3085, 3086, 3123) get generic names.
   Desk hunch to verify: v4 keeps image paths like assets/catalog/seed_images/<file>. If that path or any file name reaches the built output, the new "seed" scan would fail its own build. Confirm how v4 handles that.
5. (D) Section 8.1 self-check commands really run against the jsonl and prove each fix.

Write: ARGON_REVIEW_NET-747_CATALOG-BROWSE_v4.md on RADIO NET.
If v4 misses, GB CoS writes v5 (attempt 5 of 10). Then GB CoS 95+, then SAG, then Eric's typed YES. PLAN ONLY: no code, commits, deploys or spend. Main stays 9f04550a. Live site untouched. Stripe OFF.
