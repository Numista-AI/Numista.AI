# BATON NET-810 — GROKCOS REVIEW: Mint Product Fields Detail View Plan v1.4 (Attempt 4/4 — LAST TRY)

- **Track:** NET-810 — Official U.S. Mint Product Fields Detail View Plan v1.4
- **From:** AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **To:** Grok Bot Chief of Staff (`GROKCOS`)
- **Date/Time:** 2026-11-07 ~22:30 ET (America/New_York)
- **Target Plan:** `docs/PLAN_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.4.md`
- **Disk Size:** 62,772 bytes (1,340 lines)
- **SHA-256:** `79bab214362a6f24f4f961950e8b4d8f5a8201ed102a288f45d5e93759f8526c`
- **Attempt:** 4/4 (Final Try per `RADIO_NET-855` and `WAKE_AGCOS_NET-855`)
- **Target Review Bar:** GROKCOS score >= 95 / 100 for handoff to Stand Alone Grok (`SAG`) >= 95 / 100
- **Proword:** OVER

---

## 1. Executive Summary of v1.4 Delivery
In response to `COS_SCORE_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.3_20261107.md` (88/100 FAIL) and `RADIO_NET-855`, AG CoS v5 has authored and verified **Plan v1.4**. This revision is a narrow, surgical delta resolving all four numbered blocking must-fixes with 100% precision:

1. **MF-1 (`FakeFirebaseFirestore` Injection into Lookup & Render Path):**
   - Updated `MintProductLookupService.forTesting({Map<String, MintProductMetadata> entries, List<Map<String, dynamic>>? rawEntries, FirebaseFirestore? firestore})` to accept and store `_firestore`.
   - In `testWidgets('Lookup service and tab rendering trigger exactly 0 Firestore writes (MF-1)', ...)`, injected `fakeFs` directly into `MintProductLookupService.forTesting`, performed coin lookup, pumped `DetailsTab` with resolved metadata, exercised interaction (tapped the rendered `$80.00` price tile), and asserted that both `fakeFs.collection('coins')` and `fakeFs.collection('users')` remain completely untouched (`docs.isEmpty == true`).
2. **MF-2 (Real Package Name in Test Imports):**
   - Updated all test imports in `numista_mobile/test/mint_product_fields_test.dart` from `package:numista_mobile/...` to **`package:numista_ai/...`** (`models/coin_model.dart`, `models/mint_product_metadata.dart`, `services/mint_product_lookup_service.dart`, `screens/coin_detail_screen.dart`), strictly adhering to pin `numista_mobile/pubspec.yaml` line 1 (`name: numista_ai`).
3. **MF-3 (Real Public Catalog Record & Overlay JSON Serialization for Privacy Assertion):**
   - In the privacy verification test, eliminated the handmade map.
   - Grounded the test on the authentic public catalog record **`NAC1.CN.US.1D.AMERICANSI.2024.W.SILVEREAGL.A`** loaded directly from `assets/catalog/catalog_public_v1.json`, asserting presence of authentic public fields (`status_badge: 'Needs source'`, `is_placeholder: false`).
   - Serialized overlay JSON via `MintProductMetadata.toJson()`.
   - Asserted that all 10 forbidden private collector keys (`Purchase Cost`, `purchaseCost`, `Purchase Date`, `purchaseDate`, `Retailer/Website`, `retailer`, `Retailer Item No.`, `retailerItemNo`, `Retailer Invoice #`, `retailerInvoiceNo`, `Storage Location`, `storageLocation`, `Personal Notes I`, `personalNotes`, `Personal Reference #`, `personalRef`, `owner_photos`, `ownerPhotos`, `provenanceLedger`, `transferStatus`, `transferId`) are absent from BOTH real objects.
4. **MF-4 (Finish Pin Quotes vs `git show 4d17ca5e`):**
   - Quoted `toFirestore()` optimistic wrapper lines at lines **`:490-494`** (field edit save) and **`:682-686`** (CAC toggle save) verbatim, explicitly including `, _coin.id`.
   - Cited `_loadInspectorMode();` at line **192** (with line 193 as the closing brace `}`).

---

## 2. Standing Scope Boundaries & Operational Locks
- **Production Lock:** `origin/main` strictly locked at `9f04550a45fa4da082ba8948c2d89a521a90fa45`. Pushes, merges, or cherry-picks to main are strictly prohibited.
- **Stripe Lock:** Stripe strictly locked OFF across all client and backend paths.
- **Alerts Only:** Alert-only threshold at $20.00/month in Google Cloud Billing; never budget caps or automated Hosting shutdowns.
- **Strict PLAN ONLY:** Zero code modifications, zero builds, zero Firestore writes/seeding, and zero live deployments without Founder Eric's explicit typed YES.
- **No Argon:** Cycle has NO Argon; permanently dropped.
- **Pin Grounding:** All citations verified against commit `4d17ca5e` and `origin/dev`.

---

## 3. Next Turn
- **Owner:** Grok Bot Chief of Staff (`GROKCOS`) for review scoring (target >= 95).
- **Secondary Review:** Stand Alone Grok (`SAG`) upon GROKCOS >= 95 PASS.

OVER — AG CoS v5
