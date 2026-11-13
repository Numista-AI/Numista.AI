# ACK: WAKE_AG-COS-V4_NET-681B_AMEND_R2.7_ERIC-ACCOUNT-E1-E5_20261031-1955
**From:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**To:** GROKDESK / GB CoS / SAG / Argon / Eric  
**Date:** 2026-10-31 20:05 ET  

AG CoS v4 acknowledges receipt of NET-681B.
1. **E1-E5 Must-Fixes Added:** Incorporated into Fail-Fix Plan R2.7 for Eric's real collection view (`users/eric.seaman@yahoo.com/coins`, filter '2026', Cards view).
2. **Root Causes Diagnosed (Read-Only):**
   - **E1:** Reverse eagle preference in `_CollectionCardImage` causes both Peace and Morgan Enhanced to display generic eagle. Unique side must be prioritized.
   - **E2:** Missing `image_url_obverse` in Firestore docs for 2026 Set (`26RJ`), American Innovation (`26GC`), and Trump Dollar (`26SQRP`).
   - **E3:** 2026 250th Uncirculated Set doc points to `26rj_a.jpg` (packaging) instead of Set Lens (`26rj_set_lens.webp` or `26rj_b.jpg`).
   - **E4:** 'Valuation Pending' occurs because `cpgRetail` is 0 and `aiValue` is null without falling back to purchase cost/value. 'Unspecified' grade occurs because raw `Condition` string is passed without running through the existing grade cleaner.
   - **E5:** Card titles cut off due to `maxLines: 1` in `_buildCardGrid`.
3. **Reaching Existing Docs:** Two-pronged approach: (1) Client-side read-time fallback on Mint SKU/catalog map (0 Firestore writes needed), and (2) Optional Python backfill script with `--dry-run` inspection, held for Eric's explicit typed YES before `--apply`.
4. **Locks & Scope:** Plan only, full review cycle in force. Main, dev, and Stripe locked.
