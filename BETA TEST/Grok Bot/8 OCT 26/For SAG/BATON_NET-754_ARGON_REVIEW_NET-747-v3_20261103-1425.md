# BATON NET-754 - ARGON (Gemini 3.8): review NET-747 Catalog Browse PLAN v3 (attempt 3 of 10)
Filed by Antigravity Desk, 3 Nov 2026 2:25 PM ET.

Plan to review: AG_PLAN_NET-747_CATALOG-BROWSE_v3.md (RADIO NET / INBOX, filed 2:13 PM by AG CoS v4).
What v3 had to fix: GB CoS scored v2 82 REVISE (INBOX\GBCOS_SCORE_NET-747_CATALOG-BROWSE_v2.md), must-fixes 1-6 in BATON_NET-753 (now in PROCESSED).
Check every claim against INBOX\NET-747_inputs\entries_master_20261103.jsonl, the same data GB CoS used.

Please check especially:
1. Allow-list uses only real field names, and images, varieties, Pre-Federal and details-coming are on it.
2. Strip list plus a real scrub step for "seed" and "collection" wording inside nested values, and the scan FAILS on any hit (v3 lists "collection-derived" as a scan token; confirm plain "collection" is caught too).
3. Counts: 3,202 = 2,965 coins, 181 notes, 56 medals; 4 sourced mintages.
4. Newest: visible file-date note, and how seed records stay out.
5. Ask Morgan is a filled navy button.
6. Firestore rules deploy / Firestore writes need Eric's separate YES; deploy YES is p7v12 preview only.

Write: ARGON_REVIEW_NET-747_CATALOG-BROWSE_v3.md on RADIO NET.
Then GB CoS 95+, then SAG, then Eric's typed YES. PLAN ONLY: no code, commits, deploys or spend. Main stays 9f04550a. Live site untouched. Stripe OFF.
