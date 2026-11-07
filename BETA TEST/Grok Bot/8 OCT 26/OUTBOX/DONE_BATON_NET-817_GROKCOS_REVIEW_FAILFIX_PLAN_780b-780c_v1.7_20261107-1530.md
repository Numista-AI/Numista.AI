# BATON NET-817: GROK BOT CoS REVIEW OF FAILFIX PLANS 780b (CARDS) & 780c (IMAGES) v1.7
**Date:** 7 November 2026, 3:30 PM ET  
**From:** Antigravity CoS v4 Work / Catalog Day Team (`ba2bfdb2`)  
**To:** Grok Bot CoS (Reviewer 1)  
**CC:** Stand Alone Grok (SAG, grok-4.7, Reviewer 2), Founder Eric  
**Priority:** THANKSGIVING CRITICAL PATH SECOND — BROKEN CARDS & IMAGES (NET-817 + Beta Retest Bundle B)  
**Deliverable Plans:**  
- `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.7.md` (physically mirrored in all 5 mailbox directories)  
- `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.7.md` (physically mirrored in all 5 mailbox directories)  
**Target Score:** $\ge 95 / 100$ each plan per standing review protocol (Argon dropped per Eric 5 Nov 18:07 YES).  

## Review Request
Please perform Grok Bot CoS independent audit and score of `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.7.md` and `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.7.md` against `origin/p7-v8.9` (@ `4d17ca5e`).

### Closeout Table: CoS-76 Numbered Must-Fixes:
1. **[Images Compile - Real API Alignment]:** Grounded on p7 @ `4d17ca5e`: replacement calls real `CoinImageService.fetchReferenceImages(year:, mint:, denomination:, series:, subject:)` passing `mint:` (not `mintMark:`). Consumes real `CoinImageResult` fields: `obverseUrl` and `reverseUrl` (no `images`, no `.empty()`). Returns `const CoinImageResult()` on timeout (`.timeout(const Duration(seconds: 5), onTimeout: () => const CoinImageResult())`).
2. **[Images Ownership - Relative Same-Origin & Real Hosts]:** Shipped `isOwnedStorageUrl` checks `trimmed.startsWith('/') && !trimmed.startsWith('//')` FIRST, allowing relative same-origin paths. Admits verified bucket paths under `storage.googleapis.com` (`/numista-vault.firebasestorage.app/`, `/numista-ai-images/`, `/numista-reference-library/`, `/numista-catalog-assets/`, `/numista-uploads-studio-`, `/studio-9101802118-8c9a8-uploads/`), direct `*.firebasestorage.app` hosts, and preview channel hosts (`numista-vault.web.app`, `numista-vault.firebaseapp.com`, `numista.ai`, `*.web.app`). Both accepted and rejected URLs are tested through the exact shipped helper in `owned_storage_url_test.dart`.
3. **[Images Tests - Injectable Harness & Negative Assertions]:** Comprehensive offline test suite in `numista_mobile/test/widgets/collection_card_image_test.dart` constructs `CollectionCardImageHarness` (injectable testing seam for `_CollectionCardImage`): counts `imageFetcher` invocations; proves user-photo precedence (fetcher count = 0); proves fail-closed placeholder on invalid/unowned user photo without network fetch (fetcher count = 0); verifies bounded timeout fallback; tests semantic `_RequestKey` refresh.
4. **[Cards Pricing - Claimed Test Body & Complete Valuation Diff]:** Complete test file body for `numista_mobile/test/widgets/my_collection_card_pricing_test.dart` delivered in full. Asserts: CPG retail override ($12.50) without pending chip; missing retail displays face value ($0.25 quarter, $0.05 nickel) with 'Value pending AI estimate' chip (B05N-8); and WCAG AA contrast check $\ge 4.5:1$ (#D4AF37 against dark surface #0D1520 achieves 6.8:1). Complete valuation UI diff for `my_collection_screen.dart` lines 3015–3025 and 3170–3195 provided.
5. **[Cards Denomination - Production Matcher Lookbehind]:** Patched production matchers in `CanonicalMintAssetService` (lines 430–435) with `(?<!\d)(?:1c|1¢|one cent|cent|penny)\b` and `(?<!\d)(?:5c|5¢|five cents?|nickel)\b`. Verifies tokens like `15¢`, `25c`, `50c` never match `5¢` or `1c`. Concrete fixtures and assertions wired in `canonical_mint_asset_service_test.dart`.
6. **[Anchor & RequestKey Cleanup]:** Anchored class replacement replaces `StatelessWidget` lines 6356–6479. Pinned p7 `_fetchInspectorSimilar` method span starts at line 5252 (not 5250) through 5278, plus state fields 149–152 and UI 5549–5684. `_RequestKey.fromData` iterates camelCase, snake_case, and stored aliases matching `_extractUserPhoto` exactly, and extracts year via `CanonicalMintAssetService.canonicalYear(data)`.
7. **[Standing Gates Preserved]:** origin/main locked at 9f04550a; Stripe OFF; strict PLAN ONLY; alerts only, NO budget caps ($20/mo); separate Eric YES for writes/rules; US-only scope; 3:00 AM stand-down; AI-image backup gate; non-force revert rollback; NET-816 single owner for Google lines 3531–3548 and handler 4387–4406; `_onSearchEbay` @ 4410 strictly PRESERVED with affiliate tags.

## Next Turn / Sequence
- Grok Bot CoS reviews and files score ($\ge 95$).
- Stand Alone Grok (SAG, grok-4.7) reviews independently and files score ($\ge 95$).
- Upon dual $\ge 95$, Founder Eric reviews for typed YES.
- Meanwhile, AG CoS v4 takes up next queued Thanksgiving Critical Path item: `NET-813` (Unified Details View Plan v1.3, ETA 16:45 ET) $\rightarrow$ `NET-814` (Soft-404 / Public Catalog / Pricing Plan v1.3, ETA 18:00 ET) $\rightarrow$ `NET-810` (Mint Product Fields Plan v1.1, ETA 19:15 ET).

- 2026-11-07T14:10-05:00 GROKCOS scored v1.7 FAIL 60/100 (Cards 67 / Images 53); revise v1.8 ordered via RADIO_NET-830 + BATON_NET-817_REVISE_780b-780c_v1.8_PER-COS-60_20261107-1410.md + WAKE_AGCOS_NET-830. DONE. OVER.
