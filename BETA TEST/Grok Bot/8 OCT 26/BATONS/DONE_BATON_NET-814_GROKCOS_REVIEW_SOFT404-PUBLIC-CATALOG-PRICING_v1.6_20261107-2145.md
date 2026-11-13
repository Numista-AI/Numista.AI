# BATON NET-814 - GROKCOS REVIEW: Soft-404 / Public Catalog / Pricing Plan v1.6

- **Track ID:** NET-814 (Public Catalog Direct Route, Soft-404 Elimination, Static Entry Generation, Retail Pricing Projection & Pricing Surface Plan)
- **From:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **To:** Grok Bot Chief of Staff (`GROKCOS`)
- **Attempt:** AG CoS v5 attempt **4/4** on revision (prior v1.3 was 78 FAIL, v1.4 was 75 FAIL, v1.5 was 86 FAIL per `COS_SCORE_NET-814_SOFT404-CATALOG-PRICING_v1.5_20261107.md` and `RADIO_NET-850`)
- **Date / DTG:** Saturday, 7 November 2026, 21:45 ET (`2026-11-07 21:45:00 -05:00`)
- **Plan File Delivered:**
  - [`docs/PLAN_SOFT404-PUBLIC-CATALOG-PRICING_v1.6.md`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_SOFT404-PUBLIC-CATALOG-PRICING_v1.6.md)
  - [`docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.6.md`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.6.md) (byte-identical mirror, SHA256: `ad6a3a18c431aee9501dc084d8da3d20769d12427e813a86050daccb6ce7d685`)
- **Status:** **DELIVERED FOR GROKBOT COS REVIEW (>= 95 / 100)**
- **Mode:** **STRICT PLAN ONLY — PREVIEW GATE ONLY** (Zero code modifications, zero builds, zero test execution, zero Firestore writes/seeding, zero live deploys without Founder Eric's typed YES)

---

### Standing Operational Invariants & Pinned Boundaries
1. **Production Branch Lock:** `origin/main` strictly locked at `9f04550a45fa4da082ba8948c2d89a521a90fa45`. Direct pushes, merges, or cherry-picks to main are strictly prohibited.
2. **Stripe Lock:** Stripe strictly locked OFF across all client and backend paths.
3. **Budget Policy:** Governed strictly by an **alert-only threshold at $20.00/month** on Google Cloud Billing. Under no circumstances may any agent implement budget caps, hard limits, or automated Hosting teardowns.
4. **Strict PLAN ONLY:** Zero code edits, builds, Firestore writes/seeding, or deploys without Founder Eric typed YES.
5. **No Argon:** Cycle has NO Argon (Argon dropped permanently per Founder Eric typed YES 5 Nov 18:07 ET).
6. **Rule 6a Verbatim Code Citations:** All line references and code snippets are quoted verbatim from pinned commit `4d17ca5e` and `origin/dev`.

---

### Verification Summary of 7 Numbered Must-Fix Resolutions (Per Grok Bot CoS 86 FAIL Report & RADIO_NET-850)

1. **MF-1 (Re-quote `origin/dev:main.dart` lines 154–181):**
   - Re-quoted `origin/dev:numista_mobile/lib/main.dart` public catalog direct dispatch at lines **154–181** verbatim.
   - Explicitly clarified that lines 215–245 on `origin/dev` are the Firebase init timeout and `kApiBaseUrl` error UI, completely eliminating the incorrect line citation.

2. **MF-2 (Ground Public Call Sites in `catalog_browse_screen.dart`):**
   - Quoted `origin/dev:catalog_browse_screen.dart` lines 466 (`onTap: () => _showItemDetailModal(item)`), 810 (`void _showItemDetailModal(Map<String, dynamic> item) {`), and 80 (`_showItemDetailModal(match);`) verbatim.
   - Explicitly noted that line 315 on `origin/dev` is `child: Column(` (Morgan owl header layout) and is NOT a modal call site.

3. **MF-3 (Correct Pin `firebase.json` Line Labels):**
   - Corrected pin line labels: rewrite `source` entries run lines 51–133 (ending at `/claim/**` at line 130 and array closure at line 133).
   - Headers begin at line 135 (`"headers": [`) with first rule at line 137 (`"source": "**/*.@(js|css|wasm)"`).
   - Kept surgical merge diff intact.

4. **MF-4 (`main.dart` Dispatch Tests & Architecture Note):**
   - Added pure route parsing unit test `extractInitialNac(Uri uri)` in §9.2 testing bare `/catalog`, `/catalog/<nac>`, `?item=<nac>`, and non-catalog paths.
   - Detailed why top-level `void main()` is untestable in headless `testWidgets` due to browser window bindings, and affirmed full coverage by §9.1 preview curl tests.

5. **MF-5 (Clean 1921 Morgan OG Tags):**
   - Omitted `<meta property="og:image" ...>` and `twitter:image` for sample `NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3` because image fields are null in that record.
   - Switched `twitter:card` to `"summary"`.
   - Excluded mintage figure (mintage value is null in record). Only present non-null fields included.

6. **MF-6 (Align Valuation Pending Chip to Neutral Slate Gray):**
   - Replaced leftover "gold chip" text with neutral slate gray chip (`#F1F5F9` background, `#64748B` text) in §1, §6.2, and §6.3.

7. **MF-7 (Add Privacy Test to §7.5 File Manifest):**
   - Added `numista_mobile/test/services/catalog_census_privacy_test.dart` to the §7.5 file manifest table.

8. **MF-8 (Delivery Tracking):**
   - Documented v1.5 delivery commit `4a124977` and recorded v1.6 delivery in §11.

Passing baton to GROKCOS for CoS review (target >= 95 / 100).
