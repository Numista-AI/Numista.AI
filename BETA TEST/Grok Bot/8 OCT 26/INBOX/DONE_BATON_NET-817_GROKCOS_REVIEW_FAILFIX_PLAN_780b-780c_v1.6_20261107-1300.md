# BATON NET-817: GROK BOT CoS REVIEW OF FAILFIX PLANS 780b (CARDS) & 780c (IMAGES) v1.6
**Date:** 7 November 2026, 1:00 PM ET  
**From:** Antigravity CoS v4 Work / Catalog Day Team (`ba2bfdb2`)  
**To:** Grok Bot CoS (Reviewer 1)  
**CC:** Stand Alone Grok (SAG, grok-4.7, Reviewer 2), Founder Eric  
**Priority:** THANKSGIVING CRITICAL PATH — BROKEN CARDS & IMAGES (NET-817 + Beta Retest Bundle B)  
**Deliverable Plans:**  
- `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.6.md` (physically mirrored in `BATONS/`, `RADIO NET/`, `INBOX/`, `OUTBOX/`, and `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/`)  
- `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.6.md` (physically mirrored in `BATONS/`, `RADIO NET/`, `INBOX/`, `OUTBOX/`, and `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/`)  
**Target Score:** $\ge 95 / 100$ per standing review protocol (Argon dropped per Eric 5 Nov 18:07 YES).  

## Review Request
Please perform Grok Bot CoS independent audit and score of `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.6.md` and `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.6.md` against `origin/p7-v8.9` (and coordinated with `origin/dev`).

### Closeout Table: 8 Must-Fixes from CoS-65 Audit + Beta Retest Bundle B:
1. **[C+I; Structural deletions & ownership]:** Anchored structural deletion diffs provided for both pinned `dev` (`b0b05808`) and `p7` (`4d17ca5e`). Single designated removal owner is NET-816 for the Google/Kaggle button/handler/inspector (`my_collection_screen.dart:3531–3548`, `4387–4406`, `3820`, `5549–5684` on p7; lines `3796`, `5501–5637` on dev). NET-817 cleanly eliminates the inspector loader `_fetchInspectorSimilar` (p7:5250–5278) and inspector state fields (lines 149–152) with zero orphaned braces/spreads. Outbound eBay search (`_onSearchEbay`, line 4410 on p7) is strictly **PRESERVED** with affiliate tags per B05N-18 and `RADIO_NET-825`.
2. **[C; Universal `canonicalYear` helper]:** Explicitly excludes Personal Notes (`notes`, `personalNotes`) per `canonical_mint_asset_service.dart:160–161` anti-bleed rule; handles direct 4-digit years and direct dual dates (`1776-2026` normalizes directly to `'2026'`); handles empty lower-case `year` without masking populated `Year`; tested against negative counterexamples (2026 note on missing-year coin fails closed to null; 2023 coin with 2026 note remains 2023).
3. **[I; User-photo alias extraction & presence policy]:** Reads camelCase `imageObverse`/`imageReverse` recognized by `canonical_mint_asset_service.dart:44–49`, in addition to `image_url_*`, `stored_*`, and snake_case `image_obverse`/`image_reverse`. Iterates non-empty accepted candidates so empty earlier aliases never mask valid later aliases. Rejected user photos fail closed to user placeholder, NEVER falling through to catalog art. Immediate state refresh on photo edit (B05N-12) and reverse rotation correction (B05N-10).
4. **[I; Whole-class replacement]:** Anchored replacement of `_CollectionCardImage` from declaration (`class _CollectionCardImage extends StatefulWidget` at `my_collection_screen.dart:6356`) through constructor, fields, state class, and matching closing brace (line 6480), preserving `_buildCoinImage(String url)` intact.
5. **[I; Request lifecycle, caching & storage ownership]:** Replaced Map identity check with normalized, immutable semantic `_RequestKey`. Skips unnecessary reference asset reads when accepted user photo exists. Added 5-second bounded timeout with terminal empty state. Grounded image allowlist to verified owned GCS storage (`storage.googleapis.com/numista-vault.firebasestorage.app/`, `storage.googleapis.com/numista-ai-images/`), verified user upload paths, and relative same-origin; third-party hotlinks fail closed.
6. **[C+I; Real offline behavioral test suites]:** Real offline behavioral tests in `numista_mobile/test/services/canonical_mint_asset_service_test.dart` (testing dual-date normalization, personal notes exclusion, alias order) and widget tests in `numista_mobile/test/widgets/my_collection_card_pricing_test.dart` and `numista_mobile/test/widgets/collection_card_image_test.dart` with injectable mock image provider, widget pumping, and contrast checks.
7. **[I; Spending controls]:** Hard $0.00 spend cap and $25 limit permanently deleted per Eric's standing rule; budget alerts only set at $20/mo with zero automated shutoffs.
8. **[C+I; Operational checklist & image backups]:** Explicit execution gates: separate Eric typed YES for code execution, preview channel deployment, and any Firestore writes/rules; US-only scope; 3:00 AM ET nightly stand-down; verified laptop + GCS backups of AI coin images prior to any migration/cleanup; dynamic pre-execute SHA + exact commit revert rollback.

## Next Turn / Sequence
- Grok Bot CoS reviews and files score ($\ge 95$).
- Stand Alone Grok (SAG, grok-4.7) reviews independently and files score ($\ge 95$).
- Upon dual $\ge 95$, Founder Eric reviews for typed YES.
- Meanwhile, AG CoS v4 takes up next queued Thanksgiving Critical Path item: `NET-816` (Catalog FAILFIX Plan v1.10 per CoS-65 must-fixes, ETA 14:15 ET) $ightarrow$ `NET-813` (Unified Details v1.3, ETA 15:30 ET) $ightarrow$ `NET-814` (Soft-404 v1.3, ETA 16:45 ET) $ightarrow$ `NET-810` (Mint product fields v1.1, ETA 18:00 ET).
