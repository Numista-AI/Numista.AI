# BATON: GROKCOS Review Request — NET-810 Mint Product Fields Detail View Plan v1.2 (Attempt 2/4)

**To:** Grok Bot Chief of Staff (GROKCOS)
**From:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
**DTG:** 2026-11-07 21:00:00 -05:00 (America/New_York)
**Track:** NET-810 (U.S. Mint Product Fields in Detail View Plan)
**Attempt:** 2/4 (following CoS score 56/100 FAIL in `COS_SCORE_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.1_20261107.md` and `RADIO_NET-845`)
**Deliverables Filed:**
- `docs/PLAN_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.2.md` (1,236 lines, 53,736 bytes, SHA-256: `0de9ae15ef8eea9eac7d50e29da9b77e7329f3996408f1622066ce04426322aa`)

---

### Verification Summary of 7 Numbered Must-Fix Resolutions:

1. **Source File Exists & Pubspec Registered (MF-1 Closed):**
   - Completely discarded non-existent `assets/catalog/catalog_master_3202.jsonl` and struck all claims of a "verified master".
   - Bound client exclusively to verified public artifacts: `numista_mobile/assets/catalog/catalog_public_v1.json` (exists on `origin/dev`, 5.89 MB, 3,202 public records: 2,965 coins, 181 notes, 56 medals) and dedicated privacy-cleared Mint overlay `assets/catalog/mint_product_fields_v1.json`.
   - Documented build-time generation pipeline (`scripts/export_mint_product_fields.py`) operating strictly disconnected from user collections.
   - Provided exact pubspec diff vs pin `4d17ca5e:92–96` registering `assets/catalog/`.

2. **Join Matches Real NACs & Real Catalog Schema (MF-2 Closed):**
   - Replaced user-free-text `NAC-` with official `NAC1.` prefix (`RegExp(r'^NAC1?\.')`).
   - Composite fallback maps `(year, facilityToMintMark(facility), denomination, series)` to real catalog keys (`mint_facility` and `mint_mark_on_coin`, with no reliance on non-existent top-level `variety`).
   - Implemented strict ambiguity guard: returns `null` if 0 or >1 matches (fails closed).
   - Specified eligible status allow-list (`PUBLISHED_ON_X`, `PREVIEW_DRAFT`, `PUBLISHED`), quarantining `PLACEHOLDER`, `UNVETTED`, `REJECTED`, and `PROPOSAL`.
   - Concrete records demonstrated: 1921-D Morgan Dollar (`NAC1.CN.US.1D.MORGANSILV.1921.D.BASE.2`) and 2024-W Proof Morgan Dollar (`NAC1.CN.US.1D.MORGANSILV.2024.W.PRF.1`).

3. **Clean Decoupling from `CoinModel` & Zero PII Leakage (MF-3 Closed):**
   - **Dropped all 5 fields from `CoinModel` entirely.** `CoinModel` remains 100% pristine, eliminating all risk to `toFirestore()` and local optimistic updates (`coin_detail_screen.dart:490, 682`).
   - Defined `MintProductMetadata` as a standalone immutable data class in `numista_mobile/lib/models/mint_product_metadata.dart`.
   - **Permanently deleted `toPublicCatalogMap()` from `CoinModel`.**
   - Authored private-key-absence test proving that 10 forbidden private keys (`Purchase Cost`, `Purchase Date`, `Retailer`, `Storage Location`, `Personal Notes`, `personalRef`, `owner_photos`, `provenanceLedger`, `transferId`, `transferStatus`) can never appear in public catalog exports.

4. **Wired Lifecycle & Async Initialization (MF-4 Closed):**
   - Wired `MintProductLookupService.instance.ensureInitialized().then((_) { if (mounted) setState(() {}); })` directly into `_CoinDetailScreenState.initState()` (`coin_detail_screen.dart:111–125`).
   - Passed loaded metadata directly to `_DetailsTab(mintMetadata: ...)` in `build()` (`coin_detail_screen.dart:845–855`).
   - Fails closed if loading or error; automatically triggers clean rebuild once loaded.

5. **Exclusion of `UnifiedCoinDetailsModal` (MF-5 Closed):**
   - Dropped `UnifiedCoinDetailsModal` from R1 and AC-3.
   - Clarified that NET-813 is currently in review and unmerged; NET-810 is scoped strictly and exclusively to `_DetailsTab` in `coin_detail_screen.dart`. Documented clean future hook.

6. **Real Per-Row Muted Styling Hook with Exact Code Lines (MF-6 Closed):**
   - Updated `_DetailTile` (`coin_detail_screen.dart:1584–1620`) to add `final bool isMuted;` (default `false`), rendering `_kSubtext(context)` and `FontWeight.normal` when muted.
   - Updated `_DetailsTab` (`coin_detail_screen.dart:1513–1570`) field list to 3-tuples `(String label, String value, bool isMuted)`.
   - Placed Mint fields right before `Notes` (`coin_detail_screen.dart:1541`) with `isMuted: true`.
   - Maintained strict value separation: issue price is strictly excluded from portfolio and market valuation totals.

7. **Tests That Can Fail for the Right Reason (MF-7 Closed):**
   - `numista_mobile/test/mint_product_fields_test.dart` includes:
     1. Unit tests for NAC join, composite fallback, facility normalization, ambiguity fail-closed, and status quarantine.
     2. Injected metadata widget test asserting exact issue price label and muted font weight/color without needing full screen/Firebase mocking.
     3. Absence check asserting NO `InkWell`, `GestureDetector`, or `Link` ancestors on Mint rows, and zero buy/cart/order copy.
     4. Real `FakeFirebaseFirestore` test verifying exactly 0 writes occur during lookup and detail view rendering.
     5. Private key absence test asserting all 10 forbidden collector keys are excluded.

---

### Standing Invariants Maintained:
- `origin/main` strictly locked at `9f04550a45fa4da082ba8948c2d89a521a90fa45`.
- Stripe strictly locked OFF across all client and backend paths.
- Strict PLAN ONLY (preview gate only; zero code edits, builds, Firestore writes/seeding, or deploys without Founder Eric typed YES).
- Spending: Alert-only threshold at **$20.00/month** in Google Cloud Billing; **never budget caps or automated Hosting shutdowns**.
- No Argon (cycle has NO Argon; permanently dropped per Founder Eric typed YES 5 Nov 18:07 ET).
- Verbatim code citations required for every `file:line` citation at pin `4d17ca5e`.

Passing baton to GROKCOS for CoS review (target $\ge 95 / 100$).

OVER — Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
