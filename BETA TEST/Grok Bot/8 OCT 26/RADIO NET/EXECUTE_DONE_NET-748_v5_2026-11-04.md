# EXECUTE DONE NET-748 v5: Canonical Mint Asset Service & SKU Fallback Dictionary
- **Date/Time:** 2026-11-04 4:35 PM ET
- **Station:** AG CoS v4 Work (`ba2bfdb2`)
- **Authority:** Founder Eric typed YES: *"YES, execute NET-748 v5 to p7-gate preview only"* (3:33 PM ET, 4 Nov 2026).
- **Assigned Reference Baton:** `BATON_NET-772_EXECUTE_NET-748_v5_P7-GATE-ONLY_2026-11-04-1540.md`
- **Target Plan:** `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-748_v5_PLAN.md` (SAG 96, Argon 96, 0 must-fixes).

---

## 1. Executive Summary & Verification Metrics

| Item | Result |
| :--- | :--- |
| **Commit & Branch** | [`c294fd3c`](https://github.com/Numista-AI/Numista.AI/commit/c294fd3c799dc3d79d21a618aa166ac6e0f34640) on branch `p7-v8.9` |
| **Flutter Analysis** | `flutter analyze lib/... test/...` -> **No issues found!** (Code 0, 0 errors, 0 warnings across 9 changed items) |
| **Flutter Unit Tests** | `flutter test test/services/canonical_mint_asset_service_test.dart` -> **66/66 PASSED** (45 existing + 21 new NET-748 v5 tests, Code 0) |
| **Firestore Rules Emulator** | `npx firebase emulators:exec --only firestore "npm test"` -> **41/41 PASSED** (38 existing + 3 new SKU dictionary access tests, Code 0) |
| **Section 6 Curl Gate** | 66/66 public asset URLs tested via HTTP HEAD -> **66/66 RETURNED HTTP 200 OK** |
| **Web Build** | `flutter build web --release --base-href "/"` -> **Built build/web in 196.6s (Code 0)** |
| **Preview Channel Deploy** | `firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8` -> **Deploy complete!** |
| **Preview Channel URL** | **`https://numista-vault--p7-gate-8avtpz22.web.app`** (Version `b1df159d0124906d`) |
| **Spend** | **$0.00** |

---

## 2. Implementation Audit

### Step 1: Firestore Rules (`numista_mobile/firestore.rules`)
- Added named SKU dictionary doc read rule at lines 338-348 under `global_metadata/usmint_sku_dictionary/skus/{skuId}`:
  - `allow get: if request.auth != null;`
  - `allow list, create, update, delete: if false;`
- Tested locally with Jest under the Firestore emulator (`firestore.rules.test.js`):
  - `ALLOW: authenticated getDoc of global_metadata/usmint_sku_dictionary/skus/26SQRP succeeds` -> **PASS**
  - `DENY: unauthenticated getDoc of global_metadata/usmint_sku_dictionary/skus/26SQRP fails` -> **PASS**
  - `DENY: authenticated getDocs (list) on .../skus and setDoc both fail` -> **PASS**
- **Zero live rules deployed** (Step 1b remains locked pending Eric's separate typed YES).

### Step 2: Fallback SKU Dictionary (`add_coins_hub.dart`)
- Added `@visibleForTesting const Map<String, Map<String, dynamic>> kFallbackUsMintSkus` containing the exact 11 missing SKUs from Section 4.1:
  `{'26EA', '26XE', '26XL', '26XH', '26XF', '26GC', '26SQRP', '26RG', '23RG', '26RH', '23RH'}`.
- Added `@visibleForTesting static Map<String, dynamic> buildSkuCoinDoc(Map<String, dynamic> data, String itemSku)` mapping dictionary data to coin document schema, preserving sets vs single items.
- Updated `_lookupSku`: falls back to `_kFallbackUsMintSkus[cleanSku]` if the Firestore doc does not exist or Firestore lookup fails.
- Updated `_addSkuToCollection`: stamps `sku` and `mint_product_id` on the created coin doc.

### Step 3: Canonical Mint Asset Service (`canonical_mint_asset_service.dart`)
- Added `_normYear` helper normalizing double/int/string year representations (e.g. `'2026.0'` -> `'2026'`).
- Key list in `extractSku` updated with `retailer_item_num`, `source_product_id`, `cond`, `Condition`.
- Placed `rawSku` and `cleanSku` lookups after line 193.
- ASE proof rule added returning `26EA`.
- Quarter guard added to half dollar block to prevent cross-denomination matches.
- Mayflower Compact 2026 D preserved byte-for-byte.
- Added 2026 quarter loop matching `declaration_of_independence`, `gettysburg_address`, `revolutionary_war`, and `us_constitution`.
- Added Polly Cooper Native American Dollar, 2026 Cent (Unc P/D), and 2026 Nickel (Unc P/D) resolution blocks with verified GCS objects.

### Step 5: Screen Wiring
- `coin_image_service.dart`: wired `CanonicalMintAssetService.resolve` at line 489 for years 2026 and 2023 with verified `sourceLabel: 'Canonical Mint Asset'` and `matchedKey: pair.sku`.
- `review_hub_screen.dart`: wired `CanonicalMintAssetService.resolveFromMap(data)` at `_buildCoinThumbnail`.
- `coin_set_viewer.dart`: wired `resolveFromMap(m)` at `_CoinInSet.fromMap`.
- `inventory_gallery.dart`: wired `resolveFromMap(data)` before falling back to raw URLs.
- `my_collection_screen.dart`:
  - `_CollectionCardImage`: wired `resolveFromMap` before `directUrl`.
  - Inspector: guarded with `CanonicalMintAssetService.hasUserUploadedPhotos(data)` and wired `resolveFromMap`.
  - Vault detail: guarded with `hasUserUploadedPhotos(data)` and wired `resolveFromMap`.
- `coin_detail_screen.dart`: wired `resolveFromMap` with composite map before falling back to reference image fetch.

---

## 3. Scope & Standing Locks Verified

- **origin/main strictly untouched:** main remains locked at `9f04550a`.
- **Live Hosting untouched:** Deployed strictly to channel `p7-gate` (`numista-vault--p7-gate-8avtpz22.web.app`), NOT live hosting.
- **Live Firestore Rules untouched:** 0 rules deployed to live (`firebase deploy --only firestore:rules` was NOT run).
- **Live Firestore Writes untouched:** 0 documents written/seeded.
- **Stripe:** Remains locked OFF.

---

## 4. What Was NOT Tested / Pending

1. **Step 1b Live Firestore Rules Deploy:** Requires Eric's separate typed YES naming the rules diff, project `studio-9101802118-8c9a8`, SHA-256, and rollback procedure.
2. **Firestore Seeding:** Seeding the 11 dictionary documents into live Firestore requires its own typed authorization. On `p7-gate`, the app cleanly uses `kFallbackUsMintSkus`.
3. **Field Tester Manual Walkthrough:** Ready for review on `https://numista-vault--p7-gate-8avtpz22.web.app`.

---

## 5. Next in Queue

Proceeding to **`BATON_NET-778`** (`EXECUTE Plan C: Model Usage Audit`, report only, authorized by Eric's YES at 4:32 PM ET) before **`BATON_NET-777`** (`FAILFIX PLAN v1` for live catalog).
