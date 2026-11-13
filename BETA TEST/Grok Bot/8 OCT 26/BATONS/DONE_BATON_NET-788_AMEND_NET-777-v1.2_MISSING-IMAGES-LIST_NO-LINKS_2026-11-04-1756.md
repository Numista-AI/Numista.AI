# DONE BATON NET-788 - Amend NET-777 to v1.2 (PLAN ONLY)
**Completed By:** AG CoS v4 (`ba2bfdb2`)  
**Completed At:** 5 Nov 2026, 12:25 PM ET  
**Handed Off To:** Argon (Gemini 3.8) for scoring

---

### Deliverables Filed:
1. **`docs/FAILFIX_PLAN_NET-777_CATALOG_v1.2.md`** (Mirrored to `INBOX\`, `BATONS\`, and `RADIO NET\`):
   - 100% internal GCS storage (`gs://numista-catalog-assets` / `gs://numista-reference-library`): zero outbound links or hotlinks.
   - Credit and license rendered strictly in internal metadata and on-page caption text (no external hyperlinks).
   - Standing `MISSING_IMAGES.csv` inventory summarized across all 3,202 master entries.
   - Complete multi-tier $0 acquisition plan (US Mint / Smithsonian NNC / Wikimedia public domain mirror).
   - Strict PII gate excluding receipts, invoices, packing slips, and personal photos.
   - Deleted Section 2E CSP bridge completely (zero external hosts; cites `firebase.json:275-276` and `283-284`).
   - Fixes 2–6 fully preserved.
2. **`docs/MISSING_IMAGES.csv`** (Mirrored to `INBOX\`, `BATONS\`, and `RADIO NET\`):
   - Exactly 3,202 rows (2,965 coins, 181 notes, 56 medals).
   - Itemized by `nac_code`, `type`, `denomination`, `year`, `mint_mark`, `series`, `name`, `obverse_status`, `reverse_status`, `primary_acquisition_tier`, `candidate_source`, `license_type`, `pii_gate_status`, `estimated_cost`.
   - Real match census: Tier 1 (2,273 items), Tier 2 (747 items), Tier 3 (181 items), Tier 4 (1 item).
   - Total acquisition cost: $0.00.

Handed off to Argon via `BATON_NET-788_ARGON_REVIEW_FAILFIX_PLAN_CATALOG_v1.2_2026-11-05-1225.md`.  
AG CoS v4 immediately proceeds to **BATON_NET-791** (`780b v1.1` and `780c v1.1`).
