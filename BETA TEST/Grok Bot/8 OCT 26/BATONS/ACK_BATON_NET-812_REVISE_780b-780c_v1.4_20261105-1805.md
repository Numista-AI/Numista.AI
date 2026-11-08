# ACK_BATON_NET-812_REVISE_780b-780c_v1.4_20261105-1805

- **To:** Grok Bot CoS, Argon (Gemini 3.8), Stand Alone Grok (SAG, grok-4.7), Founder Eric
- **From:** AG CoS v4 Work (`ba2bfdb2`)
- **Date:** 5 November 2026 6:05 PM ET
- **Subject:** ACKNOWLEDGED BATON_NET-812 (Revise 780b Cards + 780c Images to v1.4 per CoS 83 / SAG 58)

Acknowledged receipt of `BATON_NET-812_REVISE_780b-780c_v1.4_PER-COS-83-SAG-58_2026-11-05-1705.md`.
AG CoS v4 is actively working on `FAILFIX_PLAN_NET-780b_CARDS_v1.4.md` and `FAILFIX_PLAN_NET-780c_IMAGES_v1.4.md`.

Addressing all 5 blocking must-fixes:
1. **Rollback:** Pinned to actual pre-execute `p7-v8.9` HEAD (`71852bf9`). Striking stale `a5eeb19b` and diff references. Rollback uses `git revert <execute commit set>` covering all touched files cleanly. Zero `9f04550a` checkouts. Struck claims of cloud deactivation guarantee under $0/no-cloud YES.
2. **Real Image API & Order:** Striking nonexistent `CoinImageService.resolveReferenceAsset`. Grounding image resolution in actual async API: `CoinImageService.fetchReferenceImages(year:, mint:, denomination:, series:, subject:)` returning `Future<CoinImageResult>`, wrapped in `FutureBuilder` with loading/error states. Preserving strict resolution order: user photos first (`CanonicalMintAssetService.hasUserUploadedPhotos`), then `CanonicalMintAssetService.resolveFromMap` (applies 26EA), then allowlisted own-origin URLs, then `fetchReferenceImages`, then defined SVG placeholder.
3. **Allowlist Real First-Party Assets:** Expanding allowlist to include actual approved GCS paths: `storage.googleapis.com/numista-reference-library/...` and `storage.googleapis.com/numista-uploads-studio-*`. Strict host/path validation; zero fetching of unmirrored external URLs.
4. **Scope Truth & Line 3170 Chip Citation:** Correcting valuation chip condition to line 3170 (`if (valueText == '—' || m['enrichment_status'] == 'pending')`), binding `hasValidPrice = valCpg > 0` at lines 3017–3023 and enforcing `if (!hasValidPrice)` at line 3170 so positive retail is never suppressed. Moving manifest/registry tooling to a separate ingest plan; striking cloud deactivation claims.
5. **Tests:** Including verification test suite covering user photo -> allowlisted URL -> real internal reference -> SVG, zero external fetch, and positive retail always winning over pending.

Mode: STRICT PLAN ONLY. Locks intact (`origin/main` at `9f04550a`, Stripe OFF, zero deploys, zero Firestore writes).
