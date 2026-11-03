# BATON NET-751: ARGON, then SAG, review NET-748 CoS v3 (ATTEMPT 10 of 10, FINAL)
From Antigravity Desk, 3 Nov 2026 11:30 AM ET, at GB CoS's request. REVIEW ONLY. No code, no commits, no deploys.
- Plan: INBOX\FAILFIX_PLAN_NET-748_CoS_v3.md, MD5 668233AA5060BB92076A63D5D57449BD, 335 lines. Check it against the sidecar.
- Writer: GB CoS. It claims to close F2-1..F2-4 and MF-1..MF-5, fix 2 compile errors and missing image paths, and add 19 tests on top of the existing 45.
- Score out of 100; 95+ to pass. List the must-fixes with line citations.
- Reviewers, please check:
  1. firestore.rules is named-doc, READ-ONLY, with no user-data path. The rules deploy is its OWN LIVE step needing Eric's separate YES.
  2. The Firestore SKU seeding (26SQRP) is its OWN LIVE step needing Eric's separate YES.
  3. MF-1: whole-word or denomination-field match, never a "cent" substring.
  4. Variable names match the real code (_skuSearchResult/_skuSearching) and flutter analyze stays clean.
  5. The R2.8.19 Mayflower block and the Row 10 D-mint test are preserved.
  6. Every SKU and image mapping has a provenance table and cited sources, with nothing invented. 26SQRP points to us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg.
  7. Every open item the plan flags.
- Order: Argon, then SAG, then Eric's typed YES. If this FAILS, Eric is notified and the work is broken into smaller chunks.
- Locks: main 9f04550a, live untouched, Stripe OFF.
- Output: INBOX\ARGON_REVIEW_NET-748_CoS_v3.md and SAG_REVIEW_NET-748_CoS_v3.md.
