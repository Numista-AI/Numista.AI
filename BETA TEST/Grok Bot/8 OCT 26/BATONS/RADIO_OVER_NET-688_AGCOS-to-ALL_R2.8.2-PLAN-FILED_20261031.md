# RADIO NET: NET-688 AGCOS-to-ALL: R2.8.2 FAILFIX PLAN FILED

**Message ID:** NET-688  
**Date:** 2026-10-31 22:05 EDT  
**From:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`, `eric@numista.ai`, PAYG `numista-qc`)  
**To:** GROK CoS / ARGON / SAG / FOUNDER ERIC  
**Classification:** DOCS-ONLY (`NO EXECUTE`)  
**Subject:** NET-647 Fail-Fix Plan R2.8.2 Filed Addressing Score 78 Blockers 1–3 & S1–S3

---

### Radio Dispatch Summary

1. **Inbound Response:** Responding to `COS_SCORE_NET-647_R2.8.1_78_REVISE_20261031-2115.md` and `WAKE_AG-COS-V4_NET-687_R2.8.2_FIX-ONLY_20261031-2115.md`.
2. **Deliverables Authored:**
   - `FAILFIX_PLAN_NET-647_R2.8.2_20261031.md` (complete, fix-only plan revision)
   - `GEMINI38_REVIEW_NET-647_R2.8.2_2026-10-31.md` (with verbatim code citations per Rule 6a)
   - `ACK_WAKE_AG-COS-V4_NET-687_R2.8.2_FIX-ONLY_20261031-2115.md`
3. **Blockers & Should-Fixes Rectified:**
   - **Blocker 1 (Verified 2026 URLs):** Replaced non-existent filenames with verified real GCS objects (`26EA_image_1.jpg`, `26XE_image_1.jpg`, `26XL_image_1.jpg`, `26RJ_image_1.jpg`, `26GC_image_1.jpg`, `MASTER_SEMIQDJT_image_1.jpg`, etc.). Verified 100% of URLs with HTTP 200 HEAD requests and byte counts.
   - **Blocker 2 (SKU-First Resolver & Negative Tests):** `Canonical2026MintAssets.resolve()` rewritten to match SKU (`retailer_item_num` / `item_number`) FIRST with exact case-insensitive trim. Title fallback enforces `\b2026\b` and program word boundaries. Negative tests specified (T1–T11, NEG-1: 2026-W Gold $\rightarrow$ null, NEG-2: 2026-W Unc $\rightarrow$ null).
   - **Blocker 3 (All 28 Audit Rows Detailed):** Explicit post-fix obverse, reverse, and card URLs defined for all 28 rows with verified HTTP 200 status codes and Content-Length bytes. Numismatic whitelist for ATB Washington obverses specified.
   - **Should-Fix S1:** Line-total guard implemented in unit cost calculation.
   - **Should-Fix S2:** Generic unique-side card display rule formalized per Eric's 15 Oct directive.
   - **Should-Fix S3:** Field Tester expectations for `26GC` clarified.
4. **Current Status & Locks:**
   - Mode: DOCS-ONLY (`NO EXECUTE`). Zero code edits, zero git commits of code, zero Firebase deploys, zero GCS uploads, zero Firestore writes.
   - Target Branch: `p7-v8.9` (`2f38fcc8`).
   - Hosting: `p7-gate` preview channel only.
   - Stand-down: 3 AM stand-down strictly observed.
5. **Turn Status:**
   - Baton passed to **ARGON** and **GROK CoS** for Plan R2.8.2 evaluation ($\ge 95$ gate).

OVER.
