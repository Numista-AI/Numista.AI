# ACK BATON NET-748: AG CoS v4, FAILFIX DIAGNOSIS + PLAN DELIVERED
**From:** AG CoS v4 / Gemini 3.8 Code Reviewer (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3` | `eric@numista.ai`)  
**To:** Grok CoS / Argon / SAG / Founder Eric  
**Date:** 3 Nov 2026, 10:07 AM ET  
**Baton Received:** `BATON_NET-748_AG_NET-746-FAILFIX-PLAN-ONLY_20261103-0950.md`  
**Deliverable Filed:** `INBOX\FAILFIX_PLAN_NET-748_AG_v1.md`  

### Status
- Diagnosis and Plan v1 completed.
- Full root cause analysis covering all 3 fails documented:
  1. Collection broken images: `CanonicalMintAssetService` unwired in UI rendering + year `.0` float strings + missing Cent/Nickel/Polly Cooper mappings.
  2. Collection grey placeholders: `coin_image_index` missing Morgan reverse & steal guard suppressing unmapped Polly Cooper reverse.
  3. Add-by-SKU session expired error: missing `global_metadata` read rule in `firestore.rules` causing `permission-denied` (translated by `NumistaErrorHelper` to "session expired") + missing `26SQRP` document in Firestore.
- NO CODE, NO COMMITS, NO DEPLOYS executed.
- Ready for Review Cycle: Argon review -> Grok CoS review (95+) -> SAG review -> Eric's typed YES.
