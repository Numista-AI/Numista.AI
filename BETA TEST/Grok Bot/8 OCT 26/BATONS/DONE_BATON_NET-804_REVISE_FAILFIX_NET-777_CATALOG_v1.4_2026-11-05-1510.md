# DONE: `BATON_NET-804_REVISE_FAILFIX_NET-777_CATALOG_v1.4_PER-COS-85-SAG-70_2026-11-05-1455.md`

- **To:** Grok Bot Chief of Staff, Argon (Gemini 3.8), Stand Alone Grok (SAG, grok-4.7), Founder Eric
- **From:** Antigravity CoS v4 Work (`ba2bfdb2`)
- **Date / Time:** 2026-11-05 3:10 PM ET
- **Status:** **DONE (`PLAN ONLY` — Zero code modifications, zero deployments, zero Firestore writes/seeding)**
- **Target Deliverables Filed:**
  1. `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.4.md` (and mirrored to `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/`, `BETA TEST/Grok Bot/8 OCT 26/BATONS/`, and `RADIO NET/`)
  2. `docs/MISSING_IMAGES.csv` (scrubbed, verified 100% clean, mirrored to all 3 repositories)

---

## Summary of SAG-92 & CoS Resolutions in Plan v1.4

1. **SAG Must-Fix 1 (Tier Table Stale Split Synchronized in §2.D):**
   - Synchronized Section 2.D tier table to match the exact live scrubbed CSV inventory:
     - **Tier 1 (Internal Scrubbed GCS / Staged Archive):** **2,354**
     - **Tier 2 (Wikimedia Commons / Smithsonian NNC Mirror):** **639**
     - **Tier 3 (US Mint / BEP Historical Currency Archive):** **181**
     - **Tier 4 (Numismatic Partner / Own Photography):** **1**
     - **Tier 5 (Excluded Private Medals - In Copyright / Awaiting License):** **27**
     - **TOTAL Master Records:** **3,202** (Coins: 2,965; Notes: 181; Medals: 56).
2. **SAG Must-Fix 2 & CoS EX-v1.3-1 (`MorganChatPopout` Constructor Signature):**
   - Corrected code specification in §5.C to match the verified implementation in `numista_mobile/lib/widgets/morgan_chat_popout.dart:11-16`:
     - `initialQuery: 'Tell me about the $coinName$coinYear'`
     - `onClose: () => Navigator.of(dialogCtx).pop()`
     - Wrapped inside a centered `Dialog` with `SizedBox(width: 420, height: 600)`.
3. **CSV Private Medals Reclassification & Mint Mark Scrub:**
   - Reclassified 27 private medals dated 1932–1976 (Franklin Mint ANCS series, Great Men of Medicine series, Medallic Art Co Aphrodite, World's Fair medals) from `Public Domain` to:
     - `license_type`: `In Copyright (Private Mint / Post-1929 - Excluded from PD Ingestion until Licensed)`
     - `candidate_source`: `Private Mint Archive / Excluded`
     - `primary_acquisition_tier`: `Tier 5 (Excluded - Private Mint / Awaiting License)`
     - `estimated_cost`: `$0.00`
   - Normalized 147 dirty facility strings (`Philadelphia Mint`, `Bureau of Engraving and Printing`, `Medallic Art Company Ltd.`, etc.) into valid tokens. 100% of 3,202 rows now contain strictly valid tokens in `{'', 'P', 'D', 'S', 'W', 'O', 'CC'}`.
   - Reclassified 13 modern US Mint official medals (1982–2023) to `Public Domain (US Govt Work)` per 17 U.S.C. § 105.
4. **Programmatic Spending Hard Stop (§2.E):**
   - Beyond email alerts at $20.00 (80%), specified an automated Google Cloud Billing Budget Pub/Sub notification wired to Cloud Function `stop-public-egress` that halts public CDN caching / restricts bucket access if monthly spend reaches the $25.00 hard cap.
5. **Strict Condition C1 Pre-Federal Flag Filter (§7.B):**
   - Removed the ambiguous `year < 1792` OR clause from Fix 5; strictly filter on `item['is_pre_federal'] == true || item['pre_federal'] == true`.
6. **Outbound `(source)` Link Removal & US-Only Tab Cleanup:**
   - Cites `origin/dev:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` lines 1010–1017: replaces `InkWell` / `launchUrl` with plain non-clickable text `Source: <institution>`.
   - Cites lines 598–603: removes `Foreign Coins` tab for a 100% US coinage, currency, and medal catalog scope.
7. **Pinned Rollback Targets (§9.A):**
   - Pinned rollback command to baseline commit `9f04550a`: `git checkout 9f04550a -- numista_mobile/firebase.json` and catalog JSON at commit `9f04550a`.
8. **Field Tester Preview Checklist Expanded (§9.B):**
   - Added explicit verification points for Condition C1 pre-federal flags, zero AI replicas in primary image slots, and zero `href`/`src` rendering of internal acquisition notes.

---

## Standing Locks
- `origin/main` strictly locked at `9f04550a`.
- Stripe strictly locked OFF across all configurations.
- Zero live deployments; zero Firestore database writes or security rules changes.
