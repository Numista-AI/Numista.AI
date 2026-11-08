# BATON NET-810 - GROKCOS REVIEW: U.S. Mint Product Fields in Coin Detail View Plan v1.1

- **Track ID:** NET-810 (Architecture Plan / Feature Specification / Thanksgiving Critical Path)
- **From:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **To:** Grok Bot Chief of Staff (`GROKCOS`)
- **Date / DTG:** Saturday, 7 November 2026, 19:40 ET (`2026-11-07 19:40:00 -05:00`)
- **Plan File Delivered:**
  - [`docs/PLAN_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.1.md`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.1.md)
- **Attempt:** AG CoS v5 attempt **1/4** on v1.1 revision (prior v1.0 was 58 FAIL)
- **Status:** **DELIVERED FOR GROKBOT COS REVIEW ($\ge 95 / 100$)**
- **Mode:** **STRICT PLAN ONLY — PREVIEW GATE ONLY** (Zero code modifications, zero builds, zero test execution, zero Firestore writes/seeding, zero live deploys without Founder Eric's typed YES)

---

### Standing Operational Invariants & Pinned Boundaries
1. **Production Branch Lock:** `origin/main` strictly locked at `9f04550a45fa4da082ba8948c2d89a521a90fa45`. Direct pushes, merges, or cherry-picks to main are strictly prohibited.
2. **Stripe Lock:** Stripe strictly locked OFF across all environments.
3. **Budget Policy:** Governed strictly by an **alert-only threshold at $20.00/month** on Google Cloud Billing. Under no circumstances may any agent implement budget caps, hard limits, or automated Hosting teardowns.
4. **Zero Firestore Writes / Seeding:** Execution of this plan performs **0 writes, 0 updates, and 0 creates** in live Firestore or user collection documents.
5. **No Argon:** Cycle has NO Argon (Argon dropped permanently per Founder Eric typed YES 5 Nov 18:07 ET).
6. **Rule 6a Verbatim Code Citations:** All line references and code snippets are quoted verbatim from pinned commit `4d17ca5e`.

---

### Summary of Numbered Must-Fix Resolutions (Per Grok Bot CoS 58 FAIL Report)

1. **MF-1 (Source-of-Truth & Ingestion Path):**
   - Specified `MintProductLookupService` performing a pure, read-only in-memory join against `assets/catalog/catalog_master_3202.jsonl` (3,202 verified master entries: 2,965 coins, 181 notes, 56 medals).
   - Primary join key: `nac_code`. Fallback composite key: `(year, mintMark, denomination, variety)`.
   - Ambiguous matches (>1) or missing matches (0) fail closed (return `null`; zero Mint product fields rendered).
   - Proposal-status records are quarantined.
   - **Zero Firestore writes, zero network calls, zero user-doc mutations.**

2. **MF-2 (`release_date` Formal Specification & Validation):**
   - Formally specified `release_date` as an authorized schema property requiring standard ISO-8601 calendar date (`YYYY-MM-DD`).
   - Strict regex and calendar validation fail closed against vague or placeholder strings (`"TBD"`, `"TBA"`, `"Fall 2026"`, `"Late 2026"`, `"Pending"`).
   - Display formatting: cleanly formatted via standard date formatting (e.g., `"Nov 12, 2026"`).
   - Pairing rule (R7): `release_time_et` is displayed **only and strictly** when paired with a valid, parsed `release_date`. Never renders `"TBD, noon ET"`.

3. **MF-3 (Preserved `toFirestore()` Signature & Dedicated Allow-List):**
   - Restored exact zero-argument `Map<String, dynamic> toFirestore()` signature in `coin_model.dart:248`.
   - Local optimistic round-trip updates in `coin_detail_screen.dart:490-494` and `682-686` remain 100% intact without parameter mismatch or compilation failure.
   - Publish allow-list filtering (Rule R8) is implemented exclusively on a dedicated method `toPublicCatalogMap({bool includeMintProductFields = false})`.

4. **MF-4 (Pinned Code Grounding & Absence of `copyWith`):**
   - Fully grounded against `coin_model.dart` at pin `4d17ca5e`: class declaration (line 4), constructor (lines 81–110), `fromMap` (lines 169–246), and `toFirestore` (lines 248–297).
   - Explicitly noted that `CoinModel` at `4d17ca5e` does **not** declare a `copyWith()` method, eliminating non-existent method invocations.

5. **MF-5 (`_DetailsTab` Structure & Muted Styling Hooks):**
   - Integrated into `_DetailsTab` (`coin_detail_screen.dart:1513-1544`) immediately before `('Notes', coin.personalNotes)` at line 1541.
   - Values styled using neutral subtext typography: `Theme.of(context).colorScheme.onSurfaceVariant` (WCAG AA compliant contrast ratio $\ge 4.5:1$).
   - Zero `InkWell` or `GestureDetector` widgets attached.

6. **MF-6 (Display Rules, Neutral Copy, Freshness & Value Separation):**
   - Replaced all retail-promotional urgency wording ("On Sale", "Sold Out") with neutral, factual copy:
     - `ON_SALE` / `AVAILABLE` $\rightarrow$ `"Available from U.S. Mint (as of YYYY-MM)"`
     - `COMING_SOON` / `SCHEDULED` $\rightarrow$ `"Scheduled by U.S. Mint"`
     - `SOLD_OUT` / `NO_LONGER_OFFERED` $\rightarrow$ `"No longer offered by U.S. Mint"`
     - `NOT_AVAILABLE` $\rightarrow$ `"Not available from U.S. Mint"`
   - Unvetted strings fail closed to suppressed (`null`).
   - Freshness safeguard: statuses older than 30 days are suppressed to prevent displaying stale availability.
   - Value separation: `productPriceUsd` is strictly historical issue price and NEVER feeds `aiEstimatedValue`, `cpgRetail`, `greysheetBid`, `meltValue`, total collection valuation, portfolio metrics, or coin sorting.

7. **MF-7 (Comprehensive Automated Verification Suite at Real Paths):**
   - Relocated test suite to real path: `numista_mobile/test/mint_product_fields_test.dart` (marked **To be authored**).
   - Includes 12 unit tests and 3 Flutter `testWidgets` tests:
     - Widget test for exact label `"U.S. Mint issue price"` and placement before Notes.
     - Card/browse absence test confirming fields never render on cards.
     - Zero buy links test verifying no clickable or promotional paths.
     - Malformed input tests (negative, NaN, strings, "TBD").
     - Round-trip persistence tests.
     - Zero Firestore writes verification using mock counter.

8. **MF-8 (Acceptance Criteria, File Manifest, Rollback & Timeline Fit):**
   - 10-point numbered operational acceptance checklist.
   - Comprehensive file manifest with real paths.
   - Targeted git revert rollback procedure using `$PRE_EXEC_SHA..HEAD`, maintaining `main` lock at `9f04550a`.
   - Timeline alignment with Catalog Go-Live checkpoint (~13 Nov 2026) ahead of Thanksgiving Meta Ads (26 Nov 2026).

---

### Turn Handoff
Turn is passed to **Grok Bot Chief of Staff (`GROKCOS`)** for independent review and rubric scoring ($\ge 95 / 100$).
Upon Grok Bot CoS pass, turn routes to **Stand Alone Grok (`SAG`)** for secondary independent review ($\ge 95 / 100$).
