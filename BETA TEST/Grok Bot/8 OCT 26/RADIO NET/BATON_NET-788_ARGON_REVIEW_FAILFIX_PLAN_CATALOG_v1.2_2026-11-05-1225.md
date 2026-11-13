# BATON NET-788 - To: Argon - REVIEW ONLY: FAILFIX PLAN v1.2 Live Catalog (NET-777 / NET-788)
From: Antigravity CoS v4 Work (`ba2bfdb2`)   5 Nov 2026 12:25 PM ET

Review order: Argon (Gemini 3.8 score 95+ required) -> GB CoS 95+ -> SAG -> Eric typed YES.

Files in INBOX, BATONS, and docs/:
- `FAILFIX_PLAN_NET-777_CATALOG_v1.2.md`
- `MISSING_IMAGES.csv` (3,202 rows verified)
- `DONE_BATON_NET-788_AMEND_NET-777-v1.2_MISSING-IMAGES-LIST_NO-LINKS_2026-11-04-1756.md`

Your tasks:
1. Quote ONLY from real files with real line numbers (see NET-767).
2. Verify all Founder Eric directives from BATON_NET-788 are comprehensively satisfied:
   - Zero outbound links or hotlinks: every catalog image must be served from our internal GCS (`gs://numista-catalog-assets` / `gs://numista-reference-library`) via our domain. Credit and license go strictly in metadata / caption text, not as links to other sites.
   - Standing `MISSING_IMAGES.csv` inventory in repo docs across all 3,202 master entries, with year, mint mark, denomination, and obverse/reverse status.
   - Acquisition plan for each missing item: license-safe copies from Wikimedia/NNC/US Mint public domain, order of precedence, real counts, and $0 cost.
   - Strict PII gate: generic coin images only, strictly excluding receipts, invoices, packing slips, and personal photos.
   - Deleted Section 2E CSP temporary bridge completely (zero external hosts; cites `firebase.json:275-276` and `283-284`).
3. Verify fixes 2 through 6 preserved from v1.1 (scored 95):
   - Item 2: Deep links (Real shareable URLs, History API).
   - Item 3: Ask Morgan (Signed-out preview modal with redirect).
   - Item 4: Era filter state (Reset on tab switch).
   - Item 5: Pre-Federal filter consistency (Condition C1 strict alignment, 9 records).
   - Item 6: First load latency (< 2.0s target).
4. Confirm standing locks:
   - PLAN ONLY. Zero code modifications. Zero deployments.
   - `origin/main` stays locked at `9f04550a`.
   - Stripe stays locked OFF.
   - Zero Firestore writes / zero seeding.

Output: `INBOX\ARGON_REVIEW_FAILFIX_PLAN_CATALOG_v1.2.md` with score, any must-fixes, and verdict.
REVIEW ONLY. Nothing executes. No deploys.
