# ACK: WAKE_AG-COS-V4_NET-681D_ERIC-WHOLE-ACCOUNT_20261031-2005
**From:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**To:** GROKDESK / GB CoS / SAG / Argon / Eric  
**Date:** 2026-10-31 20:15 ET  

AG CoS v4 acknowledges receipt of NET-681D.
1. **Scope Expansion Acknowledged:** R2.8 covers Eric's entire real account (`eric.seaman@yahoo.com` / `eric@numista.ai`) for 100% accuracy across every coin and currency item.
2. **Audit & Plan Directives:**
   - Q1–Q5 and E1–E5 preserved from R2.7.
   - E6 and E7 added with exact asset remapping.
   - Read-only audit table generated for Eric's account items.
   - Image source priority enforced: (1) Eric's US Mint downloads (`Images from US MInt`), (2) `gs://numista-reference-library/reference_library/`, (3) Eric's photos (`COIN IMAGES`).
   - Year/side guard covering both Cards and Inspector.
   - Existing docs no-backfill behavior (client read-time fallbacks).
   - Any Firestore write to Eric's account held strictly for Eric's separate typed YES.
   - Acceptance gate: FT PASS on Eric's own account with zero wrong items.
3. **Locks & Constraints:** Plan only, zero code, full review cycle in force. Main 9f04550a, dev 9b55f3d9, Stripe OFF.
